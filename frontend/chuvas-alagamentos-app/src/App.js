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
      main: '#1B4F72', // Azul Cobalto
      dark: '#325F7E',
      light: '#496F8A',
      contrastText: '#F5F9FC', // Branco Azulado
    },
    secondary: {
      main: '#CB6D51', // Cobre Metálico
      dark: '#D07D64',
      light: '#D58D77',
    },
    background: {
      default: '#F5F9FC', // Branco Azulado
      paper: '#E5E4E2',   // Platina
    },
    text: {
      primary: '#1B4F72',
      secondary: '#CB6D51',
    },
  },
  typography: {
    fontFamily: 'Neue Haas Grotesk, Arial, sans-serif',
    h1: { fontWeight: 700, fontSize: '3rem', lineHeight: 1.2 },
    h2: { fontWeight: 600, fontSize: '2.25rem', lineHeight: 1.2 },
    h3: { fontWeight: 600, fontSize: '1.5rem', lineHeight: 1.2 },
    h4: { fontWeight: 600, fontSize: '1.25rem', lineHeight: 1.2 },
    body1: { fontSize: '1rem', lineHeight: 1.5 },
    body2: { fontSize: '0.875rem', lineHeight: 1.5 },
  },
  spacing: 8, // 8px base
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1B4F72',
          color: '#F5F9FC',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          textTransform: 'none',
          fontWeight: 600,
          padding: '0.75rem 1.5rem',
          backgroundColor: '#CB6D51',
          color: '#F5F9FC',
          '&:hover': {
            backgroundColor: '#D07D64',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
          backgroundColor: '#E5E4E2',
        },
      },
    },
    MuiContainer: {
      styleOverrides: {
        root: {
          paddingTop: '100px',
          paddingBottom: '80px',
        },
      },
    },
    MuiTypography: {
      styleOverrides: {
        root: {
          color: '#1B4F72',
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          backgroundColor: '#F5F9FC',
        },
        indicator: {
          backgroundColor: '#CB6D51',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          color: '#1B4F72',
          '&.Mui-selected': {
            color: '#CB6D51',
          },
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
          <div className="App">
            <Header />
            <div className="App-content">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/previsoes" element={<Previsoes />} />
                <Route path="/historico" element={<Historico />} />
                <Route path="/recomendacoes" element={<Recomendacoes />} />
                <Route path="*" element={<h1>Página não encontrada!</h1>} />
              </Routes>
            </div>
            <Footer />
          </div>
        </Router>
      </AlertaProvider>
    </ThemeProvider>
  );
}

export default App;
