# app.py - Aplicação Flask Refatorada (mantendo funcionalidades existentes)
import os
import sys
import logging
import atexit
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, g, current_app
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from functools import wraps
import time
import json

# Configurar path do Python (mantém compatibilidade)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa configurações personalizadas
from config import config

# Cache simples em memória
app_cache = {}

def create_app(config_override=None):
    """
    Application Factory Pattern - Cria e configura a aplicação Flask
    
    Args:
        config_override: Configurações personalizadas para testes
    
    Returns:
        Flask: Instância configurada da aplicação
    """
    app = Flask(__name__)
    
    # Aplicar configurações
    configure_app(app, config_override)
    
    # Configurar extensões
    configure_extensions(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Configurar handlers de erro
    configure_error_handlers(app)
    
    # Configurar logging
    configure_logging(app)
    
    # Configurar hooks de request/response
    configure_hooks(app)
    
    # Configurar scheduler (tarefas automáticas)
    configure_scheduler(app)
    
    return app

def configure_app(app, config_override=None):
    """Configura as definições da aplicação usando novo sistema de config"""
    
    # Configurações básicas do Flask
    app.config['SECRET_KEY'] = config.app.SECRET_KEY
    app.config['DEBUG'] = config.app.DEBUG
    
    # Configurações de banco (mantém compatibilidade)
    app.config['DATABASE_URL'] = config.database.DB_URL
    app.config['DB_CONFIG'] = {
        'host': config.database.DB_HOST,
        'port': config.database.DB_PORT,
        'database': config.database.DB_NAME,
        'user': config.database.DB_USER,
        'password': config.database.DB_PASSWORD
    }
    
    # Configurações da API do tempo
    app.config['OPENWEATHER_API_KEY'] = config.api.OPENWEATHER_API_KEY
    app.config['OPENWEATHER_BASE_URL'] = config.api.OPENWEATHER_BASE_URL
    app.config['REQUEST_TIMEOUT'] = config.api.REQUEST_TIMEOUT
    app.config['MAX_RETRIES'] = config.api.MAX_RETRIES
    
    # Configurações de cache
    app.config['CACHE_TTL'] = config.cache.CACHE_TTL
    app.config['CACHE_SIZE'] = config.cache.CACHE_SIZE
    app.config['ENABLE_CACHE'] = config.cache.ENABLE_CACHE
    
    # Configurações meteorológicas
    app.config['WEATHER_UPDATE_INTERVAL'] = config.weather.UPDATE_INTERVAL
    app.config['ALERT_TEMPERATURE_MIN'] = config.weather.ALERT_TEMPERATURE_MIN
    app.config['ALERT_TEMPERATURE_MAX'] = config.weather.ALERT_TEMPERATURE_MAX
    app.config['ALERT_HUMIDITY_MIN'] = config.weather.ALERT_HUMIDITY_MIN
    app.config['ALERT_HUMIDITY_MAX'] = config.weather.ALERT_HUMIDITY_MAX
    
    # Estados e cidades
    app.config['ESTADOS_SUPORTADOS'] = config.app.ESTADOS_SUPORTADOS
    app.config['CIDADES_PRINCIPAIS'] = config.app.CIDADES_PRINCIPAIS
    
    # Configurações específicas do projeto (mantém compatibilidade)
    app.config['PORT'] = int(os.environ.get('PORT', 5000))
    
    # Aplicar configurações customizadas (para testes)
    if config_override:
        app.config.update(config_override)

def configure_extensions(app):
    """Configura extensões do Flask"""
    
    # CORS - permite requisições cross-origin (mantém configuração atual)
    CORS(app)

def register_blueprints(app):
    """Registra blueprints da aplicação"""
    
    # Blueprints existentes (mantém compatibilidade)
    try:
        from api.routes.previsao_routes import previsao_bp
        app.register_blueprint(previsao_bp)
        app.logger.info("✅ Blueprint previsao registrado")
    except ImportError as e:
        app.logger.warning(f"⚠️ Blueprint previsao não encontrado: {e}")
    
    try:
        from api.routes.historico import historico_bp
        app.register_blueprint(historico_bp)
        app.logger.info("✅ Blueprint historico registrado")
    except ImportError as e:
        app.logger.warning(f"⚠️ Blueprint historico não encontrado: {e}")
    
    # Registra rotas principais diretamente no app (mantém funcionalidades existentes)
    register_main_routes(app)

def register_main_routes(app):
    """Registra rotas principais mantendo funcionalidades existentes"""
    
    @app.route('/')
    def index():
        """Rota principal - status da API (versão melhorada)"""
        return jsonify({
            'status': 'online',
            'app': 'API do Sistema de Previsão de Alagamentos RJ/SP',
            'version': '2.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': [
                '/previsao/clima',
                '/previsao/chuvas',
                '/previsao/alagamentos', 
                '/previsao/alertas',
                '/historico/chuvas',
                '/historico/alagamentos',
                '/test-db',
                '/municipios',
                '/health',
                '/config/info',
                '/cache/stats'
            ],
            'config': {
                'debug': app.config['DEBUG'],
                'cache_enabled': app.config['ENABLE_CACHE'],
                'states_supported': len(app.config['ESTADOS_SUPORTADOS']),
                'api_ready': bool(app.config['OPENWEATHER_API_KEY']),
                'database_configured': bool(app.config['DB_CONFIG'])
            }
        })
    
    @app.route('/health')
    def health_check():
        """Health check melhorado"""
        try:
            # Testa conexão com banco
            db_status = test_database()
            
            # Testa API OpenWeather
            weather_api_status = test_openweather_api()
            
            # Testa configurações
            config_status = validate_configuration()
            
            all_ok = db_status and weather_api_status and config_status
            status = 'healthy' if all_ok else 'unhealthy'
            status_code = 200 if all_ok else 503
            
            return jsonify({
                'status': status,
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {
                    'database': 'ok' if db_status else 'error',
                    'weather_api': 'ok' if weather_api_status else 'error',
                    'configuration': 'ok' if config_status else 'error',
                    'cache': 'enabled' if app.config['ENABLE_CACHE'] else 'disabled'
                },
                'version': '2.0.0'
            }), status_code
            
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 503
    
    @app.route('/test-db', methods=['GET'])
    def test_db_endpoint():
        """Endpoint para testar conexão PostgreSQL (mantém funcionalidade)"""
        app.logger.info("🧪 Testando conexão PostgreSQL via endpoint...")
        success = test_database()
        
        return jsonify({
            'success': success,
            'message': 'Conexão testada - verifique logs do servidor',
            'database_config': {
                'host': app.config['DB_CONFIG']['host'],
                'database': app.config['DB_CONFIG']['database'],
                'user': app.config['DB_CONFIG']['user'],
                'port': app.config['DB_CONFIG']['port']
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @app.route('/municipios', methods=['GET'])
    def listar_municipios():
        """Lista municípios com fallback para PostgreSQL (mantém lógica)"""
        app.logger.info("🏙️ Buscando municípios...")
        
        try:
            # Tentar primeiro do CSV (atual)
            app.logger.info("📁 Tentando carregar do CSV...")
            
            # Busca CSV em diferentes locais possíveis
            csv_paths = [
                'data/municipios_RJ_SP_coords.csv',
                'api/data/municipios_RJ_SP_coords.csv',
                'data/raw/MunicipiosCoordenada.csv',
                'api/data/raw/MunicipiosCoordenada.csv'
            ]
            
            df = None
            for csv_path in csv_paths:
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    app.logger.info(f"✅ CSV encontrado em: {csv_path}")
                    break
            
            if df is not None:
                municipios = []
                for _, row in df.iterrows():
                    # Adapta para diferentes formatos de CSV
                    municipio_data = {
                        'nome': row.get('municipio', row.get('nome', row.get('cidade', ''))),
                        'uf': row.get('estado', row.get('uf', row.get('sigla_uf', '')))
                    }
                    if municipio_data['nome'] and municipio_data['uf']:
                        municipios.append(municipio_data)
                
                app.logger.info(f"✅ CSV carregado: {len(municipios)} municípios")
                return jsonify(municipios)
            
        except Exception as csv_error:
            app.logger.warning(f"⚠️ Erro ao carregar CSV: {csv_error}")
        
        # Fallback para PostgreSQL
        app.logger.info("🐘 Tentando carregar do PostgreSQL...")
        conn = get_db_connection()
        if not conn:
            return jsonify({'erro': 'Erro de conexão com banco de dados'}), 500
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT DISTINCT municipio as nome, estado as uf 
                    FROM municipios 
                    WHERE estado IN ('RJ', 'SP')
                    ORDER BY estado, municipio;
                """)
                municipios_db = cursor.fetchall()
                
                municipios = [dict(m) for m in municipios_db]
                app.logger.info(f"✅ PostgreSQL carregado: {len(municipios)} municípios")
                
                conn.close()
                return jsonify(municipios)
                
        except Exception as db_error:
            app.logger.error(f"❌ Erro ao carregar do PostgreSQL: {db_error}")
            conn.close()
            return jsonify({'erro': f'Erro ao carregar municípios: {str(db_error)}'}), 500
    
    # Endpoints de debug e admin (mantém funcionalidades)
    
    @app.route('/admin/atualizar-previsoes', methods=['POST', 'GET'])
    def admin_atualizar_previsoes():
        """Força atualização de previsões"""
        try:
            from api.services.openweather_service import OpenWeatherService
            resultado = OpenWeatherService.atualizar_previsoes_todas_cidades()
            return jsonify({
                'status': 'ok',
                'mensagem': 'Previsões atualizadas com sucesso!',
                'resultado': resultado,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            app.logger.error(f"❌ Erro ao atualizar previsões: {e}")
            return jsonify({
                'status': 'erro',
                'mensagem': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    @app.route('/debug/historico', methods=['GET'])
    def debug_historico():
        """Debug endpoint para verificar dados históricos"""
        conn = get_db_connection()
        if not conn:
            return jsonify({'erro': 'Erro de conexão'}), 500
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Contar registros
                cursor.execute("SELECT COUNT(*) as total FROM historico_chuvas;")
                chuvas_total = cursor.fetchone()['total']
                
                cursor.execute("SELECT COUNT(*) as total FROM historico_alagamentos;")
                alagamentos_total = cursor.fetchone()['total']
                
                # Top 5 municípios com mais registros de chuva
                cursor.execute("""
                    SELECT municipio, estado, COUNT(*) as total
                    FROM historico_chuvas
                    GROUP BY municipio, estado
                    ORDER BY total DESC
                    LIMIT 5;
                """)
                chuvas_por_municipio = cursor.fetchall()
                
                # Últimos registros de alagamentos
                cursor.execute("""
                    SELECT *
                    FROM historico_alagamentos
                    ORDER BY data DESC
                    LIMIT 5;
                """)
                ultimos_alagamentos = cursor.fetchall()
                
            conn.close()
            return jsonify({
                'chuvas_total': chuvas_total,
                'alagamentos_total': alagamentos_total,
                'chuvas_por_municipio': [dict(r) for r in chuvas_por_municipio],
                'ultimos_alagamentos': [dict(r) for r in ultimos_alagamentos],
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            app.logger.error(f"❌ Erro no debug histórico: {e}")
            conn.close()
            return jsonify({'erro': str(e)}), 500
    
    @app.route('/debug/tabelas', methods=['GET'])
    def debug_tabelas():
        """Verificar estrutura das tabelas"""
        conn = get_db_connection()
        if not conn:
            return jsonify({'erro': 'Erro de conexão'}), 500
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                result = {}
                
                # Verificar se tabelas existem
                cursor.execute("""
                    SELECT table_name, column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('historico_chuvas', 'historico_alagamentos', 'municipios')
                    ORDER BY table_name, ordinal_position;
                """)
                
                colunas = cursor.fetchall()
                for linha in colunas:
                    tabela = linha['table_name']
                    if tabela not in result:
                        result[tabela] = {'colunas': [], 'existe': True}
                    result[tabela]['colunas'].append({
                        'nome': linha['column_name'],
                        'tipo': linha['data_type']
                    })
                
                # Verificar dados de exemplo
                for tabela in ['historico_chuvas', 'historico_alagamentos', 'municipios']:
                    if tabela in result:
                        cursor.execute(f"SELECT * FROM {tabela} LIMIT 3;")
                        result[tabela]['exemplos'] = [dict(r) for r in cursor.fetchall()]
            
            conn.close()
            return jsonify(result)
            
        except Exception as e:
            app.logger.error(f"❌ Erro no debug tabelas: {e}")
            conn.close()
            return jsonify({'erro': str(e)}), 500
    
    @app.route('/admin/popular-dados-teste', methods=['POST'])
    def popular_dados_teste():
        """Popular banco com dados de teste"""
        conn = get_db_connection()
        if not conn:
            return jsonify({'erro': 'Erro de conexão'}), 500
        
        try:
            with conn.cursor() as cursor:
                # Inserir dados de teste - Municípios
                cursor.execute("""
                    INSERT INTO municipios (municipio, estado, latitude, longitude) 
                    VALUES 
                        ('Rio de Janeiro', 'RJ', -22.9068, -43.1729),
                        ('São Paulo', 'SP', -23.5505, -46.6333),
                        ('Angra dos Reis', 'RJ', -23.0067, -44.3182),
                        ('Campinas', 'SP', -22.9099, -47.0626),
                        ('Niterói', 'RJ', -22.8838, -43.1032)
                    ON CONFLICT DO NOTHING;
                """)
                
                # Inserir dados de teste - Chuvas
                cursor.execute("""
                    INSERT INTO historico_chuvas (municipio, estado, data, precipitacao, intensidade)
                    VALUES 
                        ('Rio de Janeiro', 'RJ', '2024-01-15', 25.5, 'Moderada'),
                        ('São Paulo', 'SP', '2024-01-16', 45.2, 'Forte'),
                        ('Angra dos Reis', 'RJ', '2024-01-17', 15.8, 'Fraca'),
                        ('Campinas', 'SP', '2024-01-18', 32.1, 'Moderada'),
                        ('Niterói', 'RJ', '2024-01-19', 8.4, 'Fraca')
                    ON CONFLICT DO NOTHING;
                """)
                
                # Inserir dados de teste - Alagamentos
                cursor.execute("""
                    INSERT INTO historico_alagamentos (municipio, estado, data, nivel, localizacao)
                    VALUES 
                        ('Rio de Janeiro', 'RJ', '2024-01-15', 'Médio', 'Centro'),
                        ('São Paulo', 'SP', '2024-01-16', 'Alto', 'Marginal'),
                        ('Angra dos Reis', 'RJ', '2024-01-17', 'Baixo', 'Porto'),
                        ('Campinas', 'SP', '2024-01-18', 'Médio', 'Centro'),
                        ('Niterói', 'RJ', '2024-01-19', 'Baixo', 'Centro')
                    ON CONFLICT DO NOTHING;
                """)
                
                conn.commit()
                
            conn.close()
            return jsonify({
                'status': 'sucesso',
                'mensagem': 'Dados de teste inseridos com sucesso',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            app.logger.error(f"❌ Erro ao popular dados: {e}")
            conn.close()
            return jsonify({'erro': str(e)}), 500
    
    @app.route('/debug/openweather', methods=['GET'])
    def debug_openweather():
        """Verificar configuração OpenWeather"""
        api_key = app.config['OPENWEATHER_API_KEY']
        
        if not api_key:
            return jsonify({
                'erro': 'OPENWEATHER_API_KEY não configurada',
                'configurada': False
            })
        
        # Testar uma requisição simples
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q=Rio de Janeiro,BR&appid={api_key}"
            response = requests.get(url, timeout=app.config['REQUEST_TIMEOUT'])
            
            return jsonify({
                'configurada': True,
                'chave_parcial': f"{api_key[:8]}...",
                'teste_api': response.status_code == 200,
                'resposta': response.json() if response.status_code == 200 else response.text,
                'timeout_usado': app.config['REQUEST_TIMEOUT'],
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'configurada': True,
                'chave_parcial': f"{api_key[:8]}...",
                'teste_api': False,
                'erro': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
    
    # Novos endpoints do sistema de configuração
    
    @app.route('/config/info')
    def config_info():
        """Informações de configuração (sem dados sensíveis)"""
        return jsonify({
            'application': {
                'name': 'Sistema de Previsão de Alagamentos RJ/SP',
                'version': '2.0.0',
                'debug': app.config['DEBUG']
            },
            'supported_locations': {
                'states': app.config['ESTADOS_SUPORTADOS'],
                'total_states': len(app.config['ESTADOS_SUPORTADOS']),
                'main_cities': {k: v for k, v in list(app.config['CIDADES_PRINCIPAIS'].items())[:3]},
                'total_cities': sum(len(cities) for cities in app.config['CIDADES_PRINCIPAIS'].values())
            },
            'weather_config': {
                'update_interval_minutes': app.config['WEATHER_UPDATE_INTERVAL'] // 60,
                'alert_temperature_range': {
                    'min_celsius': app.config['ALERT_TEMPERATURE_MIN'],
                    'max_celsius': app.config['ALERT_TEMPERATURE_MAX']
                },
                'alert_humidity_range': {
                    'min_percent': app.config['ALERT_HUMIDITY_MIN'],
                    'max_percent': app.config['ALERT_HUMIDITY_MAX']
                }
            },
            'cache_config': {
                'enabled': app.config['ENABLE_CACHE'],
                'ttl_minutes': app.config['CACHE_TTL'] // 60,
                'max_items': app.config['CACHE_SIZE']
            }
        })
    
    @app.route('/cache/stats')
    def cache_stats():
        """Estatísticas do cache"""
        global app_cache
        
        total_items = len(app_cache)
        cache_size_bytes = sum(len(str(v)) for v in app_cache.values()) if app_cache else 0
        
        return jsonify({
            'status': 'enabled' if app.config['ENABLE_CACHE'] else 'disabled',
            'statistics': {
                'total_items': total_items,
                'size_bytes': cache_size_bytes,
                'size_kb': round(cache_size_bytes / 1024, 2),
                'size_mb': round(cache_size_bytes / 1024 / 1024, 2)
            },
            'configuration': {
                'max_items': app.config['CACHE_SIZE'],
                'ttl_seconds': app.config['CACHE_TTL'],
                'ttl_minutes': app.config['CACHE_TTL'] // 60
            },
            'efficiency': {
                'utilization_percent': round((total_items / app.config['CACHE_SIZE']) * 100, 1) if app.config['CACHE_SIZE'] > 0 else 0
            }
        })
    
    @app.route('/cache/clear', methods=['POST'])
    def clear_cache():
        """Limpa o cache"""
        try:
            global app_cache
            cleared_items = len(app_cache)
            app_cache.clear()
            
            app.logger.info(f"Cache limpo manualmente. {cleared_items} itens removidos.")
            
            return jsonify({
                'status': 'success',
                'message': f'Cache limpo com sucesso.',
                'details': {
                    'items_removed': cleared_items,
                    'timestamp': datetime.utcnow().isoformat()
                }
            })
            
        except Exception as e:
            app.logger.error(f"Erro ao limpar cache: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Erro ao limpar o cache',
                'error': str(e)
            }), 500

def configure_error_handlers(app):
    """Configura handlers de erro personalizados"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint não encontrado',
            'message': 'A rota solicitada não existe',
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Erro interno: {error}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro inesperado',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Passa HTTPExceptions para o handler padrão
        if isinstance(e, HTTPException):
            return e
        
        app.logger.error(f"Erro não tratado: {e}", exc_info=True)
        return jsonify({
            'error': 'Erro interno',
            'message': 'Um erro inesperado ocorreu',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def configure_logging(app):
    """Configura sistema de logging melhorado"""
    
    # Configuração detalhada (mantém o formato atual)
    logging.basicConfig(
        level=logging.DEBUG if app.config['DEBUG'] else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if not app.debug:
        # Configuração para produção
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('THM API startup - version 2.0.0')

def configure_hooks(app):
    """Configura hooks de request/response"""
    
    @app.before_request
    def before_request():
        """Executado antes de cada request"""
        g.start_time = time.time()
        
        # Log da requisição (apenas em debug)
        if app.debug:
            app.logger.debug(f"Request: {request.method} {request.path}")
    
    @app.after_request
    def after_request(response):
        """Executado após cada request"""
        
        # Calcula tempo de resposta
        if hasattr(g, 'start_time'):
            response_time = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{response_time:.3f}s"
        
        # Headers de segurança
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response

def configure_scheduler(app):
    """Configura scheduler para tarefas automáticas"""
    
    def ingestao_automatica():
        """Função para ingestão automática de previsões"""
        with app.app_context():
            app.logger.info('[🔄] Iniciando ingestão automática de previsões...')
            try:
                from api.services.openweather_service import OpenWeatherService
                resultado = OpenWeatherService.atualizar_previsoes_todas_cidades()
                app.logger.info(f'✅ Ingestão automática concluída: {resultado}')
            except Exception as e:
                app.logger.error(f'❌ Erro na ingestão automática: {e}')
    
    # Configura scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(ingestao_automatica, 'cron', hour=4, minute=0)
    scheduler.start()
    
    # Registra shutdown do scheduler
    atexit.register(lambda: scheduler.shutdown())
    
    app.logger.info("📅 Scheduler configurado - ingestão automática às 04:00")

# Funções utilitárias (mantém as existentes e melhora)

def get_db_connection():
    """Conecta ao banco PostgreSQL usando novo sistema de configuração"""
    try:
        db_config = current_app.config['DB_CONFIG']
        current_app.logger.info(f"🔌 Conectando ao PostgreSQL: {db_config['host']}:{db_config['port']}")
        current_app.logger.info(f"📊 Database: {db_config['database']}")
        current_app.logger.info(f"👤 Usuário: {db_config['user']}")
        
        conn = psycopg2.connect(**db_config)
        current_app.logger.info("✅ Conexão PostgreSQL estabelecida!")
        return conn
    except psycopg2.OperationalError as e:
        current_app.logger.error(f"❌ Erro de conexão PostgreSQL: {e}")
        return None
    except Exception as e:
        current_app.logger.error(f"❌ Erro inesperado ao conectar: {e}")
        return None

def test_database():
    """Testa conexão e verifica tabelas"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Verificar versão
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            current_app.logger.info(f"🐘 PostgreSQL: {version['version'][:50]}...")
            
            # Listar tabelas
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            tables = cursor.fetchall()
            table_names = [t['table_name'] for t in tables]
            current_app.logger.info(f"📋 Tabelas encontradas: {table_names}")
            
            # Contar registros em cada tabela
            for table in tables:
                table_name = table['table_name']
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name};")
                    count = cursor.fetchone()['count']
                    current_app.logger.info(f"📊 {table_name}: {count} registros")
                except Exception as e:
                    current_app.logger.warning(f"⚠️ Erro ao contar {table_name}: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao testar banco: {e}")
        conn.close()
        return False

def test_openweather_api():
    """Testa conectividade com a API OpenWeather"""
    try:
        api_key = current_app.config['OPENWEATHER_API_KEY']
        if not api_key:
            return False
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Rio de Janeiro,BR&appid={api_key}"
        response = requests.get(url, timeout=current_app.config['REQUEST_TIMEOUT'])
        return response.status_code == 200
    except Exception:
        return False

def validate_configuration():
    """Valida configurações essenciais"""
    try:
        required_configs = [
            'SECRET_KEY',
            'DB_CONFIG',
            'OPENWEATHER_API_KEY',
            'ESTADOS_SUPORTADOS'
        ]
        
        missing_configs = []
        for config_key in required_configs:
            if not current_app.config.get(config_key):
                missing_configs.append(config_key)
        
        if missing_configs:
            current_app.logger.error(f"Configurações faltando: {missing_configs}")
            return False
        
        # Validações específicas
        if len(current_app.config['ESTADOS_SUPORTADOS']) == 0:
            current_app.logger.error("Nenhum estado configurado")
            return False
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Erro ao validar configurações: {e}")
        return False

# Decorador de cache
def cache_result(timeout=None):
    """
    Decorador para cache de resultados de funções
    
    Args:
        timeout: Tempo em segundos para expirar o cache
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_app.config['ENABLE_CACHE']:
                return f(*args, **kwargs)
            
            # Cria chave do cache
            cache_key = f"{f.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Verifica se está no cache
            global app_cache
            if cache_key in app_cache:
                cached_data, cached_time = app_cache[cache_key]
                cache_timeout = timeout or current_app.config['CACHE_TTL']
                
                if time.time() - cached_time < cache_timeout:
                    current_app.logger.debug(f"Cache hit: {cache_key}")
                    return cached_data
            
            # Executa função e armazena no cache
            result = f(*args, **kwargs)
            
            # Controla tamanho do cache
            if len(app_cache) >= current_app.config['CACHE_SIZE']:
                # Remove item mais antigo (FIFO simples)
                oldest_key = next(iter(app_cache))
                del app_cache[oldest_key]
            
            app_cache[cache_key] = (result, time.time())
            current_app.logger.debug(f"Cache miss: {cache_key}")
            
            return result
        return decorated_function
    return decorator

# Factory function principal
def create_application():
    """Função de conveniência para criar a aplicação"""
    return create_app()

# Para desenvolvimento local e compatibilidade
if __name__ == '__main__':
    # Cria aplicação usando Application Factory
    app = create_app()
    
    # Cria diretórios necessários
    os.makedirs('logs', exist_ok=True)
    
    # Configurações de startup
    port = app.config['PORT']
    debug = app.config['DEBUG']
    
    app.logger.info("🚀 Iniciando API do Sistema de Previsão de Alagamentos...")
    app.logger.info(f"🌐 Porta: {port}")
    app.logger.info(f"🔧 Debug: {debug}")
    app.logger.info(f"📦 Versão: 2.0.0")
    
    # Testar conexões na inicialização
    app.logger.info("🧪 Testando conexões...")
    
    # Testa banco
    with app.app_context():
        if test_database():
            app.logger.info("✅ PostgreSQL funcionando!")
        else:
            app.logger.warning("⚠️ PostgreSQL com problemas - usando fallbacks")
        
        # Testa API do tempo
        if test_openweather_api():
            app.logger.info("✅ OpenWeather API funcionando!")
        else:
            app.logger.warning("⚠️ OpenWeather API com problemas")
    
    app.logger.info(f"🚀 Servidor iniciando na porta {port}...")
    
    # Inicia aplicação
    app.run(
        debug=debug, 
        port=port, 
        host='0.0.0.0'
    )

# Alias para compatibilidade com deployment
application = create_application()
app = application