console.log('=== SELECAO BAR JS ===');
let cart = {};
let products = { menus: [], snacks: [], bebidas: [], toppings: [] };
let menuConfigAtual = null; 
let menusConfigurados = {}; 
try {
    const produtosData = document.getElementById('produtos-data');
    if (produtosData) {
        products = JSON.parse(produtosData.textContent);
        if (products.menus) {
            products.menus = products.menus.map(m => ({
                ...m,
                produto: m.produto || m.nome
            }));
        }
        console.log('✅ Produtos carregados:', products);
        console.log('   Toppings disponíveis:', products.toppings?.length || 0);
    }
} catch(e) {
    console.error('❌ Erro ao carregar produtos:', e);
}
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const category = this.dataset.category;
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        document.querySelectorAll('.category-content').forEach(c => c.classList.remove('active'));
        document.getElementById(category).classList.add('active');
    });
});
function changeQuantity(productId, change, tipo = null) {
    console.log('changeQuantity:', productId, change, tipo);
    productId = String(productId);
    if (!tipo) {
        const menuEncontrado = products.menus && products.menus.find(p => String(p.id) === productId);
        tipo = menuEncontrado ? 'menu' : 'bar';
    }
    if (tipo === 'menu' && change > 0) {
        abrirModalMenu(productId);
        return;
    }
    if (tipo === 'menu' && change < 0) {
        const cartKey = `${tipo}_${productId}`;
        if (cart[cartKey] && cart[cartKey].quantidade > 0) {
            cart[cartKey].quantidade--;
            const configs = Object.keys(menusConfigurados).filter(k => k.startsWith(`${productId}_`));
            if (configs.length > 0) {
                const ultimaConfig = configs[configs.length - 1];
                delete menusConfigurados[ultimaConfig];
            }
            if (cart[cartKey].quantidade === 0) {
                delete cart[cartKey];
            }
        }
        const qtyElement = document.getElementById(productId + '-qty');
        if (qtyElement) {
            qtyElement.textContent = cart[cartKey] ? cart[cartKey].quantidade : 0;
        }
        updateCartSummary();
        return;
    }
    const cartKey = `${tipo}_${productId}`;
    if (!cart[cartKey]) cart[cartKey] = { id: productId, tipo: tipo, quantidade: 0 };
    cart[cartKey].quantidade += change;
    if (cart[cartKey].quantidade < 0) cart[cartKey].quantidade = 0;
    if (cart[cartKey].quantidade === 0) {
        delete cart[cartKey];
    }
    const qtyElement = document.getElementById(productId + '-qty');
    if (qtyElement) {
        qtyElement.textContent = cart[cartKey] ? cart[cartKey].quantidade : 0;
    }
    updateCartSummary();
}
async function abrirModalMenu(menuId) {
    console.log('🔓 Abrindo modal para menu:', menuId);
    menuConfigAtual = {
        menuId: menuId,
        snackId: null,
        bebidaId: null,
        toppings: [] 
    };
    try {
        const response = await fetch(`/api/menu_produtos/${menuId}`);
        const data = await response.json();
        if (!data.success) {
            alert('Erro ao carregar produtos do menu');
            return;
        }
        console.log('📦 Produtos do menu:', data);
        const snacksContainer = document.getElementById('modalSnacks');
        snacksContainer.innerHTML = '';
        data.snacks.forEach(snack => {
            const card = criarCardProdutoModal(snack, 'snack');
            snacksContainer.appendChild(card);
        });
        const bebidasContainer = document.getElementById('modalBebidas');
        bebidasContainer.innerHTML = '';
        data.bebidas.forEach(bebida => {
            const card = criarCardProdutoModal(bebida, 'bebida');
            bebidasContainer.appendChild(card);
        });
        const sectionToppings = document.getElementById('sectionToppings');
        if (data.has_toppings && data.toppings.length > 0) {
            const toppingsContainer = document.getElementById('modalToppings');
            toppingsContainer.innerHTML = '';
            data.toppings.forEach(topping => {
                const card = criarCardToppingModal(topping);
                toppingsContainer.appendChild(card);
            });
            sectionToppings.style.display = 'block';
            console.log('✅ Toppings do menu carregados:', data.toppings.length);
        } else {
            sectionToppings.style.display = 'none';
            console.log('⚠️ Menu sem toppings');
        }
        const modal = document.getElementById('modalMenuProdutos');
        modal.style.display = 'flex';
        document.body.classList.add('modal-open');
    } catch (error) {
        console.error('❌ Erro ao abrir modal:', error);
        alert('Erro ao carregar produtos do menu');
    }
}
function criarCardToppingModal(topping) {
    const card = document.createElement('div');
    card.className = 'menu-produto-card topping-card';
    card.dataset.toppingId = topping.id;
    if (topping.imagem_url) {
        const img = document.createElement('img');
        let imagemUrl = topping.imagem_url.replace(/\\/g, '/').replace(/"/g, '').trim();
        if (!imagemUrl.startsWith('http') && !imagemUrl.startsWith('/static/')) {
            if (imagemUrl.startsWith('imgs/')) {
                imagemUrl = `/static/${imagemUrl}`;
            } else if (!imagemUrl.startsWith('/')) {
                imagemUrl = `/static/imgs/toppings/${imagemUrl}`;
            } else {
                imagemUrl = `/static${imagemUrl}`;
            }
        }
        img.src = imagemUrl;
        img.alt = topping.nome;
        img.style.width = '80px';
        img.style.height = '80px';
        img.style.objectFit = 'contain';
        img.onerror = function() {
            console.warn('Imagem não carregou:', imagemUrl);
            this.style.display = 'none';
            const icon = document.createElement('div');
            icon.className = 'menu-produto-icon';
            icon.innerHTML = '<i class="fas fa-candy-cane"></i>';
            this.parentNode.insertBefore(icon, this);
        };
        card.appendChild(img);
    } else {
        const icon = document.createElement('div');
        icon.className = 'menu-produto-icon';
        icon.innerHTML = '<i class="fas fa-candy-cane"></i>';
        card.appendChild(icon);
    }
    const nome = document.createElement('h5');
    nome.textContent = topping.nome;
    card.appendChild(nome);
    const preco = document.createElement('p');
    preco.style.color = '#FFD700';
    preco.style.fontSize = '0.85rem';
    preco.style.marginTop = '0.25rem';
    preco.textContent = `+€${parseFloat(topping.preco).toFixed(2)}`;
    card.appendChild(preco);
    card.addEventListener('click', function() {
        toggleToppingModal(topping.id);
    });
    return card;
}
function criarCardProdutoModal(produto, tipo) {
    const card = document.createElement('div');
    card.className = 'menu-produto-card';
    card.dataset.produtoId = produto.id;
    card.dataset.tipo = tipo;
    if (produto.imagem_url) {
        const img = document.createElement('img');
        img.src = `/static/${produto.imagem_url}`;
        img.alt = produto.produto;
        img.onerror = function() {
            this.style.display = 'none';
            const icon = document.createElement('div');
            icon.className = 'menu-produto-icon';
            icon.innerHTML = `<i class="${produto.icone || 'fas fa-box'}"></i>`;
            this.parentNode.insertBefore(icon, this);
        };
        card.appendChild(img);
    } else {
        const icon = document.createElement('div');
        icon.className = 'menu-produto-icon';
        icon.innerHTML = `<i class="${produto.icone || 'fas fa-box'}"></i>`;
        card.appendChild(icon);
    }
    const nome = document.createElement('h5');
    nome.textContent = produto.produto;
    card.appendChild(nome);
    card.addEventListener('click', function() {
        selecionarProdutoModal(produto.id, tipo);
    });
    return card;
}
function selecionarProdutoModal(produtoId, tipo) {
    console.log('Selecionado:', produtoId, tipo);
    const container = tipo === 'snack' ? 'modalSnacks' : 'modalBebidas';
    document.querySelectorAll(`#${container} .menu-produto-card`).forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
    if (tipo === 'snack') {
        menuConfigAtual.snackId = produtoId;
    } else {
        menuConfigAtual.bebidaId = produtoId;
    }
    const btnConfirmar = document.getElementById('btnConfirmarMenu');
    btnConfirmar.disabled = !(menuConfigAtual.snackId && menuConfigAtual.bebidaId);
}
function toggleToppingModal(toppingId) {
    const card = document.querySelector(`[data-topping-id="${toppingId}"]`);
    if (menuConfigAtual.toppings.includes(toppingId)) {
        menuConfigAtual.toppings = menuConfigAtual.toppings.filter(id => id !== toppingId);
        card.classList.remove('selected');
    } else {
        menuConfigAtual.toppings.push(toppingId);
        card.classList.add('selected');
    }
    console.log('Toppings selecionados:', menuConfigAtual.toppings);
}
function confirmarMenuConfig() {
    if (!menuConfigAtual.snackId || !menuConfigAtual.bebidaId) {
        alert('Por favor, selecione um snack e uma bebida');
        return;
    }
    console.log('✅ Configuração confirmada:', menuConfigAtual);
    const cartKey = `menu_${menuConfigAtual.menuId}`;
    if (!cart[cartKey]) {
        cart[cartKey] = { id: menuConfigAtual.menuId, tipo: 'menu', quantidade: 0, configs: [] };
    }
    cart[cartKey].quantidade++;
    cart[cartKey].configs.push({
        snackId: menuConfigAtual.snackId,
        bebidaId: menuConfigAtual.bebidaId,
        toppings: [...menuConfigAtual.toppings] 
    });
    const qtyElement = document.getElementById(menuConfigAtual.menuId + '-qty');
    if (qtyElement) {
        qtyElement.textContent = cart[cartKey].quantidade;
    }
    updateCartSummary();
    fecharModalMenu();
}
function fecharModalMenu() {
    document.getElementById('modalMenuProdutos').style.display = 'none';
    document.body.classList.remove('modal-open'); 
    menuConfigAtual = null;
    document.querySelectorAll('.menu-produto-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.getElementById('btnConfirmarMenu').disabled = true;
}
function updateCartSummary() {
    console.log('📊 Atualizando resumo do carrinho');
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    const cartSummary = document.getElementById('cartSummary');
    const produtosBarInput = document.getElementById('produtosBarInput');
    const skipBtn = document.querySelector('.skip-btn');
    let total = 0;
    let itemsHtml = '';
    let hasItems = false;
    const produtosSelecionados = [];
    for (let cartKey in cart) {
        const item = cart[cartKey];
        if (item.quantidade > 0) {
            hasItems = true;
            const produtoData = {
                id: item.id,
                quantidade: item.quantidade,
                tipo: item.tipo
            };
            if (item.tipo === 'menu' && item.configs) {
                produtoData.configs = item.configs;
            }
            produtosSelecionados.push(produtoData);
            let product = null;
            if (item.tipo === 'menu') {
                product = products.menus?.find(p => String(p.id) === String(item.id));
            } else {
                product = products.snacks?.find(p => String(p.id) === String(item.id)) ||
                         products.bebidas?.find(p => String(p.id) === String(item.id));
            }
            if (product) {
                const nomeProduto = product.produto || product.nome || 'Produto';
                const preco = product.preco || product.preco_total || 0;
                const subtotal = preco * item.quantidade;
                total += subtotal;
                itemsHtml += `
                    <div class="cart-item">
                        <span>${nomeProduto} x${item.quantidade}</span>
                        <span>€${subtotal.toFixed(2)}</span>
                    </div>
                `;
            }
        }
    }
    console.log('💰 Total:', total.toFixed(2));
    console.log('📤 Produtos:', produtosSelecionados);
    if (cartItems) cartItems.innerHTML = itemsHtml;
    if (cartTotal) cartTotal.textContent = total.toFixed(2);
    if (cartSummary) cartSummary.style.display = hasItems ? 'block' : 'none';
    if (skipBtn) {
        skipBtn.innerHTML = hasItems ? 
            '<i class="fas fa-arrow-right"></i> Continuar' : 
            '<i class="fas fa-forward"></i> Não, obrigado. Continuar sem produtos do bar';
    }
    if (produtosBarInput) {
        produtosBarInput.value = JSON.stringify(produtosSelecionados);
    }
}
function goBack() {
    window.history.back();
}
function continuarComProdutos() {
    document.getElementById('resumoForm').submit();
}
window.changeQuantity = changeQuantity;
window.continuarComProdutos = continuarComProdutos;
window.goBack = goBack;
window.abrirModalMenu = abrirModalMenu;
window.fecharModalMenu = fecharModalMenu;
window.confirmarMenuConfig = confirmarMenuConfig;
window.selecionarProdutoModal = selecionarProdutoModal;
window.toggleToppingModal = toggleToppingModal;
console.log('✅ JavaScript carregado');
