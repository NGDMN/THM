import requests
import datetime
import logging
from api.utils.db_utils import execute_query, execute_dml

# Configuração da API OpenWeatherMap
OPENWEATHER_API_KEY = "50508f185d7a5337e4929c8816d2a46e"
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Mapeamento de IDs de cidades brasileiras importantes
CITY_IDS = {
    "São Paulo": {"id": 3448439, "state": "SP"},
    "Rio de Janeiro": {"id": 3451190, "state": "RJ"},
    "Belo Horizonte": {"id": 3470127, "state": "MG"},
    "Salvador": {"id": 3450554, "state": "BA"},
    "Fortaleza": {"id": 3399415, "state": "CE"},
    "Recife": {"id": 3390760, "state": "PE"},
    # Adicionando mais cidades de SP e RJ para melhor cobertura
    "Campinas": {"id": 3467865, "state": "SP"},
    "Santos": {"id": 3449433, "state": "SP"},
    "Niterói": {"id": 3456160, "state": "RJ"},
    "Petrópolis": {"id": 3454031, "state": "RJ"},
}

logger = logging.getLogger(__name__)

class OpenWeatherService:
    """
    Serviço para interagir com a API do OpenWeatherMap
    """
    
    # Adicionar CITY_IDS como atributo estático da classe
    CITY_IDS = CITY_IDS
    
    @staticmethod
    def get_weather_forecast(cidade, estado, dias=5):
        """
        Obtém previsão do tempo para uma cidade específica
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            dias (int): Número de dias para previsão (NOTA: API gratuita do OpenWeatherMap 
                        geralmente limita a 5 dias, mesmo solicitando mais dias)
            
        Returns:
            list: Lista de previsões diárias
        """
        try:
            cidade_formatada = cidade.title()
            
            # Verificar se temos o ID da cidade ou usar pesquisa por nome
            if cidade_formatada in CITY_IDS:
                city_id = CITY_IDS[cidade_formatada]["id"]
                url = f"{OPENWEATHER_BASE_URL}/forecast?id={city_id}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
            else:
                url = f"{OPENWEATHER_BASE_URL}/forecast?q={cidade_formatada},{estado},BR&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
            
            response = requests.get(url)
            
            if response.status_code != 200:
                logger.error(f"Erro na API OpenWeatherMap: {response.status_code} - {response.text}")
                return []
                
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
            
            # Limitar ao número de dias solicitados, mas não mais do que o que temos
            dias_disponiveis = min(dias, len(previsoes))
            logger.info(f"Obtidas {dias_disponiveis} dias de previsão para {cidade_formatada}-{estado}")
            
            return previsoes[:dias_disponiveis]
            
        except Exception as e:
            logger.error(f"Erro ao obter previsão do OpenWeatherMap: {str(e)}")
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
    def atualizar_previsoes_todas_cidades(dias=5):
        """
        Atualiza previsões para todas as cidades cadastradas
        
        Args:
            dias (int): Número de dias para previsão (API gratuita limita a 5 dias)
            
        Returns:
            dict: Resultado da atualização por cidade
        """
        resultados = {}
        
        # Atualizar para cidades específicas de SP e RJ
        for cidade, info in CITY_IDS.items():
            if info["state"] in ["SP", "RJ"]:
                previsoes = OpenWeatherService.get_weather_forecast(cidade, info["state"], dias)
                registros = OpenWeatherService.salvar_previsoes(previsoes)
                resultados[cidade] = registros
        
        return resultados 