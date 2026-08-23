// Panel del estudiante: aviso de informacion nueva y solicitud de revision.
import { postJson, getJson, openModal, wireModals, status, escapeHtml } from './ui.js';

wireModals();

/* --------------------------------------------------------------- sondeo --- */
// Sondeo moderado (cada 30 s). No hace falta tiempo real al segundo: basta
// con avisar que hay informacion nueva mientras el estudiante mira el panel.
const poll = document.getElementById('poll');
if (poll) {
  let last = poll.dataset.last || '';
  setInterval(async () => {
    if (document.hidden) return;
    const result = await getJson('/estudiante/api/actualizaciones');
    if (!result.ok) return;
    if (result.last_update && result.last_update !== last) {
      last = result.last_update;
      showUpdateBanner();
    }
  }, 30000);
}

function showUpdateBanner() {
  if (document.getElementById('aviso-actualizacion')) return;
  const banner = document.createElement('div');
  banner.id = 'aviso-actualizacion';
  banner.className = 'flash flash--ok';
  banner.style.cssText = 'position:fixed;left:50%;transform:translateX(-50%);'
    + 'bottom:1.2rem;z-index:60;display:flex;gap:.6rem;align-items:center';
  banner.innerHTML = 'Hay informacion nueva publicada. '
    + '<button class="btn btn--sm" id="btn-recargar">Actualizar</button>';
  document.body.appendChild(banner);
  document.getElementById('btn-recargar')
    .addEventListener('click', () => location.reload());
}

/* ---------------------------------------------------- solicitar revision --- */
const form = document.getElementById('form-revision');

document.querySelectorAll('.js-revisar').forEach((button) => {
  button.addEventListener('click', () => {
    form.reset();
    form.grade_id.value = button.dataset.grade;
    document.getElementById('resumen-revision').innerHTML =
      `<strong>${escapeHtml(button.dataset.activity)}</strong> &middot; `
      + `nota registrada: ${escapeHtml(button.dataset.score || 'sin nota')}`;
    openModal('modal-revision');
  });
});

document.getElementById('btn-enviar-revision')?.addEventListener('click', async () => {
  const result = await postJson('/estudiante/api/solicitudes', {
    grade_id: Number(form.grade_id.value),
    reason_code: form.reason_code.value,
    message: form.message.value,
  });
  if (!result.ok) { status(result.message, 'error'); return; }
  status('Solicitud enviada. Tu profesor la vera en su panel.');
  setTimeout(() => location.reload(), 1200);
});
