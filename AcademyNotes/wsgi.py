"""Punto de entrada para el servidor de produccion (gunicorn).

    gunicorn wsgi:app

A diferencia de `python app.py`, aqui no hay modo debug ni recarga
automatica. Si la base de datos todavia no existe (primer arranque, o
despliegue sin disco persistente), se generan los datos de demostracion:
el prototipo siempre debe quedar listo para mostrarse.
"""
from pathlib import Path

from app import app

_marker = Path(app.config["DATABASE"])
if not _marker.exists():
    import seed

    seed.run(app)
    print(f"AcademyNotes: base de demostracion generada en {_marker}")
else:
    print(f"AcademyNotes: usando la base existente en {_marker}")
