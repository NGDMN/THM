import pandas as pd
import os

# Carregar dados
chuvas = pd.read_csv('data/chuvas_unificado.csv', parse_dates=['data'])
alag = pd.read_csv('data/alagamentos_unificado.csv', parse_dates=['data'])

resultados = []

for _, row in alag.iterrows():
    municipio = row['municipio']
    data_alag = row['data']
    # Filtrar chuvas do município nos 7 dias anteriores ao alagamento
    chuvas_mun = chuvas[(chuvas['municipio'] == municipio) & \
                        (chuvas['data'] < data_alag) & \
                        (chuvas['data'] >= data_alag - pd.Timedelta(days=7))]
    soma_precip = chuvas_mun['precipitacao'].sum()
    dias_chuva = (chuvas_mun['precipitacao'] > 0).sum()
    resultados.append({
        'municipio': municipio,
        'data_alagamento': data_alag,
        'chuva_7d': soma_precip,
        'dias_chuva_7d': dias_chuva
    })

df_result = pd.DataFrame(resultados)

# Estatísticas por município
padrao_municipio = df_result.groupby('municipio').agg({
    'chuva_7d': ['mean', 'median', 'min', 'max'],
    'dias_chuva_7d': ['mean', 'median', 'min', 'max']
})

os.makedirs('data', exist_ok=True)
df_result.to_csv('data/analise_alagamento_chuva.csv', index=False)
padrao_municipio.to_csv('data/padrao_alagamento_por_municipio.csv')

print('Análise concluída!')
print('Resultados salvos em data/analise_alagamento_chuva.csv e data/padrao_alagamento_por_municipio.csv') 