import React from 'react';
import { Container, Typography, Box, Button, Grid, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import TimelineIcon from '@mui/icons-material/Timeline';

const Home = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <WaterDropIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
        <Typography variant="h3" component="h1" gutterBottom>
          Sistema de Alerta de Chuvas
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Monitoramento e alertas de chuvas e alagamentos em tempo real
        </Typography>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Paper 
            sx={{ 
              p: 3, 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              '&:hover': {
                boxShadow: 6,
                transform: 'translateY(-4px)',
                transition: 'all 0.3s ease-in-out'
              }
            }}
          >
            <WaterDropIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Previsões
            </Typography>
            <Typography variant="body1" paragraph>
              Acompanhe as previsões de chuvas e riscos de alagamento para sua região
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate('/previsoes')}
              sx={{ mt: 'auto' }}
            >
              Ver Previsões
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper 
            sx={{ 
              p: 3, 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              '&:hover': {
                boxShadow: 6,
                transform: 'translateY(-4px)',
                transition: 'all 0.3s ease-in-out'
              }
            }}
          >
            <TimelineIcon sx={{ fontSize: 60, color: 'secondary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Histórico
            </Typography>
            <Typography variant="body1" paragraph>
              Consulte dados históricos de precipitação e ocorrências de alagamentos
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate('/historico')}
              sx={{ mt: 'auto' }}
            >
              Ver Histórico
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper 
            sx={{ 
              p: 3, 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              '&:hover': {
                boxShadow: 6,
                transform: 'translateY(-4px)',
                transition: 'all 0.3s ease-in-out'
              }
            }}
          >
            <WarningAmberIcon sx={{ fontSize: 60, color: 'warning.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Alertas
            </Typography>
            <Typography variant="body1" paragraph>
              Receba alertas sobre riscos de alagamento em sua região
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate('/previsoes')}
              sx={{ mt: 'auto' }}
            >
              Ver Alertas
            </Button>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mt: 6, textAlign: 'center' }}>
        <Typography variant="h5" gutterBottom>
          Sobre o Sistema
        </Typography>
        <Typography variant="body1" paragraph>
          O Sistema de Alerta de Chuvas é uma plataforma desenvolvida para monitorar e alertar sobre
          condições meteorológicas e riscos de alagamentos em diferentes regiões do Brasil.
        </Typography>
        <Button
          variant="outlined"
          onClick={() => navigate('/sobre')}
        >
          Saiba Mais
        </Button>
      </Box>
    </Container>
  );
};

export default Home; 