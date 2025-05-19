import React from 'react';
import { Container, Typography, Box, Paper, List, ListItem, ListItemText, Grid } from '@mui/material';

const recomendacoes = [
  {
    nivel: 'Alto',
    dicas: [
      'Evite áreas marcadas como risco de alagamento.',
      'Mantenha-se informado por canais oficiais da Defesa Civil.',
      'Tenha um plano de emergência para sua família.',
      'Se necessário, evacue para locais seguros indicados pelas autoridades.',
      'Não tente atravessar áreas alagadas, mesmo de carro.'
    ]
  },
  {
    nivel: 'Médio',
    dicas: [
      'Acompanhe as previsões meteorológicas e alertas.',
      'Evite deslocamentos desnecessários em dias de chuva forte.',
      'Proteja documentos e objetos de valor em locais elevados.',
      'Fique atento a sinais de elevação do nível da água.'
    ]
  },
  {
    nivel: 'Baixo',
    dicas: [
      'Monitore as condições do tempo.',
      'Mantenha-se atento a mudanças repentinas no clima.',
      'Siga orientações das autoridades locais.'
    ]
  }
];

const Recomendacoes = () => {
  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 8 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Recomendações em Caso de Alagamento
      </Typography>
      <Typography variant="body1" sx={{ mb: 4 }}>
        Siga sempre as orientações da Defesa Civil e mantenha-se informado por canais oficiais. Em caso de risco, priorize a segurança da sua família e de pessoas vulneráveis.
      </Typography>
      <Grid container spacing={3}>
        {recomendacoes.map((rec, idx) => (
          <Grid item xs={12} md={4} key={rec.nivel}>
            <Paper sx={{ 
              p: 3, 
              className: rec.nivel === 'Alto' ? 'risco-alto' : 
                        rec.nivel === 'Médio' ? 'risco-medio' : 'risco-baixo',
              background: 'background.default' 
            }}>
              <Typography variant="h5" sx={{ 
                color: rec.nivel === 'Alto' ? 'error.main' : 
                       rec.nivel === 'Médio' ? 'warning.main' : 'success.main', 
                fontWeight: 700, 
                mb: 2 
              }}>
                {rec.nivel} Risco
              </Typography>
              <List>
                {rec.dicas.map((dica, i) => (
                  <ListItem key={i} sx={{ pl: 0 }}>
                    <ListItemText primary={dica} />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Recomendacoes; 