"""Panel del profesor: asignaciones, cuaderno de notas, Excel, revisiones."""
from flask import (Blueprint, jsonify, render_template, request, send_file,
                   url_for)

from core.security import current_user, role_required
from services import (academic_service, activity_service, audit_service,
                      authorization, excel_service, feedback_service,
                      grade_service, report_service, review_service)

teacher_bp = Blueprint("teacher", __name__, url_prefix="/profesor")


def _teacher_id() -> int | None:
    return authorization.teacher_id_for_user(current_user()["id"])


def _resolve_period(assignment: dict):
    periods = academic_service.list_periods(assignment["academic_year_id"])
    requested = request.args.get("periodo", type=int)
    selected = next((p for p in periods if p["id"] == requested), None)
    if selected is None:
        selected = academic_service.active_period(assignment["academic_year_id"])
    return periods, selected


def _payload() -> dict:
    return request.get_json(silent=True) or {}


@teacher_bp.route("/")
@role_required("teacher")
def dashboard():
    user = current_user()
    teacher_id = _teacher_id()
    year = academic_service.active_year()
    assignments = academic_service.list_assignments(
        teacher_id=teacher_id, year_id=year["id"] if year else None
    )
    period = academic_service.active_period(year["id"]) if year else None

    for assignment in assignments:
        if period:
            book = grade_service.gradebook(assignment["id"], period["id"])
            assignment["activity_count"] = len(book["activities"])
            assignment["draft_count"] = book["draft_count"]
            assignment["total_weight"] = book["total_weight"]
        else:
            assignment["activity_count"] = 0
            assignment["draft_count"] = 0
            assignment["total_weight"] = 0

    return render_template(
        "teacher/dashboard.html",
        assignments=assignments,
        year=year,
        period=period,
        pending_reviews=review_service.pending_count(teacher_id),
        user=user,
    )


@teacher_bp.route("/asignacion/<int:assignment_id>")
@role_required("teacher", "admin")
def gradebook(assignment_id: int):
    user = current_user()
    assignment = authorization.assert_assignment_owner(user, assignment_id)
    periods, period = _resolve_period(assignment)
    if period is None:
        return render_template("teacher/gradebook.html", assignment=assignment,
                               periods=periods, period=None, book=None,
                               activities=[])

    book = grade_service.gradebook(assignment_id, period["id"])
    return render_template(
        "teacher/gradebook.html",
        assignment=assignment,
        periods=periods,
        period=period,
        book=book,
        activities=book["activities"],
        kinds=activity_service.KINDS,
        categories=grade_service.FEEDBACK_CATEGORIES,
        templates=feedback_service.list_templates(_teacher_id()),
        export_url=url_for("teacher.export_excel", assignment_id=assignment_id,
                           periodo=period["id"]),
    )


# ------------------------------------------------------------- ACTIVIDADES ---
@teacher_bp.route("/asignacion/<int:assignment_id>/actividades", methods=["POST"])
@role_required("teacher", "admin")
def create_activity(assignment_id: int):
    user = current_user()
    authorization.assert_assignment_owner(user, assignment_id)
    data = _payload()
    try:
        activity_id = activity_service.create_activity(
            assignment_id,
            int(data.get("period_id")),
            data.get("name", ""),
            data.get("kind", "taller"),
            data.get("weight", 10),
            data.get("due_date"),
            bool(data.get("allows_recovery")),
        )
    except (activity_service.ValidationError, TypeError, ValueError) as error:
        return jsonify({"ok": False, "message": str(error)}), 400
    audit_service.log(user, "Creo actividad", "actividad", activity_id,
                      data.get("name"))
    return jsonify({"ok": True, "id": activity_id})


@teacher_bp.route("/actividades/<int:activity_id>", methods=["POST"])
@role_required("teacher", "admin")
def update_activity(activity_id: int):
    user = current_user()
    activity = authorization.assert_activity_owner(user, activity_id)
    data = _payload()
    try:
        activity_service.update_activity(
            activity_id,
            data.get("name", activity["name"]),
            data.get("kind", activity["kind"]),
            data.get("weight", activity["weight"]),
            data.get("due_date", activity["due_date"]),
            bool(data.get("allows_recovery", activity["allows_recovery"])),
        )
    except activity_service.ValidationError as error:
        return jsonify({"ok": False, "message": str(error)}), 400
    audit_service.log(user, "Modifico actividad", "actividad", activity_id,
                      data.get("name", activity["name"]))
    return jsonify({"ok": True})


@teacher_bp.route("/actividades/<int:activity_id>/eliminar", methods=["POST"])
@role_required("teacher", "admin")
def delete_activity(activity_id: int):
    user = current_user()
    activity = authorization.assert_activity_owner(user, activity_id)
    activity_service.delete_activity(activity_id)
    audit_service.log(user, "Elimino actividad", "actividad", activity_id,
                      activity["name"])
    return jsonify({"ok": True})


@teacher_bp.route("/actividades/<int:activity_id>/publicar", methods=["POST"])
@role_required("teacher", "admin")
def publish_activity(activity_id: int):
    user = current_user()
    authorization.assert_activity_owner(user, activity_id)
    count = grade_service.publish_activity(activity_id, user)
    return jsonify({"ok": True, "publicadas": count})


# ------------------------------------------------------------------ NOTAS ---
@teacher_bp.route("/api/notas", methods=["POST"])
@role_required("teacher", "admin")
def save_grade():
    user = current_user()
    data = _payload()
    try:
        activity_id = int(data["activity_id"])
        student_id = int(data["student_id"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"ok": False, "message": "Parametros incompletos."}), 400

    authorization.assert_activity_owner(user, activity_id)
    authorization.assert_can_view_student(user, student_id)
    try:
        grade = grade_service.save_grade(
            activity_id, student_id, data.get("score"), user,
            feedback_category=data.get("feedback_category"),
            feedback_text=data.get("feedback_text"),
            is_missing=data.get("is_missing"),
            recovery_status=data.get("recovery_status"),
        )
    except grade_service.ValidationError as error:
        return jsonify({"ok": False, "message": str(error)}), 400

    activity = activity_service.get_activity(activity_id)
    rows = grade_service.student_scores(
        student_id, activity["assignment_id"], activity["period_id"]
    )
    return jsonify({
        "ok": True,
        "grade_id": grade["id"],
        "status": grade["status"],
        "promedio": grade_service.weighted_average(rows),
    })


@teacher_bp.route("/api/sugerencia", methods=["POST"])
@role_required("teacher", "admin")
def suggestion():
    """Sugerencia de retroalimentacion asistida (simulada, nunca automatica)."""
    user = current_user()
    data = _payload()
    activity_id = int(data.get("activity_id", 0))
    student_id = int(data.get("student_id", 0))
    authorization.assert_activity_owner(user, activity_id)
    activity = activity_service.get_activity(activity_id)
    student = academic_service.get_student(student_id)
    if activity is None or student is None:
        return jsonify({"ok": False, "message": "Datos incompletos."}), 400

    rows = grade_service.student_scores(
        student_id, activity["assignment_id"], activity["period_id"]
    )
    current = next((r for r in rows if r["activity_id"] == activity_id), None)
    pending = sum(1 for r in rows if r["score"] is None)
    texto = feedback_service.suggest(
        student["full_name"], activity["name"],
        current["score"] if current else None,
        grade_service.weighted_average(rows), pending,
    )
    return jsonify({"ok": True, "sugerencia": texto})


# ------------------------------------------------------------ PUBLICACION ---
@teacher_bp.route("/asignacion/<int:assignment_id>/publicar", methods=["POST"])
@role_required("teacher", "admin")
def publish_period(assignment_id: int):
    user = current_user()
    assignment = authorization.assert_assignment_owner(user, assignment_id)
    data = _payload()
    period_id = int(data.get("period_id") or 0)
    if not period_id:
        return jsonify({"ok": False, "message": "Periodo requerido."}), 400

    report_id = data.get("report_id")
    if report_id:
        report = report_service.get_report(int(report_id))
    else:
        report = report_service.open_report_for_period(
            period_id, assignment["academic_year_id"], user
        )
    if report is None:
        return jsonify({"ok": False, "message": "Preinforme no encontrado."}), 400

    count = grade_service.publish_assignment_period(
        assignment_id, period_id, report["id"], user
    )
    if report["status"] != "publicado":
        report_service.publish_report(report["id"], user)
    return jsonify({
        "ok": True,
        "publicadas": count,
        "preinforme": report["name"],
    })


# ----------------------------------------------------------------- EXCEL ---
@teacher_bp.route("/asignacion/<int:assignment_id>/exportar")
@role_required("teacher", "admin")
def export_excel(assignment_id: int):
    user = current_user()
    assignment = authorization.assert_assignment_owner(user, assignment_id)
    _periods, period = _resolve_period(assignment)
    if period is None:
        return jsonify({"ok": False, "message": "No hay periodos definidos."}), 400

    buffer = excel_service.export_gradebook(assignment, period)
    audit_service.log(user, "Exporto notas a Excel", "asignacion", assignment_id,
                      f"{assignment['subject_name']} - {assignment['group_name']} - "
                      f"{period['name']}")
    return send_file(
        buffer,
        as_attachment=True,
        download_name=excel_service.build_filename(assignment, period),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@teacher_bp.route("/asignacion/<int:assignment_id>/importar/previsualizar",
                  methods=["POST"])
@role_required("teacher", "admin")
def import_preview(assignment_id: int):
    user = current_user()
    authorization.assert_assignment_owner(user, assignment_id)
    period_id = request.form.get("period_id", type=int)
    uploaded = request.files.get("archivo")
    if uploaded is None or not uploaded.filename:
        return jsonify({"ok": False, "message": "Selecciona un archivo."}), 400
    if not uploaded.filename.lower().endswith((".xlsx", ".xlsm")):
        return jsonify({"ok": False, "message": "El archivo debe ser .xlsx."}), 400
    if not period_id:
        return jsonify({"ok": False, "message": "Periodo requerido."}), 400

    try:
        preview = excel_service.preview_import(uploaded.stream, assignment_id,
                                               period_id)
    except excel_service.ImportError_ as error:
        return jsonify({"ok": False, "message": str(error)}), 400
    return jsonify({"ok": True, **preview})


@teacher_bp.route("/asignacion/<int:assignment_id>/importar/confirmar",
                  methods=["POST"])
@role_required("teacher", "admin")
def import_confirm(assignment_id: int):
    user = current_user()
    authorization.assert_assignment_owner(user, assignment_id)
    data = _payload()
    changes = data.get("cambios") or []
    period_id = int(data.get("period_id") or 0)
    if not changes:
        return jsonify({"ok": False, "message": "No hay cambios que aplicar."}), 400
    try:
        applied = excel_service.apply_import(changes, assignment_id, period_id, user)
    except (excel_service.ImportError_, grade_service.ValidationError) as error:
        return jsonify({"ok": False, "message": str(error)}), 400
    return jsonify({"ok": True, "aplicados": applied})


# ----------------------------------------------------------- SOLICITUDES ---
@teacher_bp.route("/solicitudes")
@role_required("teacher")
def reviews():
    teacher_id = _teacher_id()
    return render_template(
        "teacher/reviews.html",
        requests=review_service.list_for_teacher(teacher_id),
        user=current_user(),
    )


@teacher_bp.route("/solicitudes/<int:request_id>/responder", methods=["POST"])
@role_required("teacher")
def respond_review(request_id: int):
    user = current_user()
    solicitud = review_service.get_request(request_id)
    if solicitud is None or solicitud["teacher_id"] != _teacher_id():
        return jsonify({"ok": False, "message": "Solicitud no encontrada."}), 404
    data = _payload()
    try:
        updated = review_service.respond(
            request_id, user,
            data.get("status", "revisada"),
            data.get("response", ""),
            data.get("new_score"),
        )
    except (review_service.ValidationError, grade_service.ValidationError) as error:
        return jsonify({"ok": False, "message": str(error)}), 400
    return jsonify({"ok": True, "estado": updated["status"],
                    "nota": updated["score"]})


# -------------------------------------------------------------- HISTORIAL ---
@teacher_bp.route("/historial")
@role_required("teacher")
def history():
    user = current_user()
    return render_template(
        "teacher/history.html",
        entries=audit_service.list_entries(limit=200, user_id=user["id"]),
        user=user,
    )
