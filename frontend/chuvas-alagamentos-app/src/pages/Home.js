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
        Monitoramento inteligente de chuvas e alagamentos nas regiões metropolitanas do Rio de Janeiro e São Paulo.
      </Typography>
      <Box sx={{ mb: 4, background: 'background.default', borderRadius: 2, p: 3, boxShadow: 1 }}>
        <Typography variant="h5" sx={{ color: 'secondary.main', mb: 2 }}>
          Sobre o Projeto
        </Typography>
        <Typography sx={{ mb: 2 }}>
          Este sistema utiliza dados meteorológicos históricos e em tempo real para prever chuvas intensas e riscos de alagamento em municípios do RJ e SP. A metodologia combina análise estatística, integração com APIs de clima e histórico de ocorrências para gerar alertas e recomendações.
        </Typography>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Metodologia
        </Typography>
        <ul style={{ marginLeft: '1.5rem', marginBottom: '1.5rem' }}>
          <li>Coleta de dados meteorológicos e históricos de alagamentos</li>
          <li>Análise de padrões de precipitação e identificação de pontos críticos</li>
          <li>Previsão de chuvas para os próximos 5 dias por município</li>
          <li>Classificação do risco de alagamento (baixo, médio, alto)</li>
          <li>Geração de recomendações baseadas em protocolos da Defesa Civil</li>
        </ul>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Como usar
        </Typography>
        <ul style={{ marginLeft: '1.5rem' }}>
          <li>Acesse <b>Previsões</b> para consultar chuvas e riscos por cidade</li>
          <li>Consulte o <b>Histórico</b> para ver dados passados de chuvas e alagamentos</li>
          <li>Em caso de alerta, siga as <b>Recomendações</b> exibidas no sistema</li>
        </ul>
      </Box>

      {alerta && alerta.nivel > 0 && (
        <Alert 
          severity={alerta.nivel > 2 ? "error" : "warning"} 
          sx={{ my: 2 }}
        >
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
      </Grid>
    </Container>
  );
};

export default Home; 