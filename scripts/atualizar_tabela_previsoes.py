#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para atualizar a tabela de previsões no PostgreSQL, adicionando colunas de risco
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

def atualizar_tabela_previsoes():
    """
    Atualiza a tabela previsoes para adicionar colunas de risco de alagamento
    """
    try:
        if USE_MOCK_DATA:
            logger.warning("Modo de simulação ativo. Não será atualizada a tabela no banco.")
            return False
        
        # Conectar ao banco de dados
        setup_database_connection()
        
        with get_connection() as conn:
            if conn is None:
                logger.error("Não foi possível conectar ao banco de dados")
                return False
            
            cursor = conn.cursor()
            
            # Script SQL para adicionar novas colunas se não existirem
            sql_update_table = """
            DO $$
            BEGIN
                -- Verificar e adicionar coluna para probabilidade de alagamento
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'previsoes' 
                              AND column_name = 'probabilidade_alagamento') THEN
                    ALTER TABLE previsoes ADD COLUMN probabilidade_alagamento NUMERIC(4,2) DEFAULT 0;
                END IF;
                
                -- Verificar e adicionar coluna para nível de risco
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'previsoes' 
                              AND column_name = 'nivel_risco') THEN
                    ALTER TABLE previsoes ADD COLUMN nivel_risco VARCHAR(10) DEFAULT 'baixo';
                END IF;
                
                -- Verificar e adicionar coluna para número estimado de afetados
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'previsoes' 
                              AND column_name = 'afetados_estimados') THEN
                    ALTER TABLE previsoes ADD COLUMN afetados_estimados INTEGER DEFAULT 0;
                END IF;
            END
            $$;
            
            -- Verificar e adicionar índice para probabilidade
            CREATE INDEX IF NOT EXISTS idx_previsoes_probabilidade 
            ON previsoes (probabilidade_alagamento);
            """
            
            cursor.execute(sql_update_table)
            conn.commit()
            logger.info("Tabela 'previsoes' atualizada com sucesso!")
            
            # Fechar conexão
            cursor.close()
            close_database_connection()
            return True
            
    except Exception as e:
        logger.error(f"Erro ao atualizar tabela de previsões: {str(e)}")
        return False

if __name__ == "__main__":
    if atualizar_tabela_previsoes():
        logger.info("Tabela atualizada com sucesso!")
    else:
        logger.error("Não foi possível atualizar a tabela.") 