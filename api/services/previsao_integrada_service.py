import logging
import datetime
from api.services.openweather_service import OpenWeatherService
from api.services.previsao_service import PrevisaoService
from api.utils.db_utils import execute_query, execute_dml

logger = logging.getLogger(__name__)

class PrevisaoIntegradaService:
    """
    Serviço para integrar previsões meteorológicas do OpenWeatherMap com 
    cálculos de risco de alagamento, e salvar no banco de dados.
    """
    
    @staticmethod
    def obter_previsoes_com_risco(cidade, estado, dias=6):
        """
        Obtém previsões meteorológicas com cálculo de risco de alagamento
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            dias (int): Número de dias para previsão (máx 6)
            
        Returns:
            list: Lista de previsões com cálculos de risco de alagamento
        """
        try:
            # Obter previsões do OpenWeatherMap
            previsoes = OpenWeatherService.get_weather_forecast(cidade, estado, dias)
            
            if not previsoes:
                logger.warning(f"Nenhuma previsão disponível para {cidade}-{estado}")
                return []
            
            # Enriquecer cada previsão com cálculos de risco
            for previsao in previsoes:
                precipitacao = previsao.get('precipitacao', 0)
                
                # Calcular impacto da precipitação
                impacto = PrevisaoService.calcular_impacto_precipitacao(
                    cidade, estado, precipitacao
                )
                
                # Adicionar informações de risco à previsão
                previsao['risco_alagamento'] = {
                    'probabilidade': impacto['probabilidade_alagamento'],
                    'nivel': impacto['nivel_risco'],
                    'afetados_estimados': impacto['afetados_estimados']
                }
            
            logger.info(f"Obtidas {len(previsoes)} previsões com análise de risco para {cidade}-{estado}")
            return previsoes
            
        except Exception as e:
            logger.error(f"Erro ao obter previsões com risco: {str(e)}")
            return []
    
    @staticmethod
    def salvar_previsoes_com_risco(previsoes):
        """
        Salva previsões com análise de risco no banco de dados
        
        Args:
            previsoes (list): Lista de previsões com análise de risco
            
        Returns:
            int: Número de registros salvos
        """
        try:
            if not previsoes:
                logger.warning("Nenhuma previsão para salvar")
                return 0
                
            # Query para inserir ou atualizar previsões com informações de risco
            query = """
            INSERT INTO previsoes (
                cidade, estado, data, temp_min, temp_max, 
                precipitacao, umidade, descricao, icone,
                probabilidade_alagamento, nivel_risco, afetados_estimados
            ) VALUES (
                :cidade, :estado, TO_DATE(:data, 'YYYY-MM-DD'), 
                :temp_min, :temp_max, :precipitacao, :umidade, :descricao, :icone,
                :probabilidade, :nivel_risco, :afetados_estimados
            )
            ON CONFLICT (cidade, estado, data) DO UPDATE SET
                temp_min = EXCLUDED.temp_min,
                temp_max = EXCLUDED.temp_max,
                precipitacao = EXCLUDED.precipitacao,
                umidade = EXCLUDED.umidade,
                descricao = EXCLUDED.descricao,
                icone = EXCLUDED.icone,
                probabilidade_alagamento = EXCLUDED.probabilidade_alagamento,
                nivel_risco = EXCLUDED.nivel_risco,
                afetados_estimados = EXCLUDED.afetados_estimados,
                updated_at = CURRENT_TIMESTAMP
            """
            
            # Preparar parâmetros para inserção
            params = []
            for previsao in previsoes:
                # Extrair dados de risco
                risco = previsao.get('risco_alagamento', {})
                
                params.append({
                    'cidade': previsao['cidade'],
                    'estado': previsao['estado'],
                    'data': previsao['data'],
                    'temp_min': previsao['temp_min'],
                    'temp_max': previsao['temp_max'],
                    'precipitacao': previsao['precipitacao'],
                    'umidade': previsao['umidade'],
                    'descricao': previsao['descricao'],
                    'icone': previsao['icone'],
                    'probabilidade': risco.get('probabilidade', 0),
                    'nivel_risco': risco.get('nivel', 'baixo'),
                    'afetados_estimados': risco.get('afetados_estimados', 0)
                })
            
            # Executar inserção
            registros_inseridos = execute_dml(query, params)
            logger.info(f"Salvos {registros_inseridos} registros de previsão com análise de risco")
            
            return registros_inseridos
            
        except Exception as e:
            logger.error(f"Erro ao salvar previsões com risco: {str(e)}")
            return 0
    
    @staticmethod
    def atualizar_previsoes_todas_cidades(dias=6):
        """
        Atualiza previsões e cálculos de risco para todas as cidades cadastradas
        
        Args:
            dias (int): Número de dias para previsão
            
        Returns:
            dict: Resultado da atualização por cidade
        """
        resultados = {}
        
        # Obter lista de cidades de SP e RJ do OpenWeatherService
        cidades = {k: v for k, v in OpenWeatherService.CITY_IDS.items() 
                  if v["state"] in ["SP", "RJ"]}
        
        logger.info(f"Atualizando previsões e riscos para {len(cidades)} cidades")
        
        # Para cada cidade, obter previsões com risco e salvar
        for cidade, info in cidades.items():
            try:
                # Obter previsões com análise de risco
                previsoes = PrevisaoIntegradaService.obter_previsoes_com_risco(
                    cidade, info["state"], dias
                )
                
                # Salvar no banco de dados
                registros = PrevisaoIntegradaService.salvar_previsoes_com_risco(previsoes)
                resultados[cidade] = registros
                
                logger.info(f"Atualizadas {registros} previsões para {cidade}")
                
            except Exception as e:
                logger.error(f"Erro ao atualizar previsões para {cidade}: {str(e)}")
                resultados[cidade] = 0
        
        return resultados
    
    @staticmethod
    def obter_alertas_alagamento(cidade=None, estado=None, limiar_probabilidade=0.6):
        """
        Obtém alertas de alagamento baseados nas previsões recentes
        
        Args:
            cidade (str, optional): Filtrar por cidade
            estado (str, optional): Filtrar por estado
            limiar_probabilidade (float): Limiar para considerar alerta
            
        Returns:
            list: Lista de alertas de alagamento
        """
        try:
            # Construir consulta para obter previsões com alto risco de alagamento
            query = """
            SELECT 
                cidade, estado, data, precipitacao,
                probabilidade_alagamento, nivel_risco, afetados_estimados,
                created_at
            FROM 
                previsoes
            WHERE 
                data >= CURRENT_DATE
                AND probabilidade_alagamento >= :limiar
            """
            
            params = {'limiar': limiar_probabilidade}
            
            # Adicionar filtros opcionais
            if cidade:
                query += " AND cidade = :cidade"
                params['cidade'] = cidade
                
            if estado:
                query += " AND estado = :estado"
                params['estado'] = estado
                
            # Ordenar por data e probabilidade
            query += " ORDER BY data, probabilidade_alagamento DESC"
            
            # Executar consulta
            df = execute_query(query, params)
            
            # Se não houver resultados, retornar lista vazia
            if df.empty:
                return []
            
            # Converter para lista de dicionários
            alertas = []
            for _, row in df.iterrows():
                alertas.append({
                    'cidade': row['cidade'],
                    'estado': row['estado'],
                    'data': row['data'].strftime('%Y-%m-%d') if hasattr(row['data'], 'strftime') else row['data'],
                    'precipitacao': float(row['precipitacao']),
                    'probabilidade': float(row['probabilidade_alagamento']),
                    'nivel_risco': row['nivel_risco'],
                    'afetados_estimados': int(row['afetados_estimados']),
                    'data_atualizacao': row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(row['created_at'], 'strftime') else row['created_at']
                })
            
            return alertas
            
        except Exception as e:
            logger.error(f"Erro ao obter alertas de alagamento: {str(e)}")
            return [] 