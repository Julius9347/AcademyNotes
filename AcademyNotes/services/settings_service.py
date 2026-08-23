"""Configuracion del prototipo guardada en la tabla settings.

Estas politicas son HIPOTESIS, no decisiones institucionales. Estan aqui
para poder cambiarlas en una demostracion y observar la reaccion de los
usuarios.
"""
from core.db import query_all, query_one, execute

DEFAULTS = {
    # Con reporte activo apagado, el estudiante y la familia solo ven las
    # notas que fueron publicadas dentro de un preinforme publicado.
    "reporte_activo": "0",
    "institucion": "Institucion Educativa Demo",
    "anio_lectivo": "2026",
}


def get(key: str, default: str | None = None) -> str | None:
    row = query_one("SELECT value FROM settings WHERE key = ?", (key,))
    if row is not None:
        return row["value"]
    if default is not None:
        return default
    return DEFAULTS.get(key)


def get_bool(key: str) -> bool:
    return str(get(key)).strip() in ("1", "true", "True", "si", "on")


def set_value(key: str, value: str) -> None:
    execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )


def all_settings() -> dict[str, str]:
    values = dict(DEFAULTS)
    for row in query_all("SELECT key, value FROM settings"):
        values[row["key"]] = row["value"]
    return values


def reporte_activo() -> bool:
    return get_bool("reporte_activo")
