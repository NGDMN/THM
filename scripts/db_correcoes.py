#!/usr/bin/env python3
"""
Script para corrigir problemas identificados no banco de dados
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import random

# Configuração do banco
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def corrigir_constraint_previsoes():
    """Corrige a constraint UNIQUE na tabela previsoes"""
    print("🔧 Corrigindo constraint UNIQUE na tabela previsoes...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Remover constraint existente se houver
        cursor.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'unique_previsao'
                ) THEN
                    ALTER TABLE previsoes DROP CONSTRAINT unique_previsao;
                END IF;
            END $$;
        """)
        
        # Adicionar nova constraint com ON CONFLICT
        cursor.execute("""
            ALTER TABLE previsoes 
            ADD CONSTRAINT unique_previsao 
            UNIQUE (cidade, estado, data);
        """)
        
        conn.commit()
        print("✅ Constraint corrigida com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir constraint: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def create_missing_tables():
    """Cria tabelas que podem estar faltando"""
    print("🔧 Criando tabelas faltantes...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Tabela de previsões
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS previsoes (
                id SERIAL PRIMARY KEY,
                cidade VARCHAR(100) NOT NULL,
                estado CHAR(2) NOT NULL,
                data DATE NOT NULL,
                precipitacao DECIMAL(5,2),
                temp_min DECIMAL(4,1),
                temp_max DECIMAL(4,1),
                umidade INTEGER,
                descricao VARCHAR(200),
                icone VARCHAR(50),
                probabilidade_alagamento DECIMAL(4,2) DEFAULT 0,
                nivel_risco VARCHAR(10) DEFAULT 'baixo',
                afetados_estimados INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cidade, estado, data)
            )
        """)
        
        # Tabela de chuvas diárias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chuvas_diarias (
                id SERIAL PRIMARY KEY,
                municipio VARCHAR(100) NOT NULL,
                estado CHAR(2) NOT NULL,
                data DATE NOT NULL,
                precipitacao_diaria DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(municipio, estado, data)
            )
        """)
        
        # Tabela de alagamentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alagamentos (
                id SERIAL PRIMARY KEY,
                municipio VARCHAR(100) NOT NULL,
                estado CHAR(2) NOT NULL,
                data DATE NOT NULL,
                local VARCHAR(200),
                dh_mortos INTEGER DEFAULT 0,
                dh_afetados INTEGER DEFAULT 0,
                latitude DECIMAL(10,8),
                longitude DECIMAL(11,8),
                nivel_gravidade VARCHAR(20) DEFAULT 'médio',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de configuração do sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracao_sistema (
                id SERIAL PRIMARY KEY,
                chave VARCHAR(100) UNIQUE NOT NULL,
                valor TEXT,
                descricao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Tabelas criadas/verificadas com sucesso!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def insert_sample_data():
    """Insere dados de exemplo para teste"""
    print("📊 Inserindo dados de exemplo...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Cidades principais para inserir dados
        cities = [
            ('Rio de Janeiro', 'RJ'),
            ('Niterói', 'RJ'),
            ('Angra dos Reis', 'RJ'),
            ('São Paulo', 'SP'),
            ('Santos', 'SP'),
            ('Campinas', 'SP')
        ]
        
        # Inserir previsões para os próximos 7 dias
        today = datetime.now().date()
        
        for cidade, estado in cities:
            for i in range(7):
                data = today + timedelta(days=i)
                precipitacao = round(random.uniform(0, 80), 1)
                temp_min = round(random.uniform(15, 25), 1)
                temp_max = round(random.uniform(25, 35), 1)
                umidade = random.randint(40, 90)
                
                cursor.execute("""
                    INSERT INTO previsoes (
                        cidade, estado, data, precipitacao, 
                        temp_min, temp_max, umidade,
                        probabilidade_alagamento, nivel_risco, afetados_estimados
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (cidade, estado, data) DO UPDATE SET
                        precipitacao = EXCLUDED.precipitacao,
                        temp_min = EXCLUDED.temp_min,
                        temp_max = EXCLUDED.temp_max,
                        umidade = EXCLUDED.umidade,
                        probabilidade_alagamento = EXCLUDED.probabilidade_alagamento,
                        nivel_risco = EXCLUDED.nivel_risco,
                        afetados_estimados = EXCLUDED.afetados_estimados,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    cidade, estado, data, precipitacao, 
                    temp_min, temp_max, umidade,
                    round(random.uniform(0, 100), 2),
                    random.choice(['baixo', 'medio', 'alto']),
                    random.randint(0, 1000)
                ))
        
        # Inserir dados históricos de chuva (últimos 30 dias)
        for cidade, estado in cities:
            for i in range(30):
                data = today - timedelta(days=i)
                precipitacao = round(random.uniform(0, 100), 1)
                
                cursor.execute("""
                    INSERT INTO chuvas_diarias (municipio, estado, data, precipitacao_diaria)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (municipio, estado, data) DO UPDATE SET
                        precipitacao_diaria = EXCLUDED.precipitacao_diaria
                """, (cidade, estado, data, precipitacao))
        
        # Inserir alguns pontos de alagamento
        alagamento_points = [
            ('Rio de Janeiro', 'RJ', 'Centro', -22.9068, -43.1729, 'alto'),
            ('Rio de Janeiro', 'RJ', 'Copacabana', -22.9711, -43.1822, 'médio'),
            ('São Paulo', 'SP', 'Centro', -23.5505, -46.6333, 'alto'),
            ('Niterói', 'RJ', 'Centro', -22.8833, -43.1036, 'médio'),
        ]
        
        for cidade, estado, local, lat, lng, gravidade in alagamento_points:
            # Inserir alguns eventos históricos
            for i in range(5):
                data = today - timedelta(days=random.randint(1, 365))
                afetados = random.randint(10, 1000) if gravidade == 'alto' else random.randint(0, 100)
                
                cursor.execute("""
                    INSERT INTO alagamentos (municipio, estado, data, local, dh_afetados, latitude, longitude, nivel_gravidade)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (cidade, estado, data, local, afetados, lat, lng, gravidade))
        
        conn.commit()
        print("✅ Dados de exemplo inseridos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados de exemplo: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def fix_db_utils():
    """Cria uma versão corrigida do db_utils.py"""
    print("🔧 Gerando correção para db_utils.py...")
    
    corrected_code = '''import os
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
'''
    
    # Salvar o código corrigido
    try:
        with open("db_utils_fixed.py", "w", encoding="utf-8") as f:
            f.write(corrected_code)
        print("✅ Arquivo db_utils_fixed.py criado com sucesso!")
        print("   Substitua o conteúdo do arquivo db_utils.py original por este.")
    except Exception as e:
        print(f"❌ Erro ao criar arquivo corrigido: {e}")

def test_fixed_queries():
    """Testa as queries com os dados inseridos"""
    print("🧪 Testando queries corrigidas...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Testar query de previsão
        cidade = "Rio de Janeiro"
        estado = "RJ"
        
        query = """
        SELECT 
            data, 
            precipitacao 
        FROM 
            previsoes 
        WHERE 
            UPPER(cidade) = UPPER(%s)
            AND UPPER(estado) = UPPER(%s)
            AND data BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
        ORDER BY data
        """
        
        cursor.execute(query, (cidade, estado))
        results = cursor.fetchall()
        
        print(f"✅ Query de previsão: {len(results)} registros encontrados")
        for result in results:
            print(f"   - {result['data']}: {result['precipitacao']}mm")
        
        # Testar query de histórico
        data_inicio = (datetime.now().date() - timedelta(days=30)).strftime('%Y-%m-%d')
        data_fim = datetime.now().date().strftime('%Y-%m-%d')
        
        query_historico = """
        SELECT 
            data, 
            precipitacao_diaria as precipitacao
        FROM 
            chuvas_diarias
        WHERE 
            UPPER(municipio) = UPPER(%s)
            AND UPPER(estado) = UPPER(%s)
            AND data BETWEEN %s AND %s
        ORDER BY data DESC
        LIMIT 5
        """
        
        cursor.execute(query_historico, (cidade, estado, data_inicio, data_fim))
        results = cursor.fetchall()
        
        print(f"✅ Query de histórico: {len(results)} registros encontrados")
        for result in results:
            print(f"   - {result['data']}: {result['precipitacao']}mm")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao testar queries: {e}")

def main():
    """Função principal para aplicar as correções"""
    print("🔧 APLICANDO CORREÇÕES NO BANCO DE DADOS")
    print("=" * 50)
    
    # Verificar conexão
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        print("✅ Conexão com banco verificada")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    corrigir_constraint_previsoes()
    create_missing_tables()
    insert_sample_data()
    fix_db_utils()
    test_fixed_queries()
    
    print("\n" + "=" * 50)
    print("✅ Correções aplicadas!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Substitua o conteúdo de db_utils.py pelo arquivo db_utils_fixed.py")
    print("2. Reinicie sua aplicação")
    print("3. Teste as APIs novamente")

if __name__ == "__main__":
    main() 