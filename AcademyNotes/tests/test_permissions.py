"""Autorizacion por recurso: la interfaz no es la fuente de verdad."""
from conftest import login

from services import activity_service


def _crear_actividad(app, data, assignment_id=None):
    with app.app_context():
        return activity_service.create_activity(
            assignment_id or data["assignment_id"], data["period_id"],
            "Taller 1", "taller", 20)


def test_profesor_no_abre_cuaderno_ajeno(teacher_client, data):
    response = teacher_client.get(f"/profesor/asignacion/{data['other_assignment_id']}")
    assert response.status_code in (302, 403)


def test_profesor_no_califica_actividad_ajena(app, teacher_client, data):
    ajena = _crear_actividad(app, data, data["other_assignment_id"])
    response = teacher_client.post("/profesor/api/notas", json={
        "activity_id": ajena,
        "student_id": data["outsider_id"],
        "score": 4.0,
    })
    assert response.status_code == 403
    assert response.get_json()["ok"] is False


def test_profesor_no_califica_estudiante_de_otro_grupo(app, teacher_client, data):
    propia = _crear_actividad(app, data)
    response = teacher_client.post("/profesor/api/notas", json={
        "activity_id": propia,
        "student_id": data["outsider_id"],
        "score": 4.0,
    })
    assert response.status_code == 403


def test_estudiante_no_entra_al_panel_del_profesor(student_client, data):
    response = student_client.get("/profesor/")
    assert response.status_code in (302, 403)


def test_estudiante_no_guarda_notas(student_client, data):
    response = student_client.post("/profesor/api/notas", json={
        "activity_id": 1, "student_id": 1, "score": 5,
    })
    assert response.status_code == 403


def test_acudiente_solo_ve_a_su_acudido(app, data):
    client = app.test_client()
    login(client, "papa")
    assert client.get(f"/familia/estudiante/{data['student_id']}").status_code == 200
    ajeno = client.get(f"/familia/estudiante/{data['outsider_id']}")
    assert ajeno.status_code in (302, 403)


def test_estudiante_no_es_admin(student_client, data):
    assert student_client.get("/admin/").status_code in (302, 403)


def test_profesor_no_es_admin(teacher_client, data):
    assert teacher_client.get("/admin/usuarios").status_code in (302, 403)
