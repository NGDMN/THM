import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Container } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import WaterDropIcon from '@mui/icons-material/WaterDrop';

const Navbar = () => {
  return (
    <>
      <AppBar position="fixed">
        <Container maxWidth="lg">
          <Toolbar disableGutters>
            <WaterDropIcon sx={{ mr: 1 }} />
            <Typography
              variant="h6"
              component={RouterLink}
              to="/"
              sx={{
                flexGrow: 1,
                textDecoration: 'none',
                color: 'inherit',
                display: 'flex',
                alignItems: 'center',
              }}
            >
              Sistema de Alerta de Chuvas
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                color="inherit"
                component={RouterLink}
                to="/previsoes"
              >
                Previsões
              </Button>
              <Button
                color="inherit"
                component={RouterLink}
                to="/historico"
              >
                Histórico
              </Button>
              <Button
                color="inherit"
                component={RouterLink}
                to="/sobre"
              >
                Sobre
              </Button>
            </Box>
          </Toolbar>
        </Container>
      </AppBar>
      <Toolbar /> {/* Espaçador para compensar o AppBar fixo */}
    </>
  );
};

export default Navbar; 