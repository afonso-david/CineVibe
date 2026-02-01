import mysql.connector

def testar_nova_logica():
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
        
        # Simular a nova query
        cursor.execute("""
            SELECT u.id, u.nome, u.email, u.criado_em, u.ultimo_login, u.is_admin,
                   u.avatar_personalizado, a.caminho as avatar_galeria,
                   COUNT(DISTINCT r.id) as num_reservas
            FROM usuarios u
            LEFT JOIN reservas r ON u.id = r.usuario_id
            LEFT JOIN avatars a ON u.avatar_id = a.id
            GROUP BY u.id, u.nome, u.email, u.criado_em, u.ultimo_login, u.is_admin, u.avatar_personalizado, a.caminho
            ORDER BY u.id DESC
            LIMIT 10
        """)
        
        usuarios = cursor.fetchall()
        
        print("=== TESTE DA NOVA LÓGICA DE AVATARES ===")
        print(f"Total de usuários: {len(usuarios)}")
        print()
        
        # Aplicar a nova lógica
        for usuario in usuarios:
            print(f"Usuário: {usuario['nome']}")
            print(f"  - Avatar personalizado: {usuario['avatar_personalizado']}")
            print(f"  - Avatar galeria: {usuario['avatar_galeria']}")
            
            # Nova lógica
            if usuario['avatar_personalizado']:
                # Se o avatar personalizado já contém o caminho completo, usar diretamente
                if usuario['avatar_personalizado'].startswith('imgs/'):
                    usuario['avatar_url'] = usuario['avatar_personalizado']
                else:
                    usuario['avatar_url'] = f"imgs/profile/{usuario['avatar_personalizado']}"
                print(f"  - Avatar final: {usuario['avatar_url']} (personalizado)")
            elif usuario['avatar_galeria']:
                # Usar avatar da galeria
                usuario['avatar_url'] = usuario['avatar_galeria']
                print(f"  - Avatar final: {usuario['avatar_url']} (galeria)")
            else:
                # Usar avatar padrão
                usuario['avatar_url'] = "imgs/avatars/default.svg"
                print(f"  - Avatar final: {usuario['avatar_url']} (padrão)")
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
    testar_nova_logica()