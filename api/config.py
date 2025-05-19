import os
from dotenv import load_dotenv

# Define o caminho para o arquivo .env na raiz do projeto
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

# Carrega as variáveis do arquivo .env da raiz
load_dotenv(dotenv_path=dotenv_path)

# Configuração para usar banco de dados real ao invés de dados simulados
USE_MOCK_DATA = False

# Configurações do banco de dados PostgreSQL no Render
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# Configuração da API do OpenWeatherMap
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_API_NAME = os.getenv('OPENWEATHER_API_NAME')

# Configuração do Flask
DEBUG = os.environ.get('FLASK_ENV', 'development') == 'development'
PORT = int(os.environ.get('PORT', 5000))

# Caminhos para arquivos de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')

# Configuração para logs
LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR) 