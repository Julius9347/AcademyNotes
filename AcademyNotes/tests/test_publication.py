"""Modelo de publicacion: registrar -> revisar -> publicar."""
from services import (academic_service, activity_service, grade_service,
                      report_service, settings_service)


def _actividad_con_nota(app, data, score=4.0):
    with app.app_context():
        activity_id = activity_service.create_activity(
            data["assignment_id"], data["period_id"], "Parcial 1", "parcial", 30)
        user = {"id": 1, "full_name": "Carlos Profe", "role": "teacher"}
        grade_service.save_grade(activity_id, data["student_id"], score, user)
        return activity_id


def _resumen_estudiante(app, data):
    with app.app_context():
        assignment = next(
            a for a in academic_service.assignments_for_group(data["group_id"])
            if a["id"] == data["assignment_id"])
        return grade_service.subject_summary(
            data["student_id"], assignment, data["period_id"], only_visible=True)


def test_una_nota_nueva_nace_en_borrador(app, data):
    activity_id = _actividad_con_nota(app, data)
    with app.app_context():
        grade = grade_service.get_grade(activity_id, data["student_id"])
        assert grade["status"] == "borrador"


def test_el_estudiante_no_ve_una_nota_en_borrador(app, data):
    _actividad_con_nota(app, data)
    resumen = _resumen_estudiante(app, data)
    assert resumen["average"] is None
    assert resumen["activities_total"] == 1     # ve la actividad
    assert resumen["activities_graded"] == 0    # pero no la calificacion


def test_publicar_en_un_preinforme_hace_visible_la_nota(app, data):
    _actividad_con_nota(app, data, 4.5)
    with app.app_context():
        user = {"id": 1, "full_name": "Carlos Profe", "role": "teacher"}
        publicadas = grade_service.publish_assignment_period(
            data["assignment_id"], data["period_id"], data["report_id"], user)
        assert publicadas == 1
        report_service.publish_report(data["report_id"], user)

    resumen = _resumen_estudiante(app, data)
    assert resumen["average"] == 4.5
    assert resumen["activities_graded"] == 1


def test_sin_preinforme_publicado_la_nota_sigue_oculta(app, data):
    """Con el modo reporte activo apagado, publicar la actividad no basta."""
    activity_id = _actividad_con_nota(app, data, 3.9)
    with app.app_context():
        settings_service.set_value("reporte_activo", "0")
        user = {"id": 1, "full_name": "Carlos Profe", "role": "teacher"}
        grade_service.publish_activity(activity_id, user)   # sin preinforme

    assert _resumen_estudiante(app, data)["average"] is None


def test_con_reporte_activo_encendido_la_nota_se_ve_al_publicar(app, data):
    activity_id = _actividad_con_nota(app, data, 3.9)
    with app.app_context():
        settings_service.set_value("reporte_activo", "1")
        user = {"id": 1, "full_name": "Carlos Profe", "role": "teacher"}
        grade_service.publish_activity(activity_id, user)

    assert _resumen_estudiante(app, data)["average"] == 3.9


def test_publicar_desde_la_ruta_del_profesor(app, teacher_client, data):
    _actividad_con_nota(app, data, 4.1)
    response = teacher_client.post(
        f"/profesor/asignacion/{data['assignment_id']}/publicar",
        json={"period_id": data["period_id"]})
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["publicadas"] == 1
    assert _resumen_estudiante(app, data)["average"] == 4.1


def test_las_alertas_explican_sus_motivos(app, data):
    _actividad_con_nota(app, data, 2.4)
    with app.app_context():
        user = {"id": 1, "full_name": "Carlos Profe", "role": "teacher"}
        grade_service.publish_assignment_period(
            data["assignment_id"], data["period_id"], data["report_id"], user)
        report_service.publish_report(data["report_id"], user)

    resumen = _resumen_estudiante(app, data)
    assert resumen["estado"] in ("requiere_atencion", "critico")
    assert resumen["motivos"]
    assert any("2.4" in motivo for motivo in resumen["motivos"])
