from ..services.databaseService import execute_query
import logging

logger = logging.getLogger(__name__)

def get_historico_chuvas(cidade, estado, data_inicial, data_final):
    """Busca histórico de chuvas para uma cidade/estado"""
    try:
        query = """
        SELECT 
            data,
            municipio,
            estado,
            precipitacao_diaria as precipitacao,
            created_at
        FROM chuvas_diarias 
        WHERE LOWER(TRIM(municipio)) = LOWER(TRIM(%(cidade)s))
        AND UPPER(TRIM(estado)) = UPPER(TRIM(%(estado)s))
        AND data BETWEEN %(data_inicial)s AND %(data_final)s
        ORDER BY data DESC
        """
        
        params = {
            'cidade': cidade,
            'estado': estado,
            'data_inicial': data_inicial,
            'data_final': data_final
        }
        
        result = execute_query(query, params)
        return result.to_dict('records')
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de chuvas: {str(e)}")
        raise

def get_historico_alagamentos(cidade, estado, data_inicial, data_final):
    """Busca histórico de alagamentos para uma cidade/estado"""
    try:
        query = """
        SELECT 
            data,
            municipio,
            estado,
            local,
            dh_afetados,
            dh_mortos,
            latitude,
            longitude,
            created_at
        FROM alagamentos 
        WHERE LOWER(TRIM(municipio)) = LOWER(TRIM(%(cidade)s))
        AND UPPER(TRIM(estado)) = UPPER(TRIM(%(estado)s))
        AND data BETWEEN %(data_inicial)s AND %(data_final)s
        ORDER BY data DESC
        """
        
        params = {
            'cidade': cidade,
            'estado': estado,
            'data_inicial': data_inicial,
            'data_final': data_final
        }
        
        result = execute_query(query, params)
        return result.to_dict('records')
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de alagamentos: {str(e)}")
        raise

def get_pontos_alagamento(cidade, estado):
    """Busca pontos de alagamento para uma cidade/estado"""
    try:
        query = """
        SELECT 
            local,
            latitude,
            longitude,
            dh_afetados,
            dh_mortos,
            data
        FROM alagamentos 
        WHERE LOWER(TRIM(municipio)) = LOWER(TRIM(%(cidade)s))
        AND UPPER(TRIM(estado)) = UPPER(TRIM(%(estado)s))
        AND data >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY data DESC
        """
        
        params = {
            'cidade': cidade,
            'estado': estado
        }
        
        result = execute_query(query, params)
        return result.to_dict('records')
        
    except Exception as e:
        logger.error(f"Erro ao buscar pontos de alagamento: {str(e)}")
        raise 