"""
Services module for AcademyNotes.

This layer contains database access routines and business logic used
by the Flask application and the tkinter UI.  Functions are generally
small wrappers around SQL queries with some validation.
"""

import models
import db

#    SEARCH

def get_all_asignatures():
    """
    Return a list of all asignatures in the system.

    Each element is a dict containing ``id`` and ``name``.  The
    results are ordered alphabetically by name.
    """
    connection = db.connect()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id_asignature, name FROM asignature ORDER BY name ASC ")
        rows = cursor.fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]
    finally:
        cursor.close()
        connection.close()

def get_student_asignatures(id_student: int):
    """
    Obtain the asignatures associated with a given student.

    Args:
        id_student: primary key of the student.

    Returns:
        A list of dicts with ``id_asignature`` and ``name`` fields.  If
        the student has duplicate entries they are filtered out.
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    try:
        cursor.execute("SELECT asig.id_asignature, asig.name FROM asignature asig INNER JOIN student_asignature s_a ON asig.id_asignature = s_a.id_asignature INNER JOIN student st ON s_a.id_student = st.id_student WHERE st.id_student = ?", (id_student,))
        rows = cursor.fetchall()
        print("rows", rows) 
    finally:
        cursor.close() 
        conection.close() 
        asignatures = []
        asignatures_dic = [{"id_asignature": r[0], "name": r[1]} for r in rows]
        for asignature in asignatures_dic:
            if asignature not in asignatures:
                asignatures.append(asignature)
        print("asignatures_dic", asignatures_dic, "asignatures", asignatures)
        return asignatures

def search_teacher_grade(id_user_teacher: int):
    """
    Look up the grade associated with a teacher user account.

    Returns the grade id or ``None`` if no mapping exists.
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    try:
        cursor.execute(
            "SELECT t.id_grade "
            "FROM teacher_asignature t JOIN users u ON u.id_user = t.id_user "        
            "WHERE u.id_user = ?", (id_user_teacher,)
                        )
        id_grade = cursor.fetchone()
    finally: 
        cursor.close() 
        conection.close()
    return id_grade[0] if id_grade else None

def search_teacher_asignature(id_user:int, id_grade:int):
    """
    Return the asignature id that a given teacher teaches for a grade.

    Args:
        id_user: user id of the teacher.
        id_grade: grade identifier.

    Returns:
        Integer id of the asignature or ``None``.
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    try:
        cursor.execute("SELECT id_asignature FROM teacher_asignature WHERE id_user = ? AND id_grade = ?", (id_user, id_grade))
        id_asignature = cursor.fetchone() 
    finally: 
        cursor.close() 
        conection.close() 
    return id_asignature[0] if id_asignature else None

def search_name_asignature_teacher(id_asignature:int):
    """
    Fetch the name of an asignature given its primary key.

    If the asignature cannot be found a default list containing
    ``"Asignatura no encontrada"`` is returned.
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    
    try:
            cursor.execute("SELECT name FROM asignature WHERE id_asignature = ?", (id_asignature,))
            name_asignature = cursor.fetchone() 
    finally: 
        cursor.close() 
        conection.close() 
    if not name_asignature:
        name_asignature = ["Asignatura no encontrada",]
    return name_asignature 

def get_id_student_by_id_user(id_user_student: int):
    """
    Given a user id return the corresponding student id.

    Returns a single-element tuple from the SQL query or ``None`` if no
    student exists.
    """
    conection = db.connect()
    cursor = conection.cursor() 
    try:
        cursor.execute("SELECT id_student FROM student WHERE id_user = ?", (id_user_student,))
        id_student = cursor.fetchone() 
    finally:
        cursor.close() 
        conection.close() 
    return id_student if id_student else None

def get_id_user_by_id_teacher(id_teacher: int):
    """
    Look up the user id associated with a teacher record.

    Returns a tuple or ``None`` when the teacher id is not found.
    """
    conection = db.connect()
    cursor = conection.cursor() 
    try:
        cursor.execute("SELECT id_user FROM teacher WHERE id_teacher = ?", (id_teacher,))
        row = cursor.fetchone() 
    finally:
        cursor.close() 
        conection.close() 
    return row if row else None

def get_teachers():
    """
    Retrieve a de‑duplicated list of all teachers in the system.

    Each list element is a dict with ``id`` and ``name``. Returns
    ``None`` if no teachers exist.
    """
    conection = db.connect()
    cursor = conection.cursor() 
    try:
        cursor.execute("SELECT t.id_teacher, u.username "
                        "FROM teacher t JOIN users u ON t.id_user = u.id_user "
                        "ORDER BY u.username ASC ",
                        )
        rows = cursor.fetchall() 
        if not rows:
            return None 
    finally:
        cursor.close() 
        conection.close() 
    teachers = []
    teachers_dic = [
            {"id": row[0], "name": row[1]} for row in rows
            ]
    for teacher in teachers_dic:
        if teacher not in teachers:
            teachers.append(teacher)
    return teachers

def get_student_for_teacher(id_grade: int):
    """
    Get students who belong to a particular grade.

    Used by teacher views to display their class roster.
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    try:
        cursor.execute(
            "SELECT s.id_student, s.id_user, u.username " 
            "FROM student s JOIN users u ON s.id_user = u.id_user "
            "WHERE s.id_grade = ? "
            "ORDER BY u.username ASC ",
            (id_grade,)
                        )
        rows = cursor.fetchall()
        if not rows:
            return None
    finally:
        cursor.close() 
        conection.close() 
    students = [
        {"id_student": row[0], "id_user": row[1], "username": row[2]} for row in rows
    ]
    return students 

def get_grades():
    """
    Return a list of all grades in the database.  Elements are dicts
    with ``id`` and ``name``.
    """
    conection = db.connect()
    cursor = conection.cursor()
    
    try:
        cursor.execute("SELECT id_grade, name FROM grade ORDER BY name ASC ")
        rows = cursor.fetchall()
        if not rows:
            return None
    finally:
        cursor.close() 
        conection.close()
    grades = [{'id': row[0], 'name': row[1]} for row in rows]
    return grades

def get_students():
    """
    Retrieve all student records, ordered by username.

    Returns a list of dictionaries containing ``id`` and ``name``.
    """
    conection = db.connect()
    cursor = conection.cursor() 
    try:
        cursor.execute("SELECT s.id_student, u.username "
                        "FROM student s JOIN users u ON s.id_user = u.id_user "
                        "ORDER BY u.username ASC ",
                        )
        rows = cursor.fetchall() 
        if not rows:
            return None 
    finally:
        cursor.close() 
        conection.close() 
    students = [
                {"id": row[0], "name": row[1]} for row in rows
            ]
    return students

def get_users():
    """
    Return all user accounts from the ``users`` table.

    Each item in the returned list includes ``id_user``, ``username``
    and ``role``.
    """
    conection = db.connect()
    cursor = conection.cursor()
    
    try:
        cursor.execute("SELECT id_user, username, role FROM users ORDER BY username ASC ")
        rows = cursor.fetchall()
        if not rows:
            return None
        print(rows)
    finally:
        cursor.close() 
        conection.close()
    users = [{'id_user': row[0], 'username': row[1], 'role': row[2]} for row in rows]
    return users

def get_students_undergraduate():
    """
    Fetch students who have not yet been assigned to a grade (i.e.,
    their ``id_grade`` is NULL).
    """
    conection = db.connect()
    cursor = conection.cursor()
    
    try:
        cursor.execute("SELECT s.id_student, u.username "
                    "FROM student s JOIN users u ON s.id_user = u.id_user " 
                    "Where s.id_grade is Null "
                    "ORDER BY u.username ASC "
                    )
        rows = cursor.fetchall()
        if not rows:
            return None
        print(rows)
    finally:
        cursor.close() 
        conection.close()
    student_undergraduate = [{'id': row[0], 'name': row[1]} for row in rows]
    return student_undergraduate

def get_grades_for_new_teacher():
    """
    Return combinations of asignatures and grades that are not yet
    associated with any teacher.  Results are grouped by asignature in
    the returned dictionary.
    """
    conection = db.connect()
    cursor = conection.cursor()
    try:
        cursor.execute("SELECT  a.id_asignature, a.name, g.id_grade, g.name "
                    "FROM asignature a "
                    "CROSS JOIN grade g "
                    "WHERE NOT EXISTS ("
                        "SELECT 1 "
                        "FROM teacher_asignature ta "
                        "WHERE ta.id_grade = g.id_grade "
                        "AND ta.id_asignature = a.id_asignature"
                    ")"
                    "ORDER BY a.name, g.name ASC "
                    )
        rows = cursor.fetchall()
        if not rows:
            return None
    finally:
        cursor.close() 
        conection.close()
    asignature_grades = {}

    for row in rows:
        name_grade = row[3]
        id_grade = row[2]
        name_asignature = row[1]
        id_asignature = row[0]
        
        if id_asignature not in asignature_grades:
            asignature_grades[id_asignature] = {
                'id': id_asignature,
                'name': name_asignature,
                'grades': []
            }
        
        asignature_grades[id_asignature]['grades'].append({'id': id_grade, 'name': name_grade})
    return asignature_grades

def get_grades_for_actually_teacher_by_asignature():
    """
    Build a nested mapping of asignatures to their teachers and the
    grades each teacher covers.
    """
    conection = db.connect()
    cursor = conection.cursor()
    try: #t1 grado t2 ta t3 u 
        cursor.execute("SELECT ta.id_teacher, u.username, g.id_grade, g.name, ta.id_asignature, a.name "
                    "FROM grade g "
                    "INNER JOIN teacher_asignature ta ON g.id_grade = ta.id_grade "
                    "INNER JOIN users u ON ta.id_user = u.id_user "
                    "INNER JOIN asignature a ON ta.id_asignature = a.id_asignature "
                    #"WHERE ta.id_teacher = ? AND ta.id_asignature = ? "
                    "ORDER BY u.username ASC ",
                    #(id_teacher, id_asignature)
                    )
        rows = cursor.fetchall()
        if not rows:
            return None
    finally:
        cursor.close() 
        conection.close()
    teacher_grades = {}

    for row in rows:
        name_asignature = row[5]
        id_asignature = row[4]
        name_grade = row[3]
        id_grade = row[2]
        name_teacher = row[1]
        id_teacher = row[0]
        
        if id_asignature not in teacher_grades:
            teacher_grades[id_asignature] = {
                'id': id_asignature,
                'name': name_asignature,
                'teachers': []  
            }
        if id_teacher not in [t['id'] for t in teacher_grades[id_asignature]['teachers']]:
            teacher_grades[id_asignature]['teachers'].append({
                'id': id_teacher,
                'name': name_teacher,
                'grades': []  
            })
        if id_grade not in [g['id'] for t in teacher_grades[id_asignature]['teachers'] for g in t['grades']]:
            for teacher in teacher_grades[id_asignature]['teachers']:
                if teacher['id'] == id_teacher:
                    teacher['grades'].append({'id': id_grade, 'name': name_grade})
        else:
            for teacher in teacher_grades[id_asignature]['teachers']:
                if teacher['id'] == id_teacher:
                    if id_grade not in [g['id'] for g in teacher['grades']]:
                        teacher['grades'].append({'id': id_grade, 'name': name_grade})
    return teacher_grades

def get_notes_last_modified(id_student: int):
    """
    return last note
    """
    
    conection = db.connect()
    cursor = conection.cursor()
    
    try:
        cursor.execute("SELECT note FROM student_asignature WHERE id_student = ? ORDER BY last_update_at  DESC LIMIT 1 ", (id_student,))
        rows = cursor.fetchall()
        if not rows:
            return None
    finally:
        cursor.close() 
        conection.close()
    id_note = [row[0] for row in rows]
    print(id_note[0])
    return id_note[0]
# VALIDATION

def sign_up_validation(option:str, name:str, password:str):
    """
    Validate a login attempt from the command‑line UI.

    This helper was originally written for a console menu and determines
    whether the supplied ``name``/``password`` correspond to a student or
    teacher.  The ``option`` argument should be ``"t"`` for teacher or
    ``"s"`` for student.  Depending on the role it may return additional
    identifiers used by the caller.
    """
#    option = input("Are you a teacher or a student? (t/s): ")
    
    match option:
        case "t":
#           name = input("Enter your name: ")
#           password = input("Enter your password: ")
            validation_sing_up = validate_sing_up_teacher(name, password)
            if validation_sing_up:
                get_student_asignatures() 
                try:
                    # asignature_teacher = int(input("Enter your asignature by ID(ej: 1): "))
                    id_teacher = get_teachers(name, password)
                    id_asignatura = search_teacher_asignature(id_teacher)
                    print(id_teacher, id_asignatura, name, password)
                    if id_asignatura is not None:
                        validate_asignature_teacher = validate_teacher_asignature(id_teacher, id_asignatura)
                        print(validate_asignature_teacher)
                        if validate_asignature_teacher:
                        #home_teacher(id_teacher, name, asignature_teacher)
                            return True, id_teacher, id_asignatura
                        else:
                            print("You are not registered for this asignature, please sign up again.")
                            return False
                    else:
                        print("You are not registered for any asignature, please sign up again.") 
                        return False
                except ValueError:
                    print("Invalid ID, please try again.")
                    return False
            else:
                    print("You are not registered, please sign up as a student.")
                    return False
                
        case "s":
#            name = input("Enter your name: ")
#           password = input("Enter your password: ")
            validation_sing_up = validate_sing_up_student(name, password)
            id_student = get_id_student_by_id_user(name, password)
            if validation_sing_up and id_student is not None:
                return True, id_student[0]
            else:
                print("You are not registered, please sign up as a student.")
                return False
        case _:
            print("Invalid option, please try again.")

def validate_teacher_asignature(id_teacher:int, id_asignature:int):
    """
    Check whether a teacher is assigned to a particular asignature.

    Returns ``True`` if the record exists, ``False`` otherwise.
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    try:
        cursor.execute("SELECT * FROM teacher_asignature WHERE id_teacher = ? AND id_asignature = ?", (id_teacher, id_asignature))
        teacher_asignature = cursor.fetchone() 
    finally: 
        cursor.close() 
        conection.close()
    if teacher_asignature:
        return True
    else:
        return False

def validate_sing_up_teacher(name:str, password:str):
    """
    Verify that a teacher credentials combination exists.
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    try: 
        cursor.execute("SELECT id_teacher FROM teacher WHERE name = ? AND password = ?", (name, password))
        id_teacher = cursor.fetchone() 
    finally: 
        cursor.close() 
        conection.close()  
    return True if id_teacher else False

def validate_sing_up_student(name:str, password:str):
    """
    Verify that a student credentials combination exists.
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    try: 
        cursor.execute("SELECT id_student FROM student WHERE name = ? AND password = ?", (name, password))
        id_student = cursor.fetchone() 
    finally: 
        cursor.close() 
        conection.close() 
    return True if id_student else False

# REGISTER

def add_user(name: str, password: str, role: str, institution: str):
    conect = db.connect()
    cursor = conect.cursor()
    
    try:
        cursor.execute("INSERT INTO users(username, password, role, institution) VALUES (?,?,?,?)", (name, password, role, institution))
        insert_id = cursor.lastrowid
    finally:
        cursor.close()
        conect.commit()
    return insert_id

def register_menu():
    """
    Simple console menu allowing a user to register as a teacher or
    student.  This was used during early development and is not invoked
    from the Flask or tkinter interfaces.
    """
    print("""
1. Login as Teacher
2. Login as Student""")
    option = input("Select an option: ")
    
    match option:
        case "1":
            name = input("Enter your name: ")
            password = input("Enter your password: ")
            get_student_asignatures()
            asignature_teacher = int(input("Enter your asignature by ID(ej: 1): "))
            id_teacher = register_teacher(name, password) 
            if id_teacher is int:
                register_asignature_teacher(id_teacher[1], asignature_teacher)
                home_teacher(id_teacher[1], name, asignature_teacher)
        case "2":
            name = input("Enter your name: ")
            password = input("Enter your password: ")
            id_student = register_student(name, password) 
            if id_student is not None:
                home_student(name, id_student)
        case _:
            print("Invalid option, please try again.")

def register_asignature_teacher(id_teacher: int, id_asignature: int):
    """
    Persist a link between a teacher and an asignature.

    The operation uses ``INSERT OR IGNORE`` to avoid duplicates and
    always returns ``True``.
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    
    try:
        cursor.execute("INSERT OR IGNORE INTO teacher_asignature(id_teacher, id_asignature) VALUES (?, ?)", (id_teacher, id_asignature))
        conection.commit() 
    finally:
        cursor.close() 
        conection.close() 
        return True

def add_student(id_user: int, id_grade: int):
    """
    Create a new student record linking a user to a grade.

    Returns the newly inserted student id (``0`` if ignored).
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    try: 
        cursor.execute("INSERT OR IGNORE INTO student(id_user, id_grade) VALUES (?, ?)", (id_user, id_grade))
        id_student = cursor.lastrowid 
        conection.commit() 
    finally: 
        cursor.close() 
        conection.close() 
    return id_student

def add_teacher(id_user: int):
    """
    Add a teacher record for the supplied user id.

    Returns a tuple ``(True, id_teacher)`` where ``id_teacher`` is the
    newly created primary key.
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    
    try:
        cursor.execute("INSERT OR IGNORE INTO teacher(id_user) VALUES (?)", (id_user,))
        id_teacher = cursor.lastrowid
        conection.commit() 
    finally:
        cursor.close() 
        conection.close()
    return True, id_teacher

def add_asignature(name: str):
    """
    Insert a new asignature with the given name.

    Returns the inserted row id.
    """
    conect = db.connect()
    cursor = conect.cursor()
    try:
        cursor.execute("INSERT INTO asignature(name) VALUES (?)", (name,))
        insert_id = cursor.lastrowid
    finally:
        cursor.close()
        conect.commit()
    return insert_id

def sync_teacher_asignature(id_teacher:int, id_asignature:int, id_user:int, id_grade:int):
    """
    Record a teacher‑asignature‑grade relationship.

    Returns the database row id of the inserted mapping.
    """
    conect = db.connect()
    cursor = conect.cursor()
    
    try:
        cursor.execute("INSERT INTO teacher_asignature(id_teacher, id_asignature, id_user, id_grade) VALUES (?,?,?,?)", (id_teacher, id_asignature, id_user, id_grade))
        insert_id = cursor.lastrowid
    finally:
        cursor.close()
        conect.commit()
    return insert_id

def add_grade_for_student(id_grade: int, id_student: int):
    """
    Assign or update a student's grade.

    Returns the cursor's ``lastrowid`` (0 for updates).
    """
    conect = db.connect()
    cursor = conect.cursor()
    try:
        cursor.execute("UPDATE student SET id_grade = ? WHERE id_student = ?", (id_grade, id_student))
        insert_id = cursor.lastrowid
    finally:
        cursor.close()
        conect.commit()
    return insert_id

def add_grade(name: str):
    """
    Create a new grade with the given name and return its id.
    """
    conect = db.connect()
    cursor = conect.cursor()
    try:
        cursor.execute("INSERT INTO grade(name) VALUES (?)", (name,))
        insert_id = cursor.lastrowid
    finally:
        cursor.close()
        conect.commit()
    return insert_id

def add_column(col_name: str, id_grade:int, id_asignature:int, id_student:int):
    """
    Add a new column entry for a student's asignature grade journal.

    ``col_name`` is typically the activity or exam name.  The function
    returns the newly created row id.
    """
    conect = db.connect()
    cursor = conect.cursor()
    try:
        cursor.execute("INSERT INTO student_asignature(col_name, id_grade, id_asignature, id_student) VALUES (?,?,?,?)", (col_name, id_grade, id_asignature, id_student))
        insert_id = cursor.lastrowid
    finally:
        cursor.close()
        conect.commit()
    return insert_id

# HOME 

def home_teacher(id_teacher:int, name:str, asignature_teacher:int):
    """
    Command‑line loop that allows a teacher to inspect and modify
    student notes interactively.
    """
    while True:
        print(f"welcome {name}")
        get_student_for_teacher()
        
        try:
            student = int(input("Select a student by ID: "))
            notes_by_student(student, asignature_teacher)
            promedio_asignature = promedio_notes(student, asignature_teacher)
            print(f"Your promedio is: {promedio_asignature}")
            print("""
1. add note
2. update note
3. delete note
4. exit
""")
            option = input("Select an option: ")
    
            match option:
                case "1":
                    add_note(student, asignature_teacher, float(input("Enter the note: ")))
                case "2":
                    update_note(asignature_teacher, student, float(input("Enter the ID note to update: ")), float(input("Enter the new note: ")))
                case "3":
                    delete_note(student, asignature_teacher, float(input("Enter the ID note to delete: ")))
                case "4": 
                    print("adiós pues")
                    break
                case _:
                    print("Invalid option, please try again.")
        except ValueError:
            print("Invalid ID, please try again.")

def home_student(name:str, id_student: int):
    """
    Simple interactive function for a student to view their notes from
    the console.  Not used by the web or UI frontends.
    """
    # print(f"¡Welcome {name}!")
    # search_asignatures()
    try:
        asignature_student = int(input("Select your asignature by ID(ej: 1): "))
        notes_by_student(asignature_student, id_student)
        promedio_asignature = promedio_notes(id_student, asignature_student)
        print(f"Your promedio is: {promedio_asignature}")
    except ValueError:
        print("Invalid ID, please try again.")

# NOTES

def delete_note(id_student:int, id_asignature:int, id_note:int, col_name: str):
    """
    Delete a specific note row for a student.

    Returns the updated average for the student/asignature combination.
    """
    conection = db.connect()
    cursor = conection.cursor()
    try:
        cursor.execute("DELETE FROM student_asignature WHERE id_student = ? AND id_asignature = ? AND id = ? AND col_name = ? AND last_update_at = DATATIME(CURRENT_TIMESTAMP)", (id_student, id_asignature, id_note, col_name))
        conection.commit()
    finally:
        cursor.close()
        conection.close()
        promedio = promedio_notes(id_student, id_asignature)
        return promedio

def update_note(id_asignature: int, id_student: int, id_note: int, new_note: float, col_name: str):
    """
    Update the value of an existing note entry.

    The function returns the recalculated average after the update.
    """
    print(id_asignature, id_student, id_note, new_note, col_name, 'services')
    conection = db.connect()
    cursor = conection.cursor()
    try:
        cursor.execute(
            "UPDATE student_asignature SET note = ?, last_update_at = CURRENT_TIMESTAMP WHERE id = ? AND id_asignature = ? AND id_student = ? AND col_name = ?",
            (new_note, id_note, id_asignature, id_student, col_name)
        )
        conection.commit()
    finally:
        cursor.close()
        conection.close()
        promedio = promedio_notes(id_student, id_asignature)
        return promedio

def add_note(id_student: int, id_asignature: int, id_grade:int, note: float, col_name: str):
    """
    Insert a student note and return the inserted id along with the
    updated average.
    """
    conection = db.connect()
    cursor = conection.cursor()
    try:
        cursor.execute("INSERT INTO student_asignature(id_student, id_asignature, id_grade, note, col_name) VALUES (?,?,?,?,?)", (id_student, id_asignature, id_grade, note, col_name))
        inserted_id = cursor.lastrowid
        conection.commit()
    finally:
        cursor.close()
        conection.close()
        promedio = promedio_notes(id_student, id_asignature)
    return inserted_id, promedio

def initialize_asignatures(asignatures: list[models.Asignature]):
    """
    Bulk insert a list of :class:`models.Asignature` objects into the
    database, ignoring duplicates.
    """
    conection = db.connect() 
    cursor = conection.cursor()
    try:
        for asignature in asignatures:
            cursor.execute("INSERT OR IGNORE INTO asignature(name) VALUES (?)", (asignature.name,))
            conection.commit() 
    finally:
        cursor.close() 
        conection.close() 
    return True

def promedio_notes(id_student:int, asignature:int):
    """
    Calculate and return the average of all notes for a student in a
    given asignature.
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    try: 
        cursor.execute("SELECT AVG(note) FROM student_asignature WHERE id_student = ? AND id_asignature = ?", (id_student, asignature))
        promedio = cursor.fetchone()
    finally:
        cursor.close() 
        conection.close()
    if promedio[0] is not None:
        avg_value = promedio[0] 
    else:
        avg_value = 0.0
    return float(avg_value)

def get_notes_by_asignature(id_asignature: int, id_grade:int):
    """
    Returns all grades for a given subject.
    Returns a list of dicts: {id, id_student, id_asignature, note, col_name, created_at}
    """
    conection = db.connect()
    cursor = conection.cursor()
    try:
        cursor.execute(
            "SELECT id, id_student, id_asignature, note, col_name, created_at FROM student_asignature WHERE id_asignature = ? AND id_grade = ? ORDER BY created_at",
            (id_asignature, id_grade)
        )
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conection.close()
    notes = []
    for row in rows:
        notes.append({
            "id": row[0],
            "id_student": row[1],
            "id_asignature": row[2],
            "note": row[3],
            "col_name": row[4],
            "created_at": row[5]
        })
    return notes

def get_teacher_asignatures(id_user: int, id_grade: int):
    """
    Returns list of subjects (id, name) associated with the teacher user (id_user).     
    """
    conection = db.connect()
    cursor = conection.cursor()
    try:
        cursor.execute(
            "SELECT a.id_asignature, a.name FROM teacher_asignature t JOIN asignature a ON t.id_asignature = a.id_asignature WHERE t.id_user = ? AND t.id_grade = ?",
            (id_user, id_grade)
        )
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conection.close()
    asignatures = [{"id": r[0], "name": r[1]} for r in rows]
    return asignatures

def get_teacher_grades(id_user: int):
    """
    Returns list of grades (id, name) associated with the teacher user (id_user).
    """
    conection = db.connect()
    cursor = conection.cursor()
    
    cursor.execute("SELECT g.id_grade, g.name FROM grade g JOIN teacher_asignature t ON g.id_grade = t.id_grade WHERE t.id_user = ?", (id_user,))
    rows = cursor.fetchall()
    
    cursor.close()
    conection.close()
    
    grades = []
    for grades_d in rows:
        grades_dic = [{"id": grades_d[0], "name": grades_d[1]}]
        for grade in grades_dic:
            if grade not in grades:
                grades.append(grade)
    return grades

def get_notes_by_student(id_asignature: int, id_student: int):
    """
    Retrieve note entries for a specific student and asignature.

    Returns a list of dictionaries containing note details.
    """
    conection = db.connect() 
    cursor = conection.cursor() 
    try:
        cursor.execute("SELECT id, id_student, id_asignature, note, col_name, created_at FROM student_asignature WHERE id_asignature=? AND id_student=?", (id_asignature, id_student))
        rows = cursor.fetchall()
    finally: 
        cursor.close() 
        conection.close() 
        notes = []
        for row in rows:
            notes.append({
                "id": row[0],
                "id_student": row[1],
                "id_asignature": row[2],
                "note": row[3],
                "col_name": row[4],
                "created_at": row[5]
            })
    return notes

