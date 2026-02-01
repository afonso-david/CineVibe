CREATE DATABASE CineVibe;
USE CineVibe;

-- =========================
-- Tabela Filmes
-- =========================
CREATE TABLE filmes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    sinopse TEXT,
    diretor VARCHAR(100),
    data_lancamento DATE,
    duracao INT,              -- duração em minutos
    classificacao VARCHAR(10),
    poster_url VARCHAR(255),
    trailer_url VARCHAR(255)
);

-- =========================
-- Tabela Géneros
-- =========================
CREATE TABLE generos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL
);

-- Relação N:N Filme-Género
CREATE TABLE filme_generos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filme_id INT,
    genero_id INT,
    FOREIGN KEY (filme_id) REFERENCES filmes(id),
    FOREIGN KEY (genero_id) REFERENCES generos(id)
);

-- =========================
-- Tabela Atores
-- =========================
CREATE TABLE atores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    data_nascimento DATE,
    nacionalidade VARCHAR(50)
);

-- Relação N:N Filme-Atores
CREATE TABLE filme_atores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filme_id INT,
    ator_id INT,
    papel VARCHAR(100),
    FOREIGN KEY (filme_id) REFERENCES filmes(id),
    FOREIGN KEY (ator_id) REFERENCES atores(id)
);

-- =========================
-- Tabela Salas
-- =========================
CREATE TABLE salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50),
    capacidade INT,
    tipo_sala ENUM('normal','IMAX','4DX') DEFAULT 'normal'
);

-- =========================
-- Tabela Lugares
-- =========================
CREATE TABLE lugares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sala_id INT,
    numero VARCHAR(10),
    tipo ENUM('normal','PMR','VIP','casal') DEFAULT 'normal',
    FOREIGN KEY (sala_id) REFERENCES salas(id)
);

-- =========================
-- Tabela Sessões
-- =========================
CREATE TABLE sessoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filme_id INT,
    sala_id INT,
    data DATE,
    hora TIME,
    tipo_sessao ENUM('2D','3D','IMAX','4DX') DEFAULT '2D',
    lugares_totais INT,
    lugares_ocupados INT DEFAULT 0,
    FOREIGN KEY (filme_id) REFERENCES filmes(id),
    FOREIGN KEY (sala_id) REFERENCES salas(id)
);

-- =========================
-- Tabela Utilizadores
-- =========================
CREATE TABLE utilizadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    tipo ENUM('user','admin') DEFAULT 'user',
    pontos INT DEFAULT 0,
    cliente BOOLEAN DEFAULT FALSE,
    tipo_subscricao ENUM('nenhuma','basico','premium','vip') DEFAULT 'nenhuma'
);

-- =========================
-- Tabela Subscrições
-- =========================
CREATE TABLE subscricoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_subscricao VARCHAR(50),
    desconto DECIMAL(5,2),
    pontos_por_euro INT,
    validade INT -- em dias
);

-- =========================
-- Tabela Histórico de Pontos
-- =========================
CREATE TABLE pontos_movimentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilizador_id INT,
    pontos INT,
    motivo VARCHAR(255),
    data_movimento DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id)
);

-- =========================
-- Tabela Bilhetes
-- =========================
CREATE TABLE bilhetes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilizador_id INT,
    sessao_id INT,
    lugar_id INT,
    estado ENUM('reservado','pago','cancelado') DEFAULT 'pago',
    codigo_qr VARCHAR(255),
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id),
    FOREIGN KEY (sessao_id) REFERENCES sessoes(id),
    FOREIGN KEY (lugar_id) REFERENCES lugares(id)
);

-- =========================
-- Tabela Reservas de Salas
-- =========================
CREATE TABLE reservas_salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilizador_id INT,
    sala_id INT,
    data DATE,
    hora TIME,
    descricao_evento TEXT,
    convidados INT,
    estado ENUM('pendente','confirmada','cancelada') DEFAULT 'pendente',
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id),
    FOREIGN KEY (sala_id) REFERENCES salas(id)
);

-- =========================
-- Tabela Bar e Compras
-- =========================
CREATE TABLE bar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto VARCHAR(100),
    preco DECIMAL(5,2)
);

CREATE TABLE compras_bar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilizador_id INT,
    produto_id INT,
    sessao_id INT,
    quantidade INT,
    preco_unitario DECIMAL(5,2),
    data_compra DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id),
    FOREIGN KEY (produto_id) REFERENCES bar(id),
    FOREIGN KEY (sessao_id) REFERENCES sessoes(id)
);

-- =========================
-- Tabela Avaliações internas
-- =========================
CREATE TABLE avaliacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filme_id INT,
    utilizador_id INT,
    nota INT,                       -- 1 a 10
    comentario TEXT,
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filme_id) REFERENCES filmes(id),
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id)
);

-- =========================
-- Tabela Avaliações externas (cache Rotten Tomatoes, IMDB)
-- =========================
CREATE TABLE avaliacoes_externas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filme_id INT,
    fonte VARCHAR(50),             -- 'Rotten Tomatoes', 'IMDB'
    pontuacao INT,
    review_count INT,
    data_atualizacao DATETIME,
    FOREIGN KEY (filme_id) REFERENCES filmes(id)
);

-- =========================
-- Histórico de filmes vistos
-- =========================
CREATE TABLE historico_filmes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilizador_id INT,
    filme_id INT,
    data_visualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id),
    FOREIGN KEY (filme_id) REFERENCES filmes(id)
);

-- =========================
-- Promoções
-- =========================
CREATE TABLE promocoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao TEXT,
    desconto DECIMAL(5,2),
    data_inicio DATE,
    data_fim DATE,
    tipo ENUM('bilhete','bar','subscricao')
);
