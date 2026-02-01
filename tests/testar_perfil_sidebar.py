#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

def testar_perfil_sidebar():
    print("=== TESTE DA SEÇÃO DE PERFIL NO SIDEBAR ===")
    
    try:
        # Testar se a página de tipos de sessão carrega
        print("\n1. Testando página de tipos de sessão...")
        response = requests.get("http://localhost:5000/admin/tipos-sessao", timeout=5)
        
        if response.status_code == 200:
            print("✅ Página carrega com sucesso")
            
            # Verificar se tem a seção de perfil
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Procurar pela seção de perfil
            sidebar_footer = soup.find('div', class_='sidebar-footer')
            if sidebar_footer:
                print("✅ Seção sidebar-footer encontrada")
                
                user_profile = sidebar_footer.find('div', class_='user-profile')
                if user_profile:
                    print("✅ Seção user-profile encontrada")
                    
                    # Verificar elementos do perfil
                    user_avatar = user_profile.find('div', class_='user-avatar')
                    user_info = user_profile.find('div', class_='user-info')
                    user_actions = user_profile.find('div', class_='user-actions')
                    
                    if user_avatar:
                        print("✅ Avatar do usuário encontrado")
                    else:
                        print("❌ Avatar do usuário não encontrado")
                    
                    if user_info:
                        print("✅ Informações do usuário encontradas")
                        user_name = user_info.find('div', class_='user-name')
                        user_role = user_info.find('div', class_='user-role')
                        
                        if user_name:
                            print(f"   Nome: {user_name.get_text().strip()}")
                        if user_role:
                            print(f"   Papel: {user_role.get_text().strip()}")
                    else:
                        print("❌ Informações do usuário não encontradas")
                    
                    if user_actions:
                        print("✅ Ações do usuário encontradas")
                        
                        # Verificar botões
                        profile_btn = user_actions.find('a', href=lambda x: x and 'perfil' in x)
                        logout_btn = user_actions.find('a', href=lambda x: x and 'logout' in x)
                        
                        if profile_btn:
                            print("✅ Botão de perfil encontrado")
                        else:
                            print("❌ Botão de perfil não encontrado")
                        
                        if logout_btn:
                            print("✅ Botão de logout encontrado")
                        else:
                            print("❌ Botão de logout não encontrado")
                    else:
                        print("❌ Ações do usuário não encontradas")
                else:
                    print("❌ Seção user-profile não encontrada")
            else:
                print("❌ Seção sidebar-footer não encontrada")
                
        elif response.status_code == 302:
            print("⚠️ Redirecionamento (provavelmente para login)")
            print("   Isso é normal se não estiver logado como admin")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Certifique-se de que a aplicação está a correr.")
        return
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return
    
    print("\n2. Verificando arquivos atualizados...")
    import os
    
    templates_verificar = [
        'templates/admin_tipos_sessao.html',
        'templates/admin_dashboard.html',
        'templates/admin_filmes.html'
    ]
    
    for template in templates_verificar:
        if os.path.exists(template):
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'sidebar-footer' in content:
                print(f"✅ {template} - Seção de perfil adicionada")
            else:
                print(f"❌ {template} - Seção de perfil não encontrada")
        else:
            print(f"⚠️ {template} - Arquivo não encontrado")
    
    print("\n🎉 TESTE CONCLUÍDO!")
    print("Acesse http://localhost:5000/admin/tipos-sessao para ver a seção de perfil")

if __name__ == "__main__":
    testar_perfil_sidebar()