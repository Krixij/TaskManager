document.addEventListener('DOMContentLoaded', () => {
  const root = document.querySelector('[data-sidebar-root]');
  const toggle = root?.querySelector('[data-sidebar-toggle]');
  const storageKey = 'taskmanager.sidebar.collapsed';
  let collapsed = false;
  try { collapsed = localStorage.getItem(storageKey) === 'true'; } catch (_) {}
  const update = () => {
    if (!root || !toggle) return;
    root.classList.toggle('is-collapsed', collapsed);
    toggle.setAttribute('aria-expanded', String(!collapsed));
    const label = collapsed ? 'Раскрыть боковую панель' : 'Свернуть боковую панель';
    toggle.setAttribute('aria-label', label);
    toggle.title = label;
  };
  update();
  toggle?.addEventListener('click', () => {
    collapsed = !collapsed;
    update();
    try { localStorage.setItem(storageKey, String(collapsed)); } catch (_) {}
  });

  const list = document.querySelector('[data-sidebar-projects]');
  if (!list) return;
  const normalize = path => path.replace(/\/+$/, '') || '/';
  const currentPath = normalize(window.location.pathname);
  const projectsLink = document.querySelector('[data-sidebar-nav="projects"]');
  const tasksLink = document.querySelector('[data-sidebar-nav="my-tasks"]');
  const calendarLink = document.querySelector('[data-sidebar-nav="calendar"]');
  const projectListPath = normalize(new URL(list.dataset.sourceUrl, location.href).pathname);
  const active = (link, state) => {
    if (!link) return;
    link.classList.toggle('is-active', state);
    if (state) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  };
  active(tasksLink, !!tasksLink && currentPath === normalize(new URL(tasksLink.href).pathname));
  active(calendarLink, !!calendarLink && currentPath === normalize(new URL(calendarLink.href).pathname));
  active(projectsLink, currentPath === projectListPath || currentPath.includes('/projects/'));
  const showMessage = message => {
    const li = document.createElement('li');
    li.className = 'sidebar__project-placeholder';
    li.textContent = message;
    list.replaceChildren(li);
  };
  (async () => {
    try {
      const response = await fetch(list.dataset.sourceUrl, { credentials: 'same-origin' });
      if (!response.ok || response.redirected) throw new Error('Ошибка запроса');
      const documentFromServer = new DOMParser().parseFromString(await response.text(), 'text/html');
      const sourceLinks = documentFromServer.querySelectorAll('.projects-panel .project-card__link');
      const seen = new Set();
      list.replaceChildren();
      sourceLinks.forEach(link => {
        const name = link.textContent.trim();
        const href = link.getAttribute('href');
        if (!name || !href) return;
        const url = new URL(href, response.url);
        if (url.origin !== location.origin || seen.has(url.pathname)) return;
        seen.add(url.pathname);
        const item = document.createElement('li');
        const a = document.createElement('a');
        a.className = 'sidebar__project-link';
        a.href = url.pathname + url.search + url.hash;
        a.textContent = name;
        a.title = name;
        if (normalize(url.pathname) === currentPath) {
          a.classList.add('is-active');
          a.setAttribute('aria-current', 'page');
        }
        item.append(a);
        list.append(item);
      });
      if (!seen.size) showMessage('Проектов пока нет');
    } catch (_) { showMessage('Не удалось загрузить проекты'); }
  })();
});
