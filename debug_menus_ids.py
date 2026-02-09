import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Kevin@15',
    database='cinevibe'
)

cursor = conn.cursor(dictionary=True)

print("=" * 60)
print("DEBUG: IDs dos Menus na Base de Dados")
print("=" * 60)

# Buscar todos os menus
cursor.execute("""
    SELECT id, nome, descricao, preco_total
    FROM menus
    ORDER BY id
""")
menus = cursor.fetchall()

print(f"\n📋 Total de menus: {len(menus)}\n")

for menu in menus:
    print(f"ID: {menu['id']}")
    print(f"   Nome: {menu['nome']}")
    print(f"   Descrição: {menu['descricao']}")
    print(f"   Preço: €{menu['preco_total']:.2f}")
    
    # Verificar se tem toppings
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM toppings_produtos
        WHERE id_menu = %s AND tipo_produto = 'menu'
    """, (menu['id'],))
    result = cursor.fetchone()
    
    if result['total'] > 0:
        print(f"   ✅ TEM TOPPINGS ({result['total']})")
    else:
        print(f"   ❌ SEM TOPPINGS")
    print()

cursor.close()
conn.close()

print("✅ Debug concluído!")
