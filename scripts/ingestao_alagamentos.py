import pandas as pd
import os
import psycopg2
from dotenv import load_dotenv
from script_limpeza_dados import load_flooding_data

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def unificar_alagamentos(pasta='./Alagamentos/'):
    df = load_flooding_data(directory=pasta)
    if df.empty:
        print('Nenhum arquivo de alagamento encontrado.')
        return pd.DataFrame()
    print('Colunas encontradas:', df.columns.tolist())
    # Padronizar colunas
    if 'UF' in df.columns:
        df = df.rename(columns={'UF': 'uf'})
    if 'Município' in df.columns:
        df = df.rename(columns={'Município': 'municipio'})
    if 'registro' in df.columns:
        df = df.rename(columns={'registro': 'data'})
    elif 'Registro' in df.columns:
        df = df.rename(columns={'Registro': 'data'})
    # Só continua se a coluna 'data' existir
    if 'data' not in df.columns:
        print('Coluna "data" não encontrada após renomear. Ignorando este arquivo.')
        return pd.DataFrame()
    df = df[df['uf'].isin(['RJ', 'SP'])]
    df['municipio'] = df['municipio'].str.upper().str.strip()
    df['data'] = pd.to_datetime(df['data'], errors='coerce').dt.date
    df = df[['uf', 'municipio', 'data']]
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/alagamentos_unificado.csv', index=False)
    print(f'{len(df)} registros salvos em data/alagamentos_unificado.csv')
    return df

def inserir_alagamentos_db(df):
    if df.empty:
        print('DataFrame vazio, nada a inserir.')
        return
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        for _, row in df.iterrows():
            cur.execute('''\
                INSERT INTO alagamentos (municipio, estado, data)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            ''', (row['municipio'], row['uf'], row['data']))
        conn.commit()
        cur.close()
        conn.close()
        print('Registros inseridos no banco de dados.')
    except Exception as e:
        print(f'Erro ao inserir no banco: {e}')

if __name__ == '__main__':
    df = unificar_alagamentos()
    inserir_alagamentos_db(df) 