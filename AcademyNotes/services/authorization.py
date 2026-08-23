"""Autorizacion por recurso.

No basta con saber que el usuario tiene rol de profesor: hay que
comprobar que la asignacion, la actividad o la nota que quiere tocar
pertenece realmente a una de sus asignaciones.
"""
from core.db import query_one
from core.security import PermissionError_


def teacher_id_for_user(user_id: int) -> int | None:
    row = query_one("SELECT id FROM teachers WHERE user_id = ?", (user_id,))
    return row["id"] if row else None


def student_id_for_user(user_id: int) -> int | None:
    row = query_one("SELECT id FROM students WHERE user_id = ?", (user_id,))
    return row["id"] if row else None


def guardian_id_for_user(user_id: int) -> int | None:
    row = query_one("SELECT id FROM guardians WHERE user_id = ?", (user_id,))
    return row["id"] if row else None


def assert_assignment_owner(user: dict, assignment_id: int) -> dict:
    """Devuelve la asignacion si pertenece al profesor; si no, lanza error.

    El administrador puede consultar cualquier asignacion.
    """
    assignment = query_one(
        """
        SELECT ta.id, ta.teacher_id, ta.subject_id, ta.group_id,
               ta.academic_year_id,
               s.name  AS subject_name,
               g.name  AS group_name,
               ay.name AS year_name,
               u.full_name AS teacher_name
        FROM teaching_assignments ta
        JOIN subjects       s  ON s.id  = ta.subject_id
        JOIN student_groups g  ON g.id  = ta.group_id
        JOIN academic_years ay ON ay.id = ta.academic_year_id
        JOIN teachers       t  ON t.id  = ta.teacher_id
        JOIN users          u  ON u.id  = t.user_id
        WHERE ta.id = ?
        """,
        (assignment_id,),
    )
    if assignment is None:
        raise PermissionError_("La asignacion no existe.")
    if user["role"] == "admin":
        return assignment
    teacher_id = teacher_id_for_user(user["id"])
    if teacher_id is None or assignment["teacher_id"] != teacher_id:
        raise PermissionError_("Esta asignacion no te pertenece.")
    return assignment


def assert_activity_owner(user: dict, activity_id: int) -> dict:
    activity = query_one(
        """
        SELECT a.*, ta.teacher_id, ta.group_id, ta.subject_id
        FROM activities a
        JOIN teaching_assignments ta ON ta.id = a.assignment_id
        WHERE a.id = ?
        """,
        (activity_id,),
    )
    if activity is None:
        raise PermissionError_("La actividad no existe.")
    if user["role"] == "admin":
        return activity
    teacher_id = teacher_id_for_user(user["id"])
    if teacher_id is None or activity["teacher_id"] != teacher_id:
        raise PermissionError_("Esta actividad no te pertenece.")
    return activity


def assert_grade_owner(user: dict, grade_id: int) -> dict:
    grade = query_one(
        """
        SELECT gr.*, a.assignment_id, ta.teacher_id
        FROM grades gr
        JOIN activities a             ON a.id  = gr.activity_id
        JOIN teaching_assignments ta  ON ta.id = a.assignment_id
        WHERE gr.id = ?
        """,
        (grade_id,),
    )
    if grade is None:
        raise PermissionError_("La calificacion no existe.")
    if user["role"] == "admin":
        return grade
    teacher_id = teacher_id_for_user(user["id"])
    if teacher_id is None or grade["teacher_id"] != teacher_id:
        raise PermissionError_("Esta calificacion no te pertenece.")
    return grade


def assert_can_view_student(user: dict, student_id: int) -> None:
    """Un acudiente solo ve a los estudiantes asociados a el."""
    if user["role"] == "admin":
        return
    if user["role"] == "student":
        if student_id_for_user(user["id"]) != student_id:
            raise PermissionError_("Solo puedes consultar tu propia informacion.")
        return
    if user["role"] == "family":
        guardian_id = guardian_id_for_user(user["id"])
        link = query_one(
            "SELECT 1 AS ok FROM guardian_student "
            "WHERE guardian_id = ? AND student_id = ?",
            (guardian_id, student_id),
        )
        if link is None:
            raise PermissionError_("Este estudiante no esta asociado a tu cuenta.")
        return
    if user["role"] == "teacher":
        teacher_id = teacher_id_for_user(user["id"])
        link = query_one(
            """
            SELECT 1 AS ok
            FROM students s
            JOIN teaching_assignments ta ON ta.group_id = s.group_id
            WHERE s.id = ? AND ta.teacher_id = ?
            """,
            (student_id, teacher_id),
        )
        if link is None:
            raise PermissionError_("Este estudiante no esta en tus grupos.")
        return
    raise PermissionError_("No tienes permiso para consultar este estudiante.")
