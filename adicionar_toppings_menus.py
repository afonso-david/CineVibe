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
    
    # Limpar registo inválido
    print("\n🗑️ Limpando registos inválidos...")
    cursor.execute("""
        DELETE FROM toppings_produtos
        WHERE id_menu IS NULL AND id_produto IS NULL
    """)
    conn.commit()
    print("✅ Registos inválidos removidos")
    
    # Buscar todos os toppings
    cursor.execute("SELECT id, nome FROM toppings ORDER BY id")
    toppings = cursor.fetchall()
    print(f"\n🍿 {len(toppings)} toppings disponíveis")
    
    # Menus que têm pipocas (baseado na descrição)
    menus_com_pipocas = [
        {'id': 1, 'nome': 'Menu Combo'},
        {'id': 3, 'nome': 'Menu Kids'},
        {'id': 5, 'nome': 'Menu Combo Duplo'}
    ]
    
    print(f"\n📋 Adicionando toppings a {len(menus_com_pipocas)} menus...")
    
    total_inseridos = 0
    
    for menu in menus_com_pipocas:
        print(f"\n📦 Menu: {menu['nome']} (ID {menu['id']})")
        
        for topping in toppings:
            try:
                # Verificar se já existe
                cursor.execute("""
                    SELECT COUNT(*) as existe
                    FROM toppings_produtos
                    WHERE id_menu = %s AND id_topping = %s AND tipo_produto = 'menu'
                """, (menu['id'], topping['id']))
                
                result = cursor.fetchone()
                
                if result['existe'] == 0:
                    cursor.execute("""
                        INSERT INTO toppings_produtos (id_topping, id_menu, tipo_produto)
                        VALUES (%s, %s, 'menu')
                    """, (topping['id'], menu['id']))
                    total_inseridos += 1
                    print(f"   ✓ Topping '{topping['nome']}' adicionado")
                else:
                    print(f"   ⚠ Topping '{topping['nome']}' já existe")
            except mysql.connector.Error as e:
                print(f"   ❌ Erro ao adicionar '{topping['nome']}': {e}")
    
    conn.commit()
    print(f"\n✅ {total_inseridos} novas associações inseridas!")
    
    # Verificar resultado final
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM toppings_produtos
        WHERE tipo_produto = 'menu'
    """)
    total_menus = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM toppings_produtos
        WHERE tipo_produto = 'bar'
    """)
    total_bar = cursor.fetchone()['total']
    
    print(f"\n📊 Resumo final:")
    print(f"   - Associações de menus: {total_menus}")
    print(f"   - Associações de produtos bar: {total_bar}")
    print(f"   - Total: {total_menus + total_bar}")
    
    # Mostrar menus com toppings
    print("\n📋 Menus com toppings:")
    cursor.execute("""
        SELECT DISTINCT
            m.id,
            m.nome,
            COUNT(tp.id_topping) as total_toppings
        FROM menus m
        JOIN toppings_produtos tp ON m.id = tp.id_menu
        WHERE tp.tipo_produto = 'menu'
        GROUP BY m.id, m.nome
        ORDER BY m.id
    """)
    menus_resultado = cursor.fetchall()
    
    for m in menus_resultado:
        print(f"   ✅ {m['nome']} (ID {m['id']}) - {m['total_toppings']} toppings")
    
    cursor.close()
    conn.close()
    print("\n✅ Script concluído com sucesso!")
    
except mysql.connector.Error as e:
    print(f"❌ Erro MySQL: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
