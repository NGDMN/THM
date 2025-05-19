import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, CircularProgress, Tabs, Tab, MenuItem, Select, FormControl, InputLabel } from '@mui/material';
import { getPrevisaoChuvas, getPrevisaoAlagamentos } from '../services/alertaService';
import { useNavigate } from 'react-router-dom';

const estados = [
  { sigla: 'RJ', nome: 'Rio de Janeiro' },
  { sigla: 'SP', nome: 'São Paulo' }
];

const cidades = {
  'RJ': [
    'Rio de Janeiro',
    'Niterói',
    'Duque de Caxias',
    'Nova Iguaçu',
    'São Gonçalo'
  ],
  'SP': [
    'São Paulo',
    'Campinas',
    'Santos',
    'Guarulhos',
    'São Bernardo do Campo'
  ]
};

const Previsoes = () => {
  const [tab, setTab] = useState(0);
  const [chuvas, setChuvas] = useState(null);
  const [alagamentos, setAlagamentos] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [estado, setEstado] = useState('RJ');
  const [cidade, setCidade] = useState('Rio de Janeiro');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const dadosChuvas = await getPrevisaoChuvas(cidade, estado);
        const dadosAlagamentos = await getPrevisaoAlagamentos(cidade, estado);
        setChuvas(dadosChuvas);
        setAlagamentos(dadosAlagamentos);
        setError(null);
      } catch (err) {
        console.error('Erro ao carregar previsões:', err);
        setError('Não foi possível carregar as previsões');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [cidade, estado]);

  const handleChangeTab = (event, newValue) => {
    setTab(newValue);
  };

  const handleEstadoChange = (event) => {
    const novoEstado = event.target.value;
    setEstado(novoEstado);
    setCidade(cidades[novoEstado][0]);
  };

  const handleCidadeChange = (event) => {
    setCidade(event.target.value);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  // Função para formatar a data
  const formatarData = (dataString) => {
    const data = new Date(dataString);
    return data.toLocaleDateString('pt-BR');
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ color: '#1B4F72', fontFamily: 'Neue Haas Grotesk, Arial, sans-serif', fontWeight: 700, fontSize: '2.25rem', lineHeight: 1.2 }}>
        Previsões para {cidade} - {estado}
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <FormControl sx={{ minWidth: 180 }}>
          <InputLabel id="estado-label">Estado</InputLabel>
          <Select
            labelId="estado-label"
            value={estado}
            label="Estado"
            onChange={handleEstadoChange}
            sx={{ background: '#F5F9FC', fontFamily: 'Neue Haas Grotesk, Arial, sans-serif' }}
          >
            {estados.map((est) => (
              <MenuItem key={est.sigla} value={est.sigla}>{est.nome}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 220 }}>
          <InputLabel id="cidade-label">Cidade</InputLabel>
          <Select
            labelId="cidade-label"
            value={cidade}
            label="Cidade"
            onChange={handleCidadeChange}
            sx={{ background: '#F5F9FC', fontFamily: 'Neue Haas Grotesk, Arial, sans-serif' }}
          >
            {cidades[estado].map((cid) => (
              <MenuItem key={cid} value={cid}>{cid}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tab} onChange={handleChangeTab}>
          <Tab label="Chuvas" />
          <Tab label="Alagamentos" />
        </Tabs>
      </Box>
      {tab === 0 && (
        <Box>
          <Typography variant="h5" gutterBottom sx={{ color: '#1B4F72', fontFamily: 'Neue Haas Grotesk, Arial, sans-serif', fontWeight: 600 }}>
            Previsão de Chuvas
          </Typography>
          {chuvas && chuvas.length > 0 ? (
            <Grid container spacing={2}>
              {chuvas.map((previsao, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Paper 
                    sx={{ 
                      p: 2, 
                      display: 'flex', 
                      flexDirection: 'column',
                      alignItems: 'center',
                      bgcolor: previsao.precipitacao >= 30 ? '#ffebee' : 
                              previsao.precipitacao >= 15 ? '#fff8e1' : '#e8f5e9',
                      fontFamily: 'Neue Haas Grotesk, Arial, sans-serif'
                    }}
                  >
                    <Typography variant="h6">{formatarData(previsao.data)}</Typography>
                    <Box 
                      sx={{ 
                        mt: 2, 
                        display: 'flex', 
                        flexDirection: 'column',
                        alignItems: 'center'
                      }}
                    >
                      <Typography variant="h4" color="text.secondary">
                        {previsao.precipitacao} mm
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        {previsao.precipitacao >= 30 ? 'Risco de alagamento' : 
                        previsao.precipitacao >= 15 ? 'Chuva moderada' : 'Chuva leve/sem chuva'}
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Alert severity="info">Nenhum dado de previsão disponível</Alert>
          )}
        </Box>
      )}
      {tab === 1 && (
        <Box>
          <Typography variant="h5" gutterBottom sx={{ color: '#1B4F72', fontFamily: 'Neue Haas Grotesk, Arial, sans-serif', fontWeight: 600 }}>
            Previsão de Alagamentos
          </Typography>
          {alagamentos ? (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper sx={{ p: 3, bgcolor: 
                  alagamentos.nivelRisco === 'alto' ? '#ffebee' : 
                  alagamentos.nivelRisco === 'médio' ? '#fff8e1' : '#e8f5e9',
                  fontFamily: 'Neue Haas Grotesk, Arial, sans-serif',
                  display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <Typography variant="h6" gutterBottom>
                    Nível de risco: {alagamentos.nivelRisco.toUpperCase()}
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    Probabilidade de alagamentos: {(alagamentos.probabilidade * 100).toFixed(0)}%
                  </Typography>
                  {(alagamentos.nivelRisco === 'alto' || alagamentos.nivelRisco === 'médio') && (
                    <Box sx={{ mt: 2 }}>
                      <button
                        style={{
                          background: '#CB6D51',
                          color: '#fff',
                          border: 'none',
                          borderRadius: 6,
                          padding: '0.75rem 1.5rem',
                          fontWeight: 700,
                          fontFamily: 'Neue Haas Grotesk, Arial, sans-serif',
                          fontSize: '1rem',
                          cursor: 'pointer',
                          boxShadow: '0 2px 8px rgba(203,109,81,0.08)',
                          transition: 'background 0.2s',
                        }}
                        onClick={() => navigate('/recomendacoes')}
                      >
                        Ver Recomendações
                      </button>
                    </Box>
                  )}
                </Paper>
              </Grid>
              {alagamentos.areasAfetadas && alagamentos.areasAfetadas.length > 0 && (
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 3, fontFamily: 'Neue Haas Grotesk, Arial, sans-serif' }}>
                    <Typography variant="h6" gutterBottom>
                      Áreas com histórico de alagamentos
                    </Typography>
                    <ul>
                      {alagamentos.areasAfetadas.map((area, index) => (
                        <li key={index}>
                          <Typography variant="body1">{area}</Typography>
                        </li>
                      ))}
                    </ul>
                  </Paper>
                </Grid>
              )}
              <Grid item xs={12} md={alagamentos.areasAfetadas && alagamentos.areasAfetadas.length > 0 ? 6 : 12}>
                <Paper sx={{ p: 3, fontFamily: 'Neue Haas Grotesk, Arial, sans-serif' }}>
                  <Typography variant="h6" gutterBottom>
                    Recomendações
                  </Typography>
                  <ul>
                    {alagamentos.recomendacoes.map((recomendacao, index) => (
                      <li key={index}>
                        <Typography variant="body1">{recomendacao}</Typography>
                      </li>
                    ))}
                  </ul>
                </Paper>
              </Grid>
            </Grid>
          ) : (
            <Alert severity="info">Nenhum dado de previsão disponível</Alert>
          )}
        </Box>
      )}
    </Container>
  );
};

export default Previsoes; 