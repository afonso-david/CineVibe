document.addEventListener('DOMContentLoaded', function() {
    const savedPosition = sessionStorage.getItem('scrollPosition');
    if (savedPosition) {
        window.scrollTo(0, parseInt(savedPosition));
        sessionStorage.removeItem('scrollPosition');
    }
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            sessionStorage.setItem('scrollPosition', window.scrollY);
        });
    });
    const actionButtons = document.querySelectorAll('button[type="submit"], input[type="submit"]');
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            sessionStorage.setItem('scrollPosition', window.scrollY);
        });
    });
});
