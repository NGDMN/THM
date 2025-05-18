import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { getDadosAlerta } from '../services/alertaService';

const Home = () => {
  const navigate = useNavigate();
  const [alerta, setAlerta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const dados = await getDadosAlerta();
        setAlerta(dados);
        setLoading(false);
      } catch (err) {
        console.error('Erro ao carregar dados:', err);
        setError('Não foi possível carregar os dados de alerta');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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
        Sistema de Previsão de Alagamentos RJ/SP
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Monitoramento em tempo real de chuvas e alagamentos nas regiões metropolitanas do Rio de Janeiro e São Paulo.
      </Typography>

      {alerta && alerta.nivel > 0 && (
        <Alert severity={alerta.nivel > 2 ? "error" : "warning"} sx={{ my: 2 }}>
          {alerta.mensagem}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12} sm={6}>
          <Paper sx={{ p: 3, height: '100%', cursor: 'pointer' }} onClick={() => navigate('/previsoes')}>
            <Typography variant="h5" component="h2" gutterBottom>
              Previsões
            </Typography>
            <Typography>
              Visualize previsões de chuvas e probabilidade de alagamentos para os próximos dias.
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Paper sx={{ p: 3, height: '100%', cursor: 'pointer' }} onClick={() => navigate('/mapa')}>
            <Typography variant="h5" component="h2" gutterBottom>
              Mapa de Ocorrências
            </Typography>
            <Typography>
              Visualize no mapa as ocorrências de alagamentos e precipitações em tempo real.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Home; 