import pandas as pd
import os
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
import traceback

# Configurações do banco de dados PostgreSQL
DB_CONFIG = {
    'dbname': 'thm_iy9l',
    'user': 'thm_admin',
    'password': 'fBfTMpHLfe2htlV9fe63mc0v9SmUTStS',
    'host': 'dpg-d0l48cre5dus73c970sg-a.ohio-postgres.render.com',
    'port': '5432'
}

# Prompt 1: Carregar Dados Meteorológicos
def load_rainfall_data(directory="Chuvas"):
    try:
        all_files = [os.path.join(directory, f) for f in os.listdir(directory) 
                     if f.endswith('.CSV') or f.endswith('.csv')]
        
        if not all_files:
            print(f"Nenhum arquivo CSV encontrado em {directory}")
            return pd.DataFrame()  # Retorna DataFrame vazio
        
        dfs = []
        for file in all_files:
            try:
                # Extrair UF e município do nome do arquivo
                filename = os.path.basename(file)
                parts = filename.split('_')
                
                # Verificar se o arquivo segue o padrão esperado
                if len(parts) >= 5:
                    uf = parts[2]  # UF está na 3ª parte (índice 2)
                    
                    # Filtrar apenas RJ e SP
                    if uf not in ['RJ', 'SP']:
                        continue
                    
                    # Município está na 5ª parte (índice 4)
                    municipio = parts[4].split('-')[0].strip()
                
                # Primeiro, vamos ler as primeiras 15 linhas para identificar o cabeçalho real
                with open(file, 'r', encoding='latin1') as f:
                    lines = [line.strip() for line in f.readlines()[:15]]
                
                # Encontrar a linha que começa com "Data;"
                header_line = -1
                for i, line in enumerate(lines):
                    if line.startswith("Data;"):
                        header_line = i
                        break
                
                if header_line >= 0:
                    # Usar a linha encontrada como cabeçalho
                    df = pd.read_csv(file, sep=';', encoding='latin1', skiprows=header_line, on_bad_lines='skip')
                    
                    # Adicionar colunas de UF e Município
                    df['UF'] = uf
                    df['Municipio'] = municipio
                    
                    print(f"Arquivo {os.path.basename(file)} carregado com sucesso.")
                    dfs.append(df)
                else:
                    print(f"Não foi possível encontrar o cabeçalho no arquivo {os.path.basename(file)}.")
                    
            except Exception as e:
                print(f"Erro ao carregar o arquivo {os.path.basename(file)}: {str(e)}")
                    
        if not dfs:
            print("Nenhum arquivo foi carregado corretamente.")
            return pd.DataFrame()  # Retorna DataFrame vazio
            
        df_chuvas = pd.concat(dfs, ignore_index=True)
        print(f"Total de {len(df_chuvas)} registros de chuva carregados.")
        return df_chuvas
    
    except Exception as e:
        print(f"Erro ao carregar dados de chuva: {str(e)}")
        traceback.print_exc()
        return pd.DataFrame()  # Retorna DataFrame vazio

# Prompt 2: Combinar Data e Hora
def combine_date_time(df_chuvas):
    try:
        if df_chuvas.empty:
            print("DataFrame de chuvas vazio. Pulando combinação de data e hora.")
            return df_chuvas
            
        # Verificar formato da data e tentar converter
        try:
            df_chuvas['Data'] = pd.to_datetime(df_chuvas['Data'], format='%Y/%m/%d')
        except:
            try:
                df_chuvas['Data'] = pd.to_datetime(df_chuvas['Data'], format='%d/%m/%Y')
            except:
                df_chuvas['Data'] = pd.to_datetime(df_chuvas['Data'], errors='coerce')
                
        # Verificar se a coluna 'Hora UTC' existe
        if 'Hora UTC' in df_chuvas.columns:
            df_chuvas['Hora UTC'] = df_chuvas['Hora UTC'].astype(str).str.replace(' UTC', '')
            df_chuvas['Datetime'] = pd.to_datetime(df_chuvas['Data'].astype(str) + ' ' + 
                                                  df_chuvas['Hora UTC'], format='%Y-%m-%d %H%M', errors='coerce')
        else:
            df_chuvas['Datetime'] = df_chuvas['Data']
            
        print("Data e hora combinadas com sucesso.")
        return df_chuvas
        
    except Exception as e:
        print(f"Erro ao combinar data e hora: {str(e)}")
        traceback.print_exc()
        return df_chuvas

# Prompt 3: Filtrar para RJ e SP
def filter_rj_sp(df_chuvas):
    try:
        if df_chuvas.empty:
            print("DataFrame de chuvas vazio. Pulando filtragem por UF.")
            return df_chuvas
            
        print(f"Registros antes do filtro: {len(df_chuvas)}")
        
        # Verificar o nome correto da coluna UF
        uf_col = None
        for col in df_chuvas.columns:
            if 'UF' in col.upper():
                uf_col = col
                break
                
        if uf_col:
            df_chuvas = df_chuvas[df_chuvas[uf_col].isin(['RJ', 'SP'])]
            print(f"Registros após filtro: {len(df_chuvas)}")
        else:
            print("Coluna UF não encontrada. Não foi possível filtrar.")
            
        return df_chuvas
        
    except Exception as e:
        print(f"Erro ao filtrar para RJ e SP: {str(e)}")
        traceback.print_exc()
        return df_chuvas

# Prompt 4: Tratar Valores Ausentes (Chuva)
def handle_missing_rainfall(df_chuvas):
    try:
        if df_chuvas.empty:
            print("DataFrame de chuvas vazio. Pulando tratamento de valores ausentes.")
            return df_chuvas
            
        # Verificar o nome correto da coluna de precipitação
        precip_col = None
        for col in df_chuvas.columns:
            if 'PRECIPITA' in col.upper() and 'HOR' in col.upper():
                precip_col = col
                break
                
        if precip_col:
            print(f"Valores ausentes antes na coluna {precip_col}: {df_chuvas[precip_col].isna().sum()}")
            df_chuvas[precip_col] = df_chuvas[precip_col].fillna(0)
            print(f"Valores ausentes após tratamento: {df_chuvas[precip_col].isna().sum()}")
        else:
            print("Coluna de precipitação não encontrada. Não foi possível tratar valores ausentes.")
            
        return df_chuvas
        
    except Exception as e:
        print(f"Erro ao tratar valores ausentes de chuva: {str(e)}")
        traceback.print_exc()
        return df_chuvas

# Prompt 5: Remover Duplicatas (Chuva)
def remove_duplicates_rainfall(df_chuvas):
    try:
        if df_chuvas.empty:
            print("DataFrame de chuvas vazio. Pulando remoção de duplicatas.")
            return df_chuvas
            
        print(f"Registros antes: {len(df_chuvas)}")
        
        # Verificar o nome correto da coluna de estação
        estacao_col = None
        for col in df_chuvas.columns:
            if 'ESTAC' in col.upper():
                estacao_col = col
                break
                
        if estacao_col and 'Datetime' in df_chuvas.columns:
            df_chuvas = df_chuvas.drop_duplicates(subset=['Datetime', estacao_col], keep='first')
            print(f"Registros após remoção de duplicatas: {len(df_chuvas)}")
        else:
            print("Colunas necessárias não encontradas. Não foi possível remover duplicatas.")
            
        return df_chuvas
        
    except Exception as e:
        print(f"Erro ao remover duplicatas: {str(e)}")
        traceback.print_exc()
        return df_chuvas

# Prompt 6: Agregar Dados de Chuva para Totais Diários
def aggregate_daily_rainfall(df_chuvas):
    try:
        if df_chuvas.empty:
            print("DataFrame de chuvas vazio. Pulando agregação diária.")
            return pd.DataFrame()
            
        # Verificar se Datetime existe
        if 'Datetime' not in df_chuvas.columns:
            print("Coluna Datetime não encontrada. Não é possível agregar por dia.")
            return pd.DataFrame()
            
        df_chuvas['Date'] = df_chuvas['Datetime'].dt.date
        
        # Verificar o nome correto das colunas necessárias
        precip_col = None
        
        for col in df_chuvas.columns:
            if 'PRECIPITA' in col.upper() and 'HOR' in col.upper():
                precip_col = col
                
        if not precip_col:
            print("Coluna de precipitação não encontrada. Não é possível agregar dados de chuva.")
            return pd.DataFrame()
        
        # Usamos diretamente a coluna Municipio que foi adicionada durante o carregamento
        # Verificamos se ela existe
        if 'Municipio' not in df_chuvas.columns:
            print("Coluna Municipio não encontrada. Não é possível agregar por município.")
            return pd.DataFrame()
            
        # Converter precipitação para número antes de somar
        df_chuvas[precip_col] = df_chuvas[precip_col].astype(str).str.replace(',', '.').astype(float)
        
        # Agregar por município, UF e data
        daily_rain = df_chuvas.groupby(['Municipio', 'UF', 'Date'])[precip_col].sum().reset_index()
        daily_rain = daily_rain.rename(columns={precip_col: 'precipitacao_diaria'})
        
        print(f"Totais diários de chuva: {len(daily_rain)} registros.")
        return daily_rain
        
    except Exception as e:
        print(f"Erro ao agregar dados de chuva: {str(e)}")
        traceback.print_exc()
        return pd.DataFrame()

# Prompt 7: Salvar Dados Limpos (Chuva)
def save_clean_rainfall(df_chuvas, daily_rain):
    try:
        # Criar pasta de dados se não existir
        os.makedirs('data', exist_ok=True)
        
        if not df_chuvas.empty:
            df_chuvas.to_csv('data/dados_meteorologicos_limpos.csv', index=False)
            print(f"Dados de chuva salvos: {len(df_chuvas)} registros")
            
        if not daily_rain.empty:
            daily_rain.to_csv('data/chuvas_diarias_limpos.csv', index=False)
            print(f"Dados diários de chuva salvos: {len(daily_rain)} registros")
            
    except Exception as e:
        print(f"Erro ao salvar dados limpos de chuva: {str(e)}")
        traceback.print_exc()

# Prompt 8: Carregar Dados de Alagamentos
def load_flooding_data(directory="Alagamentos"):
    try:
        all_files = [os.path.join(directory, f) for f in os.listdir(directory) 
                     if f.endswith('.CSV') or f.endswith('.csv')]
        
        if not all_files:
            print(f"Nenhum arquivo CSV encontrado em {directory}")
            return pd.DataFrame()
        
        dfs = []
        for file in all_files:
            try:
                # Primeiro, vamos ler as primeiras 10 linhas para identificar o cabeçalho real
                with open(file, 'r', encoding='latin1') as f:
                    lines = [line.strip() for line in f.readlines()[:10]]
                
                # Encontrar a linha que começa com "UF;"
                header_line = -1
                for i, line in enumerate(lines):
                    if line.startswith("UF;"):
                        header_line = i
                        break
                
                # Se encontrou o cabeçalho, carrega o arquivo
                if header_line >= 0:
                    df = pd.read_csv(file, sep=';', encoding='latin1', skiprows=header_line, on_bad_lines='skip')
                    
                    # Verificar se contém a coluna COBRADE
                    if 'COBRADE' in df.columns:
                        dfs.append(df)
                        print(f"Arquivo {os.path.basename(file)} carregado com sucesso.")
                    else:
                        print(f"Arquivo {os.path.basename(file)} não contém a coluna COBRADE.")
                else:
                    print(f"Não foi possível encontrar o cabeçalho no arquivo {os.path.basename(file)}.")
                    
            except Exception as e:
                print(f"Erro ao carregar o arquivo {os.path.basename(file)}: {str(e)}")
                    
        if not dfs:
            print("Nenhum arquivo foi carregado corretamente.")
            return pd.DataFrame()
            
        df_alagamentos = pd.concat(dfs, ignore_index=True)
        print(f"Dados de alagamentos carregados: {len(df_alagamentos)} registros")
        return df_alagamentos
        
    except Exception as e:
        print(f"Erro ao carregar dados de alagamentos: {str(e)}")
        traceback.print_exc()
        return pd.DataFrame()

# Prompt 9: Filtrar Alagamentos
def filter_alagamentos(df_alagamentos):
    try:
        if df_alagamentos.empty:
            print("DataFrame de alagamentos vazio. Pulando filtragem.")
            return df_alagamentos
            
        print(f"Registros antes do filtro: {len(df_alagamentos)}")
        
        if 'COBRADE' in df_alagamentos.columns:
            df_alagamentos = df_alagamentos[df_alagamentos['COBRADE'] == '12300 - Alagamentos']
            print(f"Registros após filtro: {len(df_alagamentos)}")
        else:
            print("Coluna COBRADE não encontrada. Não foi possível filtrar alagamentos.")
            
        return df_alagamentos
        
    except Exception as e:
        print(f"Erro ao filtrar alagamentos: {str(e)}")
        traceback.print_exc()
        return df_alagamentos

# Prompt 10: Padronizar Datas (Alagamentos)
def standardize_dates_flooding(df_alagamentos):
    try:
        if df_alagamentos.empty:
            print("DataFrame de alagamentos vazio. Pulando padronização de datas.")
            return df_alagamentos
            
        # Usar a coluna Registro para extrair a data
        if 'Registro' in df_alagamentos.columns:
            try:
                # Extrair a data do campo Registro (formato DD/MM/YYYY)
                df_alagamentos['Date'] = pd.to_datetime(df_alagamentos['Registro'].str.split(" ").str[0], 
                                                     format='%d/%m/%Y', errors='coerce').dt.date
                print("Datas padronizadas do campo Registro com sucesso.")
            except Exception as date_error:
                print(f"Erro ao converter datas do Registro: {str(date_error)}")
                print("Tentando outro formato de data...")
                try:
                    df_alagamentos['Date'] = pd.to_datetime(df_alagamentos['Registro'], errors='coerce').dt.date
                    print("Datas padronizadas com formato automático.")
                except:
                    print("Não foi possível converter as datas.")
        else:
            print("Coluna Registro não encontrada. Não foi possível padronizar datas.")
            
        return df_alagamentos
        
    except Exception as e:
        print(f"Erro ao padronizar datas: {str(e)}")
        traceback.print_exc()
        return df_alagamentos

# Prompt 11: Tratar Valores Ausentes (Alagamentos)
def handle_missing_flooding(df_alagamentos):
    try:
        if df_alagamentos.empty:
            print("DataFrame de alagamentos vazio. Pulando tratamento de valores ausentes.")
            return df_alagamentos
            
        # Verificar se as colunas existem
        pop_col = None
        mortos_col = None
        
        for col in df_alagamentos.columns:
            if 'POPULA' in col.upper():
                pop_col = col
            elif 'MORTOS' in col.upper():
                mortos_col = col
                
        if pop_col and mortos_col:
            print(f"Valores ausentes antes na coluna {pop_col}: {df_alagamentos[pop_col].isna().sum()}")
            print(f"Valores ausentes antes na coluna {mortos_col}: {df_alagamentos[mortos_col].isna().sum()}")
            df_alagamentos[[pop_col, mortos_col]] = df_alagamentos[[pop_col, mortos_col]].fillna(0)
            print(f"Valores ausentes após tratamento: {df_alagamentos[[pop_col, mortos_col]].isna().sum().sum()}")
        else:
            print("Colunas necessárias não encontradas. Não foi possível tratar valores ausentes.")
            
        return df_alagamentos
        
    except Exception as e:
        print(f"Erro ao tratar valores ausentes de alagamentos: {str(e)}")
        traceback.print_exc()
        return df_alagamentos

# Prompt 12: Corrigir Nomes de Municípios
def clean_municipio_names(df_alagamentos):
    try:
        if df_alagamentos.empty:
            print("DataFrame de alagamentos vazio. Pulando correção de nomes de municípios.")
            return df_alagamentos
            
        # Verificar o nome correto da coluna de município
        municipio_col = None
        for col in df_alagamentos.columns:
            if 'MUNIC' in col.upper():
                municipio_col = col
                break
                
        if municipio_col:
            df_alagamentos['Municipio'] = df_alagamentos[municipio_col].astype(str).str.upper().str.replace('-SP', '').str.replace('-RJ', '')
            print("Nomes de municípios corrigidos.")
        else:
            print("Coluna de município não encontrada. Não foi possível corrigir nomes.")
            
        return df_alagamentos
        
    except Exception as e:
        print(f"Erro ao corrigir nomes de municípios: {str(e)}")
        traceback.print_exc()
        return df_alagamentos

# Prompt 13: Salvar Dados Limpos (Alagamentos)
def save_clean_flooding(df_alagamentos):
    try:
        # Criar pasta de dados se não existir
        os.makedirs('data', exist_ok=True)
        
        if not df_alagamentos.empty:
            df_alagamentos.to_csv('data/relatorios_alagamentos_limpos.csv', index=False)
            print(f"Dados de alagamentos salvos: {len(df_alagamentos)} registros")
        else:
            print("DataFrame de alagamentos vazio. Nenhum dado salvo.")
            
    except Exception as e:
        print(f"Erro ao salvar dados limpos de alagamentos: {str(e)}")
        traceback.print_exc()

# Prompt 14: Mesclar Dados
def merge_data(df_alagamentos, daily_rain):
    try:
        if df_alagamentos.empty or daily_rain.empty:
            print("Um ou ambos os DataFrames estão vazios. Não é possível mesclar dados.")
            return pd.DataFrame()
            
        print("Colunas em df_alagamentos:", df_alagamentos.columns.tolist())
        print("Colunas em daily_rain:", daily_rain.columns.tolist())
        
        if 'Municipio' in df_alagamentos.columns and 'Date' in df_alagamentos.columns and \
           'Municipio' in daily_rain.columns and 'Date' in daily_rain.columns:
            
            # Padronizar os nomes dos municípios em ambos os DataFrames
            df_alagamentos['Municipio'] = df_alagamentos['Municipio'].str.upper().str.strip()
            daily_rain['Municipio'] = daily_rain['Municipio'].str.upper().str.strip()
            
            # Antes de mesclar, imprima alguns exemplos de valores
            print("Exemplos de Municipio em alagamentos:", df_alagamentos['Municipio'].unique()[:5])
            print("Exemplos de Municipio em chuvas:", daily_rain['Municipio'].unique()[:5])
            
            # Mesclar por Municipio e Date para ser mais preciso
            merged = pd.merge(
                df_alagamentos, 
                daily_rain, 
                on=['Municipio', 'Date'], 
                how='left',
                suffixes=('_alag', '_chuva')
            )
            
            print(f"Dados mesclados: {len(merged)} registros")
            
            # Criar pasta de dados se não existir
            os.makedirs('data', exist_ok=True)
            
            # Salvar dados mesclados
            merged.to_csv('data/alagamentos_com_precipitacao.csv', index=False)
            print("Dados detalhados salvos em 'data/alagamentos_com_precipitacao.csv' para análise manual")
            
            return merged
        else:
            print("Colunas necessárias para mesclagem não encontradas.")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Erro ao mesclar dados: {str(e)}")
        traceback.print_exc()
        return pd.DataFrame()

# Prompt 15: Analisar Precipitação em Dias de Alagamento
def analyze_flood_rainfall(merged):
    try:
        if merged.empty:
            print("DataFrame mesclado vazio. Não é possível analisar dados.")
            return {}
            
        if 'COBRADE' in merged.columns and 'precipitacao_diaria' in merged.columns:
            flood_days = merged[merged['COBRADE'] == '12300 - Alagamentos']
            
            if flood_days.empty or flood_days['precipitacao_diaria'].isna().all():
                print("Sem dados válidos para análise.")
                return {}
                
            stats = {
                'Média': flood_days['precipitacao_diaria'].mean(),
                'Mediana': flood_days['precipitacao_diaria'].median(),
                'Mínimo': flood_days['precipitacao_diaria'].min(),
                'Máximo': flood_days['precipitacao_diaria'].max()
            }
            
            print("Estatísticas da precipitação em dias de alagamento:")
            for key, value in stats.items():
                print(f"{key}: {value:.2f} mm")

            return stats
        else:
            print("Colunas necessárias não encontradas. Não é possível analisar dados.")
            return {}
            
    except Exception as e:
        print(f"Erro ao analisar precipitação em dias de alagamento: {str(e)}")
        traceback.print_exc()
        return {}

# Prompt 16: Inserir Dados no PostgreSQL
def insert_into_postgres(df_chuvas, daily_rain, df_alagamentos, merged):
    try:
        print("Iniciando conexão com PostgreSQL...")
        
        # Verificar se os DataFrames estão vazios
        if df_chuvas.empty and daily_rain.empty and df_alagamentos.empty and merged.empty:
            print("Todos os DataFrames estão vazios. Não é possível inserir dados.")
            return
        
        # Tentar conectar ao PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        
        cursor = conn.cursor()
        print("Conectado ao PostgreSQL com sucesso!")
        
        # Limpar tabelas existentes
        try:
            cursor.execute("TRUNCATE TABLE chuvas_diarias, alagamentos, chuvas_alagamentos CASCADE;")
            print("Tabelas limpas com sucesso.")
        except Exception as trunc_error:
            print(f"Aviso ao limpar tabelas: {str(trunc_error)}")
            
        # Inserir dados de chuvas diárias
        if not daily_rain.empty:
            try:
                print("Inserindo dados de chuvas diárias...")
                
                # Preparar dados para inserção
                data_tuples = []
                for _, row in daily_rain.iterrows():
                    data_tuples.append((
                        row['Municipio'],
                        row['UF'],
                        row['Date'],
                        float(row['precipitacao_diaria'])
                    ))
                
                # Usar execute_values para inserção em lote
                query = """
                    INSERT INTO chuvas_diarias (municipio, estado, data, precipitacao) 
                    VALUES %s
                """
                execute_values(cursor, query, data_tuples)
                conn.commit()
                print(f"{len(data_tuples)} registros inseridos em chuvas_diarias.")
            except Exception as insert_error:
                print(f"Erro ao inserir dados em chuvas_diarias: {str(insert_error)}")
                conn.rollback()
        
        # Inserir dados de alagamentos
        if not df_alagamentos.empty:
            try:
                print("Inserindo dados de alagamentos...")
                
                # Verificar colunas necessárias
                pop_col = None
                mortos_col = None
                
                for col in df_alagamentos.columns:
                    if 'POPULA' in col.upper():
                        pop_col = col
                    elif 'MORTOS' in col.upper():
                        mortos_col = col
                
                # Preparar dados para inserção
                data_tuples = []
                for _, row in df_alagamentos.iterrows():
                    data_tuples.append((
                        row['Municipio'],
                        row['UF'] if 'UF' in row else '',
                        row['Date'],
                        float(row[pop_col]) if pop_col else 0,
                        float(row[mortos_col]) if mortos_col else 0
                    ))
                
                # Usar execute_values para inserção em lote
                query = """
                    INSERT INTO alagamentos (municipio, estado, data, populacao, mortos) 
                    VALUES %s
                """
                execute_values(cursor, query, data_tuples)
                conn.commit()
                print(f"{len(data_tuples)} registros inseridos em alagamentos.")
            except Exception as insert_error:
                print(f"Erro ao inserir dados de alagamentos: {str(insert_error)}")
                conn.rollback()
        
        # Conexão com PostgreSQL fechada
        cursor.close()
        conn.close()
        print("Conexão com PostgreSQL fechada.")
        
    except Exception as e:
        print(f"Erro ao inserir dados no PostgreSQL: {str(e)}")
        traceback.print_exc()

# Função Principal
def main():
    try:
        print("===== PROCESSAMENTO DE DADOS =====")
        
        # Processar chuvas
        print("\n===== PROCESSAMENTO DE DADOS DE CHUVAS =====")
        df_chuvas = load_rainfall_data()
        df_chuvas = combine_date_time(df_chuvas)
        df_chuvas = filter_rj_sp(df_chuvas)
        df_chuvas = handle_missing_rainfall(df_chuvas)
        df_chuvas = remove_duplicates_rainfall(df_chuvas)
        daily_rain = aggregate_daily_rainfall(df_chuvas)
        save_clean_rainfall(df_chuvas, daily_rain)
        
        # Processar alagamentos
        print("\n===== PROCESSAMENTO DE DADOS DE ALAGAMENTOS =====")
        df_alagamentos = load_flooding_data()
        df_alagamentos = filter_alagamentos(df_alagamentos)
        df_alagamentos = standardize_dates_flooding(df_alagamentos)
        df_alagamentos = handle_missing_flooding(df_alagamentos)
        df_alagamentos = clean_municipio_names(df_alagamentos)
        save_clean_flooding(df_alagamentos)
        
        # Mesclar e analisar
        print("\n===== MESCLAGEM E ANÁLISE DE DADOS =====")
        merged = merge_data(df_alagamentos, daily_rain)
        stats = analyze_flood_rainfall(merged)
        
        # Inserir no PostgreSQL
        print("\n===== INSERÇÃO NO POSTGRESQL =====")
        insert_into_postgres(df_chuvas, daily_rain, df_alagamentos, merged)
        
        print("\n===== PROCESSAMENTO CONCLUÍDO =====")
        
    except Exception as e:
        print(f"Erro no processamento principal: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    main()