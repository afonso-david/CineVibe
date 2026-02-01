#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def testar_sessoes():
    print("=== TESTE DAS SESSÕES SEPARADAS ===")
    
    rotas_testar = [
        ('/sessao', 'Sessão Só Para Ti - Página Principal'),
        ('/sessao_exclusiva', 'Sessão Exclusiva'),
        ('/sessao_tematica', 'Sessão Temática'),
        ('/sessao_vintage', 'Sessão Vintage'),
        ('/sessao_romance', 'Sessão Romance'),
        ('/sessao_terror', 'Sessão Terror')
    ]
    
    base_url = "http://localhost:5000"
    
    for rota, nome in rotas_testar:
        try:
            print(f"\n🔍 Testando: {nome}")
            response = requests.get(f"{base_url}{rota}", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {rota} - Página carrega corretamente")
                
                # Verificar conteúdo específico
                content = response.text.lower()
                
                if rota == '/sessao':
                    if 'sessão exclusiva' in content and 'sessão temática' in content:
                        print("   ✅ Contém links para ambas as opções")
                    else:
                        print("   ❌ Links para as opções não encontrados")
                
                elif rota == '/sessao_tematica':
                    temas = ['vintage', 'romance', 'terror']
                    temas_encontrados = [tema for tema in temas if tema in content]
                    print(f"   ✅ Temas encontrados: {', '.join(temas_encontrados)}")
                    
                elif rota == '/sessao_exclusiva':
                    if 'exclusiva' in content or 'vip' in content:
                        print("   ✅ Conteúdo de sessão exclusiva presente")
                    else:
                        print("   ❌ Conteúdo de sessão exclusiva não encontrado")
                
            elif response.status_code == 302:
                print(f"⚠️ {rota} - Redirecionamento (pode ser normal)")
                
            else:
                print(f"❌ {rota} - Erro HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {rota} - Erro de conexão")
        except Exception as e:
            print(f"❌ {rota} - Erro: {str(e)}")
    
    print("\n📋 RESUMO DA ESTRUTURA:")
    print("1. /sessao - Página principal com duas opções:")
    print("   • Botão para Sessão Exclusiva")
    print("   • Botão para Sessão Temática")
    print()
    print("2. /sessao_exclusiva - Experiência VIP personalizada")
    print()
    print("3. /sessao_tematica - Página com 3 opções:")
    print("   • Sessão Vintage")
    print("   • Sessão Romance") 
    print("   • Sessão Terror")
    print()
    print("🌐 Acesse: http://localhost:5000/sessao")

if __name__ == "__main__":
    testar_sessoes()