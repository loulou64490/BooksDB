// Empêcher la sélection et le déplacement
document.oncontextmenu = function () {
    return false
}
window.ondragstart = function () {
    return false
}

const lightIcon = document.getElementById('lightIcon');
const darkIcon = document.getElementById('darkIcon');

// Fonction pour appliquer le bon thème et ajuster les icônes
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme === 'dark' ? 'dark' : 'light');
    lightIcon.classList.toggle('hidden', theme === 'dark');
    darkIcon.classList.toggle('hidden', theme !== 'dark');
}

// Charger le thème depuis le stockage ou selon la préférence système
function getPreferredTheme() {
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return savedTheme || (systemPrefersDark ? 'dark' : 'light');
}

// Gestionnaire de clics pour alterner le thème et l'enregistrer
function toggleTheme() {
    const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
}

// Appliquer le thème au chargement de la page
(function () {
    applyTheme(getPreferredTheme());

    // Rendre la page visible après application du thème
    document.body.style.visibility = 'visible';
})();

// Ajout des gestionnaires d'événements
lightIcon.addEventListener('click', toggleTheme);
darkIcon.addEventListener('click', toggleTheme);

// Éviter le flash de transition de thème au chargement
window.addEventListener('load', function () {
    let style = document.createElement('style');
    style.innerHTML = `* { transition: background 0.3s;`;
    document.head.appendChild(style);
});
