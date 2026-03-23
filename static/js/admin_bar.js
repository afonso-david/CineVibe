let currentView = 'table';
let currentSort = 'id';
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    setupSearch();
    setupFilters();
    updateViewDisplay();
    const activeTab = localStorage.getItem('adminBarActiveTab') || 'produtos';
    mostrarTab(activeTab);
});
function mostrarTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const selectedTab = document.getElementById(`tab-${tabName}`);
    if (selectedTab) {
        selectedTab.style.display = 'block';
        selectedTab.classList.add('active');
    }
    if (typeof event !== 'undefined' && event && event.target) {
        event.target.classList.add('active');
    } else {
        const btn = document.querySelector(`.tab-btn[onclick*="${tabName}"]`);
        if (btn) btn.classList.add('active');
    }
    const btnAdicionar = document.getElementById('btnAdicionar');
    const btnTexto = document.getElementById('btnAdicionarTexto');
    if (tabName === 'produtos') {
        btnAdicionar.onclick = abrirModalAdicionarProduto;
        btnTexto.textContent = 'Novo Produto';
    } else if (tabName === 'menus') {
        btnAdicionar.onclick = abrirModalAdicionarMenu;
        btnTexto.textContent = 'Novo Menu';
    } else if (tabName === 'toppings') {
        btnAdicionar.onclick = abrirModalAdicionarTopping;
        btnTexto.textContent = 'Novo Topping';
    }
    localStorage.setItem('adminBarActiveTab', tabName);
}
function initializeEventListeners() {
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.dataset.view;
            switchView(view);
        });
    });
    document.querySelectorAll('.price-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.price-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            applyFilters();
        });
    });
    const typeFilter = document.getElementById('typeFilter');
    if (typeFilter) {
        typeFilter.addEventListener('change', applyFilters);
    }
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            currentSort = this.value;
            sortProducts();
        });
    }
}
function switchView(view) {
    currentView = view;
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.view === view) {
            btn.classList.add('active');
        }
    });
    updateViewDisplay();
}
function updateViewDisplay() {
    const produtosGrid = document.getElementById('produtos-grid');
    const produtosTable = document.getElementById('produtos-table');
    const menusGrid = document.getElementById('menus-grid');
    const menusTable = document.getElementById('menus-table');
    const toppingsGrid = document.getElementById('toppings-grid');
    const toppingsTable = document.getElementById('toppings-table');
    if (currentView === 'grid') {
        if (produtosGrid) produtosGrid.style.display = 'grid';
        if (menusGrid) menusGrid.style.display = 'grid';
        if (toppingsGrid) toppingsGrid.style.display = 'grid';
        if (produtosTable) produtosTable.style.display = 'none';
        if (menusTable) menusTable.style.display = 'none';
        if (toppingsTable) toppingsTable.style.display = 'none';
    } else {
        if (produtosGrid) produtosGrid.style.display = 'none';
        if (menusGrid) menusGrid.style.display = 'none';
        if (toppingsGrid) toppingsGrid.style.display = 'none';
        if (produtosTable) produtosTable.style.display = 'block';
        if (menusTable) menusTable.style.display = 'block';
        if (toppingsTable) toppingsTable.style.display = 'block';
    }
}
function sortProducts() {
    const containers = [
        { grid: document.querySelector('#produtos-grid'), table: document.querySelector('#produtos-table tbody'), attr: 'data-produto-id' },
        { grid: document.querySelector('#menus-grid'), table: document.querySelector('#menus-table tbody'), attr: 'data-menu-id' },
        { grid: document.querySelector('#toppings-grid'), table: document.querySelector('#toppings-table tbody'), attr: 'data-topping-id' }
    ];
    containers.forEach(container => {
        [container.grid, container.table].forEach(element => {
            if (!element) return;
            const items = Array.from(element.children);
            items.sort((a, b) => {
                let aValue, bValue;
                switch (currentSort) {
                    case 'nome':
                        const aTitle = a.querySelector('.movie-title-info h4, .movie-info h3, .topping-info h3, .menu-header h3');
                        const bTitle = b.querySelector('.movie-title-info h4, .movie-info h3, .topping-info h3, .menu-header h3');
                        aValue = aTitle ? aTitle.textContent.toLowerCase() : '';
                        bValue = bTitle ? bTitle.textContent.toLowerCase() : '';
                        return aValue.localeCompare(bValue);
                    case 'preco':
                        aValue = parseFloat(a.dataset.preco) || 0;
                        bValue = parseFloat(b.dataset.preco) || 0;
                        return aValue - bValue;
                    case 'tipo':
                        aValue = a.dataset.tipo || '';
                        bValue = b.dataset.tipo || '';
                        return aValue.localeCompare(bValue);
                    default: 
                        aValue = parseInt(a.getAttribute(container.attr)) || 0;
                        bValue = parseInt(b.getAttribute(container.attr)) || 0;
                        return bValue - aValue; 
                }
            });
            items.forEach(item => element.appendChild(item));
        });
    });
}
function abrirModalAdicionarProduto() {
    document.getElementById('modalAdicionarProduto').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}
function fecharModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    const aindaAberto = document.querySelector('.modal-overlay[style*="flex"]');
    if (!aindaAberto) {
        document.body.style.overflow = 'auto';
    }
}
async function editarProduto(produtoId) {
    try {
        const response = await fetch(`/admin/bar/produtos/${produtoId}/dados`);
        const produto = await response.json();
        if (produto.error) {
            alert('Erro ao carregar dados do produto');
            return;
        }
        document.getElementById('edit_nome_produto').value = produto.nome || produto.produto || '';
        document.getElementById('edit_tipo_produto').value = produto.tipo || '';
        document.getElementById('edit_preco_produto').value = produto.preco || '';
        const imagemAtualInput = document.getElementById('imagem_atual_produto');
        const previewEdit = document.getElementById('preview_edit_imagem_produto');
        const nomeEditImagem = document.getElementById('nome_edit_imagem_produto');
        if (produto.imagem_url) {
            imagemAtualInput.value = produto.imagem_url;
            const imagemPath = produto.imagem_url.replace(/\\/g, '/').replace(/"/g, '');
            previewEdit.innerHTML = `<img src="/static/${imagemPath}" alt="Imagem atual">`;
            previewEdit.classList.add('active');
            nomeEditImagem.textContent = 'Imagem atual';
        } else {
            imagemAtualInput.value = '';
            previewEdit.innerHTML = '';
            previewEdit.classList.remove('active');
            nomeEditImagem.textContent = 'Nenhuma imagem selecionada';
        }
        document.getElementById('formEditarProduto').action = `/admin/bar/produtos/editar/${produtoId}`;
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
    alert(`Ver detalhes do produto ${produtoId} - Funcionalidade em desenvolvimento`);
}
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            applyFilters();
        });
    }
}
function setupFilters() {
}
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
        if (searchTerm && !nome.includes(searchTerm) && !tipo.toLowerCase().includes(searchTerm)) {
            visible = false;
        }
        if (typeFilter && tipo !== typeFilter) {
            visible = false;
        }
        if (priceRange !== 'all') {
            if (priceRange === '0-5' && (preco < 0 || preco > 5)) visible = false;
            if (priceRange === '5-10' && (preco < 5 || preco > 10)) visible = false;
            if (priceRange === '10+' && preco < 10) visible = false;
        }
        produto.style.display = visible ? '' : 'none';
    });
}
function limparFiltros() {
    document.getElementById('searchInput').value = '';
    document.getElementById('typeFilter').value = '';
    document.querySelectorAll('.price-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.price-btn[data-price="all"]').classList.add('active');
    applyFilters();
}
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        const modalId = event.target.id;
        fecharModal(modalId);
    }
});
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal-overlay[style*="flex"]');
        if (openModal) {
            fecharModal(openModal.id);
        }
    }
});
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
    const priceInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    priceInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });
});
function abrirModalAdicionarMenu() {
    document.getElementById('formAdicionarMenu').reset();
    document.getElementById('produtos-novo-menu-list').innerHTML = '<p class="no-produtos">Nenhum produto adicionado</p>';
    document.getElementById('modalAdicionarMenu').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}
function abrirSeletorProdutosNovoMenu() {
    window.menuContext = 'novo';
    abrirSeletorProdutos();
}
async function editarMenu(menuId) {
    console.log('=== INICIANDO EDIÇÃO DO MENU ===');
    console.log('Menu ID:', menuId);
    window.menuContext = 'editar';
    try {
        const url = `/admin/bar/menus/${menuId}/dados`;
        console.log('URL da requisição:', url);
        const response = await fetch(url);
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Erro na resposta:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const menu = await response.json();
        console.log('Menu recebido:', menu);
        if (menu.error) {
            console.error('Erro no menu:', menu.error);
            alert('Erro ao carregar dados do menu: ' + menu.error);
            return;
        }
        const nomeInput = document.getElementById('edit_nome_menu');
        const descricaoInput = document.getElementById('edit_descricao_menu');
        const precoInput = document.getElementById('edit_preco_menu');
        console.log('Elementos encontrados:', {
            nome: !!nomeInput,
            descricao: !!descricaoInput,
            preco: !!precoInput
        });
        if (!nomeInput || !descricaoInput || !precoInput) {
            throw new Error('Elementos do formulário não encontrados');
        }
        nomeInput.value = menu.nome || '';
        descricaoInput.value = menu.descricao || '';
        precoInput.value = menu.preco_total || '';
        const imagemAtualInput = document.getElementById('imagem_atual_menu');
        const previewEdit = document.getElementById('preview_edit_imagem_menu');
        const nomeEditImagem = document.getElementById('nome_edit_imagem_menu');
        if (menu.imagem_url) {
            imagemAtualInput.value = menu.imagem_url;
            previewEdit.innerHTML = `<img src="/static/${menu.imagem_url}" alt="Imagem atual">`;
            previewEdit.classList.add('active');
            nomeEditImagem.textContent = 'Imagem atual carregada';
        } else {
            imagemAtualInput.value = '';
            previewEdit.innerHTML = '';
            previewEdit.classList.remove('active');
            nomeEditImagem.textContent = 'Nenhuma imagem selecionada';
        }
        console.log('Formulário preenchido com:', {
            nome: nomeInput.value,
            descricao: descricaoInput.value,
            preco: precoInput.value,
            imagem: menu.imagem_url
        });
        const produtosList = document.getElementById('produtos-menu-list');
        if (!produtosList) {
            console.error('Lista de produtos não encontrada');
        } else {
            produtosList.innerHTML = '';
            console.log('Produtos do menu:', menu.produtos);
            if (menu.produtos && menu.produtos.length > 0) {
                menu.produtos.forEach(produto => {
                    console.log('Adicionando produto:', produto);
                    const produtoItem = document.createElement('div');
                    produtoItem.className = 'produto-item';
                    produtoItem.dataset.produtoId = produto.id;
                    produtoItem.innerHTML = `
                        <span class="produto-nome">${produto.nome}</span>
                        <span class="produto-preco">€${produto.preco.toFixed(2)}</span>
                        <button type="button" class="btn-remove-produto" onclick="removerProdutoDoMenu(${produto.id})">
                            <i class="fas fa-times"></i>
                        </button>
                        <input type="hidden" name="produtos[]" value="${produto.id}">
                    `;
                    produtosList.appendChild(produtoItem);
                });
            } else {
                produtosList.innerHTML = '<p class="no-produtos">Nenhum produto adicionado</p>';
            }
        }
        const form = document.getElementById('formEditarMenu');
        if (form) {
            form.action = `/admin/bar/menus/editar/${menuId}`;
            console.log('Form action definida:', form.action);
        } else {
            console.error('Formulário não encontrado');
        }
        const modal = document.getElementById('modalEditarMenu');
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
            console.log('Modal aberto');
        } else {
            console.error('Modal não encontrado');
        }
        console.log('=== EDIÇÃO CONCLUÍDA COM SUCESSO ===');
    } catch (error) {
        console.error('=== ERRO AO CARREGAR MENU ===');
        console.error('Erro:', error);
        console.error('Stack:', error.stack);
        alert('Erro ao carregar dados do menu: ' + error.message);
    }
}
function removerMenu(menuId) {
    if (confirm('Tem certeza que deseja remover este menu?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/bar/menus/remover/${menuId}`;
        document.body.appendChild(form);
        form.submit();
    }
}
function abrirSeletorProdutos() {
    const listId = window.menuContext === 'novo' ? 'produtos-novo-menu-list' : 'produtos-menu-list';
    document.getElementById('modalSeletorProdutos').style.display = 'flex';
    document.body.style.overflow = 'hidden';
    const produtosAdicionados = document.querySelectorAll(`#${listId} .produto-item`);
    const idsAdicionados = Array.from(produtosAdicionados).map(item => {
        const nome = item.querySelector('.produto-nome').textContent;
        return nome;
    });
    document.querySelectorAll('.produto-seletor-item').forEach(item => {
        const nome = item.dataset.produtoNome;
        if (idsAdicionados.includes(nome)) {
            item.classList.add('adicionado');
            const btn = item.querySelector('.btn-add-produto-menu');
            btn.innerHTML = '<i class="fas fa-check"></i> Adicionado';
            btn.disabled = true;
        } else {
            item.classList.remove('adicionado');
            const btn = item.querySelector('.btn-add-produto-menu');
            btn.innerHTML = '<i class="fas fa-plus"></i> Adicionar';
            btn.disabled = false;
        }
    });
    const searchInput = document.getElementById('searchProdutosSeletor');
    searchInput.value = '';
    searchInput.oninput = function() {
        const termo = this.value.toLowerCase();
        document.querySelectorAll('.produto-seletor-item').forEach(item => {
            const nome = item.dataset.produtoNome.toLowerCase();
            const tipo = item.querySelector('.produto-seletor-tipo').textContent.toLowerCase();
            if (nome.includes(termo) || tipo.includes(termo)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    };
}
function adicionarProdutoAoMenu(produtoId, produtoNome, produtoPreco) {
    console.log('Adicionando produto:', produtoId, produtoNome, produtoPreco);
    const listId = window.menuContext === 'novo' ? 'produtos-novo-menu-list' : 'produtos-menu-list';
    const produtosList = document.getElementById(listId);
    const existente = Array.from(produtosList.querySelectorAll('.produto-item')).find(item => {
        return item.querySelector('.produto-nome').textContent === produtoNome;
    });
    if (existente) {
        alert('Este produto já está no menu!');
        return;
    }
    const noProdutos = produtosList.querySelector('.no-produtos');
    if (noProdutos) {
        noProdutos.remove();
    }
    const produtoItem = document.createElement('div');
    produtoItem.className = 'produto-item';
    produtoItem.dataset.produtoId = produtoId;
    produtoItem.innerHTML = `
        <span class="produto-nome">${produtoNome}</span>
        <span class="produto-preco">€${parseFloat(produtoPreco).toFixed(2)}</span>
        <button type="button" class="btn-remove-produto" onclick="removerProdutoDoMenuContext(${produtoId}, '${window.menuContext || 'editar'}')">
            <i class="fas fa-times"></i>
        </button>
        <input type="hidden" name="produtos[]" value="${produtoId}">
    `;
    produtosList.appendChild(produtoItem);
    const seletorItem = document.querySelector(`.produto-seletor-item[data-produto-id="${produtoId}"]`);
    if (seletorItem) {
        seletorItem.classList.add('adicionado');
        const btn = seletorItem.querySelector('.btn-add-produto-menu');
        btn.innerHTML = '<i class="fas fa-check"></i> Adicionado';
        btn.disabled = true;
    }
    console.log('Produto adicionado com sucesso');
}
function removerProdutoDoMenuContext(produtoId, context) {
    console.log('Removendo produto:', produtoId, 'contexto:', context);
    const listId = context === 'novo' ? 'produtos-novo-menu-list' : 'produtos-menu-list';
    const produtoItem = document.querySelector(`#${listId} .produto-item[data-produto-id="${produtoId}"]`);
    if (produtoItem) {
        produtoItem.remove();
    }
    const produtosList = document.getElementById(listId);
    if (produtosList.children.length === 0) {
        produtosList.innerHTML = '<p class="no-produtos">Nenhum produto adicionado</p>';
    }
    const seletorItem = document.querySelector(`.produto-seletor-item[data-produto-id="${produtoId}"]`);
    if (seletorItem) {
        seletorItem.classList.remove('adicionado');
        const btn = seletorItem.querySelector('.btn-add-produto-menu');
        btn.innerHTML = '<i class="fas fa-plus"></i> Adicionar';
        btn.disabled = false;
    }
    console.log('Produto removido com sucesso');
}
function removerProdutoDoMenu(produtoId) {
    removerProdutoDoMenuContext(produtoId, 'editar');
}
document.addEventListener('DOMContentLoaded', function() {
    const imagemMenuInput = document.getElementById('imagem_menu');
    if (imagemMenuInput) {
        imagemMenuInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('nome_imagem_menu').textContent = file.name;
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('preview_imagem_menu');
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                    preview.classList.add('active');
                };
                reader.readAsDataURL(file);
            }
        });
    }
    const editImagemMenuInput = document.getElementById('edit_imagem_menu');
    if (editImagemMenuInput) {
        editImagemMenuInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('nome_edit_imagem_menu').textContent = file.name;
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('preview_edit_imagem_menu');
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                    preview.classList.add('active');
                };
                reader.readAsDataURL(file);
            }
        });
    }
    const imagemProdutoInput = document.getElementById('imagem_produto');
    if (imagemProdutoInput) {
        imagemProdutoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('nome_imagem_produto').textContent = file.name;
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('preview_imagem_produto');
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                    preview.classList.add('active');
                };
                reader.readAsDataURL(file);
            }
        });
    }
    const editImagemProdutoInput = document.getElementById('edit_imagem_produto');
    if (editImagemProdutoInput) {
        editImagemProdutoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('nome_edit_imagem_produto').textContent = file.name;
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('preview_edit_imagem_produto');
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                    preview.classList.add('active');
                };
                reader.readAsDataURL(file);
            }
        });
    }
});
function abrirModalAdicionarTopping() {
    document.getElementById('modalAdicionarTopping').style.display = 'flex';
    document.body.style.overflow = 'hidden';
    document.getElementById('formAdicionarTopping').reset();
    document.getElementById('nome_imagem_topping').textContent = 'Nenhuma imagem selecionada';
    document.getElementById('preview_imagem_topping').innerHTML = '';
    document.getElementById('preview_imagem_topping').classList.remove('active');
}
document.addEventListener('DOMContentLoaded', function() {
    const imagemToppingInput = document.getElementById('imagem_topping');
    if (imagemToppingInput) {
        imagemToppingInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('nome_imagem_topping').textContent = file.name;
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('preview_imagem_topping');
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                    preview.classList.add('active');
                };
                reader.readAsDataURL(file);
            }
        });
    }
});
function editarTopping(toppingId) {
    console.log('Editando topping:', toppingId);
    fetch(`/admin/bar/toppings/${toppingId}/dados`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Erro ao carregar dados do topping: ' + data.error);
                return;
            }
            console.log('Dados do topping:', data);
            document.getElementById('edit_nome_topping').value = data.nome || '';
            document.getElementById('edit_descricao_topping').value = data.descricao || '';
            document.getElementById('edit_preco_topping').value = data.preco || '';
            document.getElementById('imagem_atual_topping').value = data.imagem_url || '';
            const preview = document.getElementById('preview_edit_imagem_topping');
            if (data.imagem_url) {
                const imagemPath = data.imagem_url.replace(/\\/g, '/').replace(/"/g, '');
                preview.innerHTML = `<img src="/static/${imagemPath}" alt="Preview">`;
                preview.classList.add('active');
                document.getElementById('nome_edit_imagem_topping').textContent = 'Imagem atual';
            } else {
                preview.innerHTML = '';
                preview.classList.remove('active');
                document.getElementById('nome_edit_imagem_topping').textContent = 'Nenhuma imagem selecionada';
            }
            const form = document.getElementById('formEditarTopping');
            form.action = `/admin/bar/toppings/editar/${toppingId}`;
            document.getElementById('modalEditarTopping').style.display = 'flex';
            document.body.style.overflow = 'hidden';
        })
        .catch(error => {
            console.error('Erro ao buscar dados do topping:', error);
            alert('Erro ao carregar dados do topping');
        });
}
function removerTopping(toppingId) {
    if (confirm('Tem certeza que deseja remover este topping?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/bar/toppings/remover/${toppingId}`;
        document.body.appendChild(form);
        form.submit();
    }
}
document.addEventListener('DOMContentLoaded', function() {
    const editImagemToppingInput = document.getElementById('edit_imagem_topping');
    if (editImagemToppingInput) {
        editImagemToppingInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('nome_edit_imagem_topping').textContent = file.name;
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('preview_edit_imagem_topping');
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                    preview.classList.add('active');
                };
                reader.readAsDataURL(file);
            }
        });
    }
});
