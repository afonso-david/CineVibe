# CineVibe - Sistema de Reserva de Bilhetes de Cinema

Projeto Académico - PAP 2026

## Requisitos do Sistema

Antes de começar, certifique-se de ter instalado:

- Python 3.8 ou superior
- MySQL 8.0 ou superior
- Navegador web moderno (Chrome, Firefox, Edge)

## Instalação Passo a Passo

### 1. Preparar o Ambiente Python

Abra o terminal/prompt de comando na pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

### 2. Configurar a Base de Dados

#### 2.1. Criar a Base de Dados

Abra o MySQL Workbench, DBeaver ou outro cliente MySQL e execute:

```sql
CREATE DATABASE cinevibe CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 2.2. Importar os Dados

No mesmo cliente MySQL, importe o ficheiro `cinevibe.sql`:

- MySQL Workbench: File > Run SQL Script > Selecionar `cinevibe.sql`
- DBeaver: Botão direito na base de dados > Execute SQL Script > Selecionar `cinevibe.sql`
- Linha de comandos:
```bash
mysql -u root -p cinevibe < cinevibe.sql
```

### 3. Configurar Credenciais da Base de Dados

Abra o ficheiro `app.py` e localize a função `get_db_connection()` (aproximadamente linha 381).

Altere as credenciais conforme a sua configuração MySQL:

```python
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="A_SUA_SENHA_MYSQL",  # Altere aqui
        database="cinevibe"
    )
```

### 4. Executar a Aplicação

No terminal, execute:

```bash
python app.py
```

A aplicação estará disponível em: `http://127.0.0.1:5000`

## Credenciais de Acesso

Ao executar a aplicação pela primeira vez:

1. Aceda a `http://127.0.0.1:5000/registo`
2. Crie uma conta de utilizador
3. Para tornar a conta em administrador, execute no MySQL:

```sql
UPDATE usuarios SET is_admin = TRUE WHERE email = 'seu_email@exemplo.com';
```

Depois faça login e aceda ao dashboard admin em `/admin`

## Funcionalidades Principais

### Área Pública
- Navegação de filmes em cartaz
- Pesquisa e filtros avançados
- Visualização de detalhes dos filmes
- Informações sobre cinemas
- Sessões temáticas (Vintage, Romance, Terror)
- Funcionalidades de acessibilidade (Audiodescrição, LGP, Legendagem)

### Área de Utilizador
- Reserva de bilhetes com seleção de lugares
- Escolha de produtos do bar (menus, snacks, bebidas, toppings)
- Sistema de recompensas e pontos
- Histórico de reservas
- Gestão de perfil e avatar

### Área de Administração
- Dashboard com estatísticas em tempo real
- Gestão completa de filmes, atores e realizadores
- Gestão de cinemas, salas e horários
- Gestão de produtos do bar
- Gestão de utilizadores e reservas
- Exportação de relatórios

## Estrutura do Projeto

```
cinevibe/
├── app.py                    # Aplicação Flask principal (configurar credenciais MySQL aqui)
├── requirements.txt          # Dependências Python
├── cinevibe.sql             # Base de dados completa
├── static/
│   ├── css/                 # Ficheiros CSS
│   ├── js/                  # Ficheiros JavaScript
│   ├── imgs/                # Imagens e recursos
│   └── Vídeos/              # Vídeos promocionais
└── templates/               # Templates HTML
```

## Resolução de Problemas

### Erro de Conexão à Base de Dados
- Verifique se o MySQL está a correr
- Confirme as credenciais no ficheiro `app.py` (função `get_db_connection`)
- Certifique-se que a base de dados `cinevibe` foi criada

### Erro ao Importar cinevibe.sql
- Verifique se tem permissões suficientes
- Certifique-se que está a usar MySQL 8.0+
- Tente importar em partes menores se o ficheiro for muito grande

### Porta 5000 já em uso
- Altere a porta no final do ficheiro `app.py`:
```python
app.run(debug=True, port=5001)
```

### Módulos Python em falta
- Execute novamente: `pip install -r requirements.txt`
- Verifique se está a usar Python 3.8+

## Tecnologias Utilizadas

- Backend: Python 3, Flask
- Base de Dados: MySQL 8
- Frontend: HTML5, CSS3, JavaScript
- Gráficos: Chart.js
- Ícones: Font Awesome
- Fontes: Google Fonts (Inter, Montserrat, Roboto)



Desenvolvido como Prova de Aptidão Profissional - 2026
