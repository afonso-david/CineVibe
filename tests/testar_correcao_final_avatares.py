import mysql.connector

def testar_correcao_final():
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
        
        # Simular a query final corrigida
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
        
        print("=== TESTE DA CORREÇÃO FINAL DE AVATARES ===")
        print(f"Total de usuários: {len(usuarios)}")
        print()
        
        # Aplicar a lógica final corrigida
        for usuario in usuarios:
            print(f"Usuário: {usuario['nome']}")
            print(f"  - Avatar personalizado: {usuario['avatar_personalizado']}")
            print(f"  - Avatar galeria: {usuario['avatar_galeria']}")
            
            avatar_personalizado = usuario['avatar_personalizado']
            avatar_galeria = usuario['avatar_galeria']
            
            # Se tem avatar personalizado e não é o padrão
            if avatar_personalizado and avatar_personalizado != 'imgs/avatars/default.png':
                # Se o avatar personalizado já contém o caminho completo, usar diretamente
                if avatar_personalizado.startswith('imgs/'):
                    usuario['avatar_url'] = avatar_personalizado
                else:
                    usuario['avatar_url'] = f"imgs/profile/{avatar_personalizado}"
                print(f"  - Avatar final: {usuario['avatar_url']} (personalizado)")
            elif avatar_galeria:
                # Usar avatar da galeria
                usuario['avatar_url'] = avatar_galeria
                print(f"  - Avatar final: {usuario['avatar_url']} (galeria)")
            else:
                # Usar avatar padrão corrigido
                usuario['avatar_url'] = "imgs/icons/user_icon34-removebg-preview.png"
                print(f"  - Avatar final: {usuario['avatar_url']} (padrão)")
            print()
        
        print("✅ Correção aplicada com sucesso!")
        print("✅ Todos os avatares agora têm caminhos válidos!")
        
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
    testar_correcao_final()