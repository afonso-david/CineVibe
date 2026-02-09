import mysql.connector
import json

# Configuração da conexão
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Kevin@15',
    'database': 'cinevibe'
}

# Simular produtos selecionados
produtos_bar_json = json.dumps([
    {'id': 1, 'quantidade': 1},  # Pipocas Salgadas
])

print("🧪 TESTE DO FLUXO DE TOPPINGS")
print("=" * 50)

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    
    print("\n📦 Produtos selecionados:")
    produtos_bar = json.loads(produtos_bar_json)
    for p in produtos_bar:
        print(f"   - ID: {p['id']}, Quantidade: {p['quantidade']}")
    
    print("\n🔍 VERIFICANDO CADA PRODUTO:")
    
    produtos_com_toppings = []
    
    for produto in produtos_bar:
        produto_id = produto.get('id')
        quantidade = produto.get('quantidade', 1)
        
        print(f"\n--- Produto ID: {produto_id} ---")
        
        # Verificar se é topping
        if str(produto_id).startswith('topping_'):
            print("⏭️ É um topping, pulando...")
            continue
        
        # Buscar produto no bar
        cursor.execute("""
            SELECT id, produto, preco, categoria, imagem_url
            FROM bar
            WHERE id = %s
        """, (produto_id,))
        produto_info = cursor.fetchone()
        
        if not produto_info:
            print("❌ Não encontrado no bar, buscando em menus...")
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
            # Verificar tipo
            tipo_produto = 'menu' if produto_info['categoria'] == 'menu' else 'bar'
            print(f"📋 Tipo: {tipo_produto}")
            
            # Verificar toppings
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
            total_toppings = result['total'] if result else 0
            print(f"🍿 Toppings associados: {total_toppings}")
            
            if total_toppings > 0:
                produtos_com_toppings.append({
                    'id': produto_id,
                    'tipo': tipo_produto,
                    'nome': produto_info['produto']
                })
                print(f"✅ PRODUTO COM TOPPINGS!")
        else:
            print(f"❌ Produto não encontrado!")
    
    print("\n" + "=" * 50)
    print(f"\n📊 RESULTADO FINAL:")
    print(f"   Total de produtos verificados: {len(produtos_bar)}")
    print(f"   Produtos com toppings: {len(produtos_com_toppings)}")
    
    if produtos_com_toppings:
        print("\n✅ DEVE MOSTRAR PÁGINA DE TOPPINGS!")
        print("\n   Produtos com toppings:")
        for p in produtos_com_toppings:
            print(f"      - {p['nome']} (ID {p['id']}, tipo: {p['tipo']})")
    else:
        print("\n❌ NÃO DEVE MOSTRAR PÁGINA DE TOPPINGS")
        print("   Redirecionando direto para resumo...")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as e:
    print(f"❌ Erro MySQL: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
