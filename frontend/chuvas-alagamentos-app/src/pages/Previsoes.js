import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, CircularProgress, Tabs, Tab } from '@mui/material';
import { getPrevisaoChuvas, getPrevisaoAlagamentos } from '../services/alertaService';

const Previsoes = () => {
  const [tab, setTab] = useState(0);
  const [chuvas, setChuvas] = useState(null);
  const [alagamentos, setAlagamentos] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cidade, setCidade] = useState('Rio de Janeiro');
  const [estado, setEstado] = useState('RJ');

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
      <Typography variant="h4" component="h1" gutterBottom>
        Previsões para {cidade} - {estado}
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tab} onChange={handleChangeTab}>
          <Tab label="Chuvas" />
          <Tab label="Alagamentos" />
        </Tabs>
      </Box>

      {tab === 0 && (
        <Box>
          <Typography variant="h5" gutterBottom>
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
                              previsao.precipitacao >= 15 ? '#fff8e1' : '#e8f5e9'
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
          <Typography variant="h5" gutterBottom>
            Previsão de Alagamentos
          </Typography>
          
          {alagamentos ? (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper sx={{ p: 3, bgcolor: 
                  alagamentos.nivelRisco === 'alto' ? '#ffebee' : 
                  alagamentos.nivelRisco === 'médio' ? '#fff8e1' : '#e8f5e9' 
                }}>
                  <Typography variant="h6" gutterBottom>
                    Nível de risco: {alagamentos.nivelRisco.toUpperCase()}
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    Probabilidade de alagamentos: {(alagamentos.probabilidade * 100).toFixed(0)}%
                  </Typography>
                </Paper>
              </Grid>
              
              {alagamentos.areasAfetadas && alagamentos.areasAfetadas.length > 0 && (
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 3 }}>
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
                <Paper sx={{ p: 3 }}>
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