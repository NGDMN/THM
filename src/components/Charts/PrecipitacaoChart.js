import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { meteoService } from '../../services/api';

// Registrar os componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const PrecipitacaoChart = ({ cidade, estado, dias = 7 }) => {
  const [dadosPrevisao, setDadosPrevisao] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDadosPrevisao = async () => {
      try {
        setIsLoading(true);
        const data = await meteoService.getPrevisaoChuvas(cidade, estado);
        setDadosPrevisao(data);
        setIsLoading(false);
      } catch (err) {
        console.error('Erro ao carregar dados de previsão:', err);
        setError('Não foi possível carregar os dados de previsão. Tente novamente mais tarde.');
        setIsLoading(false);
      }
    };

    fetchDadosPrevisao();
  }, [cidade, estado, dias]);

  if (isLoading) {
    return <div>Carregando gráfico...</div>;
  }

  if (error) {
    return <div>Erro: {error}</div>;
  }

  if (!dadosPrevisao || !dadosPrevisao.length) {
    return <div>Não há dados de previsão disponíveis.</div>;
  }

  // Preparar dados para o gráfico
  const labels = dadosPrevisao.map(d => new Date(d.data).toLocaleDateString('pt-BR'));
  const precipitacoes = dadosPrevisao.map(d => d.precipitacao);
  
  // Definir limites para cores de alerta
  const alertaAlto = 50; // mm - chuva muito forte
  const alertaMedio = 25; // mm - chuva moderada

  // Gerar array de cores baseado nos valores de precipitação
  const backgroundColors = precipitacoes.map(valor => {
    if (valor >= alertaAlto) return 'rgba(255, 0, 0, 0.2)'; // Vermelho para alerta alto
    if (valor >= alertaMedio) return 'rgba(255, 165, 0, 0.2)'; // Laranja para alerta médio
    return 'rgba(53, 162, 235, 0.2)'; // Azul para normal
  });

  const borderColors = precipitacoes.map(valor => {
    if (valor >= alertaAlto) return 'rgb(255, 0, 0)';
    if (valor >= alertaMedio) return 'rgb(255, 165, 0)';
    return 'rgb(53, 162, 235)';
  });

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Precipitação (mm)',
        data: precipitacoes,
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `Previsão de Precipitação - ${cidade}/${estado}`,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const valor = context.parsed.y;
            let label = `Precipitação: ${valor} mm`;
            
            if (valor >= alertaAlto) {
              label += ' - Risco Alto de Alagamento';
            } else if (valor >= alertaMedio) {
              label += ' - Risco Médio de Alagamento';
            }
            
            return label;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Precipitação (mm)'
        },
        ticks: {
          callback: function(value) {
            return `${value} mm`;
          }
        }
      },
      x: {
        title: {
          display: true,
          text: 'Data'
        }
      }
    }
  };

  return (
    <div className="chart-container">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default PrecipitacaoChart; 