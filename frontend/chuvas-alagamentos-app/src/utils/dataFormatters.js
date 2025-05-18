/**
 * Utilitários para formatação de dados
 */

// Formata data para exibição (DD/MM/YYYY)
export const formatarData = (data) => {
  if (!data) return '';
  
  if (typeof data === 'string') {
    const dataObj = new Date(data);
    return dataObj.toLocaleDateString('pt-BR');
  }
  
  return data.toLocaleDateString('pt-BR');
};

// Formata data para exibição com hora (DD/MM/YYYY HH:MM)
export const formatarDataHora = (data) => {
  if (!data) return '';
  
  if (typeof data === 'string') {
    const dataObj = new Date(data);
    return `${dataObj.toLocaleDateString('pt-BR')} ${dataObj.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`;
  }
  
  return `${data.toLocaleDateString('pt-BR')} ${data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`;
};

// Formata data para envio à API (YYYY-MM-DD)
export const formatarDataAPI = (data) => {
  if (!data) return '';
  
  if (typeof data === 'string') {
    const dataObj = new Date(data);
    return dataObj.toISOString().split('T')[0];
  }
  
  return data.toISOString().split('T')[0];
};

// Formata valor de precipitação (mm)
export const formatarPrecipitacao = (valor) => {
  if (valor === null || valor === undefined) return '-';
  return `${valor.toFixed(1)} mm`;
};

// Formata probabilidade (%)
export const formatarProbabilidade = (valor) => {
  if (valor === null || valor === undefined) return '-';
  return `${Math.round(valor * 100)}%`;
};

// Formata nível de alerta
export const formatarNivelAlerta = (nivel) => {
  switch (nivel) {
    case 0:
      return 'Normal';
    case 1:
      return 'Atenção';
    case 2:
      return 'Alerta';
    case 3:
      return 'Emergência';
    default:
      return 'Desconhecido';
  }
};

// Retorna cor para nível de alerta
export const corNivelAlerta = (nivel) => {
  switch (nivel) {
    case 0:
      return '#4caf50'; // Verde
    case 1:
      return '#ff9800'; // Laranja
    case 2:
      return '#f44336'; // Vermelho
    case 3:
      return '#9c27b0'; // Roxo
    default:
      return '#9e9e9e'; // Cinza
  }
};

export default {
  formatarData,
  formatarDataHora,
  formatarDataAPI,
  formatarPrecipitacao,
  formatarProbabilidade,
  formatarNivelAlerta,
  corNivelAlerta
}; 