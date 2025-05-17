import React, { useState } from 'react';
import { Container, Grid, Paper, Typography, FormControl, InputLabel, Select, MenuItem, Box } from '@mui/material';
import AlagamentoMap from '../Map/AlagamentoMap';
import PrecipitacaoChart from '../Charts/PrecipitacaoChart';

// Lista de estados e cidades disponíveis
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

const Dashboard = () => {
  const [estado, setEstado] = useState('RJ');
  const [cidade, setCidade] = useState('Rio de Janeiro');
  
  const handleEstadoChange = (event) => {
    const novoEstado = event.target.value;
    setEstado(novoEstado);
    // Reset cidade para a primeira da lista do novo estado
    setCidade(cidades[novoEstado][0]);
  };
  
  const handleCidadeChange = (event) => {
    setCidade(event.target.value);
  };
  
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Sistema de Monitoramento de Chuvas e Alagamentos
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel id="estado-label">Estado</InputLabel>
            <Select
              labelId="estado-label"
              id="estado-select"
              value={estado}
              label="Estado"
              onChange={handleEstadoChange}
            >
              {estados.map((est) => (
                <MenuItem key={est.sigla} value={est.sigla}>
                  {est.nome}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel id="cidade-label">Cidade</InputLabel>
            <Select
              labelId="cidade-label"
              id="cidade-select"
              value={cidade}
              label="Cidade"
              onChange={handleCidadeChange}
            >
              {cidades[estado].map((cid) => (
                <MenuItem key={cid} value={cid}>
                  {cid}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      
      <Grid container spacing={3}>
        {/* Mapa de Alagamentos */}
        <Grid item xs={12}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 550,
            }}
          >
            <Typography variant="h6" component="h2" gutterBottom>
              Mapa de Pontos de Alagamento - {cidade}/{estado}
            </Typography>
            <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
              <AlagamentoMap cidade={cidade} estado={estado} />
            </Box>
          </Paper>
        </Grid>
        
        {/* Gráfico de Previsão de Chuvas */}
        <Grid item xs={12} md={8}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 400,
            }}
          >
            <Typography variant="h6" component="h2" gutterBottom>
              Previsão de Precipitação - {cidade}/{estado}
            </Typography>
            <Box sx={{ flexGrow: 1 }}>
              <PrecipitacaoChart cidade={cidade} estado={estado} dias={7} />
            </Box>
          </Paper>
        </Grid>
        
        {/* Caixa de Estatísticas */}
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 400,
            }}
          >
            <Typography variant="h6" component="h2" gutterBottom>
              Análise de Risco de Alagamento
            </Typography>
            <Box sx={{ p: 2 }}>
              <Typography variant="h5" component="div" color="error" gutterBottom>
                Alto Risco
              </Typography>
              <Typography variant="body1" paragraph>
                A previsão indica alta probabilidade de alagamentos nas próximas 24-48 horas.
              </Typography>
              <Typography variant="subtitle1" fontWeight="bold">
                Recomendações:
              </Typography>
              <Typography variant="body2" component="ul" sx={{ pl: 2 }}>
                <li>Evite áreas marcadas em vermelho no mapa</li>
                <li>Mantenha-se informado sobre alertas da Defesa Civil</li>
                <li>Tenha um plano de emergência preparado</li>
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 