import mysql.connector

def verificar_estrutura_reservas():
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
        
        # Verificar estrutura da tabela reservas
        cursor.execute("DESCRIBE reservas")
        colunas = cursor.fetchall()
        
        print("=== ESTRUTURA DA TABELA RESERVAS ===")
        for coluna in colunas:
            print(f"- {coluna['Field']}: {coluna['Type']} ({coluna['Null']}, {coluna['Key']})")
        print()
        
        # Verificar algumas reservas de exemplo
        cursor.execute("""
            SELECT r.*, u.nome as usuario_nome, f.titulo as filme_titulo, 
                   c.nome as cinema_nome
            FROM reservas r
            LEFT JOIN usuarios u ON r.usuario_id = u.id
            LEFT JOIN filmes f ON r.filme_id = f.id
            LEFT JOIN cinemas c ON r.cinema_id = c.id
            ORDER BY r.reservado_em DESC
            LIMIT 10
        """)
        
        reservas = cursor.fetchall()
        
        print("=== EXEMPLOS DE RESERVAS ===")
        for reserva in reservas:
            print(f"ID: {reserva['id']}")
            print(f"  - Usuário: {reserva['usuario_nome']}")
            print(f"  - Filme: {reserva['filme_titulo']}")
            print(f"  - Cinema: {reserva['cinema_nome']}")
            print(f"  - Data Sessão: {reserva['data_sessao']}")
            print(f"  - Status: {reserva.get('status', 'N/A')}")
            print(f"  - Lugar: {reserva.get('lugar', 'N/A')}")
            print(f"  - Reservado em: {reserva.get('reservado_em', 'N/A')}")
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
    verificar_estrutura_reservas()