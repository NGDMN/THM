import axios from 'axios';
import { mockPrevisaoChuvas, mockPontosAlagamento, mockPrevisaoAlagamentos } from './mockData';

// Definir a URL base da API
const API_URL = 'https://thm-api.onrender.com/api';

// Flag para usar dados mock (desenvolvimento) ou API real (produção)
const USE_MOCK_DATA = false;

// Criar instância do axios com configuração base
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Serviços para obter dados meteorológicos
export const meteoService = {
  // Obter previsão de chuvas para os próximos dias
  getPrevisaoChuvas: async (cidade, estado) => {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          if (mockPrevisaoChuvas[estado] && mockPrevisaoChuvas[estado][cidade]) {
            resolve(mockPrevisaoChuvas[estado][cidade]);
          } else {
            // Fallback para Rio de Janeiro se a cidade não estiver nos mocks
            resolve(mockPrevisaoChuvas['RJ']['Rio de Janeiro']);
          }
        }, 500); // Simular tempo de resposta da API
      });
    }
    
    try {
      const response = await api.get(`/previsao/chuvas`, {
        params: { cidade, estado }
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao obter previsão de chuvas:', error);
      throw error;
    }
  },
  
  // Obter dados históricos de chuvas
  getDadosHistoricos: async (cidade, estado, dataInicio, dataFim) => {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          // Gerar dados históricos aleatórios
          const dadosHistoricos = [];
          const startDate = new Date(dataInicio);
          const endDate = new Date(dataFim);
          
          for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
            dadosHistoricos.push({
              data: new Date(d).toISOString().split('T')[0],
              precipitacao: Math.random() * 100
            });
          }
          
          resolve(dadosHistoricos);
        }, 700);
      });
    }
    
    try {
      const response = await api.get(`/historico/chuvas`, {
        params: { cidade, estado, dataInicio, dataFim }
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao obter dados históricos:', error);
      throw error;
    }
  }
};

// Serviços para obter dados de alagamentos
export const alagamentoService = {
  // Obter previsão de risco de alagamentos
  getPrevisaoAlagamentos: async (cidade, estado) => {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          if (mockPrevisaoAlagamentos[estado] && mockPrevisaoAlagamentos[estado][cidade]) {
            resolve(mockPrevisaoAlagamentos[estado][cidade]);
          } else {
            // Fallback para Rio de Janeiro se a cidade não estiver nos mocks
            resolve(mockPrevisaoAlagamentos['RJ']['Rio de Janeiro']);
          }
        }, 600);
      });
    }
    
    try {
      const response = await api.get(`/previsao/alagamentos`, {
        params: { cidade, estado }
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao obter previsão de alagamentos:', error);
      throw error;
    }
  },
  
  // Obter dados históricos de alagamentos
  getDadosHistoricos: async (cidade, estado, dataInicio, dataFim) => {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          // Gerar dados históricos aleatórios
          const dadosHistoricos = [];
          const startDate = new Date(dataInicio);
          const endDate = new Date(dataFim);
          
          for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 15)) {
            if (Math.random() > 0.7) { // 30% de chance de ter ocorrido um alagamento
              dadosHistoricos.push({
                data: new Date(d).toISOString().split('T')[0],
                local: 'Área central',
                nivelGravidade: Math.random() > 0.5 ? 'alto' : 'médio',
                afetados: Math.floor(Math.random() * 1000)
              });
            }
          }
          
          resolve(dadosHistoricos);
        }, 800);
      });
    }
    
    try {
      const response = await api.get(`/historico/alagamentos`, {
        params: { cidade, estado, dataInicio, dataFim }
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao obter histórico de alagamentos:', error);
      throw error;
    }
  },
  
  // Obter pontos de alagamento em um mapa
  getPontosAlagamento: async (cidade, estado) => {
    if (USE_MOCK_DATA) {
      return new Promise((resolve) => {
        setTimeout(() => {
          if (mockPontosAlagamento[estado] && mockPontosAlagamento[estado][cidade]) {
            resolve(mockPontosAlagamento[estado][cidade]);
          } else {
            // Fallback para Rio de Janeiro se a cidade não estiver nos mocks
            resolve(mockPontosAlagamento['RJ']['Rio de Janeiro']);
          }
        }, 550);
      });
    }
    
    try {
      const response = await api.get(`/pontos/alagamentos`, {
        params: { cidade, estado }
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao obter pontos de alagamento:', error);
      throw error;
    }
  }
};

export default api; 