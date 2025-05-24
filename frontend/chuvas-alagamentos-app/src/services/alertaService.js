import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://thm-pg0z.onrender.com';

// Configuração do axios com timeout padrão
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000, // Aumentado para 10s
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

// Função para normalizar dados de data
const normalizarData = (dataString) => {
  if (!dataString) return null;
  
  try {
    // Remove timezone se presente
    let dataLimpa = dataString;
    if (dataString.includes('T')) {
      dataLimpa = dataString.split('T')[0];
    }
    
    // Garantir formato YYYY-MM-DD
    if (dataLimpa.includes('/')) {
      const partes = dataLimpa.split('/');
      if (partes.length === 3) {
        // Assume DD/MM/YYYY ou MM/DD/YYYY
        const [p1, p2, p3] = partes;
        if (p3.length === 4) {
          // DD/MM/YYYY ou MM/DD/YYYY -> YYYY-MM-DD
          if (parseInt(p1) > 12) {
            // DD/MM/YYYY
            dataLimpa = `${p3}-${p2.padStart(2, '0')}-${p1.padStart(2, '0')}`;
          } else {
            // MM/DD/YYYY
            dataLimpa = `${p3}-${p1.padStart(2, '0')}-${p2.padStart(2, '0')}`;
          }
        }
      }
    }
    
    // Validar se a data é válida
    const data = new Date(dataLimpa);
    if (isNaN(data.getTime())) {
      console.warn('Data inválida após normalização:', dataString, '->', dataLimpa);
      return null;
    }
    
    return dataLimpa;
  } catch (error) {
    console.error('Erro ao normalizar data:', dataString, error);
    return null;
  }
};

// Função para processar dados da API
const processarDadosAPI = (dados, tipo = 'chuvas') => {
  if (!dados) return [];
  
  const dadosArray = Array.isArray(dados) ? dados : [dados];
  
  return dadosArray.map(item => {
    const itemProcessado = { ...item };
    
    // Normalizar data
    if (item.data) {
      itemProcessado.data = normalizarData(item.data);
    }
    
    // Garantir campos numéricos
    if (tipo === 'chuvas') {
      itemProcessado.precipitacao = parseFloat(item.precipitacao || 0);
      if (item.temperatura) {
        itemProcessado.temperatura = parseFloat(item.temperatura);
      }
      if (item.umidade) {
        itemProcessado.umidade = parseInt(item.umidade);
      }
    }
    
    // Garantir campos de texto
    itemProcessado.municipio = item.municipio || item.cidade || '';
    itemProcessado.estado = item.estado || item.uf || '';
    
    return itemProcessado;
  }).filter(item => item.data); // Remove itens sem data válida
};

// Obter dados de alerta atual
export const getDadosAlerta = async (cidade, estado) => {
  console.log('🚨 getDadosAlerta:', { cidade, estado });
  
  try {
    const params = {};
    if (cidade) params.cidade = cidade;
    if (estado) params.estado = estado;
    
    const response = await api.get('/previsao/alertas', { params });
    
    // Processar resposta da API
    const dados = response.data;
    if (dados && dados.nivel > 0) {
      return [{
        id: `alert_${Date.now()}`,
        municipio: cidade,
        estado: estado,
        data: new Date().toISOString().split('T')[0],
        nivel: dados.nivel >= 3 ? 'alto' : dados.nivel >= 2 ? 'medio' : 'baixo',
        tipo: 'alagamento',
        descricao: dados.mensagem || 'Alerta de alagamento ativo',
        regioes_afetadas: dados.regioes_afetadas || [],
        data_atualizacao: dados.data_atualizacao
      }];
    }
    
    return [];
  } catch (error) {
    console.warn('⚠️ Erro ao buscar alertas:', error.message);
    return [];
  }
};

// Obter previsão de chuvas
export const getPrevisaoChuvas = async (cidade, estado) => {
  console.log('🌧️ getPrevisaoChuvas:', { cidade, estado });
  
  try {
    const response = await api.get('/previsao/chuvas', {
      params: { cidade, estado }
    });
    
    const dadosProcessados = processarDadosAPI(response.data, 'chuvas');
    console.log('✅ Dados processados da API:', dadosProcessados.length, 'registros');
    
    if (dadosProcessados.length === 0) {
      throw new Error('Nenhum dado válido retornado pela API');
    }
    
    return dadosProcessados;
    
  } catch (error) {
    console.warn('⚠️ Erro na API de previsão:', error.message);
    throw error; // Re-throw para mostrar erro real ao usuário
  }
};

// Obter previsão de alagamentos
export const getPrevisaoAlagamentos = async (cidade, estado) => {
  console.log('🌊 getPrevisaoAlagamentos:', { cidade, estado });
  
  try {
    const response = await api.get('/previsao/alagamentos', {
      params: { cidade, estado }
    });
    
    const dadosProcessados = processarDadosAPI(response.data, 'alagamentos');
    return dadosProcessados;
  } catch (error) {
    console.warn('⚠️ Erro na API de alagamentos:', error.message);
    return []; // Retorna array vazio em caso de erro
  }
};

// Obter histórico de chuvas
export const getHistoricoChuvas = async (cidade, estado, dataInicial, dataFinal) => {
  console.log('📚 getHistoricoChuvas:', { cidade, estado, dataInicial, dataFinal });
  
  try {
    if (!cidade || !estado) {
      throw new Error('Cidade e estado são obrigatórios');
    }

    const response = await api.get('/historico/chuvas', {
      params: { cidade, estado, dataInicial, dataFinal }
    });

    const dadosProcessados = processarDadosAPI(response.data, 'chuvas');
    console.log('✅ Histórico processado:', dadosProcessados.length, 'registros');
    
    return dadosProcessados;
    
  } catch (error) {
    console.error('❌ Erro ao buscar histórico de chuvas:', error.message);
    throw error; // Re-throw para mostrar erro real
  }
};

// Obter histórico de alagamentos
export const getHistoricoAlagamentos = async (cidade, estado, dataInicial, dataFinal) => {
  console.log('🌊📚 getHistoricoAlagamentos:', { cidade, estado, dataInicial, dataFinal });
  
  try {
    if (!cidade || !estado) {
      throw new Error('Cidade e estado são obrigatórios');
    }

    const response = await api.get('/historico/alagamentos', {
      params: { cidade, estado, dataInicial, dataFinal }
    });

    const dadosProcessados = processarDadosAPI(response.data, 'alagamentos');
    console.log('✅ Histórico de alagamentos processado:', dadosProcessados.length, 'registros');
    
    return dadosProcessados;
    
  } catch (error) {
    console.error('❌ Erro ao buscar histórico de alagamentos:', error.message);
    return []; // Retorna array vazio para não quebrar a interface
  }
};

// Obter lista de municípios - filtrada para RJ e SP
export const getMunicipios = async (estado = null) => {
  console.log('🏙️ getMunicipios:', { estado });
  
  try {
    const response = await api.get('/municipios', {
      params: estado ? { estado } : {}
    });
    
    let dados = Array.isArray(response.data) ? response.data : [];
    
    // Filtrar apenas RJ e SP
    dados = dados.filter(municipio => 
      municipio && municipio.uf && ['RJ', 'SP'].includes(municipio.uf)
    );
    
    // Se foi solicitado um estado específico, filtrar por ele
    if (estado) {
      dados = dados.filter(municipio => municipio.uf === estado);
    }
    
    console.log('✅ Municípios filtrados (RJ/SP):', dados.length);
    return dados;
    
  } catch (error) {
    console.warn('⚠️ Erro na API de municípios:', error.message);
    
    // Fallback com municípios principais de RJ e SP
    const municipiosFallback = [
      // Rio de Janeiro
      { nome: 'Rio de Janeiro', uf: 'RJ' },
      { nome: 'Niterói', uf: 'RJ' },
      { nome: 'Petrópolis', uf: 'RJ' },
      { nome: 'Nova Iguaçu', uf: 'RJ' },
      { nome: 'Duque de Caxias', uf: 'RJ' },
      { nome: 'São Gonçalo', uf: 'RJ' },
      { nome: 'Volta Redonda', uf: 'RJ' },
      { nome: 'Campos dos Goytacazes', uf: 'RJ' },
      { nome: 'Angra dos Reis', uf: 'RJ' },
      { nome: 'Cabo Frio', uf: 'RJ' },
      // São Paulo
      { nome: 'São Paulo', uf: 'SP' },
      { nome: 'Guarulhos', uf: 'SP' },
      { nome: 'Campinas', uf: 'SP' },
      { nome: 'São Bernardo do Campo', uf: 'SP' },
      { nome: 'Santo André', uf: 'SP' },
      { nome: 'Osasco', uf: 'SP' },
      { nome: 'São José dos Campos', uf: 'SP' },
      { nome: 'Ribeirão Preto', uf: 'SP' },
      { nome: 'Sorocaba', uf: 'SP' },
      { nome: 'Santos', uf: 'SP' }
    ];
    
    const dadosFiltrados = estado ? 
      municipiosFallback.filter(m => m.uf === estado) : 
      municipiosFallback;
    
    console.log('📋 Usando municípios fallback:', dadosFiltrados.length);
    return dadosFiltrados;
  }
};

// Obter lista de estados (apenas RJ e SP)
export const getEstados = async () => {
  console.log('🗺️ getEstados');
  
  const estadosSuportados = [
    { sigla: 'RJ', nome: 'Rio de Janeiro', regiao: 'Sudeste' },
    { sigla: 'SP', nome: 'São Paulo', regiao: 'Sudeste' }
  ];
  
  console.log('📋 Estados suportados:', estadosSuportados.length);
  return estadosSuportados;
};

// Função para verificar se a API está disponível
export const verificarStatusAPI = async () => {
  try {
    const response = await api.get('/health', { timeout: 5000 });
    return response.status === 200;
  } catch (error) {
    console.warn('🔍 API Health Check falhou:', error.message);
    return false;
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