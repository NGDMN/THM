#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
db_utils.py - Versão corrigida com debugging avançado
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuração do banco de dados
DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def get_db_connection():
    """Obtém conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar com o banco: {e}")
        raise

def log_query_params(query, params):
    """Log da query e parâmetros para debugging"""
    logger.debug(f"Query: {query}")
    logger.debug(f"Params: {params}")

def get_previsao_chuvas(cidade, estado):
    """
    Busca previsões de chuva para uma cidade específica
    """
    logger.info(f"=== get_previsao_chuvas ===")
    logger.info(f"Cidade: '{cidade}', Estado: '{estado}'")
    
    # Validação de entrada
    if not cidade or not estado:
        logger.warning(f"Parâmetros inválidos - Cidade: '{cidade}', Estado: '{estado}'")
        return []
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query melhorada com logs detalhados
        query = """
            SELECT 
                p.id,
                p.cidade,
                p.estado,
                p.data,
                p.temp_min,
                p.temp_max,
                COALESCE(p.precipitacao, 0) as precipitacao,
                p.umidade,
                p.descricao,
                p.icone,
                COALESCE(p.probabilidade_alagamento, 0) as probabilidade_alagamento,
                COALESCE(p.nivel_risco, 'baixo') as nivel_risco,
                COALESCE(p.afetados_estimados, 0) as afetados_estimados,
                p.created_at,
                p.updated_at,
                COALESCE(hist.total_afetados, 0) as historico_afetados
            FROM previsoes p
            LEFT JOIN (
                SELECT 
                    municipio, 
                    estado, 
                    SUM(COALESCE(dh_afetados, 0)) as total_afetados
                FROM alagamentos 
                WHERE LOWER(TRIM(municipio)) = LOWER(TRIM(%s)) 
                AND LOWER(TRIM(estado)) = LOWER(TRIM(%s))
                GROUP BY municipio, estado
            ) hist ON LOWER(TRIM(p.cidade)) = LOWER(TRIM(hist.municipio)) 
                   AND LOWER(TRIM(p.estado)) = LOWER(TRIM(hist.estado))
            WHERE LOWER(TRIM(p.cidade)) = LOWER(TRIM(%s)) 
            AND LOWER(TRIM(p.estado)) = LOWER(TRIM(%s))
            AND p.data >= %s
            ORDER BY p.data ASC
        """
        
        params = (cidade, estado, cidade, estado, date.today())
        log_query_params(query, params)
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        logger.info(f"Resultados encontrados: {len(resultados)}")
        
        # Log dos primeiros resultados para debugging
        for i, row in enumerate(resultados[:3]):
            logger.debug(f"Resultado {i+1}: Data={row['data']}, Precipitação={row['precipitacao']}")
        
        # Converter para formato JSON serializable
        previsoes = []
        for row in resultados:
            previsao = {
                'id': row['id'],
                'cidade': row['cidade'],
                'estado': row['estado'],
                'data': row['data'].strftime('%Y-%m-%d') if row['data'] else None,
                'temp_min': float(row['temp_min']) if row['temp_min'] is not None else None,
                'temp_max': float(row['temp_max']) if row['temp_max'] is not None else None,
                'precipitacao': float(row['precipitacao']) if row['precipitacao'] is not None else 0.0,
                'umidade': float(row['umidade']) if row['umidade'] is not None else None,
                'descricao': row['descricao'],
                'icone': row['icone'],
                'probabilidade_alagamento': float(row['probabilidade_alagamento']) if row['probabilidade_alagamento'] is not None else 0.0,
                'nivel_risco': row['nivel_risco'] or 'baixo',
                'afetados_estimados': int(row['afetados_estimados']) if row['afetados_estimados'] is not None else 0,
                'historico_afetados': int(row['historico_afetados']) if row['historico_afetados'] is not None else 0,
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
            }
            previsoes.append(previsao)
        
        cursor.close()
        return previsoes
        
    except Exception as e:
        logger.error(f"Erro em get_previsao_chuvas: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_historico_chuvas(cidade, estado, limite=30):
    """
    Busca histórico de chuvas para uma cidade
    """
    logger.info(f"=== get_historico_chuvas ===")
    logger.info(f"Cidade: '{cidade}', Estado: '{estado}', Limite: {limite}")
    
    if not cidade or not estado:
        logger.warning(f"Parâmetros inválidos - Cidade: '{cidade}', Estado: '{estado}'")
        return []
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                id,
                municipio as cidade,
                estado,
                data,
                COALESCE(precipitacao_diaria, 0) as precipitacao,
                created_at,
                updated_at
            FROM chuvas_diarias 
            WHERE LOWER(TRIM(municipio)) = LOWER(TRIM(%s)) 
            AND LOWER(TRIM(estado)) = LOWER(TRIM(%s))
            ORDER BY data DESC 
            LIMIT %s
        """
        
        params = (cidade, estado, limite)
        log_query_params(query, params)
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        logger.info(f"Histórico de chuvas encontrado: {len(resultados)}")
        
        # Converter para formato JSON serializable
        historico = []
        for row in resultados:
            item = {
                'id': row['id'],
                'cidade': row['cidade'],
                'estado': row['estado'],
                'data': row['data'].strftime('%Y-%m-%d') if row['data'] else None,
                'precipitacao': float(row['precipitacao']) if row['precipitacao'] is not None else 0.0,
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
            }
            historico.append(item)
        
        cursor.close()
        return historico
        
    except Exception as e:
        logger.error(f"Erro em get_historico_chuvas: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_historico_alagamentos(cidade, estado):
    """
    Busca histórico de alagamentos para uma cidade
    """
    logger.info(f"=== get_historico_alagamentos ===")
    logger.info(f"Cidade: '{cidade}', Estado: '{estado}'")
    
    if not cidade or not estado:
        logger.warning(f"Parâmetros inválidos - Cidade: '{cidade}', Estado: '{estado}'")
        return []
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                id,
                municipio as cidade,
                estado,
                data,
                local,
                COALESCE(dh_mortos, 0) as mortos,
                COALESCE(dh_afetados, 0) as afetados,
                created_at,
                updated_at
            FROM alagamentos 
            WHERE LOWER(TRIM(municipio)) = LOWER(TRIM(%s)) 
            AND LOWER(TRIM(estado)) = LOWER(TRIM(%s))
            ORDER BY data DESC
        """
        
        params = (cidade, estado)
        log_query_params(query, params)
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        logger.info(f"Histórico de alagamentos encontrado: {len(resultados)}")
        
        # Converter para formato JSON serializable
        alagamentos = []
        for row in resultados:
            item = {
                'id': row['id'],
                'cidade': row['cidade'],
                'estado': row['estado'],
                'data': row['data'].strftime('%Y-%m-%d') if row['data'] else None,
                'local': row['local'],
                'mortos': int(row['mortos']) if row['mortos'] is not None else 0,
                'afetados': int(row['afetados']) if row['afetados'] is not None else 0,
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
            }
            alagamentos.append(item)
        
        cursor.close()
        return alagamentos
        
    except Exception as e:
        logger.error(f"Erro em get_historico_alagamentos: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_municipios():
    """
    Busca lista de municípios disponíveis
    """
    logger.info("=== get_municipios ===")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buscar municípios das previsões e do histórico
        query = """
            SELECT DISTINCT cidade, estado, 'previsao' as fonte
            FROM previsoes
            WHERE cidade IS NOT NULL AND estado IS NOT NULL
            UNION
            SELECT DISTINCT municipio as cidade, estado, 'historico' as fonte
            FROM chuvas_diarias
            WHERE municipio IS NOT NULL AND estado IS NOT NULL
            UNION
            SELECT DISTINCT municipio as cidade, estado, 'alagamento' as fonte
            FROM alagamentos
            WHERE municipio IS NOT NULL AND estado IS NOT NULL
            ORDER BY estado, cidade
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        logger.info(f"Municípios encontrados: {len(resultados)}")
        
        # Agrupar por município
        municipios_dict = {}
        for row in resultados:
            chave = f"{row['cidade']}_{row['estado']}"
            if chave not in municipios_dict:
                municipios_dict[chave] = {
                    'cidade': row['cidade'],
                    'estado': row['estado'],
                    'fontes': []
                }
            municipios_dict[chave]['fontes'].append(row['fonte'])
        
        municipios = list(municipios_dict.values())
        cursor.close()
        return municipios
        
    except Exception as e:
        logger.error(f"Erro em get_municipios: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Funções de teste e debugging
def test_api_functions():
    """Testa todas as funções da API"""
    print("🧪 TESTANDO FUNÇÕES DA API")
    print("=" * 50)
    
    # Teste 1: Municípios
    print("1. Testando get_municipios()...")
    municipios = get_municipios()
    print(f"   ✅ {len(municipios)} municípios encontrados")
    
    # Teste 2: Previsão
    print("\n2. Testando get_previsao_chuvas()...")
    previsoes = get_previsao_chuvas("Rio de Janeiro", "RJ")
    print(f"   ✅ {len(previsoes)} previsões encontradas")
    
    # Teste 3: Histórico de chuvas
    print("\n3. Testando get_historico_chuvas()...")
    historico = get_historico_chuvas("Rio de Janeiro", "RJ")
    print(f"   ✅ {len(historico)} registros de chuva encontrados")
    
    # Teste 4: Histórico de alagamentos
    print("\n4. Testando get_historico_alagamentos()...")
    alagamentos = get_historico_alagamentos("Rio de Janeiro", "RJ")
    print(f"   ✅ {len(alagamentos)} registros de alagamentos encontrados")
    
    print("\n✅ Todos os testes concluídos!")

if __name__ == "__main__":
    test_api_functions() 