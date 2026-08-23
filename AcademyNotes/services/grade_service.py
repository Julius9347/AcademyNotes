"""Calificaciones: registro, promedio ponderado, publicacion y consulta.

Estados de una calificacion:
    borrador   -> solo la ve el profesor
    publicada  -> visible para estudiante y familia (puede cambiar)
    final      -> calificacion oficial del periodo

Que sea "publicada" no basta para que el estudiante la vea: si el modo
reporte activo esta apagado, ademas debe pertenecer a un preinforme
publicado (ver settings_service).
"""
from datetime import date

from flask import current_app

from core.db import execute, query_all, query_one, scalar, transaction
from services import alert_service, audit_service, settings_service


class ValidationError(Exception):
    """Datos invalidos (se traduce a HTTP 400)."""


FEEDBACK_CATEGORIES = (
    "Dominio adecuado",
    "Requiere practica",
    "Presenta dificultades",
    "Debe reforzar conceptos",
    "Actividad incompleta",
    "No entrego",
    "Requiere recuperacion",
)


def _limits() -> tuple[float, float]:
    config = current_app.config
    return float(config.get("MIN_SCORE", 1.0)), float(config.get("MAX_SCORE", 5.0))


def validate_score(score) -> float | None:
    """None significa 'sin calificar', que es un estado valido."""
    if score is None or score == "":
        return None
    try:
        value = float(str(score).replace(",", "."))
    except (TypeError, ValueError):
        raise ValidationError("La nota debe ser un numero.")
    minimum, maximum = _limits()
    if value < minimum or value > maximum:
        raise ValidationError(
            f"La nota debe estar entre {minimum:.1f} y {maximum:.1f}."
        )
    return round(value, 2)


def visibility_condition(alias: str = "gr") -> str:
    """Condicion SQL que decide que puede ver un estudiante o acudiente."""
    base = f"{alias}.status IN ('publicada','final')"
    if settings_service.reporte_activo():
        return base
    return (
        f"{base} AND {alias}.published_report_id IN "
        "(SELECT id FROM reports WHERE status = 'publicado')"
    )


# ------------------------------------------------------- REGISTRO DE NOTAS ---
def get_grade(activity_id: int, student_id: int) -> dict | None:
    return query_one(
        "SELECT * FROM grades WHERE activity_id = ? AND student_id = ?",
        (activity_id, student_id),
    )


def save_grade(activity_id: int, student_id: int, score, user: dict,
               feedback_category: str | None = None,
               feedback_text: str | None = None,
               is_missing: bool | None = None,
               recovery_status: str | None = None) -> dict:
    """Crea o actualiza una calificacion y deja constancia en el historial."""
    value = validate_score(score)
    existing = get_grade(activity_id, student_id)

    if existing is None:
        grade_id = execute(
            """
            INSERT INTO grades
                (activity_id, student_id, score, feedback_category, feedback_text,
                 is_missing, recovery_status, updated_by)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (activity_id, student_id, value, feedback_category, feedback_text,
             1 if is_missing else 0, recovery_status or "ninguna", user["id"]),
        )
        audit_service.log(
            user, "Registro calificacion", "calificacion", grade_id,
            _describe(activity_id, student_id), None, value,
        )
    else:
        grade_id = existing["id"]
        execute(
            """
            UPDATE grades
               SET score = ?, feedback_category = ?, feedback_text = ?,
                   is_missing = ?, recovery_status = ?, updated_by = ?,
                   updated_at = datetime('now','localtime')
             WHERE id = ?
            """,
            (
                value,
                feedback_category if feedback_category is not None
                else existing["feedback_category"],
                feedback_text if feedback_text is not None
                else existing["feedback_text"],
                (1 if is_missing else 0) if is_missing is not None
                else existing["is_missing"],
                recovery_status or existing["recovery_status"],
                user["id"],
                grade_id,
            ),
        )
        if existing["score"] != value:
            audit_service.log(
                user, "Modifico calificacion", "calificacion", grade_id,
                _describe(activity_id, student_id), existing["score"], value,
            )
    return get_grade(activity_id, student_id)


def _describe(activity_id: int, student_id: int) -> str:
    row = query_one(
        """
        SELECT a.name AS activity_name, s.name AS subject_name, u.full_name
        FROM activities a
        JOIN teaching_assignments ta ON ta.id = a.assignment_id
        JOIN subjects s ON s.id = ta.subject_id
        JOIN students st ON st.id = ?
        JOIN users u ON u.id = st.user_id
        WHERE a.id = ?
        """,
        (student_id, activity_id),
    )
    if row is None:
        return "Calificacion"
    return f"{row['full_name']} - {row['subject_name']} - {row['activity_name']}"


def update_score_only(grade_id: int, score, user: dict, reason: str) -> dict | None:
    """Cambio de nota fuera del cuaderno (por ejemplo, tras una revision)."""
    value = validate_score(score)
    existing = query_one("SELECT * FROM grades WHERE id = ?", (grade_id,))
    if existing is None:
        raise ValidationError("La calificacion no existe.")
    execute(
        "UPDATE grades SET score = ?, updated_by = ?, "
        "updated_at = datetime('now','localtime') WHERE id = ?",
        (value, user["id"], grade_id),
    )
    audit_service.log(
        user, "Modifico calificacion", "calificacion", grade_id,
        f"{_describe(existing['activity_id'], existing['student_id'])} ({reason})",
        existing["score"], value,
    )
    return query_one("SELECT * FROM grades WHERE id = ?", (grade_id,))


# --------------------------------------------------------------- PROMEDIOS ---
def weighted_average(rows: list[dict]) -> float | None:
    """Promedio ponderado. rows = [{score, weight}, ...].

    Solo entran las actividades que ya tienen nota; no se usa AVG simple
    porque las actividades pesan distinto.
    """
    total_weight = 0.0
    total = 0.0
    for row in rows:
        if row.get("score") is None:
            continue
        weight = float(row.get("weight") or 0)
        if weight <= 0:
            continue
        total += float(row["score"]) * weight
        total_weight += weight
    if total_weight == 0:
        return None
    return round(total / total_weight, 2)


def student_scores(student_id: int, assignment_id: int, period_id: int,
                   only_visible: bool = False) -> list[dict]:
    sql = """
        SELECT gr.id, gr.score, gr.status, gr.is_missing, gr.recovery_status,
               gr.feedback_category, gr.feedback_text, gr.published_report_id,
               a.id AS activity_id, a.name AS activity_name, a.weight,
               a.kind, a.due_date, a.allows_recovery
        FROM activities a
        LEFT JOIN grades gr ON gr.activity_id = a.id AND gr.student_id = ?
        WHERE a.assignment_id = ? AND a.period_id = ?
    """
    params: list = [student_id, assignment_id, period_id]
    sql += " ORDER BY COALESCE(a.due_date, a.created_at), a.id"
    rows = query_all(sql, params)
    if only_visible:
        # La actividad siempre se lista: el estudiante debe saber que trabajo
        # existe. Lo que se filtra es la calificacion, no la actividad.
        # Una nota no visible se muestra como actividad sin calificar: se
        # oculta tambien el id para que no se pueda pedir revision de algo
        # que todavia no esta publicado.
        for row in rows:
            if row["id"] is not None and not _is_visible(row):
                row["id"] = None
                row["score"] = None
                row["status"] = "borrador"
    return rows


def _is_visible(row: dict) -> bool:
    if row.get("status") not in ("publicada", "final"):
        return False
    if settings_service.reporte_activo():
        return True
    if not row.get("published_report_id"):
        return False
    report = query_one(
        "SELECT status FROM reports WHERE id = ?", (row["published_report_id"],)
    )
    return bool(report and report["status"] == "publicado")


def subject_summary(student_id: int, assignment: dict, period_id: int,
                    only_visible: bool = True) -> dict:
    """Resumen de una asignatura para un estudiante: promedio, tendencia,
    pendientes, estado y motivos.
    """
    rows = student_scores(student_id, assignment["id"], period_id, only_visible)
    graded = [row for row in rows if row["score"] is not None]
    average = weighted_average(rows)
    today = date.today().isoformat()

    pending = 0
    for row in rows:
        if row["score"] is not None:
            continue
        if row.get("is_missing"):
            pending += 1
        elif row.get("due_date") and row["due_date"] < today:
            pending += 1
    recovery_pending = sum(
        1 for row in rows if row.get("recovery_status") in ("disponible", "pendiente")
    )

    trend_value = alert_service.trend([row["score"] for row in graded])
    evaluation = alert_service.evaluate(
        average, trend_value, pending, recovery_pending, len(graded)
    )

    return {
        "assignment_id": assignment["id"],
        "subject_id": assignment["subject_id"],
        "subject_name": assignment["subject_name"],
        "teacher_name": assignment.get("teacher_name"),
        "average": average,
        "activities_total": len(rows),
        "activities_graded": len(graded),
        "pending": pending,
        "recovery_pending": recovery_pending,
        "activities": rows,
        **evaluation,
    }


def student_overview(student_id: int, group_id: int, period_id: int,
                     only_visible: bool = True) -> list[dict]:
    """Resumen de todas las asignaturas del estudiante en un periodo."""
    from services import academic_service  # import local: evita ciclo

    summaries = []
    for assignment in academic_service.assignments_for_group(group_id):
        assignment = dict(assignment, id=assignment["id"])
        summaries.append(
            subject_summary(student_id, assignment, period_id, only_visible)
        )
    return summaries


def global_average(summaries: list[dict]) -> float | None:
    values = [s["average"] for s in summaries if s["average"] is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 2)


# -------------------------------------------------------- CUADERNO DOCENTE ---
def gradebook(assignment_id: int, period_id: int) -> dict:
    """Matriz estudiante x actividad para la vista del profesor."""
    assignment = query_one(
        "SELECT group_id FROM teaching_assignments WHERE id = ?", (assignment_id,)
    )
    if assignment is None:
        raise ValidationError("La asignacion no existe.")

    activities = query_all(
        "SELECT * FROM activities WHERE assignment_id = ? AND period_id = ? "
        "ORDER BY COALESCE(due_date, created_at), id",
        (assignment_id, period_id),
    )
    students = query_all(
        """
        SELECT s.id, s.student_code, u.full_name
        FROM students s JOIN users u ON u.id = s.user_id
        WHERE s.group_id = ? ORDER BY u.full_name
        """,
        (assignment["group_id"],),
    )
    grades = query_all(
        """
        SELECT gr.* FROM grades gr
        JOIN activities a ON a.id = gr.activity_id
        WHERE a.assignment_id = ? AND a.period_id = ?
        """,
        (assignment_id, period_id),
    )
    by_key = {(g["activity_id"], g["student_id"]): g for g in grades}

    rows = []
    for student in students:
        cells = []
        for activity in activities:
            grade = by_key.get((activity["id"], student["id"]))
            cells.append({
                "activity_id": activity["id"],
                "grade_id": grade["id"] if grade else None,
                "score": grade["score"] if grade else None,
                "status": grade["status"] if grade else "borrador",
                "feedback_category": grade["feedback_category"] if grade else None,
                "feedback_text": grade["feedback_text"] if grade else None,
                "is_missing": bool(grade["is_missing"]) if grade else False,
                "recovery_status": grade["recovery_status"] if grade else "ninguna",
                "weight": activity["weight"],
            })
        rows.append({
            "student_id": student["id"],
            "student_code": student["student_code"],
            "full_name": student["full_name"],
            "cells": cells,
            "average": weighted_average(cells),
        })

    return {
        "activities": activities,
        "students": rows,
        "total_weight": round(sum(a["weight"] for a in activities), 2),
        "draft_count": sum(
            1 for g in grades if g["status"] == "borrador" and g["score"] is not None
        ),
    }


# ------------------------------------------------------------- PUBLICACION ---
def publish_activity(activity_id: int, user: dict, report_id: int | None = None) -> int:
    """Pasa a 'publicada' las notas registradas de una actividad."""
    count = scalar(
        "SELECT COUNT(*) FROM grades WHERE activity_id = ? AND status = 'borrador' "
        "AND score IS NOT NULL",
        (activity_id,),
    ) or 0
    execute(
        """
        UPDATE grades
           SET status = 'publicada',
               published_at = datetime('now','localtime'),
               published_report_id = ?,
               updated_at = datetime('now','localtime')
         WHERE activity_id = ? AND status = 'borrador' AND score IS NOT NULL
        """,
        (report_id, activity_id),
    )
    activity = query_one("SELECT name FROM activities WHERE id = ?", (activity_id,))
    audit_service.log(
        user, "Publico actividad", "actividad", activity_id,
        f"{activity['name'] if activity else 'Actividad'}: {count} calificaciones publicadas",
        "borrador", "publicada",
    )
    return count


def publish_assignment_period(assignment_id: int, period_id: int, report_id: int,
                              user: dict) -> int:
    """Publica todas las notas en borrador de una asignacion dentro de un
    preinforme. Es la operacion que usa el profesor al cerrar su revision.
    """
    with transaction() as connection:
        cursor = connection.execute(
            """
            UPDATE grades
               SET status = 'publicada',
                   published_at = datetime('now','localtime'),
                   published_report_id = ?,
                   updated_at = datetime('now','localtime')
             WHERE score IS NOT NULL
               AND status = 'borrador'
               AND activity_id IN (
                     SELECT id FROM activities
                      WHERE assignment_id = ? AND period_id = ?)
            """,
            (report_id, assignment_id, period_id),
        )
        count = cursor.rowcount
    audit_service.log(
        user, "Publico calificaciones", "asignacion", assignment_id,
        f"{count} calificaciones publicadas en el preinforme #{report_id}",
        "borrador", "publicada",
    )
    return count


def last_update_for_student(student_id: int) -> str:
    """Marca de tiempo para el sondeo del estudiante."""
    value = scalar(
        f"""
        SELECT MAX(gr.updated_at) FROM grades gr
        WHERE gr.student_id = ? AND {visibility_condition('gr')}
        """,
        (student_id,),
    )
    report = scalar(
        "SELECT MAX(published_at) FROM reports WHERE status = 'publicado'"
    )
    return max(filter(None, [value, report, ""]), default="")
