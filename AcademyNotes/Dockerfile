# Imagen del prototipo AcademyNotes.
#
# Sirve para cualquier plataforma que ejecute contenedores (Render, Railway,
# Fly, una VM propia). NO sirve para plataformas serverless tipo Vercel: la
# aplicacion escribe en SQLite y necesita un disco y un proceso persistentes.
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

# La base de demostracion se genera al construir la imagen, no al arrancar:
# sembrar tarda ~20 s en esta maquina y esa espera la pagaria quien abriera
# el enlace primero. Asi cada despliegue viaja con su demo lista.
# Si algun dia se monta un volumen en /data, wsgi.py vuelve a sembrar solo.
RUN python seed.py

EXPOSE 8080

# Un solo worker: SQLite no admite escrituras concurrentes desde varios
# procesos. Los hilos bastan de sobra para una demostracion.
CMD ["gunicorn", "wsgi:app", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "1", \
     "--threads", "8", \
     "--timeout", "60", \
     "--access-logfile", "-"]
