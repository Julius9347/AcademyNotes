const buttonAddColumn = document.getElementById("addNoteColumn");
let table = document.getElementById("studentsTable");
let students = [];
const body = document.querySelector('body');
/**
 * Carga e inserta los estudiantes en la tabla respecto al grado actual.
 * 
 * @async
 * @param {number} id_grade - ID del grado a cargar
 * @returns {Promise<Object|null>} Objeto con array de estudiantes o null si falla
 * @throws {Error} Si la respuesta del servidor no es válida
 * 
 * @example
 * const data = await loadStudents(1);
 * console.log(data.students); // [{id: 1, name: 'Juan', average: 4.5}, ...]
 */
async function loadStudents(id_grade) {
    let table = document.getElementById("studentsTable");
    const response = await fetch(`http://127.0.0.1:5000/api/reload_students_by_grade?id_grade=${encodeURIComponent(id_grade)}`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        credentials: 'include'
    });
    if (!response.ok) {
        let thead = table.querySelector('thead'); // K let -> const
        let tbody = table.querySelector('tbody'); // K let -> const
        if (thead) thead.remove();
        if (tbody) tbody.remove();
        if (!body.querySelector('#err-not-found-students')) {
            body.querySelector('#asignatureSelect').classList.add('hide');
            body.querySelector('button').classList.add('hide');
            const div = document.createElement('div');
            div.id = 'err-not-found-students';
            div.innerHTML = 'No se hallaron estudiantes. Cambie el grado.'
            body.append(div);
        }
        return null;
    }
    if (body.querySelector('#err-not-found-students')) {
        body.querySelector('#err-not-found-students').remove();
    }

    const data = await response.json();
    students = data.students || [];

    // construir tabla: thead y tbody
    let thead = table.querySelector('thead'); // K let -> const
    let tbody = table.querySelector('tbody'); // K let -> const
    if (thead) thead.remove();
    if (tbody) tbody.remove();

    thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    headerRow.innerHTML = `<th>N°</th><th id="headerNameStudents">Nombre Estudiante</th><th class="promedio-header">Promedio</th>`;
    thead.appendChild(headerRow);
    table.appendChild(thead);

    tbody = document.createElement('tbody');
    students.forEach((s, idx) => {
        const tr = document.createElement('tr');
        tr.dataset.studentId = s.id;
        const tdIndex = document.createElement('td');
        tdIndex.textContent = idx + 1;
        const tdName = document.createElement('td');
        tdName.textContent = s.name;
        const tdPromedio = document.createElement('td');
        tdPromedio.className = 'promedio-cell';
        tdPromedio.textContent = s.average != null ? s.average.toFixed(2) : 'N/A';
        tr.appendChild(tdIndex);
        tr.appendChild(tdName);
        tr.appendChild(tdPromedio);
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    return data;
};
/**
 * Recarga los estudiantes cuando la tabla es borrada y recargada.
 * 
 * Similar a `loadStudents` pero adaptada para el reinicio después de cambios
 * en el selector de grado o asignatura.
 * 
 * @async
 * @param {number} id_grade - ID del grado
 * @returns {Promise<Object|null>} Objeto con array de estudiantes actualizado o null
 * @throws {Error} Si la respuesta del servidor falla
 */
async function ReloadStudents(id_grade) {
    const response = await fetch(`http://127.0.0.1:5000/api/reload_students_by_grade?id_grade=${encodeURIComponent(id_grade)}`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        credentials: 'include'
    });
    if (!response.ok) {
        let thead = table.querySelector('thead'); // K let -> const
        let tbody = table.querySelector('tbody'); // K let -> const
        if (thead) thead.remove();
        if (tbody) tbody.remove();
        if (!body.querySelector('#err-not-found-students')) {
            body.querySelector('#asignatureSelect').classList.add('hide');
            body.querySelector('button').classList.add('hide');
            const div = document.createElement('div');
            div.id = 'err-not-found-students';
            div.innerHTML = 'No se hallaron estudiantes'
            body.append(div);
        }
        return null;
    }

    if (body.querySelector('#err-not-found-students')) {
        body.querySelector('#err-not-found-students').remove();
    }
    body.querySelector('#asignatureSelect').classList.remove('hide');
    body.querySelector('button').classList.remove('hide');

    const data = await response.json();
    students = data.students || [];

    // construir tabla: thead y tbody
    let thead = table.querySelector('thead'); // K let -> const
    let tbody = table.querySelector('tbody'); // K let -> const
    if (thead) thead.remove();
    if (tbody) tbody.remove();

    thead = document.createElement('thead');
    const headerRow = document.createElement('tr'); // J let -> const
    headerRow.innerHTML = `<th>N°</th><th id="headerNameStudents">Nombre Estudiante</th><th class="promedio-header">Promedio</th>`;
    thead.appendChild(headerRow);
    table.appendChild(thead);

    tbody = document.createElement('tbody');
    // console.log(students)
    students.forEach((s, idx) => {
        const tr = document.createElement('tr');
        tr.dataset.studentId = s.id_student;
        const tdIndex = document.createElement('td');
        tdIndex.textContent = idx + 1;
        const tdName = document.createElement('td');
        tdName.textContent = s.username;
        const tdPromedio = document.createElement('td');
        tdPromedio.className = 'promedio-cell';
        tdPromedio.textContent = s.average != null ? s.average.toFixed(2) : 'N/A';
        tr.appendChild(tdIndex);
        tr.appendChild(tdName);
        tr.appendChild(tdPromedio);
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    return data;
};
/**
 * Crea una función debounced que retrasa la ejecución.
 * 
 * Útil para evitar llamadas frecuentes (ej: al escribir en inputs).
 * Cancela las llamadas previas y ejecuta después del tiempo especificado.
 * 
 * @param {Function} fn - Función a ejecutar con retraso
 * @param {number} [wait=400] - Milisegundos a esperar antes de ejecutar
 * @returns {Function} Función debounced que recibe argumentos variádicos
 * 
 * @example
 * const debouncedSearch = debounce((query) => fetchResults(query), 500);
 * input.addEventListener('input', (e) => debouncedSearch(e.target.value));
 */
const debounce = (fn, wait = 400) => {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), wait); };
};
/**
 * Crea una nueva nota para un estudiante en el servidor.
 * 
 * Realiza una petición POST para registrar una nueva calificación.
 * 
 * @async
 * @param {number} studentId - ID del estudiante
 * @param {number} asignatureId - ID de la asignatura
 * @param {number} id_grade - ID del grado
 * @param {number} note - Calificación (1 a 5)
 * @param {string} colName - Nombre de la columna/actividad
 * @returns {Promise<Object>} Objeto con {ok: true, id: number, promedio: number}
 * @throws {Error} Si la creación de la nota fracasa
 */
async function createNote(studentId, asignatureId, id_grade, note, colName) {
    console.log(studentId, asignatureId, id_grade, note, colName)
    const payload = { student_id: Number(studentId), asignature_id: Number(asignatureId), id_grade: Number(id_grade), note: parseFloat(note), col_name: colName };
    const res = await fetch('http://127.0.0.1:5000/add_note_js', {
        method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Error creando nota');
    return data;
};
/**
 * Elimina todas las columnas de nota actuales (th y td) de la tabla.
 * 
 * Preserva las columnas N°, Nombre Estudiante y Promedio.
 * 
 * @returns {void}
 */
function clearNoteColumns() {
    const tableEl = document.getElementById('studentsTable');
    const thead = tableEl.querySelector('thead');
    const tbody = tableEl.querySelector('tbody');
    if (!thead || !tbody) return;
    const headerRow = thead.querySelector('tr');
    const promedioHeader = headerRow.querySelector('.promedio-header');
    // eliminar todos los th que no sean N° o Nombre o Promedio
    const ths = Array.from(headerRow.querySelectorAll('th'));
    ths.forEach(th => {
        if (th === promedioHeader) return;
        if (th.textContent === 'N°' || th.textContent === 'Nombre Estudiante') return;
        headerRow.removeChild(th);
    });
    // eliminar td que contengan inputs.note-input en cada fila
    Array.from(tbody.querySelectorAll('tr')).forEach(tr => {
        const inputs = Array.from(tr.querySelectorAll('input.note-input'));
        inputs.forEach(inp => {
            const td = inp.closest('td');
            if (td) td.remove();
        });
    });
};
/**
 * Limpia completamente la tabla de estudiantes (headers y rows).
 * 
 * Remove todos los th, td e inputs para reiniciar la tabla.
 * 
 * @returns {void}
 */
function clearTable() {
    const table = document.getElementById('studentsTable');
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');
    const divError = table.querySelector('.div');
    if (divError) {
        divError.remove()
    }
    if (!thead || !tbody) return;
    //if (table) table.removeAttribute('data-asignature-id');

    const headerRow = thead.querySelector('tr');
    const ths = Array.from(headerRow.querySelectorAll('th'));

    ths.forEach(th => headerRow.removeChild(th));

    Array.from(tbody.querySelectorAll('tr')).forEach(tr => {
        const inputs = Array.from(tr.querySelectorAll('input.note-input'));
        inputs.forEach(inp => {
            const td = inp.closest('td');
            const tr = inp.closest('tr');
            if (td) td.remove();
            if (tr) tr.remove();
        });
    });
};
/**
 * Carga las asignaturas del profesor y las inserta en el select.
 * 
 * Obtiene las asignaturas del servidor, las ordena y permite cambiar
 * entre ellas. Al cambiar, recarga automáticamente los estudiantes y notas.
 * 
 * @async
 * @param {number} id_grade - ID del grado
 * @param {boolean} [loadAsignatures=true] - Si se deben agregar event listeners
 * @returns {Promise<Array>} Array de asignaturas [{id, name}, ...]
 * @throws {Error} Si no está autorizado o la petición falla
 */
async function loadAsignature(id_grade, loadAsignatures = true) {
    try {
        const res = await fetch(`http://127.0.0.1:5000/api/teacher/asignatures?id_grade=${encodeURIComponent(id_grade)}`, { credentials: 'include' });
        if (!res.ok) throw new Error('No autorizado');
        const data = await res.json();
        //console.log(data)
        const asignatures = data.asignatures || [];
        const select = document.getElementById('asignatureSelect');
        select.innerHTML = '';
        let options = [];
        asignatures.forEach((a) => {
            //console.log(a.name);
            const opt = document.createElement('option');
            opt.value = a.id;
            opt.textContent = a.name;
            select.appendChild(opt);
            options.push(opt.value)
        });
        // seleccionar la asignatura que viene en el table dataset, si existe
        const current = table ? table.dataset.asignatureId : null;
        //console.log(select.value, current, options)
        // console.log(options)
        if (current && options.includes(current)) {
            select.value = current;
            // console.log("Asignatura cargada desde dataset:", current);
        } else if (select.options.length > 0) {
            select.selectedIndex = 0;
            table.dataset.asignatureId = select.value;
            // console.log("Asignatura cargada desde primera opcion:", select.value);
        }
        if (!loadAsignatures) {
            //console.log("No cargar asignatura");
            return asignatures;
        }

        // al cambiar seleccion, limpiar columnas y recargar notas
        select.addEventListener('change', async (e) => {
            const val = e.target.value;
            if (!val) return;
            clearTable();
            table.dataset.asignatureId = val;
            await ReloadStudents(table.dataset.gradeId);
            await loadNotesForAsignature(val, table.dataset.gradeId);
        });
        return asignatures;
    } catch (err) {
        console.error('Error cargando asignaturas:', err);
        return [];
    }
};
/**
 * Carga los grados disponibles para el profesor actual.
 * 
 * Obtiene del servidor la lista de grados, los inserta en un select
 * y permite cambiar entre ellos para recargar estudiantes y notas.
 * 
 * @async
 * @returns {Promise<Array>} Array de grados [{id, name}, ...]
 * @throws {Error} Si no está autorizado
 */
async function loadGradesForTeacher() {
    try {
        const res = await fetch('http://127.0.0.1:5000/api/teacher/grades', { credentials: 'include' });
        if (!res.ok) throw new Error('No autorizado');
        const data = await res.json();
        const grades = data.grades || [];
        //console.log(grades)
        try {
            grades.sort((a, b) => a.name - b.name);
        } catch (err) {
            console.log('orden alfabetico', (err));
        }
        const select = document.getElementById('gradeSelect');
        select.innerHTML = '';
        grades.forEach((g) => {
            const opt = document.createElement('option');
            opt.value = g.id;
            opt.textContent = g.name;
            select.appendChild(opt);
        });
        const current = table ? table.dataset.gradeId : null;
        if (current) {
            select.value = current;
        } else if (select.options.length > 0) {
            select.selectedIndex = 0;
            table.dataset.gradeId = select.value;
        }
        select.addEventListener('change', async (e) => {
            const val = e.target.value;
            if (!val) return;
            table.dataset.gradeId = val;
            clearTable();
            await ReloadStudents(val);
            await loadAsignature(val, loadAsignatures = false);
            await loadNotesForAsignature(table.dataset.asignatureId, val);
        });
        return grades;
    } catch (err) {
        console.error('Error cargando grados:', err);
        return [];
    }
};
/**
 * Carga las notas de una asignatura específica y las inserta en inputs.
 * 
 * Obtiene todas las notas del servidor, las agrupa por columna (actividad)
 * y las coloca en los inputs correspondientes de cada estudiante.
 * 
 * @async
 * @param {number} asignatureId - ID de la asignatura
 * @param {number} gradeId - ID del grado
 * @returns {Promise<void>}
 * @throws {Error} Si la petición falla
 */
async function loadNotesForAsignature(asignatureId, gradeId) {
    if (!asignatureId) return;
    try {
        const res = await fetch(`http://127.0.0.1:5000/api/teacher/notes?id_asignature=${encodeURIComponent(asignatureId)}&id_grade=${encodeURIComponent(gradeId)}`, { credentials: 'include' });
        if (!res.ok) return;
        const data = await res.json();
        // console.log(data, "data notes", asignatureId, gradeId);
        const notes = data.notes || [];
        const colOrder = [];
        const notesByCol = {};
        for (const n of notes) {
            const cn = n.col_name || 'nota';
            if (!notesByCol[cn]) { notesByCol[cn] = []; colOrder.push(cn); }
            notesByCol[cn].push(n);
        }
        for (const cn of colOrder) {
            addNoteColumnWithName(cn, cn);
            for (const note of notesByCol[cn]) {
                const tr = document.querySelector(`tr[data-student-id="${note.id_student}"]`);
                if (!tr) continue;
                const input = tr.querySelector(`input[name="${cn}"]`);
                if (input) {
                    input.value = note.note;
                    input.dataset.noteId = note.id;
                }
            }
        }
        computeAllAverages();
    } catch (err) {
        console.error('Error cargando notas:', err);
    }
};
/**
 * Actualiza una nota existente en el servidor.
 * 
 * @async
 * @param {number} noteId - ID de la nota a actualizar
 * @param {number} studentId - ID del estudiante
 * @param {number} asignatureId - ID de la asignatura
 * @param {number} note - Nuevo valor de la calificación
 * @param {string} colName - Nombre de la columna
 * @returns {Promise<boolean>} true si se actualizó exitosamente
 * @throws {Error} Si la actualización falla
 */
async function updateNote(noteId, studentId, asignatureId, note, colName) {
    const payload = { student_id: Number(studentId), asignature_id: Number(asignatureId), note_id: Number(noteId), note: parseFloat(note), col_name: colName };
    const res = await fetch('http://127.0.0.1:5000/update_note_js', {
        method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Error actualizando nota');
    return true;
};
/**
 * Borra una nota del servidor.
 * 
 * @async
 * @param {number} noteId - ID de la nota a eliminar
 * @param {number} studentId - ID del estudiante
 * @param {number} asignatureId - ID de la asignatura
 * @param {string} colName - Nombre de la columna
 * @returns {Promise<boolean>} true si se eliminó exitosamente
 * @throws {Error} Si la eliminación falla
 */
async function deleteNote(noteId, studentId, asignatureId, colName) {
    const payload = { student_id: Number(studentId), asignature_id: Number(asignatureId), note_id: Number(noteId), col_name: colName };
    const res = await fetch('http://127.0.0.1:5000/delete_note_js', {
        method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Error borrando nota');
    return true;
};
/**
 * Envía una nota (crea, actualiza o borra) con debounce.
 * 
 * Intercepta cambios en un input y decide si crear, actualizar o eliminar
 * según si el input tiene un `noteId` asignado.
 * 
 * @async
 * @param {HTMLInputElement} inputEl - Input del que se leyó el cambio
 * @returns {Promise<void>}
 * @throws {Error} Si alguna operación en el servidor falla (capturada en consola)
 */
const sendNote = debounce(async (inputEl) => {
    const studentId = inputEl.dataset.studentId;
    const asignatureId = table.dataset.asignatureId;
    const gradeId = table.dataset.gradeId;
    // console.log(gradeId, "gradeId");
    const value = inputEl.value === '' ? '' : inputEl.value;
    const colName = inputEl.name;
    try {
        if (value === '') {
            // borrar si existe noteId
            if (inputEl.dataset.noteId) {
                await deleteNote(inputEl.dataset.noteId, studentId, asignatureId, colName);
                delete inputEl.dataset.noteId;
                console.log('Nota eliminada');
            }
            // recalcular promedio de la fila
            const trDel = inputEl.closest('tr');
            if (trDel) computeRowAverage(trDel);
            return;
        }
        if (inputEl.dataset.noteId) {
            await updateNote(inputEl.dataset.noteId, studentId, asignatureId, value, colName);
            // console.log('Nota actualizada');
            const trUpd = inputEl.closest('tr');
            if (trUpd) computeRowAverage(trUpd);
        } else {
            // console.log("add nota");
            const insertedId = await createNote(studentId, asignatureId, gradeId, value, colName);
            inputEl.dataset.noteId = insertedId.id;
            const trNew = inputEl.closest('tr');
            if (trNew) computeRowAverage(trNew);
        }
    } catch (err) {
        console.error(err);
        // opcional: mostrar error al profe
    }
}, 500);
/**
 * Calcula el promedio de notas para una fila de estudiante específica.
 * 
 * Obtiene todos los inputs de tipo `note-input` en la fila, calcula
 * el promedio y actualiza la celda de promedio.
 * 
 * @param {HTMLTableRowElement} tr - Elemento de fila <tr>
 * @returns {void}
 */
function computeRowAverage(tr) {
    if (!tr) return;
    const inputs = Array.from(tr.querySelectorAll('input.note-input'));
    const values = inputs.map(i => parseFloat(i.value)).filter(v => !isNaN(v));
    const promCell = tr.querySelector('.promedio-cell');
    if (!promCell) return;
    if (values.length === 0) {
        promCell.textContent = 'N/A';
        return;
    }
    const sum = values.reduce((a, b) => a + b, 0);
    const avg = sum / values.length;
    promCell.textContent = avg.toFixed(2);
};
/**
 * Recalcula los promedios de todas las filas de estudiantes.
 * 
 * Itera sobre cada fila visible en tbody y llama a `computeRowAverage`.
 * 
 * @returns {void}
 */
function computeAllAverages() {
    const rows = Array.from(document.querySelectorAll('tbody tr'));
    rows.forEach(r => computeRowAverage(r));
};
// añadir columna de nota (con nombre de columna opcional)
/**
 * Añade una nueva columna de nota a la tabla con campos de entrada.
 * 
 * Crea un nuevo `<th>` en el header y agrega `<input type="number">` en cada
 * fila de estudiante. Opcionalmente persiste la columna en el servidor.
 * 
 * @async
 * @param {string} colName - Nombre técnico de la columna (ej: "Parcial1")
 * @param {string} label - Etiqueta visible en el header (ej: "Parcial 1")
 * @param {number} asignatureId - ID de la asignatura (solo si saveColumn=true)
 * @param {number} gradeId - ID del grado (solo si saveColumn=true)
 * @param {boolean} [saveColumn=false] - Si true, persiste en el servidor
 * @returns {Promise<void>}
 * @throws {Error} Si saveColumn=true y la petición falla
 */
async function addNoteColumnWithName(colName, label, asignatureId, gradeId, saveColumn = false) {
    const table = document.getElementById('studentsTable');
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');
    if (!thead || !tbody) return;

    const headerRow = thead.querySelector('tr');
    const promedioHeader = headerRow.querySelector('.promedio-header');

    const th = document.createElement('th');
    th.textContent = label || colName || `Nota`;
    // insertar antes de la columna Promedio
    headerRow.insertBefore(th, promedioHeader);

    // agregar inputs por estudiante antes de la celda promedio
    Array.from(tbody.querySelectorAll('tr')).forEach(async (tr) => {
        const td = document.createElement('td');
        const input = document.createElement('input');
        input.type = 'number';
        input.min = '1';
        input.max = '5';
        input.step = '0.1';
        input.className = 'note-input';
        input.name = colName; // usamos el nombre de columna como identificador
        input.dataset.colName = colName;
        input.dataset.studentId = tr.dataset.studentId;
        input.addEventListener('input', (e) => sendNote(e.target));
        if (saveColumn) {
            console.log(asignatureId, gradeId, colName)
            const payload = { id_asignature: Number(asignatureId), id_grade: Number(gradeId), id_studet: tr.dataset.studentId, col_name: colName };
            const res = await fetch('http://127.0.0.1:5000/add_column_js', {
                method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.message || 'Error creando nota');
        }
        td.appendChild(input);
        const promedioCell = tr.querySelector('.promedio-cell');
        tr.insertBefore(td, promedioCell);
    });
};
/**
 * Abre un diálogo para que el profesor agregue una nueva columna de nota.
 * 
 * Solicita el nombre de la columna (ej: "Parcial 1", "Examen") mediante
 * un prompt y luego la añade a la tabla y al servidor.
 * 
 * @returns {void}
 */
function addNoteColumn() {
    // pedir nombre de columna al profesor
    const colName = prompt('Nombre de la columna (ej: Parcial 1, Examen):');
    if (!colName) return;
    addNoteColumnWithName(colName, colName, table.dataset.asignatureId, table.dataset.gradeId, saveColumn = true);
};
// inicializar
document.addEventListener('DOMContentLoaded', async () => {
    // cargar asignaturas y luego cargar notas para la asignatura seleccionada
    const grades = await loadGradesForTeacher();
    await loadStudents(table.dataset.gradeId);
    const asignatures = await loadAsignature(id_grade = table.dataset.gradeId);
    const select = document.getElementById('asignatureSelect');
    const current = table ? table.dataset.asignatureId : null;
    const selected = current || (select ? select.value : null);
    if (selected) {
        table.dataset.asignatureId = selected;
        await loadNotesForAsignature(selected, table.dataset.gradeId);
    }
    if (buttonAddColumn) buttonAddColumn.addEventListener('click', addNoteColumn);
});