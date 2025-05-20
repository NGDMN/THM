-- Dropar tabelas se existirem
DROP TABLE IF EXISTS chuvas_diarias CASCADE;
DROP TABLE IF EXISTS alagamentos CASCADE;

-- Criar tabela de chuvas diárias
CREATE TABLE chuvas_diarias (
    id SERIAL PRIMARY KEY,
    municipio VARCHAR(100) NOT NULL,
    estado VARCHAR(2) NOT NULL,
    data DATE NOT NULL,
    precipitacao_diaria FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Adicionar restrição de unicidade
ALTER TABLE chuvas_diarias 
    ADD CONSTRAINT chuvas_diarias_municipio_estado_data_key 
    UNIQUE (municipio, estado, data);

-- Criar tabela de alagamentos
CREATE TABLE alagamentos (
    id SERIAL PRIMARY KEY,
    municipio VARCHAR(100) NOT NULL,
    estado VARCHAR(2) NOT NULL,
    data DATE NOT NULL,
    local VARCHAR(255),
    dh_mortos INTEGER DEFAULT 0,
    dh_afetados INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Adicionar restrição de unicidade para alagamentos
ALTER TABLE alagamentos 
    ADD CONSTRAINT alagamentos_municipio_estado_data_key 
    UNIQUE (municipio, estado, data);

-- Criar função para atualizar o timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar triggers para atualizar o timestamp
CREATE TRIGGER update_chuvas_diarias_updated_at
    BEFORE UPDATE ON chuvas_diarias
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alagamentos_updated_at
    BEFORE UPDATE ON alagamentos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 