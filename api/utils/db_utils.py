import os
import pandas as pd
from contextlib import contextmanager
from ..config import DB_CONFIG, USE_MOCK_DATA

# Flag para verificar se psycopg2 está disponível
PSYCOPG2_AVAILABLE = False

# Tentar importar psycopg2, mas não falhar se não estiver disponível
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    print("psycopg2 não está disponível. Usando dados simulados.")

def get_db_connection():
    """
    Cria uma nova conexão com o banco de dados PostgreSQL
    
    Returns:
        connection: Conexão com o banco ou None se houver erro
    """
    if not PSYCOPG2_AVAILABLE or USE_MOCK_DATA:
        print("Usando dados simulados em vez de acessar o banco de dados.")
        return None
        
    try:
        connection = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {str(e)}")
        return None

def execute_query(query, params=None):
    """
    Executa uma query SQL e retorna os resultados como DataFrame
    
    Args:
        query (str): Query SQL a ser executada
        params (dict): Parâmetros para a query
        
    Returns:
        DataFrame: Resultados da query
    """
    try:
        print(f"[DEBUG] Executando query: {query}")
        print(f"[DEBUG] Parâmetros: {params}")
        
        conn = get_db_connection()
        if not conn:
            print("[DEBUG] Erro: Não foi possível conectar ao banco de dados")
            return pd.DataFrame()
        
        # Usar pandas para executar a query e retornar DataFrame
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        print(f"[DEBUG] Query executada com sucesso. Registros retornados: {len(df)}")
        return df
        
    except Exception as e:
        print(f"[DEBUG] Erro ao executar query: {str(e)}")
        return pd.DataFrame()

def execute_dml(query, params=None):
    """
    Executa operações DML (INSERT, UPDATE, DELETE) no banco de dados.
    
    Args:
        query (str): Query SQL a ser executada
        params (dict ou list, optional): Parâmetros para a query. Defaults to None.
        
    Returns:
        int: Número de linhas afetadas ou 0 em caso de erro/simulação
    """
    # Se psycopg2 não estiver disponível ou estiver em modo simulação, retornar 0
    if not PSYCOPG2_AVAILABLE or USE_MOCK_DATA:
        print("Usando dados simulados em vez de acessar o banco de dados.")
        return 0
        
    try:
        conn = get_db_connection()
        if not conn:
            print("Erro: Não foi possível conectar ao banco de dados")
            return 0
        
        cursor = conn.cursor()
        
        if params:
            if isinstance(params, list):
                cursor.executemany(query, params)
            else:
                cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        rows_affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        return rows_affected
        
    except Exception as e:
        print(f"Erro ao executar operação DML: {str(e)}")
        return 0
