import pandas as pd
import requests
import time
import sys
import os

# Carregar municípios
os.makedirs('data', exist_ok=True)
municipios = pd.read_csv('data/municipios_RJ_SP.csv')
municipios.columns = [c.lower() for c in municipios.columns]
municipios = municipios.rename(columns={'estado': 'uf', 'município': 'municipio'})

coords = []
total = len(municipios)
for i, row in municipios.iterrows():
    municipio = row['municipio']
    uf = row['uf']
    query = f"{municipio}, {uf}, Brasil"
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
    try:
        resp = requests.get(url, headers={'User-Agent': 'THM-Coleta/1.0'})
        data = resp.json()
        if data:
            lat = data[0]['lat']
            lon = data[0]['lon']
        else:
            lat = lon = None
    except Exception as e:
        print(f'Erro ao buscar {municipio}/{uf}: {e}')
        lat = lon = None
    coords.append({'estado': uf, 'municipio': municipio, 'lat': lat, 'lon': lon})
    # Barra de progresso
    progresso = int((i+1)/total*40)
    sys.stdout.write('\r[' + '#' * progresso + '-' * (40-progresso) + f'] {i+1}/{total} municípios')
    sys.stdout.flush()
    time.sleep(1)  # Respeitar limites da API

print()  # Nova linha após a barra de progresso
coords_df = pd.DataFrame(coords)
coords_df.to_csv('data/municipios_RJ_SP_coords.csv', index=False)
print("Arquivo 'data/municipios_RJ_SP_coords.csv' gerado com sucesso!") 