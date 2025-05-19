import React from 'react';
import { Box, Typography, Container, Link } from '@mui/material';

const Footer = () => {
  return (
    <Box
      component="footer"
      className="App-footer"
    >
      <Container maxWidth="lg">
        <Typography variant="body1" align="center" sx={{ color: '#F5F9FC' }}>
          Sistema de Previsão de Alagamentos RJ/SP - © {new Date().getFullYear()}
        </Typography>
        <Typography variant="body2" align="center" sx={{ color: '#F5F9FC' }}>
          Desenvolvido por Goodman Solution Experts
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer; 