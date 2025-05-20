import pandas as pd
import os
import psycopg2
from dotenv import load_dotenv
from script_limpeza_dados import load_rainfall_data
from psycopg2.extras import execute_values
import traceback

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# Nota: É necessário criar uma restrição de unicidade na tabela chuvas_diarias
# para as colunas municipio, estado e data. Execute o seguinte SQL:
# ALTER TABLE chuvas_diarias ADD CONSTRAINT chuvas_diarias_municipio_estado_data_key 
# UNIQUE (municipio, estado, data);

def unificar_chuvas(pasta='./Chuvas/'):
    df = load_rainfall_data(directory=pasta)
    if df.empty:
        print('Nenhum arquivo de chuva encontrado.')
        return pd.DataFrame()
    
    print('Colunas encontradas:', df.columns.tolist())
    
    # Padronizar colunas
    if 'UF' in df.columns:
        df = df.rename(columns={'UF': 'uf'})
    if 'Municipio' in df.columns:
        df = df.rename(columns={'Municipio': 'municipio'})
    if 'Data' in df.columns:
        df = df.rename(columns={'Data': 'data'})
    if 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)' in df.columns:
        df = df.rename(columns={'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'precipitacao'})
    
    # Filtrar apenas RJ e SP
    df = df[df['uf'].isin(['RJ', 'SP'])]
    
    # Padronizar município
    df['municipio'] = df['municipio'].str.upper().str.strip()
    
    # Converter data para datetime e extrair apenas a data
    df['data'] = pd.to_datetime(df['data'], errors='coerce').dt.date
    
    # Converter precipitação para numérico, tratando possíveis erros
    df['precipitacao'] = pd.to_numeric(df['precipitacao'].astype(str).str.replace(',', '.'), errors='coerce')
    
    # Remover linhas com valores nulos em precipitação
    df = df.dropna(subset=['precipitacao'])
    
    # Agregação diária por município e data (soma da precipitação)
    df = df.groupby(['uf', 'municipio', 'data'], as_index=False).agg({
        'precipitacao': 'sum'
    })
    
    # Verificar duplicatas após agregação
    duplicatas = df.duplicated(subset=['municipio', 'data'], keep=False)
    if duplicatas.any():
        print(f'ATENÇÃO: Encontradas {duplicatas.sum()} duplicatas após agregação!')
        print(df[duplicatas].sort_values(['municipio', 'data']))
    
    # Salvar resultado intermediário
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/chuvas_unificado.csv', index=False)
    print(f'{len(df)} registros salvos em data/chuvas_unificado.csv')
    
    return df

def inserir_chuvas_db(df):
    if df.empty:
        print('DataFrame vazio, nada a inserir.')
        return
        
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Preparar dados para inserção em lote
        data_tuples = []
        for _, row in df.iterrows():
            data_tuples.append((
                row['municipio'],
                row['uf'],
                row['data'],
                float(row['precipitacao'])
            ))
            
        # Query de inserção com ON CONFLICT
        query = """
            INSERT INTO chuvas_diarias (municipio, estado, data, precipitacao_diaria)
            VALUES %s
            ON CONFLICT (municipio, estado, data) 
            DO UPDATE SET 
                precipitacao_diaria = EXCLUDED.precipitacao_diaria,
                updated_at = CURRENT_TIMESTAMP
        """
        
        # Executar inserção em lote
        execute_values(cur, query, data_tuples)
        conn.commit()
        
        print(f'{len(data_tuples)} registros inseridos/atualizados no banco de dados.')
        
    except Exception as e:
        print(f'Erro ao inserir no banco: {str(e)}')
        print('Detalhes do erro:')
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def setup_database():
    """Executa o script SQL de configuração do banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Ler e executar o arquivo SQL
        with open('scripts/setup_database.sql', 'r') as f:
            sql_script = f.read()
            cur.execute(sql_script)
            
        conn.commit()
        print('Banco de dados configurado com sucesso!')
        
    except Exception as e:
        print(f'Erro ao configurar banco de dados: {str(e)}')
        print('Detalhes do erro:')
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    # Primeiro, configurar o banco de dados
    setup_database()
    
    # Depois, processar e inserir os dados
    df = unificar_chuvas()
    inserir_chuvas_db(df) 