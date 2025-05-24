from flask import Blueprint, request, jsonify
from ..controllers.previsaoController import get_previsao_chuvas, get_previsao_alagamentos, get_alertas_atuais
import logging

# Criar blueprint para rotas de previsão
previsao_bp = Blueprint('previsao', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    try:
        # Obter parâmetros (opcionais)
        cidade = request.args.get('cidade', 'Rio de Janeiro')
        estado = request.args.get('estado', 'RJ')
        
        # Buscar alertas no banco
        alertas = get_alertas_atuais(cidade, estado)
        
        if alertas:
            return jsonify({
                'nivel': alertas[0]['nivel_risco'],
                'mensagem': alertas[0]['mensagem'],
                'data_atualizacao': alertas[0]['data'],
                'regioes_afetadas': alertas[0]['areas_afetadas']
            })
        
        # Se não encontrou alertas, retorna nível 0
        return jsonify({
            'nivel': 0,
            'mensagem': 'Sem alertas de alagamento ativos.',
            'data_atualizacao': None,
            'regioes_afetadas': []
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter alertas: {str(e)}")
        return jsonify({
            'erro': 'Erro ao obter dados de alerta',
            'mensagem': str(e)
        }), 500

@previsao_bp.route('/previsao/chuvas', methods=['GET'])
def get_previsao_chuvas_route():
    """Obter previsão de chuvas"""
    try:
        cidade = request.args.get('cidade', '').strip()
        estado = request.args.get('estado', '').strip()
        
        if not cidade or not estado:
            return jsonify({'error': 'Parâmetros cidade e estado são obrigatórios'}), 400
        
        dados = get_previsao_chuvas(cidade, estado)
        
        return jsonify({
            'data': dados,
            'total': len(dados)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar previsão de chuvas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500

@previsao_bp.route('/previsao/alagamentos', methods=['GET'])
def get_previsao_alagamentos_route():
    """Obter previsão de alagamentos"""
    try:
        cidade = request.args.get('cidade', '').strip()
        estado = request.args.get('estado', '').strip()
        
        if not cidade or not estado:
            return jsonify({'error': 'Parâmetros cidade e estado são obrigatórios'}), 400
        
        dados = get_previsao_alagamentos(cidade, estado)
        
        return jsonify({
            'data': dados,
            'total': len(dados)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar previsão de alagamentos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500 