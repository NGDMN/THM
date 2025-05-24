import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Previsoes from './pages/Previsoes';
import Historico from './pages/Historico';
import Sobre from './pages/Sobre';
import Footer from './components/Footer';
import Alertas from './pages/Alertas';
import ApiDebugDashboard from './pages/ApiDebugDashboard';
import './App.css';

// Contextos
import { AlertaProvider } from './contexts/AlertaContext';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1B4F72',
      light: '#2C6B94',
      dark: '#0A3D5C',
    },
    secondary: {
      main: '#CB6D51',
      light: '#E08B73',
      dark: '#A55A43',
    },
    warning: {
      main: '#FFA726',
      light: '#FFB851',
      dark: '#F57C00',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          padding: '8px 16px',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 2px 4px rgba(0,0,0,0.2)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0px 2px 4px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0px 4px 8px rgba(0,0,0,0.2)',
          },
        },
      },
    },
  },
  shape: {
    borderRadius: 8,
  },
  spacing: 8,
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AlertaProvider>
        <Router>
          <div className="App">
            <Navbar />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/previsoes" element={<Previsoes />} />
              <Route path="/historico" element={<Historico />} />
              <Route path="/sobre" element={<Sobre />} />
              <Route path="/alertas" element={<Alertas />} />
              <Route path="/debug" element={<ApiDebugDashboard />} />
            </Routes>
            <Footer />
          </div>
        </Router>
      </AlertaProvider>
    </ThemeProvider>
  );
}

export default App;
