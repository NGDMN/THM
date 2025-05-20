import pandas as pd
import os

# Carregar estatísticas por município
padrao = pd.read_csv('data/padrao_alagamento_por_municipio.csv', header=[0,1], index_col=0)

# Extrair apenas a mediana da chuva acumulada em 7 dias
thresholds = padrao[('chuva_7d', 'median')].reset_index()
thresholds.columns = ['municipio', 'threshold_chuva_7d']

os.makedirs('data', exist_ok=True)
thresholds.to_csv('data/thresholds_chuva_7d.csv', index=False)

print('Thresholds de risco exportados para data/thresholds_chuva_7d.csv') 