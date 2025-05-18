import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Componentes
import Header from './components/Header';
import Footer from './components/Footer';

// Páginas
import Home from './pages/Home';
import Previsoes from './pages/Previsoes';
import Historico from './pages/Historico';
import Mapa from './pages/Mapa';

// Contextos
import { AlertaProvider } from './contexts/AlertaContext';

// Tema da aplicação
const theme = createTheme({
  palette: {
    primary: {
      main: '#0277bd', // Azul escuro
    },
    secondary: {
      main: '#26a69a', // Verde água
    },
    background: {
      default: '#f5f5f5', // Cinza claro para o fundo
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AlertaProvider>
        <Router>
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column',
            minHeight: '100vh'
          }}>
            <Header />
            <Box component="main" sx={{ 
              flexGrow: 1,
              py: 2
            }}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/previsoes" element={<Previsoes />} />
                <Route path="/historico" element={<Historico />} />
                <Route path="/mapa" element={<Mapa />} />
                <Route path="*" element={<h1>Página não encontrada!</h1>} />
              </Routes>
            </Box>
            <Footer />
          </Box>
        </Router>
      </AlertaProvider>
    </ThemeProvider>
  );
}

export default App;
