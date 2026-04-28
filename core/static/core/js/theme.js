/* AptiTrack Theme Toggle */
(function() {
  const THEME_KEY = 'aptitrack-theme';
  const toggle = document.getElementById('theme-toggle');
  
  function getPreferred() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }

  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
    if (toggle) toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
  }

  apply(getPreferred());
  if (toggle) {
    toggle.addEventListener('click', function() {
      const current = document.documentElement.getAttribute('data-theme');
      apply(current === 'dark' ? 'light' : 'dark');
    });
  }
})();
