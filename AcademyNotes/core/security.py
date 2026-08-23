"""Autenticacion, sesion y control de acceso.

Regla del proyecto: la interfaz nunca es la fuente de verdad de los
permisos. Toda ruta protegida verifica en backend usuario + rol y, cuando
opera sobre un recurso concreto, tambien la pertenencia del recurso
(ver services.authorization).
"""
from functools import wraps

from flask import g, jsonify, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from core.db import query_one

ROLES = ("admin", "teacher", "student", "family")

ROLE_HOME = {
    "admin": "admin.dashboard",
    "teacher": "teacher.dashboard",
    "student": "student.dashboard",
    "family": "family.dashboard",
}

ROLE_LABEL = {
    "admin": "Administrador",
    "teacher": "Profesor",
    "student": "Estudiante",
    "family": "Acudiente",
}


class PermissionError_(Exception):
    """El usuario esta autenticado pero no puede tocar este recurso."""


def hash_password(raw_password: str) -> str:
    return generate_password_hash(raw_password)


def verify_password(password_hash: str, raw_password: str) -> bool:
    return check_password_hash(password_hash, raw_password)


def login_user(user: dict) -> None:
    session.clear()
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    session["full_name"] = user["full_name"]
    session.permanent = False


def logout_user() -> None:
    session.clear()


def current_user() -> dict | None:
    """Usuario de la sesion, releido de la base en cada request."""
    if "user" not in g:
        user_id = session.get("user_id")
        g.user = None
        if user_id is not None:
            g.user = query_one(
                "SELECT id, username, full_name, role, email, is_active "
                "FROM users WHERE id = ? AND is_active = 1",
                (user_id,),
            )
    return g.user


def _wants_json() -> bool:
    return (
        request.path.startswith("/api")
        or "/api/" in request.path
        or request.headers.get("X-Requested-With") == "fetch"
        or request.accept_mimetypes.best == "application/json"
    )


def _deny(status: int, message: str):
    if _wants_json():
        return jsonify({"ok": False, "message": message}), status
    if status == 401:
        return redirect(url_for("auth.login", next=request.path))
    return redirect(url_for("auth.acceso_denegado"))


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user() is None:
            return _deny(401, "Debes iniciar sesion.")
        return view(*args, **kwargs)

    return wrapper


def role_required(*roles: str):
    """Exige sesion iniciada y uno de los roles indicados."""

    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None:
                return _deny(401, "Debes iniciar sesion.")
            if user["role"] not in roles:
                return _deny(403, "No tienes permiso para esta operacion.")
            return view(*args, **kwargs)

        return wrapper

    return decorator


def authenticate(username: str, raw_password: str) -> dict | None:
    user = query_one(
        "SELECT id, username, full_name, role, password_hash, is_active "
        "FROM users WHERE username = ?",
        (username,),
    )
    if user is None or not user["is_active"]:
        return None
    if not verify_password(user["password_hash"], raw_password):
        return None
    user.pop("password_hash")
    return user
