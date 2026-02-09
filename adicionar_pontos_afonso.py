import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Kevin@15',
    database='cinevibe'
)

cursor = conn.cursor(dictionary=True)

print("Adicionando 2500 pontos ao usuário 'afonso'...")
print("=" * 80)

# Buscar o usuário afonso
cursor.execute("SELECT id, nome, email FROM usuarios WHERE nome = 'afonso'")
usuario = cursor.fetchone()

if usuario:
    print(f"Usuário encontrado: {usuario['nome']} (ID: {usuario['id']})")
    print(f"Email: {usuario['email']}")
    print(f"Pontos a adicionar: 2500")
    print("-" * 80)
    
    # Adicionar movimento de pontos
    cursor.execute("""
        INSERT INTO pontos_movimentos 
        (utilizador_id, pontos, motivo, data_movimento)
        VALUES (%s, %s, %s, NOW())
    """, (usuario['id'], 2500, 'Bónus especial adicionado manualmente'))
    
    conn.commit()
    
    print(f"\n✅ 2500 pontos adicionados com sucesso!")
    print(f"   Motivo: Bónus especial adicionado manualmente")
    
    # Verificar total de pontos
    cursor.execute("""
        SELECT COALESCE(SUM(pontos), 0) as total_pontos
        FROM pontos_movimentos
        WHERE utilizador_id = %s
    """, (usuario['id'],))
    
    resultado = cursor.fetchone()
    total_pontos = resultado['total_pontos'] if resultado else 0
    
    print(f"   Total de pontos do usuário: {total_pontos}")
else:
    print("❌ Usuário 'afonso' não encontrado na base de dados")

print("=" * 80)

conn.close()
