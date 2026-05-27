(() => {
  const storageKey = 'delacau-theme';
  const paletteKey = 'delacau-palette-preview';
  const root = document.documentElement;
  const button = document.querySelector('[data-theme-toggle]');
  const paletteButtons = [...document.querySelectorAll('[data-palette]')];

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

  function currentPalette() {
    return localStorage.getItem(paletteKey) || 'route';
  }

  function applyPalette(palette) {
    root.dataset.palette = palette;
    paletteButtons.forEach((item) => {
      const active = item.dataset.palette === palette;
      item.classList.toggle('active', active);
      item.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
  }

  applyTheme(currentTheme());
  applyPalette(currentPalette());

  if (button) {
    button.addEventListener('click', () => {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem(storageKey, next);
      applyTheme(next);
    });
  }

  paletteButtons.forEach((item) => {
    item.addEventListener('click', () => {
      const next = item.dataset.palette;
      localStorage.setItem(paletteKey, next);
      applyPalette(next);
    });
  });
})();
