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
            print(f"[LOG] Parâmetros recebidos: cidade={cidade}, estado={estado}")
            query = """
            SELECT 
                data, 
                precipitacao 
            FROM 
                previsoes 
            WHERE 
                UPPER(cidade) = UPPER(:cidade)
                AND UPPER(estado) = UPPER(:estado)
                AND data BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
            ORDER BY data
            """
            params = {"cidade": cidade, "estado": estado}
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
            print(f"[LOG] Parâmetros recebidos: cidade={cidade}, estado={estado}, data_inicio={data_inicio}, data_fim={data_fim}")
            query = """
            SELECT 
                data, 
                precipitacao_diaria as precipitacao
            FROM 
                chuvas_diarias
            WHERE 
                UPPER(cidade) = UPPER(:cidade)
                AND UPPER(estado) = UPPER(:estado)
                AND data BETWEEN :data_inicio AND :data_fim
            ORDER BY data
            """
            params = {"cidade": cidade, "estado": estado, "data_inicio": data_inicio, "data_fim": data_fim}
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
            print(f"[LOG] Erro ao buscar histórico de chuvas: {e}")
            return [] 