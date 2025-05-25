# routes/previsao.py - Rotas de Previsão Refatoradas
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, g
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
import time

# Imports dos services (com fallback para compatibilidade)
try:
    from ..services.openweather_service import OpenWeatherService
except ImportError:
    from api.services.openweather_service import OpenWeatherService

try:
    from ..services.previsao_service import PrevisaoService
except ImportError:
    # Fallback se o service não existir ainda
    class PrevisaoService:
        @staticmethod
        def calcular_impacto_precipitacao(cidade, estado, precipitacao):
            return {
                'probabilidade_alagamento': min(int(precipitacao * 2), 100),
                'nivel_risco': 'baixo' if precipitacao < 20 else 'médio' if precipitacao < 50 else 'alto',
                'afetados_estimados': int(precipitacao * 100)
            }

# Criar blueprint
previsao_bp = Blueprint('previsao', __name__)

# Cache específico para previsões
previsao_cache = {}

def cache_previsao(timeout=1800):  # 30 minutos por padrão
    """Decorador de cache específico para previsões"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_app.config.get('ENABLE_CACHE', True):
                return f(*args, **kwargs)
            
            # Criar chave do cache baseada nos parâmetros da requisição
            cache_key = f"{f.__name__}:{request.endpoint}:{hash(str(request.args))}"
            
            # Verificar cache
            global previsao_cache
            if cache_key in previsao_cache:
                cached_data, cached_time = previsao_cache[cache_key]
                if time.time() - cached_time < timeout:
                    current_app.logger.debug(f"Cache hit: {cache_key}")
                    cached_data['_cached'] = True
                    cached_data['_cache_time'] = cached_time
                    return jsonify(cached_data)
            
            # Executar função
            result = f(*args, **kwargs)
            
            # Armazenar no cache apenas se for sucesso
            if hasattr(result, 'status_code') and result.status_code == 200:
                result_data = result.get_json()
                
                # Controlar tamanho do cache
                if len(previsao_cache) >= current_app.config.get('CACHE_SIZE', 1000):
                    oldest_key = next(iter(previsao_cache))
                    del previsao_cache[oldest_key]
                
                previsao_cache[cache_key] = (result_data, time.time())
                current_app.logger.debug(f"Cache stored: {cache_key}")
            
            return result
        return decorated_function
    return decorator

def validate_location_params():
    """Decorador para validar parâmetros de localização"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cidade = request.args.get('cidade', '').strip()
            estado = request.args.get('estado', '').strip()
            
            # Validações básicas
            if not cidade or not estado:
                return jsonify({
                    'error': 'Parâmetros obrigatórios',
                    'message': 'Os parâmetros cidade e estado são obrigatórios',
                    'required_params': ['cidade', 'estado'],
                    'timestamp': datetime.utcnow().isoformat()
                }), 400
            
            # Validar estado (expandido para todos os estados suportados)
            estados_suportados = current_app.config.get('ESTADOS_SUPORTADOS', ['RJ', 'SP'])
            if estado.upper() not in estados_suportados:
                return jsonify({
                    'error': 'Estado não suportado',
                    'message': f'O estado {estado} não está na lista de estados suportados',
                    'supported_states': estados_suportados,
                    'timestamp': datetime.utcnow().isoformat()
                }), 400
            
            # Armazenar parâmetros validados no contexto da requisição
            g.cidade = cidade.title()  # Padroniza capitalização
            g.estado = estado.upper()  # Padroniza para maiúsculo
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_db_connection():
    """Conecta ao banco usando configurações centralizadas"""
    try:
        db_config = current_app.config['DB_CONFIG']
        conn = psycopg2.connect(
            dbname=db_config['database'],
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port'],
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        current_app.logger.error(f"Erro ao conectar ao banco: {e}")
        return None

def execute_query(query, params=None):
    """Executa query com tratamento de erro melhorado"""
    conn = get_db_connection()
    if not conn:
        raise Exception("Não foi possível conectar ao banco de dados")
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or {})
            result = cursor.fetchall()
            
            # Converter para lista de dicionários
            return [dict(row) for row in result]
            
    except Exception as e:
        current_app.logger.error(f"Erro na query: {e}")
        raise
    finally:
        conn.close()

@previsao_bp.route('/alertas', methods=['GET'])
@validate_location_params()
@cache_previsao(timeout=600)  # Cache de 10 minutos para alertas
def alertas_atuais():
    """
    Endpoint para alertas de chuvas e alagamentos atuais
    
    Query params:
        cidade (str): Nome da cidade
        estado (str): Sigla do estado
    
    Returns:
        JSON com dados de alertas atuais
    """
    try:
        cidade = g.cidade
        estado = g.estado
        
        current_app.logger.info(f"🚨 Buscando alertas para {cidade}-{estado}")
        
        # Buscar alertas no banco de dados
        conn = get_db_connection()
        
        if conn:
            try:
                with conn.cursor() as cursor:
                    # Buscar alertas ativos para a região
                    cursor.execute("""
                        SELECT 
                            nivel_risco,
                            mensagem,
                            data_inicio,
                            data_fim,
                            areas_afetadas,
                            precipitacao_prevista,
                            created_at
                        FROM alertas_alagamentos 
                        WHERE LOWER(TRIM(municipio)) = LOWER(TRIM(%s))
                        AND UPPER(TRIM(estado)) = UPPER(TRIM(%s))
                        AND data_fim >= CURRENT_TIMESTAMP
                        AND ativo = true
                        ORDER BY nivel_risco DESC, created_at DESC
                        LIMIT 5
                    """, (cidade, estado))
                    
                    alertas = cursor.fetchall()
                    
                    if alertas:
                        alerta_principal = alertas[0]
                        return jsonify({
                            'status': 'alert',
                            'nivel': alerta_principal['nivel_risco'],
                            'mensagem': alerta_principal['mensagem'],
                            'data_inicio': alerta_principal['data_inicio'].isoformat() if alerta_principal['data_inicio'] else None,
                            'data_fim': alerta_principal['data_fim'].isoformat() if alerta_principal['data_fim'] else None,
                            'regioes_afetadas': json.loads(alerta_principal['areas_afetadas']) if alerta_principal['areas_afetadas'] else [f"{cidade}-{estado}"],
                            'precipitacao_prevista': alerta_principal['precipitacao_prevista'],
                            'total_alertas': len(alertas),
                            'timestamp': datetime.utcnow().isoformat()
                        })
                
                conn.close()
                
            except Exception as e:
                current_app.logger.error(f"Erro ao buscar alertas no banco: {e}")
                conn.close()
        
        # Buscar alertas baseados em previsões meteorológicas atuais
        try:
            # Obter dados meteorológicos atuais
            weather_data = OpenWeatherService.get_current_weather(cidade, estado)
            
            if weather_data:
                precipitacao = weather_data.get('precipitacao', 0)
                temperatura = weather_data.get('temperatura', 25)
                umidade = weather_data.get('umidade', 50)
                
                # Calcular nível de risco baseado nos dados meteorológicos
                nivel_risco = 0
                mensagem = "Sem alertas de alagamento ativos."
                
                # Lógica de determinação de alertas
                if precipitacao > current_app.config.get('ALERT_PRECIPITATION_HIGH', 50):
                    nivel_risco = 3
                    mensagem = f"ALERTA ALTO: Chuvas intensas previstas ({precipitacao}mm). Risco elevado de alagamentos."
                elif precipitacao > current_app.config.get('ALERT_PRECIPITATION_MEDIUM', 25):
                    nivel_risco = 2
                    mensagem = f"ALERTA MÉDIO: Chuvas moderadas previstas ({precipitacao}mm). Possibilidade de alagamentos."
                elif precipitacao > current_app.config.get('ALERT_PRECIPITATION_LOW', 10):
                    nivel_risco = 1
                    mensagem = f"ATENÇÃO: Chuvas leves previstas ({precipitacao}mm). Acompanhe as condições."
                
                # Ajustar nível baseado em outros fatores
                if umidade > current_app.config.get('ALERT_HUMIDITY_MAX', 90):
                    nivel_risco = min(nivel_risco + 1, 3)
                    mensagem += f" Umidade alta ({umidade}%)."
                
                return jsonify({
                    'status': 'calculated',
                    'nivel': nivel_risco,
                    'mensagem': mensagem,
                    'data_atualizacao': datetime.utcnow().isoformat(),
                    'regioes_afetadas': [f"{cidade}-{estado}"],
                    'condicoes_atuais': {
                        'precipitacao': precipitacao,
                        'temperatura': temperatura,
                        'umidade': umidade
                    },
                    'fonte': 'OpenWeatherMap',
                    'timestamp': datetime.utcnow().isoformat()
                })
                
        except Exception as e:
            current_app.logger.warning(f"Erro ao obter dados meteorológicos: {e}")
        
        # Fallback - sem alertas ativos
        return jsonify({
            'status': 'normal',
            'nivel': 0,
            'mensagem': 'Sem alertas de alagamento ativos. Condições meteorológicas estáveis.',
            'data_atualizacao': datetime.utcnow().isoformat(),
            'regioes_afetadas': [],
            'fonte': 'Sistema local',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter alertas: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Não foi possível obter dados de alertas',
            'details': str(e) if current_app.debug else 'Erro interno',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@previsao_bp.route('/previsao/chuvas', methods=['GET'])
@validate_location_params()
@cache_previsao(timeout=3600)  # Cache de 1 hora para previsões
def get_previsao_chuvas():
    """
    Obter previsão de chuvas para os próximos dias
    
    Query params:
        cidade (str): Nome da cidade
        estado (str): Sigla do estado
        dias (int, opcional): Número de dias (padrão: 7, máximo: 14)
    
    Returns:
        JSON com previsões de chuva
    """
    try:
        cidade = g.cidade
        estado = g.estado
        dias = min(request.args.get('dias', 7, type=int), 14)  # Máximo 14 dias
        
        current_app.logger.info(f"🌧️ Buscando previsão de chuvas: {cidade}-{estado} ({dias} dias)")
        
        # Buscar previsões no banco de dados
        query = """
        SELECT 
            data,
            municipio,
            estado,
            precipitacao_prevista as precipitacao,
            temperatura_prevista as temperatura,
            umidade_prevista as umidade,
            probabilidade_chuva,
            intensidade_chuva,
            velocidade_vento,
            direcao_vento,
            pressao_atmosferica,
            visibilidade,
            condicao_tempo,
            created_at,
            updated_at
        FROM previsao_chuvas 
        WHERE LOWER(TRIM(municipio)) = LOWER(TRIM(%(cidade)s))
        AND UPPER(TRIM(estado)) = UPPER(TRIM(%(estado)s))
        AND data >= CURRENT_DATE
        AND data <= CURRENT_DATE + INTERVAL '%(dias)s days'
        ORDER BY data ASC
        """
        
        params = {
            'cidade': cidade,
            'estado': estado,
            'dias': dias
        }
        
        try:
            dados = execute_query(query, params)
            
            # Processar e enriquecer dados
            for item in dados:
                # Converter datas para string
                if 'data' in item and item['data']:
                    item['data'] = item['data'].strftime('%Y-%m-%d') if hasattr(item['data'], 'strftime') else str(item['data'])
                
                # Garantir tipos corretos
                for campo_numerico in ['precipitacao', 'temperatura', 'umidade', 'probabilidade_chuva', 'velocidade_vento', 'pressao_atmosferica', 'visibilidade']:
                    if campo_numerico in item and item[campo_numerico] is not None:
                        try:
                            item[campo_numerico] = float(item[campo_numerico])
                        except (ValueError, TypeError):
                            item[campo_numerico] = 0.0
                
                # Adicionar classificação de intensidade
                precipitacao = item.get('precipitacao', 0)
                if precipitacao < 2.5:
                    item['classificacao_chuva'] = 'Sem chuva'
                elif precipitacao < 10:
                    item['classificacao_chuva'] = 'Chuva fraca'
                elif precipitacao < 50:
                    item['classificacao_chuva'] = 'Chuva moderada'
                elif precipitacao < 100:
                    item['classificacao_chuva'] = 'Chuva forte'
                else:
                    item['classificacao_chuva'] = 'Chuva muito forte'
                
                # Adicionar timestamp de processamento
                item['processed_at'] = datetime.utcnow().isoformat()
            
            if dados:
                current_app.logger.info(f"✅ Encontradas {len(dados)} previsões no banco")
                
                # Estatísticas resumidas
                total_precipitacao = sum(item.get('precipitacao', 0) for item in dados)
                precipitacao_media = total_precipitacao / len(dados) if dados else 0
                
                return jsonify({
                    'status': 'success',
                    'fonte': 'banco_de_dados',
                    'cidade': cidade,
                    'estado': estado,
                    'periodo': {
                        'inicio': dados[0]['data'],
                        'fim': dados[-1]['data'],
                        'total_dias': len(dados)
                    },
                    'resumo': {
                        'total_precipitacao_mm': round(total_precipitacao, 2),
                        'precipitacao_media_mm': round(precipitacao_media, 2),
                        'dias_com_chuva': len([d for d in dados if d.get('precipitacao', 0) > 0])
                    },
                    'previsoes': dados,
                    'total': len(dados),
                    'timestamp': datetime.utcnow().isoformat()
                })
                
        except Exception as db_error:
            current_app.logger.warning(f"Erro ao buscar no banco: {db_error}")
        
        # Fallback: buscar dados da API OpenWeather
        current_app.logger.info("🌐 Buscando dados da API OpenWeather...")
        
        try:
            previsoes_api = OpenWeatherService.get_weather_forecast(cidade, estado, dias)
            
            if previsoes_api:
                current_app.logger.info(f"✅ Obtidas {len(previsoes_api)} previsões da API")
                
                return jsonify({
                    'status': 'success',
                    'fonte': 'openweather_api',
                    'cidade': cidade,
                    'estado': estado,
                    'previsoes': previsoes_api,
                    'total': len(previsoes_api),
                    'timestamp': datetime.utcnow().isoformat(),
                    'nota': 'Dados obtidos diretamente da API OpenWeather'
                })
            
        except Exception as api_error:
            current_app.logger.error(f"Erro na API OpenWeather: {api_error}")
        
        # Se chegou até aqui, não encontrou dados
        current_app.logger.warning(f"Nenhuma previsão encontrada para {cidade}-{estado}")
        
        # Verificar cidades disponíveis para sugestões
        try:
            check_query = """
                SELECT DISTINCT municipio, estado, COUNT(*) as total_previsoes
                FROM previsao_chuvas 
                WHERE UPPER(estado) = UPPER(%(estado)s)
                AND data >= CURRENT_DATE
                GROUP BY municipio, estado
                ORDER BY total_previsoes DESC
                LIMIT 10
            """
            cidades_disponiveis = execute_query(check_query, {'estado': estado})
            
        except Exception:
            cidades_disponiveis = []
        
        return jsonify({
            'status': 'not_found',
            'message': f'Nenhuma previsão encontrada para {cidade}-{estado}',
            'cidade_buscada': cidade,
            'estado_buscado': estado,
            'sugestoes': {
                'cidades_disponiveis': cidades_disponiveis[:5],
                'total_cidades_com_dados': len(cidades_disponiveis)
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 404
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar previsão de chuvas: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Não foi possível obter previsões de chuva',
            'details': str(e) if current_app.debug else 'Erro interno',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@previsao_bp.route('/previsao/alagamentos', methods=['GET'])
@validate_location_params()
@cache_previsao(timeout=3600)  # Cache de 1 hora
def get_previsao_alagamentos():
    """
    Obter previsão de alagamentos baseada em dados meteorológicos
    
    Query params:
        cidade (str): Nome da cidade
        estado (str): Sigla do estado
        dias (int, opcional): Número de dias (padrão: 7)
    
    Returns:
        JSON com previsões de alagamento
    """
    try:
        cidade = g.cidade
        estado = g.estado
        dias = min(request.args.get('dias', 7, type=int), 14)
        
        current_app.logger.info(f"🌊 Buscando previsão de alagamentos: {cidade}-{estado}")
        
        # Buscar previsões de alagamento no banco
        query = """
        SELECT 
            data,
            municipio,
            estado,
            nivel_risco,
            probabilidade,
            recomendacoes,
            areas_risco,
            precipitacao_acumulada,
            fatores_risco,
            populacao_afetada_estimada,
            created_at,
            updated_at
        FROM previsao_alagamentos 
        WHERE LOWER(TRIM(municipio)) = LOWER(TRIM(%(cidade)s))
        AND UPPER(TRIM(estado)) = UPPER(TRIM(%(estado)s))
        AND data >= CURRENT_DATE
        AND data <= CURRENT_DATE + INTERVAL '%(dias)s days'
        ORDER BY data ASC
        """
        
        params = {'cidade': cidade, 'estado': estado, 'dias': dias}
        
        try:
            dados = execute_query(query, params)
            
            # Processar dados JSON
            for item in dados:
                # Converter data
                if 'data' in item and item['data']:
                    item['data'] = item['data'].strftime('%Y-%m-%d') if hasattr(item['data'], 'strftime') else str(item['data'])
                
                # Processar campos JSON
                for campo_json in ['recomendacoes', 'areas_risco', 'fatores_risco']:
                    if campo_json in item and isinstance(item[campo_json], str):
                        try:
                            item[campo_json] = json.loads(item[campo_json])
                        except (json.JSONDecodeError, TypeError):
                            item[campo_json] = []
                
                # Garantir tipos numéricos
                for campo_numerico in ['probabilidade', 'precipitacao_acumulada', 'populacao_afetada_estimada']:
                    if campo_numerico in item and item[campo_numerico] is not None:
                        try:
                            item[campo_numerico] = float(item[campo_numerico])
                        except (ValueError, TypeError):
                            item[campo_numerico] = 0.0
                
                # Adicionar classificação de risco
                probabilidade = item.get('probabilidade', 0)
                if probabilidade < 20:
                    item['classificacao_risco'] = 'Muito baixo'
                elif probabilidade < 40:
                    item['classificacao_risco'] = 'Baixo'
                elif probabilidade < 60:
                    item['classificacao_risco'] = 'Moderado'
                elif probabilidade < 80:
                    item['classificacao_risco'] = 'Alto'
                else:
                    item['classificacao_risco'] = 'Muito alto'
            
            if dados:
                current_app.logger.info(f"✅ Encontradas {len(dados)} previsões de alagamento")
                
                # Calcular estatísticas
                probabilidade_maxima = max((item.get('probabilidade', 0) for item in dados), default=0)
                nivel_risco_max = max((item.get('nivel_risco', 'baixo') for item in dados), default='baixo', 
                                    key=lambda x: {'baixo': 1, 'médio': 2, 'alto': 3}.get(x, 0))
                
                return jsonify({
                    'status': 'success',
                    'fonte': 'banco_de_dados',
                    'cidade': cidade,
                    'estado': estado,
                    'periodo': {
                        'inicio': dados[0]['data'],
                        'fim': dados[-1]['data'],
                        'total_dias': len(dados)
                    },
                    'resumo': {
                        'probabilidade_maxima': probabilidade_maxima,
                        'nivel_risco_maximo': nivel_risco_max,
                        'dias_com_risco': len([d for d in dados if d.get('probabilidade', 0) > 20])
                    },
                    'previsoes': dados,
                    'total': len(dados),
                    'timestamp': datetime.utcnow().isoformat()
                })
                
        except Exception as db_error:
            current_app.logger.warning(f"Erro ao buscar previsões de alagamento: {db_error}")
        
        # Fallback: calcular baseado em previsões de chuva
        current_app.logger.info("🔄 Calculando risco baseado em previsões de chuva...")
        
        try:
            # Buscar previsões de chuva para calcular risco
            chuva_query = """
            SELECT data, precipitacao_prevista
            FROM previsao_chuvas 
            WHERE LOWER(TRIM(municipio)) = LOWER(TRIM(%(cidade)s))
            AND UPPER(TRIM(estado)) = UPPER(TRIM(%(estado)s))
            AND data >= CURRENT_DATE
            AND data <= CURRENT_DATE + INTERVAL '%(dias)s days'
            ORDER BY data ASC
            """
            
            previsoes_chuva = execute_query(chuva_query, params)
            
            if previsoes_chuva:
                previsoes_alagamento = []
                
                for previsao in previsoes_chuva:
                    precipitacao = previsao.get('precipitacao_prevista', 0) or 0
                    
                    # Calcular risco baseado na precipitação
                    impacto = PrevisaoService.calcular_impacto_precipitacao(cidade, estado, precipitacao)
                    
                    previsoes_alagamento.append({
                        'data': previsao['data'].strftime('%Y-%m-%d') if hasattr(previsao['data'], 'strftime') else str(previsao['data']),
                        'municipio': cidade,
                        'estado': estado,
                        'nivel_risco': impacto['nivel_risco'],
                        'probabilidade': impacto['probabilidade_alagamento'],
                        'precipitacao_base': precipitacao,
                        'populacao_afetada_estimada': impacto['afetados_estimados'],
                        'fonte_calculo': 'previsao_chuva',
                        'recomendacoes': [
                            "Monitore as condições meteorológicas",
                            "Evite áreas propensas a alagamento" if impacto['probabilidade_alagamento'] > 50 else "Mantenha atenção às condições"
                        ],
                        'areas_risco': ['Centro', 'Zona baixa'] if impacto['probabilidade_alagamento'] > 30 else []
                    })
                
                return jsonify({
                    'status': 'calculated',
                    'fonte': 'calculo_precipitacao',
                    'cidade': cidade,
                    'estado': estado,
                    'previsoes': previsoes_alagamento,
                    'total': len(previsoes_alagamento),
                    'timestamp': datetime.utcnow().isoformat(),
                    'nota': 'Risco calculado baseado em previsões de precipitação'
                })
                
        except Exception as calc_error:
            current_app.logger.error(f"Erro ao calcular risco: {calc_error}")
        
        # Último fallback - resposta vazia
        return jsonify({
            'status': 'not_found',
            'message': f'Nenhuma previsão de alagamento encontrada para {cidade}-{estado}',
            'cidade': cidade,
            'estado': estado,
            'previsoes': [],
            'total': 0,
            'timestamp': datetime.utcnow().isoformat()
        }), 404
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar previsão de alagamentos: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Não foi possível obter previsões de alagamento',
            'details': str(e) if current_app.debug else 'Erro interno',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@previsao_bp.route('/clima', methods=['GET'])
@validate_location_params()
@cache_previsao(timeout=1800)  # Cache de 30 minutos
def previsao_clima():
    """
    Endpoint para previsão meteorológica completa usando OpenWeatherMap
    
    Query params:
        cidade (str): Nome da cidade
        estado (str): Sigla do estado
        dias (int, opcional): Número de dias para previsão (máx 5 para API gratuita)
    
    Returns:
        JSON com dados meteorológicos completos
    """
    try:
        cidade = g.cidade
        estado = g.estado
        dias = min(request.args.get('dias', 5, type=int), 5)  # API gratuita permite até 5 dias
        
        current_app.logger.info(f"🌤️ Buscando previsão meteorológica: {cidade}-{estado} ({dias} dias)")
        
        # Obter previsão do tempo da API
        previsoes = OpenWeatherService.get_weather_forecast(cidade, estado, dias)
        
        # Calcular impacto e risco de alagamentos para cada dia
        previsoes_enriquecidas = []
        
        for previsao in previsoes:
            precipitacao = previsao.get('precipitacao', 0)
            
            # Calcular impacto usando o service
            impacto = PrevisaoService.calcular_impacto_precipitacao(cidade, estado, precipitacao)
            
            # Enriquecer dados da previsão
            previsao_enriquecida = {
                **previsao,
                'risco_alagamento': {
                    'probabilidade': impacto['probabilidade_alagamento'],
                    'nivel': impacto['nivel_risco'],
                    'afetados_estimados': impacto['afetados_estimados'],
                    'classificacao': 'Muito baixo' if impacto['probabilidade_alagamento'] < 20 else
                                   'Baixo' if impacto['probabilidade_alagamento'] < 40 else
                                   'Moderado' if impacto['probabilidade_alagamento'] < 60 else
                                   'Alto' if impacto['probabilidade_alagamento'] < 80 else 'Muito alto'
                },
                'alertas': {
                    'temperatura': 'alta' if previsao.get('temperatura', 25) > current_app.config.get('ALERT_TEMPERATURE_MAX', 40) else
                                  'baixa' if previsao.get('temperatura', 25) < current_app.config.get('ALERT_TEMPERATURE_MIN', 0) else 'normal',
                    'umidade': 'alta' if previsao.get('umidade', 50) > current_app.config.get('ALERT_HUMIDITY_MAX', 90) else
                              'baixa' if previsao.get('umidade', 50) < current_app.config.get('ALERT_HUMIDITY_MIN', 20) else 'normal',
                    'precipitacao': 'intensa' if precipitacao > 50 else 'moderada' if precipitacao > 25 else 'leve' if precipitacao > 5 else 'sem_chuva'
                },
                'recomendacoes': gerar_recomendacoes(previsao, impacto)
            }
            
            previsoes_enriquecidas.append(previsao_enriquecida)
        
        # Calcular estatísticas gerais do período
        total_precipitacao = sum(p.get('precipitacao', 0) for p in previsoes)
        temperatura_media = sum(p.get('temperatura', 0) for p in previsoes) / len(previsoes) if previsoes else 0
        umidade_media = sum(p.get('umidade', 0) for p in previsoes) / len(previsoes) if previsoes else 0
        risco_maximo = max(p['risco_alagamento']['probabilidade'] for p in previsoes_enriquecidas)
        
        # Determinar alerta geral para o período
        alerta_geral = determinar_alerta_periodo(previsoes_enriquecidas)
        
        return jsonify({
            'status': 'success',
            'cidade': cidade,
            'estado': estado,
            'fonte': 'OpenWeatherMap',
            'periodo': {
                'inicio': previsoes[0].get('data'),
                'fim': previsoes[-1].get('data'),
                'total_dias': len(previsoes)
            },
            'resumo_periodo': {
                'total_precipitacao_mm': round(total_precipitacao, 2),
                'temperatura_media_c': round(temperatura_media, 1),
                'umidade_media_percent': round(umidade_media, 1),
                'risco_alagamento_maximo': risco_maximo,
                'dias_com_chuva': len([p for p in previsoes if p.get('precipitacao', 0) > 0]),
                'alerta_geral': alerta_geral
            },
            'previsoes': previsoes_enriquecidas,
            'total': len(previsoes_enriquecidas),
            'timestamp': datetime.utcnow().isoformat(),
            'cache_info': {
                'cached': False,
                'ttl_seconds': 1800
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter previsão meteorológica: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Não foi possível obter previsão meteorológica',
            'details': str(e) if current_app.debug else 'Erro interno',
            'timestamp': datetime.utcnow().isoformat()
        }), 500