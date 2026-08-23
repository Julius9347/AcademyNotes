"""Solicitudes de revision e historial de cambios."""
import pytest

from services import (activity_service, audit_service, grade_service,
                      report_service, review_service)

USER_PROFE = {"id": 2, "full_name": "Carlos Profe", "role": "teacher"}
USER_ALUMNO = {"id": 4, "full_name": "Ana Estudiante", "role": "student"}


@pytest.fixture()
def nota_publicada(app, data):
    with app.app_context():
        activity_id = activity_service.create_activity(
            data["assignment_id"], data["period_id"], "Parcial 1", "parcial", 30)
        grade_service.save_grade(activity_id, data["student_id"], 3.2, USER_PROFE)
        grade_service.publish_assignment_period(
            data["assignment_id"], data["period_id"], data["report_id"], USER_PROFE)
        report_service.publish_report(data["report_id"], USER_PROFE)
        grade = grade_service.get_grade(activity_id, data["student_id"])
        return {"activity_id": activity_id, "grade_id": grade["id"], **data}


def test_modificar_una_nota_queda_en_el_historial(app, nota_publicada):
    with app.app_context():
        grade_service.save_grade(nota_publicada["activity_id"],
                                 nota_publicada["student_id"], 3.7, USER_PROFE)
        entradas = audit_service.grade_history(nota_publicada["grade_id"])
        cambio = next(e for e in entradas if e["action"] == "Modifico calificacion")
        assert cambio["old_value"] == "3.2"
        assert cambio["new_value"] == "3.7"
        assert cambio["user_name"] == "Carlos Profe"


def test_el_estudiante_solicita_revision(app, nota_publicada):
    with app.app_context():
        request_id = review_service.create_request(
            nota_publicada["grade_id"], nota_publicada["student_id"],
            "posible_error", "Entregue el punto 3 y no aparece calificado.",
            USER_ALUMNO)
        solicitud = review_service.get_request(request_id)
        assert solicitud["status"] == "pendiente"
        assert review_service.pending_count(nota_publicada["teacher_id"]) == 1


def test_no_se_permiten_solicitudes_vacias_ni_duplicadas(app, nota_publicada):
    with app.app_context():
        with pytest.raises(review_service.ValidationError):
            review_service.create_request(nota_publicada["grade_id"],
                                          nota_publicada["student_id"],
                                          "posible_error", "corto", USER_ALUMNO)
        with pytest.raises(review_service.ValidationError):
            review_service.create_request(nota_publicada["grade_id"],
                                          nota_publicada["student_id"],
                                          "inventado", "Una explicacion valida.",
                                          USER_ALUMNO)
        review_service.create_request(nota_publicada["grade_id"],
                                      nota_publicada["student_id"],
                                      "posible_error", "Una explicacion valida.",
                                      USER_ALUMNO)
        with pytest.raises(review_service.ValidationError):
            review_service.create_request(nota_publicada["grade_id"],
                                          nota_publicada["student_id"],
                                          "posible_error", "Otra explicacion valida.",
                                          USER_ALUMNO)


def test_el_profesor_acepta_y_corrige_la_nota(app, nota_publicada):
    with app.app_context():
        request_id = review_service.create_request(
            nota_publicada["grade_id"], nota_publicada["student_id"],
            "no_aparece", "Falta el punto 3 que si entregue.", USER_ALUMNO)

        review_service.respond(request_id, USER_PROFE, "aceptada",
                               "Revise la entrega y ajusto la nota.", 3.7)

        grade = grade_service.get_grade(nota_publicada["activity_id"],
                                        nota_publicada["student_id"])
        assert grade["score"] == 3.7

        solicitud = review_service.get_request(request_id)
        assert solicitud["status"] == "aceptada"

        historial = audit_service.grade_history(nota_publicada["grade_id"])
        assert any("solicitud de revision" in (e["description"] or "")
                   for e in historial)


def test_responder_exige_explicacion(app, nota_publicada):
    with app.app_context():
        request_id = review_service.create_request(
            nota_publicada["grade_id"], nota_publicada["student_id"],
            "no_entiendo", "No entiendo como se calculo.", USER_ALUMNO)
        with pytest.raises(review_service.ValidationError):
            review_service.respond(request_id, USER_PROFE, "rechazada", "")


def test_el_estudiante_no_pide_revision_de_una_nota_ajena(app, nota_publicada):
    with app.app_context():
        with pytest.raises(review_service.ValidationError):
            review_service.create_request(
                nota_publicada["grade_id"], nota_publicada["student2_id"],
                "posible_error", "Esta nota no es mia.", USER_ALUMNO)
