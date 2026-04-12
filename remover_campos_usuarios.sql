-- Script para remover campos inúteis da tabela usuarios
-- Execute este script na base de dados cinevibe

USE cinevibe;

-- Remover campo tipo_usuario (não é usado para lógica de negócio)
ALTER TABLE usuarios DROP COLUMN tipo_usuario;

-- Remover campo biografia (nunca é lido, apenas UPDATE sem SELECT)
ALTER TABLE usuarios DROP COLUMN biografia;

-- Remover campo filme_favorito_id (nunca é lido, apenas UPDATE sem SELECT)
ALTER TABLE usuarios DROP COLUMN filme_favorito_id;

-- Remover campo avatar (upload personalizado não existe no frontend)
ALTER TABLE usuarios DROP COLUMN avatar;

-- Remover campo avatar_personalizado (campo duplicado e inútil)
ALTER TABLE usuarios DROP COLUMN avatar_personalizado;

-- Verificar estrutura final da tabela
-- Campos restantes: id, nome, email, senha, criado_em, ultimo_login, avatar_id, social_provider, social_id, is_admin
DESCRIBE usuarios;
