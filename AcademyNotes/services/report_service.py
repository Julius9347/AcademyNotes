"""Preinformes: el mecanismo de publicacion del prototipo.

Un preinforme agrupa lo que se hace visible a estudiantes y familias en
un momento concreto del periodo. Registrar no es publicar.
"""
from core.db import execute, query_all, query_one
from services import audit_service


def list_reports(year_id: int | None = None, period_id: int | None = None,
                 status: str | None = None) -> list[dict]:
    sql = """
        SELECT r.*, p.name AS period_name, ay.name AS year_name,
               (SELECT COUNT(*) FROM grades gr WHERE gr.published_report_id = r.id)
                   AS grade_count
        FROM reports r
        JOIN academic_periods p ON p.id = r.period_id
        JOIN academic_years ay  ON ay.id = r.academic_year_id
        WHERE 1=1
    """
    params: list = []
    if year_id:
        sql += " AND r.academic_year_id = ?"
        params.append(year_id)
    if period_id:
        sql += " AND r.period_id = ?"
        params.append(period_id)
    if status:
        sql += " AND r.status = ?"
        params.append(status)
    sql += " ORDER BY p.sequence, r.id"
    return query_all(sql, params)


def get_report(report_id: int) -> dict | None:
    return query_one(
        """
        SELECT r.*, p.name AS period_name, ay.name AS year_name
        FROM reports r
        JOIN academic_periods p ON p.id = r.period_id
        JOIN academic_years ay  ON ay.id = r.academic_year_id
        WHERE r.id = ?
        """,
        (report_id,),
    )


def create_report(year_id: int, period_id: int, name: str, kind: str,
                  report_date: str | None, user: dict) -> int:
    report_id = execute(
        """
        INSERT INTO reports
            (academic_year_id, period_id, name, kind, report_date, created_by)
        VALUES (?,?,?,?,?,?)
        """,
        (year_id, period_id, name.strip(), kind, report_date or None, user["id"]),
    )
    audit_service.log(user, "Creo preinforme", "preinforme", report_id, name)
    return report_id


def publish_report(report_id: int, user: dict) -> dict | None:
    execute(
        "UPDATE reports SET status = 'publicado', "
        "published_at = datetime('now','localtime') WHERE id = ?",
        (report_id,),
    )
    report = get_report(report_id)
    audit_service.log(
        user, "Publico preinforme", "preinforme", report_id,
        report["name"] if report else "", "borrador", "publicado",
    )
    return report


def open_report_for_period(period_id: int, year_id: int, user: dict) -> dict:
    """Devuelve el preinforme en borrador del periodo; si no hay, lo crea.

    Permite que el profesor publique en un solo paso durante una
    demostracion sin depender de que el administrador lo prepare antes.
    """
    report = query_one(
        "SELECT * FROM reports WHERE period_id = ? AND status = 'borrador' "
        "ORDER BY id LIMIT 1",
        (period_id,),
    )
    if report is not None:
        return report
    period = query_one("SELECT name FROM academic_periods WHERE id = ?", (period_id,))
    name = f"Preinforme {period['name']}" if period else "Preinforme"
    report_id = create_report(year_id, period_id, name, "preinforme", None, user)
    return get_report(report_id)


def reports_for_student(student_id: int) -> list[dict]:
    """Preinformes publicados que corresponden al anio del estudiante."""
    return query_all(
        """
        SELECT r.*, p.name AS period_name
        FROM reports r
        JOIN academic_periods p ON p.id = r.period_id
        JOIN student_groups g   ON g.academic_year_id = r.academic_year_id
        JOIN students s         ON s.group_id = g.id
        WHERE s.id = ? AND r.status = 'publicado'
        ORDER BY p.sequence, r.id
        """,
        (student_id,),
    )
