document.addEventListener('DOMContentLoaded', function() {
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const navMenu = document.getElementById('navMenu');
    const mobileOverlay = document.getElementById('mobileOverlay');

    console.log('Hamburger Menu Script Loaded');
    console.log('hamburgerBtn:', hamburgerBtn);
    console.log('navMenu:', navMenu);
    console.log('mobileOverlay:', mobileOverlay);

    if (!hamburgerBtn || !navMenu || !mobileOverlay) {
        console.error('Elementos do menu não encontrados!');
        return;
    }

    function toggleMenu() {
        console.log('Toggle menu chamado');
        hamburgerBtn.classList.toggle('active');
        navMenu.classList.toggle('mobile-active');
        mobileOverlay.classList.toggle('active');
        document.body.style.overflow = navMenu.classList.contains('mobile-active') ? 'hidden' : '';
    }

    hamburgerBtn.addEventListener('click', function(e) {
        console.log('Hamburger clicado!', e);
        toggleMenu();
    });
    
    mobileOverlay.addEventListener('click', toggleMenu);

    navMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            if (navMenu.classList.contains('mobile-active')) {
                toggleMenu();
            }
        });
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && navMenu.classList.contains('mobile-active')) {
            toggleMenu();
        }
    });
});
