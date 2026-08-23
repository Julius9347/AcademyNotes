"""Acceso a datos: unica puerta de entrada a SQLite.

Ninguna ruta debe importar sqlite3 directamente. Las rutas llaman a los
servicios y los servicios usan estos helpers.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

from flask import current_app, g

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_db() -> sqlite3.Connection:
    """Conexion por request, reutilizada dentro del mismo contexto."""
    if "db" not in g:
        connection = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def close_db(_exception: BaseException | None = None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def query_all(sql: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    """SELECT que devuelve una lista de diccionarios."""
    rows = get_db().execute(sql, tuple(params)).fetchall()
    return [dict(row) for row in rows]


def query_one(sql: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
    """SELECT que devuelve un unico diccionario o None."""
    row = get_db().execute(sql, tuple(params)).fetchone()
    return dict(row) if row is not None else None


def scalar(sql: str, params: Iterable[Any] = ()) -> Any:
    """SELECT de un solo valor (COUNT, AVG, MAX...)."""
    row = get_db().execute(sql, tuple(params)).fetchone()
    return row[0] if row is not None else None


def execute(sql: str, params: Iterable[Any] = ()) -> int:
    """INSERT/UPDATE/DELETE con commit. Devuelve lastrowid."""
    connection = get_db()
    cursor = connection.execute(sql, tuple(params))
    connection.commit()
    return cursor.lastrowid


@contextmanager
def transaction():
    """Agrupa varias escrituras: si algo falla, no queda nada aplicado.

    Se usa sobre todo en la importacion de Excel, donde una importacion
    fallida no debe dejar datos parcialmente modificados.
    """
    connection = get_db()
    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    else:
        connection.commit()


def init_db() -> None:
    """Crea el esquema desde cero. Borra los datos existentes."""
    db_path = Path(current_app.config["DATABASE"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    close_db()
    if db_path.exists():
        db_path.unlink()
    connection = get_db()
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    connection.commit()


def database_exists() -> bool:
    return Path(current_app.config["DATABASE"]).exists()


def init_app(app) -> None:
    app.teardown_appcontext(close_db)
