import React, { useState } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, Button, TextField, Tabs, Tab } from '@mui/material';
import { getHistoricoChuvas, getHistoricoAlagamentos } from '../services/alertaService';

const Historico = () => {
  const [tab, setTab] = useState(0);
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');
  const [dados, setDados] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChangeTab = (event, newValue) => {
    setTab(newValue);
    setDados(null); // Limpar dados ao trocar a aba
  };

  const handleBuscar = async () => {
    if (!dataInicio || !dataFim) {
      setError('Por favor, selecione as datas de início e fim');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Buscar dados de acordo com a aba selecionada
      if (tab === 0) {
        const resultado = await getHistoricoChuvas(dataInicio, dataFim);
        setDados(resultado);
      } else {
        const resultado = await getHistoricoAlagamentos(dataInicio, dataFim);
        setDados(resultado);
      }
    } catch (err) {
      console.error('Erro ao buscar histórico:', err);
      setError('Não foi possível carregar os dados históricos');
      setDados(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Histórico
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tab} onChange={handleChangeTab}>
          <Tab label="Chuvas" />
          <Tab label="Alagamentos" />
        </Tabs>
      </Box>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Filtros
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <TextField
              label="Data Início"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={dataInicio}
              onChange={(e) => setDataInicio(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              label="Data Fim"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={dataFim}
              onChange={(e) => setDataFim(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button 
              variant="contained" 
              onClick={handleBuscar}
              disabled={loading}
              fullWidth
            >
              {loading ? 'Carregando...' : 'Buscar'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {dados ? (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Resultados
          </Typography>
          {/* Área para exibição dos resultados */}
          <Box sx={{ mt: 2 }}>
            <Typography>
              Dados temporários para simulação. Implemente a visualização real com os dados recebidos da API.
            </Typography>
          </Box>
        </Paper>
      ) : !loading && !error && (
        <Alert severity="info">
          Selecione um período e clique em Buscar para visualizar o histórico
        </Alert>
      )}
    </Container>
  );
};

export default Historico; 