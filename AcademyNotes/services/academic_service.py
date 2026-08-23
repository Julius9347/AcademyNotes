"""Estructura academica: anios, periodos, grupos, asignaturas, personas
y asignaciones docentes.
"""
from typing import Any

from core.db import execute, query_all, query_one
from core.security import hash_password


# --------------------------------------------------------------- ANIOS ---
def active_year() -> dict | None:
    return query_one(
        "SELECT * FROM academic_years WHERE is_active = 1 ORDER BY id DESC LIMIT 1"
    ) or query_one("SELECT * FROM academic_years ORDER BY id DESC LIMIT 1")


def list_years() -> list[dict]:
    return query_all("SELECT * FROM academic_years ORDER BY name DESC")


def add_year(name: str, is_active: bool = False) -> int:
    year_id = execute(
        "INSERT INTO academic_years (name, is_active) VALUES (?, ?)",
        (name, 1 if is_active else 0),
    )
    if is_active:
        execute("UPDATE academic_years SET is_active = 0 WHERE id <> ?", (year_id,))
    return year_id


# ------------------------------------------------------------ PERIODOS ---
def list_periods(year_id: int) -> list[dict]:
    """Un anio puede tener 3 o 4 periodos: nunca se asume la cantidad."""
    return query_all(
        "SELECT * FROM academic_periods WHERE academic_year_id = ? ORDER BY sequence",
        (year_id,),
    )


def active_period(year_id: int) -> dict | None:
    return query_one(
        "SELECT * FROM academic_periods WHERE academic_year_id = ? AND is_active = 1 "
        "ORDER BY sequence LIMIT 1",
        (year_id,),
    ) or query_one(
        "SELECT * FROM academic_periods WHERE academic_year_id = ? ORDER BY sequence LIMIT 1",
        (year_id,),
    )


def get_period(period_id: int) -> dict | None:
    return query_one("SELECT * FROM academic_periods WHERE id = ?", (period_id,))


def add_period(
    year_id: int, name: str, sequence: int,
    start_date: str | None = None, end_date: str | None = None,
    is_active: bool = False,
) -> int:
    period_id = execute(
        """
        INSERT INTO academic_periods
            (academic_year_id, name, sequence, start_date, end_date, is_active)
        VALUES (?,?,?,?,?,?)
        """,
        (year_id, name, sequence, start_date, end_date, 1 if is_active else 0),
    )
    if is_active:
        execute(
            "UPDATE academic_periods SET is_active = 0 "
            "WHERE academic_year_id = ? AND id <> ?",
            (year_id, period_id),
        )
    return period_id


def set_active_period(period_id: int) -> None:
    period = get_period(period_id)
    if period is None:
        return
    execute(
        "UPDATE academic_periods SET is_active = 0 WHERE academic_year_id = ?",
        (period["academic_year_id"],),
    )
    execute("UPDATE academic_periods SET is_active = 1 WHERE id = ?", (period_id,))


# -------------------------------------------------------------- GRUPOS ---
def list_groups(year_id: int | None = None) -> list[dict]:
    sql = """
        SELECT g.*, ay.name AS year_name,
               (SELECT COUNT(*) FROM students s WHERE s.group_id = g.id) AS student_count
        FROM student_groups g
        JOIN academic_years ay ON ay.id = g.academic_year_id
    """
    params: list[Any] = []
    if year_id:
        sql += " WHERE g.academic_year_id = ?"
        params.append(year_id)
    sql += " ORDER BY g.name"
    return query_all(sql, params)


def add_group(name: str, year_id: int) -> int:
    return execute(
        "INSERT INTO student_groups (name, academic_year_id) VALUES (?, ?)",
        (name, year_id),
    )


# --------------------------------------------------------- ASIGNATURAS ---
def list_subjects() -> list[dict]:
    return query_all("SELECT * FROM subjects ORDER BY name")


def add_subject(name: str) -> int:
    return execute("INSERT INTO subjects (name) VALUES (?)", (name,))


# ------------------------------------------------------------ PERSONAS ---
def create_user(
    username: str, raw_password: str, full_name: str, role: str,
    email: str | None = None,
) -> int:
    return execute(
        """
        INSERT INTO users (username, password_hash, full_name, role, email)
        VALUES (?,?,?,?,?)
        """,
        (username, hash_password(raw_password), full_name, role, email),
    )


def create_teacher(username: str, password: str, full_name: str,
                   email: str | None = None) -> int:
    user_id = create_user(username, password, full_name, "teacher", email)
    return execute("INSERT INTO teachers (user_id) VALUES (?)", (user_id,))


def create_student(username: str, password: str, full_name: str,
                   student_code: str, group_id: int | None,
                   email: str | None = None) -> int:
    user_id = create_user(username, password, full_name, "student", email)
    return execute(
        "INSERT INTO students (user_id, student_code, group_id) VALUES (?,?,?)",
        (user_id, student_code, group_id),
    )


def create_guardian(username: str, password: str, full_name: str,
                    relationship: str = "Acudiente",
                    email: str | None = None) -> int:
    user_id = create_user(username, password, full_name, "family", email)
    return execute(
        "INSERT INTO guardians (user_id, relationship) VALUES (?,?)",
        (user_id, relationship),
    )


def link_guardian_student(guardian_id: int, student_id: int) -> None:
    execute(
        "INSERT OR IGNORE INTO guardian_student (guardian_id, student_id) VALUES (?,?)",
        (guardian_id, student_id),
    )


def list_users(role: str | None = None) -> list[dict]:
    sql = """
        SELECT u.id, u.username, u.full_name, u.role, u.email, u.is_active,
               u.created_at,
               s.student_code, g.name AS group_name
        FROM users u
        LEFT JOIN students s      ON s.user_id = u.id
        LEFT JOIN student_groups g ON g.id = s.group_id
    """
    params: list[Any] = []
    if role:
        sql += " WHERE u.role = ?"
        params.append(role)
    sql += " ORDER BY u.role, u.full_name"
    return query_all(sql, params)


def list_teachers() -> list[dict]:
    return query_all(
        """
        SELECT t.id, t.user_id, u.full_name, u.username
        FROM teachers t JOIN users u ON u.id = t.user_id
        ORDER BY u.full_name
        """
    )


def list_students(group_id: int | None = None) -> list[dict]:
    sql = """
        SELECT s.id, s.student_code, s.group_id, u.full_name, u.username,
               g.name AS group_name
        FROM students s
        JOIN users u ON u.id = s.user_id
        LEFT JOIN student_groups g ON g.id = s.group_id
    """
    params: list[Any] = []
    if group_id:
        sql += " WHERE s.group_id = ?"
        params.append(group_id)
    sql += " ORDER BY u.full_name"
    return query_all(sql, params)


def get_student(student_id: int) -> dict | None:
    return query_one(
        """
        SELECT s.id, s.student_code, s.group_id, u.full_name, u.id AS user_id,
               g.name AS group_name, g.academic_year_id
        FROM students s
        JOIN users u ON u.id = s.user_id
        LEFT JOIN student_groups g ON g.id = s.group_id
        WHERE s.id = ?
        """,
        (student_id,),
    )


def students_of_guardian(guardian_id: int) -> list[dict]:
    return query_all(
        """
        SELECT s.id, s.student_code, u.full_name, g.name AS group_name,
               g.academic_year_id
        FROM guardian_student gs
        JOIN students s            ON s.id = gs.student_id
        JOIN users u               ON u.id = s.user_id
        LEFT JOIN student_groups g ON g.id = s.group_id
        WHERE gs.guardian_id = ?
        ORDER BY u.full_name
        """,
        (guardian_id,),
    )


# ------------------------------------------------- ASIGNACIONES DOCENTES ---
def add_assignment(teacher_id: int, subject_id: int, group_id: int,
                   year_id: int) -> int:
    return execute(
        """
        INSERT OR IGNORE INTO teaching_assignments
            (teacher_id, subject_id, group_id, academic_year_id)
        VALUES (?,?,?,?)
        """,
        (teacher_id, subject_id, group_id, year_id),
    )


def list_assignments(teacher_id: int | None = None,
                     year_id: int | None = None) -> list[dict]:
    sql = """
        SELECT ta.id, ta.teacher_id, ta.subject_id, ta.group_id,
               ta.academic_year_id,
               s.name  AS subject_name,
               g.name  AS group_name,
               ay.name AS year_name,
               u.full_name AS teacher_name,
               (SELECT COUNT(*) FROM students st WHERE st.group_id = ta.group_id)
                   AS student_count
        FROM teaching_assignments ta
        JOIN subjects       s  ON s.id  = ta.subject_id
        JOIN student_groups g  ON g.id  = ta.group_id
        JOIN academic_years ay ON ay.id = ta.academic_year_id
        JOIN teachers       t  ON t.id  = ta.teacher_id
        JOIN users          u  ON u.id  = t.user_id
        WHERE 1=1
    """
    params: list[Any] = []
    if teacher_id:
        sql += " AND ta.teacher_id = ?"
        params.append(teacher_id)
    if year_id:
        sql += " AND ta.academic_year_id = ?"
        params.append(year_id)
    sql += " ORDER BY g.name, s.name"
    return query_all(sql, params)


def assignments_for_group(group_id: int) -> list[dict]:
    """Asignaturas que recibe un grupo, con su profesor."""
    return query_all(
        """
        SELECT ta.id, ta.subject_id, ta.teacher_id,
               s.name AS subject_name, u.full_name AS teacher_name
        FROM teaching_assignments ta
        JOIN subjects s ON s.id = ta.subject_id
        JOIN teachers t ON t.id = ta.teacher_id
        JOIN users    u ON u.id = t.user_id
        WHERE ta.group_id = ?
        ORDER BY s.name
        """,
        (group_id,),
    )
