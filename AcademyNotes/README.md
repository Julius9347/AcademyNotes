# AcademyNotes — Academic Tracking Prototype v0.1

> **Este proyecto es un prototipo para validación de requisitos y no representa
> todavía la arquitectura definitiva del producto.** Los datos son simulados y
> las políticas de publicación, los umbrales de alerta y las reglas de
> recuperación son **hipótesis** que deben validarse con usuarios reales antes
> de cerrar cualquier decisión.

## Qué es

AcademyNotes es una plataforma de **seguimiento académico y evaluación
formativa**. No busca responder solo *«¿qué nota tiene el estudiante?»*, sino:

- ¿Cómo está evolucionando?
- ¿Qué actividades ha hecho y cuáles le faltan?
- ¿Su rendimiento mejora o empeora?
- ¿Requiere atención? ¿Puede recuperar?
- ¿Cuándo debería intervenir el estudiante, la familia o el colegio?

Con dos principios de diseño en tensión permanente:

1. Que ningún estudiante descubra demasiado tarde que necesitaba ayuda.
2. Que ayudar al estudiante **no signifique más trabajo para el profesor**.

## Objetivo del prototipo

Poder mostrarse a profesores, estudiantes, familias y administradores para
**recoger retroalimentación y descubrir los requisitos reales** del colegio.
No compite en cantidad de funciones con el sistema institucional existente:
compite en simplicidad, confianza y acompañamiento.

## Stack

Flask · SQLite · Jinja2 · JavaScript vanilla (módulos ES, sin build step) ·
openpyxl para Excel · pytest.

Sin ORM, sin framework de frontend, sin Docker, sin servicios externos. La
simplicidad es una característica del prototipo.

## Instalación y ejecución

```bash
pip install -r requirements.txt
python app.py
```

Abre <http://127.0.0.1:5000/>. La primera ejecución crea
`instance/academynotes.db` con los datos de demostración.

Para reconstruir la base desde cero en cualquier momento:

```bash
python seed.py
```

Pruebas:

```bash
python -m pytest tests -q          # toda la suite
python -m pytest tests/test_publication.py -q      # un archivo
python -m pytest tests -q -k promedio_ponderado    # una prueba
```

### Configuración

`ACADEMYNOTES_SECRET_KEY` define la clave de sesión. Si no está definida se
genera una y se guarda en `instance/dev_secret_key` (nunca en el código).
El resto de parámetros está en `config.py` (escala de notas, rutas, límites).

## Usuarios de demostración

Contraseña para todos: **`demo1234`**

| Usuario | Rol | Contexto |
|---|---|---|
| `admin` | Administrador | Ana Morales |
| `crodriguez` | Profesor | Matemáticas 10-A y 10-B, Ciencias 11-A |
| `lgomez` | Profesora | Español 10-A/10-B, Sociales 10-A |
| `apena` | Profesor | Inglés 10-A/11-A, Matemáticas 11-A |
| `jperez` | Estudiante 10-A | Desempeño **descendente** |
| `mfernandez` | Estudiante 10-A | Buen desempeño |
| `slopez` | Estudiante 10-A | Actividades **pendientes** |
| `mjimenez` | Estudiante 10-A | Con **recuperación** |
| `acastro` | Estudiante 10-A | Requiere atención |
| `mperez` | Acudiente | Madre de Juan Pérez |
| `cortiz` | Acudiente | Madre de Gabriela Ortiz y Felipe Cárdenas |

El usuario de un estudiante se forma con la inicial del nombre y el apellido.

## Datos seed

Año lectivo 2026 con **4 periodos** (el sistema admite 3 o 4; no está fijado),
3 grupos (10-A, 10-B, 11-A), 5 asignaturas, 18 estudiantes, 3 profesores,
5 acudientes, 9 asignaciones docentes y ~370 calificaciones repartidas en
situaciones deliberadamente variadas: buen desempeño, desempeño estable,
desempeño descendente, actividades sin entregar, recuperaciones pendientes y
casos que requieren atención.

El Periodo 1 está completo y publicado; el Periodo 2 (activo) tiene una parte
publicada y una parte **en borrador**, para poder demostrar el flujo de
publicación en vivo.

## Escenario de demostración

1. Entra como `crodriguez` → **Matemáticas · 10-A** → Periodo 2.
2. **Nueva actividad**: «Parcial de ecuaciones», peso 30%.
3. Registra notas en la tabla (se guardan solas; Enter baja a la siguiente fila).
4. Observa que quedan **en borrador**.
5. Entra como `jperez`: ve la actividad, pero no la calificación.
6. Vuelve al profesor → **Revisar y publicar**.
7. `jperez` ya ve la nota, el promedio ponderado, su estado y los motivos.
8. Entra como `mperez` (acudiente): el mismo progreso con recomendaciones de
   acompañamiento.
9. Como `jperez`, **Solicitar revisión** sobre esa nota.
10. Como `crodriguez`, responde en **Solicitudes** y corrige la nota.
11. **Historial**: el cambio queda con valor anterior y nuevo.

## Funciones disponibles

**Profesor** — cursos y asignaciones; actividades con tipo, ponderación y
fecha; cuaderno de notas con guardado automático y estados visibles
(*Guardando… / Guardado / Error + Reintentar*); retroalimentación en cuatro
niveles (nota, categoría rápida, plantillas reutilizables, sugerencia asistida
simulada que el profesor acepta, edita o descarta); marcado de no entregado y
recuperaciones; exportación e importación de Excel; publicación; solicitudes de
revisión; historial propio.

**Estudiante** — promedio ponderado, estado académico con motivos explícitos,
tendencia, actividades y pendientes por asignatura, preinformes publicados,
aviso de información nueva (sondeo cada 30 s) y solicitud de revisión con guía
previa.

**Familia** — seguimiento por acudido, asignaturas que requieren atención,
motivos y una recomendación concreta de acompañamiento.

**Administrador** — usuarios, años, periodos, grupos, asignaturas, asignaciones
docentes, preinformes, modo *reporte activo*, historial de auditoría y copias
de seguridad demostrativas.

## Estructura

```
app.py                 fábrica de la aplicación y arranque
config.py              configuración (SECRET_KEY por entorno, escala de notas)
seed.py                datos de demostración
core/
  schema.sql           esquema relacional completo
  db.py                único acceso a SQLite (query_all, execute, transaction)
  security.py          hash de contraseñas, sesión, login_required/role_required
services/              lógica de negocio y SQL (nunca tocan request/session)
  authorization.py     permisos por recurso (asignación, actividad, nota)
  academic_service.py  años, periodos, grupos, asignaturas, personas
  activity_service.py  actividades y ponderaciones
  grade_service.py     notas, promedio ponderado, publicación, visibilidad
  report_service.py    preinformes
  alert_service.py     reglas de alerta explicables (sin IA)
  review_service.py    solicitudes de revisión
  excel_service.py     exportar / previsualizar / importar
  audit_service.py     historial
  backup_service.py    copias demostrativas
blueprints/            rutas por rol (auth, teacher, student, family, admin)
templates/ static/     Jinja2 + CSS y módulos ES sin build step
tests/                 pruebas de los flujos críticos
_legacy/               código de la versión anterior, archivado (puede borrarse)
```

**Tres capas, estrictas:** ruta → servicio → `core/db`. Las rutas no escriben
SQL; los servicios no leen `request` ni `session`.

## Modelo de publicación

Una calificación vive en tres estados: **borrador** (solo el profesor) →
**publicada** (estudiante y familia; puede cambiar) → **final**.

Que una nota esté publicada no basta para que se vea: con el **modo reporte
activo apagado** (por defecto) además debe pertenecer a un **preinforme
publicado**. Encendido, se ve en cuanto el profesor publica. El interruptor
está en *Ajustes* y existe precisamente para probar ambas políticas con
usuarios reales.

## Despliegue

**En línea:** <https://academynotes-demo-production.up.railway.app>

Desplegado en **Railway** desde este repositorio, construyendo con el
`Dockerfile`.

> **Pendiente: el redespliegue automático todavía no está activo.** El servicio
> se creó por API y quedó sin disparador de GitHub, así que un `push` a `main`
> no reconstruye nada por sí solo. Para activarlo, en el panel de Railway:
> servicio `academynotes-demo` → *Settings* → *Source* → conectar el repositorio
> `Julius9347/AcademyNotes` y conceder acceso a la GitHub App de Railway.
> Mientras tanto, se despliega a mano con *Redeploy* en el panel.

| | |
|---|---|
| Proyecto | `AcademyNotes` (workspace `jdrg4's Projects`) |
| Servicio | `academynotes-demo`, entorno `production` |
| Origen | `Julius9347/AcademyNotes`, rama `main`, raíz `AcademyNotes` |
| Construcción | `Dockerfile` (ver `railway.json`) |
| Salud | `GET /entrar`, reinicio ante fallo con 3 reintentos |

Variables configuradas en el servicio: `ACADEMYNOTES_SECRET_KEY` (clave de
sesión estable), `ACADEMYNOTES_HTTPS=1` (cookie `Secure`) y
`ACADEMYNOTES_DATA_DIR=/data`.

**Los datos se reinician en cada despliegue.** La base viaja horneada en la
imagen, así que cada versión arranca con una demo limpia y reproducible. Lo que
un profesor registre durante una sesión de retroalimentación se pierde al
desplegar de nuevo. Para conservarlo habría que montar un volumen en la ruta de
`ACADEMYNOTES_DATA_DIR`: `wsgi.py` detecta si ya existe una base y solo siembra
cuando no la encuentra.

### Lo que hace portable este montaje

Nada de esto depende de Railway, por si conviene cambiar de plataforma:

| Archivo | Para qué sirve |
|---|---|
| `Dockerfile` | Imagen lista, con la demo sembrada en tiempo de construcción (arranque < 1 s) |
| `.dockerignore` | Deja fuera `_legacy/`, `instance/` y el historial de git |
| `Procfile` | Comando de arranque para plataformas que lo leen (Render, Railway, Heroku) |
| `wsgi.py` | Entrada de producción con gunicorn, sin modo debug; siembra si no encuentra base |
| `config.py` | `ACADEMYNOTES_SECRET_KEY`, `ACADEMYNOTES_DATA_DIR` y `ACADEMYNOTES_HTTPS` por entorno |
| `.github/workflows/ci.yml` | Ejecuta las pruebas en cada cambio de `main` y en cada pull request |

Si algún día se cambia de plataforma, el requisito que descarta opciones es
este: **tiene que ser un contenedor o una máquina persistente, no serverless.**
La aplicación escribe en SQLite, y las plataformas serverless (Vercel, Netlify
Functions, Lambda) dan un sistema de archivos efímero y distinto por instancia:
las notas que guardara un profesor no las vería el estudiante, y el historial se
perdería. Usarlas exigiría migrar antes a Postgres. Sirven Render, Fly, Koyeb o
una máquina propia.

### Nota de costes (comprobado en agosto de 2026)

Conviene verificar los niveles gratuitos antes de decidir, porque han cambiado:
Fly.io **eliminó el suyo en 2024** — hoy solo ofrece una prueba de 2 horas de
máquina o 7 días, con tarjeta obligatoria — y Render mantiene uno gratuito, pero
el servicio se duerme a los 15 minutos y tarda unos 50 s en despertar. Un
contenedor pequeño encendido de forma permanente ronda los 3 USD/mes.

## Limitaciones del prototipo

- La restauración de copias es una **simulación verificada**, no una
  restauración real; no hay estrategia de recuperación ante desastres.
- No hay notificaciones reales por correo, SMS, WhatsApp ni push: se simulan
  con estados dentro de la aplicación.
- La «sugerencia» de retroalimentación se genera con reglas a partir de los
  datos existentes. **No hay IA y nunca decide la calificación.**
- Las alertas usan reglas fijas y explicables, no un modelo predictivo. Los
  umbrales (3.0 / 3.5 / caída de 0.3) están sin validar.
- Un solo tipo de administrador; no hay niveles de permiso administrativo.
- No implementa PIAR, observador, citaciones ni mensajería institucional.
- Sin HTTPS, sin recuperación de contraseña, sin límite de intentos de acceso:
  es un prototipo para ejecución local y demostración.
- El servidor usa `debug=True` y SQLite con una conexión por petición: no está
  dimensionado para uso concurrente real.
