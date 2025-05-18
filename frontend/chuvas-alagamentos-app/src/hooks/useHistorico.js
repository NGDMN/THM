import { useState, useCallback } from 'react';
import { getHistoricoChuvas, getHistoricoAlagamentos } from '../services/alertaService';

// Hook para gerenciar dados históricos
const useHistorico = () => {
  const [dadosChuvas, setDadosChuvas] = useState([]);
  const [dadosAlagamentos, setDadosAlagamentos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Carregar histórico de chuvas
  const carregarHistoricoChuvas = useCallback(async (dataInicio, dataFim) => {
    try {
      setLoading(true);
      const dados = await getHistoricoChuvas(dataInicio, dataFim);
      setDadosChuvas(dados);
      setError(null);
      return dados;
    } catch (err) {
      console.error('Erro ao carregar histórico de chuvas:', err);
      setError('Não foi possível carregar o histórico de chuvas');
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Carregar histórico de alagamentos
  const carregarHistoricoAlagamentos = useCallback(async (dataInicio, dataFim) => {
    try {
      setLoading(true);
      const dados = await getHistoricoAlagamentos(dataInicio, dataFim);
      setDadosAlagamentos(dados);
      setError(null);
      return dados;
    } catch (err) {
      console.error('Erro ao carregar histórico de alagamentos:', err);
      setError('Não foi possível carregar o histórico de alagamentos');
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Carregar ambos os históricos
  const carregarHistorico = useCallback(async (dataInicio, dataFim) => {
    try {
      setLoading(true);
      const [chuvas, alagamentos] = await Promise.all([
        getHistoricoChuvas(dataInicio, dataFim),
        getHistoricoAlagamentos(dataInicio, dataFim)
      ]);
      
      setDadosChuvas(chuvas);
      setDadosAlagamentos(alagamentos);
      setError(null);
      
      return { chuvas, alagamentos };
    } catch (err) {
      console.error('Erro ao carregar histórico:', err);
      setError('Não foi possível carregar os dados históricos');
      return { chuvas: [], alagamentos: [] };
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    dadosChuvas,
    dadosAlagamentos,
    loading,
    error,
    carregarHistoricoChuvas,
    carregarHistoricoAlagamentos,
    carregarHistorico
  };
};

export default useHistorico; 