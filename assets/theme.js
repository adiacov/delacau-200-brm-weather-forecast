(() => {
  const storageKey = 'delacau-theme';
  const root = document.documentElement;
  const button = document.querySelector('[data-theme-toggle]');

  function systemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function currentTheme() {
    return localStorage.getItem(storageKey) || systemTheme();
  }

  function applyTheme(theme) {
    root.dataset.theme = theme;
    if (button) {
      button.textContent = theme === 'dark' ? '☀️' : '🌙';
      button.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
      button.setAttribute('title', theme === 'dark' ? 'Light theme' : 'Dark theme');
    }
  }

  applyTheme(currentTheme());


  function scenarioFromHash() {
    const match = window.location.hash.match(/^#scenario-(8|10|13)$/);
    return match ? match[1] : null;
  }

  function openScenario(duration, scroll = false) {
    const target = document.querySelector(`.scenario[data-scenario="${duration}"]`);
    if (!target) return;
    document.querySelectorAll('.scenario').forEach((scenario) => {
      scenario.open = scenario === target;
    });
    if (scroll) {
      target.scrollIntoView({ block: 'start' });
    }
  }

  const initialScenario = scenarioFromHash();
  if (initialScenario) {
    openScenario(initialScenario, false);
  }

  document.querySelectorAll('.scenario').forEach((scenario) => {
    scenario.addEventListener('toggle', () => {
      if (!scenario.open) return;
      document.querySelectorAll('.scenario').forEach((other) => {
        if (other !== scenario) other.open = false;
      });
      const duration = scenario.dataset.scenario;
      if (duration) {
        history.replaceState(null, '', `${window.location.pathname}${window.location.search}#scenario-${duration}`);
      }
    });
  });

  document.querySelectorAll('[data-source-link]').forEach((link) => {
    link.addEventListener('click', () => {
      const open = document.querySelector('.scenario[open][data-scenario]');
      if (!open) return;
      const hash = `#scenario-${open.dataset.scenario}`;
      const url = new URL(link.getAttribute('href'), window.location.href);
      url.hash = hash;
      link.href = url.pathname + url.search + url.hash;
    });
  });

  window.addEventListener('hashchange', () => {
    const duration = scenarioFromHash();
    if (duration) openScenario(duration, true);
  });

  if (button) {
    button.addEventListener('click', () => {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem(storageKey, next);
      applyTheme(next);
    });
  }
})();
