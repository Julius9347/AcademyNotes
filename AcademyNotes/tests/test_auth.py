"""Autenticacion: contrasenas, sesion y rutas protegidas."""
from conftest import PASSWORD, login

from core.db import query_one
from core.security import authenticate


def test_password_no_se_guarda_en_texto_plano(app, data):
    with app.app_context():
        row = query_one("SELECT password_hash FROM users WHERE username = 'profe'")
        assert PASSWORD not in row["password_hash"]
        assert row["password_hash"].startswith(("pbkdf2:", "scrypt:", "argon2"))


def test_authenticate_valida_credenciales(app, data):
    with app.app_context():
        assert authenticate("profe", PASSWORD)["role"] == "teacher"
        assert authenticate("profe", "incorrecta") is None
        assert authenticate("inexistente", PASSWORD) is None


def test_login_correcto_redirige_al_panel(client, data):
    response = login(client, "profe")
    assert response.status_code == 302
    assert "/profesor/" in response.headers["Location"]


def test_login_incorrecto_muestra_error(client, data):
    response = client.post("/entrar", data={"username": "profe", "password": "mala"})
    assert response.status_code == 200
    assert "incorrectos" in response.get_data(as_text=True)


def test_ruta_protegida_redirige_a_login(client, data):
    response = client.get("/profesor/")
    assert response.status_code == 302
    assert "/entrar" in response.headers["Location"]


def test_api_protegida_responde_401_json(client, data):
    response = client.post("/profesor/api/notas", json={})
    assert response.status_code == 401
    assert response.get_json()["ok"] is False


def test_next_solo_acepta_rutas_internas(client, data):
    """El parametro next no debe poder sacar al usuario del sitio."""
    externos = ["//evil.com", "/\\evil.com", "https://evil.com",
                "http:/evil.com", "javascript:alert(1)"]
    for destino in externos:
        response = client.post(f"/entrar?next={destino}",
                               data={"username": "profe", "password": PASSWORD})
        assert response.status_code == 302
        assert response.headers["Location"] == "/profesor/", destino
        client.get("/salir")


def test_next_respeta_una_ruta_interna(client, data):
    response = client.post("/entrar?next=/profesor/historial",
                           data={"username": "profe", "password": PASSWORD})
    assert response.headers["Location"] == "/profesor/historial"


def test_logout_cierra_la_sesion(teacher_client):
    assert teacher_client.get("/profesor/").status_code == 200
    teacher_client.get("/salir")
    assert teacher_client.get("/profesor/").status_code == 302
