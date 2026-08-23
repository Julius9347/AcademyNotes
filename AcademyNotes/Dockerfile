# Imagen del prototipo AcademyNotes para Fly.io.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# El sistema de archivos de la maquina es efimero: cada despliegue arranca
# con una base limpia generada por seed.py (ver wsgi.py). Es lo que se quiere
# para una demostracion reproducible.
ENV ACADEMYNOTES_DATA_DIR=/data \
    ACADEMYNOTES_HTTPS=1
RUN mkdir -p /data

EXPOSE 8080

# Un solo worker: SQLite no admite escrituras concurrentes desde varios
# procesos. Los hilos bastan de sobra para una demostracion.
CMD ["gunicorn", "wsgi:app", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "1", \
     "--threads", "8", \
     "--timeout", "60", \
     "--access-logfile", "-"]
