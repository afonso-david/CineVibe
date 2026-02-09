import mysql.connector

# Configuração da conexão
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Kevin@15',
    'database': 'cinevibe'
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    
    print("🔗 Conectado à base de dados")
    
    # Buscar todas as pipocas
    print("\n🍿 PRODUTOS COM 'PIPOCAS' NO NOME:")
    cursor.execute("""
        SELECT id, produto, preco, categoria, icone, imagem_url
        FROM bar
        WHERE LOWER(produto) LIKE '%pipocas%'
        ORDER BY id
    """)
    pipocas = cursor.fetchall()
    
    for p in pipocas:
        print(f"\n📦 ID: {p['id']}")
        print(f"   Nome: {p['produto']}")
        print(f"   Preço: €{p['preco']}")
        print(f"   Categoria: {p['categoria']}")
        print(f"   Ícone: {p['icone']}")
        print(f"   Imagem: {p['imagem_url']}")
    
    # Verificar toppings associados
    print("\n\n🔗 ASSOCIAÇÕES NA TABELA TOPPINGS_PRODUTOS:")
    cursor.execute("""
        SELECT 
            tp.id,
            tp.id_produto,
            b.produto as nome_produto,
            tp.id_topping,
            t.nome as nome_topping,
            tp.tipo_produto
        FROM toppings_produtos tp
        LEFT JOIN bar b ON tp.id_produto = b.id
        LEFT JOIN toppings t ON tp.id_topping = t.id
        WHERE tp.tipo_produto = 'bar'
        ORDER BY tp.id_produto, tp.id_topping
    """)
    associacoes = cursor.fetchall()
    
    for a in associacoes:
        print(f"   - Produto ID {a['id_produto']} ({a['nome_produto']}) → Topping ID {a['id_topping']} ({a['nome_topping']})")
    
    # Verificar se há algum problema com o ID 1
    print("\n\n🔍 VERIFICAÇÃO ESPECÍFICA - PIPOCAS SALGADAS (ID 1):")
    cursor.execute("SELECT * FROM bar WHERE id = 1")
    pipoca_1 = cursor.fetchone()
    
    if pipoca_1:
        print("✅ Produto ID 1 existe:")
        print(f"   Nome: {pipoca_1['produto']}")
        print(f"   Preço: €{pipoca_1['preco']}")
        print(f"   Categoria: {pipoca_1['categoria']}")
    else:
        print("❌ Produto ID 1 NÃO EXISTE!")
    
    # Verificar toppings para ID 1
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM toppings_produtos
        WHERE id_produto = 1 AND tipo_produto = 'bar'
    """)
    result = cursor.fetchone()
    print(f"\n   Toppings associados: {result['total']}")
    
    cursor.close()
    conn.close()
    print("\n✅ Verificação concluída!")
    
except mysql.connector.Error as e:
    print(f"❌ Erro MySQL: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
