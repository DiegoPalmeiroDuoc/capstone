function scrollToSection(id) {
    const section = document.getElementById(id);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

function toggleMenu() {
    const navMenu = document.getElementById('nav-menu');
    const hamburger = document.querySelector('.hamburger');

    navMenu.classList.toggle('show');
    hamburger.classList.toggle('open');
}

// Efecto Parallax más suave con JS
window.addEventListener('scroll', function() {
    const hero = document.getElementById('hero');
    let scrollPosition = window.pageYOffset;
    hero.style.backgroundPositionY = (scrollPosition * 0.4) + "px";
});
