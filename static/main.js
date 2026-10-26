const toggle = document.querySelector('.menu-toggle');
if (toggle) toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  document.querySelector('#navigation').classList.toggle('open', open);
});
for (const link of document.querySelectorAll('nav a')) {
  if (new URL(link.href).pathname === window.location.pathname) {
    link.setAttribute('aria-current', 'page');
  }
}

async function submitApi(form, method, data) {
  const result = form.querySelector('.form-result');
  const button = form.querySelector('button');
  button.disabled = true;
  result.textContent = 'Сохраняем…';
  try {
    const response = await fetch(form.action, {
      method, credentials: 'same-origin',
      headers: {'Content-Type': 'application/json',
        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value},
      body: JSON.stringify(data),
    });
    const payload = await response.json().catch(() => ({error: 'Сессия истекла. Обновите страницу и войдите снова.'}));
    if (!response.ok) throw new Error(payload.error || 'Не удалось сохранить.');
    result.textContent = 'Сохранено.';
    if (method === 'PATCH') window.location.reload();
    else if (form.action.includes('/api/exhibitions/')) window.location.assign('/exhibitions/' + payload.id + '/');
    else window.location.reload();
  } catch (error) {
    result.textContent = error.message;
    result.classList.add('error');
  } finally { button.disabled = false; }
}
for (const form of document.querySelectorAll('[data-api-form]')) {
  form.addEventListener('submit', event => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    delete data.csrfmiddlewaretoken;
    submitApi(form, 'POST', data);
  });
}
for (const form of document.querySelectorAll('[data-cancel-form]')) {
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (window.confirm('Отменить выставку и освободить зал?')) {
      submitApi(form, 'PATCH', {is_cancelled: true});
    }
  });
}
