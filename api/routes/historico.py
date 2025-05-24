from flask import Blueprint, request, jsonify
from ..models.chuvas import ChuvasModel
from ..models.alagamentos import AlagamentosModel
import datetime
from ..utils.db_utils import execute_query
import logging

# Criar blueprint para rotas de histórico
historico_bp = Blueprint('historico', __name__)

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@historico_bp.route('/historico/chuvas', methods=['GET'])
def get_historico_chuvas():
    """Obter histórico de chuvas com debug completo"""
    try:
        # 1. Capturar e logar todos os parâmetros recebidos
        cidade = request.args.get('cidade', '').strip()
        estado = request.args.get('estado', '').strip()
        data_inicial = request.args.get('dataInicial', '').strip()
        data_final = request.args.get('dataFinal', '').strip()
        
        logger.debug(f"=== HISTÓRICO CHUVAS DEBUG ===")
        logger.debug(f"Parâmetros recebidos:")
        logger.debug(f"  - cidade: '{cidade}' (len: {len(cidade)})")
        logger.debug(f"  - estado: '{estado}' (len: {len(estado)})")
        logger.debug(f"  - dataInicial: '{data_inicial}'")
        logger.debug(f"  - dataFinal: '{data_final}'")
        logger.debug(f"Headers: {dict(request.headers)}")
        logger.debug(f"Args completos: {dict(request.args)}")
        
        # 2. Validação rigorosa dos parâmetros
        if not cidade or not estado:
            logger.error(f"Parâmetros obrigatórios ausentes - cidade: '{cidade}', estado: '{estado}'")
            return jsonify({
                'error': 'Parâmetros cidade e estado são obrigatórios',
                'received': {
                    'cidade': cidade,
                    'estado': estado,
                    'dataInicial': data_inicial,
                    'dataFinal': data_final
                }
            }), 400
        
        # 3. Normalizar nomes de cidades (tratar acentos e case)
        cidade_normalizada = cidade.title().replace(' Dos ', ' dos ').replace(' De ', ' de ').replace(' Da ', ' da ')
        logger.debug(f"Cidade normalizada: '{cidade_normalizada}'")
        
        # 4. Construir query com diferentes variações para busca flexível
        base_query = """
        SELECT 
            data,
            municipio,
            estado,
            precipitacao,
            temperatura,
            umidade,
            created_at
        FROM historico_chuvas 
        WHERE 1=1
        """
        
        params = {}
        conditions = []
        
        # Busca flexível por cidade (múltiplas variações)
        city_variations = [
            cidade,
            cidade_normalizada,
            cidade.upper(),
            cidade.lower(),
            cidade.replace(' ', ''),
            cidade.replace('-', ' ')
        ]
        
        city_conditions = []
        for i, variation in enumerate(city_variations):
            param_name = f'cidade_{i}'
            city_conditions.append(f"LOWER(TRIM(municipio)) = LOWER(TRIM(%(cidade_{i})s))")
            params[param_name] = variation
        
        conditions.append(f"({' OR '.join(city_conditions)})")
        
        # Estado
        conditions.append("UPPER(TRIM(estado)) = UPPER(TRIM(%(estado)s))")
        params['estado'] = estado
        
        # Datas se fornecidas
        if data_inicial:
            conditions.append("data >= %(data_inicial)s")
            params['data_inicial'] = data_inicial
        
        if data_final:
            conditions.append("data <= %(data_final)s")
            params['data_final'] = data_final
        
        # Query final
        query = base_query + " AND " + " AND ".join(conditions) + " ORDER BY data DESC"
        
        logger.debug(f"Query construída: {query}")
        logger.debug(f"Parâmetros da query: {params}")
        
        # 5. Primeiro, verificar se existem dados para esta cidade (busca ampla)
        check_query = "SELECT DISTINCT municipio, estado, COUNT(*) as total FROM historico_chuvas WHERE LOWER(municipio) LIKE LOWER(%(cidade_like)s) GROUP BY municipio, estado"
        check_params = {'cidade_like': f'%{cidade}%'}
        
        logger.debug(f"Verificando cidades disponíveis: {check_query}")
        logger.debug(f"Parâmetros de verificação: {check_params}")
        
        check_result = execute_query(check_query, check_params)
        logger.debug(f"Cidades encontradas: {check_result.to_dict('records') if not check_result.empty else 'Nenhuma'}")
        
        # 6. Executar query principal
        result = execute_query(query, params)
        
        logger.debug(f"Resultados encontrados: {len(result)} registros")
        
        if result.empty:
            # 7. Diagnóstico adicional se não encontrar dados
            logger.warning("Nenhum resultado encontrado. Executando diagnósticos...")
            
            # Buscar todas as cidades no estado
            diagnostic_query = "SELECT DISTINCT municipio FROM historico_chuvas WHERE UPPER(estado) = UPPER(%(estado)s) ORDER BY municipio"
            diagnostic_result = execute_query(diagnostic_query, {'estado': estado})
            available_cities = diagnostic_result['municipio'].tolist() if not diagnostic_result.empty else []
            
            logger.debug(f"Cidades disponíveis no estado {estado}: {available_cities}")
            
            # Contar total de registros
            count_query = "SELECT COUNT(*) as total FROM historico_chuvas"
            count_result = execute_query(count_query)
            total_records = count_result.iloc[0]['total'] if not count_result.empty else 0
            
            logger.debug(f"Total de registros na tabela: {total_records}")
            
            return jsonify({
                'data': [],
                'debug_info': {
                    'parametros_recebidos': {
                        'cidade': cidade,
                        'estado': estado,
                        'data_inicial': data_inicial,
                        'data_final': data_final
                    },
                    'cidade_normalizada': cidade_normalizada,
                    'cidades_similares_encontradas': check_result.to_dict('records') if not check_result.empty else [],
                    'cidades_disponiveis_estado': available_cities,
                    'total_registros_tabela': total_records,
                    'query_executada': query,
                    'parametros_query': params
                }
            })
        
        # 8. Processar e retornar dados encontrados
        dados = result.to_dict('records')
        
        # Garantir que os dados estão no formato correto
        for item in dados:
            if 'data' in item and item['data']:
                item['data'] = str(item['data'])
            if 'precipitacao' in item and item['precipitacao'] is not None:
                item['precipitacao'] = float(item['precipitacao'])
            if 'temperatura' in item and item['temperatura'] is not None:
                item['temperatura'] = float(item['temperatura'])
            if 'umidade' in item and item['umidade'] is not None:
                item['umidade'] = int(item['umidade'])
        
        logger.debug(f"Dados processados: {len(dados)} registros")
        logger.debug(f"Exemplo de registro: {dados[0] if dados else 'Nenhum'}")
        
        return jsonify({
            'data': dados,
            'total': len(dados),
            'debug_info': {
                'parametros_utilizados': params,
                'query_executada': query
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de chuvas: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e),
            'debug_info': {
                'parametros_recebidos': {
                    'cidade': request.args.get('cidade', ''),
                    'estado': request.args.get('estado', ''),
                    'dataInicial': request.args.get('dataInicial', ''),
                    'dataFinal': request.args.get('dataFinal', '')
                }
            }
        }), 500

@historico_bp.route('/historico/alagamentos', methods=['GET'])
def get_historico_alagamentos():
    """Obter histórico de alagamentos com debug"""
    try:
        cidade = request.args.get('cidade', '').strip()
        estado = request.args.get('estado', '').strip()
        data_inicial = request.args.get('dataInicial', '').strip()
        data_final = request.args.get('dataFinal', '').strip()
        
        logger.debug(f"=== HISTÓRICO ALAGAMENTOS DEBUG ===")
        logger.debug(f"Parâmetros: cidade='{cidade}', estado='{estado}'")
        
        if not cidade or not estado:
            return jsonify({'error': 'Parâmetros cidade e estado são obrigatórios'}), 400
        
        query = """
        SELECT 
            data,
            municipio,
            estado,
            nivel_alagamento,
            areas_afetadas,
            numero_ocorrencias,
            created_at
        FROM historico_alagamentos 
        WHERE LOWER(TRIM(municipio)) = LOWER(TRIM(%(cidade)s))
        AND UPPER(TRIM(estado)) = UPPER(TRIM(%(estado)s))
        """
        
        params = {
            'cidade': cidade,
            'estado': estado
        }
        
        if data_inicial:
            query += " AND data >= %(data_inicial)s"
            params['data_inicial'] = data_inicial
        
        if data_final:
            query += " AND data <= %(data_final)s"
            params['data_final'] = data_final
        
        query += " ORDER BY data DESC"
        
        logger.debug(f"Query alagamentos: {query}")
        logger.debug(f"Parâmetros: {params}")
        
        result = execute_query(query, params)
        dados = result.to_dict('records')
        
        # Processar areas_afetadas se for string JSON
        for item in dados:
            if 'data' in item and item['data']:
                item['data'] = str(item['data'])
            if 'areas_afetadas' in item and isinstance(item['areas_afetadas'], str):
                try:
                    import json
                    item['areas_afetadas'] = json.loads(item['areas_afetadas'])
                except:
                    item['areas_afetadas'] = [item['areas_afetadas']]
        
        logger.debug(f"Alagamentos encontrados: {len(dados)}")
        
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