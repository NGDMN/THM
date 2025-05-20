import requests
import pandas as pd
import psycopg2
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}
API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = 'https://api.openweathermap.org/data/2.5/forecast'

# Usar o arquivo data/municipios_RJ_SP_coords.csv
csv_path = 'data/municipios_RJ_SP_coords.csv'
municipios = pd.read_csv(csv_path)
municipios = municipios.dropna(subset=['lat', 'lon'])

previsoes = []
for _, row in municipios.iterrows():
    municipio = row['municipio']
    estado = row['estado']
    lat = row['lat']
    lon = row['lon']
    url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
    resp = requests.get(url)
    if resp.status_code == 200:
        dados = resp.json()
        for item in dados['list']:
            data_prev = item['dt_txt'][:10]
            # Apenas hoje + próximos 4 dias
            data_dt = datetime.strptime(data_prev, '%Y-%m-%d').date()
            hoje = datetime.now().date()
            if hoje <= data_dt <= hoje + timedelta(days=4):
                precipitacao = item.get('rain', {}).get('3h', 0)
                previsoes.append({
                    'estado': estado,
                    'municipio': municipio,
                    'data': data_prev,
                    'precipitacao': precipitacao
                })
    else:
        print(f'Erro ao coletar previsão para {municipio}: {resp.status_code}')

# Agrupar por municipio, estado, data e somar precipitação diária
if previsoes:
    df = pd.DataFrame(previsoes)
    df = df.groupby(['municipio', 'estado', 'data'], as_index=False)['precipitacao'].sum()
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/previsoes.csv', index=False)
    print('Previsões salvas em data/previsoes.csv')

    # Inserir no banco
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        for _, row in df.iterrows():
            cur.execute('''\
                INSERT INTO previsoes (cidade, estado, data, precipitacao)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (cidade, estado, data) DO UPDATE SET precipitacao = EXCLUDED.precipitacao
            ''', (row['municipio'], row['estado'], row['data'], row['precipitacao']))
        conn.commit()
        cur.close()
        conn.close()
        print('Previsões inseridas no banco.')
    except Exception as e:
        print(f'Erro ao inserir previsões no banco: {e}')
else:
    print('Nenhuma previsão coletada.')

# Atualizar thresholds de risco sempre que atualizar a previsão
def atualizar_thresholds():
    try:
        import subprocess
        subprocess.run(['python', 'scripts/exportar_thresholds.py'], check=True)
    except Exception as e:
        print(f'Erro ao atualizar thresholds: {e}')

if __name__ == '__main__':
    atualizar_thresholds() 