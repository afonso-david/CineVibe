import mysql.connector

def verificar_avatares():
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
        
        # Verificar avatares dos usuários
        cursor.execute("""
            SELECT u.id, u.nome, u.avatar_personalizado, u.avatar_id, a.caminho as avatar_galeria
            FROM usuarios u
            LEFT JOIN avatars a ON u.avatar_id = a.id
            LIMIT 10
        """)
        
        usuarios = cursor.fetchall()
        
        print("=== VERIFICAÇÃO DE AVATARES DOS USUÁRIOS ===")
        print(f"Total de usuários verificados: {len(usuarios)}")
        print()
        
        for usuario in usuarios:
            print(f"Usuário: {usuario['nome']}")
            print(f"  - ID: {usuario['id']}")
            print(f"  - Avatar personalizado: {usuario['avatar_personalizado']}")
            print(f"  - Avatar ID: {usuario['avatar_id']}")
            print(f"  - Avatar da galeria: {usuario['avatar_galeria']}")
            
            # Determinar qual avatar usar
            if usuario['avatar_personalizado']:
                avatar_final = f"imgs/profile/{usuario['avatar_personalizado']}"
                print(f"  - Avatar final: {avatar_final} (personalizado)")
            elif usuario['avatar_galeria']:
                avatar_final = usuario['avatar_galeria']
                print(f"  - Avatar final: {avatar_final} (galeria)")
            else:
                avatar_final = "imgs/avatars/default.svg"
                print(f"  - Avatar final: {avatar_final} (padrão)")
            print()
        
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
    verificar_avatares()