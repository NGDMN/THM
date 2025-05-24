from flask import Blueprint, request, jsonify
from ..controllers.historicoController import get_historico_chuvas, get_historico_alagamentos, get_pontos_alagamento
import logging
from datetime import datetime, timedelta

# Criar blueprint para rotas de histórico
historico_bp = Blueprint('historico', __name__)

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@historico_bp.route('/historico/chuvas', methods=['GET'])
def get_historico_chuvas_route():
    """Obter histórico de chuvas"""
    try:
        cidade = request.args.get('cidade', '').strip()
        estado = request.args.get('estado', '').strip()
        data_inicial = request.args.get('data_inicial')
        data_final = request.args.get('data_final')
        
        if not cidade or not estado:
            return jsonify({'error': 'Parâmetros cidade e estado são obrigatórios'}), 400
            
        # Se não foram fornecidas datas, usar últimos 30 dias
        if not data_inicial:
            data_inicial = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not data_final:
            data_final = datetime.now().strftime('%Y-%m-%d')
            
        dados = get_historico_chuvas(cidade, estado, data_inicial, data_final)
        
        return jsonify({
            'data': dados,
            'total': len(dados)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de chuvas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500

@historico_bp.route('/historico/alagamentos', methods=['GET'])
def get_historico_alagamentos_route():
    """Obter histórico de alagamentos"""
    try:
        cidade = request.args.get('cidade', '').strip()
        estado = request.args.get('estado', '').strip()
        data_inicial = request.args.get('data_inicial')
        data_final = request.args.get('data_final')
        
        if not cidade or not estado:
            return jsonify({'error': 'Parâmetros cidade e estado são obrigatórios'}), 400
            
        # Se não foram fornecidas datas, usar últimos 30 dias
        if not data_inicial:
            data_inicial = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not data_final:
            data_final = datetime.now().strftime('%Y-%m-%d')
            
        dados = get_historico_alagamentos(cidade, estado, data_inicial, data_final)
        
        return jsonify({
            'data': dados,
            'total': len(dados)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de alagamentos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500

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
    try:
        cidade = request.args.get('cidade', '').strip()
        estado = request.args.get('estado', '').strip()
        
        if not cidade or not estado:
            return jsonify({'error': 'Parâmetros cidade e estado são obrigatórios'}), 400
            
        dados = get_pontos_alagamento(cidade, estado)
        
        return jsonify({
            'data': dados,
            'total': len(dados)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar pontos de alagamento: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500 