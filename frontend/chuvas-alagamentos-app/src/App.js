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
import Recomendacoes from './pages/Recomendacoes';

// Contextos
import { AlertaProvider } from './contexts/AlertaContext';

// Tema da aplicação
const theme = createTheme({
  palette: {
    primary: {
      main: '#1B4F72', // Azul escuro
    },
    secondary: {
      main: '#CB6D51', // Laranja
    },
    background: {
      default: '#F5F9FC', // Cinza claro para o fundo
    },
    error: {
      main: '#d32f2f', // Vermelho para alertas de erro
      light: '#ffebee', // Vermelho claro para fundo
    },
    warning: {
      main: '#ed6c02', // Laranja para alertas de aviso
      light: '#fff8e1', // Laranja claro para fundo
    },
    info: {
      main: '#0288d1', // Azul para alertas de informação
      light: '#e3f2fd', // Azul claro para fundo
    },
    success: {
      main: '#2e7d32', // Verde para alertas de sucesso
      light: '#e8f5e9', // Verde claro para fundo
    },
  },
  typography: {
    fontFamily: [
      'Neue Haas Grotesk',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontWeight: 700,
      fontSize: '3rem',
      lineHeight: 1.2,
      color: '#1B4F72',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2.25rem',
      lineHeight: 1.2,
      color: '#1B4F72',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
      lineHeight: 1.2,
      color: '#1B4F72',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.2,
      color: '#1B4F72',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.2,
      color: '#1B4F72',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
      lineHeight: 1.2,
      color: '#1B4F72',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
      color: '#1B4F72',
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
      color: '#1B4F72',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          textTransform: 'none',
          fontWeight: 600,
          padding: '0.75rem 1.5rem',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1B4F72',
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
        },
      },
    },
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
                <Route path="/recomendacoes" element={<Recomendacoes />} />
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
