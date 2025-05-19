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
            # Query para obter previsões do banco de dados
            query = """
            SELECT 
                municipio, 
                data, 
                precipitacao_diaria 
            FROM 
                chuvas_diarias 
            WHERE 
                municipio = :cidade
                AND data BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
            ORDER BY 
                data
            """
            
            params = {'cidade': cidade}
            df = execute_query(query, params)
            
            # Se não houver dados, retornar lista vazia
            if df.empty:
                return []
            
            # Converter para formato esperado pela API
            resultado = []
            for _, row in df.iterrows():
                resultado.append({
                    'data': row['data'].strftime('%Y-%m-%d'),
                    'precipitacao': float(row['precipitacao_diaria'])
                })
            
            return resultado
            
        except Exception as e:
            print(f"Erro ao obter previsão de chuvas: {str(e)}")
            return []
    
    @staticmethod
    def get_historico_chuvas(cidade, estado, data_inicio, data_fim):
        """
        Obtém dados históricos de chuvas para o período especificado
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            data_inicio (str): Data inicial no formato YYYY-MM-DD
            data_fim (str): Data final no formato YYYY-MM-DD
            
        Returns:
            list: Lista de dicionários com data e precipitação
        """
        try:
            # Query para obter histórico do banco de dados
            query = """
            SELECT 
                municipio, 
                data, 
                precipitacao_diaria 
            FROM 
                chuvas_diarias 
            WHERE 
                municipio = :cidade
                AND data BETWEEN TO_DATE(:data_inicio, 'YYYY-MM-DD') 
                            AND TO_DATE(:data_fim, 'YYYY-MM-DD')
            ORDER BY 
                data
            """
            
            params = {
                'cidade': cidade,
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
            
            df = execute_query(query, params)
            
            # Se não houver dados, retornar lista vazia
            if df.empty:
                return []
            
            # Converter para formato esperado pela API
            resultado = []
            for _, row in df.iterrows():
                resultado.append({
                    'data': row['data'].strftime('%Y-%m-%d'),
                    'precipitacao': float(row['precipitacao_diaria'])
                })
            
            return resultado
            
        except Exception as e:
            print(f"Erro ao obter histórico de chuvas: {str(e)}")
            return [] 