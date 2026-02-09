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
    
    # 1. Criar tabela de relacionamento
    print("\n📋 Criando tabela toppings_produtos...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS toppings_produtos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            id_topping INT NOT NULL,
            id_produto INT NULL,
            id_menu INT NULL,
            tipo_produto ENUM('bar', 'menu') NOT NULL,
            FOREIGN KEY (id_topping) REFERENCES toppings(id) ON DELETE CASCADE,
            FOREIGN KEY (id_produto) REFERENCES bar(id) ON DELETE CASCADE,
            FOREIGN KEY (id_menu) REFERENCES menus(id) ON DELETE CASCADE,
            UNIQUE KEY unique_topping_produto (id_topping, id_produto, tipo_produto),
            UNIQUE KEY unique_topping_menu (id_topping, id_menu, tipo_produto)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    conn.commit()
    print("✅ Tabela toppings_produtos criada")
    
    # 2. Buscar todos os toppings
    cursor.execute("SELECT id, nome FROM toppings ORDER BY id")
    toppings = cursor.fetchall()
    print(f"\n🍿 Toppings encontrados: {len(toppings)}")
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
    print(f"\n🍿 Produtos com pipocas encontrados: {len(produtos_pipocas)}")
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
    print(f"\n🍿 Menus com pipocas encontrados: {len(menus_pipocas)}")
    for m in menus_pipocas:
        print(f"   - ID {m['id']}: {m['nome']}")
    
    # 5. Popular tabela - associar todos os toppings a todos os produtos/menus com pipocas
    print("\n📝 Populando tabela toppings_produtos...")
    
    total_inseridos = 0
    
    # Associar toppings aos produtos do bar
    for topping in toppings:
        for produto in produtos_pipocas:
            try:
                cursor.execute("""
                    INSERT INTO toppings_produtos (id_topping, id_produto, tipo_produto)
                    VALUES (%s, %s, 'bar')
                """, (topping['id'], produto['id']))
                total_inseridos += 1
                print(f"   ✓ Topping '{topping['nome']}' → Produto '{produto['produto']}'")
            except mysql.connector.IntegrityError:
                print(f"   ⚠ Já existe: Topping '{topping['nome']}' → Produto '{produto['produto']}'")
    
    # Associar toppings aos menus
    for topping in toppings:
        for menu in menus_pipocas:
            try:
                cursor.execute("""
                    INSERT INTO toppings_produtos (id_topping, id_menu, tipo_produto)
                    VALUES (%s, %s, 'menu')
                """, (topping['id'], menu['id']))
                total_inseridos += 1
                print(f"   ✓ Topping '{topping['nome']}' → Menu '{menu['nome']}'")
            except mysql.connector.IntegrityError:
                print(f"   ⚠ Já existe: Topping '{topping['nome']}' → Menu '{menu['nome']}'")
    
    conn.commit()
    print(f"\n✅ Total de associações inseridas: {total_inseridos}")
    
    # 6. Verificar resultado final
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
        LIMIT 10
    """)
    exemplos = cursor.fetchall()
    
    print("\n📋 Exemplos de associações:")
    for ex in exemplos:
        print(f"   - {ex['topping']} → {ex['produto_menu']} ({ex['tipo_produto']})")
    
    cursor.close()
    conn.close()
    print("\n✅ Script concluído com sucesso!")
    
except mysql.connector.Error as e:
    print(f"❌ Erro MySQL: {e}")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
