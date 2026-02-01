import mysql.connector

def verificar_reservas_hoje():
    conn = None
    cursor = None
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='cinevibe',
            user='root',
            password='Kevin@15'
        )
        cursor = conn.cursor(dictionary=True)
        
        # Verificar reservas de hoje
        cursor.execute("""
            SELECT r.id, r.data_sessao, u.nome as usuario_nome, f.titulo as filme_titulo
            FROM reservas r
            LEFT JOIN usuarios u ON r.usuario_id = u.id
            LEFT JOIN filmes f ON r.filme_id = f.id
            WHERE r.data_sessao = '2026-01-08'
            ORDER BY r.id
        """)
        
        reservas_hoje = cursor.fetchall()
        
        print("=== RESERVAS DE HOJE (2026-01-08) ===")
        if reservas_hoje:
            for reserva in reservas_hoje:
                print(f"ID {reserva['id']}: {reserva['usuario_nome']} - {reserva['filme_titulo']} - {reserva['data_sessao']}")
        else:
            print("Nenhuma reserva encontrada para hoje.")
        
        print(f"\nTotal: {len(reservas_hoje)} reservas")
        
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
    verificar_reservas_hoje()