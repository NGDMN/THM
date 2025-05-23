#!/usr/bin/env python3
"""
Script de diagnóstico para identificar problemas no banco de dados
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Adicionar o caminho do projeto ao sys.path se necessário
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    print("❌ ERRO: psycopg2 não está disponível!")
    PSYCOPG2_AVAILABLE = False
    sys.exit(1)

# Configuração do banco (ajuste conforme necessário)
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def test_connection():
    """Testa a conexão com o banco de dados"""
    print("🔍 Testando conexão com o banco de dados...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ Conexão estabelecida com sucesso!")
        print(f"📄 Versão do PostgreSQL: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def check_tables():
    """Verifica se as tabelas existem e quantos registros têm"""
    print("\n🔍 Verificando tabelas do banco...")
    
    tables_to_check = [
        'previsoes',
        'chuvas_diarias', 
        'alagamentos',
        'configuracao_sistema'
    ]
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for table in tables_to_check:
            try:
                # Verificar se a tabela existe
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    )
                """, (table,))
                
                exists = cursor.fetchone()[0]
                
                if exists:
                    # Contar registros
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"✅ Tabela '{table}': {count} registros")
                    
                    # Para tabelas principais, mostrar algumas colunas
                    if table in ['previsoes', 'chuvas_diarias', 'alagamentos']:
                        cursor.execute(f"""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE table_name = '{table}' 
                            ORDER BY ordinal_position
                        """)
                        columns = cursor.fetchall()
                        print(f"   📋 Colunas: {', '.join([col[0] for col in columns])}")
                        
                        # Mostrar alguns dados de exemplo
                        if count > 0:
                            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                            sample_data = cursor.fetchall()
                            print(f"   📊 Exemplo de dados:")
                            for i, row in enumerate(sample_data, 1):
                                print(f"      Registro {i}: {row}")
                else:
                    print(f"❌ Tabela '{table}': NÃO EXISTE")
                    
            except Exception as e:
                print(f"❌ Erro ao verificar tabela '{table}': {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro geral ao verificar tabelas: {e}")

def check_cities_data():
    """Verifica dados específicos para as cidades testadas"""
    print("\n🔍 Verificando dados para cidades específicas...")
    
    cities_to_check = [
        ('Rio de Janeiro', 'RJ'),
        ('Angra dos Reis', 'RJ'),
        ('São Paulo', 'SP'),
        ('Niterói', 'RJ')
    ]
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        for cidade, estado in cities_to_check:
            print(f"\n🏙️  Verificando: {cidade} - {estado}")
            
            # Verificar na tabela previsoes
            cursor.execute("""
                SELECT COUNT(*) as total, MIN(data) as data_min, MAX(data) as data_max
                FROM previsoes 
                WHERE UPPER(cidade) = UPPER(%s) AND UPPER(estado) = UPPER(%s)
            """, (cidade, estado))
            
            result = cursor.fetchone()
            if result['total'] > 0:
                print(f"   ✅ Previsões: {result['total']} registros (de {result['data_min']} até {result['data_max']})")
            else:
                print(f"   ❌ Previsões: Nenhum registro encontrado")
                
                # Verificar variações do nome da cidade
                print(f"   🔍 Verificando variações do nome...")
                cursor.execute("""
                    SELECT DISTINCT cidade, estado, COUNT(*) as total
                    FROM previsoes 
                    WHERE cidade ILIKE %s OR cidade ILIKE %s
                    GROUP BY cidade, estado
                    ORDER BY total DESC
                    LIMIT 5
                """, (f'%{cidade.split()[0]}%', f'%{cidade}%'))
                
                variations = cursor.fetchall()
                if variations:
                    print(f"   📋 Possíveis variações encontradas:")
                    for var in variations:
                        print(f"      - {var['cidade']} ({var['estado']}): {var['total']} registros")
            
            # Verificar na tabela chuvas_diarias
            cursor.execute("""
                SELECT COUNT(*) as total, MIN(data) as data_min, MAX(data) as data_max
                FROM chuvas_diarias 
                WHERE UPPER(municipio) = UPPER(%s) AND UPPER(estado) = UPPER(%s)
            """, (cidade, estado))
            
            result = cursor.fetchone()
            if result['total'] > 0:
                print(f"   ✅ Chuvas históricas: {result['total']} registros (de {result['data_min']} até {result['data_max']})")
            else:
                print(f"   ❌ Chuvas históricas: Nenhum registro encontrado")
            
            # Verificar na tabela alagamentos
            cursor.execute("""
                SELECT COUNT(*) as total, MIN(data) as data_min, MAX(data) as data_max
                FROM alagamentos 
                WHERE UPPER(municipio) = UPPER(%s) AND UPPER(estado) = UPPER(%s)
            """, (cidade, estado))
            
            result = cursor.fetchone()
            if result['total'] > 0:
                print(f"   ✅ Alagamentos: {result['total']} registros (de {result['data_min']} até {result['data_max']})")
            else:
                print(f"   ❌ Alagamentos: Nenhum registro encontrado")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados das cidades: {e}")

def check_query_issues():
    """Verifica se há problemas específicos nas queries"""
    print("\n🔍 Testando queries específicas...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Testar query de previsão de chuvas (copiada do código)
        cidade = "Rio de Janeiro"
        estado = "RJ"
        
        print(f"🧪 Testando query de previsão para {cidade}-{estado}...")
        
        query = """
        SELECT 
            data, 
            precipitacao 
        FROM 
            previsoes 
        WHERE 
            UPPER(cidade) = UPPER(%(cidade)s)
            AND UPPER(estado) = UPPER(%(estado)s)
            AND data BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
        ORDER BY data
        """
        
        params = {"cidade": cidade, "estado": estado}
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        print(f"   📊 Resultados: {len(results)} registros")
        for result in results:
            print(f"      - {result['data']}: {result['precipitacao']}mm")
        
        # Testar sem filtro de data para ver se há dados
        print(f"\n🧪 Testando sem filtro de data...")
        
        query_no_date = """
        SELECT 
            data, 
            precipitacao 
        FROM 
            previsoes 
        WHERE 
            UPPER(cidade) = UPPER(%(cidade)s)
            AND UPPER(estado) = UPPER(%(estado)s)
        ORDER BY data DESC
        LIMIT 10
        """
        
        cursor.execute(query_no_date, params)
        results = cursor.fetchall()
        
        print(f"   📊 Resultados sem filtro de data: {len(results)} registros")
        for result in results:
            print(f"      - {result['data']}: {result['precipitacao']}mm")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao testar queries: {e}")

def main():
    """Função principal do diagnóstico"""
    print("🩺 DIAGNÓSTICO DO BANCO DE DADOS")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    print("🔍 Verificando configuração...")
    for key in ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']:
        value = os.getenv(key)
        if value:
            if 'PASSWORD' in key:
                print(f"✅ {key}: ***")
            else:
                print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: NÃO DEFINIDA")
    
    if not test_connection():
        print("❌ Não foi possível conectar ao banco. Verifique as configurações.")
        return
    
    check_tables()
    check_cities_data() 
    check_query_issues()
    
    print("\n" + "=" * 50)
    print("✅ Diagnóstico concluído!")

if __name__ == "__main__":
    main() 