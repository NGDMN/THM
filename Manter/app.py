from flask import Flask, jsonify
from flask_cors import CORS
from api.routes.previsao import previsao_bp
from api.routes.historico import historico_bp
from api.config import PORT, DEBUG
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adicionar código para configurar o path do Python
import sys
# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

# Configurações do banco PostgreSQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'dpg-d0l48cre5dus73c970sg-a.ohio-postgres.render.com'),
    'database': os.getenv('DB_NAME', 'thm_iy9l'),
    'user': os.getenv('DB_USER', 'thm_admin'),
    'password': os.getenv('DB_PASSWORD', 'fBfTMpHLfe2htlV9fe63mc0v9SmUTStS'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    """Conecta ao banco PostgreSQL com logs detalhados"""
    try:
        logger.info(f"🔌 Tentando conectar ao PostgreSQL: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        logger.info(f"📊 Database: {DB_CONFIG['database']}")
        logger.info(f"👤 Usuário: {DB_CONFIG['user']}")
        
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("✅ Conexão PostgreSQL estabelecida!")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"❌ Erro de conexão PostgreSQL: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao conectar: {e}")
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
            logger.info(f"🐘 PostgreSQL: {version['version'][:50]}...")
            
            # Listar tabelas
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            tables = cursor.fetchall()
            table_names = [t['table_name'] for t in tables]
            logger.info(f"📋 Tabelas encontradas: {table_names}")
            
            # Contar registros em cada tabela
            for table in tables:
                table_name = table['table_name']
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name};")
                    count = cursor.fetchone()['count']
                    logger.info(f"📊 {table_name}: {count} registros")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao contar {table_name}: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar banco: {e}")
        conn.close()
        return False

# Registrar blueprints
app.register_blueprint(previsao_bp)
app.register_blueprint(historico_bp)

# Adicionar rota básica para verificar se a API está funcionando
@app.route('/')
def index():
    return {
        'status': 'online',
        'mensagem': 'API do Sistema de Previsão de Alagamentos RJ/SP',
        'endpoints': [
            '/previsao/clima',
            '/previsao/chuvas',
            '/previsao/alagamentos',
            '/previsao/alertas',
            '/historico/chuvas',
            '/historico/alagamentos',
            '/test-db',
            '/municipios'
        ]
    }

# NOVO: Endpoint para testar conexão PostgreSQL
@app.route('/test-db', methods=['GET'])
def test_db_endpoint():
    """Endpoint para testar conexão com PostgreSQL"""
    logger.info("🧪 Testando conexão PostgreSQL via endpoint...")
    success = test_database()
    
    return jsonify({
        'success': success,
        'message': 'Conexão testada - verifique logs do servidor',
        'database_config': {
            'host': DB_CONFIG['host'],
            'database': DB_CONFIG['database'],
            'user': DB_CONFIG['user'],
            'port': DB_CONFIG['port']
        }
    })

# ATUALIZADO: Endpoint de municípios com fallback para PostgreSQL
@app.route('/municipios', methods=['GET'])
def listar_municipios():
    logger.info("🏙️ Buscando municípios...")
    
    try:
        # Tentar primeiro do CSV (atual)
        logger.info("📁 Tentando carregar do CSV...")
        df = pd.read_csv('data/municipios_RJ_SP_coords.csv')
        municipios = [
            {'uf': row['estado'], 'nome': row['municipio']}
            for _, row in df.iterrows()
        ]
        logger.info(f"✅ CSV carregado: {len(municipios)} municípios")
        return jsonify(municipios)
        
    except Exception as csv_error:
        logger.warning(f"⚠️ Erro ao carregar CSV: {csv_error}")
        logger.info("🐘 Tentando carregar do PostgreSQL...")
        
        # Fallback para PostgreSQL
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
                logger.info(f"✅ PostgreSQL carregado: {len(municipios)} municípios")
                
                conn.close()
                return jsonify(municipios)
                
        except Exception as db_error:
            logger.error(f"❌ Erro ao carregar do PostgreSQL: {db_error}")
            conn.close()
            return jsonify({'erro': f'Erro ao carregar municípios: {str(db_error)}'}), 500

# Endpoint temporário para forçar ingestão de previsões
@app.route('/admin/atualizar-previsoes', methods=['POST', 'GET'])
def admin_atualizar_previsoes():
    try:
        from api.services.openweather_service import OpenWeatherService
        resultado = OpenWeatherService.atualizar_previsoes_todas_cidades()
        return {
            'status': 'ok',
            'mensagem': 'Previsões atualizadas com sucesso!',
            'resultado': resultado
        }, 200
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar previsões: {e}")
        return {
            'status': 'erro',
            'mensagem': str(e)
        }, 500

# NOVO: Endpoint para verificar dados históricos
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
            'chuvas_por_municipio': chuvas_por_municipio,
            'ultimos_alagamentos': ultimos_alagamentos
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no debug histórico: {e}")
        conn.close()
        return jsonify({'erro': str(e)}), 500

# Função para ingestão automática
def ingestao_automatica():
    logger.info('[🔄] Iniciando ingestão automática de previsões...')
    try:
        from api.services.openweather_service import OpenWeatherService
        resultado = OpenWeatherService.atualizar_previsoes_todas_cidades()
        logger.info(f'✅ Ingestão automática concluída: {resultado}')
    except Exception as e:
        logger.error(f'❌ Erro na ingestão automática: {e}')

# Agendar ingestão diária às 04:00
scheduler = BackgroundScheduler()
scheduler.add_job(ingestao_automatica, 'cron', hour=4, minute=0)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

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
        logger.error(f"❌ Erro no debug tabelas: {e}")
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
                    ('Angra dos Reis', 'RJ', -23.0067, -44.3182)
                ON CONFLICT DO NOTHING;
            """)
            
            # Inserir dados de teste - Chuvas
            cursor.execute("""
                INSERT INTO historico_chuvas (municipio, estado, data, precipitacao, intensidade)
                VALUES 
                    ('Rio de Janeiro', 'RJ', '2024-01-15', 25.5, 'Moderada'),
                    ('São Paulo', 'SP', '2024-01-16', 45.2, 'Forte'),
                    ('Angra dos Reis', 'RJ', '2024-01-17', 15.8, 'Fraca')
                ON CONFLICT DO NOTHING;
            """)
            
            # Inserir dados de teste - Alagamentos
            cursor.execute("""
                INSERT INTO historico_alagamentos (municipio, estado, data, nivel, localizacao)
                VALUES 
                    ('Rio de Janeiro', 'RJ', '2024-01-15', 'Médio', 'Centro'),
                    ('São Paulo', 'SP', '2024-01-16', 'Alto', 'Marginal'),
                    ('Angra dos Reis', 'RJ', '2024-01-17', 'Baixo', 'Porto')
                ON CONFLICT DO NOTHING;
            """)
            
            conn.commit()
            
        conn.close()
        return jsonify({
            'status': 'sucesso',
            'mensagem': 'Dados de teste inseridos com sucesso'
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao popular dados: {e}")
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/debug/openweather', methods=['GET'])
def debug_openweather():
    """Verificar configuração OpenWeather"""
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    if not api_key:
        return jsonify({
            'erro': 'OPENWEATHER_API_KEY não configurada',
            'configurada': False
        })
    
    # Testar uma requisição simples
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Rio de Janeiro,BR&appid={api_key}"
        response = requests.get(url, timeout=10)
        
        return jsonify({
            'configurada': True,
            'chave_parcial': f"{api_key[:8]}...",
            'teste_api': response.status_code == 200,
            'resposta': response.json() if response.status_code == 200 else response.text
        })
        
    except Exception as e:
        return jsonify({
            'configurada': True,
            'chave_parcial': f"{api_key[:8]}...",
            'teste_api': False,
            'erro': str(e)
        })

if __name__ == '__main__':
    logger.info("🚀 Iniciando API do Sistema de Previsão de Alagamentos...")
    logger.info(f"🌐 Porta: {PORT}")
    logger.info(f"🔧 Debug: {DEBUG}")
    
    # Testar conexão PostgreSQL na inicialização
    logger.info("🧪 Testando conexão PostgreSQL...")
    if test_database():
        logger.info("✅ PostgreSQL funcionando!")
    else:
        logger.warning("⚠️ PostgreSQL com problemas - usando fallbacks")
    
    logger.info(f"🚀 Servidor iniciando na porta {PORT}...")
    app.run(debug=DEBUG, port=PORT, host='0.0.0.0')