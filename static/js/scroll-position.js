// Guardar e restaurar posição do scroll em operações admin

// Guardar posição antes de submeter formulário
document.addEventListener('DOMContentLoaded', function() {
    // Restaurar posição se existir
    const savedPosition = sessionStorage.getItem('scrollPosition');
    if (savedPosition) {
        window.scrollTo(0, parseInt(savedPosition));
        sessionStorage.removeItem('scrollPosition');
    }

    // Guardar posição antes de submeter qualquer formulário
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            sessionStorage.setItem('scrollPosition', window.scrollY);
        });
    });

    // Guardar posição antes de clicar em botões que fazem ações
    const actionButtons = document.querySelectorAll('button[type="submit"], input[type="submit"]');
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            sessionStorage.setItem('scrollPosition', window.scrollY);
        });
    });
});
