#!/usr/bin/env python3
"""
Script para testar a funcionalidade de seleção de lugares
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

def testar_estrutura_salas():
    """Testa se as salas têm capacidades definidas"""
    print("🏢 TESTANDO ESTRUTURA DAS SALAS...")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, nome_sala, capacidade, tipo_sala FROM salas ORDER BY id")
        salas = cursor.fetchall()
        
        print(f"📊 Total de salas encontradas: {len(salas)}")
        
        for sala in salas:
            print(f"   Sala {sala['id']}: {sala['nome_sala']} - {sala['capacidade']} lugares ({sala['tipo_sala']})")
            
            # Calcular layout baseado na capacidade
            capacidade = sala['capacidade']
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
            
            print(f"      → Layout: {layout} ({fileiras} fileiras x {lugares_por_fileira} lugares)")
        
    except Exception as e:
        print(f"❌ Erro ao testar salas: {e}")
    finally:
        cursor.close()
        conn.close()

def testar_horarios_sessao():
    """Testa se há horários de sessão disponíveis"""
    print("\n🎬 TESTANDO HORÁRIOS DE SESSÃO...")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT hs.id, f.titulo, c.nome as cinema, s.nome_sala, s.capacidade, h.hora
            FROM horarios_sessao hs
            JOIN filmes f ON hs.id_filme = f.id
            JOIN cinemas c ON hs.id_cinema = c.id
            JOIN salas s ON hs.id_sala = s.id
            JOIN horarios h ON hs.id_horario = h.id
            ORDER BY hs.id
            LIMIT 5
        """)
        sessoes = cursor.fetchall()
        
        print(f"📊 Sessões encontradas (primeiras 5): {len(sessoes)}")
        
        for sessao in sessoes:
            print(f"   Sessão {sessao['id']}: {sessao['titulo']}")
            print(f"      → Cinema: {sessao['cinema']}")
            print(f"      → Sala: {sessao['nome_sala']} ({sessao['capacidade']} lugares)")
            print(f"      → Horário: {sessao['hora']}")
        
    except Exception as e:
        print(f"❌ Erro ao testar sessões: {e}")
    finally:
        cursor.close()
        conn.close()

def testar_reservas_existentes():
    """Testa se há reservas existentes"""
    print("\n🎫 TESTANDO RESERVAS EXISTENTES...")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        hoje = date.today().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT sessao_id, data_sessao, COUNT(*) as total_reservas, 
                   GROUP_CONCAT(lugar ORDER BY lugar) as lugares
            FROM reservas
            WHERE data_sessao >= %s
            GROUP BY sessao_id, data_sessao
            ORDER BY sessao_id, data_sessao
            LIMIT 5
        """, (hoje,))
        reservas = cursor.fetchall()
        
        print(f"📊 Reservas encontradas (a partir de hoje): {len(reservas)}")
        
        for reserva in reservas:
            print(f"   Sessão {reserva['sessao_id']} - {reserva['data_sessao']}: {reserva['total_reservas']} reservas")
            print(f"      → Lugares: {reserva['lugares']}")
        
    except Exception as e:
        print(f"❌ Erro ao testar reservas: {e}")
    finally:
        cursor.close()
        conn.close()

def testar_tipos_sessao():
    """Testa se há tipos de sessão com preços"""
    print("\n💰 TESTANDO TIPOS DE SESSÃO...")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, nome, preco_bilhete FROM tipos_sessao ORDER BY id")
        tipos = cursor.fetchall()
        
        print(f"📊 Tipos de sessão encontrados: {len(tipos)}")
        
        for tipo in tipos:
            print(f"   Tipo {tipo['id']}: {tipo['nome']} - €{tipo['preco_bilhete']}")
        
    except Exception as e:
        print(f"❌ Erro ao testar tipos de sessão: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🧪 INICIANDO TESTES DA FUNCIONALIDADE DE SELEÇÃO DE LUGARES")
    print("=" * 70)
    
    testar_estrutura_salas()
    testar_horarios_sessao()
    testar_reservas_existentes()
    testar_tipos_sessao()
    
    print("\n✅ TESTES CONCLUÍDOS!")
    print("=" * 70)