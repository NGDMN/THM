import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { alagamentoService } from '../../services/api';
import L from 'leaflet';

// Corrigir o problema do ícone padrão do Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

// Definir cores para níveis de risco
const getRiskColor = (riskLevel) => {
  switch (riskLevel) {
    case 'alto':
      return '#ff0000'; // vermelho
    case 'médio':
      return '#ff9900'; // laranja 
    case 'baixo':
      return '#ffff00'; // amarelo
    default:
      return '#00ff00'; // verde
  }
};

const AlagamentoMap = ({ cidade, estado }) => {
  const [pontosAlagamento, setPontosAlagamento] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Estado do Brasil para centralizar o mapa (caso não haja cidade/estado específico)
  const posicaoPadrao = [-22.9068, -43.1729]; // Rio de Janeiro
  
  // Carregar pontos de alagamento
  useEffect(() => {
    const fetchPontosAlagamento = async () => {
      try {
        setIsLoading(true);
        const data = await alagamentoService.getPontosAlagamento(cidade, estado);
        setPontosAlagamento(data);
        setIsLoading(false);
      } catch (err) {
        console.error('Erro ao carregar pontos de alagamento:', err);
        setError('Não foi possível carregar os pontos de alagamento. Tente novamente mais tarde.');
        setIsLoading(false);
      }
    };
    
    fetchPontosAlagamento();
  }, [cidade, estado]);
  
  if (isLoading) {
    return <div>Carregando mapa...</div>;
  }
  
  if (error) {
    return <div>Erro: {error}</div>;
  }
  
  return (
    <div className="map-container" style={{ height: '500px', width: '100%' }}>
      <MapContainer 
        center={posicaoPadrao} 
        zoom={11} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {pontosAlagamento.map((ponto, index) => (
          <React.Fragment key={index}>
            <Marker 
              position={[ponto.latitude, ponto.longitude]}
            >
              <Popup>
                <div>
                  <h3>{ponto.local}</h3>
                  <p>Nível de risco: {ponto.nivelRisco}</p>
                  <p>Precipitação prevista: {ponto.precipitacaoPrevista} mm</p>
                  {ponto.ultimoAlagamento && (
                    <p>Último alagamento: {new Date(ponto.ultimoAlagamento).toLocaleDateString()}</p>
                  )}
                </div>
              </Popup>
            </Marker>
            
            {/* Círculo para representar a área de risco */}
            <Circle
              center={[ponto.latitude, ponto.longitude]}
              radius={ponto.raioAfetado || 300}
              pathOptions={{
                fillColor: getRiskColor(ponto.nivelRisco),
                fillOpacity: 0.3,
                color: getRiskColor(ponto.nivelRisco),
                weight: 1
              }}
            />
          </React.Fragment>
        ))}
      </MapContainer>
    </div>
  );
};

export default AlagamentoMap; 