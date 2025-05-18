import React from 'react';
import { Box, Typography, Container, Link } from '@mui/material';

const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: 'primary.main',
        color: 'white'
      }}
    >
      <Container maxWidth="lg">
        <Typography variant="body1" align="center">
          Sistema de Previsão de Alagamentos RJ/SP - © {new Date().getFullYear()}
        </Typography>
        <Typography variant="body2" align="center">
          Desenvolvido com <Link color="inherit" href="https://reactjs.org/">React</Link> e 
          <Link color="inherit" href="https://flask.palletsprojects.com/"> Flask</Link>
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer; 