// Admin Cinemas JavaScript

// Animação de entrada das linhas da tabela
document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('.movies-table-pro tbody tr');
    rows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateY(20px)';
        setTimeout(() => {
            row.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        }, index * 50);
    });

    // Inicializar controles de visualização
    initializeViewControls();
    initializeFilters();
});

// Controles de visualização (Grid/Table)
function initializeViewControls() {
    const viewButtons = document.querySelectorAll('.view-btn');
    const gridView = document.getElementById('cinemas-grid');
    const tableView = document.getElementById('cinemas-table');

    viewButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.dataset.view;
            
            // Atualizar botões ativos
            viewButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Alternar visualizações
            if (view === 'grid') {
                tableView.style.display = 'none';
                gridView.style.display = 'grid';
                
                // Animar cards
                const cards = gridView.querySelectorAll('.movie-card-pro');
                cards.forEach((card, index) => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px) scale(0.9)';
                    setTimeout(() => {
                        card.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0) scale(1)';
                    }, index * 50);
                });
            } else {
                gridView.style.display = 'none';
                tableView.style.display = 'block';
                
                // Animar linhas da tabela
                const rows = tableView.querySelectorAll('tbody tr');
                rows.forEach((row, index) => {
                    row.style.opacity = '0';
                    row.style.transform = 'translateX(-20px)';
                    setTimeout(() => {
                        row.style.transition = 'all 0.3s ease';
                        row.style.opacity = '1';
                        row.style.transform = 'translateX(0)';
                    }, index * 30);
                });
            }
        });
    });
}

// Inicializar filtros
function initializeFilters() {
    const searchInput = document.getElementById('searchInput');
    const regiaoFilter = document.getElementById('regiaoFilter');
    const sortSelect = document.getElementById('sortSelect');

    // Pesquisa com debounce
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            filtrarCinemas();
        }, 300);
    });

    // Filtro de região
    regiaoFilter.addEventListener('change', filtrarCinemas);

    // Ordenação
    sortSelect.addEventListener('change', ordenarCinemas);
}

function filtrarCinemas() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const regiao = document.getElementById('regiaoFilter').value;
    
    const gridCards = document.querySelectorAll('#cinemas-grid .movie-card-pro');
    const tableRows = document.querySelectorAll('#cinemas-table tbody tr');
    
    let visibleCount = 0;

    // Filtrar cards do grid
    gridCards.forEach(card => {
        const nome = card.querySelector('h3').textContent.toLowerCase();
        const localizacao = card.querySelector('.detail-item span').textContent.toLowerCase();
        const cardRegiao = card.dataset.regiao;
        
        const matchSearch = nome.includes(search) || localizacao.includes(search);
        const matchRegiao = !regiao || cardRegiao === regiao;
        
        if (matchSearch && matchRegiao) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    // Filtrar linhas da tabela
    tableRows.forEach(row => {
        const nome = row.querySelector('h4').textContent.toLowerCase();
        const localizacao = row.querySelector('.location-text').textContent.toLowerCase();
        const rowRegiao = row.dataset.regiao;
        
        const matchSearch = nome.includes(search) || localizacao.includes(search);
        const matchRegiao = !regiao || rowRegiao === regiao;
        
        if (matchSearch && matchRegiao) {
            row.style.display = 'table-row';
        } else {
            row.style.display = 'none';
        }
    });

    // Mostrar mensagem se não encontrar resultados
    updateEmptyState(visibleCount === 0 && (search.length > 0 || regiao));
}

function ordenarCinemas() {
    const sortBy = document.getElementById('sortSelect').value;
    const gridView = document.getElementById('cinemas-grid');
    const tableView = document.getElementById('cinemas-table');
    
    // Ordenar grid
    const gridCards = Array.from(gridView.querySelectorAll('.movie-card-pro'));
    gridCards.sort((a, b) => {
        let aVal, bVal;
        
        switch(sortBy) {
            case 'id':
                aVal = parseInt(a.dataset.cinemaId);
                bVal = parseInt(b.dataset.cinemaId);
                break;
            case 'nome':
                aVal = a.querySelector('h3').textContent;
                bVal = b.querySelector('h3').textContent;
                break;
            case 'regiao':
                aVal = a.dataset.regiao || '';
                bVal = b.dataset.regiao || '';
                break;
            case 'salas':
                aVal = parseInt(a.querySelector('.stat-badge.salas').textContent.split(' ')[0]);
                bVal = parseInt(b.querySelector('.stat-badge.salas').textContent.split(' ')[0]);
                break;
            case 'filmes':
                aVal = parseInt(a.querySelector('.stat-badge.filmes').textContent.split(' ')[0]);
                bVal = parseInt(b.querySelector('.stat-badge.filmes').textContent.split(' ')[0]);
                break;
            default:
                return 0;
        }
        
        if (typeof aVal === 'string') {
            return aVal.localeCompare(bVal);
        }
        return aVal - bVal;
    });
    
    gridCards.forEach(card => gridView.appendChild(card));
    
    // Ordenar tabela
    const tableBody = tableView.querySelector('tbody');
    const tableRows = Array.from(tableBody.querySelectorAll('tr'));
    tableRows.sort((a, b) => {
        let aVal, bVal;
        
        switch(sortBy) {
            case 'id':
                aVal = parseInt(a.dataset.cinemaId);
                bVal = parseInt(b.dataset.cinemaId);
                break;
            case 'nome':
                aVal = a.querySelector('h4').textContent;
                bVal = b.querySelector('h4').textContent;
                break;
            case 'regiao':
                aVal = a.dataset.regiao || '';
                bVal = b.dataset.regiao || '';
                break;
            case 'salas':
                aVal = parseInt(a.querySelector('.count-badge.salas').textContent);
                bVal = parseInt(b.querySelector('.count-badge.salas').textContent);
                break;
            case 'filmes':
                aVal = parseInt(a.querySelector('.count-badge.filmes').textContent);
                bVal = parseInt(b.querySelector('.count-badge.filmes').textContent);
                break;
            default:
                return 0;
        }
        
        if (typeof aVal === 'string') {
            return aVal.localeCompare(bVal);
        }
        return aVal - bVal;
    });
    
    tableRows.forEach(row => tableBody.appendChild(row));
}

function limparFiltros() {
    document.getElementById('searchInput').value = '';
    document.getElementById('regiaoFilter').value = '';
    filtrarCinemas();
}

function abrirModalAdicionarCinema() {
    const modal = document.getElementById('modalAdicionarCinema');
    modal.style.display = 'flex';
    
    // Animação de entrada
    const modalContent = modal.querySelector('.modal-content');
    modalContent.style.transform = 'translateY(50px) scale(0.9)';
    modalContent.style.opacity = '0';
    
    setTimeout(() => {
        modalContent.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        modalContent.style.transform = 'translateY(0) scale(1)';
        modalContent.style.opacity = '1';
    }, 10);
    
    // Focar no primeiro campo
    setTimeout(() => {
        document.getElementById('nome').focus();
    }, 400);
}

function fecharModal(modalId) {
    const modal = document.getElementById(modalId);
    const modalContent = modal.querySelector('.modal-content');
    
    modalContent.style.transform = 'translateY(30px) scale(0.95)';
    modalContent.style.opacity = '0';
    
    setTimeout(() => {
        modal.style.display = 'none';
        // Reset form
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
            // Resetar botões de submit
            const submitBtn = form.querySelector('.btn-confirm');
            if (submitBtn) {
                submitBtn.disabled = false;
                if (modalId === 'modalAdicionarCinema') {
                    submitBtn.innerHTML = '<i class="fas fa-save"></i> Adicionar Cinema';
                } else if (modalId === 'modalEditarCinema') {
                    submitBtn.innerHTML = '<i class="fas fa-save"></i> Salvar Alterações';
                }
            }
        }
    }, 300);
}

function editarCinema(id) {
    // Buscar dados do cinema via AJAX
    fetch(`/admin/cinemas/editar/${id}`, {
        headers: {
            'Accept': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao carregar dados do cinema');
            }
            return response.json();
        })
        .then(cinema => {
            // Preencher o formulário de edição
            document.getElementById('edit_nome').value = cinema.nome || '';
            document.getElementById('edit_localizacao').value = cinema.localizacao || '';
            document.getElementById('edit_regiao').value = cinema.regiao || '';
            document.getElementById('edit_email').value = cinema.email || '';
            document.getElementById('edit_telefone').value = cinema.telefone || '';
            document.getElementById('edit_imagem_url').value = cinema.imagem_url || '';
            document.getElementById('edit_descricao').value = cinema.descricao || '';
            
            // Configurar o formulário para enviar para a rota correta
            document.getElementById('formEditarCinema').action = `/admin/cinemas/editar/${id}`;
            
            // Abrir modal
            abrirModalEditarCinema();
        })
        .catch(error => {
            console.error('Erro ao carregar dados do cinema:', error);
            showNotification('Erro ao carregar dados do cinema', 'error');
        });
}

function abrirModalEditarCinema() {
    const modal = document.getElementById('modalEditarCinema');
    modal.style.display = 'flex';
    
    // Animação de entrada
    const modalContent = modal.querySelector('.modal-content');
    modalContent.style.transform = 'translateY(50px) scale(0.9)';
    modalContent.style.opacity = '0';
    
    setTimeout(() => {
        modalContent.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        modalContent.style.transform = 'translateY(0) scale(1)';
        modalContent.style.opacity = '1';
    }, 10);
    
    // Focar no primeiro campo
    setTimeout(() => {
        document.getElementById('edit_nome').focus();
    }, 400);
}

function removerCinema(id, nome) {
    // Criar modal de confirmação personalizado
    const confirmModal = createConfirmModal(
        'Remover Cinema',
        `Tem certeza que deseja remover o cinema "${nome}"?`,
        'Esta ação não pode ser desfeita e removerá todas as sessões associadas.',
        () => {
            // Adicionar animação de saída
            const row = document.querySelector(`tr[data-cinema-id="${id}"]`);
            const card = document.querySelector(`div[data-cinema-id="${id}"]`);
            
            if (row) {
                row.style.transition = 'all 0.4s ease';
                row.style.transform = 'scale(0.8) translateX(-20px)';
                row.style.opacity = '0';
            }
            
            if (card) {
                card.style.transition = 'all 0.4s ease';
                card.style.transform = 'scale(0.8) translateY(-20px)';
                card.style.opacity = '0';
            }
            
            // Fazer requisição
            fetch(`/admin/cinemas/remover/${id}`, {
                method: 'POST'
            })
            .then(response => {
                if (response.ok) {
                    setTimeout(() => {
                        location.reload();
                    }, 400);
                } else {
                    showNotification('Erro ao remover cinema', 'error');
                    // Reverter animação
                    if (row) {
                        row.style.transform = '';
                        row.style.opacity = '1';
                    }
                    if (card) {
                        card.style.transform = '';
                        card.style.opacity = '1';
                    }
                }
            })
            .catch(() => {
                showNotification('Erro ao remover cinema', 'error');
                // Reverter animação
                if (row) {
                    row.style.transform = '';
                    row.style.opacity = '1';
                }
                if (card) {
                    card.style.transform = '';
                    card.style.opacity = '1';
                }
            });
        }
    );
    
    document.body.appendChild(confirmModal);
}

function updateEmptyState(show) {
    let emptyState = document.querySelector('.empty-state-filter');
    
    if (show && !emptyState) {
        emptyState = document.createElement('div');
        emptyState.className = 'empty-state-filter';
        emptyState.innerHTML = `
            <i class="fas fa-search"></i>
            <h3>Nenhum cinema encontrado</h3>
            <p>Tente ajustar os filtros de pesquisa.</p>
        `;
        
        const activeView = document.querySelector('.view-btn.active').dataset.view;
        if (activeView === 'grid') {
            document.getElementById('cinemas-grid').appendChild(emptyState);
        } else {
            document.querySelector('.movies-table-container').parentNode.appendChild(emptyState);
        }
    } else if (!show && emptyState) {
        emptyState.remove();
    }
}

// Fechar modal ao clicar fora
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal-overlay')) {
        const modalContent = e.target.querySelector('.modal-content');
        modalContent.style.transform = 'translateY(30px) scale(0.95)';
        modalContent.style.opacity = '0';
        
        setTimeout(() => {
            e.target.style.display = 'none';
        }, 300);
    }
});

// Funções utilitárias
function createConfirmModal(title, message, subtitle, onConfirm) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 400px;">
            <div class="modal-header">
                <h2><i class="fas fa-exclamation-triangle" style="color: #f59e0b;"></i> ${title}</h2>
            </div>
            <div class="modal-body">
                <p style="color: #ffffff; font-size: 1.1rem; margin-bottom: 8px;">${message}</p>
                <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">${subtitle}</p>
            </div>
            <div class="modal-actions">
                <button class="btn-cancel" onclick="this.closest('.modal-overlay').remove()">Cancelar</button>
                <button class="btn-confirm" style="background: linear-gradient(135deg, #ef4444, #dc2626);">
                    <i class="fas fa-trash"></i> Remover
                </button>
            </div>
        </div>
    `;
    
    modal.querySelector('.btn-confirm').onclick = function() {
        onConfirm();
        modal.remove();
    };
    
    return modal;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        transform: translateX(400px);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    `;
    
    if (type === 'error') {
        notification.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
    } else if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, #10b981, #059669)';
    } else {
        notification.style.background = 'linear-gradient(135deg, #3b82f6, #2563eb)';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => notification.remove(), 400);
    }, 3000);
}

// Validação do formulário de adicionar
document.addEventListener('DOMContentLoaded', function() {
    const addForm = document.querySelector('#modalAdicionarCinema form');
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            const nome = document.getElementById('nome').value.trim();
            const regiao = document.getElementById('regiao').value.trim();
            
            if (!nome || !regiao) {
                e.preventDefault();
                showNotification('Por favor, preencha o nome e a região', 'error');
                if (!nome) document.getElementById('nome').focus();
                else if (!regiao) document.getElementById('regiao').focus();
                return;
            }
            
            // Mostrar loading no botão
            const submitBtn = this.querySelector('.btn-confirm');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adicionando...';
            submitBtn.disabled = true;
        });
    }
});

// Validação do formulário de editar
document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.querySelector('#formEditarCinema');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            const nome = document.getElementById('edit_nome').value.trim();
            const localizacao = document.getElementById('edit_localizacao').value.trim();
            
            if (!nome || !localizacao) {
                e.preventDefault();
                showNotification('Por favor, preencha os campos obrigatórios', 'error');
                if (!nome) document.getElementById('edit_nome').focus();
                else if (!localizacao) document.getElementById('edit_localizacao').focus();
                return;
            }
            
            // Mostrar loading no botão
            const submitBtn = this.querySelector('.btn-confirm');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';
            submitBtn.disabled = true;
            
            // Adicionar feedback visual na linha da tabela
            const cinemaId = this.action.split('/').pop();
            const row = document.querySelector(`tr[data-cinema-id="${cinemaId}"]`);
            if (row) {
                row.style.background = 'rgba(255, 215, 0, 0.1)';
                row.style.transform = 'scale(1.02)';
            }
        });
    }
});