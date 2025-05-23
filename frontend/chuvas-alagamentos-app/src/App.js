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

// Contextos
import { AlertaProvider } from './contexts/AlertaContext';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
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
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/previsoes" element={<Previsoes />} />
            <Route path="/historico" element={<Historico />} />
            <Route path="/sobre" element={<Sobre />} />
          </Routes>
          <Footer />
        </Router>
      </AlertaProvider>
    </ThemeProvider>
  );
}

export default App;
