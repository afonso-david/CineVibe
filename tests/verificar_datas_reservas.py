import mysql.connector
from datetime import datetime, date

def verificar_datas_reservas():
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
        
        # Data de hoje
        hoje = date.today()
        print(f"=== VERIFICAÇÃO DE DATAS DAS RESERVAS ===")
        print(f"Data de hoje: {hoje}")
        print()
        
        # Buscar todas as reservas com suas datas
        cursor.execute("""
            SELECT r.id, r.data_sessao, r.reservado_em, 
                   u.nome as usuario_nome, f.titulo as filme_titulo
            FROM reservas r
            LEFT JOIN usuarios u ON r.usuario_id = u.id
            LEFT JOIN filmes f ON r.filme_id = f.id
            ORDER BY r.data_sessao DESC
            LIMIT 20
        """)
        
        reservas = cursor.fetchall()
        
        print("=== RESERVAS ENCONTRADAS ===")
        reservas_hoje = 0
        reservas_futuras = 0
        reservas_passadas = 0
        
        for reserva in reservas:
            data_sessao = reserva['data_sessao']
            print(f"ID {reserva['id']}: {reserva['usuario_nome']} - {reserva['filme_titulo']}")
            print(f"  Data da sessão: {data_sessao}")
            print(f"  Reservado em: {reserva['reservado_em']}")
            
            if data_sessao:
                if data_sessao == hoje:
                    print("  ✅ HOJE")
                    reservas_hoje += 1
                elif data_sessao > hoje:
                    print("  📅 FUTURA")
                    reservas_futuras += 1
                else:
                    print("  📆 PASSADA")
                    reservas_passadas += 1
            print()
        
        print("=== RESUMO ===")
        print(f"Reservas para hoje: {reservas_hoje}")
        print(f"Reservas futuras: {reservas_futuras}")
        print(f"Reservas passadas: {reservas_passadas}")
        print(f"Total: {len(reservas)}")
        
        # Verificar especificamente reservas de hoje
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM reservas 
            WHERE data_sessao = %s
        """, (hoje,))
        
        count_hoje = cursor.fetchone()['count']
        print(f"\nReservas exatamente para hoje ({hoje}): {count_hoje}")
        
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
    verificar_datas_reservas()