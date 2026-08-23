"""Panel de la familia o acudiente.

La experiencia se orienta a acompanar, no a sancionar: estado, motivos y
una recomendacion concreta de que conversar.
"""
from flask import Blueprint, render_template, request

from core.security import PermissionError_, current_user, role_required
from services import (academic_service, alert_service, authorization,
                      grade_service, report_service)

family_bp = Blueprint("family", __name__, url_prefix="/familia")


def _guardian_id() -> int:
    guardian_id = authorization.guardian_id_for_user(current_user()["id"])
    if guardian_id is None:
        raise PermissionError_("Tu usuario no esta asociado a un acudiente.")
    return guardian_id


@family_bp.route("/")
@role_required("family")
def dashboard():
    children = academic_service.students_of_guardian(_guardian_id())
    resumen = []
    for child in children:
        period = (academic_service.active_period(child["academic_year_id"])
                  if child["academic_year_id"] else None)
        summaries = []
        if period and child.get("group_name"):
            student = academic_service.get_student(child["id"])
            summaries = grade_service.student_overview(
                student["id"], student["group_id"], period["id"], only_visible=True
            )
        atencion = [s for s in summaries
                    if s["estado"] in ("requiere_atencion", "critico")]
        resumen.append({
            "student": child,
            "period": period,
            "promedio": grade_service.global_average(summaries),
            "asignaturas": len(summaries),
            "atencion": atencion,
            "pendientes": sum(s["pending"] for s in summaries),
        })
    return render_template("family/dashboard.html", resumen=resumen,
                           user=current_user())


@family_bp.route("/estudiante/<int:student_id>")
@role_required("family")
def student_detail(student_id: int):
    user = current_user()
    authorization.assert_can_view_student(user, student_id)
    student = academic_service.get_student(student_id)
    year_id = student["academic_year_id"]
    periods = academic_service.list_periods(year_id) if year_id else []
    requested = request.args.get("periodo", type=int)
    period = next((p for p in periods if p["id"] == requested), None)
    if period is None and year_id:
        period = academic_service.active_period(year_id)

    summaries = []
    if period and student["group_id"]:
        summaries = grade_service.student_overview(
            student["id"], student["group_id"], period["id"], only_visible=True
        )
    for summary in summaries:
        summary["recomendacion"] = alert_service.recommendation(summary["estado"])

    return render_template(
        "family/student.html",
        student=student,
        periods=periods,
        period=period,
        summaries=summaries,
        promedio_general=grade_service.global_average(summaries),
        atencion=[s for s in summaries
                  if s["estado"] in ("requiere_atencion", "critico")],
        reports=report_service.reports_for_student(student["id"]),
        user=user,
    )
