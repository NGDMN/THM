import requests
import datetime
import logging
import time
from api.utils.db_utils import execute_query, execute_dml
from api.config import OPENWEATHER_API_KEY
from api.services.previsao_service import PrevisaoService

# Configuração da API OpenWeatherMap
# OPENWEATHER_API_KEY agora vem do config
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Mapeamento de IDs de cidades de SP e RJ
CITY_IDS = {
    # São Paulo
    "São Paulo": {"id": 3448439, "state": "SP"},
    "Campinas": {"id": 3467865, "state": "SP"},
    "Santos": {"id": 3449433, "state": "SP"},
    "Guarulhos": {"id": 3461786, "state": "SP"},
    "São Bernardo do Campo": {"id": 3449319, "state": "SP"},
    "Osasco": {"id": 3455713, "state": "SP"},
    "São José dos Campos": {"id": 3448636, "state": "SP"},
    "Ribeirão Preto": {"id": 3451328, "state": "SP"},
    "Sorocaba": {"id": 3447399, "state": "SP"},
    "São José do Rio Preto": {"id": 3448632, "state": "SP"},
    
    # Rio de Janeiro
    "Rio de Janeiro": {"id": 3451190, "state": "RJ"},
    "Niterói": {"id": 3456160, "state": "RJ"},
    "Petrópolis": {"id": 3454031, "state": "RJ"},
    "Nova Iguaçu": {"id": 3456163, "state": "RJ"},
    "São Gonçalo": {"id": 3448903, "state": "RJ"},
    "Duque de Caxias": {"id": 3464305, "state": "RJ"},
    "São João de Meriti": {"id": 3448905, "state": "RJ"},
    "Belford Roxo": {"id": 3470127, "state": "RJ"},
    "Angra dos Reis": {"id": 3472287, "state": "RJ"},
    "Volta Redonda": {"id": 3444924, "state": "RJ"}
}

logger = logging.getLogger(__name__)

class OpenWeatherService:
    """
    Serviço para interagir com a API do OpenWeatherMap
    """
    
    # Adicionar CITY_IDS como atributo estático da classe
    CITY_IDS = CITY_IDS
    
    @staticmethod
    def get_weather_forecast(cidade, estado, dias=5, max_retries=3):
        """
        Obtém previsão do tempo para uma cidade específica
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            dias (int): Número de dias para previsão
            max_retries (int): Número máximo de tentativas em caso de erro
            
        Returns:
            list: Lista de previsões diárias
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                cidade_formatada = cidade.title()
                
                # Verificar se temos o ID da cidade ou usar pesquisa por nome
                if cidade_formatada in CITY_IDS:
                    city_id = CITY_IDS[cidade_formatada]["id"]
                    url = f"{OPENWEATHER_BASE_URL}/forecast?id={city_id}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
                else:
                    url = f"{OPENWEATHER_BASE_URL}/forecast?q={cidade_formatada},{estado},BR&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
                
                response = requests.get(url)
                
                if response.status_code == 401:
                    logger.error("API key inválida ou expirada")
                    return []
                elif response.status_code == 429:
                    logger.warning("Limite de requisições excedido, aguardando...")
                    time.sleep(60)  # Espera 1 minuto antes de tentar novamente
                    retry_count += 1
                    continue
                elif response.status_code != 200:
                    logger.error(f"Erro na API OpenWeatherMap: {response.status_code} - {response.text}")
                    retry_count += 1
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    continue
                    
                data = response.json()
                
                # Processar dados da previsão
                previsoes = []
                data_atual = None
                previsao_diaria = None
                
                for item in data.get('list', []):
                    # Converter timestamp para data
                    timestamp = item.get('dt')
                    data_hora = datetime.datetime.fromtimestamp(timestamp)
                    data = data_hora.date()
                    
                    # Se for uma nova data, criar nova previsão diária
                    if data != data_atual:
                        # Salvar previsão anterior se existir
                        if previsao_diaria:
                            previsoes.append(previsao_diaria)
                        
                        # Iniciar nova previsão
                        data_atual = data
                        previsao_diaria = {
                            'data': data.strftime('%Y-%m-%d'),
                            'cidade': cidade_formatada,
                            'estado': estado,
                            'temp_min': item['main']['temp_min'],
                            'temp_max': item['main']['temp_max'],
                            'precipitacao': 0,  # Será acumulado
                            'umidade': item['main']['humidity'],
                            'descricao': item['weather'][0]['description'],
                            'icone': item['weather'][0]['icon']
                        }
                    
                    # Atualizar temperatura máxima/mínima se necessário
                    if item['main']['temp_max'] > previsao_diaria['temp_max']:
                        previsao_diaria['temp_max'] = item['main']['temp_max']
                    if item['main']['temp_min'] < previsao_diaria['temp_min']:
                        previsao_diaria['temp_min'] = item['main']['temp_min']
                    
                    # Acumular precipitação (se disponível)
                    if 'rain' in item and '3h' in item['rain']:
                        previsao_diaria['precipitacao'] += item['rain']['3h']
                
                # Adicionar última previsão
                if previsao_diaria and data_atual:
                    previsoes.append(previsao_diaria)
                
                # Limitar ao número de dias solicitados
                dias_disponiveis = min(dias, len(previsoes))
                logger.info(f"Obtidas {dias_disponiveis} dias de previsão para {cidade_formatada}-{estado}")
                
                return previsoes[:dias_disponiveis]
                
            except Exception as e:
                logger.error(f"Erro ao obter previsão do OpenWeatherMap: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    continue
                return []
    
    @staticmethod
    def salvar_previsoes(previsoes):
        """
        Salva previsões no banco de dados
        
        Args:
            previsoes (list): Lista de previsões diárias
            
        Returns:
            int: Número de previsões salvas
        """
        try:
            # Query para inserir ou atualizar previsões
            query = """
            INSERT INTO previsoes (
                cidade, estado, data, temp_min, temp_max, 
                precipitacao, umidade, descricao, icone
            ) VALUES (
                :cidade, :estado, TO_DATE(:data, 'YYYY-MM-DD'), 
                :temp_min, :temp_max, :precipitacao, :umidade, :descricao, :icone
            )
            ON CONFLICT (cidade, estado, data) DO UPDATE SET
                temp_min = EXCLUDED.temp_min,
                temp_max = EXCLUDED.temp_max,
                precipitacao = EXCLUDED.precipitacao,
                umidade = EXCLUDED.umidade,
                descricao = EXCLUDED.descricao,
                icone = EXCLUDED.icone
            """
            
            # Preparar parâmetros para inserção
            params = []
            for previsao in previsoes:
                params.append({
                    'cidade': previsao['cidade'],
                    'estado': previsao['estado'],
                    'data': previsao['data'],
                    'temp_min': previsao['temp_min'],
                    'temp_max': previsao['temp_max'],
                    'precipitacao': previsao['precipitacao'],
                    'umidade': previsao['umidade'],
                    'descricao': previsao['descricao'],
                    'icone': previsao['icone']
                })
            
            # Executar inserção
            registros_inseridos = execute_dml(query, params)
            
            return registros_inseridos
            
        except Exception as e:
            logger.error(f"Erro ao salvar previsões: {str(e)}")
            return 0
    
    @staticmethod
    def atualizar_previsoes_todas_cidades(dias=7):
        """
        Atualiza previsões para todas as cidades cadastradas
        
        Args:
            dias (int): Número de dias para previsão
            
        Returns:
            dict: Resultado da atualização por cidade
        """
        resultados = {}
        logger.info("Iniciando atualização de previsões para todas as cidades...")
        
        for cidade, info in CITY_IDS.items():
            try:
                logger.info(f"Buscando previsões para {cidade}-{info['state']}")
                previsoes = OpenWeatherService.get_weather_forecast(cidade, info["state"], dias)
                
                if not previsoes:
                    logger.warning(f"Nenhuma previsão obtida para {cidade}")
                    resultados[cidade] = 0
                    continue
                
                # Enriquecer previsões com dados de risco
                previsoes = OpenWeatherService.enrich_with_risk(previsoes, cidade, info["state"])
                
                # Salvar previsões
                registros = OpenWeatherService.salvar_previsoes(previsoes)
                logger.info(f"Registros inseridos para {cidade}: {registros}")
                resultados[cidade] = registros
                
            except Exception as e:
                logger.error(f"Erro ao atualizar previsões para {cidade}: {str(e)}")
                resultados[cidade] = 0
        
        logger.info(f"Resultado final da atualização: {resultados}")
        return resultados

    @staticmethod
    def enrich_with_risk(previsoes, cidade, estado):
        """
        Enriquecer previsões meteorológicas com cálculo de risco de alagamento
        """
        for previsao in previsoes:
            precipitacao = previsao.get('precipitacao', 0)
            impacto = PrevisaoService.calcular_impacto_precipitacao(cidade, estado, precipitacao)
            previsao['risco_alagamento'] = {
                'probabilidade': impacto['probabilidade_alagamento'],
                'nivel': impacto['nivel_risco'],
                'afetados_estimados': impacto['afetados_estimados']
            }
        return previsoes 