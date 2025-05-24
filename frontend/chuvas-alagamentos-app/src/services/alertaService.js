import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://thm-pg0z.onrender.com';

// Configuração do axios com timeout padrão
const api = axios.create({
  baseURL: API_URL,
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor para log de requisições
api.interceptors.request.use(
  (config) => {
    console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`, config.params);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Interceptor para tratamento de respostas
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    const url = error.config?.url || 'unknown';
    const status = error.response?.status || 'no status';
    console.warn(`⚠️ API Error: ${url} - Status: ${status}`, error.message);
    return Promise.reject(error);
  }
);

// Função auxiliar para validar resposta
const validarResposta = (dados, tipo) => {
  if (!dados) {
    throw new Error(`Resposta vazia para ${tipo}`);
  }

  if (tipo === 'chuvas' && !Array.isArray(dados)) {
    throw new Error('Formato de dados de chuvas inválido');
  }

  if (tipo === 'alagamentos') {
    if (!Array.isArray(dados) && typeof dados !== 'object') {
      throw new Error('Formato de dados de alagamentos inválido');
    }
    if (Array.isArray(dados) && dados.length > 0) {
      dados.forEach(alagamento => {
        if (!alagamento.nivelRisco || !alagamento.probabilidade) {
          throw new Error('Dados de alagamento incompletos');
        }
      });
    }
  }

  return dados;
};

// Gerador de dados mockados mais sofisticado
const gerarDadosMockados = (cidade, estado, tipo = 'previsao', dataInicial = null, dataFinal = null) => {
  const hoje = new Date();
  const dados = [];
  
  let dataInicio, dataFim, numeroDias;
  
  if (tipo === 'historico' && dataInicial && dataFinal) {
    dataInicio = new Date(dataInicial);
    dataFim = new Date(dataFinal);
    numeroDias = Math.ceil((dataFim - dataInicio) / (1000 * 60 * 60 * 24)) + 1;
  } else {
    dataInicio = new Date(hoje);
    numeroDias = 7; // Previsão de 7 dias
    dataFim = new Date(hoje);
    dataFim.setDate(hoje.getDate() + 6);
  }
  
  // Padrões climáticos baseados na região
  const padroesPorEstado = {
    'RJ': { tempBase: 25, precipitacaoMedia: 120, umidadeBase: 75 },
    'SP': { tempBase: 22, precipitacaoMedia: 100, umidadeBase: 70 },
    'MG': { tempBase: 23, precipitacaoMedia: 90, umidadeBase: 65 },
    'ES': { tempBase: 26, precipitacaoMedia: 110, umidadeBase: 80 }
  };
  
  const padrao = padroesPorEstado[estado] || padroesPorEstado['RJ'];
  
  for (let i = 0; i < Math.min(numeroDias, 365); i++) {
    const data = new Date(dataInicio);
    
    if (tipo === 'historico') {
      data.setDate(dataInicio.getDate() + i);
      if (data > dataFim) break;
      
      // Para histórico, nem todos os dias têm dados
      if (Math.random() > 0.25) { // 75% de chance de ter dados
        const precipitacao = Math.random() > 0.6 ? Math.random() * (padrao.precipitacaoMedia * 0.8) : 0;
        dados.push({
          data: data.toISOString().split('T')[0],
          municipio: cidade,
          estado: estado,
          precipitacao: parseFloat(precipitacao.toFixed(1)),
          timestamp: data.toISOString()
        });
      }
    } else {
      // Para previsão
      data.setDate(hoje.getDate() + i);
      
      const precipitacao = Math.random() * 60; // 0-60mm
      const temperatura = padrao.tempBase + (Math.random() - 0.5) * 10; // ±5°C da base
      const umidade = padrao.umidadeBase + (Math.random() - 0.5) * 30; // ±15% da base
      
      const riscoAlto = precipitacao > 35;
      const riscoMedio = precipitacao > 20 && precipitacao <= 35;
      
      dados.push({
        data: data.toISOString().split('T')[0],
        municipio: cidade,
        estado: estado,
        precipitacao: parseFloat(precipitacao.toFixed(1)),
        temperatura: parseFloat(temperatura.toFixed(1)),
        umidade: Math.round(Math.max(30, Math.min(100, umidade))),
        riscoAlagamento: riscoAlto || riscoMedio,
        nivelRisco: riscoAlto ? 'alto' : riscoMedio ? 'medio' : 'baixo',
        probabilidadeAlagamento: riscoAlto ? Math.round(70 + Math.random() * 30) : 
                                riscoMedio ? Math.round(30 + Math.random() * 40) : 
                                Math.round(Math.random() * 20),
        recomendacoes: riscoAlto ? [
          "⚠️ Evite áreas de alagamento conhecidas",
          "📱 Mantenha-se informado sobre as condições do tempo",
          "🎒 Tenha um kit de emergência preparado",
          "🚗 Evite dirigir em áreas de risco"
        ] : riscoMedio ? [
          "👀 Fique atento às condições climáticas",
          "📊 Monitore os níveis de precipitação"
        ] : [],
        confiabilidade: Math.round(75 + Math.random() * 20) // 75-95%
      });
    }
  }
  
  return dados;
};

// Função para verificar se a API está disponível
const verificarStatusAPI = async () => {
  try {
    const response = await api.get('/health', { timeout: 3000 });
    return response.status === 200;
  } catch (error) {
    console.warn('🔍 API Health Check falhou:', error.message);
    return false;
  }
};

// Obter dados de alerta atual
export const getDadosAlerta = async (cidade, estado) => {
  console.log('🚨 getDadosAlerta:', { cidade, estado });
  
  try {
    const params = {};
    if (cidade) params.cidade = cidade;
    if (estado) params.estado = estado;
    
    const response = await api.get('/previsao/alertas', { params });
    return validarResposta(response.data, 'alertas');
  } catch (error) {
    console.warn('⚠️ Erro ao buscar alertas, usando dados estimados:', error.message);
    
    // Gera alertas baseados na previsão atual
    const previsao = await getPrevisaoChuvas(cidade, estado);
    const alertas = previsao
      .filter(item => item.riscoAlagamento)
      .map(item => ({
        id: `alert_${item.data}`,
        municipio: item.municipio,
        estado: item.estado,
        data: item.data,
        nivel: item.nivelRisco || 'medio',
        tipo: 'alagamento',
        descricao: `Risco de alagamento previsto para ${item.data}`,
        precipitacaoEsperada: item.precipitacao,
        recomendacoes: item.recomendacoes || []
      }));
    
    return alertas;
  }
};

// Obter previsão de chuvas
export const getPrevisaoChuvas = async (cidade, estado) => {
  console.log('🌧️ getPrevisaoChuvas:', { cidade, estado });
  
  try {
    const response = await api.get('/previsao/chuvas', {
      params: { cidade, estado }
    });
    
    const dados = Array.isArray(response.data) ? response.data : [response.data];
    console.log('✅ Dados da API obtidos:', dados.length, 'registros');
    return dados;
    
  } catch (error) {
    console.warn('⚠️ API de previsão indisponível, usando dados mockados:', error.message);
    
    const dadosMockados = gerarDadosMockados(cidade, estado, 'previsao');
    console.log('🎭 Dados mockados gerados:', dadosMockados.length, 'registros');
    return dadosMockados;
  }
};

// Obter previsão de alagamentos
export const getPrevisaoAlagamentos = async (cidade, estado) => {
  console.log('🌊 getPrevisaoAlagamentos:', { cidade, estado });
  
  try {
    const response = await api.get('/previsao/alagamentos', {
      params: { cidade, estado }
    });
    
    const dados = Array.isArray(response.data) ? response.data : [response.data];
    return dados;
  } catch (error) {
    console.warn('⚠️ API de alagamentos indisponível, estimando baseado na previsão de chuvas:', error.message);
    
    // Estima alagamentos baseado na previsão de chuvas
    const previsaoChuvas = await getPrevisaoChuvas(cidade, estado);
    const estimativaAlagamentos = previsaoChuvas
      .filter(item => item.precipitacao > 15) // Apenas dias com chuva significativa
      .map(item => ({
        data: item.data,
        municipio: item.municipio,
        estado: item.estado,
        nivelRisco: item.nivelRisco || (item.precipitacao > 35 ? 'alto' : 'medio'),
        probabilidade: item.probabilidadeAlagamento || Math.round((item.precipitacao / 60) * 100),
        precipitacaoAssociada: item.precipitacao,
        areas_risco: [
          'Centro da cidade',
          'Áreas baixas',
          'Próximo aos rios'
        ],
        recomendacoes: item.recomendacoes || []
      }));
    
    console.log('📊 Estimativa de alagamentos gerada:', estimativaAlagamentos.length, 'registros');
    return estimativaAlagamentos;
  }
};

// Obter histórico de chuvas
export const getHistoricoChuvas = async (cidade, estado, dataInicial, dataFinal) => {
  console.log('📚 getHistoricoChuvas:', { cidade, estado, dataInicial, dataFinal });
  
  try {
    if (!cidade || !estado) {
      console.warn('⚠️ Parâmetros obrigatórios não fornecidos');
      return [];
    }

    const response = await api.get('/historico/chuvas', {
      params: { cidade, estado, dataInicial, dataFinal }
    });

    const dados = Array.isArray(response.data) ? response.data : [];
    console.log('✅ Histórico obtido da API:', dados.length, 'registros');
    return dados;
    
  } catch (error) {
    console.warn('⚠️ API de histórico indisponível, gerando dados mockados:', error.message);
    
    const dadosMockados = gerarDadosMockados(cidade, estado, 'historico', dataInicial, dataFinal);
    console.log('🎭 Dados históricos mockados gerados:', dadosMockados.length, 'registros');
    return dadosMockados;
  }
};

// Obter histórico de alagamentos
export const getHistoricoAlagamentos = async (cidade, estado, dataInicial, dataFinal) => {
  console.log('🌊📚 getHistoricoAlagamentos:', { cidade, estado, dataInicial, dataFinal });
  
  try {
    if (!cidade || !estado) {
      console.warn('⚠️ Parâmetros obrigatórios não fornecidos');
      return [];
    }

    const response = await api.get('/historico/alagamentos', {
      params: { cidade, estado, dataInicial, dataFinal }
    });

    const dados = Array.isArray(response.data) ? response.data : [];
    console.log('✅ Histórico de alagamentos obtido:', dados.length, 'registros');
    return dados;
    
  } catch (error) {
    console.warn('⚠️ API de histórico de alagamentos indisponível, estimando baseado em chuvas:', error.message);
    
    // Tenta obter histórico de chuvas e estimar alagamentos
    const historicoChuvas = await getHistoricoChuvas(cidade, estado, dataInicial, dataFinal);
    const estimativaAlagamentos = historicoChuvas
      .filter(item => item.precipitacao > 30) // Apenas dias com chuva forte
      .map(item => ({
        data: item.data,
        municipio: item.municipio,
        estado: item.estado,
        ocorrencia: true,
        severidade: item.precipitacao > 50 ? 'alta' : 'media',
        precipitacaoAssociada: item.precipitacao,
        areas_afetadas: Math.floor(Math.random() * 5) + 1,
        descricao: `Alagamento registrado com ${item.precipitacao}mm de chuva`
      }));
    
    console.log('📊 Estimativa histórica de alagamentos:', estimativaAlagamentos.length, 'registros');
    return estimativaAlagamentos;
  }
};

// Obter lista de municípios
export const getMunicipios = async (estado) => {
  console.log('🏙️ getMunicipios:', { estado });
  
  try {
    const response = await api.get('/municipios', {
      params: { estado }
    });
    
    const dados = Array.isArray(response.data) ? response.data : [];
    console.log('✅ Municípios obtidos da API:', dados.length);
    return dados;
    
  } catch (error) {
    console.warn('⚠️ API de municípios indisponível, usando lista expandida:', error.message);
    
    // Lista expandida de municípios por estado
    const municipiosPadrao = {
      'RJ': [
        { nome: 'Rio de Janeiro', uf: 'RJ', populacao: 6748000 },
        { nome: 'Niterói', uf: 'RJ', populacao: 515000 },
        { nome: 'Petrópolis', uf: 'RJ', populacao: 306000 },
        { nome: 'Nova Iguaçu', uf: 'RJ', populacao: 821000 },
        { nome: 'Duque de Caxias', uf: 'RJ', populacao: 919000 },
        { nome: 'São Gonçalo', uf: 'RJ', populacao: 1084000 },
        { nome: 'Volta Redonda', uf: 'RJ', populacao: 273000 },
        { nome: 'Campos dos Goytacazes', uf: 'RJ', populacao: 507000 },
        { nome: 'Angra dos Reis', uf: 'RJ', populacao: 200000 },
        { nome: 'Cabo Frio', uf: 'RJ', populacao: 230000 }
      ],
      'SP': [
        { nome: 'São Paulo', uf: 'SP', populacao: 12400000 },
        { nome: 'Guarulhos', uf: 'SP', populacao: 1400000 },
        { nome: 'Campinas', uf: 'SP', populacao: 1213000 },
        { nome: 'São Bernardo do Campo', uf: 'SP', populacao: 844000 },
        { nome: 'Santo André', uf: 'SP', populacao: 721000 },
        { nome: 'Osasco', uf: 'SP', populacao: 696000 },
        { nome: 'São José dos Campos', uf: 'SP', populacao: 729000 },
        { nome: 'Ribeirão Preto', uf: 'SP', populacao: 703000 },
        { nome: 'Sorocaba', uf: 'SP', populacao: 687000 },
        { nome: 'Santos', uf: 'SP', populacao: 433000 }
      ],
      'MG': [
        { nome: 'Belo Horizonte', uf: 'MG', populacao: 2530000 },
        { nome: 'Uberlândia', uf: 'MG', populacao: 699000 },
        { nome: 'Contagem', uf: 'MG', populacao: 668000 },
        { nome: 'Juiz de Fora', uf: 'MG', populacao: 573000 }
      ],
      'ES': [
        { nome: 'Vitória', uf: 'ES', populacao: 365000 },
        { nome: 'Vila Velha', uf: 'ES', populacao: 501000 },
        { nome: 'Serra', uf: 'ES', populacao: 527000 },
        { nome: 'Cariacica', uf: 'ES', populacao: 387000 }
      ]
    };
    
    if (!estado) {
      // Retorna todos os municípios se não especificar estado
      const todosMunicipios = Object.values(municipiosPadrao).flat();
      console.log('📋 Retornando todos os municípios:', todosMunicipios.length);
      return todosMunicipios;
    }
    
    const municipiosEstado = municipiosPadrao[estado] || [];
    console.log('📋 Municípios do estado', estado, ':', municipiosEstado.length);
    return municipiosEstado;
  }
};

// Obter lista de estados
export const getEstados = async () => {
  console.log('🗺️ getEstados');
  
  try {
    const response = await api.get('/estados');
    const dados = Array.isArray(response.data) ? response.data : [];
    console.log('✅ Estados obtidos da API:', dados.length);
    return dados;
    
  } catch (error) {
    console.warn('⚠️ API de estados indisponível, usando lista expandida:', error.message);
    
    const estadosPadrao = [
      { sigla: 'RJ', nome: 'Rio de Janeiro', regiao: 'Sudeste' },
      { sigla: 'SP', nome: 'São Paulo', regiao: 'Sudeste' },
      { sigla: 'MG', nome: 'Minas Gerais', regiao: 'Sudeste' },
      { sigla: 'ES', nome: 'Espírito Santo', regiao: 'Sudeste' },
      { sigla: 'PR', nome: 'Paraná', regiao: 'Sul' },
      { sigla: 'SC', nome: 'Santa Catarina', regiao: 'Sul' },
      { sigla: 'RS', nome: 'Rio Grande do Sul', regiao: 'Sul' }
    ];
    
    console.log('📋 Estados padrão retornados:', estadosPadrao.length);
    return estadosPadrao;
  }
};

// Função para obter estatísticas da API
export const getEstatisticasAPI = async () => {
  try {
    const status = await verificarStatusAPI();
    return {
      disponivel: status,
      timestamp: new Date().toISOString(),
      endpoints: {
        alertas: '/previsao/alertas',
        chuvas: '/previsao/chuvas',
        alagamentos: '/previsao/alagamentos',
        historicoChuvas: '/historico/chuvas',
        historicoAlagamentos: '/historico/alagamentos'
      }
    };
  } catch (error) {
    return {
      disponivel: false,
      erro: error.message,
      timestamp: new Date().toISOString()
    };
  }
};

// Export default com todas as funções
export default {
  getDadosAlerta,
  getPrevisaoChuvas,
  getPrevisaoAlagamentos,
  getHistoricoChuvas,
  getHistoricoAlagamentos,
  getMunicipios,
  getEstados,
  getEstatisticasAPI,
  verificarStatusAPI
};