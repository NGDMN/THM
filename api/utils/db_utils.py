import os
import cx_Oracle
import pandas as pd
from contextlib import contextmanager
from api.config import DB_CONFIG, TNS_ADMIN

# Configurar o ambiente Oracle
if TNS_ADMIN:
    os.environ['TNS_ADMIN'] = TNS_ADMIN

@contextmanager
def get_connection():
    """
    Gerenciador de contexto para obter uma conexão com o banco Oracle
    e garantir seu fechamento após o uso.
    """
    connection = None
    try:
        connection = cx_Oracle.connect(
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            dsn=DB_CONFIG['dsn'],
            encoding=DB_CONFIG['encoding']
        )
        yield connection
    except cx_Oracle.Error as e:
        error, = e.args
        print(f"Erro ao conectar ao Oracle Database: {error.message}")
        raise
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
        pd.DataFrame: Resultados da consulta
    """
    try:
        with get_connection() as connection:
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
        int: Número de linhas afetadas
    """
    try:
        with get_connection() as connection:
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