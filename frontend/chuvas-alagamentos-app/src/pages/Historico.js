import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, CircularProgress, Tabs, Tab, TextField, Button, MenuItem, Select, FormControl, InputLabel, Chip } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import ptBR from 'date-fns/locale/pt-BR';
import { getHistoricoChuvas, getHistoricoAlagamentos, getMunicipios } from '../services/alertaService';
import { format } from 'date-fns';
import Diagnostico from '../components/Diagnostico';
import { List, ListItem, ListItemText } from '@mui/material';
import { WarningIcon } from '@mui/icons-material';
import { TableContainer, Table, TableHead, TableBody, TableRow } from '@mui/material';

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
          acc[municipio.uf].push(municipio.nome);
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

      if (dataInicio && dataFim && dataInicio > dataFim) {
        setError('A data inicial não pode ser maior que a data final');
        return;
      }

      const dataInicioFormatada = dataInicio ? format(dataInicio, 'yyyy-MM-dd') : format(new Date('2020-01-01'), 'yyyy-MM-dd');
      const dataFimFormatada = dataFim ? format(dataFim, 'yyyy-MM-dd') : format(new Date(), 'yyyy-MM-dd');
      
      const [dadosChuvas, dadosAlagamentos] = await Promise.all([
        getHistoricoChuvas(cidade, estado, dataInicioFormatada, dataFimFormatada),
        getHistoricoAlagamentos(cidade, estado, dataInicioFormatada, dataFimFormatada)
      ]);

      if (!dadosChuvas || dadosChuvas.length === 0) {
        setError('Nenhum dado encontrado para o período selecionado');
        setChuvas([]);
        setAlagamentos([]);
      } else {
        setChuvas(dadosChuvas);
        setAlagamentos(dadosAlagamentos || []);
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

  const handleSubmit = async (event) => {
    event.preventDefault();
    await handleBuscar();
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
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Histórico de Chuvas e Alagamentos
      </Typography>

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

        <TextField
          label="Data Inicial"
          type="date"
          value={dataInicio}
          onChange={(e) => setDataInicio(e.target.value)}
          InputLabelProps={{ shrink: true }}
          sx={{ minWidth: 180 }}
        />

        <TextField
          label="Data Final"
          type="date"
          value={dataFim}
          onChange={(e) => setDataFim(e.target.value)}
          InputLabelProps={{ shrink: true }}
          sx={{ minWidth: 180 }}
        />

        <Button 
          variant="contained" 
          onClick={handleSubmit}
          disabled={loading}
        >
          Buscar
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      ) : chuvas.length > 0 ? (
        <>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Estatísticas do Período
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1">
                  Precipitação Total: {estatisticasChuvas.total} mm
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1">
                  Média Diária: {estatisticasChuvas.media} mm
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1">
                  Máxima Registrada: {estatisticasChuvas.maxima} mm
                </Typography>
              </Grid>
            </Grid>
          </Paper>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Data</TableCell>
                  <TableCell align="right">Precipitação (mm)</TableCell>
                  <TableCell>Alagamento</TableCell>
                  <TableCell>Detalhes</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {chuvas.map((chuva) => {
                  const alagamentosDoDia = alagamentos.filter(
                    a => format(new Date(a.data), 'yyyy-MM-dd') === format(new Date(chuva.data), 'yyyy-MM-dd')
                  );
                  return (
                    <TableRow 
                      key={chuva.data}
                      sx={{ 
                        bgcolor: alagamentosDoDia.length > 0 ? '#fff3e0' : 'inherit',
                        '&:hover': { bgcolor: alagamentosDoDia.length > 0 ? '#ffe0b2' : '#f5f5f5' }
                      }}
                    >
                      <TableCell>{format(new Date(chuva.data), 'dd/MM/yyyy')}</TableCell>
                      <TableCell align="right">{chuva.precipitacao.toFixed(1)}</TableCell>
                      <TableCell>
                        {alagamentosDoDia.length > 0 ? (
                          <Chip 
                            label="Sim" 
                            color="warning" 
                            size="small"
                            icon={<WarningIcon />}
                          />
                        ) : (
                          <Chip 
                            label="Não" 
                            color="success" 
                            size="small"
                          />
                        )}
                      </TableCell>
                      <TableCell>
                        {alagamentosDoDia.length > 0 && (
                          <Box>
                            <Typography variant="body2" color="warning.dark">
                              Nível: {alagamentosDoDia[0].nivelAlagamento}
                            </Typography>
                            {alagamentosDoDia[0].areasAfetadas && (
                              <Typography variant="body2">
                                Áreas: {alagamentosDoDia[0].areasAfetadas.join(', ')}
                              </Typography>
                            )}
                          </Box>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      ) : (
        <Alert severity="info" sx={{ mt: 2 }}>
          Nenhum dado histórico encontrado para o período selecionado.
        </Alert>
      )}
    </Container>
  );
};

export default Historico; 