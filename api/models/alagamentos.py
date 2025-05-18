import pandas as pd
import datetime
import random
from ..utils.db_utils import execute_query

class AlagamentosModel:
    """
    Modelo para manipulação de dados de alagamentos
    """
    
    @staticmethod
    def get_previsao_alagamentos(cidade, estado):
        """
        Obtém previsão de risco de alagamentos
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            
        Returns:
            dict: Dicionário com informações sobre risco de alagamentos
        """
        try:
            # Primeiro verifica se há previsão de chuvas fortes
            query = """
            SELECT 
                MAX(precipitacao_diaria) as max_precipitacao
            FROM 
                chuvas_diarias 
            WHERE 
                municipio = :cidade
                AND data BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '3 days'
            """
            
            params = {'cidade': cidade}
            df = execute_query(query, params)
            
            # Se não houver dados ou não for possível acessar o banco, usar dados simulados
            if df.empty or 'max_precipitacao' not in df.columns:
                return AlagamentosModel._gerar_previsao_simulada(cidade, estado)
            
            # Determinar nível de risco com base na precipitação máxima
            max_precipitacao = float(df['max_precipitacao'].iloc[0]) if not pd.isna(df['max_precipitacao'].iloc[0]) else 0
            
            if max_precipitacao >= 50:
                nivel_risco = 'alto'
                probabilidade = random.uniform(0.75, 0.95)
            elif max_precipitacao >= 30:
                nivel_risco = 'médio'
                probabilidade = random.uniform(0.45, 0.75)
            else:
                nivel_risco = 'baixo'
                probabilidade = random.uniform(0.10, 0.45)
            
            # Buscar áreas com histórico de alagamentos
            query_areas = """
            SELECT 
                DISTINCT local
            FROM 
                alagamentos 
            WHERE 
                municipio = :cidade
            ORDER BY 
                local
            """
            
            df_areas = execute_query(query_areas, params)
            
            if df_areas.empty or 'local' not in df_areas.columns:
                # Se não houver dados, usar áreas simuladas
                areas_afetadas = AlagamentosModel._gerar_areas_simuladas(cidade, estado)
            else:
                areas_afetadas = df_areas['local'].tolist()
            
            # Gerar recomendações com base no nível de risco
            recomendacoes = AlagamentosModel._gerar_recomendacoes(nivel_risco)
            
            return {
                'probabilidade': round(probabilidade, 2),
                'nivelRisco': nivel_risco,
                'recomendacoes': recomendacoes,
                'areasAfetadas': areas_afetadas
            }
            
        except Exception as e:
            print(f"Erro ao obter previsão de alagamentos: {str(e)}")
            # Retornar dados simulados em caso de erro
            return AlagamentosModel._gerar_previsao_simulada(cidade, estado)
    
    @staticmethod
    def get_historico_alagamentos(cidade, estado, data_inicio, data_fim):
        """
        Obtém histórico de ocorrências de alagamentos
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            data_inicio (str): Data inicial no formato YYYY-MM-DD
            data_fim (str): Data final no formato YYYY-MM-DD
            
        Returns:
            list: Lista de dicionários com informações de alagamentos
        """
        try:
            # Query para obter histórico do banco de dados (adaptada para PostgreSQL)
            query = """
            SELECT 
                municipio, 
                data, 
                local,
                dh_mortos,
                dh_afetados
            FROM 
                alagamentos 
            WHERE 
                municipio = :cidade
                AND data BETWEEN TO_DATE(:data_inicio, 'YYYY-MM-DD') 
                            AND TO_DATE(:data_fim, 'YYYY-MM-DD')
            ORDER BY 
                data DESC
            """
            
            params = {
                'cidade': cidade,
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
            
            df = execute_query(query, params)
            
            # Se não houver dados históricos, gerar dados simulados para teste
            if df.empty:
                return AlagamentosModel._gerar_historico_simulado(cidade, estado, data_inicio, data_fim)
            
            # Converter para formato esperado pela API
            resultado = []
            for _, row in df.iterrows():
                # Determinar nível de gravidade com base nos afetados
                if pd.isna(row['dh_afetados']) or row['dh_afetados'] == 0:
                    nivel_gravidade = 'baixo'
                elif row['dh_afetados'] > 500:
                    nivel_gravidade = 'alto'
                else:
                    nivel_gravidade = 'médio'
                
                resultado.append({
                    'data': row['data'].strftime('%Y-%m-%d'),
                    'local': row['local'] if not pd.isna(row['local']) else 'Área central',
                    'nivelGravidade': nivel_gravidade,
                    'afetados': int(row['dh_afetados']) if not pd.isna(row['dh_afetados']) else 0
                })
            
            return resultado
            
        except Exception as e:
            print(f"Erro ao obter histórico de alagamentos: {str(e)}")
            # Retornar dados simulados em caso de erro
            return AlagamentosModel._gerar_historico_simulado(cidade, estado, data_inicio, data_fim)
    
    @staticmethod
    def get_pontos_alagamento(cidade, estado):
        """
        Obtém pontos de alagamento conhecidos
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            
        Returns:
            list: Lista de dicionários com pontos de alagamento
        """
        try:
            # Em um sistema real, estes dados viriam de uma tabela específica
            # com coordenadas e informações de pontos críticos
            # Por enquanto, vamos retornar dados simulados
            return AlagamentosModel._gerar_pontos_simulados(cidade, estado)
            
        except Exception as e:
            print(f"Erro ao obter pontos de alagamento: {str(e)}")
            return AlagamentosModel._gerar_pontos_simulados(cidade, estado)
    
    @staticmethod
    def _gerar_previsao_simulada(cidade, estado):
        """
        Gera previsão simulada de risco de alagamentos
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            
        Returns:
            dict: Previsão simulada
        """
        # Simular condições diferentes para RJ e SP
        if estado == 'RJ':
            if cidade == 'Rio de Janeiro':
                nivel_risco = 'alto'
                probabilidade = random.uniform(0.75, 0.95)
            else:
                nivel_risco = 'médio'
                probabilidade = random.uniform(0.45, 0.75)
        else:  # SP
            if cidade == 'São Paulo':
                nivel_risco = 'médio'
                probabilidade = random.uniform(0.45, 0.75)
            else:
                nivel_risco = 'baixo'
                probabilidade = random.uniform(0.10, 0.45)
        
        # Gerar recomendações com base no nível de risco
        recomendacoes = AlagamentosModel._gerar_recomendacoes(nivel_risco)
        
        # Gerar áreas afetadas simuladas
        areas_afetadas = AlagamentosModel._gerar_areas_simuladas(cidade, estado)
        
        return {
            'probabilidade': round(probabilidade, 2),
            'nivelRisco': nivel_risco,
            'recomendacoes': recomendacoes,
            'areasAfetadas': areas_afetadas
        }
    
    @staticmethod
    def _gerar_historico_simulado(cidade, estado, data_inicio, data_fim):
        """
        Gera histórico simulado de alagamentos
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            data_inicio (str): Data inicial
            data_fim (str): Data final
            
        Returns:
            list: Histórico simulado
        """
        resultado = []
        data_inicio = datetime.datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim = datetime.datetime.strptime(data_fim, '%Y-%m-%d').date()
        
        # Quantidade de ocorrências (mais para RJ, menos para SP)
        num_ocorrencias = random.randint(5, 10) if estado == 'RJ' else random.randint(2, 7)
        
        # Gerar datas aleatórias no intervalo
        delta = (data_fim - data_inicio).days
        if delta <= 0:
            return resultado
        
        datas = sorted(random.sample(range(delta), min(num_ocorrencias, delta)), reverse=True)
        
        areas = AlagamentosModel._gerar_areas_simuladas(cidade, estado)
        
        for dias in datas:
            data = data_inicio + datetime.timedelta(days=dias)
            
            nivel_gravidade = random.choice(['baixo', 'médio', 'alto'])
            afetados = 0
            if nivel_gravidade == 'baixo':
                afetados = random.randint(10, 100)
            elif nivel_gravidade == 'médio':
                afetados = random.randint(100, 500)
            else:  # alto
                afetados = random.randint(500, 1000)
            
            resultado.append({
                'data': data.strftime('%Y-%m-%d'),
                'local': random.choice(areas),
                'nivelGravidade': nivel_gravidade,
                'afetados': afetados
            })
        
        return resultado
    
    @staticmethod
    def _gerar_pontos_simulados(cidade, estado):
        """
        Gera pontos simulados de alagamento para o mapa
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            
        Returns:
            list: Lista de pontos simulados
        """
        # Coordenadas aproximadas dos centros das cidades
        coordenadas = {
            'RJ': {
                'Rio de Janeiro': (-22.9068, -43.1729),
                'Niterói': (-22.8859, -43.1152),
                'Duque de Caxias': (-22.7654, -43.3102),
                'Nova Iguaçu': (-22.7556, -43.4603),
                'São Gonçalo': (-22.8268, -43.0634)
            },
            'SP': {
                'São Paulo': (-23.5505, -46.6333),
                'Campinas': (-22.9071, -47.0625),
                'Santos': (-23.9619, -46.3342),
                'Guarulhos': (-23.4543, -46.5337),
                'São Bernardo do Campo': (-23.6944, -46.5654)
            }
        }
        
        # Verificar se temos coordenadas para a cidade
        if estado not in coordenadas or cidade not in coordenadas[estado]:
            # Fallback para coordenadas da capital do estado
            if estado == 'RJ':
                base_lat, base_lon = coordenadas['RJ']['Rio de Janeiro']
            else:
                base_lat, base_lon = coordenadas['SP']['São Paulo']
        else:
            base_lat, base_lon = coordenadas[estado][cidade]
        
        # Quantidade de pontos (mais para cidades maiores)
        if cidade in ['Rio de Janeiro', 'São Paulo']:
            num_pontos = random.randint(5, 8)
        else:
            num_pontos = random.randint(2, 4)
        
        resultado = []
        areas = AlagamentosModel._gerar_areas_simuladas(cidade, estado)
        niveis_risco = ['alto', 'médio', 'baixo']
        
        for i in range(num_pontos):
            # Gerar coordenadas aleatórias próximas ao centro da cidade
            lat = base_lat + random.uniform(-0.05, 0.05)
            lon = base_lon + random.uniform(-0.05, 0.05)
            
            # Nível de risco - probabilidade maior para alto em cidades com mais histórico
            if cidade in ['Rio de Janeiro', 'São Paulo']:
                nivel_risco = random.choices(
                    niveis_risco, 
                    weights=[0.5, 0.3, 0.2]
                )[0]
            else:
                nivel_risco = random.choices(
                    niveis_risco, 
                    weights=[0.2, 0.4, 0.4]
                )[0]
            
            # Gerar precipitação prevista baseada no nível de risco
            if nivel_risco == 'alto':
                precipitacao = random.uniform(40, 60)
            elif nivel_risco == 'médio':
                precipitacao = random.uniform(25, 40)
            else:
                precipitacao = random.uniform(10, 25)
            
            # Data do último alagamento (mais recente para áreas de alto risco)
            hoje = datetime.date.today()
            if nivel_risco == 'alto':
                dias_atras = random.randint(10, 60)
            elif nivel_risco == 'médio':
                dias_atras = random.randint(30, 90)
            else:
                dias_atras = random.randint(60, 180)
            
            ultimo_alagamento = (hoje - datetime.timedelta(days=dias_atras)).strftime('%Y-%m-%d')
            
            # Raio afetado - maior para níveis mais altos de risco
            if nivel_risco == 'alto':
                raio = random.randint(300, 450)
            elif nivel_risco == 'médio':
                raio = random.randint(200, 300)
            else:
                raio = random.randint(100, 200)
            
            resultado.append({
                'latitude': lat,
                'longitude': lon,
                'local': areas[i % len(areas)],
                'nivelRisco': nivel_risco,
                'precipitacaoPrevista': round(precipitacao, 1),
                'ultimoAlagamento': ultimo_alagamento,
                'raioAfetado': raio
            })
        
        return resultado
    
    @staticmethod
    def _gerar_areas_simuladas(cidade, estado):
        """
        Gera nomes de áreas simuladas para cada cidade
        
        Args:
            cidade (str): Nome da cidade
            estado (str): Sigla do estado
            
        Returns:
            list: Lista de nomes de áreas
        """
        areas = {
            'Rio de Janeiro': ['Praça da Bandeira', 'Maracanã', 'Tijuca (Parte baixa)', 
                              'Jardim Botânico', 'Copacabana', 'Centro'],
            'Niterói': ['Centro', 'São Domingos', 'Icaraí', 'Santa Rosa'],
            'São Paulo': ['Pinheiros', 'Sé', 'Lapa', 'Butantã', 'Santo Amaro', 'Ipiranga'],
            'Campinas': ['Centro', 'Barão Geraldo', 'Taquaral', 'Bosque']
        }
        
        # Retornar áreas específicas ou áreas genéricas para outras cidades
        if cidade in areas:
            return areas[cidade]
        
        # Áreas genéricas
        return ['Centro', 'Área Comercial', 'Bairro Residencial', 'Região Central']
    
    @staticmethod
    def _gerar_recomendacoes(nivel_risco):
        """
        Gera recomendações baseadas no nível de risco
        
        Args:
            nivel_risco (str): Nível de risco (alto, médio, baixo)
            
        Returns:
            list: Lista de recomendações
        """
        recomendacoes = {
            'alto': [
                'Evite áreas marcadas em vermelho no mapa',
                'Mantenha-se informado sobre alertas da Defesa Civil',
                'Tenha um plano de emergência preparado',
                'Considere a possibilidade de evacuação preventiva',
                'Não atravesse áreas alagadas'
            ],
            'médio': [
                'Esteja atento às previsões meteorológicas',
                'Evite áreas com histórico de alagamentos',
                'Mantenha-se informado sobre alertas da Defesa Civil',
                'Evite deslocamentos desnecessários em caso de chuva forte'
            ],
            'baixo': [
                'Monitore as condições meteorológicas',
                'Esteja atento a mudanças climáticas repentinas',
                'Verifique os canais oficiais de informação'
            ]
        }
        
        return recomendacoes.get(nivel_risco, ['Mantenha-se informado sobre o clima']) 