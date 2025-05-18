#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para analisar a relação entre volume de chuvas e ocorrências de alagamentos.
Este script busca dados históricos no banco e calcula limiares de precipitação
que aumentam a probabilidade de alagamentos em cada região.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import psycopg2
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("relacao_chuvas_alagamentos.log"),
        logging.StreamHandler()
    ]
)

# Adicionar diretório pai ao path para importar módulos da API
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Importar configurações do banco
from api.config import DB_CONFIG

def conectar_banco():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco: {e}")
        return None

def obter_dados_historicos():
    """
    Obtém dados históricos de chuvas e alagamentos do banco de dados
    
    Returns:
        tuple: (df_chuvas, df_alagamentos) ou (None, None) em caso de erro
    """
    conn = conectar_banco()
    if not conn:
        return None, None
        
    try:
        # Obter dados de chuvas
        query_chuvas = """
        SELECT 
            municipio, 
            estado, 
            data, 
            precipitacao_diaria
        FROM 
            chuvas_diarias 
        ORDER BY 
            municipio, data
        """
        
        df_chuvas = pd.read_sql(query_chuvas, conn)
        
        # Obter dados de alagamentos
        query_alagamentos = """
        SELECT 
            municipio, 
            estado, 
            data, 
            local,
            nivel_gravidade,
            dh_afetados
        FROM 
            alagamentos 
        ORDER BY 
            municipio, data
        """
        
        df_alagamentos = pd.read_sql(query_alagamentos, conn)
        
        logging.info(f"Obtidos {len(df_chuvas)} registros de chuvas e {len(df_alagamentos)} de alagamentos")
        return df_chuvas, df_alagamentos
        
    except Exception as e:
        logging.error(f"Erro ao obter dados históricos: {e}")
        return None, None
    finally:
        conn.close()

def preparar_dados_para_analise(df_chuvas, df_alagamentos):
    """
    Prepara os dados para análise, criando um dataset combinado
    
    Args:
        df_chuvas (pd.DataFrame): DataFrame com dados de chuvas
        df_alagamentos (pd.DataFrame): DataFrame com dados de alagamentos
        
    Returns:
        pd.DataFrame: DataFrame combinado para análise
    """
    # Verificar se temos dados suficientes
    if df_chuvas.empty or df_alagamentos.empty:
        logging.error("Dados insuficientes para análise")
        return None
    
    # Converter datas para o mesmo formato
    df_chuvas['data'] = pd.to_datetime(df_chuvas['data'])
    df_alagamentos['data'] = pd.to_datetime(df_alagamentos['data'])
    
    # Criar coluna de dia anterior para análise de chuva dos dias anteriores
    df_chuvas['dia_anterior'] = df_chuvas['data'] - timedelta(days=1)
    
    # Criar dataframe combinado
    df_combinado = pd.DataFrame()
    
    # Lista de cidades para análise
    cidades = df_chuvas['municipio'].unique()
    
    for cidade in cidades:
        # Filtrar dados para a cidade
        chuvas_cidade = df_chuvas[df_chuvas['municipio'] == cidade].copy()
        alagamentos_cidade = df_alagamentos[df_alagamentos['municipio'] == cidade].copy()
        
        if chuvas_cidade.empty or alagamentos_cidade.empty:
            logging.warning(f"Dados insuficientes para a cidade {cidade}")
            continue
            
        # Criar coluna indicando se houve alagamento naquela data
        datas_alagamentos = set(alagamentos_cidade['data'].dt.date)
        chuvas_cidade['houve_alagamento'] = chuvas_cidade['data'].dt.date.apply(
            lambda x: 1 if x in datas_alagamentos else 0
        )
        
        # Adicionar chuva do dia anterior
        chuvas_cidade = chuvas_cidade.merge(
            chuvas_cidade[['data', 'precipitacao_diaria']],
            left_on='dia_anterior',
            right_on='data',
            how='left',
            suffixes=('', '_anterior')
        )
        
        # Adicionar a média móvel de 3 dias
        chuvas_cidade['media_3_dias'] = chuvas_cidade.sort_values('data').groupby('municipio')['precipitacao_diaria'].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )
        
        # Adicionar ao dataframe combinado
        df_combinado = pd.concat([df_combinado, chuvas_cidade])
    
    # Limpar e preparar dataframe final
    if not df_combinado.empty:
        colunas = ['municipio', 'estado', 'data', 'precipitacao_diaria', 
                   'precipitacao_diaria_anterior', 'media_3_dias', 'houve_alagamento']
        df_final = df_combinado[colunas].dropna()
        
        logging.info(f"Dataset combinado criado com {len(df_final)} registros")
        return df_final
    else:
        logging.error("Não foi possível criar dataset combinado")
        return None

def analisar_relacao(df):
    """
    Analisa a relação entre chuvas e alagamentos
    
    Args:
        df (pd.DataFrame): DataFrame combinado para análise
        
    Returns:
        dict: Dicionário com resultados da análise
    """
    if df is None or df.empty:
        return None
    
    resultados = {}
    
    # Analisar por cidade
    for cidade in df['municipio'].unique():
        df_cidade = df[df['municipio'] == cidade].copy()
        
        if len(df_cidade) < 30:  # Verificar se há dados suficientes
            logging.warning(f"Dados insuficientes para análise estatística em {cidade}")
            continue
            
        estado = df_cidade['estado'].iloc[0]
        
        # Estatísticas básicas
        media_chuva_com_alagamento = df_cidade[df_cidade['houve_alagamento'] == 1]['precipitacao_diaria'].mean()
        media_chuva_sem_alagamento = df_cidade[df_cidade['houve_alagamento'] == 0]['precipitacao_diaria'].mean()
        media_3dias_com_alagamento = df_cidade[df_cidade['houve_alagamento'] == 1]['media_3_dias'].mean()
        
        # Encontrar limiar com regressão logística
        X = df_cidade[['precipitacao_diaria', 'media_3_dias']]
        y = df_cidade['houve_alagamento']
        
        try:
            # Divisão treino/teste
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
            
            # Treinar modelo
            model = LogisticRegression(class_weight='balanced')
            model.fit(X_train, y_train)
            
            # Avaliar modelo
            y_pred = model.predict(X_test)
            accuracy = (y_pred == y_test).mean()
            
            # Encontrar limiar de precipitação com 70% de probabilidade de alagamento
            coef = model.coef_[0]
            intercept = model.intercept_[0]
            
            # Para probabilidade de 0.7: log(0.7/0.3) = coef[0]*x + coef[1]*media + intercept
            # Considerando média igual à precipitação (dia chuvoso constante)
            log_odds = np.log(0.7/0.3)
            limiar_precipitacao = (log_odds - intercept) / (coef[0] + coef[1])
            
            # Armazenar resultados
            resultados[cidade] = {
                'estado': estado,
                'media_chuva_com_alagamento': round(media_chuva_com_alagamento, 2),
                'media_chuva_sem_alagamento': round(media_chuva_sem_alagamento, 2),
                'media_3dias_com_alagamento': round(media_3dias_com_alagamento, 2),
                'limiar_precipitacao': round(max(20, limiar_precipitacao), 2),
                'accuracy_modelo': round(accuracy, 2),
                'coeficientes': coef.tolist(),
                'intercept': float(intercept)
            }
            
            logging.info(f"Análise para {cidade}/{estado}: Limiar de precipitação = {resultados[cidade]['limiar_precipitacao']:.2f}mm")
            
        except Exception as e:
            logging.error(f"Erro na análise para {cidade}: {e}")
    
    return resultados

def salvar_resultados(resultados):
    """
    Salva os resultados da análise no banco de dados
    
    Args:
        resultados (dict): Resultados da análise
        
    Returns:
        bool: True se sucesso, False caso contrário
    """
    if not resultados:
        return False
        
    conn = conectar_banco()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        # Criar tabela se não existir
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS parametros_alagamento (
            id SERIAL PRIMARY KEY,
            municipio VARCHAR(100) NOT NULL,
            estado CHAR(2) NOT NULL,
            limiar_precipitacao NUMERIC(6,2) NOT NULL,
            media_historica NUMERIC(6,2),
            coeficiente_diario NUMERIC(10,6),
            coeficiente_media NUMERIC(10,6),
            intercepto NUMERIC(10,6),
            precisao_modelo NUMERIC(5,2),
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT uq_param_cidade UNIQUE (municipio)
        )
        """)
        
        # Inserir/atualizar dados para cada cidade
        for cidade, dados in resultados.items():
            query = """
            INSERT INTO parametros_alagamento 
                (municipio, estado, limiar_precipitacao, media_historica, 
                coeficiente_diario, coeficiente_media, intercepto, precisao_modelo)
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (municipio) DO UPDATE SET
                limiar_precipitacao = EXCLUDED.limiar_precipitacao,
                media_historica = EXCLUDED.media_historica,
                coeficiente_diario = EXCLUDED.coeficiente_diario,
                coeficiente_media = EXCLUDED.coeficiente_media,
                intercepto = EXCLUDED.intercepto,
                precisao_modelo = EXCLUDED.precisao_modelo,
                data_atualizacao = CURRENT_TIMESTAMP
            """
            
            cursor.execute(query, (
                cidade,
                dados['estado'],
                dados['limiar_precipitacao'],
                dados['media_chuva_com_alagamento'],
                dados['coeficientes'][0],
                dados['coeficientes'][1],
                dados['intercept'],
                dados['accuracy_modelo']
            ))
        
        conn.commit()
        logging.info(f"Resultados salvos para {len(resultados)} cidades")
        return True
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao salvar resultados: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def criar_visualizacao(df, resultados):
    """
    Cria visualização da relação entre chuvas e alagamentos
    
    Args:
        df (pd.DataFrame): DataFrame combinado para análise
        resultados (dict): Resultados da análise
    """
    if df is None or df.empty or not resultados:
        return
        
    try:
        # Criar diretório para gráficos se não existir
        graficos_dir = os.path.join(BASE_DIR, 'data', 'graficos')
        os.makedirs(graficos_dir, exist_ok=True)
        
        # Selecionar cidades com dados suficientes
        for cidade in df['municipio'].unique():
            if cidade not in resultados:
                continue
                
            df_cidade = df[df['municipio'] == cidade].copy()
            limiar = resultados[cidade]['limiar_precipitacao']
            
            plt.figure(figsize=(10, 6))
            
            # Scatter plot de precipitação x média móvel, colorido por ocorrência de alagamento
            plt.scatter(df_cidade[df_cidade['houve_alagamento']==0]['precipitacao_diaria'], 
                      df_cidade[df_cidade['houve_alagamento']==0]['media_3_dias'],
                      alpha=0.5, label='Sem alagamento')
            
            plt.scatter(df_cidade[df_cidade['houve_alagamento']==1]['precipitacao_diaria'], 
                      df_cidade[df_cidade['houve_alagamento']==1]['media_3_dias'],
                      alpha=0.7, color='red', label='Com alagamento')
            
            # Adicionar linha de limiar
            plt.axhline(y=limiar, color='r', linestyle='--', alpha=0.7, 
                      label=f'Limiar: {limiar:.1f}mm')
            
            plt.title(f'Relação entre Precipitação e Alagamentos - {cidade}')
            plt.xlabel('Precipitação Diária (mm)')
            plt.ylabel('Média Móvel 3 dias (mm)')
            plt.legend()
            plt.grid(alpha=0.3)
            
            # Salvar gráfico
            plt.savefig(os.path.join(graficos_dir, f'relacao_chuva_alagamento_{cidade}.png'))
            plt.close()
            
        logging.info(f"Visualizações salvas em {graficos_dir}")
        
    except Exception as e:
        logging.error(f"Erro ao criar visualizações: {e}")

def main():
    """Função principal para análise de relação entre chuvas e alagamentos"""
    logging.info("Iniciando análise de relação entre chuvas e alagamentos...")
    
    # Obter dados históricos
    df_chuvas, df_alagamentos = obter_dados_historicos()
    
    if df_chuvas is None or df_alagamentos is None:
        logging.error("Não foi possível obter dados para análise")
        return
    
    # Preparar dados para análise
    df_combinado = preparar_dados_para_analise(df_chuvas, df_alagamentos)
    
    if df_combinado is None:
        logging.error("Não foi possível preparar dados para análise")
        return
    
    # Analisar relação
    resultados = analisar_relacao(df_combinado)
    
    if not resultados:
        logging.error("Não foi possível analisar a relação entre chuvas e alagamentos")
        return
    
    # Salvar resultados
    salvar_resultados(resultados)
    
    # Criar visualizações
    criar_visualizacao(df_combinado, resultados)
    
    logging.info("Análise de relação entre chuvas e alagamentos concluída")
    
    # Imprimir resumo dos resultados
    print("\nResumo dos resultados:")
    print("======================")
    for cidade, dados in resultados.items():
        print(f"\n{cidade}/{dados['estado']}:")
        print(f"  Limiar de precipitação para alerta: {dados['limiar_precipitacao']:.1f}mm")
        print(f"  Média histórica em dias com alagamento: {dados['media_chuva_com_alagamento']:.1f}mm")
        print(f"  Precisão do modelo: {dados['accuracy_modelo'] * 100:.1f}%")

if __name__ == "__main__":
    main() 