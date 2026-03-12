"""
Database utilities for the AcademyNotes application.

Provides connection helpers, schema creation and simple inspection
functions used by other modules.
"""

import sqlite3 
# from multiprocessing.forkserver import connect_to_new_process

def connect():
    """
    Open a connection to the SQLite database file ``notes.db``.

    The caller is responsible for closing the returned connection
    object.

    Returns:
        sqlite3.Connection
    """
    conection = sqlite3.connect('notes.db')
    
    return conection

def create_table():    
    """
    Create all of the application's tables and indexes if they do not
    already exist.

    This function can be invoked at startup to ensure the schema is
    initialized.
    """
    conection = connect()
    cursor = conection.cursor()
    conection.execute("PRAGMA foreign_keys = ON")
    #Tabla central de usuarios
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL, 
                    role TEXT NOT NULL DEFAULT 'student',
                    institution TEXT,
                    created_at DATE DEFAULT (DATE('now'))
                    )""")
    #Rolles que referencia users.id_user
    cursor.execute("""CREATE TABLE IF NOT EXISTS teacher(
                    id_teacher INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_user INTEGER UNIQUE,
                    bio TEXT,
                    FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE
        )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student (
        id_student INTEGER PRIMARY KEY AUTOINCREMENT,
        id_user INTEGER UNIQUE NOT NULL,
        id_grade INTEGER,
        FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asignature (
        id_asignature INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS grade (
        id_grade INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    """)

    # Relación entre estudiante y asignatura que guarda notas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_asignature (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_student INTEGER NOT NULL,
        id_asignature INTEGER NOT NULL,
        id_grade INTEGER,
        note REAL,
        col_name TEXT,
        created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
        last_update_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
        FOREIGN KEY (id_student) REFERENCES student(id_student) ON DELETE CASCADE,
        FOREIGN KEY (id_asignature) REFERENCES asignature(id_asignature) ON DELETE CASCADE,
        FOREIGN KEY (id_grade) REFERENCES grade(id_grade)
        UNIQUE (id_student, id_asignature, col_name)
    );
    """)

    # Relación que indica qué asignaturas da cada teacher (mapping)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teacher_asignature (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_teacher INTEGER NOT NULL,
        id_asignature INTEGER NOT NULL,
        id_user INTEGER,
        id_grade INTEGER,
        FOREIGN KEY (id_teacher) REFERENCES teacher(id_teacher) ON DELETE CASCADE,
        FOREIGN KEY (id_asignature) REFERENCES asignature(id_asignature) ON DELETE CASCADE,
        FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE,
        FOREIGN KEY (id_grade) REFERENCES grade(id_grade) ON DELETE CASCADE,
        UNIQUE (id_teacher, id_asignature, id_grade)
    );
    """)

    # índices para consultas frecuentes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_asignature_student ON student_asignature(id_student);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_asignature_asignature ON student_asignature(id_asignature);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")

    
    conection.commit() 
    cursor.close() 
    conection.close()

def search_tables(name_tables: list[str]):
    """
    Utility for debugging that prints the contents of the named tables.

    Args:
        name_tables: list of table names to inspect.
    """
    conection = connect() 
    cursor = conection.cursor()
    try:
        for name_table in name_tables:
            print(f"Table {name_table}:                     ")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name_table,))
            if cursor.fetchall():
                cursor.execute(f"SELECT * FROM {name_table}")
                filas = cursor.fetchall() 
                if filas:
                    columns = [description[0] for description in cursor.description]
                    print(" | ".join(columns))
                    for fila in filas:
                        print(" | ".join(str(valor) for valor in fila))
                else:
                    print(f"No data found in table {name_table}.")
            else:
                print(f"Table {name_table} does not exist.")
    finally:
        cursor.close() 
        conection.close()

def delete_table(name_table:str):
    """
    Drop a table by name.  Used during development or testing to reset
    schema state.
    """
    conection = connect()
    cursor = conection.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {name_table}")
    conection.commit()
    cursor.close()
    conection.close() 

def registrar():
    """
    Insert some sample users/students into the database.  This helper is
    only intended for initial manual testing and is invoked from the
    ``__main__`` guard at the bottom of the file.
    """
    conection = connect()
    cursor = conection.cursor()
    
    cursor.execute("INSERT INTO users (username, password, role, institution) VALUES (?,?,?,?)", ('Andres Arias', '1234', 'student', 'OVA'))
    cursor.execute("INSERT INTO student (id_user) VALUES (?)", (15,))
    cursor.execute("INSERT INTO users (username, password, role, institution) VALUES (?,?,?,?)", ('Felipe Ocampo', '1234', 'student', 'OVA'))
    cursor.execute("INSERT INTO student (id_user) VALUES (?)", (16,))
    cursor.execute("INSERT INTO users (username, password, role, institution) VALUES (?,?,?,?)", ('Juan Ocampo', '1234', 'student', 'OVA'))
    cursor.execute("INSERT INTO student (id_user) VALUES (?)", (17,))
    
    cursor.close()
    conection.commit()


if __name__ == "__main__":
    #delete_table('student_asignature')
    create_table()
    #registrar()
    search_tables([ 'users', 'teacher', 'student', 'asignature', 'grade', 'student_asignature', 'teacher_asignature'])