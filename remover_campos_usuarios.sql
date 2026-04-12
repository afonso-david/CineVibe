-- Script para remover campos inúteis da tabela usuarios
-- Execute este script na base de dados cinevibe

USE cinevibe;

-- Remover campo tipo_usuario (não é usado para lógica de negócio)
ALTER TABLE usuarios DROP COLUMN tipo_usuario;

-- Remover campo biografia (nunca é lido, apenas UPDATE sem SELECT)
ALTER TABLE usuarios DROP COLUMN biografia;

-- Remover campo filme_favorito_id (nunca é lido, apenas UPDATE sem SELECT)
ALTER TABLE usuarios DROP COLUMN filme_favorito_id;

-- Verificar estrutura final da tabela
DESCRIBE usuarios;
