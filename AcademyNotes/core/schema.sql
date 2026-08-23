-- Esquema relacional del prototipo AcademyNotes v0.1
-- Fechas guardadas como TEXT ISO: datetime('now','localtime').

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------- identidad ---
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    full_name     TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK (role IN ('admin','teacher','student','family')),
    email         TEXT,
    is_active     INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- --------------------------------------------------- estructura academica ---
CREATE TABLE academic_years (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL UNIQUE,
    is_active INTEGER NOT NULL DEFAULT 0
);

-- Un anio puede tener 3 o 4 periodos: la cantidad no esta fijada en el esquema.
CREATE TABLE academic_periods (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_year_id INTEGER NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
    name             TEXT    NOT NULL,
    sequence         INTEGER NOT NULL,
    start_date       TEXT,
    end_date         TEXT,
    is_active        INTEGER NOT NULL DEFAULT 0,
    UNIQUE (academic_year_id, sequence)
);

CREATE TABLE student_groups (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT    NOT NULL,
    academic_year_id INTEGER NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
    UNIQUE (name, academic_year_id)
);

CREATE TABLE subjects (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL UNIQUE
);

-- -------------------------------------------------------------- personas ---
CREATE TABLE teachers (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE students (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    student_code TEXT    NOT NULL UNIQUE,
    group_id     INTEGER REFERENCES student_groups(id) ON DELETE SET NULL
);

CREATE TABLE guardians (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    relationship TEXT
);

CREATE TABLE guardian_student (
    guardian_id INTEGER NOT NULL REFERENCES guardians(id) ON DELETE CASCADE,
    student_id  INTEGER NOT NULL REFERENCES students(id)  ON DELETE CASCADE,
    PRIMARY KEY (guardian_id, student_id)
);

-- La asignacion docente es la unidad de autorizacion del sistema: un profesor
-- solo puede operar sobre las asignaciones que realmente tiene.
CREATE TABLE teaching_assignments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id       INTEGER NOT NULL REFERENCES teachers(id)       ON DELETE CASCADE,
    subject_id       INTEGER NOT NULL REFERENCES subjects(id)       ON DELETE CASCADE,
    group_id         INTEGER NOT NULL REFERENCES student_groups(id) ON DELETE CASCADE,
    academic_year_id INTEGER NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
    UNIQUE (teacher_id, subject_id, group_id, academic_year_id)
);

-- ------------------------------------------------------------ preinformes ---
CREATE TABLE reports (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_year_id INTEGER NOT NULL REFERENCES academic_years(id)   ON DELETE CASCADE,
    period_id        INTEGER NOT NULL REFERENCES academic_periods(id) ON DELETE CASCADE,
    name             TEXT    NOT NULL,
    kind             TEXT    NOT NULL DEFAULT 'preinforme'
                     CHECK (kind IN ('preinforme','final')),
    report_date      TEXT,
    status           TEXT    NOT NULL DEFAULT 'borrador'
                     CHECK (status IN ('borrador','publicado')),
    published_at     TEXT,
    created_by       INTEGER REFERENCES users(id),
    created_at       TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- --------------------------------------------------- actividades y notas ---
CREATE TABLE activities (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id   INTEGER NOT NULL REFERENCES teaching_assignments(id) ON DELETE CASCADE,
    period_id       INTEGER NOT NULL REFERENCES academic_periods(id)     ON DELETE CASCADE,
    name            TEXT    NOT NULL,
    kind            TEXT    NOT NULL DEFAULT 'taller'
                    CHECK (kind IN ('taller','quiz','parcial','proyecto','otro')),
    weight          REAL    NOT NULL DEFAULT 10,
    due_date        TEXT,
    allows_recovery INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- Una calificacion vive en tres estados: borrador -> publicada -> final.
CREATE TABLE grades (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id         INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    student_id          INTEGER NOT NULL REFERENCES students(id)   ON DELETE CASCADE,
    score               REAL,
    status              TEXT    NOT NULL DEFAULT 'borrador'
                        CHECK (status IN ('borrador','publicada','final')),
    feedback_category   TEXT,
    feedback_text       TEXT,
    is_missing          INTEGER NOT NULL DEFAULT 0,
    recovery_status     TEXT    NOT NULL DEFAULT 'ninguna'
                        CHECK (recovery_status IN ('ninguna','disponible','pendiente','realizada')),
    published_report_id INTEGER REFERENCES reports(id) ON DELETE SET NULL,
    published_at        TEXT,
    updated_by          INTEGER REFERENCES users(id),
    created_at          TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    updated_at          TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    UNIQUE (activity_id, student_id)
);

-- ------------------------------------------------- solicitudes de revision ---
CREATE TABLE review_requests (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    grade_id         INTEGER NOT NULL REFERENCES grades(id)   ON DELETE CASCADE,
    student_id       INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    reason_code      TEXT    NOT NULL,
    message          TEXT,
    status           TEXT    NOT NULL DEFAULT 'pendiente'
                     CHECK (status IN ('pendiente','revisada','aceptada','rechazada')),
    teacher_response TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    resolved_at      TEXT,
    resolved_by      INTEGER REFERENCES users(id)
);

-- --------------------------------------------------- auditoria y soporte ---
CREATE TABLE audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    user_id     INTEGER,
    user_name   TEXT,
    role        TEXT,
    action      TEXT    NOT NULL,
    entity      TEXT,
    entity_id   INTEGER,
    description TEXT,
    old_value   TEXT,
    new_value   TEXT
);

CREATE TABLE backups (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    filename        TEXT    NOT NULL,
    size_bytes      INTEGER NOT NULL DEFAULT 0,
    status          TEXT    NOT NULL DEFAULT 'completado',
    created_by_name TEXT,
    kind            TEXT    NOT NULL DEFAULT 'manual'
);

CREATE TABLE settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE feedback_templates (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER REFERENCES teachers(id) ON DELETE CASCADE,
    text       TEXT    NOT NULL
);

-- --------------------------------------------------------------- indices ---
CREATE INDEX idx_grades_activity     ON grades(activity_id);
CREATE INDEX idx_grades_student      ON grades(student_id);
CREATE INDEX idx_grades_status       ON grades(status);
CREATE INDEX idx_activities_assign   ON activities(assignment_id, period_id);
CREATE INDEX idx_students_group      ON students(group_id);
CREATE INDEX idx_assignments_teacher ON teaching_assignments(teacher_id);
CREATE INDEX idx_audit_created       ON audit_log(created_at DESC);
CREATE INDEX idx_reviews_status      ON review_requests(status);
