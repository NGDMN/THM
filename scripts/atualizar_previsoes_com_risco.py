#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para atualizar previsões meteorológicas com análise de risco de alagamento
usando o serviço integrado. Recomendado executar diariamente.
"""

import os
import sys
import logging
import datetime

# Adicionar diretório raiz ao path para importar módulos da API
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.services.previsao_integrada_service import PrevisaoIntegradaService
from api.utils.db_utils import setup_database_connection, close_database_connection
from api.config import USE_MOCK_DATA

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'update_previsao_risco.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Função principal para atualizar previsões meteorológicas com análise de risco
    """
    try:
        logger.info("Iniciando atualização de previsões com análise de risco")
        
        # Estabelecer conexão com o banco de dados
        logger.info("Conectando ao banco de dados")
        if USE_MOCK_DATA:
            logger.info("Usando dados simulados - sem conexão com banco de dados")
        else:
            setup_database_connection()
        
        # Solicitar 6 dias de previsão (máximo que conseguimos obter)
        dias_previsao = 6
        logger.info(f"Solicitando {dias_previsao} dias de previsão com análise de risco")
        
        # Atualizar previsões com risco para todas as cidades
        logger.info("Atualizando previsões para cidades de SP e RJ")
        resultados = PrevisaoIntegradaService.atualizar_previsoes_todas_cidades(dias=dias_previsao)
        
        # Registrar resultados
        if resultados:
            total_registros = sum(resultados.values())
            logger.info(f"Previsões atualizadas com sucesso: {total_registros} registros.")
            
            for cidade, registros in resultados.items():
                logger.info(f"  - {cidade}: {registros} previsões atualizadas")
        else:
            logger.warning("Nenhum resultado retornado. Verifique a conexão com a API.")
        
        # Verificar alertas de alto risco
        try:
            alertas = PrevisaoIntegradaService.obter_alertas_alagamento(limiar_probabilidade=0.7)
            
            if alertas:
                logger.warning(f"Detectados {len(alertas)} alertas de alto risco:")
                for alerta in alertas:
                    logger.warning(f"  * ALERTA: {alerta['cidade']}-{alerta['estado']} - "
                                 f"Data: {alerta['data']} - "
                                 f"Probabilidade: {alerta['probabilidade']:.0%} - "
                                 f"Nível: {alerta['nivel_risco']}")
            else:
                logger.info("Não foram detectados alertas de alto risco.")
        except Exception as e:
            logger.error(f"Erro ao verificar alertas: {str(e)}")
        
        # Fechar conexão com o banco de dados
        if not USE_MOCK_DATA:
            close_database_connection()
        
        logger.info("Atualização de previsões com risco concluída com sucesso!")
        return 0
        
    except Exception as e:
        logger.error(f"Erro durante atualização de previsões com risco: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 