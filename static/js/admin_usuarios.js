// Admin Usuarios JavaScript - Following admin_filmes pattern

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

    // Date filter buttons
    document.querySelectorAll('.date-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.date-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            applyFilters();
        });
    });

    // Status filter
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', applyFilters);
    }

    // Sort select
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            currentSort = this.value;
            sortUsers();
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
    const gridElement = document.getElementById('usuarios-grid');
    const tableElement = document.getElementById('usuarios-table');
    
    if (currentView === 'grid') {
        if (gridElement) gridElement.style.display = 'grid';
        if (tableElement) tableElement.style.display = 'none';
    } else {
        if (gridElement) gridElement.style.display = 'none';
        if (tableElement) tableElement.style.display = 'block';
    }
}

// Sort users
function sortUsers() {
    const containers = [
        document.querySelector('#usuarios-grid'),
        document.querySelector('#usuarios-table tbody')
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
                    
                case 'email':
                    aValue = a.querySelector('.director-cell, .email').textContent.toLowerCase();
                    bValue = b.querySelector('.director-cell, .email').textContent.toLowerCase();
                    return aValue.localeCompare(bValue);
                    
                case 'criado_em':
                    aValue = new Date(a.dataset.criado);
                    bValue = new Date(b.dataset.criado);
                    return bValue - aValue; // Descending order
                    
                default: // id
                    aValue = parseInt(a.dataset.usuarioId) || 0;
                    bValue = parseInt(b.dataset.usuarioId) || 0;
                    return bValue - aValue; // Descending order for ID
            }
        });
        
        // Reorder elements
        items.forEach(item => container.appendChild(item));
    });
}

// Modal Management
function abrirModalAdicionarUsuario() {
    document.getElementById('modalAdicionarUsuario').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function fecharModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    document.body.style.overflow = 'auto';
}

// User Management
function removerUsuario(usuarioId) {
    if (confirm('Tem certeza que deseja remover este usuário? Esta ação não pode ser desfeita e removerá todas as reservas associadas.')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/usuarios/remover/${usuarioId}`;
        
        document.body.appendChild(form);
        form.submit();
    }
}

async function verUsuarioDetalhes(usuarioId) {
    try {
        // Mostrar loading
        document.getElementById('usuarioDetalhesContent').innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i>
                Carregando detalhes do usuário...
            </div>
        `;
        
        // Abrir modal
        document.getElementById('modalVerUsuario').style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Carregar dados
        const response = await fetch(`/admin/usuarios/${usuarioId}/detalhes`);
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('usuarioDetalhesContent').innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Erro ao carregar detalhes do usuário</p>
                </div>
            `;
            return;
        }
        
        // Renderizar detalhes
        let reservasHtml = '';
        if (data.ultimas_reservas && data.ultimas_reservas.length > 0) {
            reservasHtml = `
                <div class="reservas-section">
                    <div class="section-header">
                        <h4><i class="fas fa-ticket-alt"></i> Últimas Reservas</h4>
                        <span class="reservas-count">${data.ultimas_reservas.length} reserva${data.ultimas_reservas.length > 1 ? 's' : ''}</span>
                    </div>
                    <div class="reservas-list">
                        ${data.ultimas_reservas.map((reserva, index) => `
                            <div class="reserva-card" style="animation-delay: ${index * 0.1}s">
                                <div class="reserva-main">
                                    <div class="filme-header">
                                        <div class="filme-icon">
                                            <i class="fas fa-film"></i>
                                        </div>
                                        <div class="filme-title">
                                            <h5>${reserva.filme_titulo}</h5>
                                            <span class="cinema-name">
                                                <i class="fas fa-map-marker-alt"></i>
                                                ${reserva.cinema_nome}
                                            </span>
                                        </div>
                                        <div class="tipo-badge ${reserva.tipo_sessao.toLowerCase().replace(/\s+/g, '')}">
                                            ${reserva.tipo_sessao}
                                        </div>
                                    </div>
                                    <div class="reserva-info">
                                        <div class="info-row">
                                            <div class="info-col">
                                                <i class="fas fa-calendar"></i>
                                                <span>Data: ${new Date(reserva.data_sessao).toLocaleDateString('pt-PT')}</span>
                                            </div>
                                            <div class="info-col">
                                                <i class="fas fa-chair"></i>
                                                <span>Lugares: ${reserva.lugares}</span>
                                            </div>
                                        </div>
                                        <div class="info-row">
                                            <div class="info-col">
                                                <i class="fas fa-clock"></i>
                                                <span>Reservado: ${new Date(reserva.data_reserva).toLocaleDateString('pt-PT')}</span>
                                            </div>
                                            ${reserva.total ? `
                                            <div class="info-col">
                                                <i class="fas fa-euro-sign"></i>
                                                <span>Total: ${reserva.total}€</span>
                                            </div>
                                            ` : '<div class="info-col"></div>'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            reservasHtml = `
                <div class="reservas-section">
                    <div class="section-header">
                        <h4><i class="fas fa-ticket-alt"></i> Reservas</h4>
                    </div>
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fas fa-ticket-alt"></i>
                        </div>
                        <h5>Nenhuma reserva encontrada</h5>
                        <p>Este usuário ainda não realizou nenhuma reserva no sistema.</p>
                    </div>
                </div>
            `;
        }
        
        document.getElementById('usuarioDetalhesContent').innerHTML = `
            <div class="user-details">
                <div class="user-header">
                    <div class="user-avatar-large">
                        <img src="${data.avatar_url}" alt="${data.nome}" onerror="this.src='/static/imgs/icons/user_icon34-removebg-preview.png'">
                    </div>
                    <div class="user-basic-info">
                        <h3>${data.nome}</h3>
                        <span class="user-type ${data.is_admin ? 'admin' : 'user'}">
                            <i class="fas fa-${data.is_admin ? 'shield-alt' : 'user'}"></i>
                            ${data.is_admin ? 'Administrador' : 'Usuário'}
                        </span>
                    </div>
                </div>
                
                <div class="user-info-grid">
                    <div class="info-section">
                        <h4><i class="fas fa-info-circle"></i> Informações Pessoais</h4>
                        <div class="info-row">
                            <span class="info-label">Email:</span>
                            <span class="info-value">${data.email}</span>
                        </div>
                        ${data.telefone ? `
                        <div class="info-row">
                            <span class="info-label">Telefone:</span>
                            <span class="info-value">${data.telefone}</span>
                        </div>
                        ` : ''}
                        <div class="info-row">
                            <span class="info-label">Data de Registro:</span>
                            <span class="info-value">${data.criado_em || 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Último Login:</span>
                            <span class="info-value">${data.ultimo_login || 'Nunca'}</span>
                        </div>
                    </div>
                    
                    <div class="info-section">
                        <h4><i class="fas fa-chart-bar"></i> Estatísticas</h4>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-number">${data.num_reservas || 0}</div>
                                <div class="stat-label">Total de Reservas</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            ${reservasHtml}
        `;
        
    } catch (error) {
        console.error('Erro ao carregar detalhes do usuário:', error);
        document.getElementById('usuarioDetalhesContent').innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Erro ao carregar detalhes do usuário</p>
            </div>
        `;
    }
}

// Search Functionality
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            applyFilters();
        });
        
        // Auto-search on page load if there's a search term
        if (searchInput.value) {
            applyFilters();
        }
    }
}

// Filter Setup
function setupFilters() {
    // Already handled in initializeEventListeners
}

// Apply all filters
function applyFilters() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    const activeDateBtn = document.querySelector('.date-btn.active');
    const dateRange = activeDateBtn ? activeDateBtn.dataset.date : 'all';
    
    filterUsers(searchTerm, statusFilter, dateRange);
}

function filterUsers(searchTerm, statusFilter, dateRange) {
    const usuarios = document.querySelectorAll('[data-usuario-id]');
    
    usuarios.forEach(usuario => {
        const nome = usuario.querySelector('.movie-title-info h4, .movie-info h3').textContent.toLowerCase();
        const email = usuario.querySelector('.director-cell, .email').textContent.toLowerCase();
        const isAdmin = usuario.dataset.admin === '1';
        const criadoEm = new Date(usuario.dataset.criado);
        
        let visible = true;
        
        // Search filter
        if (searchTerm && !nome.includes(searchTerm) && !email.includes(searchTerm)) {
            visible = false;
        }
        
        // Status filter
        if (statusFilter) {
            if (statusFilter === 'admin' && !isAdmin) visible = false;
            if (statusFilter === 'user' && isAdmin) visible = false;
        }
        
        // Date filter
        if (dateRange !== 'all' && criadoEm) {
            const now = new Date();
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
            
            if (dateRange === 'today' && criadoEm < today) visible = false;
            if (dateRange === 'week' && criadoEm < weekAgo) visible = false;
            if (dateRange === 'month' && criadoEm < monthAgo) visible = false;
        }
        
        usuario.style.display = visible ? '' : 'none';
    });
}

function limparFiltros() {
    // Clear search
    document.getElementById('searchInput').value = '';
    
    // Reset status filter
    document.getElementById('statusFilter').value = '';
    
    // Reset date filter
    document.querySelectorAll('.date-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.date-btn[data-date="all"]').classList.add('active');
    
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
    
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.value && !emailRegex.test(this.value)) {
                this.style.borderColor = '#ff4757';
                alert('Por favor, insira um email válido.');
            } else {
                this.style.borderColor = 'rgba(255, 215, 0, 0.3)';
            }
        });
    });
    
    // Password validation
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value && this.value.length < 6) {
                this.style.borderColor = '#ff4757';
            } else {
                this.style.borderColor = 'rgba(255, 215, 0, 0.3)';
            }
        });
    });
});

// Loading state styles
const loadingStyle = document.createElement('style');
loadingStyle.textContent = `
    .loading {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 40px;
        color: #9ca3af;
    }
    
    .loading i {
        animation: spin 1s linear infinite;
        margin-right: 8px;
        font-size: 1.2rem;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .error-state {
        text-align: center;
        padding: 40px;
        color: #ef4444;
    }
    
    .error-state i {
        font-size: 2rem;
        margin-bottom: 12px;
    }
    
    .user-details {
        padding: 20px 0;
    }
    
    .user-header {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    .user-avatar-large {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        overflow: hidden;
        border: 3px solid #FFD700;
    }
    
    .user-avatar-large img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .user-basic-info h3 {
        color: #ffffff;
        font-size: 1.5rem;
        margin: 0 0 8px 0;
    }
    
    .user-type {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .user-type.admin {
        background: rgba(255, 215, 0, 0.2);
        color: #FFD700;
    }
    
    .user-type.user {
        background: rgba(59, 130, 246, 0.2);
        color: #3b82f6;
    }
    
    .user-info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 30px;
        margin-bottom: 30px;
    }
    
    .info-section h4 {
        color: #FFD700;
        font-size: 1.1rem;
        margin: 0 0 15px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .info-label {
        color: #9ca3af;
        font-weight: 500;
    }
    
    .info-value {
        color: #ffffff;
        font-weight: 400;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    .stat-item {
        text-align: center;
        padding: 15px;
        background: rgba(255, 215, 0, 0.1);
        border-radius: 10px;
        border: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #FFD700;
        margin-bottom: 5px;
    }
    
    .stat-label {
        color: #d1d5db;
        font-size: 0.9rem;
    }
    
    @media (max-width: 768px) {
        .user-info-grid {
            grid-template-columns: 1fr;
            gap: 20px;
        }
        
        .user-header {
            flex-direction: column;
            text-align: center;
        }
    }
    
    /* ===== DESIGN LIMPO E ESPAÇOSO PARA RESERVAS ===== */
    .reservas-section {
        margin-top: 30px;
        padding-top: 25px;
        border-top: 2px solid rgba(255, 215, 0, 0.2);
        position: relative;
        width: 100%;
        overflow: visible;
    }
    
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
    }
    
    .section-header h4 {
        color: #FFD700;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .reservas-count {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 215, 0, 0.1));
        color: #FFD700;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    
    .reservas-list {
        display: flex;
        gap: 20px;
        overflow-x: auto;
        overflow-y: hidden;
        padding: 12px 8px 20px 8px;
        scroll-behavior: smooth;
        width: 100%;
        min-height: 240px;
    }
    
    .reserva-card {
        background: linear-gradient(135deg, #1e293b, #334155);
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 12px;
        padding: 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        animation: slideInUp 0.5s ease forwards;
        opacity: 0;
        transform: translateY(20px);
        flex: 0 0 340px;
        height: 220px;
        min-width: 340px;
    }
    
    @keyframes slideInUp {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .reserva-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(to bottom, #FFD700, #FFA500);
        border-radius: 0 2px 2px 0;
    }
    
    .reserva-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 215, 0, 0.4);
        background: linear-gradient(135deg, #1e293b, #374151);
    }
    
    .reserva-main {
        padding: 20px;
        padding-left: 24px;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .filme-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .filme-icon {
        width: 45px;
        height: 45px;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #1a1a2e;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    
    .filme-title {
        flex: 1;
        min-width: 0;
    }
    
    .filme-title h5 {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0 0 6px 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .cinema-name {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .cinema-name i {
        color: #FFD700;
        font-size: 0.8rem;
    }
    
    .tipo-badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 1px solid;
        flex-shrink: 0;
    }
    
    .tipo-badge.2d {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(34, 197, 94, 0.1));
        color: #22c55e;
        border-color: rgba(34, 197, 94, 0.3);
    }
    
    .tipo-badge.3d {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(168, 85, 247, 0.1));
        color: #a855f7;
        border-color: rgba(168, 85, 247, 0.3);
    }
    
    .tipo-badge.imax {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));
        color: #ef4444;
        border-color: rgba(239, 68, 68, 0.3);
    }
    
    .tipo-badge.4dx {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.1));
        color: #f59e0b;
        border-color: rgba(245, 158, 11, 0.3);
    }
    
    .reserva-info {
        display: flex;
        flex-direction: column;
        gap: 12px;
        flex: 1;
    }
    
    .info-row {
        display: flex;
        gap: 30px;
    }
    
    .info-col {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #e2e8f0;
        font-size: 0.9rem;
        font-weight: 500;
        flex: 1;
        min-width: 0;
    }
    
    .info-col i {
        color: #FFD700;
        width: 16px;
        text-align: center;
        font-size: 0.85rem;
        flex-shrink: 0;
    }
    
    .info-col span {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    /* Estado vazio */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
        border: 2px dashed rgba(255, 215, 0, 0.3);
        border-radius: 16px;
        color: #94a3b8;
    }
    
    .empty-icon {
        font-size: 4rem;
        color: rgba(255, 215, 0, 0.3);
        margin-bottom: 20px;
    }
    
    .empty-state h5 {
        color: #e2e8f0;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0 0 10px 0;
    }
    
    .empty-state p {
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* Scrollbar horizontal personalizada */
    .reservas-list::-webkit-scrollbar {
        height: 10px;
    }
    
    .reservas-list::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        margin: 0 10px;
    }
    
    .reservas-list::-webkit-scrollbar-thumb {
        background: linear-gradient(to right, #FFD700, #FFA500);
        border-radius: 5px;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    
    .reservas-list::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(to right, #FFA500, #FF8C00);
    }
    
    /* Responsividade */
    @media (max-width: 1400px) {
        .reserva-card {
            flex: 0 0 320px;
            min-width: 320px;
        }
    }
    
    @media (max-width: 1200px) {
        .reserva-card {
            flex: 0 0 300px;
            min-width: 300px;
        }
        
        .modal-content.large {
            width: 98%;
            max-width: none;
        }
    }
    
    @media (max-width: 768px) {
        .reserva-card {
            flex: 0 0 280px;
            min-width: 280px;
            height: 240px;
        }
        
        .reserva-main {
            padding: 16px;
            padding-left: 20px;
        }
        
        .filme-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
        }
        
        .filme-title {
            width: 100%;
        }
        
        .tipo-badge {
            align-self: flex-start;
        }
        
        .info-row {
            flex-direction: column;
            gap: 8px;
        }
        
        .info-col {
            font-size: 0.85rem;
        }
        
        .section-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
        }
        
        .modal-content.large {
            width: 95%;
            margin: 10px;
        }
        
        .modal-body {
            padding: 20px;
        }
    }
    
    @media (max-width: 480px) {
        .reserva-card {
            flex: 0 0 260px;
            min-width: 260px;
            height: 260px;
        }
        
        .reservas-list {
            gap: 15px;
            padding: 10px 5px 15px 5px;
        }
        
        .modal-content.large {
            width: 98%;
            margin: 5px;
        }
    }
            gap: 10px;
        }
    }
    
    @media (max-width: 480px) {
        .reserva-card {
            flex: 0 0 260px;
            height: 240px;
        }
        
        .reservas-list {
            gap: 12px;
        }
    }
`;
document.head.appendChild(loadingStyle);