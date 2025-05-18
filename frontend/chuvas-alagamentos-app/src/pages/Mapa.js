import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Paper, Alert, CircularProgress } from '@mui/material';

const Mapa = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Simulando carregamento de dados do mapa
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

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
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Mapa de Ocorrências
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4, minHeight: '500px' }}>
        <Typography variant="body1" paragraph>
          Esta é uma implementação temporária da página de Mapa.
        </Typography>
        <Typography variant="body1" paragraph>
          Aqui seria implementado um mapa interativo mostrando as áreas com ocorrências de chuvas intensas
          e pontos de alagamento. O mapa poderia utilizar bibliotecas como Google Maps API, Leaflet, ou similar.
        </Typography>
        <Box
          sx={{
            height: '400px',
            width: '100%',
            backgroundColor: '#eee',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            border: '1px dashed #ccc'
          }}
        >
          <Typography variant="h6" color="text.secondary">
            Área do Mapa
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default Mapa; 