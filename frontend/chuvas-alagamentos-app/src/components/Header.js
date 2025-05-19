import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();

  return (
    <AppBar position="static" className="App-header">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: '#F5F9FC' }}>
          Sistema de Previsão de Alagamentos RJ/SP
        </Typography>
        <Box>
          <Button color="inherit" onClick={() => navigate('/')}
            sx={{ color: '#F5F9FC' }}
          >
            Início
          </Button>
          <Button color="inherit" onClick={() => navigate('/previsoes')}
            sx={{ color: '#F5F9FC' }}
          >
            Previsões
          </Button>
          <Button color="inherit" onClick={() => navigate('/historico')}
            sx={{ color: '#F5F9FC' }}
          >
            Histórico
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header; 