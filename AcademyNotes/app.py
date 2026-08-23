"""AcademyNotes - Academic Tracking Prototype v0.1

Punto de entrada. `python app.py` crea la base de datos con datos de
demostracion si todavia no existe y levanta el servidor local.
"""
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for

from config import Config
from core import db as core_db
from core.security import (PermissionError_, ROLE_LABEL, current_user)


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

    core_db.init_app(app)

    from blueprints.admin import admin_bp
    from blueprints.auth import auth_bp
    from blueprints.family import family_bp
    from blueprints.student import student_bp
    from blueprints.teacher import teacher_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_globals():
        from services import alert_service, settings_service
        user = current_user()
        return {
            "current_user": user,
            "role_label": ROLE_LABEL,
            "estado_class": alert_service.ESTADO_CLASS,
            "institucion": settings_service.get("institucion"),
            "reporte_activo": settings_service.reporte_activo(),
            "app_version": "v0.1",
        }

    @app.errorhandler(PermissionError_)
    def handle_permission(error):
        message = str(error) or "No tienes permiso para esta operacion."
        if request.path.startswith("/api") or "/api/" in request.path:
            return jsonify({"ok": False, "message": message}), 403
        return render_template("403.html", message=message), 403

    @app.errorhandler(404)
    def handle_404(_error):
        if "/api/" in request.path:
            return jsonify({"ok": False, "message": "Recurso no encontrado."}), 404
        return render_template("404.html"), 404

    return app


app = create_app()


def _bootstrap_if_needed() -> None:
    """Prepara la base de demostracion la primera vez que se ejecuta."""
    if Path(app.config["DATABASE"]).exists():
        return
    print("No existe la base de datos: generando datos de demostracion...")
    import seed
    seed.run(app)


if __name__ == "__main__":
    _bootstrap_if_needed()
    print("AcademyNotes v0.1  ->  http://127.0.0.1:5000/")
    app.run(host="127.0.0.1", port=5000, debug=True)
