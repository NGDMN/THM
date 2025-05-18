import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, CircularProgress, Tabs, Tab } from '@mui/material';
import { getPrevisaoChuvas, getPrevisaoAlagamentos } from '../services/alertaService';

const Previsoes = () => {
  const [tab, setTab] = useState(0);
  const [chuvas, setChuvas] = useState(null);
  const [alagamentos, setAlagamentos] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Por enquanto, usando Rio de Janeiro como padrão
        const dadosChuvas = await getPrevisaoChuvas();
        const dadosAlagamentos = await getPrevisaoAlagamentos();
        
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
  }, []);

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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Previsões
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
          
          {chuvas ? (
            <Grid container spacing={2}>
              {/* Renderizar dados de chuvas quando disponíveis */}
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography>
                    Dados temporários para simulação. Implemente a visualização real com os dados recebidos da API.
                  </Typography>
                </Paper>
              </Grid>
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
            <Grid container spacing={2}>
              {/* Renderizar dados de alagamentos quando disponíveis */}
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography>
                    Dados temporários para simulação. Implemente a visualização real com os dados recebidos da API.
                  </Typography>
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