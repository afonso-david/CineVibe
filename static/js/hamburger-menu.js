document.addEventListener('DOMContentLoaded', function() {
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const navMenu = document.getElementById('navMenu');
    const mobileOverlay = document.getElementById('mobileOverlay');

    if (!hamburgerBtn || !navMenu || !mobileOverlay) {
        return;
    }

    function toggleMenu() {
        hamburgerBtn.classList.toggle('active');
        navMenu.classList.toggle('mobile-active');
        mobileOverlay.classList.toggle('active');
        document.body.style.overflow = navMenu.classList.contains('mobile-active') ? 'hidden' : '';
    }

    hamburgerBtn.addEventListener('click', toggleMenu);
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
