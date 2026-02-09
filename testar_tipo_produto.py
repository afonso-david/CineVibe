import mysql.connector
import json

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Kevin@15',
    database='cinevibe'
)

cursor = conn.cursor(dictionary=True)

print("=" * 60)
print("TESTE: Verificar identificação de tipo de produto")
print("=" * 60)

# Teste 1: Menu Combo (ID 1)
print("\n📦 TESTE 1: Menu Combo (ID 1)")
produtos_bar_json = '[{"id": "1", "quantidade": 1, "tipo": "menu"}]'
produtos_bar = json.loads(produtos_bar_json)

for produto in produtos_bar:
    produto_id = produto.get('id')
    tipo = produto.get('tipo', 'bar')
    
    print(f"   ID: {produto_id}, Tipo: {tipo}")
    
    if tipo == 'menu':
        cursor.execute("SELECT id, nome as produto FROM menus WHERE id = %s", (produto_id,))
        produto_info = cursor.fetchone()
        if produto_info:
            print(f"   ✅ Menu encontrado: {produto_info['produto']}")
            
            # Verificar toppings
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM toppings_produtos
                WHERE id_menu = %s AND tipo_produto = 'menu'
            """, (produto_id,))
            result = cursor.fetchone()
            print(f"   🍿 Toppings: {result['total']}")

# Teste 2: Pipocas Salgadas (ID 1 no bar)
print("\n📦 TESTE 2: Pipocas Salgadas (ID 1 no bar)")
produtos_bar_json = '[{"id": "1", "quantidade": 1, "tipo": "bar"}]'
produtos_bar = json.loads(produtos_bar_json)

for produto in produtos_bar:
    produto_id = produto.get('id')
    tipo = produto.get('tipo', 'bar')
    
    print(f"   ID: {produto_id}, Tipo: {tipo}")
    
    if tipo == 'bar':
        cursor.execute("SELECT id, produto FROM bar WHERE id = %s", (produto_id,))
        produto_info = cursor.fetchone()
        if produto_info:
            print(f"   ✅ Produto encontrado: {produto_info['produto']}")
            
            # Verificar toppings
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM toppings_produtos
                WHERE id_produto = %s AND tipo_produto = 'bar'
            """, (produto_id,))
            result = cursor.fetchone()
            print(f"   🍿 Toppings: {result['total']}")

# Teste 3: Menu Kids (ID 3)
print("\n📦 TESTE 3: Menu Kids (ID 3)")
produtos_bar_json = '[{"id": "3", "quantidade": 1, "tipo": "menu"}]'
produtos_bar = json.loads(produtos_bar_json)

for produto in produtos_bar:
    produto_id = produto.get('id')
    tipo = produto.get('tipo', 'bar')
    
    print(f"   ID: {produto_id}, Tipo: {tipo}")
    
    if tipo == 'menu':
        cursor.execute("SELECT id, nome as produto FROM menus WHERE id = %s", (produto_id,))
        produto_info = cursor.fetchone()
        if produto_info:
            print(f"   ✅ Menu encontrado: {produto_info['produto']}")
            
            # Verificar toppings
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM toppings_produtos
                WHERE id_menu = %s AND tipo_produto = 'menu'
            """, (produto_id,))
            result = cursor.fetchone()
            print(f"   🍿 Toppings: {result['total']}")

cursor.close()
conn.close()

print("\n✅ Teste concluído!")
