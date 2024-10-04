document.oncontextmenu = function () { return false }
window.ondragstart = function () { return false }

const lightIcon = document.getElementById('lightIcon');
const darkIcon = document.getElementById('darkIcon');

// Fonction pour alterner le thème et les icônes
lightIcon.addEventListener('click', () => {
  // Activer le thème sombre
  document.documentElement.style.setProperty('--bg', 'black');
  document.documentElement.style.setProperty('--primary', 'white');

  // Alterner les icônes
  lightIcon.classList.add('hidden');
  darkIcon.classList.remove('hidden');
});

darkIcon.addEventListener('click', () => {
  // Activer le thème clair
  document.documentElement.style.setProperty('--bg', 'white');
  document.documentElement.style.setProperty('--primary', 'black');

  // Alterner les icônes
  darkIcon.classList.add('hidden');
  lightIcon.classList.remove('hidden');
});
