#!/usr/bin/env python3
"""
Script para testar a configuração de email do CineVibe
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def testar_email():
    """Testa o envio de email com as configurações atuais"""
    
    try:
        # Importar configurações
        from email_config import EMAIL_CONFIG
        print("✅ Configurações de email carregadas")
    except ImportError:
        print("❌ Ficheiro email_config.py não encontrado!")
        print("Execute: python setup.py")
        return False
    
    # Configurações
    smtp_server = EMAIL_CONFIG.get('smtp_server', 'smtp.gmail.com')
    smtp_port = EMAIL_CONFIG.get('smtp_port', 587)
    email_user = EMAIL_CONFIG.get('email')
    email_password = EMAIL_CONFIG.get('password')
    use_tls = EMAIL_CONFIG.get('use_tls', True)
    
    if not email_user or not email_password:
        print("❌ Email ou senha não configurados!")
        return False
    
    print(f"📧 Testando envio de email...")
    print(f"   Servidor: {smtp_server}:{smtp_port}")
    print(f"   Email: {email_user}")
    print(f"   TLS: {'Sim' if use_tls else 'Não'}")
    
    try:
        # Criar mensagem de teste
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_user  # Enviar para si próprio
        msg['Subject'] = "🎬 CineVibe - Teste de Email"
        
        corpo = """
        <html>
        <body>
            <h2>🎬 CineVibe - Teste de Configuração</h2>
            <p>Se recebeu este email, a configuração está a funcionar corretamente!</p>
            <p><strong>Data/Hora:</strong> {}</p>
            <hr>
            <p><em>Este é um email de teste automático do sistema CineVibe.</em></p>
        </body>
        </html>
        """.format(datetime.now().strftime("%d/%m/%Y às %H:%M:%S"))
        
        msg.attach(MIMEText(corpo, 'html', 'utf-8'))
        
        # Conectar ao servidor SMTP
        print("🔗 Conectando ao servidor SMTP...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        if use_tls:
            server.starttls()
            print("🔒 TLS ativado")
        
        # Fazer login
        print("🔑 Fazendo login...")
        server.login(email_user, email_password)
        
        # Enviar email
        print("📤 Enviando email de teste...")
        server.send_message(msg)
        server.quit()
        
        print("✅ Email enviado com sucesso!")
        print(f"📬 Verifique a caixa de entrada de: {email_user}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Erro de autenticação!")
        print("   Verifique:")
        print("   - Email está correto")
        print("   - Está a usar senha de app (não senha normal)")
        print("   - Verificação em 2 passos está ativa")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ Erro SMTP: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    from datetime import datetime
    
    print("🎬 CineVibe - Teste de Email")
    print("=" * 40)
    
    if testar_email():
        print("\n🎉 Configuração de email está funcionando!")
    else:
        print("\n❌ Problemas na configuração de email")
        print("📖 Consulte GUIA_CONFIGURACAO_EMAIL.md para ajuda")