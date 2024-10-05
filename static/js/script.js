document.oncontextmenu = function () { return false }
window.ondragstart = function () { return false }

// TODO: thème sombre persistant

const lightIcon = document.getElementById('lightIcon');
const darkIcon = document.getElementById('darkIcon');

// Fonction pour alterner le thème et les icônes
lightIcon.addEventListener('click', () => {
  // Activer le thème sombre
  document.documentElement.style.setProperty('--bg', '0,0,0');
  document.documentElement.style.setProperty('--primary', '255,255,255');

  // Alterner les icônes
  lightIcon.classList.add('hidden');
  darkIcon.classList.remove('hidden');
});

darkIcon.addEventListener('click', () => {
  // Activer le thème clair
  document.documentElement.style.setProperty('--bg', '255,255,255');
  document.documentElement.style.setProperty('--primary', '0,0,0');

  // Alterner les icônes
  darkIcon.classList.add('hidden');
  lightIcon.classList.remove('hidden');
});
