import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, CircularProgress, Tabs, Tab, TextField, Button } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import ptBR from 'date-fns/locale/pt-BR';
import { getHistoricoChuvas, getHistoricoAlagamentos } from '../services/alertaService';
import { format } from 'date-fns';

// Componente para gráfico de linha simples
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Historico = () => {
  const [tab, setTab] = useState(0);
  const [dadosChuvas, setDadosChuvas] = useState([]);
  const [dadosAlagamentos, setDadosAlagamentos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Parâmetros de busca
  const [cidade, setCidade] = useState('Rio de Janeiro');
  const [estado, setEstado] = useState('RJ');
  const [dataInicio, setDataInicio] = useState(new Date(new Date().setMonth(new Date().getMonth() - 1)));
  const [dataFim, setDataFim] = useState(new Date());

  // Carregar dados quando os parâmetros mudam
  const handleBuscar = async () => {
    try {
      setLoading(true);
      
      // Formatar datas para API
      const dataInicioFormatada = format(dataInicio, 'yyyy-MM-dd');
      const dataFimFormatada = format(dataFim, 'yyyy-MM-dd');
      
      // Buscar dados
      if (tab === 0) {
        const dados = await getHistoricoChuvas(cidade, estado, dataInicioFormatada, dataFimFormatada);
        setDadosChuvas(dados);
      } else {
        const dados = await getHistoricoAlagamentos(cidade, estado, dataInicioFormatada, dataFimFormatada);
        setDadosAlagamentos(dados);
      }
      
      setError(null);
    } catch (err) {
      console.error('Erro ao carregar histórico:', err);
      setError('Não foi possível carregar os dados históricos');
    } finally {
      setLoading(false);
    }
  };

  // Mudar aba
  const handleChangeTab = (event, newValue) => {
    setTab(newValue);
  };

  // Calcular média e total de chuvas
  const calcularEstatisticas = () => {
    if (!dadosChuvas || dadosChuvas.length === 0) {
      return { total: 0, media: 0, maxima: 0 };
    }
    
    const total = dadosChuvas.reduce((soma, item) => soma + item.precipitacao, 0);
    const media = total / dadosChuvas.length;
    const maxima = Math.max(...dadosChuvas.map(item => item.precipitacao));
    
    return {
      total: parseFloat(total.toFixed(1)),
      media: parseFloat(media.toFixed(1)),
      maxima: parseFloat(maxima.toFixed(1))
    };
  };

  const estatisticasChuvas = calcularEstatisticas();

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
      
      {/* Filtros comuns */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <TextField
              label="Cidade"
              value={cidade}
              onChange={(e) => setCidade(e.target.value)}
              fullWidth
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <TextField
              label="Estado"
              value={estado}
              onChange={(e) => setEstado(e.target.value)}
              fullWidth
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ptBR}>
              <DatePicker
                label="Data Início"
                value={dataInicio}
                onChange={(newValue) => setDataInicio(newValue)}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} sm={3}>
            <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ptBR}>
              <DatePicker
                label="Data Fim"
                value={dataFim}
                onChange={(newValue) => setDataFim(newValue)}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} sm={1}>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleBuscar}
              disabled={loading}
              fullWidth
            >
              Buscar
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>
      )}
      
      {tab === 0 && !loading && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Histórico de Chuvas - {cidade}/{estado}
          </Typography>
          
          {dadosChuvas && dadosChuvas.length > 0 ? (
            <>
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={4}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6" gutterBottom>Total</Typography>
                    <Typography variant="h4">{estatisticasChuvas.total} mm</Typography>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} sm={4}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6" gutterBottom>Média Diária</Typography>
                    <Typography variant="h4">{estatisticasChuvas.media} mm</Typography>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} sm={4}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6" gutterBottom>Máxima</Typography>
                    <Typography variant="h4">{estatisticasChuvas.maxima} mm</Typography>
                  </Paper>
                </Grid>
              </Grid>
              
              <Paper sx={{ p: 2, mb: 3 }}>
                <Typography variant="h6" gutterBottom>Precipitação Diária (mm)</Typography>
                <Box sx={{ height: 400 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={dadosChuvas}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="data" 
                        tickFormatter={(tick) => {
                          const date = new Date(tick);
                          return `${date.getDate()}/${date.getMonth() + 1}`;
                        }}
                      />
                      <YAxis />
                      <Tooltip 
                        formatter={(value) => [`${value} mm`, 'Precipitação']}
                        labelFormatter={(label) => {
                          const date = new Date(label);
                          return format(date, 'dd/MM/yyyy');
                        }}
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="precipitacao" 
                        stroke="#1976d2" 
                        name="Precipitação (mm)" 
                        activeDot={{ r: 8 }} 
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            </>
          ) : (
            <Alert severity="info">Nenhum dado encontrado para o período selecionado</Alert>
          )}
        </Box>
      )}
      
      {tab === 1 && !loading && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Histórico de Alagamentos - {cidade}/{estado}
          </Typography>
          
          {dadosAlagamentos && dadosAlagamentos.length > 0 ? (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Ocorrências Registradas: {dadosAlagamentos.length}
                  </Typography>
                  
                  {dadosAlagamentos.map((alagamento, index) => (
                    <Paper 
                      key={index} 
                      sx={{ 
                        p: 2, 
                        my: 2, 
                        bgcolor: 
                          alagamento.nivelGravidade === 'alto' ? '#ffebee' : 
                          alagamento.nivelGravidade === 'médio' ? '#fff8e1' : '#e8f5e9'
                      }}
                    >
                      <Typography variant="h6">
                        {new Date(alagamento.data).toLocaleDateString('pt-BR')}
                      </Typography>
                      <Typography variant="body1">
                        Local: {alagamento.local}
                      </Typography>
                      <Typography variant="body2">
                        Nível de gravidade: {alagamento.nivelGravidade.toUpperCase()}
                      </Typography>
                      <Typography variant="body2">
                        Pessoas afetadas: {alagamento.afetados}
                      </Typography>
                    </Paper>
                  ))}
                </Paper>
              </Grid>
            </Grid>
          ) : (
            <Alert severity="info">Nenhum alagamento registrado para o período selecionado</Alert>
          )}
        </Box>
      )}
    </Container>
  );
};

export default Historico; 