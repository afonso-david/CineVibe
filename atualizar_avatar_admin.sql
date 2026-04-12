-- Script para adicionar avatar especial do Admin
-- Execute este script na base de dados cinevibe

USE cinevibe;

-- 1. Adicionar o avatar do admin à tabela avatars
-- Categoria 1 = Super Heróis (ou cria uma categoria especial se preferires)
INSERT INTO avatars (nome, caminho, categoria_id) 
VALUES ('Admin CineVibe', 'imgs/Logo/perfil.png', 1);

-- 2. Obter o ID do avatar recém-criado e atualizar o admin
SET @avatar_admin_id = LAST_INSERT_ID();

-- 3. Atualizar o utilizador admin (ID 13) para usar este avatar
UPDATE usuarios 
SET avatar_id = @avatar_admin_id
WHERE id = 13;

-- 4. Verificar a atualização
SELECT u.id, u.nome, u.email, u.avatar_id, a.caminho as avatar_path
FROM usuarios u
LEFT JOIN avatars a ON u.avatar_id = a.id
WHERE u.id = 13;
