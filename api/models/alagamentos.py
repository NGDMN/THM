import pandas as pd
import datetime
from ..utils.db_utils import execute_query

class AlagamentosModel:
    """
    Modelo para manipulação de dados de alagamentos
    """
    
    @staticmethod
    def get_previsao_alagamentos(cidade, estado):
        """
        Obtém previsão de risco de alagamentos
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            
        Returns:
            dict: Dicionário com informações sobre risco de alagamentos
        """
        try:
            # Primeiro verifica se há previsão de chuvas fortes
            query = """
            SELECT 
                MAX(precipitacao_diaria) as max_precipitacao
            FROM 
                chuvas_diarias 
            WHERE 
                municipio = :cidade
                AND data BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '3 days'
            """
            
            params = {'cidade': cidade}
            df = execute_query(query, params)
            
            # Se não houver dados, retornar informação base
            if df.empty or 'max_precipitacao' not in df.columns:
                return {
                    'probabilidade': 0,
                    'nivelRisco': 'desconhecido',
                    'recomendacoes': ['Dados insuficientes para análise'],
                    'areasAfetadas': []
                }
            
            # Determinar nível de risco com base na precipitação máxima
            max_precipitacao = float(df['max_precipitacao'].iloc[0]) if not pd.isna(df['max_precipitacao'].iloc[0]) else 0
            
            if max_precipitacao >= 50:
                nivel_risco = 'alto'
                probabilidade = 0.8
            elif max_precipitacao >= 30:
                nivel_risco = 'médio'
                probabilidade = 0.5
            else:
                nivel_risco = 'baixo'
                probabilidade = 0.2
            
            # Buscar áreas com histórico de alagamentos
            query_areas = """
            SELECT 
                DISTINCT local
            FROM 
                alagamentos 
            WHERE 
                municipio = :cidade
            ORDER BY 
                local
            """
            
            df_areas = execute_query(query_areas, params)
            
            if df_areas.empty or 'local' not in df_areas.columns:
                areas_afetadas = []
            else:
                areas_afetadas = df_areas['local'].tolist()
            
            # Gerar recomendações com base no nível de risco
            recomendacoes = AlagamentosModel._gerar_recomendacoes(nivel_risco)
            
            return {
                'probabilidade': round(probabilidade, 2),
                'nivelRisco': nivel_risco,
                'recomendacoes': recomendacoes,
                'areasAfetadas': areas_afetadas
            }
            
        except Exception as e:
            print(f"Erro ao obter previsão de alagamentos: {str(e)}")
            return {
                'probabilidade': 0,
                'nivelRisco': 'desconhecido',
                'recomendacoes': ['Erro ao processar dados'],
                'areasAfetadas': []
            }
    
    @staticmethod
    def get_historico_alagamentos(cidade, estado, data_inicio, data_fim):
        """
        Obtém histórico de ocorrências de alagamentos
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            data_inicio (str): Data inicial no formato YYYY-MM-DD
            data_fim (str): Data final no formato YYYY-MM-DD
            
        Returns:
            list: Lista de dicionários com informações de alagamentos
        """
        try:
            # Query para obter histórico do banco de dados
            query = """
            SELECT 
                municipio, 
                data, 
                local,
                dh_mortos,
                dh_afetados
            FROM 
                alagamentos 
            WHERE 
                municipio = :cidade
                AND data BETWEEN TO_DATE(:data_inicio, 'YYYY-MM-DD') 
                            AND TO_DATE(:data_fim, 'YYYY-MM-DD')
            ORDER BY 
                data DESC
            """
            
            params = {
                'cidade': cidade,
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
            
            df = execute_query(query, params)
            
            # Se não houver dados históricos, retornar lista vazia
            if df.empty:
                return []
            
            # Converter para formato esperado pela API
            resultado = []
            for _, row in df.iterrows():
                # Determinar nível de gravidade com base nos afetados
                if pd.isna(row['dh_afetados']) or row['dh_afetados'] == 0:
                    nivel_gravidade = 'baixo'
                elif row['dh_afetados'] > 500:
                    nivel_gravidade = 'alto'
                else:
                    nivel_gravidade = 'médio'
                
                resultado.append({
                    'data': row['data'].strftime('%Y-%m-%d'),
                    'local': row['local'] if not pd.isna(row['local']) else 'Área central',
                    'nivelGravidade': nivel_gravidade,
                    'afetados': int(row['dh_afetados']) if not pd.isna(row['dh_afetados']) else 0
                })
            
            return resultado
            
        except Exception as e:
            print(f"Erro ao obter histórico de alagamentos: {str(e)}")
            return []
    
    @staticmethod
    def get_pontos_alagamento(cidade, estado):
        """
        Obtém pontos de alagamento conhecidos
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            
        Returns:
            list: Lista de dicionários com pontos de alagamento
        """
        try:
            query = """
            SELECT 
                local,
                latitude,
                longitude,
                nivel_gravidade
            FROM 
                alagamentos 
            WHERE 
                municipio = :cidade
                AND estado = :estado
                AND latitude IS NOT NULL
                AND longitude IS NOT NULL
            GROUP BY 
                local, latitude, longitude, nivel_gravidade
            """
            
            params = {'cidade': cidade, 'estado': estado}
            df = execute_query(query, params)
            
            if df.empty:
                return []
                
            resultado = []
            for _, row in df.iterrows():
                resultado.append({
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'local': row['local'],
                    'nivelRisco': row['nivel_gravidade'] if not pd.isna(row['nivel_gravidade']) else 'médio'
                })
                
            return resultado
            
        except Exception as e:
            print(f"Erro ao obter pontos de alagamento: {str(e)}")
            return []
    
    @staticmethod
    def _gerar_recomendacoes(nivel_risco):
        """
        Gera recomendações baseadas no nível de risco
        
        Args:
            nivel_risco (str): Nível de risco (alto, médio, baixo)
            
        Returns:
            list: Lista de recomendações
        """
        recomendacoes = {
            'alto': [
                'Evite áreas marcadas em vermelho no mapa',
                'Mantenha-se informado sobre alertas da Defesa Civil',
                'Tenha um plano de emergência preparado',
                'Considere a possibilidade de evacuação preventiva',
                'Não atravesse áreas alagadas'
            ],
            'médio': [
                'Esteja atento às previsões meteorológicas',
                'Evite áreas com histórico de alagamentos',
                'Mantenha-se informado sobre alertas da Defesa Civil',
                'Evite deslocamentos desnecessários em caso de chuva forte'
            ],
            'baixo': [
                'Monitore as condições meteorológicas',
                'Esteja atento a mudanças climáticas repentinas',
                'Verifique os canais oficiais de informação'
            ]
        }
        
        return recomendacoes.get(nivel_risco, ['Mantenha-se informado sobre o clima']) 