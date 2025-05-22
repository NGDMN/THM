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
export const getPrevisaoChuvas = async (cidade, estado, dias = 7) => {
  try {
    if (!cidade || !estado) {
      throw new Error('Cidade e estado são obrigatórios');
    }

    console.log('Buscando previsão de chuvas:', { cidade, estado, dias });
    const response = await axios.get(
      `${API_URL}/previsao/chuvas?cidade=${encodeURIComponent(cidade)}&estado=${encodeURIComponent(estado)}&dias=${dias}`
    );
    console.log('Resposta da API (chuvas):', response.data);
    return validarResposta(response.data, 'chuvas');
  } catch (error) {
    console.error('Erro ao buscar previsão de chuvas:', error);
    throw new Error(error.response?.data?.message || 'Erro ao buscar previsão de chuvas');
  }
};

// Obter previsão de alagamentos
export const getPrevisaoAlagamentos = async (cidade, estado, dias = 7) => {
  try {
    if (!cidade || !estado) {
      throw new Error('Cidade e estado são obrigatórios');
    }

    console.log('Buscando previsão de alagamentos:', { cidade, estado, dias });
    const response = await axios.get(
      `${API_URL}/previsao/alagamentos?cidade=${encodeURIComponent(cidade)}&estado=${encodeURIComponent(estado)}&dias=${dias}`
    );
    console.log('Resposta da API (alagamentos):', response.data);
    return validarResposta(response.data, 'alagamentos');
  } catch (error) {
    console.error('Erro ao buscar previsão de alagamentos:', error);
    throw new Error(error.response?.data?.message || 'Erro ao buscar previsão de alagamentos');
  }
};

// Obter histórico de chuvas
export const getHistoricoChuvas = async (cidade, estado, inicio, fim) => {
  try {
    if (!cidade || !estado) {
      throw new Error('Cidade e estado são obrigatórios');
    }

    const params = new URLSearchParams();
    params.append('cidade', cidade);
    params.append('estado', estado);
    if (inicio) params.append('dataInicio', inicio);
    if (fim) params.append('dataFim', fim);
    
    console.log('Buscando histórico de chuvas:', { cidade, estado, inicio, fim });
    const response = await axios.get(`${API_URL}/historico/chuvas?${params.toString()}`);
    console.log('Resposta da API (histórico chuvas):', response.data);
    return validarResposta(response.data, 'chuvas');
  } catch (error) {
    console.error('Erro ao buscar histórico de chuvas:', error);
    throw new Error(error.response?.data?.message || 'Erro ao buscar histórico de chuvas');
  }
};

// Obter histórico de alagamentos
export const getHistoricoAlagamentos = async (cidade, estado, inicio, fim) => {
  try {
    if (!cidade || !estado) {
      throw new Error('Cidade e estado são obrigatórios');
    }

    const params = new URLSearchParams();
    params.append('cidade', cidade);
    params.append('estado', estado);
    if (inicio) params.append('dataInicio', inicio);
    if (fim) params.append('dataFim', fim);
    
    console.log('Buscando histórico de alagamentos:', { cidade, estado, inicio, fim });
    const response = await axios.get(`${API_URL}/historico/alagamentos?${params.toString()}`);
    console.log('Resposta da API (histórico alagamentos):', response.data);
    return validarResposta(response.data, 'alagamentos');
  } catch (error) {
    console.error('Erro ao buscar histórico de alagamentos:', error);
    throw new Error(error.response?.data?.message || 'Erro ao buscar histórico de alagamentos');
  }
};

// Obter lista de municípios
export const getMunicipios = async () => {
  try {
    console.log('Buscando lista de municípios');
    const response = await axios.get(`${API_URL}/municipios`);
    console.log('Resposta da API (municipios):', response.data);
    return validarResposta(response.data, 'municipios');
  } catch (error) {
    console.error('Erro ao buscar lista de municípios:', error);
    throw new Error(error.response?.data?.message || 'Erro ao buscar lista de municípios');
  }
};

export default {
  getDadosAlerta,
  getPrevisaoChuvas,
  getPrevisaoAlagamentos,
  getHistoricoChuvas,
  getHistoricoAlagamentos,
  getMunicipios
}; 