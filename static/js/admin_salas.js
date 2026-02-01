// Admin Salas JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar controles
    initializeViewControls();
    initializeFilters();
    initializeSearch();
    initializeSort();
    
    // Animação inicial das linhas da tabela
    animateTableRows();
});

// Controles de visualização
function initializeViewControls() {
    const viewButtons = document.querySelectorAll('.view-btn');
    const gridView = document.getElementById('salas-grid');
    const tableView = document.getElementById('salas-table');

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
                animateGridCards();
            } else {
                gridView.style.display = 'none';
                tableView.style.display = 'block';
                animateTableRows();
            }
        });
    });
}

// Inicializar filtros
function initializeFilters() {
    const cinemaFilter = document.getElementById('cinemaFilter');
    const tipoFilter = document.getElementById('tipoFilter');

    if (cinemaFilter) {
        cinemaFilter.addEventListener('change', applyFilters);
    }
    
    if (tipoFilter) {
        tipoFilter.addEventListener('change', applyFilters);
    }
}

// Inicializar pesquisa
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', applyFilters);
    }
}

// Inicializar ordenação
function initializeSort() {
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', sortSalas);
    }
}

// Aplicar filtros
function applyFilters() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const cinemaFilter = document.getElementById('cinemaFilter').value;
    const tipoFilter = document.getElementById('tipoFilter').value;
    
    // Filtrar cards (grid view)
    const cards = document.querySelectorAll('.movie-card-pro');
    cards.forEach(card => {
        const nome = card.querySelector('h3').textContent.toLowerCase();
        const cinema = card.dataset.cinema;
        const tipo = card.dataset.tipo;
        
        const matchesSearch = nome.includes(searchTerm);
        const matchesCinema = !cinemaFilter || cinema === cinemaFilter;
        const matchesTipo = !tipoFilter || tipo === tipoFilter;
        
        if (matchesSearch && matchesCinema && matchesTipo) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
    
    // Filtrar linhas (table view)
    const rows = document.querySelectorAll('.movies-table-pro tbody tr');
    rows.forEach(row => {
        const nome = row.querySelector('h4').textContent.toLowerCase();
        const cinema = row.dataset.cinema;
        const tipo = row.dataset.tipo;
        
        const matchesSearch = nome.includes(searchTerm);
        const matchesCinema = !cinemaFilter || cinema === cinemaFilter;
        const matchesTipo = !tipoFilter || tipo === tipoFilter;
        
        if (matchesSearch && matchesCinema && matchesTipo) {
            row.style.display = 'table-row';
        } else {
            row.style.display = 'none';
        }
    });
}

// Ordenar salas
function sortSalas() {
    const sortBy = document.getElementById('sortSelect').value;
    const gridView = document.getElementById('salas-grid');
    const tableView = document.getElementById('salas-table');
    
    // Ordenar cards
    const cards = Array.from(gridView.querySelectorAll('.movie-card-pro'));
    const rows = Array.from(tableView.querySelectorAll('tbody tr'));
    
    cards.sort((a, b) => {
        switch(sortBy) {
            case 'nome':
                return a.querySelector('h3').textContent.localeCompare(b.querySelector('h3').textContent);
            case 'cinema':
                return a.querySelector('.genre').textContent.localeCompare(b.querySelector('.genre').textContent);
            case 'capacidade':
                const capA = parseInt(a.querySelector('.duration').textContent);
                const capB = parseInt(b.querySelector('.duration').textContent);
                return capB - capA;
            case 'tipo':
                return a.dataset.tipo.localeCompare(b.dataset.tipo);
            default:
                return parseInt(a.dataset.salaId) - parseInt(b.dataset.salaId);
        }
    });
    
    rows.sort((a, b) => {
        switch(sortBy) {
            case 'nome':
                return a.querySelector('h4').textContent.localeCompare(b.querySelector('h4').textContent);
            case 'cinema':
                return a.querySelector('.genre-tag').textContent.localeCompare(b.querySelector('.genre-tag').textContent);
            case 'capacidade':
                const capA = parseInt(a.querySelector('.count-badge').textContent);
                const capB = parseInt(b.querySelector('.count-badge').textContent);
                return capB - capA;
            case 'tipo':
                return a.dataset.tipo.localeCompare(b.dataset.tipo);
            default:
                return parseInt(a.dataset.salaId) - parseInt(b.dataset.salaId);
        }
    });
    
    // Reordenar elementos
    cards.forEach(card => gridView.appendChild(card));
    rows.forEach(row => tableView.querySelector('tbody').appendChild(row));
}

// Limpar filtros
function limparFiltros() {
    document.getElementById('searchInput').value = '';
    document.getElementById('cinemaFilter').value = '';
    document.getElementById('tipoFilter').value = '';
    applyFilters();
}

// Animações
function animateTableRows() {
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
}

function animateGridCards() {
    const cards = document.querySelectorAll('.movie-card-pro');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px) scale(0.9)';
        setTimeout(() => {
            card.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0) scale(1)';
        }, index * 50);
    });
}

// Modal functions
function abrirModalAdicionarSala() {
    document.getElementById('modalAdicionarSala').style.display = 'flex';
}

function editarSala(salaId) {
    // Buscar dados da sala
    fetch(`/admin/salas/${salaId}/dados`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const sala = data.sala;
                document.getElementById('edit_nome').value = sala.nome_sala;
                document.getElementById('edit_id_cinema').value = sala.id_cinema;
                document.getElementById('edit_capacidade').value = sala.capacidade;
                document.getElementById('edit_tipo_sala').value = sala.tipo_sala;
                
                document.getElementById('formEditarSala').action = `/admin/salas/editar/${salaId}`;
                document.getElementById('modalEditarSala').style.display = 'flex';
            } else {
                alert('Erro ao carregar dados da sala');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao carregar dados da sala');
        });
}

function removerSala(salaId, nomeSala) {
    if (confirm(`Tem certeza que deseja remover a sala "${nomeSala}"?`)) {
        // Criar form para enviar DELETE request
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/salas/remover/${salaId}`;
        document.body.appendChild(form);
        form.submit();
    }
}

function fecharModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Fechar modal ao clicar fora
document.addEventListener('click', function(e) {
    const modals = document.querySelectorAll('.modal-overlay');
    modals.forEach(modal => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});