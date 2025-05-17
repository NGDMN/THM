import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
import cx_Oracle
import traceback

# Prompt 1: Carregar Dados Meteorológicos
def load_rainfall_data(directory="C:\\Users\\Neil\\OneDrive\\Python\\Projetos\\THM\\Chuvas"):
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
        print("Dados de chuva carregados:")
        print(df_chuvas.head())
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
            
        print("Data e hora combinadas:")
        print(df_chuvas[['Data', 'Datetime']].head())
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
            print("Valores ausentes antes:")
            print(df_chuvas[precip_col].isna().sum())
            df_chuvas[precip_col] = df_chuvas[precip_col].fillna(0)
            print("Valores ausentes após:")
            print(df_chuvas[precip_col].isna().sum())
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
            print(f"Registros após: {len(df_chuvas)}")
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
        daily_rain = daily_rain.rename(columns={precip_col: 'Precipitação Diária (mm)'})
        
        print("Totais diários de chuva:")
        print(daily_rain.head())
        return daily_rain
        
    except Exception as e:
        print(f"Erro ao agregar dados de chuva: {str(e)}")
        traceback.print_exc()
        return pd.DataFrame()

# Prompt 7: Salvar Dados Limpos (Chuva)
def save_clean_rainfall(df_chuvas, daily_rain):
    try:
        if not df_chuvas.empty:
            df_chuvas.to_csv('dados_meteorologicos_limpos.csv', index=False)
            print(f"Dados de chuva salvos: {len(df_chuvas)} registros")
            
        if not daily_rain.empty:
            daily_rain.to_csv('chuvas_diarias_limpos.csv', index=False)
            print(f"Dados diários de chuva salvos: {len(daily_rain)} registros")
            
    except Exception as e:
        print(f"Erro ao salvar dados limpos de chuva: {str(e)}")
        traceback.print_exc()

# Prompt 8: Carregar Dados de Alagamentos
def load_flooding_data(directory="C:\\Users\\Neil\\OneDrive\\Python\\Projetos\\THM\\Alagamentos"):
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
        print("Dados de alagamentos carregados:")
        print(df_alagamentos.head())
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
                print("Datas padronizadas do campo Registro:")
                print(df_alagamentos[['Registro', 'Date']].head())
            except Exception as date_error:
                print(f"Erro ao converter datas do Registro: {str(date_error)}")
                print("Tentando outro formato de data...")
                try:
                    df_alagamentos['Date'] = pd.to_datetime(df_alagamentos['Registro'], errors='coerce').dt.date
                    print("Datas padronizadas com formato automático:")
                    print(df_alagamentos[['Registro', 'Date']].head())
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
            print("Valores ausentes antes:")
            print(df_alagamentos[[pop_col, mortos_col]].isna().sum())
            df_alagamentos[[pop_col, mortos_col]] = df_alagamentos[[pop_col, mortos_col]].fillna(0)
            print("Valores ausentes após:")
            print(df_alagamentos[[pop_col, mortos_col]].isna().sum())
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
            print("Nomes de municípios corrigidos:")
            print(df_alagamentos['Municipio'].head())
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
        if not df_alagamentos.empty:
            df_alagamentos.to_csv('relatorios_alagamentos_limpos.csv', index=False)
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
            
            # Mesclar por Municipio, UF e Date para ser mais preciso
            merged = pd.merge(
                df_alagamentos, 
                daily_rain, 
                on=['Municipio', 'Date'], 
                how='left',
                suffixes=('_alag', '_chuva')
            )
            
            print("Dados mesclados:")
            print(merged[['Municipio', 'Date', 'Precipitação Diária (mm)']].head())
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
            
        if 'COBRADE' in merged.columns and 'Precipitação Diária (mm)' in merged.columns:
            flood_days = merged[merged['COBRADE'] == '12300 - Alagamentos']
            
            if flood_days.empty or flood_days['Precipitação Diária (mm)'].isna().all():
                print("Sem dados válidos para análise.")
                return {}
                
            stats = {
                'Média': flood_days['Precipitação Diária (mm)'].mean(),
                'Mediana': flood_days['Precipitação Diária (mm)'].median(),
                'Mínimo': flood_days['Precipitação Diária (mm)'].min(),
                'Máximo': flood_days['Precipitação Diária (mm)'].max()
            }
            
            print("Estatísticas da precipitação em dias de alagamento:")
            for key, value in stats.items():
                print(f"{key}: {value:.2f} mm")
                
            # Criar gráficos mais informativos
            try:
                plt.figure(figsize=(15, 10))
                
                # Subplot 1: Histograma
                plt.subplot(2, 2, 1)
                plt.hist(flood_days['Precipitação Diária (mm)'].dropna(), bins=10, color='skyblue', edgecolor='black')
                plt.title('Distribuição da Precipitação em Dias de Alagamento')
                plt.xlabel('Precipitação Diária (mm)')
                plt.ylabel('Frequência')
                plt.grid(True, alpha=0.3)
                
                # Subplot 2: Gráfico de barras por município
                plt.subplot(2, 2, 2)
                muni_rain = flood_days.groupby('Municipio')['Precipitação Diária (mm)'].mean().sort_values(ascending=False)
                muni_rain = muni_rain.head(10)  # Top 10 municípios
                muni_rain.plot(kind='bar', color='lightgreen')
                plt.title('Média de Precipitação por Município em Dias de Alagamento')
                plt.xlabel('Município')
                plt.ylabel('Precipitação Média (mm)')
                plt.xticks(rotation=45, ha='right')
                plt.grid(True, alpha=0.3)
                
                # Subplot 3: Gráfico de dispersão entre população afetada e precipitação
                plt.subplot(2, 2, 3)
                if 'População' in flood_days.columns:
                    plt.scatter(flood_days['Precipitação Diária (mm)'], flood_days['População'], alpha=0.6, color='coral')
                    plt.title('Relação entre Precipitação e População Afetada')
                    plt.xlabel('Precipitação Diária (mm)')
                    plt.ylabel('População Afetada')
                    plt.grid(True, alpha=0.3)
                
                # Subplot 4: Boxplot
                plt.subplot(2, 2, 4)
                if 'UF' in flood_days.columns:
                    flood_days.boxplot(column='Precipitação Diária (mm)', by='UF')
                    plt.title('Distribuição de Precipitação por Estado')
                    plt.suptitle('')  # Remove o título automático
                    plt.xlabel('Estado')
                    plt.ylabel('Precipitação Diária (mm)')
                    plt.grid(True, alpha=0.3)
                
                plt.tight_layout()
                plt.savefig('precipitacao_alagamentos.png')
                print("Gráficos detalhados salvos como 'precipitacao_alagamentos.png'")
                
                # Adicional: Gerar CSV com todos os dados mesclados para análise manual
                flood_days.to_csv('alagamentos_com_precipitacao.csv', index=False)
                print("Dados detalhados salvos em 'alagamentos_com_precipitacao.csv' para análise manual")
                
            except Exception as plt_error:
                print(f"Erro ao criar gráfico: {str(plt_error)}")
                
            return stats
        else:
            print("Colunas necessárias não encontradas. Não é possível analisar dados.")
            return {}
            
    except Exception as e:
        print(f"Erro ao analisar precipitação em dias de alagamento: {str(e)}")
        traceback.print_exc()
        return {}

# Prompt 16: Inserir Dados no Oracle SQL
def insert_into_oracle(df_chuvas, daily_rain, df_alagamentos, merged, connection_string):
    try:
        print("Iniciando conexão com Oracle SQL...")
        
        # Configurar local do wallet (importante para conexão segura)
        wallet_location = r'C:\Users\Neil\OracleWallet'  # Caminho fornecido pelo usuário
        os.environ['TNS_ADMIN'] = wallet_location
        print(f"Wallet configurado em: {wallet_location}")
        
        # Adicionar o Oracle Client ao PATH temporariamente
        oracle_client_path = r'C:\Oracle\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8'
        if oracle_client_path not in os.environ['PATH']:
            os.environ['PATH'] = oracle_client_path + os.pathsep + os.environ['PATH']
            print(f"Oracle Client adicionado ao PATH temporariamente: {oracle_client_path}")
            
        # Inicializar o Oracle Client explicitamente
        try:
            cx_Oracle.init_oracle_client(lib_dir=oracle_client_path)
            print("Oracle Client inicializado com sucesso!")
        except Exception as init_error:
            if "already initialized" in str(init_error):
                print("Oracle Client já estava inicializado!")
            else:
                print(f"Atenção: {str(init_error)}")
                print("Tentando seguir com a conexão mesmo assim...")
        
        # Verificar se os DataFrames estão vazios
        if df_chuvas.empty or daily_rain.empty or df_alagamentos.empty or merged.empty:
            print("Um ou mais DataFrames estão vazios. Não é possível inserir todos os dados.")
            return
            
        # Tentar conectar ao Oracle
        try:
            connection = cx_Oracle.connect(connection_string)
            cursor = connection.cursor()
            print("Conectado ao Oracle SQL com sucesso!")
        except Exception as conn_error:
            print(f"Erro ao conectar ao Oracle SQL: {str(conn_error)}")
            print("Pulando inserção de dados no Oracle.")
            return
            
        # Criar tabelas (com tratamento de erro)
        try:
            cursor.execute("""
                CREATE TABLE chuvas_diarias (
                    municipio VARCHAR2(100),
                    data DATE,
                    precipitacao_diaria NUMBER
                )
            """)
            print("Tabela chuvas_diarias criada com sucesso.")
        except Exception as table1_error:
            print(f"Erro ao criar tabela chuvas_diarias: {str(table1_error)}")
            print("A tabela pode já existir. Continuando...")
            
        try:
            cursor.execute("""
                CREATE TABLE alagamentos (
                    municipio VARCHAR2(100),
                    data DATE,
                    populacao NUMBER,
                    dh_mortos NUMBER
                )
            """)
            print("Tabela alagamentos criada com sucesso.")
        except Exception as table2_error:
            print(f"Erro ao criar tabela alagamentos: {str(table2_error)}")
            print("A tabela pode já existir. Continuando...")
            
        try:
            cursor.execute("""
                CREATE TABLE chuvas_alagamentos (
                    municipio VARCHAR2(100),
                    data DATE,
                    precipitacao_diaria NUMBER,
                    populacao NUMBER,
                    dh_mortos NUMBER
                )
            """)
            print("Tabela chuvas_alagamentos criada com sucesso.")
        except Exception as table3_error:
            print(f"Erro ao criar tabela chuvas_alagamentos: {str(table3_error)}")
            print("A tabela pode já existir. Continuando...")
        
        # Verificar colunas necessárias
        pop_col = None
        mortos_col = None
        
        for col in df_alagamentos.columns:
            if 'POPULA' in col.upper():
                pop_col = col
            elif 'MORTOS' in col.upper():
                mortos_col = col
                
        # Inserir dados
        records_inserted = 0
        try:
            for _, row in daily_rain.iterrows():
                try:
                    cursor.execute(
                        "INSERT INTO chuvas_diarias (municipio, data, precipitacao_diaria) VALUES (:1, :2, :3)",
                        (row['Municipio'], row['Date'], row['Precipitação Diária (mm)'])
                    )
                    records_inserted += 1
                except Exception as insert_error:
                    print(f"Erro ao inserir linha em chuvas_diarias: {str(insert_error)}")
                    
            print(f"{records_inserted} registros inseridos em chuvas_diarias.")
        except Exception as e:
            print(f"Erro ao inserir dados em chuvas_diarias: {str(e)}")
            
        records_inserted = 0
        try:
            for _, row in df_alagamentos.iterrows():
                try:
                    cursor.execute(
                        "INSERT INTO alagamentos (municipio, data, populacao, dh_mortos) VALUES (:1, :2, :3, :4)",
                        (row['Municipio'], row['Date'], 
                         row[pop_col] if pop_col else 0, 
                         row[mortos_col] if mortos_col else 0)
                    )
                    records_inserted += 1
                except Exception as insert_error:
                    print(f"Erro ao inserir linha em alagamentos: {str(insert_error)}")
                    
            print(f"{records_inserted} registros inseridos em alagamentos.")
        except Exception as e:
            print(f"Erro ao inserir dados em alagamentos: {str(e)}")
            
        records_inserted = 0
        try:
            for _, row in merged.iterrows():
                try:
                    cursor.execute(
                        "INSERT INTO chuvas_alagamentos (municipio, data, precipitacao_diaria, populacao, dh_mortos) VALUES (:1, :2, :3, :4, :5)",
                        (row['Municipio'], row['Date'], 
                         row['Precipitação Diária (mm)'] if 'Precipitação Diária (mm)' in row else 0, 
                         row[pop_col] if pop_col else 0, 
                         row[mortos_col] if mortos_col else 0)
                    )
                    records_inserted += 1
                except Exception as insert_error:
                    print(f"Erro ao inserir linha em chuvas_alagamentos: {str(insert_error)}")
                    
            print(f"{records_inserted} registros inseridos em chuvas_alagamentos.")
        except Exception as e:
            print(f"Erro ao inserir dados em chuvas_alagamentos: {str(e)}")
        
        # Commit e fechar conexão
        try:
            connection.commit()
            print("Alterações confirmadas com sucesso!")
        except Exception as commit_error:
            print(f"Erro ao confirmar alterações: {str(commit_error)}")
            
        cursor.close()
        connection.close()
        print("Conexão com Oracle SQL fechada.")
        
    except Exception as e:
        print(f"Erro ao inserir dados no Oracle SQL: {str(e)}")
        traceback.print_exc()

# Prompt 17: Buscar Previsões de Chuva com OpenWeatherMap
def fetch_weather_forecast(api_key):
    try:
        if not api_key or api_key == "sua_chave_api_openweathermap":
            print("Chave API do OpenWeatherMap não fornecida ou inválida. Pulando busca de previsões.")
            return pd.DataFrame()
            
        import requests
        
        cities = [
            {'name': 'São Paulo', 'lat': -23.55, 'lon': -46.63},
            {'name': 'Rio de Janeiro', 'lat': -22.90, 'lon': -43.17}
        ]
        
        forecasts = []
        for city in cities:
            try:
                url = f"https://api.openweathermap.org/data/2.5/forecast?lat={city['lat']}&lon={city['lon']}&appid={api_key}&units=metric"
                response = requests.get(url)
                
                if response.status_code != 200:
                    print(f"Erro ao buscar previsões para {city['name']}: Código de status {response.status_code}")
                    continue
                    
                data = response.json()
                
                for forecast in data['list']:
                    date = datetime.fromtimestamp(forecast['dt']).date()
                    rain = forecast.get('rain', {}).get('3h', 0)
                    forecasts.append({
                        'Municipio': city['name'].upper(),
                        'Date': date,
                        'Precipitação Prevista (mm)': rain
                    })
                    
                print(f"Previsões para {city['name']} obtidas com sucesso.")
            except Exception as city_error:
                print(f"Erro ao processar previsões para {city['name']}: {str(city_error)}")
                
        if not forecasts:
            print("Nenhuma previsão foi obtida. Retornando DataFrame vazio.")
            return pd.DataFrame()
            
        df_forecast = pd.DataFrame(forecasts)
        df_forecast.to_csv('previsoes_chuva.csv', index=False)
        print("Previsões de chuva salvas:")
        print(df_forecast.head())
        return df_forecast
        
    except Exception as e:
        print(f"Erro ao buscar previsões de chuva: {str(e)}")
        traceback.print_exc()
        return pd.DataFrame()

# Função Principal
def main():
    try:
        print("===== Iniciando processamento de dados =====")
        
        # Processar chuvas
        print("\n===== PROCESSAMENTO DE DADOS DE CHUVA =====")
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
        
        # Inserir no Oracle SQL
        print("\n===== INSERÇÃO NO ORACLE SQL =====")
        # A string de conexão usando o DSN fornecido pelo usuário
        username = "ADMIN"
        password = "Chuvas1Alagamentos"  # Credenciais corretas
        dsn = "chuvasalagamentos_high"
        connection_string = f"{username}/{password}@{dsn}"
        
        # Para usar a conexão Oracle, remova o comentário da linha abaixo
        # e certifique-se de ter configurado o wallet e o cliente Oracle
        insert_into_oracle(df_chuvas, daily_rain, df_alagamentos, merged, connection_string)
        print("Para inserir dados no Oracle SQL, configure seu banco de dados seguindo as instruções em 'Configuração do Oracle Database.md' e descomente a linha acima.")
        
        # Buscar previsões (usando a chave API correta)
        print("\n===== BUSCA DE PREVISÕES DE CHUVA =====")
        api_key = "50508f185d7a5337e4929c8816d2a46e"  # Chave API corrigida
        df_forecast = fetch_weather_forecast(api_key)
        
        print("\n===== PROCESSAMENTO CONCLUÍDO =====")
        
    except Exception as e:
        print(f"Erro no processamento principal: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    main()