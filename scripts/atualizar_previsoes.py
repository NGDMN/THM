#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para atualizar previsões meteorológicas usando a API do OpenWeatherMap.
Executar este script diariamente para manter as previsões atualizadas.
"""

import os
import sys
import logging
import datetime

# Adicionar diretório raiz ao path para importar módulos da API
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.services.openweather_service import OpenWeatherService
from api.utils.db_utils import setup_database_connection, close_database_connection
from api.config import USE_MOCK_DATA

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'update_previsao.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Função principal para atualizar previsões meteorológicas
    """
    try:
        logger.info("Iniciando atualização de previsões meteorológicas")
        
        # Estabelecer conexão com o banco de dados
        logger.info("Conectando ao banco de dados")
        if USE_MOCK_DATA:
            logger.info("Usando dados simulados - sem conexão com banco de dados")
        else:
            setup_database_connection()
        
        # Solicitar 7 dias de previsão (nota: API gratuita pode limitar a 5 dias)
        dias_previsao = 7
        logger.info(f"Solicitando {dias_previsao} dias de previsão (API gratuita pode limitar a 5 dias)")
        
        # Atualizar previsões para todas as cidades cadastradas
        logger.info("Atualizando previsões para SP e RJ")
        resultados = OpenWeatherService.atualizar_previsoes_todas_cidades(dias=dias_previsao)
        
        # Registrar resultados
        if resultados:
            total_registros = sum(resultados.values())
            logger.info(f"Previsões atualizadas com sucesso: {total_registros} registros.")
            
            for cidade, registros in resultados.items():
                logger.info(f"  - {cidade}: {registros} previsões atualizadas")
        else:
            logger.warning("Nenhum resultado retornado. Verifique a conexão com a API OpenWeatherMap.")
        
        # Fechar conexão com o banco de dados
        if not USE_MOCK_DATA:
            close_database_connection()
        
        logger.info("Atualização de previsões concluída com sucesso!")
        return 0
        
    except Exception as e:
        logger.error(f"Erro durante atualização de previsões: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 