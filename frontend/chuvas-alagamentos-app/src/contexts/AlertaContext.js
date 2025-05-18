import React, { createContext, useState, useEffect, useContext } from 'react';
import { getDadosAlerta } from '../services/alertaService';

// Criando o contexto
const AlertaContext = createContext();

// Hook personalizado para usar o contexto
export const useAlerta = () => useContext(AlertaContext);

// Provedor de contexto
export const AlertaProvider = ({ children }) => {
  const [alerta, setAlerta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Função para buscar dados atualizados
  const atualizarDadosAlerta = async () => {
    try {
      setLoading(true);
      const dados = await getDadosAlerta();
      setAlerta(dados);
      setError(null);
    } catch (err) {
      console.error('Erro ao carregar dados de alerta:', err);
      setError('Falha ao carregar informações de alerta');
    } finally {
      setLoading(false);
    }
  };

  // Carregar dados ao iniciar
  useEffect(() => {
    atualizarDadosAlerta();

    // Atualizar dados a cada 5 minutos
    const intervalo = setInterval(() => {
      atualizarDadosAlerta();
    }, 5 * 60 * 1000);

    return () => clearInterval(intervalo);
  }, []);

  // Valores a serem disponibilizados pelo contexto
  const value = {
    alerta,
    loading,
    error,
    atualizarDadosAlerta,
  };

  return (
    <AlertaContext.Provider value={value}>
      {children}
    </AlertaContext.Provider>
  );
};

export default AlertaContext; 