"""Solicitudes de revision de una calificacion.

El objetivo es canalizar el desacuerdo por un camino ordenado en lugar de
que aparezca como reclamo informal, y que toda consecuencia quede
registrada en el historial.
"""
from core.db import execute, query_all, query_one
from services import audit_service, grade_service

REASONS = {
    "no_aparece": "No aparece una actividad que entregue.",
    "posible_error": "Creo que existe un error en la calificacion.",
    "no_entiendo": "No entiendo como se obtuvo la calificacion.",
    "otro": "Otro.",
}

GUIDELINES = (
    "Revisa la actividad y los criterios antes de enviar.",
    "Explica concretamente que deseas que se revise.",
    "Indica si entregaste la actividad y por que medio.",
    "No solicites un cambio unicamente porque deseas una nota mayor.",
)


class ValidationError(Exception):
    pass


def create_request(grade_id: int, student_id: int, reason_code: str,
                   message: str, user: dict) -> int:
    if reason_code not in REASONS:
        raise ValidationError("Motivo de revision invalido.")
    if not message or len(message.strip()) < 10:
        raise ValidationError(
            "Explica en al menos 10 caracteres que deseas que se revise."
        )
    grade = query_one("SELECT * FROM grades WHERE id = ?", (grade_id,))
    if grade is None or grade["student_id"] != student_id:
        raise ValidationError("La calificacion no corresponde al estudiante.")
    existing = query_one(
        "SELECT id FROM review_requests WHERE grade_id = ? AND status = 'pendiente'",
        (grade_id,),
    )
    if existing is not None:
        raise ValidationError("Ya existe una solicitud pendiente para esta nota.")

    request_id = execute(
        """
        INSERT INTO review_requests (grade_id, student_id, reason_code, message)
        VALUES (?,?,?,?)
        """,
        (grade_id, student_id, reason_code, message.strip()),
    )
    audit_service.log(
        user, "Solicito revision", "solicitud", request_id, REASONS[reason_code]
    )
    return request_id


def _base_query() -> str:
    return """
        SELECT rr.*, gr.score, gr.activity_id, gr.student_id,
               a.name AS activity_name, a.assignment_id,
               s.name AS subject_name, g.name AS group_name,
               u.full_name AS student_name, ta.teacher_id
        FROM review_requests rr
        JOIN grades gr               ON gr.id = rr.grade_id
        JOIN activities a            ON a.id = gr.activity_id
        JOIN teaching_assignments ta ON ta.id = a.assignment_id
        JOIN subjects s              ON s.id = ta.subject_id
        JOIN student_groups g        ON g.id = ta.group_id
        JOIN students st             ON st.id = rr.student_id
        JOIN users u                 ON u.id = st.user_id
    """


def list_for_teacher(teacher_id: int, status: str | None = None) -> list[dict]:
    sql = _base_query() + " WHERE ta.teacher_id = ?"
    params: list = [teacher_id]
    if status:
        sql += " AND rr.status = ?"
        params.append(status)
    sql += " ORDER BY CASE rr.status WHEN 'pendiente' THEN 0 ELSE 1 END, rr.id DESC"
    rows = query_all(sql, params)
    for row in rows:
        row["reason_label"] = REASONS.get(row["reason_code"], row["reason_code"])
    return rows


def list_for_student(student_id: int) -> list[dict]:
    rows = query_all(
        _base_query() + " WHERE rr.student_id = ? ORDER BY rr.id DESC",
        (student_id,),
    )
    for row in rows:
        row["reason_label"] = REASONS.get(row["reason_code"], row["reason_code"])
    return rows


def get_request(request_id: int) -> dict | None:
    row = query_one(_base_query() + " WHERE rr.id = ?", (request_id,))
    if row:
        row["reason_label"] = REASONS.get(row["reason_code"], row["reason_code"])
    return row


def pending_count(teacher_id: int) -> int:
    row = query_one(
        """
        SELECT COUNT(*) AS total
        FROM review_requests rr
        JOIN grades gr               ON gr.id = rr.grade_id
        JOIN activities a            ON a.id = gr.activity_id
        JOIN teaching_assignments ta ON ta.id = a.assignment_id
        WHERE ta.teacher_id = ? AND rr.status = 'pendiente'
        """,
        (teacher_id,),
    )
    return row["total"] if row else 0


def respond(request_id: int, user: dict, status: str, response: str,
            new_score=None) -> dict | None:
    """Responde una solicitud. Si se acepta con nota nueva, se actualiza la
    calificacion y el cambio queda en el historial.
    """
    if status not in ("revisada", "aceptada", "rechazada"):
        raise ValidationError("Estado de respuesta invalido.")
    request = get_request(request_id)
    if request is None:
        raise ValidationError("La solicitud no existe.")
    if not response or not response.strip():
        raise ValidationError("Debes escribir una explicacion para el estudiante.")

    if status == "aceptada" and new_score not in (None, ""):
        grade_service.update_score_only(
            request["grade_id"], new_score, user,
            f"solicitud de revision #{request_id}",
        )

    execute(
        """
        UPDATE review_requests
           SET status = ?, teacher_response = ?,
               resolved_at = datetime('now','localtime'), resolved_by = ?
         WHERE id = ?
        """,
        (status, response.strip(), user["id"], request_id),
    )
    audit_service.log(
        user, "Respondio solicitud de revision", "solicitud", request_id,
        f"{request['student_name']} - {request['activity_name']}",
        request["status"], status,
    )
    return get_request(request_id)
