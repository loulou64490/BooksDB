document.oncontextmenu = function () { return false }
window.ondragstart = function () { return false }

const lightIcon = document.getElementById('lightIcon');
const darkIcon = document.getElementById('darkIcon');

// Fonction pour appliquer le bon thème et ajuster les icônes
function applyTheme(theme) {
  if (theme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    lightIcon.classList.add('hidden');
    darkIcon.classList.remove('hidden');
  } else {
    document.documentElement.removeAttribute('data-theme');
    darkIcon.classList.add('hidden');
    lightIcon.classList.remove('hidden');
  }
}

// Charger le thème au chargement de la page et ajuster les icônes
function loadTheme() {
  const savedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (savedTheme) {
    applyTheme(savedTheme);
  } else if (systemPrefersDark) {
    applyTheme('dark');
  } else {
    applyTheme('light');
  }
}

// Gestionnaires d'événements pour alterner le thème et ajuster les icônes
lightIcon.addEventListener('click', () => {
  applyTheme('dark');
  localStorage.setItem('theme', 'dark');
});

darkIcon.addEventListener('click', () => {
  applyTheme('light');
  localStorage.setItem('theme', 'light');
});

// Eviter le flash au chargement et afficher l'icône correcte
(function() {
  const savedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = savedTheme || (systemPrefersDark ? 'dark' : 'light');

  // Appliquer le bon thème immédiatement et ajuster l'icône visible
  if (theme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    lightIcon.classList.add('hidden');
    darkIcon.classList.remove('hidden');
  } else {
    document.documentElement.removeAttribute('data-theme');
    darkIcon.classList.add('hidden');
    lightIcon.classList.remove('hidden');
  }

  // Rendre la page visible après que le thème est appliqué
  document.addEventListener('DOMContentLoaded', function() {
    document.body.style.visibility = 'visible';
  });
})();