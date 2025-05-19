import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Sistema de Previsão de Alagamentos RJ/SP
        </Typography>
        <Box>
          <Button color="inherit" onClick={() => navigate('/')}>
            Início
          </Button>
          <Button color="inherit" onClick={() => navigate('/previsoes')}>
            Previsões
          </Button>
          <Button color="inherit" onClick={() => navigate('/mapa')}>
            Mapa
          </Button>
          <Button color="inherit" onClick={() => navigate('/historico')}>
            Histórico
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header; 