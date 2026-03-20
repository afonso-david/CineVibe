// Newsletter functionality
document.addEventListener('DOMContentLoaded', function() {
    // Encontrar todos os formulários de newsletter
    const newsletterForms = document.querySelectorAll('.newsletter-form');
    
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[type="email"]');
            const button = this.querySelector('button[type="submit"]');
            const email = emailInput.value.trim();
            
            if (!email) {
                showNotification('Por favor, insira um email válido.', 'error');
                return;
            }
            
            // Validar formato do email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showNotification('Por favor, insira um email válido.', 'error');
                return;
            }
            
            // Desabilitar botão e mostrar loading
            const originalText = button.textContent;
            button.textContent = 'Subscrevendo...';
            button.disabled = true;
            emailInput.disabled = true;
            
            // Enviar dados para o servidor
            fetch('/newsletter/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `email=${encodeURIComponent(email)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    this.reset();
                } else {
                    showNotification(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                showNotification('Erro ao processar subscrição. Tente novamente.', 'error');
            })
            .finally(() => {
                // Restaurar botão
                button.textContent = originalText;
                button.disabled = false;
                emailInput.disabled = false;
            });
        });
    });
});

// Função para mostrar notificações
function showNotification(message, type = 'info') {
    // Remover notificação existente se houver
    const existingNotification = document.querySelector('.newsletter-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Criar nova notificação
    const notification = document.createElement('div');
    notification.className = `newsletter-notification newsletter-notification--${type}`;
    notification.innerHTML = `
        <div class="newsletter-notification__content">
            <span class="newsletter-notification__icon">
                ${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}
            </span>
            <span class="newsletter-notification__message">${message}</span>
            <button class="newsletter-notification__close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Adicionar estilos inline para garantir que funciona
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        max-width: 400px;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        font-family: Arial, sans-serif;
        font-size: 14px;
        line-height: 1.4;
        animation: slideInRight 0.3s ease-out;
        ${type === 'success' ? 'background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724;' : ''}
        ${type === 'error' ? 'background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;' : ''}
        ${type === 'info' ? 'background-color: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460;' : ''}
    `;
    
    const content = notification.querySelector('.newsletter-notification__content');
    content.style.cssText = `
        display: flex;
        align-items: center;
        gap: 12px;
    `;
    
    const icon = notification.querySelector('.newsletter-notification__icon');
    icon.style.cssText = `
        font-size: 18px;
        flex-shrink: 0;
    `;
    
    const messageEl = notification.querySelector('.newsletter-notification__message');
    messageEl.style.cssText = `
        flex: 1;
        margin: 0;
    `;
    
    const closeBtn = notification.querySelector('.newsletter-notification__close');
    closeBtn.style.cssText = `
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background-color 0.2s;
        ${type === 'success' ? 'color: #155724;' : ''}
        ${type === 'error' ? 'color: #721c24;' : ''}
        ${type === 'info' ? 'color: #0c5460;' : ''}
    `;
    
    closeBtn.addEventListener('mouseenter', function() {
        this.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
    });
    
    closeBtn.addEventListener('mouseleave', function() {
        this.style.backgroundColor = 'transparent';
    });
    
    // Adicionar animação CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Adicionar ao DOM
    document.body.appendChild(notification);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideInRight 0.3s ease-out reverse';
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}