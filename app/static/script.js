// Empêcher la sélection et le déplacement
document.oncontextmenu = window.ondragstart = () => false;

// Éviter le flash de transition de thème au chargement
window.addEventListener('load', () => {
    const style = document.createElement('style');
    style.textContent = `*{ transition: background 0.2s, border 0.2s; }`;
    document.head.appendChild(style);
});

// Liste pour stocker les IDs dont l'affichage a été modifié
let modifiedIds = [];

// Fonction pour mettre à jour l'affichage d'un élément
const updateDisplay = (id, value) => {
    // Parcourir la liste et masquer tous les éléments sauf celui passé en argument
    modifiedIds.forEach((existingId) => {
        if (existingId !== id) {
            document.getElementById(existingId).style.display = 'none';
        }
    });

    // Mettre à jour l'affichage de l'élément spécifié
    document.getElementById(id).style.display = value;

    // Si l'ID n'est pas déjà dans la liste, on l'ajoute
    if (!modifiedIds.includes(id)) {
        modifiedIds.push(id);
    }
};

const loginSwitcher = (id, value) => {
    document.getElementById(id).style.display = value;
}

const expand = (id) => {
    if (document.getElementById(id).classList.contains('comm_comm')) {
        document.getElementById(id).classList.remove('comm_comm');
    } else {
        document.getElementById(id).classList.add('comm_comm');
    }
}

// Sélection des icônes
const systemIcon = document.getElementById('systemIcon');
const darkIcon = document.getElementById('darkIcon');
const lightIcon = document.getElementById('lightIcon');

// Fonction pour appliquer le thème
function applyTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else if (theme === 'light') {
        document.documentElement.removeAttribute('data-theme'); // Utilisation du thème clair par défaut
    } else {
        // Thème système
        applySystemTheme();
    }
}

// Fonction pour détecter le thème système et l'appliquer
function applySystemTheme() {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
}

// Fonction pour afficher l'icône correspondante
function updateIcons(theme) {
    systemIcon.classList.add('hidden');
    darkIcon.classList.add('hidden');
    lightIcon.classList.add('hidden');

    if (theme === 'dark') {
        darkIcon.classList.remove('hidden');
    } else if (theme === 'light') {
        lightIcon.classList.remove('hidden');
    } else {
        systemIcon.classList.remove('hidden');
    }
}

// Fonction pour passer au thème suivant
function cycleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'system';
    let newTheme;

    if (currentTheme === 'system') {
        newTheme = 'dark';
    } else if (currentTheme === 'dark') {
        newTheme = 'light';
    } else {
        newTheme = 'system';
    }

    // Appliquer et enregistrer le nouveau thème
    applyTheme(newTheme);
    updateIcons(newTheme);
    localStorage.setItem('theme', newTheme);

    // Si on repasse au thème système, réactiver l'écoute des changements système
    if (newTheme === 'system') {
        startSystemThemeListener();
    } else {
        stopSystemThemeListener();
    }
}

// Listener de changement de thème système
function startSystemThemeListener() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    // Ajoute un listener pour détecter les changements de thème système
    mediaQuery.addEventListener('change', applySystemTheme);
}

function stopSystemThemeListener() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    // Supprime le listener si on n'est plus en mode "système"
    mediaQuery.removeEventListener('change', applySystemTheme);
}

// Initialisation du thème lors du chargement de la page
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'system';
    applyTheme(savedTheme);
    updateIcons(savedTheme);

    // Si le thème est "système", écouter les changements du système
    if (savedTheme === 'system') {
        startSystemThemeListener();
    }
}

// Ajouter l'événement de clic sur le bouton pour changer de thème
document.getElementById('themeSwitcherButton').addEventListener('click', cycleTheme);

// Initialiser le thème au chargement de la page
initializeTheme();

document.body.classList.remove('hidden');

document.querySelectorAll('.menu-button').forEach(button => {
    button.addEventListener('click', (event) => {
        // Ferme les autres menus ouverts
        document.querySelectorAll('.menu-popup').forEach(menu => menu.style.display = 'none');

        // Identifie le menu associé
        const menuId = `comm-${button.id}`;
        const menu = document.getElementById(menuId);

        if (!menu) return; // Si le menu n'existe pas, on arrête ici

        // Affiche ou masque le menu
        menu.style.display = menu.style.display === 'none' || menu.style.display === '' ? 'flex' : 'none';

        // Obtient les coordonnées du bouton
        const buttonRect = button.getBoundingClientRect();

        // Position de base du menu : à droite du bouton
        let left = buttonRect.right + window.scrollX;
        let top = buttonRect.top + window.scrollY;

        // Ajuste la position si le menu dépasse à droite
        if (left + menu.offsetWidth > window.innerWidth + window.scrollX) {
            left = buttonRect.left + window.scrollX - menu.offsetWidth;
        }

        // Ajuste la position si le menu dépasse en bas
        if (top + menu.offsetHeight > window.innerHeight + window.scrollY) {
            top = buttonRect.bottom + window.scrollY - menu.offsetHeight;
        }

        // Applique la position finale
        menu.style.left = `${left}px`;
        menu.style.top = `${top}px`;

        // Empêche l'événement click de se propager au document
        event.stopPropagation();
    });
});

// Masquer les menus en cliquant en dehors
document.addEventListener("click", (e) => {
    document.querySelectorAll(".menu-popup").forEach((menu) => {
        menu.style.display = "none";
    });
});

// Remplacez 'votreID' par l'ID de votre élément
setTimeout(function() {
    document.getElementById('flash').style.display = 'none';
}, 3000);
