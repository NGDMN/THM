import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, CircularProgress, Tabs, Tab, MenuItem, Select, FormControl, InputLabel } from '@mui/material';
import { getPrevisaoChuvas, getPrevisaoAlagamentos, getMunicipios } from '../services/alertaService';
import { useNavigate } from 'react-router-dom';

const estados = [
  { sigla: 'RJ', nome: 'Rio de Janeiro' },
  { sigla: 'SP', nome: 'São Paulo' }
];

const Previsoes = () => {
  const [tab, setTab] = useState(0);
  const [chuvas, setChuvas] = useState([]);
  const [alagamentos, setAlagamentos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [estado, setEstado] = useState('RJ');
  const [cidade, setCidade] = useState('');
  const [municipios, setMunicipios] = useState({});
  const navigate = useNavigate();

  // Carregar lista de municípios
  useEffect(() => {
    const fetchMunicipios = async () => {
      try {
        setLoading(true);
        const dados = await getMunicipios();
        if (!Array.isArray(dados)) {
          throw new Error('Formato de dados inválido');
        }
        
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
        setError(null);
      } catch (err) {
        console.error('Erro ao carregar municípios:', err);
        setError('Não foi possível carregar a lista de municípios');
      } finally {
        setLoading(false);
      }
    };
    fetchMunicipios();
  }, []);

  // Carregar dados de previsão
  useEffect(() => {
    const fetchData = async () => {
      if (!cidade || !estado) return;
      
      try {
        setLoading(true);
        const [dadosChuvas, dadosAlagamentos] = await Promise.all([
          getPrevisaoChuvas(cidade, estado),
          getPrevisaoAlagamentos(cidade, estado)
        ]);
        
        if (Array.isArray(dadosChuvas)) {
          setChuvas(dadosChuvas);
        } else {
          console.error('Dados de chuvas em formato inválido:', dadosChuvas);
          setChuvas([]);
        }
        
        if (Array.isArray(dadosAlagamentos)) {
          setAlagamentos(dadosAlagamentos);
        } else {
          console.error('Dados de alagamentos em formato inválido:', dadosAlagamentos);
          setAlagamentos([]);
        }
        
        setError(null);
      } catch (err) {
        console.error('Erro ao carregar previsões:', err);
        setError('Não foi possível carregar as previsões');
        setChuvas([]);
        setAlagamentos([]);
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
    if (municipios[novoEstado]?.length > 0) {
      setCidade(municipios[novoEstado][0]);
    } else {
      setCidade('');
    }
  };

  const handleCidadeChange = (event) => {
    setCidade(event.target.value);
  };

  if (loading && !cidade) {
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

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {tab === 0 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                Previsão de Chuvas - {cidade}/{estado}
              </Typography>
              {Array.isArray(chuvas) && chuvas.length > 0 ? (
                <Grid container spacing={2}>
                  {chuvas.map((previsao, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                      <Paper 
                        sx={{ 
                          p: 2, 
                          display: 'flex', 
                          flexDirection: 'column',
                          alignItems: 'center',
                          bgcolor: previsao.precipitacao >= 30 ? 'error.light' : 
                                   previsao.precipitacao >= 15 ? 'warning.light' : 
                                   'success.light'
                        }}
                      >
                        <Typography variant="h6">{previsao.data}</Typography>
                        <Typography variant="body1" sx={{ fontWeight: 'bold', fontSize: '1.5rem' }}>
                          {previsao.precipitacao} mm
                        </Typography>
                        {previsao.precipitacao >= 30 && (
                          <Alert severity="error" sx={{ mt: 2 }}>
                            Risco de alagamento!
                          </Alert>
                        )}
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Alert severity="info">
                  Nenhuma previsão disponível para o período selecionado
                </Alert>
              )}
            </Box>
          )}

          {tab === 1 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                Previsão de Alagamentos - {cidade}/{estado}
              </Typography>
              {Array.isArray(alagamentos) && alagamentos.length > 0 ? (
                <Grid container spacing={2}>
                  {alagamentos.map((alagamento, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                      <Paper 
                        sx={{ 
                          p: 2,
                          bgcolor: alagamento.nivelGravidade === 'alto' ? '#ffebee' : 
                                   alagamento.nivelGravidade === 'médio' ? '#fff8e1' : '#e8f5e9'
                        }}
                      >
                        <Typography variant="h6">
                          {alagamento.data}
                        </Typography>
                        <Typography variant="body1">
                          Local: {alagamento.local}
                        </Typography>
                        <Typography variant="body2">
                          Nível de gravidade: {alagamento.nivelGravidade.toUpperCase()}
                        </Typography>
                        <Typography variant="body2">
                          Probabilidade: {alagamento.probabilidade}%
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Alert severity="info">
                  Nenhuma previsão de alagamento disponível
                </Alert>
              )}
            </Box>
          )}
        </>
      )}
    </Container>
  );
};

export default Previsoes; 