"""Alertas academicas explicables.

Deliberadamente NO se usa un modelo predictivo: son reglas simples que
siempre pueden mostrar sus motivos. Los umbrales son una hipotesis y
deben validarse con el colegio antes de fijarlos.
"""

UMBRAL_APROBACION = 3.0
UMBRAL_ATENCION = 3.5
CAIDA_SIGNIFICATIVA = 0.3

ESTADOS = ("sin_datos", "adecuado", "estable", "requiere_atencion", "critico")

ESTADO_LABEL = {
    "sin_datos": "Sin informacion suficiente",
    "adecuado": "Desempeno adecuado",
    "estable": "Desempeno estable",
    "requiere_atencion": "Requiere atencion",
    "critico": "Requiere acompanamiento",
}

# Clase CSS del distintivo que acompana a cada estado en la interfaz.
ESTADO_CLASS = {
    "sin_datos": "muted",
    "adecuado": "ok",
    "estable": "info",
    "requiere_atencion": "warn",
    "critico": "alert",
}

TENDENCIA_LABEL = {
    "ascendente": "Ascendente",
    "estable": "Estable",
    "descendente": "Descendente",
    "sin_datos": "Sin datos",
}


def trend(scores: list[float]) -> str:
    """Compara la primera mitad de las notas con la segunda mitad."""
    valid = [s for s in scores if s is not None]
    if len(valid) < 2:
        return "sin_datos"
    half = len(valid) // 2
    first = valid[:half] or valid[:1]
    second = valid[half:] or valid[-1:]
    delta = (sum(second) / len(second)) - (sum(first) / len(first))
    if delta <= -CAIDA_SIGNIFICATIVA:
        return "descendente"
    if delta >= CAIDA_SIGNIFICATIVA:
        return "ascendente"
    return "estable"


def evaluate(average: float | None, trend_value: str, pending: int,
             recovery_pending: int = 0, graded: int = 0) -> dict:
    """Devuelve estado + motivos legibles.

    El lenguaje evita el alarmismo: se habla de atencion y acompanamiento,
    nunca de 'estas perdiendo'.
    """
    reasons: list[str] = []

    if graded == 0 and pending == 0:
        return {
            "estado": "sin_datos",
            "estado_label": ESTADO_LABEL["sin_datos"],
            "motivos": ["Todavia no hay calificaciones publicadas."],
            "tendencia": trend_value,
            "tendencia_label": TENDENCIA_LABEL.get(trend_value, "Sin datos"),
        }

    if average is not None and average < UMBRAL_APROBACION:
        reasons.append(f"Promedio actual {average:.1f}, por debajo de {UMBRAL_APROBACION:.1f}.")
    elif average is not None and average < UMBRAL_ATENCION:
        reasons.append(f"Promedio actual {average:.1f}, cerca del limite.")

    if trend_value == "descendente":
        reasons.append("El desempeno viene descendiendo respecto a las primeras actividades.")

    if pending == 1:
        reasons.append("Hay 1 actividad pendiente por entregar o calificar.")
    elif pending > 1:
        reasons.append(f"Hay {pending} actividades pendientes por entregar o calificar.")

    if recovery_pending:
        reasons.append(f"Tiene {recovery_pending} recuperacion(es) pendiente(s).")

    critico = (average is not None and average < UMBRAL_APROBACION) and (
        pending >= 2 or trend_value == "descendente"
    )
    if critico:
        estado = "critico"
    elif reasons:
        estado = "requiere_atencion"
    elif trend_value == "ascendente":
        estado = "adecuado"
    else:
        estado = "estable"

    if not reasons:
        if average is not None:
            reasons.append(f"Promedio actual {average:.1f}, sin senales de dificultad.")
        else:
            reasons.append("Sin senales de dificultad.")

    return {
        "estado": estado,
        "estado_label": ESTADO_LABEL[estado],
        "motivos": reasons,
        "tendencia": trend_value,
        "tendencia_label": TENDENCIA_LABEL.get(trend_value, "Sin datos"),
    }


def recommendation(estado: str) -> str:
    """Sugerencia breve de acompanamiento para la familia."""
    return {
        "critico": "Conviene conversar con el estudiante esta semana y revisar juntos "
                   "las actividades pendientes antes del cierre del periodo.",
        "requiere_atencion": "Un buen momento para preguntar como va la asignatura y "
                             "revisar que actividades faltan por entregar.",
        "estable": "El desempeno se mantiene. Acompanar la rutina de estudio es suficiente.",
        "adecuado": "El desempeno viene mejorando. Reconocer el avance ayuda a sostenerlo.",
        "sin_datos": "Todavia no hay informacion publicada en esta asignatura.",
    }.get(estado, "")
