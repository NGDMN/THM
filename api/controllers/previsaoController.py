from ..services.databaseService import execute_query
import logging

logger = logging.getLogger(__name__)

def get_previsao_chuvas(cidade, estado):
    """Busca previsão de chuvas para uma cidade/estado"""
    try:
        query = """
        SELECT 
            data,
            cidade as municipio,
            estado,
            precipitacao,
            temp_min as temperatura_minima,
            temp_max as temperatura_maxima,
            umidade,
            descricao,
            icone,
            probabilidade_alagamento,
            nivel_risco,
            afetados_estimados,
            created_at
        FROM previsoes 
        WHERE LOWER(TRIM(cidade)) = LOWER(TRIM(%(cidade)s))
        AND UPPER(TRIM(estado)) = UPPER(TRIM(%(estado)s))
        AND data >= CURRENT_DATE
        AND data <= CURRENT_DATE + INTERVAL '7 days'
        ORDER BY data ASC
        """
        
        params = {
            'cidade': cidade,
            'estado': estado
        }
        
        result = execute_query(query, params)
        return result.to_dict('records')
        
    except Exception as e:
        logger.error(f"Erro ao buscar previsão de chuvas: {str(e)}")
        raise

def get_previsao_alagamentos(cidade, estado):
    """Busca previsão de alagamentos para uma cidade/estado"""
    try:
        query = """
        SELECT 
            data,
            cidade as municipio,
            estado,
            nivel_risco,
            probabilidade_alagamento as probabilidade,
            afetados_estimados,
            created_at
        FROM previsoes 
        WHERE LOWER(TRIM(cidade)) = LOWER(TRIM(%(cidade)s))
        AND UPPER(TRIM(estado)) = UPPER(TRIM(%(estado)s))
        AND data >= CURRENT_DATE
        AND data <= CURRENT_DATE + INTERVAL '7 days'
        AND probabilidade_alagamento > 0
        ORDER BY data ASC
        """
        
        params = {
            'cidade': cidade,
            'estado': estado
        }
        
        result = execute_query(query, params)
        return result.to_dict('records')
        
    except Exception as e:
        logger.error(f"Erro ao buscar previsão de alagamentos: {str(e)}")
        raise

def get_alertas_atuais(cidade, estado):
    """Busca alertas atuais para uma cidade/estado"""
    try:
        query = """
        SELECT 
            data,
            cidade as municipio,
            estado,
            nivel_risco,
            probabilidade_alagamento,
            afetados_estimados,
            created_at
        FROM previsoes 
        WHERE LOWER(TRIM(cidade)) = LOWER(TRIM(%(cidade)s))
        AND UPPER(TRIM(estado)) = UPPER(TRIM(%(estado)s))
        AND data >= CURRENT_DATE
        AND data <= CURRENT_DATE + INTERVAL '7 days'
        AND nivel_risco IN ('alto', 'medio')
        ORDER BY data ASC, probabilidade_alagamento DESC
        LIMIT 1
        """
        
        params = {
            'cidade': cidade,
            'estado': estado
        }
        
        result = execute_query(query, params)
        return result.to_dict('records')
        
    except Exception as e:
        logger.error(f"Erro ao buscar alertas: {str(e)}")
        raise 