import mysql.connector

def testar_admin_reservas():
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
        
        # Simular a query da função admin_reservas
        query = """
            SELECT r.id, r.reservado_em, r.data_sessao, r.lugar, r.status,
                   r.nome_cliente, r.email_cliente, r.telefone_cliente,
                   u.nome as usuario_nome, u.email as usuario_email,
                   f.titulo as filme_titulo, f.poster_url,
                   c.nome as cinema_nome,
                   ts.nome as tipo_sessao
            FROM reservas r
            LEFT JOIN usuarios u ON r.usuario_id = u.id
            LEFT JOIN filmes f ON r.filme_id = f.id
            LEFT JOIN cinemas c ON r.cinema_id = c.id
            LEFT JOIN tipos_sessao ts ON r.tipo_sessao_id = ts.id
            ORDER BY r.reservado_em DESC
            LIMIT 10
        """
        
        cursor.execute(query)
        reservas = cursor.fetchall()
        
        print("=== TESTE DA FUNÇÃO ADMIN_RESERVAS ===")
        print(f"Total de reservas encontradas: {len(reservas)}")
        print()
        
        for reserva in reservas:
            print(f"ID: {reserva['id']}")
            print(f"  - Usuário: {reserva['usuario_nome'] or reserva['nome_cliente'] or 'N/A'}")
            print(f"  - Email: {reserva['usuario_email'] or reserva['email_cliente'] or 'N/A'}")
            print(f"  - Filme: {reserva['filme_titulo']}")
            print(f"  - Cinema: {reserva['cinema_nome']}")
            print(f"  - Data Sessão: {reserva['data_sessao']}")
            print(f"  - Lugar: {reserva['lugar']}")
            print(f"  - Status: {reserva['status']}")
            print(f"  - Tipo Sessão: {reserva['tipo_sessao']}")
            print(f"  - Reservado em: {reserva['reservado_em']}")
            print()
        
        # Testar estatísticas
        cursor.execute("SELECT COUNT(*) as total FROM reservas")
        total_reservas = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as confirmadas FROM reservas WHERE status = 'confirmada'")
        reservas_confirmadas = cursor.fetchone()['confirmadas']
        
        cursor.execute("SELECT COUNT(*) as pendentes FROM reservas WHERE status = 'pendente'")
        reservas_pendentes = cursor.fetchone()['pendentes']
        
        print("=== ESTATÍSTICAS ===")
        print(f"Total de reservas: {total_reservas}")
        print(f"Reservas confirmadas: {reservas_confirmadas}")
        print(f"Reservas pendentes: {reservas_pendentes}")
        
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
    testar_admin_reservas()