"""Actividades y evaluaciones.

Una calificacion no es una columna suelta: cuelga de una actividad que
tiene nombre, tipo, ponderacion, fecha y periodo.
"""
from core.db import execute, query_all, query_one

KINDS = ("taller", "quiz", "parcial", "proyecto", "otro")


class ValidationError(Exception):
    """Datos de entrada invalidos (se traduce a HTTP 400)."""


def validate_activity(name: str, weight: float, kind: str) -> None:
    if not name or not name.strip():
        raise ValidationError("El nombre de la actividad es obligatorio.")
    if kind not in KINDS:
        raise ValidationError(f"Tipo de actividad invalido: {kind}.")
    try:
        weight = float(weight)
    except (TypeError, ValueError):
        raise ValidationError("La ponderacion debe ser un numero.")
    if weight <= 0 or weight > 100:
        raise ValidationError("La ponderacion debe estar entre 0 y 100.")


def create_activity(assignment_id: int, period_id: int, name: str,
                    kind: str = "taller", weight: float = 10,
                    due_date: str | None = None,
                    allows_recovery: bool = False) -> int:
    validate_activity(name, weight, kind)
    return execute(
        """
        INSERT INTO activities
            (assignment_id, period_id, name, kind, weight, due_date, allows_recovery)
        VALUES (?,?,?,?,?,?,?)
        """,
        (assignment_id, period_id, name.strip(), kind, float(weight),
         due_date or None, 1 if allows_recovery else 0),
    )


def update_activity(activity_id: int, name: str, kind: str, weight: float,
                    due_date: str | None, allows_recovery: bool) -> None:
    validate_activity(name, weight, kind)
    execute(
        """
        UPDATE activities
           SET name = ?, kind = ?, weight = ?, due_date = ?,
               allows_recovery = ?, updated_at = datetime('now','localtime')
         WHERE id = ?
        """,
        (name.strip(), kind, float(weight), due_date or None,
         1 if allows_recovery else 0, activity_id),
    )


def delete_activity(activity_id: int) -> None:
    execute("DELETE FROM activities WHERE id = ?", (activity_id,))


def get_activity(activity_id: int) -> dict | None:
    return query_one(
        """
        SELECT a.*, ta.subject_id, ta.group_id, ta.teacher_id,
               s.name AS subject_name, g.name AS group_name,
               p.name AS period_name
        FROM activities a
        JOIN teaching_assignments ta ON ta.id = a.assignment_id
        JOIN subjects        s ON s.id = ta.subject_id
        JOIN student_groups  g ON g.id = ta.group_id
        JOIN academic_periods p ON p.id = a.period_id
        WHERE a.id = ?
        """,
        (activity_id,),
    )


def list_activities(assignment_id: int, period_id: int | None = None) -> list[dict]:
    sql = """
        SELECT a.*,
               (SELECT COUNT(*) FROM grades gr
                 WHERE gr.activity_id = a.id AND gr.score IS NOT NULL) AS graded_count,
               (SELECT COUNT(*) FROM grades gr
                 WHERE gr.activity_id = a.id AND gr.status = 'borrador') AS draft_count
        FROM activities a
        WHERE a.assignment_id = ?
    """
    params: list = [assignment_id]
    if period_id:
        sql += " AND a.period_id = ?"
        params.append(period_id)
    sql += " ORDER BY COALESCE(a.due_date, a.created_at), a.id"
    return query_all(sql, params)


def activities_for_student(student_id: int, period_id: int,
                           subject_id: int | None = None) -> list[dict]:
    """Actividades que le corresponden a un estudiante por su grupo.

    Las actividades siempre son visibles (el estudiante debe saber que
    trabajo existe); la calificacion sigue las reglas de publicacion.
    """
    sql = """
        SELECT a.*, s.name AS subject_name, ta.subject_id, ta.id AS assignment_id
        FROM activities a
        JOIN teaching_assignments ta ON ta.id = a.assignment_id
        JOIN subjects s              ON s.id = ta.subject_id
        JOIN students st             ON st.group_id = ta.group_id
        WHERE st.id = ? AND a.period_id = ?
    """
    params: list = [student_id, period_id]
    if subject_id:
        sql += " AND ta.subject_id = ?"
        params.append(subject_id)
    sql += " ORDER BY COALESCE(a.due_date, a.created_at), a.id"
    return query_all(sql, params)


def total_weight(assignment_id: int, period_id: int) -> float:
    rows = query_all(
        "SELECT weight FROM activities WHERE assignment_id = ? AND period_id = ?",
        (assignment_id, period_id),
    )
    return round(sum(row["weight"] for row in rows), 2)
