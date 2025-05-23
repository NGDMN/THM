import pandas as pd
import datetime
from ..utils.db_utils import execute_query

class AlagamentosModel:
    """
    Modelo para manipulação de dados de alagamentos
    """
    
    @staticmethod
    def _normalizar_nome_cidade(cidade):
        """
        Normaliza o nome da cidade para o formato padrão
        """
        if not cidade:
            return cidade
        # Remove hífens e espaços extras
        cidade = cidade.replace('-', ' ').strip()
        # Converte para título (primeira letra de cada palavra em maiúscula)
        return cidade.title()
    
    @staticmethod
    def get_previsao_alagamentos(cidade, estado):
        """
        Obtém previsão de risco de alagamentos para os próximos 7 dias
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado (RJ ou SP)
            
        Returns:
            list: Lista de dicionários com data e risco de alagamento
        """
        try:
            print(f"[DEBUG] Iniciando get_previsao_alagamentos com: cidade={cidade}, estado={estado}")
            
            # Normalizar nome da cidade
            cidade_normalizada = AlagamentosModel._normalizar_nome_cidade(cidade)
            print(f"[DEBUG] Nome da cidade normalizado: {cidade_normalizada}")
            
            # Buscar dados de precipitação
            query = """
            SELECT 
                data, 
                precipitacao,
                CASE 
                    WHEN precipitacao > 50 THEN 'Alto'
                    WHEN precipitacao > 30 THEN 'Médio'
                    ELSE 'Baixo'
                END as risco
            FROM 
                previsoes 
            WHERE 
                UPPER(cidade) = UPPER(%(cidade)s)
                AND UPPER(estado) = UPPER(%(estado)s)
                AND data BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
            ORDER BY data
            """
            
            params = {"cidade": cidade_normalizada, "estado": estado}
            print(f"[DEBUG] Query SQL: {query}")
            print(f"[DEBUG] Parâmetros: {params}")
            
            result = execute_query(query, params)
            print(f"[DEBUG] Resultado da tabela previsoes: {len(result) if not result.empty else 0} registros")
            
            if result.empty:
                print(f"[DEBUG] Nenhum dado encontrado")
                return []
                
            resultado = []
            for _, row in result.iterrows():
                # Verificar se a data não é futura
                if row['data'].date() <= datetime.date.today():
                    resultado.append({
                        'data': row['data'].strftime('%Y-%m-%d'),
                        'precipitacao': float(row['precipitacao']) if row['precipitacao'] is not None else 0.0,
                        'risco': row['risco']
                    })
            
            print(f"[DEBUG] Retornando {len(resultado)} registros")
            return resultado
            
        except Exception as e:
            print(f"[DEBUG] Erro ao buscar previsões de alagamentos: {e}")
            return []
    
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
                municipio = %(cidade)s
                AND data BETWEEN %(data_inicio)s AND %(data_fim)s
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
                municipio = %(cidade)s
                AND estado = %(estado)s
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