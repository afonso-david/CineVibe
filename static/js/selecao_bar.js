console.log('=== SELECAO BAR JS ===');

let cart = {};
let products = { menus: [], snacks: [], bebidas: [] };

// Carregar produtos
try {
    const produtosData = document.getElementById('produtos-data');
    if (produtosData) {
        products = JSON.parse(produtosData.textContent);
        
        // NORMALIZAR: garantir que todos os produtos têm a propriedade 'produto'
        if (products.menus) {
            products.menus = products.menus.map(m => ({
                ...m,
                produto: m.produto || m.nome  // Usar 'nome' se 'produto' não existir
            }));
        }
        
        console.log('✅ Produtos carregados e normalizados:', products);
        console.log('   Menus:', products.menus?.length || 0);
        console.log('   Snacks:', products.snacks?.length || 0);
        console.log('   Bebidas:', products.bebidas?.length || 0);
        
        // DEBUG: Mostrar IDs dos menus
        if (products.menus && products.menus.length > 0) {
            console.log('📋 IDs dos Menus:');
            products.menus.forEach(m => {
                console.log(`   - ID ${m.id}: ${m.produto || m.nome}`);
            });
        }
    }
} catch(e) {
    console.error('❌ Erro ao carregar produtos:', e);
}

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const category = this.dataset.category;
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        document.querySelectorAll('.category-content').forEach(c => c.classList.remove('active'));
        document.getElementById(category).classList.add('active');
    });
});

// FUNÇÃO PRINCIPAL
function changeQuantity(productId, change, tipo = null) {
    console.log('═══════════════════════════════════════');
    console.log('🔧 changeQuantity CHAMADO');
    console.log('   productId:', productId, '(tipo:', typeof productId, ')');
    console.log('   change:', change);
    console.log('   tipo fornecido:', tipo);
    
    productId = String(productId);
    
    // Se tipo não foi fornecido, tentar detectar
    if (!tipo) {
        console.log('   🔍 Tipo não fornecido, tentando detectar...');
        // Verificar se é um menu
        const menuEncontrado = products.menus && products.menus.find(p => String(p.id) === productId);
        if (menuEncontrado) {
            tipo = 'menu';
            console.log('   ✅ Detectado como MENU:', menuEncontrado.produto || menuEncontrado.nome);
        } else {
            tipo = 'bar';
            console.log('   ✅ Detectado como BAR (produto individual)');
        }
    } else {
        console.log('   ✅ Tipo fornecido explicitamente:', tipo);
    }
    
    console.log('   📌 TIPO FINAL:', tipo);
    console.log('   📌 PRODUCT ID FINAL:', productId);
    
    // Criar chave única com tipo
    const cartKey = `${tipo}_${productId}`;
    console.log('   🔑 Chave do carrinho:', cartKey);
    
    if (!cart[cartKey]) cart[cartKey] = { id: productId, tipo: tipo, quantidade: 0 };
    cart[cartKey].quantidade += change;
    if (cart[cartKey].quantidade < 0) cart[cartKey].quantidade = 0;
    
    // Remover do cart se quantidade for 0
    if (cart[cartKey].quantidade === 0) {
        delete cart[cartKey];
        console.log('   🗑️ Removido do carrinho (quantidade = 0)');
    } else {
        console.log('   ✅ Quantidade atualizada:', cart[cartKey].quantidade);
    }
    
    console.log('   📦 Carrinho completo:', JSON.parse(JSON.stringify(cart)));
    
    // Atualizar DOM
    const qtyElement = document.getElementById(productId + '-qty');
    if (qtyElement) {
        qtyElement.textContent = cart[cartKey] ? cart[cartKey].quantidade : 0;
        console.log('   ✅ DOM atualizado');
    } else {
        console.error('   ❌ Elemento DOM não encontrado:', productId + '-qty');
    }
    
    console.log('═══════════════════════════════════════');
    
    updateCartSummary();
}

function updateCartSummary() {
    console.log('📊 ═══ UPDATE CART SUMMARY ═══');
    
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    const cartSummary = document.getElementById('cartSummary');
    const produtosBarInput = document.getElementById('produtosBarInput');
    const skipBtn = document.querySelector('.skip-btn');
    
    let total = 0;
    let itemsHtml = '';
    let hasItems = false;
    const produtosSelecionados = [];
    
    console.log('📦 Itens no carrinho:', Object.keys(cart).length);
    
    for (let cartKey in cart) {
        const item = cart[cartKey];
        console.log(`   🔍 Processando: ${cartKey}`, item);
        
        if (item.quantidade > 0) {
            hasItems = true;
            
            // Adicionar ao array com tipo identificado
            produtosSelecionados.push({
                id: item.id,
                quantidade: item.quantidade,
                tipo: item.tipo
            });
            
            console.log(`   ✅ Adicionado: ID=${item.id}, Tipo=${item.tipo}, Qtd=${item.quantidade}`);
            
            // Encontrar produto baseado no tipo
            let product = null;
            
            if (item.tipo === 'menu') {
                product = products.menus?.find(p => String(p.id) === String(item.id));
                if (product) {
                    console.log(`   ✅ Menu encontrado: ${product.produto || product.nome}`);
                } else {
                    console.error(`   ❌ Menu ID ${item.id} NÃO encontrado!`);
                }
            } else {
                // Tentar em snacks
                product = products.snacks?.find(p => String(p.id) === String(item.id));
                if (product) {
                    console.log(`   ✅ Snack encontrado: ${product.produto}`);
                } else {
                    // Tentar em bebidas
                    product = products.bebidas?.find(p => String(p.id) === String(item.id));
                    if (product) {
                        console.log(`   ✅ Bebida encontrada: ${product.produto}`);
                    } else {
                        console.error(`   ❌ Produto ID ${item.id} NÃO encontrado em nenhuma categoria!`);
                    }
                }
            }
            
            if (product) {
                const nomeProduto = product.produto || product.nome || 'Produto';
                const subtotal = product.preco * item.quantidade;
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
    console.log('📤 Produtos a enviar:', JSON.stringify(produtosSelecionados));
    
    if (cartItems) cartItems.innerHTML = itemsHtml;
    if (cartTotal) cartTotal.textContent = total.toFixed(2);
    if (cartSummary) cartSummary.style.display = hasItems ? 'block' : 'none';
    
    // Atualizar botão skip
    if (skipBtn) {
        skipBtn.innerHTML = hasItems ? 
            '<i class="fas fa-arrow-right"></i> Continuar' : 
            '<i class="fas fa-forward"></i> Não, obrigado. Continuar sem produtos do bar';
    }
    
    // Atualizar campo hidden
    if (produtosBarInput) {
        produtosBarInput.value = JSON.stringify(produtosSelecionados);
        console.log('✅ Campo hidden atualizado');
    }
    
    console.log('📊 ═══ FIM UPDATE CART SUMMARY ═══');
}

function goBack() {
    window.history.back();
}

function continuarComProdutos() {
    // Atualizar o carrinho antes de submeter
    updateCartSummary();
    
    // Submeter o formulário
    const form = document.getElementById('resumoForm');
    if (form) {
        form.submit();
    }
}

// Prevenir submissão do formulário se não houver produtos
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('resumoForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Atualizar produtos antes de submeter
            updateCartSummary();
            
            const produtosInput = document.getElementById('produtosBarInput');
            const produtosValue = produtosInput ? produtosInput.value : '[]';
            
            console.log('📤 Submetendo formulário com produtos:', produtosValue);
            
            // Se não houver produtos no carrinho, avisar
            if (Object.keys(cart).length === 0 || Object.values(cart).every(q => q === 0)) {
                console.log('⚠️ Nenhum produto no carrinho');
            }
        });
    }
});

// Tornar funções globais
window.changeQuantity = changeQuantity;
window.continuarComProdutos = continuarComProdutos;

console.log('✅ JavaScript carregado');
