import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();

  const headerStyle = {
    background: '#1976d2',
    color: '#F5F9FC', // branco azulado
    padding: '16px 0',
    textAlign: 'center',
  };

  return (
    <AppBar position="fixed" className="App-header">
      <Toolbar sx={{ alignItems: 'center', height: '100%' }}>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }} color="primary.contrastText">
          Sistema de Previsão de Alagamentos RJ/SP
        </Typography>
        <Box>
          <Button color="inherit" onClick={() => navigate('/')}
          >
            Início
          </Button>
          <Button color="inherit" onClick={() => navigate('/previsoes')}
          >
            Previsões
          </Button>
          <Button color="inherit" onClick={() => navigate('/historico')}
          >
            Histórico
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header; 