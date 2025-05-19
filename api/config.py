import os
# Removendo a dependência do arquivo .env que está causando erro
# from dotenv import load_dotenv
# load_dotenv()

# Configuração para usar banco de dados real ao invés de dados simulados
USE_MOCK_DATA = False

# Configurações do banco de dados PostgreSQL no Render
DB_CONFIG = {
    'dbname': 'thm_iy9l',
    'user': 'thm_admin',
    'password': 'fBfTMpHLfe2htlV9fe63mc0v9SmUTStS',
    'host': 'dpg-d0l48cre5dus73c970sg-a.ohio-postgres.render.com',
    'port': '5432'
}

# Configuração da API do OpenWeatherMap
OPENWEATHER_API_KEY = "50508f185d7a5337e4929c8816d2a46e"
OPENWEATHER_API_NAME = "Projeto_THM"

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