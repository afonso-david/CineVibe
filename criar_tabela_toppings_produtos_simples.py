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
    
    # 1. Criar tabela de relacionamento SEM foreign keys para bar e menus
    print("\n📋 Criando tabela toppings_produtos...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS toppings_produtos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            id_topping INT NOT NULL,
            id_produto INT NULL,
            id_menu INT NULL,
            tipo_produto ENUM('bar', 'menu') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_topping (id_topping),
            INDEX idx_produto (id_produto),
            INDEX idx_menu (id_menu)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    conn.commit()
    print("✅ Tabela toppings_produtos criada")
    
    # 2. Buscar todos os toppings
    cursor.execute("SELECT id, nome FROM toppings ORDER BY id")
    toppings = cursor.fetchall()
    print(f"\n🍿 Toppings disponíveis: {len(toppings)}")
    for t in toppings:
        print(f"   - ID {t['id']}: {t['nome']}")
    
    # 3. Buscar produtos do bar que contêm "pipocas"
    cursor.execute("""
        SELECT id, produto, categoria 
        FROM bar 
        WHERE LOWER(produto) LIKE '%pipocas%'
        ORDER BY id
    """)
    produtos_pipocas = cursor.fetchall()
    print(f"\n🍿 Produtos com pipocas: {len(produtos_pipocas)}")
    for p in produtos_pipocas:
        print(f"   - ID {p['id']}: {p['produto']} ({p['categoria']})")
    
    # 4. Buscar menus que contêm "pipocas"
    cursor.execute("""
        SELECT id, nome 
        FROM menus 
        WHERE LOWER(nome) LIKE '%pipocas%'
        ORDER BY id
    """)
    menus_pipocas = cursor.fetchall()
    print(f"\n🍿 Menus com pipocas: {len(menus_pipocas)}")
    for m in menus_pipocas:
        print(f"   - ID {m['id']}: {m['nome']}")
    
    # 5. Limpar tabela antes de popular
    cursor.execute("DELETE FROM toppings_produtos")
    conn.commit()
    print("\n🗑️ Tabela toppings_produtos limpa")
    
    # 6. Popular tabela - associar todos os toppings a todos os produtos/menus com pipocas
    print("\n📝 Populando tabela toppings_produtos...")
    
    total_inseridos = 0
    
    # Associar toppings aos produtos do bar
    for topping in toppings:
        for produto in produtos_pipocas:
            cursor.execute("""
                INSERT INTO toppings_produtos (id_topping, id_produto, tipo_produto)
                VALUES (%s, %s, 'bar')
            """, (topping['id'], produto['id']))
            total_inseridos += 1
            print(f"   ✓ Topping '{topping['nome']}' → Produto '{produto['produto']}'")
    
    # Associar toppings aos menus
    for topping in toppings:
        for menu in menus_pipocas:
            cursor.execute("""
                INSERT INTO toppings_produtos (id_topping, id_menu, tipo_produto)
                VALUES (%s, %s, 'menu')
            """, (topping['id'], menu['id']))
            total_inseridos += 1
            print(f"   ✓ Topping '{topping['nome']}' → Menu '{menu['nome']}'")
    
    conn.commit()
    print(f"\n✅ Total de associações inseridas: {total_inseridos}")
    
    # 7. Verificar resultado final
    cursor.execute("SELECT COUNT(*) as total FROM toppings_produtos")
    total = cursor.fetchone()['total']
    print(f"\n📊 Total de registos na tabela toppings_produtos: {total}")
    
    # Mostrar alguns exemplos
    cursor.execute("""
        SELECT 
            tp.id,
            t.nome as topping,
            COALESCE(b.produto, m.nome) as produto_menu,
            tp.tipo_produto
        FROM toppings_produtos tp
        LEFT JOIN toppings t ON tp.id_topping = t.id
        LEFT JOIN bar b ON tp.id_produto = b.id
        LEFT JOIN menus m ON tp.id_menu = m.id
        ORDER BY tp.id
        LIMIT 20
    """)
    exemplos = cursor.fetchall()
    
    print("\n📋 Exemplos de associações:")
    for ex in exemplos:
        print(f"   - {ex['topping']} → {ex['produto_menu']} ({ex['tipo_produto']})")
    
    cursor.close()
    conn.close()
    print("\n✅ Script concluído com sucesso!")
    print("\n💡 Agora os toppings só aparecem para produtos/menus que contêm pipocas!")
    
except mysql.connector.Error as e:
    print(f"❌ Erro MySQL: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
