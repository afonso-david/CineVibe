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
    
    # Buscar todos os menus
    print("\n📋 TODOS OS MENUS:")
    cursor.execute("""
        SELECT id, nome, preco_total, descricao
        FROM menus
        ORDER BY id
    """)
    menus = cursor.fetchall()
    
    for m in menus:
        print(f"\n📦 ID: {m['id']}")
        print(f"   Nome: {m['nome']}")
        print(f"   Preço: €{m['preco_total']}")
        print(f"   Descrição: {m['descricao']}")
    
    # Verificar associações de menus com toppings
    print("\n\n🔗 MENUS COM TOPPINGS ASSOCIADOS:")
    cursor.execute("""
        SELECT DISTINCT
            tp.id_menu,
            m.nome as nome_menu,
            COUNT(tp.id_topping) as total_toppings
        FROM toppings_produtos tp
        JOIN menus m ON tp.id_menu = m.id
        WHERE tp.tipo_produto = 'menu'
        GROUP BY tp.id_menu, m.nome
        ORDER BY tp.id_menu
    """)
    menus_com_toppings = cursor.fetchall()
    
    if menus_com_toppings:
        for m in menus_com_toppings:
            print(f"\n✅ Menu ID {m['id_menu']}: {m['nome_menu']}")
            print(f"   Total de toppings: {m['total_toppings']}")
            
            # Mostrar quais toppings
            cursor.execute("""
                SELECT t.id, t.nome, t.preco
                FROM toppings_produtos tp
                JOIN toppings t ON tp.id_topping = t.id
                WHERE tp.id_menu = %s AND tp.tipo_produto = 'menu'
                ORDER BY t.nome
            """, (m['id_menu'],))
            toppings = cursor.fetchall()
            
            print("   Toppings disponíveis:")
            for t in toppings:
                print(f"      - {t['nome']} (€{t['preco']})")
    else:
        print("❌ Nenhum menu com toppings associados!")
    
    # Verificar todos os registos na tabela toppings_produtos
    print("\n\n📊 TODOS OS REGISTOS EM TOPPINGS_PRODUTOS:")
    cursor.execute("""
        SELECT 
            tp.id,
            tp.id_topping,
            t.nome as topping_nome,
            tp.id_produto,
            b.produto as produto_nome,
            tp.id_menu,
            m.nome as menu_nome,
            tp.tipo_produto
        FROM toppings_produtos tp
        LEFT JOIN toppings t ON tp.id_topping = t.id
        LEFT JOIN bar b ON tp.id_produto = b.id
        LEFT JOIN menus m ON tp.id_menu = m.id
        ORDER BY tp.tipo_produto, tp.id_menu, tp.id_produto
    """)
    todos = cursor.fetchall()
    
    print(f"\nTotal de registos: {len(todos)}")
    print("\nPor tipo:")
    
    # Agrupar por tipo
    por_tipo = {}
    for r in todos:
        tipo = r['tipo_produto']
        if tipo not in por_tipo:
            por_tipo[tipo] = []
        por_tipo[tipo].append(r)
    
    for tipo, registos in por_tipo.items():
        print(f"\n{tipo.upper()}: {len(registos)} registos")
        for r in registos:
            if tipo == 'menu':
                print(f"   - Menu '{r['menu_nome']}' (ID {r['id_menu']}) → Topping '{r['topping_nome']}'")
            else:
                print(f"   - Produto '{r['produto_nome']}' (ID {r['id_produto']}) → Topping '{r['topping_nome']}'")
    
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
