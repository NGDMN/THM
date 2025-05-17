import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do banco de dados Oracle
DB_CONFIG = {
    'user': os.getenv('ORACLE_USER', 'ADMIN'),
    'password': os.getenv('ORACLE_PASSWORD', ''),
    'dsn': os.getenv('ORACLE_DSN', 'chuvasalagamentos_high'),
    'encoding': 'UTF-8'
}

# Diretório do Oracle Wallet
TNS_ADMIN = os.getenv('TNS_ADMIN', '')

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