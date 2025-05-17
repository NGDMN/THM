import pandas as pd
import numpy as np
import datetime
from api.utils.db_utils import execute_query, execute_dml

class PrevisaoService:
    """
    Serviço para cálculos de previsão de alagamentos
    """
    
    @staticmethod
    def calcular_probabilidade_alagamento(cidade, estado, precipitacao):
        """
        Calcula probabilidade de alagamento com base na precipitação prevista
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            precipitacao (float): Precipitação prevista em mm
            
        Returns:
            float: Probabilidade de alagamento (0-1)
        """
        try:
            # Em um sistema real, este cálculo seria baseado em um modelo
            # treinado com dados históricos. Aqui simplificamos com uma função
            # baseada em limiares de precipitação.
            
            # Obter parâmetros históricos da cidade
            query = """
            SELECT 
                AVG(c.precipitacao_diaria) as media_precip_alagamento
            FROM 
                chuvas_diarias c
            INNER JOIN 
                alagamentos a ON c.municipio = a.municipio AND c.data = a.data
            WHERE 
                c.municipio = :cidade
            """
            
            params = {'cidade': cidade}
            df = execute_query(query, params)
            
            # Se não houver dados suficientes, usar valores padrão
            if df.empty or 'media_precip_alagamento' not in df.columns:
                if estado == 'RJ':
                    limiar_base = 35.0  # mm - Rio tem mais alagamentos com menos chuva
                else:
                    limiar_base = 45.0  # mm - São Paulo precisa de mais chuva para alagar
            else:
                limiar_base = float(df['media_precip_alagamento'].iloc[0])
                if pd.isna(limiar_base) or limiar_base == 0:
                    limiar_base = 40.0  # valor padrão
            
            # Cálculo de probabilidade simplificado
            if precipitacao <= 10:
                return 0.05  # chuva fraca, baixa probabilidade
            elif precipitacao <= 25:
                # Probabilidade cresce lentamente até 25mm
                return 0.05 + (precipitacao - 10) * 0.025
            elif precipitacao < limiar_base:
                # Crescimento mais acentuado até o limiar
                return 0.30 + (precipitacao - 25) * (0.60 / (limiar_base - 25))
            else:
                # Após o limiar, probabilidade alta
                excedente = precipitacao - limiar_base
                return min(0.90 + excedente * 0.01, 0.99)
        
        except Exception as e:
            print(f"Erro ao calcular probabilidade de alagamento: {str(e)}")
            # Valor padrão em caso de erro
            return 0.50 if precipitacao > 30 else 0.25
    
    @staticmethod
    def identificar_pontos_criticos(cidade, estado):
        """
        Identifica pontos críticos de alagamento com base no histórico
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            
        Returns:
            list: Lista de pontos críticos ordenados por frequência
        """
        try:
            # Query para obter pontos com mais ocorrências
            query = """
            SELECT 
                local,
                COUNT(*) as num_ocorrencias,
                MAX(data) as ultima_ocorrencia
            FROM 
                alagamentos
            WHERE 
                municipio = :cidade
            GROUP BY 
                local
            ORDER BY 
                num_ocorrencias DESC
            """
            
            params = {'cidade': cidade}
            df = execute_query(query, params)
            
            # Se não houver dados, retornar lista vazia
            if df.empty:
                return []
            
            # Converter para formato esperado
            pontos_criticos = []
            for _, row in df.iterrows():
                pontos_criticos.append({
                    'local': row['local'],
                    'num_ocorrencias': int(row['num_ocorrencias']),
                    'ultima_ocorrencia': row['ultima_ocorrencia'].strftime('%Y-%m-%d') if not pd.isna(row['ultima_ocorrencia']) else None
                })
            
            return pontos_criticos
            
        except Exception as e:
            print(f"Erro ao identificar pontos críticos: {str(e)}")
            return []
    
    @staticmethod
    def calcular_impacto_precipitacao(cidade, estado, precipitacao_prevista):
        """
        Calcula o impacto esperado de uma precipitação prevista
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            precipitacao_prevista (float): Precipitação prevista em mm
            
        Returns:
            dict: Dados de impacto esperado
        """
        try:
            # Em um sistema real, este seria um modelo mais complexo
            # com base em múltiplas variáveis (solo, relevo, urbanização)
            
            # Obter média histórica de afetados por faixa de precipitação
            query = """
            SELECT 
                CASE
                    WHEN c.precipitacao_diaria < 30 THEN 'baixa'
                    WHEN c.precipitacao_diaria < 50 THEN 'média'
                    ELSE 'alta'
                END as faixa_precipitacao,
                AVG(a.dh_afetados) as media_afetados
            FROM 
                chuvas_diarias c
            INNER JOIN 
                alagamentos a ON c.municipio = a.municipio AND c.data = a.data
            WHERE 
                c.municipio = :cidade
            GROUP BY 
                CASE
                    WHEN c.precipitacao_diaria < 30 THEN 'baixa'
                    WHEN c.precipitacao_diaria < 50 THEN 'média'
                    ELSE 'alta'
                END
            """
            
            params = {'cidade': cidade}
            df = execute_query(query, params)
            
            # Determinar faixa da precipitação prevista
            if precipitacao_prevista < 30:
                faixa = 'baixa'
            elif precipitacao_prevista < 50:
                faixa = 'média'
            else:
                faixa = 'alta'
            
            # Se não houver dados históricos, usar estimativas padrão
            if df.empty:
                if faixa == 'baixa':
                    afetados_estimados = 50
                    nivel_risco = 'baixo'
                elif faixa == 'média':
                    afetados_estimados = 200
                    nivel_risco = 'médio'
                else:
                    afetados_estimados = 500
                    nivel_risco = 'alto'
            else:
                # Buscar média de afetados para a faixa correspondente
                row = df[df['faixa_precipitacao'] == faixa]
                if not row.empty:
                    media_afetados = float(row['media_afetados'].iloc[0])
                    if pd.isna(media_afetados):
                        # Valor padrão se não houver dados
                        media_afetados = 200
                else:
                    # Valor padrão se não houver dados para esta faixa
                    media_afetados = 200
                
                # Adicionar variação aleatória para simular incerteza
                afetados_estimados = int(media_afetados * np.random.uniform(0.8, 1.2))
                
                # Determinar nível de risco
                if afetados_estimados < 100:
                    nivel_risco = 'baixo'
                elif afetados_estimados < 300:
                    nivel_risco = 'médio'
                else:
                    nivel_risco = 'alto'
            
            # Calcular probabilidade de alagamento
            probabilidade = PrevisaoService.calcular_probabilidade_alagamento(
                cidade, estado, precipitacao_prevista
            )
            
            return {
                'precipitacao': round(precipitacao_prevista, 1),
                'probabilidade_alagamento': round(probabilidade, 2),
                'afetados_estimados': afetados_estimados,
                'nivel_risco': nivel_risco
            }
            
        except Exception as e:
            print(f"Erro ao calcular impacto de precipitação: {str(e)}")
            # Valores padrão em caso de erro
            return {
                'precipitacao': round(precipitacao_prevista, 1),
                'probabilidade_alagamento': 0.5,
                'afetados_estimados': 100,
                'nivel_risco': 'médio',
                'erro': str(e)
            } 