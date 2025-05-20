import axios from 'axios';

const API_URL = 'https://thm-pg0z.onrender.com';

// Obter dados de alerta atual
export const getDadosAlerta = async (cidade, estado) => {
  try {
    const params = {};
    if (cidade) params.cidade = cidade;
    if (estado) params.estado = estado;
    const response = await axios.get(`${API_URL}/previsao/alertas`, { params });
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar dados de alerta:', error);
    throw error;
  }
};

// Obter previsão de chuvas
export const getPrevisaoChuvas = async (cidade, estado, dias = 7) => {
  try {
    const response = await axios.get(
      `${API_URL}/previsao/chuvas?cidade=${cidade}&estado=${estado}&dias=${dias}`
    );
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar previsão de chuvas:', error);
    throw error;
  }
};

// Obter previsão de alagamentos
export const getPrevisaoAlagamentos = async (cidade, estado, dias = 7) => {
  try {
    const response = await axios.get(
      `${API_URL}/previsao/alagamentos?cidade=${cidade}&estado=${estado}&dias=${dias}`
    );
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar previsão de alagamentos:', error);
    throw error;
  }
};

// Obter histórico de chuvas
export const getHistoricoChuvas = async (cidade, estado, inicio, fim) => {
  try {
    const response = await axios.get(
      `${API_URL}/historico/chuvas?cidade=${cidade}&estado=${estado}&dataInicio=${inicio}&dataFim=${fim}`
    );
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar histórico de chuvas:', error);
    throw error;
  }
};

// Obter histórico de alagamentos
export const getHistoricoAlagamentos = async (cidade, estado, inicio, fim) => {
  try {
    const response = await axios.get(
      `${API_URL}/historico/alagamentos?cidade=${cidade}&estado=${estado}&dataInicio=${inicio}&dataFim=${fim}`
    );
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar histórico de alagamentos:', error);
    throw error;
  }
};

// Obter lista de municípios
export const getMunicipios = async () => {
  try {
    const response = await axios.get(`${API_URL}/municipios`);
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar lista de municípios:', error);
    throw error;
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