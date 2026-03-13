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
    initializeViewControls();
    initializeFilters();
});
function initializeViewControls() {
    const viewButtons = document.querySelectorAll('.view-btn');
    const gridView = document.getElementById('atores-grid');
    const tableView = document.getElementById('atores-table');
    viewButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.dataset.view;
            viewButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            if (view === 'grid') {
                tableView.style.display = 'none';
                gridView.style.display = 'grid';
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
function initializeFilters() {
    const searchInput = document.getElementById('searchInput');
    const nacionalidadeFilter = document.getElementById('nacionalidadeFilter');
    const sortSelect = document.getElementById('sortSelect');
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            filtrarAtores();
        }, 300);
    });
    nacionalidadeFilter.addEventListener('change', filtrarAtores);
    sortSelect.addEventListener('change', ordenarAtores);
}
function filtrarAtores() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const nacionalidade = document.getElementById('nacionalidadeFilter').value;
    const gridCards = document.querySelectorAll('#atores-grid .movie-card-pro');
    const tableRows = document.querySelectorAll('#atores-table tbody tr');
    let visibleCount = 0;
    gridCards.forEach(card => {
        const nome = card.querySelector('h3').textContent.toLowerCase();
        const cardNacionalidade = card.dataset.nacionalidade;
        const matchSearch = nome.includes(search);
        const matchNacionalidade = !nacionalidade || cardNacionalidade === nacionalidade;
        if (matchSearch && matchNacionalidade) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    tableRows.forEach(row => {
        const nome = row.querySelector('h4').textContent.toLowerCase();
        const rowNacionalidade = row.dataset.nacionalidade;
        const matchSearch = nome.includes(search);
        const matchNacionalidade = !nacionalidade || rowNacionalidade === nacionalidade;
        if (matchSearch && matchNacionalidade) {
            row.style.display = 'table-row';
        } else {
            row.style.display = 'none';
        }
    });
    updateEmptyState(visibleCount === 0 && (search.length > 0 || nacionalidade));
}
function ordenarAtores() {
    const sortBy = document.getElementById('sortSelect').value;
    const gridView = document.getElementById('atores-grid');
    const tableView = document.getElementById('atores-table');
    const gridCards = Array.from(gridView.querySelectorAll('.movie-card-pro'));
    gridCards.sort((a, b) => {
        let aVal, bVal;
        switch(sortBy) {
            case 'id':
                aVal = parseInt(a.dataset.atorId);
                bVal = parseInt(b.dataset.atorId);
                break;
            case 'nome':
                aVal = a.querySelector('h3').textContent;
                bVal = b.querySelector('h3').textContent;
                break;
            case 'nacionalidade':
                aVal = a.dataset.nacionalidade || '';
                bVal = b.dataset.nacionalidade || '';
                break;
            case 'filmes':
                aVal = parseInt(a.querySelector('.duration').textContent.split(' ')[0]);
                bVal = parseInt(b.querySelector('.duration').textContent.split(' ')[0]);
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
    const tableBody = tableView.querySelector('tbody');
    const tableRows = Array.from(tableBody.querySelectorAll('tr'));
    tableRows.sort((a, b) => {
        let aVal, bVal;
        switch(sortBy) {
            case 'id':
                aVal = parseInt(a.dataset.atorId);
                bVal = parseInt(b.dataset.atorId);
                break;
            case 'nome':
                aVal = a.querySelector('h4').textContent;
                bVal = b.querySelector('h4').textContent;
                break;
            case 'nacionalidade':
                aVal = a.dataset.nacionalidade || '';
                bVal = b.dataset.nacionalidade || '';
                break;
            case 'filmes':
                aVal = parseInt(a.querySelector('.count-badge').textContent);
                bVal = parseInt(b.querySelector('.count-badge').textContent);
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
    document.getElementById('nacionalidadeFilter').value = '';
    filtrarAtores();
}
function abrirModalAdicionarAtor() {
    const modal = document.getElementById('modalAdicionarAtor');
    modal.style.display = 'flex';
    const modalContent = modal.querySelector('.modal-content');
    modalContent.style.transform = 'translateY(50px) scale(0.9)';
    modalContent.style.opacity = '0';
    setTimeout(() => {
        modalContent.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        modalContent.style.transform = 'translateY(0) scale(1)';
        modalContent.style.opacity = '1';
    }, 10);
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
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
            const submitBtn = form.querySelector('.btn-confirm');
            if (submitBtn) {
                submitBtn.disabled = false;
                if (modalId === 'modalAdicionarAtor') {
                    submitBtn.innerHTML = '<i class="fas fa-save"></i> Adicionar Ator';
                } else if (modalId === 'modalEditarAtor') {
                    submitBtn.innerHTML = '<i class="fas fa-save"></i> Salvar Alterações';
                }
            }
        }
    }, 300);
}
function editarAtor(id) {
    fetch(`/admin/atores/${id}/dados`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(ator => {
            if (ator.error) {
                throw new Error(ator.error);
            }
            const nomeField = document.getElementById('edit_nome');
            const nacionalidadeField = document.getElementById('edit_nacionalidade');
            if (nomeField) nomeField.value = ator.nome || '';
            if (nacionalidadeField) nacionalidadeField.value = ator.nacionalidade || '';
            document.getElementById('formEditarAtor').action = `/admin/atores/editar/${id}`;
            abrirModalEditarAtor();
        })
        .catch(error => {
            console.error('Erro ao carregar dados do ator:', error);
            showNotification('Erro ao carregar dados do ator: ' + error.message, 'error');
        });
}
function abrirModalEditarAtor() {
    const modal = document.getElementById('modalEditarAtor');
    modal.style.display = 'flex';
    const modalContent = modal.querySelector('.modal-content');
    modalContent.style.transform = 'translateY(50px) scale(0.9)';
    modalContent.style.opacity = '0';
    setTimeout(() => {
        modalContent.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        modalContent.style.transform = 'translateY(0) scale(1)';
        modalContent.style.opacity = '1';
    }, 10);
    setTimeout(() => {
        document.getElementById('edit_nome').focus();
    }, 400);
}
function removerAtor(id, nome) {
    const confirmModal = createConfirmModal(
        'Remover Ator',
        `Tem certeza que deseja remover o ator "${nome}"?`,
        'Esta ação não pode ser desfeita.',
        () => {
            const row = document.querySelector(`tr[data-ator-id="${id}"]`);
            if (row) {
                row.style.transition = 'all 0.4s ease';
                row.style.transform = 'scale(0.8) translateX(-20px)';
                row.style.opacity = '0';
            }
            fetch(`/admin/atores/remover/${id}`, {
                method: 'POST'
            })
            .then(response => {
                if (response.ok) {
                    setTimeout(() => {
                        location.reload();
                    }, 400);
                } else {
                    showNotification('Erro ao remover ator', 'error');
                    if (row) {
                        row.style.transform = '';
                        row.style.opacity = '1';
                    }
                }
            })
            .catch(() => {
                showNotification('Erro ao remover ator', 'error');
                if (row) {
                    row.style.transform = '';
                    row.style.opacity = '1';
                }
            });
        }
    );
    document.body.appendChild(confirmModal);
}
let searchTimeout;
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const search = this.value.toLowerCase();
            searchTimeout = setTimeout(() => {
                const rows = document.querySelectorAll('.movies-table-pro tbody tr');
                let visibleTableCount = 0;
                rows.forEach(row => {
                    const nome = row.querySelector('h4').textContent.toLowerCase();
                    const nacionalidade = row.querySelector('.genre-tag').textContent.toLowerCase();
                    if (nome.includes(search) || nacionalidade.includes(search)) {
                        row.style.display = 'table-row';
                        row.style.animation = 'fadeIn 0.3s ease';
                        visibleTableCount++;
                    } else {
                        row.style.display = 'none';
                    }
                });
                const cards = document.querySelectorAll('#atores-grid .movie-card-pro');
                let visibleGridCount = 0;
                cards.forEach(card => {
                    const nome = card.querySelector('h3').textContent.toLowerCase();
                    const nacionalidade = card.querySelector('.genre').textContent.toLowerCase();
                    if (nome.includes(search) || nacionalidade.includes(search)) {
                        card.style.display = 'block';
                        visibleGridCount++;
                    } else {
                        card.style.display = 'none';
                    }
                });
                const activeView = document.querySelector('.view-btn.active').dataset.view;
                const visibleCount = activeView === 'grid' ? visibleGridCount : visibleTableCount;
                updateEmptyState(visibleCount === 0 && search.length > 0);
            }, 300);
        });
    }
});
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
function createConfirmModal(title, message, subtitle, onConfirm) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.style.display = 'flex';
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
                <button class="btn-cancel">Cancelar</button>
                <button class="btn-confirm" style="background: linear-gradient(135deg, #ef4444, #dc2626);">
                    <i class="fas fa-trash"></i> Remover
                </button>
            </div>
        </div>
    `;
    
    modal.querySelector('.btn-cancel').onclick = function() {
        modal.remove();
    };
    
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
function updateEmptyState(show) {
    let emptyState = document.querySelector('.empty-state-filter');
    if (show && !emptyState) {
        emptyState = document.createElement('div');
        emptyState.className = 'empty-state-filter';
        emptyState.innerHTML = `
            <i class="fas fa-search"></i>
            <h3>Nenhum ator encontrado</h3>
            <p>Tente ajustar os filtros de pesquisa.</p>
        `;
        const activeView = document.querySelector('.view-btn.active').dataset.view;
        if (activeView === 'grid') {
            document.getElementById('atores-grid').appendChild(emptyState);
        } else {
            document.querySelector('.movies-table-container').parentNode.appendChild(emptyState);
        }
    } else if (!show && emptyState) {
        emptyState.remove();
    }
}
document.querySelector('#modalAdicionarAtor form').addEventListener('submit', function(e) {
    const nome = document.getElementById('nome').value.trim();
    if (!nome) {
        e.preventDefault();
        showNotification('Por favor, preencha o nome do ator', 'error');
        document.getElementById('nome').focus();
        return;
    }
    const submitBtn = this.querySelector('.btn-confirm');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adicionando...';
    submitBtn.disabled = true;
});
document.querySelector('#formEditarAtor').addEventListener('submit', function(e) {
    const nome = document.getElementById('edit_nome').value.trim();
    if (!nome) {
        e.preventDefault();
        showNotification('Por favor, preencha o nome do ator', 'error');
        document.getElementById('edit_nome').focus();
        return;
    }
    const submitBtn = this.querySelector('.btn-confirm');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';
    submitBtn.disabled = true;
    const atorId = this.action.split('/').pop();
    const row = document.querySelector(`tr[data-ator-id="${atorId}"]`);
    if (row) {
        row.style.background = 'rgba(255, 215, 0, 0.1)';
        row.style.transform = 'scale(1.02)';
    }
});