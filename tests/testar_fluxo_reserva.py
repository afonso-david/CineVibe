#!/usr/bin/env python3
"""
Script para testar o fluxo completo de reserva
"""

import mysql.connector
from datetime import date

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kevin@15",
        database="cinevibe"
    )

def testar_fluxo_reserva():
    """Testa o fluxo completo de reserva"""
    print("🎫 TESTANDO FLUXO DE RESERVA...")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar uma sessão disponível
        cursor.execute("""
            SELECT hs.id as horario_id, hs.id_cinema as cinema_id, hs.id_tipo_sessao as tipo_id,
                   hs.id_filme as filme_id, f.titulo, c.nome as cinema_nome, 
                   ts.nome as tipo_nome, ts.preco_bilhete, s.nome_sala, s.capacidade
            FROM horarios_sessao hs
            JOIN filmes f ON hs.id_filme = f.id
            JOIN cinemas c ON hs.id_cinema = c.id
            JOIN tipos_sessao ts ON hs.id_tipo_sessao = ts.id
            JOIN salas s ON hs.id_sala = s.id
            WHERE ts.preco_bilhete > 0
            ORDER BY hs.id
            LIMIT 1
        """)
        sessao = cursor.fetchone()
        
        if not sessao:
            print("❌ Nenhuma sessão encontrada")
            return
        
        print(f"✅ Sessão encontrada:")
        print(f"   ID: {sessao['horario_id']}")
        print(f"   Filme: {sessao['titulo']}")
        print(f"   Cinema: {sessao['cinema_nome']}")
        print(f"   Tipo: {sessao['tipo_nome']} (€{sessao['preco_bilhete']})")
        print(f"   Sala: {sessao['nome_sala']} ({sessao['capacidade']} lugares)")
        
        # Gerar URL de teste
        hoje = date.today().strftime('%Y-%m-%d')
        url_reserva = f"/reserva?horario={sessao['horario_id']}&cinema={sessao['cinema_id']}&tipo={sessao['tipo_id']}&data={hoje}"
        url_selecao = f"/selecao_lugares?horario_id={sessao['horario_id']}&cinema_id={sessao['cinema_id']}&tipo_sessao_id={sessao['tipo_id']}&filme_id={sessao['filme_id']}&data_sessao={hoje}&quantidade=2"
        
        print(f"\n🔗 URLs de teste:")
        print(f"   Reserva: http://localhost:5000{url_reserva}")
        print(f"   Seleção: http://localhost:5000{url_selecao}")
        
        # Simular layout da sala
        capacidade = sessao['capacidade']
        if capacidade <= 150:
            fileiras = 10
            lugares_por_fileira = 15
            layout = "Pequena"
        elif capacidade <= 300:
            fileiras = 15
            lugares_por_fileira = 20
            layout = "Média"
        else:
            fileiras = 20
            lugares_por_fileira = 18
            layout = "Grande (IMAX)"
        
        print(f"\n🏢 Layout da sala:")
        print(f"   Tipo: {layout}")
        print(f"   Fileiras: {fileiras}")
        print(f"   Lugares por fileira: {lugares_por_fileira}")
        print(f"   Total calculado: {fileiras * lugares_por_fileira}")
        print(f"   Capacidade BD: {capacidade}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🧪 TESTANDO FLUXO DE RESERVA")
    print("=" * 50)
    
    testar_fluxo_reserva()
    
    print("\n✅ TESTE CONCLUÍDO!")
    print("=" * 50)