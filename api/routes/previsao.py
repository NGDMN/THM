from flask import Blueprint, request, jsonify
from ..models.chuvas import ChuvasModel
from ..models.alagamentos import AlagamentosModel

# Criar blueprint para rotas de previsão
previsao_bp = Blueprint('previsao', __name__)

@previsao_bp.route('/alertas', methods=['GET'])
def alertas_atuais():
    """
    Endpoint para alertas de chuvas e alagamentos atuais
    
    Returns:
        JSON com dados de alertas
    """
    try:
        # Simplificado para teste - normalmente usaria dados reais do modelo
        return jsonify({
            'nivel': 1,
            'mensagem': 'Alerta de chuvas moderadas para as próximas 24h nas regiões sul e oeste.',
            'data_atualizacao': '2023-11-15T14:30:00',
            'regioes_afetadas': [
                'Zona Sul - RJ',
                'Zona Oeste - RJ'
            ]
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