import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, CircularProgress, Tabs, Tab, TextField, Button, MenuItem, Select, FormControl, InputLabel } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import ptBR from 'date-fns/locale/pt-BR';
import { getHistoricoChuvas, getHistoricoAlagamentos, getMunicipios } from '../services/alertaService';
import { format } from 'date-fns';

// Componente para gráfico de linha simples
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const estados = [
  { sigla: 'RJ', nome: 'Rio de Janeiro' },
  { sigla: 'SP', nome: 'São Paulo' }
];

const Historico = () => {
  const [tab, setTab] = useState(0);
  const [chuvas, setChuvas] = useState(null);
  const [alagamentos, setAlagamentos] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [estado, setEstado] = useState('RJ');
  const [cidade, setCidade] = useState('');
  const [municipios, setMunicipios] = useState({});
  const [dataInicio, setDataInicio] = useState(null);
  const [dataFim, setDataFim] = useState(null);

  useEffect(() => {
    const fetchMunicipios = async () => {
      try {
        const dados = await getMunicipios();
        const municipiosPorEstado = dados.reduce((acc, municipio) => {
          if (!acc[municipio.uf]) {
            acc[municipio.uf] = [];
          }
          acc[municipios.uf].push(municipio.nome);
          return acc;
        }, {});
        setMunicipios(municipiosPorEstado);
        if (municipiosPorEstado[estado]?.length > 0) {
          setCidade(municipiosPorEstado[estado][0]);
        }
      } catch (err) {
        console.error('Erro ao carregar municípios:', err);
        setError('Não foi possível carregar a lista de municípios');
      }
    };
    fetchMunicipios();
  }, []);

  const handleBuscar = async () => {
    try {
      setLoading(true);
      setError(null);

      // Validação das datas
      if (dataInicio && dataFim && dataInicio > dataFim) {
        setError('A data inicial não pode ser maior que a data final');
        return;
      }

      const dataInicioFormatada = dataInicio ? format(dataInicio, 'yyyy-MM-dd') : format(new Date('2020-01-01'), 'yyyy-MM-dd');
      const dataFimFormatada = dataFim ? format(dataFim, 'yyyy-MM-dd') : format(new Date(), 'yyyy-MM-dd');
      
      if (tab === 0) {
        const dados = await getHistoricoChuvas(cidade, estado, dataInicioFormatada, dataFimFormatada);
        if (!dados || dados.length === 0) {
          setError('Nenhum dado encontrado para o período selecionado');
          setChuvas([]);
        } else {
          setChuvas(dados);
        }
      } else {
        const dados = await getHistoricoAlagamentos(cidade, estado, dataInicioFormatada, dataFimFormatada);
        if (!dados || dados.length === 0) {
          setError('Nenhum dado encontrado para o período selecionado');
          setAlagamentos([]);
        } else {
          setAlagamentos(dados);
        }
      }
    } catch (err) {
      console.error('Erro ao carregar histórico:', err);
      setError('Não foi possível carregar os dados históricos');
      setChuvas([]);
      setAlagamentos([]);
    } finally {
      setLoading(false);
    }
  };

  const handleChangeTab = (event, newValue) => {
    setTab(newValue);
  };

  const handleEstadoChange = (event) => {
    const novoEstado = event.target.value;
    setEstado(novoEstado);
    if (municipios[novoEstado]?.length > 0) {
      setCidade(municipios[novoEstado][0]);
    }
  };

  const handleCidadeChange = (event) => {
    setCidade(event.target.value);
  };

  const calcularEstatisticas = () => {
    if (!chuvas || chuvas.length === 0) {
      return { total: 0, media: 0, maxima: 0 };
    }
    const total = chuvas.reduce((soma, item) => soma + item.precipitacao, 0);
    const media = total / chuvas.length;
    const maxima = Math.max(...chuvas.map(item => item.precipitacao));
    return {
      total: parseFloat(total.toFixed(1)),
      media: parseFloat(media.toFixed(1)),
      maxima: parseFloat(maxima.toFixed(1))
    };
  };

  const estatisticasChuvas = calcularEstatisticas();

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
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Histórico para {cidade} - {estado}
      </Typography>
      <Box sx={{ mb: 2, background: 'background.default', borderRadius: 2, p: 2 }}>
        O histórico está disponível a partir de <b>01/01/2020</b>. Não há limitação para o intervalo de datas.
      </Box>
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <FormControl sx={{ minWidth: 180 }}>
          <InputLabel id="estado-label">Estado</InputLabel>
          <Select
            labelId="estado-label"
            value={estado}
            label="Estado"
            onChange={handleEstadoChange}
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
          >
            {municipios[estado]?.map((cid) => (
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
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ptBR}>
              <DatePicker
                label="Data Início"
                value={dataInicio}
                onChange={(newValue) => {
                  setDataInicio(newValue);
                }}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    variant: "outlined"
                  }
                }}
                format="dd/MM/yyyy"
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} sm={3}>
            <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ptBR}>
              <DatePicker
                label="Data Fim"
                value={dataFim}
                onChange={(newValue) => {
                  setDataFim(newValue);
                }}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    variant: "outlined"
                  }
                }}
                format="dd/MM/yyyy"
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} sm={2}>
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
      {tab === 0 && !loading && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Histórico de Chuvas - {cidade}/{estado}
          </Typography>
          {chuvas && chuvas.length > 0 ? (
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
                      data={chuvas}
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
            <Alert 
              severity="info"
            >
              Nenhum dado encontrado para o período selecionado
            </Alert>
          )}
        </Box>
      )}
      {tab === 1 && !loading && (
        <Box>
          <Typography variant="h5" gutterBottom sx={{ color: '#1B4F72', fontFamily: 'Neue Haas Grotesk, Arial, sans-serif', fontWeight: 600 }}>
            Histórico de Alagamentos - {cidade}/{estado}
          </Typography>
          {alagamentos && alagamentos.length > 0 ? (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Paper sx={{ p: 2, fontFamily: 'Neue Haas Grotesk, Arial, sans-serif' }}>
                  <Typography variant="h6" gutterBottom>
                    Ocorrências Registradas: {alagamentos.length}
                  </Typography>
                  {alagamentos.map((alagamento, index) => (
                    <Paper 
                      key={index} 
                      sx={{ 
                        p: 2, 
                        my: 2, 
                        bgcolor: 
                          alagamento.nivelGravidade === 'alto' ? '#ffebee' : 
                          alagamento.nivelGravidade === 'médio' ? '#fff8e1' : '#e8f5e9',
                        fontFamily: 'Neue Haas Grotesk, Arial, sans-serif'
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