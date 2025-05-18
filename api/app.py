from flask import Flask
from flask_cors import CORS
from .routes.previsao import previsao_bp
from .routes.historico import historico_bp

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

# Registrar blueprints
app.register_blueprint(previsao_bp, url_prefix='/api/previsao')
app.register_blueprint(historico_bp, url_prefix='/api/historico')

# Adicionar rota básica para verificar se a API está funcionando
@app.route('/')
def index():
    return {
        'status': 'online',
        'mensagem': 'API do Sistema de Previsão de Alagamentos RJ/SP',
        'endpoints': [
            '/api/previsao/chuvas',
            '/api/previsao/alagamentos',
            '/api/historico/chuvas',
            '/api/historico/alagamentos',
            '/api/pontos/alagamentos'
        ]
    }

if __name__ == '__main__':
    app.run(debug=True) 