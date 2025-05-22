import React from 'react';
import { Container, Typography, Paper, Box, Grid } from '@mui/material';
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import TimelineIcon from '@mui/icons-material/Timeline';

const Sobre = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Sobre o Sistema
      </Typography>

      <Paper sx={{ p: 4, mb: 4 }}>
        <Typography variant="body1" paragraph>
          O Sistema de Alerta de Chuvas é uma plataforma desenvolvida para monitorar e alertar sobre
          condições meteorológicas e riscos de alagamentos em diferentes regiões do Brasil.
        </Typography>

        <Grid container spacing={4} sx={{ mt: 2 }}>
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <WaterDropIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Previsões de Chuvas
              </Typography>
              <Typography variant="body2">
                Monitoramento em tempo real das condições meteorológicas,
                fornecendo previsões precisas de precipitação para os próximos dias.
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <WarningAmberIcon sx={{ fontSize: 60, color: 'warning.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Alertas de Alagamentos
              </Typography>
              <Typography variant="body2">
                Sistema de alerta preventivo que identifica áreas com risco
                de alagamento baseado em dados históricos e previsões meteorológicas.
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <TimelineIcon sx={{ fontSize: 60, color: 'secondary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Histórico de Dados
              </Typography>
              <Typography variant="body2">
                Acesso a dados históricos de precipitação e ocorrências de
                alagamentos para análise e planejamento preventivo.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>
          Como Utilizar
        </Typography>
        <Typography variant="body1" paragraph>
          1. Na seção "Previsões", selecione o estado e município desejados para visualizar
          as previsões de chuvas e possíveis riscos de alagamento.
        </Typography>
        <Typography variant="body1" paragraph>
          2. Na seção "Histórico", você pode consultar dados passados de precipitação
          e ocorrências de alagamentos, filtrando por período e localização.
        </Typography>
        <Typography variant="body1">
          O sistema é atualizado constantemente para fornecer informações precisas e
          relevantes para a prevenção de desastres naturais relacionados a chuvas.
        </Typography>
      </Paper>
    </Container>
  );
};

export default Sobre; 