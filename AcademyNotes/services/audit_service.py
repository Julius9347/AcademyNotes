"""Historial y auditoria.

Objetivo de producto: que un profesor pueda confiar en el sistema sin
mantener un Excel paralelo. Todo cambio relevante queda registrado con
quien, que, cuando, valor anterior y valor nuevo.
"""
from typing import Any

from core.db import query_all, execute, scalar


def log(
    user: dict | None,
    action: str,
    entity: str | None = None,
    entity_id: int | None = None,
    description: str | None = None,
    old_value: Any = None,
    new_value: Any = None,
) -> int:
    """Registra una entrada del historial."""
    return execute(
        """
        INSERT INTO audit_log
            (user_id, user_name, role, action, entity, entity_id,
             description, old_value, new_value)
        VALUES (?,?,?,?,?,?,?,?,?)
        """,
        (
            (user or {}).get("id"),
            (user or {}).get("full_name", "Sistema"),
            (user or {}).get("role"),
            action,
            entity,
            entity_id,
            description,
            None if old_value is None else str(old_value),
            None if new_value is None else str(new_value),
        ),
    )


def list_entries(
    limit: int = 200,
    entity: str | None = None,
    user_id: int | None = None,
    search: str | None = None,
) -> list[dict]:
    sql = "SELECT * FROM audit_log WHERE 1=1"
    params: list[Any] = []
    if entity:
        sql += " AND entity = ?"
        params.append(entity)
    if user_id:
        sql += " AND user_id = ?"
        params.append(user_id)
    if search:
        sql += " AND (description LIKE ? OR user_name LIKE ? OR action LIKE ?)"
        like = f"%{search}%"
        params += [like, like, like]
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    return query_all(sql, params)


def count_entries() -> int:
    return scalar("SELECT COUNT(*) FROM audit_log") or 0


def grade_history(grade_id: int) -> list[dict]:
    """Historial de una calificacion concreta."""
    return query_all(
        "SELECT * FROM audit_log WHERE entity = 'calificacion' AND entity_id = ? "
        "ORDER BY id DESC",
        (grade_id,),
    )
