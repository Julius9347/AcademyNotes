"""Configuracion del prototipo AcademyNotes.

La SECRET_KEY se toma de la variable de entorno ACADEMYNOTES_SECRET_KEY.
Si no existe (caso tipico en desarrollo local), se genera una vez y se
guarda en instance/dev_secret_key para que las sesiones sobrevivan a los
reinicios del servidor. Nunca se escribe una clave en el codigo fuente.
"""
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"


def _dev_secret_key() -> str:
    INSTANCE_DIR.mkdir(exist_ok=True)
    key_file = INSTANCE_DIR / "dev_secret_key"
    if not key_file.exists():
        key_file.write_text(secrets.token_hex(32), encoding="utf-8")
    return key_file.read_text(encoding="utf-8").strip()


# En un despliegue, ACADEMYNOTES_DATA_DIR apunta al disco persistente (o a
# cualquier ruta escribible). Sin esa variable se usa instance/, como en local.
DATA_DIR = Path(os.environ.get("ACADEMYNOTES_DATA_DIR") or INSTANCE_DIR)


class Config:
    """Configuracion base (desarrollo / demostracion)."""

    SECRET_KEY = os.environ.get("ACADEMYNOTES_SECRET_KEY") or _dev_secret_key()
    DATABASE = str(DATA_DIR / "academynotes.db")
    BACKUP_DIR = str(DATA_DIR / "backups")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # El despliegue va detras de HTTPS; en local (http) la cookie debe seguir
    # viajando, por eso es configurable y no un valor fijo.
    SESSION_COOKIE_SECURE = os.environ.get("ACADEMYNOTES_HTTPS") == "1"
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB: suficiente para un .xlsx
    # Escala de calificacion del prototipo. Configurable: la escala real
    # todavia es una hipotesis que debe validarse con el colegio.
    MIN_SCORE = 1.0
    MAX_SCORE = 5.0
    PASSING_SCORE = 3.0


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret-key"
