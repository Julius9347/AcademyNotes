"""Fixtures de prueba: un colegio minimo creado desde cero en cada test."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from config import TestConfig  # noqa: E402
from core.db import execute, init_db  # noqa: E402
from services import academic_service as academic  # noqa: E402

PASSWORD = "prueba1234"


@pytest.fixture()
def app(tmp_path):
    class Config(TestConfig):
        DATABASE = str(tmp_path / "test.db")
        BACKUP_DIR = str(tmp_path / "backups")

    application = create_app(Config)
    with application.app_context():
        init_db()
    return application


@pytest.fixture()
def data(app):
    """Estructura minima: 1 profesor con 1 asignacion, 2 estudiantes, 1 acudiente."""
    with app.app_context():
        year_id = academic.add_year("2026", is_active=True)
        period_id = academic.add_period(year_id, "Periodo 1", 1, is_active=True)
        period2_id = academic.add_period(year_id, "Periodo 2", 2)
        group_id = academic.add_group("10-A", year_id)
        other_group_id = academic.add_group("10-B", year_id)
        subject_id = academic.add_subject("Matematicas")

        academic.create_user("admin", PASSWORD, "Ana Admin", "admin")
        teacher_id = academic.create_teacher("profe", PASSWORD, "Carlos Profe")
        other_teacher_id = academic.create_teacher("otro", PASSWORD, "Otra Profe")

        student_id = academic.create_student("ana", PASSWORD, "Ana Estudiante",
                                             "EST001", group_id)
        student2_id = academic.create_student("luis", PASSWORD, "Luis Estudiante",
                                              "EST002", group_id)
        outsider_id = academic.create_student("zoe", PASSWORD, "Zoe Ajena",
                                              "EST003", other_group_id)

        guardian_id = academic.create_guardian("papa", PASSWORD, "Padre Ana")
        academic.link_guardian_student(guardian_id, student_id)

        assignment_id = academic.add_assignment(teacher_id, subject_id, group_id,
                                                year_id)
        other_assignment_id = academic.add_assignment(
            other_teacher_id, subject_id, other_group_id, year_id)

        report_id = execute(
            """
            INSERT INTO reports (academic_year_id, period_id, name, kind, status)
            VALUES (?,?,?,?,?)
            """,
            (year_id, period_id, "Preinforme 1", "preinforme", "borrador"),
        )

        return {
            "year_id": year_id,
            "period_id": period_id,
            "period2_id": period2_id,
            "group_id": group_id,
            "subject_id": subject_id,
            "teacher_id": teacher_id,
            "other_teacher_id": other_teacher_id,
            "student_id": student_id,
            "student2_id": student2_id,
            "outsider_id": outsider_id,
            "guardian_id": guardian_id,
            "assignment_id": assignment_id,
            "other_assignment_id": other_assignment_id,
            "report_id": report_id,
        }


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username, password=PASSWORD):
    return client.post("/entrar", data={"username": username, "password": password},
                       follow_redirects=False)


@pytest.fixture()
def teacher_client(app, data):
    test_client = app.test_client()
    login(test_client, "profe")
    return test_client


@pytest.fixture()
def student_client(app, data):
    test_client = app.test_client()
    login(test_client, "ana")
    return test_client
