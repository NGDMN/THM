import pandas as pd
import datetime
from ..utils.db_utils import execute_query

class ChuvasModel:
    """
    Modelo para manipulação de dados de chuvas
    """
    
    @staticmethod
    def get_previsao_chuvas(cidade, estado):
        """
        Obtém previsão de chuvas para os próximos 7 dias
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado (RJ ou SP)
            
        Returns:
            list: Lista de dicionários com data e precipitação prevista
        """
        try:
            print(f"[LOG] Buscando previsões para cidade={cidade}, estado={estado}")
            # Query para obter previsões da tabela correta
            query = """
            SELECT 
                data, 
                precipitacao 
            FROM 
                previsoes 
            WHERE 
                cidade = :cidade
                AND estado = :estado
                AND data BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
            ORDER BY data
            """
            print(f"[LOG] Query: {query}")
            params = {"cidade": cidade, "estado": estado}
            print(f"[LOG] Params: {params}")
            result = execute_query(query, params)
            print(f"[LOG] Resultado: {result}")
            if result.empty:
                return []
            resultado = []
            for _, row in result.iterrows():
                resultado.append({
                    'data': row['data'].strftime('%Y-%m-%d'),
                    'precipitacao': float(row['precipitacao'])
                })
            return resultado
        except Exception as e:
            print(f"[LOG] Erro ao buscar previsões: {e}")
            return []
    
    @staticmethod
    def get_historico_chuvas(cidade, estado, data_inicio, data_fim):
        """
        Obtém histórico de chuvas para o período informado
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado (RJ ou SP)
            data_inicio (str): Data inicial (YYYY-MM-DD)
            data_fim (str): Data final (YYYY-MM-DD)
        Returns:
            list: Lista de dicionários com data e precipitação
        """
        try:
            print(f"[LOG] Buscando histórico de chuvas para cidade={cidade}, estado={estado}, de {data_inicio} até {data_fim}")
            query = """
            SELECT 
                data, 
                precipitacao_diaria as precipitacao
            FROM 
                chuvas_diarias
            WHERE 
                municipio = :cidade
                AND estado = :estado
                AND data BETWEEN :data_inicio AND :data_fim
            ORDER BY data
            """
            print(f"[LOG] Query: {query}")
            params = {"cidade": cidade, "estado": estado, "data_inicio": data_inicio, "data_fim": data_fim}
            print(f"[LOG] Params: {params}")
            result = execute_query(query, params)
            print(f"[LOG] Resultado: {result}")
            return result
        except Exception as e:
            print(f"[LOG] Erro ao buscar histórico de chuvas: {e}")
            return [] 