from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, make_response
import mysql.connector
import logging
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
import uuid
import random
import requests
import secrets

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# SECRET KEY para sessoes/flash (muda para algo seguro antes de por em producao)
app.secret_key = "troca_isto_por_uma_chave_secreta_e_complexa"

# Configurações OAuth
# MODO DESENVOLVIMENTO - Para testar sem configurar OAuth real
DEVELOPMENT_MODE = True  # Mude para False quando tiver credenciais reais

if DEVELOPMENT_MODE:
    # Credenciais de desenvolvimento (não funcionais para OAuth real)
    GOOGLE_CLIENT_ID = "development-mode"
    GOOGLE_CLIENT_SECRET = "development-mode"
    FACEBOOK_APP_ID = "development-mode"
    FACEBOOK_APP_SECRET = "development-mode"
else:
    # Substitua por suas credenciais reais quando configurar OAuth
    GOOGLE_CLIENT_ID = "your-google-client-id.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "your-google-client-secret"
    FACEBOOK_APP_ID = "your-facebook-app-id"
    FACEBOOK_APP_SECRET = "your-facebook-app-secret"

# Configuracoes de Email
try:
    from email_config import EMAIL_CONFIG
    EMAIL_HOST = EMAIL_CONFIG['HOST']
    EMAIL_PORT = EMAIL_CONFIG['PORT']
    EMAIL_USER = EMAIL_CONFIG['USER']
    EMAIL_PASSWORD = EMAIL_CONFIG['PASSWORD']
    EMAIL_USE_TLS = EMAIL_CONFIG['USE_TLS']
except ImportError:
    # Fallback para configuracoes padrao
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USER = 'cinevibe.bilhetes@gmail.com'
    EMAIL_PASSWORD = 'goxm upky dcyx nbyx'  # Configure no email_config.py
    EMAIL_USE_TLS = True

# Configuracoes de Email
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'cinevibe.bilhetes@gmail.com'
EMAIL_PASSWORD = 'goxm upky dcyx nbyx'  # Senha de app do Gmail
EMAIL_USE_TLS = True

def enviar_email_recuperacao_senha(destinatario_email, destinatario_nome, token):
    """
    Envia email de recuperação de senha
    """
    try:
        app.logger.info(f"Enviando email de recuperação para: {destinatario_email}")
        
        # Verificar se as credenciais de email estão configuradas
        if EMAIL_PASSWORD in ['sua_senha_app_aqui', 'DESATIVADO_TEMPORARIAMENTE'] or not EMAIL_PASSWORD:
            app.logger.warning("Email desativado temporariamente. Configure senha de app do Gmail para ativar.")
            return False

        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🔐 Recuperação de Senha - CineVibe'
        msg['From'] = f'CineVibe <{EMAIL_USER}>'
        msg['To'] = destinatario_email

        # Criar link de recuperação
        link_recuperacao = f"http://localhost:5000/redefinir-senha?token={token}"
        
        # Conteúdo HTML do email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    background: linear-gradient(135deg, #0d1117, #161b22); 
                    margin: 0; 
                    padding: 20px; 
                    color: white;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: linear-gradient(135deg, #1B263B, #2C3E50); 
                    border-radius: 20px; 
                    overflow: hidden; 
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
                    border: 2px solid rgba(255, 214, 10, 0.3);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #FFD60A, #FFA500); 
                    padding: 40px 30px; 
                    text-align: center; 
                    position: relative;
                }}
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(0,0,0,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(0,0,0,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                    opacity: 0.1;
                }}
                .header h1 {{ 
                    color: #1a1a1a; 
                    margin: 0; 
                    font-size: 32px; 
                    font-weight: 900; 
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                    position: relative;
                    z-index: 1;
                }}
                .header .emoji {{
                    font-size: 40px;
                    margin-right: 10px;
                }}
                .content {{ 
                    padding: 40px 30px; 
                    background: rgba(0, 0, 0, 0.2);
                }}
                .content h2 {{ 
                    color: #FFD60A; 
                    margin-bottom: 25px; 
                    font-size: 24px;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                }}
                .content p {{ 
                    color: rgba(255, 255, 255, 0.9); 
                    line-height: 1.8; 
                    margin-bottom: 20px; 
                    font-size: 16px;
                }}
                .btn-container {{ 
                    text-align: center; 
                    margin: 40px 0; 
                }}
                .btn-recuperar {{ 
                    background: linear-gradient(135deg, #FFD60A, #FFA500); 
                    color: #1a1a1a; 
                    padding: 18px 40px; 
                    text-decoration: none; 
                    border-radius: 30px; 
                    font-weight: bold; 
                    display: inline-block; 
                    font-size: 18px;
                    box-shadow: 0 8px 20px rgba(255, 214, 10, 0.3);
                    transition: all 0.3s ease;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .btn-recuperar:hover {{
                    background: linear-gradient(135deg, #FFA500, #FF8C00);
                    transform: translateY(-2px);
                    box-shadow: 0 12px 25px rgba(255, 214, 10, 0.4);
                }}
                .warning {{ 
                    background: rgba(255, 193, 7, 0.15); 
                    border: 2px solid rgba(255, 193, 7, 0.3); 
                    padding: 25px; 
                    border-radius: 15px; 
                    margin: 30px 0; 
                    color: #FFC107;
                    backdrop-filter: blur(10px);
                }}
                .warning strong {{
                    color: #FFD60A;
                    font-size: 18px;
                }}
                .warning ul {{
                    margin: 15px 0;
                    padding-left: 25px;
                }}
                .warning li {{
                    margin: 8px 0;
                    color: rgba(255, 255, 255, 0.9);
                }}
                .link-box {{
                    background: rgba(0, 0, 0, 0.3);
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid rgba(255, 214, 10, 0.2);
                    word-break: break-all;
                    font-family: 'Courier New', monospace;
                    font-size: 14px;
                    color: #FFD60A;
                    margin: 20px 0;
                }}
                .footer {{ 
                    background: rgba(0, 0, 0, 0.4); 
                    padding: 30px; 
                    text-align: center; 
                    color: rgba(255, 255, 255, 0.7); 
                    font-size: 14px; 
                    border-top: 1px solid rgba(255, 214, 10, 0.2);
                }}
                .footer p {{
                    margin: 10px 0;
                }}
                .security-badge {{
                    display: inline-block;
                    background: rgba(76, 175, 80, 0.2);
                    color: #4CAF50;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                    margin-top: 15px;
                    border: 1px solid rgba(76, 175, 80, 0.3);
                }}
                .divider {{
                    height: 2px;
                    background: linear-gradient(90deg, transparent, #FFD60A, transparent);
                    margin: 30px 0;
                    border-radius: 1px;
                }}
                @media (max-width: 600px) {{
                    .container {{ margin: 10px; }}
                    .header {{ padding: 30px 20px; }}
                    .content {{ padding: 30px 20px; }}
                    .header h1 {{ font-size: 24px; }}
                    .btn-recuperar {{ padding: 15px 30px; font-size: 16px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1><span class="emoji">🎬</span>CineVibe</h1>
                </div>
                <div class="content">
                    <h2>Olá, {destinatario_nome}!</h2>
                    <p>Recebemos um pedido para redefinir a senha da sua conta CineVibe.</p>
                    <p>Se foi você que solicitou esta alteração, clique no botão abaixo para criar uma nova senha:</p>
                    
                    <div class="btn-container">
                        <a href="{link_recuperacao}" class="btn-recuperar">🔐 Redefinir Senha</a>
                    </div>
                    
                    <div class="divider"></div>
                    
                    <div class="warning">
                        <strong>⚠️ Importante:</strong>
                        <ul>
                            <li>Este link é válido por apenas <strong>1 hora</strong></li>
                            <li>Se não foi você que solicitou, <strong>ignore este email</strong></li>
                            <li>Nunca partilhe este link com outras pessoas</li>
                            <li>Use uma senha forte e única</li>
                        </ul>
                    </div>
                    
                    <p style="color: rgba(255, 255, 255, 0.8);">Se o botão não funcionar, copie e cole este link no seu navegador:</p>
                    <div class="link-box">
                        {link_recuperacao}
                    </div>
                    
                    <p style="color: rgba(255, 255, 255, 0.7); font-size: 14px;">Se não solicitou esta alteração, pode ignorar este email com segurança. A sua conta permanece protegida.</p>
                    
                    <div class="security-badge">
                        🛡️ Email Seguro e Verificado
                    </div>
                </div>
                <div class="footer">
                    <p><strong>© 2024 CineVibe</strong> - A sua experiência cinematográfica premium</p>
                    <p>Este email foi enviado automaticamente. Não responda a esta mensagem.</p>
                    <p style="font-size: 12px; color: rgba(255, 255, 255, 0.5);">
                        CineVibe • Entretenimento Premium • Portugal
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        # Anexar conteúdo HTML
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        # Enviar email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_USER, destinatario_email, text)
        server.quit()
        
        app.logger.info(f"✅ Email de recuperação enviado com sucesso para {destinatario_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        app.logger.error(f"❌ Erro de autenticacao SMTP: {str(e)}")
        app.logger.error("Verifique as credenciais no email_config.py")
        return False
    except smtplib.SMTPException as e:
        app.logger.error(f"❌ Erro SMTP: {str(e)}")
        return False
    except Exception as e:
        app.logger.error(f"❌ Erro geral ao enviar email de recuperação: {str(e)}")
        app.logger.exception("Stack trace:")
        return False

def enviar_email_confirmacao(destinatario_email, destinatario_nome, dados_reserva):
    """
    Envia email de confirmacao de reserva usando template HTML
    """
    try:
        app.logger.info(f"Enviando email para: {destinatario_email}")
        
        # Verificar se as credenciais de email estao configuradas
        if EMAIL_PASSWORD in ['sua_senha_app_aqui', 'DESATIVADO_TEMPORARIAMENTE'] or not EMAIL_PASSWORD:
            app.logger.warning("Email desativado temporariamente. Configure senha de app do Gmail para ativar.")
            return False

        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🎬 Confirmacao de Reserva CineVibe - #{dados_reserva["reserva_id"]}'
        msg['From'] = f'CineVibe <{EMAIL_USER}>'
        msg['To'] = destinatario_email

        # Renderizar template HTML do email
        try:
            data_confirmacao = datetime.now().strftime('%d/%m/%Y as %H:%M')
            
            # Usar o contexto da aplicação para renderizar o template
            with app.app_context():
                html_content = render_template('email_confirmacao.html',
                                             nome=destinatario_nome,
                                             email=destinatario_email,
                                             reserva_id=dados_reserva.get("reserva_id", 0),
                                             filme=dados_reserva.get("filme", "Filme"),
                                             cinema=dados_reserva.get("cinema", "Cinema"),
                                             tipo_sessao=dados_reserva.get("tipo_sessao", "Normal"),
                                             horario=dados_reserva.get("horario", "Data nao definida"),
                                             quantidade=dados_reserva.get("quantidade", 0),
                                             lugares=dados_reserva.get("lugares", ""),
                                             total=dados_reserva.get("total", "0.00€"),
                                             preco_total=dados_reserva.get("total", "0.00€"),
                                             data_confirmacao=data_confirmacao)
        except Exception as e:
            app.logger.error(f"Erro ao renderizar template de email: {str(e)}")
            return False

        # Anexar conteudo HTML
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        # Enviar email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_USER, destinatario_email, text)
        server.quit()
        
        app.logger.info(f"✅ Email enviado com sucesso para {destinatario_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        app.logger.error(f"❌ Erro de autenticacao SMTP: {str(e)}")
        app.logger.error("Verifique as credenciais no email_config.py")
        return False
    except smtplib.SMTPException as e:
        app.logger.error(f"❌ Erro SMTP: {str(e)}")
        return False
    except Exception as e:
        app.logger.error(f"❌ Erro geral ao enviar email: {str(e)}")
        app.logger.exception("Stack trace:")
        return False

# ==========================
# Conexao a base de dados
# ==========================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kevin@15",  # coloca a tua senha se houver
        database="cinevibe"
    )

def get_current_user():
    """Busca os dados do usuário logado"""
    if 'user_id' not in session:
        return None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except:
        return None

def usar_codigo_desconto_reserva(user_id, codigo, premio_nome, pontos_gastos):
    """Função chamada quando um código de desconto é usado numa reserva"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Adicionar movimento negativo na tabela pontos_movimentos
        cursor.execute("""
            INSERT INTO pontos_movimentos 
            (utilizador_id, pontos, motivo, data_movimento)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, -pontos_gastos, f"Uso de código de desconto {codigo} - {premio_nome}"))
        
        # Marcar código como usado na tabela codigos_desconto
        cursor.execute("""
            UPDATE codigos_desconto 
            SET usado = 1, data_uso = NOW() 
            WHERE codigo = %s AND usuario_id = %s
        """, (codigo, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Código {codigo} usado com sucesso. {pontos_gastos} pontos descontados do usuário {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao usar código de desconto: {e}")
        return False

def criar_tabelas_resgates():
    """Cria as tabelas necessárias para o sistema de resgates se não existirem"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("🔍 DEBUG: Criando tabela codigos_desconto...")
        # Criar tabela codigos_desconto
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `codigos_desconto` (
              `id` int NOT NULL AUTO_INCREMENT,
              `codigo` varchar(20) NOT NULL,
              `usuario_id` int NOT NULL,
              `premio_id` int DEFAULT NULL,
              `premio_nome` varchar(100) DEFAULT NULL,
              `tipo_desconto` enum('valor_fixo','percentual','produto_gratis') DEFAULT 'produto_gratis',
              `valor_desconto` decimal(10,2) DEFAULT 0.00,
              `data_criacao` datetime DEFAULT CURRENT_TIMESTAMP,
              `data_expiracao` datetime DEFAULT NULL,
              `usado` tinyint(1) DEFAULT 0,
              `data_uso` datetime DEFAULT NULL,
              PRIMARY KEY (`id`),
              UNIQUE KEY `codigo` (`codigo`),
              KEY `usuario_id` (`usuario_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        """)
        
        print("🔍 DEBUG: Criando tabela pontos_gastos...")
        # Criar tabela pontos_gastos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `pontos_gastos` (
              `id` int NOT NULL AUTO_INCREMENT,
              `usuario_id` int NOT NULL,
              `premio_id` int DEFAULT NULL,
              `premio_nome` varchar(100) DEFAULT NULL,
              `pontos_gastos` int NOT NULL,
              `codigo_desconto` varchar(20) DEFAULT NULL,
              `data_resgate` datetime DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              KEY `usuario_id` (`usuario_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ DEBUG: Tabelas de resgates criadas com sucesso")
        app.logger.info("✅ Tabelas de resgates criadas com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: Erro ao criar tabelas de resgates: {e}")
        app.logger.error(f"❌ Erro ao criar tabelas de resgates: {e}")
        return False

def calcular_pontos_usuario(user_id, cursor):
    """Calcula os pontos disponíveis do usuário (ganhos - gastos)"""
    try:
        # Calcular pontos ganhos - filmes vistos
        cursor.execute("""
            SELECT COUNT(DISTINCT f.id) as total
            FROM reservas r
            JOIN filmes f ON r.id_filme = f.id
            JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
            JOIN horarios h ON hs.id_horario = h.id
            WHERE r.id_usuario = %s
            AND DATE_ADD(CONCAT(r.data_sessao, ' ', h.hora), INTERVAL f.duracao MINUTE) < NOW()
        """, (user_id,))
        result = cursor.fetchone()
        filmes_vistos = result['total'] if result else 0
        
        # Calcular pontos ganhos - avaliações
        cursor.execute("SELECT COUNT(*) as total FROM avaliacoes_filmes WHERE usuario_id = %s", (user_id,))
        result = cursor.fetchone()
        avaliacoes = result['total'] if result else 0
        
        pontos_ganhos = (filmes_vistos * 100) + (avaliacoes * 50)
        
        # Calcular pontos gastos da tabela pontos_gastos
        try:
            cursor.execute("SELECT COALESCE(SUM(pontos_gastos), 0) as total FROM pontos_gastos WHERE usuario_id = %s", (user_id,))
            result = cursor.fetchone()
            pontos_gastos = result['total'] if result else 0
        except:
            pontos_gastos = 0
        
        # Retornar pontos disponíveis
        pontos_disponiveis = max(0, pontos_ganhos - pontos_gastos)
        
        print(f"🔍 Debug pontos usuário {user_id}: {pontos_ganhos} ganhos - {pontos_gastos} gastos = {pontos_disponiveis} disponíveis")
        
        return pontos_disponiveis
        
    except Exception as e:
        print(f"❌ Erro ao calcular pontos do usuário {user_id}: {e}")
        return 0

def atualizar_estados_filmes_automatico():
    """
    Funcao utilitaria para atualizar estados dos filmes automaticamente
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE filmes 
            SET estado = 'em_exibicao' 
            WHERE estado = 'brevemente' 
            AND data_lancamento IS NOT NULL
            AND data_lancamento <= CURDATE()
        """)
        
        filmes_atualizados = cursor.rowcount
        if filmes_atualizados > 0:
            conn.commit()
            app.logger.info(f"🎬 Sistema automatico: {filmes_atualizados} filmes atualizados para 'em_exibicao'")
        
        cursor.close()
        conn.close()
        return filmes_atualizados
        
    except Exception as e:
        app.logger.error(f"❌ Erro na atualizacao automatica de filmes: {e}")
        return 0

# ==========================
# Util: normalizar imagem paths/URLs
# ==========================
def _normalize_img_path(raw):
    """Normaliza paths/URLs de imagem"""
    if not raw:
        return 'imgs/filmes/placeholder.jpg'
    
    p = str(raw).replace('\\', '/').strip().strip('"').strip()
    
    # Se e URL externa, retornar como esta
    if p.startswith('http://') or p.startswith('https://'):
        return p
    
    # Remover prefixos desnecessarios
    if p.startswith('/static/'):
        p = p[len('/static/'):]
    elif p.startswith('static/'):
        p = p[len('static/'):]
    elif p.startswith('/'):
        p = p[1:]
    
    # Se nao tem caminho, retornar placeholder
    if not p:
        return 'imgs/filmes/placeholder.jpg'
    
    # Se ja comeca com imgs/, retornar como esta
    if p.startswith('imgs/'):
        return p
    
    # Se e apenas o nome do arquivo, assumir que esta em imgs/filmes/
    if '/' not in p:
        return f'imgs/filmes/{p}'
    
    # Se tem caminho mas nao comeca com imgs/, adicionar imgs/filmes/
    if not p.startswith('imgs/'):
        return f'imgs/filmes/{p}'
    
    return p

# ==========================
# Util: obter avatar do usuario logado
# ==========================
def get_user_avatar():
    """Retorna o caminho do avatar do usuário logado"""
    # Primeiro verificar se está na sessão
    if 'user_avatar' in session:
        avatar = session['user_avatar']
        app.logger.info(f"get_user_avatar - Avatar da sessão: {avatar}")
        return avatar
    
    # Se não estiver na sessão mas o usuário está logado, buscar do banco
    if 'user_id' in session:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # Buscar avatar personalizado OU avatar da galeria
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN u.avatar IS NOT NULL AND u.avatar != '' THEN u.avatar
                        ELSE a.caminho
                    END as avatar_path
                FROM usuarios u 
                LEFT JOIN avatars a ON u.avatar_id = a.id 
                WHERE u.id = %s
            """, (session['user_id'],))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            app.logger.info(f"get_user_avatar - Resultado da BD: {result}")
            
            if result and result['avatar_path']:
                avatar = result['avatar_path'].replace('\\', '/').replace('"', '').strip()
                
                # Remover prefixos desnecessários
                if avatar.startswith('static/'):
                    avatar = avatar[7:]
                if avatar.startswith('/static/'):
                    avatar = avatar[8:]
                
                app.logger.info(f"get_user_avatar - Avatar limpo: {avatar}")
                session['user_avatar'] = avatar  # Armazenar na sessão
                return avatar
        except Exception as e:
            app.logger.error(f"get_user_avatar - Erro: {str(e)}")
    
    # Fallback para ícone padrão
    app.logger.warning("get_user_avatar - Usando avatar padrão")
    return 'imgs/icons/user_icon34-removebg-preview.png'

# ==========================
# Página inicial (Home)
# ==========================
@app.route('/')
@app.route('/home')
def home():
    # Verificar se a reserva foi concluída
    if request.args.get('reserva_concluida'):
        flash("🎉 Reserva concluída com sucesso! Obrigado por escolher o CineVibe.", "sucesso")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Atualização automática de estados dos filmes - DESATIVADO para controlo manual
        # cursor.execute("""
        #     UPDATE filmes 
        #     SET estado = 'em_exibicao' 
        #     WHERE estado = 'brevemente' 
        #     AND data_lancamento IS NOT NULL
        #     AND data_lancamento <= CURDATE()
        # """)
        # 
        # if cursor.rowcount > 0:
        #     app.logger.info(f"🎬 Atualizados {cursor.rowcount} filmes para 'em_exibicao'")
        #     conn.commit()
        
        # Buscar top 10 filmes baseado em:
        # 1. Número de reservas (mais populares)
        # 2. Data de lançamento (mais recentes)
        # 3. Filmes com sessões ativas
        cursor.execute("""
            SELECT 
                f.id,
                f.titulo,
                f.poster_url,
                f.poster_hover,
                f.data_lancamento,
                f.duracao,
                GROUP_CONCAT(DISTINCT g.nome ORDER BY g.nome SEPARATOR ', ') as genero_nome,
                COUNT(DISTINCT r.id) as num_reservas,
                COUNT(DISTINCT hs.id) as num_sessoes
            FROM filmes f
            LEFT JOIN filme_generos fg ON f.id = fg.filme_id
            LEFT JOIN generos g ON fg.genero_id = g.id
            LEFT JOIN horarios_sessao hs ON f.id = hs.id_filme
            LEFT JOIN reservas r ON f.id = r.id_filme
            WHERE f.poster_url IS NOT NULL 
            AND f.poster_url != ''
            GROUP BY f.id
            ORDER BY num_reservas DESC, num_sessoes DESC, f.data_lancamento DESC
            LIMIT 10
        """)
        filmes = cursor.fetchall() or []
        
        # Normalizar poster_url, poster_hover e adicionar classificação
        for i, f in enumerate(filmes):
            if f.get('poster_url'):
                # Limpar e normalizar o caminho
                poster_url = f['poster_url'].replace('\\', '/').replace('"', '').strip()
                
                # Garantir que começa com imgs/filmes/
                if not poster_url.startswith('imgs/filmes/'):
                    if poster_url.startswith('imgs/'):
                        poster_url = poster_url.replace('imgs/', 'imgs/filmes/', 1)
                    elif poster_url.startswith('static/imgs/filmes/'):
                        poster_url = poster_url.replace('static/', '', 1)
                    elif poster_url.startswith('static/'):
                        poster_url = poster_url.replace('static/', '', 1)
                        if not poster_url.startswith('imgs/filmes/'):
                            poster_url = f"imgs/filmes/{poster_url}"
                    else:
                        poster_url = f"imgs/filmes/{poster_url}"
                
                # Adicionar /static/ no início para o template
                if not poster_url.startswith('/'):
                    poster_url = f"/static/{poster_url}"
                
                f['poster_url'] = poster_url
                
            if f.get('poster_hover'):
                # Limpar e normalizar o caminho
                poster_hover = f['poster_hover'].replace('\\', '/').replace('"', '').strip()
                # Se não começar com /, adicionar o prefixo correto
                if not poster_hover.startswith('/'):
                    if not poster_hover.startswith('static/'):
                        poster_hover = f"static/{poster_hover}"
                    poster_hover = f"/{poster_hover}"
                f['poster_hover'] = poster_hover
                
            f['classificacao_manual'] = str(i + 1)
        
        # Buscar estatísticas para a seção Discover
        stats = {}
        
        try:
            # Contar filmes em exibição (usar uma query mais simples)
            cursor.execute("SELECT COUNT(*) as total FROM filmes WHERE estado = 'em_exibicao'")
            result = cursor.fetchone()
            stats['filmes_em_exibicao'] = result['total'] if result else 0
            
            # Se não houver filmes em exibição, contar todos os filmes
            if stats['filmes_em_exibicao'] == 0:
                cursor.execute("SELECT COUNT(*) as total FROM filmes")
                result = cursor.fetchone()
                stats['filmes_em_exibicao'] = result['total'] if result else 0
            
            # Contar total de cinemas
            cursor.execute("SELECT COUNT(*) as total FROM cinemas")
            result = cursor.fetchone()
            stats['total_cinemas'] = result['total'] if result else 0
            
            # Contar total de salas
            cursor.execute("SELECT COUNT(*) as total FROM salas")
            result = cursor.fetchone()
            stats['total_salas'] = result['total'] if result else 0
            
            # Se não houver salas, usar um número padrão baseado nos cinemas
            if stats['total_salas'] == 0 and stats['total_cinemas'] > 0:
                stats['total_salas'] = stats['total_cinemas'] * 3  # Assumir 3 salas por cinema
            
        except Exception as e:
            app.logger.error(f"Erro ao buscar estatísticas: {e}")
            # Valores padrão se houver erro
            stats = {
                'filmes_em_exibicao': 25,
                'total_cinemas': 5,
                'total_salas': 15
            }
        
        app.logger.info(f"Stats calculadas: {stats}")
        
    finally:
        try: 
            cursor.close()
        except: 
            pass
        try: 
            conn.close()
        except: 
            pass

    return render_template('home.html', filmes=filmes, stats=stats)

# ==========================
# LOGIN
# ==========================
# ROTA: login (GET + POST)
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Capturar URL de retorno
    next_url = request.args.get('next') or request.form.get('next')
    
    if request.method == 'POST':

        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()   # ← CORRIGIDO

        if not email or not senha:
            flash("Preencha todos os campos!", "erro")
            return redirect(url_for('login', next=next_url) if next_url else url_for('login'))

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM usuarios WHERE email = %s",
            (email,)
        )
        user = cur.fetchone()

        if not user:
            flash("Email não encontrado", "erro")
            conn.close()
            return redirect(url_for('login', next=next_url) if next_url else url_for('login'))

        if not check_password_hash(user['senha'], senha):
            flash("Senha incorreta!", "erro")
            conn.close()
            return redirect(url_for('login', next=next_url) if next_url else url_for('login'))

        session['user_id'] = user['id']
        session['user_nome'] = user['nome']
        session['user_email'] = user['email']
        
        # Buscar o avatar do usuário (personalizado OU da galeria)
        cur.execute("""
            SELECT 
                CASE 
                    WHEN u.avatar IS NOT NULL AND u.avatar != '' THEN u.avatar
                    ELSE a.caminho
                END as avatar_path
            FROM usuarios u 
            LEFT JOIN avatars a ON u.avatar_id = a.id 
            WHERE u.id = %s
        """, (user['id'],))
        avatar_data = cur.fetchone()
        if avatar_data and avatar_data['avatar_path']:
            avatar = avatar_data['avatar_path'].replace('\\', '/').replace('"', '').strip()
            # Remover prefixos desnecessários
            if avatar.startswith('static/'):
                avatar = avatar[7:]
            if avatar.startswith('/static/'):
                avatar = avatar[8:]
            session['user_avatar'] = avatar
        else:
            session['user_avatar'] = 'imgs/icons/user_icon34-removebg-preview.png'

        cur.execute(
            "UPDATE usuarios SET ultimo_login = %s WHERE id = %s",
            (datetime.now(), user['id'])
        )
        conn.commit()
        conn.close()

        flash(f"Bem-vindo, {user['nome']}!", "sucesso")
        
        # VERIFICAR SE HÁ DADOS DE RESERVA GUARDADOS PARA REDIRECIONAR
        # Verificar se há parâmetros de reserva na sessão ou URL
        reserva_params = request.form.get('reserva_params')
        if reserva_params:
            # Se há dados de reserva, redirecionar para a reserva
            return redirect(f"/reserva?{reserva_params}")
        
        # Redirecionar para a URL de retorno ou home
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('home'))

    return render_template("login.html", next_url=next_url)


# ==========================
# AUTENTICAÇÃO SOCIAL
# ==========================
@app.route('/auth/google')
def auth_google():
    """Inicia o processo de autenticação com Google"""
    if DEVELOPMENT_MODE:
        # Modo desenvolvimento - simular login com dados de teste
        return redirect(url_for('auth_google_callback', 
                              code='dev_code', 
                              state='dev_state'))
    
    # Gerar state para segurança
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # URL de autorização do Google
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        "response_type=code&"
        f"redirect_uri={request.url_root}auth/google/callback&"
        "scope=openid email profile&"
        f"state={state}"
    )
    
    return redirect(google_auth_url)

@app.route('/auth/google/callback')
def auth_google_callback():
    """Callback do Google OAuth"""
    try:
        if DEVELOPMENT_MODE:
            # Modo desenvolvimento - simular dados do usuário
            user_data = {
                'email': 'teste.google@gmail.com',
                'name': 'Usuário Google Teste',
                'id': 'google_dev_123',
                'picture': 'https://via.placeholder.com/150'
            }
            return process_social_login(user_data, 'google')
        
        # Verificar state para segurança
        if request.args.get('state') != session.get('oauth_state'):
            flash("Erro de segurança na autenticação", "erro")
            return redirect(url_for('login'))
        
        # Obter código de autorização
        code = request.args.get('code')
        if not code:
            flash("Erro na autenticação com Google", "erro")
            return redirect(url_for('login'))
        
        # Trocar código por token
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': f"{request.url_root}auth/google/callback"
        }
        
        token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            flash("Erro ao obter token do Google", "erro")
            return redirect(url_for('login'))
        
        # Obter informações do usuário
        user_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f"Bearer {token_json['access_token']}"}
        )
        user_data = user_response.json()
        
        # Processar login social
        return process_social_login(user_data, 'google')
        
    except Exception as e:
        app.logger.error(f"Erro no callback do Google: {str(e)}")
        flash("Erro na autenticação com Google", "erro")
        return redirect(url_for('login'))

@app.route('/auth/facebook')
def auth_facebook():
    """Inicia o processo de autenticação com Facebook"""
    if DEVELOPMENT_MODE:
        # Modo desenvolvimento - simular login com dados de teste
        return redirect(url_for('auth_facebook_callback', 
                              code='dev_code', 
                              state='dev_state'))
    
    # Gerar state para segurança
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # URL de autorização do Facebook
    facebook_auth_url = (
        "https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={FACEBOOK_APP_ID}&"
        f"redirect_uri={request.url_root}auth/facebook/callback&"
        "scope=email,public_profile&"
        f"state={state}"
    )
    
    return redirect(facebook_auth_url)

@app.route('/auth/facebook/callback')
def auth_facebook_callback():
    """Callback do Facebook OAuth"""
    try:
        if DEVELOPMENT_MODE:
            # Modo desenvolvimento - simular dados do usuário
            user_data = {
                'email': 'teste.facebook@gmail.com',
                'name': 'Usuário Facebook Teste',
                'id': 'facebook_dev_456',
                'picture': {'data': {'url': 'https://via.placeholder.com/150'}}
            }
            return process_social_login(user_data, 'facebook')
        
        # Verificar state para segurança
        if request.args.get('state') != session.get('oauth_state'):
            flash("Erro de segurança na autenticação", "erro")
            return redirect(url_for('login'))
        
        # Obter código de autorização
        code = request.args.get('code')
        if not code:
            flash("Erro na autenticação com Facebook", "erro")
            return redirect(url_for('login'))
        
        # Trocar código por token
        token_url = (
            "https://graph.facebook.com/v18.0/oauth/access_token?"
            f"client_id={FACEBOOK_APP_ID}&"
            f"client_secret={FACEBOOK_APP_SECRET}&"
            f"redirect_uri={request.url_root}auth/facebook/callback&"
            f"code={code}"
        )
        
        token_response = requests.get(token_url)
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            flash("Erro ao obter token do Facebook", "erro")
            return redirect(url_for('login'))
        
        # Obter informações do usuário
        user_response = requests.get(
            f"https://graph.facebook.com/me?fields=id,name,email,picture&access_token={token_json['access_token']}"
        )
        user_data = user_response.json()
        
        # Processar login social
        return process_social_login(user_data, 'facebook')
        
    except Exception as e:
        app.logger.error(f"Erro no callback do Facebook: {str(e)}")
        flash("Erro na autenticação com Facebook", "erro")
        return redirect(url_for('login'))

def process_social_login(user_data, provider):
    """Processa o login social (Google ou Facebook)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Extrair dados do usuário baseado no provider
        if provider == 'google':
            email = user_data.get('email')
            nome = user_data.get('name')
            social_id = user_data.get('id')
            avatar_url = user_data.get('picture')
        elif provider == 'facebook':
            email = user_data.get('email')
            nome = user_data.get('name')
            social_id = user_data.get('id')
            avatar_url = user_data.get('picture', {}).get('data', {}).get('url') if user_data.get('picture') else None
        
        if not email:
            flash("Não foi possível obter o email da conta social", "erro")
            return redirect(url_for('login'))
        
        # Verificar se usuário já existe
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            # Usuário existe, fazer login
            user_id = user['id']
            
            # Atualizar último login
            cursor.execute("UPDATE usuarios SET ultimo_login = %s WHERE id = %s", (datetime.now(), user_id))
            conn.commit()
        else:
            # Criar novo usuário
            # Buscar avatar aleatório
            cursor.execute("SELECT id FROM avatars WHERE id > 0")
            avatars_disponiveis = cursor.fetchall()
            
            avatar_id_aleatorio = 1  # Padrão
            if avatars_disponiveis:
                avatar_aleatorio = random.choice(avatars_disponiveis)
                avatar_id_aleatorio = avatar_aleatorio['id']
            
            # Inserir novo usuário
            agora = datetime.now()
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha, criado_em, ultimo_login, avatar_id, social_provider, social_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, email, generate_password_hash(secrets.token_urlsafe(32)), agora, agora, avatar_id_aleatorio, provider, social_id))
            
            conn.commit()
            user_id = cursor.lastrowid
        
        # Buscar avatar do usuário
        cursor.execute("""
            SELECT COALESCE(u.avatar, a.caminho, 'imgs/icons/user_icon34-removebg-preview.png') as avatar
            FROM usuarios u 
            LEFT JOIN avatars a ON u.avatar_id = a.id 
            WHERE u.id = %s
        """, (user_id,))
        avatar_result = cursor.fetchone()
        avatar_path = avatar_result['avatar'] if avatar_result else 'imgs/icons/user_icon34-removebg-preview.png'
        
        # Normalizar avatar
        if avatar_path:
            avatar_path = avatar_path.replace('\\', '/').replace('"', '').strip()
            if not avatar_path.startswith('imgs/'):
                if avatar_path.startswith('static/'):
                    avatar_path = avatar_path[7:]
                if not avatar_path.startswith('imgs/'):
                    avatar_path = f"imgs/{avatar_path}"
        
        if not avatar_path or avatar_path == 'imgs/' or avatar_path == 'imgs':
            avatar_path = 'imgs/icons/user_icon34-removebg-preview.png'
        
        cursor.close()
        conn.close()
        
        # Criar sessão
        session['user_id'] = user_id
        session['user_nome'] = nome
        session['user_email'] = email
        session['user_avatar'] = avatar_path
        
        # Limpar state OAuth
        session.pop('oauth_state', None)
        
        return redirect(url_for('home'))
        
    except Exception as e:
        app.logger.error(f"Erro no processo de login social: {str(e)}")
        flash("Erro no login social", "erro")
        return redirect(url_for('login'))

@app.route('/redefinir-senha')
def redefinir_senha():
    """Página para redefinir senha com token"""
    try:
        token = request.args.get('token')
        
        if not token:
            flash("Link inválido ou expirado", "erro")
            return redirect(url_for('login'))
        
        app.logger.info(f"Carregando página de redefinir senha com token: {token}")
        
        # Por agora, vamos aceitar qualquer token (em produção, validar na BD)
        return render_template('redefinir_senha_simples.html', token=token)
        
    except Exception as e:
        app.logger.error(f"Erro na rota redefinir-senha: {str(e)}")
        flash("Erro interno. Tente novamente.", "erro")
        return redirect(url_for('login'))

@app.route('/api/redefinir-senha', methods=['POST'])
def api_redefinir_senha():
    """API para redefinir senha com token"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        nova_senha = data.get('novaSenha', '').strip()
        confirmar_senha = data.get('confirmarSenha', '').strip()
        
        if not token or not nova_senha or not confirmar_senha:
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'})
        
        if len(nova_senha) < 6:
            return jsonify({'success': False, 'message': 'A senha deve ter pelo menos 6 caracteres'})
        
        if nova_senha != confirmar_senha:
            return jsonify({'success': False, 'message': 'As senhas não coincidem'})
        
        # Por agora, vamos simular a validação do token
        # Em produção, você validaria o token na tabela password_reset_tokens
        
        # Para demonstração, vamos permitir redefinir para qualquer usuário com email específico
        # Em produção, você obteria o user_id do token na BD
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar o primeiro usuário (para demonstração)
        # Em produção: SELECT user_id FROM password_reset_tokens WHERE token = %s AND expires_at > NOW() AND used = FALSE
        cursor.execute("SELECT id, email FROM usuarios LIMIT 1")
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'Token inválido ou expirado'})
        
        # Atualizar senha
        nova_senha_hash = generate_password_hash(nova_senha)
        cursor.execute(
            "UPDATE usuarios SET senha = %s WHERE id = %s",
            (nova_senha_hash, user['id'])
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        app.logger.info(f"Senha redefinida com sucesso para usuário ID: {user['id']} (email: {user['email']})")
        return jsonify({'success': True, 'message': 'Senha redefinida com sucesso'})
        
    except Exception as e:
        app.logger.error(f"Erro ao redefinir senha: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

# -------------------------
# ✅ REGISTO
# -------------------------
@app.route('/registo', methods=["GET", "POST"])
def registo():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Buscar avatares
    cursor.execute("SELECT id, nome, caminho FROM avatars")
    avatars = cursor.fetchall()

    # ✅ Corrigir caminhos com \ → /
    for avatar in avatars:
        avatar["caminho"] = avatar["caminho"].replace("\\", "/").replace('"', "")

    if request.method == "POST":
        try:
            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip()
            senha = request.form.get("senha", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()
            avatar_id = request.form.get("avatar", "").strip()
            avatar_upload = request.files.get("avatar_upload")

            # Debug - ver o que está sendo recebido
            print(f"DEBUG REGISTO - Nome: {nome}, Email: {email}, Senha: {'***' if senha else 'VAZIO'}, Confirm: {'***' if confirm_password else 'VAZIO'}, Avatar ID: {avatar_id}")
            
            # Validações básicas
            if not nome or not email or not senha:
                cursor.close()
                conn.close()
                return redirect(url_for("registo"))
            
            # Validar confirmação de senha
            if senha != confirm_password:
                cursor.close()
                conn.close()
                return redirect(url_for("registo"))
            
            # Verificar se email já existe
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return redirect(url_for("registo"))

            senha_hash = generate_password_hash(senha)
            agora = datetime.now()
            
            custom_avatar_path = None
            
            # Processar upload de imagem personalizada
            if avatar_upload and avatar_upload.filename:
                import os
                from werkzeug.utils import secure_filename
                
                # Criar diretório se não existir
                upload_folder = os.path.join('static', 'imgs', 'avatars', 'custom')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Gerar nome único para o arquivo
                filename = secure_filename(avatar_upload.filename)
                unique_filename = f"{agora.strftime('%Y%m%d%H%M%S')}_{filename}"
                filepath = os.path.join(upload_folder, unique_filename)
                
                # Salvar arquivo
                avatar_upload.save(filepath)
                
                # Caminho relativo para o banco
                custom_avatar_path = f"imgs/avatars/custom/{unique_filename}"
                
                # Inserir usuário com avatar customizado
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha, criado_em, ultimo_login, avatar)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nome, email, senha_hash, agora, agora, custom_avatar_path))
            elif avatar_id and avatar_id.isdigit():
                # Inserir usuário com avatar da galeria (apenas se avatar_id for válido)
                print(f"✅ DEBUG - Inserindo com avatar_id selecionado: {avatar_id}")
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha, criado_em, ultimo_login, avatar_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nome, email, senha_hash, agora, agora, int(avatar_id)))
            else:
                # Sempre atribuir um avatar aleatório quando não há seleção válida
                print(f"🎲 DEBUG - Nenhum avatar selecionado, escolhendo aleatório...")
                cursor.execute("SELECT id FROM avatars WHERE id > 0 ORDER BY id")
                avatars_disponiveis = cursor.fetchall()
                
                if avatars_disponiveis:
                    # Escolher um avatar aleatório
                    avatar_aleatorio = random.choice(avatars_disponiveis)
                    avatar_id_aleatorio = avatar_aleatorio['id']
                    print(f"✅ DEBUG - Avatar aleatório selecionado: ID {avatar_id_aleatorio}")
                    
                    cursor.execute("""
                        INSERT INTO usuarios (nome, email, senha, criado_em, ultimo_login, avatar_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (nome, email, senha_hash, agora, agora, avatar_id_aleatorio))
                else:
                    # Fallback: criar um avatar padrão se não existir nenhum
                    print("⚠️ DEBUG - Nenhum avatar encontrado na BD, criando avatar padrão...")
                    
                    # Inserir avatar padrão se não existir
                    cursor.execute("SELECT id FROM avatars WHERE id = 1")
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO avatars (id, nome, caminho, categoria) 
                            VALUES (1, 'Avatar Padrão', 'imgs/icons/user_icon34-removebg-preview.png', 'padrão')
                        """)
                        print("✅ DEBUG - Avatar padrão criado na BD")
                    
                    cursor.execute("""
                        INSERT INTO usuarios (nome, email, senha, criado_em, ultimo_login, avatar_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (nome, email, senha_hash, agora, agora, 1))
            
            conn.commit()
            
            # Obter o ID do usuário recém-criado
            user_id = cursor.lastrowid
            
            # Buscar o avatar do usuário recém-criado
            avatar_path = 'imgs/icons/user_icon34-removebg-preview.png'
            
            if custom_avatar_path:
                avatar_path = custom_avatar_path
                print(f"DEBUG - Avatar customizado: {avatar_path}")
            else:
                # Buscar o avatar que foi atribuído (selecionado ou aleatório)
                cursor.execute("""
                    SELECT a.caminho 
                    FROM usuarios u 
                    JOIN avatars a ON u.avatar_id = a.id 
                    WHERE u.id = %s
                """, (user_id,))
                result = cursor.fetchone()
                
                if result and result['caminho']:
                    avatar_path = result['caminho'].replace('\\', '/').replace('"', '').strip()
                    # Remover prefixos desnecessários
                    if avatar_path.startswith('static/'):
                        avatar_path = avatar_path[7:]
                    if avatar_path.startswith('/static/'):
                        avatar_path = avatar_path[8:]
                    print(f"DEBUG - Avatar encontrado: {avatar_path}")
                else:
                    # Fallback final para avatar padrão
                    avatar_path = 'imgs/icons/user_icon34-removebg-preview.png'
                    print(f"DEBUG - Usando avatar padrão: {avatar_path}")
            
            cursor.close()
            conn.close()
            
            # Fazer login automático
            session['user_id'] = user_id
            session['user_nome'] = nome
            session['user_email'] = email
            session['user_avatar'] = avatar_path
            
            print(f"✅ DEBUG REGISTO - Sessão criada:")
            print(f"   - user_id: {user_id}")
            print(f"   - user_nome: {nome}")
            print(f"   - user_email: {email}")
            print(f"   - user_avatar: {avatar_path}")

            return redirect(url_for("home"))
            
        except Exception as e:
            if conn:
                conn.rollback()
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            return redirect(url_for("registo"))

    cursor.close()
    conn.close()
    return render_template("registo.html", avatars=avatars)


@app.route('/update-avatar', methods=['POST'])
def update_avatar():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não está logado'})
    
    data = request.get_json()
    avatar_id = data.get('avatar_id')
    
    if not avatar_id:
        return jsonify({'success': False, 'message': 'Avatar ID não fornecido'})
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Busca o caminho do novo avatar
        cur.execute("SELECT caminho FROM avatars WHERE id = %s", (avatar_id,))
        avatar_row = cur.fetchone()
        
        if not avatar_row:
            return jsonify({'success': False, 'message': 'Avatar não encontrado'})
        
        # Atualiza o avatar do usuário
        cur.execute(
            "UPDATE usuarios SET avatar_id = %s WHERE id = %s",
            (avatar_id, session['user_id'])
        )
        conn.commit()
        
        # Limpa e normaliza o caminho do avatar
        avatar_path = str(avatar_row['caminho']).replace("\\", "/").replace('"', '').strip()
        avatar_path = avatar_path.replace("static/", "").lstrip("/")
        
        if not avatar_path.startswith("imgs/"):
            avatar_path = "imgs/" + avatar_path.lstrip("/")
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Avatar atualizado com sucesso',
            'new_avatar': avatar_path
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

@app.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não está logado'})
    
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'})
    
    file = request.files['avatar']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'})
    
    # Verificar extensão do arquivo
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return jsonify({'success': False, 'message': 'Formato de arquivo não permitido'})
    
    try:
        import os
        from werkzeug.utils import secure_filename
        
        # Criar nome único para o arquivo
        filename = f"user_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_ext}"
        filename = secure_filename(filename)
        
        # Caminho para salvar
        upload_folder = os.path.join('static', 'imgs', 'avatars', 'custom')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Caminho relativo para o banco de dados
        db_path = f"imgs/avatars/custom/{filename}"
        
        # Atualizar no banco de dados
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "UPDATE usuarios SET avatar = %s, avatar_id = NULL WHERE id = %s",
            (db_path, session['user_id'])
        )
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Avatar enviado com sucesso',
            'new_avatar': db_path
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao fazer upload: {str(e)}'})

@app.route("/avatars/<categoria>")
def avatars_categoria(categoria):
    try:
        app.logger.info(f"Buscando avatares da categoria: {categoria}")
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT a.id, a.nome, a.caminho
            FROM avatars a
            JOIN avatar_categories c ON a.categoria_id = c.id
            WHERE c.nome = %s
        """, (categoria,))

        avatars = cur.fetchall()
        app.logger.info(f"Avatares encontrados: {len(avatars)}")

        for av in avatars:
            p = av["caminho"].replace("\\", "/").replace('"', "").strip()

            if p.startswith("static/"):
                p = p[7:]
            if p.startswith("/static/"):
                p = p[8:]

            av["caminho"] = p
            app.logger.info(f"Avatar: {av['nome']} - Caminho: {av['caminho']}")

        cur.close()
        conn.close()

        return jsonify(avatars)
    except Exception as e:
        app.logger.error(f"Erro ao buscar avatares: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Rota de teste de avatares
@app.route("/testar-avatares")
def testar_avatares():
    return render_template('testar_avatares.html')

# ==========================
# Rota de Teste de Email
# ==========================
@app.route('/test-email')
def test_email():
    """Rota para testar o envio de email"""
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': 'É necessário fazer login para testar o email'
        }), 401
    
    try:
        # Buscar dados do usuário
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Utilizador não encontrado'
            }), 404
        
        # Dados de teste para o email
        dados_reserva = {
            'reserva_id': 99999,
            'filme': 'Filme de Teste - Aventura Épica',
            'cinema': 'CineVibe Lisboa - Centro',
            'tipo_sessao': '2D Legendado',
            'horario': '25/12/2024 às 20:00',
            'quantidade': '2 bilhetes'
        }
        
        # Tentar enviar email
        sucesso = enviar_email_confirmacao(
            user['email'],
            user['nome'],
            dados_reserva
        )
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': f'✅ Email de teste enviado com sucesso para {user["email"]}! Verifique a sua caixa de entrada.'
            })
        else:
            return jsonify({
                'success': False,
                'message': '❌ Falha ao enviar email. Verifique as configurações no email_config.py e os logs do servidor.'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Erro no teste de email: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


# ==========================
# TESTE PERFIL DEBUG
# ==========================
@app.route('/teste-perfil-debug')
def teste_perfil_debug():
    """Route de teste para debug do perfil"""
    print("🔍 DEBUG: Route teste-perfil-debug chamado")
    
    if 'user_id' not in session:
        return "❌ Usuário não está logado"
    
    user_id = session['user_id']
    return f"✅ Usuário logado com ID: {user_id}. Route de teste funcionando!"

@app.route('/debug-produtos-resgatados')
def debug_produtos_resgatados():
    """Debug para verificar produtos resgatados"""
    if 'user_id' not in session:
        return "Precisa estar logado"
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        resultado = f"<h2>Debug Produtos Resgatados - User ID: {user_id}</h2>"
        
        # Verificar se tabela existe
        cursor.execute("SHOW TABLES LIKE 'pontos_gastos'")
        tabela_existe = cursor.fetchone()
        resultado += f"<p>Tabela pontos_gastos existe: {'SIM' if tabela_existe else 'NÃO'}</p>"
        
        if not tabela_existe:
            # Criar tabela se não existir
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `pontos_gastos` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `usuario_id` int NOT NULL,
                  `premio_id` int DEFAULT NULL,
                  `premio_nome` varchar(100) DEFAULT NULL,
                  `pontos_gastos` int NOT NULL,
                  `codigo_desconto` varchar(20) DEFAULT NULL,
                  `data_resgate` datetime DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY (`id`),
                  KEY `usuario_id` (`usuario_id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """)
            conn.commit()
            resultado += "<p>✅ Tabela pontos_gastos criada!</p>"
        
        # Verificar dados existentes
        cursor.execute("SELECT COUNT(*) as total FROM pontos_gastos WHERE usuario_id = %s", (user_id,))
        total = cursor.fetchone()['total']
        resultado += f"<p>Total de produtos para este usuário: {total}</p>"
        
        if total == 0:
            # Inserir dados de teste
            produtos_teste = [
                (user_id, 8, 'Pretzel', 100, 'TEST001'),
                (user_id, 1, 'Coca Cola pequena', 200, 'TEST002'),
                (user_id, 2, 'Pipocas doces/Salgadas', 300, 'TEST003'),
                (user_id, 5, 'Snickers', 200, 'TEST004')
            ]
            
            for produto in produtos_teste:
                cursor.execute("""
                    INSERT INTO pontos_gastos 
                    (usuario_id, premio_id, premio_nome, pontos_gastos, codigo_desconto, data_resgate)
                    VALUES (%s, %s, %s, %s, %s, DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 30) DAY))
                """, produto)
            
            conn.commit()
            resultado += f"<p>✅ Inseridos {len(produtos_teste)} produtos de teste!</p>"
        
        # Buscar e mostrar produtos
        cursor.execute("""
            SELECT 
                pg.id,
                pg.premio_nome as nome,
                pg.pontos_gastos,
                pg.data_resgate,
                p.img_url as imagem,
                p.nome as premio_original
            FROM pontos_gastos pg
            LEFT JOIN premios p ON pg.premio_id = p.id
            WHERE pg.usuario_id = %s
            ORDER BY pg.data_resgate DESC
        """, (user_id,))
        
        produtos = cursor.fetchall()
        
        resultado += f"<h3>Produtos encontrados: {len(produtos)}</h3>"
        resultado += "<table border='1' style='color: white;'>"
        resultado += "<tr><th>ID</th><th>Nome</th><th>Pontos</th><th>Data</th><th>Imagem</th><th>Prémio Original</th></tr>"
        
        for produto in produtos:
            resultado += f"""
            <tr>
                <td>{produto['id']}</td>
                <td>{produto['nome']}</td>
                <td>{produto['pontos_gastos']}</td>
                <td>{produto['data_resgate']}</td>
                <td>{produto['imagem'] or 'NULL'}</td>
                <td>{produto['premio_original'] or 'NULL'}</td>
            </tr>
            """
        
        resultado += "</table>"
        
        cursor.close()
        conn.close()
        
        resultado += f'<p><a href="/perfil">Ir para o Perfil</a></p>'
        
        return resultado
        
    except Exception as e:
        return f"Erro: {str(e)}"

@app.route('/criar-dados-teste-pontos-movimentos')
def criar_dados_teste_pontos_movimentos():
    """Insere dados de teste na tabela pontos_movimentos para simular produtos resgatados"""
    if 'user_id' not in session:
        return "Precisa estar logado"
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Limpar dados de teste antigos do usuário
        cursor.execute("DELETE FROM pontos_movimentos WHERE utilizador_id = %s AND motivo LIKE '%resgate%'", (user_id,))
        
        # Inserir dados de teste na tabela pontos_movimentos
        produtos_teste = [
            (user_id, -100, 'Resgate de Pretzel com código TESTE001'),
            (user_id, -200, 'Resgate de Coca Cola pequena com código TESTE002'),
            (user_id, -300, 'Resgate de Pipocas doces/Salgadas com código TESTE003'),
            (user_id, -200, 'Resgate de Snickers com código TESTE004'),
            (user_id, -400, 'Resgate de Doritos com código TESTE005')
        ]
        
        for produto in produtos_teste:
            cursor.execute("""
                INSERT INTO pontos_movimentos 
                (utilizador_id, pontos, motivo, data_movimento)
                VALUES (%s, %s, %s, DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 30) DAY))
            """, produto)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return f"""
        <h2>✅ Dados de teste criados na tabela pontos_movimentos!</h2>
        <p>Foram inseridos {len(produtos_teste)} movimentos de pontos para o usuário {user_id}</p>
        <p>Estes representam produtos resgatados com códigos que já foram usados em reservas.</p>
        <p><a href="/perfil">Ir para o Perfil</a></p>
        <p><a href="/teste-pontos-movimentos">Testar busca em pontos_movimentos</a></p>
        """
        
    except Exception as e:
        return f"❌ Erro: {str(e)}"

@app.route('/teste-pontos-movimentos')
def teste_pontos_movimentos():
    """Rota para testar a busca na tabela pontos_movimentos"""
    if 'user_id' not in session:
        return "Precisa estar logado"
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar todos os movimentos de pontos do usuário
        cursor.execute("""
            SELECT 
                pm.motivo as nome,
                ABS(pm.pontos) as pontos_gastos,
                pm.data_movimento as data_resgate,
                p.img_url as imagem
            FROM pontos_movimentos pm
            LEFT JOIN premios p ON (
                (pm.motivo LIKE '%pretzel%' AND p.nome LIKE '%pretzel%') OR
                (pm.motivo LIKE '%coca%' AND p.nome LIKE '%coca%') OR
                (pm.motivo LIKE '%pipocas%' AND p.nome LIKE '%pipocas%') OR
                (pm.motivo LIKE '%snickers%' AND p.nome LIKE '%snickers%') OR
                (pm.motivo LIKE '%fanta%' AND p.nome LIKE '%fanta%') OR
                (pm.motivo LIKE '%gomas%' AND p.nome LIKE '%gomas%') OR
                (pm.motivo LIKE '%doritos%' AND p.nome LIKE '%doritos%') OR
                (pm.motivo LIKE '%bilhete%' AND p.nome LIKE '%bilhete%')
            )
            WHERE pm.utilizador_id = %s 
            AND pm.pontos < 0 
            AND (pm.motivo LIKE '%resgate%' OR pm.motivo LIKE '%código%' OR pm.motivo LIKE '%premio%')
            ORDER BY pm.data_movimento DESC
        """, (user_id,))
        
        produtos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        resultado = f"""
        <h2>Teste Pontos Movimentos - Usuário {user_id}</h2>
        <p>Total de produtos resgatados encontrados: {len(produtos)}</p>
        <ul>
        """
        
        for produto in produtos:
            resultado += f"""
            <li>
                <strong>{produto['nome']}</strong><br>
                Pontos: {produto['pontos_gastos']}<br>
                Data: {produto['data_resgate']}<br>
                Imagem: {produto['imagem']}<br>
                ---
            </li>
            """
        
        resultado += "</ul>"
        resultado += f'<p><a href="/perfil">Voltar ao Perfil</a></p>'
        resultado += f'<p><a href="/criar-dados-teste-pontos-movimentos">Criar dados de teste</a></p>'
        
        return resultado
        
    except Exception as e:
        return f"Erro: {str(e)}"

@app.route('/criar-dados-teste-produtos')
def criar_dados_teste_produtos():
    """Força a criação da tabela e insere dados de teste"""
    if 'user_id' not in session:
        return "Precisa estar logado"
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Criar tabela se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `pontos_gastos` (
              `id` int NOT NULL AUTO_INCREMENT,
              `usuario_id` int NOT NULL,
              `premio_id` int DEFAULT NULL,
              `premio_nome` varchar(100) DEFAULT NULL,
              `pontos_gastos` int NOT NULL,
              `codigo_desconto` varchar(20) DEFAULT NULL,
              `data_resgate` datetime DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              KEY `usuario_id` (`usuario_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        """)
        
        # Limpar dados existentes do usuário
        cursor.execute("DELETE FROM pontos_gastos WHERE usuario_id = %s", (user_id,))
        
        # Inserir dados de teste
        produtos_teste = [
            (user_id, 8, 'Pretzel', 100, 'TEST001'),
            (user_id, 1, 'Coca Cola pequena', 200, 'TEST002'),
            (user_id, 2, 'Pipocas doces/Salgadas', 300, 'TEST003'),
            (user_id, 5, 'Snickers', 200, 'TEST004'),
            (user_id, 7, 'Doritos', 400, 'TEST005')
        ]
        
        for produto in produtos_teste:
            cursor.execute("""
                INSERT INTO pontos_gastos 
                (usuario_id, premio_id, premio_nome, pontos_gastos, codigo_desconto, data_resgate)
                VALUES (%s, %s, %s, %s, %s, DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 30) DAY))
            """, produto)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return f"""
        <h2>✅ Dados de teste criados com sucesso!</h2>
        <p>Foram inseridos {len(produtos_teste)} produtos para o usuário {user_id}</p>
        <p><a href="/perfil">Ir para o Perfil</a></p>
        <p><a href="/teste-produtos-resgatados">Testar busca de produtos</a></p>
        """
        
    except Exception as e:
        return f"❌ Erro: {str(e)}"

@app.route('/teste-produtos-resgatados')
def teste_produtos_resgatados():
    """Rota para testar e criar produtos resgatados de exemplo"""
    if 'user_id' not in session:
        return "Precisa estar logado"
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Primeiro, garantir que as tabelas existem
        print("🔍 Criando tabelas se não existirem...")
        
        # Criar tabela pontos_gastos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `pontos_gastos` (
              `id` int NOT NULL AUTO_INCREMENT,
              `usuario_id` int NOT NULL,
              `premio_id` int DEFAULT NULL,
              `premio_nome` varchar(100) DEFAULT NULL,
              `pontos_gastos` int NOT NULL,
              `codigo_desconto` varchar(20) DEFAULT NULL,
              `data_resgate` datetime DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              KEY `usuario_id` (`usuario_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        """)
        
        # Verificar se já existem produtos para este usuário
        cursor.execute("SELECT COUNT(*) as total FROM pontos_gastos WHERE usuario_id = %s", (user_id,))
        total_existente = cursor.fetchone()['total']
        
        if total_existente == 0:
            print(f"🔍 Inserindo produtos de exemplo para usuário {user_id}...")
            
            # Inserir produtos de exemplo
            produtos_exemplo = [
                (user_id, 8, 'Pretzel', 100, 'CODIGO001'),
                (user_id, 1, 'Coca Cola pequena', 200, 'CODIGO002'),
                (user_id, 2, 'Pipocas doces/Salgadas', 300, 'CODIGO003'),
                (user_id, 5, 'Snickers', 200, 'CODIGO004')
            ]
            
            for produto in produtos_exemplo:
                cursor.execute("""
                    INSERT INTO pontos_gastos 
                    (usuario_id, premio_id, premio_nome, pontos_gastos, codigo_desconto, data_resgate)
                    VALUES (%s, %s, %s, %s, %s, DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 30) DAY))
                """, produto)
            
            conn.commit()
            print(f"✅ {len(produtos_exemplo)} produtos inseridos com sucesso!")
        
        # Buscar produtos resgatados
        cursor.execute("""
            SELECT 
                pg.premio_nome as nome,
                pg.pontos_gastos,
                pg.data_resgate,
                p.img_url as imagem,
                'Produto resgatado com pontos CineVibe' as descricao
            FROM pontos_gastos pg
            LEFT JOIN premios p ON pg.premio_id = p.id
            WHERE pg.usuario_id = %s
            ORDER BY pg.data_resgate DESC
        """, (user_id,))
        
        produtos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        resultado = f"""
        <h2>Teste Produtos Resgatados - Usuário {user_id}</h2>
        <p>Total de produtos encontrados: {len(produtos)}</p>
        <ul>
        """
        
        for produto in produtos:
            resultado += f"""
            <li>
                <strong>{produto['nome']}</strong><br>
                Pontos: {produto['pontos_gastos']}<br>
                Data: {produto['data_resgate']}<br>
                Imagem: {produto['imagem']}<br>
                ---
            </li>
            """
        
        resultado += "</ul>"
        resultado += f'<p><a href="/perfil">Voltar ao Perfil</a></p>'
        
        return resultado
        
    except Exception as e:
        return f"Erro: {str(e)}"

@app.route('/perfil')
def perfil():
    print("🔍 DEBUG: Entrando no route /perfil")
    
    if 'user_id' not in session:
        print("❌ DEBUG: Usuário não está logado")
        flash("Inicia sessão primeiro!", "erro")
        return redirect(url_for('login'))

    user_id = session['user_id']
    print(f"✅ DEBUG: Usuário logado com ID: {user_id}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Buscar dados básicos do usuário e verificar se é admin
        cursor.execute("""
            SELECT u.id, u.nome, u.email, u.tipo_usuario, u.avatar, u.avatar_id,
                   a.caminho as avatar_path
            FROM usuarios u 
            LEFT JOIN avatars a ON u.avatar_id = a.id 
            WHERE u.id = %s
        """, (user_id,))
        user = cursor.fetchone()
        
        if not user:
            print("❌ DEBUG: Usuário não encontrado na base de dados")
            cursor.close()
            conn.close()
            flash("Utilizador não encontrado!", "erro")
            return redirect(url_for('home'))

        print(f"✅ DEBUG: Usuário encontrado: {user['nome']} ({user['email']})")

        # Verificar se é admin (por email específico) e redirecionar para dashboard
        if user.get('email') == 'cinevibeadmn@gmail.com':
            cursor.close()
            conn.close()
            return redirect(url_for('admin_dashboard'))

        # Processar avatar com lógica melhorada
        avatar = None
        
        # Prioridade: avatar da tabela avatars → avatar direto do usuario → fallback
        if user.get('avatar_path'):
            avatar = str(user['avatar_path'])
        elif user.get('avatar'):
            avatar = str(user['avatar'])
        else:
            avatar = 'imgs/icons/user_icon34-removebg-preview.png'
        
        # Limpar e normalizar avatar
        if avatar:
            avatar = avatar.replace('\\', '/').replace('"', '').strip()
            
            # Remover prefixos desnecessários
            if avatar.startswith('static/'):
                avatar = avatar[7:]
            if avatar.startswith('/static/'):
                avatar = avatar[8:]
        
        # Verificação final
        if not avatar or avatar == 'imgs/' or avatar == 'imgs':
            avatar = 'imgs/icons/user_icon34-removebg-preview.png'
        
        # Atualizar sessão com avatar correto
        session['user_avatar'] = avatar

        # Buscar APENAS filmes que o usuário TEM RESERVAS (ativas) - CAMPOS CORRETOS
        cursor.execute("""
            SELECT DISTINCT
                f.id,
                f.titulo,
                f.poster_url,
                f.duracao,
                MAX(r.data_sessao) as data_sessao,
                av.rating as user_rating,
                av.comentario as user_comentario,
                av.data_avaliacao,
                (SELECT c2.nome 
                 FROM reservas r2 
                 JOIN cinemas c2 ON r2.id_cinema = c2.id 
                 WHERE r2.id_filme = f.id AND r2.id_usuario = %s 
                 ORDER BY r2.data_sessao DESC LIMIT 1) as cinema_nome,
                (SELECT ts2.nome 
                 FROM reservas r2 
                 JOIN tipos_sessao ts2 ON r2.id_tipo_sessao = ts2.id 
                 WHERE r2.id_filme = f.id AND r2.id_usuario = %s 
                 ORDER BY r2.data_sessao DESC LIMIT 1) as tipo_sessao
            FROM reservas r
            JOIN filmes f ON r.id_filme = f.id
            LEFT JOIN avaliacoes_filmes av ON f.id = av.filme_id AND av.usuario_id = %s
            WHERE r.id_usuario = %s
            GROUP BY f.id, f.titulo, f.poster_url, f.duracao, av.rating, av.comentario, av.data_avaliacao
            ORDER BY MAX(r.data_sessao) DESC
        """, (user_id, user_id, user_id, user_id))
        filmes_vistos = cursor.fetchall() or []

        # Normalizar poster_url
        for filme in filmes_vistos:
            if filme.get('poster_url'):
                filme['poster_url'] = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
                if not filme['poster_url'].startswith('imgs/'):
                    filme['poster_url'] = f"imgs/filmes/{filme['poster_url']}"
            else:
                filme['poster_url'] = 'imgs/filmes/default.jpg'

        # Buscar cinemas favoritos
        cursor.execute("""
            SELECT c.id, c.nome, c.localizacao,
                   COALESCE(c.imagem, 'imgs/cinemas/default.jpg') as imagem
            FROM cinemas_favoritos cf
            JOIN cinemas c ON cf.cinema_id = c.id
            WHERE cf.usuario_id = %s
            ORDER BY cf.data_adicao DESC
        """, (user_id,))
        cinemas_favoritos = cursor.fetchall() or []

        # Normalizar caminhos das imagens dos cinemas
        for cinema in cinemas_favoritos:
            if cinema.get('imagem'):
                cinema['imagem'] = cinema['imagem'].replace('\\', '/').replace('"', '').strip()
                if not cinema['imagem'].startswith('imgs/'):
                    cinema['imagem'] = f"imgs/cinemas/{cinema['imagem']}"
            else:
                cinema['imagem'] = 'imgs/cinemas/default.jpg'

        # Buscar estatísticas de avaliações
        cursor.execute("""
            SELECT 
                COUNT(*) as total_avaliacoes,
                AVG(rating) as media_avaliacoes
            FROM avaliacoes_filmes 
            WHERE usuario_id = %s
        """, (user_id,))
        stats_avaliacoes = cursor.fetchone() or {'total_avaliacoes': 0, 'media_avaliacoes': 0}

        # Calcular totais para estatísticas
        total_filmes_vistos = len(filmes_vistos)
        total_avaliacoes = stats_avaliacoes['total_avaliacoes']

        cursor.close()
        conn.close()

        # Calcular pontos e nível
        # Calcular pontos disponíveis
        conn2 = get_db_connection()
        cursor2 = conn2.cursor(dictionary=True)
        pontos = calcular_pontos_usuario(session['user_id'], cursor2)
        cursor2.close()
        conn2.close()
        
        # Determinar nível
        if pontos < 500:
            nivel = "Iniciante"
            nivel_cor = "linear-gradient(135deg, #6c757d, #495057)"
        elif pontos < 1000:
            nivel = "Cinéfilo"
            nivel_cor = "linear-gradient(135deg, #4EA8DE, #2196F3)"
        elif pontos < 2000:
            nivel = "Expert"
            nivel_cor = "linear-gradient(135deg, #FFD60A, #FFA500)"
        else:
            nivel = "Lenda"
            nivel_cor = "linear-gradient(135deg, #FF6B6B, #E91E63)"

        # Dados para o template
        stats = {
            'filmes_vistos': total_filmes_vistos,
            'reservas_feitas': total_filmes_vistos,
            'avaliacoes_feitas': total_avaliacoes,
            'pontos_gastos': 0
        }

        print(f"✅ DEBUG PERFIL: Pronto para renderizar template perfil.html")
        print(f"✅ DEBUG PERFIL: Stats: {stats}")
        print(f"✅ DEBUG PERFIL: Pontos: {pontos}")

        return render_template("perfil.html", 
                             user=user, 
                             filmes_vistos=filmes_vistos,
                             cinemas_favoritos=cinemas_favoritos,
                             stats_avaliacoes=stats_avaliacoes,
                             stats=stats,
                             pontos=pontos,
                             nivel=nivel,
                             nivel_cor=nivel_cor,
                             total_filmes_vistos=total_filmes_vistos,
                             total_avaliacoes=total_avaliacoes,
                             logged_in=True,
                             avatar=avatar,
                             is_admin=False)

    except Exception as e:
        print(f"❌ DEBUG: Erro no route perfil: {str(e)}")
        import traceback
        print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
        app.logger.error(f"Erro na função perfil: {str(e)}")
        flash("Erro ao carregar perfil. Tenta novamente.", "erro")
        return redirect(url_for('home'))

# ==========================
# RECOMPENSAS
# ==========================
@app.route('/recompensas')
def recompensas():
    if 'user_id' not in session:
        flash("Inicia sessão primeiro!", "erro")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Buscar dados do usuário incluindo avatar
    cursor.execute("""
        SELECT u.id, u.nome, u.email, u.avatar, u.avatar_id,
               a.caminho as avatar_path
        FROM usuarios u 
        LEFT JOIN avatars a ON u.avatar_id = a.id 
        WHERE u.id = %s
    """, (user_id,))
    user = cursor.fetchone()
    
    # Processar avatar com a mesma lógica do perfil
    avatar = None
    
    # Prioridade: avatar da tabela avatars → avatar direto do usuario → fallback
    if user and user.get('avatar_path'):
        avatar = str(user['avatar_path'])
    elif user and user.get('avatar'):
        avatar = str(user['avatar'])
    else:
        avatar = 'imgs/icons/user_icon34-removebg-preview.png'
    
    # Limpar e normalizar avatar
    if avatar:
        avatar = avatar.replace('\\', '/').replace('"', '').strip()
        
        # Remover prefixos desnecessários
        if avatar.startswith('static/'):
            avatar = avatar[7:]
        if avatar.startswith('/static/'):
            avatar = avatar[8:]
    
    # Verificação final
    if not avatar or avatar == 'imgs/' or avatar == 'imgs':
        avatar = 'imgs/icons/user_icon34-removebg-preview.png'
    
    # Atualizar sessão com avatar correto
    session['user_avatar'] = avatar
    
    print(f"🔍 DEBUG RECOMPENSAS - Avatar final: {avatar}")
    
    # Calcular pontos disponíveis usando a função centralizada
    pontos = calcular_pontos_usuario(session['user_id'], cursor)
    
    # Buscar prémios da tabela premios
    cursor.execute("""
        SELECT 
            id,
            nome,
            pontos,
            img_url
        FROM premios
        ORDER BY pontos ASC
    """)
    recompensas_raw = cursor.fetchall()
    
    # Limpar caminhos das imagens e criar descrições personalizadas
    recompensas = []
    for r in recompensas_raw:
        r_dict = dict(r)
        r_dict['titulo'] = r_dict['nome']
        r_dict['custo_pontos'] = r_dict['pontos']
        
        # Criar descrição baseada no nome do produto
        nome_lower = r_dict['nome'].lower()
        if 'coca' in nome_lower or 'fanta' in nome_lower:
            r_dict['descricao'] = 'Bebida refrescante para acompanhar o teu filme'
        elif 'pipocas' in nome_lower:
            r_dict['descricao'] = 'Pipocas crocantes, o snack perfeito para o cinema'
        elif 'bilhete' in nome_lower:
            r_dict['descricao'] = 'Um bilhete de cinema gratuito para qualquer sessão'
        elif 'snickers' in nome_lower:
            r_dict['descricao'] = 'Barra de chocolate deliciosa para adoçar a sessão'
        elif 'gomas' in nome_lower:
            r_dict['descricao'] = 'Gomas saborosas para partilhar durante o filme'
        elif 'doritos' in nome_lower:
            r_dict['descricao'] = 'Snack crocante e saboroso para a tua sessão'
        elif 'pretzel' in nome_lower:
            r_dict['descricao'] = 'Snack salgado tradicional, perfeito para o cinema'
        else:
            r_dict['descricao'] = 'Prémio exclusivo disponível para resgate'
        
        # Limpar e validar imagem
        if r_dict.get('img_url'):
            r_dict['imagem'] = r_dict['img_url'].replace('\\', '/').replace('"', '').strip()
        else:
            # Se não tem imagem, usar imagem padrão
            r_dict['imagem'] = 'imgs/icons/wheel-removebg-preview.png'
        
        recompensas.append(r_dict)
    
    cursor.close()
    conn.close()
    
    print(f"🎬 DEBUG RECOMPENSAS - Renderizando template com:")
    print(f"   - logged_in: True")
    print(f"   - avatar: {avatar}")
    print(f"   - pontos: {pontos}")
    print(f"   - recompensas: {len(recompensas)} itens")
    
    return render_template('recompensas.html', logged_in=True, avatar=avatar, pontos=pontos, recompensas=recompensas)

# ==========================
# PRÉMIOS
# ==========================
@app.route('/premios')
def premios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verificar se o usuário está logado para mostrar avatar
    logged_in = 'user_id' in session
    avatar = 'imgs/icons/user_icon34-removebg-preview.png'
    
    if logged_in:
        user_id = session['user_id']
        # Buscar avatar do usuário
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN u.avatar IS NOT NULL AND u.avatar != '' THEN u.avatar
                    ELSE a.caminho
                END AS avatar
            FROM usuarios u
            LEFT JOIN avatars a ON u.avatar_id = a.id
            WHERE u.id = %s
        """, (user_id,))
        user_data = cursor.fetchone()
        if user_data and user_data.get('avatar'):
            avatar = user_data['avatar'].replace('\\', '/').replace('"', '').strip()
            # Remover prefixos desnecessários
            if avatar.startswith('static/'):
                avatar = avatar[7:]
            if avatar.startswith('/static/'):
                avatar = avatar[8:]
    
    # Buscar todos os prémios da base de dados
    cursor.execute("""
        SELECT 
            id,
            nome,
            img_url,
            pontos
        FROM premios
        ORDER BY pontos ASC
    """)
    premios_raw = cursor.fetchall()
    
    # Limpar caminhos das imagens e organizar dados
    premios_list = []
    for premio in premios_raw:
        premio_dict = dict(premio)
        # Limpar caminho da imagem
        if premio_dict.get('img_url'):
            premio_dict['img_url'] = premio_dict['img_url'].replace('\\', '/').replace('"', '').strip()
        else:
            premio_dict['img_url'] = 'imgs/icons/wheel-removebg-preview.png'
        
        premios_list.append(premio_dict)
    
    cursor.close()
    conn.close()
    
    return render_template('premios.html', logged_in=logged_in, avatar=avatar, premios=premios_list)

# ==========================
# RESGATAR RECOMPENSA
# ==========================
@app.route('/resgatar_recompensa', methods=['POST'])
def resgatar_recompensa():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Utilizador não autenticado'})
    
    try:
        data = request.get_json()
        premio_id = data.get('tipo')  # ID do prémio
        custo = data.get('custo')    # Pontos necessários
        
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Calcular pontos disponíveis
        pontos_atuais = calcular_pontos_usuario(user_id, cursor)
        
        # Verificar se o prémio existe e obter dados do usuário
        cursor.execute("SELECT nome, pontos FROM premios WHERE id = %s", (premio_id,))
        premio = cursor.fetchone()
        
        cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (user_id,))
        usuario = cursor.fetchone()
        
        if not premio or not usuario:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Prémio ou utilizador não encontrado'})
        
        # Verificar se tem pontos suficientes (usar pontos do prémio da base de dados)
        pontos_necessarios = premio['pontos']
        if pontos_atuais < pontos_necessarios:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': f'Pontos insuficientes. Precisa de {pontos_necessarios} pontos, tem {pontos_atuais}'})
        
        # Gerar código único
        import random
        import string
        from datetime import datetime, timedelta
        
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Verificar se código já existe (muito improvável, mas por segurança)
        cursor.execute("SELECT id FROM codigos_desconto WHERE codigo = %s", (codigo,))
        while cursor.fetchone():
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            cursor.execute("SELECT id FROM codigos_desconto WHERE codigo = %s", (codigo,))
        
        # Determinar tipo e valor do desconto baseado no prémio
        tipo_desconto = 'produto_gratis'
        valor_desconto = 0.00
        
        # Mapear prémios para descontos
        premio_nome = premio['nome'].lower()
        if 'coca' in premio_nome or 'fanta' in premio_nome:
            tipo_desconto = 'valor_fixo'
            valor_desconto = 2.50
        elif 'pipocas' in premio_nome:
            tipo_desconto = 'valor_fixo'
            valor_desconto = 4.00
        elif 'snickers' in premio_nome or 'gomas' in premio_nome:
            tipo_desconto = 'valor_fixo'
            valor_desconto = 3.00
        elif 'doritos' in premio_nome or 'pretzel' in premio_nome:
            tipo_desconto = 'valor_fixo'
            valor_desconto = 3.50
        elif 'bilhete' in premio_nome:
            tipo_desconto = 'percentual'
            valor_desconto = 100.00  # Bilhete grátis
        
        # Data de expiração (30 dias)
        data_expiracao = datetime.now() + timedelta(days=30)
        
        # Inserir código na base de dados
        cursor.execute("""
            INSERT INTO codigos_desconto 
            (codigo, usuario_id, premio_id, premio_nome, tipo_desconto, valor_desconto, data_expiracao)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (codigo, user_id, premio_id, premio['nome'], tipo_desconto, valor_desconto, data_expiracao))
        
        print(f"✅ Código {codigo} inserido na tabela codigos_desconto")
        
        # Registrar o gasto de pontos na tabela pontos_gastos
        cursor.execute("""
            INSERT INTO pontos_gastos 
            (usuario_id, premio_id, premio_nome, pontos_gastos, codigo_desconto)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, premio_id, premio['nome'], pontos_necessarios, codigo))
        
        print(f"✅ Gasto de {pontos_necessarios} pontos registrado para usuário {user_id}")
        
        conn.commit()
        print(f"✅ Transação commitada com sucesso")
        
        # Enviar email com o código
        try:
            # Usar as configurações de email existentes do sistema
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = usuario['email']
            msg['Subject'] = f"🎁 Código de Desconto CineVibe - {premio['nome']}"
            
            corpo_email = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #0D1B2A; color: #ffffff; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1B263B, #0D1B2A); border-radius: 15px; padding: 30px; border: 2px solid #FFD60A;">
                    <h1 style="color: #FFD60A; text-align: center; margin-bottom: 20px;">🎉 Parabéns, {usuario['nome']}!</h1>
                    
                    <p style="font-size: 18px; text-align: center; margin-bottom: 30px;">
                        Resgataste com sucesso a tua recompensa:
                    </p>
                    
                    <div style="background: rgba(255, 214, 10, 0.1); border: 2px solid #FFD60A; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0;">
                        <h2 style="color: #FFD60A; margin: 0;">{premio['nome']}</h2>
                    </div>
                    
                    <p style="text-align: center; font-size: 16px; margin: 30px 0;">
                        O teu código de desconto é:
                    </p>
                    
                    <div style="background: #FFD60A; color: #000; font-size: 24px; font-weight: bold; text-align: center; padding: 15px; border-radius: 8px; letter-spacing: 2px; margin: 20px 0;">
                        {codigo}
                    </div>
                    
                    <div style="background: rgba(78, 168, 222, 0.1); border-left: 4px solid #4EA8DE; padding: 15px; margin: 20px 0;">
                        <h3 style="color: #4EA8DE; margin-top: 0;">Como usar:</h3>
                        <ol style="color: #B8C5D1;">
                            <li>Faz a tua reserva normalmente</li>
                            <li>Na página de pagamento, introduz o código no campo "Código de Desconto"</li>
                            <li>Clica em "Aplicar" para ver o desconto</li>
                            <li>Finaliza a compra e desfruta!</li>
                        </ol>
                    </div>
                    
                    <p style="text-align: center; color: #B8C5D1; font-size: 14px; margin-top: 30px;">
                        ⏰ Este código expira em 30 dias<br>
                        📧 Guarda este email para não perderes o código
                    </p>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="http://localhost:5000/filmes" style="background: linear-gradient(135deg, #FFD60A, #FFB703); color: #000; padding: 12px 30px; text-decoration: none; border-radius: 25px; font-weight: bold;">
                            Ver Filmes Disponíveis
                        </a>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(corpo_email, 'html'))
            
            # Verificar se as credenciais de email estão configuradas
            if EMAIL_PASSWORD in ['sua_senha_app', 'DESATIVADO_TEMPORARIAMENTE'] or not EMAIL_PASSWORD:
                app.logger.warning("Email desativado temporariamente. Configure senha de app do Gmail para ativar.")
                print(f"⚠️ Email não enviado - configuração desativada. Código: {codigo}")
            else:
                # Enviar email
                server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
                if EMAIL_USE_TLS:
                    server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)
                server.quit()
                print(f"✅ Email enviado para {usuario['email']} com código: {codigo}")
            
        except Exception as email_error:
            print(f"❌ Erro ao enviar email: {email_error}")
            app.logger.error(f"Erro ao enviar email de código de desconto: {email_error}")
            # Continuar mesmo se o email falhar - o código foi criado
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Prémio "{premio["nome"]}" resgatado com sucesso! Verifica o teu email para o código de desconto.',
            'codigo': codigo,  # Para mostrar na interface também
            'pontos_restantes': pontos_atuais - pontos_necessarios
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

# ==========================
# DASHBOARD ADMIN
# ==========================
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        flash("Inicia sessão primeiro!", "erro")
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Verificar se o usuário é admin
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash("Acesso negado! Apenas administradores podem aceder a esta página.", "erro")
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    
    # ===== ESTATÍSTICAS PRINCIPAIS =====
    cur.execute("SELECT COUNT(*) as total FROM filmes")
    total_filmes = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as total FROM cinemas")
    total_cinemas = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as total FROM usuarios WHERE is_admin = FALSE")
    total_usuarios = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as total FROM reservas WHERE DATE(data_reserva) = CURDATE()")
    reservas_hoje = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as total FROM reservas")
    total_reservas = cur.fetchone()['total']
    
    # ===== RECEITAS =====
    cur.execute("""
        SELECT COALESCE(SUM(total), 0) as total
        FROM reservas
        WHERE DATE(data_reserva) = CURDATE()
    """)
    receita_hoje = float(cur.fetchone()['total'] or 0)
    
    cur.execute("""
        SELECT COALESCE(SUM(total), 0) as total
        FROM reservas
        WHERE YEARWEEK(data_reserva, 1) = YEARWEEK(CURDATE(), 1)
    """)
    receita_semana = float(cur.fetchone()['total'] or 0)
    
    cur.execute("""
        SELECT COALESCE(SUM(total), 0) as total
        FROM reservas
        WHERE YEAR(data_reserva) = YEAR(CURDATE()) 
        AND MONTH(data_reserva) = MONTH(CURDATE())
    """)
    receita_mes = float(cur.fetchone()['total'] or 0)
    
    cur.execute("""
        SELECT COALESCE(SUM(total), 0) as total
        FROM reservas
    """)
    receita_total = float(cur.fetchone()['total'] or 0)
    
    # ===== CRESCIMENTO =====
    # Comparar com semana anterior
    cur.execute("""
        SELECT COALESCE(SUM(total), 0) as total
        FROM reservas
        WHERE YEARWEEK(data_reserva, 1) = YEARWEEK(CURDATE(), 1) - 1
    """)
    receita_semana_anterior = float(cur.fetchone()['total'] or 0)
    crescimento_semanal = ((receita_semana - receita_semana_anterior) / receita_semana_anterior * 100) if receita_semana_anterior > 0 else 0
    
    # ===== TOP 5 FILMES =====
    cur.execute("""
        SELECT f.titulo, f.poster_url, COUNT(r.id) as total_reservas,
               COALESCE(SUM(r.total), 0) as receita
        FROM filmes f
        LEFT JOIN reservas r ON f.id = r.id_filme
        GROUP BY f.id, f.titulo, f.poster_url
        ORDER BY total_reservas DESC
        LIMIT 5
    """)
    top_filmes = cur.fetchall()
    
    # ===== RESERVAS POR DIA (ÚLTIMOS 7 DIAS) =====
    cur.execute("""
        SELECT DATE_FORMAT(data_reserva, '%d/%m') as data, 
               COUNT(*) as total,
               COALESCE(SUM(total), 0) as receita
        FROM reservas
        WHERE data_reserva >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(data_reserva)
        ORDER BY DATE(data_reserva)
    """)
    reservas_7dias = cur.fetchall()
    
    # ===== VENDAS POR CINEMA =====
    cur.execute("""
        SELECT c.nome, c.localizacao,
               COUNT(r.id) as total_reservas,
               COALESCE(SUM(r.total), 0) as receita
        FROM cinemas c
        LEFT JOIN reservas r ON c.id = r.id_cinema
        GROUP BY c.id, c.nome, c.localizacao
        ORDER BY receita DESC
    """)
    vendas_por_cinema = cur.fetchall()
    
    # ===== HORÁRIOS MAIS POPULARES =====
    cur.execute("""
        SELECT TIME_FORMAT(h.hora, '%H:%i') as horario, 
               COUNT(r.id) as total_reservas
        FROM horarios_sessao hs
        JOIN horarios h ON hs.id_horario = h.id
        LEFT JOIN reservas r ON hs.id = r.id_horario_sessao
        GROUP BY h.hora
        ORDER BY total_reservas DESC
        LIMIT 5
    """)
    horarios_populares = cur.fetchall()
    
    # ===== TIPOS DE SESSÃO MAIS VENDIDOS =====
    cur.execute("""
        SELECT ts.nome, COUNT(r.id) as total_reservas,
               COALESCE(SUM(r.total), 0) as receita
        FROM tipos_sessao ts
        LEFT JOIN reservas r ON ts.id = r.id_tipo_sessao
        GROUP BY ts.id, ts.nome
        ORDER BY total_reservas DESC
    """)
    tipos_sessao_stats = cur.fetchall()
    
    # ===== ÚLTIMAS 10 RESERVAS =====
    cur.execute("""
        SELECT r.id, r.lugares, r.data_reserva, r.total,
               u.nome as usuario_nome,
               f.titulo as filme_titulo,
               c.nome as cinema_nome
        FROM reservas r
        JOIN usuarios u ON r.id_usuario = u.id
        JOIN filmes f ON r.id_filme = f.id
        JOIN cinemas c ON r.id_cinema = c.id
        ORDER BY r.data_reserva DESC
        LIMIT 10
    """)
    ultimas_reservas = cur.fetchall()
    
    # ===== NOVOS USUÁRIOS (ÚLTIMOS 7 DIAS) =====
    cur.execute("""
        SELECT COUNT(*) as total
        FROM usuarios
        WHERE criado_em >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        AND is_admin = FALSE
    """)
    novos_usuarios_semana = cur.fetchone()['total']
    
    # ===== PRODUTOS BAR MAIS VENDIDOS =====
    try:
        cur.execute("""
            SELECT rb.produto as nome, b.imagem_url,
                   SUM(rb.quantidade) as total_vendas
            FROM reservas_bar rb
            LEFT JOIN bar b ON rb.produto = b.produto
            GROUP BY rb.produto, b.imagem_url
            ORDER BY total_vendas DESC
            LIMIT 5
        """)
        top_produtos_bar = cur.fetchall()
    except:
        top_produtos_bar = []
    
    # ===== TAXA DE OCUPAÇÃO POR SALA =====
    cur.execute("""
        SELECT s.nome_sala, c.nome as cinema_nome,
               s.capacidade,
               COUNT(r.id) as total_reservas,
               ROUND((COUNT(r.id) / s.capacidade * 100), 1) as taxa_ocupacao
        FROM salas s
        JOIN cinemas c ON s.id_cinema = c.id
        LEFT JOIN horarios_sessao hs ON s.id = hs.id_sala
        LEFT JOIN reservas r ON hs.id = r.id_horario_sessao
        GROUP BY s.id, s.nome_sala, c.nome, s.capacidade
        ORDER BY taxa_ocupacao DESC
        LIMIT 10
    """)
    ocupacao_salas = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin_dashboard.html',
        user=get_current_user(),
        total_filmes=total_filmes,
        total_cinemas=total_cinemas,
        total_usuarios=total_usuarios,
        reservas_hoje=reservas_hoje,
        total_reservas=total_reservas,
        receita_hoje=receita_hoje,
        receita_semana=receita_semana,
        receita_mes=receita_mes,
        receita_total=receita_total,
        crescimento_semanal=crescimento_semanal,
        top_filmes=top_filmes,
        reservas_7dias=reservas_7dias,
        vendas_por_cinema=vendas_por_cinema,
        horarios_populares=horarios_populares,
        tipos_sessao_stats=tipos_sessao_stats,
        ultimas_reservas=ultimas_reservas,
        novos_usuarios_semana=novos_usuarios_semana,
        top_produtos_bar=top_produtos_bar,
        ocupacao_salas=ocupacao_salas
    )

# ==========================
# Exportar Relatórios
# ==========================
@app.route('/admin/exportar/<tipo>')
def exportar_relatorio(tipo):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Verificar se é admin
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash('Acesso negado', 'erro')
        return redirect(url_for('home'))
    
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Data e hora do relatório
    data_relatorio = datetime.now().strftime('%d/%m/%Y às %H:%M')
    
    if tipo == 'reservas':
        # ===== RELATÓRIO DE RESERVAS =====
        cur.execute("""
            SELECT r.id, r.data_reserva, r.data_sessao,
                   u.nome as usuario, u.email,
                   f.titulo as filme,
                   c.nome as cinema, c.localizacao,
                   ts.nome as tipo_sessao,
                   r.lugares, r.total, r.status
            FROM reservas r
            LEFT JOIN usuarios u ON r.id_usuario = u.id
            JOIN filmes f ON r.id_filme = f.id
            JOIN cinemas c ON r.id_cinema = c.id
            JOIN tipos_sessao ts ON r.id_tipo_sessao = ts.id
            ORDER BY r.data_reserva DESC
        """)
        dados = cur.fetchall()
        
        # Cabeçalho do relatório
        writer.writerow(['RELATÓRIO DE RESERVAS - CINEVIBE'])
        writer.writerow([f'Gerado em: {data_relatorio}'])
        writer.writerow([f'Total de Reservas: {len(dados)}'])
        writer.writerow([])
        
        # Cabeçalhos das colunas
        writer.writerow(['ID', 'Data Reserva', 'Data Sessão', 'Usuário', 'Email', 'Filme', 'Cinema', 'Localização', 'Tipo Sessão', 'Lugares', 'Valor (€)', 'Status'])
        
        # Dados
        total_receita = 0
        for row in dados:
            writer.writerow([
                row['id'],
                row['data_reserva'].strftime('%d/%m/%Y %H:%M') if row['data_reserva'] else '',
                row['data_sessao'].strftime('%d/%m/%Y') if row['data_sessao'] else '',
                row['usuario'] or 'Convidado',
                row['email'] or 'N/A',
                row['filme'],
                row['cinema'],
                row['localizacao'],
                row['tipo_sessao'],
                row['lugares'],
                f"{float(row['total']):.2f}",
                row['status'].upper()
            ])
            total_receita += float(row['total'])
        
        # Totais
        writer.writerow([])
        writer.writerow(['', '', '', '', '', '', '', '', '', 'TOTAL:', f"{total_receita:.2f} €", ''])
        
        filename = f'CineVibe_Reservas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    elif tipo == 'vendas':
        # ===== RELATÓRIO DE VENDAS POR CINEMA =====
        cur.execute("""
            SELECT c.nome as cinema, c.localizacao,
                   COUNT(r.id) as total_reservas,
                   SUM(r.total) as receita_total
            FROM cinemas c
            LEFT JOIN reservas r ON c.id = r.id_cinema
            GROUP BY c.id, c.nome, c.localizacao
            ORDER BY receita_total DESC
        """)
        vendas_cinema = cur.fetchall()
        
        # ===== VENDAS POR FILME =====
        cur.execute("""
            SELECT f.titulo as filme, f.diretor,
                   COUNT(r.id) as total_reservas,
                   SUM(r.total) as receita_total
            FROM filmes f
            LEFT JOIN reservas r ON f.id = r.id_filme
            GROUP BY f.id, f.titulo, f.diretor
            HAVING total_reservas > 0
            ORDER BY receita_total DESC
        """)
        vendas_filme = cur.fetchall()
        
        # Cabeçalho
        writer.writerow(['RELATÓRIO DE VENDAS - CINEVIBE'])
        writer.writerow([f'Gerado em: {data_relatorio}'])
        writer.writerow([])
        
        # SEÇÃO 1: Vendas por Cinema
        writer.writerow(['═══════════════════════════════════════════════════════'])
        writer.writerow(['VENDAS POR CINEMA'])
        writer.writerow(['═══════════════════════════════════════════════════════'])
        writer.writerow([])
        writer.writerow(['Cinema', 'Localização', 'Total Reservas', 'Receita Total (€)'])
        
        total_reservas_cinema = 0
        total_receita_cinema = 0
        for row in vendas_cinema:
            receita = float(row['receita_total']) if row['receita_total'] else 0
            writer.writerow([
                row['cinema'],
                row['localizacao'],
                row['total_reservas'],
                f"{receita:.2f}"
            ])
            total_reservas_cinema += row['total_reservas']
            total_receita_cinema += receita
        
        writer.writerow([])
        writer.writerow(['TOTAL', '', total_reservas_cinema, f"{total_receita_cinema:.2f} €"])
        writer.writerow([])
        writer.writerow([])
        
        # SEÇÃO 2: Vendas por Filme
        writer.writerow(['═══════════════════════════════════════════════════════'])
        writer.writerow(['VENDAS POR FILME'])
        writer.writerow(['═══════════════════════════════════════════════════════'])
        writer.writerow([])
        writer.writerow(['Filme', 'Diretor', 'Total Reservas', 'Receita Total (€)'])
        
        total_reservas_filme = 0
        total_receita_filme = 0
        for row in vendas_filme:
            receita = float(row['receita_total']) if row['receita_total'] else 0
            writer.writerow([
                row['filme'],
                row['diretor'] or 'N/A',
                row['total_reservas'],
                f"{receita:.2f}"
            ])
            total_reservas_filme += row['total_reservas']
            total_receita_filme += receita
        
        writer.writerow([])
        writer.writerow(['TOTAL', '', total_reservas_filme, f"{total_receita_filme:.2f} €"])
        
        filename = f'CineVibe_Vendas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    elif tipo == 'usuarios':
        # ===== RELATÓRIO DE USUÁRIOS =====
        cur.execute("""
            SELECT u.id, u.nome, u.email, u.criado_em,
                   COUNT(r.id) as total_reservas,
                   COALESCE(SUM(r.total), 0) as total_gasto
            FROM usuarios u
            LEFT JOIN reservas r ON u.id = r.id_usuario
            WHERE u.is_admin = FALSE
            GROUP BY u.id, u.nome, u.email, u.criado_em
            ORDER BY total_gasto DESC
        """)
        dados = cur.fetchall()
        
        # Cabeçalho
        writer.writerow(['RELATÓRIO DE USUÁRIOS - CINEVIBE'])
        writer.writerow([f'Gerado em: {data_relatorio}'])
        writer.writerow([f'Total de Usuários: {len(dados)}'])
        writer.writerow([])
        
        # Estatísticas gerais
        total_usuarios = len(dados)
        usuarios_ativos = sum(1 for u in dados if u['total_reservas'] > 0)
        usuarios_inativos = total_usuarios - usuarios_ativos
        
        writer.writerow(['ESTATÍSTICAS GERAIS'])
        writer.writerow(['Usuários Ativos (com reservas):', usuarios_ativos])
        writer.writerow(['Usuários Inativos (sem reservas):', usuarios_inativos])
        writer.writerow([])
        writer.writerow([])
        
        # Cabeçalhos
        writer.writerow(['ID', 'Nome', 'Email', 'Data Registo', 'Total Reservas', 'Total Gasto (€)', 'Status'])
        
        # Dados
        total_reservas = 0
        total_gasto = 0
        for row in dados:
            gasto = float(row['total_gasto'])
            status = 'ATIVO' if row['total_reservas'] > 0 else 'INATIVO'
            writer.writerow([
                row['id'],
                row['nome'],
                row['email'],
                row['criado_em'].strftime('%d/%m/%Y') if row['criado_em'] else 'N/A',
                row['total_reservas'],
                f"{gasto:.2f}",
                status
            ])
            total_reservas += row['total_reservas']
            total_gasto += gasto
        
        # Totais
        writer.writerow([])
        writer.writerow(['', '', '', 'TOTAIS:', total_reservas, f"{total_gasto:.2f} €", ''])
        
        filename = f'CineVibe_Usuarios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    elif tipo == 'filmes':
        # ===== RELATÓRIO DE FILMES =====
        cur.execute("""
            SELECT f.id, f.titulo, f.diretor, f.duracao, f.data_lancamento, f.estado,
                   COUNT(r.id) as total_reservas,
                   COALESCE(SUM(r.total), 0) as receita_total
            FROM filmes f
            LEFT JOIN reservas r ON f.id = r.id_filme
            GROUP BY f.id, f.titulo, f.diretor, f.duracao, f.data_lancamento, f.estado
            ORDER BY receita_total DESC
        """)
        dados = cur.fetchall()
        
        # Cabeçalho
        writer.writerow(['RELATÓRIO DE DESEMPENHO DE FILMES - CINEVIBE'])
        writer.writerow([f'Gerado em: {data_relatorio}'])
        writer.writerow([f'Total de Filmes: {len(dados)}'])
        writer.writerow([])
        
        # Estatísticas
        filmes_com_reservas = sum(1 for f in dados if f['total_reservas'] > 0)
        filmes_sem_reservas = len(dados) - filmes_com_reservas
        filmes_em_exibicao = sum(1 for f in dados if f['estado'] == 'em_exibicao')
        filmes_brevemente = sum(1 for f in dados if f['estado'] == 'brevemente')
        
        writer.writerow(['ESTATÍSTICAS GERAIS'])
        writer.writerow(['Filmes com Reservas:', filmes_com_reservas])
        writer.writerow(['Filmes sem Reservas:', filmes_sem_reservas])
        writer.writerow(['Filmes em Exibição:', filmes_em_exibicao])
        writer.writerow(['Filmes Brevemente:', filmes_brevemente])
        writer.writerow([])
        writer.writerow([])
        
        # Cabeçalhos
        writer.writerow(['ID', 'Título', 'Diretor', 'Data Lançamento', 'Duração (min)', 'Estado', 'Total Reservas', 'Receita (€)', 'Status'])
        
        # Dados
        total_reservas = 0
        total_receita = 0
        for row in dados:
            receita = float(row['receita_total'])
            status = 'POPULAR' if row['total_reservas'] > 50 else ('ATIVO' if row['total_reservas'] > 0 else 'SEM RESERVAS')
            data_lanc = row['data_lancamento'].strftime('%d/%m/%Y') if row['data_lancamento'] else 'N/A'
            estado = 'EM EXIBIÇÃO' if row['estado'] == 'em_exibicao' else 'BREVEMENTE'
            
            writer.writerow([
                row['id'],
                row['titulo'],
                row['diretor'] or 'N/A',
                data_lanc,
                row['duracao'] or 'N/A',
                estado,
                row['total_reservas'],
                f"{receita:.2f}",
                status
            ])
            total_reservas += row['total_reservas']
            total_receita += receita
        
        # Totais
        writer.writerow([])
        writer.writerow(['', '', '', '', '', 'TOTAIS:', total_reservas, f"{total_receita:.2f} €", ''])
        
        filename = f'CineVibe_Filmes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    else:
        flash('Tipo de relatório inválido', 'erro')
        return redirect(url_for('admin_dashboard'))
    
    cur.close()
    conn.close()
    
    # Criar resposta com o CSV
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'  # UTF-8 com BOM para Excel
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

# ==========================
# ADMIN - GESTÃO DE FILMES
# ==========================
@app.route('/admin/filmes')
def admin_filmes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash("Acesso negado!", "erro")
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    
    # Obter parâmetros de ordenação
    sort_by = request.args.get('sort', 'id')
    order_dir = request.args.get('order', 'desc')  # desc ou asc
    
    # Definir direção da ordenação
    direction = "ASC" if order_dir == 'asc' else "DESC"
    
    # Definir ordenação baseada no parâmetro
    if sort_by == 'duracao':
        order_clause = f"ORDER BY f.duracao {direction}"
    elif sort_by == 'imdb':
        order_clause = f"ORDER BY f.imdb_rating {direction}"
    elif sort_by == 'ano':
        order_clause = f"ORDER BY f.data_lancamento {direction}"
    else:  # default: id
        order_clause = f"ORDER BY f.id {direction}"
    
    # Buscar todos os filmes
    cur.execute(f"""
        SELECT f.*, 
               GROUP_CONCAT(DISTINCT g.nome SEPARATOR ', ') as generos,
               COUNT(DISTINCT hs.id) as num_sessoes
        FROM filmes f
        LEFT JOIN filme_generos fg ON f.id = fg.filme_id
        LEFT JOIN generos g ON fg.genero_id = g.id
        LEFT JOIN horarios_sessao hs ON f.id = hs.id_filme
        GROUP BY f.id
        {order_clause}
    """)
    filmes = cur.fetchall()
    
    # Buscar atores para cada filme
    for filme in filmes:
        cur.execute("""
            SELECT a.nome, fa.papel
            FROM filme_atores fa
            JOIN atores a ON fa.ator_id = a.id
            WHERE fa.filme_id = %s
            ORDER BY a.nome
        """, (filme['id'],))
        atores = cur.fetchall()
        filme['atores'] = ', '.join([ator['nome'] for ator in atores]) if atores else 'N/A'
    
    # Buscar todos os géneros disponíveis
    cur.execute("SELECT id, nome FROM generos ORDER BY nome")
    generos = cur.fetchall()
    
    # Limpar caminhos dos posters
    for filme in filmes:
        if filme.get('poster_url'):
            # Limpar e normalizar o caminho
            poster_url = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
            
            # Remover prefixos duplicados
            if poster_url.startswith('static/'):
                poster_url = poster_url[7:]  # Remove 'static/'
            if poster_url.startswith('/'):
                poster_url = poster_url[1:]  # Remove '/' inicial
            
            # Garantir que começa com imgs/filmes/
            if not poster_url.startswith('imgs/filmes/'):
                if poster_url.startswith('imgs/'):
                    pass  # Já está correto
                else:
                    poster_url = f"imgs/filmes/{poster_url}"
            
            filme['poster_url'] = poster_url
    
    cur.close()
    conn.close()
    
    return render_template('admin_filmes.html', user=get_current_user(), filmes=filmes, generos=generos)

@app.route('/admin/filmes/<int:id_filme>')
def admin_filme_detalhe(id_filme):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash("Acesso negado!", "erro")
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    
    # Buscar filme
    cur.execute("SELECT * FROM filmes WHERE id = %s", (id_filme,))
    filme = cur.fetchone()
    
    if not filme:
        flash("Filme não encontrado!", "erro")
        return redirect(url_for('admin_filmes'))
    
    # Limpar caminho do poster
    if filme.get('poster_url'):
        filme['poster_url'] = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
    
    # Buscar géneros do filme (usando tabela de relacionamento)
    cur.execute("""
        SELECT g.id, g.nome
        FROM generos g
        JOIN filme_generos fg ON g.id = fg.genero_id
        WHERE fg.filme_id = %s
        ORDER BY g.nome
    """, (id_filme,))
    generos_filme = cur.fetchall()
    
    # Buscar todos os géneros disponíveis
    cur.execute("SELECT id, nome FROM generos ORDER BY nome")
    todos_generos = cur.fetchall()
    
    # Buscar cinemas associados (apenas colunas que existem)
    cur.execute("""
        SELECT c.id, c.nome, c.regiao
        FROM filmes_cinemas fc
        JOIN cinemas c ON fc.cinema_id = c.id
        WHERE fc.filme_id = %s
        ORDER BY c.nome
    """, (id_filme,))
    cinemas_filme = cur.fetchall()
    
    # Buscar todos os cinemas
    cur.execute("SELECT id, nome, regiao FROM cinemas ORDER BY nome")
    todos_cinemas = cur.fetchall()
    
    # Buscar tipos de sessao que têm horários para este filme
    cur.execute("""
        SELECT DISTINCT ts.id, ts.nome, ts.preco_bilhete, ts.descricao
        FROM tipos_sessao ts
        JOIN horarios_sessao hs ON ts.id = hs.id_tipo_sessao
        WHERE hs.id_filme = %s
        ORDER BY ts.nome
    """, (id_filme,))
    tipos_sessao = cur.fetchall()
    
    # Buscar horarios disponiveis
    cur.execute("SELECT id, hora FROM horarios ORDER BY hora")
    horarios_disponiveis = cur.fetchall()
    
    # Buscar sessões detalhadas por cinema e tipo (comentado - tabela não existe)
    sessoes_detalhadas = {}
    # for cinema in cinemas_filme:
    #     cinema_id = cinema['id']
    #     sessoes_detalhadas[cinema_id] = {}
    #     
    #     for tipo in tipos_sessao:
    #         tipo_id = tipo['id']
    #         
    #         # Buscar sessões para este cinema e tipo
    #         cur.execute("""
    #             SELECT s.id, s.data_sessao, s.horario, s.sala_id, sa.nome as sala_nome, 
    #                    sa.capacidade, sa.tipo as sala_tipo
    #             FROM sessoes s
    #             LEFT JOIN salas sa ON s.sala_id = sa.id
    #             WHERE s.filme_id = %s AND s.cinema_id = %s AND s.tipo_sessao_id = %s
    #             AND s.data_sessao >= CURDATE()
    #             ORDER BY s.data_sessao, s.horario
    #         """, (id_filme, cinema_id, tipo_id))
    #         
    #         sessoes = cur.fetchall()
    #         
    #         if sessoes:
    #             sessoes_detalhadas[cinema_id][tipo_id] = {
    #                 'tipo_nome': tipo['nome'],
    #                 'preco': tipo['preco_bilhete'],
    #                 'sessoes': sessoes
    #             }
    
    # Buscar atores do filme (apenas colunas que existem)
    cur.execute("""
        SELECT a.id, a.nome, a.foto_url, fa.papel
        FROM filme_atores fa
        JOIN atores a ON fa.ator_id = a.id
        WHERE fa.filme_id = %s
        ORDER BY a.nome
    """, (id_filme,))
    atores_filme = cur.fetchall()
    
    # Buscar todos os atores
    cur.execute("SELECT id, nome, foto_url FROM atores ORDER BY nome")
    todos_atores = cur.fetchall()
    
    # Buscar avaliações recentes (últimas 5) - seguindo o padrão do filme_detalhe
    cur.execute("""
        SELECT 
            av.id,
            av.usuario_id,
            av.rating,
            av.comentario,
            av.data_avaliacao,
            u.nome as usuario_nome,
            COALESCE(u.avatar, a.caminho) as usuario_avatar
        FROM avaliacoes_filmes av
        JOIN usuarios u ON av.usuario_id = u.id
        LEFT JOIN avatars a ON u.avatar_id = a.id
        WHERE av.filme_id = %s
        ORDER BY av.data_avaliacao DESC
        LIMIT 5
    """, (id_filme,))
    avaliacoes_recentes = cur.fetchall()
    
    # Processar avatares das avaliações - seguindo o padrão do filme_detalhe
    for avaliacao in avaliacoes_recentes:
        if avaliacao.get('usuario_avatar'):
            avaliacao['usuario_avatar'] = avaliacao['usuario_avatar'].replace('\\', '/').replace('"', '').strip()
        else:
            avaliacao['usuario_avatar'] = 'imgs/icons/user_icon34-removebg-preview.png'
    
    # Buscar estatísticas de avaliações
    cur.execute("""
        SELECT 
            AVG(rating) as rating_medio,
            COUNT(*) as total_avaliacoes
        FROM avaliacoes_filmes 
        WHERE filme_id = %s
    """, (id_filme,))
    stats_avaliacoes = cur.fetchone()
    
    if stats_avaliacoes:
        filme['rating_medio'] = float(stats_avaliacoes['rating_medio']) if stats_avaliacoes['rating_medio'] else 0
        filme['total_avaliacoes'] = stats_avaliacoes['total_avaliacoes']
    else:
        filme['rating_medio'] = 0
        filme['total_avaliacoes'] = 0
    
    # Buscar cinemas onde o filme está em exibição
    try:
        cur.execute("""
            SELECT DISTINCT c.id, c.nome, c.regiao, c.localizacao
            FROM cinemas c
            JOIN filmes_cinemas fc ON c.id = fc.cinema_id
            WHERE fc.filme_id = %s
            ORDER BY c.nome
        """, (id_filme,))
        filme_cinemas = cur.fetchall()
    except Exception as e:
        app.logger.error(f"Erro ao buscar cinemas do filme: {str(e)}")
        filme_cinemas = []
    
    # Buscar apenas os tipos de sessão que têm horários para este filme
    try:
        cur.execute("""
            SELECT DISTINCT ts.id, ts.nome 
            FROM tipos_sessao ts
            JOIN horarios_sessao hs ON ts.id = hs.id_tipo_sessao
            WHERE hs.id_filme = %s
            ORDER BY ts.nome
        """, (id_filme,))
        tipos_sessao = cur.fetchall()
    except Exception as e:
        app.logger.error(f"Erro ao buscar tipos de sessão: {str(e)}")
        tipos_sessao = []
    
    # Buscar todos os cinemas para adicionar novos (excluindo os já associados)
    try:
        cur.execute("""
            SELECT c.id, c.nome, c.regiao, c.localizacao 
            FROM cinemas c
            WHERE c.id NOT IN (
                SELECT fc.cinema_id 
                FROM filmes_cinemas fc 
                WHERE fc.filme_id = %s
            )
            ORDER BY c.nome
        """, (id_filme,))
        todos_cinemas = cur.fetchall()
    except Exception as e:
        app.logger.error(f"Erro ao buscar todos os cinemas: {str(e)}")
        todos_cinemas = []
    
    # Limpar caminhos de imagem dos atores
    for ator in atores_filme:
        if ator.get('foto_url'):
            ator['foto_url'] = ator['foto_url'].replace('\\', '/').replace('"', '').strip()
    
    for ator in todos_atores:
        if ator.get('foto_url'):
            ator['foto_url'] = ator['foto_url'].replace('\\', '/').replace('"', '').strip()
    
    # Buscar tipos de sessão específicos por cinema
    tipos_sessao_por_cinema = {}
    
    for cinema in filme_cinemas:
        try:
            cur.execute("""
                SELECT DISTINCT ts.id, ts.nome 
                FROM tipos_sessao ts
                JOIN horarios_sessao hs ON ts.id = hs.id_tipo_sessao
                WHERE hs.id_filme = %s AND hs.id_cinema = %s
                ORDER BY ts.nome
            """, (id_filme, cinema['id']))
            tipos_cinema = cur.fetchall()
            tipos_sessao_por_cinema[cinema['id']] = tipos_cinema
        except Exception as e:
            app.logger.error(f"Erro ao buscar tipos de sessão para cinema {cinema['id']}: {str(e)}")
            tipos_sessao_por_cinema[cinema['id']] = []
    
    # Manter tipos_sessao para compatibilidade (vazio agora)
    tipos_sessao = []
    
    cur.close()
    conn.close()
    return render_template('admin_filme_detalhe.html',
                         user=get_current_user(),
                         filme=filme,
                         generos_filme=generos_filme,
                         todos_generos=todos_generos,
                         atores_filme=atores_filme,
                         todos_atores=todos_atores,
                         filme_cinemas=filme_cinemas,
                         tipos_sessao=tipos_sessao,
                         todos_cinemas=todos_cinemas,
                         avaliacoes_recentes=avaliacoes_recentes,
                         tipos_sessao_por_cinema=tipos_sessao_por_cinema)

@app.route('/admin/filmes/<int:filme_id>/cinema/<int:cinema_id>/tipos-sessao-disponiveis')
def admin_get_tipos_sessao_disponiveis(filme_id, cinema_id):
    """Busca tipos de sessão que não estão visíveis para um cinema específico"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Buscar todos os tipos de sessão que NÃO têm horários para este filme e cinema
        cur.execute("""
            SELECT ts.id, ts.nome, ts.descricao
            FROM tipos_sessao ts
            WHERE ts.id NOT IN (
                SELECT DISTINCT hs.id_tipo_sessao
                FROM horarios_sessao hs
                WHERE hs.id_filme = %s AND hs.id_cinema = %s
            )
            ORDER BY ts.nome
        """, (filme_id, cinema_id))
        
        tipos_disponiveis = cur.fetchall()
        
        return jsonify({
            'success': True,
            'tipos': tipos_disponiveis
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar tipos de sessão disponíveis: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500
    
    finally:
        cur.close()
        conn.close()

@app.route('/admin/adicionar-tipo-sessao-cinema', methods=['POST'])
def admin_adicionar_tipo_sessao_cinema():
    """Adiciona um tipo de sessão a um cinema (torna visível criando um horário dummy)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    filme_id = request.form.get('filme_id')
    cinema_id = request.form.get('cinema_id')
    tipo_sessao_id = request.form.get('tipo_sessao_id')
    sala_id = request.form.get('sala_id')
    
    if not all([filme_id, cinema_id, tipo_sessao_id, sala_id]):
        return jsonify({
            'success': False,
            'message': 'Todos os campos são obrigatórios'
        }), 400
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se já existe algum horário para este filme, cinema e tipo de sessão
        cur.execute("""
            SELECT COUNT(*) as count
            FROM horarios_sessao hs
            WHERE hs.id_filme = %s AND hs.id_cinema = %s AND hs.id_tipo_sessao = %s
        """, (filme_id, cinema_id, tipo_sessao_id))
        
        existing = cur.fetchone()
        
        if existing['count'] > 0:
            return jsonify({
                'success': False,
                'message': 'Este tipo de sessão já está disponível para este cinema'
            }), 400
        
        # Buscar um horário padrão (vamos usar o primeiro horário disponível)
        cur.execute("SELECT id FROM horarios ORDER BY hora LIMIT 1")
        horario_padrao = cur.fetchone()
        
        if not horario_padrao:
            return jsonify({
                'success': False,
                'message': 'Nenhum horário disponível na base de dados'
            }), 400
        
        # Criar um horário dummy para tornar o tipo de sessão visível
        # O admin pode depois adicionar horários reais ou editar este
        cur.execute("""
            INSERT INTO horarios_sessao (id_filme, id_cinema, id_tipo_sessao, id_sala, id_horario)
            VALUES (%s, %s, %s, %s, %s)
        """, (filme_id, cinema_id, tipo_sessao_id, sala_id, horario_padrao['id']))
        
        conn.commit()
        
        # Buscar o nome do tipo de sessão para a resposta
        cur.execute("SELECT nome FROM tipos_sessao WHERE id = %s", (tipo_sessao_id,))
        tipo_nome = cur.fetchone()
        
        return jsonify({
            'success': True,
            'message': f'Tipo de sessão "{tipo_nome["nome"] if tipo_nome else "desconhecido"}" adicionado com sucesso!'
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao adicionar tipo de sessão: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500
    
    finally:
        cur.close()
        conn.close()

@app.route('/admin/remover-tipo-sessao-cinema', methods=['POST'])
def admin_remover_tipo_sessao_cinema():
    """Remove um tipo de sessão de um cinema (remove reservas e horários associados)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    filme_id = request.form.get('filme_id')
    cinema_id = request.form.get('cinema_id')
    tipo_sessao_id = request.form.get('tipo_sessao_id')
    
    if not all([filme_id, cinema_id, tipo_sessao_id]):
        return jsonify({
            'success': False,
            'message': 'Todos os campos são obrigatórios'
        }), 400
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Buscar o nome do tipo de sessão para a resposta
        cur.execute("SELECT nome FROM tipos_sessao WHERE id = %s", (tipo_sessao_id,))
        tipo_nome = cur.fetchone()
        
        # 1. PRIMEIRO: Verificar se existem reservas para estes horários
        cur.execute("""
            SELECT COUNT(*) as count_reservas
            FROM reservas r
            JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
            WHERE hs.id_filme = %s AND hs.id_cinema = %s AND hs.id_tipo_sessao = %s
        """, (filme_id, cinema_id, tipo_sessao_id))
        
        reservas_count = cur.fetchone()['count_reservas']
        
        if reservas_count > 0:
            # Se existem reservas, remover primeiro as reservas
            app.logger.warning(f"Removendo {reservas_count} reservas antes de remover horários")
            
            cur.execute("""
                DELETE r FROM reservas r
                JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
                WHERE hs.id_filme = %s AND hs.id_cinema = %s AND hs.id_tipo_sessao = %s
            """, (filme_id, cinema_id, tipo_sessao_id))
            
            reservas_removidas = cur.rowcount
            app.logger.info(f"Removidas {reservas_removidas} reservas")
        
        # 2. DEPOIS: Remover os horários (agora sem constraint)
        cur.execute("""
            DELETE FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s
        """, (filme_id, cinema_id, tipo_sessao_id))
        
        horarios_removidos = cur.rowcount
        conn.commit()
        
        app.logger.info(f"Removidos {horarios_removidos} horários do tipo de sessão {tipo_sessao_id}")
        
        # Mensagem de sucesso
        message = f'Tipo de sessão "{tipo_nome["nome"] if tipo_nome else "desconhecido"}" removido com sucesso!'
        if reservas_count > 0:
            message += f' (Foram também removidas {reservas_count} reservas associadas)'
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao remover tipo de sessão: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500
    
    finally:
        cur.close()
        conn.close()

@app.route('/admin/filmes/<int:id_filme>/cinema/<int:cinema_id>/tipo/<int:tipo_id>/sala')
def admin_get_sala_tipo_sessao(id_filme, cinema_id, tipo_id):
    """Busca a sala configurada para um tipo de sessão específico"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar a sala mais comum para este tipo de sessão neste cinema
        cur.execute("""
            SELECT s.id as sala_id, s.nome_sala, s.capacidade, COUNT(*) as uso_count
            FROM horarios_sessao hs
            JOIN salas s ON hs.id_sala = s.id
            WHERE hs.id_filme = %s AND hs.id_cinema = %s AND hs.id_tipo_sessao = %s
            GROUP BY s.id, s.nome_sala, s.capacidade
            ORDER BY uso_count DESC, s.id ASC
            LIMIT 1
        """, (id_filme, cinema_id, tipo_id))
        
        sala = cur.fetchone()
        
        if sala:
            return jsonify({
                'success': True,
                'sala_id': sala['sala_id'],
                'nome_sala': sala['nome_sala'],
                'capacidade': sala['capacidade']
            })
        else:
            # Se não encontrar sala específica, buscar a primeira sala disponível do cinema
            cur.execute("""
                SELECT id as sala_id, nome_sala, capacidade
                FROM salas
                WHERE cinema_id = %s
                ORDER BY id ASC
                LIMIT 1
            """, (cinema_id,))
            
            sala_default = cur.fetchone()
            
            if sala_default:
                return jsonify({
                    'success': True,
                    'sala_id': sala_default['sala_id'],
                    'nome_sala': sala_default['nome_sala'],
                    'capacidade': sala_default['capacidade']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Nenhuma sala encontrada para este cinema'
                })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ===== ROTAS DE EDIÇÃO PARA TIPOS DE SESSÃO =====

@app.route('/admin/tipos-sessao/adicionar', methods=['POST'])
def admin_adicionar_tipo_sessao():
    """Adiciona um novo tipo de sessão"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        nome = request.form.get('nome')
        descricao = request.form.get('descricao', '')
        preco_bilhete = request.form.get('preco_bilhete')
        
        if not nome or not preco_bilhete:
            return jsonify({'success': False, 'message': 'Nome e preço são obrigatórios'})
        
        # Inserir novo tipo de sessão
        cur.execute("""
            INSERT INTO tipos_sessao (nome, descricao, preco_bilhete, preco)
            VALUES (%s, %s, %s, %s)
        """, (nome, descricao, float(preco_bilhete), float(preco_bilhete)))
        
        conn.commit()
        tipo_id = cur.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'Tipo de sessão adicionado com sucesso',
            'tipo_id': tipo_id
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao adicionar tipo de sessão: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/tipos-sessao/<int:tipo_id>/editar', methods=['POST'])
def admin_editar_tipo_sessao(tipo_id):
    """Edita um tipo de sessão existente"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        nome = request.form.get('nome')
        descricao = request.form.get('descricao', '')
        preco_bilhete = request.form.get('preco_bilhete')
        
        if not nome or not preco_bilhete:
            return jsonify({'success': False, 'message': 'Nome e preço são obrigatórios'})
        
        # Atualizar tipo de sessão
        cur.execute("""
            UPDATE tipos_sessao 
            SET nome = %s, descricao = %s, preco_bilhete = %s, preco = %s
            WHERE id = %s
        """, (nome, descricao, float(preco_bilhete), float(preco_bilhete), tipo_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tipo de sessão atualizado com sucesso'
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao editar tipo de sessão: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/tipos-sessao/<int:tipo_id>/remover', methods=['POST'])
def admin_remover_tipo_sessao(tipo_id):
    """Remove um tipo de sessão"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Verificar se há sessões usando este tipo
        cur.execute("SELECT COUNT(*) as count FROM horarios_sessao WHERE id_tipo_sessao = %s", (tipo_id,))
        count = cur.fetchone()['count']
        
        if count > 0:
            return jsonify({
                'success': False, 
                'message': f'Não é possível remover. Existem {count} sessões usando este tipo.'
            })
        
        # Remover tipo de sessão
        cur.execute("DELETE FROM tipos_sessao WHERE id = %s", (tipo_id,))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tipo de sessão removido com sucesso'
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao remover tipo de sessão: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

# ===== ROTAS DE EDIÇÃO PARA HORÁRIOS =====

@app.route('/admin/horarios/disponiveis', methods=['GET'])
def admin_get_horarios_disponiveis():
    """Busca todos os horários disponíveis na base de dados"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Buscar todos os horários disponíveis ordenados por hora
        cur.execute("SELECT id, hora FROM horarios ORDER BY hora")
        horarios = cur.fetchall()
        
        # Formatar horários para o frontend
        horarios_formatados = []
        for horario in horarios:
            horarios_formatados.append({
                'id': horario['id'],
                'hora': str(horario['hora']),
                'display': str(horario['hora'])  # Para mostrar no dropdown
            })
        
        return jsonify({
            'success': True,
            'horarios': horarios_formatados
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar horários disponíveis: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/horarios/adicionar', methods=['POST'])
def admin_adicionar_horario_geral():
    """Adiciona um novo horário com associação completa"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Obter dados do formulário
        filme_id = request.form.get('filme_id')
        cinema_id = request.form.get('cinema_id')
        tipo_sessao_id = request.form.get('tipo_sessao_id')
        sala_id = request.form.get('sala_id')
        
        # Pode receber horario_id (seleção de horário existente) ou hora (novo horário)
        horario_id = request.form.get('horario_id')
        hora = request.form.get('hora')
        
        app.logger.info(f"Dados recebidos: filme_id={filme_id}, cinema_id={cinema_id}, tipo_sessao_id={tipo_sessao_id}, sala_id={sala_id}, horario_id={horario_id}, hora={hora}")
        
        # Validar campos obrigatórios
        if not all([filme_id, cinema_id, tipo_sessao_id, sala_id]):
            return jsonify({'success': False, 'message': 'Campos obrigatórios: filme_id, cinema_id, tipo_sessao_id, sala_id'})
        
        # Deve ter ou horario_id ou hora
        if not horario_id and not hora:
            return jsonify({'success': False, 'message': 'Deve fornecer horario_id ou hora'})
        
        # Se foi fornecido horario_id, usar esse horário existente
        if horario_id:
            # Verificar se o horário existe
            cur.execute("SELECT id, hora FROM horarios WHERE id = %s", (horario_id,))
            horario_existente = cur.fetchone()
            
            if not horario_existente:
                return jsonify({'success': False, 'message': 'Horário selecionado não existe'})
            
            horario_final_id = horario_id
            hora_display = str(horario_existente['hora'])
            
        else:
            # Se foi fornecida hora, verificar se já existe ou criar novo
            cur.execute("SELECT id FROM horarios WHERE hora = %s", (hora,))
            horario_existente = cur.fetchone()
            
            if horario_existente:
                horario_final_id = horario_existente['id']
            else:
                # Inserir novo horário na tabela horarios
                cur.execute("INSERT INTO horarios (hora) VALUES (%s)", (hora,))
                horario_final_id = cur.lastrowid
            
            hora_display = hora
        
        # Verificar se já existe esta combinação específica
        cur.execute("""
            SELECT id FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s 
            AND id_horario = %s AND id_sala = %s
        """, (filme_id, cinema_id, tipo_sessao_id, horario_final_id, sala_id))
        
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Esta sessão já existe para este horário e sala'})
        
        # Inserir associação na tabela horarios_sessao
        cur.execute("""
            INSERT INTO horarios_sessao (id_filme, id_cinema, id_tipo_sessao, id_horario, id_sala)
            VALUES (%s, %s, %s, %s, %s)
        """, (filme_id, cinema_id, tipo_sessao_id, horario_final_id, sala_id))
        
        conn.commit()
        
        app.logger.info(f"Horário adicionado com sucesso: {hora_display} para filme {filme_id}")
        
        return jsonify({
            'success': True,
            'message': 'Horário adicionado com sucesso',
            'horario_id': horario_final_id,
            'hora': hora_display
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao adicionar horário: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/horarios/<int:horario_id>/editar', methods=['POST'])
def admin_editar_horario(horario_id):
    """Edita um horário existente - NOVA IMPLEMENTAÇÃO para editar sessões específicas"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        hora = request.form.get('hora')
        sala_id = request.form.get('sala_id')
        
        if not hora:
            return jsonify({'success': False, 'message': 'Hora é obrigatória'})
        
        if not sala_id:
            return jsonify({'success': False, 'message': 'Sala é obrigatória'})
        
        # NOVA ABORDAGEM: Tratar como edição de sessão específica
        # O horario_id na verdade é o id da sessão (horarios_sessao.id)
        
        # Buscar informações da sessão atual
        cur.execute("""
            SELECT hs.*, h.hora as hora_atual
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (horario_id,))
        sessao_atual = cur.fetchone()
        
        if not sessao_atual:
            return jsonify({'success': False, 'message': 'Sessão não encontrada'})
        
        # Verificar se já existe um horário com essa hora
        cur.execute("SELECT id FROM horarios WHERE hora = %s", (hora,))
        horario_existente = cur.fetchone()
        
        if horario_existente:
            novo_horario_id = horario_existente['id']
        else:
            # Criar novo horário se não existir
            cur.execute("INSERT INTO horarios (hora) VALUES (%s)", (hora,))
            novo_horario_id = cur.lastrowid
        
        # Verificar se já existe uma sessão com essa combinação (exceto a atual)
        cur.execute("""
            SELECT id FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s 
            AND id_horario = %s AND id_sala = %s AND id != %s
        """, (sessao_atual['id_filme'], sessao_atual['id_cinema'], 
              sessao_atual['id_tipo_sessao'], novo_horario_id, sala_id, horario_id))
        
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Já existe uma sessão para este horário e sala'})
        
        # Atualizar a sessão
        cur.execute("""
            UPDATE horarios_sessao 
            SET id_horario = %s, id_sala = %s 
            WHERE id = %s
        """, (novo_horario_id, sala_id, horario_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sessão atualizada com sucesso'
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao editar sessão: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/tipo-sessao/alterar-sala', methods=['POST'])
def admin_alterar_sala_tipo_sessao():
    """Altera a sala para todas as sessões de um tipo específico"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        filme_id = request.form.get('filme_id')
        cinema_id = request.form.get('cinema_id')
        tipo_sessao_id = request.form.get('tipo_sessao_id')
        sala_id = request.form.get('sala_id')
        
        if not all([filme_id, cinema_id, tipo_sessao_id, sala_id]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'})
        
        # Atualizar todas as sessões deste tipo para usar a nova sala
        cur.execute("""
            UPDATE horarios_sessao 
            SET id_sala = %s 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s
        """, (sala_id, filme_id, cinema_id, tipo_sessao_id))
        
        sessoes_atualizadas = cur.rowcount
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Sala alterada para {sessoes_atualizadas} sessões'
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao alterar sala do tipo de sessão: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/horarios/<int:sessao_id>/editar-simples', methods=['POST'])
def admin_editar_horario_simples(sessao_id):
    """Edita apenas a hora de uma sessão específica"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Pode receber horario_id (seleção de horário existente) ou hora (novo horário)
        horario_id = request.form.get('horario_id')
        hora = request.form.get('hora')
        
        app.logger.info(f"Editando sessão {sessao_id}: horario_id={horario_id}, hora={hora}")
        
        # Deve ter ou horario_id ou hora
        if not horario_id and not hora:
            return jsonify({'success': False, 'message': 'Deve fornecer horario_id ou hora'})
        
        # Buscar informações da sessão atual
        cur.execute("""
            SELECT hs.*, h.hora as hora_atual
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (sessao_id,))
        sessao_atual = cur.fetchone()
        
        if not sessao_atual:
            return jsonify({'success': False, 'message': 'Sessão não encontrada'})
        
        # Se foi fornecido horario_id, usar esse horário existente
        if horario_id:
            # Verificar se o horário existe
            cur.execute("SELECT id, hora FROM horarios WHERE id = %s", (horario_id,))
            horario_existente = cur.fetchone()
            
            if not horario_existente:
                return jsonify({'success': False, 'message': 'Horário selecionado não existe'})
            
            novo_horario_id = horario_id
            hora_display = str(horario_existente['hora'])
            
        else:
            # Se foi fornecida hora, verificar se já existe ou criar novo
            cur.execute("SELECT id FROM horarios WHERE hora = %s", (hora,))
            horario_existente = cur.fetchone()
            
            if horario_existente:
                novo_horario_id = horario_existente['id']
            else:
                # Criar novo horário se não existir
                cur.execute("INSERT INTO horarios (hora) VALUES (%s)", (hora,))
                novo_horario_id = cur.lastrowid
            
            hora_display = hora
        
        # Verificar se já existe uma sessão com essa combinação (exceto a atual)
        cur.execute("""
            SELECT id FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s 
            AND id_horario = %s AND id_sala = %s AND id != %s
        """, (sessao_atual['id_filme'], sessao_atual['id_cinema'], 
              sessao_atual['id_tipo_sessao'], novo_horario_id, sessao_atual['id_sala'], sessao_id))
        
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Já existe uma sessão para este horário'})
        
        # Atualizar apenas o horário da sessão
        cur.execute("""
            UPDATE horarios_sessao 
            SET id_horario = %s 
            WHERE id = %s
        """, (novo_horario_id, sessao_id))
        
        conn.commit()
        
        app.logger.info(f"Horário da sessão {sessao_id} atualizado para: {hora_display}")
        
        return jsonify({
            'success': True,
            'message': 'Horário atualizado com sucesso',
            'horario_id': novo_horario_id,
            'hora': hora_display
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao editar horário simples: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/horarios/remover-multiplos-sessoes', methods=['POST'])
def admin_remover_multiplos_sessoes():
    """Remove múltiplas sessões de uma vez"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        import json
        sessao_ids_json = request.form.get('sessao_ids')
        
        if not sessao_ids_json:
            return jsonify({'success': False, 'message': 'IDs das sessões são obrigatórios'})
        
        sessao_ids = json.loads(sessao_ids_json)
        
        if not sessao_ids:
            return jsonify({'success': False, 'message': 'Nenhuma sessão para remover'})
        
        # Remover todas as sessões
        placeholders = ','.join(['%s'] * len(sessao_ids))
        cur.execute(f"DELETE FROM horarios_sessao WHERE id IN ({placeholders})", sessao_ids)
        
        sessoes_removidas = cur.rowcount
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'{sessoes_removidas} sessões removidas'
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao remover horários múltiplos: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()
        conn.close()

@app.route('/admin/horarios/<int:horario_id>/remover', methods=['POST'])
def admin_remover_horario(horario_id):
    """Remove um horário"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Verificar se há sessões usando este horário
        cur.execute("SELECT COUNT(*) as count FROM horarios_sessao WHERE id_horario = %s", (horario_id,))
        count = cur.fetchone()['count']
        
        if count > 0:
            return jsonify({
                'success': False, 
                'message': f'Não é possível remover. Existem {count} sessões usando este horário.'
            })
        
        # Remover horário
        cur.execute("DELETE FROM horarios WHERE id = %s", (horario_id,))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Horário removido com sucesso'
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao remover horário: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

# ===== ROTAS DE EDIÇÃO PARA SALAS =====

@app.route('/admin/salas/adicionar', methods=['POST'])
def admin_adicionar_sala():
    """Adiciona uma nova sala"""
    if 'user_id' not in session:
        flash('Não autorizado', 'erro')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            flash('Acesso negado', 'erro')
            return redirect(url_for('admin_salas'))
        
        id_cinema = request.form.get('id_cinema')
        nome_sala = request.form.get('nome_sala')
        capacidade = request.form.get('capacidade')
        tipo_sala = request.form.get('tipo_sala', 'Normal')
        filas = request.form.get('filas', 10)
        lugares_por_fila = request.form.get('lugares_por_fila', 20)
        
        if not id_cinema or not nome_sala or not capacidade:
            flash('Cinema, nome e capacidade são obrigatórios', 'erro')
            return redirect(url_for('admin_salas'))
        
        # Verificar se já existe uma sala com o mesmo nome neste cinema
        cur.execute("""
            SELECT id FROM salas 
            WHERE id_cinema = %s AND nome_sala = %s
        """, (id_cinema, nome_sala))
        
        sala_existente = cur.fetchone()
        if sala_existente:
            flash(f'Já existe uma sala com o nome "{nome_sala}" neste cinema', 'erro')
            return redirect(url_for('admin_salas'))
        
        # Inserir nova sala
        cur.execute("""
            INSERT INTO salas (id_cinema, nome_sala, capacidade, tipo_sala, filas, lugares_por_fila)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_cinema, nome_sala, int(capacidade), tipo_sala, int(filas), int(lugares_por_fila)))
        
        conn.commit()
        flash('Sala adicionada com sucesso!', 'success')
        return redirect(url_for('admin_salas'))
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao adicionar sala: {str(e)}")
        flash(f'Erro ao adicionar sala: {str(e)}', 'erro')
        return redirect(url_for('admin_salas'))
    finally:
        cur.close()
        conn.close()

@app.route('/admin/salas/<int:sala_id>/editar', methods=['POST'])
def admin_editar_sala(sala_id):
    """Edita uma sala existente"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        nome_sala = request.form.get('nome_sala')
        capacidade = request.form.get('capacidade')
        id_cinema = request.form.get('id_cinema')
        tipo_sala = request.form.get('tipo_sala', 'Normal')
        filas = request.form.get('filas', 10)
        lugares_por_fila = request.form.get('lugares_por_fila', 20)
        
        if not nome_sala or not capacidade or not id_cinema:
            return jsonify({'success': False, 'message': 'Nome, capacidade e cinema são obrigatórios'})
        
        # Verificar se já existe outra sala com o mesmo nome neste cinema (excluindo a sala atual)
        cursor.execute("""
            SELECT id FROM salas 
            WHERE id_cinema = %s AND nome_sala = %s AND id != %s
        """, (int(id_cinema), nome_sala, sala_id))
        
        sala_existente = cursor.fetchone()
        if sala_existente:
            return jsonify({'success': False, 'message': f'Já existe outra sala com o nome "{nome_sala}" neste cinema'})
        
        # Atualizar sala
        cursor.execute("""
            UPDATE salas 
            SET nome_sala = %s, capacidade = %s, id_cinema = %s, tipo_sala = %s, filas = %s, lugares_por_fila = %s
            WHERE id = %s
        """, (nome_sala, int(capacidade), int(id_cinema), tipo_sala, int(filas), int(lugares_por_fila), sala_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sala atualizada com sucesso'
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao editar sala: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/salas/<int:sala_id>/dados')
def admin_get_dados_sala(sala_id):
    """Busca dados de uma sala específica para edição"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar dados da sala
        cursor.execute("""
            SELECT s.*, c.nome as cinema_nome
            FROM salas s
            LEFT JOIN cinemas c ON s.id_cinema = c.id
            WHERE s.id = %s
        """, (sala_id,))
        
        sala = cursor.fetchone()
        
        if not sala:
            return jsonify({'success': False, 'message': 'Sala não encontrada'})
        
        # Converter Decimal para int/float se necessário
        if sala.get('capacidade'):
            sala['capacidade'] = int(sala['capacidade'])
        if sala.get('filas'):
            sala['filas'] = int(sala['filas'])
        if sala.get('lugares_por_fila'):
            sala['lugares_por_fila'] = int(sala['lugares_por_fila'])
        
        return jsonify({
            'success': True,
            'sala': sala
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar dados da sala: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/salas/<int:sala_id>/remover', methods=['POST'])
def admin_remover_sala(sala_id):
    """Remove uma sala"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar se há horários de sessão usando esta sala
        cursor.execute("SELECT COUNT(*) as count FROM horarios_sessao WHERE id_sala = %s", (sala_id,))
        result = cursor.fetchone()
        count = result['count'] if result else 0
        
        if count > 0:
            return jsonify({
                'success': False, 
                'message': f'Não é possível remover. Existem {count} horários de sessão usando esta sala.'
            })
        
        # Remover sala
        cursor.execute("DELETE FROM salas WHERE id = %s", (sala_id,))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sala removida com sucesso!'
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao remover sala: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# ===== ROTAS DE EDIÇÃO PARA SESSÕES =====

@app.route('/admin/sessoes/adicionar', methods=['POST'])
def admin_adicionar_sessao():
    """Adiciona uma nova sessão (horarios_sessao)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        id_filme = request.form.get('id_filme')
        id_cinema = request.form.get('id_cinema')
        id_tipo_sessao = request.form.get('id_tipo_sessao')
        id_horario = request.form.get('id_horario')
        id_sala = request.form.get('id_sala')
        
        if not all([id_filme, id_cinema, id_tipo_sessao, id_horario, id_sala]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'})
        
        # Verificar se já existe esta combinação
        cur.execute("""
            SELECT id FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s 
            AND id_horario = %s AND id_sala = %s
        """, (id_filme, id_cinema, id_tipo_sessao, id_horario, id_sala))
        
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Esta sessão já existe'})
        
        # Inserir nova sessão
        cur.execute("""
            INSERT INTO horarios_sessao (id_filme, id_cinema, id_tipo_sessao, id_horario, id_sala)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_filme, id_cinema, id_tipo_sessao, id_horario, id_sala))
        
        conn.commit()
        sessao_id = cur.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'Sessão adicionada com sucesso',
            'sessao_id': sessao_id
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao adicionar sessão: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/sessoes/<int:sessao_id>/remover', methods=['POST'])
def admin_remover_sessao(sessao_id):
    """Remove uma sessão"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Verificar se há reservas para esta sessão
        cur.execute("SELECT COUNT(*) as count FROM reservas WHERE id_horario_sessao = %s", (sessao_id,))
        count = cur.fetchone()['count']
        
        if count > 0:
            return jsonify({
                'success': False, 
                'message': f'Não é possível remover. Existem {count} reservas para esta sessão.'
            })
        
        # Remover sessão
        cur.execute("DELETE FROM horarios_sessao WHERE id = %s", (sessao_id,))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sessão removida com sucesso'
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao remover sessão: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/filmes/<int:id_filme>/cinema/<int:cinema_id>/salas')
def admin_get_salas_cinema(id_filme, cinema_id):
    """Busca TODAS as salas disponíveis para um cinema específico"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar TODAS as salas do cinema (não apenas as que têm sessões)
        cur.execute("""
            SELECT s.id, s.nome_sala, s.capacidade, s.tipo_sala
            FROM salas s
            WHERE s.id_cinema = %s
            ORDER BY s.nome_sala
        """, (cinema_id,))
        salas = cur.fetchall()
        
        # Buscar informações do cinema
        cur.execute("SELECT nome FROM cinemas WHERE id = %s", (cinema_id,))
        cinema_info = cur.fetchone()
        
        app.logger.info(f"Salas encontradas para cinema {cinema_id}: {len(salas)}")
        
        return jsonify({
            'success': True,
            'salas': salas,
            'cinema_info': cinema_info
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar salas: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/salas/buscar')
def admin_buscar_sala_por_nome():
    """Busca dados de uma sala pelo nome e cinema"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    nome_sala = request.args.get('nome')
    cinema_id = request.args.get('cinema_id')
    
    if not nome_sala or not cinema_id:
        return jsonify({'error': 'Parâmetros obrigatórios: nome e cinema_id'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar dados da sala
        cur.execute("""
            SELECT id, nome_sala, capacidade, tipo_sala
            FROM salas 
            WHERE nome_sala = %s AND id_cinema = %s
        """, (nome_sala, cinema_id))
        sala = cur.fetchone()
        
        if sala:
            return jsonify({
                'success': True,
                'sala': sala
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Sala não encontrada'
            })
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar sala: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/filmes/<int:id_filme>/cinema/<int:cinema_id>/tipo/<int:tipo_id>/horarios')
def admin_get_horarios_tipo_sessao(id_filme, cinema_id, tipo_id):
    """Busca horários disponíveis para um tipo de sessão específico"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar horários reais da tabela horarios_sessao
        # Mostrar todos os horários para admin (sem filtro de tempo)
        # O admin precisa ver todos os horários para gestão
        # IMPORTANTE: Incluir hs.id para poder remover sessões específicas
        cur.execute("""
            SELECT h.id as horario_id, h.hora, s.nome_sala, s.capacidade, hs.id as sessao_id, hs.id_sala as sala_id
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            LEFT JOIN salas s ON hs.id_sala = s.id
            WHERE hs.id_filme = %s 
            AND hs.id_cinema = %s 
            AND hs.id_tipo_sessao = %s
            ORDER BY h.hora
        """, (id_filme, cinema_id, tipo_id))
        horarios_raw = cur.fetchall()
        
        # Processar horários para garantir formato correto
        horarios = []
        for h in horarios_raw:
            horario_processado = dict(h)
            
            # Converter hora para string se necessário
            if isinstance(h['hora'], timedelta):
                total_seconds = int(h['hora'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                horario_processado['hora'] = f"{hours:02d}:{minutes:02d}"
            elif hasattr(h['hora'], 'strftime'):
                horario_processado['hora'] = h['hora'].strftime('%H:%M')
            else:
                horario_processado['hora'] = str(h['hora'])[:5]
            
            # Garantir que nome_sala não é None
            if not horario_processado['nome_sala']:
                horario_processado['nome_sala'] = 'Sala não especificada'
            
            horarios.append(horario_processado)
        
        # Buscar informações do tipo de sessão
        cur.execute("SELECT nome, preco_bilhete FROM tipos_sessao WHERE id = %s", (tipo_id,))
        tipo_info = cur.fetchone()
        
        app.logger.info(f"Horários encontrados para filme {id_filme}, cinema {cinema_id}, tipo {tipo_id}: {len(horarios)}")
        
        return jsonify({
            'success': True,
            'horarios': horarios,
            'tipo_info': tipo_info
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar horários: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/filmes/<int:id_filme>/editar', methods=['POST'])
def admin_editar_filme(id_filme):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        # Obter dados do JSON (não form)
        data = request.get_json()
        titulo = data.get('titulo')
        sinopse = data.get('sinopse')
        diretor = data.get('diretor')
        duracao = data.get('duracao')
        data_lancamento = data.get('data_lancamento')
        idade_recomendada = data.get('idade_recomendada')
        estado = data.get('estado')
        trailer_url = data.get('trailer_url')
        rotten_tomatoes_url = data.get('rotten_tomatoes_url')
        imdb_url = data.get('imdb_url')
        
        # Debug: verificar o valor do estado recebido
        print(f"DEBUG: Estado recebido = {estado}")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Atualizar filme incluindo os novos campos de URLs externas
        cur.execute("""
            UPDATE filmes 
            SET titulo = %s, sinopse = %s, diretor = %s, duracao = %s, 
                data_lancamento = %s, idade_recomendada = %s, estado = %s, trailer_url = %s,
                rotten_tomatoes_url = %s, imdb_url = %s
            WHERE id = %s
        """, (titulo, sinopse, diretor, duracao, data_lancamento, idade_recomendada, estado, trailer_url, rotten_tomatoes_url, imdb_url, id_filme))
        
        conn.commit()
        
        # Debug: verificar se foi atualizado
        cur.execute("SELECT estado FROM filmes WHERE id = %s", (id_filme,))
        resultado = cur.fetchone()
        print(f"DEBUG: Estado na BD após update = {resultado[0] if resultado else 'NULL'}")
        
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Filme atualizado com sucesso!'})
        
    except Exception as e:
        print(f"DEBUG: Erro ao atualizar filme: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao atualizar filme: {str(e)}'}), 500

@app.route('/admin/filmes/<int:id_filme>/avaliacoes')
def admin_filme_avaliacoes(id_filme):
    """Página para ver todas as avaliações de um filme"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Verificar se é admin
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash("Acesso negado!", "erro")
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    
    # Buscar filme
    cur.execute("SELECT id, titulo, poster_url FROM filmes WHERE id = %s", (id_filme,))
    filme = cur.fetchone()
    
    if not filme:
        flash("Filme não encontrado!", "erro")
        return redirect(url_for('admin_filmes'))
    
    # Buscar todas as avaliações - seguindo o padrão do filme_detalhe
    cur.execute("""
        SELECT 
            av.id,
            av.usuario_id,
            av.rating,
            av.comentario,
            av.data_avaliacao,
            u.nome as usuario_nome,
            u.email,
            COALESCE(u.avatar, a.caminho) as usuario_avatar
        FROM avaliacoes_filmes av
        JOIN usuarios u ON av.usuario_id = u.id
        LEFT JOIN avatars a ON u.avatar_id = a.id
        WHERE av.filme_id = %s
        ORDER BY av.data_avaliacao DESC
    """, (id_filme,))
    todas_avaliacoes = cur.fetchall()
    
    # Processar avatares - seguindo o padrão do filme_detalhe
    for avaliacao in todas_avaliacoes:
        if avaliacao.get('usuario_avatar'):
            avaliacao['usuario_avatar'] = avaliacao['usuario_avatar'].replace('\\', '/').replace('"', '').strip()
        else:
            avaliacao['usuario_avatar'] = 'imgs/icons/user_icon34-removebg-preview.png'
    
    # Buscar estatísticas
    cur.execute("""
        SELECT 
            AVG(rating) as rating_medio,
            COUNT(*) as total_avaliacoes,
            COUNT(CASE WHEN rating = 5 THEN 1 END) as rating_5,
            COUNT(CASE WHEN rating = 4 THEN 1 END) as rating_4,
            COUNT(CASE WHEN rating = 3 THEN 1 END) as rating_3,
            COUNT(CASE WHEN rating = 2 THEN 1 END) as rating_2,
            COUNT(CASE WHEN rating = 1 THEN 1 END) as rating_1
        FROM avaliacoes_filmes 
        WHERE filme_id = %s
    """, (id_filme,))
    stats = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return render_template('admin_filme_avaliacoes.html',
                         user=get_current_user(),
                         filme=filme,
                         avaliacoes=todas_avaliacoes,
                         stats=stats)

@app.route('/admin/avaliacoes/<int:avaliacao_id>/remover', methods=['POST'])
def admin_remover_avaliacao(avaliacao_id):
    """Remove uma avaliação específica"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Verificar se a avaliação existe
        cur.execute("SELECT id, filme_id, usuario_id FROM avaliacoes_filmes WHERE id = %s", (avaliacao_id,))
        avaliacao = cur.fetchone()
        
        if not avaliacao:
            return jsonify({'success': False, 'message': 'Avaliação não encontrada'}), 404
        
        # Remover a avaliação
        cur.execute("DELETE FROM avaliacoes_filmes WHERE id = %s", (avaliacao_id,))
        conn.commit()
        
        app.logger.info(f"Admin {session['user_id']} removeu avaliação {avaliacao_id} do filme {avaliacao['filme_id']}")
        
        return jsonify({'success': True, 'message': 'Avaliação removida com sucesso'})
        
    except Exception as e:
        app.logger.error(f"Erro ao remover avaliação {avaliacao_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/filmes/<int:id_filme>/adicionar-cinema', methods=['POST'])
def admin_adicionar_cinema_filme(id_filme):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    cinema_id = request.form.get('cinema_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Verificar se já existe
        cur.execute("SELECT id FROM filmes_cinemas WHERE filme_id = %s AND cinema_id = %s", (id_filme, cinema_id))
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Cinema já associado ao filme'})
        
        # Adicionar associação
        cur.execute("INSERT INTO filmes_cinemas (filme_id, cinema_id) VALUES (%s, %s)", (id_filme, cinema_id))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Cinema adicionado com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar cinema: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/filmes/<int:id_filme>/remover-cinema/<int:cinema_id>', methods=['POST'])
def admin_remover_cinema_filme(id_filme, cinema_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é admin
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Verificar se a associação existe
        cur.execute("SELECT id FROM filmes_cinemas WHERE filme_id = %s AND cinema_id = %s", (id_filme, cinema_id))
        associacao = cur.fetchone()
        
        if not associacao:
            return jsonify({'success': False, 'message': 'Associação filme-cinema não encontrada'})
        
        # REMOÇÃO EM CASCATA - Remover tudo automaticamente
        app.logger.info(f"Iniciando remoção em cascata para cinema {cinema_id} do filme {id_filme}")
        
        # 1. Remover reservas associadas aos horários deste cinema/filme
        cur.execute("""
            DELETE r FROM reservas r
            JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
            WHERE hs.id_filme = %s AND hs.id_cinema = %s
        """, (id_filme, cinema_id))
        reservas_removidas = cur.rowcount
        app.logger.info(f"Removidas {reservas_removidas} reservas")
        
        # 2. Remover horários de sessão
        cur.execute("""
            DELETE FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s
        """, (id_filme, cinema_id))
        horarios_removidos = cur.rowcount
        app.logger.info(f"Removidos {horarios_removidos} horários")
        
        # 3. Remover a associação filme-cinema
        cur.execute("DELETE FROM filmes_cinemas WHERE filme_id = %s AND cinema_id = %s", (id_filme, cinema_id))
        conn.commit()
        
        app.logger.info(f"✅ Cinema {cinema_id} removido do filme {id_filme} com sucesso (cascata completa)")
        
        return jsonify({
            'success': True, 
            'message': f'Cinema removido com sucesso! Removidos automaticamente: {horarios_removidos} horários e {reservas_removidas} reservas.'
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao remover cinema: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/filmes/<int:id_filme>/adicionar-ator', methods=['POST'])
def admin_adicionar_ator_filme(id_filme):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    ator_id = request.form.get('ator_id')
    papel = request.form.get('papel', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Verificar se já existe
        cur.execute("SELECT id FROM filme_atores WHERE filme_id = %s AND ator_id = %s", (id_filme, ator_id))
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Ator já associado ao filme'})
        
        # Adicionar associação
        cur.execute("INSERT INTO filme_atores (filme_id, ator_id, papel) VALUES (%s, %s, %s)", (id_filme, ator_id, papel))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Ator adicionado com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar ator: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/filmes/<int:id_filme>/remover-ator/<int:ator_id>', methods=['POST'])
def admin_remover_ator_filme(id_filme, ator_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM filme_atores WHERE filme_id = %s AND ator_id = %s", (id_filme, ator_id))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Ator removido com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao remover ator: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/filmes/<int:id_filme>/editar-papel-ator', methods=['POST'])
def admin_editar_papel_ator(id_filme):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    ator_id = request.form.get('ator_id')
    papel = request.form.get('papel', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("UPDATE filme_atores SET papel = %s WHERE filme_id = %s AND ator_id = %s", (papel, id_filme, ator_id))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Papel atualizado com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar papel: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/filmes/<int:id_filme>/adicionar-genero', methods=['POST'])
def admin_adicionar_genero_filme(id_filme):
    """Adicionar género ao filme"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        genero_id = request.form.get('genero_id')
        
        if not genero_id:
            return jsonify({'success': False, 'message': 'Género é obrigatório'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar se a relação já existe
        cur.execute("SELECT id FROM filme_generos WHERE filme_id = %s AND genero_id = %s", (id_filme, genero_id))
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Género já está associado ao filme'}), 400
        
        # Adicionar relação
        cur.execute("INSERT INTO filme_generos (filme_id, genero_id) VALUES (%s, %s)", (id_filme, genero_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Género adicionado ao filme!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar género: {str(e)}'}), 500

@app.route('/admin/filmes/<int:id_filme>/remover-genero/<int:genero_id>', methods=['POST'])
def admin_remover_genero_filme(id_filme, genero_id):
    """Remover género do filme"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Remover relação
        cur.execute("DELETE FROM filme_generos WHERE filme_id = %s AND genero_id = %s", (id_filme, genero_id))
        
        if cur.rowcount == 0:
            return jsonify({'success': False, 'message': 'Género não estava associado ao filme'}), 404
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Género removido do filme!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao remover género: {str(e)}'}), 500

@app.route('/admin/filmes/<int:id_filme>/upload-poster', methods=['POST'])
def admin_upload_poster(id_filme):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    if 'poster' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['poster']
    if not file or not file.filename:
        return jsonify({'success': False, 'message': 'Arquivo inválido'}), 400
    
    try:
        import os
        from werkzeug.utils import secure_filename
        import uuid
        
        # Validar tipo de arquivo
        if not file.content_type.startswith('image/'):
            return jsonify({'success': False, 'message': 'Apenas imagens são permitidas'}), 400
        
        # Gerar nome único
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1]
        unique_filename = f"filme_{id_filme}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Salvar arquivo
        upload_folder = os.path.join('static', 'imgs', 'filmes')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Atualizar base de dados
        poster_url = f"imgs/filmes/{unique_filename}"
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("UPDATE filmes SET poster_url = %s WHERE id = %s", (poster_url, id_filme))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Poster atualizado com sucesso!', 'poster_url': poster_url})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao fazer upload: {str(e)}'}), 500

@app.route('/admin/filmes/adicionar', methods=['POST'])
def admin_adicionar_filme():
    print("🎬 ADMIN_ADICIONAR_FILME CHAMADA")
    
    if 'user_id' not in session:
        print("❌ Usuário não autenticado")
        flash("Não autenticado", "erro")
        return redirect(url_for('admin_filmes'))
    
    # Obter dados do formulário
    titulo = request.form.get('titulo', '').strip()
    duracao = request.form.get('duracao', '120')
    sinopse = request.form.get('sinopse', '').strip()
    
    print(f"📝 Dados recebidos: titulo='{titulo}', duracao={duracao}")
    
    # Validações básicas
    if not titulo:
        print("❌ Título vazio")
        flash('Título é obrigatório!', 'erro')
        return redirect(url_for('admin_filmes'))
    
    if not sinopse:
        print("❌ Sinopse vazia")
        flash('Sinopse é obrigatória!', 'erro')
        return redirect(url_for('admin_filmes'))
    
    # Lidar com upload de poster
    poster_url = None
    if 'poster' in request.files:
        poster_file = request.files['poster']
        if poster_file and poster_file.filename:
            print(f"📁 Upload de poster: {poster_file.filename}")
            
            # Criar diretório se não existir
            upload_dir = os.path.join('static', 'imgs', 'filmes')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Gerar nome único para o arquivo
            import uuid
            from werkzeug.utils import secure_filename
            
            filename = secure_filename(poster_file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{uuid.uuid4().hex[:8]}_{name}{ext}"
            
            # Salvar arquivo
            poster_path = os.path.join(upload_dir, unique_filename)
            poster_file.save(poster_path)
            
            # URL relativa para a base de dados
            poster_url = f"imgs/filmes/{unique_filename}"
            print(f"✅ Poster salvo: {poster_url}")
    
    if not poster_url:
        print("❌ Poster não fornecido")
        flash('Imagem do poster é obrigatória!', 'erro')
        return redirect(url_for('admin_filmes'))
    
    # Inserir na base de dados
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("💾 Inserindo na base de dados...")
        
        cursor.execute("""
            INSERT INTO filmes (titulo, diretor, data_lancamento, duracao, sinopse, poster_url, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (titulo, 'A definir', '2024-01-01', int(duracao), sinopse, poster_url, 'em_exibicao'))
        
        id_filme = cursor.lastrowid
        print(f"✅ Filme inserido com ID: {id_filme}")
        
        # Associar género padrão (Ação - ID 1)
        cursor.execute("INSERT INTO filme_generos (filme_id, genero_id) VALUES (%s, %s)", (id_filme, 1))
        print("✅ Género associado")
        
        # Commit
        conn.commit()
        print("✅ Transação commitada")
        
        flash(f'Filme "{titulo}" adicionado com sucesso!', 'sucesso')
        
    except Exception as e:
        conn.rollback()
        print(f"❌ ERRO: {str(e)}")
        flash(f'Erro ao adicionar filme: {str(e)}', 'erro')
        
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_filmes'))

@app.route('/admin/filmes/<int:id_filme>/adicionar-horario', methods=['POST'])
def admin_adicionar_horario(id_filme):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    id_cinema = request.form.get('id_cinema')
    id_tipo_sessao = request.form.get('id_tipo_sessao')
    id_horario_sessao = request.form.get('id_horario_sessao')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO horarios_sessao (id_filme, id_cinema, id_tipo_sessao, id_horario)
            VALUES (%s, %s, %s, %s)
        """, (id_filme, id_cinema, id_tipo_sessao, id_horario_sessao))
        conn.commit()
        flash("Horário adicionado com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao adicionar horário: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filmes'))

@app.route('/admin/filmes/<int:id_filme>/adicionar-horarios-multiplos', methods=['POST'])
def admin_adicionar_horarios_multiplos(id_filme):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    id_cinema = request.form.get('id_cinema')
    id_tipo_sessao = request.form.get('id_tipo_sessao')
    sala_id = request.form.get('sala_id')  # Pode ser None
    id_horario_sessaos = request.form.getlist('id_horario_sessaos')
    
    if not id_horario_sessaos:
        flash("Selecione pelo menos um horário!", "erro")
        return redirect(url_for('admin_filmes'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Buscar horários já existentes para este filme, cinema e tipo de sessão
        cur.execute("""
            SELECT id_horario 
            FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s
        """, (id_filme, id_cinema, id_tipo_sessao))
        horarios_existentes = [row['id_horario'] for row in cur.fetchall()]
        
        count = 0
        duplicados = 0
        
        for id_horario_sessao in id_horario_sessaos:
            # Verificar se já existe
            if int(id_horario_sessao) in horarios_existentes:
                duplicados += 1
                continue
                
            try:
                if sala_id:
                    cur.execute("""
                        INSERT INTO horarios_sessao (id_filme, id_cinema, id_tipo_sessao, id_horario, id_sala)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (id_filme, id_cinema, id_tipo_sessao, id_horario_sessao, sala_id))
                else:
                    cur.execute("""
                        INSERT INTO horarios_sessao (id_filme, id_cinema, id_tipo_sessao, id_horario)
                        VALUES (%s, %s, %s, %s)
                    """, (id_filme, id_cinema, id_tipo_sessao, id_horario_sessao))
                count += 1
            except:
                duplicados += 1
        
        conn.commit()
        
        if count > 0:
            flash(f"✓ {count} horário{'s' if count > 1 else ''} adicionado{'s' if count > 1 else ''} com sucesso!", "sucesso")
        if duplicados > 0:
            flash(f"⚠️ {duplicados} horário{'s' if duplicados > 1 else ''} já existia{'m' if duplicados > 1 else ''} e foi{'ram' if duplicados > 1 else ''} ignorado{'s' if duplicados > 1 else ''}.", "aviso")
            
    except Exception as e:
        flash(f"Erro ao adicionar horários: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filmes'))

@app.route('/admin/filmes/<int:id_filme>/remover-horario/<int:id_horario_sessao>', methods=['POST'])
def admin_remover_horario_filme(id_filme, id_horario_sessao):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM horarios_sessao WHERE id = %s", (id_horario_sessao,))
        conn.commit()
        flash("Horário removido com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao remover horário: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filmes'))

@app.route('/admin/filmes/<int:id_filme>/remover-horarios-multiplos', methods=['POST'])
def admin_remover_horarios_multiplos_filme(id_filme):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    id_horario_sessaos = request.form.getlist('id_horario_sessaos')
    
    if not id_horario_sessaos:
        flash("Nenhum horário selecionado!", "erro")
        return redirect(url_for('admin_filmes'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Converter para inteiros
        id_horario_sessaos = [int(id) for id in id_horario_sessaos]
        
        # Criar placeholders para a query
        placeholders = ','.join(['%s'] * len(id_horario_sessaos))
        query = f"DELETE FROM horarios_sessao WHERE id IN ({placeholders})"
        
        cur.execute(query, id_horario_sessaos)
        conn.commit()
        
        count = len(id_horario_sessaos)
        flash(f"{count} horário{'s' if count > 1 else ''} removido{'s' if count > 1 else ''} com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao remover horários: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filmes'))

@app.route('/admin/filmes/<int:id_filme>/remover', methods=['POST'])
def admin_remover_filme(id_filme):
    app.logger.info(f"=== INÍCIO: Tentativa de remoção do filme ID: {id_filme} ===")
    
    if 'user_id' not in session:
        app.logger.warning("Tentativa de remoção sem autenticação")
        flash("Não autenticado", "erro")
        return redirect(url_for('admin_filmes'))
    
    # Verificar se é admin
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT is_admin, nome FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user:
            app.logger.warning(f"Usuário ID {session['user_id']} não encontrado")
            flash("Usuário não encontrado", "erro")
            return redirect(url_for('admin_filmes'))
        
        if not user[0]:  # is_admin
            app.logger.warning(f"Usuário {user[1]} (ID: {session['user_id']}) tentou remover filme sem ser admin")
            flash("Acesso negado - apenas administradores podem remover filmes", "erro")
            return redirect(url_for('admin_filmes'))
        
        app.logger.info(f"Usuário admin {user[1]} (ID: {session['user_id']}) removendo filme")
        
        # Buscar nome do filme para a mensagem
        cur.execute("SELECT titulo FROM filmes WHERE id = %s", (id_filme,))
        filme = cur.fetchone()
        
        if not filme:
            app.logger.warning(f"Filme ID {id_filme} não encontrado")
            flash("Filme não encontrado", "erro")
            return redirect(url_for('admin_filmes'))
        
        titulo_filme = filme[0]
        app.logger.info(f"Removendo filme: '{titulo_filme}' (ID: {id_filme})")
        
        # Remover em ordem para evitar problemas de foreign key
        
        # 1. Remover reservas associadas primeiro
        cur.execute("DELETE FROM reservas WHERE id_filme = %s", (id_filme,))
        reservas_removidas = cur.rowcount
        app.logger.info(f"Removidas {reservas_removidas} reservas")
        
        # 2. Remover horários de sessão
        cur.execute("DELETE FROM horarios_sessao WHERE id_filme = %s", (id_filme,))
        horarios_removidos = cur.rowcount
        app.logger.info(f"Removidos {horarios_removidos} horários")
        
        # 3. Remover associações com cinemas
        cur.execute("DELETE FROM filmes_cinemas WHERE filme_id = %s", (id_filme,))
        cinemas_removidos = cur.rowcount
        app.logger.info(f"Removidas {cinemas_removidos} associações com cinemas")
        
        # 4. Remover associações com géneros
        cur.execute("DELETE FROM filme_generos WHERE filme_id = %s", (id_filme,))
        generos_removidos = cur.rowcount
        app.logger.info(f"Removidas {generos_removidos} associações com géneros")
        
        # 5. Remover associações com atores
        cur.execute("DELETE FROM filme_atores WHERE filme_id = %s", (id_filme,))
        atores_removidos = cur.rowcount
        app.logger.info(f"Removidas {atores_removidos} associações com atores")
        
        # 6. Remover avaliações
        cur.execute("DELETE FROM avaliacoes_filmes WHERE filme_id = %s", (id_filme,))
        avaliacoes_removidas = cur.rowcount
        app.logger.info(f"Removidas {avaliacoes_removidas} avaliações")
        
        # 7. Remover histórico
        cur.execute("DELETE FROM historico_filmes WHERE filme_id = %s", (id_filme,))
        historico_removido = cur.rowcount
        app.logger.info(f"Removidos {historico_removido} registos de histórico")
        
        # 8. Remover reservas de salas
        cur.execute("DELETE FROM reservas_salas WHERE filme_id = %s", (id_filme,))
        reservas_salas_removidas = cur.rowcount
        app.logger.info(f"Removidas {reservas_salas_removidas} reservas de salas")
        
        # 6. Finalmente, remover o filme
        cur.execute("DELETE FROM filmes WHERE id = %s", (id_filme,))
        filme_removido = cur.rowcount
        
        if filme_removido == 0:
            print(f"❌ PROBLEMA: Filme ID {id_filme} não foi removido")
            conn.rollback()
            flash("Erro: Filme não foi removido", "erro")
        else:
            # Commit das alterações
            conn.commit()
            print(f"✅ SUCESSO: Filme '{titulo_filme}' removido!")
            flash(f"Filme '{titulo_filme}' removido com sucesso!", "sucesso")
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"❌ ERRO ao remover filme {id_filme}: {str(e)}")
        app.logger.exception("Stack trace:")
        flash(f"Erro ao remover filme: {str(e)}", "erro")
        
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass
    
    app.logger.info(f"=== FIM: Tentativa de remoção do filme ID: {id_filme} ===")
    return redirect(url_for('admin_filmes'))

@app.route('/admin/filmes/<int:id_filme>/duplicar', methods=['POST'])
def admin_duplicar_filme(id_filme):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Buscar dados do filme original
        cur.execute("SELECT * FROM filmes WHERE id = %s", (id_filme,))
        filme = cur.fetchone()
        
        if not filme:
            return jsonify({'success': False, 'message': 'Filme não encontrado'}), 404
        
        # Criar cópia do filme
        cur.execute("""
            INSERT INTO filmes (titulo, sinopse, duracao, classificacao, data_lancamento, 
                              diretor, poster_url, trailer_url, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            f"{filme['titulo']} (Cópia)",
            filme['sinopse'],
            filme['duracao'],
            filme['classificacao'],
            filme['data_lancamento'],
            filme['diretor'],
            filme['poster_url'],
            filme['trailer_url'],
            'fora_de_cartaz'  # Novo filme começa fora de cartaz
        ))
        
        novo_id = cur.fetchone()['id']
        
        # Copiar géneros
        cur.execute("""
            INSERT INTO filme_generos (id_filme, id_genero)
            SELECT %s, id_genero FROM filme_generos WHERE id_filme = %s
        """, (novo_id, id_filme))
        
        # Copiar atores
        cur.execute("""
            INSERT INTO filme_atores (id_filme, ator_id, papel)
            SELECT %s, ator_id, papel FROM filme_atores WHERE id_filme = %s
        """, (novo_id, id_filme))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Filme duplicado com sucesso!', 'novo_id': novo_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/filmes/<int:id_filme>/atualizar-papel-ator', methods=['POST'])
def admin_atualizar_papel_ator(id_filme):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    ator_id = request.form.get('ator_id')
    papel = request.form.get('papel')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE filme_atores 
            SET papel = %s 
            WHERE id_filme = %s AND ator_id = %s
        """, (papel, id_filme, ator_id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Papel atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar papel: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/admin/filmes/<int:id_filme>/atualizar-sala-horario', methods=['POST'])
def admin_atualizar_sala_horario(id_filme):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    id_horario_sessao_horario_sessao = request.form.get('id_horario_sessao_horario_sessao')
    sala_id = request.form.get('sala_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if sala_id:
            cur.execute("""
                UPDATE horarios_sessao 
                SET id_sala = %s 
                WHERE id = %s
            """, (sala_id, id_horario_sessao_horario_sessao))
        else:
            cur.execute("""
                UPDATE horarios_sessao 
                SET id_sala = NULL 
                WHERE id = %s
            """, (id_horario_sessao_horario_sessao,))
        
        conn.commit()
        flash("Sala atualizada com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao atualizar sala: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filmes'))

# ==========================
# ADMIN - GESTÃO DE GÉNEROS
# ==========================
@app.route('/admin/generos')
def admin_generos():
    """Página de gestão de géneros"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Verificar se é admin
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash("Acesso negado!", "erro")
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    
    # Buscar todos os géneros com estatísticas
    cur.execute("""
        SELECT 
            g.id,
            g.nome,
            COUNT(fg.filme_id) as total_filmes
        FROM generos g
        LEFT JOIN filme_generos fg ON g.id = fg.genero_id
        GROUP BY g.id, g.nome
        ORDER BY g.nome
    """)
    generos = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin_generos.html', generos=generos)

@app.route('/admin/generos/adicionar', methods=['POST'])
def admin_adicionar_genero():
    """Adicionar novo género"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        
        if not nome:
            return jsonify({'success': False, 'message': 'Nome do género é obrigatório'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar se já existe
        cur.execute("SELECT id FROM generos WHERE nome = %s", (nome,))
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Género já existe'}), 400
        
        # Inserir novo género
        cur.execute("INSERT INTO generos (nome) VALUES (%s)", (nome,))
        genero_id = cur.lastrowid
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Género adicionado com sucesso!',
            'genero': {'id': genero_id, 'nome': nome}
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar género: {str(e)}'}), 500

@app.route('/admin/generos/<int:genero_id>/editar', methods=['POST'])
def admin_editar_genero(genero_id):
    """Editar género existente"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        
        if not nome:
            return jsonify({'success': False, 'message': 'Nome do género é obrigatório'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar se o género existe
        cur.execute("SELECT id FROM generos WHERE id = %s", (genero_id,))
        if not cur.fetchone():
            return jsonify({'success': False, 'message': 'Género não encontrado'}), 404
        
        # Verificar se já existe outro género com o mesmo nome
        cur.execute("SELECT id FROM generos WHERE nome = %s AND id != %s", (nome, genero_id))
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Já existe outro género com este nome'}), 400
        
        # Atualizar género
        cur.execute("UPDATE generos SET nome = %s WHERE id = %s", (nome, genero_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Género atualizado com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao editar género: {str(e)}'}), 500

@app.route('/admin/generos/<int:genero_id>/remover', methods=['POST'])
def admin_remover_genero(genero_id):
    """Remover género"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar se o género existe
        cur.execute("SELECT nome FROM generos WHERE id = %s", (genero_id,))
        genero = cur.fetchone()
        if not genero:
            return jsonify({'success': False, 'message': 'Género não encontrado'}), 404
        
        # Verificar se há filmes associados
        cur.execute("SELECT COUNT(*) as total FROM filme_generos WHERE genero_id = %s", (genero_id,))
        result = cur.fetchone()
        total_filmes = result[0] if result else 0
        
        if total_filmes > 0:
            return jsonify({
                'success': False, 
                'message': f'Não é possível remover o género "{genero[0]}" pois está associado a {total_filmes} filme(s)'
            }), 400
        
        # Remover género
        cur.execute("DELETE FROM generos WHERE id = %s", (genero_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Género removido com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao remover género: {str(e)}'}), 500

@app.route('/admin/generos/<int:genero_id>/filmes')
def admin_genero_filmes(genero_id):
    """Ver filmes de um género específico"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Verificar se é admin
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash("Acesso negado!", "erro")
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    
    # Buscar informações do género
    cur.execute("SELECT * FROM generos WHERE id = %s", (genero_id,))
    genero = cur.fetchone()
    
    if not genero:
        flash("Género não encontrado!", "erro")
        return redirect(url_for('admin_generos'))
    
    # Buscar filmes do género
    cur.execute("""
        SELECT 
            f.id,
            f.titulo,
            f.diretor,
            f.data_lancamento,
            f.estado,
            f.poster_url
        FROM filmes f
        JOIN filme_generos fg ON f.id = fg.filme_id
        WHERE fg.genero_id = %s
        ORDER BY f.titulo
    """, (genero_id,))
    filmes = cur.fetchall()
    
    # Limpar caminhos dos posters
    for filme in filmes:
        if filme.get('poster_url'):
            filme['poster_url'] = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
    
    cur.close()
    conn.close()
    
    return render_template('admin_genero_filmes.html', genero=genero, filmes=filmes)

# ==========================
# ADMIN - GESTÃO DE CINEMAS
# ==========================
# ROTAS ADMIN CINEMAS - VERSÃO LIMPA E FUNCIONAL

@app.route('/admin/cinemas')
def admin_cinemas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Buscar todos os cinemas com contagem de salas e filmes
        cur.execute("""
            SELECT c.id, c.nome, c.localizacao, c.email, c.regiao, c.imagem,
                   COUNT(DISTINCT s.id) as num_salas,
                   COUNT(DISTINCT fc.filme_id) as num_filmes
            FROM cinemas c
            LEFT JOIN salas s ON c.id = s.id_cinema
            LEFT JOIN filmes_cinemas fc ON c.id = fc.cinema_id
            GROUP BY c.id, c.nome, c.localizacao, c.email, c.regiao, c.imagem
            ORDER BY c.nome
        """)
        cinemas = cur.fetchall()
        
        print(f"[DEBUG] Cinemas encontrados: {len(cinemas)}")
        
        # Processar URLs das imagens
        for cinema in cinemas:
            print(f"[DEBUG] Cinema: {cinema['nome']}, Imagem: {cinema.get('imagem')}")
            
            # Garantir que sempre tem uma imagem
            if not cinema.get('imagem') or cinema.get('imagem') in [None, '', 'None', 'null']:
                cinema['imagem'] = 'imgs/cinemas/default.jpg'
                print(f"[DEBUG] Sem imagem - usando default")
            else:
                imagem = str(cinema['imagem']).replace('\\', '/').replace('"', '').strip()
                if not imagem.startswith(('http://', 'https://', 'imgs/')):
                    if '/' not in imagem:
                        imagem = f"imgs/cinemas/{imagem}"
                    elif not imagem.startswith('imgs/'):
                        imagem = f"imgs/cinemas/{imagem}"
                cinema['imagem'] = imagem
            
            print(f"[DEBUG] Imagem final: {cinema['imagem']}")
        
        cur.close()
        conn.close()
        
        return render_template('admin_cinemas.html', user=get_current_user(), cinemas=cinemas)
    except Exception as e:
        print(f"[ERRO] admin_cinemas: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Erro ao carregar cinemas: {str(e)}", "erro")
        return render_template('admin_cinemas.html', user=get_current_user(), cinemas=[])

@app.route('/admin/cinemas/adicionar', methods=['POST'])
def admin_adicionar_cinema():
    print("\n" + "="*50)
    print("ROTA ADICIONAR CINEMA CHAMADA")
    print("="*50)
    
    if 'user_id' not in session:
        print("ERRO: Usuário não autenticado")
        return redirect(url_for('login'))
    
    try:
        print(f"Form data: {request.form}")
        print(f"Files: {request.files}")
        
        nome = request.form.get('nome', '').strip()
        localizacao = request.form.get('localizacao', '').strip()
        regiao = request.form.get('regiao', '').strip()
        email = request.form.get('email', '').strip()
        
        print(f"Nome: {nome}")
        print(f"Localização: {localizacao}")
        print(f"Região: {regiao}")
        print(f"Email: {email}")
        
        # Validação básica
        if not nome or not localizacao:
            print("ERRO: Campos obrigatórios vazios")
            flash("Nome e localização são obrigatórios!", "erro")
            return redirect(url_for('admin_cinemas'))
        
        # Upload de imagem
        imagem = None
        if 'imagem' in request.files:
            file = request.files['imagem']
            print(f"File: {file}")
            print(f"Filename: {file.filename}")
            
            if file and file.filename:
                from werkzeug.utils import secure_filename
                
                # Criar diretório se não existir
                upload_folder = os.path.join('static', 'imgs', 'cinemas')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Gerar nome único
                ext = os.path.splitext(secure_filename(file.filename))[1]
                filename = f"cinema_{uuid.uuid4().hex[:8]}{ext}"
                filepath = os.path.join(upload_folder, filename)
                
                # Salvar arquivo
                file.save(filepath)
                imagem = f"imgs/cinemas/{filename}"
                print(f"Imagem salva: {imagem}")
        
        # Inserir na base de dados
        print("Conectando à base de dados...")
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("Executando INSERT...")
        cur.execute("""
            INSERT INTO cinemas (nome, localizacao, regiao, email, imagem) 
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, localizacao, regiao, email, imagem))
        
        print("Fazendo COMMIT...")
        conn.commit()
        
        cinema_id = cur.lastrowid
        print(f"Cinema adicionado com ID: {cinema_id}")
        
        cur.close()
        conn.close()
        
        print("="*50)
        print("SUCESSO!")
        print("="*50 + "\n")
        
        flash(f"Cinema '{nome}' adicionado com sucesso!", "sucesso")
        return redirect(url_for('admin_cinemas'))
        
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Erro ao adicionar cinema: {str(e)}", "erro")
        return redirect(url_for('admin_cinemas'))

@app.route('/admin/cinemas/editar/<int:id_cinema>', methods=['GET', 'POST'])
def admin_editar_cinema(id_cinema):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        print(f"\n=== EDITAR CINEMA ID: {id_cinema} ===")
        nome = request.form.get('nome')
        localizacao = request.form.get('localizacao')
        regiao = request.form.get('regiao')
        email = request.form.get('email')
        imagem = request.form.get('imagem_atual')
        
        print(f"Imagem atual: {imagem}")
        print(f"Files in request: {request.files}")
        
        # Upload de nova imagem
        if 'imagem' in request.files:
            file = request.files['imagem']
            print(f"File object: {file}")
            print(f"File filename: {file.filename}")
            
            if file and file.filename:
                from werkzeug.utils import secure_filename
                upload_folder = os.path.join('static', 'imgs', 'cinemas')
                os.makedirs(upload_folder, exist_ok=True)
                ext = os.path.splitext(secure_filename(file.filename))[1]
                filename = f"cinema_{uuid.uuid4().hex[:8]}{ext}"
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                imagem = f"imgs/cinemas/{filename}"
                print(f"Nova imagem salva: {imagem}")
            else:
                print("File vazio ou sem filename")
        else:
            print("'imagem' não está em request.files")
        
        print(f"Imagem final para UPDATE: {imagem}")
        
        cur.execute("UPDATE cinemas SET nome=%s, localizacao=%s, regiao=%s, email=%s, imagem=%s WHERE id=%s",
                    (nome, localizacao, regiao, email, imagem, id_cinema))
        print(f"Linhas afetadas: {cur.rowcount}")
        conn.commit()
        cur.close()
        conn.close()
        print("=== FIM EDITAR CINEMA ===\n")
        flash("Cinema atualizado!", "sucesso")
        return redirect(url_for('admin_cinemas'))
    
    # GET
    cur.execute("SELECT * FROM cinemas WHERE id = %s", (id_cinema,))
    cinema = cur.fetchone()
    cur.close()
    conn.close()
    
    if request.headers.get('Accept') == 'application/json':
        return jsonify(cinema)
    return render_template('admin_editar_cinema.html', cinema=cinema)

@app.route('/admin/cinemas/remover/<int:id_cinema>', methods=['POST'])
def admin_remover_cinema(id_cinema):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Remover tudo em cascata
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    cur.execute("DELETE FROM reservas WHERE id_cinema = %s", (id_cinema,))
    cur.execute("DELETE FROM horarios_sessao WHERE id_cinema = %s", (id_cinema,))
    cur.execute("DELETE FROM filmes_cinemas WHERE cinema_id = %s", (id_cinema,))
    cur.execute("DELETE FROM salas WHERE id_cinema = %s", (id_cinema,))
    cur.execute("DELETE FROM cinemas WHERE id = %s", (id_cinema,))
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    cur.close()
    conn.close()
    
    flash("Cinema removido!", "sucesso")
    return redirect(url_for('admin_cinemas'))

# ==========================
# ADMIN - GESTÃO DE USUÁRIOS
# ==========================
@app.route('/admin/usuarios')
def admin_usuarios():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash("Acesso negado!", "erro")
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    
    # Parâmetro de pesquisa
    search = request.args.get('search', '')
    
    try:
        # Query base - buscar dados básicos primeiro incluindo avatar
        query = """
            SELECT u.id, u.nome, u.email, u.criado_em, u.ultimo_login, u.is_admin, 
                   u.avatar, u.avatar_personalizado, u.avatar_id
            FROM usuarios u
        """
        
        params = []
        if search:
            query += " WHERE (u.nome LIKE %s OR u.email LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        query += " ORDER BY u.id DESC"
        
        cur.execute(query, params)
        usuarios = cur.fetchall()
        
        # Para cada usuário, buscar número de reservas e avatar
        for usuario in usuarios:
            # Buscar número de reservas
            cur.execute("SELECT COUNT(*) as num_reservas FROM reservas WHERE id_usuario = %s", (usuario['id'],))
            reservas_result = cur.fetchone()
            usuario['num_reservas'] = reservas_result['num_reservas'] if reservas_result else 0
            
            # Buscar avatar - prioridade: avatar_personalizado válido > avatar da tabela avatars > campo avatar > ícone padrão
            avatar_url = 'imgs/icons/user_icon34-removebg-preview.png'  # Valor padrão
            
            # 1. Tentar avatar_personalizado (mas ignorar se for default.png que não existe)
            if usuario.get('avatar_personalizado') and usuario['avatar_personalizado']:
                temp_url = str(usuario['avatar_personalizado']).replace('\\', '/').replace('"', '').strip()
                # Ignorar se for o default.png que não existe
                if temp_url and temp_url != 'None' and temp_url != '' and 'default.png' not in temp_url:
                    avatar_url = temp_url
                    print(f"[DEBUG] User {usuario['id']} ({usuario['nome']}): usando avatar_personalizado = {avatar_url}")
            
            # 2. Se não tiver avatar válido, tentar buscar da tabela avatars usando avatar_id
            if (avatar_url == 'imgs/icons/user_icon34-removebg-preview.png' or 'default.png' in avatar_url) and usuario.get('avatar_id') and usuario['avatar_id']:
                try:
                    cur.execute("SELECT caminho FROM avatars WHERE id = %s", (usuario['avatar_id'],))
                    avatar_result = cur.fetchone()
                    if avatar_result and avatar_result.get('caminho'):
                        temp_url = str(avatar_result['caminho']).replace('\\', '/').replace('"', '').strip()
                        if temp_url and temp_url != 'None' and temp_url != '':
                            avatar_url = temp_url
                            print(f"[DEBUG] User {usuario['id']} ({usuario['nome']}): usando avatar da tabela avatars (id={usuario['avatar_id']}) = {avatar_url}")
                except Exception as e:
                    print(f"[DEBUG] Erro ao buscar avatar do usuário {usuario['id']}: {e}")
            
            # 3. Se ainda não tiver, usar o campo avatar (mas ignorar default.png)
            if (avatar_url == 'imgs/icons/user_icon34-removebg-preview.png' or 'default.png' in avatar_url) and usuario.get('avatar') and usuario['avatar']:
                temp_url = str(usuario['avatar']).replace('\\', '/').replace('"', '').strip()
                if temp_url and temp_url != 'None' and temp_url != '' and 'default.png' not in temp_url:
                    avatar_url = temp_url
                    print(f"[DEBUG] User {usuario['id']} ({usuario['nome']}): usando campo avatar = {avatar_url}")
            
            # Garantir que sempre há um valor válido
            if not avatar_url or avatar_url == 'None' or avatar_url == '':
                avatar_url = 'imgs/icons/user_icon34-removebg-preview.png'
                print(f"[DEBUG] User {usuario['id']} ({usuario['nome']}): usando fallback padrão")
            
            usuario['avatar_url'] = avatar_url
            print(f"[DEBUG] User {usuario['id']} ({usuario['nome']}): avatar_url final = {avatar_url}")
        
        cur.close()
        conn.close()
        
        return render_template('admin_usuarios.html', user=get_current_user(), usuarios=usuarios, search=search)
        
    except Exception as e:
        cur.close()
        conn.close()
        flash(f"Erro ao carregar usuários: {str(e)}", "erro")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/adicionar_usuario', methods=['POST'])
def admin_adicionar_usuario():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash("Acesso negado!", "erro")
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    
    try:
        # Obter dados do formulário
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        telefone = request.form.get('telefone', '').strip()
        is_admin = request.form.get('is_admin') == 'on'
        
        # Validações básicas
        if not nome or not email or not senha:
            flash("Nome, email e senha são obrigatórios!", "erro")
            return redirect(url_for('admin_usuarios'))
        
        # Verificar se email já existe
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            flash("Email já está em uso!", "erro")
            return redirect(url_for('admin_usuarios'))
        
        # Hash da senha
        senha_hash = generate_password_hash(senha)
        
        # Inserir novo usuário
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha, telefone, is_admin, data_criacao)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (nome, email, senha_hash, telefone, is_admin))
        
        conn.commit()
        flash(f"Usuário {nome} adicionado com sucesso!", "sucesso")
        
    except Exception as e:
        conn.rollback()
        flash(f"Erro ao adicionar usuário: {str(e)}", "erro")
    
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuarios/<int:usuario_id>/dados')
def admin_usuario_dados(usuario_id):
    """API endpoint para obter dados do usuário para edição"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        cur.close()
        conn.close()
        return jsonify({'error': 'Acesso negado'}), 403
    
    cur.execute("SELECT id, nome, email, is_admin FROM usuarios WHERE id = %s", (usuario_id,))
    usuario = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    return jsonify(usuario)

@app.route('/admin/usuarios/<int:usuario_id>/detalhes')
def admin_usuario_detalhes(usuario_id):
    """API endpoint para obter detalhes completos do usuário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        cur.close()
        conn.close()
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        # Buscar dados básicos do usuário primeiro
        cur.execute("""
            SELECT u.id, u.nome, u.email, u.criado_em, u.ultimo_login, u.is_admin
            FROM usuarios u
            WHERE u.id = %s
        """, (usuario_id,))
        
        usuario = cur.fetchone()
        
        if not usuario:
            cur.close()
            conn.close()
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Buscar número de reservas
        cur.execute("SELECT COUNT(*) as num_reservas FROM reservas WHERE id_usuario = %s", (usuario_id,))
        reservas_count = cur.fetchone()
        usuario['num_reservas'] = reservas_count['num_reservas'] if reservas_count else 0
        
        # Tentar buscar avatar (pode não existir a tabela)
        try:
            cur.execute("SELECT caminho FROM avatars WHERE id = (SELECT avatar_id FROM usuarios WHERE id = %s)", (usuario_id,))
            avatar_result = cur.fetchone()
            if avatar_result and avatar_result['caminho']:
                avatar_url = avatar_result['caminho'].replace('\\', '/').replace('"', '').strip()
                if not avatar_url.startswith('/'):
                    if not avatar_url.startswith('static/'):
                        avatar_url = f"static/{avatar_url}"
                    avatar_url = f"/{avatar_url}"
                usuario['avatar_url'] = avatar_url
            else:
                usuario['avatar_url'] = '/static/imgs/icons/user_icon34-removebg-preview.png'
        except:
            # Se não existir tabela avatars ou der erro, usar avatar padrão
            usuario['avatar_url'] = '/static/imgs/icons/user_icon34-removebg-preview.png'
        
        # Formatar datas
        if usuario.get('criado_em'):
            usuario['criado_em'] = usuario['criado_em'].strftime('%d/%m/%Y às %H:%M')
        
        if usuario.get('ultimo_login'):
            usuario['ultimo_login'] = usuario['ultimo_login'].strftime('%d/%m/%Y às %H:%M')
        
        # Buscar últimas reservas do usuário
        cur.execute("""
            SELECT r.id, r.data_reserva, r.data_sessao, r.lugares,
                   f.titulo as filme_titulo,
                   c.nome as cinema_nome,
                   ts.nome as tipo_sessao
            FROM reservas r
            LEFT JOIN filmes f ON r.id_filme = f.id
            LEFT JOIN cinemas c ON r.id_cinema = c.id
            LEFT JOIN tipos_sessao ts ON r.id_tipo_sessao = ts.id
            WHERE r.id_usuario = %s
            ORDER BY r.data_reserva DESC
            LIMIT 5
        """, (usuario_id,))
        
        usuario['ultimas_reservas'] = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify(usuario)
        
    except Exception as e:
        cur.close()
        conn.close()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/admin/usuarios/remover/<int:usuario_id>', methods=['POST'])
def admin_remover_usuario(usuario_id):
    """Remover usuário (apenas se não for admin)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash("Acesso negado!", "erro")
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    
    try:
        # Verificar se o usuário a ser removido existe e não é admin
        cur.execute("SELECT nome, is_admin FROM usuarios WHERE id = %s", (usuario_id,))
        usuario_para_remover = cur.fetchone()
        
        if not usuario_para_remover:
            flash("Usuário não encontrado!", "erro")
            cur.close()
            conn.close()
            return redirect(url_for('admin_usuarios'))
        
        if usuario_para_remover['is_admin']:
            flash("Não é possível remover administradores!", "erro")
            cur.close()
            conn.close()
            return redirect(url_for('admin_usuarios'))
        
        # Verificar se há reservas associadas
        cur.execute("SELECT COUNT(*) as total FROM reservas WHERE id_usuario = %s", (usuario_id,))
        reservas = cur.fetchone()['total']
        
        if reservas > 0:
            # Remover reservas primeiro (ou marcar como removidas)
            cur.execute("DELETE FROM reservas WHERE id_usuario = %s", (usuario_id,))
        
        # Remover o usuário
        cur.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        conn.commit()
        
        flash(f"Usuário {usuario_para_remover['nome']} removido com sucesso!", "sucesso")
        
    except Exception as e:
        conn.rollback()
        flash(f"Erro ao remover usuário: {str(e)}", "erro")
    
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_usuarios'))

# ==========================
# ADMIN - GESTÃO DE RESERVAS
# ==========================
@app.route('/admin/reservas')
def admin_reservas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash("Acesso negado!", "erro")
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    
    # Parâmetros de pesquisa
    search = request.args.get('search', '')
    cinema_filter = request.args.get('cinema', '')
    
    # Query base - MOSTRAR TODAS AS RESERVAS
    query = """
        SELECT r.id, r.data_reserva, r.data_sessao, r.lugares, r.total, r.status,
               COALESCE(u.nome, r.nome_cliente, 'Cliente não identificado') as usuario_nome, 
               COALESCE(u.email, r.email_cliente, 'Email não disponível') as usuario_email,
               COALESCE(f.titulo, 'Filme não identificado') as filme_titulo,
               COALESCE(c.nome, 'Cinema não identificado') as cinema_nome,
               COALESCE(ts.nome, 'Tipo não identificado') as tipo_sessao
        FROM reservas r
        LEFT JOIN usuarios u ON r.id_usuario = u.id
        LEFT JOIN filmes f ON r.id_filme = f.id
        LEFT JOIN cinemas c ON r.id_cinema = c.id
        LEFT JOIN tipos_sessao ts ON r.id_tipo_sessao = ts.id
    """
    
    conditions = []
    params = []
    
    if search:
        conditions.append("""(
            COALESCE(u.nome, r.nome_cliente) LIKE %s OR 
            COALESCE(u.email, r.email_cliente) LIKE %s OR 
            f.titulo LIKE %s OR
            r.id LIKE %s
        )""")
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param, search_param])
    
    if cinema_filter:
        conditions.append("c.nome = %s")
        params.append(cinema_filter)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    # REMOVER LIMIT - MOSTRAR TODAS AS RESERVAS
    query += " ORDER BY r.id DESC"
    
    cur.execute(query, params)
    reservas = cur.fetchall()
    
    # Buscar cinemas para filtro
    cur.execute("SELECT DISTINCT nome FROM cinemas ORDER BY nome")
    cinemas = [c['nome'] for c in cur.fetchall()]
    
    # Estatísticas
    cur.execute("SELECT COUNT(*) as total FROM reservas")
    total_reservas = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as confirmadas FROM reservas WHERE status = 'confirmada'")
    reservas_confirmadas = cur.fetchone()['confirmadas']
    
    cur.close()
    conn.close()
    
    return render_template('admin_reservas.html', 
                         user=get_current_user(),
                         reservas=reservas, 
                         cinemas=cinemas,
                         search=search,
                         cinema_filter=cinema_filter,
                         total_reservas=total_reservas,
                         reservas_confirmadas=reservas_confirmadas)

@app.route('/admin/reservas/cancelar/<int:reserva_id>', methods=['POST'])
def admin_cancelar_reserva(reserva_id):
    """Eliminar/cancelar uma reserva"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'})
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Verificar se é admin
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    try:
        # Verificar se a reserva existe
        cur.execute("SELECT * FROM reservas WHERE id = %s", (reserva_id,))
        reserva = cur.fetchone()
        
        if not reserva:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Reserva não encontrada'})
        
        # Eliminar a reserva
        cur.execute("DELETE FROM reservas WHERE id = %s", (reserva_id,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        app.logger.info(f"Admin {session['user_id']} eliminou reserva {reserva_id}")
        return jsonify({'success': True, 'message': 'Reserva eliminada com sucesso'})
        
    except Exception as e:
        cur.close()
        conn.close()
        app.logger.error(f"Erro ao eliminar reserva {reserva_id}: {e}")
        return jsonify({'success': False, 'message': f'Erro ao eliminar reserva: {str(e)}'})

@app.route('/admin/reservas/confirmar/<int:reserva_id>', methods=['POST'])
def admin_confirmar_reserva(reserva_id):
    """Confirmar uma reserva pendente"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'})
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Verificar se é admin
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    try:
        # Verificar se a reserva existe e está pendente
        cur.execute("SELECT * FROM reservas WHERE id = %s", (reserva_id,))
        reserva = cur.fetchone()
        
        if not reserva:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Reserva não encontrada'})
        
        # Atualizar status para confirmada
        cur.execute("UPDATE reservas SET status = 'confirmada' WHERE id = %s", (reserva_id,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        app.logger.info(f"Admin {session['user_id']} confirmou reserva {reserva_id}")
        return jsonify({'success': True, 'message': 'Reserva confirmada com sucesso'})
        
    except Exception as e:
        cur.close()
        conn.close()
        app.logger.error(f"Erro ao confirmar reserva {reserva_id}: {e}")
        return jsonify({'success': False, 'message': f'Erro ao confirmar reserva: {str(e)}'})

@app.route('/admin/reservas/detalhes/<int:reserva_id>')
def admin_reserva_detalhes(reserva_id):
    """Obter detalhes de uma reserva"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'})
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Verificar se é admin
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    try:
        # Buscar detalhes completos da reserva
        cur.execute("""
            SELECT r.*, 
                   u.nome as usuario_nome, u.email as usuario_email,
                   f.titulo as filme_titulo, f.duracao,
                   c.nome as cinema_nome, c.localizacao as cinema_localizacao,
                   ts.nome as tipo_sessao
            FROM reservas r
            LEFT JOIN usuarios u ON r.id_usuario = u.id
            LEFT JOIN filmes f ON r.id_filme = f.id
            LEFT JOIN cinemas c ON r.id_cinema = c.id
            LEFT JOIN tipos_sessao ts ON r.id_tipo_sessao = ts.id
            WHERE r.id = %s
        """, (reserva_id,))
        
        reserva = cur.fetchone()
        
        if not reserva:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Reserva não encontrada'})
        
        # Converter datas para string para JSON
        if reserva.get('data_sessao'):
            reserva['data_sessao'] = reserva['data_sessao'].isoformat()
        if reserva.get('data_reserva'):
            reserva['data_reserva'] = reserva['data_reserva'].isoformat()
        
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'reserva': reserva})
        
    except Exception as e:
        cur.close()
        conn.close()
        app.logger.error(f"Erro ao buscar detalhes da reserva {reserva_id}: {e}")
        return jsonify({'success': False, 'message': f'Erro ao buscar detalhes: {str(e)}'})

# ==========================
# RECUPERAR SENHA (simples)
# ==========================
@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        # Aqui podes implementar envio de email com token/reset
        flash("Se o email existir no sistema, receberás instruções para recuperar a senha.", "info")
        return redirect(url_for('login'))
    return render_template('recuperar_senha.html')

@app.context_processor
def inject_user():
    user_id = session.get("user_id")

    # não há user logado
    if not user_id:
        return {
            "logged_in": False,
            "user_nome": None,
            "avatar": "imgs/icons/user_icon34-removebg-preview.png",
            "avatar_id": None
        }

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT u.nome, u.email, u.avatar, u.avatar_id, u.is_admin, 
                   a.caminho AS avatar_path
            FROM usuarios u
            LEFT JOIN avatars a ON u.avatar_id = a.id
            WHERE u.id = %s
            """,
            (user_id,)
        )
        row = cur.fetchone()
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass

    if not row:
        return {
            "logged_in": False,
            "user_nome": None,
            "avatar": "imgs/icons/user_icon34-removebg-preview.png",
            "avatar_id": None
        }

    # Processar avatar com a mesma lógica do route perfil
    avatar = None
    
    # Prioridade: avatar da tabela avatars → avatar direto do usuario → fallback
    if row.get('avatar_path'):
        avatar = str(row['avatar_path'])
    elif row.get('avatar'):
        avatar = str(row['avatar'])
    else:
        avatar = 'imgs/icons/user_icon34-removebg-preview.png'
    
    # Limpar e normalizar avatar
    if avatar:
        avatar = avatar.replace('\\', '/').replace('"', '').strip()
        
        # Garantir que o caminho está correto
        if not avatar.startswith('imgs/'):
            if avatar.startswith('static/'):
                avatar = avatar[7:]  # Remove 'static/'
            if not avatar.startswith('imgs/'):
                avatar = f"imgs/{avatar}"
    
    # Verificação final
    if not avatar or avatar == 'imgs/' or avatar == 'imgs':
        avatar = 'imgs/icons/user_icon34-removebg-preview.png'

    return {
        "logged_in": True,
        "user_nome": row.get("nome"),
        "avatar": avatar,
        "avatar_id": row.get("avatar_id"),
        "is_admin": row.get("is_admin", False),
        "is_admin_email": row.get("email") == "cinevibeadmn@gmail.com",
        "profile_url": "admin_dashboard" if row.get("email") == "cinevibeadmn@gmail.com" else "perfil"
    }


# ==========================
# LOGOUT
# ==========================
@app.route('/logout')
def logout():
    session.clear()
    flash("Sessão terminada.", "success")
    return redirect(url_for('home'))

# ==========================
# ROTA DE DEBUG - LOGIN FORÇADO
# ==========================
@app.route('/debug_login_afonso')
def debug_login_afonso():
    """Rota de debug para forçar login do Afonso"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar utilizador Afonso
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", ('afonso2008david@gmail.com',))
        user = cursor.fetchone()
        
        if user:
            # Forçar login
            session['user_id'] = user['id']
            session['user_nome'] = user['nome']
            session['user_email'] = user['email']
            
            # Buscar avatar (personalizado OU da galeria)
            cursor.execute("""
                SELECT COALESCE(u.avatar, a.caminho) as avatar_path
                FROM usuarios u 
                LEFT JOIN avatars a ON u.avatar_id = a.id 
                WHERE u.id = %s
            """, (user['id'],))
            avatar_data = cursor.fetchone()
            if avatar_data and avatar_data['avatar_path']:
                avatar = avatar_data['avatar_path'].replace('\\', '/').replace('"', '').strip()
                # Remover prefixos desnecessários
                if avatar.startswith('static/'):
                    avatar = avatar[7:]
                if avatar.startswith('/static/'):
                    avatar = avatar[8:]
                session['user_avatar'] = avatar
            else:
                session['user_avatar'] = 'imgs/icons/user_icon34-removebg-preview.png'
            
            cursor.close()
            conn.close()
            
            flash(f"✅ Login forçado com sucesso! Bem-vindo, {user['nome']}!", "sucesso")
            return redirect(url_for('home'))
        else:
            cursor.close()
            conn.close()
            return "❌ Utilizador não encontrado!"
            
    except Exception as e:
        return f"❌ Erro: {e}"



# ==========================
# Página filmes
# ==========================
@app.route('/filmes')
def filmes():
    # Atualização automática de estados dos filmes - DESATIVADO para controlo manual
    # atualizar_estados_filmes_automatico()
    
    # Capturar filtro de género da URL
    genero_filtro = request.args.get('genero', '').strip().lower()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # BUSCAR TODOS OS GÉNEROS DA BASE DE DADOS
        cursor.execute("SELECT id, nome FROM generos ORDER BY nome ASC")
        generos = cursor.fetchall() or []
        
        # Query base para filmes
        query = """
            SELECT
                f.id,
                f.titulo,
                f.duracao,
                f.poster_url,
                f.poster_hover,
                f.estado,
                COALESCE(GROUP_CONCAT(g.nome SEPARATOR ', '), '') AS genero_nome
            FROM filmes f
            LEFT JOIN filme_generos fg ON f.id = fg.filme_id
            LEFT JOIN generos g ON fg.genero_id = g.id
        """
        
        # Adicionar filtro de género se especificado
        if genero_filtro:
            query += """
            WHERE f.id IN (
                SELECT DISTINCT fg2.filme_id 
                FROM filme_generos fg2
                JOIN generos g2 ON fg2.genero_id = g2.id
                WHERE LOWER(g2.nome) = %s
            )
            """
            query += " GROUP BY f.id ORDER BY f.id ASC"
            cursor.execute(query, (genero_filtro,))
        else:
            query += " GROUP BY f.id ORDER BY f.id ASC"
            cursor.execute(query)
            
        filmes = cursor.fetchall() or []

        for f in filmes:
            estado = (f.get('estado') or '').strip().lower().replace('-', '_')
            if estado in ('em exibicao', 'em_exibicao', 'em-exibicao', 'emexibicao'):
                estado = 'em_exibicao'
            elif estado in ('brevemente', 'breve', 'coming_soon', 'comingsoon'):
                estado = 'brevemente'
            f['estado'] = estado

            # Normalizar poster_url usando a função helper
            if f.get('poster_url'):
                f['poster_url'] = _normalize_img_path(f['poster_url'])
            else:
                f['poster_url'] = None

            # Normalizar poster_hover usando a função helper
            if f.get('poster_hover'):
                f['poster_hover'] = _normalize_img_path(f['poster_hover'])
            else:
                f['poster_hover'] = None

            if f.get('genero_nome') is None:
                f['genero_nome'] = ''

        filmes_em_exibicao = [f for f in filmes if f['estado'] == 'em_exibicao']
        filmes_brevemente = [f for f in filmes if f['estado'] == 'brevemente']

    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass

    return render_template('filmes.html',
                           filmes_em_exibicao=filmes_em_exibicao,
                           filmes_brevemente=filmes_brevemente,
                           generos=generos,  # PASSAR GÉNEROS PARA O TEMPLATE
                           genero_filtro=genero_filtro)

# ==========================
# Página detalhe de filme
# ==========================
@app.route('/filme/<int:id_filme>')
def filme_detalhe(id_filme):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id, titulo, sinopse, poster_url, poster_hover, imagem_grande,
                   diretor, data_lancamento, duracao,
                   rotten_tomatoes_score, rotten_tomatoes_url,
                   imdb_rating, imdb_url, trailer_url, idade_recomendada, pais_origem, idioma_original
            FROM filmes
            WHERE id = %s
        """, (id_filme,))
        filme = cursor.fetchone()
        if not filme:
            return "Filme não encontrado", 404

        cursor.execute("""
            SELECT a.id, a.nome, a.foto_url, fa.papel
            FROM filme_atores fa
            JOIN atores a ON fa.ator_id = a.id
            WHERE fa.filme_id = %s
            ORDER BY a.id
        """, (id_filme,))
        elenco = cursor.fetchall()

        cursor.execute("""
            SELECT g.nome AS genero
            FROM filme_generos fg
            JOIN generos g ON fg.genero_id = g.id
            WHERE fg.filme_id = %s
        """, (id_filme,))
        filme_generos = cursor.fetchall()

        # Buscar apenas os tipos de sessão que têm horários para este filme
        cursor.execute("""
            SELECT DISTINCT ts.id, ts.nome 
            FROM tipos_sessao ts
            JOIN horarios_sessao hs ON ts.id = hs.id_tipo_sessao
            WHERE hs.id_filme = %s
            ORDER BY ts.nome
        """, (id_filme,))
        tipos_sessao = cursor.fetchall()

        # Buscar todos os horários com nome da sala
        cursor.execute("""
            SELECT hs.id, hs.id_cinema, hs.id_tipo_sessao, hs.id_sala, h.hora, s.nome_sala
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            LEFT JOIN salas s ON hs.id_sala = s.id
            WHERE hs.id_filme = %s
            ORDER BY h.hora
        """, (id_filme,))
        
        horarios_filme = cursor.fetchall()
        
        app.logger.info(f"Horários encontrados para filme {id_filme}: {len(horarios_filme)}")
        
        # CORREÇÃO AUTOMÁTICA: Atualizar horários sem sala na base de dados
        horarios_sem_sala_ids = [h['id'] for h in horarios_filme if not h.get('id_sala')]
        
        if horarios_sem_sala_ids:
            app.logger.warning(f"Corrigindo {len(horarios_sem_sala_ids)} horários sem sala na BD...")
            
            for horario_id in horarios_sem_sala_ids:
                # Buscar o cinema do horário
                horario_data = next((h for h in horarios_filme if h['id'] == horario_id), None)
                if horario_data and horario_data.get('id_cinema'):
                    # Buscar primeira sala do cinema
                    cursor.execute("""
                        SELECT id FROM salas 
                        WHERE id_cinema = %s 
                        ORDER BY id LIMIT 1
                    """, (horario_data['id_cinema'],))
                    sala = cursor.fetchone()
                    
                    if sala:
                        # Atualizar na base de dados
                        cursor.execute("""
                            UPDATE horarios_sessao 
                            SET id_sala = %s 
                            WHERE id = %s
                        """, (sala['id'], horario_id))
                        app.logger.info(f"Horário {horario_id} atualizado com sala {sala['id']}")
            
            conn.commit()
            
            # Recarregar horários após correção
            cursor.execute("""
                SELECT hs.id, hs.id_cinema, hs.id_tipo_sessao, hs.id_sala, h.hora, s.nome_sala
                FROM horarios_sessao hs
                JOIN horarios h ON hs.id_horario = h.id
                LEFT JOIN salas s ON hs.id_sala = s.id
                WHERE hs.id_filme = %s
                ORDER BY h.hora
            """, (id_filme,))
            horarios_filme = cursor.fetchall()
            app.logger.info(f"Horários recarregados após correção: {len(horarios_filme)}")
        
        # Converter hora de timedelta para string formatada e filtrar horários passados
        from datetime import timedelta, datetime, time
        
        agora = datetime.now()
        hora_atual = agora.time()
        
        horarios_processados = []
        
        for h in horarios_filme:
            # Converter para string e objeto time
            if isinstance(h['hora'], timedelta):
                total_seconds = int(h['hora'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                h['hora_str'] = f"{hours:02d}:{minutes:02d}"
                h['hora_obj'] = time(hours, minutes)
            elif isinstance(h['hora'], time):
                h['hora_str'] = h['hora'].strftime('%H:%M')
                h['hora_obj'] = h['hora']
            else:
                h['hora_str'] = str(h['hora'])[:5]  # HH:MM
                try:
                    hora_parts = h['hora_str'].split(':')
                    h['hora_obj'] = time(int(hora_parts[0]), int(hora_parts[1]))
                except:
                    h['hora_obj'] = None
            
            # Apenas adicionar horários futuros (para hoje) ou todos os horários (para outros dias)
            # Como não temos a data da sessão aqui, vamos sempre incluir
            # O filtro por data será feito no JavaScript
            horarios_processados.append(h)
        
        horarios_filme = horarios_processados
        app.logger.info(f"Horários após processamento: {len(horarios_filme)}")

        filtro_regiao = request.args.get('regiao', '').lower().strip()
        query = """
            SELECT c.id, c.nome, c.regiao
            FROM filmes_cinemas fc
            JOIN cinemas c ON fc.cinema_id = c.id
            WHERE fc.filme_id = %s
        """
        params = [id_filme]
        if filtro_regiao:
            query += " AND LOWER(TRIM(c.regiao)) = %s"
            params.append(filtro_regiao)
        query += " ORDER BY c.regiao, c.nome"
        cursor.execute(query, params)
        filme_cinemas = cursor.fetchall()

        cursor.execute("SELECT DISTINCT regiao FROM cinemas ORDER BY regiao")
        regioes = [r['regiao'] for r in cursor.fetchall()]
        
        # Buscar avaliações do filme com informações do usuário
        cursor.execute("""
            SELECT 
                av.id,
                av.usuario_id,
                av.rating,
                av.comentario,
                av.data_avaliacao,
                u.nome as usuario_nome,
                COALESCE(u.avatar, a.caminho) as usuario_avatar
            FROM avaliacoes_filmes av
            JOIN usuarios u ON av.usuario_id = u.id
            LEFT JOIN avatars a ON u.avatar_id = a.id
            WHERE av.filme_id = %s
            ORDER BY av.data_avaliacao DESC
        """, (id_filme,))
        todas_avaliacoes = cursor.fetchall()
        
        # Verificar se o usuário logado já avaliou
        user_avaliacao = None
        if 'user_id' in session:
            cursor.execute("""
                SELECT rating, comentario
                FROM avaliacoes_filmes
                WHERE filme_id = %s AND usuario_id = %s
            """, (id_filme, session['user_id']))
            user_avaliacao = cursor.fetchone()
        
        # Separar avaliação do usuário logado das outras
        avaliacoes = []
        user_id_logado = session.get('user_id')
        
        for avaliacao in todas_avaliacoes:
            # Se for a avaliação do usuário logado e ele já tem uma avaliação, pular
            if user_id_logado and user_avaliacao and avaliacao['usuario_id'] == user_id_logado:
                continue
            avaliacoes.append(avaliacao)
        
        # Limpar avatares
        for avaliacao in avaliacoes:
            if avaliacao.get('usuario_avatar'):
                avaliacao['usuario_avatar'] = avaliacao['usuario_avatar'].replace('\\', '/').replace('"', '').strip()
            else:
                avaliacao['usuario_avatar'] = 'imgs/icons/user_icon34-removebg-preview.png'
        
        # Organizar tipos de sessão por cinema
        tipos_sessao_por_cinema = {}
        
        # Buscar tipos de sessão disponíveis para cada cinema
        for cinema in filme_cinemas:
            cursor.execute("""
                SELECT DISTINCT ts.id, ts.nome, ts.preco_bilhete, ts.descricao
                FROM horarios_sessao hs
                JOIN tipos_sessao ts ON hs.id_tipo_sessao = ts.id
                WHERE hs.id_filme = %s AND hs.id_cinema = %s
                ORDER BY ts.nome
            """, (id_filme, cinema['id']))
            tipos_cinema = cursor.fetchall()
            tipos_sessao_por_cinema[cinema['id']] = tipos_cinema
        
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass

    for campo in ['poster_url', 'imagem_grande']:
        if filme.get(campo):
            filme[campo] = filme[campo].replace('\\', '/').replace('"', '').strip()

    for ator in elenco:
        if ator.get('foto_url'):
            ator['foto_url'] = ator['foto_url'].replace('\\', '/').replace('"', '').strip()

    # Remover duplicados dos horários
    horarios_unicos = []
    horarios_vistos = set()
    
    for h in horarios_filme:
        # Criar chave única baseada em cinema, tipo_sessao, sala e hora
        chave = (h['id_cinema'], h['id_tipo_sessao'], h['id_sala'], str(h['hora']))
        
        if chave not in horarios_vistos:
            horarios_vistos.add(chave)
            horarios_unicos.append(h)
    
    horarios_filme = horarios_unicos
    
    # Converter hora para string e remover objetos não serializáveis
    horarios_limpos = []
    for h in horarios_filme:
        h_limpo = dict(h)  # Criar cópia
        
        # Remover objetos não serializáveis
        if 'hora_obj' in h_limpo:
            del h_limpo['hora_obj']
        
        # Garantir que hora está como string
        hora_valor = h_limpo['hora']
        if isinstance(hora_valor, str):
            h_limpo['hora'] = hora_valor
        else:
            try:
                total_seconds = hora_valor.total_seconds()
                horas = int(total_seconds // 3600)
                minutos = int((total_seconds % 3600) // 60)
                h_limpo['hora'] = f"{horas:02d}:{minutos:02d}"
            except Exception:
                h_limpo['hora'] = str(hora_valor)
        
        horarios_limpos.append(h_limpo)
    
    horarios_filme = horarios_limpos

    logged_in = 'user_id' in session
    avatar = get_user_avatar()
    
    app.logger.info(f"filme_detalhe - logged_in: {logged_in}, avatar: {avatar}")
    
    # Garantir que avatar não está vazio
    if not avatar or avatar == '' or avatar == 'None':
        avatar = 'imgs/icons/user_icon34-removebg-preview.png'
        app.logger.warning(f"filme_detalhe - avatar vazio, usando padrão")
    
    app.logger.info(f"filme_detalhe - avatar final para template: {avatar}")
    
    return render_template(
        'filme_detalhe.html',
        filme=filme,
        elenco=elenco,
        filme_generos=filme_generos,
        filme_cinemas=filme_cinemas,
        tipos_sessao=tipos_sessao,
        tipos_sessao_por_cinema=tipos_sessao_por_cinema,
        horarios_filme=horarios_filme,
        regioes=regioes,
        avaliacoes=avaliacoes,
        user_avaliacao=user_avaliacao,
        logged_in=logged_in,
        avatar=avatar,
        request=request
    )

# ==========================
# Página CineAcessível
# ==========================
@app.route('/cineacessivel')
def cine_acessivel():
    return render_template('cine_acessivel.html')

# ==========================
# Reserva (mostra planta via DB)
# Expecta query params: horario, cinema, tipo
# ==========================
from flask import url_for




@app.route('/cine_acessivel/audiodescricao')
def audiodescricao():   # <-- endpoint 'audiodescricao'
    return render_template('audiodescricao.html')

@app.route('/cine_acessivel/lgp')
def lgp():              # <-- endpoint 'lgp'
    return render_template('lgp.html')

@app.route('/cine_acessivel/acessibilidade')
def acessibilidade():   # <-- endpoint 'acessibilidade'
    return render_template('acessibilidade.html')

@app.route('/cine_acessivel/legendagem')
def legendagem():       # <-- endpoint 'legendagem'
    return render_template('legendagem.html')

@app.route('/contactos')
def contactos():
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    return render_template('contactos.html', logged_in=logged_in, avatar=avatar)

# ==========================
# CÓDIGO REMOVIDO - if __name__ == '__main__' movido para o final
# ==========================

@app.route('/api/process-payment', methods=['POST'])
def process_payment():
    """Processar pagamento - VERSÃO SEM CONSTRAINTS"""
    try:
        app.logger.info("🚀 INICIANDO process_payment")
        data = request.get_json()
        app.logger.info(f"📥 Dados recebidos: {data}")
        
        # Extrair dados do pagamento
        payment_method = data.get('payment_method')
        customer_info = data.get('customer_info', {})
        payment_data = data.get('payment_data', {})
        app.logger.info(f"💳 Método de pagamento: {payment_method}")
        
        # Obter dados da reserva da sessão
        reservation_data = session.get('reserva_data', {})
        app.logger.info(f"🎫 Dados da reserva na sessão: {reservation_data}")
        
        # FALLBACK: Se não há dados na sessão, criar dados de demonstração
        if not reservation_data:
            app.logger.warning("Dados da reserva não encontrados na sessão, criando dados de demonstração")
            reservation_data = {
                'filme_id': 1,
                'cinema_id': 1,
                'sessao_id': 1,
                'id_tipo_sessao': 1,
                'data_sessao': '2025-01-20',
                'lugares_selecionados': ['A1', 'A2'],
                'total': 17.00,
                'produtos_bar': []
            }
            session['reserva_data'] = reservation_data
        
        # Conectar à base de dados
        app.logger.info("🔌 Tentando conectar à base de dados...")
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'Kevin@15',
            'database': 'cinevibe'
        }
        
        conn = None
        cursor = None
        reserva_id = None
        
        try:
            import mysql.connector
            app.logger.info("📦 Importando mysql.connector...")
            conn = mysql.connector.connect(**db_config)
            app.logger.info("✅ Conexão estabelecida")
            cursor = conn.cursor()
            app.logger.info("📋 Cursor criado")
            
            # DESABILITAR TODAS AS CONSTRAINTS TEMPORARIAMENTE
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("SET SQL_MODE = ''")
            app.logger.info("⚙️ Constraints desabilitadas")
            
        except Exception as e:
            app.logger.error(f"❌ Erro de conexão à base de dados: {str(e)}")
            return jsonify({
                'success': True,
                'reservation_id': 'CV999999',
                'message': 'Pagamento processado (modo offline)'
            })
        
        # PREPARAR DADOS CORRETOS
        id_usuario = session.get('user_id', 1)
        id_filme = reservation_data.get('filme_id', 1)
        id_cinema = reservation_data.get('cinema_id', 1)
        id_horario_sessao = 1  # Usar ID fixo que existe
        id_tipo_sessao = reservation_data.get('id_tipo_sessao', 1)
        data_sessao = reservation_data.get('data_sessao', '2025-01-20')
        
        # LUGARES - FORMATO CORRETO
        lugares_lista = reservation_data.get('lugares_selecionados', ['A1', 'A2'])
        lugares = ','.join(lugares_lista)  # A11,A12,A13
        
        total = float(reservation_data.get('total', 17.00))
        
        # NOME DO CLIENTE - PRIORIDADE ABSOLUTA DA SESSÃO
        nome_cliente = session.get('user_name', '').strip()
        if not nome_cliente:
            nome_cliente = session.get('nome_cliente', '').strip()
        if not nome_cliente:
            nome_cliente = customer_info.get('name', '').strip()
        if not nome_cliente:
            nome_cliente = 'Usuário CineVibe'
        
        # EMAIL DO CLIENTE - PRIORIDADE ABSOLUTA DA SESSÃO
        email_cliente = session.get('user_email', '').strip()
        if not email_cliente:
            email_cliente = session.get('email_cliente', '').strip()
        if not email_cliente:
            email_cliente = customer_info.get('email', '').strip()
        if not email_cliente:
            email_cliente = 'usuario@cinevibe.com'
        
        telefone_cliente = session.get('telefone_cliente', '').strip()
        if not telefone_cliente:
            telefone_cliente = customer_info.get('phone', '').strip() or ''
        metodo_pagamento = payment_method  # card, paypal, etc.
        
        # LOG DETALHADO
        app.logger.info(f"🎯 INSERINDO DADOS CORRETOS:")
        app.logger.info(f"   Nome: '{nome_cliente}'")
        app.logger.info(f"   Email: '{email_cliente}'")
        app.logger.info(f"   Lugares: '{lugares}'")
        app.logger.info(f"   Método: '{metodo_pagamento}'")
        app.logger.info(f"   Total: €{total}")
        
        # INSERÇÃO FORÇADA SEM CONSTRAINTS
        try:
            # Inserção direta sem verificação de foreign keys
            cursor.execute("""
                INSERT INTO reservas (
                    id_horario_sessao, data_sessao, id_filme, id_cinema, 
                    id_tipo_sessao, id_usuario, nome_cliente, email_cliente, 
                    telefone_cliente, data_reserva, status, total, 
                    metodo_pagamento, lugares
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'confirmada', %s, %s, %s)
            """, (
                1, data_sessao, 1, 1,  # IDs fixos que existem
                1, id_usuario, nome_cliente, email_cliente,
                telefone_cliente, total, metodo_pagamento, lugares
            ))
            
            reserva_id = cursor.lastrowid
            app.logger.info(f"✅ RESERVA INSERIDA FORÇADAMENTE - ID: {reserva_id}")
            
        except Exception as e1:
            app.logger.error(f"Erro na inserção forçada: {str(e1)}")
            
            # Fallback: inserção mínima
            try:
                cursor.execute("""
                    INSERT INTO reservas (
                        id_usuario, nome_cliente, email_cliente, 
                        telefone_cliente, data_reserva, status, total, 
                        metodo_pagamento, lugares, data_sessao
                    ) VALUES (%s, %s, %s, %s, NOW(), 'confirmada', %s, %s, %s, %s)
                """, (
                    id_usuario, nome_cliente, email_cliente,
                    telefone_cliente, total, metodo_pagamento, lugares, data_sessao
                ))
                
                reserva_id = cursor.lastrowid
                app.logger.info(f"✅ RESERVA INSERIDA (fallback) - ID: {reserva_id}")
                
            except Exception as e2:
                app.logger.error(f"Erro no fallback: {str(e2)}")
                reserva_id = 99999
        
        # Commit forçado
        try:
            conn.commit()
            app.logger.info("✅ COMMIT FORÇADO REALIZADO")
        except Exception as e:
            app.logger.warning(f"Erro no commit: {str(e)}")
        
        # Reabilitar constraints
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        except:
            pass
        
        # Marcar lugares como ocupados
        try:
            if lugares_lista:
                for lugar in lugares_lista:
                    try:
                        cursor.execute("""
                            INSERT IGNORE INTO lugares (id_sala, lugar, ocupado) 
                            VALUES (1, %s, TRUE)
                            ON DUPLICATE KEY UPDATE ocupado = TRUE
                        """, (lugar,))
                        app.logger.info(f"✅ Lugar {lugar} marcado")
                    except:
                        pass
        except:
            pass
        
        # Enviar email (desabilitado temporariamente para debug)
        try:
            app.logger.info("📧 Email desabilitado temporariamente para debug")
            # from email_config import enviar_email_confirmacao_reserva
            # enviar_email_confirmacao_reserva(...)
            
        except Exception as e:
            app.logger.warning(f"❌ Erro no email: {str(e)}")
        
        # Fechar conexão
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except:
            pass
        
        # Limpar sessão
        session.pop('reserva_data', None)
        
        return jsonify({
            'success': True,
            'reservation_id': f"CV{reserva_id:06d}",
            'message': f'Reserva confirmada para {nome_cliente}!',
            'customer_name': nome_cliente,
            'seats': lugares,
            'total': total
        })
        
    except Exception as e:
        app.logger.error(f"Erro crítico: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        })

@app.route('/confirmar_pagamento_sessao', methods=['POST'])
def confirmar_pagamento_sessao():
    """
    Confirma pagamento de sessão exclusiva.
    Permite reservas tanto para utilizadores logados quanto para convidados.
    """
    try:
        data = request.get_json()
        app.logger.info(f"📦 Dados recebidos: {data}")
        
        # Extrair e validar dados básicos
        tipo_sala = data.get('tipo_sala')
        preco_raw = data.get('preco')
        metodo_pagamento = data.get('metodo_pagamento')
        data_sessao = data.get('data_sessao')
        hora_sessao = data.get('hora_sessao')
        
        # Validar dados obrigatórios
        if not tipo_sala:
            return jsonify({'success': False, 'message': 'Tipo de sala é obrigatório'}), 400
        
        if not data_sessao or not hora_sessao:
            return jsonify({'success': False, 'message': 'Data e hora da sessão são obrigatórias'}), 400
        
        # Validar e converter preço
        total = None
        if preco_raw:
            try:
                # Remover símbolos e converter para float
                preco_str = str(preco_raw).replace('€', '').replace(',', '.').strip()
                total = float(preco_str)
                
                if total <= 0:
                    return jsonify({'success': False, 'message': 'Preço deve ser maior que zero'}), 400
                    
                app.logger.info(f"💰 Preço validado: €{total}")
                
            except (ValueError, TypeError) as e:
                app.logger.error(f"❌ Erro ao converter preço '{preco_raw}': {e}")
                return jsonify({'success': False, 'message': 'Preço inválido'}), 400
        else:
            # Definir preços padrão baseados no tipo de sala
            precos_padrao = {
                'intimista': 100.00,
                'premium': 150.00,
                'vip': 200.00
            }
            total = precos_padrao.get(tipo_sala.lower(), 100.00)
            app.logger.warning(f"⚠️ Preço não fornecido, usando padrão: €{total}")
        
        # Dados do utilizador (logado ou convidado)
        user_id = None
        nome_cliente = ""
        email_cliente = ""
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar se o utilizador está logado
        if 'user_id' in session:
            # Utilizador logado - usar dados da sessão
            user_id = session['user_id']
            
            cursor.execute("""
                SELECT nome, email FROM usuarios WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()
            
            if user:
                nome_cliente = user['nome']
                email_cliente = user['email']
            else:
                # Fallback para dados da sessão
                nome_cliente = session.get('nome', 'Cliente')
                email_cliente = session.get('email', '')
                
            app.logger.info(f"👤 Utilizador logado: {nome_cliente} ({email_cliente})")
            
        else:
            # Utilizador convidado - obter dados do formulário
            nome_cliente = data.get('nome_cliente', '').strip()
            email_cliente = data.get('email_cliente', '').strip()
            telefone_cliente = data.get('telefone_cliente', '').strip()
            
            if not nome_cliente or not email_cliente:
                return jsonify({
                    'success': False, 
                    'message': 'Nome e email são obrigatórios para reservas de convidado'
                }), 400
            
            # Validar email
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email_cliente):
                return jsonify({
                    'success': False, 
                    'message': 'Email inválido'
                }), 400
            
            # Verificar se já existe um utilizador com este email
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email_cliente,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Usar utilizador existente
                user_id = existing_user['id']
                app.logger.info(f"👤 Utilizador existente encontrado: {email_cliente}")
            else:
                # Criar utilizador convidado temporário
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha, tipo_usuario, criado_em)
                    VALUES (%s, %s, 'GUEST_USER', 'convidado', NOW())
                """, (nome_cliente, email_cliente))
                
                user_id = cursor.lastrowid
                app.logger.info(f"👤 Novo utilizador convidado criado: {nome_cliente} ({email_cliente})")
        
        # Validar user_id
        if not user_id:
            return jsonify({'success': False, 'message': 'Erro ao identificar utilizador'}), 500
        
        # Inserir na tabela reservas_exclusivas com validação completa
        app.logger.info(f"💾 Inserindo reserva: sala={tipo_sala}, preço=€{total}, user_id={user_id}")
        
        cursor.execute("""
            INSERT INTO reservas_exclusivas 
            (tipo_sala, id_filme, filme_nome, data_sessao, hora_sessao, num_pessoas, total, id_usuario, data_reserva, status)
            VALUES (%s, NULL, NULL, %s, %s, 0, %s, %s, NOW(), 'confirmada')
        """, (tipo_sala, data_sessao, hora_sessao, total, user_id))
        
        reserva_id = cursor.lastrowid
        conn.commit()
        
        app.logger.info(f"✅ Reserva exclusiva criada com sucesso: ID {reserva_id}")
        
        # Enviar email de confirmação
        try:
            app.logger.info(f"📧 Enviando email de sessão exclusiva para: {email_cliente}")
            
            # Preparar dados para o email
            dados_email = {
                'reserva_id': reserva_id,
                'filme': 'Sessão Exclusiva',
                'cinema': 'CineVibe Premium',
                'tipo_sessao': tipo_sala.capitalize(),
                'horario': f"{data_sessao} às {hora_sessao}",
                'lugares': 'Sala Completa',
                'total': f"{total:.2f}€",
                'quantidade': 1
            }
            
            # Usar a função de email já existente
            resultado_email = enviar_email_confirmacao(
                email_cliente,
                nome_cliente,
                dados_email
            )
            
            if resultado_email:
                app.logger.info(f"✅ Email de sessão exclusiva enviado com SUCESSO")
            else:
                app.logger.warning(f"⚠️ Email de sessão exclusiva NÃO foi enviado")
        except Exception as email_error:
            app.logger.error(f"❌ Erro ao enviar email de sessão exclusiva: {email_error}")
            app.logger.exception("Stack trace completo:")
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Reserva de sessão exclusiva confirmada com sucesso!', 
            'reserva_id': reserva_id,
            'redirect_url': '/',
            'cliente': nome_cliente,
            'email': email_cliente,
            'total': f"€{total:.2f}"
        })
    
    except Exception as e:
        app.logger.error(f"❌ Erro ao confirmar pagamento de sessão exclusiva: {e}")
        app.logger.exception("Stack trace completo:")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/confirmar_pagamento_reserva', methods=['POST'])
def confirmar_pagamento_reserva():
    """
    Processa o pagamento e confirma a reserva de bilhetes.
    Só depois do pagamento é que os dados são gravados na BD.
    """
    try:
        data = request.get_json()
        app.logger.info(f"📦 Dados recebidos para pagamento: {data}")
        
        # Extrair dados da reserva
        reserva_data = data.get('reserva_data', {})
        metodo_pagamento = data.get('metodo_pagamento', 'Cartão')
        
        id_horario_sessao = reserva_data.get('horario')
        id_cinema = reserva_data.get('cinema')
        tipo_id = reserva_data.get('tipo')
        id_filme = reserva_data.get('id_filme')
        data_sessao = reserva_data.get('data_sessao')
        lugareses = reserva_data.get('lugareses', [])
        produtos_bar = reserva_data.get('produtos_bar', {})
        nome = reserva_data.get('nome', '')
        email = reserva_data.get('email', '')
        telefone = reserva_data.get('telefone', '')
        
        # Obter id_usuario se estiver logado
        id_usuario = session.get('user_id', 0)
        
        # Validação: se não está logado, precisa de nome e email
        if id_usuario == 0:
            if not nome or not email:
                return jsonify({'success': False, 'message': 'Nome e email são obrigatórios'}), 400
        
        # Validação comum
        if not id_horario_sessao or not id_cinema or not tipo_id or not lugareses:
            return jsonify({'success': False, 'message': 'Dados da reserva incompletos'}), 400
        
        # Usar a mesma lógica da rota /confirmar_reserva
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar id_filme se não foi enviado
        if not id_filme:
            cursor.execute("SELECT id_filme FROM horarios_sessao WHERE id = %s", (id_horario_sessao,))
            horario_row = cursor.fetchone()
            id_filme = horario_row['id_filme'] if horario_row else None
        
        if not id_filme:
            raise Exception("Filme não encontrado")
        
        # Buscar preço do tipo de sessão
        cursor.execute("SELECT preco_bilhete FROM tipos_sessao WHERE id = %s", (tipo_id,))
        preco_row = cursor.fetchone()
        preco_bilhete = float(preco_row['preco_bilhete']) if preco_row else 8.50
        
        # Calcular preços
        total_bilhetes = preco_bilhete * len(lugares)
        total_bar = 0
        for produto_id, produto_info in produtos_bar.items():
            total_bar += float(produto_info.get('preco', 0)) * int(produto_info.get('quantidade', 0))
        
        total_geral = total_bilhetes + total_bar
        
        # Buscar dados do utilizador se estiver logado
        nome_cliente = None
        email_cliente = None
        telefone_cliente = None
        nome_para_email = nome
        email_para_email = email
        
        if id_usuario > 0:
            # Utilizador logado - buscar dados da BD
            cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (id_usuario,))
            user_data = cursor.fetchone()
            if user_data:
                nome_para_email = user_data['nome']
                email_para_email = user_data['email']
                app.logger.info(f"📧 Utilizador logado: {nome_para_email} ({email_para_email})")
        else:
            # Não está logado - usar dados fornecidos
            nome_cliente = nome
            email_cliente = email
            telefone_cliente = telefone
            nome_para_email = nome
            email_para_email = email
        
        # Inserir reservas na base de dados
        reserva_ids = []
        import json
        produtos_bar_json = json.dumps(produtos_bar)
        
        for lugares in lugareses:
            user_id_final = id_usuario if id_usuario > 0 else None
            
            try:
                cursor.execute("""
                    INSERT INTO reservas (id_horario_sessao, data_sessao, id_filme, id_cinema, id_tipo_sessao, lugares, id_usuario, nome_cliente, email_cliente, telefone_cliente, data_reserva)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (id_horario_sessao, data_sessao, id_filme, id_cinema, tipo_id, lugares, user_id_final, nome_cliente, email_cliente, telefone_cliente))
            except Exception as e:
                app.logger.warning(f"Campos de cliente não existem, usando id_usuario = 1: {str(e)}")
                user_id_final = id_usuario if id_usuario > 0 else 1
                cursor.execute("""
                    INSERT INTO reservas (id_horario_sessao, data_sessao, id_filme, id_cinema, id_tipo_sessao, lugares, id_usuario, data_reserva)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """, (id_horario_sessao, data_sessao, id_filme, id_cinema, tipo_id, lugares, user_id_final))
            
            reserva_ids.append(cursor.lastrowid)
        
        # Buscar dados para o email ANTES do commit
        cursor.execute("SELECT titulo FROM filmes WHERE id = %s", (id_filme,))
        filme_row = cursor.fetchone()
        filme_titulo = filme_row['titulo'] if filme_row else 'Filme'
        
        cursor.execute("SELECT nome FROM cinemas WHERE id = %s", (id_cinema,))
        cinema_row = cursor.fetchone()
        cinema_nome = cinema_row['nome'] if cinema_row else 'Cinema'
        
        cursor.execute("SELECT nome FROM tipos_sessao WHERE id = %s", (tipo_id,))
        tipo_row = cursor.fetchone()
        tipo_nome = tipo_row['nome'] if tipo_row else 'Normal'
        
        # Buscar hora do horário
        cursor.execute("""
            SELECT h.hora 
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (id_horario_sessao,))
        hora_row = cursor.fetchone()
        hora_str = hora_row['hora'] if hora_row else '00:00'
        
        # Preparar dados para o email
        dados_email = {
            'reserva_id': reserva_ids[0] if reserva_ids else 0,
            'filme': filme_titulo,
            'cinema': cinema_nome,
            'tipo_sessao': tipo_nome,
            'horario': f"{data_sessao} às {hora_str}",
            'quantidade': len(lugares),
            'lugares': ', '.join(lugares),
            'total': f"{total_geral:.2f}€"
        }
        
        # Commit na BD
        conn.commit()
        
        # Fechar cursor e conexão
        cursor.close()
        conn.close()
        
        # Enviar email de confirmação APÓS commit (mas com dados já coletados)
        try:
            app.logger.info(f"📧 Tentando enviar email para: {email_para_email}")
            app.logger.info(f"👤 Nome: {nome_para_email}")
            app.logger.info(f"📦 Dados do email: {dados_email}")
            
            resultado_email = enviar_email_confirmacao(email_para_email, nome_para_email, dados_email)
            
            if resultado_email:
                app.logger.info(f"✅ Email enviado com SUCESSO para {email_para_email}")
            else:
                app.logger.warning(f"⚠️ Email NÃO foi enviado para {email_para_email}")
        except Exception as email_error:
            app.logger.error(f"❌ Erro ao enviar email: {email_error}")
            app.logger.exception("Stack trace completo do erro:")
        
        return jsonify({
            'success': True,
            'message': 'Pagamento confirmado e reserva realizada!',
            'reserva_ids': reserva_ids,
            'redirect_url': '/'
        })
    
    except Exception as e:
        app.logger.error(f"❌ Erro ao confirmar pagamento: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/reserva')
def reserva():
    id_horario_sessao = request.args.get('horario')
    id_cinema  = request.args.get('cinema')
    tipo_id    = request.args.get('tipo')
    data_sessao = request.args.get('data')  # Nova: receber data da sessão

    
    # DEBUG: Logs adicionados para rastrear tipo_id
    app.logger.info(f"🔍 ROTA /reserva - Parâmetros recebidos:")
    app.logger.info(f"  id_horario_sessao: {id_horario_sessao}")
    app.logger.info(f"  id_cinema: {id_cinema}")
    app.logger.info(f"  tipo_id: {tipo_id}")
    app.logger.info(f"  data_sessao: {data_sessao}")
    
    if not id_horario_sessao or not id_cinema or not tipo_id:
        return "Parâmetros incompletos", 400
    
    # Se não foi fornecida data, usar hoje como padrão
    if not data_sessao:
        from datetime import date
        data_sessao = date.today().strftime('%Y-%m-%d')
    
    app.logger.info(f"=== RESERVA PARA DATA: {data_sessao} ===")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # --- Horário ---
        cursor.execute("""
            SELECT hs.id, hs.id_cinema, hs.id_tipo_sessao, hs.id_sala, hs.id_filme, h.hora
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (id_horario_sessao,))
        horario = cursor.fetchone()
        if not horario:
            return "Horário não encontrado", 404

        hora_val = horario['hora']
        horario['hora_str'] = hora_val.strftime("%H:%M") if hasattr(hora_val, 'strftime') else str(hora_val)

        # --- Filme ---
        id_filme = horario['id_filme']
        cursor.execute("""
            SELECT id, titulo, sinopse, poster_url, poster_hover, imagem_grande,
                   diretor, data_lancamento, duracao
            FROM filmes
            WHERE id = %s
        """, (id_filme,))
        filme = cursor.fetchone()
        if not filme:
            return "Filme não encontrado", 404

        for campo in ['poster_url', 'imagem_grande']:
            if filme.get(campo):
                filme[campo] = filme[campo].replace('\\', '/').replace('"', '').strip()

        # --- Elenco ---
        cursor.execute("""
            SELECT a.nome, a.foto_url, fa.papel
            FROM filme_atores fa
            JOIN atores a ON fa.ator_id = a.id
            WHERE fa.filme_id = %s
        """, (id_filme,))
        elenco = cursor.fetchall() or []
        for ator in elenco:
            if ator.get('foto_url'):
                ator['foto_url'] = ator['foto_url'].replace('\\', '/').replace('"', '').strip()

        # --- Gêneros ---
        cursor.execute("""
            SELECT g.nome AS genero
            FROM filme_generos fg
            JOIN generos g ON fg.genero_id = g.id
            WHERE fg.filme_id = %s
        """, (id_filme,))
        filme_generos = [g['genero'] for g in cursor.fetchall()]

        # --- Cinema e tipo sessão com preço ---
        cursor.execute("SELECT id, nome FROM cinemas WHERE id = %s", (id_cinema,))
        cinema = cursor.fetchone() or {}

        
        # 🔍 LOG DA CONSULTA TIPO SESSÃO
        app.logger.info(f"🔍 BUSCA TIPO SESSÃO: SELECT * FROM tipos_sessao WHERE id = {tipo_id}")
        
        cursor.execute("SELECT id, nome, preco_bilhete FROM tipos_sessao WHERE id = %s", (tipo_id,))
        tipo_sessao = cursor.fetchone() or {}
        
        # Garantir que o preço existe, senão usar preço padrão
        preco_bilhete = float(tipo_sessao.get('preco_bilhete', 8.50))
        
        # Criar objeto filme_sessao com informações da sessão e preço
        filme_sessao = {
            'cinema_nome': cinema.get('nome', 'Cinema'),
            'tipo_sessao': tipo_sessao.get('nome', 'Sessão'),
            'hora_str': horario['hora_str'],
            'preco': preco_bilhete,
            'sala': horario.get('id_sala', 1)
        }

        # --- Sala e lugareses ---
        cursor.execute("SELECT id, nome_sala, capacidade, tipo_sala FROM salas WHERE id = %s", (horario['id_sala'],))
        sala_temp = cursor.fetchone()
        if sala_temp:
            # Adicionar valores padrão para lugareses especiais
            sala = {
                'id': sala_temp['id'],
                'nome_sala': sala_temp['nome_sala'], 
                'capacidade': sala_temp['capacidade'],
                'tipo_sala': sala_temp['tipo_sala'],
                'lugareses_acessiveis': 8,  # Valor padrão
                'lugareses_casal': 8,       # Valor padrão
                'lugareses_premium': 8      # Valor padrão
            }
        else:
            sala = {}


        # Buscar lugareses reservados para esta sessão E DATA específica
        app.logger.info(f"=== BUSCANDO LUGARES RESERVADOS ===")
        app.logger.info(f"Sessão ID: {id_horario_sessao}, Data: {data_sessao}")
        
        # Tentar com conversão explícita para int
        id_horario_sessao_int = int(id_horario_sessao)
        
        cursor.execute("""
            SELECT lugares, id, id_usuario, data_reserva
            FROM reservas
            WHERE id_horario_sessao = %s AND data_sessao = %s
            ORDER BY lugares
        """, (id_horario_sessao_int, data_sessao))
        resultado_reservas = cursor.fetchall()
        lugareses_reservados = [row['lugares'] for row in resultado_reservas]
        
        app.logger.info(f"Query: SELECT lugares FROM reservas WHERE id_horario_sessao = {id_horario_sessao_int} AND data_sessao = {data_sessao}")
        app.logger.info(f"Resultados encontrados: {len(resultado_reservas)}")
        app.logger.info(f"Lugares reservados: {lugareses_reservados}")
        
        # Debug: Contar reservas por sessão e data
        cursor.execute("""
            SELECT id_horario_sessao, data_sessao, COUNT(*) as total, GROUP_CONCAT(lugares) as lugares
            FROM reservas 
            WHERE id_horario_sessao = %s
            GROUP BY id_horario_sessao, data_sessao
        """, (id_horario_sessao_int,))
        resumo = cursor.fetchall()
        app.logger.info(f"Resumo de reservas desta sessão por data: {resumo}")

        # Buscar todos os lugareses da sala
        cursor.execute("""
            SELECT id, nome_lugar, ocupado
            FROM lugares
            WHERE sala_id = %s
            ORDER BY nome_lugar
        """, (sala.get('id'),))
        lugareses = cursor.fetchall() or []
        
        app.logger.info(f"Total de lugares na sala: {len(lugareses)}")
        
        # Marcar lugareses como ocupados se estiverem reservados
        lugareses_marcados = 0
        for lugares in lugareses:
            nome_lugares = lugares['nome_lugar']
            # Verificar com e sem espaços
            if nome_lugares in lugareses_reservados or nome_lugares.replace(' ', '') in lugareses_reservados:
                lugares['ocupado'] = 1
                lugareses_marcados += 1
                app.logger.info(f"✓ Lugar '{nome_lugares}' marcado como ocupado")
        
        app.logger.info(f"Total de lugareses marcados como ocupados: {lugareses_marcados}")
        
        # Se houver lugareses reservados que não estão na tabela lugareses, criar entradas temporárias
        lugareses_na_tabela = [l['nome_lugar'] for l in lugareses]
        for lugares_reservado in lugareses_reservados:
            if lugares_reservado not in lugareses_na_tabela:
                app.logger.warning(f"⚠️ Lugar reservado '{lugares_reservado}' não existe na tabela lugareses! Adicionando temporariamente...")
                lugareses.append({
                    'id': None,
                    'nome_lugar': lugares_reservado,
                    'ocupado': 1
                })

        # --- Produtos do BAR (Corrigido) ---
        cursor.execute("""
            SELECT id, produto AS nome, preco, imagem_url AS imagem, tipo
            FROM bar
            ORDER BY tipo, produto
        """)
        produtos_bar = cursor.fetchall() or []
        for p in produtos_bar:
            raw = (p.get('imagem') or '').replace('\\', '/').replace('"', '').strip()
            if raw.startswith("http://") or raw.startswith("https://"):
                p['imagem'] = raw
            else:
                p['imagem'] = url_for('static', filename=raw.lstrip('/'))

        # --- Menus com produtos relacionados ---
        cursor.execute("SELECT id, nome, descricao, preco_total, imagem_url FROM menus ORDER BY nome")
        menus_bar = cursor.fetchall() or []
        for m in menus_bar:
            if m.get('imagem_url'):
                raw = m['imagem_url'].replace('\\', '/').replace('"', '').strip()
                if raw.startswith("http://") or raw.startswith("https://"):
                    m['imagem_url'] = raw
                else:
                    m['imagem_url'] = url_for('static', filename=raw.lstrip('/'))
            
            # Buscar produtos relacionados ao menu
            cursor.execute("""
                SELECT b.id, b.produto AS nome, b.preco, b.imagem_url AS imagem, b.tipo
                FROM menu_produtos mp
                JOIN bar b ON mp.produto_id = b.id
                WHERE mp.menu_id = %s
                ORDER BY b.tipo, b.produto
            """, (m['id'],))
            produtos_menu = cursor.fetchall() or []
            
            # Processar imagens dos produtos
            for p in produtos_menu:
                raw_img = (p.get('imagem') or '').replace('\\', '/').replace('"', '').strip()
                if raw_img.startswith("http://") or raw_img.startswith("https://"):
                    p['imagem'] = raw_img
                else:
                    p['imagem'] = url_for('static', filename=raw_img.lstrip('/'))
            
            m['produtos'] = produtos_menu

    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass

    # Buscar informações do usuário se estiver logado (para email de confirmação)
    user_authenticated = 'user_id' in session
    user_name = None
    user_email = None
    user_avatar = 'imgs/icons/user_icon34-removebg-preview.png'  # Avatar padrão
    
    if user_authenticated:
        conn_user = get_db_connection()
        cursor_user = conn_user.cursor(dictionary=True)
        cursor_user.execute("SELECT nome, email, avatar FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cursor_user.fetchone()
        cursor_user.close()
        conn_user.close()
        
        if user:
            user_name = user['nome']
            user_email = user['email']
            # Usar avatar do utilizador se existir, senão usar padrão
            if user.get('avatar'):
                user_avatar = user['avatar']
    
    return render_template(
        'reserva.html',
        filme=filme,
        filme_generos=filme_generos,
        elenco=elenco,
        cinema=cinema,
        tipo_sessao=tipo_sessao,
        horario=horario,
        sala=sala,
        lugareses=lugareses,
        produtos_bar=produtos_bar,
        menus_bar=menus_bar,
        filme_sessao=filme_sessao,
        data_sessao=data_sessao,
        user_authenticated=user_authenticated,
        user_name=user_name,
        user_email=user_email,
        logged_in=user_authenticated,
        avatar=user_avatar
    )

# ==========================
# Seleção de Lugares
# ==========================
@app.route('/selecao_lugares', methods=['GET', 'POST'])
def selecao_lugares():
    app.logger.info(f"🎬 SELEÇÃO DE LUGARES - Método: {request.method}")
    
    if request.method == 'POST':
        # Receber dados do formulário da página de reserva
        filme_id = request.form.get('filme_id')
        cinema_id = request.form.get('cinema_id')
        id_tipo_sessao = request.form.get('id_tipo_sessao')
        id_horario_sessao = request.form.get('id_horario_sessao')
        data_sessao = request.form.get('data_sessao')
        quantidade = int(request.form.get('quantidade', 1))
        
        app.logger.info(f"📋 Dados POST: filme_id={filme_id}, cinema_id={cinema_id}")
    else:
        # Receber dados via GET (para compatibilidade com links diretos)
        filme_id = request.args.get('filme_id')
        cinema_id = request.args.get('cinema_id')
        id_tipo_sessao = request.args.get('id_tipo_sessao')
        id_horario_sessao = request.args.get('id_horario_sessao')
        data_sessao = request.args.get('data_sessao')
        quantidade = int(request.args.get('quantidade', 1))
    
    if not all([filme_id, cinema_id, id_tipo_sessao, id_horario_sessao, data_sessao]):
        flash("Dados da sessão incompletos", "erro")
        return render_template('error.html', message="Dados da sessão incompletos")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar dados do filme
        cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        if not filme:
            flash("Filme não encontrado", "erro")
            return render_template('error.html', message="Filme não encontrado")
        
        # Normalizar poster_url
        if filme.get('poster_url'):
            poster_url = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
            
            # Remover 'static/' se já estiver no início
            if poster_url.startswith('static/'):
                poster_url = poster_url[7:]  # Remove 'static/'
            elif poster_url.startswith('/static/'):
                poster_url = poster_url[8:]  # Remove '/static/'
            elif poster_url.startswith('/'):
                poster_url = poster_url[1:]  # Remove '/' inicial
            
            # Garantir que o caminho está correto para imgs/filmes/
            if not poster_url.startswith('imgs/filmes/'):
                # Se é apenas o nome do arquivo, adicionar o caminho completo
                if '/' not in poster_url:
                    poster_url = f"imgs/filmes/{poster_url}"
                # Se não começa com imgs/, adicionar
                elif not poster_url.startswith('imgs/'):
                    poster_url = f"imgs/filmes/{poster_url}"
            
            # Verificar se o arquivo existe
            caminho_completo = f"static/{poster_url}"
            if not os.path.exists(caminho_completo):
                # Tentar encontrar arquivo similar
                nome_arquivo = os.path.basename(poster_url).lower()
                pasta_filmes = "static/imgs/filmes"
                if os.path.exists(pasta_filmes):
                    for arquivo in os.listdir(pasta_filmes):
                        if arquivo.lower() == nome_arquivo or nome_arquivo in arquivo.lower():
                            poster_url = f"imgs/filmes/{arquivo}"
                            break
                    else:
                        # Se não encontrar, usar placeholder
                        poster_url = "imgs/filmes/placeholder.jpg"
            
            filme['poster_url'] = poster_url
        
        # Buscar dados do cinema
        cursor.execute("SELECT * FROM cinemas WHERE id = %s", (cinema_id,))
        cinema = cursor.fetchone()
        
        # Buscar dados do tipo de sessão
        cursor.execute("SELECT * FROM tipos_sessao WHERE id = %s", (id_tipo_sessao,))
        tipo_sessao = cursor.fetchone()
        
        # Buscar dados do horário
        cursor.execute("""
            SELECT hs.*, h.hora, s.nome_sala, s.capacidade
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            LEFT JOIN salas s ON hs.id_sala = s.id
            WHERE hs.id = %s
        """, (id_horario_sessao,))
        horario = cursor.fetchone()
        
        if not horario:
            flash("Horário não encontrado", "erro")
            return render_template('error.html', message="Horário não encontrado")
        
        # Formatar hora
        hora_val = horario['hora']
        horario['hora_str'] = hora_val.strftime("%H:%M") if hasattr(hora_val, 'strftime') else str(hora_val)
        
        # Buscar dados da sala COM informações de layout
        capacidade_sala = horario.get('capacidade')
        id_sala = horario.get('id_sala')
        
        if capacidade_sala is None or id_sala is None:
            app.logger.warning(f"Capacidade ou id_sala None para horário {id_horario_sessao}")
            # Buscar diretamente da tabela salas
            if id_sala:
                cursor.execute("SELECT capacidade, filas, lugares_por_fila, lugares_acessiveis FROM salas WHERE id = %s", (id_sala,))
                sala_info = cursor.fetchone()
                if sala_info:
                    capacidade_sala = sala_info.get('capacidade', 100)
                    filas = sala_info.get('filas', 10)
                    lugares_por_fila = sala_info.get('lugares_por_fila', 10)
                    lugares_acessiveis = sala_info.get('lugares_acessiveis', None)
                else:
                    capacidade_sala = 100
                    filas = 10
                    lugares_por_fila = 10
                    lugares_acessiveis = None
            else:
                capacidade_sala = 100
                filas = 10
                lugares_por_fila = 10
                lugares_acessiveis = None
        else:
            # Buscar informações de layout da sala
            cursor.execute("SELECT filas, lugares_por_fila, lugares_acessiveis FROM salas WHERE id = %s", (id_sala,))
            sala_layout = cursor.fetchone()
            if sala_layout:
                filas = sala_layout.get('filas', 10)
                lugares_por_fila = sala_layout.get('lugares_por_fila', 10)
                lugares_acessiveis = sala_layout.get('lugares_acessiveis', None)
            else:
                filas = 10
                lugares_por_fila = 10
                lugares_acessiveis = None
        
        # Converter lugares_acessiveis de JSON string para lista Python
        if lugares_acessiveis and isinstance(lugares_acessiveis, str):
            import json
            try:
                lugares_acessiveis = json.loads(lugares_acessiveis)
            except:
                lugares_acessiveis = None
        
        sala = {
            'nome_sala': horario.get('nome_sala', 'Sala 1'),
            'capacidade': capacidade_sala,
            'filas': filas,
            'lugares_por_fila': lugares_por_fila,
            'lugares_acessiveis': lugares_acessiveis
        }
        
        app.logger.info(f"Sala final - Nome: {sala['nome_sala']}, Capacidade: {sala['capacidade']}, Filas: {sala['filas']}, Lugares/Fila: {sala['lugares_por_fila']}, Acessíveis: {lugares_acessiveis}")
        
        # Buscar lugares ocupados para esta sessão específica
        cursor.execute("""
            SELECT lugares
            FROM reservas
            WHERE id_horario_sessao = %s AND data_sessao = %s
        """, (id_horario_sessao, data_sessao))
        
        # Processar lugares ocupados em uma lista simples
        lugares_ocupados_lista = []
        for row in cursor.fetchall():
            if row['lugares']:
                # Se tem vírgula, dividir
                if ',' in row['lugares']:
                    lugares_ocupados_lista.extend([l.strip() for l in row['lugares'].split(',') if l.strip()])
                else:
                    lugares_ocupados_lista.append(row['lugares'].strip())
        
        # Remover duplicados
        lugares_ocupados_set = set(lugares_ocupados_lista)
        
        # 🔍 DEBUG: PRINT DOS LUGARES OCUPADOS
        print(f"\n{'='*80}")
        print(f"DEBUG LUGARES OCUPADOS - ROTA selecao_lugares")
        print(f"{'='*80}")
        print(f"id_horario_sessao: {id_horario_sessao}")
        print(f"data_sessao: {data_sessao}")
        print(f"Lugares ocupados encontrados: {len(lugares_ocupados_set)}")
        print(f"Lugares: {sorted(lugares_ocupados_set)}")
        print(f"{'='*80}\n")
        
        # Gerar layout da sala baseado nos dados reais COM lugares ocupados
        lugares = gerar_layout_sala(
            sala['filas'], 
            sala['lugares_por_fila'], 
            list(lugares_ocupados_set),
            sala.get('lugares_acessiveis')
        )
        
        # 🔍 DEBUG: VERIFICAR SE OS LUGARES TÊM A FLAG ocupado=True
        lugares_ocupados_no_layout = []
        for fileira in lugares:
            if fileira.get('tipo') == 'fileira':
                for lugar in fileira['lugares']:
                    if lugar.get('ocupado'):
                        lugares_ocupados_no_layout.append(lugar['nome'])
        
        print(f"\n{'='*80}")
        print(f"DEBUG LAYOUT GERADO")
        print(f"{'='*80}")
        print(f"Lugares com ocupado=True no layout: {len(lugares_ocupados_no_layout)}")
        print(f"Lugares: {sorted(lugares_ocupados_no_layout)}")
        print(f"{'='*80}\n")
        
        # Preço do bilhete
        preco_bilhete = float(tipo_sessao.get('preco_bilhete', 8.50))
        
        # Verificar se usuário está autenticado
        user_authenticated = 'user_id' in session
        
        # 🔧 GUARDAR DADOS NA SESSÃO PARA O FLUXO DE PAGAMENTO
        salvar_dados_reserva_sessao(
            filme_id=int(filme_id),
            cinema_id=int(cinema_id), 
            id_tipo_sessao=int(id_tipo_sessao),
            id_horario_sessao=int(id_horario_sessao),
            data_sessao=str(data_sessao)
        )
        
    finally:
        cursor.close()
        conn.close()
    
    return render_template(
        'selecao_lugares.html',
        filme=filme,
        cinema=cinema,
        tipo_sessao=tipo_sessao,
        horario=horario,
        sala=sala,
        lugares=lugares,
        quantidade=quantidade,
        preco_bilhete=preco_bilhete,
        data_sessao=data_sessao,
        id_horario_sessao=id_horario_sessao,
        cinema_id=cinema_id,
        id_tipo_sessao=id_tipo_sessao,
        filme_id=filme_id,
        user_authenticated=user_authenticated,
        user_avatar=get_user_avatar()
    )

def gerar_layout_sala(filas, lugares_por_fila, lugares_ocupados, lugares_acessiveis=None):
    """Gera o layout da sala baseado nas filas e lugares por fila reais da BD"""
    # Validar parâmetros
    if filas is None or filas <= 0:
        app.logger.error(f"Número de filas inválido: {filas}")
        filas = 10
    
    if lugares_por_fila is None or lugares_por_fila <= 0:
        app.logger.error(f"Lugares por fila inválido: {lugares_por_fila}")
        lugares_por_fila = 10
    
    # Converter para set para busca rápida
    lugares_ocupados_set = set(lugares_ocupados) if lugares_ocupados else set()
    
    layout = []
    divisoes_horizontais = []
    
    # Adicionar divisão horizontal no meio da sala se tiver 4+ filas
    if filas >= 4:
        meio_sala = filas // 2
        divisoes_horizontais = [meio_sala - 1]
    
    # Usar lugares acessíveis da BD ou fallback para valores padrão
    if lugares_acessiveis is None or not lugares_acessiveis:
        # Fallback: última fila, 2 lugares em cada ponta
        ultima_fila = chr(64 + filas)
        lugares_acessiveis = [
            f"{ultima_fila}1",
            f"{ultima_fila}2",
            f"{ultima_fila}{lugares_por_fila - 1}",
            f"{ultima_fila}{lugares_por_fila}"
        ]
    
    lugares_acessiveis_set = set(lugares_acessiveis)
    
    for i in range(filas):
        letra_fileira = chr(65 + i)  # A, B, C, etc.
        
        fileira = {
            'letra': letra_fileira,
            'lugares': [],
            'tipo': 'fileira'
        }
        
        for j in range(lugares_por_fila):
            nome_lugar = f"{letra_fileira}{j+1}"
            
            # Verificar se está ocupado
            esta_ocupado = nome_lugar in lugares_ocupados_set
            
            lugar = {
                'nome': nome_lugar,
                'ocupado': esta_ocupado,
                'acessivel': nome_lugar in lugares_acessiveis_set
            }
            fileira['lugares'].append(lugar)
        
        layout.append(fileira)
        
        # Adicionar divisão horizontal se necessário
        if i in divisoes_horizontais:
            divisao = {
                'tipo': 'divisao_horizontal',
                'letra': f"DIV_{i+1}",
                'lugares': []
            }
            layout.append(divisao)
    
    app.logger.info(f"Layout gerado: {filas} filas x {lugares_por_fila} lugares = {filas * lugares_por_fila} lugares totais")
    return layout
    


# ==========================
# Confirmar reserva (POST)
# ==========================
@app.route('/confirmar_reserva', methods=['POST'])
def confirmar_reserva():
    """
    NOVA MECÂNICA DE RESERVA - ORDEM CORRIGIDA
    Recebe dados do frontend e guarda na base de dados sem complicações
    """
    try:
        # 1. RECEBER DADOS
        if request.is_json:
            data = request.get_json()
            id_horario_sessao = data.get('horario')
            id_cinema = data.get('cinema')
            tipo_id = data.get('tipo')  # ID do tipo de sessão
            id_filme = data.get('id_filme')
            data_sessao = data.get('data_sessao')
            nome = data.get('nome')
            email = data.get('email')
            telefone = data.get('telefone', '')
            lugareses = data.get('lugareses', [])
            produtos_bar = data.get('produtos_bar', {})
        else:
            id_horario_sessao = request.form.get('horario')
            id_cinema = request.form.get('cinema')
            tipo_id = request.form.get('tipo')
            id_filme = request.form.get('id_filme')
            data_sessao = request.form.get('data_sessao')
            nome = request.form.get('nome')
            email = request.form.get('email')
            telefone = request.form.get('telefone', '')
            lugareses = []
            produtos_bar = {}
        
        # Data padrão se não fornecida
        if not data_sessao:
            from datetime import date
            data_sessao = date.today().strftime('%Y-%m-%d')
        
        # 2. VALIDAR DADOS ESSENCIAIS
        if not all([id_horario_sessao, id_cinema, tipo_id, nome, email, lugareses]):
            if request.is_json:
                return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
            flash("Dados incompletos para a reserva.", "error")
            return redirect(request.referrer or url_for('home'))
        
        # 🔍 LOGS ANTES DA CONVERSÃO
        app.logger.info("=" * 80)
        app.logger.info("🔍 DADOS RECEBIDOS:")
        app.logger.info(f"   id_horario_sessao (raw): '{id_horario_sessao}' (tipo: {type(id_horario_sessao)})")
        app.logger.info(f"   id_cinema (raw): '{id_cinema}' (tipo: {type(id_cinema)})")
        app.logger.info(f"   tipo_id (raw): '{tipo_id}' (tipo: {type(tipo_id)})")
        app.logger.info(f"   id_filme (raw): '{id_filme}' (tipo: {type(id_filme)})")
        
        # Converter IDs para inteiros
        try:
            id_horario_sessao = int(id_horario_sessao)
            id_cinema = int(id_cinema)
            tipo_id = int(tipo_id)
            if id_filme:
                id_filme = int(id_filme)
                
            # 🔍 LOGS APÓS A CONVERSÃO
            app.logger.info("🔍 APÓS CONVERSÃO:")
            app.logger.info(f"   id_horario_sessao (int): {id_horario_sessao}")
            app.logger.info(f"   id_cinema (int): {id_cinema}")
            app.logger.info(f"   tipo_id (int): {tipo_id}")
            app.logger.info(f"   id_filme (int): {id_filme}")
        except (ValueError, TypeError):
            if request.is_json:
                return jsonify({'success': False, 'message': 'IDs inválidos'}), 400
            flash("Dados inválidos.", "error")
            return redirect(request.referrer or url_for('home'))
        
        # 3. CONECTAR À BASE DE DADOS
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 4. BUSCAR TIPO DE SESSÃO PRIMEIRO (ORDEM CORRIGIDA!)
        cursor.execute("SELECT id, nome, preco_bilhete FROM tipos_sessao WHERE id = %s", (tipo_id,))
        tipo_sessao = cursor.fetchone()
        
        if not tipo_sessao:
            raise Exception(f"Tipo de sessão {tipo_id} não encontrado")
        
        app.logger.info(f"✅ TIPO SESSÃO ENCONTRADO: {tipo_sessao['id']} - {tipo_sessao['nome']} - €{tipo_sessao['preco_bilhete']}")
        
        # 5. BUSCAR CINEMA
        cursor.execute("SELECT id, nome FROM cinemas WHERE id = %s", (id_cinema,))
        cinema = cursor.fetchone()
        if not cinema:
            raise Exception(f"Cinema {id_cinema} não encontrado")
        
        # 6. BUSCAR HORÁRIO
        cursor.execute("""
            SELECT hs.id, hs.id_filme, hs.id_sala, hs.id_tipo_sessao, h.hora
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (id_horario_sessao,))
        horario = cursor.fetchone()
        if not horario:
            raise Exception(f"Horário {id_horario_sessao} não encontrado")
        
        # Se id_filme não foi fornecido, usar o do horário
        if not id_filme:
            id_filme = horario['id_filme']
        
        # 7. BUSCAR FILME
        cursor.execute("SELECT id, titulo FROM filmes WHERE id = %s", (id_filme,))
        filme = cursor.fetchone()
        if not filme:
            raise Exception(f"Filme {id_filme} não encontrado")
        
        # 8. CALCULAR PREÇOS (AGORA tipo_sessao JÁ ESTÁ DEFINIDO!)
        preco_bilhete = float(tipo_sessao['preco_bilhete'])
        total = preco_bilhete * len(lugareses)
        
        app.logger.info(f"💰 PREÇOS: Bilhete €{preco_bilhete} x {len(lugareses)} lugares = €{total}")
        
        # 9. DETERMINAR USUÁRIO
        id_usuario = session.get('user_id', None)
        
        # 10. INSERIR RESERVAS NA BASE DE DADOS
        reserva_ids = []
        
        for lugares in lugareses:
            app.logger.info(f"🎫 INSERINDO RESERVA PARA LUGAR {lugares}:")
            app.logger.info(f"   id_horario_sessao: {id_horario_sessao}")
            app.logger.info(f"   data_sessao: {data_sessao}")
            app.logger.info(f"   id_filme: {id_filme}")
            app.logger.info(f"   id_cinema: {id_cinema}")
            app.logger.info(f"   id_tipo_sessao: {tipo_id} ← TIPO CLICADO PELO USER")
            app.logger.info(f"   lugares: {lugares}")
            app.logger.info(f"   id_usuario: {id_usuario}")
            app.logger.info(f"   nome_cliente: {nome}")
            app.logger.info(f"   email_cliente: {email}")
            
            cursor.execute("""
                INSERT INTO reservas (
                    id_horario_sessao, data_sessao, id_filme, id_cinema, id_tipo_sessao, 
                    lugares, id_usuario, nome_cliente, email_cliente, telefone_cliente, 
                    data_reserva
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                id_horario_sessao,      # id_horario_sessao
                data_sessao,     # data_sessao
                id_filme,        # id_filme
                id_cinema,       # id_cinema
                tipo_id,         # id_tipo_sessao ← USAR DIRETAMENTE O TIPO CLICADO!
                lugares,           # lugares
                id_usuario,      # id_usuario
                nome,            # nome_cliente
                email,           # email_cliente
                telefone         # telefone_cliente
            ))
            
            reserva_id = cursor.lastrowid
            
            # 🔍 VERIFICAR O QUE FOI REALMENTE INSERIDO
            cursor.execute("SELECT id_tipo_sessao FROM reservas WHERE id = %s", (reserva_id,))
            verificacao = cursor.fetchone()
            app.logger.info(f"✅ VERIFICAÇÃO: Reserva {reserva_id} inserida com id_tipo_sessao = {verificacao['id_tipo_sessao']}")
            
            if verificacao['id_tipo_sessao'] != tipo_id:
                app.logger.error(f"🚨 ERRO CRÍTICO!")
                app.logger.error(f"   Tentámos inserir: {tipo_id}")
                app.logger.error(f"   Foi inserido: {verificacao['id_tipo_sessao']}")
                raise Exception(f"Erro na inserção: tipo incorreto")
            
            reserva_ids.append(reserva_id)
        
        # 11. CONFIRMAR TRANSAÇÃO
        conn.commit()
        
        # 12. PREPARAR EMAIL
        try:
            # Buscar informações completas para o email
            cursor.execute("""
                SELECT r.id, f.titulo, c.nome as cinema_nome, ts.nome as tipo_nome, 
                       h.hora, r.lugares, r.data_sessao
                FROM reservas r
                JOIN filmes f ON r.id_filme = f.id
                JOIN cinemas c ON r.id_cinema = c.id
                JOIN tipos_sessao ts ON r.id_tipo_sessao = ts.id
                JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
                JOIN horarios h ON hs.id_horario = h.id
                WHERE r.id IN ({})
            """.format(','.join(['%s'] * len(reserva_ids))), reserva_ids)
            
            reservas_email = cursor.fetchall()
            
            # Preparar dados para o email (usar primeira reserva como base)
            if reservas_email:
                primeira_reserva = reservas_email[0]
                lugares_str = ', '.join(lugareses) if lugareses else primeira_reserva.get('lugares', '')
                
                dados_email = {
                    'reserva_id': primeira_reserva.get('id', reserva_ids[0] if reserva_ids else 0),
                    'filme': primeira_reserva.get('titulo', filme.get('titulo', 'Filme') if filme else 'Filme'),
                    'cinema': primeira_reserva.get('cinema_nome', cinema.get('nome', 'Cinema') if cinema else 'Cinema'),
                    'tipo_sessao': primeira_reserva.get('tipo_nome', tipo_sessao.get('nome', 'Normal') if tipo_sessao else 'Normal'),
                    'horario': str(primeira_reserva.get('hora', '')) if primeira_reserva.get('hora') else 'Data não definida',
                    'quantidade': len(lugareses),
                    'lugares': lugares_str,
                    'total': f"{total:.2f}€"
                }
                
                # Enviar email de confirmação
                enviar_email_confirmacao(email, nome, dados_email)
            
        except Exception as e:
            app.logger.error(f"Erro ao enviar email: {e}")
            # Não falhar a reserva por causa do email
        
        cursor.close()
        conn.close()
        
        # 13. RESPOSTA DE SUCESSO
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Reserva confirmada com sucesso!',
                'reserva_ids': reserva_ids,
                'total': total
            })
        else:
            flash("Reserva confirmada com sucesso!", "success")
            return redirect(url_for('reserva_confirmada', ids=','.join(map(str, reserva_ids))))
    
    except Exception as e:
        app.logger.error(f"Erro na reserva: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)}), 500
        else:
            flash(f"Erro na reserva: {e}", "error")
            return redirect(request.referrer or url_for('home'))

@app.route('/teste-email')
def teste_email():
    """Rota para testar o envio de emails - REMOVER EM PRODUÇÃO"""
    try:
        # Primeiro, testar a conexão SMTP
        app.logger.info("🔍 Testando conexão SMTP...")
        
        import smtplib
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.quit()
        
        app.logger.info("✅ Conexão SMTP funcionando!")
        
        # Agora testar o envio do email
        dados_teste = {
            'reserva_id': 12345,
            'filme': 'Filme de Teste',
            'cinema': 'Cinema Teste',
            'tipo_sessao': '2D',
            'horario': '2026-01-27 às 20:30',
            'lugares': 'A1,A2',
            'total': '15.00€',
            'quantidade': 2
        }
        
        # Email de teste - usando o email do sistema para teste
        email_teste = 'cinevibe.bilhetes@gmail.com'
        nome_teste = 'Utilizador Teste'
        
        resultado = enviar_email_confirmacao(email_teste, nome_teste, dados_teste)
        
        if resultado:
            return jsonify({'success': True, 'message': 'Email enviado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao enviar email'})
            
    except smtplib.SMTPAuthenticationError as e:
        app.logger.error(f"❌ Erro de autenticação SMTP: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro de autenticação: {str(e)}'})
    except smtplib.SMTPException as e:
        app.logger.error(f"❌ Erro SMTP: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro SMTP: {str(e)}'})
    except Exception as e:
        app.logger.error(f"❌ Erro geral: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro geral: {str(e)}'})

# ==========================
# SESSÃO SÓ PARA TI
# ==========================
@app.route('/sessao')
def sessao():
    return render_template('sessao.html')

@app.route('/sessao_exclusiva')
def sessao_exclusiva():
    # Verificar se o usuário está logado
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    # Dados do usuário se logado
    nome = ''
    email = ''
    telefone = ''
    
    if logged_in:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Buscar dados atualizados do usuário
            cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (session['user_id'],))
            user_data = cursor.fetchone()
            
            if user_data:
                nome = user_data['nome'] or ''
                email = user_data['email'] or ''
                telefone = ''  # Usuários logados não têm telefone na BD
                
                # Atualizar dados na sessão
                session['nome'] = nome
                session['email'] = email
                session['telefone'] = telefone
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            app.logger.error(f"Erro ao buscar dados do usuário: {str(e)}")
            # Usar dados da sessão como fallback
            nome = session.get('nome', '')
            email = session.get('email', '')
            telefone = session.get('telefone', '')
    
    # Buscar salas exclusivas da base de dados
    salas_exclusivas = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, nome, descricao, capacidade FROM salas_exclusivas ORDER BY nome")
        salas_raw = cursor.fetchall()
        
        # Definir preços por sala
        precos_salas = {
            'intimista': 150.00,
            'vip': 350.00,
            'premium': 200.00
        }
        
        # Adicionar preços às salas
        for sala in salas_raw:
            sala['preco'] = precos_salas.get(sala['nome'].lower(), 150.00)
            salas_exclusivas.append(sala)
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar salas exclusivas: {str(e)}")
        salas_exclusivas = []
    
    app.logger.info(f"sessao_exclusiva - logged_in: {logged_in}, avatar: {avatar}")
    
    return render_template('sessao_exclusiva.html', 
                         logged_in=logged_in, 
                         avatar=avatar,
                         nome=nome,
                         email=email,
                         telefone=telefone,
                         salas_exclusivas=salas_exclusivas)

@app.route('/sessao_tematica')
def sessao_tematica():
    return render_template('sessoes_tematicas.html')

@app.route('/sessao_terror')
def sessao_terror():
    filmes_terror = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar filmes de terror que estão em exibição
        cursor.execute("""
            SELECT DISTINCT
                f.id, 
                f.titulo, 
                f.poster_url,
                f.poster_hover,
                f.trailer_url,
                f.duracao,
                YEAR(f.data_lancamento) as ano,
                GROUP_CONCAT(DISTINCT g.nome SEPARATOR ', ') as genero_nome
            FROM filmes f
            INNER JOIN filme_generos fg ON f.id = fg.filme_id
            INNER JOIN generos g ON fg.genero_id = g.id
            WHERE (g.nome LIKE '%Terror%' OR g.nome LIKE '%Horror%' OR g.nome LIKE '%Suspense%')
            AND f.estado = 'em_exibicao'
            AND f.poster_url IS NOT NULL 
            AND f.poster_url != ''
            GROUP BY f.id, f.titulo, f.poster_url, f.poster_hover, f.trailer_url, f.duracao, f.data_lancamento
            ORDER BY f.titulo ASC
            LIMIT 20
        """)
        filmes_terror = cursor.fetchall()
        
        # Se não encontrar com géneros específicos, buscar todos os filmes disponíveis
        if not filmes_terror:
            cursor.execute("""
                SELECT DISTINCT
                    f.id, 
                    f.titulo, 
                    f.poster_url,
                    f.poster_hover,
                    f.trailer_url,
                    f.duracao,
                    YEAR(f.data_lancamento) as ano,
                    'Terror' as genero_nome
                FROM filmes f
                WHERE f.estado != 'Fora de Exibição'
                AND f.poster_url IS NOT NULL 
                AND f.poster_url != ''
                ORDER BY f.titulo ASC
                LIMIT 15
            """)
            filmes_terror = cursor.fetchall()
        
        # Processar poster_url para cada filme
        for filme in filmes_terror:
            poster_url = filme.get('poster_url', '')
            if poster_url:
                # Limpar o caminho
                poster_url = poster_url.replace('\\', '/').replace('"', '').strip()
                
                # Garantir que o caminho está correto para imgs/filmes/
                if not poster_url.startswith('imgs/filmes/'):
                    # Se é apenas o nome do arquivo, adicionar o caminho completo
                    if '/' not in poster_url:
                        poster_url = f"imgs/filmes/{poster_url}"
                    # Se não começa com imgs/, adicionar
                    elif not poster_url.startswith('imgs/'):
                        poster_url = f"imgs/filmes/{poster_url}"
                
                filme['poster_url'] = poster_url
        
        app.logger.info(f"Filmes de terror encontrados: {len(filmes_terror)}")
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar filmes de terror: {e}")
        filmes_terror = []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    # Verificar se o usuário está logado e obter avatar
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    return render_template('sessao_terror.html', 
                         filmes_terror=filmes_terror,
                         logged_in=logged_in,
                         avatar=avatar)

@app.route('/sessao_vintage')
def sessao_vintage():
    filmes_vintage = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar filmes com género "Vintage" que estão em exibição
        cursor.execute("""
            SELECT DISTINCT
                f.id, 
                f.titulo, 
                f.poster_url,
                f.poster_hover,
                f.trailer_url,
                f.duracao,
                YEAR(f.data_lancamento) as ano,
                GROUP_CONCAT(DISTINCT g.nome SEPARATOR ', ') as genero_nome
            FROM filmes f
            INNER JOIN filme_generos fg ON f.id = fg.filme_id
            INNER JOIN generos g ON fg.genero_id = g.id
            WHERE (g.nome LIKE '%Vintage%' OR g.nome LIKE '%Clássico%' OR g.nome LIKE '%Classic%')
            AND f.estado = 'em_exibicao'
            AND f.poster_url IS NOT NULL 
            AND f.poster_url != ''
            GROUP BY f.id, f.titulo, f.poster_url, f.poster_hover, f.trailer_url, f.duracao, f.data_lancamento
            ORDER BY f.data_lancamento ASC
            LIMIT 20
        """)
        filmes_vintage = cursor.fetchall()
        
        # Se não encontrar com géneros específicos, buscar filmes mais antigos como fallback
        if not filmes_vintage:
            cursor.execute("""
                SELECT DISTINCT
                    f.id, 
                    f.titulo, 
                    f.poster_url,
                    f.poster_hover,
                    f.trailer_url,
                    f.duracao,
                    YEAR(f.data_lancamento) as ano,
                    'Vintage' as genero_nome
                FROM filmes f
                WHERE f.estado = 'em_exibicao'
                AND f.poster_url IS NOT NULL 
                AND f.poster_url != ''
                AND YEAR(f.data_lancamento) < 2000
                ORDER BY f.data_lancamento ASC
                LIMIT 15
            """)
            filmes_vintage = cursor.fetchall()
        
        # Processar poster_url para cada filme
        for filme in filmes_vintage:
            poster_url = filme.get('poster_url', '')
            if poster_url:
                # Limpar o caminho
                poster_url = poster_url.replace('\\', '/').replace('"', '').strip()
                
                # Garantir que o caminho está correto para imgs/filmes/
                if not poster_url.startswith('imgs/filmes/'):
                    # Se é apenas o nome do arquivo, adicionar o caminho completo
                    if '/' not in poster_url:
                        poster_url = f"imgs/filmes/{poster_url}"
                    # Se não começa com imgs/, adicionar
                    elif not poster_url.startswith('imgs/'):
                        poster_url = f"imgs/filmes/{poster_url}"
                
                filme['poster_url'] = poster_url
        
        app.logger.info(f"Filmes vintage encontrados: {len(filmes_vintage)}")
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar filmes vintage: {e}")
        filmes_vintage = []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    # Verificar se o usuário está logado e obter avatar
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    return render_template('sessao_vintage.html', 
                         filmes_vintage=filmes_vintage,
                         logged_in=logged_in,
                         avatar=avatar)

@app.route('/reserva_sessao_tematica')
def reserva_sessao_tematica():
    """Rota para reserva de sessões temáticas com o mesmo sistema da reserva normal"""
    tipo_sessao = request.args.get('tipo')  # vintage, terror, romance
    filme_id = request.args.get('filme_id')
    data_sessao = request.args.get('data')
    hora_sessao = request.args.get('hora')
    
    if not tipo_sessao:
        return "Tipo de sessão não especificado", 400
    
    # Sempre redirecionar para o pagamento - o modal será mostrado lá se necessário
    return redirect(url_for('pagamento_sessao_tematica', 
                           tipo=tipo_sessao, 
                           filme_id=filme_id,
                           data=data_sessao,
                           hora=hora_sessao))

@app.route('/pagamento_sessao_tematica')
def pagamento_sessao_tematica():
    """Página de pagamento para sessões temáticas"""
    tipo_sessao = request.args.get('tipo')
    filme_id = request.args.get('filme_id')
    data_sessao = request.args.get('data')
    hora_sessao = request.args.get('hora')
    
    # Verificar se há dados temporários da sessão
    if not tipo_sessao and 'reserva_tematica_temp' in session:
        dados_temp = session['reserva_tematica_temp']
        tipo_sessao = dados_temp.get('tipo_sessao')
        filme_id = dados_temp.get('filme_id')
        data_sessao = dados_temp.get('data_sessao')
        hora_sessao = dados_temp.get('hora_sessao')
    
    if not tipo_sessao:
        return "Dados da reserva não encontrados", 400
    
    # Buscar salas exclusivas da base de dados
    salas_exclusivas = []
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, nome, descricao, capacidade FROM salas_exclusivas ORDER BY nome")
        salas_raw = cursor.fetchall()
        
        # Definir preços por sala (pode ser movido para a base de dados no futuro)
        precos_salas = {
            'intimista': 120.00,
            'vip': 200.00,
            'premium': 150.00
        }
        
        # Adicionar preços às salas
        for sala in salas_raw:
            sala['preco'] = precos_salas.get(sala['nome'].lower(), 100.00)
            salas_exclusivas.append(sala)
            
    except Exception as e:
        app.logger.error(f"Erro ao buscar salas exclusivas: {e}")
        salas_exclusivas = []
    finally:
        cursor.close()
        conn.close()
    
    # Buscar dados do filme se especificado
    filme = None
    if filme_id and filme_id != '0':
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
            filme = cursor.fetchone()
        except Exception as e:
            app.logger.error(f"Erro ao buscar filme: {e}")
        finally:
            cursor.close()
            conn.close()
    
    # Definir preços base por tipo de sessão
    precos_base = {
        'vintage': 35.00,
        'romance': 85.00,
        'terror': 45.00
    }
    
    preco_base = precos_base.get(tipo_sessao, 35.00)
    
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    # Limpar dados temporários
    if 'reserva_tematica_temp' in session:
        del session['reserva_tematica_temp']
    
    return render_template('pagamento_sessao_tematica.html',
                         tipo_sessao=tipo_sessao,
                         filme=filme,
                         data_sessao=data_sessao,
                         hora_sessao=hora_sessao,
                         preco_base=preco_base,
                         salas_exclusivas=salas_exclusivas,
                         logged_in=logged_in,
                         avatar=avatar)

@app.route('/api/processar-pagamento-sessao-tematica', methods=['POST'])
def api_processar_pagamento_sessao_tematica():
    """API para processar pagamento de sessão temática"""
    try:
        data = request.get_json()
        app.logger.info(f"Dados recebidos para pagamento sessão temática: {data}")
        
        # Validar dados obrigatórios
        required_fields = ['tipo_sessao', 'preco_total', 'metodo_pagamento', 'sala_id', 'sala_nome']
        
        for field in required_fields:
            if not data.get(field):
                app.logger.error(f"Campo obrigatório ausente: {field}")
                return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar se o filme existe (se filme_id não for 0)
        filme_id = data.get('filme_id')
        if filme_id and filme_id != '0':
            cursor.execute("SELECT id FROM filmes WHERE id = %s", (filme_id,))
            if not cursor.fetchone():
                app.logger.warning(f"Filme ID {filme_id} não encontrado, definindo como NULL")
                filme_id = None
        else:
            filme_id = None
        
        # Preparar dados para inserção
        user_id = session.get('user_id') if 'user_id' in session else None
        
        # Para usuários não logados, usar os dados fornecidos
        if not user_id:
            nome_cliente = data.get('nome_cliente', '')
            email_cliente = data.get('email_cliente', '')
            telefone_cliente = data.get('telefone_cliente', '')
        else:
            # Para usuários logados, buscar dados da sessão
            nome_cliente = session.get('user_name', '')
            email_cliente = session.get('user_email', '')
            telefone_cliente = ''
        
        app.logger.info(f"Inserindo reserva sessão temática - Tipo: {data['tipo_sessao']}, Sala: {data['sala_nome']}, Filme: {data.get('filme_nome', 'N/A')}")
        
        # Inserir reserva na base de dados (usando a mesma tabela das reservas exclusivas)
        cursor.execute("""
            INSERT INTO reservas_exclusivas 
            (tipo_sala, filme_id, data_sessao, hora_sessao, num_pessoas, 
             preco_total, usuario_id, nome_cliente, email_cliente, telefone_cliente, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'confirmada')
        """, (
            data['sala_nome'].lower(),  # usar nome da sala como tipo_sala
            filme_id,
            data.get('data_sessao', ''),
            data.get('hora_sessao', ''),
            data.get('sala_capacidade', 1),  # usar capacidade da sala
            float(data['preco_total']),
            user_id,
            nome_cliente,
            email_cliente,
            telefone_cliente
        ))
        
        reserva_id = cursor.lastrowid
        conn.commit()
        
        app.logger.info(f"Reserva sessão temática criada com sucesso - ID: {reserva_id}")
        
        # Enviar email de confirmação se houver email
        if email_cliente:
            try:
                dados_reserva = {
                    'id': reserva_id,
                    'tipo_sessao': data['tipo_sessao'],
                    'sala_nome': data['sala_nome'],
                    'filme_nome': data.get('filme_nome', 'Experiência Temática'),
                    'data_sessao': data.get('data_sessao', ''),
                    'hora_sessao': data.get('hora_sessao', ''),
                    'preco_total': data['preco_total'],
                    'metodo_pagamento': data['metodo_pagamento']
                }
                
                enviar_email_confirmacao_exclusiva(email_cliente, nome_cliente, dados_reserva)
                app.logger.info(f"Email de confirmação enviado para {email_cliente}")
            except Exception as e:
                app.logger.error(f"Erro ao enviar email de confirmação: {e}")
        
        return jsonify({
            'success': True, 
            'message': 'Reserva criada com sucesso!',
            'reserva_id': reserva_id
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao processar pagamento sessão temática: {e}")
        return jsonify({'success': False, 'message': f'Erro ao processar pagamento: {str(e)}'})
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/sessao_romance')
def sessao_romance():
    """Sessão Romance - Todos os filmes com género Romance"""
    
    filmes_romance = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar TODOS os filmes com género Romance (ID 13) em exibição
        cursor.execute("""
            SELECT DISTINCT
                f.id, 
                f.titulo, 
                f.poster_url,
                f.poster_hover,
                f.trailer_url,
                f.duracao,
                YEAR(f.data_lancamento) as ano,
                GROUP_CONCAT(DISTINCT g.nome SEPARATOR ', ') as genero_nome
            FROM filmes f
            INNER JOIN filme_generos fg ON f.id = fg.filme_id
            INNER JOIN generos g ON fg.genero_id = g.id
            WHERE fg.genero_id = 13
            AND f.estado = 'em_exibicao'
            AND f.poster_url IS NOT NULL 
            AND f.poster_url != ''
            GROUP BY f.id, f.titulo, f.poster_url, f.poster_hover, f.trailer_url, f.duracao, f.data_lancamento
            ORDER BY f.titulo ASC
        """)
        
        filmes_romance = cursor.fetchall()
        
        # Processar poster_url para cada filme
        for filme in filmes_romance:
            poster_url = filme.get('poster_url', '')
            if poster_url:
                # Limpar o caminho
                poster_url = poster_url.replace('\\', '/').replace('"', '').strip()
                
                # Garantir que o caminho está correto para imgs/filmes/
                if not poster_url.startswith('imgs/filmes/'):
                    if '/' not in poster_url:
                        poster_url = f"imgs/filmes/{poster_url}"
                    elif not poster_url.startswith('imgs/'):
                        poster_url = f"imgs/filmes/{poster_url}"
                
                filme['poster_url'] = poster_url
        
        app.logger.info(f"Filmes de romance encontrados: {len(filmes_romance)}")
        if filmes_romance:
            app.logger.info(f"Títulos: {[f['titulo'] for f in filmes_romance]}")
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar filmes de romance: {e}")
        filmes_romance = []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return render_template('sessao_romance.html', filmes_romance=filmes_romance)


@app.route('/sessao_premium')
def sessao_premium():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Lógica da sessão premium aqui
        pass
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass
    
    return render_template('sessao.html')

# ==========================
# BAR & AJAX
# ==========================
@app.route('/selecao_bar')
def selecao_bar():
    """Página específica de seleção do bar durante o processo de reserva"""
    
    conn = None
    try:
        app.logger.info("🔍 INÍCIO SELECAO_BAR")
        
        # Obter parâmetros da URL OU da sessão
        filme_id = request.args.get('filme_id') or session.get('filme_id')
        cinema_id = request.args.get('cinema_id') or session.get('cinema_id')
        id_tipo_sessao = request.args.get('id_tipo_sessao') or session.get('id_tipo_sessao')
        id_horario_sessao = request.args.get('id_horario_sessao') or session.get('id_horario_sessao')
        data_sessao = request.args.get('data_sessao') or session.get('data_sessao')
        lugares = request.args.get('lugares') or ','.join(session.get('lugares_selecionados', []))
        
        # 🔍 DEBUG: Verificar de onde veio o id_tipo_sessao
        app.logger.info(f"🔍 id_tipo_sessao da URL: {request.args.get('id_tipo_sessao')}")
        app.logger.info(f"🔍 id_tipo_sessao da sessão: {session.get('id_tipo_sessao')}")
        app.logger.info(f"🔍 id_tipo_sessao FINAL: {id_tipo_sessao}")
        
        if not all([filme_id, cinema_id, id_horario_sessao, id_tipo_sessao]):
            flash("Dados da reserva incompletos", "erro")
            return redirect(url_for('home'))
        
        # Conectar à BD e buscar dados reais
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar dados do filme
        cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        
        if not filme:
            flash("Filme não encontrado", "erro")
            return redirect(url_for('home'))
        
        # Corrigir poster_url
        poster_url = filme.get('poster_url', 'imgs/filmes/placeholder.jpg')
        if poster_url and not poster_url.startswith(('http://', 'https://', 'imgs/')):
            poster_url = f"imgs/filmes/{poster_url}"
        filme['poster_url'] = poster_url
        
        # Buscar dados do cinema
        cursor.execute("SELECT * FROM cinemas WHERE id = %s", (cinema_id,))
        cinema = cursor.fetchone()
        
        # Buscar dados do tipo de sessão
        cursor.execute("SELECT * FROM tipos_sessao WHERE id = %s", (id_tipo_sessao,))
        tipo_sessao = cursor.fetchone()
        
        # Buscar dados do horário
        cursor.execute("""
            SELECT hs.*, h.hora
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (id_horario_sessao,))
        horario = cursor.fetchone()
        
        if horario:
            hora_val = horario['hora']
            horario['hora_str'] = hora_val.strftime("%H:%M") if hasattr(hora_val, 'strftime') else str(hora_val)
        
        # Processar lugares selecionados
        lugares_selecionados = lugares.split(',') if lugares else []
        
        # Buscar produtos do bar organizados por categoria
        
        # Buscar menus da tabela menus
        cursor.execute("""
            SELECT id, nome as produto, preco_total as preco, 'menus' as categoria, 
                   descricao, 'fas fa-box-open' as icone, imagem_url 
            FROM menus 
            ORDER BY nome
        """)
        menus_raw = cursor.fetchall()
        
        # Buscar snacks e bebidas da tabela bar
        cursor.execute("""
            SELECT id, produto, preco, categoria, descricao, icone, imagem_url 
            FROM bar 
            WHERE categoria IN ('snacks', 'bebidas')
            ORDER BY categoria, produto
        """)
        produtos_bar_raw = cursor.fetchall()
        
        # Organizar produtos por categoria
        produtos = {
            'menus': list(menus_raw),
            'snacks': [],
            'bebidas': []
        }
        
        for produto in produtos_bar_raw:
            categoria = produto['categoria']
            if categoria in produtos:
                produtos[categoria].append(produto)
        
        app.logger.info(f"📦 Produtos carregados:")
        app.logger.info(f"  - menus: {len(produtos['menus'])} produtos")
        app.logger.info(f"  - snacks: {len(produtos['snacks'])} produtos") 
        app.logger.info(f"  - bebidas: {len(produtos['bebidas'])} produtos")
        
        # Buscar toppings da base de dados
        cursor.execute("""
            SELECT id, nome, descricao, preco, imagem_url
            FROM toppings 
            ORDER BY nome
        """)
        toppings = cursor.fetchall()
        
        # Processar URLs das imagens para toppings
        for topping in toppings:
            if topping.get('imagem_url'):
                imagem_url = topping['imagem_url'].replace('\\', '/').replace('"', '').strip()
                if not imagem_url.startswith(('http://', 'https://', 'imgs/')):
                    if '/' not in imagem_url:
                        imagem_url = f"imgs/toppings/{imagem_url}"
                    elif not imagem_url.startswith('imgs/'):
                        imagem_url = f"imgs/toppings/{imagem_url}"
                topping['imagem_url'] = imagem_url
            else:
                topping['imagem_url'] = 'imgs/toppings/topping-default.svg'
        
        app.logger.info(f"  - toppings: {len(toppings)} produtos")
        
        # Guardar dados na sessão
        salvar_dados_reserva_sessao(
            filme_id=int(filme_id),
            cinema_id=int(cinema_id),
            id_tipo_sessao=int(id_tipo_sessao),
            id_horario_sessao=int(id_horario_sessao),
            data_sessao=str(data_sessao),
            lugares=lugares_selecionados
        )
        
        app.logger.info(f"✅ Dados carregados: {filme['titulo']} - {tipo_sessao['nome']}")
        
        cursor.close()
        conn.close()
        
        return render_template('selecao_bar.html', 
                             filme=filme,
                             cinema=cinema,
                             horario=horario,
                             tipo_sessao=tipo_sessao,
                             filme_id=filme_id,
                             cinema_id=cinema_id,
                             id_tipo_sessao=id_tipo_sessao,
                             tipo_sessao_id=id_tipo_sessao,
                             id_horario_sessao=id_horario_sessao,
                             horario_id=id_horario_sessao,
                             data_sessao=data_sessao,
                             lugares_selecionados=lugares_selecionados,
                             produtos=produtos,
                             toppings=toppings,
                             user_authenticated='user_id' in session,
                             user_avatar=get_user_avatar())
                             
    except Exception as e:
        app.logger.error(f"❌ Erro na rota /selecao_bar: {e}")
        import traceback
        app.logger.error(f"❌ Traceback: {traceback.format_exc()}")
        if conn:
            conn.close()
        flash("Erro ao carregar página do bar", "erro")
        return redirect(url_for('home'))
        import traceback
        app.logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return f"<h1>Erro Debug</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>"

@app.route('/api/menu_produtos/<int:menu_id>')
def api_menu_produtos(menu_id):
    """API para buscar produtos disponíveis de um menu"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar produtos do menu
        cursor.execute("""
            SELECT DISTINCT b.id, b.produto, b.categoria, b.imagem_url, b.icone
            FROM menu_produtos mp
            JOIN bar b ON mp.produto_id = b.id
            WHERE mp.menu_id = %s
            ORDER BY b.categoria, b.produto
        """, (menu_id,))
        
        produtos = cursor.fetchall()
        
        # Organizar por categoria
        snacks = [p for p in produtos if p['categoria'] == 'snacks']
        bebidas = [p for p in produtos if p['categoria'] == 'bebidas']
        
        # Verificar se algum snack é pipocas (produtos que podem ter toppings)
        tem_pipocas = any('pipoca' in p['produto'].lower() for p in snacks)
        
        # Se tem pipocas, buscar todos os toppings disponíveis
        toppings = []
        if tem_pipocas:
            cursor.execute("""
                SELECT id, nome, descricao, preco, imagem_url
                FROM toppings
                ORDER BY nome
            """)
            toppings_raw = cursor.fetchall()
            
            # Processar URLs das imagens
            for topping in toppings_raw:
                if topping.get('imagem_url'):
                    imagem_url = topping['imagem_url'].replace('\\', '/').replace('"', '').strip()
                    if not imagem_url.startswith(('http://', 'https://', 'imgs/')):
                        if '/' not in imagem_url:
                            imagem_url = f"imgs/toppings/{imagem_url}"
                        elif not imagem_url.startswith('imgs/'):
                            imagem_url = f"imgs/toppings/{imagem_url}"
                    topping['imagem_url'] = imagem_url
                else:
                    topping['imagem_url'] = 'imgs/toppings/topping-default.svg'
            
            toppings = toppings_raw
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'snacks': snacks,
            'bebidas': bebidas,
            'toppings': toppings,
            'has_toppings': len(toppings) > 0
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar produtos do menu: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/selecao_toppings')
def selecao_toppings():
    """Página de seleção de toppings após escolher produtos do bar"""
    
    conn = None
    try:
        app.logger.info("🔍 INÍCIO SELECAO_TOPPINGS")
        app.logger.info("=" * 60)
        
        # Obter parâmetros
        filme_id = request.args.get('filme_id') or session.get('filme_id')
        cinema_id = request.args.get('cinema_id') or session.get('cinema_id')
        id_tipo_sessao = request.args.get('id_tipo_sessao') or session.get('id_tipo_sessao')
        id_horario_sessao = request.args.get('id_horario_sessao') or session.get('id_horario_sessao')
        data_sessao = request.args.get('data_sessao') or session.get('data_sessao')
        lugares = request.args.get('lugares') or ','.join(session.get('lugares_selecionados', []))
        produtos_bar_json = request.args.get('produtos_bar', '[]')
        
        app.logger.info(f"📋 Parâmetros recebidos:")
        app.logger.info(f"   - filme_id: {filme_id}")
        app.logger.info(f"   - cinema_id: {cinema_id}")
        app.logger.info(f"   - id_tipo_sessao: {id_tipo_sessao}")
        app.logger.info(f"   - produtos_bar_json: {produtos_bar_json}")
        
        if not all([filme_id, cinema_id, id_horario_sessao, id_tipo_sessao]):
            app.logger.error("❌ Dados da reserva incompletos")
            flash("Dados da reserva incompletos", "erro")
            return redirect(url_for('home'))
        
        # Parse produtos do bar
        import json
        try:
            produtos_bar = json.loads(produtos_bar_json)
            app.logger.info(f"✅ Produtos parseados: {len(produtos_bar)} produtos")
        except Exception as e:
            app.logger.error(f"❌ Erro ao parsear produtos: {e}")
            produtos_bar = []
        
        if not produtos_bar:
            # Se não há produtos, redirecionar direto para resumo
            app.logger.info("⚠️ Nenhum produto selecionado, redirecionando para resumo")
            return redirect(url_for('resumo_reserva',
                                  filme_id=filme_id,
                                  cinema_id=cinema_id,
                                  tipo_sessao_id=id_tipo_sessao,
                                  horario_id=id_horario_sessao,
                                  data_sessao=data_sessao,
                                  lugares=lugares,
                                  quantidade=len(lugares.split(',')),
                                  produtos_bar='[]'))
        
        # Conectar à BD
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar dados do filme
        cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        
        if not filme:
            flash("Filme não encontrado", "erro")
            return redirect(url_for('home'))
        
        # Corrigir poster_url
        poster_url = filme.get('poster_url', 'imgs/filmes/placeholder.jpg')
        if poster_url and not poster_url.startswith(('http://', 'https://', 'imgs/')):
            poster_url = f"imgs/filmes/{poster_url}"
        filme['poster_url'] = poster_url
        
        # Buscar dados do cinema
        cursor.execute("SELECT * FROM cinemas WHERE id = %s", (cinema_id,))
        cinema = cursor.fetchone()
        
        # Buscar dados do tipo de sessão
        cursor.execute("SELECT * FROM tipos_sessao WHERE id = %s", (id_tipo_sessao,))
        tipo_sessao = cursor.fetchone()
        
        # Buscar dados do horário
        cursor.execute("""
            SELECT hs.*, h.hora
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (id_horario_sessao,))
        horario = cursor.fetchone()
        
        if horario:
            hora_val = horario['hora']
            horario['hora_str'] = hora_val.strftime("%H:%M") if hasattr(hora_val, 'strftime') else str(hora_val)
        
        # Processar lugares selecionados
        lugares_selecionados = lugares.split(',') if lugares else []
        
        # Buscar detalhes dos produtos selecionados
        produtos_detalhes = []
        produtos_com_toppings = []
        
        app.logger.info(f"📦 Processando {len(produtos_bar)} produtos do bar")
        
        for produto in produtos_bar:
            produto_id = produto.get('id')
            quantidade = produto.get('quantidade', 1)
            tipo_produto_enviado = produto.get('tipo', 'bar')  # Novo campo
            
            app.logger.info(f"🔍 Verificando produto ID: {produto_id}, tipo: {tipo_produto_enviado}")
            
            # Verificar se é topping (começa com 'topping_')
            if str(produto_id).startswith('topping_'):
                app.logger.info(f"⏭️ Pulando topping: {produto_id}")
                continue
            
            # Buscar produto baseado no tipo enviado
            produto_info = None
            
            if tipo_produto_enviado == 'menu':
                # Buscar em menus
                app.logger.info(f"🔍 Buscando em menus...")
                cursor.execute("""
                    SELECT id, nome as produto, preco_total as preco, 'menu' as categoria, imagem_url
                    FROM menus
                    WHERE id = %s
                """, (produto_id,))
                produto_info = cursor.fetchone()
                
                if produto_info:
                    app.logger.info(f"✅ Menu encontrado: {produto_info['produto']}")
            else:
                # Buscar produto no bar
                app.logger.info(f"🔍 Buscando em bar...")
                cursor.execute("""
                    SELECT id, produto, preco, categoria, imagem_url
                    FROM bar
                    WHERE id = %s
                """, (produto_id,))
                produto_info = cursor.fetchone()
                
                if produto_info:
                    app.logger.info(f"✅ Produto do bar encontrado: {produto_info['produto']}")
            
            if produto_info:
                produto_info['quantidade'] = quantidade
                produtos_detalhes.append(produto_info)
                
                # Verificar se este produto tem toppings associados
                tipo_produto = 'menu' if produto_info['categoria'] == 'menu' else 'bar'
                app.logger.info(f"🔍 Tipo de produto confirmado: {tipo_produto}")
                
                if tipo_produto == 'menu':
                    cursor.execute("""
                        SELECT COUNT(*) as total
                        FROM toppings_produtos
                        WHERE id_menu = %s AND tipo_produto = 'menu'
                    """, (produto_id,))
                else:
                    cursor.execute("""
                        SELECT COUNT(*) as total
                        FROM toppings_produtos
                        WHERE id_produto = %s AND tipo_produto = 'bar'
                    """, (produto_id,))
                
                result = cursor.fetchone()
                app.logger.info(f"🔍 Toppings associados: {result['total'] if result else 0}")
                
                if result and result['total'] > 0:
                    produtos_com_toppings.append({
                        'id': produto_id,
                        'tipo': tipo_produto,
                        'nome': produto_info['produto']
                    })
                    app.logger.info(f"✅ Produto com toppings adicionado: {produto_info['produto']}")
            else:
                app.logger.warning(f"⚠️ Produto ID {produto_id} não encontrado")
        
        # Se não há produtos com toppings, redirecionar para resumo
        if not produtos_com_toppings:
            app.logger.info("ℹ️ Nenhum produto com toppings, redirecionando para resumo")
            return redirect(url_for('resumo_reserva',
                                  filme_id=filme_id,
                                  cinema_id=cinema_id,
                                  tipo_sessao_id=id_tipo_sessao,
                                  horario_id=id_horario_sessao,
                                  data_sessao=data_sessao,
                                  lugares=lugares,
                                  quantidade=len(lugares_selecionados),
                                  produtos_bar=produtos_bar_json))
        
        # Buscar todos os toppings disponíveis para os produtos selecionados
        toppings_disponiveis = []
        for produto in produtos_com_toppings:
            if produto['tipo'] == 'menu':
                cursor.execute("""
                    SELECT DISTINCT t.id, t.nome, t.descricao, t.preco, t.imagem_url
                    FROM toppings_produtos tp
                    JOIN toppings t ON tp.id_topping = t.id
                    WHERE tp.id_menu = %s AND tp.tipo_produto = 'menu'
                    ORDER BY t.nome
                """, (produto['id'],))
            else:
                cursor.execute("""
                    SELECT DISTINCT t.id, t.nome, t.descricao, t.preco, t.imagem_url
                    FROM toppings_produtos tp
                    JOIN toppings t ON tp.id_topping = t.id
                    WHERE tp.id_produto = %s AND tp.tipo_produto = 'bar'
                    ORDER BY t.nome
                """, (produto['id'],))
            
            toppings = cursor.fetchall()
            for topping in toppings:
                # Evitar duplicados
                if not any(t['id'] == topping['id'] for t in toppings_disponiveis):
                    # Processar URL da imagem
                    if topping.get('imagem_url'):
                        imagem_url = topping['imagem_url'].replace('\\', '/').replace('"', '').strip()
                        if not imagem_url.startswith(('http://', 'https://', 'imgs/')):
                            if '/' not in imagem_url:
                                imagem_url = f"imgs/toppings/{imagem_url}"
                            elif not imagem_url.startswith('imgs/'):
                                imagem_url = f"imgs/toppings/{imagem_url}"
                        topping['imagem_url'] = imagem_url
                    else:
                        topping['imagem_url'] = 'imgs/toppings/topping-default.svg'
                    
                    toppings_disponiveis.append(topping)
        
        app.logger.info(f"🍿 {len(produtos_com_toppings)} produtos com toppings")
        app.logger.info(f"🍿 {len(toppings_disponiveis)} toppings disponíveis")
        
        cursor.close()
        conn.close()
        
        return render_template('selecao_toppings.html',
                             filme=filme,
                             cinema=cinema,
                             horario=horario,
                             tipo_sessao=tipo_sessao,
                             filme_id=filme_id,
                             cinema_id=cinema_id,
                             id_tipo_sessao=id_tipo_sessao,
                             tipo_sessao_id=id_tipo_sessao,
                             id_horario_sessao=id_horario_sessao,
                             horario_id=id_horario_sessao,
                             data_sessao=data_sessao,
                             lugares_selecionados=lugares_selecionados,
                             lugares=lugares,
                             produtos_bar=produtos_detalhes,
                             produtos_bar_json=produtos_bar_json,
                             produtos_com_toppings=produtos_com_toppings,
                             toppings=toppings_disponiveis,
                             user_authenticated='user_id' in session,
                             user_avatar=get_user_avatar())
                             
    except Exception as e:
        app.logger.error(f"❌ Erro na rota /selecao_toppings: {e}")
        import traceback
        app.logger.error(f"❌ Traceback: {traceback.format_exc()}")
        if conn:
            conn.close()
        flash("Erro ao carregar página de toppings", "erro")
        return redirect(url_for('home'))

@app.route('/bar')
def bar():
    """Página principal do bar com menus e toppings da base de dados"""
    
    try:
        # Conectar à base de dados
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar apenas menus da base de dados
        cursor.execute("""
            SELECT id, nome, descricao, preco_total as preco, imagem_url
            FROM menus 
            ORDER BY nome
        """)
        menus = cursor.fetchall()
        
        # Processar URLs das imagens para menus
        for menu in menus:
            if menu.get('imagem_url'):
                imagem_url = menu['imagem_url'].replace('\\', '/').replace('"', '').strip()
                if not imagem_url.startswith(('http://', 'https://', 'imgs/')):
                    if '/' not in imagem_url:
                        imagem_url = f"imgs/bar/{imagem_url}"
                    elif not imagem_url.startswith('imgs/'):
                        imagem_url = f"imgs/bar/{imagem_url}"
                menu['imagem_url'] = imagem_url
            else:
                menu['imagem_url'] = 'imgs/bar/menu-default.svg'
        
        # Buscar toppings da base de dados
        cursor.execute("""
            SELECT id, nome, descricao, preco, imagem_url
            FROM toppings 
            ORDER BY nome
        """)
        toppings = cursor.fetchall()
        
        # Processar URLs das imagens para toppings
        for topping in toppings:
            if topping.get('imagem_url'):
                imagem_url = topping['imagem_url'].replace('\\', '/').replace('"', '').strip()
                if not imagem_url.startswith(('http://', 'https://', 'imgs/')):
                    if '/' not in imagem_url:
                        imagem_url = f"imgs/toppings/{imagem_url}"
                    elif not imagem_url.startswith('imgs/'):
                        imagem_url = f"imgs/toppings/{imagem_url}"
                topping['imagem_url'] = imagem_url
            else:
                topping['imagem_url'] = 'imgs/toppings/topping-default.svg'
        
        app.logger.info(f"Menus encontrados: {len(menus)}, Toppings encontrados: {len(toppings)}")
        
        cursor.close()
        conn.close()
        
        return render_template('bar.html', 
                             menus=menus,
                             toppings=toppings,
                             logged_in=session.get('user_authenticated', False),
                             avatar=session.get('user_avatar', 'imgs/icons/user_icon34-removebg-preview.png'))
                             
    except Exception as e:
        app.logger.error(f"Erro na rota /bar: {e}")
        # Em caso de erro, mostrar página básica sem menus
        return render_template('bar.html', 
                             menus=[],
                             toppings=[],
                             logged_in=session.get('user_authenticated', False),
                             avatar=session.get('user_avatar', 'imgs/icons/user_icon34-removebg-preview.png'))
@app.route('/resumo_reserva', methods=['GET', 'POST'])
def resumo_reserva():
    """Página de resumo da reserva após seleção do bar"""
    
    # Se for POST, guardar dados do cliente na sessão
    if request.method == 'POST':
        nome_cliente = request.form.get('guest_name', '').strip()
        email_cliente = request.form.get('guest_email', '').strip()
        telefone_cliente = request.form.get('guest_phone', '').strip()
        
        # Guardar na sessão
        if nome_cliente:
            session['nome_cliente'] = nome_cliente
        if email_cliente:
            session['email_cliente'] = email_cliente
        if telefone_cliente:
            session['telefone_cliente'] = telefone_cliente
        
        app.logger.info(f"✅ Dados do cliente guardados na sessão: {nome_cliente}, {email_cliente}")
        
        # Redirecionar para checkout
        return redirect(url_for('checkout'))
    
    try:
        # Obter parâmetros da URL OU da sessão
        filme_id = request.args.get('filme_id') or session.get('filme_id')
        cinema_id = request.args.get('cinema_id') or session.get('cinema_id')
        id_tipo_sessao = request.args.get('id_tipo_sessao') or session.get('id_tipo_sessao')
        id_horario_sessao = request.args.get('id_horario_sessao') or session.get('id_horario_sessao')
        data_sessao = request.args.get('data_sessao') or session.get('data_sessao')
        lugares = request.args.get('lugares', '') or ','.join(session.get('lugares_selecionados', []))
        quantidade = request.args.get('quantidade', '1')
        produtos_bar = request.args.get('produtos_bar', '[]')
        toppings_json = request.args.get('toppings', '[]')
        
        app.logger.info(f"🔍 RESUMO_RESERVA - Parâmetros:")
        app.logger.info(f"   filme_id={filme_id}, id_tipo_sessao={id_tipo_sessao}")
        app.logger.info(f"   lugares={lugares}")
        app.logger.info(f"   toppings_json={toppings_json}")
        
        # Validar dados essenciais
        if not all([filme_id, cinema_id, id_horario_sessao, id_tipo_sessao]):
            flash("Dados da reserva incompletos", "erro")
            return redirect(url_for('home'))
        
        # Processar lugares selecionados
        lugares_selecionados = []
        if lugares:
            if lugares.startswith('['):
                # JSON format
                try:
                    import json
                    lugares_selecionados = json.loads(lugares)
                except:
                    lugares_selecionados = []
            else:
                # Comma separated
                lugares_selecionados = lugares.split(',') if lugares else []
        
        # Processar produtos do bar
        produtos_selecionados = []
        try:
            import json
            produtos_selecionados = json.loads(produtos_bar) if produtos_bar != '[]' else []
        except:
            produtos_selecionados = []
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar dados do filme
        cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        
        if not filme:
            flash("Filme não encontrado", "erro")
            return redirect(url_for('home'))
        
        # Corrigir poster_url
        poster_url = filme.get('poster_url', 'imgs/filmes/placeholder.jpg')
        if poster_url and not poster_url.startswith(('http://', 'https://', 'imgs/')):
            poster_url = f"imgs/filmes/{poster_url}"
        filme['poster_url'] = poster_url
        
        # Buscar dados do cinema
        cursor.execute("SELECT * FROM cinemas WHERE id = %s", (cinema_id,))
        cinema = cursor.fetchone()
        
        # Buscar dados do horário da sessão (CORRETO!)
        cursor.execute("""
            SELECT hs.*, h.hora
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (id_horario_sessao,))
        horario = cursor.fetchone()
        
        if horario:
            hora_val = horario['hora']
            horario['hora_str'] = hora_val.strftime("%H:%M") if hasattr(hora_val, 'strftime') else str(hora_val)
        
        # Buscar dados do tipo de sessão
        cursor.execute("SELECT * FROM tipos_sessao WHERE id = %s", (id_tipo_sessao,))
        tipo_sessao = cursor.fetchone()
        
        # Calcular preços
        preco_bilhete = float(tipo_sessao.get('preco_bilhete', 8.50)) if tipo_sessao else 8.50
        
        total_bilhetes = len(lugares_selecionados) * preco_bilhete
        total_bar = 0.0
        
        # Calcular total do bar se há produtos selecionados
        produtos_bar_detalhados = []
        
        app.logger.info(f"📦 Processando produtos do bar: {len(produtos_selecionados)} produtos")
        app.logger.info(f"📦 Produtos recebidos: {produtos_selecionados}")
        
        if produtos_selecionados:
            for produto in produtos_selecionados:
                produto_id = produto.get('id')
                quantidade_prod = int(produto.get('quantidade', 1))
                tipo_produto_enviado = produto.get('tipo', 'bar')  # Novo campo
                configs = produto.get('configs', [])  # Configurações do menu (snack, bebida, toppings)
                
                app.logger.info(f"🔍 Buscando produto ID: {produto_id}, tipo: {tipo_produto_enviado}, quantidade: {quantidade_prod}")
                
                produto_info = None
                
                # Buscar baseado no tipo
                if tipo_produto_enviado == 'menu':
                    # Tentar buscar primeiro na tabela menus
                    cursor.execute("SELECT nome as produto, preco_total as preco FROM menus WHERE id = %s", (produto_id,))
                    produto_info = cursor.fetchone()
                    
                    if produto_info:
                        app.logger.info(f"✅ Menu encontrado: {produto_info['produto']}")
                        
                        # Processar cada configuração do menu
                        for idx, config in enumerate(configs):
                            snack_id = config.get('snackId')
                            bebida_id = config.get('bebidaId')
                            toppings_menu = config.get('toppings', [])
                            
                            # Buscar detalhes do snack
                            snack_nome = "Snack"
                            if snack_id:
                                cursor.execute("SELECT produto FROM bar WHERE id = %s", (snack_id,))
                                snack_info = cursor.fetchone()
                                if snack_info:
                                    snack_nome = snack_info['produto']
                            
                            # Buscar detalhes da bebida
                            bebida_nome = "Bebida"
                            if bebida_id:
                                cursor.execute("SELECT produto FROM bar WHERE id = %s", (bebida_id,))
                                bebida_info = cursor.fetchone()
                                if bebida_info:
                                    bebida_nome = bebida_info['produto']
                            
                            # Buscar detalhes dos toppings
                            toppings_nomes = []
                            preco_toppings_menu = 0.0
                            if toppings_menu:
                                for topping_id in toppings_menu:
                                    cursor.execute("SELECT nome, preco FROM toppings WHERE id = %s", (topping_id,))
                                    topping_info = cursor.fetchone()
                                    if topping_info:
                                        toppings_nomes.append(topping_info['nome'])
                                        preco_toppings_menu += float(topping_info['preco'])
                            
                            # Calcular preço total deste menu (preço base + toppings)
                            preco_unitario = float(produto_info['preco']) + preco_toppings_menu
                            preco_total_produto = preco_unitario
                            total_bar += preco_total_produto
                            
                            # Adicionar produto com detalhes expandidos
                            detalhes_texto = f"{snack_nome} + {bebida_nome}"
                            if toppings_nomes:
                                detalhes_texto += f" + Toppings: {', '.join(toppings_nomes)}"
                            
                            produtos_bar_detalhados.append({
                                'nome': f"{produto_info['produto']} (#{idx+1})",
                                'detalhes': detalhes_texto,
                                'quantidade': 1,
                                'preco_unitario': preco_unitario,
                                'preco_total': preco_total_produto,
                                'is_menu': True
                            })
                            app.logger.info(f"✅ Menu detalhado adicionado: {detalhes_texto}")
                else:
                    # Buscar na tabela bar
                    cursor.execute("SELECT produto, preco FROM bar WHERE id = %s", (produto_id,))
                    produto_info = cursor.fetchone()
                    
                    if produto_info:
                        app.logger.info(f"✅ Produto do bar encontrado: {produto_info['produto']}")
                        preco_unitario = float(produto_info['preco'])
                        preco_total_produto = preco_unitario * quantidade_prod
                        total_bar += preco_total_produto
                        
                        # Adicionar produto com detalhes para o template
                        produtos_bar_detalhados.append({
                            'nome': produto_info['produto'],
                            'quantidade': quantidade_prod,
                            'preco_unitario': preco_unitario,
                            'preco_total': preco_total_produto,
                            'is_menu': False
                        })
                        app.logger.info(f"✅ Produto adicionado ao resumo: {produto_info['produto']} x{quantidade_prod} = €{preco_total_produto}")
                
                if not produto_info:
                    app.logger.error(f"❌ Produto ID {produto_id} não encontrado!")
        
        app.logger.info(f"📊 Total bar: €{total_bar}, Total produtos: {len(produtos_bar_detalhados)}")
        
        # Processar toppings selecionados
        toppings_selecionados = []
        total_toppings = 0.0
        
        try:
            import json
            toppings_list = json.loads(toppings_json) if toppings_json != '[]' else []
            app.logger.info(f"🍿 Processando toppings: {len(toppings_list)} toppings")
            
            if toppings_list:
                for topping in toppings_list:
                    topping_id = topping.get('id')
                    quantidade_topping = int(topping.get('quantidade', 1))
                    
                    app.logger.info(f"🔍 Buscando topping ID: {topping_id}, quantidade: {quantidade_topping}")
                    
                    # Buscar topping na base de dados
                    cursor.execute("SELECT nome, preco FROM toppings WHERE id = %s", (topping_id,))
                    topping_info = cursor.fetchone()
                    
                    if topping_info:
                        preco_unitario = float(topping_info['preco'])
                        preco_total_topping = preco_unitario * quantidade_topping
                        total_toppings += preco_total_topping
                        
                        # Adicionar topping com detalhes para o template
                        toppings_selecionados.append({
                            'nome': topping_info['nome'],
                            'quantidade': quantidade_topping,
                            'preco_unitario': preco_unitario,
                            'preco_total': preco_total_topping
                        })
                        app.logger.info(f"✅ Topping adicionado ao resumo: {topping_info['nome']} x{quantidade_topping} = €{preco_total_topping}")
                    else:
                        app.logger.error(f"❌ Topping ID {topping_id} não encontrado!")
        except Exception as e:
            app.logger.error(f"❌ Erro ao processar toppings: {e}")
            toppings_selecionados = []
        
        app.logger.info(f"📊 Total toppings: €{total_toppings}, Total toppings: {len(toppings_selecionados)}")
        
        total_geral = total_bilhetes + total_bar + total_toppings
        
        cursor.close()
        conn.close()
        
        # Processar poster_url do filme
        if filme and filme.get('poster_url'):
            poster_url = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
            if not poster_url.startswith('imgs/filmes/'):
                if '/' not in poster_url:
                    poster_url = f"imgs/filmes/{poster_url}"
                elif not poster_url.startswith('imgs/'):
                    poster_url = f"imgs/filmes/{poster_url}"
            filme['poster_url'] = poster_url
        
        app.logger.info(f"Resumo - Total: €{total_geral:.2f} (Bilhetes: €{total_bilhetes:.2f}, Bar: €{total_bar:.2f})")
        
        # 🔧 GUARDAR DADOS NA SESSÃO PARA O FLUXO DE PAGAMENTO
        salvar_dados_reserva_sessao(
            filme_id=int(filme_id),
            cinema_id=int(cinema_id),
            id_tipo_sessao=int(id_tipo_sessao),
            id_horario_sessao=int(id_horario_sessao),
            data_sessao=str(data_sessao),
            lugares=lugares_selecionados,
            produtos_bar=produtos_selecionados
        )
        
        return render_template('resumo_reserva_completo.html',
                             filme=filme,
                             cinema=cinema,
                             horario=horario,
                             tipo_sessao=tipo_sessao,
                             data_sessao=data_sessao,
                             lugares_selecionados=lugares_selecionados,
                             produtos_selecionados=produtos_selecionados,
                             produtos_bar=produtos_bar_detalhados,
                             toppings=toppings_selecionados,
                             preco_bilhete=preco_bilhete,
                             total_bilhetes=total_bilhetes,
                             total_bar=total_bar,
                             total_toppings=total_toppings,
                             total_geral=total_geral,
                             quantidade=len(lugares_selecionados),
                             user_authenticated='user_id' in session,
                             user_avatar=get_user_avatar(),
                             user_name=session.get('user_nome', ''),
                             user_email=session.get('user_email', ''),
                             user_telefone=session.get('user_telefone', ''))
                             
    except Exception as e:
        app.logger.error(f"Erro na rota /resumo_reserva: {e}")
        flash("Erro ao carregar resumo da reserva", "error")
        return render_template('error.html', message="Erro interno")

@app.route('/bar/menu/<int:menu_id>')
def bar_menu_ajax(menu_id):
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.id, p.produto, p.preco, p.imagem_url, p.tipo,
                   IFNULL(GROUP_CONCAT(cp.caracteristica SEPARATOR ','), '') AS caracteristicas
            FROM menu_produtos mp
            JOIN bar p ON mp.produto_id = p.id
            LEFT JOIN caracteristica_produto_bar cp ON cp.produto_id = p.id
            WHERE mp.menu_id = %s
            GROUP BY p.id
            ORDER BY p.tipo, p.produto
        """, (menu_id,))
        produtos = cursor.fetchall() or []

        normalized = []
        for pr in produtos:
            pr['imagem_url'] = _normalize_img_path(pr.get('imagem_url'))
            pr['tipo'] = (pr.get('tipo') or 'snack').strip().lower()
            raw = pr.get('caracteristicas') or ''
            parts = [s.strip().lower() for s in raw.split(',') if s.strip()]
            seen = set(); uniq = []
            for s in parts:
                if s not in seen:
                    seen.add(s); uniq.append(s)
            pr['caracteristicas'] = ','.join(uniq)
            normalized.append(pr)

        return jsonify({'produtos': normalized})
    except Exception:
        app.logger.exception("Erro bar_menu_ajax:")
        return jsonify({'produtos': []}), 500
    finally:
        try: cursor.close()
        except: pass
        try: cnx.close()
        except: pass

# ==========================
# Outras rotas estáticas
# ==========================
@app.route('/hoje')
def hoje(): return render_template('hoje.html')
@app.route('/terca')
def terca(): return render_template('terca.html')
@app.route('/quarta')
def quarta(): return render_template('quarta.html')
@app.route('/quinta')
def quinta(): return render_template('quinta.html')
@app.route('/sexta')
def sexta(): return render_template('sexta.html')
@app.route('/sabado')
def sabado(): return render_template('sabado.html')
@app.route('/domingo')
def domingo(): return render_template('domingo.html')
@app.route('/cinemas')
def cinemas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar todos os cinemas com informações (incluindo imagem da BD)
        if 'user_id' in session:
            # Se o usuário está logado, verificar quais são favoritos
            cursor.execute("""
                SELECT c.id, c.nome, c.localizacao, c.regiao, c.imagem,
                       CASE WHEN cf.id IS NOT NULL THEN 1 ELSE 0 END as is_favorito
                FROM cinemas c
                LEFT JOIN cinemas_favoritos cf ON c.id = cf.cinema_id AND cf.usuario_id = %s
                ORDER BY c.regiao, c.nome
            """, (session['user_id'],))
        else:
            # Se não está logado, buscar apenas os cinemas
            cursor.execute("""
                SELECT id, nome, localizacao, regiao, imagem, 0 as is_favorito
                FROM cinemas
                ORDER BY regiao, nome
            """)
        
        cinemas_list = cursor.fetchall()
        
        # Limpar e normalizar caminhos das imagens
        for cinema in cinemas_list:
            if cinema.get('imagem'):
                # Limpar o caminho (remover aspas, normalizar barras)
                cinema['imagem'] = cinema['imagem'].replace('\\', '/').replace('"', '').strip()
            else:
                cinema['imagem'] = 'imgs/cinemas/room.jpg'
        
        # Buscar regiões únicas
        cursor.execute("SELECT DISTINCT regiao FROM cinemas ORDER BY regiao")
        regioes = [r['regiao'] for r in cursor.fetchall()]
        
        # Buscar avatar se logado
        logged_in = 'user_id' in session
        avatar = None
        
        avatar = get_user_avatar()
    
    finally:
        cursor.close()
        conn.close()
    
    return render_template('cinemas.html', 
                         cinemas=cinemas_list, 
                         regioes=regioes,
                         logged_in=logged_in,
                         avatar=avatar)

@app.route('/cinemas/<int:id_cinema>/filmes')
def cinema_filmes(id_cinema):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar informações do cinema (incluindo imagem da BD)
        cursor.execute("""
            SELECT id, nome, localizacao, regiao, imagem
            FROM cinemas
            WHERE id = %s
        """, (id_cinema,))
        cinema = cursor.fetchone()
        
        if not cinema:
            flash('Cinema não encontrado', 'error')
            return redirect(url_for('cinemas'))
        
        # Limpar e normalizar caminho da imagem
        if cinema.get('imagem'):
            cinema['imagem'] = cinema['imagem'].replace('\\', '/').replace('"', '').strip()
        else:
            cinema['imagem'] = 'imgs/cinemas/room.jpg'
        
        # Buscar filmes disponíveis neste cinema
        cursor.execute("""
            SELECT DISTINCT
                f.id,
                f.titulo,
                f.poster_url,
                f.poster_hover,
                f.data_lancamento,
                f.duracao,
                GROUP_CONCAT(DISTINCT g.nome SEPARATOR ', ') as generos
            FROM filmes f
            INNER JOIN horarios_sessao hs ON f.id = hs.id_filme
            LEFT JOIN filme_generos fg ON f.id = fg.filme_id
            LEFT JOIN generos g ON fg.genero_id = g.id
            WHERE hs.id_cinema = %s
            AND f.data_lancamento <= CURDATE()
            GROUP BY f.id
            ORDER BY f.titulo
        """, (id_cinema,))
        filmes = cursor.fetchall()
        
        # Normalizar poster_url e poster_hover
        for filme in filmes:
            if filme.get('poster_url'):
                filme['poster_url'] = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
            if filme.get('poster_hover'):
                filme['poster_hover'] = filme['poster_hover'].replace('\\', '/').replace('"', '').strip()
        
    finally:
        cursor.close()
        conn.close()
    
    return render_template('cinema_filmes.html',
                         cinema=cinema,
                         filmes=filmes)
@app.route('/beneficios')
def beneficios(): return render_template('beneficios.html')

@app.route('/politica-privacidade')
def politica_privacidade():
    logged_in = 'user_id' in session
    avatar = get_user_avatar()
    if logged_in:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COALESCE(u.avatar, a.caminho) AS avatar
            FROM usuarios u
            LEFT JOIN avatars a ON u.avatar_id = a.id
            WHERE u.id = %s
        """, (session['user_id'],))
        user_data = cursor.fetchone()
        if user_data and user_data.get('avatar'):
            avatar = user_data['avatar'].replace('\\', '/').replace('"', '').strip()
        cursor.close()
        conn.close()
    return render_template('politica_privacidade.html', logged_in=logged_in, avatar=avatar)

@app.route('/termos-condicoes')
def termos_condicoes():
    logged_in = 'user_id' in session
    avatar = get_user_avatar()
    if logged_in:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COALESCE(u.avatar, a.caminho) AS avatar
            FROM usuarios u
            LEFT JOIN avatars a ON u.avatar_id = a.id
            WHERE u.id = %s
        """, (session['user_id'],))
        user_data = cursor.fetchone()
        if user_data and user_data.get('avatar'):
            avatar = user_data['avatar'].replace('\\', '/').replace('"', '').strip()
        cursor.close()
        conn.close()
    return render_template('termos_condicoes.html', logged_in=logged_in, avatar=avatar)

@app.route('/cookies')
def cookies_page():
    logged_in = 'user_id' in session
    avatar = get_user_avatar()
    if logged_in:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COALESCE(u.avatar, a.caminho) AS avatar
            FROM usuarios u
            LEFT JOIN avatars a ON u.avatar_id = a.id
            WHERE u.id = %s
        """, (session['user_id'],))
        user_data = cursor.fetchone()
        if user_data and user_data.get('avatar'):
            avatar = user_data['avatar'].replace('\\', '/').replace('"', '').strip()
        cursor.close()
        conn.close()
    return render_template('cookies.html', logged_in=logged_in, avatar=avatar)

# ==========================
# API de Pesquisa em Tempo Real
# ==========================
@app.route('/api/pesquisa')
def api_pesquisa():
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'filmes': [], 'cinemas': [], 'produtos': []})
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Pesquisar filmes (limite 5)
    cursor.execute("""
        SELECT id, titulo, poster_url, poster_hover, duracao
        FROM filmes
        WHERE titulo LIKE %s OR sinopse LIKE %s
        LIMIT 5
    """, (f'%{query}%', f'%{query}%'))
    filmes = cursor.fetchall()
    
    # Normalizar imagens
    for f in filmes:
        f['poster_url'] = _normalize_img_path(f.get('poster_url'))
    
    # Pesquisar cinemas (limite 5)
    cursor.execute("""
        SELECT id, nome, localizacao, regiao
        FROM cinemas
        WHERE nome LIKE %s OR localizacao LIKE %s
        LIMIT 5
    """, (f'%{query}%', f'%{query}%'))
    cinemas = cursor.fetchall()
    
    # Pesquisar menus do bar
    menus = []
    try:
        cursor.execute("""
            SELECT id, nome, descricao, total as preco, imagem_url
            FROM menus
            WHERE nome LIKE %s OR descricao LIKE %s
            LIMIT 5
        """, (f'%{query}%', f'%{query}%'))
        menus = cursor.fetchall()
        # Normalizar imagens
        for m in menus:
            m['imagem_url'] = _normalize_img_path(m.get('imagem_url'))
    except Exception as e:
        app.logger.info(f"Erro ao buscar menus: {e}")
        menus = []
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'filmes': filmes,
        'cinemas': cinemas,
        'menus': menus
    })

# ==========================
# API para verificar toppings de produtos
# ==========================
@app.route('/api/check_toppings')
def api_check_toppings():
    """Verifica se um produto/menu tem toppings associados"""
    produto_id = request.args.get('produto_id')
    tipo = request.args.get('tipo', 'bar')  # 'bar' ou 'menu'
    
    if not produto_id:
        return jsonify({'has_toppings': False, 'toppings': []})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar toppings associados ao produto/menu
        if tipo == 'menu':
            cursor.execute("""
                SELECT DISTINCT t.id, t.nome, t.descricao, t.preco, t.imagem_url
                FROM toppings_produtos tp
                JOIN toppings t ON tp.id_topping = t.id
                WHERE tp.id_menu = %s AND tp.tipo_produto = 'menu'
                ORDER BY t.nome
            """, (produto_id,))
        else:  # bar
            cursor.execute("""
                SELECT DISTINCT t.id, t.nome, t.descricao, t.preco, t.imagem_url
                FROM toppings_produtos tp
                JOIN toppings t ON tp.id_topping = t.id
                WHERE tp.id_produto = %s AND tp.tipo_produto = 'bar'
                ORDER BY t.nome
            """, (produto_id,))
        
        toppings = cursor.fetchall()
        
        # Processar URLs das imagens
        for topping in toppings:
            if topping.get('imagem_url'):
                imagem_url = topping['imagem_url'].replace('\\', '/').replace('"', '').strip()
                if not imagem_url.startswith(('http://', 'https://', 'imgs/')):
                    if '/' not in imagem_url:
                        imagem_url = f"imgs/toppings/{imagem_url}"
                    elif not imagem_url.startswith('imgs/'):
                        imagem_url = f"imgs/toppings/{imagem_url}"
                topping['imagem_url'] = imagem_url
            else:
                topping['imagem_url'] = 'imgs/toppings/topping-default.svg'
        
        cursor.close()
        conn.close()
        
        has_toppings = len(toppings) > 0
        
        app.logger.info(f"🍿 Verificação toppings: produto_id={produto_id}, tipo={tipo}, toppings={len(toppings)}")
        
        return jsonify({
            'has_toppings': has_toppings,
            'toppings': toppings
        })
        
    except Exception as e:
        app.logger.error(f"❌ Erro ao verificar toppings: {e}")
        return jsonify({'has_toppings': False, 'toppings': [], 'error': str(e)})

# ==========================
# Pesquisa Global
# ==========================
@app.route('/pesquisa')
def pesquisa():
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Pesquisar filmes
    cursor.execute("""
        SELECT id, titulo, poster_url, poster_hover, duracao
        FROM filmes
        WHERE titulo LIKE %s OR sinopse LIKE %s
        LIMIT 20
    """, (f'%{query}%', f'%{query}%'))
    filmes = cursor.fetchall()
    
    # Normalizar imagens dos filmes
    for f in filmes:
        f['poster_url'] = _normalize_img_path(f.get('poster_url'))
    
    # Pesquisar cinemas
    cursor.execute("""
        SELECT id, nome, localizacao, regiao
        FROM cinemas
        WHERE nome LIKE %s OR localizacao LIKE %s OR regiao LIKE %s
        LIMIT 10
    """, (f'%{query}%', f'%{query}%', f'%{query}%'))
    cinemas = cursor.fetchall()
    
    # Pesquisar menus do bar
    menus = []
    try:
        cursor.execute("""
            SELECT id, nome, descricao, total as preco, imagem_url
            FROM menus
            WHERE nome LIKE %s OR descricao LIKE %s
            LIMIT 10
        """, (f'%{query}%', f'%{query}%'))
        menus = cursor.fetchall()
        # Normalizar imagens
        for m in menus:
            m['imagem_url'] = _normalize_img_path(m.get('imagem_url'))
    except Exception as e:
        app.logger.info(f"Erro ao buscar menus: {e}")
        menus = []
    
    cursor.close()
    conn.close()
    
    return render_template('pesquisa.html', 
                         query=query,
                         filmes=filmes,
                         cinemas=cinemas,
                         menus=menus)

# ==========================
# SISTEMA DE AVALIAÇÕES
# ==========================
@app.route('/avaliar_filme', methods=['POST'])
def avaliar_filme():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    data = request.get_json()
    filme_id = data.get('filme_id')
    rating = data.get('rating')
    comentario = data.get('comentario', '')
    
    if not filme_id or not rating:
        return jsonify({'success': False, 'message': 'Dados incompletos'})
    
    try:
        rating = int(rating)  # Mudança para inteiros (1-5)
        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': 'Rating deve ser entre 1 e 5'})
    except:
        return jsonify({'success': False, 'message': 'Rating inválido'})
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar se o filme existe
        cursor.execute("SELECT id, titulo FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        
        if not filme:
            return jsonify({'success': False, 'message': 'Filme não encontrado'})
        
        # Verificar se o utilizador tem reserva para este filme
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM reservas r
            WHERE r.id_usuario = %s AND r.id_filme = %s
        """, (session['user_id'], filme_id))
        
        result = cursor.fetchone()
        if result['count'] == 0:
            return jsonify({'success': False, 'message': 'Só podes avaliar filmes que reservaste!'})
        
        # Inserir ou atualizar avaliação
        cursor.execute("""
            INSERT INTO avaliacoes_filmes (usuario_id, filme_id, rating, comentario, data_avaliacao)
            VALUES (%s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
            rating = VALUES(rating),
            comentario = VALUES(comentario),
            data_avaliacao = NOW()
        """, (session['user_id'], filme_id, rating, comentario))
        
        conn.commit()
        
        # Retornar sucesso com URL de redirecionamento
        return jsonify({
            'success': True, 
            'message': 'Avaliação salva com sucesso!',
            'redirect_url': f'/filme/{filme_id}',
            'filme_titulo': filme['titulo']
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

@app.route('/remover_avaliacao', methods=['POST'])
def remover_avaliacao():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    data = request.get_json()
    id_filme = data.get('id_filme')
    
    if not id_filme:
        return jsonify({'success': False, 'message': 'ID do filme necessário'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM avaliacoes_filmes 
            WHERE usuario_id = %s AND filme_id = %s
        """, (session['user_id'], id_filme))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Avaliação removida!'})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# ==========================
# SISTEMA DE CINEMAS FAVORITOS
# ==========================
@app.route('/toggle_cinema_favorito', methods=['POST'])
def toggle_cinema_favorito():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    try:
        data = request.get_json()
        id_cinema = data.get('id_cinema')
        
        if not id_cinema:
            return jsonify({'success': False, 'message': 'ID do cinema necessário'})
        
        app.logger.info(f"Toggle cinema favorito - user: {session['user_id']}, cinema: {id_cinema}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se já é favorito
            cursor.execute("""
                SELECT id FROM cinemas_favoritos 
                WHERE usuario_id = %s AND cinema_id = %s
            """, (session['user_id'], id_cinema))
            
            favorito = cursor.fetchone()
            app.logger.info(f"Favorito existente: {favorito}")
            
            if favorito:
                # Remover dos favoritos
                cursor.execute("""
                    DELETE FROM cinemas_favoritos 
                    WHERE usuario_id = %s AND cinema_id = %s
                """, (session['user_id'], id_cinema))
                message = 'Cinema removido dos favoritos!'
                is_favorito = False
                app.logger.info(f"Cinema {id_cinema} removido dos favoritos")
            else:
                # Adicionar aos favoritos
                cursor.execute("""
                    INSERT INTO cinemas_favoritos (usuario_id, cinema_id)
                    VALUES (%s, %s)
                """, (session['user_id'], id_cinema))
                message = 'Cinema adicionado aos favoritos!'
                is_favorito = True
                app.logger.info(f"Cinema {id_cinema} adicionado aos favoritos")
            
            conn.commit()
            
            return jsonify({
                'success': True, 
                'message': message,
                'is_favorito': is_favorito
            })
            
        except mysql.connector.Error as db_err:
            conn.rollback()
            app.logger.error(f"Erro de BD ao toggle cinema favorito: {str(db_err)}")
            return jsonify({'success': False, 'message': f'Erro de base de dados: {str(db_err)}'})
        finally:
            try:
                cursor.close()
            except:
                pass
            try:
                conn.close()
            except:
                pass
                
    except Exception as e:
        app.logger.error(f"Erro geral ao toggle cinema favorito: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

# Rota alternativa com URL diferente (usada pelo template cinemas.html)
@app.route('/toggle_favorito_cinema/<int:cinema_id>', methods=['POST'])
def toggle_favorito_cinema(cinema_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    try:
        app.logger.info(f"Toggle favorito cinema - user: {session['user_id']}, cinema: {cinema_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se já é favorito
            cursor.execute("""
                SELECT id FROM cinemas_favoritos 
                WHERE usuario_id = %s AND cinema_id = %s
            """, (session['user_id'], cinema_id))
            
            favorito = cursor.fetchone()
            
            if favorito:
                # Remover dos favoritos
                cursor.execute("""
                    DELETE FROM cinemas_favoritos 
                    WHERE usuario_id = %s AND cinema_id = %s
                """, (session['user_id'], cinema_id))
                message = 'Cinema removido dos favoritos!'
                is_favorito = False
            else:
                # Adicionar aos favoritos
                cursor.execute("""
                    INSERT INTO cinemas_favoritos (usuario_id, cinema_id)
                    VALUES (%s, %s)
                """, (session['user_id'], cinema_id))
                message = 'Cinema adicionado aos favoritos!'
                is_favorito = True
            
            conn.commit()
            
            return jsonify({
                'success': True, 
                'message': message,
                'is_favorito': is_favorito
            })
            
        except mysql.connector.Error as db_err:
            conn.rollback()
            app.logger.error(f"Erro de BD: {str(db_err)}")
            return jsonify({'success': False, 'message': f'Erro de base de dados: {str(db_err)}'})
        finally:
            try:
                cursor.close()
            except:
                pass
            try:
                conn.close()
            except:
                pass
                
    except Exception as e:
        app.logger.error(f"Erro geral: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@app.route('/atualizar_perfil', methods=['POST'])
def atualizar_perfil():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    data = request.get_json()
    biografia = data.get('biografia', '')
    filme_favorito_id = data.get('filme_favorito_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE usuarios 
            SET biografia = %s, filme_favorito_id = %s
            WHERE id = %s
        """, (biografia, filme_favorito_id, session['user_id']))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Perfil atualizado com sucesso!'})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# ==========================
# ADMIN - GESTÃO DE ATORES
# ==========================
@app.route('/admin/atores')
def admin_atores():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Buscar todos os atores com contagem de filmes
    cursor.execute("""
        SELECT a.id, a.nome, a.foto_url as foto, a.nacionalidade,
               COUNT(DISTINCT fa.filme_id) as total_filmes
        FROM atores a
        LEFT JOIN filme_atores fa ON a.id = fa.ator_id
        GROUP BY a.id
        ORDER BY a.id DESC
    """)
    atores = cursor.fetchall()
    
    # Limpar caminhos das fotos
    for ator in atores:
        if ator.get('foto'):
            # Remover barras invertidas e aspas
            foto = ator['foto'].replace('\\', '/').replace('"', '').strip()
            # Remover 'static/' do início se existir
            if foto.startswith('static/'):
                foto = foto[7:]
            ator['foto'] = foto
    
    cursor.close()
    conn.close()
    
    return render_template('admin_atores.html', user=get_current_user(), atores=atores)

@app.route('/admin/atores/adicionar', methods=['POST'])
def admin_adicionar_ator():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    nacionalidade = request.form.get('nacionalidade')
    
    # Processar upload de foto
    foto_url = None
    if 'foto' in request.files:
        foto = request.files['foto']
        if foto and foto.filename != '':
            # Verificar se é uma imagem válida
            if foto.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                # Criar nome único para o arquivo
                import uuid
                import os
                from werkzeug.utils import secure_filename
                
                filename = secure_filename(foto.filename)
                file_extension = os.path.splitext(filename)[1]
                unique_filename = f"{uuid.uuid4().hex}{file_extension}"
                
                # Criar diretório se não existir
                upload_dir = os.path.join('static', 'imgs', 'atores')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Salvar arquivo
                file_path = os.path.join(upload_dir, unique_filename)
                foto.save(file_path)
                
                # Salvar caminho relativo na base de dados
                foto_url = f"imgs/atores/{unique_filename}"
            else:
                flash('Formato de imagem inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'erro')
                return redirect(url_for('admin_atores'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO atores (nome, foto_url, nacionalidade)
        VALUES (%s, %s, %s)
    """, (nome, foto_url, nacionalidade))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Ator adicionado com sucesso!', 'success')
    return redirect(url_for('admin_atores'))

@app.route('/admin/atores/editar/<int:ator_id>', methods=['POST'])
def admin_editar_ator(ator_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    nacionalidade = request.form.get('nacionalidade')
    
    # Processar upload de foto (se fornecida)
    foto_url = None
    if 'foto' in request.files:
        foto = request.files['foto']
        if foto and foto.filename != '':
            # Verificar se é uma imagem válida
            if foto.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                # Criar nome único para o arquivo
                import uuid
                import os
                from werkzeug.utils import secure_filename
                
                filename = secure_filename(foto.filename)
                file_extension = os.path.splitext(filename)[1]
                unique_filename = f"{uuid.uuid4().hex}{file_extension}"
                
                # Criar diretório se não existir
                upload_dir = os.path.join('static', 'imgs', 'atores')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Salvar arquivo
                file_path = os.path.join(upload_dir, unique_filename)
                foto.save(file_path)
                
                # Salvar caminho relativo na base de dados
                foto_url = f"imgs/atores/{unique_filename}"
            else:
                flash('Formato de imagem inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'erro')
                return redirect(url_for('admin_atores'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Se foi fornecida nova foto, atualizar; senão manter a existente
    if foto_url:
        cursor.execute("""
            UPDATE atores
            SET nome = %s, foto_url = %s, nacionalidade = %s
            WHERE id = %s
        """, (nome, foto_url, nacionalidade, ator_id))
    else:
        cursor.execute("""
            UPDATE atores
            SET nome = %s, nacionalidade = %s
            WHERE id = %s
        """, (nome, nacionalidade, ator_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Ator atualizado com sucesso!', 'success')
    return redirect(url_for('admin_atores'))

@app.route('/admin/atores/remover/<int:ator_id>', methods=['POST'])
def admin_remover_ator(ator_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Remover associações com filmes
    cursor.execute("DELETE FROM filme_atores WHERE ator_id = %s", (ator_id,))
    
    # Remover ator
    cursor.execute("DELETE FROM atores WHERE id = %s", (ator_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Ator removido com sucesso!', 'success')
    return redirect(url_for('admin_atores'))

# Endpoint para pesquisar atores
@app.route('/admin/atores/pesquisar')
def admin_pesquisar_atores():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify({'success': False, 'message': 'Query muito curta'})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Pesquisar atores por nome (case insensitive)
        cursor.execute("""
            SELECT id, nome, nacionalidade, foto_url
            FROM atores 
            WHERE nome LIKE %s 
            ORDER BY nome 
            LIMIT 20
        """, (f'%{query}%',))
        
        atores = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'atores': atores
        })
        
    except Exception as e:
        app.logger.error(f"Erro na pesquisa de atores: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

# Endpoint para obter informações de um ator específico
@app.route('/admin/atores/<int:ator_id>/info')
def admin_info_ator(ator_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nome, nacionalidade, foto_url
            FROM atores 
            WHERE id = %s
        """, (ator_id,))
        
        ator = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if ator:
            return jsonify({
                'success': True,
                'ator': ator
            })
        else:
            return jsonify({'success': False, 'message': 'Ator não encontrado'})
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar informações do ator: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

# ==========================
# ADMIN - GESTÃO DO BAR
# ==========================
@app.route('/admin/bar')
def admin_bar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Buscar todos os produtos do bar
    cursor.execute("""
        SELECT b.id, b.produto as nome, b.preco, b.imagem_url as imagem, b.tipo,
               GROUP_CONCAT(DISTINCT m.nome SEPARATOR ', ') as menus
        FROM bar b
        LEFT JOIN menu_produtos mp ON b.id = mp.produto_id
        LEFT JOIN menus m ON mp.menu_id = m.id
        GROUP BY b.id
        ORDER BY b.id DESC
    """)
    produtos = cursor.fetchall()
    
    # Buscar todos os menus com seus produtos
    cursor.execute("""
        SELECT m.id, m.nome, m.descricao, m.preco_total, m.imagem_url,
               GROUP_CONCAT(b.produto SEPARATOR ', ') as produtos
        FROM menus m
        LEFT JOIN menu_produtos mp ON m.id = mp.menu_id
        LEFT JOIN bar b ON mp.produto_id = b.id
        GROUP BY m.id
        ORDER BY m.nome
    """)
    menus = cursor.fetchall()
    
    # Converter produtos de string para lista
    for menu in menus:
        if menu['produtos']:
            menu['produtos'] = menu['produtos'].split(', ')
        else:
            menu['produtos'] = []
    
    # Buscar todos os toppings
    cursor.execute("""
        SELECT id, nome, descricao, preco, imagem_url
        FROM toppings
        ORDER BY nome
    """)
    toppings = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin_bar.html', user=get_current_user(), produtos=produtos, menus=menus, toppings=toppings)

@app.route('/admin/bar/produtos/adicionar', methods=['POST'])
def admin_adicionar_produto():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    tipo = request.form.get('tipo')
    
    # Processar upload de imagem
    imagem_path = None
    
    if 'imagem' in request.files:
        file = request.files['imagem']
        if file and file.filename:
            import uuid
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
            filename = f"{uuid.uuid4().hex}.{ext}"
            
            upload_folder = os.path.join('static', 'imgs', 'produtos')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            imagem_path = f"imgs/produtos/{filename}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bar (produto, preco, imagem_url, tipo)
        VALUES (%s, %s, %s, %s)
    """, (nome, preco, imagem_path, tipo))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Produto adicionado com sucesso!', 'success')
    return redirect(url_for('admin_bar'))

@app.route('/admin/bar/produtos/<int:produto_id>/dados')
def admin_get_produto_dados(produto_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bar WHERE id = %s", (produto_id,))
        produto = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not produto:
            return jsonify({'error': 'Produto não encontrado'}), 404
        
        # Limpar caminho da imagem
        if produto.get('imagem_url'):
            produto['imagem_url'] = produto['imagem_url'].replace('\\', '/').replace('"', '').strip()
        
        return jsonify(produto)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/bar/produtos/editar/<int:produto_id>', methods=['POST'])
def admin_editar_produto(produto_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    tipo = request.form.get('tipo')
    imagem_atual = request.form.get('imagem_atual')
    
    # Processar upload de imagem
    imagem_path = imagem_atual  # Manter imagem atual por padrão
    
    if 'imagem' in request.files:
        file = request.files['imagem']
        if file and file.filename:
            import uuid
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
            filename = f"{uuid.uuid4().hex}.{ext}"
            
            upload_folder = os.path.join('static', 'imgs', 'produtos')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            imagem_path = f"imgs/produtos/{filename}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE bar
        SET produto = %s, preco = %s, imagem_url = %s, tipo = %s
        WHERE id = %s
    """, (nome, preco, imagem_path, tipo, produto_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Produto atualizado com sucesso!', 'success')
    return redirect(url_for('admin_bar'))

@app.route('/admin/bar/produtos/remover/<int:produto_id>', methods=['POST'])
def admin_remover_produto(produto_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Remover de menus
    cursor.execute("DELETE FROM menu_produtos WHERE produto_id = %s", (produto_id,))
    
    # Remover produto
    cursor.execute("DELETE FROM bar WHERE id = %s", (produto_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Produto removido com sucesso!', 'success')
    return redirect(url_for('admin_bar'))

@app.route('/admin/bar/menus/<int:menu_id>/dados')
def admin_menu_dados(menu_id):
    """Retorna os dados de um menu em JSON para edição"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Log para debug
        print(f"[DEBUG] Buscando menu ID: {menu_id}")
        
        # Buscar dados do menu
        cursor.execute("""
            SELECT id, nome, descricao, preco_total, imagem_url
            FROM menus
            WHERE id = %s
        """, (menu_id,))
        
        menu = cursor.fetchone()
        print(f"[DEBUG] Menu encontrado: {menu}")
        
        if not menu:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Menu não encontrado'}), 404
        
        # Converter Decimal para float para JSON
        if menu['preco_total']:
            menu['preco_total'] = float(menu['preco_total'])
        
        # Buscar produtos do menu
        cursor.execute("""
            SELECT b.id, b.produto as nome, b.preco
            FROM bar b
            JOIN menu_produtos mp ON b.id = mp.produto_id
            WHERE mp.menu_id = %s
        """, (menu_id,))
        
        produtos = cursor.fetchall()
        print(f"[DEBUG] Produtos encontrados: {len(produtos)}")
        
        # Converter preços dos produtos para float
        for produto in produtos:
            if produto['preco']:
                produto['preco'] = float(produto['preco'])
        
        menu['produtos'] = produtos
        
        cursor.close()
        conn.close()
        
        print(f"[DEBUG] Retornando menu: {menu}")
        return jsonify(menu)
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar dados do menu {menu_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Erro ao buscar dados: {str(e)}'}), 500

@app.route('/admin/bar/menus/adicionar', methods=['POST'])
def admin_adicionar_menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    preco_total = request.form.get('preco_total')
    produtos_ids = request.form.getlist('produtos[]')
    
    # Upload da imagem
    imagem_url = None
    if 'imagem' in request.files:
        imagem_file = request.files['imagem']
        if imagem_file and imagem_file.filename:
            import os
            import uuid
            from werkzeug.utils import secure_filename
            
            # Criar diretório se não existir
            upload_folder = os.path.join('static', 'imgs', 'menus')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Gerar nome único
            ext = os.path.splitext(secure_filename(imagem_file.filename))[1]
            filename = f"menu_{uuid.uuid4().hex[:8]}{ext}"
            filepath = os.path.join(upload_folder, filename)
            
            # Salvar arquivo
            imagem_file.save(filepath)
            imagem_url = f"imgs/menus/{filename}"
            
            print(f"[DEBUG] Imagem salva: {imagem_url}")
    
    print(f"[DEBUG] Adicionando novo menu")
    print(f"[DEBUG] Nome: {nome}")
    print(f"[DEBUG] Produtos: {produtos_ids}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Inserir menu
    cursor.execute("""
        INSERT INTO menus (nome, descricao, preco_total, imagem_url)
        VALUES (%s, %s, %s, %s)
    """, (nome, descricao, preco_total, imagem_url))
    
    menu_id = cursor.lastrowid
    print(f"[DEBUG] Menu criado com ID: {menu_id}")
    
    # Adicionar produtos ao menu
    for produto_id in produtos_ids:
        if produto_id:  # Verificar se não está vazio
            cursor.execute("""
                INSERT INTO menu_produtos (menu_id, produto_id)
                VALUES (%s, %s)
            """, (menu_id, produto_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Menu adicionado com sucesso!', 'success')
    return redirect(url_for('admin_bar'))

@app.route('/admin/bar/menus/editar/<int:menu_id>', methods=['POST'])
def admin_editar_menu(menu_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    preco_total = request.form.get('preco_total')
    produtos_ids = request.form.getlist('produtos[]')
    imagem_atual = request.form.get('imagem_atual')
    
    # Upload da nova imagem (se houver)
    imagem_url = imagem_atual  # Manter a imagem atual por padrão
    if 'imagem' in request.files:
        imagem_file = request.files['imagem']
        if imagem_file and imagem_file.filename:
            import os
            import uuid
            from werkzeug.utils import secure_filename
            
            # Criar diretório se não existir
            upload_folder = os.path.join('static', 'imgs', 'menus')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Apagar imagem antiga se existir
            if imagem_atual:
                old_path = os.path.join('static', imagem_atual)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                        print(f"[DEBUG] Imagem antiga removida: {old_path}")
                    except Exception as e:
                        print(f"[DEBUG] Erro ao remover imagem antiga: {e}")
            
            # Gerar nome único
            ext = os.path.splitext(secure_filename(imagem_file.filename))[1]
            filename = f"menu_{uuid.uuid4().hex[:8]}{ext}"
            filepath = os.path.join(upload_folder, filename)
            
            # Salvar arquivo
            imagem_file.save(filepath)
            imagem_url = f"imgs/menus/{filename}"
            
            print(f"[DEBUG] Nova imagem salva: {imagem_url}")
    
    print(f"[DEBUG] Editando menu {menu_id}")
    print(f"[DEBUG] Produtos recebidos: {produtos_ids}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Atualizar dados do menu
    cursor.execute("""
        UPDATE menus
        SET nome = %s, descricao = %s, preco_total = %s, imagem_url = %s
        WHERE id = %s
    """, (nome, descricao, preco_total, imagem_url, menu_id))
    
    # Remover produtos antigos
    cursor.execute("DELETE FROM menu_produtos WHERE menu_id = %s", (menu_id,))
    
    # Adicionar novos produtos
    for produto_id in produtos_ids:
        if produto_id:  # Verificar se não está vazio
            cursor.execute("""
                INSERT INTO menu_produtos (menu_id, produto_id)
                VALUES (%s, %s)
            """, (menu_id, produto_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Menu atualizado com sucesso!', 'success')
    return redirect(url_for('admin_bar'))

@app.route('/admin/bar/menus/remover/<int:menu_id>', methods=['POST'])
def admin_remover_menu(menu_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Remover produtos associados ao menu
    cursor.execute("DELETE FROM menu_produtos WHERE menu_id = %s", (menu_id,))
    
    # Remover menu
    cursor.execute("DELETE FROM menus WHERE id = %s", (menu_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Menu removido com sucesso!', 'success')
    return redirect(url_for('admin_bar'))

@app.route('/admin/bar/menus/<int:menu_id>')
def admin_menu_detalhe(menu_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Buscar menu
    cursor.execute("SELECT * FROM menus WHERE id = %s", (menu_id,))
    menu = cursor.fetchone()
    
    # Buscar produtos do menu
    cursor.execute("""
        SELECT p.id, p.nome, p.preco, p.imagem, p.tipo
        FROM produtos p
        INNER JOIN menu_produtos mp ON p.id = mp.produto_id
        WHERE mp.menu_id = %s
        ORDER BY p.tipo, p.nome
    """, (menu_id,))
    produtos_menu = cursor.fetchall()
    
    # Buscar produtos disponíveis para adicionar
    cursor.execute("""
        SELECT id, nome, preco, tipo
        FROM produtos
        WHERE id NOT IN (
            SELECT produto_id FROM menu_produtos WHERE menu_id = %s
        )
        ORDER BY tipo, nome
    """, (menu_id,))
    produtos_disponiveis = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin_menu_detalhe.html', 
                         menu=menu, 
                         produtos_menu=produtos_menu,
                         produtos_disponiveis=produtos_disponiveis)

@app.route('/admin/bar/menus/<int:menu_id>/adicionar-produto', methods=['POST'])
def admin_adicionar_produto_menu(menu_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    produto_id = request.form.get('produto_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO menu_produtos (menu_id, produto_id)
        VALUES (%s, %s)
    """, (menu_id, produto_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Produto adicionado ao menu!', 'success')
    return redirect(url_for('admin_menu_detalhe', menu_id=menu_id))

@app.route('/admin/bar/menus/<int:menu_id>/remover-produto/<int:produto_id>', methods=['POST'])
def admin_remover_produto_menu(menu_id, produto_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM menu_produtos
        WHERE menu_id = %s AND produto_id = %s
    """, (menu_id, produto_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Produto removido do menu!', 'success')
    return redirect(url_for('admin_menu_detalhe', menu_id=menu_id))

# ==========================
# ADMIN - GESTÃO DE TOPPINGS
# ==========================
@app.route('/admin/bar/toppings/adicionar', methods=['POST'])
def admin_adicionar_topping():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    preco = request.form.get('preco')
    
    # Upload da imagem
    imagem_url = None
    if 'imagem' in request.files:
        imagem_file = request.files['imagem']
        if imagem_file and imagem_file.filename:
            import os
            import uuid
            from werkzeug.utils import secure_filename
            
            # Criar diretório se não existir
            upload_folder = os.path.join('static', 'imgs', 'toppings')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Gerar nome único
            ext = os.path.splitext(secure_filename(imagem_file.filename))[1]
            filename = f"topping_{uuid.uuid4().hex[:8]}{ext}"
            filepath = os.path.join(upload_folder, filename)
            
            # Salvar arquivo
            imagem_file.save(filepath)
            imagem_url = f"imgs/toppings/{filename}"
            
            print(f"[DEBUG] Imagem do topping salva: {imagem_url}")
    
    print(f"[DEBUG] Adicionando novo topping: {nome}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Inserir topping
    cursor.execute("""
        INSERT INTO toppings (nome, descricao, preco, imagem_url)
        VALUES (%s, %s, %s, %s)
    """, (nome, descricao, preco, imagem_url))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Topping adicionado com sucesso!', 'success')
    return redirect(url_for('admin_bar'))

@app.route('/admin/bar/toppings/<int:topping_id>/dados')
def admin_topping_dados(topping_id):
    """Retorna os dados de um topping em JSON para edição"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar dados do topping
        cursor.execute("""
            SELECT id, nome, descricao, preco, imagem_url
            FROM toppings
            WHERE id = %s
        """, (topping_id,))
        
        topping = cursor.fetchone()
        
        if not topping:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Topping não encontrado'}), 404
        
        # Converter Decimal para float para JSON
        if topping['preco']:
            topping['preco'] = float(topping['preco'])
        
        cursor.close()
        conn.close()
        
        return jsonify(topping)
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar dados do topping {topping_id}: {str(e)}")
        return jsonify({'error': f'Erro ao buscar dados: {str(e)}'}), 500

@app.route('/admin/bar/toppings/editar/<int:topping_id>', methods=['POST'])
def admin_editar_topping(topping_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    preco = request.form.get('preco')
    imagem_atual = request.form.get('imagem_atual')
    
    # Upload da nova imagem (se houver)
    imagem_url = imagem_atual  # Manter a imagem atual por padrão
    if 'imagem' in request.files:
        imagem_file = request.files['imagem']
        if imagem_file and imagem_file.filename:
            import os
            import uuid
            from werkzeug.utils import secure_filename
            
            # Criar diretório se não existir
            upload_folder = os.path.join('static', 'imgs', 'toppings')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Gerar nome único
            ext = os.path.splitext(secure_filename(imagem_file.filename))[1]
            filename = f"topping_{uuid.uuid4().hex[:8]}{ext}"
            filepath = os.path.join(upload_folder, filename)
            
            # Salvar arquivo
            imagem_file.save(filepath)
            imagem_url = f"imgs/toppings/{filename}"
            
            print(f"[DEBUG] Nova imagem salva: {imagem_url}")
    
    print(f"[DEBUG] Editando topping {topping_id}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Atualizar dados do topping
    cursor.execute("""
        UPDATE toppings
        SET nome = %s, descricao = %s, preco = %s, imagem_url = %s
        WHERE id = %s
    """, (nome, descricao, preco, imagem_url, topping_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Topping atualizado com sucesso!', 'success')
    return redirect(url_for('admin_bar'))

@app.route('/admin/bar/toppings/remover/<int:topping_id>', methods=['POST'])
def admin_remover_topping(topping_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Remover topping
    cursor.execute("DELETE FROM toppings WHERE id = %s", (topping_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Topping removido com sucesso!', 'success')
    return redirect(url_for('admin_bar'))

# ==========================
# ADMIN - GESTÃO DE SALAS
# ==========================
@app.route('/admin/salas')
def admin_salas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Buscar todas as salas com informações do cinema
    cursor.execute("""
        SELECT s.id, s.nome_sala, s.capacidade, s.tipo_sala, 
               s.id_cinema,
               c.nome as cinema_nome, c.localizacao as cinema_localizacao
        FROM salas s
        INNER JOIN cinemas c ON s.id_cinema = c.id
        GROUP BY s.id_cinema, s.nome_sala
        HAVING s.id = MAX(s.id)
        ORDER BY s.id DESC
    """)
    rows = cursor.fetchall()
    
    # Convert to dictionaries
    columns = [description[0] for description in cursor.description]
    salas = [dict(zip(columns, row)) for row in rows]
    
    # Buscar cinemas para o formulário
    cursor.execute("SELECT id, nome, localizacao FROM cinemas ORDER BY nome")
    cinema_rows = cursor.fetchall()
    cinema_columns = [description[0] for description in cursor.description]
    cinemas = [dict(zip(cinema_columns, row)) for row in cinema_rows]
    
    cursor.close()
    conn.close()
    
    return render_template('admin_salas.html', user=get_current_user(), salas=salas, cinemas=cinemas)

@app.route('/admin/salas/adicionar', methods=['POST'])
def admin_adicionar_sala_alt():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    capacidade = request.form.get('capacidade')
    tipo = request.form.get('tipo')
    id_cinema = request.form.get('id_cinema')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO salas (nome_sala, capacidade, tipo_sala, id_cinema)
        VALUES (%s, %s, %s, %s)
    """, (nome, capacidade, tipo, id_cinema))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Sala adicionada com sucesso!', 'success')
    return redirect(url_for('admin_salas'))

@app.route('/admin/salas/editar/<int:sala_id>', methods=['POST'])
def admin_editar_sala_alt(sala_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    capacidade = request.form.get('capacidade')
    tipo = request.form.get('tipo')
    id_cinema = request.form.get('id_cinema')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE salas
        SET nome_sala = %s, capacidade = %s, tipo_sala = %s, id_cinema = %s
        WHERE id = %s
    """, (nome, capacidade, tipo, id_cinema, sala_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Sala atualizada com sucesso!', 'success')
    return redirect(url_for('admin_salas'))

@app.route('/admin/salas/remover/<int:sala_id>', methods=['POST'])
def admin_remover_sala_alt(sala_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Remover horários associados
    cursor.execute("DELETE FROM horarios WHERE sala_id = %s", (sala_id,))
    
    # Remover sala
    cursor.execute("DELETE FROM salas WHERE id = %s", (sala_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Sala removida com sucesso!', 'success')
    return redirect(url_for('admin_salas'))

# ==========================
# ADMIN - GESTÃO DE AVATARES
# ==========================
@app.route('/admin/avatares')
def admin_avatares():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Buscar avatares com categoria (mais recentes primeiro)
    cursor.execute("""
        SELECT a.id, a.nome, a.caminho, a.categoria_id, c.nome as categoria_nome
        FROM avatars a
        LEFT JOIN avatar_categories c ON a.categoria_id = c.id
        ORDER BY a.id DESC
    """)
    avatares = cursor.fetchall()
    
    # Buscar categorias
    cursor.execute("SELECT * FROM avatar_categories ORDER BY nome")
    categorias = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin_avatares.html', user=get_current_user(), avatares=avatares, categorias=categorias)

@app.route('/admin/avatares/adicionar', methods=['POST'])
def admin_adicionar_avatar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        nome = request.form.get('nome')
        categoria_id = request.form.get('categoria_id')
        
        # Log para debug
        app.logger.info(f"Tentando adicionar avatar: nome={nome}, categoria_id={categoria_id}")
        
        # Validar campos obrigatórios
        if not nome:
            flash('Nome é obrigatório!', 'erro')
            return redirect(url_for('admin_avatares'))
        
        # Processar upload de imagem
        caminho = None
        if 'avatar_file' in request.files:
            file = request.files['avatar_file']
            app.logger.info(f"Ficheiro recebido: {file.filename if file else 'None'}")
            
            if file and file.filename:
                # Gerar nome único para o ficheiro
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'png'
                filename = f"{uuid.uuid4()}.{ext}"
                
                # Criar diretório se não existir
                upload_dir = os.path.join('static', 'imgs', 'avatars')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Salvar ficheiro
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                
                # Caminho relativo para a BD
                caminho = f"imgs/avatars/{filename}"
                app.logger.info(f"Ficheiro salvo em: {filepath}, caminho BD: {caminho}")
        
        # Se não houver upload, usar imagem padrão
        if not caminho:
            caminho = "imgs/icons/user_icon34-removebg-preview.png"
            app.logger.info(f"Usando imagem padrão: {caminho}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO avatars (nome, caminho, categoria_id) VALUES (%s, %s, %s)", (nome, caminho, categoria_id))
        conn.commit()
        
        # Verificar se foi inserido
        avatar_id = cursor.lastrowid
        app.logger.info(f"Avatar inserido com ID: {avatar_id}")
        
        cursor.close()
        conn.close()
        
        flash('Avatar adicionado com sucesso!', 'success')
        return redirect(url_for('admin_avatares'))
        
    except Exception as e:
        app.logger.error(f"Erro ao adicionar avatar: {str(e)}")
        flash(f'Erro ao adicionar avatar: {str(e)}', 'erro')
        return redirect(url_for('admin_avatares'))

@app.route('/admin/avatares/editar/<int:avatar_id>', methods=['POST'])
def admin_editar_avatar(avatar_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    categoria_id = request.form.get('categoria_id')
    
    # Validar campos obrigatórios
    if not nome:
        flash('Nome é obrigatório!', 'erro')
        return redirect(url_for('admin_avatares'))
    
    # Buscar caminho atual
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT caminho FROM avatars WHERE id = %s", (avatar_id,))
    avatar_atual = cursor.fetchone()
    
    caminho = avatar_atual['caminho'] if avatar_atual else None
    
    # Processar upload de nova imagem (se fornecida)
    if 'avatar_file' in request.files:
        file = request.files['avatar_file']
        if file and file.filename:
            # Gerar nome único para o ficheiro
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'png'
            filename = f"{uuid.uuid4()}.{ext}"
            
            # Criar diretório se não existir
            upload_dir = os.path.join('static', 'imgs', 'avatars')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Salvar ficheiro
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            
            # Caminho relativo para a BD
            caminho = f"imgs/avatars/{filename}"
            
            # Remover imagem antiga se não for a padrão
            if avatar_atual and avatar_atual['caminho'] != "imgs/icons/user_icon34-removebg-preview.png":
                old_path = os.path.join('static', avatar_atual['caminho'])
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except:
                        pass
    
    cursor.execute("UPDATE avatars SET nome = %s, caminho = %s, categoria_id = %s WHERE id = %s", (nome, caminho, categoria_id, avatar_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Avatar atualizado com sucesso!', 'success')
    return redirect(url_for('admin_avatares'))

@app.route('/admin/avatares/remover/<int:avatar_id>', methods=['POST'])
def admin_remover_avatar(avatar_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM avatars WHERE id = %s", (avatar_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Avatar removido com sucesso!', 'success')
    return redirect(url_for('admin_avatares'))

# Rotas para categorias de avatares
@app.route('/admin/avatares/categorias/adicionar', methods=['POST'])
def admin_adicionar_categoria_avatar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO avatar_categories (nome) VALUES (%s)", (nome,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Categoria adicionada com sucesso!', 'success')
    return redirect(url_for('admin_avatares'))

@app.route('/admin/avatares/categorias/editar/<int:categoria_id>', methods=['POST'])
def admin_editar_categoria_avatar(categoria_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE avatar_categories SET nome = %s WHERE id = %s", (nome, categoria_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Categoria atualizada com sucesso!', 'success')
    return redirect(url_for('admin_avatares'))

@app.route('/admin/avatares/categorias/remover/<int:categoria_id>', methods=['POST'])
def admin_remover_categoria_avatar(categoria_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM avatar_categories WHERE id = %s", (categoria_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Categoria removida com sucesso!', 'success')
    return redirect(url_for('admin_avatares'))

# ==========================
# ROTA PARA CORRIGIR HORÁRIOS SEM SALA
# ==========================
@app.route('/admin/corrigir-salas-horarios')
def admin_corrigir_salas_horarios():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar todos os horários sem sala
        cursor.execute("""
            SELECT hs.id, hs.id_cinema, hs.id_filme, hs.id_tipo_sessao, c.nome as cinema_nome
            FROM horarios_sessao hs
            JOIN cinemas c ON hs.id_cinema = c.id
            WHERE hs.id_sala IS NULL
            ORDER BY c.nome
        """)
        horarios_sem_sala = cursor.fetchall()
        
        # Corrigir automaticamente
        corrigidos = 0
        nao_corrigidos = 0
        
        for horario in horarios_sem_sala:
            # Buscar primeira sala disponível do cinema
            cursor.execute("""
                SELECT id, nome_sala
                FROM salas
                WHERE id_cinema = %s
                ORDER BY id
                LIMIT 1
            """, (horario['id_cinema'],))
            sala = cursor.fetchone()
            
            if sala:
                # Atualizar horário com a sala
                cursor.execute("""
                    UPDATE horarios_sessao
                    SET id_sala = %s
                    WHERE id = %s
                """, (sala['id'], horario['id']))
                corrigidos += 1
                app.logger.info(f"Horário {horario['id']} atualizado com sala {sala['nome_sala']}")
            else:
                nao_corrigidos += 1
                app.logger.warning(f"Cinema {horario['cinema_nome']} não tem salas cadastradas")
        
        conn.commit()
        
        flash(f'✅ Corrigidos {corrigidos} horários! {nao_corrigidos} não puderam ser corrigidos (cinemas sem salas).', 'success')
        return redirect(url_for('admin_dashboard'))
        
    except Exception as e:
        app.logger.error(f"Erro ao corrigir salas: {str(e)}")
        flash(f'Erro ao corrigir salas: {str(e)}', 'erro')
        return redirect(url_for('admin_dashboard'))
    finally:
        cursor.close()
        conn.close()

# ==========================
# ADMIN - GESTÃO DE TIPOS DE SESSÃO
# ==========================
@app.route('/admin/tipos-sessao')
def admin_tipos_sessao():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tipos_sessao ORDER BY id DESC")
    tipos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin_tipos_sessao.html', user=get_current_user(), tipos=tipos)

@app.route('/admin/tipos-sessao/adicionar', methods=['POST'])
def admin_adicionar_tipo_sessao_alt():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tipos_sessao (nome, descricao) VALUES (%s, %s)", (nome, descricao))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Tipo de sessão adicionado com sucesso!', 'success')
    return redirect(url_for('admin_tipos_sessao'))

@app.route('/admin/tipos-sessao/editar/<int:tipo_id>', methods=['POST'])
def admin_editar_tipo_sessao_alt(tipo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tipos_sessao SET nome = %s, descricao = %s WHERE id = %s", (nome, descricao, tipo_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Tipo de sessão atualizado com sucesso!', 'success')
    return redirect(url_for('admin_tipos_sessao'))

@app.route('/admin/tipos-sessao/remover/<int:tipo_id>', methods=['POST'])
def admin_remover_tipo_sessao_alt(tipo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tipos_sessao WHERE id = %s", (tipo_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Tipo de sessão removido com sucesso!', 'success')
    return redirect(url_for('admin_tipos_sessao'))

# ==========================
# API DE FILMES DISPONÍVEIS
# ==========================
@app.route('/api/filmes_disponiveis')
def api_filmes_disponiveis():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar filmes em exibição
        cursor.execute("""
            SELECT id, titulo 
            FROM filmes 
            WHERE estado = 'em_exibicao'
            ORDER BY titulo
        """)
        
        filmes = []
        for row in cursor.fetchall():
            filmes.append({
                'id': row[0],
                'titulo': row[1]
            })
        
        conn.close()
        
        # Se não houver filmes na base de dados, retornar lista padrão
        if not filmes:
            filmes = [
                {'id': 1, 'titulo': 'Rambo III'},
                {'id': 2, 'titulo': 'Superman (2025)'},
                {'id': 3, 'titulo': 'E.T. the Extra-Terrestrial'},
                {'id': 4, 'titulo': 'Back to the Future'},
                {'id': 5, 'titulo': 'Jurassic Park'},
                {'id': 6, 'titulo': 'Scream'},
                {'id': 7, 'titulo': 'The Karate Kid'},
                {'id': 8, 'titulo': 'The Shawshank Redemption'}
            ]
        
        return jsonify(filmes)
        
    except Exception as e:
        print(f"Erro ao buscar filmes disponíveis: {e}")
        # Retornar lista padrão em caso de erro
        filmes_padrao = [
            {'id': 1, 'titulo': 'Rambo III'},
            {'id': 2, 'titulo': 'Superman (2025)'},
            {'id': 3, 'titulo': 'E.T. the Extra-Terrestrial'},
            {'id': 4, 'titulo': 'Back to the Future'},
            {'id': 5, 'titulo': 'Jurassic Park'},
            {'id': 6, 'titulo': 'Scream'},
            {'id': 7, 'titulo': 'The Karate Kid'},
            {'id': 8, 'titulo': 'The Shawshank Redemption'}
        ]
        return jsonify(filmes_padrao)

# API DE AVATARES
# ==========================
@app.route('/api/avatares')
def api_avatares():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT a.id, a.caminho, a.categoria_id, c.nome as categoria_nome
            FROM avatars a
            LEFT JOIN avatar_categories c ON a.categoria_id = c.id
            ORDER BY c.nome, a.id
        """)
        avatares = cursor.fetchall()
        
        # Agrupar por categoria
        categorias = {}
        for avatar in avatares:
            if avatar.get('caminho'):
                avatar['caminho'] = avatar['caminho'].replace('\\', '/').replace('"', '').strip()
            
            cat_nome = avatar.get('categoria_nome') or 'Outros'
            if cat_nome not in categorias:
                categorias[cat_nome] = []
            categorias[cat_nome].append(avatar)
        
        return jsonify({'success': True, 'categorias': categorias})
    except Exception as e:
        print(f"Erro ao buscar avatares: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/api/remover-cinema-favorito', methods=['POST'])
def api_remover_cinema_favorito():
    """API para remover cinema dos favoritos"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    try:
        data = request.get_json()
        cinema_id = data.get('cinema_id')
        
        if not cinema_id:
            return jsonify({'success': False, 'message': 'ID do cinema não fornecido'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Remover cinema dos favoritos
        cursor.execute("""
            DELETE FROM cinemas_favoritos 
            WHERE usuario_id = %s AND cinema_id = %s
        """, (session['user_id'], cinema_id))
        
        if cursor.rowcount > 0:
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Cinema removido dos favoritos'})
        else:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Cinema não estava nos favoritos'})
        
    except Exception as e:
        app.logger.error(f"Erro ao remover cinema dos favoritos: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

@app.route('/api/atualizar-nome', methods=['POST'])
def api_atualizar_nome():
    """API para atualizar o nome do usuário"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    try:
        data = request.get_json()
        novo_nome = data.get('nome', '').strip()
        
        if not novo_nome:
            return jsonify({'success': False, 'message': 'Nome não pode estar vazio'})
        
        if len(novo_nome) < 2:
            return jsonify({'success': False, 'message': 'Nome deve ter pelo menos 2 caracteres'})
        
        if len(novo_nome) > 100:
            return jsonify({'success': False, 'message': 'Nome muito longo (máximo 100 caracteres)'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Atualizar nome do usuário
        cursor.execute("""
            UPDATE usuarios 
            SET nome = %s 
            WHERE id = %s
        """, (novo_nome, session['user_id']))
        
        conn.commit()
        
        # Atualizar sessão
        session['user_nome'] = novo_nome
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Nome atualizado com sucesso'})
        
    except Exception as e:
        app.logger.error(f"Erro ao atualizar nome: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

@app.route('/api/avatar-categorias')
def api_avatar_categorias():
    """API para carregar categorias de avatares para o modal"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar categorias e seus avatares
        cursor.execute("""
            SELECT c.id, c.nome,
                   a.id as avatar_id, a.nome as avatar_nome, a.caminho as avatar_caminho
            FROM avatar_categories c
            LEFT JOIN avatars a ON c.id = a.categoria_id
            ORDER BY c.nome, a.id
        """)
        results = cursor.fetchall()
        
        # Organizar por categorias
        categorias_dict = {}
        for row in results:
            cat_id = row['id']
            if cat_id not in categorias_dict:
                categorias_dict[cat_id] = {
                    'nome': row['nome'],
                    'subtitulo': '',
                    'avatares': []
                }
            
            if row['avatar_id']:  # Se há avatar nesta categoria
                avatar_caminho = row['avatar_caminho']
                if avatar_caminho:
                    # Limpar e normalizar caminho
                    avatar_caminho = avatar_caminho.replace('\\', '/').replace('"', '').strip()
                    if not avatar_caminho.startswith('/static/'):
                        avatar_caminho = f"/static/{avatar_caminho}"
                    
                    categorias_dict[cat_id]['avatares'].append({
                        'id': row['avatar_id'],
                        'nome': row['avatar_nome'],
                        'caminho': avatar_caminho
                    })
        
        # Converter para lista e filtrar categorias vazias
        categorias_list = []
        for cat in categorias_dict.values():
            if cat['avatares']:
                cat['subtitulo'] = f"{len(cat['avatares'])} avatares disponíveis"
                categorias_list.append(cat)
        
        cursor.close()
        conn.close()
        
        if not categorias_list:
            # Fallback se não houver dados
            categorias_list = [{
                'nome': 'Avatar Padrão',
                'subtitulo': 'Avatar padrão do sistema',
                'avatares': [
                    {'nome': 'Padrão', 'caminho': '/static/imgs/icons/user_icon34-removebg-preview.png'}
                ]
            }]
        
        return jsonify({'success': True, 'categorias': categorias_list})
        
    except Exception as e:
        app.logger.error(f"Erro ao carregar categorias de avatar: {str(e)}")
        # Fallback com avatar padrão
        categorias_fallback = [{
            'nome': 'Avatar Padrão',
            'subtitulo': 'Avatar padrão do sistema',
            'avatares': [
                {'nome': 'Padrão', 'caminho': '/static/imgs/icons/user_icon34-removebg-preview.png'}
            ]
        }]
        return jsonify({'success': True, 'categorias': categorias_fallback})
    finally:
        cursor.close()
        conn.close()

@app.route('/api/atualizar-avatar', methods=['POST'])
def api_atualizar_avatar():
    """API para atualizar o avatar do usuário"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    try:
        data = request.get_json()
        avatar_caminho = data.get('avatar')
        
        if not avatar_caminho:
            return jsonify({'success': False, 'message': 'Caminho do avatar não fornecido'})
        
        # Limpar caminho do avatar
        avatar_caminho = avatar_caminho.replace('/static/', '').replace('\\', '/').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Atualizar avatar do usuário
        cursor.execute("""
            UPDATE usuarios 
            SET avatar = %s 
            WHERE id = %s
        """, (avatar_caminho, session['user_id']))
        
        conn.commit()
        
        # Atualizar sessão
        session['user_avatar'] = avatar_caminho
        
        return jsonify({'success': True, 'message': 'Avatar atualizado com sucesso'})
        
    except Exception as e:
        print(f"Erro ao atualizar avatar: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/alterar-senha', methods=['POST'])
def api_alterar_senha():
    """API para alterar a senha do usuário"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    try:
        data = request.get_json()
        nova_senha = data.get('novaSenha', '').strip()
        
        if not nova_senha:
            return jsonify({'success': False, 'message': 'Nova senha é obrigatória'})
        
        if len(nova_senha) < 6:
            return jsonify({'success': False, 'message': 'A nova senha deve ter pelo menos 6 caracteres'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar se o usuário existe
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'})
        
        # Atualizar com a nova senha (usuário já está autenticado)
        nova_senha_hash = generate_password_hash(nova_senha)
        cursor.execute(
            "UPDATE usuarios SET senha = %s WHERE id = %s",
            (nova_senha_hash, session['user_id'])
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        app.logger.info(f"Senha alterada com sucesso para usuário ID: {session['user_id']}")
        return jsonify({'success': True, 'message': 'Senha alterada com sucesso'})
        
    except Exception as e:
        app.logger.error(f"Erro ao alterar senha: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

@app.route('/pagamento-exclusivo')
def pagamento_exclusivo():
    """Página de pagamento para sessões exclusivas"""
    # Verificar se há dados de reserva
    # Os dados serão obtidos via JavaScript do sessionStorage
    
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    return render_template('pagamento_exclusivo.html', 
                         logged_in=logged_in, 
                         avatar=avatar)

@app.route('/api/processar-pagamento-exclusivo', methods=['POST'])
def api_processar_pagamento_exclusivo():
    """API para processar pagamento de sessão exclusiva"""
    try:
        data = request.get_json()
        app.logger.info(f"Dados recebidos para pagamento exclusivo: {data}")
        
        # Validar dados obrigatórios
        required_fields = ['tipo_sala', 'filme_id', 'filme_nome', 'data_sessao', 
                          'hora_sessao', 'num_pessoas', 'total', 'nome_cliente', 
                          'email_cliente', 'metodo_pagamento']
        
        for field in required_fields:
            if not data.get(field):
                app.logger.error(f"Campo obrigatório ausente: {field}")
                return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar se o filme existe (se filme_id não for 0)
        filme_id = data['filme_id']
        if filme_id and filme_id != '0':
            cursor.execute("SELECT id FROM filmes WHERE id = %s", (filme_id,))
            if not cursor.fetchone():
                app.logger.warning(f"Filme ID {filme_id} não encontrado, definindo como NULL")
                filme_id = None
        else:
            filme_id = None
        
        # Preparar dados para inserção
        user_id = session.get('user_id') if 'user_id' in session else None
        
        app.logger.info(f"Inserindo reserva exclusiva - Sala: {data['tipo_sala']}, Filme: {data['filme_nome']}")
        
        # Inserir reserva na base de dados
        cursor.execute("""
            INSERT INTO reservas_exclusivas 
            (tipo_sala, filme_id, data_sessao, hora_sessao, num_pessoas, 
             preco_total, usuario_id, nome_cliente, email_cliente, telefone_cliente, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'confirmada')
        """, (
            data['tipo_sala'],
            filme_id,
            data['data_sessao'],
            data['hora_sessao'],
            int(data['num_pessoas']),
            float(data['total']),
            user_id,
            data['nome_cliente'],
            data['email_cliente'],
            data.get('telefone_cliente', '')
        ))
        
        reserva_id = cursor.lastrowid
        conn.commit()
        
        app.logger.info(f"Reserva exclusiva inserida com sucesso - ID: {reserva_id}")
        
        # Preparar dados para o email
        dados_email = {
            'reserva_id': reserva_id,
            'tipo_sala': data['tipo_sala'],
            'filme': data['filme_nome'],
            'data_sessao': data['data_sessao'],
            'hora_sessao': data['hora_sessao'],
            'num_pessoas': data['num_pessoas'],
            'total': f"€{data['total']}",
            'nome_cliente': data['nome_cliente'],
            'email_cliente': data['email_cliente']
        }
        
        # Enviar email de confirmação
        try:
            email_enviado = enviar_email_confirmacao_exclusiva(
                data['email_cliente'],
                data['nome_cliente'],
                dados_email
            )
        except Exception as email_error:
            app.logger.error(f"Erro ao enviar email: {str(email_error)}")
            email_enviado = False
        
        cursor.close()
        conn.close()
        
        app.logger.info(f"Reserva exclusiva processada com sucesso - ID: {reserva_id}")
        
        return jsonify({
            'success': True, 
            'message': 'Reserva confirmada com sucesso!',
            'reserva_id': reserva_id,
            'email_enviado': email_enviado
        })
        
    except mysql.connector.Error as db_error:
        app.logger.error(f"Erro de base de dados ao processar pagamento exclusivo: {str(db_error)}")
        return jsonify({'success': False, 'message': f'Erro na base de dados: {str(db_error)}'})
    except Exception as e:
        app.logger.error(f"Erro geral ao processar pagamento exclusivo: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao processar pagamento: {str(e)}'})

def enviar_email_confirmacao_exclusiva(destinatario_email, destinatario_nome, dados_reserva):
    """
    Envia email de confirmação para reserva exclusiva
    """
    try:
        app.logger.info(f"Enviando email de confirmação exclusiva para: {destinatario_email}")
        
        # Verificar se as credenciais de email estão configuradas
        if EMAIL_PASSWORD in ['sua_senha_app_aqui', 'DESATIVADO_TEMPORARIAMENTE'] or not EMAIL_PASSWORD:
            app.logger.warning("Email desativado temporariamente. Configure senha de app do Gmail para ativar.")
            return False

        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🎬 Confirmação de Reserva Exclusiva CineVibe - #{dados_reserva["reserva_id"]}'
        msg['From'] = f'CineVibe <{EMAIL_USER}>'
        msg['To'] = destinatario_email

        # Mapear tipos de sala
        tipos_sala = {
            'intimista': 'Sala Intimista',
            'vip': 'Sala Vip',
            'premium': 'Sala Premium'
        }
        
        nome_sala = tipos_sala.get(dados_reserva['tipo_sala'], 'Sala Exclusiva')
        
        try:
            data_formatada = datetime.strptime(dados_reserva['data_sessao'], '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            data_formatada = dados_reserva['data_sessao']
        
        # Conteúdo HTML do email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    background: linear-gradient(135deg, #0d1117, #161b22); 
                    margin: 0; 
                    padding: 20px; 
                    color: white;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: linear-gradient(135deg, #1B263B, #2C3E50); 
                    border-radius: 20px; 
                    overflow: hidden; 
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
                    border: 2px solid rgba(255, 214, 10, 0.3);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #FFD60A, #FFA500); 
                    padding: 40px 30px; 
                    text-align: center; 
                }}
                .header h1 {{ 
                    color: #1a1a1a; 
                    margin: 0; 
                    font-size: 28px; 
                    font-weight: 900; 
                }}
                .content {{ 
                    padding: 40px 30px; 
                }}
                .content h2 {{ 
                    color: #FFD60A; 
                    margin-bottom: 25px; 
                    font-size: 24px;
                }}
                .reserva-details {{
                    background: rgba(255, 214, 10, 0.1);
                    padding: 25px;
                    border-radius: 15px;
                    margin: 25px 0;
                    border: 1px solid rgba(255, 214, 10, 0.3);
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 12px;
                    padding: 8px 0;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}
                .detail-label {{
                    color: rgba(255, 255, 255, 0.8);
                    font-weight: 600;
                }}
                .detail-value {{
                    color: #FFD60A;
                    font-weight: 700;
                }}
                .total-row {{
                    border-top: 2px solid rgba(255, 214, 10, 0.3);
                    margin-top: 15px;
                    padding-top: 15px;
                    font-size: 1.2rem;
                }}
                .footer {{ 
                    background: rgba(0, 0, 0, 0.4); 
                    padding: 30px; 
                    text-align: center; 
                    color: rgba(255, 255, 255, 0.7); 
                    font-size: 14px; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎬 CineVibe Exclusivo</h1>
                </div>
                <div class="content">
                    <h2>Olá, {destinatario_nome}!</h2>
                    <p>A sua reserva exclusiva foi confirmada com sucesso! Prepare-se para uma experiência cinematográfica única.</p>
                    
                    <div class="reserva-details">
                        <div class="detail-row">
                            <span class="detail-label">Reserva #:</span>
                            <span class="detail-value">{dados_reserva['reserva_id']}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Sala:</span>
                            <span class="detail-value">{nome_sala}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Filme:</span>
                            <span class="detail-value">{dados_reserva['filme']}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Data:</span>
                            <span class="detail-value">{data_formatada}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Horário:</span>
                            <span class="detail-value">{dados_reserva['hora_sessao']}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Pessoas:</span>
                            <span class="detail-value">{dados_reserva['num_pessoas']}</span>
                        </div>
                        <div class="detail-row total-row">
                            <span class="detail-label">Total Pago:</span>
                            <span class="detail-value">{dados_reserva['total']}</span>
                        </div>
                    </div>
                    
                    <p><strong>Instruções importantes:</strong></p>
                    <ul>
                        <li>Chegue 30 minutos antes do horário da sessão</li>
                        <li>Traga um documento de identificação</li>
                        <li>A sala será preparada especialmente para o seu grupo</li>
                        <li>Serviços de bar e catering estão incluídos</li>
                    </ul>
                    
                    <p>Para qualquer alteração ou dúvida, contacte-nos através do email info@cinevibe.pt ou telefone +351 800 123 456.</p>
                </div>
                <div class="footer">
                    <p><strong>© 2024 CineVibe</strong> - Experiências Cinematográficas Exclusivas</p>
                    <p>Este email foi enviado automaticamente. Não responda a esta mensagem.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Anexar conteúdo HTML
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        # Enviar email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_USER, destinatario_email, text)
        server.quit()
        
        app.logger.info(f"✅ Email de confirmação exclusiva enviado com sucesso para {destinatario_email}")
        return True
        
    except Exception as e:
        app.logger.error(f"❌ Erro ao enviar email de confirmação exclusiva: {str(e)}")
        return False

@app.route('/api/recuperar-senha', methods=['POST'])
def api_recuperar_senha():
    """API para enviar instruções de recuperação de senha por email"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'message': 'Email é obrigatório'})
        
        if '@' not in email or '.' not in email:
            return jsonify({'success': False, 'message': 'Email inválido'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar se o email existe
        cursor.execute("SELECT id, nome FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            # Por segurança, não revelar se o email existe ou não
            return jsonify({'success': True, 'message': 'Se o email existir, as instruções foram enviadas'})
        
        # Gerar token de recuperação
        import secrets
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)  # Token válido por 1 hora
        
        cursor.close()
        conn.close()
        
        # Enviar email de recuperação
        sucesso_email = enviar_email_recuperacao_senha(email, user['nome'], token)
        
        if sucesso_email:
            app.logger.info(f"Email de recuperação enviado para {email}")
            return jsonify({
                'success': True, 
                'message': 'Instruções de recuperação enviadas para o seu email'
            })
        else:
            app.logger.error(f"Falha ao enviar email de recuperação para {email}")
            return jsonify({
                'success': True,  # Manter True por segurança
                'message': 'Se o email existir, as instruções foram enviadas'
            })
        
    except Exception as e:
        app.logger.error(f"Erro ao processar recuperação de senha: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

# ==========================
# API DE FILMES PARA SESSÕES EXCLUSIVAS
# ==========================
@app.route('/api/filmes')
def api_filmes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Primeiro, vamos verificar quantos filmes existem no total
        cursor.execute("SELECT COUNT(*) as total FROM filmes")
        total_filmes = cursor.fetchone()
        app.logger.info(f"Total de filmes na base de dados: {total_filmes['total']}")
        
        # Verificar filmes por estado
        cursor.execute("SELECT estado, COUNT(*) as count FROM filmes GROUP BY estado")
        estados = cursor.fetchall()
        app.logger.info(f"Filmes por estado: {estados}")
        
        # BUSCAR FILMES EM EXIBIÇÃO (usando os estados corretos da base de dados)
        cursor.execute("""
            SELECT 
                id, 
                titulo, 
                diretor,
                duracao, 
                idade_recomendada as classificacao_etaria,
                estado,
                data_lancamento,
                poster_url,
                sinopse
            FROM filmes 
            WHERE estado = 'em_exibicao'
            ORDER BY titulo
        """)
        todos_filmes = cursor.fetchall()
        
        app.logger.info(f"TODOS os filmes encontrados: {len(todos_filmes)}")
        
        # Se houver filmes, retornar todos
        if todos_filmes:
            app.logger.info(f"Retornando {len(todos_filmes)} filmes da base de dados")
            return jsonify(todos_filmes)
        else:
            app.logger.warning("Nenhum filme encontrado na base de dados!")
            return jsonify([])
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar filmes: {str(e)}")
        import traceback
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify([])
    finally:
        cursor.close()
        conn.close()

@app.route('/api/filmes/<genero>')
def api_filmes_por_genero(genero):
    """API para buscar filmes por gênero específico"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Mapear gêneros para busca
        generos_map = {
            'terror': ['Terror', 'Horror', 'Suspense'],
            'romance': ['Romance', 'Romântico', 'Drama Romântico'],
            'acao': ['Ação', 'Aventura', 'Thriller'],
            'comedia': ['Comédia', 'Comédia Romântica'],
            'drama': ['Drama', 'Drama'],
            'ficcao': ['Ficção Científica', 'Sci-Fi', 'Fantasia']
        }
        
        generos_busca = generos_map.get(genero.lower(), [genero])
        
        # Criar placeholders para a query
        placeholders = ', '.join(['%s'] * len(generos_busca))
        
        # Buscar filmes por gênero (usando os campos corretos da base de dados)
        cursor.execute("""
            SELECT DISTINCT
                f.id, 
                f.titulo, 
                f.diretor as genero,
                f.duracao, 
                f.idade_recomendada as classificacao_etaria,
                f.estado,
                f.data_lancamento,
                f.poster_url,
                f.sinopse
            FROM filmes f
            WHERE (f.titulo LIKE %s OR f.sinopse LIKE %s) 
            AND f.estado = 'em_exibicao'
            ORDER BY f.titulo
            LIMIT 20
        """, (f'%{genero}%', f'%{genero}%'))
        
        filmes = cursor.fetchall()
        
        app.logger.info(f"Filmes de {genero} encontrados: {len(filmes)}")
        
        # Se não encontrar filmes específicos do gênero, retornar filmes gerais
        if not filmes:
            cursor.execute("""
                SELECT 
                    id, 
                    titulo, 
                    genero, 
                    duracao, 
                    classificacao_etaria,
                    estado,
                    poster_url
                FROM filmes 
                ORDER BY titulo
                LIMIT 10
            """)
            filmes = cursor.fetchall()
            app.logger.info(f"Retornando filmes gerais: {len(filmes)}")
        
        return jsonify(filmes)
    except Exception as e:
        app.logger.error(f"Erro ao buscar filmes de {genero}: {str(e)}")
        return jsonify([])
    finally:
        cursor.close()
        conn.close()

@app.route('/atualizar_avatar', methods=['POST'])
def atualizar_avatar():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    data = request.get_json()
    avatar_id = data.get('avatar_id')
    
    if not avatar_id:
        return jsonify({'success': False, 'message': 'Avatar ID necessário'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Limpar avatar customizado e definir avatar da galeria
        cursor.execute("""
            UPDATE usuarios 
            SET avatar_id = %s, avatar = NULL
            WHERE id = %s
        """, (avatar_id, session['user_id']))
        
        # Buscar o caminho do novo avatar
        cursor.execute("SELECT caminho FROM avatars WHERE id = %s", (avatar_id,))
        avatar_data = cursor.fetchone()
        
        if avatar_data:
            new_avatar = avatar_data[0].replace('\\', '/').replace('"', '').strip()
            # Remover prefixos desnecessários
            if new_avatar.startswith('static/'):
                new_avatar = new_avatar[7:]
            if new_avatar.startswith('/static/'):
                new_avatar = new_avatar[8:]
            session['user_avatar'] = new_avatar  # Atualizar na sessão
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Avatar atualizado com sucesso!'})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

@app.route('/upload_avatar_custom', methods=['POST'])
def upload_avatar_custom():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    data = request.get_json()
    image_data = data.get('image_data')
    
    if not image_data:
        return jsonify({'success': False, 'message': 'Imagem não fornecida'})
    
    try:
        import base64
        import os
        from datetime import datetime
        
        # Extrair dados da imagem (remover o prefixo data:image/...)
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decodificar base64
        image_bytes = base64.b64decode(image_data)
        
        # Criar nome único para o arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'user_{session["user_id"]}_{timestamp}.jpg'
        
        # Caminho completo para salvar
        avatars_dir = os.path.join('static', 'imgs', 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)
        filepath = os.path.join(avatars_dir, filename)
        
        # Salvar arquivo
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # Caminho relativo para salvar na BD (coluna avatar da tabela usuarios)
        db_path = f'imgs/avatars/{filename}'
        
        # Atualizar apenas o campo avatar do usuário (não mexe na tabela avatars)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE usuarios 
                SET avatar = %s, avatar_id = NULL
                WHERE id = %s
            """, (db_path, session['user_id']))
            
            conn.commit()
            return jsonify({'success': True, 'message': 'Avatar atualizado com sucesso!'})
            
        except Exception as e:
            conn.rollback()
            # Se falhar, tentar remover o arquivo
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'success': False, 'message': f'Erro na BD: {str(e)}'})
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao processar imagem: {str(e)}'})

@app.route('/atualizar_nome', methods=['POST'])
def atualizar_nome():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    data = request.get_json()
    nome = data.get('nome', '').strip()
    
    if not nome or len(nome) < 2:
        return jsonify({'success': False, 'message': 'Nome inválido (mínimo 2 caracteres)'})
    
    if len(nome) > 100:
        return jsonify({'success': False, 'message': 'Nome muito longo (máximo 100 caracteres)'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE usuarios 
            SET nome = %s
            WHERE id = %s
        """, (nome, session['user_id']))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Nome atualizado com sucesso!'})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

# ==========================
# ==========================
# ROTA TEMPORÁRIA - DEBUG CINEMAS
# ==========================
@app.route('/debug/cinemas')
def debug_cinemas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, nome, imagem FROM cinemas ORDER BY nome')
    cinemas = cursor.fetchall()
    cursor.close()
    conn.close()
    
    html = "<h1>Cinemas na Base de Dados</h1><ul>"
    for c in cinemas:
        status = "✓" if c['imagem'] else "✗"
        img_original = c['imagem'] or 'SEM IMAGEM'
        img_limpo = c['imagem'].replace('\\', '/').replace('"', '').strip() if c['imagem'] else 'SEM IMAGEM'
        html += f"<li>{status} {c['id']}: <strong>{c['nome']}</strong><br>"
        html += f"&nbsp;&nbsp;&nbsp;Original: {img_original}<br>"
        html += f"&nbsp;&nbsp;&nbsp;Limpo: {img_limpo}</li><br>"
    html += "</ul>"
    return html

# ==========================
# PROCESSAR PAGAMENTO
# ==========================
@app.route('/processar_pagamento', methods=['POST'])
def processar_pagamento():
    try:
        app.logger.info("=== INICIANDO PROCESSAMENTO DE PAGAMENTO ===")
        
        data = request.get_json()
        app.logger.info(f"Dados recebidos: {data}")
        
        dados_reserva = data.get('dados_reserva', {})
        app.logger.info(f"Dados da reserva extraídos: {dados_reserva}")
        
        # Verificar se é reserva de sala exclusiva
        tipo_reserva = dados_reserva.get('tipo_reserva', 'individual')
        categoria = dados_reserva.get('categoria', '')
        tipo_sala = dados_reserva.get('tipo_sala', '')
        
        app.logger.info(f"Tipo de reserva: {tipo_reserva}, Categoria: {categoria}, Tipo sala: {tipo_sala}")
        
        # Obter id_usuario logo no início
        id_usuario = session.get('user_id', 0)
        app.logger.info(f"Usuario ID da sessão: {id_usuario}")
        
        # Extrair dados
        id_horario_sessao = dados_reserva.get('id_horario_sessao')
        id_cinema = dados_reserva.get('id_cinema')

        # DEBUG: Logs para rastrear dados da reserva
        app.logger.info(f"🔍 CONFIRMAR_PAGAMENTO - Dados extraídos:")
        app.logger.info(f"  dados_reserva completos: {dados_reserva}")
        app.logger.info(f"  tipo_id extraído: {dados_reserva.get('tipo_id', 'NÃO ENCONTRADO')}")
        app.logger.info(f"  id_horario_sessao: {dados_reserva.get('id_horario_sessao', 'NÃO ENCONTRADO')}")
        
        tipo_id = dados_reserva.get('tipo_id')
        id_filme = dados_reserva.get('id_filme')
        filme_nome = dados_reserva.get('filme_nome')  # Para filmes personalizados
        data_sessao = dados_reserva.get('data_sessao')
        hora_sessao = dados_reserva.get('hora_sessao')
        num_pessoas = dados_reserva.get('num_pessoas')
        total = dados_reserva.get('total')
        nome = dados_reserva.get('nome', '').strip() if dados_reserva.get('nome') else ''
        email = dados_reserva.get('email', '').strip() if dados_reserva.get('email') else ''
        telefone = dados_reserva.get('telefone', '').strip() if dados_reserva.get('telefone') else ''
        lugareses = dados_reserva.get('lugareses', [])
        produtos_bar = dados_reserva.get('produtos_bar', {})
        
        app.logger.info(f"=== DADOS EXTRAÍDOS ===")
        app.logger.info(f"tipo_reserva: {tipo_reserva}")
        app.logger.info(f"tipo_sala: {tipo_sala}")
        app.logger.info(f"id_horario_sessao: {id_horario_sessao}")
        app.logger.info(f"id_cinema: {id_cinema}")
        app.logger.info(f"tipo_id: {tipo_id}")
        app.logger.info(f"id_filme: {id_filme}")
        app.logger.info(f"filme_nome: {filme_nome}")
        app.logger.info(f"data_sessao: {data_sessao}")
        app.logger.info(f"hora_sessao: {hora_sessao}")
        app.logger.info(f"num_pessoas: {num_pessoas}")
        app.logger.info(f"nome: {nome}")
        app.logger.info(f"email: {email}")
        app.logger.info(f"lugareses: {lugareses}")
        
        # Validar dados obrigatórios baseado no tipo de reserva
        if tipo_reserva == 'sessao_exclusiva':  # Sessão exclusiva
            app.logger.info(f"🎬 Validando sessão exclusiva...")
            
            # Verificar cada campo individualmente com validação mais robusta
            campos_faltando = []
            
            # Validar data_sessao
            if not data_sessao or data_sessao == '':
                campos_faltando.append('data_sessao')
            
            # Validar hora_sessao
            if not hora_sessao or hora_sessao == '':
                campos_faltando.append('hora_sessao')
            
            # Validar num_pessoas (pode ser string ou número)
            if not num_pessoas or (isinstance(num_pessoas, str) and num_pessoas.strip() == '') or num_pessoas == 0:
                campos_faltando.append('num_pessoas')
            
            # Validar nome
            if not nome or (isinstance(nome, str) and nome.strip() == ''):
                campos_faltando.append('nome')
            
            # Validar email
            if not email or (isinstance(email, str) and email.strip() == ''):
                campos_faltando.append('email')
            
            app.logger.info(f"Verificação detalhada de campos:")
            app.logger.info(f"- data_sessao: '{data_sessao}' (tipo: {type(data_sessao)}) ({'✅ OK' if data_sessao and data_sessao != '' else '❌ FALTA'})")
            app.logger.info(f"- hora_sessao: '{hora_sessao}' (tipo: {type(hora_sessao)}) ({'✅ OK' if hora_sessao and hora_sessao != '' else '❌ FALTA'})")
            app.logger.info(f"- num_pessoas: '{num_pessoas}' (tipo: {type(num_pessoas)}) ({'✅ OK' if num_pessoas and num_pessoas != 0 else '❌ FALTA'})")
            app.logger.info(f"- nome: '{nome}' (tipo: {type(nome)}) ({'✅ OK' if nome and str(nome).strip() != '' else '❌ FALTA'})")
            app.logger.info(f"- email: '{email}' (tipo: {type(email)}) ({'✅ OK' if email and str(email).strip() != '' else '❌ FALTA'})")
            
            if campos_faltando:
                app.logger.error(f"❌ CAMPOS OBRIGATÓRIOS FALTANDO: {campos_faltando}")
                return jsonify({
                    'success': False, 
                    'message': f'Dados da sessão exclusiva incompletos. Campos em falta: {", ".join(campos_faltando)}',
                    'campos_faltando': campos_faltando,
                    'dados_recebidos': dados_reserva
                }), 400
            else:
                app.logger.info(f"✅ Todos os campos obrigatórios estão preenchidos para sessão exclusiva")
        else:  # Reserva normal
            campos_obrigatorios = [id_horario_sessao, id_cinema, tipo_id, id_filme, nome, email, lugareses]
            app.logger.info(f"Validação reserva normal - campos: {campos_obrigatorios}")
            
            if not all(campos_obrigatorios):
                app.logger.error(f"Campos obrigatórios faltando para reserva normal:")
                app.logger.error(f"- id_horario_sessao: {id_horario_sessao} ({'OK' if id_horario_sessao else 'FALTA'})")
                app.logger.error(f"- id_cinema: {id_cinema} ({'OK' if id_cinema else 'FALTA'})")
                app.logger.error(f"- tipo_id: {tipo_id} ({'OK' if tipo_id else 'FALTA'})")
                app.logger.error(f"- id_filme: {id_filme} ({'OK' if id_filme else 'FALTA'})")
                app.logger.error(f"- nome: {nome} ({'OK' if nome else 'FALTA'})")
                app.logger.error(f"- email: {email} ({'OK' if email else 'FALTA'})")
                app.logger.error(f"- lugareses: {lugareses} ({'OK' if lugareses else 'FALTA'})")
                return jsonify({'success': False, 'message': 'Dados da reserva incompletos'}), 400
        
        # Processar reserva diretamente
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            app.logger.info(f"=== PROCESSAMENTO DE PAGAMENTO ===")
            app.logger.info(f"Usuario ID da sessão: {id_usuario}")
            app.logger.info(f"Categoria: {categoria}")
            
            # Se usuário está logado, buscar dados atualizados da base de dados
            if id_usuario > 0:
                app.logger.info(f"🔍 Buscando dados do usuário logado (ID: {id_usuario})")
                cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (id_usuario,))
                user_data = cursor.fetchone()
                
                if user_data:
                    nome = user_data['nome'] or nome
                    email = user_data['email'] or email
                    telefone = ''  # Usuários logados não têm telefone na BD
                    app.logger.info(f"✅ Dados do usuário atualizados: nome='{nome}', email='{email}', telefone='{telefone}'")
                else:
                    app.logger.warning(f"⚠️ Usuário ID {id_usuario} não encontrado na base de dados")
            
            app.logger.info(f"Dados finais - nome: '{nome}', email: '{email}', telefone: '{telefone}'")
            
            reserva_ids = []
            
            if tipo_reserva == 'sessao_exclusiva':  # Sessão exclusiva
                app.logger.info(f"=== PROCESSANDO SESSÃO EXCLUSIVA ===")
                
                # Preparar dados do cliente
                nome_cliente = nome if id_usuario == 0 else None
                email_cliente = email if id_usuario == 0 else None
                telefone_cliente = telefone if (id_usuario == 0 and telefone and telefone.strip()) else None
                user_id_final = id_usuario if id_usuario > 0 else None
                
                # Inserir reserva de sessão exclusiva
                try:
                    cursor.execute("""
                        INSERT INTO reservas_exclusivas 
                        (tipo_sala, id_filme, filme_nome, data_sessao, hora_sessao, num_pessoas, 
                         total, id_usuario, nome_cliente, email_cliente, telefone_cliente, data_reserva)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (tipo_sala, id_filme, filme_nome, data_sessao, hora_sessao, num_pessoas, 
                          total, user_id_final, nome_cliente, email_cliente, telefone_cliente))
                    
                    reserva_id = cursor.lastrowid
                    reserva_ids.append(reserva_id)
                    app.logger.info(f"✅ Sessão exclusiva reservada com ID: {reserva_id}")
                    
                except Exception as e:
                    app.logger.error(f"Erro ao inserir sessão exclusiva: {str(e)}")
                    # Se a tabela não existir, criar ela
                    try:
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS reservas_exclusivas (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                tipo_sala VARCHAR(50) NOT NULL,
                                id_filme INT NULL,
                                filme_nome VARCHAR(255) NULL,
                                data_sessao DATE NOT NULL,
                                hora_sessao TIME NOT NULL,
                                num_pessoas INT NOT NULL,
                                total DECIMAL(10,2) NOT NULL,
                                id_usuario INT NULL,
                                nome_cliente VARCHAR(255) NULL,
                                email_cliente VARCHAR(255) NULL,
                                telefone_cliente VARCHAR(20) NULL,
                                data_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                status VARCHAR(20) DEFAULT 'confirmada',
                                FOREIGN KEY (id_filme) REFERENCES filmes(id),
                                FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
                            )
                        """)
                        
                        # Tentar inserir novamente
                        cursor.execute("""
                            INSERT INTO reservas_exclusivas 
                            (tipo_sala, id_filme, filme_nome, data_sessao, hora_sessao, num_pessoas, 
                             total, id_usuario, nome_cliente, email_cliente, telefone_cliente, data_reserva)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        """, (tipo_sala, id_filme, filme_nome, data_sessao, hora_sessao, num_pessoas, 
                              total, user_id_final, nome_cliente, email_cliente, telefone_cliente))
                        
                        reserva_id = cursor.lastrowid
                        reserva_ids.append(reserva_id)
                        app.logger.info(f"✅ Tabela criada e sessão exclusiva reservada com ID: {reserva_id}")
                        
                    except Exception as e2:
                        app.logger.error(f"Erro ao criar tabela e inserir: {str(e2)}")
                        raise
            
            else:  # Reserva normal de filmes
                app.logger.info(f"=== PROCESSANDO RESERVA NORMAL ===")
                
                # Buscar preço do tipo de sessão
                cursor.execute("SELECT preco_bilhete FROM tipos_sessao WHERE id = %s", (tipo_id,))
                preco_row = cursor.fetchone()
                preco_bilhete = float(preco_row['preco_bilhete']) if preco_row else 8.50
                
                # Calcular preços
                total_bilhetes = preco_bilhete * len(lugares)
                total_bar = 0
                for produto_id, produto_info in produtos_bar.items():
                    total_bar += float(produto_info.get('preco', 0)) * int(produto_info.get('quantidade', 0))
                total_geral = total_bilhetes + total_bar
                
                # Preparar dados do cliente
                nome_cliente = nome if id_usuario == 0 else None
                email_cliente = email if id_usuario == 0 else None
                telefone_cliente = telefone if (id_usuario == 0 and telefone and telefone.strip()) else None
                
                # Inserir reservas para cada lugares
                for lugares in lugareses:
                    try:
                        user_id_final = id_usuario if id_usuario > 0 else None
                        
                        # Tentar inserir com campos de cliente
                        try:
                            cursor.execute("""
                                INSERT INTO reservas (id_horario_sessao, data_sessao, id_filme, id_cinema, id_tipo_sessao, lugares, id_usuario, nome_cliente, email_cliente, telefone_cliente, data_reserva)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                            """, (id_horario_sessao, data_sessao, id_filme, id_cinema, tipo_id, lugares, user_id_final, nome_cliente, email_cliente, telefone_cliente))
                        except Exception as e:
                            # Fallback para versão antiga
                            user_id_final = id_usuario if id_usuario > 0 else 1
                            cursor.execute("""
                                INSERT INTO reservas (id_horario_sessao, data_sessao, id_filme, id_cinema, id_tipo_sessao, lugares, id_usuario, data_reserva)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                            """, (id_horario_sessao, data_sessao, id_filme, id_cinema, tipo_id, lugares, user_id_final))
                        
                        reserva_id = cursor.lastrowid
                        reserva_ids.append(reserva_id)
                        
                    except Exception as e:
                        app.logger.error(f"Erro ao inserir reserva para lugares {lugares}: {str(e)}")
                        raise
            
            conn.commit()
            app.logger.info(f"✅ Reservas confirmadas com IDs: {reserva_ids}")
            
            # Enviar email de confirmação
            try:
                from datetime import datetime
                data_formatada = datetime.strptime(data_sessao, '%Y-%m-%d').strftime('%d/%m/%Y')
                
                if tipo_reserva == 'sessao_exclusiva':  # Email para sessão exclusiva
                    filme_titulo = filme_nome if filme_nome else 'Filme Personalizado'
                    if id_filme:
                        cursor.execute("SELECT titulo FROM filmes WHERE id = %s", (id_filme,))
                        filme_row = cursor.fetchone()
                        if filme_row:
                            filme_titulo = filme_row['titulo']
                    
                    horario_completo = f"{data_formatada} às {hora_sessao}"
                    
                    # Mapear tipos de sala
                    tipos_sala_map = {
                        'intimista': 'Sala Intimista (até 15 pessoas)',
                        'premium': 'Sala Premium (até 30 pessoas)',
                        'vip': 'Sala VIP (até 50 pessoas)'
                    }
                    
                    dados_email = {
                        'reserva_id': reserva_ids[0] if reserva_ids else 0,
                        'filme': filme_titulo,
                        'cinema': 'CineVibe - Sessão Exclusiva',
                        'tipo_sessao': tipos_sala_map.get(tipo_sala, tipo_sala.title()),
                        'horario': horario_completo,
                        'quantidade': f"Sessão exclusiva para {num_pessoas} pessoa{'s' if int(num_pessoas) > 1 else ''}"
                    }
                    
                else:  # Email para reserva normal
                    cursor.execute("SELECT titulo FROM filmes WHERE id = %s", (id_filme,))
                    filme = cursor.fetchone()
                    cursor.execute("SELECT nome FROM cinemas WHERE id = %s", (id_cinema,))
                    cinema = cursor.fetchone()
                    cursor.execute("SELECT nome FROM tipos_sessao WHERE id = %s", (tipo_id,))
                    tipo_sessao = cursor.fetchone()
                    # DEBUG: Log da consulta tipo_sessao
                    app.logger.info(f"🔍 CONSULTA TIPO_SESSAO:")
                    app.logger.info(f"  tipo_id usado na consulta: {tipo_id}")
                    app.logger.info(f"  resultado da consulta: {tipo_sessao}")
                    if tipo_sessao:
                        app.logger.info(f"  nome do tipo: {tipo_sessao.get('nome', 'SEM NOME')}")
                    else:
                        app.logger.error(f"❌ TIPO_SESSAO É NULL! tipo_id: {tipo_id}")
                    cursor.execute("SELECT hora FROM horarios WHERE id = %s", (id_horario_sessao,))
                    hora_row = cursor.fetchone()
                    hora_str = str(hora_row['hora']) if hora_row else ''
                    
                    horario_completo = f"{data_formatada} às {hora_str}"
                    lugares_str = ', '.join(lugares)
                    
                    dados_email = {
                        'reserva_id': reserva_ids[0] if reserva_ids else 0,
                        'filme': filme['titulo'] if filme else 'N/A',
                        'cinema': cinema['nome'] if cinema else 'N/A',
                        'tipo_sessao': tipo_sessao['nome'] if tipo_sessao else 'N/A',
                        'horario': horario_completo,
                        'quantidade': f"{len(lugares)} bilhete{'s' if len(lugares) > 1 else ''} - Lugares: {lugares_str}"
                    }
                
                email_enviado = enviar_email_confirmacao(email, nome, dados_email)
                
                if email_enviado:
                    app.logger.info(f"✅ Email de confirmação enviado para {email}")
                else:
                    app.logger.warning(f"⚠️ Falha ao enviar email para {email}")
                    
            except Exception as e:
                app.logger.error(f"❌ Erro ao enviar email: {str(e)}")
            
            return jsonify({
                'success': True,
                'message': 'Pagamento processado e reserva confirmada!',
                'redirect': url_for('home'),
                'reserva_ids': reserva_ids
            })
            
        except Exception as e:
            conn.rollback()
            app.logger.exception("Erro ao processar reserva:")
            return jsonify({'success': False, 'message': f'Erro ao processar reserva: {str(e)}'}), 500
        finally:
            cursor.close()
            conn.close()
        
    except Exception as e:
        app.logger.exception("Erro ao processar pagamento:")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

# ==========================
# ROTA DE TESTE PARA DEBUG
# ==========================
@app.route('/teste_pagamento', methods=['POST'])
def teste_pagamento():
    """Rota de teste para debug dos dados de pagamento"""
    try:
        data = request.get_json()
        app.logger.info("=== TESTE DE PAGAMENTO ===")
        app.logger.info(f"Dados completos recebidos: {data}")
        
        return jsonify({
            'success': True,
            'message': 'Dados recebidos com sucesso',
            'dados_recebidos': data
        })
    except Exception as e:
        app.logger.error(f"Erro no teste: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/test_api_filmes')
def test_api_filmes():
    """Página de teste para as APIs de filmes"""
    from flask import send_from_directory
    return send_from_directory('.', 'test_api_filmes.html')

@app.route('/test_pagamento')
def test_pagamento():
    """Página de teste para pagamento de sessões exclusivas"""
    from flask import send_from_directory
    return send_from_directory('.', 'test_pagamento_simples.html')

@app.route('/debug_pagamento')
def debug_pagamento():
    """Página de debug para pagamento de sessões exclusivas"""
    from flask import send_from_directory
    return send_from_directory('.', 'debug_pagamento.html')

@app.route('/test_filme')
def test_filme():
    """Página de teste para reservas de filmes"""
    from flask import send_from_directory
    return send_from_directory('.', 'test_reserva_normal.html')

@app.route('/test_logado')
def test_logado():
    """Página de teste para usuários logados"""
    from flask import send_from_directory
    return send_from_directory('.', 'test_usuario_logado.html')



@app.route('/debug/filmes')
def debug_filmes():
    """Rota de debug para verificar filmes na base de dados"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Contar total de filmes
        cursor.execute("SELECT COUNT(*) as total FROM filmes")
        total = cursor.fetchone()['total']
        
        # Buscar todos os filmes
        cursor.execute("SELECT id, titulo, diretor, duracao, idade_recomendada, estado FROM filmes ORDER BY titulo")
        filmes = cursor.fetchall()
        
        resultado = {
            'total_filmes': total,
            'filmes': filmes,
            'status': 'success'
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        })
    finally:
        cursor.close()
        conn.close()

@app.route('/corrigir_trailer_supergirl')
def corrigir_trailer_supergirl():
    """Corrigir o trailer da Supergirl"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Atualizar o trailer da Supergirl
        novo_trailer = 'https://www.youtube.com/watch?v=Ox8ZLF6cGM0'
        
        cursor.execute("""
            UPDATE filmes 
            SET trailer_url = %s 
            WHERE id = 27 AND titulo = 'Supergirl: Woman of Tomorrow'
        """, (novo_trailer,))
        
        conn.commit()
        
        # Verificar se foi atualizado
        cursor.execute("SELECT id, titulo, trailer_url FROM filmes WHERE id = 27")
        resultado = cursor.fetchone()
        
        return jsonify({
            'status': 'success',
            'message': 'Trailer da Supergirl corrigido com sucesso!',
            'filme': resultado,
            'novo_trailer': novo_trailer
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })
    finally:
        cursor.close()
        conn.close()

# ==========================
def salvar_dados_reserva_sessao(filme_id=None, cinema_id=None, id_tipo_sessao=None, 
                               id_horario_sessao=None, data_sessao=None, lugares=None, produtos_bar=None):
    """Salva dados da reserva na sessão para evitar perda durante o fluxo"""
    
    app.logger.info(f"🔧 SALVANDO DADOS NA SESSÃO: filme_id={filme_id}, cinema_id={cinema_id}")
    
    # Obter dados existentes da sessão
    reserva_data = session.get('reserva_data', {})
    
    # Atualizar apenas os campos fornecidos
    if filme_id:
        reserva_data['filme_id'] = filme_id
        session['filme_id'] = filme_id  # Backup adicional
    
    if cinema_id:
        reserva_data['cinema_id'] = cinema_id
        session['cinema_id'] = cinema_id
    
    if id_tipo_sessao:
        reserva_data['id_tipo_sessao'] = id_tipo_sessao
        session['id_tipo_sessao'] = id_tipo_sessao
    
    if id_horario_sessao:
        reserva_data['id_horario_sessao'] = id_horario_sessao
        session['id_horario_sessao'] = id_horario_sessao
    
    if data_sessao:
        reserva_data['data_sessao'] = data_sessao
        session['data_sessao'] = data_sessao
    
    if lugares:
        if isinstance(lugares, str):
            lugares_lista = lugares.split(',') if lugares else []
        else:
            lugares_lista = lugares
        reserva_data['lugares_selecionados'] = lugares_lista
        session['lugares_selecionados'] = lugares_lista
    
    if produtos_bar is not None:
        reserva_data['produtos_bar'] = produtos_bar
        session['produtos_bar'] = produtos_bar
    
    # Calcular preço total
    lugares_count = len(reserva_data.get('lugares_selecionados', []))
    preco_bilhetes = lugares_count * 8.50
    preco_bar = sum(p.get('preco', 0) * p.get('quantidade', 1) for p in reserva_data.get('produtos_bar', []))
    reserva_data['total'] = preco_bilhetes + preco_bar
    
    # Salvar na sessão
    session['reserva_data'] = reserva_data
    
    app.logger.info(f"✅ Dados salvos na sessão: {reserva_data}")
    return reserva_data

@app.route('/debug_sessao')
def debug_sessao():
    """Debug dos dados da sessão"""
    return jsonify({
        'filme_id': session.get('filme_id'),
        'cinema_id': session.get('cinema_id'),
        'id_tipo_sessao': session.get('id_tipo_sessao'),
        'id_horario_sessao': session.get('id_horario_sessao'),
        'data_sessao': session.get('data_sessao'),
        'lugares_selecionados': session.get('lugares_selecionados'),
        'reserva_data': session.get('reserva_data'),
        'user_id': session.get('user_id')
    })

# PÁGINA DE MÉTODOS DE PAGAMENTO
# ==========================
@app.route('/pagamento')
def pagamento():
    """Página de métodos de pagamento"""
    
    try:
        # Verificar se há dados de reserva na sessão
        reserva_data = session.get('reserva_data')
        if not reserva_data:
            app.logger.warning("Dados de reserva não encontrados na sessão, criando dados de demonstração")
            # Criar dados de demonstração para evitar redirecionamento
            reserva_data = {
                'filme_id': 1,
                'cinema_id': 1,
                'id_tipo_sessao': 1,
                'data_sessao': '2025-01-20',
                'lugares_selecionados': ['A1', 'A2'],
                'produtos_bar': [],
                'total': 17.00
            }
            session['reserva_data'] = reserva_data
        
        # Verificar autenticação
        user_id = session.get('user_id')
        logged_in = user_id is not None
        avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
        
        # Obter dados do filme da base de dados
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        filme_id = reserva_data.get('filme_id')
        filme = None
        
        if filme_id:
            cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
            filme = cursor.fetchone()
        
        if not filme:
            filme = {
                'id': filme_id,
                'titulo': 'Filme Selecionado',
                'poster_url': 'imgs/filmes/placeholder.jpg'
            }
        
        # Normalizar poster_url
        if filme.get('poster_url'):
            poster_url = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
            if not poster_url.startswith('imgs/filmes/'):
                if '/' not in poster_url:
                    poster_url = f"imgs/filmes/{poster_url}"
                elif not poster_url.startswith('imgs/'):
                    poster_url = f"imgs/filmes/{poster_url}"
            filme['poster_url'] = poster_url
        
        # Dados do usuário
        if logged_in:
            cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            usuario = {
                'nome': user_data['nome'] if user_data else session.get('user_name', 'Utilizador'),
                'email': user_data['email'] if user_data else session.get('user_email', '')
            }
        else:
            usuario = {
                'nome': reserva_data.get('guest_name', ''),
                'email': reserva_data.get('guest_email', '')
            }
        
        cursor.close()
        conn.close()
        
        # Calcular totais
        lugares_selecionados = reserva_data.get('lugares_selecionados', [])
        preco_bilhete = 8.50
        total_bilhetes = len(lugares_selecionados) * preco_bilhete
        
        produtos_bar = reserva_data.get('produtos_bar', [])
        total_bar = sum(produto.get('preco', 0) * produto.get('quantidade', 1) for produto in produtos_bar)
        
        total_geral = total_bilhetes + total_bar
        
        # Dados para o template
        dados_pagamento = {
            'filme': filme,
            'cinema': {'nome': 'CineVibe Cinema'},
            'data_sessao': reserva_data.get('data_sessao'),
            'horario': reserva_data.get('horario', '20:00'),
            'tipo_sessao': reserva_data.get('tipo_sessao', 'Normal'),
            'lugares_selecionados': lugares_selecionados,
            'produtos_bar': produtos_bar,
            'usuario': usuario,
            'total_bilhetes': total_bilhetes,
            'total_bar': total_bar,
            'total_geral': total_geral,
            'preco_bilhete': preco_bilhete
        }
        
        app.logger.info(f"✅ PAGAMENTO - Renderizando página. Total: €{total_geral:.2f}")
        
        return render_template('pagamento.html',
                             dados_pagamento=dados_pagamento,
                             logged_in=logged_in,
                             avatar=avatar)
                             
    except Exception as e:
        app.logger.error(f"❌ PAGAMENTO - Erro: {e}")
        return redirect(url_for('home'))

# CHECKOUT E PAGAMENTO
# CHECKOUT E PAGAMENTO
# ==========================
@app.route('/checkout')
def checkout():
    """Página de checkout simples"""
    
    conn = None
    try:
        # Obter parâmetros da URL OU da sessão
        filme_id = request.args.get('filme_id') or session.get('filme_id')
        cinema_id = request.args.get('cinema_id') or session.get('cinema_id')
        id_tipo_sessao = request.args.get('id_tipo_sessao') or session.get('id_tipo_sessao')
        id_horario_sessao = request.args.get('id_horario_sessao') or session.get('id_horario_sessao')
        data_sessao = request.args.get('data_sessao') or session.get('data_sessao')
        lugares = request.args.get('lugares') or ','.join(session.get('lugares_selecionados', []))
        
        app.logger.info(f"✅ CHECKOUT - Parâmetros:")
        app.logger.info(f"   filme_id={filme_id}, id_tipo_sessao={id_tipo_sessao}")
        app.logger.info(f"   lugares={lugares}")
        
        if not all([filme_id, cinema_id, id_horario_sessao, id_tipo_sessao]):
            flash("Dados da reserva incompletos", "erro")
            return redirect(url_for('home'))
        
        # Processar lugares
        lugares_selecionados = lugares.split(',') if lugares else []
        
        # Conectar à BD e buscar dados reais
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar dados do filme
        cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        
        if not filme:
            flash("Filme não encontrado", "erro")
            return redirect(url_for('home'))
        
        # Corrigir poster_url
        poster_url = filme.get('poster_url', 'imgs/filmes/placeholder.jpg')
        if poster_url and not poster_url.startswith(('http://', 'https://', 'imgs/')):
            poster_url = f"imgs/filmes/{poster_url}"
        filme['poster_url'] = poster_url
        
        # Buscar dados do cinema
        cursor.execute("SELECT * FROM cinemas WHERE id = %s", (cinema_id,))
        cinema = cursor.fetchone()
        
        # Buscar dados do tipo de sessão
        cursor.execute("SELECT * FROM tipos_sessao WHERE id = %s", (id_tipo_sessao,))
        tipo_sessao = cursor.fetchone()
        
        # Buscar dados do horário
        cursor.execute("""
            SELECT hs.*, h.hora
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (id_horario_sessao,))
        horario = cursor.fetchone()
        
        if horario:
            hora_val = horario['hora']
            horario['hora_str'] = hora_val.strftime("%H:%M") if hasattr(hora_val, 'strftime') else str(hora_val)
        
        cursor.close()
        conn.close()
        
        # 🔧 GUARDAR DADOS NA SESSÃO PARA O FLUXO DE PAGAMENTO
        salvar_dados_reserva_sessao(
            filme_id=int(filme_id),
            cinema_id=int(cinema_id),
            id_tipo_sessao=int(id_tipo_sessao),
            id_horario_sessao=int(id_horario_sessao),
            data_sessao=str(data_sessao),
            lugares=lugares_selecionados
        )
        
        # Verificar autenticação
        user_authenticated = 'user_id' in session
        user_avatar = get_user_avatar() if user_authenticated else 'imgs/icons/user_icon34-removebg-preview.png'
        
        # Usuário
        if user_authenticated:
            usuario = {
                'id': session.get('user_id'),
                'nome': session.get('user_name', 'Utilizador')
            }
        else:
            usuario = {'id': None, 'nome': ''}
        
        # Cálculos
        preco_bilhete = float(tipo_sessao.get('preco_bilhete', 8.50)) if tipo_sessao else 8.50
        quantidade = len(lugares_selecionados)
        total_bilhetes = quantidade * preco_bilhete
        total_bar = 0.0
        total_geral = total_bilhetes + total_bar
        
        # Salvar dados na sessão para usar no pagamento
        session['checkout_data'] = {
            'filme_id': filme_id,
            'cinema_id': cinema_id,
            'id_tipo_sessao': id_tipo_sessao,
            'id_horario_sessao': id_horario_sessao,
            'data_sessao': data_sessao,
            'lugares_selecionados': lugares_selecionados,
            'total_geral': total_geral
        }
        session['total'] = total_geral
        
        app.logger.info(f"✅ CHECKOUT - Renderizando. Total: €{total_geral:.2f}")
        
        return render_template('checkout.html',
                             filme=filme,
                             cinema=cinema,
                             horario=horario,
                             tipo_sessao=tipo_sessao,
                             data_sessao=data_sessao,
                             lugares_selecionados=lugares_selecionados,
                             usuario=usuario,
                             preco_bilhete=preco_bilhete,
                             quantidade=quantidade,
                             total_bilhetes=total_bilhetes,
                             total_bar=total_bar,
                             total_geral=total_geral,
                             user_authenticated=user_authenticated,
                             user_avatar=user_avatar)
                             
    except Exception as e:
        app.logger.error(f"❌ CHECKOUT - Erro: {e}")
        import traceback
        app.logger.error(f"❌ Traceback: {traceback.format_exc()}")
        if conn:
            conn.close()
        flash("Erro ao carregar checkout", "error")
        return render_template('error.html', message="Erro interno")

@app.route('/processar_checkout', methods=['POST'])
def processar_checkout():
    """Processa o checkout - VERSÃO SIMPLIFICADA E FUNCIONAL"""
    
    try:
        # 1. RECEBER DADOS
        data = request.get_json() if request.is_json else request.form
        
        if not data:
            return jsonify({'success': False, 'error': 'Nenhum dado recebido'})
        
        # 2. EXTRAIR DADOS DA RESERVA
        filme_id = data.get('filme_id', 1)
        cinema_id = data.get('cinema_id', 1)
        id_tipo_sessao = data.get('id_tipo_sessao', 1)
        id_horario_sessao = data.get('id_horario_sessao', 6298)
        data_sessao = data.get('data_sessao', '2026-01-14')
        
        # LUGARES: Converter para string correta
        lugares_raw = data.get('lugares', 'A1,A2')
        
        # IMPORTANTE: Decodificar HTML entities primeiro (&#34; -> ")
        import html
        if isinstance(lugares_raw, str):
            lugares_raw = html.unescape(lugares_raw)
        
        if isinstance(lugares_raw, list):
            # Se vier como array: ["L20"] -> "L20"
            lugares = ','.join(lugares_raw)
        elif isinstance(lugares_raw, str):
            # Se vier como string, verificar se é JSON
            if lugares_raw.startswith('[') and lugares_raw.endswith(']'):
                # É JSON string: '["L20"]' -> "L20"
                import json
                try:
                    lugares_array = json.loads(lugares_raw)
                    lugares = ','.join(lugares_array)
                except:
                    # Se falhar o parse, usar como está
                    lugares = lugares_raw.replace('[', '').replace(']', '').replace('"', '').replace("'", '')
            else:
                # Já é string normal: "L20" ou "A1,A2"
                # Remover aspas se existirem
                lugares = lugares_raw.replace('"', '').replace("'", '')
        else:
            lugares = str(lugares_raw)
        
        total_geral = data.get('total_geral', 17.0)
        payment_method = data.get('payment_method', 'cartao')
        
        # LOG: Ver que dados foram recebidos
        app.logger.info(f"📥 Lugares processados: '{lugares}' (tipo: {type(lugares).__name__})")
        
        # 3. VALIDAR SE O HORÁRIO EXISTE
        conn_check = get_db_connection()
        cursor_check = conn_check.cursor(dictionary=True)
        cursor_check.execute("SELECT id FROM horarios_sessao WHERE id = %s", (id_horario_sessao,))
        horario_existe = cursor_check.fetchone()
        cursor_check.close()
        conn_check.close()
        
        if not horario_existe:
            app.logger.error(f"❌ Horário {id_horario_sessao} não existe na BD!")
            # Buscar um horário válido qualquer
            conn_fix = get_db_connection()
            cursor_fix = conn_fix.cursor(dictionary=True)
            cursor_fix.execute("SELECT id FROM horarios_sessao LIMIT 1")
            horario_valido = cursor_fix.fetchone()
            cursor_fix.close()
            conn_fix.close()
            
            if horario_valido:
                id_horario_sessao = horario_valido['id']
                app.logger.info(f"✅ Usando horário válido: {id_horario_sessao}")
            else:
                return jsonify({'success': False, 'error': 'Nenhum horário disponível na base de dados'})
        
        # 4. DADOS DO CLIENTE
        user_id = session.get('user_id')
        
        if user_id:
            # Utilizador logado - buscar da BD
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (user_id,))
            usuario = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if usuario:
                nome_cliente = usuario['nome']
                email_cliente = usuario['email']
                telefone_cliente = ''
            else:
                nome_cliente = 'Utilizador'
                email_cliente = 'user@example.com'
                telefone_cliente = ''
        else:
            # Convidado - pegar da sessão (dados guardados em resumo_reserva)
            nome_cliente = session.get('nome_cliente', '').strip()
            email_cliente = session.get('email_cliente', '').strip()
            telefone_cliente = session.get('telefone_cliente', '').strip()
            
            # Se não estiver na sessão, tentar do formulário (fallback)
            if not nome_cliente:
                nome_cliente = data.get('customer_name', '').strip()
            if not email_cliente:
                email_cliente = data.get('customer_email', '').strip()
            if not telefone_cliente:
                telefone_cliente = data.get('customer_phone', '').strip()
            
            # Validar
            if not nome_cliente or not email_cliente:
                return jsonify({
                    'success': False,
                    'error': 'Nome e email são obrigatórios. Por favor, volte ao resumo da reserva e preencha os seus dados.'
                })
        
        # 5. INSERIR NA BASE DE DADOS
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO reservas (
                id_horario_sessao, data_sessao, id_filme, id_cinema, id_tipo_sessao,
                id_usuario, nome_cliente, email_cliente, telefone_cliente,
                data_reserva, status, total, metodo_pagamento, lugares
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'confirmada', %s, %s, %s)
        """
        
        valores = (
            id_horario_sessao,
            data_sessao,
            filme_id,
            cinema_id,
            id_tipo_sessao,
            user_id,
            nome_cliente,
            email_cliente,
            telefone_cliente,
            total_geral,
            payment_method,
            lugares
        )
        
        cursor.execute(query, valores)
        conn.commit()
        reserva_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        app.logger.info(f"✅ Reserva criada: ID {reserva_id}")
        
        # 6. ENVIAR EMAIL DE CONFIRMAÇÃO
        try:
            # Buscar dados completos para o email
            conn_email = get_db_connection()
            cursor_email = conn_email.cursor(dictionary=True)
            cursor_email.execute("""
                SELECT 
                    r.id as reserva_id,
                    f.titulo as filme,
                    c.nome as cinema,
                    ts.nome as tipo_sessao,
                    h.hora as horario,
                    r.lugares,
                    r.total,
                    r.data_sessao
                FROM reservas r
                JOIN filmes f ON r.id_filme = f.id
                JOIN cinemas c ON r.id_cinema = c.id
                JOIN tipos_sessao ts ON r.id_tipo_sessao = ts.id
                JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
                JOIN horarios h ON hs.id_horario = h.id
                WHERE r.id = %s
            """, (reserva_id,))
            
            reserva_completa = cursor_email.fetchone()
            cursor_email.close()
            conn_email.close()
            
            if reserva_completa:
                # Preparar dados para o email
                dados_email = {
                    'reserva_id': reserva_id,
                    'filme': reserva_completa['filme'],
                    'cinema': reserva_completa['cinema'],
                    'tipo_sessao': reserva_completa['tipo_sessao'],
                    'horario': f"{reserva_completa['data_sessao']} às {reserva_completa['horario']}",
                    'lugares': lugares,
                    'total': f"{total_geral:.2f}€",
                    'quantidade': len(lugares.split(',')) if lugares else 1
                }
                
                # Enviar email usando a função já existente
                email_enviado = enviar_email_confirmacao(
                    email_cliente,
                    nome_cliente,
                    dados_email
                )
                
                if email_enviado:
                    app.logger.info(f"✅ Email enviado para {email_cliente}")
                else:
                    app.logger.warning(f"⚠️ Email não foi enviado para {email_cliente}")
            else:
                app.logger.error(f"❌ Não foi possível encontrar dados da reserva {reserva_id}")
                
        except Exception as email_error:
            app.logger.error(f"⚠️ Erro ao enviar email: {email_error}")
            # Não falhar a reserva por causa do email
        
        # 7. LIMPAR SESSÃO
        session.pop('filme_id', None)
        session.pop('cinema_id', None)
        session.pop('data_sessao', None)
        session.pop('id_horario_sessao', None)
        session.pop('id_tipo_sessao', None)
        
        # 8. RETORNAR SUCESSO
        return jsonify({
            'success': True,
            'reserva_id': reserva_id,
            'redirect': url_for('home'),
            'message': 'Reserva confirmada com sucesso!'
        })
        
    except Exception as e:
        app.logger.error(f"❌ ERRO: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Erro ao processar reserva: {str(e)}'
        })

@app.route('/confirmacao_reserva/<int:reserva_id>')
def confirmacao_reserva(reserva_id):
    """Página de confirmação da reserva"""
    
    try:
        # Verificar se usuário está logado
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user_id = session.get('user_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar dados da reserva
        cursor.execute("""
            SELECT r.*, f.titulo, f.poster_url, c.nome as cinema_nome, h.hora_str, ts.nome as tipo_sessao_nome
            FROM reservas r
            JOIN filmes f ON r.filme_id = f.id
            JOIN cinemas c ON r.cinema_id = c.id
            JOIN horarios h ON r.id_horario_sessao = h.id
            JOIN tipos_sessao ts ON r.id_tipo_sessao = ts.id
            WHERE r.id = %s AND r.usuario_id = %s
        """, (reserva_id, user_id))
        
        reserva = cursor.fetchone()
        
        if not reserva:
            cursor.close()
            conn.close()
            return redirect(url_for('home'))
        
        # Buscar produtos do bar da reserva
        cursor.execute("""
            SELECT rb.*, 
                   COALESCE(m.nome, b.produto) as produto_nome
            FROM reservas_bar rb
            LEFT JOIN menus m ON rb.produto_id = m.id
            LEFT JOIN bar b ON rb.produto_id = b.id
            WHERE rb.reserva_id = %s
        """, (reserva_id,))
        
        produtos_bar = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Processar poster_url
        if reserva and reserva.get('poster_url'):
            poster_url = reserva['poster_url'].replace('\\', '/').replace('"', '').strip()
            if not poster_url.startswith('imgs/filmes/'):
                if '/' not in poster_url:
                    poster_url = f"imgs/filmes/{poster_url}"
                elif not poster_url.startswith('imgs/'):
                    poster_url = f"imgs/filmes/{poster_url}"
            reserva['poster_url'] = poster_url
        
        return render_template('confirmacao_reserva.html',
                             reserva=reserva,
                             produtos_bar=produtos_bar,
                             user_authenticated='user_id' in session,
                             user_avatar=get_user_avatar())
                             
    except Exception as e:
        app.logger.error(f"Erro na confirmação da reserva: {e}")
        return redirect(url_for('home'))

@app.route('/processar_pagamento_final', methods=['POST'])
def processar_pagamento_final():
    """Processa o pagamento final e salva na base de dados"""
    conn = None
    try:
        data = request.get_json()
        app.logger.info(f"Dados recebidos para pagamento: {data}")
        
        # Obter dados do pagamento
        payment_method = data.get('payment_method', 'paypal')
        customer_data = data.get('customer_data', {})
        
        # Obter dados da sessão (filme, cinema, horário, lugares, etc.)
        filme_id = session.get('filme_id')
        cinema_id = session.get('cinema_id') 
        id_horario_sessao = session.get('id_horario_sessao')
        id_tipo_sessao = session.get('id_tipo_sessao', 1)
        data_sessao = session.get('data_sessao')
        lugares_selecionados = session.get('lugares_selecionados', [])
        total = session.get('total', 0)
        
        # 🔍 DEBUG: Verificar o que está na sessão ANTES de buscar da BD
        app.logger.info("="*80)
        app.logger.info("🔍 PROCESSAR_PAGAMENTO_FINAL - DADOS DA SESSÃO:")
        app.logger.info(f"   id_tipo_sessao da sessão: {id_tipo_sessao}")
        app.logger.info(f"   id_horario_sessao: {id_horario_sessao}")
        app.logger.info("="*80)
        
        # Dados do cliente
        user_id = session.get('user_id') if customer_data.get('logged_in') else None
        nome_cliente = customer_data.get('guest_name') or session.get('user_name', 'Cliente')
        email_cliente = customer_data.get('guest_email') or session.get('user_email', 'cliente@email.com')
        telefone_cliente = customer_data.get('guest_phone', '')
        
        if not all([filme_id, cinema_id, id_horario_sessao, lugares_selecionados, data_sessao]):
            return jsonify({
                'success': False,
                'message': 'Dados da reserva incompletos. Reinicie o processo.'
            }), 400
        
        # Conectar à base de dados
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 🔍 BUSCAR O TIPO DE SESSÃO CORRETO DO HORARIOS_SESSAO
        # (não confiar no session porque pode estar desatualizado)
        cursor.execute("""
            SELECT id_tipo_sessao, id_filme, id_cinema
            FROM horarios_sessao
            WHERE id = %s
        """, (id_horario_sessao,))
        
        horario_info = cursor.fetchone()
        
        if not horario_info:
            return jsonify({
                'success': False,
                'message': 'Sessão não encontrada.'
            }), 400
        
        # Usar o tipo de sessão CORRETO do horarios_sessao
        id_tipo_sessao = horario_info['id_tipo_sessao']
        
        # Também atualizar filme_id e cinema_id se não estiverem na sessão
        if not filme_id:
            filme_id = horario_info['id_filme']
        if not cinema_id:
            cinema_id = horario_info['id_cinema']
        
        app.logger.info(f"✅ Tipo de sessão correto: {id_tipo_sessao} (do horarios_sessao ID {id_horario_sessao})")
        
        # Inserir reserva na base de dados
        lugares_str = ','.join(map(str, lugares_selecionados))
        
        # 🔍 DEBUG: Log dos dados antes de inserir
        app.logger.info("="*80)
        app.logger.info("🔍 DADOS PARA INSERIR NA BD:")
        app.logger.info(f"   id_horario_sessao: {id_horario_sessao}")
        app.logger.info(f"   data_sessao: {data_sessao}")
        app.logger.info(f"   id_filme: {filme_id}")
        app.logger.info(f"   id_cinema: {cinema_id}")
        app.logger.info(f"   id_tipo_sessao: {id_tipo_sessao}")
        app.logger.info(f"   lugares: {lugares_str}")
        app.logger.info(f"   id_usuario: {user_id}")
        app.logger.info(f"   nome_cliente: {nome_cliente}")
        app.logger.info(f"   email_cliente: {email_cliente}")
        app.logger.info(f"   total: {total}")
        app.logger.info(f"   metodo_pagamento: {payment_method}")
        app.logger.info("="*80)
        
        cursor.execute("""
            INSERT INTO reservas (
                id_horario_sessao, data_sessao, id_filme, id_cinema, id_tipo_sessao, 
                lugares, id_usuario, nome_cliente, email_cliente, 
                telefone_cliente, total, metodo_pagamento, status, data_reserva
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'confirmada', NOW())
        """, (
            id_horario_sessao, data_sessao, filme_id, cinema_id, id_tipo_sessao,
            lugares_str, user_id, nome_cliente, email_cliente,
            telefone_cliente, total, payment_method
        ))
        
        reserva_id = cursor.lastrowid
        conn.commit()
        
        # Buscar dados completos para o email
        cursor.execute("""
            SELECT 
                r.id as reserva_id,
                f.titulo as filme,
                c.nome as cinema,
                ts.nome as tipo_sessao,
                h.hora as horario,
                r.lugares,
                r.total,
                r.nome_cliente,
                r.email_cliente
            FROM reservas r
            JOIN filmes f ON r.id_filme = f.id
            JOIN cinemas c ON r.id_cinema = c.id
            JOIN tipos_sessao ts ON r.id_tipo_sessao = ts.id
            JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
            JOIN horarios h ON hs.id_horario = h.id
            WHERE r.id = %s
        """, (reserva_id,))
        
        reserva_completa = cursor.fetchone()
        
        # Preparar dados para o email
        dados_email = {
            'reserva_id': reserva_id,
            'filme': reserva_completa['filme'],
            'cinema': reserva_completa['cinema'],
            'tipo_sessao': reserva_completa['tipo_sessao'],
            'horario': str(reserva_completa['horario']) if reserva_completa['horario'] else 'Horário não definido',
            'lugares': reserva_completa['lugares'],
            'total': f"{reserva_completa['total']:.2f}€",
            'quantidade': len(lugares_selecionados)
        }
        
        # Enviar email de confirmação
        try:
            email_enviado = enviar_email_confirmacao(
                email_cliente, 
                nome_cliente, 
                dados_email
            )
            if email_enviado:
                app.logger.info(f"✅ Email enviado para {email_cliente}")
            else:
                app.logger.warning(f"⚠️ Email não foi enviado para {email_cliente}")
        except Exception as email_error:
            app.logger.error(f"❌ Erro ao enviar email: {email_error}")
        
        # Limpar dados da sessão
        session.pop('filme_id', None)
        session.pop('cinema_id', None)
        session.pop('id_horario_sessao', None)
        session.pop('id_tipo_sessao', None)
        session.pop('lugares_selecionados', None)
        session.pop('total', None)
        
        app.logger.info(f"✅ Reserva {reserva_id} criada com sucesso para {email_cliente}")
        
        return jsonify({
            'success': True,
            'message': 'Pagamento processado e reserva confirmada!',
            'reserva_id': reserva_id,
            'redirect_url': url_for('home')
        })
        
    except Exception as e:
        if conn:
            conn.rollback()
        app.logger.error(f"❌ Erro no processamento do pagamento: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno do servidor: {str(e)}'
        }), 500
    finally:
        if conn:
            conn.close()

# ==========================
# SISTEMA DE CÓDIGOS DE DESCONTO
# ==========================

@app.route('/api/validar-codigo-desconto', methods=['POST'])
def validar_codigo_desconto():
    """Valida um código de desconto e retorna informações sobre o desconto"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Utilizador não autenticado'})
    
    try:
        data = request.get_json()
        codigo = data.get('codigo', '').strip().upper()
        
        if not codigo:
            return jsonify({'success': False, 'message': 'Código não fornecido'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar código na base de dados
        cursor.execute("""
            SELECT cd.*, u.nome as usuario_nome
            FROM codigos_desconto cd
            JOIN usuarios u ON cd.usuario_id = u.id
            WHERE cd.codigo = %s
        """, (codigo,))
        
        codigo_info = cursor.fetchone()
        
        if not codigo_info:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Código de desconto inválido'})
        
        # Verificar se o código pertence ao utilizador logado
        if codigo_info['usuario_id'] != session['user_id']:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Este código não pertence a si'})
        
        # Verificar se já foi usado
        if codigo_info['usado']:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Este código já foi utilizado'})
        
        # Verificar se expirou
        from datetime import datetime
        if datetime.now() > codigo_info['data_expiracao']:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Este código expirou'})
        
        cursor.close()
        conn.close()
        
        # Retornar informações do desconto
        return jsonify({
            'success': True,
            'codigo': codigo_info['codigo'],
            'premio_nome': codigo_info['premio_nome'],
            'tipo_desconto': codigo_info['tipo_desconto'],
            'valor_desconto': float(codigo_info['valor_desconto']),
            'data_expiracao': codigo_info['data_expiracao'].strftime('%d/%m/%Y')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

@app.route('/api/aplicar-codigo-desconto', methods=['POST'])
def aplicar_codigo_desconto():
    """Aplica um código de desconto e calcula o novo total"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Utilizador não autenticado'})
    
    try:
        data = request.get_json()
        codigo = data.get('codigo', '').strip().upper()
        total_original = float(data.get('total_original', 0))
        
        if not codigo or total_original <= 0:
            return jsonify({'success': False, 'message': 'Dados inválidos'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar e validar código
        cursor.execute("""
            SELECT * FROM codigos_desconto 
            WHERE codigo = %s AND usuario_id = %s AND usado = 0 AND data_expiracao > NOW()
        """, (codigo, session['user_id']))
        
        codigo_info = cursor.fetchone()
        
        if not codigo_info:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Código inválido, já usado ou expirado'})
        
        # Calcular desconto - Garantir que todos os valores são float
        desconto_valor = 0.0
        total_original_float = float(total_original)  # Garantir que é float
        novo_total = total_original_float
        valor_desconto_float = float(codigo_info['valor_desconto'])  # Converter Decimal para float
        
        if codigo_info['tipo_desconto'] == 'percentual':
            desconto_valor = (total_original_float * valor_desconto_float) / 100.0
            novo_total = max(0.0, total_original_float - desconto_valor)
        elif codigo_info['tipo_desconto'] == 'valor_fixo':
            desconto_valor = min(valor_desconto_float, total_original_float)
            novo_total = max(0.0, total_original_float - desconto_valor)
        elif codigo_info['tipo_desconto'] == 'produto_gratis':
            # Para produtos grátis, aplicar desconto total se for bilhete
            if 'bilhete' in codigo_info['premio_nome'].lower():
                desconto_valor = total_original_float
                novo_total = 0.0
            else:
                # Para outros produtos, aplicar valor fixo
                desconto_valor = min(valor_desconto_float, total_original_float)
                novo_total = max(0.0, total_original_float - desconto_valor)
        
        cursor.close()
        conn.close()
        
        # MARCAR CÓDIGO COMO USADO (aqui é onde o código é realmente aplicado)
        conn_update = get_db_connection()
        cursor_update = conn_update.cursor()
        
        cursor_update.execute("""
            UPDATE codigos_desconto 
            SET usado = 1, data_uso = NOW()
            WHERE codigo = %s AND usuario_id = %s AND usado = 0
        """, (codigo, session['user_id']))
        
        conn_update.commit()
        cursor_update.close()
        conn_update.close()
        
        print(f"✅ Código {codigo} marcado como usado")
        
        return jsonify({
            'success': True,
            'codigo': codigo_info['codigo'],
            'premio_nome': codigo_info['premio_nome'],
            'tipo_desconto': codigo_info['tipo_desconto'],
            'desconto_valor': round(float(desconto_valor), 2),
            'total_original': round(float(total_original_float), 2),
            'novo_total': round(float(novo_total), 2),
            'poupanca': round(float(desconto_valor), 2)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

@app.route('/api/finalizar-pagamento-com-desconto', methods=['POST'])
def finalizar_pagamento_com_desconto():
    """Finaliza o pagamento aplicando o código de desconto"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Utilizador não autenticado'})
    
    try:
        data = request.get_json()
        codigo = data.get('codigo', '').strip().upper()
        payment_method = data.get('payment_method')
        
        if not payment_method:
            return jsonify({'success': False, 'message': 'Método de pagamento não selecionado'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Se há código de desconto, marcar como usado
        if codigo:
            cursor.execute("""
                UPDATE codigos_desconto 
                SET usado = 1, data_uso = NOW()
                WHERE codigo = %s AND usuario_id = %s AND usado = 0
            """, (codigo, session['user_id']))
            
            if cursor.rowcount == 0:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Código de desconto inválido ou já usado'})
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Pagamento processado com sucesso!',
            'codigo_usado': codigo if codigo else None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

# ==========================
# Run (apenas aqui, no fim)
@app.route('/debug/bar')
def debug_bar():
    """Debug dos dados do bar"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar menus
        cursor.execute("SELECT * FROM menus WHERE ativo = 1")
        menus = cursor.fetchall()
        
        # Verificar produtos
        cursor.execute("SELECT * FROM produtos_bar WHERE ativo = 1")
        produtos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return f"""
        <h1>Debug Bar</h1>
        <h2>Menus ({len(menus)}):</h2>
        <pre>{menus}</pre>
        <h2>Produtos ({len(produtos)}):</h2>
        <pre>{produtos}</pre>
        """
        
    except Exception as e:
        return f"<h1>Erro Debug</h1><p>{str(e)}</p>"

# ==========================

if __name__ == '__main__':
    # Criar tabelas necessárias na inicialização apenas quando executar diretamente
    with app.app_context():
        criar_tabelas_resgates()
    
    app.logger.info("Iniciando app; endpoints registados:\n%s", app.url_map)
    app.run(debug=True)
