import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const Footer = () => {
  return (
    <Box
      component="footer"
      className="App-footer pattern-footer"
      sx={{ 
        backgroundColor: 'primary.main', 
        color: 'primary.contrastText', 
        position: 'fixed', 
        left: 0, 
        bottom: 0, 
        width: '100%', 
        height: '70px', 
        zIndex: 9999, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        boxShadow: '0 -2px 4px rgba(0,0,0,0.08)',
        padding: '8px 0'
      }}
    >
      <Container maxWidth="lg" sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <Typography variant="body1" align="center" color="primary.contrastText">
          Sistema de Previsão de Alagamentos RJ/SP - © {new Date().getFullYear()}
        </Typography>
        <Typography variant="body2" align="center" color="primary.contrastText">
          Desenvolvido por Goodman Solution Experts
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer; 