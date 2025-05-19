#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para criar a tabela de previsões no PostgreSQL
"""

import os
import sys
import logging

# Adicionar diretório raiz ao path para importar módulos da API
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.utils.db_utils import setup_database_connection, close_database_connection, get_connection
from api.config import USE_MOCK_DATA

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def criar_tabela_previsoes():
    """
    Cria a tabela previsoes no banco de dados PostgreSQL
    """
    try:
        if USE_MOCK_DATA:
            logger.warning("Modo de simulação ativo. Não será criada a tabela no banco.")
            return False
        
        # Conectar ao banco de dados
        setup_database_connection()
        
        with get_connection() as conn:
            if conn is None:
                logger.error("Não foi possível conectar ao banco de dados")
                return False
            
            cursor = conn.cursor()
            
            # Criar a tabela se não existir
            sql_create_table = """
            CREATE TABLE IF NOT EXISTS previsoes (
                id SERIAL PRIMARY KEY,
                cidade VARCHAR(100) NOT NULL,
                estado VARCHAR(2) NOT NULL,
                data DATE NOT NULL,
                temp_min NUMERIC(5,2),
                temp_max NUMERIC(5,2),
                precipitacao NUMERIC(6,2),
                umidade INTEGER,
                descricao VARCHAR(200),
                icone VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_previsao UNIQUE (cidade, estado, data)
            );
            
            -- Adicionar índices para melhorar performance
            CREATE INDEX IF NOT EXISTS idx_previsoes_cidade ON previsoes(cidade);
            CREATE INDEX IF NOT EXISTS idx_previsoes_data ON previsoes(data);
            CREATE INDEX IF NOT EXISTS idx_previsoes_estado ON previsoes(estado);
            """
            
            cursor.execute(sql_create_table)
            conn.commit()
            logger.info("Tabela 'previsoes' criada ou já existente com sucesso!")
            
            # Fechar conexão
            cursor.close()
            close_database_connection()
            return True
            
    except Exception as e:
        logger.error(f"Erro ao criar tabela de previsões: {str(e)}")
        return False

if __name__ == "__main__":
    if criar_tabela_previsoes():
        logger.info("Tabela criada com sucesso!")
    else:
        logger.error("Não foi possível criar a tabela.") 