// Empêcher la sélection et le déplacement
document.oncontextmenu = window.ondragstart = () => false;

const lightIcon = document.getElementById('lightIcon');
const darkIcon = document.getElementById('darkIcon');

// Fonction pour appliquer le thème et ajuster les icônes
const applyTheme = theme => {
    const isDark = theme === 'dark';
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    lightIcon.classList.toggle('hidden', isDark);
    darkIcon.classList.toggle('hidden', !isDark);
};

// Charger le thème depuis le stockage ou selon la préférence système
const getPreferredTheme = () => localStorage.getItem('theme') ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

// Alterner le thème et l'enregistrer
const toggleTheme = () => {
    const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
};

// Appliquer le thème et rendre la page visible après le chargement
document.addEventListener('DOMContentLoaded', () => {
    applyTheme(getPreferredTheme());
    document.body.style.visibility = 'visible';
});

// Ajouter les gestionnaires de clics pour alterner le thème
lightIcon.onclick = darkIcon.onclick = toggleTheme;

// Éviter le flash de transition de thème au chargement
window.addEventListener('load', () => {
    const style = document.createElement('style');
    style.textContent = `*{ transition: background 0.2s; } .hover { transition: background 0.2s, transform 0.1s, box-shadow 0.1s; }`;
    document.head.appendChild(style);
});

// Fonction pour mettre à jour l'affichage d'un élément
const updateDisplay = (id, value) => {
    document.getElementById(id).style.display = value;
};
