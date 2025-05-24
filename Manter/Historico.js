import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, CircularProgress, Tabs, Tab, TextField, Button, MenuItem, Select, FormControl, InputLabel, Chip } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import ptBR from 'date-fns/locale/pt-BR';
import { getHistoricoChuvas, getHistoricoAlagamentos, getMunicipios } from '../services/alertaService';
import { format, parseISO } from 'date-fns';
import Diagnostico from '../components/Diagnostico';
import { List, ListItem, ListItemText } from '@mui/material';
import { WarningAmber } from '@mui/icons-material';
import { TableContainer, Table, TableHead, TableBody, TableRow, TableCell } from '@mui/material';
import PatternBackground, { PATTERN_PRESETS } from '../components/PatternBackground';

// Componente para gráfico de linha simples
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const estados = [
  { sigla: 'RJ', nome: 'Rio de Janeiro' },
  { sigla: 'SP', nome: 'São Paulo' }
];

const Historico = () => {
  const [tab, setTab] = useState(0);
  const [chuvas, setChuvas] = useState([]);
  const [alagamentos, setAlagamentos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingData, setLoadingData] = useState(false);
  const [error, setError] = useState(null);
  const [estado, setEstado] = useState('RJ');
  const [cidade, setCidade] = useState('');
  const [municipios, setMunicipios] = useState([]);
  const [dataInicio, setDataInicio] = useState(null);
  const [dataFim, setDataFim] = useState(null);

  // Carregar municípios quando o estado muda
  useEffect(() => {
    const fetchMunicipios = async () => {
      if (!estado) return;
      
      setLoading(true);
      try {
        console.log('🏙️ Carregando municípios para estado:', estado);
        const dados = await getMunicipios(estado);
        console.log('✅ Municípios recebidos:', dados?.length || 0, 'registros');
        
        if (Array.isArray(dados) && dados.length > 0) {
          setMunicipios(dados);
          // Define a primeira cidade como padrão
          setCidade(dados[0].nome || dados[0]);
          setError(null);
        } else {
          setMunicipios([]);
          setCidade('');
          setError('Nenhum município encontrado para este estado');
        }
      } catch (err) {
        console.error('❌ Erro ao carregar municípios:', err);
        setError('Não foi possível carregar a lista de municípios');
        setMunicipios([]);
        setCidade('');
      } finally {
        setLoading(false);
      }
    };
    
    fetchMunicipios();
  }, [estado]);

  const handleBuscar = async () => {
    if (!cidade || !estado) {
      setError('Selecione uma cidade e um estado antes de buscar.');
      return;
    }

    if (dataInicio && dataFim && new Date(dataInicio) > new Date(dataFim)) {
      setError('A data inicial não pode ser maior que a data final');
      return;
    }

    setLoadingData(true);
    setError(null);

    try {
      // Definir datas padrão se não informadas
      const dataInicioFormatada = dataInicio || '2020-01-01';
      const dataFimFormatada = dataFim || format(new Date(), 'yyyy-MM-dd');
      
      console.log('🔍 Buscando histórico para:', { 
        cidade, 
        estado, 
        dataInicioFormatada, 
        dataFimFormatada 
      });
      
      const [dadosChuvas, dadosAlagamentos] = await Promise.all([
        getHistoricoChuvas(cidade, estado, dataInicioFormatada, dataFimFormatada),
        getHistoricoAlagamentos(cidade, estado, dataInicioFormatada, dataFimFormatada)
      ]);

      console.log('✅ Dados recebidos - Chuvas:', dadosChuvas?.length || 0, 'Alagamentos:', dadosAlagamentos?.length || 0);

      // Garantir que sempre temos arrays válidos
      const chuvasArray = Array.isArray(dadosChuvas) ? dadosChuvas : [];
      const alagamentosArray = Array.isArray(dadosAlagamentos) ? dadosAlagamentos : [];

      setChuvas(chuvasArray);
      setAlagamentos(alagamentosArray);

      if (chuvasArray.length === 0 && alagamentosArray.length === 0) {
        setError('Nenhum dado encontrado para o período selecionado');
      }
    } catch (err) {
      console.error('❌ Erro ao carregar histórico:', err);
      setError('Erro ao carregar dados históricos: ' + (err.message || 'Erro desconhecido'));
      setChuvas([]);
      setAlagamentos([]);
    } finally {
      setLoadingData(false);
    }
  };

  const handleChangeTab = (event, newValue) => {
    setTab(newValue);
  };

  const handleEstadoChange = (event) => {
    const novoEstado = event.target.value;
    setEstado(novoEstado);
    setCidade(''); // Limpar cidade ao mudar estado
  };

  const handleCidadeChange = (event) => {
    setCidade(event.target.value);
  };

  const calcularEstatisticas = () => {
    if (!Array.isArray(chuvas) || chuvas.length === 0) {
      return { total: 0, media: 0, maxima: 0 };
    }
    
    const valores = chuvas.map(item => {
      const precip = item.precipitacao || item.mm || item.valor || 0;
      return typeof precip === 'number' ? precip : parseFloat(precip) || 0;
    });
    
    const total = valores.reduce((soma, valor) => soma + valor, 0);
    const media = total / valores.length;
    const maxima = Math.max(...valores);
    
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

  const formatarData = (dataString) => {
    try {
      if (!dataString) return 'Data não disponível';
      
      let data;
      if (dataString.includes('T')) {
        data = parseISO(dataString);
      } else if (dataString.includes('-')) {
        data = new Date(dataString + 'T00:00:00');
      } else {
        data = new Date(dataString);
      }
      
      if (isNaN(data.getTime())) {
        console.warn('⚠️ Data inválida:', dataString);
        return 'Data inválida';
      }
      
      return format(data, 'dd/MM/yyyy', { locale: ptBR });
    } catch (error) {
      console.error('❌ Erro ao formatar data:', error, 'Data:', dataString);
      return 'Data inválida';
    }
  };

  const getPrecipitacao = (item) => {
    return item.precipitacao || item.mm || item.valor || 0;
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
          <CircularProgress />
          <Typography sx={{ ml: 2 }}>Carregando municípios...</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <PatternBackground {...PATTERN_PRESETS.content}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Histórico de Chuvas e Alagamentos
        </Typography>

        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
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
              disabled={municipios.length === 0}
            >
              {municipios.length > 0 ? 
                municipios.map((municipio, index) => {
                  const nomeMunicipio = municipio.nome || municipio;
                  return (
                    <MenuItem key={index} value={nomeMunicipio}>
                      {nomeMunicipio}
                    </MenuItem>
                  );
                }) : 
                <MenuItem value="">Nenhum município disponível</MenuItem>
              }
            </Select>
          </FormControl>

          <TextField
            label="Data Inicial"
            type="date"
            value={dataInicio || ''}
            onChange={(e) => setDataInicio(e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={{ minWidth: 180 }}
          />

          <TextField
            label="Data Final"
            type="date"
            value={dataFim || ''}
            onChange={(e) => setDataFim(e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={{ minWidth: 180 }}
          />

          <Button 
            type="submit"
            variant="contained" 
            disabled={loadingData || !cidade}
          >
            {loadingData ? 'Buscando...' : 'Buscar'}
          </Button>
        </Box>

        {loadingData ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
            <Typography sx={{ ml: 2 }}>Carregando dados históricos...</Typography>
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        ) : (chuvas.length > 0 || alagamentos.length > 0) ? (
          <>
            {chuvas.length > 0 && (
              <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Estatísticas do Período - {cidade}, {estado}
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
            )}

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
                  {chuvas.length > 0 ? chuvas.map((chuva, index) => {
                    const dataItem = chuva.data || chuva.date;
                    const alagamentosDoDia = alagamentos.filter(
                      a => {
                        try {
                          const dataAlagamento = a.data || a.date;
                          if (!dataItem || !dataAlagamento) return false;
                          
                          const dataChuvaStr = format(new Date(dataItem), 'yyyy-MM-dd');
                          const dataAlagamentoStr = format(new Date(dataAlagamento), 'yyyy-MM-dd');
                          return dataChuvaStr === dataAlagamentoStr;
                        } catch (e) {
                          return false;
                        }
                      }
                    );
                    
                    return (
                      <TableRow 
                        key={`${dataItem}-${index}`}
                        sx={{ 
                          bgcolor: alagamentosDoDia.length > 0 ? '#fff3e0' : 'inherit',
                          '&:hover': { bgcolor: alagamentosDoDia.length > 0 ? '#ffe0b2' : '#f5f5f5' }
                        }}
                      >
                        <TableCell>{formatarData(dataItem)}</TableCell>
                        <TableCell align="right">
                          {getPrecipitacao(chuva).toFixed(1)}
                        </TableCell>
                        <TableCell>
                          {alagamentosDoDia.length > 0 ? (
                            <Chip 
                              label="Sim" 
                              color="warning" 
                              size="small"
                              icon={<WarningAmber />}
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
                                Nível: {alagamentosDoDia[0].nivelAlagamento || alagamentosDoDia[0].nivel || 'N/A'}
                              </Typography>
                              {alagamentosDoDia[0].areasAfetadas && (
                                <Typography variant="body2">
                                  Áreas: {Array.isArray(alagamentosDoDia[0].areasAfetadas) 
                                    ? alagamentosDoDia[0].areasAfetadas.join(', ')
                                    : alagamentosDoDia[0].areasAfetadas}
                                </Typography>
                              )}
                            </Box>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  }) : alagamentos.map((alagamento, index) => (
                    <TableRow 
                      key={`alagamento-${index}`}
                      sx={{ 
                        bgcolor: '#fff3e0',
                        '&:hover': { bgcolor: '#ffe0b2' }
                      }}
                    >
                      <TableCell>{formatarData(alagamento.data || alagamento.date)}</TableCell>
                      <TableCell align="right">N/A</TableCell>
                      <TableCell>
                        <Chip 
                          label="Sim" 
                          color="warning" 
                          size="small"
                          icon={<WarningAmber />}
                        />
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" color="warning.dark">
                            Nível: {alagamento.nivelAlagamento || alagamento.nivel || 'N/A'}
                          </Typography>
                          {alagamento.areasAfetadas && (
                            <Typography variant="body2">
                              Áreas: {Array.isArray(alagamento.areasAfetadas) 
                                ? alagamento.areasAfetadas.join(', ')
                                : alagamento.areasAfetadas}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        ) : (
          <Alert severity="info" sx={{ mt: 2 }}>
            {cidade ? 
              'Nenhum dado histórico encontrado para o período selecionado.' : 
              'Selecione uma cidade para visualizar os dados históricos.'
            }
          </Alert>
        )}
      </Container>
    </PatternBackground>
  );
};

export default Historico;