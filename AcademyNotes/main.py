# http://127.0.0.1:5000/
"""
Main application module for AcademyNotes.

Defines Flask routes and auxiliary functions. Each route handles
JSON requests or renders templates, delegating database operations to
the `services` package.
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from db import connect
from flask_cors import CORS  
import traceback
import services

app = Flask(__name__)
app.secret_key = "cambiar_en_prod"
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5500"]}}, supports_credentials=True)

@app.route("/add_note_js", methods=["POST"])
def add_note_js():
    """
    Handle an AJAX request to add a student note.

    The client is expected to send a JSON payload with the following
    keys::

        {
            "student_id": int,
            "asignature_id": int,
            "id_grade": int,
            "note": float,
            "col_name": str
        }

    Performs basic validation on the parameters and delegates to
    :func:`services.add_note` to persist the information.  Returns a
    JSON response indicating success or an error message with an
    appropriate HTTP status code.
    """
    data = request.get_json(silent=True or {})
    student_id = data.get("student_id")
    asignature_id = data.get("asignature_id")
    id_grade = data.get("id_grade")
    note = data.get("note")
    col_name = data.get("col_name")
    if not student_id or asignature_id is None or note is None or col_name is None or id_grade is None:
        return jsonify({"message": "Parametros incompletos"}), 400
    if float(note) > 5 or float(note) < 1:
        #print("DEBUG: if note")
        return jsonify({"message": "La nota debe ser superior a 1 e inferior a 5"}), 400
    try:
        #print(int(student_id), "id_student", int(asignature_id), "id_asignature", int(id_grade), "id_grade", float(note), "note", "col name", col_name)
        inserted_id, promedio = services.add_note(int(student_id), int(asignature_id), int(id_grade), float(note), col_name)
        return jsonify({"ok": True, "id": inserted_id, "promedio": promedio}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/add_user_js', methods=['POST'])
def add_user_js():
    """
    Accepts a POST request to create a new user record.

    The JSON body must contain ``name``, ``password``, ``role`` and
    ``institution`` fields.  On success, the newly created user id is
    returned.  Any missing field or an exception from the service layer
    results in a JSON error response.
    """
    data = request.get_json(silent=True or {})
    username = data.get("name")
    password = data.get("password")
    role = data.get("role")
    institution = data.get('institution')
    if not username or not password or not role or institution is None:
        return jsonify({"message": "Parametros incompletos"}), 400
    try:
        inserted_id = services.add_user(username, password, role, institution)
        return jsonify({"ok": True, "id": inserted_id}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/add_teacher_js', methods=['POST'])
def add_teacher_js():
    """
    Creates a teacher record for an existing user.

    Expected JSON payload contains ``id_user``.  The function converts
    the value to an integer and calls :func:`services.add_teacher`.
    """
    data = request.get_json(silent=True or {})
    id_user = data.get("id_user")
    if not id_user:
        return jsonify({"message": "Parametros incompletos"}), 400
    try:
        inserted_id = services.add_teacher(int(id_user))
        return jsonify({"ok": True, "id": inserted_id}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/add_student_js', methods=['POST'])
def add_student_js():
    """
    API endpoint used by the frontend to register a student.

    JSON arguments ``id_user`` and ``id_grade`` are required.  If the
    values are present the service layer is invoked to create the
    student record.
    """
    data = request.get_json(silent=True or {})
    id_user = data.get("id_user")
    id_grade = data.get('id_grade')
    if not id_user or id_grade is None:
        return jsonify({"message": "Parametros incompletos"}), 400
    try:
        inserted_id = services.add_student(int(id_user), int(id_grade))
        return jsonify({"ok": True, "id": inserted_id}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/update_note_js", methods=["POST"])
def update_note_js():
    """
    Update an existing note for a student.

    The request body must include ``student_id``, ``asignature_id``,
    ``note_id`` and ``note``.  After validating the inputs the
    handler calls :func:`services.update_note` and returns the new
    average.
    """
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    asignature_id = data.get("asignature_id")
    note_id = data.get("note_id")
    note = data.get("note")
    col_name = data.get("col_name")
    if None in (student_id, asignature_id, note_id, note):
        return jsonify({"message": "Parametros incompletos"}), 400
    try:
        promedio = services.update_note(int(asignature_id), int(student_id), int(note_id), float(note), col_name)
        return jsonify({"ok": True, "promedio": promedio}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/delete_note_js", methods=["POST"])
def delete_note_js():
    """
    Remove a previously recorded note.

    Expects ``student_id``, ``asignature_id`` and ``note_id`` in the
    JSON payload.  Delegates to :func:`services.delete_note` and
    returns the updated average on success.
    """
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    asignature_id = data.get("asignature_id")
    note_id = data.get("note_id")
    col_name = data.get("col_name")
    print(col_name, 'delete')
    if None in (student_id, asignature_id, note_id):
        return jsonify({"message": "Parametros incompletos"}), 400
    try:
        promedio = services.delete_note(int(student_id), int(asignature_id), int(note_id), col_name)
        return jsonify({"ok": True, "promedio": promedio}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/add_column_js", methods=["POST"])
def add_column_js():
    """
    Endpoint for creating a new grading column for a student.

    The request must send ``id_asignature``, ``id_grade``,
    ``col_name`` and ``id_studet`` (sic) in the JSON body.  The values
    are validated and passed through :func:`services.add_column`.
    """
    data = request.get_json(silent=True or {})
    id_asignature = data.get("id_asignature")
    id_grade = data.get("id_grade")
    col_name = data.get("col_name")
    id_student = data.get('id_studet')
    if not id_asignature or col_name is None or id_grade is None or id_student is None:
        return jsonify({"message": "Parametros incompletos"}), 400
    try:
        print(int(id_asignature), "id_asignature", int(id_grade), "id_grade", "col name", col_name)
        inserted_id = services.add_column( col_name, int(id_grade), int(id_asignature), int(id_student))
        return jsonify({"ok": True, "id": inserted_id}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

def validate_user(user: str, password: str):
    """
    Check a username/password pair against the database.

    Args:
        user: the username supplied by the client.
        password: the corresponding password.

    Returns:
        A tuple of (role, id_user, name) if the credentials are valid,
        or ``(None, None)`` if they are not.  Database errors are
        caught and cause a traceback to be printed.
    """
    try:
        conection = connect() 
        cursor = conection.cursor()
        cursor.execute("SELECT id_user, role, username FROM users WHERE username = ? AND password = ?", (user, password))
        result = cursor.fetchone()
        cursor.close() 
        conection.close()
        if not result:
            return None, None
        id_user, role, name = result[0], result[1], result[2]
        return role, id_user, name 
    except Exception:
        traceback.print_exc() 
        return None, None 

@app.route("/", methods=["GET"])
def index():
    """
    Render the login page.

    This is the root route; it simply returns the ``login.html``
    template so that users can enter their credentials.
    """
    return render_template("login.html") 

@app.route("/loginJs", methods=["POST"])
def login(): 
    """
    Handle AJAX login requests from the frontend.

    Expects ``username`` and ``password`` in the JSON body.  The
    credentials are verified with :func:`validate_user`.  On success
    the user's id, role and display name are stored in the session and
    returned to the client.
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password") 
    
    if not username or not password:
        return jsonify({"success": False, "message": "username y password requeridos." })
    
    role, id_user, name = validate_user(username, password)  
       
    if id_user and role:
        session["id_user"] = id_user
        session["role"] = role 
        session["username"] = name
        
        return jsonify({"success": True, "role": role, "id": id_user, "name": name}), 200
    return jsonify({"success": False, "message": "Credenciales inválidas."}), 401

@app.route("/appTeacher")
def app_teacher(): 
    """
    Render the teacher application page.

    Redirects anonymous visitors to the login page.  Uses the
    ``appTeacher.html`` template and passes the logged‑in username.
    """
    if not session.get("id_user"):
        return redirect(url_for("index"))
    return render_template("appTeacher.html", username=session["username"]), 200

@app.route("/appStudent")
def app_student():
    """
    Render the student application page after ensuring the user is
    authenticated.
    """
    if not session.get("id_user"):
        return redirect(url_for("index"))
    return render_template("appStudent.html", username=session["username"]), 200

@app.route("/appAdministrator")
def app_administrator():
    """
    Render the administrator dashboard template.

    The username is hardcoded as "Administrador" for now.
    """
    if not session.get("id_user"):
        return redirect(url_for("index"))
    return render_template("appAdmin.html", username="Administrador"), 200

@app.route("/api/teacher/students", methods=["GET"])
def api_teacher_students():
    """
    API route returning a list of students for the currently logged-in
    teacher.

    The handler checks the session, fetches the teacher's grade and
    asignature via the services layer and then augments each student
    record with an average grade.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    id_grade = services.search_teacher_grade(session["id_user"])
    if id_grade is None:
        return jsonify({"message": "No autorizado"}), 401
    id_asignature = services.search_teacher_asignature(session["id_user"], id_grade)
    if id_asignature is None:
        return jsonify({"message": "No autorizado"}), 401
    students = services.get_student_for_teacher(id_grade)
    if students is None:
        return jsonify({"message": "No students founds"}), 404
    for i in range(len(students)):
        students[i]["average"] = services.promedio_notes(students[i]["id_student"], id_asignature)
    #print(students)
    return jsonify({"students": students}), 200 

@app.route("/api/reload_students_by_grade", methods=["GET"])
def api_reload_students_by_grade():
    """
    Reload students for a specific grade; used by the frontend when a
    grade selector changes.

    Expects ``id_grade`` as a query parameter and returns a JSON list
    of students along with the teacher's asignature id.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    id_grade = request.args.get("id_grade")
    if id_grade is None:
        return jsonify({"message": "id_grade requerido"}), 400
    id_asignature = services.search_teacher_asignature(session["id_user"], int(id_grade))
    if not id_grade:
        return jsonify({"message": "id_grade requerido"}), 400
    try:
        students = services.get_student_for_teacher(int(id_grade))
        if students is None:
            return jsonify({"message": "No students founds"}), 404
        return jsonify({"students": students, "id_asignature": id_asignature}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/teacher/notes', methods=['GET'])
def api_teacher_notes():
    """
    Return notes for a given asignature and grade.

    Query parameters ``id_asignature`` and ``id_grade`` are required.
    The service layer is called to fetch the list of notes.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    # obtener id_asignature desde query param ?id_asignature=1
    id_asignature = request.args.get('id_asignature')
    id_grade = request.args.get('id_grade')
    if not id_asignature or id_grade is None:
        return jsonify({"message": "id_asignature requerido"}), 400
    try:
        notes = services.get_notes_by_asignature(int(id_asignature), int(id_grade)) 
        return jsonify({"notes": notes}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/teacher/asignatures', methods=['GET'])
def api_teacher_asignatures():
    """
    Provide the asignatures that a teacher is responsible for.

    Uses the session's ``id_user`` to look up the grade and then fetches
    the matching asignatures via :func:`services.get_teacher_asignatures`.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    try:
        id_grade = services.search_teacher_grade(session["id_user"])
        id_grade_arg = request.args.get("id_grade")
        if id_grade_arg != id_grade:
            id_grade = id_grade_arg
        if id_grade is None:
            return jsonify({"message": "No autorizado"}), 401
        print(id_grade, "api teacher asignatures")
        asignatures = services.get_teacher_asignatures(session["id_user"], int(id_grade)) 
        return jsonify({"asignatures": asignatures}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/notes", methods=["GET"])
def api_add_notes():
    """
    Legacy endpoint for adding notes via API (non-JS).

    Expects a JSON payload containing ``id_student``, ``id_asignature``
    and ``note``.  Simply passes the values to
    :func:`services.add_note`.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    data = request.get_json(silent=True) or {}
    id_student = data.get("id_student")
    id_asignature = data.get("id_asignature")
    note = data.get("note")
    if id_student is None or id_asignature is None or note is None:
        return jsonify({"message": "Parametros incompletos"}), 400
    try:
        services.add_note(int(id_student), int(id_asignature), float(note))
        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/teacher/grades", methods=["GET"])
def api_teacher_grades():
    """
    Return the list of grades that a teacher can manage.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    try:
        grades = services.get_teacher_grades(session["id_user"])
        return jsonify({"grades": grades}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/student/asignatures", methods=["GET"])
def api_student_asignatures():
    """
    Fetch asignatures available to the logged-in student along with
    their average marks.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    try:         
        id_student = services.get_id_student_by_id_user(session["id_user"])  
        #print(id_student, "id_Student", session["id_user"], "id_user", "api student asignatures")      
        if id_student is None:
            return jsonify({"message": "id_student requerido"}), 400
        asignatures = services.get_student_asignatures(int(id_student[0]))
        for i in range (len(asignatures)):
            asignatures[i]["average"] = services.promedio_notes(int(id_student[0]), asignatures[i]["id_asignature"])        
        #print(asignatures, "asignatures con promedio")
        return jsonify({"asignatures": asignatures}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/student/notes", methods=["GET"])
def api_student_notes():
    """
    Retrieve notes for the currently logged-in student.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    try:
        id_asignature = request.args.get("id_asignature")
        if id_asignature is None:
            return jsonify({"message": "id_asignature requerido"}), 400
        id_student = services.get_id_student_by_id_user(session["id_user"])
        if id_student is None:
            return jsonify({"message": "id_student requerido"}), 400
        notes = services.get_notes_by_student(int(id_asignature), int(id_student[0]))
        return jsonify({"notes": notes}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/asignatures', methods=['GET'])
def api_asignatures():
    """
    Return all asignatures in the system.  Used by the frontend to
    populate selection controls.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    try:
        asignatures = services.get_all_asignatures() 
        return jsonify({"asignatures": asignatures}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/add_asignature_js", methods=["POST"])
def add_asignature():
    """
    Create a new asignature from a JSON request. The ``name`` field is
    required.
    """
    data = request.get_json(silent=True or {})
    name_asignature = data.get("name")
    print(name_asignature)
    if not name_asignature:
        return jsonify({"message": "Nombre de la asigntura requerido"}), 400
    try:
        inserted_id = services.add_asignature(str(name_asignature))
        return jsonify({"ok": True, "id": inserted_id}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/sync_teacher_asignature", methods=['POST'])
def sync_teacher_asugnature():
    """
    Associate a teacher with an asignature and grade.

    Expects ``id_teacher``, ``id_grade`` and ``id_asignature`` in the
    JSON body.  The function looks up the corresponding ``id_user`` and
    then calls :func:`services.sync_teacher_asignature`.
    """
    data = request.get_json(silent=True or {})
    id_teacher = data.get('id_teacher')
    id_grade = data.get('id_grade')
    id_asignature = data.get('id_asignature')
    id_user = services.get_id_user_by_id_teacher(int(id_teacher))
    print(data, id_teacher, id_grade, id_user[0])
    if not id_teacher or not id_grade or not id_user or not id_asignature:
        return jsonify({"message": "Existen campos incompletos"}), 400
    try:
        inserted_id = services.sync_teacher_asignature(int(id_teacher), int(id_asignature), id_user[0], int(id_grade))
        print(inserted_id, "id asignature")
        return jsonify({"ok": True, "id": inserted_id}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/admin/teachers", methods=["GET"])
def api_admin_teachers():
    """
    Administrator endpoint to list all teachers in the system.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    teachers = services.get_teachers()
    if teachers is None:
        return jsonify({"message": "No teachers founds"}), 404
    return jsonify({"teachers": teachers}), 200

@app.route('/api/new_teacher_asignatures', methods=['GET'])
def api_new_teacher_asignatures():
    """
    Provide a list of asignature/grade combinations that are not yet
    assigned to any teacher.  Useful for onboarding new teachers.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    try:
        asignatures = services.get_grades_for_new_teacher() 
        if asignatures is None:
            return jsonify({"message": "No asignatures founds"}), 404
        return jsonify(list(asignatures.values())), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/actually_teacher_asignatures', methods=['GET'])
def api_actually_teacher_asignatures():
    """
    Return the current mapping of teachers to asignatures and grades.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    try:
        teachers = services.get_grades_for_actually_teacher_by_asignature() 
        if teachers is None:
            return jsonify({"message": "No asignatures founds"}), 404
        return jsonify(list(teachers.values())), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/grades", methods=["GET"])
def api_grade():
    """
    List all grades in the database.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    grades = services.get_grades()
    if grades is None:
        return jsonify({"message": "No grades founds"}), 404
    return jsonify({"grades": grades}), 200

@app.route('/api/students/admin', methods=["GET"])
def api_students_admin():
    """
    Administrator API returning every student record.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    students = services.get_students()
    if students is None:
        return jsonify({"message": "No students founds"}), 404
    return jsonify({"students": students}), 200

@app.route('/api/users/admin', methods=['GET'])
def api_user_admin():
    """
    Return a list of all user accounts for administrative purposes.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    users = services.get_users()
    if users is None:
        return jsonify({"message": "No users founds"}), 404
    return jsonify({"users": users}), 200

@app.route('/api/students_undergraduate', methods=['GET'])
def api_students_undergraduate():
    """
    Fetch students who have not yet been assigned a grade.
    """
    if not session.get("id_user"):
        return jsonify({"message": "No autorizado"}), 401
    students = services.get_students_undergraduate()
    if students is None:
        return jsonify({"message": "No student founds"}), 404
    return jsonify({"students": students}), 200

@app.route("/add_grade_for_student", methods=["POST"])
def add_grade_for_student():
    """
    Assign a grade to an existing student.

    The JSON body must contain ``id_grade`` and ``id_student``.
    """
    data = request.get_json(silent=True or {})
    id_grade = data.get("id_grade")
    id_student = data.get("id_student")
    if not id_grade or not id_student:
        return jsonify({"message": "Campos incompletos"}), 400
    try:
        inserted_id = services.add_grade_for_student(int(id_grade), int(id_student))
        return jsonify({"ok": True, "id": inserted_id}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/add_grade_js", methods=["POST"])
def add_grade():
    """
    Create a new grade entry via REST.

    Expects ``name`` field in the JSON payload.
    """
    data = request.get_json(silent=True or {})
    name_grade = data.get("name")
    print(name_grade)
    if not name_grade:
        return jsonify({"message": "Nombre del grado requerido"}), 400
    try:
        inserted_id = services.add_grade(str(name_grade))
        return jsonify({"ok": True, "id": inserted_id}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/logout")
def logout(): 
    """
    Log the current user out by clearing the session and redirecting
    to the login page.
    """
    session.clear() 
    return redirect(url_for("index"))

@app.route('/api/notes/last-update')
def last_update():
    # could read from DB or cache el tiempo de la última nota cambiada
    id_student = services.get_id_student_by_id_user(session['id_user'])
    if id_student is None:
        return jsonify({'message': 'student not found'})
    return jsonify({ 'last': services.get_notes_last_modified(id_student[0])})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)