"""
Pacote de configuração da API
"""
from .database import DB_CONFIG, USE_MOCK_DATA, API_CONFIG
from .openweather import OPENWEATHER_API_KEY

# Extrair configurações da API
PORT = API_CONFIG['port']
DEBUG = API_CONFIG['debug']

__all__ = [
    'DB_CONFIG',
    'USE_MOCK_DATA',
    'API_CONFIG',
    'OPENWEATHER_API_KEY',
    'PORT',
    'DEBUG'
] 