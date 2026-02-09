import mysql.connector
import json

# Conectar à base de dados
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Kevin@15',
    database='cinevibe'
)

cursor = conn.cursor(dictionary=True)

print("=" * 60)
print("TESTE: Simular seleção de menu e verificar toppings")
print("=" * 60)

# Simular produtos_bar_json que vem do formulário
# Testando com Menu Combo (ID 1)
produtos_bar_json = '[{"id": "1", "quantidade": 1}]'
produtos_bar = json.loads(produtos_bar_json)

print(f"\n📦 Produtos recebidos: {produtos_bar}")

produtos_com_toppings = []

for produto in produtos_bar:
    produto_id = produto.get('id')
    quantidade = produto.get('quantidade', 1)
    
    print(f"\n🔍 Verificando produto ID: {produto_id}")
    
    # Buscar produto no bar
    cursor.execute("""
        SELECT id, produto, preco, categoria, imagem_url
        FROM bar
        WHERE id = %s
    """, (produto_id,))
    produto_info = cursor.fetchone()
    
    if not produto_info:
        # Tentar buscar em menus
        print(f"🔍 Produto não encontrado no bar, buscando em menus...")
        cursor.execute("""
            SELECT id, nome as produto, preco_total as preco, 'menu' as categoria, imagem_url
            FROM menus
            WHERE id = %s
        """, (produto_id,))
        produto_info = cursor.fetchone()
        
        if produto_info:
            print(f"✅ Menu encontrado: {produto_info['produto']}")
    else:
        print(f"✅ Produto do bar encontrado: {produto_info['produto']}")
    
    if produto_info:
        # Verificar se este produto tem toppings associados
        tipo_produto = 'menu' if produto_info['categoria'] == 'menu' else 'bar'
        print(f"🔍 Tipo de produto: {tipo_produto}")
        
        if tipo_produto == 'menu':
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM toppings_produtos
                WHERE id_menu = %s AND tipo_produto = 'menu'
            """, (produto_id,))
        else:
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM toppings_produtos
                WHERE id_produto = %s AND tipo_produto = 'bar'
            """, (produto_id,))
        
        result = cursor.fetchone()
        print(f"🔍 Toppings associados: {result['total'] if result else 0}")
        
        if result and result['total'] > 0:
            produtos_com_toppings.append({
                'id': produto_id,
                'tipo': tipo_produto,
                'nome': produto_info['produto']
            })
            print(f"✅ Produto com toppings adicionado: {produto_info['produto']}")

print(f"\n📊 RESULTADO:")
print(f"   Produtos com toppings: {len(produtos_com_toppings)}")
if produtos_com_toppings:
    print(f"   ✅ Página de toppings DEVE aparecer")
    for p in produtos_com_toppings:
        print(f"      - {p['nome']} (ID: {p['id']}, Tipo: {p['tipo']})")
else:
    print(f"   ❌ Página de toppings NÃO vai aparecer")

cursor.close()
conn.close()

print("\n✅ Teste concluído!")
