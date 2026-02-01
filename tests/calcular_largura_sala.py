#!/usr/bin/env python3
"""
Script para calcular se a sala cabe na tela sem scroll
"""

def calcular_largura_sala():
    """Calcula a largura total necessária para diferentes layouts"""
    print("📐 CALCULANDO LARGURA NECESSÁRIA PARA AS SALAS")
    print("=" * 60)
    
    # Configurações atuais
    configs = [
        {"nome": "Desktop", "lugar_size": 20, "gap": 4, "padding": 30, "tela_width": 1920},
        {"nome": "Laptop", "lugar_size": 18, "gap": 3, "padding": 20, "tela_width": 1366},
        {"nome": "Tablet", "lugar_size": 16, "gap": 2, "padding": 16, "tela_width": 768},
        {"nome": "Mobile", "lugar_size": 12, "gap": 1, "padding": 10, "tela_width": 480},
    ]
    
    # Layouts das salas
    layouts = [
        {"tipo": "Pequena", "fileiras": 8, "lugares_por_fileira": 19},
        {"tipo": "Média", "fileiras": 10, "lugares_por_fileira": 30},
        {"tipo": "Grande/IMAX", "fileiras": 12, "lugares_por_fileira": 33},
    ]
    
    for config in configs:
        print(f"\n🖥️ {config['nome']} (Tela: {config['tela_width']}px)")
        print("-" * 40)
        
        for layout in layouts:
            # Calcular largura total necessária
            lugares_width = layout['lugares_por_fileira'] * config['lugar_size']
            gaps_width = (layout['lugares_por_fileira'] - 1) * config['gap']
            padding_width = config['padding'] * 2  # padding esquerda + direita
            
            largura_total = lugares_width + gaps_width + padding_width
            
            # Verificar se cabe
            cabe = largura_total <= config['tela_width']
            status = "✅ Cabe" if cabe else "❌ Não cabe"
            
            print(f"   {layout['tipo']}: {largura_total}px {status}")
            print(f"      • {layout['lugares_por_fileira']} lugares × {config['lugar_size']}px = {lugares_width}px")
            print(f"      • {layout['lugares_por_fileira']-1} gaps × {config['gap']}px = {gaps_width}px")
            print(f"      • Padding: {padding_width}px")
            
            if not cabe:
                excesso = largura_total - config['tela_width']
                print(f"      • Excesso: {excesso}px")

def sugerir_ajustes():
    """Sugere ajustes para que todas as salas caibam"""
    print(f"\n💡 SUGESTÕES DE AJUSTE")
    print("=" * 60)
    
    # Testar diferentes tamanhos
    tela_width = 1366  # Laptop comum
    lugares_por_fileira = 33  # Pior caso (sala IMAX)
    padding = 30
    
    print(f"🎯 Objetivo: Sala IMAX (33 lugares) caber em laptop (1366px)")
    print(f"   Padding disponível: {padding * 2}px")
    print(f"   Largura útil: {tela_width - (padding * 2)}px")
    
    largura_util = tela_width - (padding * 2)
    
    # Testar diferentes combinações
    for lugar_size in range(12, 25):
        for gap in range(1, 6):
            lugares_width = lugares_por_fileira * lugar_size
            gaps_width = (lugares_por_fileira - 1) * gap
            largura_total = lugares_width + gaps_width
            
            if largura_total <= largura_util:
                print(f"   ✅ Lugar: {lugar_size}px, Gap: {gap}px → Total: {largura_total}px")
                if lugar_size >= 16:  # Tamanho mínimo aceitável
                    print(f"      🎯 RECOMENDADO: {lugar_size}px lugares, {gap}px gaps")
                    return lugar_size, gap
    
    print("   ❌ Não foi possível encontrar combinação adequada")
    return None, None

if __name__ == "__main__":
    calcular_largura_sala()
    sugerir_ajustes()
    
    print(f"\n📋 RESUMO:")
    print("• Lugares menores (20px → 16px) para caber melhor")
    print("• Gaps menores (4px → 2px) para economizar espaço")
    print("• Padding reduzido para maximizar espaço útil")
    print("• Responsividade agressiva para telas pequenas")