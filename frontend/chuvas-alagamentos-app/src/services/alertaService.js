import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://thm-pg0z.onrender.com';

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

// Dados mockados para desenvolvimento
const gerarDadosMockados = (cidade, estado) => {
  const hoje = new Date();
  const dados = [];
  
  for (let i = 0; i < 7; i++) {
    const data = new Date(hoje);
    data.setDate(hoje.getDate() + i);
    
    const precipitacao = Math.random() * 50; // 0-50mm
    const temperatura = 20 + Math.random() * 15; // 20-35°C
    const umidade = 60 + Math.random() * 40; // 60-100%
    
    dados.push({
      data: data.toISOString().split('T')[0],
      municipio: cidade,
      estado: estado,
      precipitacao: parseFloat(precipitacao.toFixed(1)),
      temperatura: parseFloat(temperatura.toFixed(1)),
      umidade: Math.round(umidade),
      riscoAlagamento: precipitacao > 30,
      probabilidadeAlagamento: precipitacao > 30 ? Math.round(precipitacao * 2) : 0,
      recomendacoes: precipitacao > 30 ? [
        "Evite áreas de alagamento conhecidas",
        "Mantenha-se informado sobre as condições do tempo",
        "Tenha um kit de emergência preparado"
      ] : []
    });
  }
  
  return dados;
};

// Obter dados de alerta atual
export const getDadosAlerta = async (cidade, estado) => {
  try {
    const params = {};
    if (cidade) params.cidade = cidade;
    if (estado) params.estado = estado;
    const response = await axios.get(`${API_URL}/previsao/alertas`, { params });
    return validarResposta(response.data, 'alertas');
  } catch (error) {
    console.error('Erro ao buscar dados de alerta:', error);
    throw new Error(error.response?.data?.message || 'Erro ao buscar dados de alerta');
  }
};

// Obter previsão de chuvas
export const getPrevisaoChuvas = async (cidade, estado) => {
  console.log('=== getPrevisaoChuvas ===');
  console.log('Parâmetros:', { cidade, estado });
  
  try {
    // Primeiro tenta a API real
    const response = await axios.get(`${API_URL}/previsao/chuvas`, {
      params: { cidade, estado },
      timeout: 5000
    });
    
    console.log('Dados da API:', response.data);
    return Array.isArray(response.data) ? response.data : [response.data];
    
  } catch (error) {
    console.warn('API indisponível, usando dados mockados:', error.message);
    
    // Se a API falhar, usa dados mockados
    const dadosMockados = gerarDadosMockados(cidade, estado);
    console.log('Dados mockados gerados:', dadosMockados);
    return dadosMockados;
  }
};

// Obter previsão de alagamentos
export const getPrevisaoAlagamentos = async (cidade, estado) => {
  try {
    const response = await axios.get(`${API_URL}/previsao/alagamentos`, {
      params: { cidade, estado },
      timeout: 5000
    });
    return Array.isArray(response.data) ? response.data : [response.data];
  } catch (error) {
    console.warn('API de alagamentos indisponível:', error.message);
    // Retorna dados vazios se a API falhar
    return [];
  }
};

// Obter histórico de chuvas
export const getHistoricoChuvas = async (cidade, estado, dataInicial, dataFinal) => {
  console.log('=== getHistoricoChuvas ===');
  console.log('Parâmetros:', { cidade, estado, dataInicial, dataFinal });
  
  try {
    if (!cidade || !estado) {
      console.warn('Cidade ou estado não definidos:', { cidade, estado });
      return [];
    }

    const response = await axios.get(`${API_URL}/historico/chuvas`, {
      params: { cidade, estado, dataInicial, dataFinal },
      timeout: 10000
    });

    console.log('Dados da API:', response.data);
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.warn('API de histórico indisponível, gerando dados mockados:', error.message);
    
    // Gerar dados históricos mockados
    const inicio = new Date(dataInicial);
    const fim = new Date(dataFinal);
    const dados = [];
    
    const dataAtual = new Date(inicio);
    while (dataAtual <= fim) {
      if (Math.random() > 0.3) { // 70% de chance de ter dados
        dados.push({
          data: dataAtual.toISOString().split('T')[0],
          municipio: cidade,
          estado: estado,
          precipitacao: parseFloat((Math.random() * 80).toFixed(1))
        });
      }
      dataAtual.setDate(dataAtual.getDate() + 1);
    }
    
    console.log('Dados mockados gerados:', dados);
    return dados;
  }
};

// Obter histórico de alagamentos
export const getHistoricoAlagamentos = async (cidade, estado, dataInicial, dataFinal) => {
  console.log('=== getHistoricoAlagamentos ===');
  console.log('Parâmetros:', { cidade, estado, dataInicial, dataFinal });
  
  try {
    if (!cidade || !estado) {
      console.warn('Cidade ou estado não definidos:', { cidade, estado });
      return [];
    }

    const response = await axios.get(`${API_URL}/historico/alagamentos`, {
      params: { cidade, estado, dataInicial, dataFinal },
      timeout: 10000
    });

    console.log('Dados da API:', response.data);
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.warn('API de histórico de alagamentos indisponível:', error.message);
    return [];
  }
};

// Obter lista de municípios
export const getMunicipios = async (estado) => {
  try {
    const response = await axios.get(`${API_URL}/municipios`, {
      params: { estado },
      timeout: 5000
    });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.warn('API de municípios indisponível, usando lista padrão:', error.message);
    
    // Lista padrão de municípios
    const municipiosPadrao = {
      'RJ': [
        { nome: 'Rio de Janeiro', uf: 'RJ' },
        { nome: 'Niterói', uf: 'RJ' },
        { nome: 'Petrópolis', uf: 'RJ' },
        { nome: 'Nova Iguaçu', uf: 'RJ' },
        { nome: 'Duque de Caxias', uf: 'RJ' },
        { nome: 'São Gonçalo', uf: 'RJ' },
        { nome: 'Volta Redonda', uf: 'RJ' },
        { nome: 'Campos dos Goytacazes', uf: 'RJ' }
      ],
      'SP': [
        { nome: 'São Paulo', uf: 'SP' },
        { nome: 'Guarulhos', uf: 'SP' },
        { nome: 'Campinas', uf: 'SP' },
        { nome: 'São Bernardo do Campo', uf: 'SP' },
        { nome: 'Santo André', uf: 'SP' },
        { nome: 'Osasco', uf: 'SP' },
        { nome: 'São José dos Campos', uf: 'SP' },
        { nome: 'Ribeirão Preto', uf: 'SP' }
      ]
    };
    
    // Retorna todos os municípios se não especificar estado
    if (!estado) {
      return [...municipiosPadrao.RJ, ...municipiosPadrao.SP];
    }
    
    return municipiosPadrao[estado] || [];
  }
};

export const getEstados = async () => {
  try {
    const response = await axios.get(`${API_URL}/estados`, { timeout: 5000 });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.warn('API de estados indisponível, usando lista padrão:', error.message);
    return [
      { sigla: 'RJ', nome: 'Rio de Janeiro' },
      { sigla: 'SP', nome: 'São Paulo' }
    ];
  }
};

export default {
  getDadosAlerta,
  getPrevisaoChuvas,
  getPrevisaoAlagamentos,
  getHistoricoChuvas,
  getHistoricoAlagamentos,
  getMunicipios,
  getEstados
};