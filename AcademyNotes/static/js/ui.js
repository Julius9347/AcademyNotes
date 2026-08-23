// Utilidades compartidas del prototipo. Sin dependencias externas.

/** POST JSON al propio servidor (misma sesion, mismo origen). */
export async function postJson(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'fetch' },
    body: JSON.stringify(payload || {}),
  });
  return readResponse(response);
}

export async function getJson(url) {
  const response = await fetch(url, { headers: { 'X-Requested-With': 'fetch' } });
  return readResponse(response);
}

export async function postForm(url, formData) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'X-Requested-With': 'fetch' },
    body: formData,
  });
  return readResponse(response);
}

async function readResponse(response) {
  let data = null;
  try {
    data = await response.json();
  } catch (error) {
    data = { ok: false, message: 'El servidor no devolvio una respuesta valida.' };
  }
  if (!response.ok) {
    return { ok: false, message: data.message || `Error ${response.status}.`, data };
  }
  return { ok: true, ...data };
}

/* ------------------------------------------------------------- modales --- */
export function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('is-open');
}

export function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove('is-open');
}

export function wireModals() {
  document.querySelectorAll('.modal').forEach((modal) => {
    modal.addEventListener('click', (event) => {
      if (event.target === modal || event.target.hasAttribute('data-close')) {
        modal.classList.remove('is-open');
      }
    });
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      document.querySelectorAll('.modal.is-open')
        .forEach((modal) => modal.classList.remove('is-open'));
    }
  });
}

/* ------------------------------------------------- barra de estado ------ */
let hideTimer = null;

/** Muestra el estado de guardado. Los errores no se ocultan solos. */
export function status(text, kind = 'info') {
  const bar = document.getElementById('savebar');
  if (!bar) return;
  const label = document.getElementById('savebar-text');
  label.textContent = text;
  bar.classList.toggle('savebar--error', kind === 'error');
  bar.classList.add('is-visible');
  clearTimeout(hideTimer);
  if (kind !== 'error') {
    hideTimer = setTimeout(() => bar.classList.remove('is-visible'), 1800);
  }
}

export function hideStatus() {
  const bar = document.getElementById('savebar');
  if (bar) bar.classList.remove('is-visible');
}

export function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[character]));
}
