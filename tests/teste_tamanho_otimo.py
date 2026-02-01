#!/usr/bin/env python3
"""
Script para testar o tamanho ótimo dos lugares
"""

def testar_tamanho_22px():
    """Testa se 22px funciona bem"""
    print("🎯 TESTANDO TAMANHO 22PX")
    print("=" * 40)
    
    # Configurações para 22px
    lugar_size = 22
    gap = 3
    padding = 30
    
    # Layouts das salas
    layouts = [
        {"tipo": "Pequena", "lugares": 19},
        {"tipo": "Média", "lugares": 30},
        {"tipo": "Grande/IMAX", "lugares": 33},
    ]
    
    # Telas comuns
    telas = [
        {"nome": "Desktop HD", "width": 1920},
        {"nome": "Laptop", "width": 1366},
        {"nome": "Tablet", "width": 768},
    ]
    
    for tela in telas:
        print(f"\n🖥️ {tela['nome']} ({tela['width']}px)")
        
        for layout in layouts:
            lugares_width = layout['lugares'] * lugar_size
            gaps_width = (layout['lugares'] - 1) * gap
            padding_width = padding * 2
            
            largura_total = lugares_width + gaps_width + padding_width
            
            cabe = largura_total <= tela['width']
            status = "✅" if cabe else "❌"
            
            print(f"   {layout['tipo']}: {largura_total}px {status}")
            
            if cabe:
                sobra = tela['width'] - largura_total
                print(f"      Sobra: {sobra}px")

def comparar_tamanhos():
    """Compara diferentes tamanhos"""
    print(f"\n📊 COMPARAÇÃO DE TAMANHOS")
    print("=" * 40)
    
    tamanhos = [16, 18, 20, 22, 24]
    lugares = 33  # Pior caso (IMAX)
    tela_width = 1366  # Laptop comum
    padding = 60
    
    print(f"Sala IMAX (33 lugares) em Laptop (1366px):")
    
    for tamanho in tamanhos:
        gap = max(1, tamanho // 8)  # Gap proporcional
        
        lugares_width = lugares * tamanho
        gaps_width = (lugares - 1) * gap
        largura_total = lugares_width + gaps_width + padding
        
        cabe = largura_total <= tela_width
        status = "✅" if cabe else "❌"
        
        visibilidade = "Muito pequeno" if tamanho < 18 else "Pequeno" if tamanho < 22 else "Bom" if tamanho < 26 else "Grande"
        
        print(f"   {tamanho}px (gap {gap}px): {largura_total}px {status} - {visibilidade}")

if __name__ == "__main__":
    testar_tamanho_22px()
    comparar_tamanhos()
    
    print(f"\n💡 CONCLUSÃO:")
    print("• 22px é um bom equilíbrio entre visibilidade e espaço")
    print("• Cabe confortavelmente na maioria das telas")
    print("• Visível o suficiente para interação fácil")
    print("• Mantém o formato quadrado")