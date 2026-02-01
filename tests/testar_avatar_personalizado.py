import mysql.connector

def testar_avatar_personalizado():
    conn = None
    cursor = None
    
    try:
        # Conectar à base de dados
        conn = mysql.connector.connect(
            host='localhost',
            database='cinevibe',
            user='root',
            password='Kevin@15'
        )
        cursor = conn.cursor(dictionary=True)
        
        # Testar a query que estava a dar erro
        query = """
            SELECT u.id, u.nome, u.email, u.criado_em, u.ultimo_login, u.is_admin,
                   u.avatar_personalizado,
                   COUNT(DISTINCT r.id) as num_reservas
            FROM usuarios u
            LEFT JOIN reservas r ON u.id = r.usuario_id
            GROUP BY u.id, u.nome, u.email, u.criado_em, u.ultimo_login, u.is_admin, u.avatar_personalizado
            ORDER BY u.criado_em DESC
            LIMIT 5
        """
        
        cursor.execute(query)
        usuarios = cursor.fetchall()
        
        print("✅ Query executada com sucesso!")
        print(f"✅ Encontrados {len(usuarios)} usuários")
        
        for usuario in usuarios:
            avatar_status = "Tem avatar personalizado" if usuario['avatar_personalizado'] else "Sem avatar personalizado"
            print(f"- {usuario['nome']}: {avatar_status}")
        
    except mysql.connector.Error as e:
        print(f"❌ Erro MySQL: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    testar_avatar_personalizado()