from flask import Blueprint, request, jsonify
from api.models.chuvas import ChuvasModel
from api.models.alagamentos import AlagamentosModel
import datetime

# Criar blueprint para rotas de histórico
historico_bp = Blueprint('historico', __name__)

@historico_bp.route('/chuvas', methods=['GET'])
def historico_chuvas():
    """
    Endpoint para obter histórico de chuvas
    
    Query params:
        cidade (str): Nome da cidade
        estado (str): Sigla do estado (RJ ou SP)
        dataInicio (str): Data inicial no formato YYYY-MM-DD
        dataFim (str): Data final no formato YYYY-MM-DD
    
    Returns:
        JSON com dados históricos de chuvas
    """
    # Obter parâmetros
    cidade = request.args.get('cidade')
    estado = request.args.get('estado')
    data_inicio = request.args.get('dataInicio')
    data_fim = request.args.get('dataFim')
    
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
    
    # Se datas não forem fornecidas, usar os últimos 30 dias
    hoje = datetime.date.today()
    
    if not data_inicio:
        data_inicio = (hoje - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    
    if not data_fim:
        data_fim = hoje.strftime('%Y-%m-%d')
    
    # Validar formato das datas
    try:
        datetime.datetime.strptime(data_inicio, '%Y-%m-%d')
        datetime.datetime.strptime(data_fim, '%Y-%m-%d')
    except ValueError:
        return jsonify({
            'erro': 'Formato de data inválido',
            'mensagem': 'As datas devem estar no formato YYYY-MM-DD'
        }), 400
    
    # Obter dados do modelo
    try:
        dados = ChuvasModel.get_historico_chuvas(cidade, estado, data_inicio, data_fim)
        return jsonify(dados)
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao obter histórico de chuvas',
            'mensagem': str(e)
        }), 500

@historico_bp.route('/alagamentos', methods=['GET'])
def historico_alagamentos():
    """
    Endpoint para obter histórico de alagamentos
    
    Query params:
        cidade (str): Nome da cidade
        estado (str): Sigla do estado (RJ ou SP)
        dataInicio (str): Data inicial no formato YYYY-MM-DD
        dataFim (str): Data final no formato YYYY-MM-DD
    
    Returns:
        JSON com dados históricos de alagamentos
    """
    # Obter parâmetros
    cidade = request.args.get('cidade')
    estado = request.args.get('estado')
    data_inicio = request.args.get('dataInicio')
    data_fim = request.args.get('dataFim')
    
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
    
    # Se datas não forem fornecidas, usar o último ano
    hoje = datetime.date.today()
    
    if not data_inicio:
        data_inicio = (hoje - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    
    if not data_fim:
        data_fim = hoje.strftime('%Y-%m-%d')
    
    # Validar formato das datas
    try:
        datetime.datetime.strptime(data_inicio, '%Y-%m-%d')
        datetime.datetime.strptime(data_fim, '%Y-%m-%d')
    except ValueError:
        return jsonify({
            'erro': 'Formato de data inválido',
            'mensagem': 'As datas devem estar no formato YYYY-MM-DD'
        }), 400
    
    # Obter dados do modelo
    try:
        dados = AlagamentosModel.get_historico_alagamentos(cidade, estado, data_inicio, data_fim)
        return jsonify(dados)
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao obter histórico de alagamentos',
            'mensagem': str(e)
        }), 500

@historico_bp.route('/pontos/alagamentos', methods=['GET'])
def pontos_alagamento():
    """
    Endpoint para obter pontos de alagamento
    
    Query params:
        cidade (str): Nome da cidade
        estado (str): Sigla do estado (RJ ou SP)
    
    Returns:
        JSON com pontos de alagamento
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
        dados = AlagamentosModel.get_pontos_alagamento(cidade, estado)
        return jsonify(dados)
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao obter pontos de alagamento',
            'mensagem': str(e)
        }), 500 