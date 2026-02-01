#!/usr/bin/env python3
"""
Script para testar os novos layouts mais largos
"""

def testar_novos_layouts():
    """Testa os novos layouts mais largos e menos altos"""
    print("🏗️ TESTANDO NOVOS LAYOUTS MAIS LARGOS...")
    
    capacidades = [100, 150, 250, 300, 350, 400]
    
    for capacidade in capacidades:
        print(f"\n🎬 Capacidade: {capacidade} lugares")
        
        # Aplicar nova lógica de layout
        if capacidade <= 150:
            # Sala pequena: 8 fileiras x 19 lugares (mais largo)
            fileiras = 8
            lugares_por_fileira = 19
            tipo = "Pequena"
        elif capacidade <= 300:
            # Sala média: 10 fileiras x 30 lugares (bem mais largo)
            fileiras = 10
            lugares_por_fileira = 30
            tipo = "Média"
        else:
            # Sala grande (IMAX): 12 fileiras x 33 lugares (muito mais largo)
            fileiras = 12
            lugares_por_fileira = 33
            tipo = "Grande/IMAX"
        
        total_calculado = fileiras * lugares_por_fileira
        
        print(f"   📊 Tipo: {tipo}")
        print(f"   📐 Layout: {fileiras} fileiras x {lugares_por_fileira} lugares")
        print(f"   🎯 Total calculado: {total_calculado}")
        print(f"   📈 Diferença: {total_calculado - capacidade} lugares")
        
        # Calcular proporção (largura vs altura)
        proporcao = lugares_por_fileira / fileiras
        print(f"   📏 Proporção (L/A): {proporcao:.1f}:1 {'(mais largo)' if proporcao > 2 else '(equilibrado)'}")

def comparar_layouts():
    """Compara layouts antigos vs novos"""
    print("\n🔄 COMPARAÇÃO: LAYOUTS ANTIGOS vs NOVOS")
    print("=" * 60)
    
    capacidades_teste = [150, 300, 400]
    
    for capacidade in capacidades_teste:
        print(f"\n🎬 Capacidade: {capacidade} lugares")
        
        # Layout antigo
        if capacidade <= 150:
            old_fileiras, old_lugares = 10, 15
        elif capacidade <= 300:
            old_fileiras, old_lugares = 15, 20
        else:
            old_fileiras, old_lugares = 20, 18
        
        # Layout novo
        if capacidade <= 150:
            new_fileiras, new_lugares = 8, 19
        elif capacidade <= 300:
            new_fileiras, new_lugares = 10, 30
        else:
            new_fileiras, new_lugares = 12, 33
        
        old_proporcao = old_lugares / old_fileiras
        new_proporcao = new_lugares / new_fileiras
        
        print(f"   📊 ANTIGO: {old_fileiras}x{old_lugares} = {old_fileiras * old_lugares} (proporção {old_proporcao:.1f}:1)")
        print(f"   ✨ NOVO:   {new_fileiras}x{new_lugares} = {new_fileiras * new_lugares} (proporção {new_proporcao:.1f}:1)")
        print(f"   📈 Melhoria: {new_proporcao - old_proporcao:.1f} pontos mais largo")
        print(f"   📉 Redução altura: {old_fileiras - new_fileiras} fileiras menos")

def simular_visual():
    """Simula como ficará visualmente"""
    print("\n👁️ SIMULAÇÃO VISUAL DOS LAYOUTS")
    print("=" * 60)
    
    # Exemplo de sala IMAX (400 lugares)
    print("\n🎬 Exemplo: Sala IMAX (400 lugares)")
    print("   Layout: 12 fileiras x 33 lugares")
    print("\n   Visualização (cada . = lugar):")
    
    for i in range(12):
        letra = chr(65 + i)  # A, B, C, etc.
        linha = f"   {letra} " + "." * 33
        if i == 5:  # Meio da sala
            linha += " ← Meio da sala"
        print(linha)
    
    print(f"\n   📐 Dimensões visuais:")
    print(f"   • Largura: 33 lugares (muito mais largo)")
    print(f"   • Altura: 12 fileiras (bem menos alto)")
    print(f"   • Proporção: 2.75:1 (quase 3x mais largo que alto)")

if __name__ == "__main__":
    print("🧪 TESTANDO LAYOUTS MAIS LARGOS")
    print("=" * 50)
    
    testar_novos_layouts()
    comparar_layouts()
    simular_visual()
    
    print("\n✅ TESTE CONCLUÍDO!")
    print("=" * 50)
    print("\n💡 RESUMO DAS MELHORIAS:")
    print("   • Salas muito mais largas (até 33 lugares por fileira)")
    print("   • Menos fileiras verticais (máximo 12 vs 20 anterior)")
    print("   • Melhor proporção visual (mais parecido com cinemas reais)")
    print("   • Menos scroll vertical necessário")
    print("   • Layout mais compacto e elegante")