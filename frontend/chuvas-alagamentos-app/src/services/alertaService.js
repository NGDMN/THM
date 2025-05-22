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
  try {
    const response = await axios.get(`${API_URL}/previsao/chuvas`, {
      params: { cidade, estado }
    });
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar previsão de chuvas:', error);
    throw new Error('Não foi possível obter a previsão de chuvas');
  }
};

// Obter previsão de alagamentos
export const getPrevisaoAlagamentos = async (cidade, estado) => {
  try {
    const response = await axios.get(`${API_URL}/previsao/alagamentos`, {
      params: { cidade, estado }
    });
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar previsão de alagamentos:', error);
    throw new Error('Não foi possível obter a previsão de alagamentos');
  }
};

// Obter histórico de chuvas
export const getHistoricoChuvas = async (cidade, estado, dataInicial, dataFinal) => {
  try {
    const response = await axios.get(`${API_URL}/historico/chuvas`, {
      params: { cidade, estado, dataInicial, dataFinal }
    });
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar histórico de chuvas:', error);
    throw new Error('Não foi possível obter o histórico de chuvas');
  }
};

// Obter histórico de alagamentos
export const getHistoricoAlagamentos = async (cidade, estado, dataInicial, dataFinal) => {
  try {
    const response = await axios.get(`${API_URL}/historico/alagamentos`, {
      params: { cidade, estado, dataInicial, dataFinal }
    });
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar histórico de alagamentos:', error);
    throw new Error('Não foi possível obter o histórico de alagamentos');
  }
};

// Obter lista de municípios
export const getMunicipios = async (estado) => {
  try {
    const response = await axios.get(`${API_URL}/municipios`, {
      params: { estado }
    });
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar municípios:', error);
    throw new Error('Não foi possível obter a lista de municípios');
  }
};

export const getEstados = async () => {
  try {
    const response = await axios.get(`${API_URL}/estados`);
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar estados:', error);
    throw new Error('Não foi possível obter a lista de estados');
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