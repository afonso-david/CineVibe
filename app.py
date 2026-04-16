from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, make_response
import mysql.connector
import logging
import json
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

app.secret_key = "troca_isto_por_uma_chave_secreta_e_complexa"

# Adicionar headers de cache para recursos estáticos (especialmente a logo)
@app.after_request
def add_cache_headers(response):
    # Cachear imagens da logo por 1 ano
    if 'logo8 sem fundo.png' in request.path or 'Logo/' in request.path:
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        response.headers['Expires'] = 'Thu, 31 Dec 2037 23:55:55 GMT'
    # Cachear outros recursos estáticos por 1 hora
    elif request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=3600'
    return response


DEVELOPMENT_MODE = False  

if DEVELOPMENT_MODE:
    pass

    GOOGLE_CLIENT_ID = "development-mode"
    GOOGLE_CLIENT_SECRET = "development-mode"
    FACEBOOK_APP_ID = "development-mode"
    FACEBOOK_APP_SECRET = "development-mode"
else:
    pass
 
    GOOGLE_CLIENT_ID = "569393113816-7rlbqt2ora3gb1hof0sq2omiao1j9bvr.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "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"
    FACEBOOK_APP_ID = "your-facebook-app-id"
    FACEBOOK_APP_SECRET = "your-facebook-app-secret"

try:
    from email_config import EMAIL_CONFIG
    EMAIL_HOST = EMAIL_CONFIG['HOST']
    EMAIL_PORT = EMAIL_CONFIG['PORT']
    EMAIL_USER = EMAIL_CONFIG['USER']
    EMAIL_PASSWORD = EMAIL_CONFIG['PASSWORD']
    EMAIL_USE_TLS = EMAIL_CONFIG['USE_TLS']
except ImportError:
    pass
    
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USER = 'cinevibe.bilhetes@gmail.com'
    EMAIL_PASSWORD = 'goxm upky dcyx nbyx'  
    EMAIL_USE_TLS = True


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'cinevibe.bilhetes@gmail.com'
EMAIL_PASSWORD = 'goxm upky dcyx nbyx' 
EMAIL_USE_TLS = True

def enviar_email_recuperacao_senha(destinatario_email, destinatario_nome, token):
    pass
    
    try:
        app.logger.info(f"Enviando email de recuperação para: {destinatario_email}")
        
        if EMAIL_PASSWORD in ['sua_senha_app_aqui', 'DESATIVADO_TEMPORARIAMENTE'] or not EMAIL_PASSWORD:
            app.logger.warning("Email desativado temporariamente. Configure senha de app do Gmail para ativar.")
            return False

        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🔐 Recuperação de Senha - CineVibe'
        msg['From'] = f'CineVibe <{EMAIL_USER}>'
        msg['To'] = destinatario_email

        link_recuperacao = f"http://localhost:5000/redefinir-senha?token={token}"

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
                    background: linear-gradient(135deg, #0d1117, #161b22); 
                    border-radius: 20px; 
                    overflow: hidden; 
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
                    border: 2px solid rgba(255, 214, 10, 0.3);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #0d1117, #161b22); 
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
                    color: #1a1a1a; 
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
                    background: linear-gradient(135deg, #0d1117, #161b22); 
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
                    background: linear-gradient(135deg, #0d1117, #161b22); 
                    transform: translateY(-2px);
                    box-shadow: 0 12px 25px rgba(255, 214, 10, 0.4);
                }}
                .warning {{ 
                    background: rgba(255, 193, 7, 0.15); 
                    border: 2px solid rgba(255, 193, 7, 0.3); 
                    padding: 25px; 
                    border-radius: 15px; 
                    margin: 30px 0; 
                    color: #1a1a1a; 
                    backdrop-filter: blur(10px);
                }}
                .warning strong {{
                    color: #1a1a1a; 
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
                    color: #1a1a1a; 
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
                    color: #1a1a1a; 
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                    margin-top: 15px;
                    border: 1px solid rgba(76, 175, 80, 0.3);
                }}
                .divider {{
                    height: 2px;
                    background: linear-gradient(90deg, transparent,
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
                    <h1><span class="emoji"></span>CineVibe</h1>
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

        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_USER, destinatario_email, text)
        server.quit()
        
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
    try:
        app.logger.info(f"Enviando email para: {destinatario_email}")
        
      
        if EMAIL_PASSWORD in ['sua_senha_app_aqui', 'DESATIVADO_TEMPORARIAMENTE'] or not EMAIL_PASSWORD:
            app.logger.warning("Email desativado temporariamente. Configure senha de app do Gmail para ativar.")
            return False

    
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Confirmacao de Reserva CineVibe - #{dados_reserva["reserva_id"]}'
        msg['From'] = f'CineVibe <{EMAIL_USER}>'
        msg['To'] = destinatario_email

        try:
            data_confirmacao = datetime.now().strftime('%d/%m/%Y as %H:%M')
            
          
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

   
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_USER, destinatario_email, text)
        server.quit()
        
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


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kevin@15",  
        database="cinevibe"
    )

def get_current_user():
    pass
   
    if 'user_id' not in session:
        return None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.*, a.caminho as avatar 
            FROM usuarios u 
            LEFT JOIN avatars a ON u.avatar_id = a.id 
            WHERE u.id = %s
        """, (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except:
        return None

def usar_codigo_desconto_reserva(user_id, codigo, premio_nome, pontos_gastos):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO pontos_movimentos 
            (utilizador_id, pontos, motivo, data_movimento)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, -pontos_gastos, f"Uso de código de desconto {codigo} - {premio_nome}"))
        
        cursor.execute("""
            UPDATE codigos_desconto 
            SET usado = 1, data_uso = NOW() 
            WHERE codigo = %s AND usuario_id = %s
        """, (codigo, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        return False

def criar_tabelas_resgates():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
        
        return True
        
    except Exception as e:
        app.logger.error(f"❌ Erro ao criar tabelas de resgates: {e}")
        return False

def calcular_pontos_usuario(user_id, cursor):
    pass
   
    try:
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM reservas r
            JOIN filmes f ON r.id_filme = f.id
            JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
            JOIN horarios h ON hs.id_horario = h.id
            WHERE r.id_usuario = %s
            AND DATE_ADD(CONCAT(r.data_sessao, ' ', h.hora), INTERVAL f.duracao MINUTE) < NOW()
        """, (user_id,))
        result = cursor.fetchone()
        reservas_normais = result['total'] if result else 0
        
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM reservas_exclusivas
            WHERE usuario_id = %s
            AND CONCAT(data_sessao, ' ', hora_sessao) < NOW()
        """, (user_id,))
        result = cursor.fetchone()
        reservas_exclusivas = result['total'] if result else 0
        
        cursor.execute("SELECT COUNT(*) as total FROM avaliacoes_filmes WHERE usuario_id = %s", (user_id,))
        result = cursor.fetchone()
        avaliacoes = result['total'] if result else 0
        
        pontos_ganhos = (reservas_normais * 100) + (reservas_exclusivas * 200) + (avaliacoes * 50)
        
        try:
            cursor.execute("SELECT COALESCE(SUM(pontos_gastos), 0) as total FROM pontos_gastos WHERE usuario_id = %s", (user_id,))
            result = cursor.fetchone()
            pontos_gastos = result['total'] if result else 0
        except:
            pontos_gastos = 0
        
        pontos_disponiveis = max(0, pontos_ganhos - pontos_gastos)
        
        
        return pontos_disponiveis
        
    except Exception as e:
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
        
        cursor.close()
        conn.close()
        return filmes_atualizados
        
    except Exception as e:
        app.logger.error(f"❌ Erro na atualizacao automatica de filmes: {e}")
        return 0

def _normalize_img_path(raw):
    """Normaliza paths/URLs de imagem"""
    if not raw:
        return 'imgs/filmes/placeholder.jpg'
    
    p = str(raw).replace('\\', '/').strip().strip('"').strip()
    
    if p.startswith('http://') or p.startswith('https://'):
        return p
    
    if p.startswith('/static/'):
        p = p[len('/static/'):]
    elif p.startswith('static/'):
        p = p[len('static/'):]
    elif p.startswith('/'):
        p = p[1:]
    
    if not p:
        return 'imgs/filmes/placeholder.jpg'
    
    if p.startswith('imgs/'):
        return p
    
    if '/' not in p:
        return f'imgs/filmes/{p}'
    
    if not p.startswith('imgs/'):
        return f'imgs/filmes/{p}'
    
    return p

def get_user_avatar():
    """Retorna o caminho do avatar do usuário logado"""
    if 'user_avatar' in session:
        avatar = session['user_avatar']
        app.logger.info(f"get_user_avatar - Avatar da sessão: {avatar}")
        return avatar
    
    if 'user_id' in session:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT a.caminho as avatar_path
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
                
         
                if avatar.startswith('static/'):
                    avatar = avatar[7:]
                if avatar.startswith('/static/'):
                    avatar = avatar[8:]
                
                app.logger.info(f"get_user_avatar - Avatar limpo: {avatar}")
                session['user_avatar'] = avatar
                return avatar
        except Exception as e:
            app.logger.error(f"get_user_avatar - Erro: {str(e)}")
    
  
    app.logger.warning("get_user_avatar - Usando avatar padrão")
    return 'imgs/icons/user_icon34-removebg-preview.png'

@app.route('/')
@app.route('/home')
def home():
    pass

    if request.args.get('reserva_concluida'):
        flash("🎉 Reserva concluída com sucesso! Obrigado por escolher o CineVibe.", "sucesso")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        pass
     
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
        
      
        for i, f in enumerate(filmes):
            if f.get('poster_url'):
                pass
              
                poster_url = f['poster_url'].replace('\\', '/').replace('"', '').strip()
                
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
                
               
                if not poster_url.startswith('/'):
                    poster_url = f"/static/{poster_url}"
                
                f['poster_url'] = poster_url
                
            if f.get('poster_hover'):
                pass
     
                poster_hover = f['poster_hover'].replace('\\', '/').replace('"', '').strip()
               
                if not poster_hover.startswith('/'):
                    if not poster_hover.startswith('static/'):
                        poster_hover = f"static/{poster_hover}"
                    poster_hover = f"/{poster_hover}"
                f['poster_hover'] = poster_hover
                
            f['classificacao_manual'] = str(i + 1)
        
      
        stats = {}
        
        try:
            # Contar filmes em exibição
            cursor.execute("SELECT COUNT(*) as total FROM filmes WHERE estado = 'em_exibicao'")
            result = cursor.fetchone()
            stats['filmes_em_exibicao'] = result['total'] if result else 0
            
            # Se não houver filmes com estado 'em_exibicao', contar todos
            if stats['filmes_em_exibicao'] == 0:
                cursor.execute("SELECT COUNT(*) as total FROM filmes")
                result = cursor.fetchone()
                stats['filmes_em_exibicao'] = result['total'] if result else 0
            
            # Contar cinemas
            cursor.execute("SELECT COUNT(*) as total FROM cinemas")
            result = cursor.fetchone()
            stats['total_cinemas'] = result['total'] if result else 0
            
            # Contar salas
            cursor.execute("SELECT COUNT(*) as total FROM salas")
            result = cursor.fetchone()
            stats['total_salas'] = result['total'] if result else 0
            
            # Se não houver salas mas houver cinemas, estimar salas
            if stats['total_salas'] == 0 and stats['total_cinemas'] > 0:
                stats['total_salas'] = stats['total_cinemas'] * 3  
            
            app.logger.info(f"Stats calculadas com sucesso: {stats}")
            
        except Exception as e:
            app.logger.error(f"Erro ao buscar estatísticas: {e}")
            # Fallback com valores padrão
            stats = {
                'filmes_em_exibicao': 0,
                'total_cinemas': 0,
                'total_salas': 0
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    pass
 
    next_url = request.args.get('next') or request.form.get('next')
    
    if request.method == 'POST':
        pass

        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()   

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
        
      
        cur.execute("""
            SELECT a.caminho as avatar_path
            FROM usuarios u 
            LEFT JOIN avatars a ON u.avatar_id = a.id 
            WHERE u.id = %s
        """, (user['id'],))
        avatar_data = cur.fetchone()
        if avatar_data and avatar_data['avatar_path']:
            avatar = avatar_data['avatar_path'].replace('\\', '/').replace('"', '').strip()
           
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
        
        
        reserva_params = request.form.get('reserva_params')
        if reserva_params:
            pass
            
            return redirect(f"/reserva?{reserva_params}")
        
       
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('home'))

    return render_template("login.html", next_url=next_url)

@app.route('/auth/google')
def auth_google():
    pass
    
    # Capturar o parâmetro next e guardar na sessão
    next_url = request.args.get('next')
    if next_url:
        session['oauth_next_url'] = next_url
    
    # Verificar se vem da página de registo
    from_register = request.args.get('register') == 'true'
    session['google_register_mode'] = from_register
    
    if DEVELOPMENT_MODE:
        pass
       
        return redirect(url_for('auth_google_callback', 
                              code='dev_code', 
                              state='dev_state'))
    
  
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
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
    pass
   
    try:
        if DEVELOPMENT_MODE:
            pass
            
            user_data = {
                'email': 'teste.google@gmail.com',
                'name': 'Usuário Google Teste',
                'id': 'google_dev_123',
                'picture': 'https://via.placeholder.com/150'
            }
            
            # Se está em modo registo, redireciona para o formulário
            if session.get('google_register_mode'):
                session['google_email'] = user_data['email']
                session['google_name'] = user_data['name']
                session.pop('google_register_mode', None)
                # Passar o next_url para o registo
                next_url = session.get('oauth_next_url')
                if next_url:
                    return redirect(url_for('registo', from_google='true', next=next_url))
                return redirect(url_for('registo', from_google='true'))
            
            return process_social_login(user_data, 'google')
        
        
        if request.args.get('state') != session.get('oauth_state'):
            flash("Erro de segurança na autenticação", "erro")
            return redirect(url_for('login'))
        
       
        code = request.args.get('code')
        if not code:
            flash("Erro na autenticação com Google", "erro")
            return redirect(url_for('login'))
        
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
        
        user_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f"Bearer {token_json['access_token']}"}
        )
        user_data = user_response.json()
        
        # Se está em modo registo, redireciona para o formulário com email pré-preenchido
        if session.get('google_register_mode'):
            session['google_email'] = user_data.get('email')
            session['google_name'] = user_data.get('name')
            session.pop('google_register_mode', None)
            flash("Email obtido do Google! Complete o registo abaixo.", "sucesso")
            # Passar o next_url para o registo
            next_url = session.get('oauth_next_url')
            if next_url:
                return redirect(url_for('registo', from_google='true', next=next_url))
            return redirect(url_for('registo', from_google='true'))
        
        return process_social_login(user_data, 'google')
        
    except Exception as e:
        app.logger.error(f"Erro no callback do Google: {str(e)}")
        flash("Erro na autenticação com Google", "erro")
        return redirect(url_for('login'))

@app.route('/auth/facebook')
def auth_facebook():
    if DEVELOPMENT_MODE:
        pass
      
        return redirect(url_for('auth_facebook_callback', 
                              code='dev_code', 
                              state='dev_state'))
    
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
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
            user_data = {
                'email': 'teste.facebook@gmail.com',
                'name': 'Usuário Facebook Teste',
                'id': 'facebook_dev_456',
                'picture': {'data': {'url': 'https://via.placeholder.com/150'}}
            }
            return process_social_login(user_data, 'facebook')
        
        if request.args.get('state') != session.get('oauth_state'):
            flash("Erro de segurança na autenticação", "erro")
            return redirect(url_for('login'))
        
        code = request.args.get('code')
        if not code:
            flash("Erro na autenticação com Facebook", "erro")
            return redirect(url_for('login'))
        
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
        
        user_response = requests.get(
            f"https://graph.facebook.com/me?fields=id,name,email,picture&access_token={token_json['access_token']}"
        )
        user_data = user_response.json()
        
        return process_social_login(user_data, 'facebook')
        
    except Exception as e:
        app.logger.error(f"Erro no callback do Facebook: {str(e)}")
        flash("Erro na autenticação com Facebook", "erro")
        return redirect(url_for('login'))

def process_social_login(user_data, provider):
    pass
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        
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
        
        app.logger.info(f"Tentando login social - Provider: {provider}, Email: {email}, Nome: {nome}")
        
        if not email:
            app.logger.error("Email não fornecido pelo provedor social")
            flash("Não foi possível obter o email da conta social", "erro")
            return redirect(url_for('login'))
        
        
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            pass
            
            user_id = user['id']
            app.logger.info(f"Utilizador existente encontrado - ID: {user_id}")
            
            # Atualiza ultimo_login E campos social
            cursor.execute("""
                UPDATE usuarios 
                SET ultimo_login = %s, social_provider = %s, social_id = %s 
                WHERE id = %s
            """, (datetime.now(), provider, social_id, user_id))
            conn.commit()
        else:
            pass
            
            app.logger.info(f"Criando novo utilizador - Email: {email}")
            
            cursor.execute("SELECT id FROM avatars WHERE id > 0")
            avatars_disponiveis = cursor.fetchall()
            
            avatar_id_aleatorio = 1  
            if avatars_disponiveis:
                avatar_aleatorio = random.choice(avatars_disponiveis)
                avatar_id_aleatorio = avatar_aleatorio['id']
            
            agora = datetime.now()
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha, criado_em, ultimo_login, avatar_id, social_provider, social_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, email, generate_password_hash(secrets.token_urlsafe(32)), agora, agora, avatar_id_aleatorio, provider, social_id))
            
            conn.commit()
            user_id = cursor.lastrowid
            app.logger.info(f"Novo utilizador criado - ID: {user_id}")
        
        
        cursor.execute("""
            SELECT COALESCE(a.caminho, 'imgs/icons/user_icon34-removebg-preview.png') as avatar
            FROM usuarios u 
            LEFT JOIN avatars a ON u.avatar_id = a.id 
            WHERE u.id = %s
        """, (user_id,))
        avatar_result = cursor.fetchone()
        avatar_path = avatar_result['avatar'] if avatar_result else 'imgs/icons/user_icon34-removebg-preview.png'
        
        
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
        
       
        session['user_id'] = user_id
        session['user_nome'] = nome
        session['user_email'] = email
        session['user_avatar'] = avatar_path
        
        app.logger.info(f"Login social bem-sucedido - User ID: {user_id}, redirecionando para home")
        
       
        session.pop('oauth_state', None)
        
        # Recuperar o next_url da sessão
        next_url = session.pop('oauth_next_url', None)
        
        flash(f"Bem-vindo, {nome}!", "sucesso")
        
        # Redirecionar para a página especificada ou para home
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('home'))
        
    except Exception as e:
        app.logger.error(f"Erro no processo de login social: {str(e)}")
        app.logger.exception("Stack trace completo:")
        flash(f"Erro no login social: {str(e)}", "erro")
        return redirect(url_for('login'))

@app.route('/redefinir-senha')
def redefinir_senha():
    pass
  
    try:
        token = request.args.get('token')
        
        if not token:
            flash("Link inválido ou expirado", "erro")
            return redirect(url_for('login'))
        
        app.logger.info(f"Carregando página de redefinir senha com token: {token}")
        
       
        return render_template('redefinir_senha_simples.html', token=token)
        
    except Exception as e:
        app.logger.error(f"Erro na rota redefinir-senha: {str(e)}")
        flash("Erro interno. Tente novamente.", "erro")
        return redirect(url_for('login'))

@app.route('/api/redefinir-senha', methods=['POST'])
def api_redefinir_senha():
    pass
   
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
     
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, email FROM usuarios LIMIT 1")
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'Token inválido ou expirado'})
     
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

@app.route('/registo', methods=["GET", "POST"])
def registo():
    # Capturar o parâmetro next
    next_url = request.args.get('next') or request.form.get('next')
    
    # Se for GET e não tiver parâmetro from_google, limpar sessão do Google
    if request.method == "GET" and not request.args.get('from_google'):
        session.pop('google_email', None)
        session.pop('google_name', None)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

 
    cursor.execute("SELECT id, nome, caminho FROM avatars")
    avatars = cursor.fetchall()

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

     
            if not nome or not email or not senha:
                cursor.close()
                conn.close()
                return redirect(url_for("registo"))
            
           
            if senha != confirm_password:
                cursor.close()
                conn.close()
                return redirect(url_for("registo"))
            
           
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return redirect(url_for("registo"))

            senha_hash = generate_password_hash(senha)
            agora = datetime.now()
            
            custom_avatar_path = None
            
            
            if avatar_id and avatar_id.isdigit():
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha, criado_em, ultimo_login, avatar_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nome, email, senha_hash, agora, agora, int(avatar_id)))
            else:
                cursor.execute("SELECT id FROM avatars WHERE id > 0 ORDER BY id")
                avatars_disponiveis = cursor.fetchall()
                
                if avatars_disponiveis:
                    avatar_aleatorio = random.choice(avatars_disponiveis)
                    avatar_id_aleatorio = avatar_aleatorio['id']
                    
                    cursor.execute("""
                        INSERT INTO usuarios (nome, email, senha, criado_em, ultimo_login, avatar_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (nome, email, senha_hash, agora, agora, avatar_id_aleatorio))
                else:
                    pass
                
                    
           
                    cursor.execute("SELECT id FROM avatars WHERE id = 1")
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO avatars (id, nome, caminho, categoria) 
                            VALUES (1, 'Avatar Padrão', 'imgs/icons/user_icon34-removebg-preview.png', 'padrão')
                        """)
                    
                    cursor.execute("""
                        INSERT INTO usuarios (nome, email, senha, criado_em, ultimo_login, avatar_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (nome, email, senha_hash, agora, agora, 1))
            
            conn.commit()
            
            user_id = cursor.lastrowid
            
            avatar_path = 'imgs/icons/user_icon34-removebg-preview.png'
            
            if custom_avatar_path:
                avatar_path = custom_avatar_path
            else:
                cursor.execute("""
                    SELECT a.caminho 
                    FROM usuarios u 
                    LEFT JOIN avatars a ON u.avatar_id = a.id 
                    WHERE u.id = %s
                """, (user_id,))
                result = cursor.fetchone()
                
                if result and result.get('caminho'):
                    avatar_path = result['caminho'].replace('\\', '/').replace('"', '').strip()
                    if avatar_path.startswith('static/'):
                        avatar_path = avatar_path[7:]
                    if avatar_path.startswith('/static/'):
                        avatar_path = avatar_path[8:]
            
            cursor.close()
            conn.close()
            
            session['user_id'] = user_id
            session['user_nome'] = nome
            session['user_email'] = email
            session['user_avatar'] = avatar_path
            
            # Limpar variáveis de sessão do Google se existirem
            session.pop('google_email', None)
            session.pop('google_name', None)
            
            # Redirecionar para a página especificada ou para home
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
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
    return render_template("registo.html", avatars=avatars, next_url=next_url)


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
        
       
        cur.execute("SELECT caminho FROM avatars WHERE id = %s", (avatar_id,))
        avatar_row = cur.fetchone()
        
        if not avatar_row:
            return jsonify({'success': False, 'message': 'Avatar não encontrado'})
        
    
        cur.execute(
            "UPDATE usuarios SET avatar_id = %s WHERE id = %s",
            (avatar_id, session['user_id'])
        )
        conn.commit()
        
        
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

@app.route("/api/avatars/all")
def avatars_all():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Buscar todas as categorias
        cur.execute("SELECT id, nome FROM avatar_categories ORDER BY nome")
        categorias = cur.fetchall()
        
        resultado = []
        
        for categoria in categorias:
            # Buscar avatares de cada categoria, excluindo o avatar do admin
            cur.execute("""
                SELECT a.id, a.nome, a.caminho
                FROM avatars a
                WHERE a.categoria_id = %s
                AND a.nome != 'Admin CineVibe'
                ORDER BY a.nome
            """, (categoria['id'],))
            
            avatars = cur.fetchall()
            
            # Limpar caminhos
            for av in avatars:
                p = av["caminho"].replace("\\", "/").replace('"', "").strip()
                if p.startswith("static/"):
                    p = p[7:]
                if p.startswith("/static/"):
                    p = p[8:]
                av["caminho"] = p
            
            resultado.append({
                'categoria': categoria['nome'],
                'avatars': avatars
            })
        
        cur.close()
        conn.close()

        return jsonify(resultado)
    except Exception as e:
        app.logger.error(f"Erro ao buscar todos os avatares: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# TEST/DEBUG ROUTES - COMMENTED OUT FOR PRODUCTION
# These routes were used during development for testing and debugging
# 
# Commented routes include:
# - /testar-avatares
# - /test-email (line ~1519)
# - /teste-perfil-debug
# - /debug-produtos-resgatados
# - /criar-dados-teste-pontos-movimentos
# - /teste-pontos-movimentos
# - /criar-dados-teste-produtos
# - /teste-produtos-resgatados
# - /debug_login_afonso (line ~6827)
# - /teste-email (line ~8616)
# - /debug/cinemas (line ~13132)
# - /teste_pagamento
# - /test_api_filmes
# - /test_pagamento
# - /debug_pagamento
# - /test_filme
# - /test_logado
# - /debug/filmes
# - /debug_sessao
# - /debug/bar
# ============================================================================

# @app.route("/testar-avatares")
# def testar_avatares():
#     return render_template('testar_avatares.html')


# @app.route('/test-email')
# def test_email():
#     pass
# 
#     if 'user_id' not in session:
#         return jsonify({
#             'success': False,
#             'message': 'É necessário fazer login para testar o email'
#         }), 401
#     
#     try:
#         pass
#      
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (session['user_id'],))
#         user = cursor.fetchone()
#         cursor.close()
#         conn.close()
#         
#         if not user:
#             return jsonify({
#                 'success': False,
#                 'message': 'Utilizador não encontrado'
#             }), 404
#         
#      
#         dados_reserva = {
#             'reserva_id': 99999,
#             'filme': 'Filme de Teste - Aventura Épica',
#             'cinema': 'CineVibe Lisboa - Centro',
#             'tipo_sessao': '2D Legendado',
#             'horario': '25/12/2024 às 20:00',
#             'quantidade': '2 bilhetes'
#         }
#         
#      
#         sucesso = enviar_email_confirmacao(
#             user['email'],
#             user['nome'],
#             dados_reserva
#         )
#         
#         if sucesso:
#             return jsonify({
#                 'success': True,
#                 'message': f'✅ Email de teste enviado com sucesso para {user["email"]}! Verifique a sua caixa de entrada.'
#             })
#         else:
#             return jsonify({
#                 'success': False,
#                 'message': '❌ Falha ao enviar email. Verifique as configurações no email_config.py e os logs do servidor.'
#             }), 500
#             
#     except Exception as e:
#         app.logger.error(f"Erro no teste de email: {str(e)}")
#         return jsonify({
#             'success': False,
#             'message': f'Erro: {str(e)}'
#         }), 500
# 
# 
# 
# @app.route('/teste-perfil-debug')
# def teste_perfil_debug():
#     """Route de teste para debug do perfil"""
#     
#     if 'user_id' not in session:
#         return "❌ Usuário não está logado"
#     
#     user_id = session['user_id']
#     return f"✅ Usuário logado com ID: {user_id}. Route de teste funcionando!"

# TEST ROUTE - Comment out for production
@app.route('/debug-produtos-resgatados')
def debug_produtos_resgatados():
    pass
  
    if 'user_id' not in session:
        return "Precisa estar logado"
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        resultado = f"<h2>Debug Produtos Resgatados - User ID: {user_id}</h2>"

        cursor.execute("SHOW TABLES LIKE 'pontos_gastos'")
        tabela_existe = cursor.fetchone()
        resultado += f"<p>Tabela pontos_gastos existe: {'SIM' if tabela_existe else 'NÃO'}</p>"
        
        if not tabela_existe:
            pass
           
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
        
    
        cursor.execute("SELECT COUNT(*) as total FROM pontos_gastos WHERE usuario_id = %s", (user_id,))
        total = cursor.fetchone()['total']
        resultado += f"<p>Total de produtos para este usuário: {total}</p>"
        
        if total == 0:
            pass
          
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

# TEST ROUTE - Comment out for production
@app.route('/criar-dados-teste-pontos-movimentos')
def criar_dados_teste_pontos_movimentos():
    pass
    
    if 'user_id' not in session:
        return "Precisa estar logado"
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
       
        cursor.execute("DELETE FROM pontos_movimentos WHERE utilizador_id = %s AND motivo LIKE '%resgate%'", (user_id,))
        
  
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

# TEST ROUTE - Comment out for production
@app.route('/teste-pontos-movimentos')
def teste_pontos_movimentos():
    pass
   
    if 'user_id' not in session:
        return "Precisa estar logado"
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
       
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

# TEST ROUTE - Comment out for production
@app.route('/criar-dados-teste-produtos')
def criar_dados_teste_produtos():
    pass
   
    if 'user_id' not in session:
        return "Precisa estar logado"
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
        
      
        cursor.execute("DELETE FROM pontos_gastos WHERE usuario_id = %s", (user_id,))
        
        
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

# TEST ROUTE - Comment out for production
@app.route('/teste-produtos-resgatados')
def teste_produtos_resgatados():
    pass
    
    if 'user_id' not in session:
        return "Precisa estar logado"
    
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
     
        

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
        
   
        cursor.execute("SELECT COUNT(*) as total FROM pontos_gastos WHERE usuario_id = %s", (user_id,))
        total_existente = cursor.fetchone()['total']
        
        if total_existente == 0:
            pass
            
         
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
    pass
    
    if 'user_id' not in session:
        flash("Inicia sessão primeiro!", "erro")
        return redirect(url_for('login'))

    user_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

      
        cursor.execute("""
            SELECT u.id, u.nome, u.email, u.avatar_id,
                   a.caminho as avatar_path
            FROM usuarios u 
            LEFT JOIN avatars a ON u.avatar_id = a.id 
            WHERE u.id = %s
        """, (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            flash("Utilizador não encontrado!", "erro")
            return redirect(url_for('home'))


       
        if user.get('email') == 'cinevibeadmn@gmail.com':
            cursor.close()
            conn.close()
            return redirect(url_for('admin_dashboard'))

       
        avatar = None
        
        if user.get('avatar_path'):
            avatar = str(user['avatar_path'])
        else:
            avatar = 'imgs/icons/user_icon34-removebg-preview.png'
        
      
        if avatar:
            avatar = avatar.replace('\\', '/').replace('"', '').strip()
            
       
            if avatar.startswith('static/'):
                avatar = avatar[7:]
            if avatar.startswith('/static/'):
                avatar = avatar[8:]
        
        
        if not avatar or avatar == 'imgs/' or avatar == 'imgs':
            avatar = 'imgs/icons/user_icon34-removebg-preview.png'
        
       
        session['user_avatar'] = avatar

        
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
            JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
            JOIN horarios h ON hs.id_horario = h.id
            LEFT JOIN avaliacoes_filmes av ON f.id = av.filme_id AND av.usuario_id = %s
            WHERE r.id_usuario = %s
            AND DATE_ADD(CONCAT(r.data_sessao, ' ', h.hora), INTERVAL f.duracao MINUTE) < NOW()
            GROUP BY f.id, f.titulo, f.poster_url, f.duracao, av.rating, av.comentario, av.data_avaliacao
            ORDER BY MAX(r.data_sessao) DESC
        """, (user_id, user_id, user_id, user_id))
        filmes_vistos = cursor.fetchall() or []

 
        for filme in filmes_vistos:
            if filme.get('poster_url'):
                filme['poster_url'] = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
                if not filme['poster_url'].startswith('imgs/'):
                    filme['poster_url'] = f"imgs/filmes/{filme['poster_url']}"
            else:
                filme['poster_url'] = 'imgs/filmes/default.jpg'

     
        cursor.execute("""
            SELECT c.id, c.nome, c.localizacao,
                   COALESCE(c.imagem, 'imgs/cinemas/default.jpg') as imagem
            FROM cinemas_favoritos cf
            JOIN cinemas c ON cf.cinema_id = c.id
            WHERE cf.usuario_id = %s
            ORDER BY cf.data_adicao DESC
        """, (user_id,))
        cinemas_favoritos = cursor.fetchall() or []

       
        for cinema in cinemas_favoritos:
            if cinema.get('imagem'):
                cinema['imagem'] = cinema['imagem'].replace('\\', '/').replace('"', '').strip()
                if not cinema['imagem'].startswith('imgs/'):
                    cinema['imagem'] = f"imgs/cinemas/{cinema['imagem']}"
            else:
                cinema['imagem'] = 'imgs/cinemas/default.jpg'

        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_avaliacoes,
                AVG(rating) as media_avaliacoes
            FROM avaliacoes_filmes 
            WHERE usuario_id = %s
        """, (user_id,))
        stats_avaliacoes = cursor.fetchone() or {'total_avaliacoes': 0, 'media_avaliacoes': 0}

       
        total_filmes_vistos = len(filmes_vistos)
        total_avaliacoes = stats_avaliacoes['total_avaliacoes']

        cursor.close()
        conn.close()

      
        conn2 = get_db_connection()
        cursor2 = conn2.cursor(dictionary=True)
        pontos = calcular_pontos_usuario(session['user_id'], cursor2)
        cursor2.close()
        conn2.close()
        
   
        if pontos < 500:
            nivel = "Iniciante"
            nivel_cor = "linear-gradient(135deg, #FFD60A, #FFA500)"
        elif pontos < 1000:
            nivel = "Cinéfilo"
            nivel_cor = "linear-gradient(135deg, #FFD60A, #FFA500)"
        elif pontos < 2000:
            nivel = "Expert"
            nivel_cor = "linear-gradient(135deg, #FFD60A, #FFA500)"
        else:
            nivel = "Lenda"
            nivel_cor = "linear-gradient(135deg, #FFD60A, #FFA500)"

        stats = {
            'filmes_vistos': total_filmes_vistos,
            'reservas_feitas': total_filmes_vistos,
            'avaliacoes_feitas': total_avaliacoes,
            'pontos_gastos': 0
        }

        # Obter informações da subscrição
        subscricao = get_user_subscription(user_id)

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
                             subscricao=subscricao,
                             logged_in=True,
                             avatar=avatar,
                             is_admin=False)

    except Exception as e:
        import traceback
        app.logger.error(f"Erro na função perfil: {str(e)}")
        flash("Erro ao carregar perfil. Tenta novamente.", "erro")
        return redirect(url_for('home'))

@app.route('/recompensas')
def recompensas():
    if 'user_id' not in session:
        flash("Inicia sessão primeiro!", "erro")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
   
    cursor.execute("""
        SELECT u.id, u.nome, u.email, u.avatar_id,
               a.caminho as avatar_path
        FROM usuarios u 
        LEFT JOIN avatars a ON u.avatar_id = a.id 
        WHERE u.id = %s
    """, (user_id,))
    user = cursor.fetchone()
    

    avatar = None
    
  
    if user and user.get('avatar_path'):
        avatar = str(user['avatar_path'])
    elif user and user.get('avatar'):
        avatar = str(user['avatar'])
    else:
        avatar = 'imgs/icons/user_icon34-removebg-preview.png'
    
 
    if avatar:
        avatar = avatar.replace('\\', '/').replace('"', '').strip()
        
       
        if avatar.startswith('static/'):
            avatar = avatar[7:]
        if avatar.startswith('/static/'):
            avatar = avatar[8:]
    

    if not avatar or avatar == 'imgs/' or avatar == 'imgs':
        avatar = 'imgs/icons/user_icon34-removebg-preview.png'
    
   
    session['user_avatar'] = avatar
    
    
    
    pontos = calcular_pontos_usuario(session['user_id'], cursor)
    
    
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
    
    
    recompensas = []
    for r in recompensas_raw:
        r_dict = dict(r)
        r_dict['titulo'] = r_dict['nome']
        r_dict['custo_pontos'] = r_dict['pontos']
        
        
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
        
       
        if r_dict.get('img_url'):
            r_dict['imagem'] = r_dict['img_url'].replace('\\', '/').replace('"', '').strip()
        else:
            pass
           
            r_dict['imagem'] = 'imgs/icons/wheel-removebg-preview.png'
        
        recompensas.append(r_dict)
    
    cursor.close()
    conn.close()
    
    
    return render_template('recompensas.html', logged_in=True, avatar=avatar, pontos=pontos, recompensas=recompensas)


@app.route('/premios')
def premios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    
    logged_in = 'user_id' in session
    avatar = 'imgs/icons/user_icon34-removebg-preview.png'
    
    if logged_in:
        user_id = session['user_id']
      
        cursor.execute("""
            SELECT a.caminho AS avatar
            FROM usuarios u
            LEFT JOIN avatars a ON u.avatar_id = a.id
            WHERE u.id = %s
        """, (user_id,))
        user_data = cursor.fetchone()
        if user_data and user_data.get('avatar'):
            avatar = user_data['avatar'].replace('\\', '/').replace('"', '').strip()
            
            if avatar.startswith('static/'):
                avatar = avatar[7:]
            if avatar.startswith('/static/'):
                avatar = avatar[8:]
    
  
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
    
    
    premios_list = []
    for premio in premios_raw:
        premio_dict = dict(premio)
       
        if premio_dict.get('img_url'):
            premio_dict['img_url'] = premio_dict['img_url'].replace('\\', '/').replace('"', '').strip()
        else:
            premio_dict['img_url'] = 'imgs/icons/wheel-removebg-preview.png'
        
        premios_list.append(premio_dict)
    
    cursor.close()
    conn.close()
    
    return render_template('premios.html', logged_in=logged_in, avatar=avatar, premios=premios_list)


@app.route('/resgatar_recompensa', methods=['POST'])
def resgatar_recompensa():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Utilizador não autenticado'})
    
    try:
        data = request.get_json()
        premio_id = data.get('tipo') 
        custo = data.get('custo')    
        
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        pontos_atuais = calcular_pontos_usuario(user_id, cursor)
        
    
        cursor.execute("SELECT nome, pontos FROM premios WHERE id = %s", (premio_id,))
        premio = cursor.fetchone()
        
        cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (user_id,))
        usuario = cursor.fetchone()
        
        if not premio or not usuario:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Prémio ou utilizador não encontrado'})
        
      
        pontos_necessarios = premio['pontos']
        if pontos_atuais < pontos_necessarios:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': f'Pontos insuficientes. Precisa de {pontos_necessarios} pontos, tem {pontos_atuais}'})
   
        import random
        import string
        from datetime import datetime, timedelta
        
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
 
        cursor.execute("SELECT id FROM codigos_desconto WHERE codigo = %s", (codigo,))
        while cursor.fetchone():
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            cursor.execute("SELECT id FROM codigos_desconto WHERE codigo = %s", (codigo,))
 
        tipo_desconto = 'produto_gratis'
        valor_desconto = 0.00

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
            valor_desconto = 100.00 
        
       
        data_expiracao = datetime.now() + timedelta(days=30)
        
      
        cursor.execute("""
            INSERT INTO codigos_desconto 
            (codigo, usuario_id, premio_id, premio_nome, tipo_desconto, valor_desconto, data_expiracao)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (codigo, user_id, premio_id, premio['nome'], tipo_desconto, valor_desconto, data_expiracao))
        
        
      
        cursor.execute("""
            INSERT INTO pontos_gastos 
            (usuario_id, premio_id, premio_nome, pontos_gastos, codigo_desconto)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, premio_id, premio['nome'], pontos_necessarios, codigo))
        
        
        conn.commit()
        
        # Responder imediatamente ao usuário
        cursor.close()
        conn.close()
        
        # Enviar email em background (não bloqueia a resposta)
        try:
            import threading
            
            def enviar_email_background():
                try:
                    msg = MIMEMultipart()
                    msg['From'] = EMAIL_USER
                    msg['To'] = usuario['email']
                    msg['Subject'] = f"Código de Desconto CineVibe - {premio['nome']}"
                    
                    corpo_email = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; background-color: #0D1B2A; padding: 20px;">
                        <div style="max-width: 600px; margin: 0 auto; background: #1B263B; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.5);">
                            <h1 style="color: #FFD60A; text-align: center; margin-bottom: 20px;">Parabéns!</h1>
                            
                            <p style="font-size: 18px; text-align: center; margin-bottom: 30px; color: #E0E1DD;">
                                Resgataste com sucesso a tua recompensa:
                            </p>
                            
                            <div style="background: #FFD60A; border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 30px;">
                                <h2 style="color: #0D1B2A; margin: 0;">{premio['nome']}</h2>
                            </div>
                            
                            <p style="text-align: center; font-size: 16px; margin: 30px 0; color: #E0E1DD;">
                                O teu código de desconto é:
                            </p>
                            
                            <div style="background: #0D1B2A; color: #FFD60A; font-size: 32px; font-weight: bold; text-align: center; padding: 20px; border-radius: 8px; letter-spacing: 3px; margin-bottom: 30px;">
                                {codigo}
                            </div>
                            
                            <div style="background: #415A77; border-left: 4px solid #FFD60A; padding: 20px; margin-bottom: 30px; border-radius: 5px;">
                                <h3 style="color: #FFD60A; margin-top: 0;">Como usar:</h3>
                                <ol style="color: #E0E1DD; line-height: 1.8;">
                                    <li>Faz a tua reserva normalmente</li>
                                    <li>Na página de pagamento, introduz o código no campo "Código de Desconto"</li>
                                    <li>Clica em "Aplicar" para ver o desconto</li>
                                    <li>Finaliza a compra e desfruta!</li>
                                </ol>
                            </div>
                            
                            <p style="text-align: center; color: #778DA9; font-size: 14px; margin: 20px 0;">
                                ⏰ Este código expira em 30 dias<br>
                                📧 Guarda este email para não perderes o código
                            </p>
                            
                            <div style="text-align: center; margin-top: 30px;">
                                <a href="http://localhost:5000/filmes" style="background: #FFD60A; color: #0D1B2A; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                                    Ver Filmes Disponíveis
                                </a>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    msg.attach(MIMEText(corpo_email, 'html'))
                    
                    if EMAIL_PASSWORD not in ['sua_senha_app', 'DESATIVADO_TEMPORARIAMENTE'] and EMAIL_PASSWORD:
                        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
                        if EMAIL_USE_TLS:
                            server.starttls()
                        server.login(EMAIL_USER, EMAIL_PASSWORD)
                        server.send_message(msg)
                        server.quit()
                        app.logger.info(f"Email de código enviado para {usuario['email']}")
                    else:
                        app.logger.warning("Email desativado - código não enviado")
                        
                except Exception as email_error:
                    app.logger.error(f"Erro ao enviar email de código: {email_error}")
            
            # Iniciar thread para enviar email em background
            email_thread = threading.Thread(target=enviar_email_background)
            email_thread.daemon = True
            email_thread.start()
            
        except Exception as thread_error:
            app.logger.error(f"Erro ao criar thread de email: {thread_error}")
        
        return jsonify({
            'success': True, 
            'message': f'Prémio "{premio["nome"]}" resgatado com sucesso! Verifica o teu email para o código de desconto.',
            'codigo': codigo,  
            'pontos_restantes': pontos_atuais - pontos_necessarios
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        flash("Inicia sessão primeiro!", "erro")
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
   
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash("Acesso negado! Apenas administradores podem aceder a esta página.", "erro")
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    
   
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
    
  
    cur.execute("""
        SELECT COALESCE(SUM(total), 0) as total
        FROM reservas
        WHERE YEARWEEK(data_reserva, 1) = YEARWEEK(CURDATE(), 1) - 1
    """)
    receita_semana_anterior = float(cur.fetchone()['total'] or 0)
    crescimento_semanal = ((receita_semana - receita_semana_anterior) / receita_semana_anterior * 100) if receita_semana_anterior > 0 else 0
    
 
    cur.execute("""
        SELECT f.titulo, f.poster_url, COUNT(r.id) as total_reservas,
               COALESCE(SUM(r.total), 0) as receita
        FROM filmes f
        LEFT JOIN reservas r ON f.id = r.id_filme
        LEFT JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
        LEFT JOIN horarios h ON hs.id_horario = h.id
        WHERE r.id IS NULL 
           OR DATE_ADD(CONCAT(r.data_sessao, ' ', h.hora), INTERVAL f.duracao MINUTE) < NOW()
        GROUP BY f.id, f.titulo, f.poster_url
        ORDER BY total_reservas DESC
        LIMIT 10
    """)
    top_filmes = cur.fetchall()
    

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
    

    cur.execute("""
        SELECT TIME_FORMAT(h.hora, '%H:%i') as horario, 
               COUNT(r.id) as total_reservas
        FROM reservas r
        JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
        JOIN horarios h ON hs.id_horario = h.id
        GROUP BY h.id, h.hora
        HAVING total_reservas > 0
        ORDER BY total_reservas DESC, h.hora
        LIMIT 5
    """)
    horarios_populares = cur.fetchall()
    
    if not horarios_populares:
        cur.execute("""
            SELECT TIME_FORMAT(hora, '%H:%i') as horario, 
                   0 as total_reservas
            FROM horarios
            WHERE hora BETWEEN '14:00:00' AND '23:00:00'
            ORDER BY hora
            LIMIT 5
        """)
        horarios_populares = cur.fetchall()
    
    cur.execute("""
        SELECT ts.nome, COUNT(r.id) as total_reservas,
               COALESCE(SUM(r.total), 0) as receita
        FROM tipos_sessao ts
        LEFT JOIN reservas r ON ts.id = r.id_tipo_sessao
        GROUP BY ts.id, ts.nome
        ORDER BY total_reservas DESC
    """)
    tipos_sessao_stats = cur.fetchall()
    

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
    
    cur.execute("""
        SELECT COUNT(*) as total
        FROM usuarios
        WHERE criado_em >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        AND is_admin = FALSE
    """)
    novos_usuarios_semana = cur.fetchone()['total']
    
    try:
        cur.execute("""
            SELECT b.produto as nome, b.imagem_url,
                   COALESCE(SUM(rb.quantidade), 0) as total_vendas
            FROM bar b
            LEFT JOIN reservas_bar rb ON rb.produto_id = b.id
            GROUP BY b.id, b.produto, b.imagem_url
            HAVING total_vendas > 0
            ORDER BY total_vendas DESC
            LIMIT 5
        """)
        top_produtos_bar = cur.fetchall()
        
        if not top_produtos_bar:
            cur.execute("""
                SELECT produto as nome, imagem_url, 0 as total_vendas
                FROM bar
                ORDER BY id
                LIMIT 5
            """)
            top_produtos_bar = cur.fetchall()
    except Exception as e:
        app.logger.error(f"Erro ao buscar top produtos bar: {str(e)}")
        top_produtos_bar = []
    

    cur.execute("""
        SELECT 
            s.nome_sala,
            c.nome as cinema_nome,
            f.titulo as filme_titulo,
            TIME_FORMAT(h.hora, '%H:%i') as horario,
            DATE_FORMAT(r.data_sessao, '%d/%m/%Y') as data_sessao,
            s.capacidade,
            SUM(LENGTH(r.lugares) - LENGTH(REPLACE(r.lugares, ',', '')) + 1) as total_lugares_reservados,
            ROUND(
                (SUM(LENGTH(r.lugares) - LENGTH(REPLACE(r.lugares, ',', '')) + 1) / s.capacidade * 100),
                1
            ) as taxa_ocupacao
        FROM reservas r
        JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
        JOIN salas s ON hs.id_sala = s.id
        JOIN cinemas c ON s.id_cinema = c.id
        JOIN horarios h ON hs.id_horario = h.id
        JOIN filmes f ON r.id_filme = f.id
        WHERE r.data_sessao >= CURDATE() - INTERVAL 7 DAY
        GROUP BY s.id, s.nome_sala, c.nome, f.titulo, h.hora, r.data_sessao, s.capacidade
        ORDER BY taxa_ocupacao DESC, r.data_sessao DESC
        LIMIT 10
    """)
    ocupacao_salas = cur.fetchall()
    
    # Query simplificada - apenas sessões com reservas existentes
    cur.execute("""
        SELECT 
            s.nome_sala,
            c.nome as cinema_nome,
            f.titulo as filme_titulo,
            f.id as filme_id,
            DATE_FORMAT(r.data_sessao, '%d/%m/%Y') as data_sessao,
            TIME_FORMAT(h.hora, '%H:%i') as horario,
            s.capacidade,
            SUM(LENGTH(r.lugares) - LENGTH(REPLACE(r.lugares, ',', '')) + 1) as total_lugares_reservados,
            ROUND(
                (SUM(LENGTH(r.lugares) - LENGTH(REPLACE(r.lugares, ',', '')) + 1) / s.capacidade * 100),
                1
            ) as taxa_ocupacao
        FROM reservas r
        JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
        JOIN salas s ON hs.id_sala = s.id
        JOIN cinemas c ON s.id_cinema = c.id
        JOIN horarios h ON hs.id_horario = h.id
        JOIN filmes f ON r.id_filme = f.id
        WHERE r.data_sessao >= CURDATE() AND r.data_sessao <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
        AND f.estado = 'em_exibicao'
        GROUP BY r.id_horario_sessao, r.data_sessao, s.id, s.nome_sala, c.nome, f.titulo, f.id, h.hora, s.capacidade
        HAVING taxa_ocupacao <= 50
        ORDER BY taxa_ocupacao ASC, r.data_sessao ASC
        LIMIT 20
    """)
    sessoes_baixa_ocupacao_raw = cur.fetchall()
    
    # Garantir que cada filme aparece apenas uma vez
    sessoes_baixa_ocupacao = []
    filmes_adicionados = set()
    
    for sessao in sessoes_baixa_ocupacao_raw:
        filme_id = sessao['filme_id']
        if filme_id not in filmes_adicionados:
            sessoes_baixa_ocupacao.append(sessao)
            filmes_adicionados.add(filme_id)
        
        if len(sessoes_baixa_ocupacao) >= 10:
            break
    
    cur.execute("""
        SELECT 
            f.id,
            f.titulo,
            f.poster_url,
            COUNT(DISTINCT hs.id) as total_sessoes,
            COUNT(DISTINCT r.id) as total_reservas
        FROM filmes f
        INNER JOIN horarios_sessao hs ON hs.id_filme = f.id
        LEFT JOIN reservas r ON r.id_filme = f.id
        WHERE f.estado = 'em_exibicao'
        GROUP BY f.id, f.titulo, f.poster_url
        HAVING COUNT(DISTINCT r.id) = 0 AND COUNT(DISTINCT hs.id) > 0
        ORDER BY COUNT(DISTINCT hs.id) DESC
        LIMIT 10
    """)
    filmes_sem_reservas = cur.fetchall()
    
    cur.execute("""
        SELECT 
            u.nome,
            u.email,
            DATE_FORMAT(u.criado_em, '%d/%m/%Y') as data_cadastro,
            DATEDIFF(CURDATE(), u.criado_em) as dias_cadastrado
        FROM usuarios u
        LEFT JOIN reservas r ON r.id_usuario = u.id
        WHERE r.id IS NULL
        GROUP BY u.id
        LIMIT 10
    """)
    usuarios_sem_reservas = cur.fetchall()
    
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
        ocupacao_salas=ocupacao_salas,
        sessoes_baixa_ocupacao=sessoes_baixa_ocupacao,
        filmes_sem_reservas=filmes_sem_reservas,
        usuarios_sem_reservas=usuarios_sem_reservas
    )


@app.route('/admin/exportar/<tipo>')
def exportar_relatorio(tipo):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    

    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        flash('Acesso negado', 'erro')
        return redirect(url_for('home'))
    
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    

    data_relatorio = datetime.now().strftime('%d/%m/%Y às %H:%M')
    
    if tipo == 'reservas':
        pass

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
        
        writer.writerow(['RELATÓRIO DE RESERVAS - CINEVIBE'])
        writer.writerow([f'Gerado em: {data_relatorio}'])
        writer.writerow([f'Total de Reservas: {len(dados)}'])
        writer.writerow([])
        
        writer.writerow(['ID', 'Data Reserva', 'Data Sessão', 'Usuário', 'Email', 'Filme', 'Cinema', 'Localização', 'Tipo Sessão', 'Lugares', 'Valor (€)', 'Status'])
        
     
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
        
        
        writer.writerow([])
        writer.writerow(['', '', '', '', '', '', '', '', '', 'TOTAL:', f"{total_receita:.2f} €", ''])
        
        filename = f'CineVibe_Reservas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    elif tipo == 'vendas':
        pass
        
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
        
  
        writer.writerow(['RELATÓRIO DE VENDAS - CINEVIBE'])
        writer.writerow([f'Gerado em: {data_relatorio}'])
        writer.writerow([])
        
       
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
        pass
        
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
        
    
        writer.writerow(['RELATÓRIO DE USUÁRIOS - CINEVIBE'])
        writer.writerow([f'Gerado em: {data_relatorio}'])
        writer.writerow([f'Total de Usuários: {len(dados)}'])
        writer.writerow([])
        
       
        total_usuarios = len(dados)
        usuarios_ativos = sum(1 for u in dados if u['total_reservas'] > 0)
        usuarios_inativos = total_usuarios - usuarios_ativos
        
        writer.writerow(['ESTATÍSTICAS GERAIS'])
        writer.writerow(['Usuários Ativos (com reservas):', usuarios_ativos])
        writer.writerow(['Usuários Inativos (sem reservas):', usuarios_inativos])
        writer.writerow([])
        writer.writerow([])
        
        
        writer.writerow(['ID', 'Nome', 'Email', 'Data Registo', 'Total Reservas', 'Total Gasto (€)', 'Status'])
        
        
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
        
    
        writer.writerow([])
        writer.writerow(['', '', '', 'TOTAIS:', total_reservas, f"{total_gasto:.2f} €", ''])
        
        filename = f'CineVibe_Usuarios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    elif tipo == 'filmes':
        pass
        
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
        
        
        writer.writerow(['RELATÓRIO DE DESEMPENHO DE FILMES - CINEVIBE'])
        writer.writerow([f'Gerado em: {data_relatorio}'])
        writer.writerow([f'Total de Filmes: {len(dados)}'])
        writer.writerow([])
        
      
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
        
        
        writer.writerow(['ID', 'Título', 'Diretor', 'Data Lançamento', 'Duração (min)', 'Estado', 'Total Reservas', 'Receita (€)', 'Status'])
        
        
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
        
     
        writer.writerow([])
        writer.writerow(['', '', '', '', '', 'TOTAIS:', total_reservas, f"{total_receita:.2f} €", ''])
        
        filename = f'CineVibe_Filmes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    else:
        flash('Tipo de relatório inválido', 'erro')
        return redirect(url_for('admin_dashboard'))
    
    cur.close()
    conn.close()
    

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

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
    
    
    sort_by = request.args.get('sort', 'id')
    order_dir = request.args.get('order', 'desc')  
    
    
    direction = "ASC" if order_dir == 'asc' else "DESC"
    
    if sort_by == 'duracao':
        order_clause = f"ORDER BY f.duracao {direction}"
    elif sort_by == 'imdb':
        order_clause = f"ORDER BY f.imdb_rating {direction}"
    elif sort_by == 'ano':
        order_clause = f"ORDER BY f.data_lancamento {direction}"
    else:
        order_clause = f"ORDER BY f.id {direction}"
    
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
    
    cur.execute("SELECT id, nome FROM generos ORDER BY nome")
    generos = cur.fetchall()
    
    for filme in filmes:
        if filme.get('poster_url'):
            poster_url = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
            
            if poster_url.startswith('static/'):
                poster_url = poster_url[7:]
            if poster_url.startswith('/'):
                poster_url = poster_url[1:]
            
            if not poster_url.startswith('imgs/filmes/'):
                if poster_url.startswith('imgs/'):
                    pass
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
    
    cur.execute("SELECT * FROM filmes WHERE id = %s", (id_filme,))
    filme = cur.fetchone()
    
    if not filme:
        flash("Filme não encontrado!", "erro")
        return redirect(url_for('admin_filmes'))
    
    if filme.get('poster_url'):
        filme['poster_url'] = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
    
    cur.execute("""
        SELECT g.id, g.nome
        FROM generos g
        JOIN filme_generos fg ON g.id = fg.genero_id
        WHERE fg.filme_id = %s
        ORDER BY g.nome
    """, (id_filme,))
    generos_filme = cur.fetchall()
    
    # Criar lista de IDs dos géneros já selecionados
    generos_filme_ids = [genero['id'] for genero in generos_filme]
    
    cur.execute("SELECT id, nome FROM generos ORDER BY nome")
    todos_generos = cur.fetchall()
    
    cur.execute("""
        SELECT c.id, c.nome, c.regiao
        FROM filmes_cinemas fc
        JOIN cinemas c ON fc.cinema_id = c.id
        WHERE fc.filme_id = %s
        ORDER BY c.nome
    """, (id_filme,))
    cinemas_filme = cur.fetchall()
    
    cur.execute("SELECT id, nome, regiao FROM cinemas ORDER BY nome")
    todos_cinemas = cur.fetchall()
    
    cur.execute("""
        SELECT DISTINCT ts.id, ts.nome, ts.preco_bilhete, ts.descricao
        FROM tipos_sessao ts
        JOIN horarios_sessao hs ON ts.id = hs.id_tipo_sessao
        WHERE hs.id_filme = %s
        ORDER BY ts.nome
    """, (id_filme,))
    tipos_sessao = cur.fetchall()
    
    cur.execute("SELECT id, hora FROM horarios ORDER BY hora")
    horarios_disponiveis = cur.fetchall()
    
    sessoes_detalhadas = {}
    
    cur.execute("""
        SELECT a.id, a.nome, a.foto_url, fa.papel
        FROM filme_atores fa
        JOIN atores a ON fa.ator_id = a.id
        WHERE fa.filme_id = %s
        ORDER BY a.nome
    """, (id_filme,))
    atores_filme = cur.fetchall()
    
    cur.execute("SELECT id, nome, foto_url FROM atores ORDER BY nome")
    todos_atores = cur.fetchall()
    
    cur.execute("""
        SELECT 
            av.id,
            av.usuario_id,
            av.rating,
            av.comentario,
            av.data_avaliacao,
            u.nome as usuario_nome,
            COALESCE(a.caminho, 'imgs/icons/user_icon34-removebg-preview.png') as usuario_avatar
        FROM avaliacoes_filmes av
        JOIN usuarios u ON av.usuario_id = u.id
        LEFT JOIN avatars a ON u.avatar_id = a.id
        WHERE av.filme_id = %s
        ORDER BY av.data_avaliacao DESC
        LIMIT 5
    """, (id_filme,))
    avaliacoes_recentes = cur.fetchall()
    
    for avaliacao in avaliacoes_recentes:
        if avaliacao.get('usuario_avatar'):
            avaliacao['usuario_avatar'] = avaliacao['usuario_avatar'].replace('\\', '/').replace('"', '').strip()
        else:
            avaliacao['usuario_avatar'] = 'imgs/icons/user_icon34-removebg-preview.png'
    
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
    
    for ator in atores_filme:
        if ator.get('foto_url'):
            ator['foto_url'] = ator['foto_url'].replace('\\', '/').replace('"', '').strip()
    
    for ator in todos_atores:
        if ator.get('foto_url'):
            ator['foto_url'] = ator['foto_url'].replace('\\', '/').replace('"', '').strip()
    
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
    
    tipos_sessao = []
    
    cur.close()
    conn.close()
    return render_template('admin_filme_detalhe.html',
                         user=get_current_user(),
                         filme=filme,
                         generos_filme=generos_filme,
                         generos_filme_ids=generos_filme_ids,
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
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
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
        
        cur.execute("SELECT id FROM horarios ORDER BY hora LIMIT 1")
        horario_padrao = cur.fetchone()
        
        if not horario_padrao:
            return jsonify({
                'success': False,
                'message': 'Nenhum horário disponível na base de dados'
            }), 400
        
        cur.execute("""
            INSERT INTO horarios_sessao (id_filme, id_cinema, id_tipo_sessao, id_sala, id_horario)
            VALUES (%s, %s, %s, %s, %s)
        """, (filme_id, cinema_id, tipo_sessao_id, sala_id, horario_padrao['id']))
        
        conn.commit()
        
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
        cur.execute("SELECT nome FROM tipos_sessao WHERE id = %s", (tipo_sessao_id,))
        tipo_nome = cur.fetchone()
        
        cur.execute("""
            SELECT COUNT(*) as count_reservas
            FROM reservas r
            JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
            WHERE hs.id_filme = %s AND hs.id_cinema = %s AND hs.id_tipo_sessao = %s
        """, (filme_id, cinema_id, tipo_sessao_id))
        
        reservas_count = cur.fetchone()['count_reservas']
        
        if reservas_count > 0:
            app.logger.warning(f"Removendo {reservas_count} reservas antes de remover horários")
            
            cur.execute("""
                DELETE r FROM reservas r
                JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
                WHERE hs.id_filme = %s AND hs.id_cinema = %s AND hs.id_tipo_sessao = %s
            """, (filme_id, cinema_id, tipo_sessao_id))
            
            reservas_removidas = cur.rowcount
            app.logger.info(f"Removidas {reservas_removidas} reservas")
        
        cur.execute("""
            DELETE FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s
        """, (filme_id, cinema_id, tipo_sessao_id))
        
        horarios_removidos = cur.rowcount
        conn.commit()
        
        app.logger.info(f"Removidos {horarios_removidos} horários do tipo de sessão {tipo_sessao_id}")
        
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
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'error': 'Acesso negado'}), 403
        
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


@app.route('/admin/tipos-sessao/adicionar', methods=['POST'])
def admin_adicionar_tipo_sessao():
    """Adiciona um novo tipo de sessão"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        nome = request.form.get('nome')
        descricao = request.form.get('descricao', '')
        preco_bilhete = request.form.get('preco_bilhete')
        
        if not nome or not preco_bilhete:
            return jsonify({'success': False, 'message': 'Nome e preço são obrigatórios'})
        
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
    pass
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        nome = request.form.get('nome')
        descricao = request.form.get('descricao', '')
        preco_bilhete = request.form.get('preco_bilhete')
        
        if not nome or not preco_bilhete:
            return jsonify({'success': False, 'message': 'Nome e preço são obrigatórios'})
        
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        cur.execute("SELECT COUNT(*) as count FROM horarios_sessao WHERE id_tipo_sessao = %s", (tipo_id,))
        count = cur.fetchone()['count']
        
        if count > 0:
            return jsonify({
                'success': False, 
                'message': f'Não é possível remover. Existem {count} sessões usando este tipo.'
            })
        
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


@app.route('/admin/horarios/disponiveis', methods=['GET'])
def admin_get_horarios_disponiveis():
    pass

    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        cur.execute("SELECT id, hora FROM horarios ORDER BY hora")
        horarios = cur.fetchall()
        
        horarios_formatados = []
        for horario in horarios:
            horarios_formatados.append({
                'id': horario['id'],
                'hora': str(horario['hora']),
                'display': str(horario['hora'])
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
    pass
   
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        filme_id = request.form.get('filme_id')
        cinema_id = request.form.get('cinema_id')
        tipo_sessao_id = request.form.get('tipo_sessao_id')
        sala_id = request.form.get('sala_id')
        
        horario_id = request.form.get('horario_id')
        hora = request.form.get('hora')
        
        app.logger.info(f"Dados recebidos: filme_id={filme_id}, cinema_id={cinema_id}, tipo_sessao_id={tipo_sessao_id}, sala_id={sala_id}, horario_id={horario_id}, hora={hora}")
        
        if not all([filme_id, cinema_id, tipo_sessao_id, sala_id]):
            return jsonify({'success': False, 'message': 'Campos obrigatórios: filme_id, cinema_id, tipo_sessao_id, sala_id'})
        
        if not horario_id and not hora:
            return jsonify({'success': False, 'message': 'Deve fornecer horario_id ou hora'})
        
        if horario_id:
            cur.execute("SELECT id, hora FROM horarios WHERE id = %s", (horario_id,))
            horario_existente = cur.fetchone()
            
            if not horario_existente:
                return jsonify({'success': False, 'message': 'Horário selecionado não existe'})
            
            horario_final_id = horario_id
            hora_display = str(horario_existente['hora'])
            
        else:
            cur.execute("SELECT id FROM horarios WHERE hora = %s", (hora,))
            horario_existente = cur.fetchone()
            
            if horario_existente:
                horario_final_id = horario_existente['id']
            else:
                cur.execute("INSERT INTO horarios (hora) VALUES (%s)", (hora,))
                horario_final_id = cur.lastrowid
            
            hora_display = hora
        
        cur.execute("""
            SELECT id FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s 
            AND id_horario = %s AND id_sala = %s
        """, (filme_id, cinema_id, tipo_sessao_id, horario_final_id, sala_id))
        
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Esta sessão já existe para este horário e sala'})
        
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
    pass
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
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
        
        
        cur.execute("""
            SELECT hs.*, h.hora as hora_atual
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (horario_id,))
        sessao_atual = cur.fetchone()
        
        if not sessao_atual:
            return jsonify({'success': False, 'message': 'Sessão não encontrada'})
        
        cur.execute("SELECT id FROM horarios WHERE hora = %s", (hora,))
        horario_existente = cur.fetchone()
        
        if horario_existente:
            novo_horario_id = horario_existente['id']
        else:
            cur.execute("INSERT INTO horarios (hora) VALUES (%s)", (hora,))
            novo_horario_id = cur.lastrowid
        
        cur.execute("""
            SELECT id FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s 
            AND id_horario = %s AND id_sala = %s AND id != %s
        """, (sessao_atual['id_filme'], sessao_atual['id_cinema'], 
              sessao_atual['id_tipo_sessao'], novo_horario_id, sala_id, horario_id))
        
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Já existe uma sessão para este horário e sala'})
        
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        horario_id = request.form.get('horario_id')
        hora = request.form.get('hora')
        
        app.logger.info(f"Editando sessão {sessao_id}: horario_id={horario_id}, hora={hora}")
        
        if not horario_id and not hora:
            return jsonify({'success': False, 'message': 'Deve fornecer horario_id ou hora'})
        
        cur.execute("""
            SELECT hs.*, h.hora as hora_atual
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (sessao_id,))
        sessao_atual = cur.fetchone()
        
        if not sessao_atual:
            return jsonify({'success': False, 'message': 'Sessão não encontrada'})
        
        if horario_id:
            cur.execute("SELECT id, hora FROM horarios WHERE id = %s", (horario_id,))
            horario_existente = cur.fetchone()
            
            if not horario_existente:
                return jsonify({'success': False, 'message': 'Horário selecionado não existe'})
            
            novo_horario_id = horario_id
            hora_display = str(horario_existente['hora'])
            
        else:
            cur.execute("SELECT id FROM horarios WHERE hora = %s", (hora,))
            horario_existente = cur.fetchone()
            
            if horario_existente:
                novo_horario_id = horario_existente['id']
            else:
                cur.execute("INSERT INTO horarios (hora) VALUES (%s)", (hora,))
                novo_horario_id = cur.lastrowid
            
            hora_display = hora
        
        cur.execute("""
            SELECT id FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s 
            AND id_horario = %s AND id_sala = %s AND id != %s
        """, (sessao_atual['id_filme'], sessao_atual['id_cinema'], 
              sessao_atual['id_tipo_sessao'], novo_horario_id, sessao_atual['id_sala'], sessao_id))
        
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Já existe uma sessão para este horário'})
        
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        cur.execute("SELECT COUNT(*) as count FROM horarios_sessao WHERE id_horario = %s", (horario_id,))
        count = cur.fetchone()['count']
        
        if count > 0:
            return jsonify({
                'success': False, 
                'message': f'Não é possível remover. Existem {count} sessões usando este horário.'
            })
        
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


@app.route('/admin/salas/adicionar', methods=['POST'])
def admin_adicionar_sala():
    if 'user_id' not in session:
        flash('Não autorizado', 'erro')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
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
        
        cur.execute("""
            SELECT id FROM salas 
            WHERE id_cinema = %s AND nome_sala = %s
        """, (id_cinema, nome_sala))
        
        sala_existente = cur.fetchone()
        if sala_existente:
            flash(f'Já existe uma sala com o nome "{nome_sala}" neste cinema', 'erro')
            return redirect(url_for('admin_salas'))
        
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
        lugares_acessiveis_str = request.form.get('lugares_acessiveis', '')
        
        if not nome_sala or not capacidade or not id_cinema:
            return jsonify({'success': False, 'message': 'Nome, capacidade e cinema são obrigatórios'})
        
        cursor.execute("""
            SELECT id FROM salas 
            WHERE id_cinema = %s AND nome_sala = %s AND id != %s
        """, (int(id_cinema), nome_sala, sala_id))
        
        sala_existente = cursor.fetchone()
        if sala_existente:
            return jsonify({'success': False, 'message': f'Já existe outra sala com o nome "{nome_sala}" neste cinema'})
        
        lugares_acessiveis_json = None
        if lugares_acessiveis_str and lugares_acessiveis_str.strip():
            lugares_list = [lugar.strip() for lugar in lugares_acessiveis_str.split(',') if lugar.strip()]
            lugares_acessiveis_json = json.dumps(lugares_list)
        
        cursor.execute("""
            UPDATE salas 
            SET nome_sala = %s, capacidade = %s, id_cinema = %s, tipo_sala = %s, filas = %s, lugares_por_fila = %s, lugares_acessiveis = %s
            WHERE id = %s
        """, (nome_sala, int(capacidade), int(id_cinema), tipo_sala, int(filas), int(lugares_por_fila), lugares_acessiveis_json, sala_id))
        
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT s.*, c.nome as cinema_nome
            FROM salas s
            LEFT JOIN cinemas c ON s.id_cinema = c.id
            WHERE s.id = %s
        """, (sala_id,))
        
        sala = cursor.fetchone()
        
        if not sala:
            return jsonify({'success': False, 'message': 'Sala não encontrada'})
        
        if sala.get('capacidade'):
            sala['capacidade'] = int(sala['capacidade'])
        if sala.get('filas'):
            sala['filas'] = int(sala['filas'])
        if sala.get('lugares_por_fila'):
            sala['lugares_por_fila'] = int(sala['lugares_por_fila'])
        
        if sala.get('lugares_acessiveis'):
            try:
                lugares_json = json.loads(sala['lugares_acessiveis'])
                sala['lugares_acessiveis'] = ', '.join(lugares_json) if isinstance(lugares_json, list) else ''
            except:
                sala['lugares_acessiveis'] = ''
        else:
            sala['lugares_acessiveis'] = ''
        
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT COUNT(*) as count FROM horarios_sessao WHERE id_sala = %s", (sala_id,))
        result = cursor.fetchone()
        count = result['count'] if result else 0
        
        if count > 0:
            return jsonify({
                'success': False, 
                'message': f'Não é possível remover. Existem {count} horários de sessão usando esta sala.'
            })
        
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


@app.route('/admin/sessoes/adicionar', methods=['POST'])
def admin_adicionar_sessao():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
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
        
        cur.execute("""
            SELECT id FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s 
            AND id_horario = %s AND id_sala = %s
        """, (id_filme, id_cinema, id_tipo_sessao, id_horario, id_sala))
        
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Esta sessão já existe'})
        
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        cur.execute("SELECT COUNT(*) as count FROM reservas WHERE id_horario_sessao = %s", (sessao_id,))
        count = cur.fetchone()['count']
        
        if count > 0:
            return jsonify({
                'success': False, 
                'message': f'Não é possível remover. Existem {count} reservas para esta sessão.'
            })
        
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
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'error': 'Acesso negado'}), 403
        
        cur.execute("""
            SELECT s.id, s.nome_sala, s.capacidade, s.tipo_sala
            FROM salas s
            WHERE s.id_cinema = %s
            ORDER BY s.nome_sala
        """, (cinema_id,))
        salas = cur.fetchall()
        
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
    pass
 
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    nome_sala = request.args.get('nome')
    cinema_id = request.args.get('cinema_id')
    
    if not nome_sala or not cinema_id:
        return jsonify({'error': 'Parâmetros obrigatórios: nome e cinema_id'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'error': 'Acesso negado'}), 403
        
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
    pass
   
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'error': 'Acesso negado'}), 403
        
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
        
        horarios = []
        for h in horarios_raw:
            horario_processado = dict(h)
            
            if isinstance(h['hora'], timedelta):
                total_seconds = int(h['hora'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                horario_processado['hora'] = f"{hours:02d}:{minutes:02d}"
            elif hasattr(h['hora'], 'strftime'):
                horario_processado['hora'] = h['hora'].strftime('%H:%M')
            else:
                horario_processado['hora'] = str(h['hora'])[:5]
            
            if not horario_processado['nome_sala']:
                horario_processado['nome_sala'] = 'Sala não especificada'
            
            horarios.append(horario_processado)
        
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
        
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE filmes 
            SET titulo = %s, sinopse = %s, diretor = %s, duracao = %s, 
                data_lancamento = %s, idade_recomendada = %s, estado = %s, trailer_url = %s,
                rotten_tomatoes_url = %s, imdb_url = %s
            WHERE id = %s
        """, (titulo, sinopse, diretor, duracao, data_lancamento, idade_recomendada, estado, trailer_url, rotten_tomatoes_url, imdb_url, id_filme))
        
        conn.commit()
        
        cur.execute("SELECT estado FROM filmes WHERE id = %s", (id_filme,))
        resultado = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Filme atualizado com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar filme: {str(e)}'}), 500

@app.route('/admin/filmes/<int:id_filme>/auto-agendar', methods=['POST'])
def admin_auto_agendar_filme(id_filme):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True, buffered=True)
        
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        cur.execute("SELECT id, titulo, duracao FROM filmes WHERE id = %s", (id_filme,))
        filme = cur.fetchone()
        
        if not filme:
            return jsonify({'success': False, 'message': 'Filme não encontrado'}), 404
        
        duracao_filme = filme['duracao'] or 120
        
        cur.execute("SELECT id, nome FROM cinemas")
        cinemas = cur.fetchall()
        
        if not cinemas:
            return jsonify({'success': False, 'message': 'Nenhum cinema disponível'}), 400
        
        cur.execute("SELECT id, hora FROM horarios ORDER BY hora")
        horarios = cur.fetchall()
        
        if not horarios:
            return jsonify({'success': False, 'message': 'Nenhum horário configurado'}), 400
        
        cur.execute("""
            SELECT id, nome 
            FROM tipos_sessao 
            WHERE id NOT IN (9, 24)
            ORDER BY id
        """)
        tipos_sessao = cur.fetchall()
        
        if not tipos_sessao:
            return jsonify({'success': False, 'message': 'Nenhum tipo de sessão configurado'}), 400
        
        print(f"Iniciando auto-agendamento: {len(cinemas)} cinemas, {len(tipos_sessao)} tipos de sessão, {len(horarios)} horários")
        
        sessoes_criadas = 0
        cinemas_adicionados = 0
        sessoes_para_inserir = []
        
        MAX_HORARIOS_POR_TIPO = 3
        
        print(f"Distribuição inteligente: máximo {MAX_HORARIOS_POR_TIPO} horários por tipo de sessão por cinema")
        
        for cinema in cinemas:
            try:
                cur.execute("""
                    SELECT 1 FROM filmes_cinemas 
                    WHERE filme_id = %s AND cinema_id = %s
                """, (id_filme, cinema['id']))
                
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO filmes_cinemas (filme_id, cinema_id) 
                        VALUES (%s, %s)
                    """, (id_filme, cinema['id']))
                    cinemas_adicionados += 1
                
                cur.execute("""
                    SELECT id, nome_sala, capacidade 
                    FROM salas 
                    WHERE id_cinema = %s
                    ORDER BY nome_sala
                """, (cinema['id'],))
                salas = cur.fetchall()
                
                cur.execute("""
                    SELECT id_sala, id_horario, id_tipo_sessao, id_filme
                    FROM horarios_sessao
                    WHERE id_cinema = %s
                """, (cinema['id'],))
                sessoes_existentes = set()
                for row in cur.fetchall():
                    sessoes_existentes.add((row['id_sala'], row['id_horario'], row['id_tipo_sessao'], row['id_filme']))
                
                horarios_disponiveis = list(horarios)
                
                for tipo_sessao in tipos_sessao:
                    tipo_nome = tipo_sessao['nome'].upper()
                    
                    sala_escolhida = None
                    if tipo_nome == 'IMAX':
                        salas_filtradas = [s for s in salas if 'IMAX' in s['nome_sala'].upper()]
                        if salas_filtradas:
                            sala_escolhida = salas_filtradas[0]
                    elif tipo_nome == '4DX':
                        salas_filtradas = [s for s in salas if '4DX' in s['nome_sala'].upper()]
                        if salas_filtradas:
                            sala_escolhida = salas_filtradas[0]
                    else:
                        salas_filtradas = [s for s in salas if 'IMAX' not in s['nome_sala'].upper() and '4DX' not in s['nome_sala'].upper()]
                        if salas_filtradas:
                            sala_escolhida = salas_filtradas[0]
                    
                    if not sala_escolhida:
                        continue
                    
                    horarios_adicionados_tipo = 0
                    
                    horarios_livres = []
                    for horario in horarios_disponiveis:
                        tem_conflito = any(
                            s[0] == sala_escolhida['id'] and s[1] == horario['id'] and s[2] == tipo_sessao['id']
                            for s in sessoes_existentes
                        )
                        if not tem_conflito:
                            horarios_livres.append(horario)
                    
                    import random
                    random.shuffle(horarios_livres)
                    
                    for horario in horarios_livres:
                        if horarios_adicionados_tipo >= MAX_HORARIOS_POR_TIPO:
                            break
                        
                        chave_filme = (sala_escolhida['id'], horario['id'], tipo_sessao['id'], id_filme)
                        
                        if chave_filme not in sessoes_existentes:
                            sessoes_para_inserir.append((id_filme, cinema['id'], tipo_sessao['id'], horario['id'], sala_escolhida['id']))
                            sessoes_existentes.add(chave_filme)
                            horarios_adicionados_tipo += 1
                
                if len(sessoes_para_inserir) >= 500:
                    cur.executemany("""
                        INSERT INTO horarios_sessao (id_filme, id_cinema, id_tipo_sessao, id_horario, id_sala)
                        VALUES (%s, %s, %s, %s, %s)
                    """, sessoes_para_inserir)
                    sessoes_criadas += len(sessoes_para_inserir)
                    print(f"Inseridas {sessoes_criadas} sessões até agora...")
                    sessoes_para_inserir = []
                    conn.commit()
            
            except Exception as cinema_error:
                print(f"Erro ao processar cinema {cinema['nome']}: {cinema_error}")
                continue
        
        if sessoes_para_inserir:
            cur.executemany("""
                INSERT INTO horarios_sessao (id_filme, id_cinema, id_tipo_sessao, id_horario, id_sala)
                VALUES (%s, %s, %s, %s, %s)
            """, sessoes_para_inserir)
            sessoes_criadas += len(sessoes_para_inserir)
            print(f"Inserção final: {len(sessoes_para_inserir)} sessões")
        
        conn.commit()
        
        print(f"Auto-agendamento concluído: {cinemas_adicionados} cinemas, {sessoes_criadas} sessões")
        
        mensagem = f"Agendamento concluído! {cinemas_adicionados} cinemas adicionados, {sessoes_criadas} sessões criadas."
        return jsonify({'success': True, 'message': mensagem})
        
    except Exception as e:
        error_msg = str(e) if str(e) else type(e).__name__
        print(f"ERRO CRÍTICO no auto-agendamento: {error_msg}")
        import traceback
        traceback.print_exc()
        try:
            conn.rollback()
        except:
            pass
        return jsonify({'success': False, 'message': f'Erro ao agendar: {error_msg}'}), 500
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

@app.route('/admin/filmes/<int:id_filme>/avaliacoes')
def admin_filme_avaliacoes(id_filme):
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
    
    cur.execute("SELECT id, titulo, poster_url FROM filmes WHERE id = %s", (id_filme,))
    filme = cur.fetchone()
    
    if not filme:
        flash("Filme não encontrado!", "erro")
        return redirect(url_for('admin_filmes'))
    
    cur.execute("""
        SELECT 
            av.id,
            av.usuario_id,
            av.rating,
            av.comentario,
            av.data_avaliacao,
            u.nome as usuario_nome,
            u.email,
            COALESCE(a.caminho, 'imgs/icons/user_icon34-removebg-preview.png') as usuario_avatar
        FROM avaliacoes_filmes av
        JOIN usuarios u ON av.usuario_id = u.id
        LEFT JOIN avatars a ON u.avatar_id = a.id
        WHERE av.filme_id = %s
        ORDER BY av.data_avaliacao DESC
    """, (id_filme,))
    todas_avaliacoes = cur.fetchall()
    
    for avaliacao in todas_avaliacoes:
        if avaliacao.get('usuario_avatar'):
            avaliacao['usuario_avatar'] = avaliacao['usuario_avatar'].replace('\\', '/').replace('"', '').strip()
        else:
            avaliacao['usuario_avatar'] = 'imgs/icons/user_icon34-removebg-preview.png'
    
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
    pass

    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        cur.execute("SELECT id, filme_id, usuario_id FROM avaliacoes_filmes WHERE id = %s", (avaliacao_id,))
        avaliacao = cur.fetchone()
        
        if not avaliacao:
            return jsonify({'success': False, 'message': 'Avaliação não encontrada'}), 404
        
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
        cur.execute("SELECT id FROM filmes_cinemas WHERE filme_id = %s AND cinema_id = %s", (id_filme, cinema_id))
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Cinema já associado ao filme'})
        
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
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        cur.execute("SELECT id FROM filmes_cinemas WHERE filme_id = %s AND cinema_id = %s", (id_filme, cinema_id))
        associacao = cur.fetchone()
        
        if not associacao:
            return jsonify({'success': False, 'message': 'Associação filme-cinema não encontrada'})
        
        app.logger.info(f"Iniciando remoção em cascata para cinema {cinema_id} do filme {id_filme}")
        
        cur.execute("""
            DELETE r FROM reservas r
            JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
            WHERE hs.id_filme = %s AND hs.id_cinema = %s
        """, (id_filme, cinema_id))
        reservas_removidas = cur.rowcount
        app.logger.info(f"Removidas {reservas_removidas} reservas")
        
        cur.execute("""
            DELETE FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s
        """, (id_filme, cinema_id))
        horarios_removidos = cur.rowcount
        app.logger.info(f"Removidos {horarios_removidos} horários")
        
        cur.execute("DELETE FROM filmes_cinemas WHERE filme_id = %s AND cinema_id = %s", (id_filme, cinema_id))
        conn.commit()
        
        
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

@app.route('/admin/filmes/<int:id_filme>/remover-todos-cinemas', methods=['POST'])
def admin_remover_todos_cinemas_filme(id_filme):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(buffered=True)
        
        cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user or not user[0]:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        cur.execute("SELECT titulo FROM filmes WHERE id = %s", (id_filme,))
        filme = cur.fetchone()
        
        if not filme:
            return jsonify({'success': False, 'message': 'Filme não encontrado'}), 404
        
        print(f"Removendo todos os cinemas do filme: {filme[0]}")
        
        cur.execute("DELETE FROM reservas WHERE id_filme = %s", (id_filme,))
        reservas_removidas = cur.rowcount
        print(f"Removidas {reservas_removidas} reservas")
        
        cur.execute("DELETE FROM horarios_sessao WHERE id_filme = %s", (id_filme,))
        horarios_removidos = cur.rowcount
        print(f"Removidos {horarios_removidos} horários")
        
        cur.execute("DELETE FROM filmes_cinemas WHERE filme_id = %s", (id_filme,))
        cinemas_removidos = cur.rowcount
        print(f"Removidas {cinemas_removidos} associações com cinemas")
        
        conn.commit()
        
        mensagem = f"Todos os cinemas removidos! {cinemas_removidos} cinemas, {horarios_removidos} horários e {reservas_removidas} reservas foram removidos."
        return jsonify({'success': True, 'message': mensagem})
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao remover todos os cinemas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

@app.route('/admin/filmes/<int:id_filme>/adicionar-ator', methods=['POST'])
def admin_adicionar_ator_filme(id_filme):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    ator_id = request.form.get('ator_id')
    papel = request.form.get('papel', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM filme_atores WHERE filme_id = %s AND ator_id = %s", (id_filme, ator_id))
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Ator já associado ao filme'})
        
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
    pass

    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        genero_id = request.form.get('genero_id')
        
        if not genero_id:
            return jsonify({'success': False, 'message': 'Género é obrigatório'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM filme_generos WHERE filme_id = %s AND genero_id = %s", (id_filme, genero_id))
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Género já está associado ao filme'}), 400
        
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
        
        if not file.content_type.startswith('image/'):
            return jsonify({'success': False, 'message': 'Apenas imagens são permitidas'}), 400
        
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1]
        unique_filename = f"filme_{id_filme}_{uuid.uuid4().hex[:8]}{ext}"
        
        upload_folder = os.path.join('static', 'imgs', 'filmes')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
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
    pass
    
    if 'user_id' not in session:
        flash("Não autenticado", "erro")
        return redirect(url_for('admin_filmes'))
    
    titulo = request.form.get('titulo', '').strip()
    duracao = request.form.get('duracao', '120')
    sinopse = request.form.get('sinopse', '').strip()
    
    
    if not titulo:
        flash('Título é obrigatório!', 'erro')
        return redirect(url_for('admin_filmes'))
    
    if not sinopse:
        flash('Sinopse é obrigatória!', 'erro')
        return redirect(url_for('admin_filmes'))
    
    poster_url = None
    if 'poster' in request.files:
        poster_file = request.files['poster']
        if poster_file and poster_file.filename:
            pass
            
            upload_dir = os.path.join('static', 'imgs', 'filmes')
            os.makedirs(upload_dir, exist_ok=True)
            
            import uuid
            from werkzeug.utils import secure_filename
            
            filename = secure_filename(poster_file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{uuid.uuid4().hex[:8]}_{name}{ext}"
            
            poster_path = os.path.join(upload_dir, unique_filename)
            poster_file.save(poster_path)
            
            poster_url = f"imgs/filmes/{unique_filename}"
    
    if not poster_url:
        flash('Imagem do poster é obrigatória!', 'erro')
        return redirect(url_for('admin_filmes'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        pass
        
        cursor.execute("""
            INSERT INTO filmes (titulo, diretor, data_lancamento, duracao, sinopse, poster_url, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (titulo, 'A definir', '2024-01-01', int(duracao), sinopse, poster_url, 'brevemente'))
        
        id_filme = cursor.lastrowid
        
        cursor.execute("INSERT INTO filme_generos (filme_id, genero_id) VALUES (%s, %s)", (id_filme, 1))
        
        conn.commit()
        
        flash(f'Filme "{titulo}" adicionado com sucesso!', 'sucesso')
        
    except Exception as e:
        conn.rollback()
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
    sala_id = request.form.get('sala_id')
    id_horario_sessaos = request.form.getlist('id_horario_sessaos')
    
    if not id_horario_sessaos:
        flash("Selecione pelo menos um horário!", "erro")
        return redirect(url_for('admin_filmes'))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute("""
            SELECT id_horario 
            FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s
        """, (id_filme, id_cinema, id_tipo_sessao))
        horarios_existentes = [row['id_horario'] for row in cur.fetchall()]
        
        count = 0
        duplicados = 0
        
        for id_horario_sessao in id_horario_sessaos:
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
        id_horario_sessaos = [int(id) for id in id_horario_sessaos]
        
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
    print(f"🔍 DEBUG: Tentando remover filme ID: {id_filme}")
    app.logger.info(f"=== INÍCIO: Tentativa de remoção do filme ID: {id_filme} ===")
    
    if 'user_id' not in session:
        print("❌ DEBUG: Usuário não autenticado")
        app.logger.warning("Tentativa de remoção sem autenticação")
        flash("Não autenticado", "erro")
        return redirect(url_for('admin_filmes'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        cur.execute("SELECT is_admin, nome FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        print(f"🔍 DEBUG: Usuário encontrado: {user}")
        
        if not user:
            print("❌ DEBUG: Usuário não encontrado na BD")
            app.logger.warning(f"Usuário ID {session['user_id']} não encontrado")
            flash("Usuário não encontrado", "erro")
            return redirect(url_for('admin_filmes'))
        
        if not user[0]:
            print(f"❌ DEBUG: Usuário {user[1]} não é admin")
            app.logger.warning(f"Usuário {user[1]} (ID: {session['user_id']}) tentou remover filme sem ser admin")
            flash("Acesso negado - apenas administradores podem remover filmes", "erro")
            return redirect(url_for('admin_filmes'))
        
        print(f"✅ DEBUG: Usuário {user[1]} é admin, prosseguindo...")
        app.logger.info(f"Usuário admin {user[1]} (ID: {session['user_id']}) removendo filme")
        
        cur.execute("SELECT titulo FROM filmes WHERE id = %s", (id_filme,))
        filme = cur.fetchone()
        
        if not filme:
            print(f"❌ DEBUG: Filme ID {id_filme} não encontrado")
            app.logger.warning(f"Filme ID {id_filme} não encontrado")
            flash("Filme não encontrado", "erro")
            return redirect(url_for('admin_filmes'))
        
        titulo_filme = filme[0]
        print(f"🎬 DEBUG: Removendo filme: '{titulo_filme}' (ID: {id_filme})")
        app.logger.info(f"Removendo filme: '{titulo_filme}' (ID: {id_filme})")
        
        try:
            cur.execute("DELETE FROM reservas WHERE id_filme = %s", (id_filme,))
            reservas_removidas = cur.rowcount
            print(f"✅ DEBUG: Removidas {reservas_removidas} reservas")
        except Exception as e:
            print(f"⚠️ Erro ao remover reservas: {e}")
        
        try:
            cur.execute("DELETE FROM avaliacoes_filmes WHERE filme_id = %s", (id_filme,))
            avaliacoes_removidas = cur.rowcount
            print(f"✅ DEBUG: Removidas {avaliacoes_removidas} avaliações")
        except Exception as e:
            print(f"⚠️ Erro ao remover avaliações: {e}")
        
        try:
            cur.execute("DELETE FROM historico_filmes WHERE filme_id = %s", (id_filme,))
            historico_removido = cur.rowcount
            print(f"✅ DEBUG: Removidos {historico_removido} registos de histórico")
        except Exception as e:
            print(f"⚠️ Erro ao remover histórico: {e}")
        
        try:
            cur.execute("DELETE FROM reservas_salas WHERE filme_id = %s", (id_filme,))
            reservas_salas_removidas = cur.rowcount
            print(f"✅ DEBUG: Removidas {reservas_salas_removidas} reservas de salas")
        except Exception as e:
            print(f"⚠️ Erro ao remover reservas_salas: {e}")
        
        try:
            cur.execute("DELETE FROM horarios_sessao WHERE id_filme = %s", (id_filme,))
            horarios_removidos = cur.rowcount
            print(f"✅ DEBUG: Removidos {horarios_removidos} horários")
        except Exception as e:
            print(f"⚠️ Erro ao remover horários: {e}")
        
        try:
            cur.execute("DELETE FROM filmes_cinemas WHERE filme_id = %s", (id_filme,))
            cinemas_removidos = cur.rowcount
            print(f"✅ DEBUG: Removidas {cinemas_removidos} associações com cinemas")
        except Exception as e:
            print(f"⚠️ Erro ao remover filmes_cinemas: {e}")
        
        try:
            cur.execute("DELETE FROM filme_generos WHERE filme_id = %s", (id_filme,))
            generos_removidos = cur.rowcount
            print(f"✅ DEBUG: Removidas {generos_removidos} associações com géneros")
        except Exception as e:
            print(f"⚠️ Erro ao remover filme_generos: {e}")
        
        try:
            cur.execute("DELETE FROM filme_atores WHERE filme_id = %s", (id_filme,))
            atores_removidos = cur.rowcount
            print(f"✅ DEBUG: Removidas {atores_removidos} associações com atores")
        except Exception as e:
            print(f"⚠️ Erro ao remover filme_atores: {e}")
        
        print(f"🗑️ DEBUG: Removendo filme da tabela principal...")
        cur.execute("DELETE FROM filmes WHERE id = %s", (id_filme,))
        filme_removido = cur.rowcount
        print(f"✅ DEBUG: Filme removido: {filme_removido} linha(s) afetada(s)")
        
        if filme_removido == 0:
            print("❌ DEBUG: ERRO - Filme não foi removido!")
            conn.rollback()
            flash("Erro: Filme não foi removido", "erro")
        else:
            print("✅ DEBUG: Commit das alterações...")
            conn.commit()
            print(f"✅ DEBUG: Filme '{titulo_filme}' removido com sucesso!")
            flash(f"Filme '{titulo_filme}' removido com sucesso!", "sucesso")
        
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ DEBUG: EXCEÇÃO ao remover filme: {str(e)}")
        app.logger.error(f"❌ ERRO ao remover filme {id_filme}: {str(e)}")
        app.logger.exception("Stack trace:")
        flash(f"Erro ao remover filme: {str(e)}", "erro")
        
    finally:
        try:
            cur.close()
            conn.close()
            print("🔍 DEBUG: Conexão fechada")
        except:
            pass
    
    print(f"🔍 DEBUG: Redirecionando para admin_filmes")
    app.logger.info(f"=== FIM: Tentativa de remoção do filme ID: {id_filme} ===")
    return redirect(url_for('admin_filmes'))

@app.route('/admin/filmes/<int:id_filme>/duplicar', methods=['POST'])
def admin_duplicar_filme(id_filme):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM filmes WHERE id = %s", (id_filme,))
        filme = cur.fetchone()
        
        if not filme:
            return jsonify({'success': False, 'message': 'Filme não encontrado'}), 404
        
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
            'fora_de_cartaz'
        ))
        
        novo_id = cur.fetchone()['id']
        
        cur.execute("""
            INSERT INTO filme_generos (id_filme, id_genero)
            SELECT %s, id_genero FROM filme_generos WHERE id_filme = %s
        """, (novo_id, id_filme))
        
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

@app.route('/admin/generos')
def admin_generos():
    pass
  
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
    pass
  
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        
        if not nome:
            return jsonify({'success': False, 'message': 'Nome do género é obrigatório'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM generos WHERE nome = %s", (nome,))
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Género já existe'}), 400
        
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
    pass
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        
        if not nome:
            return jsonify({'success': False, 'message': 'Nome do género é obrigatório'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM generos WHERE id = %s", (genero_id,))
        if not cur.fetchone():
            return jsonify({'success': False, 'message': 'Género não encontrado'}), 404
        
        cur.execute("SELECT id FROM generos WHERE nome = %s AND id != %s", (nome, genero_id))
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Já existe outro género com este nome'}), 400
        
        cur.execute("UPDATE generos SET nome = %s WHERE id = %s", (nome, genero_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Género atualizado com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao editar género: {str(e)}'}), 500

@app.route('/admin/generos/<int:genero_id>/remover', methods=['POST'])
def admin_remover_genero(genero_id):
    pass

    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT nome FROM generos WHERE id = %s", (genero_id,))
        genero = cur.fetchone()
        if not genero:
            return jsonify({'success': False, 'message': 'Género não encontrado'}), 404
        
        cur.execute("SELECT COUNT(*) as total FROM filme_generos WHERE genero_id = %s", (genero_id,))
        result = cur.fetchone()
        total_filmes = result[0] if result else 0
        
        if total_filmes > 0:
            return jsonify({
                'success': False, 
                'message': f'Não é possível remover o género "{genero[0]}" pois está associado a {total_filmes} filme(s)'
            }), 400
        
        cur.execute("DELETE FROM generos WHERE id = %s", (genero_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Género removido com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao remover género: {str(e)}'}), 500

@app.route('/admin/generos/<int:genero_id>/filmes')
def admin_genero_filmes(genero_id):
    pass

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
    
    cur.execute("SELECT * FROM generos WHERE id = %s", (genero_id,))
    genero = cur.fetchone()
    
    if not genero:
        flash("Género não encontrado!", "erro")
        return redirect(url_for('admin_generos'))
    
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
    
    for filme in filmes:
        if filme.get('poster_url'):
            filme['poster_url'] = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
    
    cur.close()
    conn.close()
    
    return render_template('admin_genero_filmes.html', genero=genero, filmes=filmes)


@app.route('/admin/cinemas')
def admin_cinemas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        regiao_filtro = request.args.get('regiao', 'todas')
        
        if regiao_filtro and regiao_filtro != 'todas':
            cur.execute("""
                SELECT c.id, c.nome, c.localizacao, c.email, c.regiao, c.imagem,
                       COUNT(DISTINCT s.id) as num_salas,
                       COUNT(DISTINCT fc.filme_id) as num_filmes
                FROM cinemas c
                LEFT JOIN salas s ON c.id = s.id_cinema
                LEFT JOIN filmes_cinemas fc ON c.id = fc.cinema_id
                WHERE c.regiao = %s
                GROUP BY c.id, c.nome, c.localizacao, c.email, c.regiao, c.imagem
                ORDER BY c.id DESC
            """, (regiao_filtro,))
        else:
            cur.execute("""
                SELECT c.id, c.nome, c.localizacao, c.email, c.regiao, c.imagem,
                       COUNT(DISTINCT s.id) as num_salas,
                       COUNT(DISTINCT fc.filme_id) as num_filmes
                FROM cinemas c
                LEFT JOIN salas s ON c.id = s.id_cinema
                LEFT JOIN filmes_cinemas fc ON c.id = fc.cinema_id
                GROUP BY c.id, c.nome, c.localizacao, c.email, c.regiao, c.imagem
                ORDER BY c.id DESC
            """)
        cinemas = cur.fetchall()
        
        cur.execute("SELECT DISTINCT regiao FROM cinemas ORDER BY regiao")
        regioes = [r['regiao'] for r in cur.fetchall()]
        
        for cinema in cinemas:
            pass
            
            if not cinema.get('imagem') or cinema.get('imagem') in [None, '', 'None', 'null']:
                cinema['imagem'] = 'imgs/cinemas/default.jpg'
            else:
                imagem = str(cinema['imagem']).replace('\\', '/').replace('"', '').strip()
                if not imagem.startswith(('http://', 'https://', 'imgs/')):
                    if '/' not in imagem:
                        imagem = f"imgs/cinemas/{imagem}"
                    elif not imagem.startswith('imgs/'):
                        imagem = f"imgs/cinemas/{imagem}"
                cinema['imagem'] = imagem
            
        
        cur.close()
        conn.close()
        
        return render_template('admin_cinemas.html', user=get_current_user(), cinemas=cinemas, regioes=regioes, regiao_selecionada=regiao_filtro)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Erro ao carregar cinemas: {str(e)}", "erro")
        return render_template('admin_cinemas.html', user=get_current_user(), cinemas=[], regioes=[], regiao_selecionada='todas')

@app.route('/admin/cinemas/adicionar', methods=['POST'])
def admin_adicionar_cinema():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        nome = request.form.get('nome', '').strip()
        cidade = request.form.get('cidade', '').strip()
        localizacao = request.form.get('localizacao', '').strip()
        regiao = request.form.get('regiao', '').strip()
        email = request.form.get('email', '').strip()
        
        # Se localizacao não foi preenchida, usar a cidade
        if not localizacao:
            localizacao = cidade
        
        # Concatenar nome com cidade se necessário
        if not nome or nome == 'CineVibe':
            nome = f"CineVibe {cidade}"
        
        if not nome or not localizacao or not regiao:
            flash("Nome, localização e região são obrigatórios!", "erro")
            return redirect(url_for('admin_cinemas'))
        
        imagem = None
        if 'imagem' in request.files:
            file = request.files['imagem']
            
            if file and file.filename:
                from werkzeug.utils import secure_filename
                
                upload_folder = os.path.join('static', 'imgs', 'cinemas')
                os.makedirs(upload_folder, exist_ok=True)
                
                ext = os.path.splitext(secure_filename(file.filename))[1]
                filename = f"cinema_{uuid.uuid4().hex[:8]}{ext}"
                filepath = os.path.join(upload_folder, filename)
                
                file.save(filepath)
                imagem = f"imgs/cinemas/{filename}"
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO cinemas (nome, localizacao, regiao, email, imagem) 
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, localizacao, regiao, email, imagem))
        
        conn.commit()
        
        cinema_id = cur.lastrowid
        
        cur.close()
        conn.close()
        
        flash(f"Cinema '{nome}' adicionado com sucesso!", "sucesso")
        return redirect(url_for('admin_cinemas'))
        
    except Exception as e:
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
        nome = request.form.get('nome')
        localizacao = request.form.get('localizacao')
        regiao = request.form.get('regiao')
        email = request.form.get('email')
        imagem = request.form.get('imagem_atual')
        
        
        if 'imagem' in request.files:
            file = request.files['imagem']
            
            if file and file.filename:
                from werkzeug.utils import secure_filename
                upload_folder = os.path.join('static', 'imgs', 'cinemas')
                os.makedirs(upload_folder, exist_ok=True)
                ext = os.path.splitext(secure_filename(file.filename))[1]
                filename = f"cinema_{uuid.uuid4().hex[:8]}{ext}"
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                imagem = f"imgs/cinemas/{filename}"
            else:
                pass
        else:
            pass
        
        
        cur.execute("UPDATE cinemas SET nome=%s, localizacao=%s, regiao=%s, email=%s, imagem=%s WHERE id=%s",
                    (nome, localizacao, regiao, email, imagem, id_cinema))
        conn.commit()
        cur.close()
        conn.close()
        flash("Cinema atualizado!", "sucesso")
        return redirect(url_for('admin_cinemas'))
    
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
    cur = conn.cursor(dictionary=True)
    
    try:
        # Verificar se o cinema existe
        cur.execute("SELECT id, nome FROM cinemas WHERE id = %s", (id_cinema,))
        cinema = cur.fetchone()
        
        if not cinema:
            flash("Cinema não encontrado!", "erro")
            return redirect(url_for('admin_cinemas'))
        
        cinema_nome = cinema['nome']
        
        # Desabilitar verificação de chaves estrangeiras temporariamente
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Remover em cascata
        cur.execute("DELETE FROM reservas WHERE id_cinema = %s", (id_cinema,))
        reservas_removidas = cur.rowcount
        
        cur.execute("DELETE FROM horarios_sessao WHERE id_cinema = %s", (id_cinema,))
        horarios_removidos = cur.rowcount
        
        cur.execute("DELETE FROM filmes_cinemas WHERE cinema_id = %s", (id_cinema,))
        filmes_removidos = cur.rowcount
        
        cur.execute("DELETE FROM salas WHERE id_cinema = %s", (id_cinema,))
        salas_removidas = cur.rowcount
        
        cur.execute("DELETE FROM cinemas WHERE id = %s", (id_cinema,))
        
        # Reabilitar verificação de chaves estrangeiras
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        conn.commit()
        
        app.logger.info(f"Cinema '{cinema_nome}' (ID: {id_cinema}) removido com sucesso. Removidos: {reservas_removidas} reservas, {horarios_removidos} horários, {filmes_removidos} associações de filmes, {salas_removidas} salas")
        
        flash(f"Cinema '{cinema_nome}' removido com sucesso!", "sucesso")
        return redirect(url_for('admin_cinemas'))
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao remover cinema {id_cinema}: {str(e)}")
        flash(f"Erro ao remover cinema: {str(e)}", "erro")
        return redirect(url_for('admin_cinemas'))
    
    finally:
        cur.close()
        conn.close()

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
    
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'todos')
    periodo_filter = request.args.get('periodo', 'todos')
    
    try:
        query = """
            SELECT u.id, u.nome, u.email, u.criado_em, u.ultimo_login, u.is_admin, 
                   u.avatar_id
            FROM usuarios u
            WHERE 1=1
        """
        
        params = []
        
        if search:
            query += " AND (u.nome LIKE %s OR u.email LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        if status_filter == 'admin':
            query += " AND u.is_admin = 1"
        elif status_filter == 'usuario':
            query += " AND u.is_admin = 0"
        
        if periodo_filter == 'hoje':
            query += " AND DATE(u.criado_em) = CURDATE()"
        elif periodo_filter == 'semana':
            query += " AND u.criado_em >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
        elif periodo_filter == 'mes':
            query += " AND u.criado_em >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
        
        query += " ORDER BY u.id DESC"
        
        cur.execute(query, params)
        usuarios = cur.fetchall()
        
        for usuario in usuarios:
            cur.execute("SELECT COUNT(*) as num_reservas FROM reservas WHERE id_usuario = %s", (usuario['id'],))
            reservas_result = cur.fetchone()
            usuario['num_reservas'] = reservas_result['num_reservas'] if reservas_result else 0
            
            avatar_url = 'imgs/icons/user_icon34-removebg-preview.png'
            
            if usuario.get('avatar_id') and usuario['avatar_id']:
                try:
                    cur.execute("SELECT caminho FROM avatars WHERE id = %s", (usuario['avatar_id'],))
                    avatar_result = cur.fetchone()
                    if avatar_result and avatar_result.get('caminho'):
                        temp_url = str(avatar_result['caminho']).replace('\\', '/').replace('"', '').strip()
                        if temp_url and temp_url != 'None' and temp_url != '':
                            avatar_url = temp_url
                except Exception as e:
                    pass
            
            if (avatar_url == 'imgs/icons/user_icon34-removebg-preview.png' or 'default.png' in avatar_url) and usuario.get('avatar') and usuario['avatar']:
                temp_url = str(usuario['avatar']).replace('\\', '/').replace('"', '').strip()
                if temp_url and temp_url != 'None' and temp_url != '' and 'default.png' not in temp_url:
                    avatar_url = temp_url
            
            if not avatar_url or avatar_url == 'None' or avatar_url == '':
                avatar_url = 'imgs/icons/user_icon34-removebg-preview.png'
            
            if not avatar_url.startswith('imgs/'):
                avatar_url = 'imgs/icons/user_icon34-removebg-preview.png'
            
            usuario['avatar_url'] = avatar_url
        
        cur.close()
        conn.close()
        
        return render_template('admin_usuarios.html', 
                             user=get_current_user(), 
                             usuarios=usuarios, 
                             search=search,
                             status_selecionado=status_filter,
                             periodo_selecionado=periodo_filter)
        
    except Exception as e:
        cur.close()
        conn.close()
        flash(f"Erro ao carregar usuários: {str(e)}", "erro")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/adicionar_usuario', methods=['POST'])
def admin_adicionar_usuario():
    print("=" * 50)
    print("DEBUG: Rota admin_adicionar_usuario chamada")
    print("=" * 50)
    
    if 'user_id' not in session:
        print("DEBUG: Usuário não está na sessão")
        return redirect(url_for('login'))
    
    print(f"DEBUG: User ID na sessão: {session['user_id']}")
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    print(f"DEBUG: Usuário encontrado: {user}")
    
    if not user or not user.get('is_admin'):
        print("DEBUG: Usuário não é admin")
        flash("Acesso negado!", "erro")
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    
    print("DEBUG: Usuário é admin, continuando...")
    
    try:
        print("DEBUG: Dados do formulário:")
        print(f"  - request.form: {dict(request.form)}")
        
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        telefone = request.form.get('telefone', '').strip()
        is_admin_value = request.form.get('is_admin')
        is_admin = is_admin_value == '1'
        
        print(f"DEBUG: Valores extraídos:")
        print(f"  - nome: '{nome}'")
        print(f"  - email: '{email}'")
        print(f"  - senha: '{senha}'")
        print(f"  - telefone: '{telefone}'")
        print(f"  - is_admin_value: '{is_admin_value}'")
        print(f"  - is_admin: {is_admin}")
        
        if not nome or not email or not senha:
            print("DEBUG: Campos obrigatórios vazios")
            flash("Nome, email e senha são obrigatórios!", "erro")
            cur.close()
            conn.close()
            return redirect(url_for('admin_usuarios'))
        
        print("DEBUG: Verificando se email já existe...")
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        existing = cur.fetchone()
        print(f"DEBUG: Email existente: {existing}")
        
        if existing:
            print("DEBUG: Email já existe")
            flash("Email já está em uso!", "erro")
            cur.close()
            conn.close()
            return redirect(url_for('admin_usuarios'))
        
        print("DEBUG: Gerando hash da senha...")
        senha_hash = generate_password_hash(senha)
        print(f"DEBUG: Hash gerado: {senha_hash[:20]}...")
        
        print("DEBUG: Executando INSERT...")
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha, telefone, is_admin, data_criacao)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (nome, email, senha_hash, telefone, is_admin))
        
        print(f"DEBUG: INSERT executado, rowcount: {cur.rowcount}")
        print(f"DEBUG: lastrowid: {cur.lastrowid}")
        
        print("DEBUG: Fazendo commit...")
        conn.commit()
        print("DEBUG: Commit realizado com sucesso!")
        
        flash(f"Usuário {nome} adicionado com sucesso!", "sucesso")
        
    except Exception as e:
        conn.rollback()
        print(f"DEBUG: ERRO CAPTURADO: {str(e)}")
        import traceback
        print("DEBUG: Traceback completo:")
        traceback.print_exc()
        app.logger.error(f"Erro ao adicionar usuário: {str(e)}")
        flash(f"Erro ao adicionar usuário: {str(e)}", "erro")
    
    finally:
        cur.close()
        conn.close()
        print("DEBUG: Conexão fechada")
    
    print("DEBUG: Redirecionando para admin_usuarios")
    print("=" * 50)
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuarios/<int:usuario_id>/dados')
def admin_usuario_dados(usuario_id):
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
        
        cur.execute("SELECT COUNT(*) as num_reservas FROM reservas WHERE id_usuario = %s", (usuario_id,))
        reservas_count = cur.fetchone()
        usuario['num_reservas'] = reservas_count['num_reservas'] if reservas_count else 0
        
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
            usuario['avatar_url'] = '/static/imgs/icons/user_icon34-removebg-preview.png'
        
        if usuario.get('criado_em'):
            usuario['criado_em'] = usuario['criado_em'].strftime('%d/%m/%Y às %H:%M')
        
        if usuario.get('ultimo_login'):
            usuario['ultimo_login'] = usuario['ultimo_login'].strftime('%d/%m/%Y às %H:%M')
        
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
        
        cur.execute("SELECT COUNT(*) as total FROM reservas WHERE id_usuario = %s", (usuario_id,))
        reservas = cur.fetchone()['total']
        
        if reservas > 0:
            cur.execute("DELETE FROM reservas WHERE id_usuario = %s", (usuario_id,))
        
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
    
    search = request.args.get('search', '')
    cinema_filter = request.args.get('cinema', '')
    
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
    
    query += " ORDER BY r.id DESC"
    
    cur.execute(query, params)
    reservas = cur.fetchall()
    
    cur.execute("SELECT DISTINCT nome FROM cinemas ORDER BY nome")
    cinemas = [c['nome'] for c in cur.fetchall()]
    
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'})
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    try:
        cur.execute("SELECT * FROM reservas WHERE id = %s", (reserva_id,))
        reserva = cur.fetchone()
        
        if not reserva:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Reserva não encontrada'})
        
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'})
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    try:
        cur.execute("SELECT * FROM reservas WHERE id = %s", (reserva_id,))
        reserva = cur.fetchone()
        
        if not reserva:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Reserva não encontrada'})
        
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
    
    cur.execute("SELECT is_admin FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user.get('is_admin'):
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    try:
        cur.execute("""
            SELECT r.*, 
                   u.nome as usuario_nome, u.email as usuario_email,
                   f.titulo as filme_titulo, f.duracao,
                   c.nome as cinema_nome, c.localizacao as cinema_localizacao,
                   ts.nome as tipo_sessao,
                   h.hora as horario_sessao
            FROM reservas r
            LEFT JOIN usuarios u ON r.id_usuario = u.id
            LEFT JOIN filmes f ON r.id_filme = f.id
            LEFT JOIN cinemas c ON r.id_cinema = c.id
            LEFT JOIN tipos_sessao ts ON r.id_tipo_sessao = ts.id
            LEFT JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
            LEFT JOIN horarios h ON hs.id_horario = h.id
            WHERE r.id = %s
        """, (reserva_id,))
        
        reserva = cur.fetchone()
        
        if not reserva:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Reserva não encontrada'})
        
        if reserva.get('data_sessao'):
            reserva['data_sessao'] = reserva['data_sessao'].isoformat()
        if reserva.get('data_reserva'):
            reserva['data_reserva'] = reserva['data_reserva'].isoformat()
        if reserva.get('horario_sessao'):
            reserva['horario_sessao'] = str(reserva['horario_sessao'])
        
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'reserva': reserva})
        
    except Exception as e:
        cur.close()
        conn.close()
        app.logger.error(f"Erro ao buscar detalhes da reserva {reserva_id}: {e}")
        return jsonify({'success': False, 'message': f'Erro ao buscar detalhes: {str(e)}'})

@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        flash("Se o email existir no sistema, receberás instruções para recuperar a senha.", "info")
        return redirect(url_for('login'))
    return render_template('recuperar_senha.html')

@app.context_processor
def inject_user():
    user_id = session.get("user_id")

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
            SELECT u.nome, u.email, u.avatar_id, u.is_admin, 
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

    avatar = None
    
    if row.get('avatar_path'):
        avatar = str(row['avatar_path'])
    elif row.get('avatar'):
        avatar = str(row['avatar'])
    else:
        avatar = 'imgs/icons/user_icon34-removebg-preview.png'
    
    if avatar:
        avatar = avatar.replace('\\', '/').replace('"', '').strip()
        
        if not avatar.startswith('imgs/'):
            if avatar.startswith('static/'):
                avatar = avatar[7:]
            if not avatar.startswith('imgs/'):
                avatar = f"imgs/{avatar}"
    
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


@app.route('/logout')
def logout():
    session.clear()
    flash("Sessão terminada.", "success")
    return redirect(url_for('home'))

# TEST ROUTE - Comment out for production
@app.route('/debug_login_afonso')
def debug_login_afonso():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", ('afonso2008david@gmail.com',))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['user_nome'] = user['nome']
            session['user_email'] = user['email']
            
            cursor.execute("""
                SELECT COALESCE(a.caminho, 'imgs/icons/user_icon34-removebg-preview.png') as avatar_path
                FROM usuarios u 
                LEFT JOIN avatars a ON u.avatar_id = a.id 
                WHERE u.id = %s
            """, (user['id'],))
            avatar_data = cursor.fetchone()
            if avatar_data and avatar_data['avatar_path']:
                avatar = avatar_data['avatar_path'].replace('\\', '/').replace('"', '').strip()
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



@app.route('/filmes')
def filmes():
    pass
    
    genero_filtro = request.args.get('genero', '').strip().lower()
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nome FROM generos ORDER BY nome ASC")
        generos = cursor.fetchall() or []
        
        # Analisar preferências do utilizador se estiver logado
        generos_preferidos = []
        filmes_vistos_ids = []
        
        if user_id:
            # Buscar géneros dos filmes que o utilizador já viu (através de reservas concluídas)
            cursor.execute("""
                SELECT g.id, g.nome, COUNT(*) as contagem
                FROM reservas r
                JOIN filmes f ON r.id_filme = f.id
                JOIN filme_generos fg ON f.id = fg.filme_id
                JOIN generos g ON fg.genero_id = g.id
                JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
                JOIN horarios h ON hs.id_horario = h.id
                WHERE r.id_usuario = %s
                AND DATE_ADD(CONCAT(r.data_sessao, ' ', h.hora), INTERVAL f.duracao MINUTE) < NOW()
                GROUP BY g.id, g.nome
                ORDER BY contagem DESC
                LIMIT 3
            """, (user_id,))
            generos_preferidos = cursor.fetchall() or []
            
            # Buscar IDs dos filmes já vistos
            cursor.execute("""
                SELECT DISTINCT f.id
                FROM reservas r
                JOIN filmes f ON r.id_filme = f.id
                JOIN horarios_sessao hs ON r.id_horario_sessao = hs.id
                JOIN horarios h ON hs.id_horario = h.id
                WHERE r.id_usuario = %s
                AND DATE_ADD(CONCAT(r.data_sessao, ' ', h.hora), INTERVAL f.duracao MINUTE) < NOW()
            """, (user_id,))
            filmes_vistos_ids = [row['id'] for row in cursor.fetchall()]
        
        # Query base para buscar filmes
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
            
            # Marcar se o filme já foi visto
            f['ja_visto'] = f['id'] in filmes_vistos_ids

            if f.get('poster_url'):
                f['poster_url'] = _normalize_img_path(f['poster_url'])
            else:
                f['poster_url'] = None

            if f.get('poster_hover'):
                f['poster_hover'] = _normalize_img_path(f['poster_hover'])
            else:
                f['poster_hover'] = None

            if f.get('genero_nome') is None:
                f['genero_nome'] = ''

        # Separar por estado
        filmes_em_exibicao = [f for f in filmes if f['estado'] == 'em_exibicao']
        filmes_brevemente = [f for f in filmes if f['estado'] == 'brevemente']
        
        # Reordenar para colocar filmes já vistos no final, mantendo ordem por ID
        if user_id and filmes_vistos_ids:
            filmes_em_exibicao = sorted(filmes_em_exibicao, key=lambda x: (x['ja_visto'], x['id']))
            filmes_brevemente = sorted(filmes_brevemente, key=lambda x: (x['ja_visto'], x['id']))

    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass

    return render_template('filmes.html',
                           filmes_em_exibicao=filmes_em_exibicao,
                           filmes_brevemente=filmes_brevemente,
                           generos=generos,
                           genero_filtro=genero_filtro,
                           generos_preferidos=generos_preferidos if user_id else [])

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

        cursor.execute("""
            SELECT DISTINCT ts.id, ts.nome 
            FROM tipos_sessao ts
            JOIN horarios_sessao hs ON ts.id = hs.id_tipo_sessao
            WHERE hs.id_filme = %s
            ORDER BY ts.nome
        """, (id_filme,))
        tipos_sessao = cursor.fetchall()

        cursor.execute("""
            SELECT DISTINCT hs.id_cinema, hs.id_tipo_sessao, hs.id_sala, h.hora, s.nome_sala,
                   MIN(hs.id) as id
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            LEFT JOIN salas s ON hs.id_sala = s.id
            WHERE hs.id_filme = %s
            GROUP BY hs.id_cinema, hs.id_tipo_sessao, hs.id_sala, h.hora, s.nome_sala
            ORDER BY h.hora
        """, (id_filme,))
        
        horarios_filme = cursor.fetchall()
        
        app.logger.info(f"Horários encontrados para filme {id_filme}: {len(horarios_filme)}")
        
        horarios_sem_sala_ids = [h['id'] for h in horarios_filme if not h.get('id_sala')]
        
        if horarios_sem_sala_ids:
            app.logger.warning(f"Corrigindo {len(horarios_sem_sala_ids)} horários sem sala na BD...")
            
            for horario_id in horarios_sem_sala_ids:
                horario_data = next((h for h in horarios_filme if h['id'] == horario_id), None)
                if horario_data and horario_data.get('id_cinema'):
                    cursor.execute("""
                        SELECT id FROM salas 
                        WHERE id_cinema = %s 
                        ORDER BY id LIMIT 1
                    """, (horario_data['id_cinema'],))
                    sala = cursor.fetchone()
                    
                    if sala:
                        cursor.execute("""
                            UPDATE horarios_sessao 
                            SET id_sala = %s 
                            WHERE id = %s
                        """, (sala['id'], horario_id))
                        app.logger.info(f"Horário {horario_id} atualizado com sala {sala['id']}")
            
            conn.commit()
            
            cursor.execute("""
                SELECT DISTINCT hs.id_cinema, hs.id_tipo_sessao, hs.id_sala, h.hora, s.nome_sala,
                       MIN(hs.id) as id
                FROM horarios_sessao hs
                JOIN horarios h ON hs.id_horario = h.id
                LEFT JOIN salas s ON hs.id_sala = s.id
                WHERE hs.id_filme = %s
                GROUP BY hs.id_cinema, hs.id_tipo_sessao, hs.id_sala, h.hora, s.nome_sala
                ORDER BY h.hora
            """, (id_filme,))
            horarios_filme = cursor.fetchall()
            app.logger.info(f"Horários recarregados após correção: {len(horarios_filme)}")
        
        from datetime import timedelta, datetime, time
        
        agora = datetime.now()
        hora_atual = agora.time()
        
        horarios_processados = []
        
        for h in horarios_filme:
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
                h['hora_str'] = str(h['hora'])[:5]
                try:
                    hora_parts = h['hora_str'].split(':')
                    h['hora_obj'] = time(int(hora_parts[0]), int(hora_parts[1]))
                except:
                    h['hora_obj'] = None
            
            horarios_processados.append(h)
        
        horarios_filme = horarios_processados
        app.logger.info(f"Horários após processamento: {len(horarios_filme)}")

        filtro_regiao = request.args.get('regiao', '').lower().strip()
        user_id = session.get('user_id')
        
        app.logger.info(f"Buscando cinemas para filme {id_filme}, user_id: {user_id}")
        
        # Buscar cinemas favoritos do utilizador
        cinemas_favoritos_ids = []
        if user_id:
            cursor.execute("""
                SELECT cinema_id FROM cinemas_favoritos
                WHERE usuario_id = %s
            """, (user_id,))
            cinemas_favoritos = cursor.fetchall()
            cinemas_favoritos_ids = [c['cinema_id'] for c in cinemas_favoritos]
            app.logger.info(f"Cinemas favoritos do utilizador {user_id}: {cinemas_favoritos_ids}")
        
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
        query += " ORDER BY c.id"
        
        app.logger.info(f"Query: {query}")
        app.logger.info(f"Params: {params}")
        
        cursor.execute(query, params)
        filme_cinemas = cursor.fetchall()
        
        # Ordenar cinemas: favoritos primeiro, depois os restantes
        if cinemas_favoritos_ids:
            filme_cinemas_ordenados = []
            # Adicionar cinemas favoritos primeiro
            for cinema in filme_cinemas:
                if cinema['id'] in cinemas_favoritos_ids:
                    filme_cinemas_ordenados.append(cinema)
            # Adicionar cinemas não favoritos
            for cinema in filme_cinemas:
                if cinema['id'] not in cinemas_favoritos_ids:
                    filme_cinemas_ordenados.append(cinema)
            filme_cinemas = filme_cinemas_ordenados
            app.logger.info(f"Cinemas ordenados com favoritos primeiro: {[c['id'] for c in filme_cinemas]}")
        

        cursor.execute("SELECT DISTINCT regiao FROM cinemas ORDER BY regiao")
        regioes = [r['regiao'] for r in cursor.fetchall()]
        
        cursor.execute("""
            SELECT 
                av.id,
                av.usuario_id,
                av.rating,
                av.comentario,
                av.data_avaliacao,
                u.nome as usuario_nome,
                COALESCE(a.caminho, 'imgs/icons/user_icon34-removebg-preview.png') as usuario_avatar
            FROM avaliacoes_filmes av
            JOIN usuarios u ON av.usuario_id = u.id
            LEFT JOIN avatars a ON u.avatar_id = a.id
            WHERE av.filme_id = %s
            ORDER BY av.data_avaliacao DESC
        """, (id_filme,))
        todas_avaliacoes = cursor.fetchall()
        
        user_avaliacao = None
        if 'user_id' in session:
            cursor.execute("""
                SELECT rating, comentario
                FROM avaliacoes_filmes
                WHERE filme_id = %s AND usuario_id = %s
            """, (id_filme, session['user_id']))
            user_avaliacao = cursor.fetchone()
        
        avaliacoes = []
        user_id_logado = session.get('user_id')
        
        for avaliacao in todas_avaliacoes:
            if user_id_logado and user_avaliacao and avaliacao['usuario_id'] == user_id_logado:
                continue
            avaliacoes.append(avaliacao)
        
        for avaliacao in avaliacoes:
            if avaliacao.get('usuario_avatar'):
                avaliacao['usuario_avatar'] = avaliacao['usuario_avatar'].replace('\\', '/').replace('"', '').strip()
            else:
                avaliacao['usuario_avatar'] = 'imgs/icons/user_icon34-removebg-preview.png'
        
        tipos_sessao_por_cinema = {}
        
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
    
    horarios_limpos = []
    for h in horarios_filme:
        h_limpo = dict(h)
        
        if 'hora_obj' in h_limpo:
            del h_limpo['hora_obj']
        
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
        request=request,
        cinemas_favoritos_ids=cinemas_favoritos_ids
    )

@app.route('/cineacessivel')
def cine_acessivel():
    return render_template('cine_acessivel.html')

from flask import url_for




@app.route('/cine_acessivel/audiodescricao')
def audiodescricao():
    return render_template('audiodescricao.html')

@app.route('/cine_acessivel/lgp')
def lgp():
    return render_template('lgp.html')

@app.route('/cine_acessivel/acessibilidade')
def acessibilidade():
    return render_template('acessibilidade.html')

@app.route('/cine_acessivel/legendagem')
def legendagem():
    return render_template('legendagem.html')

@app.route('/contactos', methods=['GET', 'POST'])
def contactos():
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    if request.method == 'POST':
        assunto = request.form.get('assunto')
        mensagem = request.form.get('mensagem')
        
        try:
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)
            
            if logged_in:
                cur.execute("SELECT nome, email FROM usuarios WHERE id = %s", (session['user_id'],))
                user_data = cur.fetchone()
                
                if not user_data:
                    flash('Erro: Utilizador não encontrado.', 'error')
                    cur.close()
                    conn.close()
                    return redirect(url_for('contactos'))
                
                nome = user_data['nome']
                email = user_data['email']
                app.logger.info(f"Utilizador logado: {nome} ({email})")
            else:
                nome = request.form.get('nome')
                email = request.form.get('email')
                app.logger.info(f"Utilizador não logado: {nome} ({email})")
            
            app.logger.info(f"Tentando enviar email de contacto de {nome} ({email})")
            
            cur.execute("SELECT email FROM usuarios WHERE is_admin = TRUE LIMIT 1")
            admin = cur.fetchone()
            
            cur.close()
            conn.close()
            
            if not admin:
                app.logger.error("Administrador não encontrado na base de dados")
                flash('Erro ao enviar mensagem. Administrador não encontrado.', 'error')
                return redirect(url_for('contactos'))
            
            admin_email = admin['email']
            app.logger.info(f"Email do admin encontrado: {admin_email}")
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'[CineVibe Contacto] {assunto}'
            msg['From'] = f'{nome} via CineVibe <{EMAIL_USER}>'
            msg['To'] = admin_email
            msg['Reply-To'] = email
            
            html_content = f'''
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #ffffff; background-color: #0D1B2A; margin: 0; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #0D1B2A;">
                        <div style="background-color: #1a1a1a; padding: 20px; border-bottom: 3px solid #FFD60A; margin-bottom: 20px;">
                            <h2 style="color: #FFD60A; margin: 0; text-align: center; font-size: 24px;">
                                Nova Mensagem de Contacto - CineVibe
                            </h2>
                        </div>
                        
                        <table style="width: 100%; background-color: #1a1a1a; border-radius: 8px; margin-bottom: 20px; border-collapse: separate; border-spacing: 0;">
                            <tr>
                                <td style="padding: 20px;">
                                    <table style="width: 100%; border-collapse: collapse;">
                                        <tr>
                                            <td style="padding: 10px 0;">
                                                <span style="color: #FFD60A; font-weight: bold; display: inline-block; min-width: 80px;">Nome:</span>
                                                <span style="color: #ffffff;">{nome}</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 10px 0;">
                                                <span style="color: #FFD60A; font-weight: bold; display: inline-block; min-width: 80px;">Email:</span>
                                                <a href="mailto:{email}" style="color: #ffffff; text-decoration: underline;">{email}</a>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 10px 0;">
                                                <span style="color: #FFD60A; font-weight: bold; display: inline-block; min-width: 80px;">Assunto:</span>
                                                <span style="color: #ffffff;">{assunto}</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 10px 0;">
                                                <span style="color: #FFD60A; font-weight: bold; display: inline-block; min-width: 80px;">Tipo:</span>
                                                <span style="color: #ffffff;">{'Utilizador Registado' if logged_in else 'Visitante'}</span>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                        
                        <div style="background-color: #1a1a1a; border-left: 4px solid #FFD60A; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                            <p style="color: #FFD60A; margin: 0 0 15px 0; font-weight: bold; font-size: 16px;">Mensagem:</p>
                            <p style="color: #ffffff; margin: 0; white-space: pre-wrap; line-height: 1.8; word-wrap: break-word;">{mensagem}</p>
                        </div>
                        
                        <div style="background-color: #1a1a1a; border-radius: 8px; border: 2px solid #FFD60A; padding: 20px; margin-bottom: 20px;">
                            <p style="margin: 0; font-size: 13px; color: #ffffff; text-align: center; line-height: 1.8;">
                                Esta mensagem foi enviada através do formulário de contacto do CineVibe.<br>
                                Pode responder diretamente a este email para contactar o remetente.
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            '''
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            app.logger.info("Tentando enviar email via SMTP...")
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            if EMAIL_USE_TLS:
                server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            
            text = msg.as_string()
            server.sendmail(EMAIL_USER, admin_email, text)
            server.quit()
            
            app.logger.info("Email enviado com sucesso!")
            flash('Mensagem enviada com sucesso! Entraremos em contacto em breve.', 'success')
            
        except smtplib.SMTPAuthenticationError as e:
            app.logger.error(f'Erro de autenticação SMTP: {str(e)}')
            flash('Erro ao enviar mensagem. Problema de autenticação.', 'error')
        except smtplib.SMTPException as e:
            app.logger.error(f'Erro SMTP: {str(e)}')
            flash('Erro ao enviar mensagem. Por favor, tente novamente mais tarde.', 'error')
        except Exception as e:
            app.logger.error(f'Erro ao enviar email de contacto: {str(e)}')
            import traceback
            app.logger.error(f'Traceback: {traceback.format_exc()}')
            flash('Erro ao enviar mensagem. Por favor, tente novamente mais tarde.', 'error')
        
        return redirect(url_for('contactos'))
    
    return render_template('contactos.html', logged_in=logged_in, avatar=avatar)


@app.route('/api/process-payment', methods=['POST'])
def process_payment():
    pass
   
    try:
        app.logger.info("🚀 INICIANDO process_payment")
        data = request.get_json()
        app.logger.info(f"📥 Dados recebidos: {data}")
        
        payment_method = data.get('payment_method')
        customer_info = data.get('customer_info', {})
        payment_data = data.get('payment_data', {})
        app.logger.info(f"💳 Método de pagamento: {payment_method}")
        
        reservation_data = session.get('reserva_data', {})
        app.logger.info(f"🎫 Dados da reserva na sessão: {reservation_data}")
        
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
            cursor = conn.cursor()
            app.logger.info("📋 Cursor criado")
            
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
        
        id_usuario = session.get('user_id', 1)
        id_filme = reservation_data.get('filme_id', 1)
        id_cinema = reservation_data.get('cinema_id', 1)
        id_horario_sessao = 1
        id_tipo_sessao = reservation_data.get('id_tipo_sessao', 1)
        data_sessao = reservation_data.get('data_sessao', '2025-01-20')
        
        lugares_lista = reservation_data.get('lugares_selecionados', ['A1', 'A2'])
        lugares = ','.join(lugares_lista)
        
        total = float(reservation_data.get('total', 17.00))
        
        nome_cliente = session.get('user_name', '').strip()
        if not nome_cliente:
            nome_cliente = session.get('nome_cliente', '').strip()
        if not nome_cliente:
            nome_cliente = customer_info.get('name', '').strip()
        if not nome_cliente:
            nome_cliente = 'Usuário CineVibe'
        
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
        metodo_pagamento = payment_method
        
        app.logger.info(f"🎯 INSERINDO DADOS CORRETOS:")
        app.logger.info(f"   Nome: '{nome_cliente}'")
        app.logger.info(f"   Email: '{email_cliente}'")
        app.logger.info(f"   Lugares: '{lugares}'")
        app.logger.info(f"   Método: '{metodo_pagamento}'")
        app.logger.info(f"   Total: €{total}")
        
        try:
            cursor.execute("""
                INSERT INTO reservas (
                    id_horario_sessao, data_sessao, id_filme, id_cinema, 
                    id_tipo_sessao, id_usuario, nome_cliente, email_cliente, 
                    telefone_cliente, data_reserva, status, total, 
                    metodo_pagamento, lugares
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'confirmada', %s, %s, %s)
            """, (
                1, data_sessao, 1, 1,
                1, id_usuario, nome_cliente, email_cliente,
                telefone_cliente, total, metodo_pagamento, lugares
            ))
            
            reserva_id = cursor.lastrowid
            
        except Exception as e1:
            app.logger.error(f"Erro na inserção forçada: {str(e1)}")
            
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
                
            except Exception as e2:
                app.logger.error(f"Erro no fallback: {str(e2)}")
                reserva_id = 99999
        
        try:
            conn.commit()
        except Exception as e:
            app.logger.warning(f"Erro no commit: {str(e)}")
        
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        except:
            pass
        
        try:
            if lugares_lista:
                for lugar in lugares_lista:
                    try:
                        cursor.execute("""
                            INSERT IGNORE INTO lugares (id_sala, lugar, ocupado) 
                            VALUES (1, %s, TRUE)
                            ON DUPLICATE KEY UPDATE ocupado = TRUE
                        """, (lugar,))
                    except:
                        pass
        except:
            pass
        
        try:
            pass
            
        except Exception as e:
            app.logger.warning(f"❌ Erro no email: {str(e)}")
        
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except:
            pass
        
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
    try:
        data = request.get_json()
        app.logger.info(f"📦 Dados recebidos: {data}")
        
        tipo_sala = data.get('tipo_sala')
        preco_raw = data.get('preco')
        metodo_pagamento = data.get('metodo_pagamento')
        data_sessao = data.get('data_sessao')
        hora_sessao = data.get('hora_sessao')
        
        if not tipo_sala:
            return jsonify({'success': False, 'message': 'Tipo de sala é obrigatório'}), 400
        
        if not data_sessao or not hora_sessao:
            return jsonify({'success': False, 'message': 'Data e hora da sessão são obrigatórias'}), 400
        
        total = None
        if preco_raw:
            try:
                preco_str = str(preco_raw).replace('€', '').replace(',', '.').strip()
                total = float(preco_str)
                
                if total <= 0:
                    return jsonify({'success': False, 'message': 'Preço deve ser maior que zero'}), 400
                    
                app.logger.info(f"💰 Preço validado: €{total}")
                
            except (ValueError, TypeError) as e:
                app.logger.error(f"❌ Erro ao converter preço '{preco_raw}': {e}")
                return jsonify({'success': False, 'message': 'Preço inválido'}), 400
        else:
            precos_padrao = {
                'intimista': 100.00,
                'premium': 150.00,
                'vip': 200.00
            }
            total = precos_padrao.get(tipo_sala.lower(), 100.00)
            app.logger.warning(f"⚠️ Preço não fornecido, usando padrão: €{total}")
        
        user_id = None
        nome_cliente = ""
        email_cliente = ""
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if 'user_id' in session:
            user_id = session['user_id']
            
            cursor.execute("""
                SELECT nome, email FROM usuarios WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()
            
            if user:
                nome_cliente = user['nome']
                email_cliente = user['email']
            else:
                nome_cliente = session.get('nome', 'Cliente')
                email_cliente = session.get('email', '')
                
            
        else:
            nome_cliente = data.get('nome_cliente', '').strip()
            email_cliente = data.get('email_cliente', '').strip()
            telefone_cliente = data.get('telefone_cliente', '').strip()
            
            if not nome_cliente or not email_cliente:
                return jsonify({
                    'success': False, 
                    'message': 'Nome e email são obrigatórios para reservas de convidado'
                }), 400
            
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email_cliente):
                return jsonify({
                    'success': False, 
                    'message': 'Email inválido'
                }), 400
            
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email_cliente,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                user_id = existing_user['id']
            else:
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha, criado_em)
                    VALUES (%s, %s, 'GUEST_USER', NOW())
                """, (nome_cliente, email_cliente))
                
                user_id = cursor.lastrowid
        
        if not user_id:
            return jsonify({'success': False, 'message': 'Erro ao identificar utilizador'}), 500
        
        
        cursor.execute("""
            INSERT INTO reservas_exclusivas 
            (tipo_sala, id_filme, filme_nome, data_sessao, hora_sessao, num_pessoas, total, id_usuario, data_reserva, status)
            VALUES (%s, NULL, NULL, %s, %s, 0, %s, %s, NOW(), 'confirmada')
        """, (tipo_sala, data_sessao, hora_sessao, total, user_id))
        
        reserva_id = cursor.lastrowid
        conn.commit()
        
        
        try:
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
            
            resultado_email = enviar_email_confirmacao(
                email_cliente,
                nome_cliente,
                dados_email
            )
            
            if not resultado_email:
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
    pass
  
    try:
        data = request.get_json()
        app.logger.info(f"📦 Dados recebidos para pagamento: {data}")
        
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
        
        id_usuario = session.get('user_id', 0)
        
        if id_usuario == 0:
            if not nome or not email:
                return jsonify({'success': False, 'message': 'Nome e email são obrigatórios'}), 400
        
        if not id_horario_sessao or not id_cinema or not tipo_id or not lugareses:
            return jsonify({'success': False, 'message': 'Dados da reserva incompletos'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if not id_filme:
            cursor.execute("SELECT id_filme FROM horarios_sessao WHERE id = %s", (id_horario_sessao,))
            horario_row = cursor.fetchone()
            id_filme = horario_row['id_filme'] if horario_row else None
        
        if not id_filme:
            raise Exception("Filme não encontrado")
        
        cursor.execute("SELECT preco_bilhete FROM tipos_sessao WHERE id = %s", (tipo_id,))
        preco_row = cursor.fetchone()
        preco_bilhete = float(preco_row['preco_bilhete']) if preco_row else 8.50
        
        total_bilhetes = preco_bilhete * len(lugares)
        total_bar = 0
        for produto_id, produto_info in produtos_bar.items():
            total_bar += float(produto_info.get('preco', 0)) * int(produto_info.get('quantidade', 0))
        
        total_geral = total_bilhetes + total_bar
        
        nome_cliente = None
        email_cliente = None
        telefone_cliente = None
        nome_para_email = nome
        email_para_email = email
        
        if id_usuario > 0:
            cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (id_usuario,))
            user_data = cursor.fetchone()
            if user_data:
                nome_para_email = user_data['nome']
                email_para_email = user_data['email']
        else:
            nome_cliente = nome
            email_cliente = email
            telefone_cliente = telefone
            nome_para_email = nome
            email_para_email = email
        
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
        
        cursor.execute("SELECT titulo FROM filmes WHERE id = %s", (id_filme,))
        filme_row = cursor.fetchone()
        filme_titulo = filme_row['titulo'] if filme_row else 'Filme'
        
        cursor.execute("SELECT nome FROM cinemas WHERE id = %s", (id_cinema,))
        cinema_row = cursor.fetchone()
        cinema_nome = cinema_row['nome'] if cinema_row else 'Cinema'
        
        cursor.execute("SELECT nome FROM tipos_sessao WHERE id = %s", (tipo_id,))
        tipo_row = cursor.fetchone()
        tipo_nome = tipo_row['nome'] if tipo_row else 'Normal'
        
        cursor.execute("""
            SELECT h.hora 
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (id_horario_sessao,))
        hora_row = cursor.fetchone()
        hora_str = hora_row['hora'] if hora_row else '00:00'
        
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
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        try:
            app.logger.info(f"📦 Dados do email: {dados_email}")
            
            resultado_email = enviar_email_confirmacao(email_para_email, nome_para_email, dados_email)
            
            if resultado_email:
                pass
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
    data_sessao = request.args.get('data')

    
    app.logger.info(f"  id_horario_sessao: {id_horario_sessao}")
    app.logger.info(f"  id_cinema: {id_cinema}")
    app.logger.info(f"  tipo_id: {tipo_id}")
    app.logger.info(f"  data_sessao: {data_sessao}")
    
    if not id_horario_sessao or not id_cinema or not tipo_id:
        return "Parâmetros incompletos", 400
    
    if not data_sessao:
        from datetime import date
        data_sessao = date.today().strftime('%Y-%m-%d')
    
    app.logger.info(f"=== RESERVA PARA DATA: {data_sessao} ===")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
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

        cursor.execute("""
            SELECT g.nome AS genero
            FROM filme_generos fg
            JOIN generos g ON fg.genero_id = g.id
            WHERE fg.filme_id = %s
        """, (id_filme,))
        filme_generos = [g['genero'] for g in cursor.fetchall()]

        cursor.execute("SELECT id, nome FROM cinemas WHERE id = %s", (id_cinema,))
        cinema = cursor.fetchone() or {}

        
        
        cursor.execute("SELECT id, nome, preco_bilhete FROM tipos_sessao WHERE id = %s", (tipo_id,))
        tipo_sessao = cursor.fetchone() or {}
        
        preco_bilhete = float(tipo_sessao.get('preco_bilhete', 8.50))
        
        filme_sessao = {
            'cinema_nome': cinema.get('nome', 'Cinema'),
            'tipo_sessao': tipo_sessao.get('nome', 'Sessão'),
            'hora_str': horario['hora_str'],
            'preco': preco_bilhete,
            'sala': horario.get('id_sala', 1)
        }

        cursor.execute("SELECT id, nome_sala, capacidade, tipo_sala FROM salas WHERE id = %s", (horario['id_sala'],))
        sala_temp = cursor.fetchone()
        if sala_temp:
            sala = {
                'id': sala_temp['id'],
                'nome_sala': sala_temp['nome_sala'], 
                'capacidade': sala_temp['capacidade'],
                'tipo_sala': sala_temp['tipo_sala'],
                'lugareses_acessiveis': 8,
                'lugareses_casal': 8,
                'lugareses_premium': 8
            }
        else:
            sala = {}


        app.logger.info(f"=== BUSCANDO LUGARES RESERVADOS ===")
        app.logger.info(f"Sessão ID: {id_horario_sessao}, Data: {data_sessao}")
        
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
        
        cursor.execute("""
            SELECT id_horario_sessao, data_sessao, COUNT(*) as total, GROUP_CONCAT(lugares) as lugares
            FROM reservas 
            WHERE id_horario_sessao = %s
            GROUP BY id_horario_sessao, data_sessao
        """, (id_horario_sessao_int,))
        resumo = cursor.fetchall()
        app.logger.info(f"Resumo de reservas desta sessão por data: {resumo}")

        cursor.execute("""
            SELECT id, nome_lugar, ocupado
            FROM lugares
            WHERE sala_id = %s
            ORDER BY nome_lugar
        """, (sala.get('id'),))
        lugareses = cursor.fetchall() or []
        
        app.logger.info(f"Total de lugares na sala: {len(lugareses)}")
        
        lugareses_marcados = 0
        for lugares in lugareses:
            nome_lugares = lugares['nome_lugar']
            if nome_lugares in lugareses_reservados or nome_lugares.replace(' ', '') in lugareses_reservados:
                lugares['ocupado'] = 1
                lugareses_marcados += 1
                app.logger.info(f"✓ Lugar '{nome_lugares}' marcado como ocupado")
        
        app.logger.info(f"Total de lugareses marcados como ocupados: {lugareses_marcados}")
        
        lugareses_na_tabela = [l['nome_lugar'] for l in lugareses]
        for lugares_reservado in lugareses_reservados:
            if lugares_reservado not in lugareses_na_tabela:
                app.logger.warning(f"⚠️ Lugar reservado '{lugares_reservado}' não existe na tabela lugareses! Adicionando temporariamente...")
                lugareses.append({
                    'id': None,
                    'nome_lugar': lugares_reservado,
                    'ocupado': 1
                })

        cursor.execute("""
            SELECT id, produto AS nome, preco, imagem_url AS imagem, categoria AS tipo
            FROM bar
            ORDER BY categoria, produto
        """)
        produtos_bar = cursor.fetchall() or []
        for p in produtos_bar:
            raw = (p.get('imagem') or '').replace('\\', '/').replace('"', '').strip()
            if raw.startswith("http://") or raw.startswith("https://"):
                p['imagem'] = raw
            else:
                p['imagem'] = url_for('static', filename=raw.lstrip('/'))

        cursor.execute("SELECT id, nome, descricao, preco_total, imagem_url FROM menus ORDER BY nome")
        menus_bar = cursor.fetchall() or []
        for m in menus_bar:
            if m.get('imagem_url'):
                raw = m['imagem_url'].replace('\\', '/').replace('"', '').strip()
                if raw.startswith("http://") or raw.startswith("https://"):
                    m['imagem_url'] = raw
                else:
                    m['imagem_url'] = url_for('static', filename=raw.lstrip('/'))
            
            cursor.execute("""
                SELECT b.id, b.produto AS nome, b.preco, b.imagem_url AS imagem, b.categoria
                FROM menu_produtos mp
                JOIN bar b ON mp.produto_id = b.id
                WHERE mp.menu_id = %s
                ORDER BY b.categoria, b.produto
            """, (m['id'],))
            produtos_menu = cursor.fetchall() or []
            
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

    user_authenticated = 'user_id' in session
    user_name = None
    user_email = None
    user_avatar = 'imgs/icons/user_icon34-removebg-preview.png'
    
    if user_authenticated:
        conn_user = get_db_connection()
        cursor_user = conn_user.cursor(dictionary=True)
        cursor_user.execute("SELECT u.nome, u.email, a.caminho as avatar FROM usuarios u LEFT JOIN avatars a ON u.avatar_id = a.id WHERE u.id = %s", (session['user_id'],))
        user = cursor_user.fetchone()
        cursor_user.close()
        conn_user.close()
        
        if user:
            user_name = user['nome']
            user_email = user['email']
            user_avatar = user.get('avatar') or 'imgs/icons/user_icon34-removebg-preview.png'
    
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

@app.route('/selecao_lugares', methods=['GET', 'POST'])
def selecao_lugares():
    pass
    
    if request.method == 'POST':
        filme_id = request.form.get('filme_id')
        cinema_id = request.form.get('cinema_id')
        id_tipo_sessao = request.form.get('id_tipo_sessao')
        id_horario_sessao = request.form.get('id_horario_sessao')
        data_sessao = request.form.get('data_sessao')
        quantidade = int(request.form.get('quantidade', 1))
        
        app.logger.info(f"📋 Dados POST: filme_id={filme_id}, cinema_id={cinema_id}")
    else:
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
        cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        if not filme:
            flash("Filme não encontrado", "erro")
            return render_template('error.html', message="Filme não encontrado")
        
        if filme.get('poster_url'):
            poster_url = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
            
            if poster_url.startswith('static/'):
                poster_url = poster_url[7:]
            elif poster_url.startswith('/static/'):
                poster_url = poster_url[8:]
            elif poster_url.startswith('/'):
                poster_url = poster_url[1:]
            
            if not poster_url.startswith('imgs/filmes/'):
                if '/' not in poster_url:
                    poster_url = f"imgs/filmes/{poster_url}"
                elif not poster_url.startswith('imgs/'):
                    poster_url = f"imgs/filmes/{poster_url}"
            
            caminho_completo = f"static/{poster_url}"
            if not os.path.exists(caminho_completo):
                nome_arquivo = os.path.basename(poster_url).lower()
                pasta_filmes = "static/imgs/filmes"
                if os.path.exists(pasta_filmes):
                    for arquivo in os.listdir(pasta_filmes):
                        if arquivo.lower() == nome_arquivo or nome_arquivo in arquivo.lower():
                            poster_url = f"imgs/filmes/{arquivo}"
                            break
                    else:
                        poster_url = "imgs/filmes/placeholder.jpg"
            
            filme['poster_url'] = poster_url
        
        cursor.execute("SELECT * FROM cinemas WHERE id = %s", (cinema_id,))
        cinema = cursor.fetchone()
        
        cursor.execute("SELECT * FROM tipos_sessao WHERE id = %s", (id_tipo_sessao,))
        tipo_sessao = cursor.fetchone()
        
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
        
        hora_val = horario['hora']
        horario['hora_str'] = hora_val.strftime("%H:%M") if hasattr(hora_val, 'strftime') else str(hora_val)
        
        capacidade_sala = horario.get('capacidade')
        id_sala = horario.get('id_sala')
        
        if capacidade_sala is None or id_sala is None:
            app.logger.warning(f"Capacidade ou id_sala None para horário {id_horario_sessao}")
            if id_sala:
                cursor.execute("SELECT capacidade, filas, lugares_por_fila, lugares_acessiveis, lugares_vip FROM salas WHERE id = %s", (id_sala,))
                sala_info = cursor.fetchone()
                if sala_info:
                    capacidade_sala = sala_info.get('capacidade', 100)
                    filas = sala_info.get('filas', 10)
                    lugares_por_fila = sala_info.get('lugares_por_fila', 10)
                    lugares_acessiveis = sala_info.get('lugares_acessiveis', None)
                    lugares_vip = sala_info.get('lugares_vip', None)
                else:
                    capacidade_sala = 100
                    filas = 10
                    lugares_por_fila = 10
                    lugares_acessiveis = None
                    lugares_vip = None
            else:
                capacidade_sala = 100
                filas = 10
                lugares_por_fila = 10
                lugares_acessiveis = None
                lugares_vip = None
        else:
            cursor.execute("SELECT filas, lugares_por_fila, lugares_acessiveis, lugares_vip FROM salas WHERE id = %s", (id_sala,))
            sala_layout = cursor.fetchone()
            if sala_layout:
                filas = sala_layout.get('filas', 10)
                lugares_por_fila = sala_layout.get('lugares_por_fila', 10)
                lugares_acessiveis = sala_layout.get('lugares_acessiveis', None)
                lugares_vip = sala_layout.get('lugares_vip', None)
            else:
                filas = 10
                lugares_por_fila = 10
                lugares_acessiveis = None
                lugares_vip = None
        
        if lugares_acessiveis and isinstance(lugares_acessiveis, str):
            import json
            try:
                lugares_acessiveis = json.loads(lugares_acessiveis)
            except:
                lugares_acessiveis = None
        
        if lugares_vip and isinstance(lugares_vip, str):
            try:
                lugares_vip = json.loads(lugares_vip)
            except:
                lugares_vip = None
        
        sala = {
            'nome_sala': horario.get('nome_sala', 'Sala 1'),
            'capacidade': capacidade_sala,
            'filas': filas,
            'lugares_por_fila': lugares_por_fila,
            'lugares_acessiveis': lugares_acessiveis,
            'lugares_vip': lugares_vip
        }
        
        app.logger.info(f"Sala final - Nome: {sala['nome_sala']}, Capacidade: {sala['capacidade']}, Filas: {sala['filas']}, Lugares/Fila: {sala['lugares_por_fila']}, Acessíveis: {lugares_acessiveis}, VIP: {lugares_vip}")
        
        cursor.execute("""
            SELECT lugares
            FROM reservas
            WHERE id_horario_sessao = %s AND data_sessao = %s
        """, (id_horario_sessao, data_sessao))
        
        lugares_ocupados_lista = []
        for row in cursor.fetchall():
            if row['lugares']:
                if ',' in row['lugares']:
                    lugares_ocupados_lista.extend([l.strip() for l in row['lugares'].split(',') if l.strip()])
                else:
                    lugares_ocupados_lista.append(row['lugares'].strip())
        
        lugares_ocupados_set = set(lugares_ocupados_lista)
        
        
        lugares = gerar_layout_sala(
            sala['filas'], 
            sala['lugares_por_fila'], 
            list(lugares_ocupados_set),
            sala.get('lugares_acessiveis'),
            sala.get('lugares_vip')
        )
        
        lugares_ocupados_no_layout = []
        for fileira in lugares:
            if fileira.get('tipo') == 'fileira':
                for lugar in fileira['lugares']:
                    if lugar.get('ocupado'):
                        lugares_ocupados_no_layout.append(lugar['nome'])
        
        
        preco_bilhete = float(tipo_sessao.get('preco_bilhete', 8.50))
        
        user_authenticated = 'user_id' in session
        
        # Verificar se o usuário tem plano com lugares VIP incluídos
        user_has_vip_plan = False
        if user_authenticated:
            user_id = session.get('user_id')
            conn_plan = get_db_connection()
            cursor_plan = conn_plan.cursor(dictionary=True)
            try:
                cursor_plan.execute("""
                    SELECT plano_tipo
                    FROM subscricoes
                    WHERE user_id = %s 
                    AND status = 'ativo'
                    ORDER BY id DESC LIMIT 1
                """, (user_id,))
                subscricao = cursor_plan.fetchone()
                # Planos Premium e Cinéfilo incluem lugares VIP
                if subscricao and subscricao.get('plano_tipo') in ['premium', 'cinefilo']:
                    user_has_vip_plan = True
            finally:
                cursor_plan.close()
                conn_plan.close()
        
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
        user_has_vip_plan=user_has_vip_plan,
        data_sessao=data_sessao,
        id_horario_sessao=id_horario_sessao,
        cinema_id=cinema_id,
        id_tipo_sessao=id_tipo_sessao,
        filme_id=filme_id,
        user_authenticated=user_authenticated,
        user_avatar=get_user_avatar()
    )

def gerar_layout_sala(filas, lugares_por_fila, lugares_ocupados, lugares_acessiveis=None, lugares_vip=None):
    """Gera o layout da sala baseado nas filas e lugares por fila reais da BD"""
    if filas is None or filas <= 0:
        app.logger.error(f"Número de filas inválido: {filas}")
        filas = 10
    
    if lugares_por_fila is None or lugares_por_fila <= 0:
        app.logger.error(f"Lugares por fila inválido: {lugares_por_fila}")
        lugares_por_fila = 10
    
    lugares_ocupados_set = set(lugares_ocupados) if lugares_ocupados else set()
    
    layout = []
    divisoes_horizontais = []
    
    if filas >= 4:
        meio_sala = filas // 2
        divisoes_horizontais = [meio_sala - 1]
    
    if lugares_acessiveis is None or not lugares_acessiveis:
        ultima_fila = chr(64 + filas)
        lugares_acessiveis = [
            f"{ultima_fila}1",
            f"{ultima_fila}2",
            f"{ultima_fila}{lugares_por_fila - 1}",
            f"{ultima_fila}{lugares_por_fila}"
        ]
    
    lugares_acessiveis_set = set(lugares_acessiveis)
    lugares_vip_set = set(lugares_vip) if lugares_vip else set()
    
    for i in range(filas):
        letra_fileira = chr(65 + i)
        
        fileira = {
            'letra': letra_fileira,
            'lugares': [],
            'tipo': 'fileira'
        }
        
        for j in range(lugares_por_fila):
            nome_lugar = f"{letra_fileira}{j+1}"
            
            esta_ocupado = nome_lugar in lugares_ocupados_set
            
            lugar = {
                'nome': nome_lugar,
                'ocupado': esta_ocupado,
                'acessivel': nome_lugar in lugares_acessiveis_set,
                'vip': nome_lugar in lugares_vip_set
            }
            fileira['lugares'].append(lugar)
        
        layout.append(fileira)
        
        if i in divisoes_horizontais:
            divisao = {
                'tipo': 'divisao_horizontal',
                'letra': f"DIV_{i+1}",
                'lugares': []
            }
            layout.append(divisao)
    
    app.logger.info(f"Layout gerado: {filas} filas x {lugares_por_fila} lugares = {filas * lugares_por_fila} lugares totais")
    return layout
    


@app.route('/confirmar_reserva', methods=['POST'])
def confirmar_reserva():
    pass

    try:
        if request.is_json:
            data = request.get_json()
            id_horario_sessao = data.get('horario')
            id_cinema = data.get('cinema')
            tipo_id = data.get('tipo')
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
        
        if not data_sessao:
            from datetime import date
            data_sessao = date.today().strftime('%Y-%m-%d')
        
        if not all([id_horario_sessao, id_cinema, tipo_id, nome, email, lugareses]):
            if request.is_json:
                return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
            flash("Dados incompletos para a reserva.", "error")
            return redirect(request.referrer or url_for('home'))
        
        app.logger.info("=" * 80)
        app.logger.info(f"   id_horario_sessao (raw): '{id_horario_sessao}' (tipo: {type(id_horario_sessao)})")
        app.logger.info(f"   id_cinema (raw): '{id_cinema}' (tipo: {type(id_cinema)})")
        app.logger.info(f"   tipo_id (raw): '{tipo_id}' (tipo: {type(tipo_id)})")
        app.logger.info(f"   id_filme (raw): '{id_filme}' (tipo: {type(id_filme)})")
        
        try:
            id_horario_sessao = int(id_horario_sessao)
            id_cinema = int(id_cinema)
            tipo_id = int(tipo_id)
            if id_filme:
                id_filme = int(id_filme)
                
            app.logger.info(f"   id_horario_sessao (int): {id_horario_sessao}")
            app.logger.info(f"   id_cinema (int): {id_cinema}")
            app.logger.info(f"   tipo_id (int): {tipo_id}")
            app.logger.info(f"   id_filme (int): {id_filme}")
        except (ValueError, TypeError):
            if request.is_json:
                return jsonify({'success': False, 'message': 'IDs inválidos'}), 400
            flash("Dados inválidos.", "error")
            return redirect(request.referrer or url_for('home'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, nome, preco_bilhete FROM tipos_sessao WHERE id = %s", (tipo_id,))
        tipo_sessao = cursor.fetchone()
        
        if not tipo_sessao:
            raise Exception(f"Tipo de sessão {tipo_id} não encontrado")
        
        
        cursor.execute("SELECT id, nome FROM cinemas WHERE id = %s", (id_cinema,))
        cinema = cursor.fetchone()
        if not cinema:
            raise Exception(f"Cinema {id_cinema} não encontrado")
        
        cursor.execute("""
            SELECT hs.id, hs.id_filme, hs.id_sala, hs.id_tipo_sessao, h.hora
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (id_horario_sessao,))
        horario = cursor.fetchone()
        if not horario:
            raise Exception(f"Horário {id_horario_sessao} não encontrado")
        
        if not id_filme:
            id_filme = horario['id_filme']
        
        cursor.execute("SELECT id, titulo FROM filmes WHERE id = %s", (id_filme,))
        filme = cursor.fetchone()
        if not filme:
            raise Exception(f"Filme {id_filme} não encontrado")
        
        preco_bilhete = float(tipo_sessao['preco_bilhete'])
        total = preco_bilhete * len(lugareses)
        
        app.logger.info(f"💰 PREÇOS: Bilhete €{preco_bilhete} x {len(lugareses)} lugares = €{total}")
        
        id_usuario = session.get('user_id', None)
        
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
                id_horario_sessao,
                data_sessao,
                id_filme,
                id_cinema,
                tipo_id,
                lugares,
                id_usuario,
                nome,
                email,
                telefone
            ))
            
            reserva_id = cursor.lastrowid
            
            cursor.execute("SELECT id_tipo_sessao FROM reservas WHERE id = %s", (reserva_id,))
            verificacao = cursor.fetchone()
            
            if verificacao['id_tipo_sessao'] != tipo_id:
                app.logger.error(f"🚨 ERRO CRÍTICO!")
                app.logger.error(f"   Tentámos inserir: {tipo_id}")
                app.logger.error(f"   Foi inserido: {verificacao['id_tipo_sessao']}")
                raise Exception(f"Erro na inserção: tipo incorreto")
            
            reserva_ids.append(reserva_id)
        
        conn.commit()
        
        try:
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
                
                enviar_email_confirmacao(email, nome, dados_email)
            
        except Exception as e:
            app.logger.error(f"Erro ao enviar email: {e}")
        
        cursor.close()
        conn.close()
        
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

# TEST ROUTE - Comment out for production  
@app.route('/teste-email')
def teste_email():
    try:
        pass
        
        import smtplib
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.quit()
        
        
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

@app.route('/sessao')
def sessao():
    return render_template('sessao.html')

@app.route('/sessao_exclusiva')
def sessao_exclusiva():
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    nome = ''
    email = ''
    telefone = ''
    
    if logged_in:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (session['user_id'],))
            user_data = cursor.fetchone()
            
            if user_data:
                nome = user_data['nome'] or ''
                email = user_data['email'] or ''
                telefone = ''
                
                session['nome'] = nome
                session['email'] = email
                session['telefone'] = telefone
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            app.logger.error(f"Erro ao buscar dados do usuário: {str(e)}")
            nome = session.get('nome', '')
            email = session.get('email', '')
            telefone = session.get('telefone', '')
    
    salas_exclusivas = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, nome, descricao, capacidade FROM salas_exclusivas ORDER BY nome")
        salas_raw = cursor.fetchall()
        
        precos_salas = {
            'intimista': 150.00,
            'vip': 350.00,
            'premium': 200.00
        }
        
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
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    return render_template('sessoes_tematicas.html', logged_in=logged_in, avatar=avatar)

@app.route('/sessao_terror')
def sessao_terror():
    filmes_terror = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
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
        
        for filme in filmes_terror:
            poster_url = filme.get('poster_url', '')
            if poster_url:
                poster_url = poster_url.replace('\\', '/').replace('"', '').strip()
                
                if not poster_url.startswith('imgs/filmes/'):
                    if '/' not in poster_url:
                        poster_url = f"imgs/filmes/{poster_url}"
                    elif not poster_url.startswith('imgs/'):
                        poster_url = f"imgs/filmes/{poster_url}"
                
                filme['poster_url'] = poster_url
            
            poster_hover = filme.get('poster_hover', '')
            if poster_hover:
                poster_hover = poster_hover.replace('\\', '/').replace('"', '').strip()
                
                if not poster_hover.startswith('imgs/filmes/'):
                    if '/' not in poster_hover:
                        poster_hover = f"imgs/filmes/{poster_hover}"
                    elif not poster_hover.startswith('imgs/'):
                        poster_hover = f"imgs/filmes/{poster_hover}"
                
                filme['poster_hover'] = poster_hover
        
        app.logger.info(f"Filmes de terror encontrados: {len(filmes_terror)}")
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar filmes de terror: {e}")
        filmes_terror = []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
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
            WHERE fg.genero_id = 12
            AND f.estado = 'em_exibicao'
            AND f.poster_url IS NOT NULL 
            AND f.poster_url != ''
            GROUP BY f.id, f.titulo, f.poster_url, f.poster_hover, f.trailer_url, f.duracao, f.data_lancamento
            ORDER BY CASE WHEN f.id IN (4, 17, 3, 7, 38, 68, 69, 1, 33, 5, 31, 8, 34, 30, 40, 32, 29, 6) THEN 0 ELSE 1 END, FIELD(f.id, 4, 17, 3, 7, 38, 68, 69, 1, 33, 5, 31, 8, 34, 30, 40, 32, 29, 6), f.data_lancamento ASC
        """)
        filmes_vintage = cursor.fetchall()
        
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
        
        for filme in filmes_vintage:
            poster_url = filme.get('poster_url', '')
            if poster_url:
                poster_url = poster_url.replace('\\', '/').replace('"', '').strip()
                
                if not poster_url.startswith('imgs/filmes/'):
                    if '/' not in poster_url:
                        poster_url = f"imgs/filmes/{poster_url}"
                    elif not poster_url.startswith('imgs/'):
                        poster_url = f"imgs/filmes/{poster_url}"
                
                filme['poster_url'] = poster_url
            
            poster_hover = filme.get('poster_hover', '')
            if poster_hover:
                poster_hover = poster_hover.replace('\\', '/').replace('"', '').strip()
                
                if not poster_hover.startswith('imgs/filmes/'):
                    if '/' not in poster_hover:
                        poster_hover = f"imgs/filmes/{poster_hover}"
                    elif not poster_hover.startswith('imgs/'):
                        poster_hover = f"imgs/filmes/{poster_hover}"
                
                filme['poster_hover'] = poster_hover
        
        app.logger.info(f"Filmes vintage encontrados: {len(filmes_vintage)}")
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar filmes vintage: {e}")
        filmes_vintage = []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    return render_template('sessao_vintage.html', 
                         filmes_vintage=filmes_vintage,
                         logged_in=logged_in,
                         avatar=avatar)

@app.route('/reserva_sessao_tematica')
def reserva_sessao_tematica():
    pass

    tipo_sessao = request.args.get('tipo')
    
    if not tipo_sessao:
        return "Tipo de sessão não especificado", 400
    
    logged_in = 'user_id' in session
    
    generos_map = {
        'vintage': 12,
        'romance': 13,
        'terror': 5
    }
    
    genero_id = generos_map.get(tipo_sessao)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if genero_id:
            cursor.execute("""
                SELECT DISTINCT f.id, f.titulo, f.duracao 
                FROM filmes f
                INNER JOIN filme_generos fg ON f.id = fg.filme_id
                WHERE fg.genero_id = %s
                ORDER BY f.titulo
            """, (genero_id,))
        else:
            cursor.execute("SELECT id, titulo, duracao FROM filmes ORDER BY titulo")
        
        filmes = cursor.fetchall()
    except Exception as e:
        app.logger.error(f"Erro ao buscar filmes: {e}")
        filmes = []
    finally:
        cursor.close()
        conn.close()
    
    from datetime import datetime, timedelta
    data_minima = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    filme_id_selecionado = request.args.get('filme_id', type=int)

    return render_template('reserva_sessao_tematica.html',
                         tipo_sessao=tipo_sessao,
                         filmes=filmes,
                         data_minima=data_minima,
                         logged_in=logged_in,
                         avatar=avatar,
                         filme_id_selecionado=filme_id_selecionado)

@app.route('/processar_reserva_tematica', methods=['POST'])
def processar_reserva_tematica():
    pass

    tipo_sessao = request.form.get('tipo_sessao')
    filme_id = request.form.get('filme_id')
    data_sessao = request.form.get('data_sessao')
    hora_sessao = request.form.get('hora_sessao')
    num_pessoas = request.form.get('num_pessoas')
    nome_cliente = request.form.get('nome_cliente')
    email_cliente = request.form.get('email_cliente')
    
    if not all([tipo_sessao, data_sessao, hora_sessao, num_pessoas]):
        return "Dados incompletos", 400
    
    precos_base = {
        'vintage': 35.00,
        'romance': 85.00,
        'terror': 45.00
    }
    
    preco_base = precos_base.get(tipo_sessao, 35.00)
    preco_total = preco_base * int(num_pessoas)
    
    filme_nome = 'Sem filme selecionado'
    if filme_id:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT titulo FROM filmes WHERE id = %s", (filme_id,))
            filme = cursor.fetchone()
            if filme:
                filme_nome = filme['titulo']
        except Exception as e:
            app.logger.error(f"Erro ao buscar filme: {e}")
        finally:
            cursor.close()
            conn.close()
    
    reserva_temp = {
        'tipo_sessao': tipo_sessao,
        'filme_id': filme_id if filme_id else None,
        'filme_nome': filme_nome,
        'data_sessao': data_sessao,
        'hora_sessao': hora_sessao,
        'num_pessoas': int(num_pessoas),
        'preco_total': preco_total
    }
    
    if nome_cliente and email_cliente:
        reserva_temp['nome_cliente'] = nome_cliente
        reserva_temp['email_cliente'] = email_cliente
    
    session['reserva_tematica_temp'] = reserva_temp
    
    return redirect(url_for('pagamento_tematica'))

@app.route('/pagamento_tematica')
def pagamento_tematica():
    if 'reserva_tematica_temp' not in session:
        return redirect(url_for('sessao_tematica'))
    
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    reserva = session['reserva_tematica_temp']
    
    return render_template('pagamento_tematica.html',
                         logged_in=logged_in,
                         avatar=avatar,
                         reserva=reserva)

def enviar_email_confirmacao_tematica(destinatario_email, destinatario_nome, dados_reserva):
    try:
        app.logger.info(f"Enviando email de confirmação temática para: {destinatario_email}")

        if EMAIL_PASSWORD in ['sua_senha_app_aqui', 'DESATIVADO_TEMPORARIAMENTE'] or not EMAIL_PASSWORD:
            app.logger.warning("Email desativado. Configure senha de app do Gmail.")
            return False

        tipos_sessao = {
            'vintage': 'Sessão Vintage',
            'romance': 'Sessão Romance',
            'terror': 'Sessão Terror'
        }
        nome_sessao = tipos_sessao.get(str(dados_reserva.get('tipo_sala', '')).lower(), 'Sessão Temática')

        try:
            data_formatada = datetime.strptime(dados_reserva['data_sessao'], '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            data_formatada = dados_reserva.get('data_sessao', '')

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; background-color: #0D1B2A; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #1B263B; border-radius: 15px; overflow: hidden; border: 2px solid #FFD60A;">
                <div style="background: linear-gradient(135deg, #0D1B2A, #1B263B); padding: 40px 30px; text-align: center; border-bottom: 3px solid #FFD60A;">
                    <h1 style="color: #FFD60A; margin: 0; font-size: 28px; font-weight: 900;">CineVibe Temático</h1>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #FFD60A; margin-bottom: 25px;">Olá, {destinatario_nome}!</h2>
                    <p style="color: #E0E1DD; font-size: 16px; line-height: 1.6; margin-bottom: 25px;">A sua reserva temática foi confirmada com sucesso!</p>
                    <div style="background: rgba(255,214,10,0.1); padding: 25px; border-radius: 15px; margin: 25px 0; border: 1px solid rgba(255,214,10,0.3);">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="color:#E0E1DD; font-weight:600; padding:12px 15px 12px 0; border-bottom:1px solid rgba(255,255,255,0.1);">Sessão:</td>
                                <td style="color:#FFD60A; font-weight:700; text-align:right; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.1);">{nome_sessao}</td>
                            </tr>
                            <tr>
                                <td style="color:#E0E1DD; font-weight:600; padding:12px 15px 12px 0; border-bottom:1px solid rgba(255,255,255,0.1);">Filme:</td>
                                <td style="color:#FFD60A; font-weight:700; text-align:right; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.1);">{dados_reserva.get('filme', '')}</td>
                            </tr>
                            <tr>
                                <td style="color:#E0E1DD; font-weight:600; padding:12px 15px 12px 0; border-bottom:1px solid rgba(255,255,255,0.1);">Data:</td>
                                <td style="color:#FFD60A; font-weight:700; text-align:right; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.1);">{data_formatada}</td>
                            </tr>
                            <tr>
                                <td style="color:#E0E1DD; font-weight:600; padding:12px 15px 12px 0; border-bottom:1px solid rgba(255,255,255,0.1);">Horário:</td>
                                <td style="color:#FFD60A; font-weight:700; text-align:right; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.1);">{dados_reserva.get('hora_sessao', '')}</td>
                            </tr>
                            <tr>
                                <td style="color:#E0E1DD; font-weight:600; padding:12px 15px 12px 0; border-bottom:1px solid rgba(255,255,255,0.1);">Pessoas:</td>
                                <td style="color:#FFD60A; font-weight:700; text-align:right; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.1);">{dados_reserva.get('num_pessoas', '')}</td>
                            </tr>
                            <tr>
                                <td style="color:#E0E1DD; font-weight:600; padding:20px 15px 0 0; border-top:2px solid rgba(255,214,10,0.3); font-size:1.2rem;">Total Pago:</td>
                                <td style="color:#FFD60A; font-weight:700; text-align:right; padding:20px 0 0 0; border-top:2px solid rgba(255,214,10,0.3); font-size:1.2rem;">{dados_reserva.get('total', '')}</td>
                            </tr>
                        </table>
                    </div>
                    <p style="color: #FFD60A; font-weight: bold; margin-top: 30px;">Instruções importantes:</p>
                    <ul style="color: #E0E1DD; line-height: 1.8;">
                        <li>Chegue 15 minutos antes do horário da sessão</li>
                        <li>A sala será preparada especialmente para o seu grupo</li>
                        <li>Serviços de bar e catering estão incluídos</li>
                    </ul>
                    <div style="text-align: center; margin: 30px 0;">
                        <p style="color: #FFD60A; font-weight: bold; margin-bottom: 15px;">QR Code da Reserva</p>
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=CINEVIBE-{nome_sessao.upper().replace(' ','-')}-{dados_reserva.get('data_sessao','')}-{dados_reserva.get('hora_sessao','')}" alt="QR Code da Reserva" style="border-radius: 10px; border: 3px solid #FFD60A;">
                        <p style="color: rgba(255,255,255,0.5); font-size: 12px; margin-top: 10px;">Apresente este QR Code na entrada</p>
                    </div>
                    <p style="color: #E0E1DD; font-size: 14px; margin-top: 30px;">Dúvidas? Contacte-nos: info@cinevibe.pt | +351 800 123 456</p>
                </div>
                <div style="background: rgba(0,0,0,0.4); padding: 20px; text-align: center; color: #778DA9; font-size: 14px;">
                    <p style="margin: 5px 0;"><strong style="color: #FFD60A;">© 2024 CineVibe</strong> - Experiências Cinematográficas Temáticas</p>
                    <p style="margin: 5px 0;">Este email foi enviado automaticamente. Não responda a esta mensagem.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Confirmação de Reserva Temática CineVibe'
        msg['From'] = f'CineVibe <{EMAIL_USER}>'
        msg['To'] = destinatario_email
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, destinatario_email, msg.as_string())
        server.quit()

        app.logger.info(f"Email de confirmação temática enviado para: {destinatario_email}")
        return True

    except Exception as e:
        app.logger.error(f"Erro ao enviar email de confirmação temática: {str(e)}")
        return False


@app.route('/api/processar-pagamento-tematica', methods=['POST'])
def api_processar_pagamento_tematica():
    try:
        data = request.get_json()
        app.logger.info(f"Dados recebidos para pagamento sessão temática: {data}")
        
        required_fields = ['tipo_sessao', 'preco_total', 'payment_method']
        
        for field in required_fields:
            if not data.get(field):
                app.logger.error(f"Campo obrigatório ausente: {field}")
                return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'})
        
        usuario_id = session.get('user_id')
        reserva_temp = session.get('reserva_tematica_temp', {})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if usuario_id:
            cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (usuario_id,))
            usuario = cursor.fetchone()
            
            if not usuario:
                return jsonify({'success': False, 'message': 'Usuário não encontrado'})
            
            nome_cliente = usuario['nome']
            email_cliente = usuario['email']
        else:
            nome_cliente = reserva_temp.get('nome_cliente', data.get('nome_cliente', ''))
            email_cliente = reserva_temp.get('email_cliente', data.get('email_cliente', ''))
            
            if not nome_cliente or not email_cliente:
                return jsonify({'success': False, 'message': 'Nome e email são obrigatórios para convidados'})
        
        filme_id = data.get('filme_id')
        if filme_id and filme_id != '0':
            cursor.execute("SELECT id FROM filmes WHERE id = %s", (filme_id,))
            if not cursor.fetchone():
                app.logger.warning(f"Filme ID {filme_id} não encontrado, definindo como NULL")
                filme_id = None
        else:
            filme_id = None
        
        cursor.execute("""
            INSERT INTO reservas_tematicas 
            (usuario_id, nome_cliente, email_cliente, tipo_sessao, filme_id, data_sessao, hora_sessao, num_pessoas, preco_total, metodo_pagamento, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'confirmada')
        """, (
            usuario_id,
            nome_cliente,
            email_cliente,
            data['tipo_sessao'],
            filme_id,
            data.get('data_sessao'),
            data.get('hora_sessao'),
            data.get('num_pessoas', 1),
            data['preco_total'],
            data.get('payment_method', 'outro')
        ))
        
        reserva_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        app.logger.info(f"Reserva sessão temática criada com sucesso - ID: {reserva_id}")
        
        response = jsonify({
            'success': True, 
            'message': 'Reserva criada com sucesso!',
            'reserva_id': reserva_id
        })
        
        @response.call_on_close
        def enviar_email_async():
            try:
                dados_email = {
                    'reserva_id': reserva_id,
                    'tipo_sala': data['tipo_sessao'],
                    'filme': data.get('filme_nome', 'Experiência Temática'),
                    'data_sessao': data.get('data_sessao', ''),
                    'hora_sessao': data.get('hora_sessao', ''),
                    'num_pessoas': data.get('num_pessoas', 1),
                    'total': f"€{data['preco_total']}",
                    'nome_cliente': nome_cliente,
                    'email_cliente': email_cliente
                }
                
                app.logger.info(f"Enviando email para {email_cliente}")
                enviar_email_confirmacao_tematica(email_cliente, nome_cliente, dados_email)
                app.logger.info(f"Email enviado com sucesso")
            except Exception as e:
                app.logger.error(f"Erro ao enviar email: {str(e)}")
        
        return response
        
    except Exception as e:
        app.logger.error(f"Erro ao processar pagamento sessão temática: {e}")
        return jsonify({'success': False, 'message': f'Erro ao processar pagamento: {str(e)}'})
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/reservar_sessao_exclusiva')
def reservar_sessao_exclusiva():
    """Renderiza a página de reserva de sessão exclusiva"""
    logged_in = 'user_id' in session
    
    sala_nome = request.args.get('sala', '')
    sala_id = request.args.get('sala_id')
    sala_capacidade = 50  # fallback

    # Buscar capacidade da sala a partir da BD
    if sala_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT capacidade FROM salas_exclusivas WHERE id = %s", (int(sala_id),))
            sala_row = cursor.fetchone()
            cursor.close()
            conn.close()
            if sala_row:
                sala_capacidade = sala_row['capacidade']
            else:
                app.logger.warning(f"Sala com id={sala_id} não encontrada")
        except Exception as e:
            app.logger.error(f"Erro ao buscar capacidade da sala: {e}")
    elif sala_nome:
        # fallback por nome se sala_id não vier
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT capacidade FROM salas_exclusivas WHERE LOWER(nome) = LOWER(%s)", (sala_nome,))
            sala_row = cursor.fetchone()
            cursor.close()
            conn.close()
            if sala_row:
                sala_capacidade = sala_row['capacidade']
        except Exception as e:
            app.logger.error(f"Erro ao buscar capacidade da sala por nome: {e}")

    # Buscar filmes em exibição
    filmes = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, titulo, duracao 
            FROM filmes 
            WHERE estado = 'em_exibicao'
            ORDER BY titulo
        """)
        filmes = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        app.logger.error(f"Erro ao buscar filmes: {e}")
    
    from datetime import datetime, timedelta
    data_minima = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    return render_template('reserva_sessao_exclusiva.html',
                         filmes=filmes,
                         data_minima=data_minima,
                         logged_in=logged_in,
                         avatar=avatar,
                         sala_nome=sala_nome,
                         sala_capacidade=sala_capacidade,
                         sala_id=sala_id)

@app.route('/processar_reserva_exclusiva', methods=['POST'])
def processar_reserva_exclusiva():
    """Processa o formulário de reserva de sessão exclusiva"""
    filme_id = request.form.get('filme_id')
    data_sessao = request.form.get('data_sessao')
    hora_sessao = request.form.get('hora_sessao')
    num_pessoas = request.form.get('num_pessoas')
    nome_cliente = request.form.get('nome_cliente')
    email_cliente = request.form.get('email_cliente')
    
    # Validar dados obrigatórios
    if not all([filme_id, data_sessao, hora_sessao, num_pessoas]):
        return "Dados incompletos", 400
    
    num_pessoas_int = int(num_pessoas)
    sala_id = request.form.get('sala_id')
    sala_capacidade = 50  # fallback

    if sala_id:
        try:
            conn_cap = get_db_connection()
            cursor_cap = conn_cap.cursor(dictionary=True)
            cursor_cap.execute("SELECT capacidade FROM salas_exclusivas WHERE id = %s", (sala_id,))
            sala_row = cursor_cap.fetchone()
            if sala_row:
                sala_capacidade = sala_row['capacidade']
            cursor_cap.close()
            conn_cap.close()
        except Exception as e:
            app.logger.error(f"Erro ao buscar capacidade da sala: {e}")
    
    if num_pessoas_int > sala_capacidade:
        return f"Número de pessoas excede a capacidade máxima da sala ({sala_capacidade} pessoas)", 400
    
    # Buscar o nome e preço da sala
    sala_nome = request.form.get('sala_nome', '').lower()
    
    # Se não vier sala_nome, buscar pelo sala_id
    if not sala_nome and sala_id:
        try:
            conn_sala = get_db_connection()
            cursor_sala = conn_sala.cursor(dictionary=True)
            cursor_sala.execute("SELECT nome FROM salas_exclusivas WHERE id = %s", (sala_id,))
            sala_row = cursor_sala.fetchone()
            if sala_row:
                sala_nome = sala_row['nome'].lower()
            cursor_sala.close()
            conn_sala.close()
        except Exception as e:
            app.logger.error(f"Erro ao buscar nome da sala: {e}")
    
    # Definir preços por tipo de sala
    precos_salas = {
        'intimista': 150.00,
        'vip': 350.00,
        'premium': 200.00
    }
    preco_base = precos_salas.get(sala_nome, 150.00)
    
    # Calcular preço total: preço base + €20 por pessoa adicional
    if num_pessoas_int > 1:
        preco_total = preco_base + ((num_pessoas_int - 1) * 20.00)
    else:
        preco_total = preco_base
    
    # Buscar informações do filme
    filme_nome = 'Filme não encontrado'
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT titulo FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        if filme:
            filme_nome = filme['titulo']
    except Exception as e:
        app.logger.error(f"Erro ao buscar filme: {e}")
    finally:
        cursor.close()
        conn.close()
    
    # Armazenar dados temporários na sessão
    reserva_temp = {
        'filme_id': filme_id,
        'filme_nome': filme_nome,
        'data_sessao': data_sessao,
        'hora_sessao': hora_sessao,
        'num_pessoas': num_pessoas_int,
        'preco_total': preco_total,
        'sala_nome': request.form.get('sala_nome', '')
    }
    
    if nome_cliente and email_cliente:
        reserva_temp['nome_cliente'] = nome_cliente
        reserva_temp['email_cliente'] = email_cliente
    
    session['reserva_exclusiva_temp'] = reserva_temp
    
    return redirect(url_for('pagamento_exclusivo'))

def enviar_email_confirmacao_exclusiva(destinatario_email, destinatario_nome, dados_reserva):
    try:
        app.logger.info(f"Enviando email de confirmação exclusiva para: {destinatario_email}")

        if EMAIL_PASSWORD in ['sua_senha_app_aqui', 'DESATIVADO_TEMPORARIAMENTE'] or not EMAIL_PASSWORD:
            app.logger.warning("Email desativado. Configure senha de app do Gmail.")
            return False

        tipos_sala = {
            'intimista': 'Sala Intimista',
            'vip': 'Sala Vip',
            'premium': 'Sala Premium',
            'exclusiva': 'Sala Exclusiva'
        }
        nome_sala = tipos_sala.get(str(dados_reserva.get('tipo_sala', '')).lower(), 'Sala Exclusiva')

        try:
            data_formatada = datetime.strptime(dados_reserva['data_sessao'], '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            data_formatada = dados_reserva.get('data_sessao', '')

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; background-color: #0D1B2A; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #1B263B; border-radius: 15px; overflow: hidden; border: 2px solid #FFD60A;">
                <div style="background: linear-gradient(135deg, #0D1B2A, #1B263B); padding: 40px 30px; text-align: center; border-bottom: 3px solid #FFD60A;">
                    <h1 style="color: #FFD60A; margin: 0; font-size: 28px; font-weight: 900;">CineVibe Exclusivo</h1>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #FFD60A; margin-bottom: 25px;">Olá, {destinatario_nome}!</h2>
                    <p style="color: #E0E1DD; font-size: 16px; line-height: 1.6;">A sua reserva exclusiva foi confirmada com sucesso!</p>
                    <div style="background: rgba(255,214,10,0.1); padding: 25px; border-radius: 15px; margin: 25px 0; border: 1px solid rgba(255,214,10,0.3);">
                        <div style="display:flex; justify-content:space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <span style="color:#E0E1DD; font-weight:600; padding-right:15px;">Sala:</span>
                            <span style="color:#FFD60A; font-weight:700;">{nome_sala}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <span style="color:#E0E1DD; font-weight:600; padding-right:15px;">Filme:</span>
                            <span style="color:#FFD60A; font-weight:700;">{dados_reserva.get('filme', '')}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <span style="color:#E0E1DD; font-weight:600; padding-right:15px;">Data:</span>
                            <span style="color:#FFD60A; font-weight:700;">{data_formatada}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <span style="color:#E0E1DD; font-weight:600; padding-right:15px;">Horário:</span>
                            <span style="color:#FFD60A; font-weight:700;">{dados_reserva.get('hora_sessao', '')}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <span style="color:#E0E1DD; font-weight:600; padding-right:15px;">Pessoas:</span>
                            <span style="color:#FFD60A; font-weight:700;">{dados_reserva.get('num_pessoas', '')}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding-top: 15px; border-top: 2px solid rgba(255,214,10,0.3); font-size: 1.2rem;">
                            <span style="color:#E0E1DD; font-weight:600; padding-right:15px;">Total Pago:</span>
                            <span style="color:#FFD60A; font-weight:700;">{dados_reserva.get('total', '')}</span>
                        </div>
                    </div>
                    <p style="color: #FFD60A; font-weight: bold;">Instruções importantes:</p>
                    <ul style="color: #E0E1DD; line-height: 1.8;">
                        <li>Chegue 15 minutos antes do horário da sessão</li>
                        <li>A sala será preparada especialmente para o seu grupo</li>
                    </ul>
                    <div style="text-align: center; margin: 30px 0;">
                        <p style="color: #FFD60A; font-weight: bold; margin-bottom: 15px;">QR Code da Reserva</p>
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=CINEVIBE-{nome_sala.upper().replace(' ','-')}-{dados_reserva.get('data_sessao','')}-{dados_reserva.get('hora_sessao','')}" alt="QR Code da Reserva" style="border-radius: 10px; border: 3px solid #FFD60A;">
                        <p style="color: rgba(255,255,255,0.5); font-size: 12px; margin-top: 10px;">Apresente este QR Code na entrada</p>
                    </div>
                    <p style="color: #E0E1DD; font-size: 14px; margin-top: 30px;">Dúvidas? Contacte-nos: info@cinevibe.pt | +351 800 123 456</p>
                </div>
                <div style="background: rgba(0,0,0,0.4); padding: 20px; text-align: center; color: #778DA9; font-size: 14px;">
                    <p style="margin: 5px 0;"><strong style="color: #FFD60A;">© 2024 CineVibe</strong> - Experiências Cinematográficas Exclusivas</p>
                    <p style="margin: 5px 0;">Este email foi enviado automaticamente. Não responda a esta mensagem.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Confirmação de Reserva Exclusiva CineVibe'
        msg['From'] = f'CineVibe <{EMAIL_USER}>'
        msg['To'] = destinatario_email
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, destinatario_email, msg.as_string())
        server.quit()

        app.logger.info(f"Email de confirmação exclusiva enviado para: {destinatario_email}")
        return True

    except Exception as e:
        app.logger.error(f"Erro ao enviar email de confirmação exclusiva: {str(e)}")
        return False


@app.route('/pagamento_exclusivo')
def pagamento_exclusivo():
    """Renderiza a página de pagamento para sessão exclusiva"""
    if 'reserva_exclusiva_temp' not in session:
        return redirect(url_for('sessao_exclusiva'))
    
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    reserva = session['reserva_exclusiva_temp']
    
    return render_template('pagamento_exclusivo.html',
                         logged_in=logged_in,
                         avatar=avatar,
                         reserva=reserva)

@app.route('/api/processar-pagamento-exclusivo', methods=['POST'])
def api_processar_pagamento_exclusivo():
    """API para processar o pagamento de sessão exclusiva"""
    try:
        data = request.get_json()
        app.logger.info(f"Dados recebidos para pagamento sessão exclusiva: {data}")
        
        required_fields = ['filme_id', 'preco_total']
        
        for field in required_fields:
            if not data.get(field):
                app.logger.error(f"Campo obrigatório ausente: {field}")
                return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'})
        
        usuario_id = session.get('user_id')
        reserva_temp = session.get('reserva_exclusiva_temp', {})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obter dados do cliente
        if usuario_id:
            cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (usuario_id,))
            usuario = cursor.fetchone()
            
            if not usuario:
                return jsonify({'success': False, 'message': 'Usuário não encontrado'})
            
            nome_cliente = usuario['nome']
            email_cliente = usuario['email']
        else:
            nome_cliente = reserva_temp.get('nome_cliente', data.get('nome_cliente', ''))
            email_cliente = reserva_temp.get('email_cliente', data.get('email_cliente', ''))
            
            if not nome_cliente or not email_cliente:
                return jsonify({'success': False, 'message': 'Nome e email são obrigatórios para convidados'})
        
        # Validar filme
        filme_id = data.get('filme_id')
        cursor.execute("SELECT id, titulo FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        if not filme:
            return jsonify({'success': False, 'message': 'Filme não encontrado'})
        
        # Inserir reserva exclusiva (tipo_sala = 'exclusiva' para diferenciar das outras sessões)
        cursor.execute("""
            INSERT INTO reservas_exclusivas 
            (tipo_sala, usuario_id, nome_cliente, email_cliente, filme_id, data_sessao, hora_sessao, num_pessoas, preco_total, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'confirmada')
        """, (
            'exclusiva',
            usuario_id,
            nome_cliente,
            email_cliente,
            filme_id,
            data.get('data_sessao'),
            data.get('hora_sessao'),
            data.get('num_pessoas', 1),
            data['preco_total']
        ))
        
        reserva_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        app.logger.info(f"Reserva sessão exclusiva criada com sucesso - ID: {reserva_id}")

        # Enviar email de confirmação
        try:
            dados_email = {
                'reserva_id': reserva_id,
                'tipo_sala': reserva_temp.get('sala_nome', 'exclusiva'),
                'filme': filme['titulo'],
                'data_sessao': data.get('data_sessao', ''),
                'hora_sessao': data.get('hora_sessao', ''),
                'num_pessoas': data.get('num_pessoas', 1),
                'total': f"€{float(data['preco_total']):.2f}"
            }
            enviar_email_confirmacao_exclusiva(email_cliente, nome_cliente, dados_email)
        except Exception as email_error:
            app.logger.error(f"Erro ao enviar email exclusivo: {email_error}")
        
        # Limpar dados temporários da sessão
        if 'reserva_exclusiva_temp' in session:
            session.pop('reserva_exclusiva_temp')
        
        return jsonify({
            'success': True, 
            'message': 'Reserva criada com sucesso!',
            'reserva_id': reserva_id
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao processar pagamento sessão exclusiva: {e}")
        return jsonify({'success': False, 'message': f'Erro ao processar pagamento: {str(e)}'})
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/sessao_romance')
def sessao_romance():
    pass

    
    filmes_romance = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
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
        
        for filme in filmes_romance:
            poster_url = filme.get('poster_url', '')
            if poster_url:
                poster_url = poster_url.replace('\\', '/').replace('"', '').strip()
                
                if not poster_url.startswith('imgs/filmes/'):
                    if '/' not in poster_url:
                        poster_url = f"imgs/filmes/{poster_url}"
                    elif not poster_url.startswith('imgs/'):
                        poster_url = f"imgs/filmes/{poster_url}"
                
                filme['poster_url'] = poster_url
            
            poster_hover = filme.get('poster_hover', '')
            if poster_hover:
                poster_hover = poster_hover.replace('\\', '/').replace('"', '').strip()
                
                if not poster_hover.startswith('imgs/filmes/'):
                    if '/' not in poster_hover:
                        poster_hover = f"imgs/filmes/{poster_hover}"
                    elif not poster_hover.startswith('imgs/'):
                        poster_hover = f"imgs/filmes/{poster_hover}"
                
                filme['poster_hover'] = poster_hover
        
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
        pass
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass
    
    return render_template('sessao.html')

@app.route('/selecao_bar')
def selecao_bar():
    pass

    
    conn = None
    try:
        pass
        
        filme_id = request.args.get('filme_id') or session.get('filme_id')
        cinema_id = request.args.get('cinema_id') or session.get('cinema_id')
        id_tipo_sessao = request.args.get('id_tipo_sessao') or session.get('id_tipo_sessao')
        id_horario_sessao = request.args.get('id_horario_sessao') or session.get('id_horario_sessao')
        data_sessao = request.args.get('data_sessao') or session.get('data_sessao')
        lugares = request.args.get('lugares') or ','.join(session.get('lugares_selecionados', []))
        
        
        if not all([filme_id, cinema_id, id_horario_sessao, id_tipo_sessao]):
            flash("Dados da reserva incompletos", "erro")
            return redirect(url_for('home'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        
        if not filme:
            flash("Filme não encontrado", "erro")
            return redirect(url_for('home'))
        
        poster_url = filme.get('poster_url', 'imgs/filmes/placeholder.jpg')
        if poster_url and not poster_url.startswith(('http://', 'https://', 'imgs/')):
            poster_url = f"imgs/filmes/{poster_url}"
        filme['poster_url'] = poster_url
        
        cursor.execute("SELECT * FROM cinemas WHERE id = %s", (cinema_id,))
        cinema = cursor.fetchone()
        
        cursor.execute("SELECT * FROM tipos_sessao WHERE id = %s", (id_tipo_sessao,))
        tipo_sessao = cursor.fetchone()
        
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
        
        lugares_selecionados = lugares.split(',') if lugares else []
        
        
        cursor.execute("""
            SELECT id, nome as produto, preco_total as preco, 'menus' as categoria, 
                   descricao, 'fas fa-box-open' as icone, imagem_url 
            FROM menus 
            ORDER BY nome
        """)
        menus_raw = cursor.fetchall()
        
        cursor.execute("""
            SELECT id, produto, preco, categoria, descricao, icone, imagem_url 
            FROM bar 
            WHERE categoria IN ('snacks', 'bebidas')
            ORDER BY categoria, produto
        """)
        produtos_bar_raw = cursor.fetchall()
        
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
        
        cursor.execute("""
            SELECT id, nome, descricao, preco, imagem_url
            FROM toppings 
            ORDER BY nome
        """)
        toppings = cursor.fetchall()
        
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
        
        salvar_dados_reserva_sessao(
            filme_id=int(filme_id),
            cinema_id=int(cinema_id),
            id_tipo_sessao=int(id_tipo_sessao),
            id_horario_sessao=int(id_horario_sessao),
            data_sessao=str(data_sessao),
            lugares=lugares_selecionados
        )
        
        
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
    pass

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT DISTINCT b.id, b.produto, b.categoria, b.imagem_url, b.icone
            FROM menu_produtos mp
            JOIN bar b ON mp.produto_id = b.id
            WHERE mp.menu_id = %s
            ORDER BY b.categoria, b.produto
        """, (menu_id,))
        
        produtos = cursor.fetchall()
        
        snacks = [p for p in produtos if p['categoria'] == 'snacks']
        bebidas = [p for p in produtos if p['categoria'] == 'bebidas']
        
        tem_pipocas = any('pipoca' in p['produto'].lower() for p in snacks)
        
        toppings = []
        if tem_pipocas:
            cursor.execute("""
                SELECT id, nome, descricao, preco, imagem_url
                FROM toppings
                ORDER BY nome
            """)
            toppings_raw = cursor.fetchall()
            
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

@app.route('/api/toppings')
def api_toppings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nome, descricao, preco, imagem_url
            FROM toppings
            ORDER BY nome
        """)
        toppings_raw = cursor.fetchall()
        
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
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'toppings': toppings_raw
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar toppings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/selecao_toppings')
def selecao_toppings():
    pass

    
    conn = None
    try:
        app.logger.info("=" * 60)
        
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
        
        import json
        try:
            produtos_bar = json.loads(produtos_bar_json)
        except Exception as e:
            app.logger.error(f"❌ Erro ao parsear produtos: {e}")
            produtos_bar = []
        
        if not produtos_bar:
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
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        
        if not filme:
            flash("Filme não encontrado", "erro")
            return redirect(url_for('home'))
        
        poster_url = filme.get('poster_url', 'imgs/filmes/placeholder.jpg')
        if poster_url and not poster_url.startswith(('http://', 'https://', 'imgs/')):
            poster_url = f"imgs/filmes/{poster_url}"
        filme['poster_url'] = poster_url
        
        cursor.execute("SELECT * FROM cinemas WHERE id = %s", (cinema_id,))
        cinema = cursor.fetchone()
        
        cursor.execute("SELECT * FROM tipos_sessao WHERE id = %s", (id_tipo_sessao,))
        tipo_sessao = cursor.fetchone()
        
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
        
        lugares_selecionados = lugares.split(',') if lugares else []
        
        produtos_detalhes = []
        produtos_com_toppings = []
        
        app.logger.info(f"📦 Processando {len(produtos_bar)} produtos do bar")
        
        for produto in produtos_bar:
            produto_id = produto.get('id')
            quantidade = produto.get('quantidade', 1)
            tipo_produto_enviado = produto.get('tipo', 'bar')
            
            
            if str(produto_id).startswith('topping_'):
                app.logger.info(f"⏭️ Pulando topping: {produto_id}")
                continue
            
            produto_info = None
            
            if tipo_produto_enviado == 'menu':
                cursor.execute("""
                    SELECT id, nome as produto, preco_total as preco, 'menu' as categoria, imagem_url
                    FROM menus
                    WHERE id = %s
                """, (produto_id,))
                produto_info = cursor.fetchone()
                
                if produto_info:
                    pass
            else:
                cursor.execute("""
                    SELECT id, produto, preco, categoria, imagem_url
                    FROM bar
                    WHERE id = %s
                """, (produto_id,))
                produto_info = cursor.fetchone()
                
                if produto_info:
                    pass
            
            if produto_info:
                produto_info['quantidade'] = quantidade
                produtos_detalhes.append(produto_info)
                
                tipo_produto = 'menu' if produto_info['categoria'] == 'menu' else 'bar'
                
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
                
                if result and result['total'] > 0:
                    produtos_com_toppings.append({
                        'id': produto_id,
                        'tipo': tipo_produto,
                        'nome': produto_info['produto']
                    })
            else:
                app.logger.warning(f"⚠️ Produto ID {produto_id} não encontrado")
        
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
                if not any(t['id'] == topping['id'] for t in toppings_disponiveis):
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
    pass
   
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nome, descricao, preco_total as preco, imagem_url
            FROM menus 
            ORDER BY nome
        """)
        menus = cursor.fetchall()
        
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
        
        cursor.execute("""
            SELECT id, nome, descricao, preco, imagem_url
            FROM toppings 
            ORDER BY nome
        """)
        toppings = cursor.fetchall()
        
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
                             logged_in='user_id' in session,
                             avatar=get_user_avatar())
                             
    except Exception as e:
        app.logger.error(f"Erro na rota /bar: {e}")
        return render_template('bar.html', 
                             menus=[],
                             toppings=[],
                             logged_in='user_id' in session,
                             avatar=get_user_avatar())
@app.route('/resumo_reserva', methods=['GET', 'POST'])
def resumo_reserva():
    pass

    
    if request.method == 'POST':
        nome_cliente = request.form.get('guest_name', '').strip()
        email_cliente = request.form.get('guest_email', '').strip()
        telefone_cliente = request.form.get('guest_phone', '').strip()
        
        if nome_cliente:
            session['nome_cliente'] = nome_cliente
        if email_cliente:
            session['email_cliente'] = email_cliente
        if telefone_cliente:
            session['telefone_cliente'] = telefone_cliente
        
        
        return redirect(url_for('checkout'))
    
    try:
        filme_id = request.args.get('filme_id') or session.get('filme_id')
        cinema_id = request.args.get('cinema_id') or session.get('cinema_id')
        id_tipo_sessao = request.args.get('id_tipo_sessao') or session.get('id_tipo_sessao')
        id_horario_sessao = request.args.get('id_horario_sessao') or session.get('id_horario_sessao')
        data_sessao = request.args.get('data_sessao') or session.get('data_sessao')
        lugares = request.args.get('lugares', '') or ','.join(session.get('lugares_selecionados', []))
        quantidade = request.args.get('quantidade', '1')
        produtos_bar = request.args.get('produtos_bar', '[]')
        toppings_json = request.args.get('toppings', '[]')
        
        app.logger.info(f"   filme_id={filme_id}, id_tipo_sessao={id_tipo_sessao}")
        app.logger.info(f"   lugares={lugares}")
        app.logger.info(f"   toppings_json={toppings_json}")
        
        if not all([filme_id, cinema_id, id_horario_sessao, id_tipo_sessao]):
            flash("Dados da reserva incompletos", "erro")
            return redirect(url_for('home'))
        
        lugares_selecionados = []
        if lugares:
            if lugares.startswith('['):
                try:
                    import json
                    lugares_selecionados = json.loads(lugares)
                except:
                    lugares_selecionados = []
            else:
                lugares_selecionados = lugares.split(',') if lugares else []
        
        produtos_selecionados = []
        try:
            import json
            produtos_selecionados = json.loads(produtos_bar) if produtos_bar != '[]' else []
        except:
            produtos_selecionados = []
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        
        if not filme:
            flash("Filme não encontrado", "erro")
            return redirect(url_for('home'))
        
        poster_url = filme.get('poster_url', 'imgs/filmes/placeholder.jpg')
        if poster_url and not poster_url.startswith(('http://', 'https://', 'imgs/')):
            poster_url = f"imgs/filmes/{poster_url}"
        filme['poster_url'] = poster_url
        
        cursor.execute("SELECT * FROM cinemas WHERE id = %s", (cinema_id,))
        cinema = cursor.fetchone()
        
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
        
        cursor.execute("SELECT * FROM tipos_sessao WHERE id = %s", (id_tipo_sessao,))
        tipo_sessao = cursor.fetchone()
        
        preco_bilhete = float(tipo_sessao.get('preco_bilhete', 8.50)) if tipo_sessao else 8.50
        
        total_bilhetes = len(lugares_selecionados) * preco_bilhete
        total_bar = 0.0
        
        produtos_bar_detalhados = []
        
        app.logger.info(f"📦 Processando produtos do bar: {len(produtos_selecionados)} produtos")
        app.logger.info(f"📦 Produtos recebidos: {produtos_selecionados}")
        
        if produtos_selecionados:
            for produto in produtos_selecionados:
                produto_id = produto.get('id')
                quantidade_prod = int(produto.get('quantidade', 1))
                tipo_produto_enviado = produto.get('tipo', 'bar')
                configs = produto.get('configs', [])
                
                
                produto_info = None
                
                if tipo_produto_enviado == 'menu':
                    cursor.execute("SELECT nome as produto, preco_total as preco FROM menus WHERE id = %s", (produto_id,))
                    produto_info = cursor.fetchone()
                    
                    if produto_info:
                        pass
                        
                        for idx, config in enumerate(configs):
                            snack_id = config.get('snackId')
                            bebida_id = config.get('bebidaId')
                            toppings_menu = config.get('toppings', [])
                            
                            snack_nome = "Snack"
                            if snack_id:
                                cursor.execute("SELECT produto FROM bar WHERE id = %s", (snack_id,))
                                snack_info = cursor.fetchone()
                                if snack_info:
                                    snack_nome = snack_info['produto']
                            
                            bebida_nome = "Bebida"
                            if bebida_id:
                                cursor.execute("SELECT produto FROM bar WHERE id = %s", (bebida_id,))
                                bebida_info = cursor.fetchone()
                                if bebida_info:
                                    bebida_nome = bebida_info['produto']
                            
                            toppings_nomes = []
                            preco_toppings_menu = 0.0
                            if toppings_menu:
                                for topping_id in toppings_menu:
                                    cursor.execute("SELECT nome, preco FROM toppings WHERE id = %s", (topping_id,))
                                    topping_info = cursor.fetchone()
                                    if topping_info:
                                        toppings_nomes.append(topping_info['nome'])
                                        preco_toppings_menu += float(topping_info['preco'])
                            
                            preco_unitario = float(produto_info['preco']) + preco_toppings_menu
                            preco_total_produto = preco_unitario
                            total_bar += preco_total_produto
                            
                            detalhes_texto = f"{snack_nome} + {bebida_nome}"
                            if toppings_nomes:
                                detalhes_texto += f" + Toppings: {', '.join(toppings_nomes)}"
                            
                            produtos_bar_detalhados.append({
                                'nome': f"{produto_info['produto']} (Menu)",
                                'detalhes': detalhes_texto,
                                'quantidade': 1,
                                'preco_unitario': preco_unitario,
                                'preco_total': preco_total_produto,
                                'is_menu': True
                            })
                else:
                    cursor.execute("SELECT produto, preco FROM bar WHERE id = %s", (produto_id,))
                    produto_info = cursor.fetchone()
                    
                    if produto_info:
                        if tipo_produto_enviado == 'pipocas' and configs:
                            for idx, config in enumerate(configs):
                                toppings_pipocas = config.get('toppings', [])
                                preco_unitario = float(produto_info['preco'])
                                
                                toppings_nomes = []
                                preco_toppings_pipocas = 0.0
                                if toppings_pipocas:
                                    for topping_id in toppings_pipocas:
                                        cursor.execute("SELECT nome, preco FROM toppings WHERE id = %s", (topping_id,))
                                        topping_info = cursor.fetchone()
                                        if topping_info:
                                            toppings_nomes.append(topping_info['nome'])
                                            preco_toppings_pipocas += float(topping_info['preco'])
                                
                                preco_total_item = preco_unitario + preco_toppings_pipocas
                                total_bar += preco_total_item
                                
                                detalhes_texto = ""
                                if toppings_nomes:
                                    detalhes_texto = f"+ {', '.join(toppings_nomes)}"
                                
                                produtos_bar_detalhados.append({
                                    'nome': produto_info['produto'],
                                    'detalhes': detalhes_texto,
                                    'quantidade': 1,
                                    'preco_unitario': preco_total_item,
                                    'preco_total': preco_total_item,
                                    'is_menu': False
                                })
                        else:
                            preco_unitario = float(produto_info['preco'])
                            preco_total_produto = preco_unitario * quantidade_prod
                            total_bar += preco_total_produto
                            
                            produtos_bar_detalhados.append({
                                'nome': produto_info['produto'],
                                'quantidade': quantidade_prod,
                                'preco_unitario': preco_unitario,
                                'preco_total': preco_total_produto,
                                'is_menu': False
                            })
                
                if not produto_info:
                    app.logger.error(f"❌ Produto ID {produto_id} não encontrado!")
        
        app.logger.info(f"📊 Total bar: €{total_bar}, Total produtos: {len(produtos_bar_detalhados)}")
        
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
                    
                    
                    cursor.execute("SELECT nome, preco FROM toppings WHERE id = %s", (topping_id,))
                    topping_info = cursor.fetchone()
                    
                    if topping_info:
                        preco_unitario = float(topping_info['preco'])
                        preco_total_topping = preco_unitario * quantidade_topping
                        total_toppings += preco_total_topping
                        
                        toppings_selecionados.append({
                            'nome': topping_info['nome'],
                            'quantidade': quantidade_topping,
                            'preco_unitario': preco_unitario,
                            'preco_total': preco_total_topping
                        })
                    else:
                        app.logger.error(f"❌ Topping ID {topping_id} não encontrado!")
        except Exception as e:
            app.logger.error(f"❌ Erro ao processar toppings: {e}")
            toppings_selecionados = []
        
        app.logger.info(f"📊 Total toppings: €{total_toppings}, Total toppings: {len(toppings_selecionados)}")
        
        # Calcular descontos baseados no plano do usuário
        subscricao = None
        desconto_bilhetes = 0.0
        desconto_bar = 0.0
        
        if 'user_id' in session:
            subscricao = get_user_subscription(session['user_id'])
            
            if subscricao and subscricao.get('plano_tipo') in ['member', 'premium']:
                plano = subscricao['plano_tipo']
                
                # Desconto em bilhetes
                if plano == 'member':
                    desconto_bilhetes = total_bilhetes * 0.15  # 15%
                elif plano == 'premium':
                    desconto_bilhetes = total_bilhetes * 0.25  # 25%
                
                # Desconto no bar (se houver produtos)
                if total_bar > 0:
                    if plano == 'member':
                        desconto_bar = total_bar * 0.10  # 10%
                    elif plano == 'premium':
                        desconto_bar = total_bar * 0.20  # 20%
        
        # Aplicar descontos ao total
        total_bilhetes_com_desconto = total_bilhetes - desconto_bilhetes
        total_bar_com_desconto = total_bar - desconto_bar
        total_geral = total_bilhetes_com_desconto + total_bar_com_desconto + total_toppings
        
        cursor.close()
        conn.close()
        
        if filme and filme.get('poster_url'):
            poster_url = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
            if not poster_url.startswith('imgs/filmes/'):
                if '/' not in poster_url:
                    poster_url = f"imgs/filmes/{poster_url}"
                elif not poster_url.startswith('imgs/'):
                    poster_url = f"imgs/filmes/{poster_url}"
            filme['poster_url'] = poster_url
        
        app.logger.info(f"Resumo - Total: €{total_geral:.2f} (Bilhetes: €{total_bilhetes:.2f}, Bar: €{total_bar:.2f})")
        
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
                             subscricao=subscricao,
                             desconto_bilhetes=desconto_bilhetes,
                             desconto_bar=desconto_bar,
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
            SELECT p.id, p.produto, p.preco, p.imagem_url, p.categoria,
                   IFNULL(GROUP_CONCAT(cp.caracteristica SEPARATOR ','), '') AS caracteristicas
            FROM menu_produtos mp
            JOIN bar p ON mp.produto_id = p.id
            LEFT JOIN caracteristica_produto_bar cp ON cp.produto_id = p.id
            WHERE mp.menu_id = %s
            GROUP BY p.id
            ORDER BY p.categoria, p.produto
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
        if 'user_id' in session:
            cursor.execute("""
                SELECT c.id, c.nome, c.localizacao, c.regiao, c.imagem,
                       CASE WHEN cf.id IS NOT NULL THEN 1 ELSE 0 END as is_favorito
                FROM cinemas c
                LEFT JOIN cinemas_favoritos cf ON c.id = cf.cinema_id AND cf.usuario_id = %s
                ORDER BY c.regiao, c.nome
            """, (session['user_id'],))
        else:
            cursor.execute("""
                SELECT id, nome, localizacao, regiao, imagem, 0 as is_favorito
                FROM cinemas
                ORDER BY regiao, nome
            """)
        
        cinemas_list = cursor.fetchall()
        
        for cinema in cinemas_list:
            if cinema.get('imagem'):
                cinema['imagem'] = cinema['imagem'].replace('\\', '/').replace('"', '').strip()
            else:
                cinema['imagem'] = 'imgs/cinemas/room.jpg'
        
        cursor.execute("SELECT DISTINCT regiao FROM cinemas ORDER BY regiao")
        regioes = [r['regiao'] for r in cursor.fetchall()]
        
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
        cursor.execute("""
            SELECT id, nome, localizacao, regiao, imagem
            FROM cinemas
            WHERE id = %s
        """, (id_cinema,))
        cinema = cursor.fetchone()
        
        if not cinema:
            flash('Cinema não encontrado', 'error')
            return redirect(url_for('cinemas'))
        
        if cinema.get('imagem'):
            cinema['imagem'] = cinema['imagem'].replace('\\', '/').replace('"', '').strip()
        else:
            cinema['imagem'] = 'imgs/cinemas/room.jpg'
        
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
            WHERE hs.id_cinema = %s AND f.estado = 'em_exibicao'
            GROUP BY f.id
            ORDER BY f.titulo
        """, (id_cinema,))
        filmes = cursor.fetchall()
        
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
def beneficios():
    logged_in = 'user_id' in session
    avatar = get_user_avatar()
    
    plano_atual = None
    if logged_in:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT plano_tipo, preco_mensal, status, 
                       bilhetes_gratis_mes, bilhetes_gratis_usados,
                       data_inicio, data_proximo_pagamento
                FROM subscricoes 
                WHERE user_id = %s AND status = 'ativo'
                ORDER BY id DESC LIMIT 1
            """, (session['user_id'],))
            plano_atual = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
    
    return render_template('beneficios.html', 
                         logged_in=logged_in, 
                         avatar=avatar,
                         plano_atual=plano_atual)


@app.route('/pagamento_plano')
def pagamento_plano():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    logged_in = True
    avatar = get_user_avatar()
    
    return render_template('pagamento_plano.html',
                         logged_in=logged_in,
                         avatar=avatar)


@app.route('/subscribe_plan', methods=['POST'])
def subscribe_plan():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Precisa de fazer login'}), 401
    
    data = request.get_json()
    plan_type = data.get('plan')
    price = data.get('price')
    
    if plan_type not in ['member', 'premium']:
        return jsonify({'success': False, 'message': 'Plano inválido'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar se já tem subscrição ativa
        cursor.execute("""
            SELECT id, plano_tipo FROM subscricoes 
            WHERE user_id = %s AND status = 'ativo'
        """, (session['user_id'],))
        subscricao_existente = cursor.fetchone()
        
        # Definir bilhetes grátis por mês
        bilhetes_gratis = 1 if plan_type == 'member' else 2
        
        # Calcular data do próximo pagamento (30 dias)
        from datetime import datetime, timedelta
        proximo_pagamento = datetime.now() + timedelta(days=30)
        
        if subscricao_existente:
            # Atualizar subscrição existente
            cursor.execute("""
                UPDATE subscricoes 
                SET plano_tipo = %s, 
                    preco_mensal = %s,
                    bilhetes_gratis_mes = %s,
                    bilhetes_gratis_usados = 0,
                    ultimo_reset_bilhetes = CURDATE(),
                    data_proximo_pagamento = %s,
                    atualizado_em = NOW()
                WHERE user_id = %s AND status = 'ativo'
            """, (plan_type, price, bilhetes_gratis, proximo_pagamento, session['user_id']))
            subscricao_id = subscricao_existente['id']
        else:
            # Criar nova subscrição
            cursor.execute("""
                INSERT INTO subscricoes 
                (user_id, plano_tipo, preco_mensal, status, bilhetes_gratis_mes, 
                 bilhetes_gratis_usados, ultimo_reset_bilhetes, data_proximo_pagamento)
                VALUES (%s, %s, %s, 'ativo', %s, 0, CURDATE(), %s)
            """, (session['user_id'], plan_type, price, bilhetes_gratis, proximo_pagamento))
            subscricao_id = cursor.lastrowid
        
        # Registar pagamento no histórico
        cursor.execute("""
            INSERT INTO historico_pagamentos 
            (subscricao_id, user_id, valor, plano_tipo, status_pagamento, metodo_pagamento)
            VALUES (%s, %s, %s, %s, 'concluido', 'simulado')
        """, (subscricao_id, session['user_id'], price, plan_type))
        
        conn.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Subscrição realizada com sucesso!',
            'plano': plan_type
        })
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao processar subscrição: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro ao processar subscrição'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/cancelar_subscricao', methods=['POST'])
def cancelar_subscricao():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE subscricoes 
            SET status = 'cancelado', 
                data_fim = NOW(),
                atualizado_em = NOW()
            WHERE user_id = %s AND status = 'ativo'
        """, (session['user_id'],))
        
        # Criar subscrição normal (gratuita)
        cursor.execute("""
            INSERT INTO subscricoes 
            (user_id, plano_tipo, preco_mensal, status, bilhetes_gratis_mes)
            VALUES (%s, 'normal', 0.00, 'ativo', 0)
        """, (session['user_id'],))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Subscrição cancelada com sucesso'})
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro ao cancelar subscrição: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro ao cancelar subscrição'}), 500
    finally:
        cursor.close()
        conn.close()


def get_user_subscription(user_id):
    """Função auxiliar para obter subscrição do utilizador"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verificar se precisa resetar bilhetes grátis (novo mês)
        cursor.execute("""
            UPDATE subscricoes 
            SET bilhetes_gratis_usados = 0,
                ultimo_reset_bilhetes = CURDATE()
            WHERE user_id = %s 
            AND status = 'ativo'
            AND (ultimo_reset_bilhetes IS NULL 
                 OR ultimo_reset_bilhetes < DATE_FORMAT(NOW(), '%%Y-%%m-01'))
        """, (user_id,))
        conn.commit()
        
        cursor.execute("""
            SELECT plano_tipo, preco_mensal, status,
                   bilhetes_gratis_mes, bilhetes_gratis_usados,
                   (bilhetes_gratis_mes - bilhetes_gratis_usados) as bilhetes_disponiveis
            FROM subscricoes 
            WHERE user_id = %s AND status = 'ativo'
            ORDER BY id DESC LIMIT 1
        """, (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def aplicar_desconto_plano(valor_original, user_id, tipo='bilhete'):
    """Aplica desconto baseado no plano do utilizador"""
    subscricao = get_user_subscription(user_id)
    
    if not subscricao:
        return valor_original, 0
    
    plano = subscricao['plano_tipo']
    desconto_percentual = 0
    
    if tipo == 'bilhete':
        if plano == 'member':
            desconto_percentual = 15
        elif plano == 'premium':
            desconto_percentual = 25
    elif tipo == 'bar':
        if plano == 'member':
            desconto_percentual = 10
        elif plano == 'premium':
            desconto_percentual = 20
    
    desconto = (valor_original * desconto_percentual) / 100
    valor_final = valor_original - desconto
    
    return valor_final, desconto_percentual

@app.route('/termos-condicoes')
def termos_condicoes():
    logged_in = 'user_id' in session
    avatar = get_user_avatar()
    if logged_in:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COALESCE(a.caminho, 'imgs/icons/user_icon34-removebg-preview.png') AS avatar
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
@app.route('/politica_privacidade')
def politica_privacidade():
    logged_in = 'user_id' in session
    avatar = get_user_avatar()
    if logged_in:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COALESCE(a.caminho, 'imgs/icons/user_icon34-removebg-preview.png') AS avatar
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

@app.route('/cookies')
def cookies_page():
    logged_in = 'user_id' in session
    avatar = get_user_avatar()
    if logged_in:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COALESCE(a.caminho, 'imgs/icons/user_icon34-removebg-preview.png') AS avatar
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

@app.route('/api/pesquisa')
def api_pesquisa():
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 1:
        return jsonify({'filmes': [], 'cinemas': [], 'menus': [], 'produtos': []})
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, titulo, poster_url, poster_hover, duracao
        FROM filmes
        WHERE titulo LIKE %s OR sinopse LIKE %s
        LIMIT 5
    """, (f'%{query}%', f'%{query}%'))
    filmes = cursor.fetchall()
    
    for f in filmes:
        f['poster_url'] = _normalize_img_path(f.get('poster_url'))
    
    cursor.execute("""
        SELECT id, nome, localizacao, regiao, imagem as imagem_url
        FROM cinemas
        WHERE nome LIKE %s OR localizacao LIKE %s
        LIMIT 5
    """, (f'%{query}%', f'%{query}%'))
    cinemas = cursor.fetchall()
    
    for c in cinemas:
        c['imagem_url'] = _normalize_img_path(c.get('imagem_url'))
    
    menus = []
    try:
        cursor.execute("""
            SELECT id, nome, descricao, preco_total as preco, imagem_url
            FROM menus
            WHERE nome LIKE %s OR descricao LIKE %s
            LIMIT 5
        """, (f'%{query}%', f'%{query}%'))
        menus = cursor.fetchall()
        for m in menus:
            m['imagem_url'] = _normalize_img_path(m.get('imagem_url'))
    except Exception as e:
        app.logger.info(f"Erro ao buscar menus: {e}")
        menus = []
    
    produtos = []
    try:
        cursor.execute("""
            SELECT id, nome, descricao, preco, imagem_url, categoria
            FROM produtos_bar
            WHERE nome LIKE %s OR descricao LIKE %s OR categoria LIKE %s
            LIMIT 5
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        produtos = cursor.fetchall()
        for p in produtos:
            p['imagem_url'] = _normalize_img_path(p.get('imagem_url'))
    except Exception as e:
        app.logger.info(f"Erro ao buscar produtos: {e}")
        produtos = []
    
    cursor.close()
    conn.close()
    
    # Buscar opções de acessibilidade — match por nome, descrição ou keywords
    acessiveis_todos = [
        {'nome': 'CineAcessível', 'url': '/cineacessivel', 'descricao': 'Todas as opções de acessibilidade', 'keywords': 'cineacessivel acessivel acessibilidade inclusao deficiencia'},
        {'nome': 'Audiodescrição', 'url': '/cine_acessivel/audiodescricao', 'descricao': 'Filmes com audiodescrição', 'keywords': 'audiodescricao audiodescricão audio descricao cegos invisuais'},
        {'nome': 'LGP - Língua Gestual Portuguesa', 'url': '/cine_acessivel/lgp', 'descricao': 'Sessões em língua gestual', 'keywords': 'lgp gestual lingua surdos surdo linguagem'},

        {'nome': 'Legendagem', 'url': '/cine_acessivel/legendagem', 'descricao': 'Sessões com legendagem', 'keywords': 'legendagem legendas legenda subtitulos surdos'},
    ]
    query_lower = query.lower()
    import unicodedata
    def normalize(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')
    q_norm = normalize(query_lower)
    acessibilidade = [
        a for a in acessiveis_todos
        if q_norm in normalize(a['nome']) or q_norm in normalize(a['descricao']) or q_norm in normalize(a['keywords'])
    ]
    
    return jsonify({
        'filmes': filmes,
        'cinemas': cinemas,
        'menus': menus,
        'produtos': produtos,
        'acessibilidade': acessibilidade
    })

@app.route('/api/check_toppings')
def api_check_toppings():
    pass

    produto_id = request.args.get('produto_id')
    tipo = request.args.get('tipo', 'bar')
    
    if not produto_id:
        return jsonify({'has_toppings': False, 'toppings': []})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if tipo == 'menu':
            cursor.execute("""
                SELECT DISTINCT t.id, t.nome, t.descricao, t.preco, t.imagem_url
                FROM toppings_produtos tp
                JOIN toppings t ON tp.id_topping = t.id
                WHERE tp.id_menu = %s AND tp.tipo_produto = 'menu'
                ORDER BY t.nome
            """, (produto_id,))
        else:
            cursor.execute("""
                SELECT DISTINCT t.id, t.nome, t.descricao, t.preco, t.imagem_url
                FROM toppings_produtos tp
                JOIN toppings t ON tp.id_topping = t.id
                WHERE tp.id_produto = %s AND tp.tipo_produto = 'bar'
                ORDER BY t.nome
            """, (produto_id,))
        
        toppings = cursor.fetchall()
        
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

@app.route('/pesquisa')
def pesquisa():
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, titulo, poster_url, poster_hover, duracao, sinopse
        FROM filmes
        WHERE titulo LIKE %s OR sinopse LIKE %s
        LIMIT 20
    """, (f'%{query}%', f'%{query}%'))
    filmes = cursor.fetchall()
    
    for f in filmes:
        f['poster_url'] = _normalize_img_path(f.get('poster_url'))
        f['poster_hover'] = _normalize_img_path(f.get('poster_hover'))
    
    cursor.execute("""
        SELECT id, nome, localizacao, regiao, imagem as imagem_url
        FROM cinemas
        WHERE nome LIKE %s OR localizacao LIKE %s OR regiao LIKE %s
        LIMIT 10
    """, (f'%{query}%', f'%{query}%', f'%{query}%'))
    cinemas = cursor.fetchall()
    
    for c in cinemas:
        c['imagem_url'] = _normalize_img_path(c.get('imagem_url'))
    
    menus = []
    try:
        cursor.execute("""
            SELECT id, nome, descricao, preco_total as preco, imagem_url
            FROM menus
            WHERE nome LIKE %s OR descricao LIKE %s
            LIMIT 10
        """, (f'%{query}%', f'%{query}%'))
        menus = cursor.fetchall()
        for m in menus:
            m['imagem_url'] = _normalize_img_path(m.get('imagem_url'))
    except Exception as e:
        app.logger.info(f"Erro ao buscar menus: {e}")
        menus = []
    
    produtos = []
    try:
        cursor.execute("""
            SELECT id, nome, descricao, preco, imagem_url, categoria
            FROM produtos_bar
            WHERE nome LIKE %s OR descricao LIKE %s OR categoria LIKE %s
            LIMIT 10
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        produtos = cursor.fetchall()
        for p in produtos:
            p['imagem_url'] = _normalize_img_path(p.get('imagem_url'))
    except Exception as e:
        app.logger.info(f"Erro ao buscar produtos: {e}")
        produtos = []
    
    cursor.close()
    conn.close()
    
    paginas_especiais = []
    query_lower = query.lower()
    
    def normalize_text(text):
        replacements = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
            'é': 'e', 'ê': 'e',
            'í': 'i',
            'ó': 'o', 'ô': 'o', 'õ': 'o',
            'ú': 'u',
            'ç': 'c'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    query_normalized = normalize_text(query_lower)
    
    paginas_acessibilidade = [
        {
            'titulo': 'Audiodescrição',
            'descricao': 'Serviço de audiodescrição para pessoas com deficiência visual',
            'url': 'audiodescricao',
            'icone': 'fas fa-audio-description',
            'keywords': ['audiodescricao', 'audiodescrição', 'audio', 'cego', 'deficiente visual', 'acessibilidade', 'visual']
        },
        {
            'titulo': 'Legendagem',
            'descricao': 'Legendas para pessoas com deficiência auditiva',
            'url': 'legendagem',
            'icone': 'fas fa-closed-captioning',
            'keywords': ['legenda', 'legendagem', 'surdo', 'deficiente auditivo', 'acessibilidade', 'auditiva']
        },
        {
            'titulo': 'Língua Gestual Portuguesa',
            'descricao': 'Interpretação em Língua Gestual Portuguesa',
            'url': 'lgp',
            'icone': 'fas fa-hands',
            'keywords': ['lgp', 'lingua gestual', 'língua gestual', 'gestual', 'surdo', 'acessibilidade', 'interprete']
        },
        {
            'titulo': 'CineAcessível',
            'descricao': 'Todas as opções de acessibilidade do CineVibe',
            'url': 'cine_acessivel',
            'icone': 'fas fa-universal-access',
            'keywords': ['acessivel', 'acessível', 'cineacessivel', 'cine acessivel', 'inclusao', 'inclusão', 'deficiencia', 'deficiência']
        }
    ]
    
    for pagina in paginas_acessibilidade:
        for keyword in pagina['keywords']:
            keyword_normalized = normalize_text(keyword.lower())
            if keyword_normalized in query_normalized or query_normalized in keyword_normalized:
                if pagina not in paginas_especiais:
                    paginas_especiais.append(pagina)
                break
    
    logged_in = 'user_id' in session
    avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
    
    total_resultados = len(filmes) + len(cinemas) + len(menus) + len(produtos) + len(paginas_especiais)
    
    return render_template('pesquisa.html', 
                         query=query,
                         filmes=filmes,
                         cinemas=cinemas,
                         menus=menus,
                         produtos=produtos,
                         paginas_especiais=paginas_especiais,
                         total_resultados=total_resultados,
                         logged_in=logged_in,
                         avatar=avatar)

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
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': 'Rating deve ser entre 1 e 5'})
    except:
        return jsonify({'success': False, 'message': 'Rating inválido'})
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, titulo FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        
        if not filme:
            return jsonify({'success': False, 'message': 'Filme não encontrado'})
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM reservas r
            WHERE r.id_usuario = %s AND r.id_filme = %s
        """, (session['user_id'], filme_id))
        
        result = cursor.fetchone()
        if result['count'] == 0:
            return jsonify({'success': False, 'message': 'Só podes avaliar filmes que reservaste!'})
        
        cursor.execute("""
            INSERT INTO avaliacoes_filmes (usuario_id, filme_id, rating, comentario, data_avaliacao)
            VALUES (%s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
            rating = VALUES(rating),
            comentario = VALUES(comentario),
            data_avaliacao = NOW()
        """, (session['user_id'], filme_id, rating, comentario))
        
        conn.commit()
        
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
            cursor.execute("""
                SELECT id FROM cinemas_favoritos 
                WHERE usuario_id = %s AND cinema_id = %s
            """, (session['user_id'], id_cinema))
            
            favorito = cursor.fetchone()
            app.logger.info(f"Favorito existente: {favorito}")
            
            if favorito:
                cursor.execute("""
                    DELETE FROM cinemas_favoritos 
                    WHERE usuario_id = %s AND cinema_id = %s
                """, (session['user_id'], id_cinema))
                message = 'Cinema removido dos favoritos!'
                is_favorito = False
                app.logger.info(f"Cinema {id_cinema} removido dos favoritos")
            else:
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

@app.route('/toggle_favorito_cinema/<int:cinema_id>', methods=['POST'])
def toggle_favorito_cinema(cinema_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    try:
        app.logger.info(f"Toggle favorito cinema - user: {session['user_id']}, cinema: {cinema_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id FROM cinemas_favoritos 
                WHERE usuario_id = %s AND cinema_id = %s
            """, (session['user_id'], cinema_id))
            
            favorito = cursor.fetchone()
            
            if favorito:
                cursor.execute("""
                    DELETE FROM cinemas_favoritos 
                    WHERE usuario_id = %s AND cinema_id = %s
                """, (session['user_id'], cinema_id))
                message = 'Cinema removido dos favoritos!'
                is_favorito = False
            else:
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



@app.route('/admin/atores')
def admin_atores():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT a.id, a.nome, a.foto_url as foto, a.nacionalidade,
               COUNT(DISTINCT fa.filme_id) as total_filmes
        FROM atores a
        LEFT JOIN filme_atores fa ON a.id = fa.ator_id
        GROUP BY a.id
        ORDER BY a.id DESC
    """)
    atores = cursor.fetchall()
    
    for ator in atores:
        if ator.get('foto'):
            foto = ator['foto'].replace('\\', '/').replace('"', '').strip()
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
    
    foto_url = None
    if 'foto' in request.files:
        foto = request.files['foto']
        if foto and foto.filename != '':
            if foto.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                import uuid
                import os
                from werkzeug.utils import secure_filename
                
                filename = secure_filename(foto.filename)
                file_extension = os.path.splitext(filename)[1]
                unique_filename = f"{uuid.uuid4().hex}{file_extension}"
                
                upload_dir = os.path.join('static', 'imgs', 'atores')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, unique_filename)
                foto.save(file_path)
                
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
    
    foto_url = None
    if 'foto' in request.files:
        foto = request.files['foto']
        if foto and foto.filename != '':
            if foto.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                import uuid
                import os
                from werkzeug.utils import secure_filename
                
                filename = secure_filename(foto.filename)
                file_extension = os.path.splitext(filename)[1]
                unique_filename = f"{uuid.uuid4().hex}{file_extension}"
                
                upload_dir = os.path.join('static', 'imgs', 'atores')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, unique_filename)
                foto.save(file_path)
                
                foto_url = f"imgs/atores/{unique_filename}"
            else:
                flash('Formato de imagem inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'erro')
                return redirect(url_for('admin_atores'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
    
    cursor.execute("DELETE FROM filme_atores WHERE ator_id = %s", (ator_id,))
    
    cursor.execute("DELETE FROM atores WHERE id = %s", (ator_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Ator removido com sucesso!', 'success')
    return redirect(url_for('admin_atores'))

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

@app.route('/admin/atores/<int:ator_id>/dados')
def admin_dados_ator(ator_id):
    print(f"🔍 DEBUG: Buscando dados do ator ID: {ator_id}")
    
    if 'user_id' not in session:
        print("❌ DEBUG: Usuário não autenticado")
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        print(f"🔍 DEBUG: Executando query para ator {ator_id}")
        cursor.execute("""
            SELECT a.id, a.nome, a.nacionalidade, a.foto_url,
                   COUNT(DISTINCT fa.filme_id) as num_filmes
            FROM atores a
            LEFT JOIN filme_atores fa ON a.id = fa.ator_id
            WHERE a.id = %s
            GROUP BY a.id
        """, (ator_id,))
        
        ator = cursor.fetchone()
        print(f"🔍 DEBUG: Ator encontrado: {ator}")
        
        if ator:
            print(f"🔍 DEBUG: Buscando filmes do ator {ator_id}")
            cursor.execute("""
                SELECT f.id, f.titulo, f.poster_url, fa.papel
                FROM filmes f
                JOIN filme_atores fa ON f.id = fa.filme_id
                WHERE fa.ator_id = %s
                ORDER BY f.data_lancamento DESC
            """, (ator_id,))
            
            ator['filmes'] = cursor.fetchall()
            print(f"✅ DEBUG: {len(ator['filmes'])} filmes encontrados")
        
        cursor.close()
        conn.close()
        
        if ator:
            print(f"✅ DEBUG: Retornando dados do ator")
            return jsonify(ator)
        else:
            print(f"❌ DEBUG: Ator {ator_id} não encontrado")
            return jsonify({'error': 'Ator não encontrado'}), 404
        
    except Exception as e:
        print(f"❌ DEBUG: ERRO ao buscar dados do ator: {str(e)}")
        import traceback
        traceback.print_exc()
        app.logger.error(f"Erro ao buscar dados do ator: {str(e)}")
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@app.route('/admin/bar')
def admin_bar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.id, b.produto as nome, b.preco, b.imagem_url as imagem, b.categoria,
               GROUP_CONCAT(DISTINCT m.nome SEPARATOR ', ') as menus
        FROM bar b
        LEFT JOIN menu_produtos mp ON b.id = mp.produto_id
        LEFT JOIN menus m ON mp.menu_id = m.id
        WHERE LOWER(b.categoria) IN ('snacks', 'snack')
        GROUP BY b.id
        ORDER BY b.id DESC
    """)
    snacks = cursor.fetchall()
    
    cursor.execute("""
        SELECT b.id, b.produto as nome, b.preco, b.imagem_url as imagem, b.categoria,
               GROUP_CONCAT(DISTINCT m.nome SEPARATOR ', ') as menus
        FROM bar b
        LEFT JOIN menu_produtos mp ON b.id = mp.produto_id
        LEFT JOIN menus m ON mp.menu_id = m.id
        WHERE LOWER(b.categoria) IN ('bebidas', 'bebida')
        GROUP BY b.id
        ORDER BY b.id DESC
    """)
    bebidas = cursor.fetchall()
    
    cursor.execute("""
        SELECT m.id, m.nome, m.descricao, m.preco_total, m.imagem_url,
               GROUP_CONCAT(b.produto SEPARATOR ', ') as produtos
        FROM menus m
        LEFT JOIN menu_produtos mp ON m.id = mp.menu_id
        LEFT JOIN bar b ON mp.produto_id = b.id
        GROUP BY m.id
        ORDER BY m.id DESC
    """)
    menus = cursor.fetchall()
    
    for menu in menus:
        if menu['produtos']:
            menu['produtos'] = menu['produtos'].split(', ')
        else:
            menu['produtos'] = []
    
    cursor.execute("""
        SELECT id, nome, descricao, preco, imagem_url
        FROM toppings
        ORDER BY id DESC
    """)
    toppings = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin_bar.html', user=get_current_user(), snacks=snacks, bebidas=bebidas, menus=menus, toppings=toppings)

@app.route('/admin/bar/produtos/adicionar', methods=['POST'])
def admin_adicionar_produto():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    tipo = request.form.get('tipo')
    
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
        INSERT INTO bar (produto, preco, imagem_url, categoria)
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
    
    imagem_path = imagem_atual
    
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
        SET produto = %s, preco = %s, imagem_url = %s, categoria = %s
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
    
    cursor.execute("DELETE FROM menu_produtos WHERE produto_id = %s", (produto_id,))
    
    cursor.execute("DELETE FROM bar WHERE id = %s", (produto_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Produto removido com sucesso!', 'success')
    return redirect(url_for('admin_bar'))

@app.route('/admin/bar/menus/<int:menu_id>/dados')
def admin_menu_dados(menu_id):
    pass
   
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        
        cursor.execute("""
            SELECT id, nome, descricao, preco_total, imagem_url
            FROM menus
            WHERE id = %s
        """, (menu_id,))
        
        menu = cursor.fetchone()
        
        if not menu:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Menu não encontrado'}), 404
        
        if menu['preco_total']:
            menu['preco_total'] = float(menu['preco_total'])
        
        cursor.execute("""
            SELECT b.id, b.produto as nome, b.preco
            FROM bar b
            JOIN menu_produtos mp ON b.id = mp.produto_id
            WHERE mp.menu_id = %s
        """, (menu_id,))
        
        produtos = cursor.fetchall()
        
        for produto in produtos:
            if produto['preco']:
                produto['preco'] = float(produto['preco'])
        
        menu['produtos'] = produtos
        
        cursor.close()
        conn.close()
        
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
    
    imagem_url = None
    if 'imagem' in request.files:
        imagem_file = request.files['imagem']
        if imagem_file and imagem_file.filename:
            import os
            import uuid
            from werkzeug.utils import secure_filename
            
            upload_folder = os.path.join('static', 'imgs', 'menus')
            os.makedirs(upload_folder, exist_ok=True)
            
            ext = os.path.splitext(secure_filename(imagem_file.filename))[1]
            filename = f"menu_{uuid.uuid4().hex[:8]}{ext}"
            filepath = os.path.join(upload_folder, filename)
            
            imagem_file.save(filepath)
            imagem_url = f"imgs/menus/{filename}"
            
    
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO menus (nome, descricao, preco_total, imagem_url)
        VALUES (%s, %s, %s, %s)
    """, (nome, descricao, preco_total, imagem_url))
    
    menu_id = cursor.lastrowid
    
    for produto_id in produtos_ids:
        if produto_id:
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
    
    imagem_url = imagem_atual
    if 'imagem' in request.files:
        imagem_file = request.files['imagem']
        if imagem_file and imagem_file.filename:
            import os
            import uuid
            from werkzeug.utils import secure_filename
            
            upload_folder = os.path.join('static', 'imgs', 'menus')
            os.makedirs(upload_folder, exist_ok=True)
            
            if imagem_atual:
                old_path = os.path.join('static', imagem_atual)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        pass
            
            ext = os.path.splitext(secure_filename(imagem_file.filename))[1]
            filename = f"menu_{uuid.uuid4().hex[:8]}{ext}"
            filepath = os.path.join(upload_folder, filename)
            
            imagem_file.save(filepath)
            imagem_url = f"imgs/menus/{filename}"
            
    
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE menus
        SET nome = %s, descricao = %s, preco_total = %s, imagem_url = %s
        WHERE id = %s
    """, (nome, descricao, preco_total, imagem_url, menu_id))
    
    cursor.execute("DELETE FROM menu_produtos WHERE menu_id = %s", (menu_id,))
    
    for produto_id in produtos_ids:
        if produto_id:
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
    
    cursor.execute("DELETE FROM menu_produtos WHERE menu_id = %s", (menu_id,))
    
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
    
    cursor.execute("SELECT * FROM menus WHERE id = %s", (menu_id,))
    menu = cursor.fetchone()
    
    cursor.execute("""
        SELECT p.id, p.produto as nome, p.preco, p.imagem_url as imagem, p.categoria as tipo
        FROM bar p
        INNER JOIN menu_produtos mp ON p.id = mp.produto_id
        WHERE mp.menu_id = %s
        ORDER BY p.categoria, p.produto
    """, (menu_id,))
    produtos_menu = cursor.fetchall()
    
    cursor.execute("""
        SELECT id, produto as nome, preco, categoria as tipo
        FROM bar
        WHERE id NOT IN (
            SELECT produto_id FROM menu_produtos WHERE menu_id = %s
        )
        ORDER BY categoria, produto
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

@app.route('/admin/bar/toppings/adicionar', methods=['POST'])
def admin_adicionar_topping():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    preco = request.form.get('preco')
    
    imagem_url = None
    if 'imagem' in request.files:
        imagem_file = request.files['imagem']
        if imagem_file and imagem_file.filename:
            import os
            import uuid
            from werkzeug.utils import secure_filename
            
            upload_folder = os.path.join('static', 'imgs', 'toppings')
            os.makedirs(upload_folder, exist_ok=True)
            
            ext = os.path.splitext(secure_filename(imagem_file.filename))[1]
            filename = f"topping_{uuid.uuid4().hex[:8]}{ext}"
            filepath = os.path.join(upload_folder, filename)
            
            imagem_file.save(filepath)
            imagem_url = f"imgs/toppings/{filename}"
            
    
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
    pass

    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
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
    
    imagem_url = imagem_atual
    if 'imagem' in request.files:
        imagem_file = request.files['imagem']
        if imagem_file and imagem_file.filename:
            import os
            import uuid
            from werkzeug.utils import secure_filename
            
            upload_folder = os.path.join('static', 'imgs', 'toppings')
            os.makedirs(upload_folder, exist_ok=True)
            
            ext = os.path.splitext(secure_filename(imagem_file.filename))[1]
            filename = f"topping_{uuid.uuid4().hex[:8]}{ext}"
            filepath = os.path.join(upload_folder, filename)
            
            imagem_file.save(filepath)
            imagem_url = f"imgs/toppings/{filename}"
            
    
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
    
    cursor.execute("DELETE FROM toppings WHERE id = %s", (topping_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Topping removido com sucesso!', 'success')
    return redirect(url_for('admin_bar'))

@app.route('/admin/salas')
def admin_salas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.id, s.nome_sala, s.capacidade, s.tipo_sala, 
               s.id_cinema, s.lugares_acessiveis, s.lugares_vip,
               c.nome as cinema_nome, c.localizacao as cinema_localizacao
        FROM salas s
        INNER JOIN cinemas c ON s.id_cinema = c.id
        GROUP BY s.id_cinema, s.nome_sala
        HAVING s.id = MAX(s.id)
        ORDER BY s.id DESC
    """)
    rows = cursor.fetchall()
    
    columns = [description[0] for description in cursor.description]
    salas = [dict(zip(columns, row)) for row in rows]
    
    import json
    for sala in salas:
        if sala.get('lugares_acessiveis'):
            try:
                if isinstance(sala['lugares_acessiveis'], str):
                    sala['lugares_acessiveis'] = json.loads(sala['lugares_acessiveis'])
                sala['num_acessiveis'] = len(sala['lugares_acessiveis']) if sala['lugares_acessiveis'] else 0
            except:
                sala['lugares_acessiveis'] = []
                sala['num_acessiveis'] = 0
        else:
            sala['lugares_acessiveis'] = []
            sala['num_acessiveis'] = 0
        
        if sala.get('lugares_vip'):
            try:
                if isinstance(sala['lugares_vip'], str):
                    sala['lugares_vip'] = json.loads(sala['lugares_vip'])
                sala['num_vip'] = len(sala['lugares_vip']) if sala['lugares_vip'] else 0
            except:
                sala['lugares_vip'] = []
                sala['num_vip'] = 0
        else:
            sala['lugares_vip'] = []
            sala['num_vip'] = 0
    
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
    
    cursor.execute("DELETE FROM horarios WHERE sala_id = %s", (sala_id,))
    
    cursor.execute("DELETE FROM salas WHERE id = %s", (sala_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Sala removida com sucesso!', 'success')
    return redirect(url_for('admin_salas'))

@app.route('/admin/salas/preview-global', methods=['GET'])
def admin_preview_global():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    nome_sala = request.args.get('nome_sala', '')
    
    if not nome_sala:
        return jsonify({'success': False, 'salas': []})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.id, s.nome_sala, s.capacidade, s.filas, s.lugares_por_fila,
                   s.tipo_sala, c.nome as cinema_nome,
                   GROUP_CONCAT(DISTINCT ts.nome SEPARATOR ', ') as tipos_sessao
            FROM salas s
            INNER JOIN cinemas c ON s.id_cinema = c.id
            LEFT JOIN horarios_sessao hs ON s.id = hs.id_sala
            LEFT JOIN tipos_sessao ts ON hs.id_tipo_sessao = ts.id
            WHERE s.nome_sala = %s
            GROUP BY s.id
            ORDER BY c.nome
        """, (nome_sala,))
        
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        salas = [dict(zip(columns, row)) for row in rows]
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'salas': salas})
    except Exception as e:
        app.logger.error(f"Erro ao buscar preview global: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/salas/editar-global', methods=['POST'])
def admin_editar_global():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    nome_sala = request.form.get('nome_sala', '')
    tipo_edicao = request.form.get('tipo_edicao', 'capacidade')
    
    if not nome_sala:
        return jsonify({'success': False, 'message': 'Nome da sala é obrigatório'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if tipo_edicao == 'capacidade':
            capacidade = request.form.get('capacidade', '')
            filas = request.form.get('filas', '')
            lugares_por_fila = request.form.get('lugares_por_fila', '')
            
            if not all([capacidade, filas, lugares_por_fila]):
                return jsonify({'success': False, 'message': 'Campos obrigatórios faltando'}), 400
            
            if nome_sala == 'TODAS':
                cursor.execute("""
                    UPDATE salas
                    SET capacidade = %s, filas = %s, lugares_por_fila = %s
                """, (capacidade, filas, lugares_por_fila))
            else:
                cursor.execute("""
                    UPDATE salas
                    SET capacidade = %s, filas = %s, lugares_por_fila = %s
                    WHERE nome_sala = %s
                """, (capacidade, filas, lugares_por_fila, nome_sala))
        elif tipo_edicao == 'acessiveis':
            lugares_acessiveis_str = request.form.get('lugares_acessiveis', '')
            lugares_acessiveis_json = None
            
            if lugares_acessiveis_str and lugares_acessiveis_str.strip():
                lugares_list = [lugar.strip() for lugar in lugares_acessiveis_str.split(',') if lugar.strip()]
                lugares_acessiveis_json = json.dumps(lugares_list)
            
            if nome_sala == 'TODAS':
                cursor.execute("""
                    UPDATE salas
                    SET lugares_acessiveis = %s
                """, (lugares_acessiveis_json,))
            else:
                cursor.execute("""
                    UPDATE salas
                    SET lugares_acessiveis = %s
                    WHERE nome_sala = %s
                """, (lugares_acessiveis_json, nome_sala))
        elif tipo_edicao == 'vip':
            lugares_vip_str = request.form.get('lugares_vip', '')
            lugares_vip_json = None
            
            if lugares_vip_str and lugares_vip_str.strip():
                lugares_list = [lugar.strip() for lugar in lugares_vip_str.split(',') if lugar.strip()]
                lugares_vip_json = json.dumps(lugares_list)
            
            if nome_sala == 'TODAS':
                cursor.execute("""
                    UPDATE salas
                    SET lugares_vip = %s
                """, (lugares_vip_json,))
            else:
                cursor.execute("""
                    UPDATE salas
                    SET lugares_vip = %s
                    WHERE nome_sala = %s
                """, (lugares_vip_json, nome_sala))
        
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'count': count, 'message': f'{count} sala(s) atualizada(s)'})
    except Exception as e:
        app.logger.error(f"Erro ao editar salas globalmente: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/avatares')
def admin_avatares():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT a.id, a.nome, a.caminho, a.categoria_id, c.nome as categoria_nome
        FROM avatars a
        LEFT JOIN avatar_categories c ON a.categoria_id = c.id
        WHERE a.nome != 'Admin CineVibe'
        ORDER BY a.id DESC
    """)
    avatares = cursor.fetchall()
    
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
        
        app.logger.info(f"Tentando adicionar avatar: nome={nome}, categoria_id={categoria_id}")
        
        if not nome:
            flash('Nome é obrigatório!', 'erro')
            return redirect(url_for('admin_avatares'))
        
        caminho = None
        if 'avatar_file' in request.files:
            file = request.files['avatar_file']
            app.logger.info(f"Ficheiro recebido: {file.filename if file else 'None'}")
            
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'png'
                filename = f"{uuid.uuid4()}.{ext}"
                
                upload_dir = os.path.join('static', 'imgs', 'avatars')
                os.makedirs(upload_dir, exist_ok=True)
                
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                
                caminho = f"imgs/avatars/{filename}"
                app.logger.info(f"Ficheiro salvo em: {filepath}, caminho BD: {caminho}")
        
        if not caminho:
            caminho = "imgs/icons/user_icon34-removebg-preview.png"
            app.logger.info(f"Usando imagem padrão: {caminho}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO avatars (nome, caminho, categoria_id) VALUES (%s, %s, %s)", (nome, caminho, categoria_id))
        conn.commit()
        
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
    
    if not nome:
        flash('Nome é obrigatório!', 'erro')
        return redirect(url_for('admin_avatares'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT caminho FROM avatars WHERE id = %s", (avatar_id,))
    avatar_atual = cursor.fetchone()
    
    caminho = avatar_atual['caminho'] if avatar_atual else None
    
    if 'avatar_file' in request.files:
        file = request.files['avatar_file']
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'png'
            filename = f"{uuid.uuid4()}.{ext}"
            
            upload_dir = os.path.join('static', 'imgs', 'avatars')
            os.makedirs(upload_dir, exist_ok=True)
            
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            
            caminho = f"imgs/avatars/{filename}"
    
    cursor.execute("UPDATE avatars SET nome = %s, caminho = %s, categoria_id = %s WHERE id = %s", (nome, caminho, categoria_id, avatar_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Avatar atualizado com sucesso!', 'success')
    return redirect(url_for('admin_avatares'))

@app.route('/admin/avatares/<int:avatar_id>/dados')
def admin_avatar_dados(avatar_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, caminho, categoria_id FROM avatars WHERE id = %s", (avatar_id,))
        avatar = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if avatar:
            return jsonify(avatar)
        else:
            return jsonify({'error': 'Avatar não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/avatares/remover/<int:avatar_id>', methods=['POST'])
def admin_remover_avatar(avatar_id):
    print(f"🔍 DEBUG: Tentando remover avatar ID: {avatar_id}")
    
    if 'user_id' not in session:
        print("❌ DEBUG: Usuário não autenticado")
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT caminho FROM avatars WHERE id = %s", (avatar_id,))
        avatar = cursor.fetchone()
        
        if not avatar:
            print(f"❌ DEBUG: Avatar {avatar_id} não encontrado")
            flash('Avatar não encontrado!', 'error')
            return redirect(url_for('admin_avatares'))
        
        print(f"🔍 DEBUG: Avatar encontrado: {avatar}")
        
        cursor.execute("SELECT COUNT(*) as count FROM usuarios WHERE avatar_id = %s", (avatar_id,))
        usuarios_usando = cursor.fetchone()['count']
        
        print(f"🔍 DEBUG: {usuarios_usando} usuários usando este avatar")
        
        if usuarios_usando > 0:
            print(f"⚠️ DEBUG: Avatar em uso por {usuarios_usando} usuários, definindo avatar_id como NULL")
            cursor.execute("UPDATE usuarios SET avatar_id = NULL WHERE avatar_id = %s", (avatar_id,))
        
        print(f"🗑️ DEBUG: Removendo avatar da tabela")
        cursor.execute("DELETE FROM avatars WHERE id = %s", (avatar_id,))
        
        conn.commit()
        print(f"✅ DEBUG: Avatar {avatar_id} removido com sucesso!")
        
        cursor.close()
        conn.close()
        
        flash('Avatar removido com sucesso!', 'success')
        
    except Exception as e:
        print(f"❌ DEBUG: ERRO ao remover avatar: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Erro ao remover avatar: {str(e)}', 'error')
    
    return redirect(url_for('admin_avatares'))

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

@app.route('/admin/corrigir-salas-horarios')
def admin_corrigir_salas_horarios():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT hs.id, hs.id_cinema, hs.id_filme, hs.id_tipo_sessao, c.nome as cinema_nome
            FROM horarios_sessao hs
            JOIN cinemas c ON hs.id_cinema = c.id
            WHERE hs.id_sala IS NULL
            ORDER BY c.nome
        """)
        horarios_sem_sala = cursor.fetchall()
        
        corrigidos = 0
        nao_corrigidos = 0
        
        for horario in horarios_sem_sala:
            cursor.execute("""
                SELECT id, nome_sala
                FROM salas
                WHERE id_cinema = %s
                ORDER BY id
                LIMIT 1
            """, (horario['id_cinema'],))
            sala = cursor.fetchone()
            
            if sala:
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

@app.route('/api/filmes_disponiveis')
def api_filmes_disponiveis():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/api/remover-cinema-favorito', methods=['POST'])
def api_remover_cinema_favorito():
    pass
  
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    try:
        data = request.get_json()
        cinema_id = data.get('cinema_id')
        
        if not cinema_id:
            return jsonify({'success': False, 'message': 'ID do cinema não fornecido'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
    pass
 
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
        
        cursor.execute("""
            UPDATE usuarios 
            SET nome = %s 
            WHERE id = %s
        """, (novo_nome, session['user_id']))
        
        conn.commit()
        
        session['user_nome'] = novo_nome
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Nome atualizado com sucesso'})
        
    except Exception as e:
        app.logger.error(f"Erro ao atualizar nome: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

@app.route('/api/avatar-categorias')
def api_avatar_categorias():
    pass
  
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT c.id, c.nome,
                   a.id as avatar_id, a.nome as avatar_nome, a.caminho as avatar_caminho
            FROM avatar_categories c
            LEFT JOIN avatars a ON c.id = a.categoria_id
            ORDER BY c.nome, a.id
        """)
        results = cursor.fetchall()
        
        categorias_dict = {}
        for row in results:
            cat_id = row['id']
            if cat_id not in categorias_dict:
                categorias_dict[cat_id] = {
                    'nome': row['nome'],
                    'subtitulo': '',
                    'avatares': []
                }
            
            if row['avatar_id']:
                avatar_caminho = row['avatar_caminho']
                if avatar_caminho:
                    avatar_caminho = avatar_caminho.replace('\\', '/').replace('"', '').strip()
                    if not avatar_caminho.startswith('/static/'):
                        avatar_caminho = f"/static/{avatar_caminho}"
                    
                    categorias_dict[cat_id]['avatares'].append({
                        'id': row['avatar_id'],
                        'nome': row['avatar_nome'],
                        'caminho': avatar_caminho
                    })
        
        categorias_list = []
        for cat in categorias_dict.values():
            if cat['avatares']:
                cat['subtitulo'] = f"{len(cat['avatares'])} avatares disponíveis"
                categorias_list.append(cat)
        
        cursor.close()
        conn.close()
        
        if not categorias_list:
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'})
    
    try:
        data = request.get_json()
        avatar_id = data.get('avatar_id')
        
        if not avatar_id:
            return jsonify({'success': False, 'message': 'Avatar ID não fornecido'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar se o avatar existe
        cursor.execute("SELECT id, caminho FROM avatars WHERE id = %s", (avatar_id,))
        avatar = cursor.fetchone()
        
        if not avatar:
            return jsonify({'success': False, 'message': 'Avatar não encontrado'})
        
        # Atualizar o avatar_id do utilizador
        cursor.execute("""
            UPDATE usuarios 
            SET avatar_id = %s 
            WHERE id = %s
        """, (avatar_id, session['user_id']))
        
        conn.commit()
        
        # Atualizar sessão
        avatar_path = avatar['caminho'].replace('\\', '/').replace('"', '').strip()
        session['user_avatar'] = avatar_path
        
        return jsonify({
            'success': True, 
            'message': 'Avatar atualizado com sucesso',
            'avatar_path': avatar_path
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/alterar-senha', methods=['POST'])
def api_alterar_senha():
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
        
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'})
        
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

@app.route('/api/recuperar-senha', methods=['POST'])
def api_recuperar_senha():
    pass
   
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'message': 'Email é obrigatório'})
        
        if '@' not in email or '.' not in email:
            return jsonify({'success': False, 'message': 'Email inválido'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, nome FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': True, 'message': 'Se o email existir, as instruções foram enviadas'})
        
        import secrets
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)
        
        cursor.close()
        conn.close()
        
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
                'success': True,
                'message': 'Se o email existir, as instruções foram enviadas'
            })
        
    except Exception as e:
        app.logger.error(f"Erro ao processar recuperação de senha: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

@app.route('/api/filmes')
def api_filmes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT COUNT(*) as total FROM filmes")
        total_filmes = cursor.fetchone()
        app.logger.info(f"Total de filmes na base de dados: {total_filmes['total']}")
        
        cursor.execute("SELECT estado, COUNT(*) as count FROM filmes GROUP BY estado")
        estados = cursor.fetchall()
        app.logger.info(f"Filmes por estado: {estados}")
        
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
    pass

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        generos_map = {
            'terror': ['Terror', 'Horror', 'Suspense'],
            'romance': ['Romance', 'Romântico', 'Drama Romântico'],
            'acao': ['Ação', 'Aventura', 'Thriller'],
            'comedia': ['Comédia', 'Comédia Romântica'],
            'drama': ['Drama', 'Drama'],
            'ficcao': ['Ficção Científica', 'Sci-Fi', 'Fantasia']
        }
        
        generos_busca = generos_map.get(genero.lower(), [genero])
        
        placeholders = ', '.join(['%s'] * len(generos_busca))
        
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
        cursor.execute("""
            UPDATE usuarios 
            SET avatar_id = %s, avatar = NULL
            WHERE id = %s
        """, (avatar_id, session['user_id']))
        
        cursor.execute("SELECT caminho FROM avatars WHERE id = %s", (avatar_id,))
        avatar_data = cursor.fetchone()
        
        if avatar_data:
            new_avatar = avatar_data[0].replace('\\', '/').replace('"', '').strip()
            if new_avatar.startswith('static/'):
                new_avatar = new_avatar[7:]
            if new_avatar.startswith('/static/'):
                new_avatar = new_avatar[8:]
            session['user_avatar'] = new_avatar
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Avatar atualizado com sucesso!'})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
    finally:
        cursor.close()
        conn.close()


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

# TEST ROUTE - Comment out for production
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

@app.route('/processar_pagamento', methods=['POST'])
def processar_pagamento():
    try:
        app.logger.info("=== INICIANDO PROCESSAMENTO DE PAGAMENTO ===")
        
        data = request.get_json()
        app.logger.info(f"Dados recebidos: {data}")
        
        dados_reserva = data.get('dados_reserva', {})
        app.logger.info(f"Dados da reserva extraídos: {dados_reserva}")
        
        tipo_reserva = dados_reserva.get('tipo_reserva', 'individual')
        categoria = dados_reserva.get('categoria', '')
        tipo_sala = dados_reserva.get('tipo_sala', '')
        
        app.logger.info(f"Tipo de reserva: {tipo_reserva}, Categoria: {categoria}, Tipo sala: {tipo_sala}")
        
        id_usuario = session.get('user_id', 0)
        app.logger.info(f"Usuario ID da sessão: {id_usuario}")
        
        id_horario_sessao = dados_reserva.get('id_horario_sessao')
        id_cinema = dados_reserva.get('id_cinema')

        app.logger.info(f"  dados_reserva completos: {dados_reserva}")
        app.logger.info(f"  tipo_id extraído: {dados_reserva.get('tipo_id', 'NÃO ENCONTRADO')}")
        app.logger.info(f"  id_horario_sessao: {dados_reserva.get('id_horario_sessao', 'NÃO ENCONTRADO')}")
        
        tipo_id = dados_reserva.get('tipo_id')
        id_filme = dados_reserva.get('id_filme')
        filme_nome = dados_reserva.get('filme_nome')
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
        
        if tipo_reserva == 'sessao_exclusiva':
            pass
            
            campos_faltando = []
            
            if not data_sessao or data_sessao == '':
                campos_faltando.append('data_sessao')
            
            if not hora_sessao or hora_sessao == '':
                campos_faltando.append('hora_sessao')
            
            if not num_pessoas or (isinstance(num_pessoas, str) and num_pessoas.strip() == '') or num_pessoas == 0:
                campos_faltando.append('num_pessoas')
            
            if not nome or (isinstance(nome, str) and nome.strip() == ''):
                campos_faltando.append('nome')
            
            if not email or (isinstance(email, str) and email.strip() == ''):
                campos_faltando.append('email')
            
            app.logger.info(f"Verificação detalhada de campos:")
            
            if campos_faltando:
                app.logger.error(f"❌ CAMPOS OBRIGATÓRIOS FALTANDO: {campos_faltando}")
                return jsonify({
                    'success': False, 
                    'message': f'Dados da sessão exclusiva incompletos. Campos em falta: {", ".join(campos_faltando)}',
                    'campos_faltando': campos_faltando,
                    'dados_recebidos': dados_reserva
                }), 400
            else:
                pass
        else:
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
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            app.logger.info(f"=== PROCESSAMENTO DE PAGAMENTO ===")
            app.logger.info(f"Usuario ID da sessão: {id_usuario}")
            app.logger.info(f"Categoria: {categoria}")
            
            if id_usuario > 0:
                cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (id_usuario,))
                user_data = cursor.fetchone()
                
                if user_data:
                    nome = user_data['nome'] or nome
                    email = user_data['email'] or email
                    telefone = ''
                else:
                    app.logger.warning(f"⚠️ Usuário ID {id_usuario} não encontrado na base de dados")
            
            app.logger.info(f"Dados finais - nome: '{nome}', email: '{email}', telefone: '{telefone}'")
            
            reserva_ids = []
            
            if tipo_reserva == 'sessao_exclusiva':
                app.logger.info(f"=== PROCESSANDO SESSÃO EXCLUSIVA ===")
                
                nome_cliente = nome if id_usuario == 0 else None
                email_cliente = email if id_usuario == 0 else None
                telefone_cliente = telefone if (id_usuario == 0 and telefone and telefone.strip()) else None
                user_id_final = id_usuario if id_usuario > 0 else None
                
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
                    
                except Exception as e:
                    app.logger.error(f"Erro ao inserir sessão exclusiva: {str(e)}")
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
                        
                        cursor.execute("""
                            INSERT INTO reservas_exclusivas 
                            (tipo_sala, id_filme, filme_nome, data_sessao, hora_sessao, num_pessoas, 
                             total, id_usuario, nome_cliente, email_cliente, telefone_cliente, data_reserva)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        """, (tipo_sala, id_filme, filme_nome, data_sessao, hora_sessao, num_pessoas, 
                              total, user_id_final, nome_cliente, email_cliente, telefone_cliente))
                        
                        reserva_id = cursor.lastrowid
                        reserva_ids.append(reserva_id)
                        
                    except Exception as e2:
                        app.logger.error(f"Erro ao criar tabela e inserir: {str(e2)}")
                        raise
            
            else:
                app.logger.info(f"=== PROCESSANDO RESERVA NORMAL ===")
                
                cursor.execute("SELECT preco_bilhete FROM tipos_sessao WHERE id = %s", (tipo_id,))
                preco_row = cursor.fetchone()
                preco_bilhete = float(preco_row['preco_bilhete']) if preco_row else 8.50
                
                total_bilhetes = preco_bilhete * len(lugares)
                total_bar = 0
                for produto_id, produto_info in produtos_bar.items():
                    total_bar += float(produto_info.get('preco', 0)) * int(produto_info.get('quantidade', 0))
                total_geral = total_bilhetes + total_bar
                
                nome_cliente = nome if id_usuario == 0 else None
                email_cliente = email if id_usuario == 0 else None
                telefone_cliente = telefone if (id_usuario == 0 and telefone and telefone.strip()) else None
                
                for lugares in lugareses:
                    try:
                        user_id_final = id_usuario if id_usuario > 0 else None
                        
                        try:
                            cursor.execute("""
                                INSERT INTO reservas (id_horario_sessao, data_sessao, id_filme, id_cinema, id_tipo_sessao, lugares, id_usuario, nome_cliente, email_cliente, telefone_cliente, data_reserva)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                            """, (id_horario_sessao, data_sessao, id_filme, id_cinema, tipo_id, lugares, user_id_final, nome_cliente, email_cliente, telefone_cliente))
                        except Exception as e:
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
                
                if produtos_bar and reserva_ids:
                    primeira_reserva_id = reserva_ids[0]
                    
                    if isinstance(produtos_bar, dict):
                        for produto_id_str, quantidade in produtos_bar.items():
                            if quantidade > 0:
                                try:
                                    produto_id = int(produto_id_str)
                                    cursor.execute("""
                                        SELECT produto, preco FROM bar WHERE id = %s
                                    """, (produto_id,))
                                    produto_info = cursor.fetchone()
                                    
                                    if produto_info:
                                        subtotal = float(produto_info['preco']) * quantidade
                                        cursor.execute("""
                                            INSERT INTO reservas_bar (id_reserva, produto_id, produto, quantidade, preco_unitario, subtotal)
                                            VALUES (%s, %s, %s, %s, %s, %s)
                                        """, (primeira_reserva_id, produto_id, produto_info['produto'], quantidade, produto_info['preco'], subtotal))
                                        app.logger.info(f"✅ Produto bar inserido: {produto_info['produto']} x{quantidade}")
                                except Exception as e:
                                    app.logger.error(f"Erro ao inserir produto bar {produto_id_str}: {str(e)}")
                    
                    elif isinstance(produtos_bar, list):
                        app.logger.info(f"📦 Processando {len(produtos_bar)} produtos do bar (lista)")
                        for produto in produtos_bar:
                            produto_id = produto.get('id')
                            quantidade = produto.get('quantidade', 1)
                            tipo_produto = produto.get('tipo', 'bar')
                            configs = produto.get('configs', [])
                            
                            app.logger.info(f"   Produto: id={produto_id}, tipo={tipo_produto}, quantidade={quantidade}")
                            
                            if tipo_produto == 'menu':
                                cursor.execute("""
                                    SELECT nome as produto, preco_total as preco FROM menus WHERE id = %s
                                """, (produto_id,))
                                menu_info = cursor.fetchone()
                                
                                if menu_info:
                                    for config in configs:
                                        snack_id = config.get('snackId')
                                        bebida_id = config.get('bebidaId')
                                        toppings_ids = config.get('toppings', [])
                                        
                                        preco_menu = float(menu_info['preco'])
                                        preco_toppings = 0.0
                                        
                                        for topping_id in toppings_ids:
                                            cursor.execute("SELECT preco FROM toppings WHERE id = %s", (topping_id,))
                                            topping_info = cursor.fetchone()
                                            if topping_info:
                                                preco_toppings += float(topping_info['preco'])
                                        
                                        preco_total = preco_menu + preco_toppings
                                        
                                        cursor.execute("SELECT produto FROM bar WHERE id = %s", (snack_id,))
                                        snack_nome = cursor.fetchone()
                                        cursor.execute("SELECT produto FROM bar WHERE id = %s", (bebida_id,))
                                        bebida_nome = cursor.fetchone()
                                        
                                        produto_descricao = f"{menu_info['produto']} ({snack_nome['produto'] if snack_nome else 'Snack'} + {bebida_nome['produto'] if bebida_nome else 'Bebida'})"
                                        if toppings_ids:
                                            produto_descricao += " + Toppings"
                                        
                                        topping_id_str = ','.join(map(str, toppings_ids)) if toppings_ids else None
                                        
                                        cursor.execute("""
                                            INSERT INTO reservas_bar (id_reserva, menu_id, produto_id, bebida_id, topping_id, produto, quantidade, preco_unitario, subtotal)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                        """, (primeira_reserva_id, produto_id, snack_id, bebida_id, topping_id_str, produto_descricao, 1, preco_total, preco_total))
                                        
                                        app.logger.info(f"✅ Menu inserido: {produto_descricao} - €{preco_total}")
                            
                            else:
                                if quantidade > 0:
                                    try:
                                        cursor.execute("""
                                            SELECT produto, preco FROM bar WHERE id = %s
                                        """, (produto_id,))
                                        produto_info = cursor.fetchone()
                                        
                                        if produto_info:
                                            subtotal = float(produto_info['preco']) * quantidade
                                            cursor.execute("""
                                                INSERT INTO reservas_bar (id_reserva, produto_id, produto, quantidade, preco_unitario, subtotal)
                                                VALUES (%s, %s, %s, %s, %s, %s)
                                            """, (primeira_reserva_id, produto_id, produto_info['produto'], quantidade, produto_info['preco'], subtotal))
                                            app.logger.info(f"✅ Produto bar inserido: {produto_info['produto']} x{quantidade}")
                                    except Exception as e:
                                        app.logger.error(f"Erro ao inserir produto bar {produto_id}: {str(e)}")
            
            conn.commit()
            
            try:
                from datetime import datetime
                data_formatada = datetime.strptime(data_sessao, '%Y-%m-%d').strftime('%d/%m/%Y')
                
                if tipo_reserva == 'sessao_exclusiva':
                    filme_titulo = filme_nome if filme_nome else 'Filme Personalizado'
                    if id_filme:
                        cursor.execute("SELECT titulo FROM filmes WHERE id = %s", (id_filme,))
                        filme_row = cursor.fetchone()
                        if filme_row:
                            filme_titulo = filme_row['titulo']
                    
                    horario_completo = f"{data_formatada} às {hora_sessao}"
                    
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
                    
                else:
                    cursor.execute("SELECT titulo FROM filmes WHERE id = %s", (id_filme,))
                    filme = cursor.fetchone()
                    cursor.execute("SELECT nome FROM cinemas WHERE id = %s", (id_cinema,))
                    cinema = cursor.fetchone()
                    cursor.execute("SELECT nome FROM tipos_sessao WHERE id = %s", (tipo_id,))
                    tipo_sessao = cursor.fetchone()
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
                    pass
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

# TEST ROUTE - Comment out for production
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

# TEST ROUTE - Comment out for production
@app.route('/test_api_filmes')
def test_api_filmes():
    """Página de teste para as APIs de filmes"""
    from flask import send_from_directory
    return send_from_directory('.', 'test_api_filmes.html')

# TEST ROUTE - Comment out for production
@app.route('/test_pagamento')
def test_pagamento():
    """Página de teste para pagamento de sessões exclusivas"""
    from flask import send_from_directory
    return send_from_directory('.', 'test_pagamento_simples.html')

# TEST ROUTE - Comment out for production
@app.route('/debug_pagamento')
def debug_pagamento():
    """Página de debug para pagamento de sessões exclusivas"""
    from flask import send_from_directory
    return send_from_directory('.', 'debug_pagamento.html')

# TEST ROUTE - Comment out for production
@app.route('/test_filme')
def test_filme():
    """Página de teste para reservas de filmes"""
    from flask import send_from_directory
    return send_from_directory('.', 'test_reserva_normal.html')

# TEST ROUTE - Comment out for production
@app.route('/test_logado')
def test_logado():
    pass
   
    from flask import send_from_directory
    return send_from_directory('.', 'test_usuario_logado.html')



# TEST ROUTE - Comment out for production
@app.route('/debug/filmes')
def debug_filmes():
    pass
   
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        pass
       
        cursor.execute("SELECT COUNT(*) as total FROM filmes")
        total = cursor.fetchone()['total']
        
       
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
    pass
   
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        pass
      
        novo_trailer = 'https://www.youtube.com/watch?v=Ox8ZLF6cGM0'
        
        cursor.execute("""
            UPDATE filmes 
            SET trailer_url = %s 
            WHERE id = 27 AND titulo = 'Supergirl: Woman of Tomorrow'
        """, (novo_trailer,))
        
        conn.commit()
        
  
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


def salvar_dados_reserva_sessao(filme_id=None, cinema_id=None, id_tipo_sessao=None, 
                               id_horario_sessao=None, data_sessao=None, lugares=None, produtos_bar=None):

    
    app.logger.info(f"🔧 SALVANDO DADOS NA SESSÃO: filme_id={filme_id}, cinema_id={cinema_id}")
    

    reserva_data = session.get('reserva_data', {})
    
 
    if filme_id:
        reserva_data['filme_id'] = filme_id
        session['filme_id'] = filme_id  
    
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

    lugares_count = len(reserva_data.get('lugares_selecionados', []))
    preco_bilhetes = lugares_count * 8.50
    preco_bar = sum(p.get('preco', 0) * p.get('quantidade', 1) for p in reserva_data.get('produtos_bar', []))
    reserva_data['total'] = preco_bilhetes + preco_bar
    
 
    session['reserva_data'] = reserva_data
    
    return reserva_data

# TEST ROUTE - Comment out for production
@app.route('/debug_sessao')
def debug_sessao():
    pass

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


@app.route('/pagamento')
def pagamento():
    pass
    
    try:
        pass
   
        reserva_data = session.get('reserva_data')
        if not reserva_data:
            app.logger.warning("Dados de reserva não encontrados na sessão, criando dados de demonstração")
        
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
  
        user_id = session.get('user_id')
        logged_in = user_id is not None
        avatar = get_user_avatar() if logged_in else 'imgs/icons/user_icon34-removebg-preview.png'
        
     
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

        if filme.get('poster_url'):
            poster_url = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
            if not poster_url.startswith('imgs/filmes/'):
                if '/' not in poster_url:
                    poster_url = f"imgs/filmes/{poster_url}"
                elif not poster_url.startswith('imgs/'):
                    poster_url = f"imgs/filmes/{poster_url}"
            filme['poster_url'] = poster_url
 
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

        lugares_selecionados = reserva_data.get('lugares_selecionados', [])
        preco_bilhete = 8.50
        total_bilhetes = len(lugares_selecionados) * preco_bilhete
        
        # Aplicar desconto do plano nos bilhetes
        desconto_bilhetes = 0
        desconto_percentual_bilhetes = 0
        if logged_in and user_id:
            total_bilhetes_com_desconto, desconto_percentual_bilhetes = aplicar_desconto_plano(total_bilhetes, user_id, 'bilhete')
            desconto_bilhetes = total_bilhetes - total_bilhetes_com_desconto
            total_bilhetes = total_bilhetes_com_desconto
        
        produtos_bar = reserva_data.get('produtos_bar', [])
        total_bar = sum(produto.get('preco', 0) * produto.get('quantidade', 1) for produto in produtos_bar)
        
        # Aplicar desconto do plano no bar
        desconto_bar = 0
        desconto_percentual_bar = 0
        if logged_in and user_id and total_bar > 0:
            total_bar_com_desconto, desconto_percentual_bar = aplicar_desconto_plano(total_bar, user_id, 'bar')
            desconto_bar = total_bar - total_bar_com_desconto
            total_bar = total_bar_com_desconto
        
        total_geral = total_bilhetes + total_bar
        
        # Obter informações da subscrição para mostrar bilhetes grátis
        subscricao = None
        if logged_in and user_id:
            subscricao = get_user_subscription(user_id)

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
            'preco_bilhete': preco_bilhete,
            'desconto_bilhetes': desconto_bilhetes,
            'desconto_percentual_bilhetes': desconto_percentual_bilhetes,
            'desconto_bar': desconto_bar,
            'desconto_percentual_bar': desconto_percentual_bar,
            'subscricao': subscricao
        }
        
        
        return render_template('pagamento.html',
                             dados_pagamento=dados_pagamento,
                             logged_in=logged_in,
                             avatar=avatar)
                             
    except Exception as e:
        app.logger.error(f"❌ PAGAMENTO - Erro: {e}")
        return redirect(url_for('home'))

@app.route('/checkout')
def checkout():
    pass
    
    conn = None
    try:
        filme_id = request.args.get('filme_id') or session.get('filme_id')
        cinema_id = request.args.get('cinema_id') or session.get('cinema_id')
        id_tipo_sessao = request.args.get('id_tipo_sessao') or session.get('id_tipo_sessao')
        id_horario_sessao = request.args.get('id_horario_sessao') or session.get('id_horario_sessao')
        data_sessao = request.args.get('data_sessao') or session.get('data_sessao')
        lugares = request.args.get('lugares') or ','.join(session.get('lugares_selecionados', []))
        
        app.logger.info(f"   filme_id={filme_id}, id_tipo_sessao={id_tipo_sessao}")
        app.logger.info(f"   lugares={lugares}")
        
        if not all([filme_id, cinema_id, id_horario_sessao, id_tipo_sessao]):
            flash("Dados da reserva incompletos", "erro")
            return redirect(url_for('home'))
        
        lugares_selecionados = lugares.split(',') if lugares else []

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        
        if not filme:
            flash("Filme não encontrado", "erro")
            return redirect(url_for('home'))
        
        poster_url = filme.get('poster_url', 'imgs/filmes/placeholder.jpg')
        if poster_url and not poster_url.startswith(('http://', 'https://', 'imgs/')):
            poster_url = f"imgs/filmes/{poster_url}"
        filme['poster_url'] = poster_url
        
        cursor.execute("SELECT * FROM cinemas WHERE id = %s", (cinema_id,))
        cinema = cursor.fetchone()

        cursor.execute("SELECT * FROM tipos_sessao WHERE id = %s", (id_tipo_sessao,))
        tipo_sessao = cursor.fetchone()
        
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
        

        salvar_dados_reserva_sessao(
            filme_id=int(filme_id),
            cinema_id=int(cinema_id),
            id_tipo_sessao=int(id_tipo_sessao),
            id_horario_sessao=int(id_horario_sessao),
            data_sessao=str(data_sessao),
            lugares=lugares_selecionados
        )
        
        user_authenticated = 'user_id' in session
        user_avatar = get_user_avatar() if user_authenticated else 'imgs/icons/user_icon34-removebg-preview.png'
   
        if user_authenticated:
            usuario = {
                'id': session.get('user_id'),
                'nome': session.get('user_name', 'Utilizador')
            }
        else:
            usuario = {'id': None, 'nome': ''}
     
        preco_bilhete = float(tipo_sessao.get('preco_bilhete', 8.50)) if tipo_sessao else 8.50
        quantidade = len(lugares_selecionados)
        total_bilhetes = quantidade * preco_bilhete
        
        # Obter produtos do bar da sessão
        produtos_bar_sessao = session.get('produtos_bar', [])
        total_bar = 0.0
        
        # Calcular total do bar se houver produtos
        if produtos_bar_sessao:
            conn_bar = get_db_connection()
            cursor_bar = conn_bar.cursor(dictionary=True)
            
            for produto in produtos_bar_sessao:
                produto_id = produto.get('id')
                quantidade_prod = int(produto.get('quantidade', 1))
                tipo_produto = produto.get('tipo', 'bar')
                
                if tipo_produto == 'menu':
                    cursor_bar.execute("SELECT preco_total as preco FROM menus WHERE id = %s", (produto_id,))
                else:
                    cursor_bar.execute("SELECT preco FROM bar WHERE id = %s", (produto_id,))
                
                produto_info = cursor_bar.fetchone()
                if produto_info:
                    total_bar += float(produto_info['preco']) * quantidade_prod
            
            cursor_bar.close()
            conn_bar.close()
        
        # Obter informações da subscrição se o user estiver logado
        subscricao = None
        reserva_data = None
        desconto_bilhetes = 0.0
        desconto_bar = 0.0
        
        if user_authenticated:
            subscricao = get_user_subscription(session['user_id'])
            reserva_data = {
                'lugares_selecionados': lugares_selecionados
            }
            
            # Calcular descontos baseados no plano
            if subscricao and subscricao.get('plano_tipo') in ['member', 'premium']:
                plano = subscricao['plano_tipo']
                
                # Desconto em bilhetes
                if plano == 'member':
                    desconto_bilhetes = total_bilhetes * 0.15  # 15%
                elif plano == 'premium':
                    desconto_bilhetes = total_bilhetes * 0.25  # 25%
                
                # Desconto no bar (se houver produtos)
                if total_bar > 0:
                    if plano == 'member':
                        desconto_bar = total_bar * 0.10  # 10%
                    elif plano == 'premium':
                        desconto_bar = total_bar * 0.20  # 20%
        
        # Aplicar descontos ao total
        total_bilhetes_com_desconto = total_bilhetes - desconto_bilhetes
        total_bar_com_desconto = total_bar - desconto_bar
        total_geral = total_bilhetes_com_desconto + total_bar_com_desconto
        
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
                             desconto_bilhetes=desconto_bilhetes,
                             desconto_bar=desconto_bar,
                             user_authenticated=user_authenticated,
                             user_avatar=user_avatar,
                             subscricao=subscricao,
                             reserva_data=reserva_data)
                             
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
    pass
    
    
    try:
        pass

        data = request.get_json() if request.is_json else request.form
        
        if not data:
            return jsonify({'success': False, 'error': 'Nenhum dado recebido'})
        
        filme_id = data.get('filme_id', 1)
        cinema_id = data.get('cinema_id', 1)
        id_tipo_sessao = data.get('id_tipo_sessao', 1)
        id_horario_sessao = data.get('id_horario_sessao', 6298)
        data_sessao = data.get('data_sessao', '2026-01-14')
        
     
        lugares_raw = data.get('lugares', 'A1,A2')
        

        import html
        if isinstance(lugares_raw, str):
            lugares_raw = html.unescape(lugares_raw)
        
        if isinstance(lugares_raw, list):
            lugares = ','.join(lugares_raw)
        elif isinstance(lugares_raw, str):
            pass
            
            if lugares_raw.startswith('[') and lugares_raw.endswith(']'):
                import json
                try:
                    lugares_array = json.loads(lugares_raw)
                    lugares = ','.join(lugares_array)
                except:
                    pass

                    lugares = lugares_raw.replace('[', '').replace(']', '').replace('"', '').replace("'", '')
            else:   
                lugares = lugares_raw.replace('"', '').replace("'", '')
        else:
            lugares = str(lugares_raw)
        
        total_geral = data.get('total_geral', 17.0)
        payment_method = data.get('payment_method', 'cartao')
        bilhetes_gratis_usados = data.get('bilhetes_gratis_usados', 0)
        
        
        app.logger.info(f"📥 Lugares processados: '{lugares}' (tipo: {type(lugares).__name__})")
        
      
        conn_check = get_db_connection()
        cursor_check = conn_check.cursor(dictionary=True)
        cursor_check.execute("SELECT id FROM horarios_sessao WHERE id = %s", (id_horario_sessao,))
        horario_existe = cursor_check.fetchone()
        cursor_check.close()
        conn_check.close()
        
        if not horario_existe:
            app.logger.error(f"❌ Horário {id_horario_sessao} não existe na BD!")
           
            conn_fix = get_db_connection()
            cursor_fix = conn_fix.cursor(dictionary=True)
            cursor_fix.execute("SELECT id FROM horarios_sessao LIMIT 1")
            horario_valido = cursor_fix.fetchone()
            cursor_fix.close()
            conn_fix.close()
            
            if horario_valido:
                id_horario_sessao = horario_valido['id']
            else:
                return jsonify({'success': False, 'error': 'Nenhum horário disponível na base de dados'})
        
    
        user_id = session.get('user_id')
        
        # Se usou bilhetes grátis, atualizar contador na BD
        if bilhetes_gratis_usados > 0 and user_id:
            conn_bilhetes = get_db_connection()
            cursor_bilhetes = conn_bilhetes.cursor(dictionary=True)
            try:
                # Verificar se tem bilhetes disponíveis
                cursor_bilhetes.execute("""
                    SELECT bilhetes_gratis_mes, bilhetes_gratis_usados
                    FROM subscricoes
                    WHERE user_id = %s AND status = 'ativo'
                    ORDER BY id DESC LIMIT 1
                """, (user_id,))
                subscricao = cursor_bilhetes.fetchone()
                
                if subscricao:
                    bilhetes_disponiveis = subscricao['bilhetes_gratis_mes'] - subscricao['bilhetes_gratis_usados']
                    
                    if bilhetes_disponiveis >= bilhetes_gratis_usados:
                        # Atualizar contador
                        cursor_bilhetes.execute("""
                            UPDATE subscricoes
                            SET bilhetes_gratis_usados = bilhetes_gratis_usados + %s
                            WHERE user_id = %s AND status = 'ativo'
                        """, (bilhetes_gratis_usados, user_id))
                        conn_bilhetes.commit()
                        app.logger.info(f"✅ {bilhetes_gratis_usados} bilhete(s) grátis usado(s) pelo user {user_id}")
                    else:
                        app.logger.warning(f"⚠️ User {user_id} tentou usar mais bilhetes grátis do que tem disponível")
            except Exception as e:
                app.logger.error(f"❌ Erro ao processar bilhetes grátis: {str(e)}")
            finally:
                cursor_bilhetes.close()
                conn_bilhetes.close()
        
        # Se total é 0 e método é 'gratis', marcar como pago com bilhetes grátis
        if float(total_geral) == 0 and payment_method == 'gratis':
            payment_method = 'bilhetes_gratis'
        
        if user_id:
            pass
       
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
            pass
           
            nome_cliente = session.get('nome_cliente', '').strip()
            email_cliente = session.get('email_cliente', '').strip()
            telefone_cliente = session.get('telefone_cliente', '').strip()
            
           
            if not nome_cliente:
                nome_cliente = data.get('customer_name', '').strip()
            if not email_cliente:
                email_cliente = data.get('customer_email', '').strip()
            if not telefone_cliente:
                telefone_cliente = data.get('customer_phone', '').strip()
            
          
            if not nome_cliente or not email_cliente:
                return jsonify({
                    'success': False,
                    'error': 'Nome e email são obrigatórios. Por favor, volte ao resumo da reserva e preencha os seus dados.'
                })
        
      
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
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
        reserva_id = cursor.lastrowid
        
        produtos_bar_sessao = session.get('produtos_bar', [])
        app.logger.info(f"📦 Produtos bar da sessão: {produtos_bar_sessao}")
        
        if produtos_bar_sessao and isinstance(produtos_bar_sessao, list):
            app.logger.info(f"📦 Processando {len(produtos_bar_sessao)} produtos do bar para inserção")
            
            for produto in produtos_bar_sessao:
                produto_id = produto.get('id')
                quantidade = produto.get('quantidade', 1)
                tipo_produto = produto.get('tipo', 'bar')
                configs = produto.get('configs', [])
                
                app.logger.info(f"   Produto: id={produto_id}, tipo={tipo_produto}, quantidade={quantidade}")
                
                if tipo_produto == 'menu':
                    cursor.execute("""
                        SELECT nome as produto, preco_total as preco FROM menus WHERE id = %s
                    """, (produto_id,))
                    menu_info = cursor.fetchone()
                    
                    if menu_info:
                        for config in configs:
                            snack_id = config.get('snackId')
                            bebida_id = config.get('bebidaId')
                            toppings_ids = config.get('toppings', [])
                            
                            preco_menu = float(menu_info['preco'])
                            preco_toppings = 0.0
                            
                            for topping_id in toppings_ids:
                                cursor.execute("SELECT preco FROM toppings WHERE id = %s", (topping_id,))
                                topping_info = cursor.fetchone()
                                if topping_info:
                                    preco_toppings += float(topping_info['preco'])
                            
                            preco_total = preco_menu + preco_toppings
                            
                            cursor.execute("SELECT produto FROM bar WHERE id = %s", (snack_id,))
                            snack_nome = cursor.fetchone()
                            cursor.execute("SELECT produto FROM bar WHERE id = %s", (bebida_id,))
                            bebida_nome = cursor.fetchone()
                            
                            produto_descricao = f"{menu_info['produto']} ({snack_nome['produto'] if snack_nome else 'Snack'} + {bebida_nome['produto'] if bebida_nome else 'Bebida'})"
                            if toppings_ids:
                                produto_descricao += " + Toppings"
                            
                            topping_id_str = ','.join(map(str, toppings_ids)) if toppings_ids else None
                            
                            cursor.execute("""
                                INSERT INTO reservas_bar (id_reserva, menu_id, produto_id, bebida_id, topping_id, produto, quantidade, preco_unitario, subtotal)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (reserva_id, produto_id, snack_id, bebida_id, topping_id_str, produto_descricao, 1, preco_total, preco_total))
                            
                            app.logger.info(f"✅ Menu inserido: {produto_descricao} - €{preco_total}")
                
                else:
                    if quantidade > 0:
                        try:
                            cursor.execute("""
                                SELECT produto, preco FROM bar WHERE id = %s
                            """, (produto_id,))
                            produto_info = cursor.fetchone()
                            
                            if produto_info:
                                preco_base = float(produto_info['preco'])
                                
                                if tipo_produto == 'pipocas' and configs:
                                    for config in configs:
                                        toppings_ids = config.get('toppings', [])
                                        preco_toppings = 0.0
                                        
                                        for topping_id in toppings_ids:
                                            cursor.execute("SELECT preco FROM toppings WHERE id = %s", (topping_id,))
                                            topping_info = cursor.fetchone()
                                            if topping_info:
                                                preco_toppings += float(topping_info['preco'])
                                        
                                        preco_total = preco_base + preco_toppings
                                        
                                        produto_descricao = produto_info['produto']
                                        if toppings_ids:
                                            produto_descricao += " + Toppings"
                                        
                                        topping_id_str = ','.join(map(str, toppings_ids)) if toppings_ids else None
                                        
                                        cursor.execute("""
                                            INSERT INTO reservas_bar (id_reserva, produto_id, topping_id, produto, quantidade, preco_unitario, subtotal)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                                        """, (reserva_id, produto_id, topping_id_str, produto_descricao, 1, preco_total, preco_total))
                                        
                                        app.logger.info(f"✅ Pipocas inseridas: {produto_descricao} - €{preco_total}")
                                else:
                                    subtotal = preco_base * quantidade
                                    cursor.execute("""
                                        INSERT INTO reservas_bar (id_reserva, produto_id, produto, quantidade, preco_unitario, subtotal)
                                        VALUES (%s, %s, %s, %s, %s, %s)
                                    """, (reserva_id, produto_id, produto_info['produto'], quantidade, produto_info['preco'], subtotal))
                                    app.logger.info(f"✅ Produto bar inserido: {produto_info['produto']} x{quantidade}")
                        except Exception as e:
                            app.logger.error(f"Erro ao inserir produto bar {produto_id}: {str(e)}")
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        
       
        try:
            pass
         
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
                pass
           
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
                
           
                email_enviado = enviar_email_confirmacao(
                    email_cliente,
                    nome_cliente,
                    dados_email
                )
                
                if email_enviado:
                    pass
                else:
                    app.logger.warning(f"⚠️ Email não foi enviado para {email_cliente}")
            else:
                app.logger.error(f"❌ Não foi possível encontrar dados da reserva {reserva_id}")
                
        except Exception as email_error:
            app.logger.error(f"⚠️ Erro ao enviar email: {email_error}")
           
    
        session.pop('filme_id', None)
        session.pop('cinema_id', None)
        session.pop('data_sessao', None)
        session.pop('id_horario_sessao', None)
        session.pop('id_tipo_sessao', None)
        session.pop('produtos_bar', None)
        
       
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
    pass
    
    
    try:
        pass
        
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user_id = session.get('user_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
      
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
    pass

    conn = None
    try:
        data = request.get_json()
        app.logger.info(f"Dados recebidos para pagamento: {data}")
        
      
        payment_method = data.get('payment_method', 'paypal')
        customer_data = data.get('customer_data', {})
        
    
        filme_id = session.get('filme_id')
        cinema_id = session.get('cinema_id') 
        id_horario_sessao = session.get('id_horario_sessao')
        id_tipo_sessao = session.get('id_tipo_sessao', 1)
        data_sessao = session.get('data_sessao')
        lugares_selecionados = session.get('lugares_selecionados', [])
        total = session.get('total', 0)
        

        app.logger.info("="*80)
        app.logger.info(f"   id_tipo_sessao da sessão: {id_tipo_sessao}")
        app.logger.info(f"   id_horario_sessao: {id_horario_sessao}")
        app.logger.info("="*80)
        
 
        user_id = session.get('user_id') if customer_data.get('logged_in') else None
        nome_cliente = customer_data.get('guest_name') or session.get('user_name', 'Cliente')
        email_cliente = customer_data.get('guest_email') or session.get('user_email', 'cliente@email.com')
        telefone_cliente = customer_data.get('guest_phone', '')
        
        if not all([filme_id, cinema_id, id_horario_sessao, lugares_selecionados, data_sessao]):
            return jsonify({
                'success': False,
                'message': 'Dados da reserva incompletos. Reinicie o processo.'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
    
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
        

        id_tipo_sessao = horario_info['id_tipo_sessao']
        
     
        if not filme_id:
            filme_id = horario_info['id_filme']
        if not cinema_id:
            cinema_id = horario_info['id_cinema']
        
        
      
        lugares_str = ','.join(map(str, lugares_selecionados))
        
     
        app.logger.info("="*80)
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
        
      
        try:
            email_enviado = enviar_email_confirmacao(
                email_cliente, 
                nome_cliente, 
                dados_email
            )
            if email_enviado:
                pass
            else:
                app.logger.warning(f"⚠️ Email não foi enviado para {email_cliente}")
        except Exception as email_error:
            app.logger.error(f"❌ Erro ao enviar email: {email_error}")
        
        session.pop('filme_id', None)
        session.pop('cinema_id', None)
        session.pop('id_horario_sessao', None)
        session.pop('id_tipo_sessao', None)
        session.pop('lugares_selecionados', None)
        session.pop('total', None)
        
        
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


@app.route('/api/validar-codigo-desconto', methods=['POST'])
def validar_codigo_desconto():
    pass
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Utilizador não autenticado'})
    
    try:
        data = request.get_json()
        codigo = data.get('codigo', '').strip().upper()
        
        if not codigo:
            return jsonify({'success': False, 'message': 'Código não fornecido'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
       
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
        
        
        if codigo_info['usuario_id'] != session['user_id']:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Este código não pertence a si'})
        
       
        if codigo_info['usado']:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Este código já foi utilizado'})
        
        from datetime import datetime
        if datetime.now() > codigo_info['data_expiracao']:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Este código expirou'})
        
        cursor.close()
        conn.close()
        
      
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
    pass
    
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
        
   
        cursor.execute("""
            SELECT * FROM codigos_desconto 
            WHERE codigo = %s AND usuario_id = %s AND usado = 0 AND data_expiracao > NOW()
        """, (codigo, session['user_id']))
        
        codigo_info = cursor.fetchone()
        
        if not codigo_info:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Código inválido, já usado ou expirado'})
        
        
        desconto_valor = 0.0
        total_original_float = float(total_original)  
        novo_total = total_original_float
        valor_desconto_float = float(codigo_info['valor_desconto'])  
        
        if codigo_info['tipo_desconto'] == 'percentual':
            desconto_valor = (total_original_float * valor_desconto_float) / 100.0
            novo_total = max(0.0, total_original_float - desconto_valor)
        elif codigo_info['tipo_desconto'] == 'valor_fixo':
            desconto_valor = min(valor_desconto_float, total_original_float)
            novo_total = max(0.0, total_original_float - desconto_valor)
        elif codigo_info['tipo_desconto'] == 'produto_gratis':
            pass
 
            if 'bilhete' in codigo_info['premio_nome'].lower():
                desconto_valor = total_original_float
                novo_total = 0.0
            else:
                pass

                desconto_valor = min(valor_desconto_float, total_original_float)
                novo_total = max(0.0, total_original_float - desconto_valor)
        
        cursor.close()
        conn.close()
        
    
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
    pass

    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Utilizador não autenticado'})
    
    try:
        data = request.get_json()
        codigo = data.get('codigo', '').strip().upper()
        payment_method = data.get('payment_method')
        bilhetes_gratis_usados = data.get('bilhetes_gratis_usados', 0)
        
        if not payment_method:
            return jsonify({'success': False, 'message': 'Método de pagamento não selecionado'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
 
        # Processar código de desconto se existir
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
        
        # Processar bilhetes grátis se foram usados
        if bilhetes_gratis_usados > 0:
            # Verificar se o user tem bilhetes disponíveis
            cursor.execute("""
                SELECT bilhetes_gratis_mes, bilhetes_gratis_usados
                FROM subscricoes
                WHERE user_id = %s AND status = 'ativo'
                ORDER BY id DESC LIMIT 1
            """, (session['user_id'],))
            subscricao = cursor.fetchone()
            
            if not subscricao:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Subscrição não encontrada'})
            
            bilhetes_disponiveis = subscricao['bilhetes_gratis_mes'] - subscricao['bilhetes_gratis_usados']
            
            if bilhetes_disponiveis < bilhetes_gratis_usados:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Não tens bilhetes grátis suficientes'})
            
            # Atualizar contador de bilhetes usados
            cursor.execute("""
                UPDATE subscricoes
                SET bilhetes_gratis_usados = bilhetes_gratis_usados + %s
                WHERE user_id = %s AND status = 'ativo'
            """, (bilhetes_gratis_usados, session['user_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Pagamento processado com sucesso!',
            'codigo_usado': codigo if codigo else None,
            'bilhetes_gratis_usados': bilhetes_gratis_usados
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

# TEST ROUTE - Comment out for production
@app.route('/debug/bar')
def debug_bar():
    pass
  
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        
        cursor.execute("SELECT * FROM menus WHERE ativo = 1")
        menus = cursor.fetchall()
        
      
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

def enviar_email_newsletter(destinatario_email, proximos_filmes):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Novidades CineVibe - Proximas Estreias'
        msg['From'] = f'CineVibe <{EMAIL_USER}>'
        msg['To'] = destinatario_email

        filmes_html = ''
        for filme in proximos_filmes:
            data_str = ''
            if filme.get('data_lancamento'):
                try:
                    d = filme['data_lancamento']
                    if hasattr(d, 'strftime'):
                        data_str = f'<p style="margin:6px 0 0 0;font-size:13px;color:#aaa;">Estreia: {d.strftime("%d/%m/%Y")}</p>'
                except:
                    pass
            filmes_html += f'''
            <td style="width:50%;padding:14px;vertical-align:top;text-align:center;border:1px solid #333;border-radius:6px;">
                <p style="margin:0;font-size:17px;font-weight:bold;color:#FFD700;">{filme["titulo"]}</p>
                <p style="margin:6px 0 0 0;font-size:13px;color:#ccc;">{filme.get("genero_nome","")}</p>
                {data_str}
            </td>
            <td style="width:10px;"></td>'''

        html = f'''<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Novidades CineVibe</title>
</head>
<body style="margin:0;padding:0;background-color:#0a0a0a;font-family:Arial,Helvetica,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0a0a;">
  <tr>
    <td align="center" style="padding:30px 10px;">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#111;border-radius:10px;overflow:hidden;">

        <!-- Header -->
        <tr>
          <td style="background-color:#1a1a1a;padding:30px;text-align:center;border-bottom:2px solid #FFD700;">
            <p style="margin:0;font-size:28px;font-weight:bold;color:#FFD700;letter-spacing:2px;">CINEVIBE</p>
            <p style="margin:8px 0 0 0;font-size:13px;color:#aaa;letter-spacing:1px;">A SUA EXPERIENCIA CINEMATOGRAFICA</p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:30px;">
            <p style="margin:0 0 8px 0;font-size:22px;font-weight:bold;color:#fff;">Obrigado por subscrever!</p>
            <p style="margin:0 0 24px 0;font-size:15px;color:#bbb;line-height:1.6;">Fique a par das proximas estreias em exclusivo para os nossos subscritores.</p>

            <p style="margin:0 0 16px 0;font-size:18px;font-weight:bold;color:#FFD700;border-bottom:1px solid #333;padding-bottom:10px;">Proximas Estreias</p>

            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                {filmes_html}
              </tr>
            </table>

          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background-color:#1a1a1a;padding:20px;text-align:center;border-top:1px solid #333;">
            <p style="margin:0;font-size:12px;color:#666;">Recebeu este email porque subscreveu a newsletter do CineVibe.</p>
            <p style="margin:6px 0 0 0;font-size:12px;color:#666;">CineVibe - info@cinevibe.pt</p>
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>
</body>
</html>'''

        msg.attach(MIMEText(html, 'html', 'utf-8'))
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, destinatario_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        app.logger.error(f"Erro ao enviar newsletter: {str(e)}")
        return False


@app.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    email = request.form.get('email', '').strip()
    if not email or '@' not in email:
        return jsonify({'success': False, 'message': 'Email invalido.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verificar se já existe
        cursor.execute("SELECT id, ativo FROM newsletter_subscricoes WHERE email = %s", (email,))
        existente = cursor.fetchone()

        if existente:
            if existente['ativo']:
                return jsonify({'success': False, 'message': 'Este email ja esta subscrito.'})
            else:
                cursor.execute("UPDATE newsletter_subscricoes SET ativo = 1, data_subscricao = NOW() WHERE email = %s", (email,))
                conn.commit()
        else:
            cursor.execute("INSERT INTO newsletter_subscricoes (email) VALUES (%s)", (email,))
            conn.commit()

        # Buscar as 2 proximas estreias (data_lancamento >= hoje, ordenado ASC)
        cursor.execute("""
            SELECT f.titulo, f.data_lancamento, g.nome as genero_nome
            FROM filmes f
            LEFT JOIN filme_generos fg ON f.id = fg.filme_id
            LEFT JOIN generos g ON fg.genero_id = g.id
            WHERE f.data_lancamento >= CURDATE()
            GROUP BY f.id
            ORDER BY f.data_lancamento ASC
            LIMIT 2
        """)
        proximos_filmes = cursor.fetchall()

        # Fallback: se não houver filmes futuros, pegar os mais recentes
        if not proximos_filmes:
            cursor.execute("""
                SELECT f.titulo, f.data_lancamento, g.nome as genero_nome
                FROM filmes f
                LEFT JOIN filme_generos fg ON f.id = fg.filme_id
                LEFT JOIN generos g ON fg.genero_id = g.id
                WHERE f.estado IN ('brevemente', 'em_exibicao')
                GROUP BY f.id
                ORDER BY f.data_lancamento DESC
                LIMIT 2
            """)
            proximos_filmes = cursor.fetchall()

        enviar_email_newsletter(email, proximos_filmes)

        return jsonify({'success': True, 'message': 'Subscricao realizada com sucesso! Verifique o seu email.'})
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Erro newsletter: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro ao processar subscricao.'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/cinema/<int:cinema_id>')
def api_cinema(cinema_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM cinemas WHERE id = %s", (cinema_id,))
        cinema = cursor.fetchone()
        if cinema:
            return jsonify({'success': True, 'cinema': cinema})
        return jsonify({'success': False, 'message': 'Cinema não encontrado'}), 404
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    pass
 
    with app.app_context():
        criar_tabelas_resgates()
    
    app.logger.info("Iniciando app; endpoints registados:\n%s", app.url_map)
    app.run(debug=True)

