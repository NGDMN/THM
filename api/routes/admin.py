from flask import Blueprint, jsonify
from ..services.openweather_service import OpenWeatherService
from ..services.previsao_service import PrevisaoService
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/atualizar-previsoes', methods=['POST'])
def atualizar_previsoes():
    """Endpoint para atualizar previsões de todas as cidades"""
    try:
        # Limpar previsões antigas
        registros_removidos = PrevisaoService.limpar_previsoes_antigas()
        logger.info(f"Removidos {registros_removidos} registros antigos")
        
        # Atualizar previsões para todas as cidades
        resultados = OpenWeatherService.atualizar_previsoes_todas_cidades(dias=5)
        
        return jsonify({
            'status': 'success',
            'message': 'Previsões atualizadas com sucesso',
            'registros_removidos': registros_removidos,
            'resultados': resultados
        })
        
    except Exception as e:
        logger.error(f"Erro ao atualizar previsões: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro ao atualizar previsões: {str(e)}'
        }), 500 