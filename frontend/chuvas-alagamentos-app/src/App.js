import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [previsoes, setPrevisoes] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    // URL da API - substituir pelo endereço correto após deploy
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    
    const buscarDados = async () => {
      try {
        setCarregando(true);
        // Chamada para API de previsão de alagamentos
        const resposta = await fetch(`${apiUrl}/api/previsao/alagamentos`);
        
        if (!resposta.ok) {
          throw new Error('Erro ao buscar dados da API');
        }
        
        const dados = await resposta.json();
        setPrevisoes(dados);
        setCarregando(false);
      } catch (erro) {
        console.error('Erro:', erro);
        setErro(erro.message);
        setCarregando(false);
      }
    };
    
    buscarDados();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Sistema de Previsão de Alagamentos RJ/SP</h1>
        <p>Monitoramento e previsão de eventos de chuvas e alagamentos</p>
      </header>
      
      <main className="App-content">
        {carregando ? (
          <p>Carregando dados...</p>
        ) : erro ? (
          <div className="erro-container">
            <p>Erro ao carregar dados: {erro}</p>
            <p>Verifique se a API está em execução ou se você está no modo de simulação.</p>
          </div>
        ) : (
          <div className="previsoes-container">
            <h2>Previsão de Alagamentos</h2>
            {previsoes.length === 0 ? (
              <p>Nenhuma previsão disponível no momento.</p>
            ) : (
              <ul className="lista-previsoes">
                {previsoes.map((previsao, index) => (
                  <li key={index} className="item-previsao">
                    <div className="previsao-info">
                      <h3>Região: {previsao.regiao || 'Não informada'}</h3>
                      <p>Data: {previsao.data || 'Não informada'}</p>
                      <p>Probabilidade: {previsao.probabilidade || 'Não informada'}%</p>
                      <p>Intensidade prevista: {previsao.intensidade || 'Não informada'}</p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </main>
      
      <footer className="App-footer">
        <p>Sistema de Previsão de Alagamentos - 2023</p>
      </footer>
    </div>
  );
}

export default App;
