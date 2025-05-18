#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para atualizar previsões de chuva diariamente, 
buscando dados de uma API externa de previsão do tempo.
Deve ser executado como um job agendado (cron, Windows Task Scheduler).
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("update_previsao.log"),
        logging.StreamHandler()
    ]
)

# Adicionar diretório pai ao path para importar módulos da API
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Importar configurações do banco
from api.config import DB_CONFIG

# Configurações da API de previsão do tempo
# Substitua pela sua chave de API real
API_KEY = os.getenv('API_CLIMATEMPO_KEY', '')

# Lista de cidades a serem monitoradas
CIDADES = [
    {'nome': 'Rio de Janeiro', 'estado': 'RJ', 'id_api': '5959'},
    {'nome': 'Niterói', 'estado': 'RJ', 'id_api': '5894'},
    {'nome': 'São Paulo', 'estado': 'SP', 'id_api': '3477'},
    {'nome': 'Campinas', 'estado': 'SP', 'id_api': '4750'}
]

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

def obter_previsao_api(cidade_id):
    """
    Obtém previsão de chuva da API do Climatempo
    
    Args:
        cidade_id (str): ID da cidade na API do Climatempo
        
    Returns:
        list: Lista de previsões para os próximos 7 dias
    """
    if not API_KEY:
        logging.warning("Chave de API não configurada. Usando dados simulados.")
        return None
        
    url = f"http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/{cidade_id}/days/15?token={API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            previsoes = []
            
            # Extrair dados de chuva dos próximos dias
            for dia in data.get('data', []):
                previsoes.append({
                    'data': dia['date'],
                    'precipitacao': dia['rain']['precipitation']
                })
            
            return previsoes
        else:
            logging.error(f"Erro ao acessar API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"Erro na requisição à API: {e}")
        return None

def gerar_dados_simulados(cidade, dias=7):
    """
    Gera dados simulados para testes quando a API não está disponível
    
    Args:
        cidade (dict): Informações da cidade
        dias (int): Número de dias para gerar previsão
        
    Returns:
        list: Lista de previsões simuladas
    """
    import random
    
    previsoes = []
    hoje = datetime.now().date()
    
    # Coeficiente para simular variações regionais
    coef = 1.2 if cidade['estado'] == 'RJ' else 0.8
    
    for i in range(dias):
        data = hoje + timedelta(days=i)
        
        # Simular variação sazonal (mais chuva no verão)
        mes = data.month
        if 12 <= mes <= 12 or 1 <= mes <= 3:  # Verão
            base_precip = random.uniform(5, 25) * coef
        else:
            base_precip = random.uniform(0, 15) * coef
            
        # Adicionar alguns picos de chuva
        if i == 2 or i == 5:  # Criar dois dias de chuva mais intensa
            base_precip *= 2
            
        previsoes.append({
            'data': data.strftime('%Y-%m-%d'),
            'precipitacao': round(base_precip, 1)
        })
    
    return previsoes

def salvar_previsoes(cidade, previsoes):
    """
    Salva as previsões de chuva no banco de dados
    
    Args:
        cidade (dict): Informações da cidade
        previsoes (list): Lista de previsões para os próximos dias
        
    Returns:
        bool: True se sucesso, False caso contrário
    """
    conn = conectar_banco()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        # Preparar dados para inserção
        registros = []
        for previsao in previsoes:
            # Converter string de data para objeto datetime se necessário
            if isinstance(previsao['data'], str):
                data = datetime.strptime(previsao['data'], '%Y-%m-%d').date()
            else:
                data = previsao['data']
                
            registros.append((
                cidade['nome'],
                cidade['estado'],
                data,
                float(previsao['precipitacao']),
                'API_CLIMATEMPO' if API_KEY else 'SIMULAÇÃO'
            ))
        
        # Inserir dados com upsert (atualizar se já existir)
        query = """
        INSERT INTO chuvas_diarias 
            (municipio, estado, data, precipitacao_diaria, fonte)
        VALUES %s
        ON CONFLICT (municipio, data) DO UPDATE SET
            precipitacao_diaria = EXCLUDED.precipitacao_diaria,
            fonte = EXCLUDED.fonte,
            data_atualizacao = CURRENT_TIMESTAMP
        """
        
        execute_values(cursor, query, registros)
        conn.commit()
        
        logging.info(f"Previsões para {cidade['nome']}/{cidade['estado']} atualizadas com sucesso.")
        return True
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao salvar previsões para {cidade['nome']}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """Função principal para atualizar previsões de todas as cidades"""
    logging.info("Iniciando atualização de previsões de chuva...")
    
    for cidade in CIDADES:
        logging.info(f"Processando cidade: {cidade['nome']}/{cidade['estado']}")
        
        # Tenta obter dados da API
        if API_KEY:
            previsoes = obter_previsao_api(cidade['id_api'])
        else:
            previsoes = None
            
        # Se não conseguir, usa dados simulados
        if not previsoes:
            logging.info(f"Usando dados simulados para {cidade['nome']}")
            previsoes = gerar_dados_simulados(cidade)
            
        # Salva no banco de dados
        if previsoes:
            sucesso = salvar_previsoes(cidade, previsoes)
            if not sucesso:
                logging.warning(f"Falha ao salvar previsões para {cidade['nome']}")
        else:
            logging.error(f"Não foi possível obter previsões para {cidade['nome']}")
    
    logging.info("Atualização de previsões concluída.")

if __name__ == "__main__":
    main() 