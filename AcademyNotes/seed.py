"""Datos de demostracion de AcademyNotes.

Genera un colegio simulado con situaciones academicas variadas para que
el prototipo pueda mostrarse a profesores, estudiantes y familias.

    python seed.py            # reconstruye instance/academynotes.db

Es deterministico: la misma semilla produce siempre la misma demostracion.
"""
import random
from datetime import date, timedelta

from core.db import execute, init_db, query_one
from services import academic_service as academic
from services import settings_service

PASSWORD = "demo1234"

TEACHERS = [
    ("crodriguez", "Carlos Rodriguez"),
    ("lgomez", "Laura Gomez"),
    ("apena", "Andres Pena"),
]

SUBJECTS = ["Matematicas", "Espanol", "Ciencias", "Ingles", "Sociales"]

GROUPS = ["10-A", "10-B", "11-A"]

# (nombre, grupo, perfil academico)
STUDENTS = [
    ("Juan Perez",        "10-A", "descendente"),
    ("Maria Fernandez",   "10-A", "alto"),
    ("Santiago Lopez",    "10-A", "pendiente"),
    ("Valentina Ramirez", "10-A", "estable"),
    ("Andres Castro",     "10-A", "atencion"),
    ("Sofia Herrera",     "10-A", "alto"),
    ("Mateo Jimenez",     "10-A", "recuperacion"),
    ("Camila Torres",     "10-B", "estable"),
    ("Sebastian Rojas",   "10-B", "descendente"),
    ("Isabella Moreno",   "10-B", "alto"),
    ("Nicolas Vargas",    "10-B", "atencion"),
    ("Daniela Suarez",    "10-B", "estable"),
    ("Emilio Navarro",    "10-B", "pendiente"),
    ("Lucia Mendoza",     "11-A", "alto"),
    ("Tomas Guerrero",    "11-A", "estable"),
    ("Gabriela Ortiz",    "11-A", "descendente"),
    ("Felipe Cardenas",   "11-A", "recuperacion"),
    ("Antonia Rivera",    "11-A", "atencion"),
]

GUARDIANS = [
    ("mperez", "Marta Perez", "Madre", ["Juan Perez"]),
    ("jlopez", "Jorge Lopez", "Padre", ["Santiago Lopez"]),
    ("rcastro", "Rosa Castro", "Madre", ["Andres Castro", "Sofia Herrera"]),
    ("hrojas", "Hector Rojas", "Padre", ["Sebastian Rojas"]),
    ("cortiz", "Clara Ortiz", "Madre", ["Gabriela Ortiz", "Felipe Cardenas"]),
]

# Que asignaturas recibe cada grupo y quien las dicta.
ASSIGNMENTS = [
    ("Carlos Rodriguez", "Matematicas", "10-A"),
    ("Carlos Rodriguez", "Matematicas", "10-B"),
    ("Carlos Rodriguez", "Ciencias",    "11-A"),
    ("Laura Gomez",      "Espanol",     "10-A"),
    ("Laura Gomez",      "Espanol",     "10-B"),
    ("Laura Gomez",      "Sociales",    "10-A"),
    ("Andres Pena",      "Ingles",      "10-A"),
    ("Andres Pena",      "Ingles",      "11-A"),
    ("Andres Pena",      "Matematicas", "11-A"),
]

# Actividades por periodo: (nombre, tipo, ponderacion, dias antes de hoy)
PERIOD1_ACTIVITIES = [
    ("Taller diagnostico", "taller",   20, 90),
    ("Quiz de conceptos",  "quiz",     20, 75),
    ("Parcial 1",          "parcial",  30, 60),
    ("Proyecto de aula",   "proyecto", 30, 48),
]
PERIOD2_ACTIVITIES = [
    ("Taller de refuerzo",  "taller",   25, 25),
    ("Quiz 2",              "quiz",     25, 12),
    ("Proyecto de periodo", "proyecto", 20, 3),
]

PROFILE_SCORES = {
    # perfil: notas sucesivas (se recortan o repiten segun haga falta)
    "alto":         [4.5, 4.7, 4.4, 4.8, 4.6, 4.9, 4.5],
    "estable":      [3.8, 3.7, 3.9, 3.6, 3.8, 3.7, 3.9],
    "descendente":  [4.2, 3.9, 3.4, 2.9, 2.6, 2.4, 2.3],
    "atencion":     [2.9, 3.0, 2.7, 2.8, 2.6, 2.9, 2.8],
    "pendiente":    [3.6, 3.5, 3.4, 3.5, 3.6, 3.4, 3.5],
    "recuperacion": [2.4, 2.6, 2.2, 2.5, 2.3, 2.7, 2.4],
}


def _days_ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


def _insert_grade(activity_id: int, student_id: int, score, status="borrador",
                  report_id=None, is_missing=0, recovery="ninguna",
                  category=None, text=None, user_id=1) -> None:
    execute(
        """
        INSERT INTO grades
            (activity_id, student_id, score, status, feedback_category,
             feedback_text, is_missing, recovery_status, published_report_id,
             published_at, updated_by)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        (activity_id, student_id, score, status, category, text, is_missing,
         recovery, report_id,
         _days_ago(1) if status != "borrador" else None, user_id),
    )


def run(app) -> dict:
    """Reconstruye la base de datos de demostracion."""
    with app.app_context():
        init_db()
        random.seed(20260823)

        # ------------------------------------------------ estructura base ---
        year_id = academic.add_year("2026", is_active=True)
        period_ids = []
        periods_def = [
            ("Periodo 1", 1, 120, 65, False),
            ("Periodo 2", 2, 64, 5, True),
            ("Periodo 3", 3, 4, -60, False),
            ("Periodo 4", 4, -61, -120, False),
        ]
        for name, sequence, start_days, end_days, active in periods_def:
            period_ids.append(academic.add_period(
                year_id, name, sequence, _days_ago(start_days),
                _days_ago(end_days), active))
        period1, period2 = period_ids[0], period_ids[1]

        group_ids = {name: academic.add_group(name, year_id) for name in GROUPS}
        subject_ids = {name: academic.add_subject(name) for name in SUBJECTS}

        # -------------------------------------------------------- personas ---
        admin_user_id = academic.create_user(
            "admin", PASSWORD, "Ana Morales", "admin", "admin@colegio.demo")

        teacher_ids = {}
        for username, full_name in TEACHERS:
            teacher_ids[full_name] = academic.create_teacher(
                username, PASSWORD, full_name, f"{username}@colegio.demo")

        student_ids = {}
        profiles = {}
        for index, (full_name, group_name, profile) in enumerate(STUDENTS, start=1):
            username = _username(full_name)
            student_ids[full_name] = academic.create_student(
                username, PASSWORD, full_name, f"EST{index:03d}",
                group_ids[group_name], f"{username}@colegio.demo")
            profiles[full_name] = profile

        for username, full_name, relationship, children in GUARDIANS:
            guardian_id = academic.create_guardian(
                username, PASSWORD, full_name, relationship,
                f"{username}@correo.demo")
            for child in children:
                academic.link_guardian_student(guardian_id, student_ids[child])

        # --------------------------------------------- asignaciones docentes ---
        assignment_ids = {}
        for teacher_name, subject_name, group_name in ASSIGNMENTS:
            assignment_ids[(subject_name, group_name)] = academic.add_assignment(
                teacher_ids[teacher_name], subject_ids[subject_name],
                group_ids[group_name], year_id)

        # ------------------------------------------------------ preinformes ---
        admin_user = {"id": admin_user_id, "full_name": "Ana Morales",
                      "role": "admin"}
        report1_id = execute(
            """
            INSERT INTO reports (academic_year_id, period_id, name, kind,
                                 report_date, status, published_at, created_by)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (year_id, period1, "Preinforme Periodo 1", "preinforme",
             _days_ago(50), "publicado", _days_ago(50), admin_user_id),
        )
        report2_id = execute(
            """
            INSERT INTO reports (academic_year_id, period_id, name, kind,
                                 report_date, status, published_at, created_by)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (year_id, period2, "Preinforme 1 - Periodo 2", "preinforme",
             _days_ago(10), "publicado", _days_ago(10), admin_user_id),
        )
        execute(
            """
            INSERT INTO reports (academic_year_id, period_id, name, kind,
                                 report_date, status, created_by)
            VALUES (?,?,?,?,?,?,?)
            """,
            (year_id, period2, "Preinforme 2 - Periodo 2", "preinforme",
             _days_ago(-5), "borrador", admin_user_id),
        )

        # ---------------------------------------- actividades y calificaciones ---
        for (subject_name, group_name), assignment_id in assignment_ids.items():
            students_in_group = [(name, profile) for name, group, profile
                                 in STUDENTS if group == group_name]

            _seed_period(assignment_id, period1, PERIOD1_ACTIVITIES,
                         students_in_group, student_ids, "publicada",
                         report1_id, admin_user_id, closed=True)
            _seed_period(assignment_id, period2, PERIOD2_ACTIVITIES,
                         students_in_group, student_ids, "publicada",
                         report2_id, admin_user_id, closed=False)

        settings_service.set_value("reporte_activo", "0")
        settings_service.set_value("institucion", "Institucion Educativa Demo")
        settings_service.set_value("anio_lectivo", "2026")

        execute(
            "INSERT INTO feedback_templates (teacher_id, text) VALUES (NULL, ?)",
            ("Buen manejo del tema. Sigue reforzando con ejercicios similares.",),
        )
        execute(
            "INSERT INTO feedback_templates (teacher_id, text) VALUES (NULL, ?)",
            ("Le falto sustentar el procedimiento. Puede mejorar explicando "
             "su razonamiento.",),
        )

        execute(
            """
            INSERT INTO audit_log (user_name, role, action, entity, description)
            VALUES (?,?,?,?,?)
            """,
            ("Sistema", "admin", "Genero datos de demostracion", "sistema",
             "Base de datos del prototipo reconstruida"),
        )

        total = query_one("SELECT COUNT(*) AS total FROM grades WHERE score IS NOT NULL")
        return {
            "estudiantes": len(STUDENTS),
            "profesores": len(TEACHERS),
            "acudientes": len(GUARDIANS),
            "asignaciones": len(assignment_ids),
            "calificaciones": total["total"] if total else 0,
        }


def _seed_period(assignment_id, period_id, activities_def, students_in_group,
                 student_ids, published_status, report_id, admin_user_id,
                 closed: bool) -> None:
    """Crea las actividades de un periodo y las califica segun cada perfil."""
    activity_rows = []
    for name, kind, weight, days in activities_def:
        activity_id = execute(
            """
            INSERT INTO activities
                (assignment_id, period_id, name, kind, weight, due_date,
                 allows_recovery)
            VALUES (?,?,?,?,?,?,?)
            """,
            (assignment_id, period_id, name, kind, weight, _days_ago(days),
             1 if kind in ("parcial", "proyecto") else 0),
        )
        activity_rows.append((activity_id, name, kind))

    last_index = len(activity_rows) - 1
    for student_name, profile in students_in_group:
        student_id = student_ids[student_name]
        scores = PROFILE_SCORES[profile]
        for index, (activity_id, _name, kind) in enumerate(activity_rows):
            score = scores[index % len(scores)]
            score = round(min(5.0, max(1.0, score + random.uniform(-0.15, 0.15))), 1)

            # La ultima actividad del periodo abierto queda en borrador:
            # es lo que el profesor todavia no ha publicado.
            is_last_open = (not closed and index == last_index)
            status = "borrador" if is_last_open else published_status
            grade_report = None if is_last_open else report_id

            if profile == "pendiente" and index >= last_index - 1 and not closed:
                # Estudiante con actividades sin entregar.
                _insert_grade(activity_id, student_id, None, "borrador", None,
                              is_missing=1, category="No entrego",
                              user_id=admin_user_id)
                continue

            recovery = "ninguna"
            category = None
            if profile == "recuperacion" and kind in ("parcial", "proyecto"):
                recovery = "disponible" if closed else "pendiente"
                category = "Requiere recuperacion"
            elif score >= 4.5:
                category = "Dominio adecuado"
            elif score < 3.0:
                category = "Presenta dificultades"

            _insert_grade(activity_id, student_id, score, status, grade_report,
                          recovery=recovery, category=category,
                          user_id=admin_user_id)


def _username(full_name: str) -> str:
    parts = full_name.lower().split()
    return (parts[0][0] + parts[-1]).replace(" ", "")


if __name__ == "__main__":
    from app import app as flask_app

    stats = run(flask_app)
    print("Base de demostracion creada:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print(f"\nUsuarios de prueba (contrasena '{PASSWORD}'):")
    print("  admin        -> Administrador")
    print("  crodriguez   -> Profesor (Matematicas 10-A, 10-B / Ciencias 11-A)")
    print("  lgomez       -> Profesora (Espanol, Sociales)")
    print("  jperez       -> Estudiante 10-A (desempeno descendente)")
    print("  mfernandez   -> Estudiante 10-A (buen desempeno)")
    print("  slopez       -> Estudiante 10-A (actividades pendientes)")
    print("  mperez       -> Acudiente de Juan Perez")
