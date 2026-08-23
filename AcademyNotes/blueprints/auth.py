"""Inicio de sesion, cierre de sesion y pagina de acceso denegado."""
from urllib.parse import urlparse

from flask import (Blueprint, redirect, render_template, request, url_for)

from core.security import (ROLE_HOME, authenticate, current_user, login_user,
                           logout_user)
from services import audit_service, settings_service

auth_bp = Blueprint("auth", __name__)


def home_for(user: dict) -> str:
    return url_for(ROLE_HOME.get(user["role"], "auth.login"))


def is_safe_destination(destino: str | None) -> bool:
    """Solo se acepta una ruta interna del propio sitio.

    Un simple startswith('/') no basta: '//otro-sitio.com' y '/\\otro-sitio.com'
    empiezan por '/' pero el navegador los interpreta como destinos externos.
    """
    if not destino or not destino.startswith("/"):
        return False
    if destino.startswith(("//", "/\\")):
        return False
    parsed = urlparse(destino)
    return not parsed.scheme and not parsed.netloc


@auth_bp.route("/")
def index():
    user = current_user()
    if user is None:
        return redirect(url_for("auth.login"))
    return redirect(home_for(user))


@auth_bp.route("/entrar", methods=["GET", "POST"])
def login():
    user = current_user()
    if user is not None and request.method == "GET":
        return redirect(home_for(user))

    error = None
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username or not password:
            error = "Escribe tu usuario y tu contrasena."
        else:
            found = authenticate(username, password)
            if found is None:
                error = "Usuario o contrasena incorrectos."
                audit_service.log(
                    None, "Intento de acceso fallido", "usuario", None, username
                )
            else:
                login_user(found)
                audit_service.log(found, "Inicio sesion", "usuario", found["id"])
                destino = request.args.get("next")
                if is_safe_destination(destino):
                    return redirect(destino)
                return redirect(home_for(found))

    return render_template(
        "login.html",
        error=error,
        institucion=settings_service.get("institucion"),
    )


@auth_bp.route("/salir")
def logout():
    user = current_user()
    if user is not None:
        audit_service.log(user, "Cerro sesion", "usuario", user["id"])
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/acceso-denegado")
def acceso_denegado():
    return render_template("403.html"), 403
