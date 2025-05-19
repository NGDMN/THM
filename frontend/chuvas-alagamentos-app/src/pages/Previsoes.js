import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, CircularProgress, Tabs, Tab, MenuItem, Select, FormControl, InputLabel, Button } from '@mui/material';
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
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
        >
          {error}
        </Alert>
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
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <FormControl sx={{ minWidth: 180 }}>
          <InputLabel id="estado-label">Estado</InputLabel>
          <Select
            labelId="estado-label"
            value={estado}
            label="Estado"
            onChange={handleEstadoChange}
            sx={{ background: 'background.default' }}
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
            sx={{ background: 'background.default' }}
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
                  bgcolor: previsao.precipitacao >= 30 ? 'error.light' : previsao.precipitacao >= 15 ? 'warning.light' : 'success.light',
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
                    {previsao.precipitacao >= 30 ? 'Risco de alagamento' : previsao.precipitacao >= 15 ? 'Chuva moderada' : 'Chuva leve/sem chuva'}
                  </Typography>
                  {previsao.precipitacao >= 30 && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      Atenção: Risco de alagamento neste dia!
                    </Alert>
                  )}
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      ) : (
        <Alert severity="info">
          Nenhuma previsão disponível para o período selecionado
        </Alert>
      )}
    </Container>
  );
};

export default Previsoes; 