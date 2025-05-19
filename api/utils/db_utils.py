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

# Variável global para armazenar a conexão
_connection = None

def setup_database_connection():
    """
    Estabelece uma conexão com o banco de dados PostgreSQL.
    Esta função deve ser chamada no início do script para configurar a conexão.
    
    Returns:
        bool: True se a conexão foi estabelecida com sucesso, False caso contrário.
    """
    global _connection
    
    if not PSYCOPG2_AVAILABLE or USE_MOCK_DATA:
        print("Usando dados simulados em vez de acessar o banco de dados.")
        return False
        
    try:
        _connection = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        print("Conexão com o banco de dados estabelecida com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {str(e)}")
        return False

def close_database_connection():
    """
    Fecha a conexão com o banco de dados PostgreSQL.
    Esta função deve ser chamada no final do script para liberar recursos.
    
    Returns:
        bool: True se a conexão foi fechada com sucesso, False caso contrário.
    """
    global _connection
    
    if _connection:
        try:
            _connection.close()
            _connection = None
            print("Conexão com o banco de dados fechada com sucesso.")
            return True
        except Exception as e:
            print(f"Erro ao fechar conexão com PostgreSQL: {str(e)}")
            return False
    
    return True  # Não há conexão para fechar

@contextmanager
def get_connection():
    """
    Gerenciador de contexto para obter uma conexão com o banco PostgreSQL
    e garantir seu fechamento após o uso.
    """
    if not PSYCOPG2_AVAILABLE or USE_MOCK_DATA:
        # Se o psycopg2 não estiver disponível, retornar None
        # O código que usa esta função deve estar preparado para lidar com isso
        yield None
        return
        
    # Usar a conexão global se disponível
    global _connection
    if _connection:
        yield _connection
        return
        
    connection = None
    try:
        connection = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        yield connection
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {str(e)}")
        yield None
    finally:
        if connection and connection != _connection:
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
    # Se psycopg2 não estiver disponível ou estiver em modo simulação, retornar DataFrame vazio
    if not PSYCOPG2_AVAILABLE or USE_MOCK_DATA:
        print("Usando dados simulados em vez de acessar o banco de dados.")
        return pd.DataFrame()
        
    try:
        with get_connection() as connection:
            if connection is None:
                return pd.DataFrame()
            
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            # Converter resultado para DataFrame
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            
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
    # Se psycopg2 não estiver disponível ou estiver em modo simulação, retornar 0
    if not PSYCOPG2_AVAILABLE or USE_MOCK_DATA:
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