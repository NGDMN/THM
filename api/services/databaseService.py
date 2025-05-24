import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from ..config.database import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    """Cria uma conexão com o banco de dados PostgreSQL"""
    try:
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

def execute_query(query, params=None):
    """Executa uma query SQL e retorna os resultados como DataFrame"""
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Não foi possível conectar ao banco de dados")
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        logger.error(f"Erro ao executar query: {str(e)}")
        raise

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