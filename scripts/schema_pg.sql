-- SCHEMA UNIFICADO PARA PRODUÇÃO - SISTEMA DE PREVISÃO DE ALAGAMENTOS RJ/SP

-- Tabela de previsões meteorológicas
CREATE TABLE IF NOT EXISTS previsoes (
    id SERIAL PRIMARY KEY,
    cidade VARCHAR(100) NOT NULL,
    estado VARCHAR(2) NOT NULL,
    data DATE NOT NULL,
    precipitacao NUMERIC(6,2),
    temp_min NUMERIC(5,2),
    temp_max NUMERIC(5,2),
    umidade INTEGER,
    descricao VARCHAR(200),
    icone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_previsao UNIQUE (cidade, estado, data)
);

CREATE INDEX IF NOT EXISTS idx_previsoes_cidade ON previsoes(cidade);
CREATE INDEX IF NOT EXISTS idx_previsoes_data ON previsoes(data);
CREATE INDEX IF NOT EXISTS idx_previsoes_estado ON previsoes(estado);

-- Tabela de chuvas diárias
CREATE TABLE IF NOT EXISTS chuvas_diarias (
    id SERIAL PRIMARY KEY,
    municipio VARCHAR(100) NOT NULL,
    estado VARCHAR(2) NOT NULL,
    data DATE NOT NULL,
    precipitacao_diaria NUMERIC(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_chuva_diaria UNIQUE (municipio, estado, data)
);

CREATE INDEX IF NOT EXISTS idx_chuva_data ON chuvas_diarias(data);
CREATE INDEX IF NOT EXISTS idx_chuva_cidade ON chuvas_diarias(municipio);
CREATE INDEX IF NOT EXISTS idx_chuva_estado ON chuvas_diarias(estado);

-- Tabela de alagamentos
CREATE TABLE IF NOT EXISTS alagamentos (
    id SERIAL PRIMARY KEY,
    municipio VARCHAR(100) NOT NULL,
    estado VARCHAR(2) NOT NULL,
    data DATE NOT NULL,
    local VARCHAR(200),
    dh_mortos INTEGER,
    dh_afetados INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_alagamento UNIQUE (municipio, estado, data, local)
);

CREATE INDEX IF NOT EXISTS idx_alag_data ON alagamentos(data);
CREATE INDEX IF NOT EXISTS idx_alag_cidade ON alagamentos(municipio);
CREATE INDEX IF NOT EXISTS idx_alag_estado ON alagamentos(estado);
CREATE INDEX IF NOT EXISTS idx_alag_local ON alagamentos(local);

-- Função para atualizar o campo updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualizar o campo updated_at
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_previsoes_updated_at') THEN
        CREATE TRIGGER update_previsoes_updated_at
        BEFORE UPDATE ON previsoes
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_chuvas_diarias_updated_at') THEN
        CREATE TRIGGER update_chuvas_diarias_updated_at
        BEFORE UPDATE ON chuvas_diarias
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_alagamentos_updated_at') THEN
        CREATE TRIGGER update_alagamentos_updated_at
        BEFORE UPDATE ON alagamentos
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    END IF;
END$$; 