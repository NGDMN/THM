import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert, CircularProgress, Tabs, Tab, TextField, Autocomplete, FormControl, InputLabel, Select, MenuItem, Tooltip } from '@mui/material';
import { getPrevisaoChuvas, getPrevisaoAlagamentos, getMunicipios } from '../services/alertaService';
import { useNavigate } from 'react-router-dom';
import Diagnostico from '../components/Diagnostico';
import WarningAmber from '@mui/icons-material/WarningAmber';
import { format } from 'date-fns';
import PatternBackground, { PATTERN_PRESETS } from '../components/PatternBackground';

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
      setLoading(true);
      try {
        const dados = await getMunicipios();
        console.log('Dados de municípios recebidos:', dados);
        
        if (!Array.isArray(dados)) {
          throw new Error('Formato de dados inválido - esperado array');
        }
        
        const municipiosPorEstado = dados.reduce((acc, municipio) => {
          if (municipio && municipio.uf && municipio.nome) {
            if (!acc[municipio.uf]) {
              acc[municipio.uf] = [];
            }
            acc[municipio.uf].push(municipio.nome);
          }
          return acc;
        }, {});
        
        setMunicipios(municipiosPorEstado);
        setMunicipiosLista(dados);
        
        // Verificação segura antes de definir a primeira cidade
        if (municipiosPorEstado[estado] && Array.isArray(municipiosPorEstado[estado]) && municipiosPorEstado[estado].length > 0) {
          setCidade(municipiosPorEstado[estado][0]);
        } else {
          setCidade('');
        }
        setError(null);
      } catch (err) {
        console.error('Erro ao carregar municípios:', err);
        setError('Não foi possível carregar a lista de municípios');
        setMunicipios({});
        setMunicipiosLista([]);
        setCidade('');
      } finally {
        setLoading(false);
      }
    };
    fetchMunicipios();
  }, []);

  // Carregar dados de previsão
  useEffect(() => {
    const fetchData = async () => {
      if (!cidade || !estado) {
        console.log('Cidade ou estado não definidos:', { cidade, estado });
        return;
      }
      
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
        
        // Tratamento mais robusto dos dados de chuvas
        let chuvasArray = [];
        if (Array.isArray(dadosChuvas)) {
          chuvasArray = dadosChuvas;
        } else if (dadosChuvas && typeof dadosChuvas === 'object') {
          // Se for um objeto único, transformar em array
          chuvasArray = [dadosChuvas];
        }
        
        // Tratamento dos dados de alagamentos
        let alagamentosArray = [];
        if (Array.isArray(dadosAlagamentos)) {
          alagamentosArray = dadosAlagamentos;
        } else if (dadosAlagamentos && typeof dadosAlagamentos === 'object') {
          alagamentosArray = [dadosAlagamentos];
        }
        
        // Combinar dados de chuvas com dados de alagamentos
        const previsoesCombinadas = chuvasArray.map(chuva => {
          // Procurar dados de alagamento correspondentes
          const alagamentoCorrespondente = alagamentosArray.find(
            alag => alag.data === chuva.data || alag.cidade === chuva.cidade
          );
          
          return {
            ...chuva,
            riscoAlagamento: alagamentoCorrespondente ? 
              (alagamentoCorrespondente.nivelRisco !== 'baixo' && alagamentoCorrespondente.nivelRisco !== 'desconhecido') : 
              false,
            probabilidadeAlagamento: alagamentoCorrespondente ? 
              alagamentoCorrespondente.probabilidade || 0 : 
              0,
            recomendacoes: alagamentoCorrespondente ? 
              alagamentoCorrespondente.recomendacoes || [] : 
              []
          };
        });
        
        console.log('Previsões combinadas:', previsoesCombinadas);
        
        setChuvas(previsoesCombinadas);
        setAlagamentos(alagamentosArray);
        
        // Se não há dados, definir erro informativo
        if (previsoesCombinadas.length === 0) {
          setError(`Nenhuma previsão encontrada para ${cidade} - ${estado}. Verifique se a cidade está correta.`);
        }
        
      } catch (err) {
        console.error('Erro ao carregar previsões:', err);
        setError(`Erro ao carregar previsões: ${err.message || 'Erro desconhecido'}`);
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
    
    // Verificação segura antes de definir cidade
    if (municipios[novoEstado] && Array.isArray(municipios[novoEstado]) && municipios[novoEstado].length > 0) {
      setCidade(municipios[novoEstado][0]);
    } else {
      setCidade('');
    }
  };

  const handleCidadeChange = (event) => {
    setCidade(event.target.value);
  };

  if (loading && !cidade && Object.keys(municipios).length === 0) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
          <CircularProgress />
          <Typography sx={{ ml: 2 }}>Carregando municípios...</Typography>
        </Box>
      </Container>
    );
  }

  const chuvasArray = Array.isArray(chuvas) ? chuvas : [];
  const alagamentosArray = Array.isArray(alagamentos) ? alagamentos : [];

  return (
    <PatternBackground {...PATTERN_PRESETS.content}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Previsões para {cidade || 'Carregando...'} - {estado}
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
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
            <Typography sx={{ ml: 2 }}>Carregando previsões...</Typography>
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        ) : chuvasArray.length > 0 ? (
          <Grid container spacing={3}>
            {chuvasArray.map((previsao, index) => (
              <Grid item xs={12} md={6} lg={4} key={previsao.data || index}>
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
                    {previsao.data ? format(new Date(previsao.data), 'dd/MM/yyyy') : 'Data não disponível'}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h4" sx={{ mr: 2 }}>
                      {(previsao.precipitacao || 0).toFixed(1)} mm
                    </Typography>
                    {previsao.riscoAlagamento && (
                      <Tooltip title="Risco de Alagamento">
                        <WarningAmber color="warning" />
                      </Tooltip>
                    )}
                  </Box>

                  {previsao.temperatura && (
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      Temperatura: {previsao.temperatura}°C
                    </Typography>
                  )}

                  {previsao.umidade && (
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      Umidade: {previsao.umidade}%
                    </Typography>
                  )}

                  {previsao.riscoAlagamento && (
                    <Box sx={{ mt: 2, p: 2, bgcolor: '#fff3e0', borderRadius: 1 }}>
                      <Typography variant="subtitle2" color="warning.dark" gutterBottom>
                        Risco de Alagamento
                      </Typography>
                      <Typography variant="body2">
                        Probabilidade: {previsao.probabilidadeAlagamento || 0}%
                      </Typography>
                      {previsao.recomendacoes && Array.isArray(previsao.recomendacoes) && previsao.recomendacoes.length > 0 && (
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
        ) : (
          <Alert severity="info" sx={{ mt: 2 }}>
            {cidade ? 
              `Nenhuma previsão disponível para ${cidade} - ${estado}. Verifique se a cidade está correta ou tente outra localização.` : 
              'Selecione uma cidade para visualizar as previsões.'
            }
          </Alert>
        )}
      </Container>
    </PatternBackground>
  );
};

export default Previsoes;