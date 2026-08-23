"""Actividades, validacion de notas y promedio ponderado."""
import pytest

from services import activity_service, grade_service


def test_crear_actividad_valida_ponderacion(app, data):
    with app.app_context():
        with pytest.raises(activity_service.ValidationError):
            activity_service.create_activity(data["assignment_id"], data["period_id"],
                                             "Taller", "taller", 0)
        with pytest.raises(activity_service.ValidationError):
            activity_service.create_activity(data["assignment_id"], data["period_id"],
                                             "Taller", "taller", 120)
        with pytest.raises(activity_service.ValidationError):
            activity_service.create_activity(data["assignment_id"], data["period_id"],
                                             "", "taller", 20)


def test_nota_fuera_de_escala_se_rechaza(app, data):
    with app.app_context():
        assert grade_service.validate_score("3,5") == 3.5   # acepta coma decimal
        assert grade_service.validate_score(None) is None   # sin calificar es valido
        with pytest.raises(grade_service.ValidationError):
            grade_service.validate_score(5.5)
        with pytest.raises(grade_service.ValidationError):
            grade_service.validate_score(0.5)
        with pytest.raises(grade_service.ValidationError):
            grade_service.validate_score("abc")


def test_promedio_es_ponderado_no_simple(app, data):
    with app.app_context():
        rows = [
            {"score": 2.0, "weight": 20},
            {"score": 3.0, "weight": 30},
            {"score": 5.0, "weight": 50},
        ]
        # Simple daria 3.33; ponderado: (40 + 90 + 250) / 100 = 3.8
        assert grade_service.weighted_average(rows) == 3.8


def test_promedio_ignora_actividades_sin_nota(app, data):
    with app.app_context():
        rows = [
            {"score": 4.0, "weight": 50},
            {"score": None, "weight": 50},
        ]
        assert grade_service.weighted_average(rows) == 4.0
        assert grade_service.weighted_average([{"score": None, "weight": 20}]) is None


def test_guardar_nota_desde_la_api(app, teacher_client, data):
    with app.app_context():
        activity_id = activity_service.create_activity(
            data["assignment_id"], data["period_id"], "Parcial", "parcial", 30)

    response = teacher_client.post("/profesor/api/notas", json={
        "activity_id": activity_id,
        "student_id": data["student_id"],
        "score": 4.2,
    })
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["promedio"] == 4.2
    assert payload["status"] == "borrador"   # registrar no es publicar

    with app.app_context():
        grade = grade_service.get_grade(activity_id, data["student_id"])
        assert grade["score"] == 4.2


def test_api_rechaza_nota_invalida(app, teacher_client, data):
    with app.app_context():
        activity_id = activity_service.create_activity(
            data["assignment_id"], data["period_id"], "Quiz", "quiz", 10)
    response = teacher_client.post("/profesor/api/notas", json={
        "activity_id": activity_id,
        "student_id": data["student_id"],
        "score": 9,
    })
    assert response.status_code == 400
    assert "entre" in response.get_json()["message"]
