#!/usr/bin/env python3
"""
Script para testar a funcionalidade de pré-seleção automática
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

def simular_preselecao():
    """Simula o algoritmo de pré-seleção de lugares"""
    print("🎯 SIMULANDO PRÉ-SELEÇÃO AUTOMÁTICA...")
    
    # Simular uma sala com alguns lugares ocupados
    fileiras = ['A', 'B', 'C', 'D', 'E']
    lugares_por_fileira = 10
    lugares_ocupados = ['A3', 'A4', 'B7', 'C1', 'C2', 'C3', 'D8', 'D9']
    
    print(f"📊 Sala simulada: {len(fileiras)} fileiras x {lugares_por_fileira} lugares")
    print(f"🚫 Lugares ocupados: {', '.join(lugares_ocupados)}")
    
    # Gerar todos os lugares disponíveis
    lugares_disponiveis = []
    for fileira in fileiras:
        for pos in range(1, lugares_por_fileira + 1):
            lugar_nome = f"{fileira}{pos}"
            if lugar_nome not in lugares_ocupados:
                lugares_disponiveis.append({
                    'nome': lugar_nome,
                    'fileira': fileira,
                    'posicao': pos
                })
    
    print(f"✅ Lugares disponíveis: {len(lugares_disponiveis)}")
    
    # Testar diferentes quantidades
    for quantidade in [1, 2, 3, 4, 5]:
        print(f"\n🎫 Testando pré-seleção para {quantidade} lugar{'es' if quantidade > 1 else ''}:")
        
        # Agrupar por fileira
        por_fileira = {}
        for lugar in lugares_disponiveis:
            fileira = lugar['fileira']
            if fileira not in por_fileira:
                por_fileira[fileira] = []
            por_fileira[fileira].append(lugar)
        
        # Ordenar por posição
        for fileira in por_fileira:
            por_fileira[fileira].sort(key=lambda x: x['posicao'])
        
        # Procurar grupo consecutivo
        melhor_grupo = None
        for fileira, lugares_fileira in por_fileira.items():
            for i in range(len(lugares_fileira) - quantidade + 1):
                # Verificar se são consecutivos
                consecutivo = True
                for j in range(1, quantidade):
                    if lugares_fileira[i + j]['posicao'] != lugares_fileira[i + j - 1]['posicao'] + 1:
                        consecutivo = False
                        break
                
                if consecutivo:
                    melhor_grupo = lugares_fileira[i:i + quantidade]
                    break
            
            if melhor_grupo:
                break
        
        if melhor_grupo:
            nomes = [lugar['nome'] for lugar in melhor_grupo]
            print(f"   ✅ Grupo consecutivo encontrado: {', '.join(nomes)}")
        else:
            # Fallback: primeiros disponíveis
            fallback = lugares_disponiveis[:quantidade]
            nomes = [lugar['nome'] for lugar in fallback]
            print(f"   ⚠️  Sem grupo consecutivo, usando primeiros disponíveis: {', '.join(nomes)}")

def testar_urls_preselecao():
    """Gera URLs de teste para diferentes quantidades"""
    print("\n🔗 URLs DE TESTE PARA PRÉ-SELEÇÃO:")
    
    base_url = "http://localhost:5000/selecao_lugares"
    params = "horario_id=155&cinema_id=1&tipo_sessao_id=1&filme_id=2&data_sessao=2026-01-10"
    
    for quantidade in [1, 2, 3, 4, 5, 6]:
        url = f"{base_url}?{params}&quantidade={quantidade}"
        print(f"   {quantidade} lugar{'es' if quantidade > 1 else ''}: {url}")

if __name__ == "__main__":
    print("🧪 TESTANDO FUNCIONALIDADE DE PRÉ-SELEÇÃO")
    print("=" * 60)
    
    simular_preselecao()
    testar_urls_preselecao()
    
    print("\n✅ TESTE CONCLUÍDO!")
    print("=" * 60)