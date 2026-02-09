// JavaScript LIMPO para reserva - SEM manipulação de estilos inline
document.addEventListener('DOMContentLoaded', function() {
    const quantityOptions = document.querySelectorAll('.quantity-option');
    const customQuantity = document.getElementById('customQuantity');
    const decreaseBtn = document.getElementById('decreaseBtn');
    const increaseBtn = document.getElementById('increaseBtn');
    const advanceBtn = document.getElementById('advanceBtn');
    const selectedQuantityInput = document.getElementById('selectedQuantity');
    let selectedQuantity = 1;
    
    // Seleciona automaticamente 1 bilhete no início
    if (quantityOptions.length > 0) {
        quantityOptions[0].classList.add('selected');
        advanceBtn.disabled = false;
        updateButtonText();
    }
    
    // Seleção de quantidade pré-definida - SEM EFEITOS VISUAIS INLINE
    quantityOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove seleção anterior
            quantityOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Adiciona seleção atual
            this.classList.add('selected');
            selectedQuantity = parseInt(this.dataset.quantity);
            
            // Atualiza input personalizado
            if (customQuantity) customQuantity.value = selectedQuantity;
            if (selectedQuantityInput) selectedQuantityInput.value = selectedQuantity;
            
            // Habilita botão avançar
            if (advanceBtn) advanceBtn.disabled = false;
            updateButtonText();
        });
    });
    
    // Botões de quantidade personalizada
    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', function() {
            let current = parseInt(customQuantity.value);
            if (current > 1) {
                customQuantity.value = current - 1;
                updateSelection();
            }
        });
    }
    
    if (increaseBtn) {
        increaseBtn.addEventListener('click', function() {
            let current = parseInt(customQuantity.value);
            if (current < 20) {
                customQuantity.value = current + 1;
                updateSelection();
            }
        });
    }
    
    // Input personalizado
    if (customQuantity) {
        customQuantity.addEventListener('input', function() {
            let value = parseInt(this.value);
            if (isNaN(value) || value < 1) {
                this.value = 1;
            } else if (value > 20) {
                this.value = 20;
            }
            updateSelection();
        });
    }
    
    function updateSelection() {
        selectedQuantity = parseInt(customQuantity.value);
        if (selectedQuantityInput) selectedQuantityInput.value = selectedQuantity;
        
        // Remove todas as seleções
        quantityOptions.forEach(opt => opt.classList.remove('selected'));
        
        // Seleciona opção correspondente se existir
        if (selectedQuantity <= 6) {
            const matchingOption = document.querySelector(`[data-quantity="${selectedQuantity}"]`);
            if (matchingOption) {
                matchingOption.classList.add('selected');
            }
        }
        
        if (advanceBtn) advanceBtn.disabled = selectedQuantity < 1;
        updateButtonText();
    }
    
    function updateButtonText() {
        if (!advanceBtn) return;
        const icon = '<i class="fas fa-arrow-right"></i>';
        if (selectedQuantity === 1) {
            advanceBtn.innerHTML = `${icon} Avançar para Seleção de Lugares`;
        } else {
            advanceBtn.innerHTML = `${icon} Selecionar ${selectedQuantity} Lugares`;
        }
    }
    
    // Loading no submit
    if (advanceBtn) {
        const form = advanceBtn.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                advanceBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Carregando...';
                advanceBtn.disabled = true;
            });
        }
    }
});
