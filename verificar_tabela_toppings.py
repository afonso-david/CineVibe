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
    
    # Verificar se a tabela existe
    cursor.execute("""
        SELECT COUNT(*) as existe
        FROM information_schema.tables 
        WHERE table_schema = 'cinevibe' 
        AND table_name = 'toppings_produtos'
    """)
    result = cursor.fetchone()
    
    if result['existe'] > 0:
        print("✅ Tabela toppings_produtos EXISTE")
        
        # Contar registos
        cursor.execute("SELECT COUNT(*) as total FROM toppings_produtos")
        total = cursor.fetchone()
        print(f"📊 Total de registos: {total['total']}")
        
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
    else:
        print("❌ Tabela toppings_produtos NÃO EXISTE")
        print("\n🔧 Vou criar a tabela agora...")
        
        # Criar tabela
        cursor.execute("""
            CREATE TABLE toppings_produtos (
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
        print("✅ Tabela criada!")
        
        # Buscar toppings
        cursor.execute("SELECT id, nome FROM toppings ORDER BY id")
        toppings = cursor.fetchall()
        print(f"\n🍿 Toppings disponíveis: {len(toppings)}")
        
        # Buscar produtos com pipocas
        cursor.execute("""
            SELECT id, produto, categoria 
            FROM bar 
            WHERE LOWER(produto) LIKE '%pipocas%'
            ORDER BY id
        """)
        produtos_pipocas = cursor.fetchall()
        print(f"🍿 Produtos com pipocas: {len(produtos_pipocas)}")
        
        # Buscar menus com pipocas
        cursor.execute("""
            SELECT id, nome 
            FROM menus 
            WHERE LOWER(nome) LIKE '%pipocas%'
            ORDER BY id
        """)
        menus_pipocas = cursor.fetchall()
        print(f"🍿 Menus com pipocas: {len(menus_pipocas)}")
        
        # Popular tabela
        print("\n📝 Populando tabela...")
        total_inseridos = 0
        
        for topping in toppings:
            for produto in produtos_pipocas:
                cursor.execute("""
                    INSERT INTO toppings_produtos (id_topping, id_produto, tipo_produto)
                    VALUES (%s, %s, 'bar')
                """, (topping['id'], produto['id']))
                total_inseridos += 1
                print(f"   ✓ {topping['nome']} → {produto['produto']}")
        
        for topping in toppings:
            for menu in menus_pipocas:
                cursor.execute("""
                    INSERT INTO toppings_produtos (id_topping, id_menu, tipo_produto)
                    VALUES (%s, %s, 'menu')
                """, (topping['id'], menu['id']))
                total_inseridos += 1
                print(f"   ✓ {topping['nome']} → {menu['nome']}")
        
        conn.commit()
        print(f"\n✅ {total_inseridos} associações inseridas!")
    
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
