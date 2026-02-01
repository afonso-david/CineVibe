from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import mysql.connector
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# SECRET KEY para sessões/flash (muda para algo seguro antes de pôr em produção)
app.secret_key = "troca_isto_por_uma_chave_secreta_e_complexa"

# Configurações de Email
try:
    from email_config import EMAIL_CONFIG
    EMAIL_HOST = EMAIL_CONFIG['HOST']
    EMAIL_PORT = EMAIL_CONFIG['PORT']
    EMAIL_USER = EMAIL_CONFIG['USER']
    EMAIL_PASSWORD = EMAIL_CONFIG['PASSWORD']
    EMAIL_USE_TLS = EMAIL_CONFIG['USE_TLS']
except ImportError:
    # Fallback para configurações padrão
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USER = 'cinevibe.bilhetes@gmail.com'
    EMAIL_PASSWORD = 'goxm upky dcyx nbyx'  # Configure no email_config.py
    EMAIL_USE_TLS = True

def enviar_email_confirmacao(destinatario_email, destinatario_nome, dados_reserva):
    """
    Envia email de confirmação de reserva usando template HTML
    """
    try:
        app.logger.info(f"Enviando email para: {destinatario_email}")
        
        # Verificar se as credenciais de email estão configuradas
        if EMAIL_PASSWORD in ['sua_senha_app_aqui', 'DESATIVADO_TEMPORARIAMENTE'] or not EMAIL_PASSWORD:
            app.logger.warning("Email desativado temporariamente. Configure senha de app do Gmail para ativar.")
            return False

        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🎬 Confirmação de Reserva CineVibe - #{dados_reserva["reserva_id"]}'
        msg['From'] = f'CineVibe <{EMAIL_USER}>'
        msg['To'] = destinatario_email

        # Renderizar template HTML do email
        try:
            from datetime import datetime
            data_confirmacao = datetime.now().strftime('%d/%m/%Y às %H:%M')
            
            html_content = render_template('email_confirmacao.html',
                                         nome=destinatario_nome,
                                         email=destinatario_email,
                                         reserva_id=dados_reserva.get("reserva_id", 0),
                                         filme=dados_reserva.get("filme", "Filme"),
                                         cinema=dados_reserva.get("cinema", "Cinema"),
                                         tipo_sessao=dados_reserva.get("tipo_sessao", "Normal"),
                                         horario=dados_reserva.get("horario", "Data não definida"),
                                         quantidade=dados_reserva.get("quantidade", 0),
                                         lugares=dados_reserva.get("lugares", ""),
                                         preco_total=dados_reserva.get("preco_total", "0.00€"),
                                         data_confirmacao=data_confirmacao)
        except Exception as template_error:
            app.logger.error(f"❌ ERRO AO RENDERIZAR TEMPLATE: {str(template_error)}")
            app.logger.error(f"Dados: {dados_reserva}")
            raise template_error

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
        
        app.logger.info(f"✅ Email enviado com sucesso para {destinatario_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        app.logger.error(f"❌ Erro de autenticação SMTP: {str(e)}")
        app.logger.error("Verifique as credenciais no email_config.py")
        return False
    except smtplib.SMTPException as e:
        app.logger.error(f"❌ Erro SMTP: {str(e)}")
        return False
    except Exception as e:
        app.logger.error(f"❌ Erro geral ao enviar email: {str(e)}")
        app.logger.exception("Stack trace:")
        return False
        app.logger.exception("Stack trace completo:")
        return False

# ==========================
# Conexão à base de dados
# ==========================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kevin@15",  # coloca a tua senha se houver
        database="cinevibe"
    )

def atualizar_estados_filmes_automatico():
    """
    Função utilitária para atualizar estados dos filmes automaticamente
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
            app.logger.info(f"🎬 Sistema automático: {filmes_atualizados} filmes atualizados para 'em_exibicao'")
        
        cursor.close()
        conn.close()
        return filmes_atualizados
        
    except Exception as e:
        app.logger.error(f"❌ Erro na atualização automática de filmes: {e}")
        return 0

# ==========================
# Util: normalizar imagem paths/URLs
# ==========================
def _normalize_img_path(raw):
    """Normaliza paths/URLs de imagem"""
    if not raw:
        return 'imgs/placeholder.svg'
    p = str(raw).replace('\\', '/').strip().strip('"').strip()
    if p.startswith('http://') or p.startswith('https://'):
        return p
    if p.startswith('/static/'):
        p = p[len('/static/'):]
    elif p.startswith('static/'):
        p = p[len('static/'):]
    elif p.startswith('/'):
        p = p[1:]
    return p or 'imgs/placeholder.svg'

# ==========================
# Util: obter avatar do usuário logado
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
                    COALESCE(u.avatar, a.caminho) as avatar_path
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
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Atualização automática de estados dos filmes
        cursor.execute("""
            UPDATE filmes 
            SET estado = 'em_exibicao' 
            WHERE estado = 'brevemente' 
            AND data_lancamento IS NOT NULL
            AND data_lancamento <= CURDATE()
        """)
        
        if cursor.rowcount > 0:
            app.logger.info(f"🎬 Atualizados {cursor.rowcount} filmes para 'em_exibicao'")
            conn.commit()
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
            LEFT JOIN reservas r ON f.id = r.filme_id
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
                f['poster_url'] = f['poster_url'].replace('\\', '/').replace('"', '').strip()
            if f.get('poster_hover'):
                f['poster_hover'] = f['poster_hover'].replace('\\', '/').replace('"', '').strip()
            f['classificacao_manual'] = str(i + 1)
        
    finally:
        try: 
            cursor.close()
        except: 
            pass
        try: 
            conn.close()
        except: 
            pass

    return render_template('home.html', filmes=filmes)

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
        
        # Buscar o avatar do usuário
        cur.execute(
            "SELECT a.caminho FROM usuarios u LEFT JOIN avatars a ON u.avatar_id = a.id WHERE u.id = %s",
            (user['id'],)
        )
        avatar_data = cur.fetchone()
        if avatar_data and avatar_data['caminho']:
            session['user_avatar'] = avatar_data['caminho'].replace('\\', '/').replace('"', '').strip()
        else:
            session['user_avatar'] = 'imgs/icons/user_icon34-removebg-preview.png'

        cur.execute(
            "UPDATE usuarios SET ultimo_login = %s WHERE id = %s",
            (datetime.now(), user['id'])
        )
        conn.commit()
        conn.close()

        flash(f"Bem-vindo, {user['nome']}!", "sucesso")
        
        # Redirecionar para a URL de retorno ou home
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('home'))

    return render_template("login.html", next_url=next_url)


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
            avatar_id = request.form.get("avatar", "").strip()
            avatar_upload = request.files.get("avatar_upload")

            # Debug - ver o que está sendo recebido
            print(f"DEBUG REGISTO - Nome: {nome}, Email: {email}, Avatar ID: {avatar_id}, Upload: {avatar_upload}")
            
            # Validações básicas
            if not nome or not email or not senha:
                flash("Preencha todos os campos!", "erro")
                cursor.close()
                conn.close()
                return redirect(url_for("registo"))
            
            # Verificar se email já existe
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Este email já está registado!", "erro")
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
            elif avatar_id:
                # Inserir usuário com avatar da galeria
                print(f"DEBUG - Inserindo com avatar_id: {avatar_id}")
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha, criado_em, ultimo_login, avatar_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nome, email, senha_hash, agora, agora, avatar_id))
            else:
                # Inserir usuário com avatar padrão (ID 1 - assumindo que existe)
                print("DEBUG - Nenhum avatar selecionado, usando avatar padrão ID 1")
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha, criado_em, ultimo_login, avatar_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nome, email, senha_hash, agora, agora, 1))
            
            conn.commit()
            
            # Obter o ID do usuário recém-criado
            user_id = cursor.lastrowid
            
            # Buscar o avatar do usuário
            avatar_path = 'imgs/icons/user_icon34-removebg-preview.png'
            
            if custom_avatar_path:
                avatar_path = custom_avatar_path
                print(f"DEBUG - Avatar customizado: {avatar_path}")
            elif avatar_id:
                cursor.execute("SELECT caminho FROM avatars WHERE id = %s", (avatar_id,))
                result = cursor.fetchone()
                print(f"DEBUG - Resultado busca avatar: {result}")
                if result and result['caminho']:
                    avatar_path = result['caminho'].replace('\\', '/').replace('"', '').strip()
                    print(f"DEBUG - Avatar da galeria: {avatar_path}")
            else:
                # Buscar avatar padrão (ID 1)
                cursor.execute("SELECT caminho FROM avatars WHERE id = 1")
                result = cursor.fetchone()
                if result and result['caminho']:
                    avatar_path = result['caminho'].replace('\\', '/').replace('"', '').strip()
                    print(f"DEBUG - Avatar padrão: {avatar_path}")
            
            cursor.close()
            conn.close()
            
            # Fazer login automático
            session['user_id'] = user_id
            session['user_nome'] = nome
            session['user_avatar'] = avatar_path

            flash(f"Bem-vindo, {nome}! Conta criada com sucesso!", "sucesso")
            return redirect(url_for("home"))
            
        except Exception as e:
            if conn:
                conn.rollback()
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            flash(f"Erro ao criar conta: {str(e)}", "erro")
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


@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        flash("Inicia sessão primeiro!", "erro")
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Buscar dados do usuário incluindo biografia e filme favorito
    cursor.execute("""
        SELECT u.id, u.nome, u.email, u.is_admin, u.biografia, u.filme_favorito_id,
               CASE 
                   WHEN u.avatar IS NOT NULL AND u.avatar != '' AND u.avatar != 'imgs/avatars/default.png' THEN u.avatar
                   WHEN a.caminho IS NOT NULL THEN a.caminho
                   ELSE 'imgs/icons/user_icon34-removebg-preview.png'
               END AS avatar,
               f.titulo AS filme_favorito_titulo,
               f.poster_url AS filme_favorito_poster
        FROM usuarios u
        LEFT JOIN avatars a ON u.avatar_id = a.id
        LEFT JOIN filmes f ON u.filme_favorito_id = f.id
        WHERE u.id = %s
    """, (user_id,))
    user = cursor.fetchone()
    
    # Limpar o caminho do avatar
    if user and user.get('avatar'):
        user['avatar'] = user['avatar'].replace('\\', '/').replace('"', '').strip()
        # Se ainda estiver vazio após limpeza, usar padrão
        if not user['avatar'] or user['avatar'] == 'imgs/' or user['avatar'] == '' or user['avatar'] == 'imgs/avatars/default.png':
            user['avatar'] = 'imgs/icons/user_icon34-removebg-preview.png'

    if not user:
        cursor.close()
        conn.close()
        flash("Utilizador não encontrado!", "erro")
        return redirect(url_for('home'))

    # Se for admin, redirecionar para o painel admin
    if user.get('is_admin'):
        cursor.close()
        conn.close()
        app.logger.info(f"Admin detectado: {user['email']} - Redirecionando para dashboard")
        return redirect(url_for('admin_dashboard'))

    # Buscar filmes vistos com avaliações
    cursor.execute("""
        SELECT 
            f.id,
            f.titulo,
            f.poster_url,
            f.duracao,
            MAX(r.data_sessao) as data_sessao,
            av.rating,
            av.comentario,
            av.data_avaliacao,
            (SELECT h2.hora 
             FROM reservas r2
             JOIN horarios_sessao hs2 ON r2.sessao_id = hs2.id
             JOIN horarios h2 ON hs2.id_horario = h2.id
             WHERE r2.filme_id = f.id 
             AND r2.usuario_id = %s
             AND r2.data_sessao = MAX(r.data_sessao)
             ORDER BY h2.hora DESC
             LIMIT 1) as hora,
            (SELECT c2.nome
             FROM reservas r2
             JOIN cinemas c2 ON r2.cinema_id = c2.id
             WHERE r2.filme_id = f.id 
             AND r2.usuario_id = %s
             AND r2.data_sessao = MAX(r.data_sessao)
             ORDER BY r2.id DESC
             LIMIT 1) as cinema_nome,
            (SELECT ts2.nome
             FROM reservas r2
             JOIN tipos_sessao ts2 ON r2.tipo_sessao_id = ts2.id
             WHERE r2.filme_id = f.id 
             AND r2.usuario_id = %s
             AND r2.data_sessao = MAX(r.data_sessao)
             ORDER BY r2.id DESC
             LIMIT 1) as tipo_sessao,
            (SELECT GROUP_CONCAT(DISTINCT g2.nome SEPARATOR ', ')
             FROM filme_generos fg2
             JOIN generos g2 ON fg2.genero_id = g2.id
             WHERE fg2.filme_id = f.id) as generos
        FROM reservas r
        JOIN filmes f ON r.filme_id = f.id
        JOIN horarios_sessao hs ON r.sessao_id = hs.id
        JOIN horarios h ON hs.id_horario = h.id
        LEFT JOIN avaliacoes_filmes av ON f.id = av.filme_id AND av.usuario_id = %s
        WHERE r.usuario_id = %s
        AND DATE_ADD(CONCAT(r.data_sessao, ' ', h.hora), INTERVAL f.duracao MINUTE) < NOW()
        GROUP BY f.id
        ORDER BY MAX(r.data_sessao) DESC
    """, (user_id, user_id, user_id, user_id, user_id))
    filmes_vistos = cursor.fetchall()
    
    # Buscar cinemas favoritos
    cursor.execute("""
        SELECT c.id, c.nome, c.localizacao, c.regiao, cf.data_adicao
        FROM cinemas_favoritos cf
        JOIN cinemas c ON cf.cinema_id = c.id
        WHERE cf.usuario_id = %s
        ORDER BY cf.data_adicao DESC
    """, (user_id,))
    cinemas_favoritos = cursor.fetchall()
    
    # Buscar estatísticas de avaliações
    cursor.execute("""
        SELECT 
            COUNT(*) as total_avaliacoes,
            AVG(rating) as media_avaliacoes,
            MAX(rating) as melhor_avaliacao,
            MIN(rating) as pior_avaliacao
        FROM avaliacoes_filmes 
        WHERE usuario_id = %s
    """, (user_id,))
    stats_avaliacoes = cursor.fetchone()
    
    # Normalizar poster_url
    for filme in filmes_vistos:
        if filme.get('poster_url'):
            filme['poster_url'] = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
    
    # Calcular pontos: 100 pontos por filme visto + 50 por avaliação
    total_filmes_vistos = len(filmes_vistos)
    total_avaliacoes = stats_avaliacoes['total_avaliacoes'] or 0
    pontos = (total_filmes_vistos * 100) + (total_avaliacoes * 50)
    
    # Determinar nível baseado nos pontos
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

    cursor.close()
    conn.close()

    if user.get("avatar"):
        user["avatar"] = user["avatar"].replace("\\", "/").replace('"', '').strip()
        avatar = user["avatar"]
        session['user_avatar'] = avatar  # Atualizar na sessão
    else:
        avatar = 'imgs/icons/user_icon34-removebg-preview.png'
        session['user_avatar'] = avatar

    return render_template("perfil.html", 
                         user=user, 
                         filmes_vistos=filmes_vistos,
                         cinemas_favoritos=cinemas_favoritos,
                         stats_avaliacoes=stats_avaliacoes,
                         pontos=pontos,
                         nivel=nivel,
                         nivel_cor=nivel_cor,
                         total_filmes_vistos=total_filmes_vistos,
                         total_avaliacoes=total_avaliacoes,
                         logged_in=True,
                         avatar=avatar,
                         is_admin=user.get('is_admin', False))

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
    
    # Buscar avatar do usuário
    cursor.execute("""
        SELECT COALESCE(u.avatar, a.caminho) AS avatar
        FROM usuarios u
        LEFT JOIN avatars a ON u.avatar_id = a.id
        WHERE u.id = %s
    """, (user_id,))
    user_data = cursor.fetchone()
    avatar = user_data['avatar'].replace('\\', '/').replace('"', '').strip() if user_data and user_data.get('avatar') else 'imgs/icons/user_icon34-removebg-preview.png'
    
    # Calcular pontos do usuário (mesmo cálculo do perfil)
    # Contar filmes ÚNICOS vistos (não reservas duplicadas)
    cursor.execute("""
        SELECT COUNT(DISTINCT f.id) as total
        FROM reservas r
        JOIN filmes f ON r.filme_id = f.id
        JOIN horarios_sessao hs ON r.sessao_id = hs.id
        JOIN horarios h ON hs.id_horario = h.id
        WHERE r.usuario_id = %s
        AND DATE_ADD(CONCAT(r.data_sessao, ' ', h.hora), INTERVAL f.duracao MINUTE) < NOW()
    """, (user_id,))
    filmes_vistos = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM avaliacoes_filmes WHERE usuario_id = %s", (user_id,))
    avaliacoes = cursor.fetchone()['total']
    
    pontos = (filmes_vistos * 100) + (avaliacoes * 50)
    
    # Buscar prémios da tabela premios
    cursor.execute("""
        SELECT 
            id,
            nome as titulo,
            'Prémio disponível para resgate' as descricao,
            pontos as custo_pontos,
            img_url as imagem
        FROM premios
        ORDER BY pontos ASC
    """)
    recompensas_raw = cursor.fetchall()
    
    # Limpar caminhos das imagens (remover barras invertidas e aspas)
    recompensas = []
    for r in recompensas_raw:
        r_dict = dict(r)
        # Limpar e validar imagem
        if r_dict.get('imagem'):
            r_dict['imagem'] = r_dict['imagem'].replace('\\', '/').replace('"', '').strip()
        else:
            # Se não tem imagem, usar imagem padrão
            r_dict['imagem'] = 'imgs/icons/wheel-removebg-preview.png'
        
        recompensas.append(r_dict)
    
    cursor.close()
    conn.close()
    
    return render_template('recompensas.html', logged_in=True, avatar=avatar, pontos=pontos, recompensas=recompensas)

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
    
    # Estatísticas gerais
    cur.execute("SELECT COUNT(*) as total FROM filmes")
    total_filmes = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as total FROM cinemas")
    total_cinemas = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as total FROM usuarios WHERE is_admin = FALSE")
    total_usuarios = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as total FROM reservas")
    total_reservas = cur.fetchone()['total']
    
    # Vendas semanais (últimos 7 dias)
    cur.execute("""
        SELECT COALESCE(SUM(ts.preco_bilhete), 0) as total_vendas
        FROM reservas r
        JOIN tipos_sessao ts ON r.tipo_sessao_id = ts.id
        WHERE r.reservado_em >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    """)
    vendas_semanais = cur.fetchone()['total_vendas'] or 0
    
    # Receita total de todos os tempos
    cur.execute("""
        SELECT COALESCE(SUM(ts.preco_bilhete), 0) as receita_total
        FROM reservas r
        JOIN tipos_sessao ts ON r.tipo_sessao_id = ts.id
    """)
    receita_total = cur.fetchone()['receita_total'] or 0
    
    # Top 10 snacks/produtos mais vendidos
    cur.execute("""
        SELECT produto, COUNT(*) as vendas
        FROM bar
        GROUP BY produto
        ORDER BY vendas DESC
        LIMIT 10
    """)
    top_snacks = cur.fetchall()
    
    # Top 10 filmes mais vistos
    cur.execute("""
        SELECT f.titulo, COUNT(r.id) as total_reservas
        FROM filmes f
        JOIN reservas r ON f.id = r.filme_id
        GROUP BY f.id, f.titulo
        ORDER BY total_reservas DESC
        LIMIT 10
    """)
    top_filmes = cur.fetchall()
    
    # Reservas por dia (últimos 7 dias)
    cur.execute("""
        SELECT DATE(reservado_em) as data, COUNT(*) as total
        FROM reservas
        WHERE reservado_em >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY DATE(reservado_em)
        ORDER BY data
    """)
    reservas_diarias = cur.fetchall()
    
    # Vendas por cinema
    cur.execute("""
        SELECT c.nome, COALESCE(SUM(ts.preco_bilhete), 0) as total_vendas
        FROM cinemas c
        LEFT JOIN reservas r ON c.id = r.cinema_id
        LEFT JOIN tipos_sessao ts ON r.tipo_sessao_id = ts.id
        GROUP BY c.id, c.nome
        ORDER BY total_vendas DESC
    """)
    vendas_por_cinema = cur.fetchall()
    
    # Horários mais populares
    cur.execute("""
        SELECT TIME_FORMAT(h.hora, '%H:%i') as horario, COUNT(r.id) as total_reservas
        FROM horarios_sessao hs
        JOIN horarios h ON hs.id_horario = h.id
        JOIN reservas r ON hs.id = r.sessao_id
        GROUP BY h.hora
        ORDER BY total_reservas DESC
        LIMIT 6
    """)
    horarios_populares = cur.fetchall()
    
    # Últimas 10 reservas
    cur.execute("""
        SELECT r.id, r.lugar, r.reservado_em,
               u.nome as usuario_nome,
               f.titulo as filme_titulo,
               c.nome as cinema_nome
        FROM reservas r
        JOIN usuarios u ON r.usuario_id = u.id
        JOIN filmes f ON r.filme_id = f.id
        JOIN cinemas c ON r.cinema_id = c.id
        ORDER BY r.reservado_em DESC
        LIMIT 10
    """)
    ultimas_reservas = cur.fetchall()
    
    # Novos usuários (últimos 7 dias)
    cur.execute("""
        SELECT COUNT(*) as total
        FROM usuarios
        WHERE criado_em >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        AND is_admin = FALSE
    """)
    novos_usuarios = cur.fetchone()['total']
    
    # Usuários ativos (últimos 30 dias)
    cur.execute("""
        SELECT COUNT(DISTINCT usuario_id) as total
        FROM reservas
        WHERE reservado_em >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    """)
    usuarios_ativos = cur.fetchone()['total']
    
    # Taxa de retorno (usuários que fizeram mais de 1 reserva)
    cur.execute("""
        SELECT 
            (COUNT(DISTINCT CASE WHEN total_reservas > 1 THEN usuario_id END) * 100.0 / 
            NULLIF(COUNT(DISTINCT usuario_id), 0)) as taxa
        FROM (
            SELECT usuario_id, COUNT(*) as total_reservas
            FROM reservas
            GROUP BY usuario_id
        ) as user_reservas
    """)
    taxa_retorno_result = cur.fetchone()
    taxa_retorno = taxa_retorno_result['taxa'] if taxa_retorno_result and taxa_retorno_result['taxa'] else 0
    
    cur.close()
    conn.close()
    
    return render_template('admin_dashboard.html',
                         total_filmes=total_filmes,
                         total_cinemas=total_cinemas,
                         total_usuarios=total_usuarios,
                         total_reservas=total_reservas,
                         vendas_semanais=vendas_semanais,
                         receita_total=receita_total,
                         top_snacks=top_snacks,
                         top_filmes=top_filmes,
                         reservas_diarias=reservas_diarias,
                         vendas_por_cinema=vendas_por_cinema,
                         horarios_populares=horarios_populares,
                         ultimas_reservas=ultimas_reservas,
                         novos_usuarios=novos_usuarios,
                         usuarios_ativos=usuarios_ativos,
                         taxa_retorno=taxa_retorno)

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
    
    # Buscar todos os filmes
    cur.execute("""
        SELECT f.*, 
               GROUP_CONCAT(DISTINCT g.nome SEPARATOR ', ') as generos,
               COUNT(DISTINCT fc.cinema_id) as num_cinemas
        FROM filmes f
        LEFT JOIN filme_generos fg ON f.id = fg.filme_id
        LEFT JOIN generos g ON fg.genero_id = g.id
        LEFT JOIN filmes_cinemas fc ON f.id = fc.filme_id
        GROUP BY f.id
        ORDER BY f.id DESC
    """)
    filmes = cur.fetchall()
    
    # Buscar todos os géneros disponíveis
    cur.execute("SELECT id, nome FROM generos ORDER BY nome")
    generos = cur.fetchall()
    
    # Limpar caminhos dos posters
    for filme in filmes:
        if filme.get('poster_url'):
            filme['poster_url'] = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
    
    cur.close()
    conn.close()
    
    return render_template('admin_filmes.html', filmes=filmes, generos=generos)

@app.route('/admin/filmes/<int:filme_id>')
def admin_filme_detalhe(filme_id):
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
    cur.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
    filme = cur.fetchone()
    
    if not filme:
        flash("Filme não encontrado!", "erro")
        return redirect(url_for('admin_filmes'))
    
    # Limpar caminho do poster
    if filme.get('poster_url'):
        filme['poster_url'] = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
    
    # Buscar cinemas associados
    cur.execute("""
        SELECT c.id, c.nome, c.regiao
        FROM filmes_cinemas fc
        JOIN cinemas c ON fc.cinema_id = c.id
        WHERE fc.filme_id = %s
        ORDER BY c.nome
    """, (filme_id,))
    cinemas_filme = cur.fetchall()
    
    # Buscar todos os cinemas
    cur.execute("SELECT id, nome, regiao FROM cinemas ORDER BY nome")
    todos_cinemas = cur.fetchall()
    
    # Buscar horários apenas dos cinemas associados ao filme
    cur.execute("""
        SELECT hs.id, hs.id_cinema, hs.id_tipo_sessao, 
               c.nome as cinema_nome, ts.nome as tipo_sessao, 
               h.hora, s.nome_sala
        FROM horarios_sessao hs
        JOIN cinemas c ON hs.id_cinema = c.id
        JOIN tipos_sessao ts ON hs.id_tipo_sessao = ts.id
        JOIN horarios h ON hs.id_horario = h.id
        LEFT JOIN salas s ON hs.id_sala = s.id
        WHERE hs.id_filme = %s 
        AND hs.id_cinema IN (
            SELECT cinema_id FROM filmes_cinemas WHERE filme_id = %s
        )
        ORDER BY c.nome, ts.nome, h.hora
    """, (filme_id, filme_id))
    horarios = cur.fetchall()
    
    # Buscar tipos de sessão
    cur.execute("SELECT id, nome FROM tipos_sessao ORDER BY id")
    tipos_sessao = cur.fetchall()
    
    # Buscar todos os horários base (para usar no template)
    cur.execute("SELECT id, hora FROM horarios ORDER BY hora")
    horarios_disponiveis = cur.fetchall()
    
    # Buscar salas por cinema
    cur.execute("""
        SELECT id, id_cinema, nome_sala, capacidade
        FROM salas
        ORDER BY id_cinema, nome_sala
    """)
    salas = cur.fetchall()
    
    # Buscar atores do filme
    cur.execute("""
        SELECT a.id, a.nome, a.foto_url, fa.papel
        FROM filme_atores fa
        JOIN atores a ON fa.ator_id = a.id
        WHERE fa.filme_id = %s
        ORDER BY a.nome
    """, (filme_id,))
    atores_filme = cur.fetchall()
    
    # Limpar caminhos das fotos dos atores
    for ator in atores_filme:
        if ator.get('foto_url'):
            ator['foto_url'] = ator['foto_url'].replace('\\', '/').replace('"', '').strip()
    
    # Buscar todos os atores disponíveis
    cur.execute("SELECT id, nome, foto_url FROM atores ORDER BY nome")
    todos_atores = cur.fetchall()
    
    # Limpar caminhos das fotos
    for ator in todos_atores:
        if ator.get('foto_url'):
            ator['foto_url'] = ator['foto_url'].replace('\\', '/').replace('"', '').strip()
    
    cur.close()
    conn.close()
    
    return render_template('admin_filme_detalhe.html',
                         filme=filme,
                         cinemas_filme=cinemas_filme,
                         todos_cinemas=todos_cinemas,
                         horarios=horarios,
                         tipos_sessao=tipos_sessao,
                         horarios_disponiveis=horarios_disponiveis,
                         atores_filme=atores_filme,
                         todos_atores=todos_atores,
                         salas=salas)

@app.route('/admin/filmes/adicionar', methods=['POST'])
def admin_adicionar_filme():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        titulo = request.form.get('titulo')
        diretor = request.form.get('diretor')
        data_lancamento = request.form.get('data_lancamento')
        duracao = request.form.get('duracao')
        idade_recomendada = request.form.get('idade_recomendada')
        sinopse = request.form.get('sinopse')
        poster_url = request.form.get('poster_url')
        trailer_url = request.form.get('trailer_url')
        estado = request.form.get('estado', 'em_exibicao')
        generos = request.form.getlist('generos[]')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Inserir o filme
        cursor.execute("""
            INSERT INTO filmes (titulo, diretor, data_lancamento, duracao, idade_recomendada, sinopse, poster_url, trailer_url, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (titulo, diretor, data_lancamento, duracao, idade_recomendada, sinopse, poster_url, trailer_url, estado))
        
        filme_id = cursor.lastrowid
        
        # Inserir os géneros associados
        if generos:
            for genero_id in generos:
                cursor.execute("""
                    INSERT INTO filme_generos (filme_id, genero_id)
                    VALUES (%s, %s)
                """, (filme_id, genero_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Filme adicionado com sucesso!', 'sucesso')
    except Exception as e:
        flash(f'Erro ao adicionar filme: {str(e)}', 'erro')
    
    return redirect(url_for('admin_filmes'))

@app.route('/admin/filmes/<int:filme_id>/adicionar-cinema', methods=['POST'])
def admin_adicionar_cinema_filme(filme_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cinema_id = request.form.get('cinema_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Verificar se já existe
        cur.execute("""
            SELECT id FROM filmes_cinemas 
            WHERE filme_id = %s AND cinema_id = %s
        """, (filme_id, cinema_id))
        
        if cur.fetchone():
            flash("Este cinema já está associado a este filme!", "erro")
        else:
            # Limpar quaisquer horários órfãos que possam existir para este cinema e filme
            # (caso existam dados antigos na base de dados)
            cur.execute("""
                DELETE FROM horarios_sessao 
                WHERE id_filme = %s AND id_cinema = %s
            """, (filme_id, cinema_id))
            
            # Adicionar cinema ao filme
            cur.execute("""
                INSERT INTO filmes_cinemas (filme_id, cinema_id)
                VALUES (%s, %s)
            """, (filme_id, cinema_id))
            
            # NÃO adicionar horários automaticamente - deixar vazio para o admin adicionar
            conn.commit()
            flash("Cinema adicionado com sucesso! Agora adicione os horários manualmente.", "sucesso")
    except Exception as e:
        conn.rollback()
        flash(f"Erro ao adicionar cinema: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filme_detalhe', filme_id=filme_id))

@app.route('/admin/filmes/<int:filme_id>/remover-cinema/<int:cinema_id>', methods=['POST'])
def admin_remover_cinema_filme(filme_id, cinema_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Primeiro remover todos os horários associados a este cinema e filme
        cur.execute("""
            DELETE FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s
        """, (filme_id, cinema_id))
        
        # Depois remover a associação cinema-filme
        cur.execute("""
            DELETE FROM filmes_cinemas 
            WHERE filme_id = %s AND cinema_id = %s
        """, (filme_id, cinema_id))
        
        conn.commit()
        flash("Cinema e seus horários removidos com sucesso!", "sucesso")
    except Exception as e:
        conn.rollback()
        flash(f"Erro ao remover cinema: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filme_detalhe', filme_id=filme_id))

@app.route('/admin/filmes/<int:filme_id>/adicionar-horario', methods=['POST'])
def admin_adicionar_horario(filme_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cinema_id = request.form.get('cinema_id')
    tipo_sessao_id = request.form.get('tipo_sessao_id')
    horario_id = request.form.get('horario_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO horarios_sessao (id_filme, id_cinema, id_tipo_sessao, id_horario)
            VALUES (%s, %s, %s, %s)
        """, (filme_id, cinema_id, tipo_sessao_id, horario_id))
        conn.commit()
        flash("Horário adicionado com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao adicionar horário: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filme_detalhe', filme_id=filme_id))

@app.route('/admin/filmes/<int:filme_id>/adicionar-horarios-multiplos', methods=['POST'])
def admin_adicionar_horarios_multiplos(filme_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cinema_id = request.form.get('cinema_id')
    tipo_sessao_id = request.form.get('tipo_sessao_id')
    sala_id = request.form.get('sala_id')  # Pode ser None
    horario_ids = request.form.getlist('horario_ids')
    
    if not horario_ids:
        flash("Selecione pelo menos um horário!", "erro")
        return redirect(url_for('admin_filme_detalhe', filme_id=filme_id))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Buscar horários já existentes para este filme, cinema e tipo de sessão
        cur.execute("""
            SELECT id_horario 
            FROM horarios_sessao 
            WHERE id_filme = %s AND id_cinema = %s AND id_tipo_sessao = %s
        """, (filme_id, cinema_id, tipo_sessao_id))
        horarios_existentes = [row['id_horario'] for row in cur.fetchall()]
        
        count = 0
        duplicados = 0
        
        for horario_id in horario_ids:
            # Verificar se já existe
            if int(horario_id) in horarios_existentes:
                duplicados += 1
                continue
                
            try:
                if sala_id:
                    cur.execute("""
                        INSERT INTO horarios_sessao (id_filme, id_cinema, id_tipo_sessao, id_horario, id_sala)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (filme_id, cinema_id, tipo_sessao_id, horario_id, sala_id))
                else:
                    cur.execute("""
                        INSERT INTO horarios_sessao (id_filme, id_cinema, id_tipo_sessao, id_horario)
                        VALUES (%s, %s, %s, %s)
                    """, (filme_id, cinema_id, tipo_sessao_id, horario_id))
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
    
    return redirect(url_for('admin_filme_detalhe', filme_id=filme_id))

@app.route('/admin/filmes/<int:filme_id>/remover-horario/<int:horario_id>', methods=['POST'])
def admin_remover_horario(filme_id, horario_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM horarios_sessao WHERE id = %s", (horario_id,))
        conn.commit()
        flash("Horário removido com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao remover horário: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filme_detalhe', filme_id=filme_id))

@app.route('/admin/filmes/<int:filme_id>/remover-horarios-multiplos', methods=['POST'])
def admin_remover_horarios_multiplos(filme_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    horario_ids = request.form.getlist('horario_ids')
    
    if not horario_ids:
        flash("Nenhum horário selecionado!", "erro")
        return redirect(url_for('admin_filme_detalhe', filme_id=filme_id))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Converter para inteiros
        horario_ids = [int(id) for id in horario_ids]
        
        # Criar placeholders para a query
        placeholders = ','.join(['%s'] * len(horario_ids))
        query = f"DELETE FROM horarios_sessao WHERE id IN ({placeholders})"
        
        cur.execute(query, horario_ids)
        conn.commit()
        
        count = len(horario_ids)
        flash(f"{count} horário{'s' if count > 1 else ''} removido{'s' if count > 1 else ''} com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao remover horários: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filme_detalhe', filme_id=filme_id))

@app.route('/admin/filmes/<int:filme_id>/editar', methods=['POST'])
def admin_editar_filme(filme_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    titulo = request.form.get('titulo')
    sinopse = request.form.get('sinopse')
    diretor = request.form.get('diretor')
    duracao = request.form.get('duracao')
    data_lancamento = request.form.get('data_lancamento')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE filmes 
            SET titulo = %s, sinopse = %s, diretor = %s, duracao = %s, data_lancamento = %s
            WHERE id = %s
        """, (titulo, sinopse, diretor, duracao, data_lancamento, filme_id))
        conn.commit()
        flash("Filme atualizado com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao atualizar filme: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filme_detalhe', filme_id=filme_id))

@app.route('/admin/filmes/<int:filme_id>/remover', methods=['POST'])
def admin_remover_filme(filme_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Remover associações
        cur.execute("DELETE FROM filmes_cinemas WHERE filme_id = %s", (filme_id,))
        cur.execute("DELETE FROM horarios_sessao WHERE id_filme = %s", (filme_id,))
        cur.execute("DELETE FROM filme_generos WHERE filme_id = %s", (filme_id,))
        cur.execute("DELETE FROM filme_atores WHERE filme_id = %s", (filme_id,))
        
        # Remover filme
        cur.execute("DELETE FROM filmes WHERE id = %s", (filme_id,))
        conn.commit()
        flash("Filme removido com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao remover filme: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filmes'))

@app.route('/admin/filmes/<int:filme_id>/adicionar-ator', methods=['POST'])
def admin_adicionar_ator_filme(filme_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    ator_id = request.form.get('ator_id')
    papel = request.form.get('papel')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO filme_atores (filme_id, ator_id, papel)
            VALUES (%s, %s, %s)
        """, (filme_id, ator_id, papel))
        conn.commit()
        flash("Ator adicionado com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao adicionar ator: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filme_detalhe', filme_id=filme_id))

@app.route('/admin/filmes/<int:filme_id>/remover-ator/<int:ator_id>', methods=['POST'])
def admin_remover_ator_filme(filme_id, ator_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            DELETE FROM filme_atores 
            WHERE filme_id = %s AND ator_id = %s
        """, (filme_id, ator_id))
        conn.commit()
        flash("Ator removido com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao remover ator: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filme_detalhe', filme_id=filme_id))

@app.route('/admin/filmes/<int:filme_id>/atualizar-sala-horario', methods=['POST'])
def admin_atualizar_sala_horario(filme_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    horario_sessao_id = request.form.get('horario_sessao_id')
    sala_id = request.form.get('sala_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if sala_id:
            cur.execute("""
                UPDATE horarios_sessao 
                SET id_sala = %s 
                WHERE id = %s
            """, (sala_id, horario_sessao_id))
        else:
            cur.execute("""
                UPDATE horarios_sessao 
                SET id_sala = NULL 
                WHERE id = %s
            """, (horario_sessao_id,))
        
        conn.commit()
        flash("Sala atualizada com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao atualizar sala: {str(e)}", "erro")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('admin_filme_detalhe', filme_id=filme_id))

# ==========================
# ADMIN - GESTÃO DE CINEMAS
# ==========================
@app.route('/admin/cinemas')
def admin_cinemas():
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
    
    # Parâmetros de pesquisa e filtro
    search = request.args.get('search', '')
    regiao_filter = request.args.get('regiao', '')
    
    # Query base
    query = """
        SELECT c.*, 
               COUNT(DISTINCT fc.filme_id) as num_filmes,
               COUNT(DISTINCT s.id) as num_salas
        FROM cinemas c
        LEFT JOIN filmes_cinemas fc ON c.id = fc.cinema_id
        LEFT JOIN salas s ON c.id = s.id_cinema
    """
    
    # Condições de filtro
    conditions = []
    params = []
    
    if search:
        conditions.append("(c.nome LIKE %s OR c.localizacao LIKE %s OR c.email LIKE %s)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
    
    if regiao_filter:
        conditions.append("c.regiao = %s")
        params.append(regiao_filter)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " GROUP BY c.id ORDER BY c.id DESC"
    
    cur.execute(query, params)
    cinemas = cur.fetchall()
    
    # Buscar regiões únicas para filtro
    cur.execute("SELECT DISTINCT regiao FROM cinemas WHERE regiao IS NOT NULL ORDER BY regiao")
    regioes = [r['regiao'] for r in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return render_template('admin_cinemas.html', 
                         cinemas=cinemas, 
                         regioes=regioes,
                         search=search,
                         regiao_filter=regiao_filter)

@app.route('/admin/cinemas/adicionar', methods=['POST'])
def admin_adicionar_cinema():
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
    
    nome = request.form.get('nome')
    regiao = request.form.get('regiao')
    email = request.form.get('email')
    
    try:
        cur.execute("""
            INSERT INTO cinemas (nome, regiao, email)
            VALUES (%s, %s, %s)
        """, (nome, regiao, email))
        conn.commit()
        flash("Cinema adicionado com sucesso!", "sucesso")
    except Exception as e:
        conn.rollback()
        flash(f"Erro ao adicionar cinema: {str(e)}", "erro")
    
    cur.close()
    conn.close()
    return redirect(url_for('admin_cinemas'))

@app.route('/admin/cinemas/editar/<int:cinema_id>', methods=['GET', 'POST'])
def admin_editar_cinema(cinema_id):
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
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        localizacao = request.form.get('localizacao')
        regiao = request.form.get('regiao')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        
        try:
            cur.execute("""
                UPDATE cinemas 
                SET nome = %s, localizacao = %s, regiao = %s, email = %s, telefone = %s
                WHERE id = %s
            """, (nome, localizacao, regiao, email, telefone, cinema_id))
            conn.commit()
            flash("Cinema atualizado com sucesso!", "sucesso")
        except Exception as e:
            conn.rollback()
            flash(f"Erro ao atualizar cinema: {str(e)}", "erro")
        
        cur.close()
        conn.close()
        return redirect(url_for('admin_cinemas'))
    
    # GET - buscar dados do cinema
    cur.execute("SELECT * FROM cinemas WHERE id = %s", (cinema_id,))
    cinema = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if not cinema:
        flash("Cinema não encontrado!", "erro")
        return redirect(url_for('admin_cinemas'))
    
    return render_template('admin_editar_cinema.html', cinema=cinema)

@app.route('/admin/cinemas/remover/<int:cinema_id>', methods=['POST'])
def admin_remover_cinema(cinema_id):
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
        # Verificar se há reservas associadas
        cur.execute("SELECT COUNT(*) as total FROM reservas WHERE cinema_id = %s", (cinema_id,))
        reservas = cur.fetchone()['total']
        
        if reservas > 0:
            flash(f"Não é possível remover este cinema. Existem {reservas} reservas associadas.", "erro")
        else:
            # Remover associações com filmes
            cur.execute("DELETE FROM filmes_cinemas WHERE cinema_id = %s", (cinema_id,))
            # Remover salas
            cur.execute("DELETE FROM salas WHERE id_cinema = %s", (cinema_id,))
            # Remover cinema
            cur.execute("DELETE FROM cinemas WHERE id = %s", (cinema_id,))
            conn.commit()
            flash("Cinema removido com sucesso!", "sucesso")
    except Exception as e:
        conn.rollback()
        flash(f"Erro ao remover cinema: {str(e)}", "erro")
    
    cur.close()
    conn.close()
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
    
    # Query base
    query = """
        SELECT u.id, u.nome, u.email, u.criado_em, u.ultimo_login, u.is_admin,
               COUNT(DISTINCT r.id) as num_reservas
        FROM usuarios u
        LEFT JOIN reservas r ON u.id = r.usuario_id
    """
    
    params = []
    if search:
        query += " WHERE (u.nome LIKE %s OR u.email LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    query += " GROUP BY u.id ORDER BY u.id DESC"
    
    cur.execute(query, params)
    usuarios = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin_usuarios.html', usuarios=usuarios, search=search)

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
    
    # Query base
    query = """
        SELECT r.id, r.reservado_em, r.data_sessao, r.lugar,
               u.nome as usuario_nome, u.email as usuario_email,
               f.titulo as filme_titulo,
               c.nome as cinema_nome,
               ts.nome as tipo_sessao
        FROM reservas r
        LEFT JOIN usuarios u ON r.usuario_id = u.id
        LEFT JOIN filmes f ON r.filme_id = f.id
        LEFT JOIN cinemas c ON r.cinema_id = c.id
        LEFT JOIN tipos_sessao ts ON r.tipo_sessao_id = ts.id
    """
    
    conditions = []
    params = []
    
    if search:
        conditions.append("(u.nome LIKE %s OR u.email LIKE %s OR f.titulo LIKE %s)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
    
    if cinema_filter:
        conditions.append("c.nome = %s")
        params.append(cinema_filter)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY r.id DESC LIMIT 100"
    
    cur.execute(query, params)
    reservas = cur.fetchall()
    
    # Buscar cinemas para filtro
    cur.execute("SELECT DISTINCT nome FROM cinemas ORDER BY nome")
    cinemas = [c['nome'] for c in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return render_template('admin_reservas.html', 
                         reservas=reservas, 
                         cinemas=cinemas,
                         search=search,
                         cinema_filter=cinema_filter)

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
            SELECT u.nome, u.email, u.avatar, u.avatar_id, u.is_admin, a.caminho AS avatar_path
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

    # Prioridade: avatar da tabela avatars → avatar direto do usuario → fallback
    avatar = None
    
    # Primeiro tenta o avatar da tabela avatars (via avatar_id)
    if row.get("avatar_path"):
        avatar_path = str(row.get("avatar_path"))
        # Limpa o caminho: remove aspas, barras invertidas, etc.
        avatar = avatar_path.replace("\\", "/").replace('"', '').strip()
        avatar = avatar.replace("static/", "").lstrip("/")
        
        # Garante que começa com imgs/
        if not avatar.startswith("imgs/"):
            avatar = "imgs/" + avatar.lstrip("/")
    
    # Se não conseguiu da tabela avatars, usa o campo avatar direto
    elif row.get("avatar"):
        avatar_direct = str(row.get("avatar"))
        avatar = avatar_direct.replace("\\", "/").replace('"', '').strip()
        avatar = avatar.replace("static/", "").lstrip("/")
        
        if not avatar.startswith("imgs/"):
            avatar = "imgs/" + avatar.lstrip("/")
    
    # Fallback final
    if not avatar or avatar == "imgs/" or avatar == "imgs":
        avatar = "imgs/icons/user_icon34-removebg-preview.png"

    return {
        "logged_in": True,
        "user_nome": row.get("nome"),
        "avatar": avatar,
        "avatar_id": row.get("avatar_id"),
        "is_admin": row.get("is_admin", False)
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
# Página filmes
# ==========================
@app.route('/filmes')
def filmes():
    # Atualização automática de estados dos filmes
    atualizar_estados_filmes_automatico()
    
    # Capturar filtro de género da URL
    genero_filtro = request.args.get('genero', '').strip().lower()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Query base
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

            if f.get('poster_url'):
                f['poster_url'] = f['poster_url'].replace('\\', '/').replace('"', '').strip()
            else:
                f['poster_url'] = None

            if f.get('poster_hover'):
                f['poster_hover'] = f['poster_hover'].replace('\\', '/').replace('"', '').strip()
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
                           genero_filtro=genero_filtro)

# ==========================
# Página detalhe de filme
# ==========================
@app.route('/filme/<int:filme_id>')
def filme_detalhe(filme_id):
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
        """, (filme_id,))
        filme = cursor.fetchone()
        if not filme:
            return "Filme não encontrado", 404

        cursor.execute("""
            SELECT a.id, a.nome, a.foto_url, fa.papel
            FROM filme_atores fa
            JOIN atores a ON fa.ator_id = a.id
            WHERE fa.filme_id = %s
            ORDER BY a.id
        """, (filme_id,))
        elenco = cursor.fetchall()

        cursor.execute("""
            SELECT g.nome AS genero
            FROM filme_generos fg
            JOIN generos g ON fg.genero_id = g.id
            WHERE fg.filme_id = %s
        """, (filme_id,))
        filme_generos = cursor.fetchall()

        cursor.execute("SELECT id, nome FROM tipos_sessao ORDER BY id")
        tipos_sessao = cursor.fetchall()

        # Buscar todos os horários com nome da sala
        cursor.execute("""
            SELECT hs.id, hs.id_cinema, hs.id_tipo_sessao, hs.id_sala, h.hora, s.nome_sala
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            LEFT JOIN salas s ON hs.id_sala = s.id
            WHERE hs.id_filme = %s
            ORDER BY h.hora
        """, (filme_id,))
        
        horarios_filme = cursor.fetchall()
        
        app.logger.info(f"Horários encontrados para filme {filme_id}: {len(horarios_filme)}")
        
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
        params = [filme_id]
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
        """, (filme_id,))
        avaliacoes = cursor.fetchall()
        
        # Limpar avatares
        for avaliacao in avaliacoes:
            if avaliacao.get('usuario_avatar'):
                avaliacao['usuario_avatar'] = avaliacao['usuario_avatar'].replace('\\', '/').replace('"', '').strip()
            else:
                avaliacao['usuario_avatar'] = 'imgs/icons/user_icon34-removebg-preview.png'
        
        # Verificar se o usuário logado já avaliou
        user_avaliacao = None
        if 'user_id' in session:
            cursor.execute("""
                SELECT rating, comentario
                FROM avaliacoes_filmes
                WHERE filme_id = %s AND usuario_id = %s
            """, (filme_id, session['user_id']))
            user_avaliacao = cursor.fetchone()
        
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
    
    # Converter hora para string
    for h in horarios_filme:
        hora_valor = h['hora']
        if isinstance(hora_valor, str):
            h['hora_str'] = hora_valor
        else:
            try:
                total_seconds = hora_valor.total_seconds()
                horas = int(total_seconds // 3600)
                minutos = int((total_seconds % 3600) // 60)
                h['hora_str'] = f"{horas:02d}:{minutos:02d}"
            except Exception:
                h['hora_str'] = str(hora_valor)

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

@app.route('/reserva/pagamento')
def reserva_pagamento():
    # Página de pagamento unificada para filmes e salas exclusivas
    logged_in = 'user_id' in session
    avatar = session.get('avatar', 'imgs/icons/user_icon34-removebg-preview.png')
    
    return render_template('pagamento.html', 
                         logged_in=logged_in, 
                         avatar=avatar)

@app.route('/pagamento')
def pagamento_standalone():
    # Obter parâmetros da URL
    tipo_pagamento = request.args.get('tipo', 'bilhete')  # bilhete, plano, recompensa
    plano = request.args.get('plano')
    recompensa_id = request.args.get('recompensa_id')
    categoria = request.args.get('categoria')  # Para sessão exclusiva
    
    # Parâmetros específicos de sessão exclusiva
    filme_id = request.args.get('filme_id')
    data = request.args.get('data')
    hora = request.args.get('hora')
    preco = request.args.get('preco')
    
    # Dados do usuário
    logged_in = 'user_id' in session
    avatar = session.get('avatar', 'imgs/icons/user_icon34-removebg-preview.png')
    
    # Preparar dados específicos baseado no tipo de pagamento
    dados_pagamento = {
        'tipo': tipo_pagamento,
        'plano': plano,
        'recompensa_id': recompensa_id,
        'categoria': categoria,
        'filme_id': filme_id,
        'data': data,
        'hora': hora,
        'preco': preco
    }
    
    return render_template('pagamento.html', 
                         logged_in=logged_in, 
                         avatar=avatar,
                         dados_pagamento=dados_pagamento)

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
        preco_total = None
        if preco_raw:
            try:
                # Remover símbolos e converter para float
                preco_str = str(preco_raw).replace('€', '').replace(',', '.').strip()
                preco_total = float(preco_str)
                
                if preco_total <= 0:
                    return jsonify({'success': False, 'message': 'Preço deve ser maior que zero'}), 400
                    
                app.logger.info(f"💰 Preço validado: €{preco_total}")
                
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
            preco_total = precos_padrao.get(tipo_sala.lower(), 100.00)
            app.logger.warning(f"⚠️ Preço não fornecido, usando padrão: €{preco_total}")
        
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
        app.logger.info(f"💾 Inserindo reserva: sala={tipo_sala}, preço=€{preco_total}, user_id={user_id}")
        
        cursor.execute("""
            INSERT INTO reservas_exclusivas 
            (tipo_sala, filme_id, filme_nome, data_sessao, hora_sessao, num_pessoas, preco_total, usuario_id, reservado_em, status)
            VALUES (%s, NULL, NULL, %s, %s, 0, %s, %s, NOW(), 'confirmada')
        """, (tipo_sala, data_sessao, hora_sessao, preco_total, user_id))
        
        reserva_id = cursor.lastrowid
        conn.commit()
        
        app.logger.info(f"✅ Reserva exclusiva criada com sucesso: ID {reserva_id}")
        
        # Enviar email de confirmação
        try:
            from email_config import enviar_email_confirmacao_sessao
            app.logger.info(f"📧 Enviando email de sessão exclusiva para: {email_cliente}")
            
            resultado_email = enviar_email_confirmacao_sessao(
                email_cliente,
                nome_cliente,
                tipo_sala.capitalize(),
                f"{preco_total:.2f}",
                metodo_pagamento,
                data_sessao,
                hora_sessao
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
            'preco_total': f"€{preco_total:.2f}"
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
        
        horario_id = reserva_data.get('horario')
        cinema_id = reserva_data.get('cinema')
        tipo_id = reserva_data.get('tipo')
        filme_id = reserva_data.get('filme_id')
        data_sessao = reserva_data.get('data_sessao')
        lugares = reserva_data.get('lugares', [])
        produtos_bar = reserva_data.get('produtos_bar', {})
        nome = reserva_data.get('nome', '')
        email = reserva_data.get('email', '')
        telefone = reserva_data.get('telefone', '')
        
        # Obter usuario_id se estiver logado
        usuario_id = session.get('user_id', 0)
        
        # Validação: se não está logado, precisa de nome e email
        if usuario_id == 0:
            if not nome or not email:
                return jsonify({'success': False, 'message': 'Nome e email são obrigatórios'}), 400
        
        # Validação comum
        if not horario_id or not cinema_id or not tipo_id or not lugares:
            return jsonify({'success': False, 'message': 'Dados da reserva incompletos'}), 400
        
        # Usar a mesma lógica da rota /confirmar_reserva
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar filme_id se não foi enviado
        if not filme_id:
            cursor.execute("SELECT id_filme FROM horarios_sessao WHERE id = %s", (horario_id,))
            horario_row = cursor.fetchone()
            filme_id = horario_row['id_filme'] if horario_row else None
        
        if not filme_id:
            raise Exception("Filme não encontrado")
        
        # Buscar preço do tipo de sessão
        cursor.execute("SELECT preco_bilhete FROM tipos_sessao WHERE id = %s", (tipo_id,))
        preco_row = cursor.fetchone()
        preco_bilhete = float(preco_row['preco_bilhete']) if preco_row else 8.50
        
        # Calcular preços
        preco_total_bilhetes = preco_bilhete * len(lugares)
        preco_total_bar = 0
        for produto_id, produto_info in produtos_bar.items():
            preco_total_bar += float(produto_info.get('preco', 0)) * int(produto_info.get('quantidade', 0))
        
        preco_total_geral = preco_total_bilhetes + preco_total_bar
        
        # Buscar dados do utilizador se estiver logado
        nome_cliente = None
        email_cliente = None
        telefone_cliente = None
        nome_para_email = nome
        email_para_email = email
        
        if usuario_id > 0:
            # Utilizador logado - buscar dados da BD
            cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (usuario_id,))
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
        
        for lugar in lugares:
            user_id_final = usuario_id if usuario_id > 0 else None
            
            try:
                cursor.execute("""
                    INSERT INTO reservas (sessao_id, data_sessao, filme_id, cinema_id, tipo_sessao_id, lugar, usuario_id, nome_cliente, email_cliente, telefone_cliente, reservado_em)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (horario_id, data_sessao, filme_id, cinema_id, tipo_id, lugar, user_id_final, nome_cliente, email_cliente, telefone_cliente))
            except Exception as e:
                app.logger.warning(f"Campos de cliente não existem, usando usuario_id = 1: {str(e)}")
                user_id_final = usuario_id if usuario_id > 0 else 1
                cursor.execute("""
                    INSERT INTO reservas (sessao_id, data_sessao, filme_id, cinema_id, tipo_sessao_id, lugar, usuario_id, reservado_em)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """, (horario_id, data_sessao, filme_id, cinema_id, tipo_id, lugar, user_id_final))
            
            reserva_ids.append(cursor.lastrowid)
        
        # Buscar dados para o email ANTES do commit
        cursor.execute("SELECT titulo FROM filmes WHERE id = %s", (filme_id,))
        filme_row = cursor.fetchone()
        filme_titulo = filme_row['titulo'] if filme_row else 'Filme'
        
        cursor.execute("SELECT nome FROM cinemas WHERE id = %s", (cinema_id,))
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
        """, (horario_id,))
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
            'preco_total': f"{preco_total_geral:.2f}€"
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
    horario_id = request.args.get('horario')
    cinema_id  = request.args.get('cinema')
    tipo_id    = request.args.get('tipo')
    data_sessao = request.args.get('data')  # Nova: receber data da sessão

    
    # DEBUG: Logs adicionados para rastrear tipo_id
    app.logger.info(f"🔍 ROTA /reserva - Parâmetros recebidos:")
    app.logger.info(f"  horario_id: {horario_id}")
    app.logger.info(f"  cinema_id: {cinema_id}")
    app.logger.info(f"  tipo_id: {tipo_id}")
    app.logger.info(f"  data_sessao: {data_sessao}")
    
    if not horario_id or not cinema_id or not tipo_id:
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
        """, (horario_id,))
        horario = cursor.fetchone()
        if not horario:
            return "Horário não encontrado", 404

        hora_val = horario['hora']
        horario['hora_str'] = hora_val.strftime("%H:%M") if hasattr(hora_val, 'strftime') else str(hora_val)

        # --- Filme ---
        filme_id = horario['id_filme']
        cursor.execute("""
            SELECT id, titulo, sinopse, poster_url, poster_hover, imagem_grande,
                   diretor, data_lancamento, duracao
            FROM filmes
            WHERE id = %s
        """, (filme_id,))
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
        """, (filme_id,))
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
        """, (filme_id,))
        filme_generos = [g['genero'] for g in cursor.fetchall()]

        # --- Cinema e tipo sessão com preço ---
        cursor.execute("SELECT id, nome FROM cinemas WHERE id = %s", (cinema_id,))
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

        # --- Sala e lugares ---
        cursor.execute("SELECT id, nome_sala, capacidade, tipo_sala FROM salas WHERE id = %s", (horario['id_sala'],))
        sala_temp = cursor.fetchone()
        if sala_temp:
            # Adicionar valores padrão para lugares especiais
            sala = {
                'id': sala_temp['id'],
                'nome_sala': sala_temp['nome_sala'], 
                'capacidade': sala_temp['capacidade'],
                'tipo_sala': sala_temp['tipo_sala'],
                'lugares_acessiveis': 8,  # Valor padrão
                'lugares_casal': 8,       # Valor padrão
                'lugares_premium': 8      # Valor padrão
            }
        else:
            sala = {}


        # Buscar lugares reservados para esta sessão E DATA específica
        app.logger.info(f"=== BUSCANDO LUGARES RESERVADOS ===")
        app.logger.info(f"Sessão ID: {horario_id}, Data: {data_sessao}")
        
        # Tentar com conversão explícita para int
        sessao_id_int = int(horario_id)
        
        cursor.execute("""
            SELECT lugar, id, usuario_id, reservado_em
            FROM reservas
            WHERE sessao_id = %s AND data_sessao = %s
            ORDER BY lugar
        """, (sessao_id_int, data_sessao))
        resultado_reservas = cursor.fetchall()
        lugares_reservados = [row['lugar'] for row in resultado_reservas]
        
        app.logger.info(f"Query: SELECT lugar FROM reservas WHERE sessao_id = {sessao_id_int} AND data_sessao = {data_sessao}")
        app.logger.info(f"Resultados encontrados: {len(resultado_reservas)}")
        app.logger.info(f"Lugares reservados: {lugares_reservados}")
        
        # Debug: Contar reservas por sessão e data
        cursor.execute("""
            SELECT sessao_id, data_sessao, COUNT(*) as total, GROUP_CONCAT(lugar) as lugares
            FROM reservas 
            WHERE sessao_id = %s
            GROUP BY sessao_id, data_sessao
        """, (sessao_id_int,))
        resumo = cursor.fetchall()
        app.logger.info(f"Resumo de reservas desta sessão por data: {resumo}")

        # Buscar todos os lugares da sala
        cursor.execute("""
            SELECT id, nome_lugar, ocupado
            FROM lugares
            WHERE sala_id = %s
            ORDER BY nome_lugar
        """, (sala.get('id'),))
        lugares = cursor.fetchall() or []
        
        app.logger.info(f"Total de lugares na sala: {len(lugares)}")
        
        # Marcar lugares como ocupados se estiverem reservados
        lugares_marcados = 0
        for lugar in lugares:
            nome_lugar = lugar['nome_lugar']
            # Verificar com e sem espaços
            if nome_lugar in lugares_reservados or nome_lugar.replace(' ', '') in lugares_reservados:
                lugar['ocupado'] = 1
                lugares_marcados += 1
                app.logger.info(f"✓ Lugar '{nome_lugar}' marcado como ocupado")
        
        app.logger.info(f"Total de lugares marcados como ocupados: {lugares_marcados}")
        
        # Se houver lugares reservados que não estão na tabela lugares, criar entradas temporárias
        lugares_na_tabela = [l['nome_lugar'] for l in lugares]
        for lugar_reservado in lugares_reservados:
            if lugar_reservado not in lugares_na_tabela:
                app.logger.warning(f"⚠️ Lugar reservado '{lugar_reservado}' não existe na tabela lugares! Adicionando temporariamente...")
                lugares.append({
                    'id': None,
                    'nome_lugar': lugar_reservado,
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
    
    if user_authenticated:
        conn_user = get_db_connection()
        cursor_user = conn_user.cursor(dictionary=True)
        cursor_user.execute("SELECT nome, email FROM usuarios WHERE id = %s", (session['user_id'],))
        user = cursor_user.fetchone()
        cursor_user.close()
        conn_user.close()
        
        if user:
            user_name = user['nome']
            user_email = user['email']
    
    return render_template(
        'reserva.html',
        filme=filme,
        filme_generos=filme_generos,
        elenco=elenco,
        cinema=cinema,
        tipo_sessao=tipo_sessao,
        horario=horario,
        sala=sala,
        lugares=lugares,
        produtos_bar=produtos_bar,
        menus_bar=menus_bar,
        filme_sessao=filme_sessao,
        data_sessao=data_sessao,
        user_authenticated=user_authenticated,
        user_name=user_name,
        user_email=user_email
    )
    


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
            horario_id = data.get('horario')
            cinema_id = data.get('cinema')
            tipo_id = data.get('tipo')  # ID do tipo de sessão
            filme_id = data.get('filme_id')
            data_sessao = data.get('data_sessao')
            nome = data.get('nome')
            email = data.get('email')
            telefone = data.get('telefone', '')
            lugares = data.get('lugares', [])
            produtos_bar = data.get('produtos_bar', {})
        else:
            horario_id = request.form.get('horario')
            cinema_id = request.form.get('cinema')
            tipo_id = request.form.get('tipo')
            filme_id = request.form.get('filme_id')
            data_sessao = request.form.get('data_sessao')
            nome = request.form.get('nome')
            email = request.form.get('email')
            telefone = request.form.get('telefone', '')
            lugares = []
            produtos_bar = {}
        
        # Data padrão se não fornecida
        if not data_sessao:
            from datetime import date
            data_sessao = date.today().strftime('%Y-%m-%d')
        
        # 2. VALIDAR DADOS ESSENCIAIS
        if not all([horario_id, cinema_id, tipo_id, nome, email, lugares]):
            if request.is_json:
                return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
            flash("Dados incompletos para a reserva.", "error")
            return redirect(request.referrer or url_for('home'))
        
        # 🔍 LOGS ANTES DA CONVERSÃO
        app.logger.info("=" * 80)
        app.logger.info("🔍 DADOS RECEBIDOS:")
        app.logger.info(f"   horario_id (raw): '{horario_id}' (tipo: {type(horario_id)})")
        app.logger.info(f"   cinema_id (raw): '{cinema_id}' (tipo: {type(cinema_id)})")
        app.logger.info(f"   tipo_id (raw): '{tipo_id}' (tipo: {type(tipo_id)})")
        app.logger.info(f"   filme_id (raw): '{filme_id}' (tipo: {type(filme_id)})")
        
        # Converter IDs para inteiros
        try:
            horario_id = int(horario_id)
            cinema_id = int(cinema_id)
            tipo_id = int(tipo_id)
            if filme_id:
                filme_id = int(filme_id)
                
            # 🔍 LOGS APÓS A CONVERSÃO
            app.logger.info("🔍 APÓS CONVERSÃO:")
            app.logger.info(f"   horario_id (int): {horario_id}")
            app.logger.info(f"   cinema_id (int): {cinema_id}")
            app.logger.info(f"   tipo_id (int): {tipo_id}")
            app.logger.info(f"   filme_id (int): {filme_id}")
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
        cursor.execute("SELECT id, nome FROM cinemas WHERE id = %s", (cinema_id,))
        cinema = cursor.fetchone()
        if not cinema:
            raise Exception(f"Cinema {cinema_id} não encontrado")
        
        # 6. BUSCAR HORÁRIO
        cursor.execute("""
            SELECT hs.id, hs.id_filme, hs.id_sala, hs.id_tipo_sessao, h.hora
            FROM horarios_sessao hs
            JOIN horarios h ON hs.id_horario = h.id
            WHERE hs.id = %s
        """, (horario_id,))
        horario = cursor.fetchone()
        if not horario:
            raise Exception(f"Horário {horario_id} não encontrado")
        
        # Se filme_id não foi fornecido, usar o do horário
        if not filme_id:
            filme_id = horario['id_filme']
        
        # 7. BUSCAR FILME
        cursor.execute("SELECT id, titulo FROM filmes WHERE id = %s", (filme_id,))
        filme = cursor.fetchone()
        if not filme:
            raise Exception(f"Filme {filme_id} não encontrado")
        
        # 8. CALCULAR PREÇOS (AGORA tipo_sessao JÁ ESTÁ DEFINIDO!)
        preco_bilhete = float(tipo_sessao['preco_bilhete'])
        preco_total = preco_bilhete * len(lugares)
        
        app.logger.info(f"💰 PREÇOS: Bilhete €{preco_bilhete} x {len(lugares)} lugares = €{preco_total}")
        
        # 9. DETERMINAR USUÁRIO
        usuario_id = session.get('user_id', None)
        
        # 10. INSERIR RESERVAS NA BASE DE DADOS
        reserva_ids = []
        
        for lugar in lugares:
            app.logger.info(f"🎫 INSERINDO RESERVA PARA LUGAR {lugar}:")
            app.logger.info(f"   sessao_id: {horario_id}")
            app.logger.info(f"   data_sessao: {data_sessao}")
            app.logger.info(f"   filme_id: {filme_id}")
            app.logger.info(f"   cinema_id: {cinema_id}")
            app.logger.info(f"   tipo_sessao_id: {tipo_id} ← TIPO CLICADO PELO USER")
            app.logger.info(f"   lugar: {lugar}")
            app.logger.info(f"   usuario_id: {usuario_id}")
            app.logger.info(f"   nome_cliente: {nome}")
            app.logger.info(f"   email_cliente: {email}")
            
            cursor.execute("""
                INSERT INTO reservas (
                    sessao_id, data_sessao, filme_id, cinema_id, tipo_sessao_id, 
                    lugar, usuario_id, nome_cliente, email_cliente, telefone_cliente, 
                    reservado_em
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                horario_id,      # sessao_id
                data_sessao,     # data_sessao
                filme_id,        # filme_id
                cinema_id,       # cinema_id
                tipo_id,         # tipo_sessao_id ← USAR DIRETAMENTE O TIPO CLICADO!
                lugar,           # lugar
                usuario_id,      # usuario_id
                nome,            # nome_cliente
                email,           # email_cliente
                telefone         # telefone_cliente
            ))
            
            reserva_id = cursor.lastrowid
            
            # 🔍 VERIFICAR O QUE FOI REALMENTE INSERIDO
            cursor.execute("SELECT tipo_sessao_id FROM reservas WHERE id = %s", (reserva_id,))
            verificacao = cursor.fetchone()
            app.logger.info(f"✅ VERIFICAÇÃO: Reserva {reserva_id} inserida com tipo_sessao_id = {verificacao['tipo_sessao_id']}")
            
            if verificacao['tipo_sessao_id'] != tipo_id:
                app.logger.error(f"🚨 ERRO CRÍTICO!")
                app.logger.error(f"   Tentámos inserir: {tipo_id}")
                app.logger.error(f"   Foi inserido: {verificacao['tipo_sessao_id']}")
                raise Exception(f"Erro na inserção: tipo incorreto")
            
            reserva_ids.append(reserva_id)
        
        # 11. CONFIRMAR TRANSAÇÃO
        conn.commit()
        
        # 12. PREPARAR EMAIL
        try:
            # Buscar informações completas para o email
            cursor.execute("""
                SELECT r.id, f.titulo, c.nome as cinema_nome, ts.nome as tipo_nome, 
                       h.hora, r.lugar, r.data_sessao
                FROM reservas r
                JOIN filmes f ON r.filme_id = f.id
                JOIN cinemas c ON r.cinema_id = c.id
                JOIN tipos_sessao ts ON r.tipo_sessao_id = ts.id
                JOIN horarios_sessao hs ON r.sessao_id = hs.id
                JOIN horarios h ON hs.id_horario = h.id
                WHERE r.id IN ({})
            """.format(','.join(['%s'] * len(reserva_ids))), reserva_ids)
            
            reservas_email = cursor.fetchall()
            
            # Enviar email de confirmação
            enviar_email_confirmacao(email, nome, reservas_email, preco_total)
            
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
                'preco_total': preco_total
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
    dados_teste = {
        'reserva_id': 12345,
        'filme': 'Filme de Teste',
        'cinema': 'Cinema Teste',
        'tipo_sessao': '2D',
        'horario': '20:30',
        'quantidade': 2
    }
    
    # Substitua pelo seu email para teste
    email_teste = 'seu_email_teste@gmail.com'
    nome_teste = 'Utilizador Teste'
    
    resultado = enviar_email_confirmacao(email_teste, nome_teste, dados_teste)
    
    if resultado:
        return jsonify({'success': True, 'message': 'Email enviado com sucesso!'})
    else:
        return jsonify({'success': False, 'message': 'Erro ao enviar email'})

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
    
    app.logger.info(f"sessao_exclusiva - logged_in: {logged_in}, avatar: {avatar}")
    
    return render_template('sessao_exclusiva.html', 
                         logged_in=logged_in, 
                         avatar=avatar,
                         nome=nome,
                         email=email,
                         telefone=telefone)

@app.route('/sessao_tematica')
def sessao_tematica():
    return render_template('sessoes_tematicas.html')

@app.route('/sessao_terror')
def sessao_terror():
    return render_template('sessao_terror.html')

@app.route('/sessao_vintage')
def sessao_vintage():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    filmes_classicos = []
    
    try:
        # Buscar TODOS os filmes com género "Vintage" (ID 12)
        cursor.execute("""
            SELECT 
                f.id, 
                f.titulo, 
                f.poster_url,
                YEAR(f.data_lancamento) as ano,
                GROUP_CONCAT(DISTINCT g.nome SEPARATOR ', ') AS genero
            FROM filmes f
            INNER JOIN filme_generos fg ON f.id = fg.filme_id
            INNER JOIN generos g ON fg.genero_id = g.id
            WHERE fg.genero_id = 12
            AND f.poster_url IS NOT NULL 
            AND f.poster_url != ''
            GROUP BY f.id, f.titulo, f.poster_url, f.data_lancamento
            ORDER BY f.data_lancamento ASC
        """)
        filmes_classicos = cursor.fetchall()
        
        # Normalizar poster_url
        for filme in filmes_classicos:
            if filme.get('poster_url'):
                filme['poster_url'] = filme['poster_url'].replace('\\', '/').replace('"', '').strip()
        
        app.logger.info(f"Filmes vintage encontrados: {len(filmes_classicos)}")
        if filmes_classicos:
            app.logger.info(f"Títulos: {[f['titulo'] for f in filmes_classicos]}")
        
    finally:
        cursor.close()
        conn.close()
    
    return render_template('sessao_vintage.html',
                         filmes_classicos=filmes_classicos)

@app.route('/sessao_romance')
def sessao_romance():
    return render_template('sessao_romance.html')



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
@app.route('/bar')
def bar():
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)

    produtos = []
    menus = []

    try:
        cursor.execute("""
            SELECT id, produto, preco, imagem_url, tipo
            FROM bar
            ORDER BY tipo, produto
        """)
        produtos = cursor.fetchall() or []

        cursor.execute("""
            SELECT produto_id, GROUP_CONCAT(caracteristica SEPARATOR ',') AS caracteristicas
            FROM caracteristica_produto_bar
            GROUP BY produto_id
        """)
        raw_caracs = cursor.fetchall() or []
        carac_dict = {}
        for row in raw_caracs:
            pid = row.get('produto_id')
            raw = row.get('caracteristicas') or ''
            parts = [p.strip().lower() for p in raw.split(',') if p.strip()]
            seen = set(); uniq = []
            for p in parts:
                if p not in seen:
                    seen.add(p); uniq.append(p)
            carac_dict[pid] = ','.join(uniq)

        for p in produtos:
            pid = p.get('id')
            p['caracteristicas'] = carac_dict.get(pid, '')
            p['imagem_url'] = _normalize_img_path(p.get('imagem_url'))
            p['tipo'] = (p.get('tipo') or 'snack').strip().lower()

        cursor.execute("SELECT id, nome, descricao, preco_total, imagem_url FROM menus ORDER BY nome")
        menus_raw = cursor.fetchall() or []
        for m in menus_raw:
            menus.append({
                'id': m['id'],
                'nome': m['nome'],
                'descricao': m.get('descricao'),
                'preco_total': m.get('preco_total'),
                'imagem_url': _normalize_img_path(m.get('imagem_url'))
            })

    except Exception:
        app.logger.exception("Erro ao buscar /bar:")
        produtos = produtos or []
        menus = menus or []
    finally:
        try: cursor.close()
        except: pass
        try: cnx.close()
        except: pass

    return render_template('bar.html', produtos=produtos, menus=menus)

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

@app.route('/cinemas/<int:cinema_id>/filmes')
def cinema_filmes(cinema_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar informações do cinema (incluindo imagem da BD)
        cursor.execute("""
            SELECT id, nome, localizacao, regiao, imagem
            FROM cinemas
            WHERE id = %s
        """, (cinema_id,))
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
        """, (cinema_id,))
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
            SELECT id, nome, descricao, preco_total as preco, imagem_url
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
            SELECT id, nome, descricao, preco_total as preco, imagem_url
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
        rating = float(rating)
        if rating < 0.5 or rating > 5.0:
            return jsonify({'success': False, 'message': 'Rating deve ser entre 0.5 e 5.0'})
        # Validar que é múltiplo de 0.5
        if (rating * 2) % 1 != 0:
            return jsonify({'success': False, 'message': 'Rating deve ser múltiplo de 0.5'})
    except:
        return jsonify({'success': False, 'message': 'Rating inválido'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se o utilizador já assistiu ao filme (considerando duração)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM reservas r
            JOIN filmes f ON r.filme_id = f.id
            JOIN horarios_sessao hs ON r.sessao_id = hs.id
            JOIN horarios h ON hs.id_horario = h.id
            WHERE r.usuario_id = %s 
            AND r.filme_id = %s
            AND DATE_ADD(CONCAT(r.data_sessao, ' ', h.hora), INTERVAL f.duracao MINUTE) < NOW()
        """, (session['user_id'], filme_id))
        
        result = cursor.fetchone()
        if result[0] == 0:
            return jsonify({'success': False, 'message': 'Só podes avaliar filmes que já assististe completamente!'})
        
        cursor.execute("""
            INSERT INTO avaliacoes_filmes (usuario_id, filme_id, rating, comentario)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            rating = VALUES(rating),
            comentario = VALUES(comentario),
            data_avaliacao = CURRENT_TIMESTAMP
        """, (session['user_id'], filme_id, rating, comentario))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Avaliação salva com sucesso!'})
        
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
    filme_id = data.get('filme_id')
    
    if not filme_id:
        return jsonify({'success': False, 'message': 'ID do filme necessário'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM avaliacoes_filmes 
            WHERE usuario_id = %s AND filme_id = %s
        """, (session['user_id'], filme_id))
        
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
    
    data = request.get_json()
    cinema_id = data.get('cinema_id')
    
    if not cinema_id:
        return jsonify({'success': False, 'message': 'ID do cinema necessário'})
    
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
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
    finally:
        cursor.close()
        conn.close()

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
    
    return render_template('admin_atores.html', atores=atores)

@app.route('/admin/atores/adicionar', methods=['POST'])
def admin_adicionar_ator():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    foto = request.form.get('foto')
    nacionalidade = request.form.get('nacionalidade')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO atores (nome, foto_url, nacionalidade)
        VALUES (%s, %s, %s)
    """, (nome, foto, nacionalidade))
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
    foto = request.form.get('foto')
    nacionalidade = request.form.get('nacionalidade')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE atores
        SET nome = %s, foto_url = %s, nacionalidade = %s
        WHERE id = %s
    """, (nome, foto, nacionalidade, ator_id))
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
    
    # Buscar todos os menus
    cursor.execute("SELECT id, nome, descricao, preco_total, imagem_url FROM menus ORDER BY nome")
    menus = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin_bar.html', produtos=produtos, menus=menus)

@app.route('/admin/bar/produtos/adicionar', methods=['POST'])
def admin_adicionar_produto():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    imagem = request.form.get('imagem')
    tipo = request.form.get('tipo')
    
    # Corrigir caminho da imagem
    if imagem:
        imagem = imagem.replace('\\', '/').replace('"', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bar (produto, preco, imagem_url, tipo)
        VALUES (%s, %s, %s, %s)
    """, (nome, preco, imagem, tipo))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Produto adicionado com sucesso!', 'success')
    return redirect(url_for('admin_bar'))

@app.route('/admin/bar/produtos/editar/<int:produto_id>', methods=['POST'])
def admin_editar_produto(produto_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    imagem = request.form.get('imagem')
    tipo = request.form.get('tipo')
    
    # Corrigir caminho da imagem
    if imagem:
        imagem = imagem.replace('\\', '/').replace('"', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE bar
        SET produto = %s, preco = %s, imagem_url = %s, tipo = %s
        WHERE id = %s
    """, (nome, preco, imagem, tipo, produto_id))
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

@app.route('/admin/bar/menus/adicionar', methods=['POST'])
def admin_adicionar_menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    preco_total = request.form.get('preco_total')
    imagem_url = request.form.get('imagem_url')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO menus (nome, descricao, preco_total, imagem_url)
        VALUES (%s, %s, %s, %s)
    """, (nome, descricao, preco_total, imagem_url))
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
    imagem_url = request.form.get('imagem_url')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE menus
        SET nome = %s, descricao = %s, preco_total = %s, imagem_url = %s
        WHERE id = %s
    """, (nome, descricao, preco_total, imagem_url, menu_id))
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
# ADMIN - GESTÃO DE SALAS
# ==========================
@app.route('/admin/salas')
def admin_salas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Buscar todas as salas com informações do cinema
    cursor.execute("""
        SELECT s.id, s.nome_sala as nome, s.capacidade, s.tipo_sala as tipo, 
               s.id_cinema as cinema_id,
               c.nome as cinema_nome, c.localizacao as cinema_localizacao
        FROM salas s
        INNER JOIN cinemas c ON s.id_cinema = c.id
        ORDER BY s.id DESC
    """)
    salas = cursor.fetchall()
    
    # Buscar cinemas para o formulário
    cursor.execute("SELECT id, nome, localizacao FROM cinemas ORDER BY nome")
    cinemas = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin_salas.html', salas=salas, cinemas=cinemas)

@app.route('/admin/salas/adicionar', methods=['POST'])
def admin_adicionar_sala():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    capacidade = request.form.get('capacidade')
    tipo = request.form.get('tipo')
    cinema_id = request.form.get('cinema_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO salas (nome_sala, capacidade, tipo_sala, id_cinema)
        VALUES (%s, %s, %s, %s)
    """, (nome, capacidade, tipo, cinema_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Sala adicionada com sucesso!', 'success')
    return redirect(url_for('admin_salas'))

@app.route('/admin/salas/editar/<int:sala_id>', methods=['POST'])
def admin_editar_sala(sala_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    capacidade = request.form.get('capacidade')
    tipo = request.form.get('tipo')
    cinema_id = request.form.get('cinema_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE salas
        SET nome_sala = %s, capacidade = %s, tipo_sala = %s, id_cinema = %s
        WHERE id = %s
    """, (nome, capacidade, tipo, cinema_id, sala_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Sala atualizada com sucesso!', 'success')
    return redirect(url_for('admin_salas'))

@app.route('/admin/salas/remover/<int:sala_id>', methods=['POST'])
def admin_remover_sala(sala_id):
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
    
    return render_template('admin_avatares.html', avatares=avatares, categorias=categorias)

@app.route('/admin/avatares/adicionar', methods=['POST'])
def admin_adicionar_avatar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    caminho = request.form.get('caminho')
    categoria_id = request.form.get('categoria_id')
    
    # Corrigir caminho automaticamente
    caminho = caminho.replace('\\', '/').replace('"', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO avatars (nome, caminho, categoria_id) VALUES (%s, %s, %s)", (nome, caminho, categoria_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Avatar adicionado com sucesso!', 'success')
    return redirect(url_for('admin_avatares'))

@app.route('/admin/avatares/editar/<int:avatar_id>', methods=['POST'])
def admin_editar_avatar(avatar_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nome = request.form.get('nome')
    caminho = request.form.get('caminho')
    categoria_id = request.form.get('categoria_id')
    
    # Corrigir caminho automaticamente
    caminho = caminho.replace('\\', '/').replace('"', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
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
    
    return render_template('admin_tipos_sessao.html', tipos=tipos)

@app.route('/admin/tipos-sessao/adicionar', methods=['POST'])
def admin_adicionar_tipo_sessao():
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
def admin_editar_tipo_sessao(tipo_id):
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
def admin_remover_tipo_sessao(tipo_id):
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
        
        # Obter usuario_id logo no início
        usuario_id = session.get('user_id', 0)
        app.logger.info(f"Usuario ID da sessão: {usuario_id}")
        
        # Extrair dados
        horario_id = dados_reserva.get('horario_id')
        cinema_id = dados_reserva.get('cinema_id')

        # DEBUG: Logs para rastrear dados da reserva
        app.logger.info(f"🔍 CONFIRMAR_PAGAMENTO - Dados extraídos:")
        app.logger.info(f"  dados_reserva completos: {dados_reserva}")
        app.logger.info(f"  tipo_id extraído: {dados_reserva.get('tipo_id', 'NÃO ENCONTRADO')}")
        app.logger.info(f"  horario_id: {dados_reserva.get('horario_id', 'NÃO ENCONTRADO')}")
        
        tipo_id = dados_reserva.get('tipo_id')
        filme_id = dados_reserva.get('filme_id')
        filme_nome = dados_reserva.get('filme_nome')  # Para filmes personalizados
        data_sessao = dados_reserva.get('data_sessao')
        hora_sessao = dados_reserva.get('hora_sessao')
        num_pessoas = dados_reserva.get('num_pessoas')
        preco_total = dados_reserva.get('preco_total')
        nome = dados_reserva.get('nome', '').strip() if dados_reserva.get('nome') else ''
        email = dados_reserva.get('email', '').strip() if dados_reserva.get('email') else ''
        telefone = dados_reserva.get('telefone', '').strip() if dados_reserva.get('telefone') else ''
        lugares = dados_reserva.get('lugares', [])
        produtos_bar = dados_reserva.get('produtos_bar', {})
        
        app.logger.info(f"=== DADOS EXTRAÍDOS ===")
        app.logger.info(f"tipo_reserva: {tipo_reserva}")
        app.logger.info(f"tipo_sala: {tipo_sala}")
        app.logger.info(f"horario_id: {horario_id}")
        app.logger.info(f"cinema_id: {cinema_id}")
        app.logger.info(f"tipo_id: {tipo_id}")
        app.logger.info(f"filme_id: {filme_id}")
        app.logger.info(f"filme_nome: {filme_nome}")
        app.logger.info(f"data_sessao: {data_sessao}")
        app.logger.info(f"hora_sessao: {hora_sessao}")
        app.logger.info(f"num_pessoas: {num_pessoas}")
        app.logger.info(f"nome: {nome}")
        app.logger.info(f"email: {email}")
        app.logger.info(f"lugares: {lugares}")
        
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
            campos_obrigatorios = [horario_id, cinema_id, tipo_id, filme_id, nome, email, lugares]
            app.logger.info(f"Validação reserva normal - campos: {campos_obrigatorios}")
            
            if not all(campos_obrigatorios):
                app.logger.error(f"Campos obrigatórios faltando para reserva normal:")
                app.logger.error(f"- horario_id: {horario_id} ({'OK' if horario_id else 'FALTA'})")
                app.logger.error(f"- cinema_id: {cinema_id} ({'OK' if cinema_id else 'FALTA'})")
                app.logger.error(f"- tipo_id: {tipo_id} ({'OK' if tipo_id else 'FALTA'})")
                app.logger.error(f"- filme_id: {filme_id} ({'OK' if filme_id else 'FALTA'})")
                app.logger.error(f"- nome: {nome} ({'OK' if nome else 'FALTA'})")
                app.logger.error(f"- email: {email} ({'OK' if email else 'FALTA'})")
                app.logger.error(f"- lugares: {lugares} ({'OK' if lugares else 'FALTA'})")
                return jsonify({'success': False, 'message': 'Dados da reserva incompletos'}), 400
        
        # Processar reserva diretamente
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            app.logger.info(f"=== PROCESSAMENTO DE PAGAMENTO ===")
            app.logger.info(f"Usuario ID da sessão: {usuario_id}")
            app.logger.info(f"Categoria: {categoria}")
            
            # Se usuário está logado, buscar dados atualizados da base de dados
            if usuario_id > 0:
                app.logger.info(f"🔍 Buscando dados do usuário logado (ID: {usuario_id})")
                cursor.execute("SELECT nome, email FROM usuarios WHERE id = %s", (usuario_id,))
                user_data = cursor.fetchone()
                
                if user_data:
                    nome = user_data['nome'] or nome
                    email = user_data['email'] or email
                    telefone = ''  # Usuários logados não têm telefone na BD
                    app.logger.info(f"✅ Dados do usuário atualizados: nome='{nome}', email='{email}', telefone='{telefone}'")
                else:
                    app.logger.warning(f"⚠️ Usuário ID {usuario_id} não encontrado na base de dados")
            
            app.logger.info(f"Dados finais - nome: '{nome}', email: '{email}', telefone: '{telefone}'")
            
            reserva_ids = []
            
            if tipo_reserva == 'sessao_exclusiva':  # Sessão exclusiva
                app.logger.info(f"=== PROCESSANDO SESSÃO EXCLUSIVA ===")
                
                # Preparar dados do cliente
                nome_cliente = nome if usuario_id == 0 else None
                email_cliente = email if usuario_id == 0 else None
                telefone_cliente = telefone if (usuario_id == 0 and telefone and telefone.strip()) else None
                user_id_final = usuario_id if usuario_id > 0 else None
                
                # Inserir reserva de sessão exclusiva
                try:
                    cursor.execute("""
                        INSERT INTO reservas_exclusivas 
                        (tipo_sala, filme_id, filme_nome, data_sessao, hora_sessao, num_pessoas, 
                         preco_total, usuario_id, nome_cliente, email_cliente, telefone_cliente, reservado_em)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (tipo_sala, filme_id, filme_nome, data_sessao, hora_sessao, num_pessoas, 
                          preco_total, user_id_final, nome_cliente, email_cliente, telefone_cliente))
                    
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
                                filme_id INT NULL,
                                filme_nome VARCHAR(255) NULL,
                                data_sessao DATE NOT NULL,
                                hora_sessao TIME NOT NULL,
                                num_pessoas INT NOT NULL,
                                preco_total DECIMAL(10,2) NOT NULL,
                                usuario_id INT NULL,
                                nome_cliente VARCHAR(255) NULL,
                                email_cliente VARCHAR(255) NULL,
                                telefone_cliente VARCHAR(20) NULL,
                                reservado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                status VARCHAR(20) DEFAULT 'confirmada',
                                FOREIGN KEY (filme_id) REFERENCES filmes(id),
                                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                            )
                        """)
                        
                        # Tentar inserir novamente
                        cursor.execute("""
                            INSERT INTO reservas_exclusivas 
                            (tipo_sala, filme_id, filme_nome, data_sessao, hora_sessao, num_pessoas, 
                             preco_total, usuario_id, nome_cliente, email_cliente, telefone_cliente, reservado_em)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        """, (tipo_sala, filme_id, filme_nome, data_sessao, hora_sessao, num_pessoas, 
                              preco_total, user_id_final, nome_cliente, email_cliente, telefone_cliente))
                        
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
                preco_total_bilhetes = preco_bilhete * len(lugares)
                preco_total_bar = 0
                for produto_id, produto_info in produtos_bar.items():
                    preco_total_bar += float(produto_info.get('preco', 0)) * int(produto_info.get('quantidade', 0))
                preco_total_geral = preco_total_bilhetes + preco_total_bar
                
                # Preparar dados do cliente
                nome_cliente = nome if usuario_id == 0 else None
                email_cliente = email if usuario_id == 0 else None
                telefone_cliente = telefone if (usuario_id == 0 and telefone and telefone.strip()) else None
                
                # Inserir reservas para cada lugar
                for lugar in lugares:
                    try:
                        user_id_final = usuario_id if usuario_id > 0 else None
                        
                        # Tentar inserir com campos de cliente
                        try:
                            cursor.execute("""
                                INSERT INTO reservas (sessao_id, data_sessao, filme_id, cinema_id, tipo_sessao_id, lugar, usuario_id, nome_cliente, email_cliente, telefone_cliente, reservado_em)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                            """, (horario_id, data_sessao, filme_id, cinema_id, tipo_id, lugar, user_id_final, nome_cliente, email_cliente, telefone_cliente))
                        except Exception as e:
                            # Fallback para versão antiga
                            user_id_final = usuario_id if usuario_id > 0 else 1
                            cursor.execute("""
                                INSERT INTO reservas (sessao_id, data_sessao, filme_id, cinema_id, tipo_sessao_id, lugar, usuario_id, reservado_em)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                            """, (horario_id, data_sessao, filme_id, cinema_id, tipo_id, lugar, user_id_final))
                        
                        reserva_id = cursor.lastrowid
                        reserva_ids.append(reserva_id)
                        
                    except Exception as e:
                        app.logger.error(f"Erro ao inserir reserva para lugar {lugar}: {str(e)}")
                        raise
            
            conn.commit()
            app.logger.info(f"✅ Reservas confirmadas com IDs: {reserva_ids}")
            
            # Enviar email de confirmação
            try:
                from datetime import datetime
                data_formatada = datetime.strptime(data_sessao, '%Y-%m-%d').strftime('%d/%m/%Y')
                
                if tipo_reserva == 'sessao_exclusiva':  # Email para sessão exclusiva
                    filme_titulo = filme_nome if filme_nome else 'Filme Personalizado'
                    if filme_id:
                        cursor.execute("SELECT titulo FROM filmes WHERE id = %s", (filme_id,))
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
                    cursor.execute("SELECT titulo FROM filmes WHERE id = %s", (filme_id,))
                    filme = cursor.fetchone()
                    cursor.execute("SELECT nome FROM cinemas WHERE id = %s", (cinema_id,))
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
                    cursor.execute("SELECT hora FROM horarios WHERE id = %s", (horario_id,))
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

# Run (apenas aqui, no fim)
# ==========================
if __name__ == '__main__':
    app.logger.info("Iniciando app; endpoints registados:\n%s", app.url_map)
    app.run(debug=True)
