import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Forçar o uso de dados simulados para evitar erros de conexão com o banco
USE_MOCK_DATA = True

# Configurações do banco de dados PostgreSQL
DB_CONFIG = {
    'dbname': os.getenv('PG_DBNAME', 'thm'),
    'user': os.getenv('PG_USER', 'postgres'),
    'password': os.getenv('PG_PASSWORD', ''),
    'host': os.getenv('PG_HOST', 'localhost'),
    'port': os.getenv('PG_PORT', '5432')
}

# Configuração do Flask
DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
PORT = int(os.getenv('PORT', 5000))

# Caminhos para arquivos de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')

# Configuração para logs
LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR) 