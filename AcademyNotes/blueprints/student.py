"""Panel del estudiante: progreso, actividades, alertas y revisiones."""
from flask import Blueprint, jsonify, render_template, request

from core.security import PermissionError_, current_user, role_required
from services import (academic_service, authorization, grade_service,
                      report_service, review_service)

student_bp = Blueprint("student", __name__, url_prefix="/estudiante")


def _student() -> dict:
    student_id = authorization.student_id_for_user(current_user()["id"])
    if student_id is None:
        raise PermissionError_("Tu usuario no esta asociado a un estudiante.")
    return academic_service.get_student(student_id)


def _period(student: dict):
    year_id = student["academic_year_id"]
    periods = academic_service.list_periods(year_id) if year_id else []
    requested = request.args.get("periodo", type=int)
    selected = next((p for p in periods if p["id"] == requested), None)
    if selected is None and year_id:
        selected = academic_service.active_period(year_id)
    return periods, selected


@student_bp.route("/")
@role_required("student")
def dashboard():
    student = _student()
    periods, period = _period(student)
    summaries = []
    if period and student["group_id"]:
        summaries = grade_service.student_overview(
            student["id"], student["group_id"], period["id"], only_visible=True
        )
    return render_template(
        "student/dashboard.html",
        student=student,
        periods=periods,
        period=period,
        summaries=summaries,
        promedio_general=grade_service.global_average(summaries),
        atencion=[s for s in summaries
                  if s["estado"] in ("requiere_atencion", "critico")],
        reports=report_service.reports_for_student(student["id"]),
        last_update=grade_service.last_update_for_student(student["id"]),
        user=current_user(),
    )


@student_bp.route("/asignatura/<int:assignment_id>")
@role_required("student")
def subject_detail(assignment_id: int):
    student = _student()
    periods, period = _period(student)
    assignment = next(
        (a for a in academic_service.assignments_for_group(student["group_id"])
         if a["id"] == assignment_id),
        None,
    )
    if assignment is None:
        raise PermissionError_("Esta asignatura no corresponde a tu grupo.")

    summary = grade_service.subject_summary(
        student["id"], assignment, period["id"], only_visible=True
    ) if period else None

    return render_template(
        "student/subject.html",
        student=student,
        assignment=assignment,
        periods=periods,
        period=period,
        summary=summary,
        motivos_guia=review_service.GUIDELINES,
        motivos=review_service.REASONS,
        user=current_user(),
    )


@student_bp.route("/api/actualizaciones")
@role_required("student")
def updates():
    """Sondeo moderado: el dashboard pregunta si hay informacion nueva."""
    student = _student()
    return jsonify({
        "ok": True,
        "last_update": grade_service.last_update_for_student(student["id"]),
    })


@student_bp.route("/solicitudes")
@role_required("student")
def reviews():
    student = _student()
    return render_template(
        "student/reviews.html",
        student=student,
        requests=review_service.list_for_student(student["id"]),
        user=current_user(),
    )


@student_bp.route("/api/solicitudes", methods=["POST"])
@role_required("student")
def create_review():
    student = _student()
    data = request.get_json(silent=True) or {}
    try:
        request_id = review_service.create_request(
            int(data.get("grade_id") or 0),
            student["id"],
            data.get("reason_code", ""),
            data.get("message", ""),
            current_user(),
        )
    except (review_service.ValidationError, TypeError, ValueError) as error:
        return jsonify({"ok": False, "message": str(error)}), 400
    return jsonify({"ok": True, "id": request_id})
