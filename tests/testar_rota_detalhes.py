import mysql.connector

def testar_rota_detalhes():
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
        
        # Testar a query da rota de detalhes
        reserva_id = 407  # ID de uma reserva que sabemos que existe
        
        cursor.execute("""
            SELECT r.*, 
                   u.nome as usuario_nome, u.email as usuario_email,
                   f.titulo as filme_titulo, f.poster_url, f.duracao,
                   c.nome as cinema_nome, c.localizacao as cinema_endereco,
                   ts.nome as tipo_sessao
            FROM reservas r
            LEFT JOIN usuarios u ON r.usuario_id = u.id
            LEFT JOIN filmes f ON r.filme_id = f.id
            LEFT JOIN cinemas c ON r.cinema_id = c.id
            LEFT JOIN tipos_sessao ts ON r.tipo_sessao_id = ts.id
            WHERE r.id = %s
        """, (reserva_id,))
        
        reserva = cursor.fetchone()
        
        print("=== TESTE DA ROTA DE DETALHES ===")
        if reserva:
            print(f"✅ Reserva encontrada: ID {reserva['id']}")
            print(f"  - Usuário: {reserva['usuario_nome']}")
            print(f"  - Email: {reserva['usuario_email']}")
            print(f"  - Filme: {reserva['filme_titulo']}")
            print(f"  - Cinema: {reserva['cinema_nome']}")
            print(f"  - Data: {reserva['data_sessao']}")
            print(f"  - Lugar: {reserva['lugar']}")
            print(f"  - Status: {reserva['status']}")
            print(f"  - Tipo: {reserva['tipo_sessao']}")
            print(f"  - Reservado em: {reserva['reservado_em']}")
            print(f"  - Sessão ID: {reserva['sessao_id']}")
            
            # Simular resposta JSON
            response = {
                'success': True,
                'reserva': dict(reserva)
            }
            print(f"\n✅ Resposta JSON seria: {response['success']}")
        else:
            print(f"❌ Reserva {reserva_id} não encontrada")
        
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
    testar_rota_detalhes()