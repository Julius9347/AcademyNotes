"""Retroalimentacion por niveles.

Nivel 1: solo nota.
Nivel 2: categoria rapida de un clic.
Nivel 3: comentarios reutilizables (plantillas).
Nivel 4: sugerencia asistida. En el prototipo la sugerencia se genera con
         reglas a partir de los datos disponibles; NO hay modelo de IA y
         nunca decide la calificacion: el profesor acepta, edita o descarta.
"""
from core.db import execute, query_all
from services.grade_service import FEEDBACK_CATEGORIES

CATEGORIES = FEEDBACK_CATEGORIES

DEFAULT_TEMPLATES = (
    "Buen manejo del tema. Sigue reforzando con ejercicios similares.",
    "Entrego a tiempo pero con errores de procedimiento. Repasar los pasos.",
    "Le falto sustentar el procedimiento. Puede mejorar explicando su razonamiento.",
    "No entrego la actividad. Puede presentarla en la fecha de recuperacion.",
)


def list_templates(teacher_id: int | None = None) -> list[dict]:
    return query_all(
        "SELECT * FROM feedback_templates WHERE teacher_id IS NULL OR teacher_id = ? "
        "ORDER BY id",
        (teacher_id,),
    )


def add_template(text: str, teacher_id: int | None = None) -> int:
    return execute(
        "INSERT INTO feedback_templates (teacher_id, text) VALUES (?,?)",
        (teacher_id, text.strip()),
    )


def suggest(student_name: str, activity_name: str, score: float | None,
            average: float | None, pending: int = 0) -> str:
    """Sugerencia simulada, construida con los datos que ya existen.

    Se marca siempre como asistente: el profesor decide.
    """
    first_name = (student_name or "El estudiante").split()[0]

    if score is None:
        base = (f"{first_name} aun no tiene calificacion en {activity_name}. "
                "Conviene confirmar si entrego la actividad.")
    elif score >= 4.5:
        base = (f"{first_name} demuestra dominio en {activity_name}. "
                "Puede avanzar con ejercicios de mayor exigencia.")
    elif score >= 3.5:
        base = (f"{first_name} alcanza los criterios de {activity_name}. "
                "Con practica adicional puede consolidar el tema.")
    elif score >= 3.0:
        base = (f"{first_name} cumple lo minimo en {activity_name}. "
                "Se recomienda repasar los puntos con mas errores.")
    else:
        base = (f"{first_name} presenta dificultades en {activity_name}. "
                "Se sugiere revisar los conceptos base antes de continuar.")

    extras = []
    if average is not None and average < 3.0:
        extras.append(f"Su promedio en la asignatura es {average:.1f}.")
    if pending:
        extras.append(f"Tiene {pending} actividad(es) pendiente(s).")
    if extras:
        base += " " + " ".join(extras)
    return base
