import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging

# Carrega variáveis do arquivo .env
load_dotenv()

@dataclass
class DatabaseConfig:
    """Configurações do banco de dados"""
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', 5432))
    DB_NAME: str = os.getenv('DB_NAME', 'sistema_climatico')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    DB_URL: str = None
    
    def __post_init__(self):
        """Constrói a URL de conexão após inicialização"""
        if not self.DB_URL:
            self.DB_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

@dataclass
class ApiConfig:
    """Configurações de APIs externas"""
    OPENWEATHER_API_KEY: str = os.getenv('OPENWEATHER_API_KEY', '')
    OPENWEATHER_BASE_URL: str = 'https://api.openweathermap.org/data/2.5'
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', 30))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', 3))

@dataclass
class AppConfig:
    """Configurações gerais da aplicação"""
    DEBUG: bool = field(default_factory=lambda: os.getenv('DEBUG', 'False').lower() == 'true')
    SECRET_KEY: str = field(default_factory=lambda: os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'))
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    
    # Estados e cidades suportados - usando field com default_factory
    ESTADOS_SUPORTADOS: List[str] = field(default_factory=lambda: [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 
        'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 
        'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ])
    
    CIDADES_PRINCIPAIS: Dict[str, List[str]] = field(default_factory=lambda: {
        'SP': ['São Paulo', 'Campinas', 'Santos', 'São Bernardo do Campo'],
        'RJ': ['Rio de Janeiro', 'Niterói', 'Campos dos Goytacazes'],
        'MG': ['Belo Horizonte', 'Uberlândia', 'Contagem'],
        'RS': ['Porto Alegre', 'Caxias do Sul', 'Pelotas'],
        'PR': ['Curitiba', 'Londrina', 'Maringá'],
        'SC': ['Florianópolis', 'Joinville', 'Blumenau'],
        'BA': ['Salvador', 'Feira de Santana', 'Vitória da Conquista'],
        'GO': ['Goiânia', 'Aparecida de Goiânia', 'Anápolis'],
        'PE': ['Recife', 'Jaboatão dos Guararapes', 'Olinda'],
        'CE': ['Fortaleza', 'Caucaia', 'Juazeiro do Norte']
    })

@dataclass
class CacheConfig:
    """Configurações de cache"""
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', 1800))  # 30 minutos
    CACHE_SIZE: int = int(os.getenv('CACHE_SIZE', 1000))
    ENABLE_CACHE: bool = os.getenv('ENABLE_CACHE', 'True').lower() == 'true'

@dataclass
class WeatherConfig:
    """Configurações específicas para dados meteorológicos"""
    UPDATE_INTERVAL: int = int(os.getenv('WEATHER_UPDATE_INTERVAL', 3600))  # 1 hora
    ALERT_TEMPERATURE_MIN: float = float(os.getenv('ALERT_TEMP_MIN', 0.0))
    ALERT_TEMPERATURE_MAX: float = float(os.getenv('ALERT_TEMP_MAX', 40.0))
    ALERT_HUMIDITY_MIN: float = float(os.getenv('ALERT_HUMIDITY_MIN', 20.0))
    ALERT_HUMIDITY_MAX: float = float(os.getenv('ALERT_HUMIDITY_MAX', 90.0))

class Config:
    """Classe principal de configurações"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.api = ApiConfig()
        self.app = AppConfig()
        self.cache = CacheConfig()
        self.weather = WeatherConfig()
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura o sistema de logging"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=getattr(logging, self.app.LOG_LEVEL),
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('app.log') if not self.app.DEBUG else logging.NullHandler()
            ]
        )
    
    def validate_all(self) -> Dict[str, Any]:
        """Valida todas as configurações e retorna um relatório"""
        validations = {
            'database': self._validate_database(),
            'api': self._validate_api(),
            'app': self._validate_app(),
            'cache': self._validate_cache(),
            'weather': self._validate_weather(),
            'overall_status': 'success'
        }
        
        # Determina status geral
        failed_validations = [k for k, v in validations.items() 
                            if isinstance(v, dict) and not v.get('valid', True)]
        
        if failed_validations:
            validations['overall_status'] = 'warning'
            validations['failed_sections'] = failed_validations
        
        return validations
    
    def _validate_database(self) -> Dict[str, Any]:
        """Valida configurações do banco de dados"""
        validation = {
            'valid': True,
            'issues': [],
            'config': {
                'host': self.database.DB_HOST,
                'port': self.database.DB_PORT,
                'database': self.database.DB_NAME,
                'user': self.database.DB_USER,
                'password_set': bool(self.database.DB_PASSWORD)
            }
        }
        
        if not self.database.DB_PASSWORD:
            validation['issues'].append('Password do banco não configurada')
            validation['valid'] = False
        
        if not self.database.DB_NAME:
            validation['issues'].append('Nome do banco não configurado')
            validation['valid'] = False
            
        return validation
    
    def _validate_api(self) -> Dict[str, Any]:
        """Valida configurações de APIs"""
        validation = {
            'valid': True,
            'issues': [],
            'config': {
                'openweather_key_set': bool(self.api.OPENWEATHER_API_KEY),
                'timeout': self.api.REQUEST_TIMEOUT,
                'max_retries': self.api.MAX_RETRIES
            }
        }
        
        if not self.api.OPENWEATHER_API_KEY:
            validation['issues'].append('Chave da API OpenWeather não configurada')
            validation['valid'] = False
        
        if self.api.REQUEST_TIMEOUT < 5:
            validation['issues'].append('Timeout muito baixo (recomendado: >= 5s)')
            
        return validation
    
    def _validate_app(self) -> Dict[str, Any]:
        """Valida configurações da aplicação"""
        validation = {
            'valid': True,
            'issues': [],
            'config': {
                'debug': self.app.DEBUG,
                'secret_key_set': bool(self.app.SECRET_KEY),
                'log_level': self.app.LOG_LEVEL,
                'estados_count': len(self.app.ESTADOS_SUPORTADOS)
            }
        }
        
        if self.app.SECRET_KEY == 'dev-secret-key-change-in-production':
            validation['issues'].append('SECRET_KEY usando valor padrão (inseguro para produção)')
            if not self.app.DEBUG:
                validation['valid'] = False
                
        return validation
    
    def _validate_cache(self) -> Dict[str, Any]:
        """Valida configurações de cache"""
        validation = {
            'valid': True,
            'issues': [],
            'config': {
                'enabled': self.cache.ENABLE_CACHE,
                'ttl': self.cache.CACHE_TTL,
                'size': self.cache.CACHE_SIZE
            }
        }
        
        if self.cache.CACHE_TTL < 300:  # 5 minutos
            validation['issues'].append('TTL do cache muito baixo (recomendado: >= 300s)')
            
        return validation
    
    def _validate_weather(self) -> Dict[str, Any]:
        """Valida configurações meteorológicas"""
        validation = {
            'valid': True,
            'issues': [],
            'config': {
                'update_interval': self.weather.UPDATE_INTERVAL,
                'temp_range': f"{self.weather.ALERT_TEMPERATURE_MIN}°C - {self.weather.ALERT_TEMPERATURE_MAX}°C",
                'humidity_range': f"{self.weather.ALERT_HUMIDITY_MIN}% - {self.weather.ALERT_HUMIDITY_MAX}%"
            }
        }
        
        if self.weather.UPDATE_INTERVAL < 600:  # 10 minutos
            validation['issues'].append('Intervalo de atualização muito baixo (recomendado: >= 600s)')
            
        return validation
    
    def get_env_template(self) -> str:
        """Retorna um template do arquivo .env"""
        return """# Configurações do Banco de Dados
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sistema_climatico
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui

# APIs Externas
OPENWEATHER_API_KEY=sua_chave_api_aqui

# Configurações da Aplicação
DEBUG=True
SECRET_KEY=sua_chave_secreta_aqui
LOG_LEVEL=INFO

# Cache
CACHE_TTL=1800
CACHE_SIZE=1000
ENABLE_CACHE=True

# Configurações Meteorológicas
WEATHER_UPDATE_INTERVAL=3600
ALERT_TEMP_MIN=0.0
ALERT_TEMP_MAX=40.0
ALERT_HUMIDITY_MIN=20.0
ALERT_HUMIDITY_MAX=90.0

# Configurações de Requisição
REQUEST_TIMEOUT=30
MAX_RETRIES=3
"""

# Instância global das configurações
config = Config()

# Função de conveniência para validação rápida
def validate_all():
    """Função de conveniência para validação"""
    return config.validate_all()

if __name__ == "__main__":
    # Teste básico quando executado diretamente
    print("🔧 Testando configurações...")
    results = validate_all()
    
    if results['overall_status'] == 'success':
        print("✅ Todas as configurações são válidas!")
    else:
        print("⚠️ Algumas configurações precisam de atenção:")
        for section, data in results.items():
            if isinstance(data, dict) and not data.get('valid', True):
                print(f"  {section}: {', '.join(data['issues'])}")