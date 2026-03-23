document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.newsletter-form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const emailInput = form.querySelector('input[type="email"]');
            const btn = form.querySelector('button[type="submit"]');
            const email = emailInput.value.trim();

            if (!email) return;

            const originalText = btn.textContent;
            btn.textContent = 'A enviar...';
            btn.disabled = true;

            fetch('/newsletter/subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'email=' + encodeURIComponent(email)
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                // Mostrar mensagem inline
                let msg = form.querySelector('.newsletter-msg');
                if (!msg) {
                    msg = document.createElement('p');
                    msg.className = 'newsletter-msg';
                    msg.style.cssText = 'margin:8px 0 0 0;font-size:13px;';
                    form.appendChild(msg);
                }
                if (data.success) {
                    msg.style.color = '#FFD700';
                    emailInput.value = '';
                } else {
                    msg.style.color = '#ff6b6b';
                }
                msg.textContent = data.message;
                btn.textContent = originalText;
                btn.disabled = false;
            })
            .catch(function () {
                btn.textContent = originalText;
                btn.disabled = false;
            });
        });
    });
});
