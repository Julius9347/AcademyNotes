let lastSeen = null

async function checkForUpdates() {
    try {
        const resp = await fetch('/api/notes/last-update');
        if (!resp.ok) throw new Error(resp.statusText);
        const data = await resp.json();
        // si cambia el valor, hay actualizaciones
        if (lastSeen !== data.last) {
            console.log(lastSeen, data.last)
            lastSeen = data.last;
            console.log('hay novedades, recargo');
            await refreshData();          // función tuya que vuelve a cargar tablas, notas…
        }
    } catch (err) {
        console.error('polling error', err);
    }
}

/**
 * Carga las asignaturas de main.py y luego inserta (id, name) en la tabla
 * @returns Array de las asignaturas cargadas
 */
async function loadAsignaturesStudent() {
    const tableAsignature = document.getElementById('tableAsignatures');
    try {
        const response = await fetch('/api/student/asignatures', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        asignatures = data.asignatures || [];


        // Clear existing table content
        let thead = tableAsignature.querySelector('thead');
        let tbody = tableAsignature.querySelector('tbody');
        if (thead) thead.remove();
        if (tbody) tbody.remove();

        tbody = document.createElement('tbody');


        asignatures.forEach((asignature, idx) => {
            const headerRow = document.createElement('tr');
            headerRow.dataset.class = "header-row " + asignature.id_asignature;
            headerRow.innerHTML = `<th>N°</th><th id="asignatura-header">Asignatura</th><th class="promedio-header">Promedio</th>`;
            const thPromedio = headerRow.querySelector('.promedio-header');
            // thPromedio.colSpan = "2";
            tbody.appendChild(headerRow);
            tableAsignature.appendChild(tbody);
            const tr = document.createElement('tr');
            tr.dataset.asignatureId = asignature.id_asignature;
            const tdIndex = document.createElement('td');
            tdIndex.textContent = idx + 1;
            const tdName = document.createElement('td');
            tdName.textContent = asignature.name;
            const tdPromedio = document.createElement('td');
            tdPromedio.className = 'promedio-cell';
            tdPromedio.textContent = asignature.average != null ? asignature.average.toFixed(1) : 'N/A';
            // tdPromedio.colSpan = "2";
            tr.appendChild(tdIndex);
            tr.appendChild(tdName);
            tr.appendChild(tdPromedio);
            tbody.appendChild(tr);
        });
        tableAsignature.appendChild(tbody);
        return asignatures;
    } catch (error) {
        console.error('Error loading asignatures:', error);
    }
}
/**
 * Carga las notas especificas de la asignatura y estudiante para insertarlas en la tabla
 * @param {number} asignatureId 
 * @returns 
 */
async function loadNotesForAsignatureStudent(asignatureId) {
    if (!asignatureId) {
        console.log('No asignature ID provided');
        return;
    }
    try {
        const res = await fetch(`http://127.0.0.1:5000/api/student/notes?id_asignature=${encodeURIComponent(asignatureId)}`, { credentials: 'include' });
        if (!res.ok) {
            console.error('Failed to fetch notes:', res.statusText);
            return;
        }
        const data = await res.json();
        const notes = data.notes || [];
        const colOrder = [];
        const notesByCol = {};
        for (const n of notes) {
            const cn = n.col_name || 'nota';
            if (!notesByCol[cn]) { notesByCol[cn] = []; colOrder.push(cn); }
            notesByCol[cn].push(n);
        }
        // console.log(notesByCol, "notesByCol");
        // console.log(colOrder, "colOrder");
        for (const cn of colOrder) {
            // console.log(cn, "cn");
            addNoteColumnWithNameStudent(cn, cn, asignatureId);
            for (const note of notesByCol[cn]) {
                // console.log(note, "note");
                const tr = document.querySelector(`tr[data-asignature-id="${note.id_asignature}"]`);
                if (!tr) continue;
                const label = tr.querySelector(`label[data-col-name="${cn}"]`);
                if (label) {
                    label.innerHTML = note.note;
                    label.dataset.noteId = note.id;
                }
            }
        }
        //computeAllAverages();
    } catch (err) {
        console.error('Error cargando notas:', err);
    }
}
/**
 * añade a la tabla las columnas de cada asugnatura
 * @param {string} colName 
 * @param {string} label 
 * @param {number} asignatureId 
 * @returns 
 */
function addNoteColumnWithNameStudent(colName, label, asignatureId) {
    const tableAsignature = document.getElementById('tableAsignatures');
    const tbody = tableAsignature.querySelector('tbody');
    if (!tbody) return;

    const headerRow = tbody.querySelector(`tr[data-class="header-row ${asignatureId}"]`);
    const promedioHeader = headerRow.querySelector('.promedio-header');

    const th = document.createElement('th');
    th.textContent = label || colName || `Nota`;
    // insertar antes de la columna Promedio
    headerRow.insertBefore(th, promedioHeader);

    Array.from(tbody.querySelectorAll(`tr[data-asignature-id="${asignatureId}"]`)).forEach(tr => {
        const td = document.createElement('td');
        const label = document.createElement('label');
        label.className = 'note-label';
        label.name = colName; // usamos el nombre de columna como identificador
        label.dataset.colName = colName;
        label.dataset.asignature = tr.dataset.asignatureId;
        td.appendChild(label);
        const promedioCell = tr.querySelector('.promedio-cell');
        tr.insertBefore(td, promedioCell);
    });
}


async function refreshData() {
    const tableAsignature = document.getElementById('tableAsignatures');
    tableAsignature.innerHTML = '';
    await loadAsignaturesStudent();
    rows = document.querySelectorAll('tr[data-asignature-id]');
    for (row of rows) {
        await loadNotesForAsignatureStudent(row.dataset.asignatureId);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await loadAsignaturesStudent();
    rows = document.querySelectorAll('tr[data-asignature-id]');
    for (row of rows) {
        await loadNotesForAsignatureStudent(row.dataset.asignatureId);
    }
    setInterval(checkForUpdates, 5000)
});