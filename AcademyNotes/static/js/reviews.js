// Respuesta del profesor a una solicitud de revision.
import { postJson, openModal, wireModals, status, escapeHtml } from './ui.js';

wireModals();

const form = document.getElementById('form-responder');
const campoNota = document.getElementById('campo-nota');

document.querySelectorAll('.js-responder').forEach((button) => {
  button.addEventListener('click', () => {
    form.reset();
    form.request_id.value = button.dataset.id;
    campoNota.style.display = 'none';
    form.new_score.value = button.dataset.score || '';
    document.getElementById('resumen-solicitud').innerHTML =
      `<strong>${escapeHtml(button.dataset.student)}</strong> &middot; `
      + `${escapeHtml(button.dataset.activity)} (nota actual: `
      + `${escapeHtml(button.dataset.score || 'sin nota')})<br>`
      + `<span class="muted">${escapeHtml(button.dataset.message)}</span>`;
    openModal('modal-responder');
  });
});

form?.status.addEventListener('change', (event) => {
  campoNota.style.display = event.target.value === 'aceptada' ? '' : 'none';
});

document.getElementById('btn-enviar-respuesta')?.addEventListener('click', async () => {
  const payload = {
    status: form.status.value,
    response: form.response.value,
    new_score: form.status.value === 'aceptada' ? form.new_score.value : null,
  };
  const result = await postJson(
    `/profesor/solicitudes/${form.request_id.value}/responder`, payload);
  if (!result.ok) { status(result.message, 'error'); return; }
  location.reload();
});
