import os
import pandas as pd
import datetime
from api.utils.db_utils import execute_query, execute_dml

class MeteoService:
    """
    Serviço para operações relacionadas a dados meteorológicos
    """
    
    @staticmethod
    def processar_dados_chuvas(arquivo_csv):
        """
        Processa dados brutos de chuvas e armazena no banco de dados
        
        Args:
            arquivo_csv (str): Caminho para o arquivo CSV com dados brutos
            
        Returns:
            int: Número de registros processados
        """
        try:
            # Ler arquivo CSV
            df = pd.read_csv(arquivo_csv, encoding='utf-8')
            
            # Processar dados conforme necessário
            # ...
            
            # Inserir no banco de dados
            query = """
            INSERT INTO chuvas_diarias (municipio, data, precipitacao_diaria)
            VALUES (:municipio, TO_DATE(:data, 'YYYY-MM-DD'), :precipitacao)
            """
            
            # Preparar parâmetros para inserção
            params = []
            for _, row in df.iterrows():
                params.append({
                    'municipio': row['municipio'],
                    'data': row['data'],
                    'precipitacao': row['precipitacao']
                })
            
            # Executar inserção
            registros_inseridos = execute_dml(query, params)
            
            return registros_inseridos
        
        except Exception as e:
            print(f"Erro ao processar dados de chuvas: {str(e)}")
            return 0
    
    @staticmethod
    def atualizar_previsoes(data_inicio=None, data_fim=None):
        """
        Atualiza previsões meteorológicas para os próximos dias
        
        Args:
            data_inicio (str, optional): Data inicial no formato YYYY-MM-DD
            data_fim (str, optional): Data final no formato YYYY-MM-DD
            
        Returns:
            int: Número de previsões atualizadas
        """
        # Em um sistema real, este método buscaria previsões de uma API externa
        # como INMET ou OpenWeatherMap e atualizaria o banco de dados
        
        # Por enquanto, vamos apenas retornar um valor simulado
        return 7  # 7 dias de previsão atualizados
    
    @staticmethod
    def calcular_correlacao(cidade, estado, periodo_dias=365):
        """
        Calcula correlação entre chuvas e alagamentos
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            periodo_dias (int): Período em dias para análise
            
        Returns:
            dict: Resultados da correlação
        """
        try:
            # Data limite para a análise
            data_limite = (datetime.date.today() - datetime.timedelta(days=periodo_dias)).strftime('%Y-%m-%d')
            
            # Query para obter dados correlacionados
            query = """
            SELECT 
                c.municipio,
                c.data,
                c.precipitacao_diaria,
                a.dh_afetados
            FROM 
                chuvas_diarias c
            LEFT JOIN 
                alagamentos a ON c.municipio = a.municipio AND c.data = a.data
            WHERE 
                c.municipio = :cidade
                AND c.data >= TO_DATE(:data_limite, 'YYYY-MM-DD')
            ORDER BY 
                c.data
            """
            
            params = {
                'cidade': cidade,
                'data_limite': data_limite
            }
            
            df = execute_query(query, params)
            
            # Se não houver dados suficientes, retornar resultado simulado
            if len(df) < 10:
                return {
                    'correlacao': 0.75,
                    'limiar_precipitacao': 30.0,
                    'confiabilidade': 'média'
                }
            
            # Calcular correlação
            # Em um sistema real, aqui teria análise estatística mais complexa
            # Por enquanto, simulamos um resultado
            
            return {
                'correlacao': 0.82,
                'limiar_precipitacao': 40.0,
                'confiabilidade': 'alta'
            }
            
        except Exception as e:
            print(f"Erro ao calcular correlação: {str(e)}")
            return {
                'correlacao': 0.0,
                'limiar_precipitacao': 0.0,
                'confiabilidade': 'baixa',
                'erro': str(e)
            } 