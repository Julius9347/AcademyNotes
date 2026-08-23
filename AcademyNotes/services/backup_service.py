"""Copias de seguridad demostrativas.

Alcance deliberadamente limitado: el prototipo copia el archivo SQLite y
registra la operacion. NO es una solucion de recuperacion ante desastres,
y la restauracion se ofrece como simulacion controlada.
"""
import shutil
from datetime import datetime
from pathlib import Path

from flask import current_app

from core.db import execute, query_all, query_one
from services import audit_service


def _backup_dir() -> Path:
    path = Path(current_app.config["BACKUP_DIR"])
    path.mkdir(parents=True, exist_ok=True)
    return path


def create_backup(user: dict, kind: str = "manual") -> dict:
    source = Path(current_app.config["DATABASE"])
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"academynotes_{stamp}.db"
    destination = _backup_dir() / filename

    status = "completado"
    size = 0
    try:
        shutil.copy2(source, destination)
        size = destination.stat().st_size
    except Exception:
        status = "fallido"

    backup_id = execute(
        """
        INSERT INTO backups (filename, size_bytes, status, created_by_name, kind)
        VALUES (?,?,?,?,?)
        """,
        (filename, size, status, user.get("full_name"), kind),
    )
    audit_service.log(
        user, "Genero copia de seguridad", "backup", backup_id, filename,
        None, status,
    )
    return get_backup(backup_id)


def list_backups() -> list[dict]:
    rows = query_all("SELECT * FROM backups ORDER BY id DESC")
    for row in rows:
        row["size_kb"] = round((row["size_bytes"] or 0) / 1024, 1)
    return rows


def get_backup(backup_id: int) -> dict | None:
    return query_one("SELECT * FROM backups WHERE id = ?", (backup_id,))


def simulate_restore(backup_id: int, user: dict) -> dict:
    """Verifica que el archivo exista y registra el intento.

    No sustituye la base activa: en un prototipo que se esta demostrando,
    una restauracion real destruiria la sesion en curso.
    """
    backup = get_backup(backup_id)
    if backup is None:
        return {"ok": False, "message": "La copia no existe."}
    path = _backup_dir() / backup["filename"]
    exists = path.exists()
    audit_service.log(
        user, "Simulo restauracion", "backup", backup_id, backup["filename"],
        None, "verificado" if exists else "archivo no encontrado",
    )
    if not exists:
        return {"ok": False, "message": "El archivo de la copia no se encuentra."}
    return {
        "ok": True,
        "message": (f"Copia {backup['filename']} verificada correctamente "
                    f"({round(path.stat().st_size / 1024, 1)} KB). "
                    "En el prototipo la restauracion es una simulacion."),
    }
