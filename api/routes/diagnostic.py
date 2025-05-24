from flask import Blueprint, request, jsonify
from ..utils.db_utils import execute_query
import logging
import pandas as pd

diagnostic_bp = Blueprint('diagnostic', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@diagnostic_bp.route('/diagnostico/dados', methods=['GET'])
def diagnostico_dados():
    """Endpoint para diagnóstico completo dos dados"""
    try:
        diagnostico = {}
        # 1. Verificar conexão com banco
        try:
            test_query = "SELECT 1 as test"
            test_result = execute_query(test_query)
            diagnostico['conexao_banco'] = 'OK' if not test_result.empty else 'FALHA'
        except Exception as e:
            diagnostico['conexao_banco'] = f'ERRO: {str(e)}'
        # 2. Contar registros em cada tabela
        tabelas = ['historico_chuvas', 'historico_alagamentos', 'previsao_chuvas', 'previsao_alagamentos', 'municipios']
        for tabela in tabelas:
            try:
                count_query = f"SELECT COUNT(*) as total FROM {tabela}"
                count_result = execute_query(count_query)
                diagnostico[f'total_{tabela}'] = count_result.iloc[0]['total'] if not count_result.empty else 0
            except Exception as e:
                diagnostico[f'total_{tabela}'] = f'ERRO: {str(e)}'
        # 3. Listar cidades disponíveis por estado
        try:
            cities_query = """
            SELECT estado, municipio, COUNT(*) as registros
            FROM historico_chuvas 
            GROUP BY estado, municipio 
            ORDER BY estado, municipio
            """
            cities_result = execute_query(cities_query)
            diagnostico['cidades_com_dados'] = cities_result.to_dict('records') if not cities_result.empty else []
        except Exception as e:
            diagnostico['cidades_com_dados'] = f'ERRO: {str(e)}'
        # 4. Verificar dados específicos para Angra dos Reis
        try:
            angra_query = """
            SELECT 'historico_chuvas' as tabela, COUNT(*) as total
            FROM historico_chuvas 
            WHERE LOWER(municipio) LIKE '%angra%'
            UNION ALL
            SELECT 'previsao_chuvas' as tabela, COUNT(*) as total
            FROM previsao_chuvas 
            WHERE LOWER(municipio) LIKE '%angra%'
            """
            angra_result = execute_query(angra_query)
            diagnostico['dados_angra_dos_reis'] = angra_result.to_dict('records') if not angra_result.empty else []
        except Exception as e:
            diagnostico['dados_angra_dos_reis'] = f'ERRO: {str(e)}'
        # 5. Verificar estrutura das tabelas
        try:
            structure_queries = {
                'historico_chuvas': "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'historico_chuvas'",
                'previsao_chuvas': "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'previsao_chuvas'"
            }
            for tabela, query in structure_queries.items():
                try:
                    struct_result = execute_query(query)
                    diagnostico[f'estrutura_{tabela}'] = struct_result.to_dict('records') if not struct_result.empty else []
                except Exception as e:
                    diagnostico[f'estrutura_{tabela}'] = f'ERRO: {str(e)}'
        except Exception as e:
            diagnostico['estrutura_tabelas'] = f'ERRO: {str(e)}'
        return jsonify({
            'status': 'success',
            'diagnostico': diagnostico,
            'timestamp': str(pd.Timestamp.now())
        })
    except Exception as e:
        logger.error(f"Erro no diagnóstico: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': str(pd.Timestamp.now())
        }), 500 