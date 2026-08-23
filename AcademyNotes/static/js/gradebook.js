// Cuaderno de notas del profesor: guardado automatico, actividades,
// retroalimentacion, importacion de Excel y publicacion.
import { postJson, postForm, openModal, closeModal, wireModals, status, escapeHtml }
  from './ui.js';

const contexto = document.getElementById('contexto');
if (contexto) {
  const ASSIGNMENT = contexto.dataset.assignment;
  const PERIOD = Number(contexto.dataset.period);

  wireModals();
  wireGrades();
  wireActivities();
  wireFeedback();
  wireImport();
  wirePublish();

  /* ------------------------------------------------ guardado automatico --- */
  function wireGrades() {
    const timers = new Map();

    document.querySelectorAll('.cell-input').forEach((input) => {
      const original = input.value;
      input.dataset.original = original;

      input.addEventListener('input', () => {
        clearTimeout(timers.get(input));
        timers.set(input, setTimeout(() => saveCell(input), 700));
      });

      input.addEventListener('blur', () => {
        clearTimeout(timers.get(input));
        if (input.value !== input.dataset.original) saveCell(input);
      });

      // Enter baja a la siguiente fila: registrar notas de corrido.
      input.addEventListener('keydown', (event) => {
        if (event.key !== 'Enter') return;
        event.preventDefault();
        clearTimeout(timers.get(input));
        saveCell(input);
        const row = input.closest('tr');
        const index = [...row.querySelectorAll('.cell-input')].indexOf(input);
        const next = row.nextElementSibling;
        if (next) {
          const target = next.querySelectorAll('.cell-input')[index];
          if (target) { target.focus(); target.select(); }
        }
      });
    });
  }

  async function saveCell(input) {
    const payload = {
      activity_id: Number(input.dataset.activity),
      student_id: Number(input.dataset.student),
      score: input.value.trim() === '' ? null : input.value.trim(),
    };
    setState(input, 'saving');
    status('Guardando...');

    const result = await postJson('/profesor/api/notas', payload);
    if (!result.ok) {
      setState(input, 'error');
      status(result.message || 'No se pudo guardar.', 'error');
      addRetry(input);
      return;
    }
    input.dataset.original = input.value;
    setState(input, 'saved');
    status('Guardado');
    updateAverage(payload.student_id, result.promedio);
  }

  function setState(input, state) {
    input.classList.remove('is-saving', 'is-saved', 'is-error');
    if (state === 'saving') input.classList.add('is-saving');
    if (state === 'saved') {
      input.classList.add('is-saved');
      setTimeout(() => input.classList.remove('is-saved'), 1400);
    }
    if (state === 'error') input.classList.add('is-error');
  }

  function addRetry(input) {
    const bar = document.getElementById('savebar');
    if (bar.querySelector('button')) return;
    const button = document.createElement('button');
    button.className = 'btn btn--sm';
    button.textContent = 'Reintentar';
    button.addEventListener('click', () => { button.remove(); saveCell(input); });
    bar.appendChild(button);
  }

  function updateAverage(studentId, average) {
    const cell = document.querySelector(`.js-avg[data-student="${studentId}"]`);
    if (cell) cell.textContent = (average === null || average === undefined) ? '-' : average;
  }

  /* -------------------------------------------------------- actividades --- */
  function wireActivities() {
    const form = document.getElementById('form-actividad');
    const nuevo = document.getElementById('btn-nueva-actividad');
    const eliminar = document.getElementById('btn-eliminar-actividad');

    nuevo?.addEventListener('click', () => {
      form.reset();
      form.activity_id.value = '';
      document.getElementById('modal-actividad-titulo').textContent = 'Nueva actividad';
      eliminar.style.display = 'none';
      openModal('modal-actividad');
    });

    document.querySelectorAll('.js-editar-actividad').forEach((button) => {
      button.addEventListener('click', () => {
        form.activity_id.value = button.dataset.activity;
        form.name.value = button.dataset.name;
        form.kind.value = button.dataset.kind;
        form.weight.value = button.dataset.weight;
        form.due_date.value = button.dataset.due;
        form.allows_recovery.checked = button.dataset.recovery === '1';
        document.getElementById('modal-actividad-titulo').textContent = 'Editar actividad';
        eliminar.style.display = '';
        openModal('modal-actividad');
      });
    });

    document.getElementById('btn-guardar-actividad')?.addEventListener('click', async () => {
      const payload = {
        period_id: PERIOD,
        name: form.name.value,
        kind: form.kind.value,
        weight: Number(form.weight.value),
        due_date: form.due_date.value || null,
        allows_recovery: form.allows_recovery.checked,
      };
      const id = form.activity_id.value;
      const url = id
        ? `/profesor/actividades/${id}`
        : `/profesor/asignacion/${ASSIGNMENT}/actividades`;
      const result = await postJson(url, payload);
      if (!result.ok) { status(result.message, 'error'); return; }
      location.reload();
    });

    eliminar?.addEventListener('click', async () => {
      const id = form.activity_id.value;
      if (!id) return;
      if (!confirm('Se eliminara la actividad y todas sus notas. Continuar?')) return;
      const result = await postJson(`/profesor/actividades/${id}/eliminar`, {});
      if (!result.ok) { status(result.message, 'error'); return; }
      location.reload();
    });
  }

  /* -------------------------------------------------- retroalimentacion --- */
  function wireFeedback() {
    const form = document.getElementById('form-detalle');

    document.querySelectorAll('.js-detalle').forEach((button) => {
      button.addEventListener('click', () => {
        form.activity_id.value = button.dataset.activity;
        form.student_id.value = button.dataset.student;
        form.feedback_category.value = button.dataset.category || '';
        form.feedback_text.value = button.dataset.text || '';
        form.is_missing.checked = button.dataset.missing === '1';
        form.recovery_status.value = button.dataset.recovery || 'ninguna';
        document.getElementById('modal-detalle-titulo').textContent =
          `Retroalimentacion: ${button.dataset.studentName}`;
        openModal('modal-detalle');
      });
    });

    document.getElementById('plantillas')?.addEventListener('change', (event) => {
      if (event.target.value) form.feedback_text.value = event.target.value;
    });

    document.getElementById('btn-sugerencia')?.addEventListener('click', async () => {
      const result = await postJson('/profesor/api/sugerencia', {
        activity_id: Number(form.activity_id.value),
        student_id: Number(form.student_id.value),
      });
      if (!result.ok) { status(result.message, 'error'); return; }
      form.feedback_text.value = result.sugerencia;
    });

    document.getElementById('btn-guardar-detalle')?.addEventListener('click', async () => {
      const activityId = Number(form.activity_id.value);
      const studentId = Number(form.student_id.value);
      // La nota actual viaja tal cual: este formulario no la modifica.
      const input = document.querySelector(
        `.cell-input[data-activity="${activityId}"][data-student="${studentId}"]`);
      const result = await postJson('/profesor/api/notas', {
        activity_id: activityId,
        student_id: studentId,
        score: input && input.value.trim() !== '' ? input.value.trim() : null,
        feedback_category: form.feedback_category.value,
        feedback_text: form.feedback_text.value,
        is_missing: form.is_missing.checked,
        recovery_status: form.recovery_status.value,
      });
      if (!result.ok) { status(result.message, 'error'); return; }
      closeModal('modal-detalle');
      location.reload();
    });
  }

  /* ------------------------------------------------------- importacion --- */
  function wireImport() {
    let cambios = [];

    document.getElementById('btn-importar')?.addEventListener('click', () => {
      cambios = [];
      document.getElementById('preview-importacion').innerHTML = '';
      document.getElementById('btn-confirmar-importacion').style.display = 'none';
      openModal('modal-importar');
    });

    document.getElementById('btn-previsualizar')?.addEventListener('click', async () => {
      const file = document.getElementById('archivo-excel').files[0];
      const box = document.getElementById('preview-importacion');
      if (!file) { box.innerHTML = '<div class="flash flash--error">Selecciona un archivo.</div>'; return; }

      const data = new FormData();
      data.append('archivo', file);
      data.append('period_id', PERIOD);
      box.innerHTML = '<p class="muted">Analizando archivo...</p>';

      const result = await postForm(
        `/profesor/asignacion/${ASSIGNMENT}/importar/previsualizar`, data);
      if (!result.ok) {
        box.innerHTML = `<div class="flash flash--error">${escapeHtml(result.message)}</div>`;
        return;
      }
      cambios = result.cambios || [];
      box.innerHTML = renderPreview(result);
      document.getElementById('btn-confirmar-importacion').style.display =
        cambios.length ? '' : 'none';
    });

    document.getElementById('btn-confirmar-importacion')?.addEventListener('click', async () => {
      const result = await postJson(
        `/profesor/asignacion/${ASSIGNMENT}/importar/confirmar`,
        { cambios, period_id: PERIOD });
      if (!result.ok) { status(result.message, 'error'); return; }
      location.reload();
    });
  }

  function renderPreview(result) {
    const rows = (result.cambios || []).map((change) => `
      <tr>
        <td>${escapeHtml(change.student_name)}</td>
        <td>${escapeHtml(change.activity_name)}</td>
        <td class="center muted">${change.old_score ?? '-'}</td>
        <td class="center"><strong>${change.new_score}</strong></td>
        <td><span class="badge ${change.accion === 'Nueva' ? 'badge--info' : 'badge--warn'}">${change.accion}</span></td>
      </tr>`).join('');

    const errors = (result.errores || []).map((error) => `
      <li>Fila ${error.fila}: ${escapeHtml(error.detalle)}</li>`).join('');

    return `
      <div class="row" style="margin:.8rem 0">
        <span class="badge badge--ok">${result.total_validos} cambio(s)</span>
        <span class="badge badge--muted">${result.sin_cambios} sin cambios</span>
        ${result.errores.length ? `<span class="badge badge--alert">${result.errores.length} error(es)</span>` : ''}
      </div>
      ${errors ? `<div class="flash flash--error"><strong>Se omitiran:</strong><ul>${errors}</ul></div>` : ''}
      ${rows ? `<div class="table-wrap"><table class="table table--compact">
          <thead><tr><th>Estudiante</th><th>Actividad</th><th class="center">Antes</th>
          <th class="center">Despues</th><th>Accion</th></tr></thead>
          <tbody>${rows}</tbody></table></div>`
        : '<p class="muted">No hay cambios que aplicar.</p>'}`;
  }

  /* -------------------------------------------------------- publicacion --- */
  function wirePublish() {
    document.getElementById('btn-publicar')?.addEventListener('click', () => {
      document.getElementById('resultado-publicacion').innerHTML = '';
      openModal('modal-publicar');
    });

    document.getElementById('btn-confirmar-publicacion')?.addEventListener('click', async () => {
      const box = document.getElementById('resultado-publicacion');
      box.innerHTML = '<p class="muted">Publicando...</p>';
      const result = await postJson(
        `/profesor/asignacion/${ASSIGNMENT}/publicar`, { period_id: PERIOD });
      if (!result.ok) {
        box.innerHTML = `<div class="flash flash--error">${escapeHtml(result.message)}</div>`;
        return;
      }
      box.innerHTML = `<div class="flash flash--ok">
        ${result.publicadas} calificacion(es) publicadas en "${escapeHtml(result.preinforme)}".
        </div>`;
      setTimeout(() => location.reload(), 1200);
    });
  }
}
