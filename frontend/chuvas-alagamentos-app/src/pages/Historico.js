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
  const [loadingData, setLoadingData] = useState(false); // Loading separado para busca de dados
  const [error, setError] = useState(null);
  const [estado, setEstado] = useState('RJ');
  const [cidade, setCidade] = useState('');
  const [municipios, setMunicipios] = useState({});
  const [dataInicio, setDataInicio] = useState(null);
  const [dataFim, setDataFim] = useState(null);
  const [municipiosCarregados, setMunicipiosCarregados] = useState(false); // Flag para controlar carregamento

  // Carregar municípios apenas uma vez na inicialização
  useEffect(() => {
    const fetchMunicipios = async () => {
      if (municipiosCarregados) return; // Evita recarregamento desnecessário
      
      setLoading(true);
      try {
        const dados = await getMunicipios(estado);
        console.log('Dados de municípios recebidos:', dados);
        
        // Verificação mais robusta dos dados
        let municipiosPorEstado = {};
        if (Array.isArray(dados)) {
          municipiosPorEstado = dados.reduce((acc, municipio) => {
            if (municipio && municipio.uf && municipio.nome) {
              if (!acc[municipio.uf]) {
                acc[municipio.uf] = [];
              }
              acc[municipio.uf].push(municipio.nome);
            }
            return acc;
          }, {});
        }
        
        setMunicipios(municipiosPorEstado);
        
        // Verificação segura antes de acessar o array
        if (municipiosPorEstado[estado] && Array.isArray(municipiosPorEstado[estado]) && municipiosPorEstado[estado].length > 0) {
          setCidade(municipiosPorEstado[estado][0]);
        } else {
          setCidade('');
        }
        
        setMunicipiosCarregados(true); // Marca como carregado
        setError(null);
      } catch (err) {
        console.error('Erro ao carregar municípios:', err);
        setError('Não foi possível carregar a lista de municípios');
        setMunicipios({});
        setCidade('');
      } finally {
        setLoading(false);
      }
    };
    
    fetchMunicipios();
  }, []); // Removido 'estado' das dependências para evitar loop

  // Efeito separado para atualizar cidade quando estado muda (após municípios carregados)
  useEffect(() => {
    if (municipiosCarregados && municipios[estado]) {
      if (Array.isArray(municipios[estado]) && municipios[estado].length > 0) {
        setCidade(municipios[estado][0]);
      } else {
        setCidade('');
      }
    }
  }, [estado, municipiosCarregados, municipios]);

  const handleBuscar = async () => {
    try {
      setLoadingData(true); // Use loading separado para não afetar a interface
      setError(null);

      if (!cidade || !estado) {
        setError('Selecione uma cidade e um estado antes de buscar.');
        console.warn('Tentativa de busca com cidade ou estado vazio:', { cidade, estado });
        setLoadingData(false);
        return;
      }

      if (dataInicio && dataFim && dataInicio > dataFim) {
        setError('A data inicial não pode ser maior que a data final');
        setLoadingData(false);
        return;
      }

      const dataInicioFormatada = dataInicio ? format(new Date(dataInicio), 'yyyy-MM-dd') : format(new Date('2020-01-01'), 'yyyy-MM-dd');
      const dataFimFormatada = dataFim ? format(new Date(dataFim), 'yyyy-MM-dd') : format(new Date(), 'yyyy-MM-dd');
      
      console.log('Buscando histórico para:', { cidade, estado, dataInicioFormatada, dataFimFormatada });
      
      const [dadosChuvas, dadosAlagamentos] = await Promise.all([
        getHistoricoChuvas(cidade, estado, dataInicioFormatada, dataFimFormatada),
        getHistoricoAlagamentos(cidade, estado, dataInicioFormatada, dataFimFormatada)
      ]);

      console.log('Dados de chuvas recebidos:', dadosChuvas);
      console.log('Dados de alagamentos recebidos:', dadosAlagamentos);

      // Garantir que sempre temos arrays
      const chuvasArray = Array.isArray(dadosChuvas) ? dadosChuvas : [];
      const alagamentosArray = Array.isArray(dadosAlagamentos) ? dadosAlagamentos : [];

      if (chuvasArray.length === 0) {
        setError('Nenhum dado encontrado para o período selecionado');
      }
      
      setChuvas(chuvasArray);
      setAlagamentos(alagamentosArray);
    } catch (err) {
      console.error('Erro ao carregar histórico:', err);
      setError('Não foi possível carregar os dados históricos');
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
    // A cidade será atualizada automaticamente pelo useEffect
  };

  const handleCidadeChange = (event) => {
    setCidade(event.target.value);
  };

  const calcularEstatisticas = () => {
    if (!Array.isArray(chuvas) || chuvas.length === 0) {
      return { total: 0, media: 0, maxima: 0 };
    }
    const total = chuvas.reduce((soma, item) => soma + (item.precipitacao || 0), 0);
    const media = total / chuvas.length;
    const maxima = Math.max(...chuvas.map(item => item.precipitacao || 0));
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
      
      // Tenta diferentes formatos de data
      let data;
      if (dataString.includes('T')) {
        // Formato ISO
        data = parseISO(dataString);
      } else if (dataString.includes('-')) {
        // Formato YYYY-MM-DD
        data = new Date(dataString);
      } else {
        // Tenta converter direto
        data = new Date(dataString);
      }
      
      if (isNaN(data.getTime())) {
        console.warn('Data inválida:', dataString);
        return 'Data inválida';
      }
      
      return format(data, 'dd/MM/yyyy', { locale: ptBR });
    } catch (error) {
      console.error('Erro ao formatar data:', error);
      return 'Data inválida';
    }
  };

  // Loading inicial apenas para municípios
  if (loading && !municipiosCarregados) {
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
              disabled={!municipios[estado] || municipios[estado].length === 0}
            >
              {municipios[estado] && Array.isArray(municipios[estado]) ? 
                municipios[estado].map((cid) => (
                  <MenuItem key={cid} value={cid}>{cid}</MenuItem>
                )) : 
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
            variant="contained" 
            onClick={handleSubmit}
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
        ) : Array.isArray(chuvas) && chuvas.length > 0 ? (
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
                  {chuvas.map((chuva, index) => {
                    const alagamentosDoDia = Array.isArray(alagamentos) ? alagamentos.filter(
                      a => format(new Date(a.data), 'yyyy-MM-dd') === format(new Date(chuva.data), 'yyyy-MM-dd')
                    ) : [];
                    
                    return (
                      <TableRow 
                        key={chuva.data || index}
                        sx={{ 
                          bgcolor: alagamentosDoDia.length > 0 ? '#fff3e0' : 'inherit',
                          '&:hover': { bgcolor: alagamentosDoDia.length > 0 ? '#ffe0b2' : '#f5f5f5' }
                        }}
                      >
                        <TableCell>{formatarData(chuva.data)}</TableCell>
                        <TableCell align="right">{(chuva.precipitacao || 0).toFixed(1)}</TableCell>
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
                                Nível: {alagamentosDoDia[0].nivelAlagamento || 'N/A'}
                              </Typography>
                              {alagamentosDoDia[0].areasAfetadas && Array.isArray(alagamentosDoDia[0].areasAfetadas) && (
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