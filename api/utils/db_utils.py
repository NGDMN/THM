import os
import pandas as pd
from contextlib import contextmanager
from ..config import DB_CONFIG, TNS_ADMIN, USE_MOCK_DATA

# Flag para verificar se cx_Oracle está disponível
CX_ORACLE_AVAILABLE = False

# Tentar importar cx_Oracle, mas não falhar se não estiver disponível
try:
    import cx_Oracle
    CX_ORACLE_AVAILABLE = True
    
    # Configurar o ambiente Oracle apenas se cx_Oracle estiver disponível
    if TNS_ADMIN:
        os.environ['TNS_ADMIN'] = TNS_ADMIN
except ImportError:
    print("cx_Oracle não está disponível. Usando dados simulados.")

@contextmanager
def get_connection():
    """
    Gerenciador de contexto para obter uma conexão com o banco Oracle
    e garantir seu fechamento após o uso.
    """
    if not CX_ORACLE_AVAILABLE or USE_MOCK_DATA:
        # Se o cx_Oracle não estiver disponível, retornar None
        # O código que usa esta função deve estar preparado para lidar com isso
        yield None
        return
        
    connection = None
    try:
        connection = cx_Oracle.connect(
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            dsn=DB_CONFIG['dsn'],
            encoding=DB_CONFIG['encoding']
        )
        yield connection
    except Exception as e:
        print(f"Erro ao conectar ao Oracle Database: {str(e)}")
        yield None
    finally:
        if connection:
            connection.close()

def execute_query(query, params=None):
    """
    Executa uma consulta SELECT no banco de dados e retorna os resultados como DataFrame.
    
    Args:
        query (str): Query SQL a ser executada
        params (dict, optional): Parâmetros para a query. Defaults to None.
        
    Returns:
        pd.DataFrame: Resultados da consulta ou DataFrame vazio em caso de erro/simulação
    """
    # Se cx_Oracle não estiver disponível ou estiver em modo simulação, retornar DataFrame vazio
    if not CX_ORACLE_AVAILABLE or USE_MOCK_DATA:
        print("Usando dados simulados em vez de acessar o banco de dados.")
        return pd.DataFrame()
        
    try:
        with get_connection() as connection:
            if connection is None:
                return pd.DataFrame()
                
            if params:
                df = pd.read_sql(query, connection, params=params)
            else:
                df = pd.read_sql(query, connection)
            return df
    except Exception as e:
        print(f"Erro ao executar query: {str(e)}")
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
    # Se cx_Oracle não estiver disponível ou estiver em modo simulação, retornar 0
    if not CX_ORACLE_AVAILABLE or USE_MOCK_DATA:
        print("Usando dados simulados em vez de acessar o banco de dados.")
        return 0
        
    try:
        with get_connection() as connection:
            if connection is None:
                return 0
                
            cursor = connection.cursor()
            if params:
                if isinstance(params, list):
                    cursor.executemany(query, params)
                else:
                    cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows_affected = cursor.rowcount
            connection.commit()
            return rows_affected
    except Exception as e:
        print(f"Erro ao executar operação DML: {str(e)}")
        return 0 