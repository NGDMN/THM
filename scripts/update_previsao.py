#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para atualizar previsões de chuva diariamente, 
buscando dados da API Climatempo e atualizar o banco de dados.
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
# Obter chave API do ambiente ou do arquivo de configuração
API_KEY = os.getenv('API_CLIMATEMPO_KEY', '')

# Nível de precipitação para emitir alerta (em mm)
LIMIAR_ALERTA_CHUVA = 30.0  # mm de chuva por dia

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

def obter_municipios_rj_sp():
    """
    Obtém lista de todos os municípios de RJ e SP do banco de dados
    
    Returns:
        list: Lista de dicionários com informações dos municípios
    """
    conn = conectar_banco()
    if not conn:
        return []
        
    cursor = conn.cursor()
    municipios = []
    
    try:
        # Buscar todos os municípios de RJ e SP 
        query = """
        SELECT DISTINCT municipio, estado 
        FROM chuvas_diarias 
        WHERE estado IN ('RJ', 'SP')
        ORDER BY estado, municipio
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        for municipio, estado in resultados:
            municipios.append({
                'nome': municipio,
                'estado': estado,
                'id_api': ''  # Não temos os IDs da API para todos os municípios
            })
            
        # Se não encontrou municípios, incluir ao menos as capitais
        if not municipios:
            municipios = [
                {'nome': 'Rio de Janeiro', 'estado': 'RJ', 'id_api': '5959'},
                {'nome': 'São Paulo', 'estado': 'SP', 'id_api': '3477'}
            ]
        
        return municipios
        
    except Exception as e:
        logging.error(f"Erro ao obter municípios: {e}")
        return [
            {'nome': 'Rio de Janeiro', 'estado': 'RJ', 'id_api': '5959'},
            {'nome': 'São Paulo', 'estado': 'SP', 'id_api': '3477'}
        ]
    finally:
        cursor.close()
        conn.close()

def obter_previsao_api(cidade_id):
    """
    Obtém previsão de chuva da API do Climatempo para os próximos 7 dias
    
    Args:
        cidade_id (str): ID da cidade na API do Climatempo
        
    Returns:
        list: Lista de previsões para os próximos 7 dias
    """
    if not API_KEY:
        logging.warning("Chave de API não configurada. Não é possível obter previsões reais.")
        return None
        
    url = f"http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/{cidade_id}/days/15?token={API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            previsoes = []
            
            # Extrair dados de chuva dos próximos dias (hoje + 6 dias)
            hoje = datetime.now().date()
            contador_dias = 0
            
            for dia in data.get('data', []):
                data_previsao = datetime.strptime(dia['date'], '%Y-%m-%d').date()
                if data_previsao >= hoje and contador_dias < 7:
                    previsoes.append({
                        'data': dia['date'],
                        'precipitacao': dia['rain']['precipitation']
                    })
                    contador_dias += 1
            
            return previsoes
        else:
            logging.error(f"Erro ao acessar API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"Erro na requisição à API: {e}")
        return None

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
                'API_CLIMATEMPO' if API_KEY else 'INPE' # Usar outra fonte se não tiver API Climatempo
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

def verificar_alerta_alagamentos():
    """
    Verifica municípios com risco de alagamentos baseado nas previsões de chuva
    e atualiza a tabela de configuração do sistema com essa informação
    
    Returns:
        list: Lista de municípios com alertas
    """
    conn = conectar_banco()
    if not conn:
        return []
        
    cursor = conn.cursor()
    municipios_alerta = []
    
    try:
        # Buscar municípios com previsão de chuva acima do limiar
        hoje = datetime.now().date()
        proximos_dias = hoje + timedelta(days=6)
        
        query = """
        SELECT municipio, estado, data, precipitacao_diaria
        FROM chuvas_diarias
        WHERE data BETWEEN %s AND %s
        AND precipitacao_diaria >= %s
        ORDER BY data, municipio
        """
        
        cursor.execute(query, (hoje, proximos_dias, LIMIAR_ALERTA_CHUVA))
        resultados = cursor.fetchall()
        
        for municipio, estado, data, precipitacao in resultados:
            municipios_alerta.append({
                'municipio': municipio,
                'estado': estado,
                'data': data.strftime('%Y-%m-%d'),
                'precipitacao': precipitacao
            })
            logging.info(f"ALERTA: {municipio}/{estado} com previsão de {precipitacao}mm para {data}")
        
        # Atualizar configuração do sistema com informação de alerta
        if municipios_alerta:
            # Converter para JSON para armazenar no banco
            json_alerta = json.dumps(municipios_alerta)
            
            query_update = """
            UPDATE configuracao_sistema
            SET valor = %s, data_atualizacao = CURRENT_TIMESTAMP
            WHERE chave = 'ALERTA_ALAGAMENTOS'
            """
            
            cursor.execute(query_update, (json_alerta,))
            
            # Se não existir o registro, criar
            if cursor.rowcount == 0:
                query_insert = """
                INSERT INTO configuracao_sistema (chave, valor, descricao)
                VALUES ('ALERTA_ALAGAMENTOS', %s, 'Municípios com alerta de alagamentos')
                """
                cursor.execute(query_insert, (json_alerta,))
            
            conn.commit()
        else:
            # Se não houver alertas, limpar o valor anterior
            query_update = """
            UPDATE configuracao_sistema
            SET valor = '[]', data_atualizacao = CURRENT_TIMESTAMP
            WHERE chave = 'ALERTA_ALAGAMENTOS'
            """
            cursor.execute(query_update)
            conn.commit()
            
        return municipios_alerta
            
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao verificar alertas de alagamentos: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def main():
    """Função principal para atualizar previsões de todas as cidades"""
    logging.info("Iniciando atualização de previsões de chuva...")
    
    # Obter lista de todos os municípios de RJ e SP
    municipios = obter_municipios_rj_sp()
    logging.info(f"Total de {len(municipios)} municípios encontrados para processamento")
    
    for cidade in municipios:
        logging.info(f"Processando cidade: {cidade['nome']}/{cidade['estado']}")
        
        # Tenta obter dados da API se tiver ID da cidade
        previsoes = None
        if API_KEY and cidade.get('id_api'):
            previsoes = obter_previsao_api(cidade['id_api'])
            
        # Se não conseguir dados da API, pular cidade
        if not previsoes:
            logging.warning(f"Sem dados de previsão para {cidade['nome']}. Continuando para próxima cidade.")
            continue
            
        # Salva no banco de dados
        sucesso = salvar_previsoes(cidade, previsoes)
        if not sucesso:
            logging.warning(f"Falha ao salvar previsões para {cidade['nome']}")
    
    # Verificar alertas de alagamentos
    municipios_alerta = verificar_alerta_alagamentos()
    if municipios_alerta:
        logging.info(f"ALERTA DE ALAGAMENTOS: {len(municipios_alerta)} ocorrências identificadas")
        for alerta in municipios_alerta:
            logging.info(f"  - {alerta['municipio']}/{alerta['estado']}: {alerta['precipitacao']}mm em {alerta['data']}")
    else:
        logging.info("Nenhum alerta de alagamento identificado para os próximos dias")
    
    logging.info("Atualização de previsões concluída.")

if __name__ == "__main__":
    main() 