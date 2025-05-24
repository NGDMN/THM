import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from ..config import DB_CONFIG, USE_MOCK_DATA
import logging
import json
import os

logger = logging.getLogger(__name__)

def get_db_connection():
    """Cria uma conexão com o banco de dados PostgreSQL"""
    try:
        # Verificar se as configurações do banco estão presentes
        required_configs = ['dbname', 'user', 'password', 'host', 'port']
        missing_configs = [config for config in required_configs if not DB_CONFIG.get(config)]
        
        if missing_configs:
            raise Exception(f"Configurações do banco de dados ausentes: {', '.join(missing_configs)}")
        
        conn = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        return None

def get_mock_data(query_name):
    """Carrega dados mockados do arquivo JSON"""
    try:
        mock_file = os.path.join(os.path.dirname(__file__), '..', 'mock', f'{query_name}.json')
        if os.path.exists(mock_file):
            with open(mock_file, 'r') as f:
                return pd.DataFrame(json.load(f))
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Erro ao carregar dados mockados: {str(e)}")
        return pd.DataFrame()

def execute_query(query, params=None):
    """Executa uma query SQL e retorna os resultados como DataFrame"""
    try:
        # Se estiver em modo de desenvolvimento e USE_MOCK_DATA for True
        if USE_MOCK_DATA:
            logger.info("Usando dados mockados")
            return get_mock_data('previsoes')
        
        conn = get_db_connection()
        if not conn:
            logger.error("Não foi possível conectar ao banco de dados")
            return get_mock_data('previsoes')
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        logger.error(f"Erro ao executar query: {str(e)}")
        return get_mock_data('previsoes')

def execute_dml(query, params=None):
    """Executa operações DML (INSERT, UPDATE, DELETE) no banco de dados"""
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Não foi possível conectar ao banco de dados")
        
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        rows_affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        return rows_affected
    except Exception as e:
        logger.error(f"Erro ao executar operação DML: {str(e)}")
        raise 