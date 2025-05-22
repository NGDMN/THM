import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, CircularProgress, Tabs, Tab, TextField, Autocomplete, FormControl, InputLabel, Select, MenuItem, Tooltip } from '@mui/material';
import { getPrevisaoChuvas, getPrevisaoAlagamentos, getMunicipios } from '../services/alertaService';
import { useNavigate } from 'react-router-dom';
import Diagnostico from '../components/Diagnostico';
import WarningIcon from '@mui/icons-material/Warning';
import { format } from 'date-fns';

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
  const [municipiosLista, setMunicipiosLista] = useState([]);
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
        setMunicipiosLista(dados);
        
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
        setError(null);
        console.log('Buscando previsões para:', { cidade, estado });
        
        const [dadosChuvas, dadosAlagamentos] = await Promise.all([
          getPrevisaoChuvas(cidade, estado),
          getPrevisaoAlagamentos(cidade, estado)
        ]);
        
        console.log('Dados de chuvas recebidos:', dadosChuvas);
        console.log('Dados de alagamentos recebidos:', dadosAlagamentos);
        
        const chuvasArray = Array.isArray(dadosChuvas) ? dadosChuvas : [];
        const alagamentosArray = Array.isArray(dadosAlagamentos) ? dadosAlagamentos : (dadosAlagamentos ? [dadosAlagamentos] : []);
        setChuvas(chuvasArray);
        setAlagamentos(alagamentosArray);
      } catch (err) {
        console.error('Erro ao carregar previsões:', err);
        setError(err.message || 'Não foi possível carregar as previsões');
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

  const chuvasArray = Array.isArray(chuvas) ? chuvas : [];
  const alagamentosArray = Array.isArray(alagamentos) ? alagamentos : (alagamentos ? [alagamentos] : []);

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

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {chuvasArray.length === 0 && alagamentosArray.length === 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Nenhuma previsão disponível para o período selecionado.
            </Alert>
          )}
          {chuvasArray.map((previsao, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <Paper 
                sx={{ 
                  p: 2,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                  bgcolor: previsao.riscoAlagamento ? '#fff3e0' : 'background.paper'
                }}
              >
                <Typography variant="h6" gutterBottom>
                  {format(new Date(previsao.data), 'dd/MM/yyyy')}
                </Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h4" sx={{ mr: 2 }}>
                    {previsao.precipitacao.toFixed(1)} mm
                  </Typography>
                  {previsao.riscoAlagamento && (
                    <Tooltip title="Risco de Alagamento">
                      <WarningIcon color="warning" />
                    </Tooltip>
                  )}
                </Box>

                {previsao.riscoAlagamento && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: '#fff3e0', borderRadius: 1 }}>
                    <Typography variant="subtitle2" color="warning.dark" gutterBottom>
                      Risco de Alagamento
                    </Typography>
                    <Typography variant="body2">
                      Probabilidade: {previsao.probabilidadeAlagamento}%
                    </Typography>
                    {previsao.recomendacoes && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Recomendações:
                        </Typography>
                        <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                          {previsao.recomendacoes.map((rec, idx) => (
                            <li key={idx}>
                              <Typography variant="body2">{rec}</Typography>
                            </li>
                          ))}
                        </ul>
                      </Box>
                    )}
                  </Box>
                )}
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default Previsoes; 