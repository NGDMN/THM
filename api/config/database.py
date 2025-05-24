import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações do banco de dados PostgreSQL
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'thm'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

# Flag para usar dados reais do banco
USE_MOCK_DATA = os.getenv('USE_MOCK_DATA', 'False').lower() == 'true'

# Configurações da API
API_CONFIG = {
    'debug': os.getenv('FLASK_ENV', 'development') == 'development',
    'port': int(os.getenv('PORT', 5000))
} 