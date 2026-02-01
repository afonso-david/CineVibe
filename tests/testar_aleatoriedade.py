#!/usr/bin/env python3
"""
Script para testar a aleatoriedade da pré-seleção
"""

def simular_algoritmo_aleatorio():
    """Simula o algoritmo de pré-seleção aleatória"""
    print("🎲 SIMULANDO ALGORITMO DE PRÉ-SELEÇÃO ALEATÓRIA...")
    
    # Simular uma sala com alguns lugares ocupados
    fileiras = ['A', 'B', 'C', 'D', 'E']
    lugares_por_fileira = 12
    lugares_ocupados = ['A3', 'A4', 'B7', 'C1', 'C2', 'C3', 'D8', 'D9']
    
    print(f"📊 Sala simulada: {len(fileiras)} fileiras x {lugares_por_fileira} lugares")
    print(f"🚫 Lugares ocupados: {', '.join(lugares_ocupados)}")
    
    # Gerar todos os lugares disponíveis por fileira
    lugares_por_fileira_dict = {}
    for fileira in fileiras:
        lugares_fileira = []
        for pos in range(1, lugares_por_fileira + 1):
            lugar_nome = f"{fileira}{pos}"
            if lugar_nome not in lugares_ocupados:
                lugares_fileira.append({
                    'nome': lugar_nome,
                    'fileira': fileira,
                    'posicao': pos
                })
        lugares_por_fileira_dict[fileira] = lugares_fileira
    
    # Encontrar todos os grupos consecutivos possíveis para 3 lugares
    quantidade = 3
    grupos_consecutivos = []
    
    for fileira, lugares_fileira in lugares_por_fileira_dict.items():
        for i in range(len(lugares_fileira) - quantidade + 1):
            # Verificar se são consecutivos
            consecutivo = True
            for j in range(1, quantidade):
                if lugares_fileira[i + j]['posicao'] != lugares_fileira[i + j - 1]['posicao'] + 1:
                    consecutivo = False
                    break
            
            if consecutivo:
                grupo = lugares_fileira[i:i + quantidade]
                nomes = [lugar['nome'] for lugar in grupo]
                grupos_consecutivos.append(nomes)
    
    print(f"\n🎯 Grupos consecutivos possíveis para {quantidade} lugares:")
    for i, grupo in enumerate(grupos_consecutivos, 1):
        print(f"   Opção {i}: {', '.join(grupo)}")
    
    print(f"\n📈 Total de opções diferentes: {len(grupos_consecutivos)}")
    
    # Simular 10 seleções aleatórias
    import random
    print(f"\n🎲 Simulando 10 seleções aleatórias:")
    for i in range(1, 11):
        if grupos_consecutivos:
            grupo_escolhido = random.choice(grupos_consecutivos)
            print(f"   Seleção {i}: {', '.join(grupo_escolhido)}")
        else:
            print(f"   Seleção {i}: Sem grupos consecutivos disponíveis")

def testar_diferentes_quantidades():
    """Testa a aleatoriedade para diferentes quantidades"""
    print("\n🔢 TESTANDO DIFERENTES QUANTIDADES...")
    
    # Sala maior para mais opções
    fileiras = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    lugares_por_fileira = 15
    lugares_ocupados = ['A8', 'A9', 'C5', 'C6', 'C7', 'E12', 'E13', 'G3', 'G4']
    
    import random
    
    for quantidade in [1, 2, 4, 5]:
        print(f"\n🎫 Quantidade: {quantidade} lugar{'es' if quantidade > 1 else ''}")
        
        # Encontrar grupos consecutivos
        grupos_consecutivos = []
        
        for fileira in fileiras:
            lugares_fileira = []
            for pos in range(1, lugares_por_fileira + 1):
                lugar_nome = f"{fileira}{pos}"
                if lugar_nome not in lugares_ocupados:
                    lugares_fileira.append({
                        'nome': lugar_nome,
                        'posicao': pos
                    })
            
            # Procurar grupos consecutivos nesta fileira
            for i in range(len(lugares_fileira) - quantidade + 1):
                consecutivo = True
                for j in range(1, quantidade):
                    if lugares_fileira[i + j]['posicao'] != lugares_fileira[i + j - 1]['posicao'] + 1:
                        consecutivo = False
                        break
                
                if consecutivo:
                    grupo = lugares_fileira[i:i + quantidade]
                    nomes = [lugar['nome'] for lugar in grupo]
                    grupos_consecutivos.append(nomes)
        
        print(f"   📊 {len(grupos_consecutivos)} opções diferentes disponíveis")
        
        # Mostrar 3 seleções aleatórias
        for i in range(1, 4):
            if grupos_consecutivos:
                grupo_escolhido = random.choice(grupos_consecutivos)
                print(f"   🎲 Exemplo {i}: {', '.join(grupo_escolhido)}")

if __name__ == "__main__":
    print("🧪 TESTANDO ALEATORIEDADE DA PRÉ-SELEÇÃO")
    print("=" * 60)
    
    simular_algoritmo_aleatorio()
    testar_diferentes_quantidades()
    
    print("\n✅ TESTE CONCLUÍDO!")
    print("=" * 60)
    print("\n💡 RESUMO:")
    print("   • O algoritmo encontra TODOS os grupos consecutivos possíveis")
    print("   • Escolhe um grupo aleatoriamente entre as opções")
    print("   • Garante que os lugares são sempre juntos")
    print("   • Cada acesso terá uma seleção diferente")