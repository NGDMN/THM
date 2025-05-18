-- Criação das tabelas para o sistema THM no PostgreSQL

-- Tabela de chuvas diárias
CREATE TABLE IF NOT EXISTS chuvas_diarias (
    id SERIAL PRIMARY KEY,
    municipio VARCHAR(100) NOT NULL,
    estado CHAR(2) NOT NULL,
    data DATE NOT NULL,
    precipitacao_diaria NUMERIC(6,2) NOT NULL DEFAULT 0,
    fonte VARCHAR(100),
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_chuva_cidade_data UNIQUE (municipio, data)
);

-- Índices para melhorar performance de consultas frequentes
CREATE INDEX IF NOT EXISTS idx_chuva_data ON chuvas_diarias(data);
CREATE INDEX IF NOT EXISTS idx_chuva_cidade ON chuvas_diarias(municipio);

-- Tabela de alagamentos
CREATE TABLE IF NOT EXISTS alagamentos (
    id SERIAL PRIMARY KEY,
    municipio VARCHAR(100) NOT NULL,
    estado CHAR(2) NOT NULL,
    data DATE NOT NULL,
    local VARCHAR(200),
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    nivel_gravidade VARCHAR(20),
    dh_mortos INTEGER DEFAULT 0,
    dh_afetados INTEGER DEFAULT 0,
    descricao TEXT,
    fonte VARCHAR(100),
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhorar performance de consultas frequentes
CREATE INDEX IF NOT EXISTS idx_alag_data ON alagamentos(data);
CREATE INDEX IF NOT EXISTS idx_alag_cidade ON alagamentos(municipio);
CREATE INDEX IF NOT EXISTS idx_alag_local ON alagamentos(local);

-- Tabela para configuração do sistema
CREATE TABLE IF NOT EXISTS configuracao_sistema (
    id SERIAL PRIMARY KEY,
    chave VARCHAR(50) NOT NULL UNIQUE,
    valor TEXT,
    descricao TEXT,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir configurações iniciais
INSERT INTO configuracao_sistema (chave, valor, descricao)
VALUES 
    ('INTERVALO_ATUALIZACAO', '24', 'Intervalo em horas para atualização dos dados de previsão'),
    ('FONTE_DADOS_CHUVA', 'API_CLIMATEMPO', 'Fonte de dados para previsão de chuvas'),
    ('LIMIAR_ALERTA', '30', 'Precipitação em mm/dia para emitir alerta de alagamento'),
    ('USA_DADOS_SIMULADOS', 'false', 'Indica se o sistema deve usar dados simulados quando não há dados reais')
ON CONFLICT (chave) DO NOTHING;

-- Função para atualizar automaticamente a data de atualização
CREATE OR REPLACE FUNCTION update_data_atualizacao()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_atualizacao = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualizar data_atualizacao quando os registros são modificados
CREATE TRIGGER update_chuvas_diarias_data_atualizacao
BEFORE UPDATE ON chuvas_diarias
FOR EACH ROW EXECUTE FUNCTION update_data_atualizacao();

CREATE TRIGGER update_configuracao_sistema_data_atualizacao
BEFORE UPDATE ON configuracao_sistema
FOR EACH ROW EXECUTE FUNCTION update_data_atualizacao(); 