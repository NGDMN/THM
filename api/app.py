from flask import Flask
from flask_cors import CORS
from api.routes.previsao import previsao_bp
from api.routes.historico import historico_bp
from api.config import PORT, DEBUG

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

if __name__ == '__main__':
    print(f"Iniciando servidor na porta {PORT}...")
    app.run(debug=DEBUG, port=PORT, host='0.0.0.0') 