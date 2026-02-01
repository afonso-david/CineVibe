// Admin Bar JavaScript - Following admin_filmes pattern

// Global variables
let currentView = 'table';
let currentSort = 'id';

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    setupSearch();
    setupFilters();
    updateViewDisplay();
});

// Initialize all event listeners
function initializeEventListeners() {
    // View toggle buttons
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.dataset.view;
            switchView(view);
        });
    });

    // Price filter buttons
    document.querySelectorAll('.price-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.price-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            applyFilters();
        });
    });

    // Type filter
    const typeFilter = document.getElementById('typeFilter');
    if (typeFilter) {
        typeFilter.addEventListener('change', applyFilters);
    }

    // Sort select
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            currentSort = this.value;
            sortProducts();
        });
    }
}

// Switch between grid and table view
function switchView(view) {
    currentView = view;
    
    // Update button states
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.view === view) {
            btn.classList.add('active');
        }
    });
    
    updateViewDisplay();
}

// Update view display based on current view
function updateViewDisplay() {
    const gridElement = document.getElementById('produtos-grid');
    const tableElement = document.getElementById('produtos-table');
    
    if (currentView === 'grid') {
        if (gridElement) gridElement.style.display = 'grid';
        if (tableElement) tableElement.style.display = 'none';
    } else {
        if (gridElement) gridElement.style.display = 'none';
        if (tableElement) tableElement.style.display = 'block';
    }
}

// Sort products
function sortProducts() {
    const containers = [
        document.querySelector('#produtos-grid'),
        document.querySelector('#produtos-table tbody')
    ];
    
    containers.forEach(container => {
        if (!container) return;
        
        const items = Array.from(container.children);
        
        items.sort((a, b) => {
            let aValue, bValue;
            
            switch (currentSort) {
                case 'nome':
                    aValue = a.querySelector('.movie-title-info h4, .movie-info h3').textContent.toLowerCase();
                    bValue = b.querySelector('.movie-title-info h4, .movie-info h3').textContent.toLowerCase();
                    return aValue.localeCompare(bValue);
                    
                case 'preco':
                    aValue = parseFloat(a.dataset.preco) || 0;
                    bValue = parseFloat(b.dataset.preco) || 0;
                    return aValue - bValue;
                    
                case 'tipo':
                    aValue = a.dataset.tipo || '';
                    bValue = b.dataset.tipo || '';
                    return aValue.localeCompare(bValue);
                    
                default: // id
                    aValue = parseInt(a.dataset.produtoId) || 0;
                    bValue = parseInt(b.dataset.produtoId) || 0;
                    return bValue - aValue; // Descending order for ID
            }
        });
        
        // Reorder elements
        items.forEach(item => container.appendChild(item));
    });
}

// Modal Management
function abrirModalAdicionarProduto() {
    document.getElementById('modalAdicionarProduto').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function fecharModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Product Management
async function editarProduto(produtoId) {
    try {
        const response = await fetch(`/admin/bar/produtos/${produtoId}/dados`);
        const produto = await response.json();
        
        if (produto.error) {
            alert('Erro ao carregar dados do produto');
            return;
        }
        
        // Preencher formulário
        document.getElementById('edit_nome_produto').value = produto.nome || produto.produto || '';
        document.getElementById('edit_tipo_produto').value = produto.tipo || '';
        document.getElementById('edit_preco_produto').value = produto.preco || '';
        document.getElementById('edit_imagem_produto').value = produto.imagem_url || '';
        
        // Configurar ação do formulário
        document.getElementById('formEditarProduto').action = `/admin/bar/produtos/editar/${produtoId}`;
        
        // Abrir modal
        document.getElementById('modalEditarProduto').style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
    } catch (error) {
        console.error('Erro ao carregar produto:', error);
        alert('Erro ao carregar dados do produto');
    }
}

function removerProduto(produtoId) {
    if (confirm('Tem certeza que deseja remover este produto?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/bar/produtos/remover/${produtoId}`;
        
        document.body.appendChild(form);
        form.submit();
    }
}

function verProdutoDetalhes(produtoId) {
    // Placeholder for product details view
    alert(`Ver detalhes do produto ${produtoId} - Funcionalidade em desenvolvimento`);
}

// Search Functionality
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            applyFilters();
        });
    }
}

// Filter Setup
function setupFilters() {
    // Already handled in initializeEventListeners
}

// Apply all filters
function applyFilters() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const typeFilter = document.getElementById('typeFilter').value;
    const activePriceBtn = document.querySelector('.price-btn.active');
    const priceRange = activePriceBtn ? activePriceBtn.dataset.price : 'all';
    
    filterProducts(searchTerm, typeFilter, priceRange);
}

function filterProducts(searchTerm, typeFilter, priceRange) {
    const produtos = document.querySelectorAll('[data-produto-id]');
    
    produtos.forEach(produto => {
        const nome = produto.querySelector('.movie-title-info h4, .movie-info h3').textContent.toLowerCase();
        const tipo = produto.dataset.tipo || '';
        const preco = parseFloat(produto.dataset.preco) || 0;
        
        let visible = true;
        
        // Search filter
        if (searchTerm && !nome.includes(searchTerm) && !tipo.toLowerCase().includes(searchTerm)) {
            visible = false;
        }
        
        // Type filter
        if (typeFilter && tipo !== typeFilter) {
            visible = false;
        }
        
        // Price filter
        if (priceRange !== 'all') {
            if (priceRange === '0-5' && (preco < 0 || preco > 5)) visible = false;
            if (priceRange === '5-10' && (preco < 5 || preco > 10)) visible = false;
            if (priceRange === '10+' && preco < 10) visible = false;
        }
        
        produto.style.display = visible ? '' : 'none';
    });
}

function limparFiltros() {
    // Clear search
    document.getElementById('searchInput').value = '';
    
    // Reset type filter
    document.getElementById('typeFilter').value = '';
    
    // Reset price filter
    document.querySelectorAll('.price-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.price-btn[data-price="all"]').classList.add('active');
    
    // Apply filters
    applyFilters();
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        const modalId = event.target.id;
        fecharModal(modalId);
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal-overlay[style*="flex"]');
        if (openModal) {
            fecharModal(openModal.id);
        }
    }
});

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#ff4757';
                    isValid = false;
                } else {
                    field.style.borderColor = 'rgba(255, 215, 0, 0.3)';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Por favor, preencha todos os campos obrigatórios.');
            }
        });
    });
    
    // Validate price inputs
    const priceInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    priceInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });
});