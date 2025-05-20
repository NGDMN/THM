import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const Footer = () => {
  return (
    <Box
      component="footer"
      className="App-footer"
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