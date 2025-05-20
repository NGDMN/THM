import pandas as pd
import os

# URLs da API do IBGE para RJ (33) e SP (35)
urls = {
    'RJ': 'https://servicodados.ibge.gov.br/api/v1/localidades/estados/33/municipios',
    'SP': 'https://servicodados.ibge.gov.br/api/v1/localidades/estados/35/municipios'
}

df_list = []
for estado, url in urls.items():
    df = pd.read_json(url)
    df_list.append(pd.DataFrame({
        'Estado': estado,
        'Município': df['nome']
    }))

municipios_df = pd.concat(df_list, ignore_index=True)
os.makedirs('data', exist_ok=True)
municipios_df.to_csv('data/municipios_RJ_SP.csv', index=False)
print("Arquivo 'data/municipios_RJ_SP.csv' gerado com sucesso!") 