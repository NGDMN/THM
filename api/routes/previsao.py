from flask import Blueprint, request, jsonify
from ..models.chuvas import ChuvasModel
from ..models.alagamentos import AlagamentosModel
from ..services.openweather_service import OpenWeatherService
from ..services.previsao_service import PrevisaoService
import json
import psycopg2
from ..config import DB_CONFIG

# Criar blueprint para rotas de previsão
previsao_bp = Blueprint('previsao', __name__)

def get_db_connection():
    """Cria uma conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

@previsao_bp.route('/alertas', methods=['GET'])
def alertas_atuais():
    """
    Endpoint para alertas de chuvas e alagamentos atuais
    
    Query params:
        cidade (str, opcional): Nome da cidade
        estado (str, opcional): Sigla do estado (RJ ou SP)
    
    Returns:
        JSON com dados de alertas
    """
    # Obter parâmetros (opcionais)
    cidade = request.args.get('cidade', 'Rio de Janeiro')
    estado = request.args.get('estado', 'RJ')
    
    try:
        # Primeiro, verificar se existem alertas registrados no banco
        conn = get_db_connection()
        
        if conn:
            cursor = conn.cursor()
            # Buscar informações de alerta na tabela de configuração
            cursor.execute("SELECT valor FROM configuracao_sistema WHERE chave = 'ALERTA_ALAGAMENTOS'")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result and result[0]:
                # Converter dados JSON para lista de dicionários
                alertas = json.loads(result[0])
                
                # Filtrar apenas alertas da cidade/estado solicitados, se houver
                alertas_cidade = [alerta for alerta in alertas 
                                 if alerta.get('municipio').lower() == cidade.lower() 
                                 and alerta.get('estado') == estado]
                
                if alertas_cidade:
                    # Existe alerta específico para esta cidade
                    return jsonify({
                        'nivel': 2,  # Nível alto de alerta
                        'mensagem': f"Alerta de risco de alagamentos para {cidade}-{estado} nos próximos dias devido a chuvas intensas.",
                        'data_atualizacao': alertas_cidade[0].get('data'),
                        'regioes_afetadas': [f"{cidade} - {estado}"],
                        'precipitacao_prevista': [f"{alerta.get('precipitacao')}mm em {alerta.get('data')}" for alerta in alertas_cidade]
                    })
                elif alertas:
                    # Existem alertas para outras cidades
                    regioes = [f"{alerta.get('municipio')} - {alerta.get('estado')}" for alerta in alertas]
                    return jsonify({
                        'nivel': 1,  # Nível de atenção
                        'mensagem': "Alertas de risco de alagamentos em algumas regiões devido a chuvas intensas.",
                        'data_atualizacao': alertas[0].get('data'),
                        'regioes_afetadas': regioes
                    })
        
        # Se não encontrou alertas no banco ou sem conexão com banco, retorna dados simulados por região
        if estado == 'RJ':
            nivel = 0 
            mensagem = 'Sem alertas de alagamento ativos. Previsão de chuvas leves nos próximos dias.'
            regioes = []
        elif estado == 'SP':
            nivel = 0
            mensagem = 'Sem alertas de alagamento ativos. Tempo estável nos próximos dias.'
            regioes = []
        else:
            nivel = 0
            mensagem = 'Sem alertas ativos para a região.'
            regioes = []
            
        return jsonify({
            'nivel': nivel,
            'mensagem': mensagem,
            'data_atualizacao': '2023-11-15T14:30:00',
            'regioes_afetadas': regioes
        })
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao obter dados de alerta',
            'mensagem': str(e)
        }), 500

@previsao_bp.route('/chuvas', methods=['GET'])
def previsao_chuvas():
    """
    Endpoint para previsão de chuvas
    
    Query params:
        cidade (str): Nome da cidade
        estado (str): Sigla do estado (RJ ou SP)
    
    Returns:
        JSON com dados de previsão
    """
    # Obter parâmetros
    cidade = request.args.get('cidade')
    estado = request.args.get('estado')
    
    # Validar parâmetros
    if not cidade or not estado:
        return jsonify({
            'erro': 'Parâmetros inválidos',
            'mensagem': 'Os parâmetros cidade e estado são obrigatórios'
        }), 400
    
    # Validar estado (apenas RJ e SP)
    if estado not in ['RJ', 'SP']:
        return jsonify({
            'erro': 'Estado inválido',
            'mensagem': 'O estado deve ser RJ ou SP'
        }), 400
    
    # Obter dados do modelo
    try:
        dados = ChuvasModel.get_previsao_chuvas(cidade, estado)
        return jsonify(dados)
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao obter previsão',
            'mensagem': str(e)
        }), 500

@previsao_bp.route('/alagamentos', methods=['GET'])
def previsao_alagamentos():
    """
    Endpoint para previsão de risco de alagamentos
    
    Query params:
        cidade (str): Nome da cidade
        estado (str): Sigla do estado (RJ ou SP)
    
    Returns:
        JSON com dados de previsão de risco
    """
    # Obter parâmetros
    cidade = request.args.get('cidade')
    estado = request.args.get('estado')
    
    # Validar parâmetros
    if not cidade or not estado:
        return jsonify({
            'erro': 'Parâmetros inválidos',
            'mensagem': 'Os parâmetros cidade e estado são obrigatórios'
        }), 400
    
    # Validar estado (apenas RJ e SP)
    if estado not in ['RJ', 'SP']:
        return jsonify({
            'erro': 'Estado inválido',
            'mensagem': 'O estado deve ser RJ ou SP'
        }), 400
    
    # Obter dados do modelo
    try:
        dados = AlagamentosModel.get_previsao_alagamentos(cidade, estado)
        return jsonify(dados)
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao obter previsão de alagamentos',
            'mensagem': str(e)
        }), 500

@previsao_bp.route('/clima', methods=['GET'])
def previsao_clima():
    """
    Endpoint para previsão meteorológica usando OpenWeatherMap
    
    Query params:
        cidade (str): Nome da cidade
        estado (str): Sigla do estado (RJ ou SP)
        dias (int, opcional): Número de dias para previsão (máx 5)
    
    Returns:
        JSON com dados meteorológicos
    """
    # Obter parâmetros
    cidade = request.args.get('cidade')
    estado = request.args.get('estado')
    dias = request.args.get('dias', 5, type=int)
    
    # Validar parâmetros
    if not cidade or not estado:
        return jsonify({
            'erro': 'Parâmetros inválidos',
            'mensagem': 'Os parâmetros cidade e estado são obrigatórios'
        }), 400
    
    # Validar estado (apenas RJ e SP para a versão atual)
    if estado not in ['RJ', 'SP']:
        return jsonify({
            'erro': 'Estado inválido',
            'mensagem': 'O estado deve ser RJ ou SP'
        }), 400
    
    # Limitar o número de dias (API free do OpenWeatherMap permite até 5 dias)
    if dias > 5:
        dias = 5
    
    # Obter previsão do tempo
    try:
        previsoes = OpenWeatherService.get_weather_forecast(cidade, estado, dias)
        
        # Se não encontrou previsões, retornar erro
        if not previsoes:
            return jsonify({
                'erro': 'Dados não encontrados',
                'mensagem': f'Não foi possível obter previsões para {cidade}-{estado}'
            }), 404
        
        # Calcular impacto e risco de alagamentos para cada dia
        for previsao in previsoes:
            precipitacao = previsao.get('precipitacao', 0)
            impacto = PrevisaoService.calcular_impacto_precipitacao(
                cidade, estado, precipitacao
            )
            previsao['risco_alagamento'] = {
                'probabilidade': impacto['probabilidade_alagamento'],
                'nivel': impacto['nivel_risco'],
                'afetados_estimados': impacto['afetados_estimados']
            }
        
        return jsonify({
            'cidade': cidade,
            'estado': estado,
            'fonte': 'OpenWeatherMap',
            'previsoes': previsoes
        })
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao obter previsão meteorológica',
            'mensagem': str(e)
        }), 500 