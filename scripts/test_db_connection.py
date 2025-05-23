import psycopg2
import pandas as pd
from datetime import datetime, timedelta

# Configurações do banco de dados
DB_CONFIG = {
    'dbname': 'thm_iy9l',
    'user': 'thm_admin',
    'password': 'fBfTMpHLfe2htlV9fe63mc0v9SmUTStS',
    'host': 'dpg-d0l48cre5dus73c970sg-a.ohio-postgres.render.com',
    'port': '5432'
}

def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conexão com o banco de dados estabelecida com sucesso!")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None

def test_query_previsoes(conn, cidade, estado):
    """Testa a query de previsões"""
    try:
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
        
        print(f"\n🔍 Testando query de previsões:")
        print(f"Query: {query}")
        print(f"Parâmetros: cidade={cidade}, estado={estado}")
        
        df = pd.read_sql_query(query, conn, params=(cidade, estado))
        
        print(f"\nResultados encontrados: {len(df)} registros")
        if not df.empty:
            print("\nPrimeiros registros:")
            print(df.head())
        else:
            print("\nNenhum registro encontrado!")
            
    except Exception as e:
        print(f"❌ Erro ao executar query de previsões: {e}")

def test_query_chuvas_diarias(conn, cidade, estado):
    """Testa a query de chuvas diárias"""
    try:
        query = """
        SELECT 
            data, 
            precipitacao_diaria as precipitacao
        FROM 
            chuvas_diarias
        WHERE 
            UPPER(municipio) = UPPER(%s)
            AND UPPER(estado) = UPPER(%s)
            AND data BETWEEN CURRENT_DATE - INTERVAL '30 days' AND CURRENT_DATE + INTERVAL '7 days'
        ORDER BY data DESC
        LIMIT 7
        """
        
        print(f"\n🔍 Testando query de chuvas diárias:")
        print(f"Query: {query}")
        print(f"Parâmetros: cidade={cidade}, estado={estado}")
        
        df = pd.read_sql_query(query, conn, params=(cidade, estado))
        
        print(f"\nResultados encontrados: {len(df)} registros")
        if not df.empty:
            print("\nPrimeiros registros:")
            print(df.head())
        else:
            print("\nNenhum registro encontrado!")
            
    except Exception as e:
        print(f"❌ Erro ao executar query de chuvas diárias: {e}")

def main():
    # Testar conexão
    conn = test_connection()
    if not conn:
        return
    
    try:
        # Testar com diferentes variações de cidade
        cidades_teste = [
            "Rio de Janeiro",
            "rio de janeiro",
            "RIO DE JANEIRO",
            "rio-de-janeiro"
        ]
        
        for cidade in cidades_teste:
            print(f"\n{'='*50}")
            print(f"Testando com cidade: {cidade}")
            print(f"{'='*50}")
            
            # Testar query de previsões
            test_query_previsoes(conn, cidade, "RJ")
            
            # Testar query de chuvas diárias
            test_query_chuvas_diarias(conn, cidade, "RJ")
            
    finally:
        conn.close()
        print("\n✅ Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main() 