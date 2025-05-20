from flask import Flask, jsonify
from flask_cors import CORS
from api.routes.previsao import previsao_bp
from api.routes.historico import historico_bp
from api.config import PORT, DEBUG
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import pandas as pd

# Adicionar código para configurar o path do Python
import os
import sys
# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

# Registrar blueprints
app.register_blueprint(previsao_bp, url_prefix='/previsao')
app.register_blueprint(historico_bp, url_prefix='/historico')

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
            '/historico/alagamentos'
        ]
    }

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
        return {
            'status': 'erro',
            'mensagem': str(e)
        }, 500

# Função para ingestão automática
def ingestao_automatica():
    print('[LOG] Iniciando ingestão automática de previsões...')
    try:
        from api.services.openweather_service import OpenWeatherService
        resultado = OpenWeatherService.atualizar_previsoes_todas_cidades()
        print(f'[LOG] Ingestão automática concluída: {resultado}')
    except Exception as e:
        print(f'[LOG] Erro na ingestão automática: {e}')

# Agendar ingestão diária às 04:00
scheduler = BackgroundScheduler()
scheduler.add_job(ingestao_automatica, 'cron', hour=4, minute=0)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

@app.route('/municipios', methods=['GET'])
def listar_municipios():
    try:
        df = pd.read_csv('data/municipios_RJ_SP_coords.csv')
        municipios = [
            {'uf': row['uf'], 'nome': row['municipio']}
            for _, row in df.iterrows()
        ]
        return jsonify(municipios)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    print(f"Iniciando servidor na porta {PORT}...")
    app.run(debug=DEBUG, port=PORT, host='0.0.0.0') 