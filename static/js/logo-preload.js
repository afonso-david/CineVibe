// Preload e cache da logo para evitar flickering
(function() {
    // Registrar Service Worker para cache persistente
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/static/sw.js').then(function(registration) {
                console.log('ServiceWorker registrado com sucesso');
            }).catch(function(err) {
                console.log('ServiceWorker falhou:', err);
            });
        });
    }
    
    // Criar e cachear a imagem da logo imediatamente
    const logoImg = new Image();
    logoImg.src = '/static/imgs/Logo/logo8 sem fundo.png';
    
    // Forçar o navegador a manter a imagem em cache
    logoImg.onload = function() {
        // Armazenar no sessionStorage para acesso rápido
        try {
            const canvas = document.createElement('canvas');
            canvas.width = logoImg.width;
            canvas.height = logoImg.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(logoImg, 0, 0);
            sessionStorage.setItem('cinevibe_logo_cached', 'true');
        } catch(e) {
            console.log('Logo cached in browser memory');
        }
    };
    
    // Prevenir o flickering durante navegação
    window.addEventListener('beforeunload', function() {
        const logos = document.querySelectorAll('.logo');
        logos.forEach(logo => {
            logo.style.opacity = '1';
            logo.style.visibility = 'visible';
        });
    });
    
    // Garantir que a logo apareça imediatamente ao carregar
    document.addEventListener('DOMContentLoaded', function() {
        const logos = document.querySelectorAll('.logo');
        logos.forEach(logo => {
            logo.style.opacity = '1';
            logo.style.visibility = 'visible';
        });
    });
})();
