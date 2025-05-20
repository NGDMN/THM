import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const Footer = () => {
  const footerStyle = {
    background: '#1976d2',
    color: '#F5F9FC', // branco azulado
    padding: '12px 0',
    textAlign: 'center',
  };

  return (
    <Box
      component="footer"
      className="App-footer pattern-footer"
      sx={{ backgroundColor: 'primary.main', color: 'primary.contrastText', position: 'fixed', left: 0, bottom: 0, width: '100%', height: '70px', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 -2px 4px rgba(0,0,0,0.08)' }}
    >
      <Container maxWidth="lg">
        <Typography variant="body1" align="center">
          Sistema de Previsão de Alagamentos RJ/SP - © {new Date().getFullYear()}
        </Typography>
        <Typography variant="body2" align="center">
          Desenvolvido por Goodman Solution Experts
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer; 