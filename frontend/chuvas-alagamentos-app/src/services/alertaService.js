import axios from 'axios';

const API_URL = 'https://thm-api.onrender.com/api';

// Cidade e estado padrão para todas as requisições
const CIDADE_PADRAO = 'Rio de Janeiro';
const ESTADO_PADRAO = 'RJ';

// Obter dados de alerta atual
export const getDadosAlerta = async () => {
  try {
    const response = await axios.get(`${API_URL}/previsao/alertas`);
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar dados de alerta:', error);
    throw error;
  }
};

// Obter previsão de chuvas
export const getPrevisaoChuvas = async (dias = 7) => {
  try {
    const response = await axios.get(
      `${API_URL}/previsao/chuvas?cidade=${CIDADE_PADRAO}&estado=${ESTADO_PADRAO}&dias=${dias}`
    );
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar previsão de chuvas:', error);
    throw error;
  }
};

// Obter previsão de alagamentos
export const getPrevisaoAlagamentos = async (dias = 7) => {
  try {
    const response = await axios.get(
      `${API_URL}/previsao/alagamentos?cidade=${CIDADE_PADRAO}&estado=${ESTADO_PADRAO}&dias=${dias}`
    );
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar previsão de alagamentos:', error);
    throw error;
  }
};

// Obter histórico de chuvas
export const getHistoricoChuvas = async (inicio, fim) => {
  try {
    const response = await axios.get(
      `${API_URL}/historico/chuvas?cidade=${CIDADE_PADRAO}&estado=${ESTADO_PADRAO}&dataInicio=${inicio}&dataFim=${fim}`
    );
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar histórico de chuvas:', error);
    throw error;
  }
};

// Obter histórico de alagamentos
export const getHistoricoAlagamentos = async (inicio, fim) => {
  try {
    const response = await axios.get(
      `${API_URL}/historico/alagamentos?cidade=${CIDADE_PADRAO}&estado=${ESTADO_PADRAO}&dataInicio=${inicio}&dataFim=${fim}`
    );
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar histórico de alagamentos:', error);
    throw error;
  }
};

export default {
  getDadosAlerta,
  getPrevisaoChuvas,
  getPrevisaoAlagamentos,
  getHistoricoChuvas,
  getHistoricoAlagamentos
}; 