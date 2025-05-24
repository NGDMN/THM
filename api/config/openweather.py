"""
Configurações da API OpenWeather
"""
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Chave da API OpenWeather
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '') 