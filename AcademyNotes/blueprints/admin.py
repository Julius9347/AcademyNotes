"""Panel del administrador: configuracion academica, publicacion,
historial y respaldos.

En v0.1 existe un unico tipo de administrador.
"""
import sqlite3

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)

from core.db import scalar
from core.security import current_user, role_required
from services import (academic_service, audit_service, backup_service,
                      report_service, settings_service)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _form(name: str, default: str = "") -> str:
    return (request.form.get(name) or default).strip()


@admin_bp.route("/")
@role_required("admin")
def dashboard():
    year = academic_service.active_year()
    period = academic_service.active_period(year["id"]) if year else None
    metrics = {
        "estudiantes": scalar("SELECT COUNT(*) FROM students") or 0,
        "profesores": scalar("SELECT COUNT(*) FROM teachers") or 0,
        "acudientes": scalar("SELECT COUNT(*) FROM guardians") or 0,
        "grupos": scalar("SELECT COUNT(*) FROM student_groups") or 0,
        "asignaturas": scalar("SELECT COUNT(*) FROM subjects") or 0,
        "actividades": scalar("SELECT COUNT(*) FROM activities") or 0,
        "notas": scalar("SELECT COUNT(*) FROM grades WHERE score IS NOT NULL") or 0,
        "borradores": scalar(
            "SELECT COUNT(*) FROM grades WHERE status = 'borrador' "
            "AND score IS NOT NULL") or 0,
        "solicitudes": scalar(
            "SELECT COUNT(*) FROM review_requests WHERE status = 'pendiente'") or 0,
    }
    return render_template(
        "admin/dashboard.html",
        year=year, period=period, metrics=metrics,
        reporte_activo=settings_service.reporte_activo(),
        entries=audit_service.list_entries(limit=8),
        user=current_user(),
    )


# --------------------------------------------------------------- USUARIOS ---
@admin_bp.route("/usuarios", methods=["GET", "POST"])
@role_required("admin")
def users():
    year = academic_service.active_year()
    if request.method == "POST":
        role = _form("role", "student")
        username = _form("username")
        password = _form("password")
        full_name = _form("full_name")
        try:
            if not username or not password or not full_name:
                raise ValueError("Usuario, nombre y contrasena son obligatorios.")
            if role == "teacher":
                academic_service.create_teacher(username, password, full_name,
                                                _form("email") or None)
            elif role == "student":
                group_id = request.form.get("group_id", type=int)
                code = _form("student_code") or username.upper()
                academic_service.create_student(username, password, full_name,
                                                code, group_id,
                                                _form("email") or None)
            elif role == "family":
                guardian_id = academic_service.create_guardian(
                    username, password, full_name,
                    _form("relationship", "Acudiente"), _form("email") or None)
                for student_id in request.form.getlist("student_ids", type=int):
                    academic_service.link_guardian_student(guardian_id, student_id)
            else:
                academic_service.create_user(username, password, full_name,
                                             "admin", _form("email") or None)
            audit_service.log(current_user(), "Creo usuario", "usuario", None,
                              f"{full_name} ({role})")
            flash(f"Usuario {full_name} creado correctamente.", "ok")
        except sqlite3.IntegrityError:
            flash("Ese nombre de usuario o codigo ya existe.", "error")
        except ValueError as error:
            flash(str(error), "error")
        return redirect(url_for("admin.users"))

    return render_template(
        "admin/users.html",
        users=academic_service.list_users(),
        groups=academic_service.list_groups(year["id"] if year else None),
        students=academic_service.list_students(),
        user=current_user(),
    )


# --------------------------------------------------------------- ACADEMICO ---
@admin_bp.route("/academico", methods=["GET", "POST"])
@role_required("admin")
def academic():
    year = academic_service.active_year()
    if request.method == "POST":
        accion = _form("accion")
        try:
            if accion == "anio":
                academic_service.add_year(_form("name"), True)
            elif accion == "periodo":
                academic_service.add_period(
                    request.form.get("year_id", type=int) or year["id"],
                    _form("name"),
                    request.form.get("sequence", type=int) or 1,
                    _form("start_date") or None,
                    _form("end_date") or None,
                    bool(request.form.get("is_active")),
                )
            elif accion == "periodo_activo":
                academic_service.set_active_period(
                    request.form.get("period_id", type=int))
            elif accion == "grupo":
                academic_service.add_group(
                    _form("name"),
                    request.form.get("year_id", type=int) or year["id"])
            elif accion == "asignatura":
                academic_service.add_subject(_form("name"))
            audit_service.log(current_user(), f"Configuro {accion}", "academico")
            flash("Configuracion academica actualizada.", "ok")
        except sqlite3.IntegrityError:
            flash("Ese registro ya existe.", "error")
        except (TypeError, ValueError) as error:
            flash(f"Datos invalidos: {error}", "error")
        return redirect(url_for("admin.academic"))

    return render_template(
        "admin/academic.html",
        years=academic_service.list_years(),
        year=year,
        periods=academic_service.list_periods(year["id"]) if year else [],
        groups=academic_service.list_groups(year["id"] if year else None),
        subjects=academic_service.list_subjects(),
        user=current_user(),
    )


# ------------------------------------------------------------ ASIGNACIONES ---
@admin_bp.route("/asignaciones", methods=["GET", "POST"])
@role_required("admin")
def assignments():
    year = academic_service.active_year()
    if request.method == "POST":
        academic_service.add_assignment(
            request.form.get("teacher_id", type=int),
            request.form.get("subject_id", type=int),
            request.form.get("group_id", type=int),
            request.form.get("year_id", type=int) or year["id"],
        )
        audit_service.log(current_user(), "Creo asignacion docente", "asignacion")
        flash("Asignacion creada.", "ok")
        return redirect(url_for("admin.assignments"))

    return render_template(
        "admin/assignments.html",
        assignments=academic_service.list_assignments(
            year_id=year["id"] if year else None),
        teachers=academic_service.list_teachers(),
        subjects=academic_service.list_subjects(),
        groups=academic_service.list_groups(year["id"] if year else None),
        year=year,
        user=current_user(),
    )


# -------------------------------------------------------------- PREINFORMES ---
@admin_bp.route("/preinformes", methods=["GET", "POST"])
@role_required("admin")
def reports():
    year = academic_service.active_year()
    if request.method == "POST":
        report_service.create_report(
            year["id"],
            request.form.get("period_id", type=int),
            _form("name", "Preinforme"),
            _form("kind", "preinforme"),
            _form("report_date") or None,
            current_user(),
        )
        flash("Preinforme creado en estado borrador.", "ok")
        return redirect(url_for("admin.reports"))

    return render_template(
        "admin/reports.html",
        reports=report_service.list_reports(year_id=year["id"] if year else None),
        periods=academic_service.list_periods(year["id"]) if year else [],
        user=current_user(),
    )


@admin_bp.route("/preinformes/<int:report_id>/publicar", methods=["POST"])
@role_required("admin")
def publish_report(report_id: int):
    report_service.publish_report(report_id, current_user())
    flash("Preinforme publicado. Ya es visible para estudiantes y familias.", "ok")
    return redirect(url_for("admin.reports"))


# ------------------------------------------------------------------ AJUSTES ---
@admin_bp.route("/ajustes", methods=["GET", "POST"])
@role_required("admin")
def settings():
    if request.method == "POST":
        activo = "1" if request.form.get("reporte_activo") else "0"
        anterior = settings_service.get("reporte_activo")
        settings_service.set_value("reporte_activo", activo)
        settings_service.set_value("institucion",
                                   _form("institucion", "Institucion Educativa Demo"))
        audit_service.log(current_user(), "Cambio configuracion", "ajustes", None,
                          "Modo reporte activo", anterior, activo)
        flash("Configuracion guardada.", "ok")
        return redirect(url_for("admin.settings"))

    return render_template(
        "admin/settings.html",
        settings=settings_service.all_settings(),
        reporte_activo=settings_service.reporte_activo(),
        user=current_user(),
    )


# ---------------------------------------------------------------- AUDITORIA ---
@admin_bp.route("/auditoria")
@role_required("admin")
def audit():
    return render_template(
        "admin/audit.html",
        entries=audit_service.list_entries(
            limit=300, search=request.args.get("q") or None),
        total=audit_service.count_entries(),
        search=request.args.get("q", ""),
        user=current_user(),
    )


# ------------------------------------------------------------------ BACKUPS ---
@admin_bp.route("/backups", methods=["GET", "POST"])
@role_required("admin")
def backups():
    if request.method == "POST":
        backup = backup_service.create_backup(current_user())
        if backup and backup["status"] == "completado":
            flash(f"Copia {backup['filename']} creada correctamente.", "ok")
        else:
            flash("No se pudo crear la copia de seguridad.", "error")
        return redirect(url_for("admin.backups"))

    return render_template("admin/backups.html",
                           backups=backup_service.list_backups(),
                           user=current_user())


@admin_bp.route("/backups/<int:backup_id>/restaurar", methods=["POST"])
@role_required("admin")
def restore_backup(backup_id: int):
    result = backup_service.simulate_restore(backup_id, current_user())
    return jsonify(result), (200 if result["ok"] else 400)
