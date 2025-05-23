import pandas as pd
import datetime
from ..utils.db_utils import execute_query

class ChuvasModel:
    """
    Modelo para manipulação de dados de chuvas
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
            print(f"[DEBUG] Iniciando get_previsao_chuvas com: cidade={cidade}, estado={estado}")
            
            # Normalizar nome da cidade
            cidade_normalizada = ChuvasModel._normalizar_nome_cidade(cidade)
            print(f"[DEBUG] Nome da cidade normalizado: {cidade_normalizada}")
            
            # CORREÇÃO: Usar campos padronizados e verificar ambas as tabelas
            query = """
            SELECT 
                data, 
                precipitacao 
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
            
            # Se não encontrou dados na tabela previsoes, tentar chuvas_diarias
            if result.empty:
                print(f"[DEBUG] Sem dados em 'previsoes', tentando 'chuvas_diarias'...")
                query_historico = """
                SELECT 
                    data, 
                    precipitacao_diaria as precipitacao
                FROM 
                    chuvas_diarias
                WHERE 
                    UPPER(municipio) = UPPER(%(cidade)s)
                    AND UPPER(estado) = UPPER(%(estado)s)
                    AND data BETWEEN CURRENT_DATE - INTERVAL '30 days' AND CURRENT_DATE + INTERVAL '7 days'
                ORDER BY data DESC
                LIMIT 7
                """
                print(f"[DEBUG] Query SQL (chuvas_diarias): {query_historico}")
                result = execute_query(query_historico, params)
                print(f"[DEBUG] Resultado da tabela chuvas_diarias: {len(result) if not result.empty else 0} registros")
            
            if result.empty:
                print(f"[DEBUG] Nenhum dado encontrado em ambas as tabelas")
                return []
                
            resultado = []
            for _, row in result.iterrows():
                # Verificar se a data não é futura
                if row['data'].date() <= datetime.date.today():
                    resultado.append({
                        'data': row['data'].strftime('%Y-%m-%d'),
                        'precipitacao': float(row['precipitacao']) if row['precipitacao'] is not None else 0.0
                    })
            
            print(f"[DEBUG] Retornando {len(resultado)} registros")
            return resultado
            
        except Exception as e:
            print(f"[DEBUG] Erro ao buscar previsões: {e}")
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
            
            # Tentar primeiro na tabela chuvas_diarias (dados históricos)
            query = """
            SELECT 
                data, 
                precipitacao_diaria as precipitacao
            FROM 
                chuvas_diarias
            WHERE 
                UPPER(municipio) = UPPER(%(cidade)s)
                AND UPPER(estado) = UPPER(%(estado)s)
                AND data BETWEEN %(data_inicio)s AND %(data_fim)s
            ORDER BY data
            """
            
            params = {"cidade": cidade, "estado": estado, "data_inicio": data_inicio, "data_fim": data_fim}
            result = execute_query(query, params)
            print(f"[LOG] Resultado chuvas_diarias: {len(result) if not result.empty else 0} registros")
            
            # Se não encontrou dados históricos, tentar na tabela de previsões
            if result.empty:
                print(f"[LOG] Sem dados históricos, tentando tabela previsoes...")
                query_previsoes = """
                SELECT 
                    data, 
                    precipitacao
                FROM 
                    previsoes
                WHERE 
                    UPPER(cidade) = UPPER(%(cidade)s)
                    AND UPPER(estado) = UPPER(%(estado)s)
                    AND data BETWEEN %(data_inicio)s AND %(data_fim)s
                ORDER BY data
                """
                result = execute_query(query_previsoes, params)
                print(f"[LOG] Resultado previsoes: {len(result) if not result.empty else 0} registros")
            
            if result.empty:
                print(f"[LOG] Nenhum dado encontrado em ambas as tabelas")
                return []
                
            resultado = []
            for _, row in result.iterrows():
                resultado.append({
                    'data': row['data'].strftime('%Y-%m-%d'),
                    'precipitacao': float(row['precipitacao']) if row['precipitacao'] is not None else 0.0
                })
                
            print(f"[LOG] Retornando {len(resultado)} registros")
            return resultado
            
        except Exception as e:
            print(f"[LOG] Erro ao buscar histórico de chuvas: {e}")
            return []