import pandas as pd
import psycopg2
import os
from datetime import timedelta

DB_CONFIG = {
    'dbname': 'thm_iy9l',
    'user': 'thm_admin',
    'password': 'fBfTMpHLfe2htlV9fe63mc0v9SmUTStS',
    'host': 'dpg-d0l48cre5dus73c970sg-a.ohio-postgres.render.com',
    'port': '5432'
}

def calcular_indice():
    # Carregar dados limpos
    chuvas = pd.read_csv('data/chuvas_unificado.csv', parse_dates=['data'])
    alag = pd.read_csv('data/alagamentos_unificado.csv', parse_dates=['data'])
    # Calcular média móvel de 7 dias de chuva por município
    chuvas['media_7d'] = chuvas.groupby('municipio')['precipitacao'].transform(lambda x: x.rolling(7, min_periods=1).mean())
    # Contar alagamentos nos últimos 7 dias por município
    alag['alag_1'] = 1
    alag_agg = alag.groupby(['municipio', 'data'])['alag_1'].sum().reset_index()
    alag_agg['alag_7d'] = alag_agg.groupby('municipio')['alag_1'].transform(lambda x: x.rolling(7, min_periods=1).sum())
    # Juntar
    df = pd.merge(chuvas, alag_agg[['municipio', 'data', 'alag_7d']], on=['municipio', 'data'], how='left').fillna(0)
    # Índice de risco: 0.7 * média chuva + 0.3 * alag_7d
    df['indice_risco'] = 0.7 * df['media_7d'] + 0.3 * df['alag_7d']
    df_out = df[['municipio', 'data', 'media_7d', 'alag_7d', 'indice_risco']]
    os.makedirs('data', exist_ok=True)
    df_out.to_csv('data/indice_risco.csv', index=False)
    print('Índice de risco salvo em data/indice_risco.csv')
    return df_out

def inserir_indice_db(df):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        for _, row in df.iterrows():
            cur.execute('''\
                INSERT INTO indice_risco (municipio, data, media_7d, alag_7d, indice_risco)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (municipio, data) DO UPDATE SET indice_risco = EXCLUDED.indice_risco
            ''', (row['municipio'], row['data'], row['media_7d'], row['alag_7d'], row['indice_risco']))
        conn.commit()
        cur.close()
        conn.close()
        print('Índice de risco inserido no banco.')
    except Exception as e:
        print(f'Erro ao inserir índice no banco: {e}')

if __name__ == '__main__':
    df = calcular_indice()
    inserir_indice_db(df) 