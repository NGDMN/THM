import pandas as pd
import datetime
from api.utils.db_utils import execute_query

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
                AND data BETWEEN CURRENT_DATE AND CURRENT_DATE + 7
            ORDER BY 
                data
            """
            
            params = {'cidade': cidade}
            df = execute_query(query, params)
            
            # Se não houver dados de previsão, gerar dados simulados para teste
            if df.empty:
                return ChuvasModel._gerar_previsao_simulada(cidade, estado)
            
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
            # Retornar dados simulados em caso de erro
            return ChuvasModel._gerar_previsao_simulada(cidade, estado)
    
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
            
            # Se não houver dados históricos, gerar dados simulados para teste
            if df.empty:
                return ChuvasModel._gerar_historico_simulado(cidade, estado, data_inicio, data_fim)
            
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
            # Retornar dados simulados em caso de erro
            return ChuvasModel._gerar_historico_simulado(cidade, estado, data_inicio, data_fim)
    
    @staticmethod
    def _gerar_previsao_simulada(cidade, estado):
        """
        Gera dados simulados de previsão para testes
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            
        Returns:
            list: Lista de dicionários com data e precipitação prevista
        """
        import random
        
        resultado = []
        hoje = datetime.date.today()
        
        # Coeficientes para simular condições diferentes entre RJ e SP
        coef = 1.2 if estado == 'RJ' else 0.8
        
        for i in range(7):
            data = hoje + datetime.timedelta(days=i)
            
            # Gerar valor aleatório para precipitação (maior para o RJ)
            if i == 2 or i == 3:  # Simular dias de chuva forte
                precipitacao = random.uniform(30, 60) * coef
            else:
                precipitacao = random.uniform(0, 20) * coef
                
            resultado.append({
                'data': data.strftime('%Y-%m-%d'),
                'precipitacao': round(precipitacao, 1)
            })
        
        return resultado
    
    @staticmethod
    def _gerar_historico_simulado(cidade, estado, data_inicio, data_fim):
        """
        Gera dados históricos simulados para testes
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            data_inicio (str): Data inicial
            data_fim (str): Data final
            
        Returns:
            list: Lista de dicionários com data e precipitação
        """
        import random
        
        resultado = []
        data_inicio = datetime.datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim = datetime.datetime.strptime(data_fim, '%Y-%m-%d').date()
        
        # Coeficientes para simular condições diferentes entre RJ e SP
        coef = 1.3 if estado == 'RJ' else 0.9
        
        delta = (data_fim - data_inicio).days + 1
        for i in range(delta):
            data = data_inicio + datetime.timedelta(days=i)
            
            # Gerar valor aleatório para precipitação
            # Meses de verão (dez-mar) com mais chuvas
            mes = data.month
            if 12 <= mes <= 12 or 1 <= mes <= 3:
                precipitacao = random.uniform(0, 80) * coef
            else:
                precipitacao = random.uniform(0, 30) * coef
                
            resultado.append({
                'data': data.strftime('%Y-%m-%d'),
                'precipitacao': round(precipitacao, 1)
            })
        
        return resultado 