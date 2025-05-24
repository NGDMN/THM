import { createTheme } from '@mui/material/styles';

// Cores exatas do Manual de Identidade Visual
const BRAND_COLORS = {
  // Cores Principais
  azulCobalto: {
    main: '#1B4F72',
    90: '#325F7E',
    80: '#496F8A', 
    70: '#607F96'
  },
  cobreMetalico: {
    main: '#CB6D51',
    90: '#D07D64',
    80: '#D58D77',
    70: '#DA9D8A'
  },
  // Cores Secundárias
  platina: {
    main: '#E5E4E2',
    90: '#E8E7E5',
    80: '#EBEAE8',
    70: '#EEEDED'
  },
  brancoAzulado: '#F5F9FC'
};

// Tipografia conforme manual - usando fontes web similares
const TYPOGRAPHY_CONFIG = {
  fontFamily: [
    '"Helvetica Neue"',
    '"Inter"',
    '"Roboto"',
    '-apple-system',
    'BlinkMacSystemFont',
    '"Segoe UI"',
    'Arial',
    'sans-serif'
  ].join(','),
  h1: {
    fontSize: '3rem',
    fontWeight: 700,
    lineHeight: 1.2,
    letterSpacing: '-0.02em'
  },
  h2: {
    fontSize: '2.25rem',
    fontWeight: 600,
    lineHeight: 1.2,
    letterSpacing: '-0.01em'
  },
  h3: {
    fontSize: '1.5rem',
    fontWeight: 600,
    lineHeight: 1.2
  },
  h4: {
    fontSize: '1.25rem',
    fontWeight: 600,
    lineHeight: 1.3
  },
  h5: {
    fontSize: '1.125rem',
    fontWeight: 500,
    lineHeight: 1.3
  },
  h6: {
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.3
  },
  body1: {
    fontSize: '1rem',
    fontWeight: 400,
    lineHeight: 1.5
  },
  body2: {
    fontSize: '0.875rem',
    fontWeight: 400,
    lineHeight: 1.5
  },
  button: {
    fontSize: '0.875rem',
    fontWeight: 600,
    textTransform: 'none',
    letterSpacing: '0.02em'
  },
  caption: {
    fontSize: '0.75rem',
    fontWeight: 400,
    lineHeight: 1.4
  }
};

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: BRAND_COLORS.azulCobalto.main,
      light: BRAND_COLORS.azulCobalto[70],
      dark: BRAND_COLORS.azulCobalto[90],
      contrastText: BRAND_COLORS.brancoAzulado
    },
    secondary: {
      main: BRAND_COLORS.cobreMetalico.main,
      light: BRAND_COLORS.cobreMetalico[70],
      dark: BRAND_COLORS.cobreMetalico[90],
      contrastText: BRAND_COLORS.brancoAzulado
    },
    background: {
      default: BRAND_COLORS.brancoAzulado,
      paper: '#FFFFFF',
      alt: BRAND_COLORS.platina.main
    },
    surface: {
      main: '#FFFFFF',
      variant: BRAND_COLORS.platina[90],
      container: BRAND_COLORS.platina[80]
    },
    text: {
      primary: BRAND_COLORS.azulCobalto.main,
      secondary: BRAND_COLORS.azulCobalto[80],
      disabled: BRAND_COLORS.platina.main,
      hint: BRAND_COLORS.azulCobalto[70]
    },
    success: {
      main: '#4CAF50',
      light: '#81C784',
      dark: '#388E3C'
    },
    warning: {
      main: BRAND_COLORS.cobreMetalico.main,
      light: BRAND_COLORS.cobreMetalico[70],
      dark: BRAND_COLORS.cobreMetalico[90]
    },
    error: {
      main: '#F44336',
      light: '#EF5350',
      dark: '#D32F2F'
    },
    info: {
      main: BRAND_COLORS.azulCobalto[80],
      light: BRAND_COLORS.azulCobalto[70],
      dark: BRAND_COLORS.azulCobalto.main
    },
    grey: {
      50: BRAND_COLORS.brancoAzulado,
      100: BRAND_COLORS.platina[70],
      200: BRAND_COLORS.platina[80],
      300: BRAND_COLORS.platina[90],
      400: BRAND_COLORS.platina.main,
      500: BRAND_COLORS.azulCobalto[70],
      600: BRAND_COLORS.azulCobalto[80],
      700: BRAND_COLORS.azulCobalto[90],
      800: BRAND_COLORS.azulCobalto.main,
      900: '#0F3A5F'
    }
  },
  typography: TYPOGRAPHY_CONFIG,
  spacing: 8,
  shape: {
    borderRadius: 8
  },
  shadows: [
    'none',
    '0px 1px 3px rgba(27, 79, 114, 0.12), 0px 1px 2px rgba(27, 79, 114, 0.08)',
    '0px 1px 5px rgba(27, 79, 114, 0.12), 0px 2px 2px rgba(27, 79, 114, 0.08)',
    '0px 1px 8px rgba(27, 79, 114, 0.12), 0px 3px 4px rgba(27, 79, 114, 0.08)',
    '0px 2px 4px rgba(27, 79, 114, 0.12), 0px 1px 10px rgba(27, 79, 114, 0.08)',
    '0px 3px 5px rgba(27, 79, 114, 0.12), 0px 1px 18px rgba(27, 79, 114, 0.08)',
    '0px 4px 5px rgba(27, 79, 114, 0.12), 0px 1px 10px rgba(27, 79, 114, 0.08)',
    '0px 5px 5px rgba(27, 79, 114, 0.12), 0px 2px 2px rgba(27, 79, 114, 0.08)',
    '0px 5px 6px rgba(27, 79, 114, 0.12), 0px 3px 6px rgba(27, 79, 114, 0.08)',
    '0px 6px 6px rgba(27, 79, 114, 0.12), 0px 3px 6px rgba(27, 79, 114, 0.08)',
    '0px 6px 7px rgba(27, 79, 114, 0.12), 0px 4px 5px rgba(27, 79, 114, 0.08)',
    '0px 7px 8px rgba(27, 79, 114, 0.12), 0px 4px 7px rgba(27, 79, 114, 0.08)',
    '0px 7px 9px rgba(27, 79, 114, 0.12), 0px 4px 7px rgba(27, 79, 114, 0.08)',
    '0px 8px 9px rgba(27, 79, 114, 0.12), 0px 5px 7px rgba(27, 79, 114, 0.08)',
    '0px 8px 10px rgba(27, 79, 114, 0.12), 0px 5px 8px rgba(27, 79, 114, 0.08)',
    '0px 8px 11px rgba(27, 79, 114, 0.12), 0px 5px 8px rgba(27, 79, 114, 0.08)',
    '0px 9px 11px rgba(27, 79, 114, 0.12), 0px 6px 8px rgba(27, 79, 114, 0.08)',
    '0px 9px 12px rgba(27, 79, 114, 0.12), 0px 6px 9px rgba(27, 79, 114, 0.08)',
    '0px 10px 13px rgba(27, 79, 114, 0.12), 0px 6px 9px rgba(27, 79, 114, 0.08)',
    '0px 10px 13px rgba(27, 79, 114, 0.12), 0px 7px 9px rgba(27, 79, 114, 0.08)',
    '0px 11px 14px rgba(27, 79, 114, 0.12), 0px 7px 10px rgba(27, 79, 114, 0.08)',
    '0px 11px 15px rgba(27, 79, 114, 0.12), 0px 7px 10px rgba(27, 79, 114, 0.08)',
    '0px 12px 15px rgba(27, 79, 114, 0.12), 0px 8px 10px rgba(27, 79, 114, 0.08)',
    '0px 12px 16px rgba(27, 79, 114, 0.12), 0px 8px 11px rgba(27, 79, 114, 0.08)',
    '0px 13px 16px rgba(27, 79, 114, 0.12), 0px 8px 11px rgba(27, 79, 114, 0.08)'
  ],
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: BRAND_COLORS.azulCobalto.main,
          color: BRAND_COLORS.brancoAzulado,
          boxShadow: '0px 2px 8px rgba(27, 79, 114, 0.15)'
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          paddingTop: 12,
          paddingBottom: 12,
          paddingLeft: 24,
          paddingRight: 24,
          textTransform: 'none',
          fontWeight: 600,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 4px 12px rgba(27, 79, 114, 0.15)'
          }
        },
        containedPrimary: {
          backgroundColor: BRAND_COLORS.azulCobalto.main,
          color: BRAND_COLORS.brancoAzulado,
          '&:hover': {
            backgroundColor: BRAND_COLORS.azulCobalto[90]
          }
        },
        containedSecondary: {
          backgroundColor: BRAND_COLORS.cobreMetalico.main,
          color: BRAND_COLORS.brancoAzulado,
          '&:hover': {
            backgroundColor: BRAND_COLORS.cobreMetalico[90]
          }
        },
        outlined: {
          borderColor: BRAND_COLORS.azulCobalto.main,
          color: BRAND_COLORS.azulCobalto.main,
          '&:hover': {
            backgroundColor: `${BRAND_COLORS.azulCobalto.main}08`,
            borderColor: BRAND_COLORS.azulCobalto[90]
          }
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0px 4px 20px rgba(27, 79, 114, 0.08)',
          border: `1px solid ${BRAND_COLORS.platina[90]}`,
          '&:hover': {
            boxShadow: '0px 8px 28px rgba(27, 79, 114, 0.12)',
            transform: 'translateY(-2px)',
            transition: 'all 0.3s ease-in-out'
          }
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
          borderRadius: 12
        },
        elevation1: {
          boxShadow: '0px 2px 8px rgba(27, 79, 114, 0.08)'
        }
      }
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          fontWeight: 500
        },
        colorPrimary: {
          backgroundColor: `${BRAND_COLORS.azulCobalto.main}15`,
          color: BRAND_COLORS.azulCobalto.main
        },
        colorSecondary: {
          backgroundColor: `${BRAND_COLORS.cobreMetalico.main}15`,
          color: BRAND_COLORS.cobreMetalico.main
        }
      }
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          border: 'none'
        },
        standardInfo: {
          backgroundColor: `${BRAND_COLORS.azulCobalto.main}10`,
          color: BRAND_COLORS.azulCobalto.main,
          '& .MuiAlert-icon': {
            color: BRAND_COLORS.azulCobalto.main
          }
        },
        standardWarning: {
          backgroundColor: `${BRAND_COLORS.cobreMetalico.main}10`,
          color: BRAND_COLORS.cobreMetalico.main,
          '& .MuiAlert-icon': {
            color: BRAND_COLORS.cobreMetalico.main
          }
        }
      }
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '& fieldset': {
              borderColor: BRAND_COLORS.platina.main
            },
            '&:hover fieldset': {
              borderColor: BRAND_COLORS.azulCobalto[70]
            },
            '&.Mui-focused fieldset': {
              borderColor: BRAND_COLORS.azulCobalto.main
            }
          }
        }
      }
    }
  }
});

// Utilitários para cores da marca
export const brandColors = BRAND_COLORS;

// Função para obter cor com opacidade
export const getColorWithOpacity = (color, opacity) => {
  const hex = color.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};

// Gradientes da marca
export const brandGradients = {
  primary: `linear-gradient(135deg, ${BRAND_COLORS.azulCobalto.main} 0%, ${BRAND_COLORS.azulCobalto[80]} 100%)`,
  secondary: `linear-gradient(135deg, ${BRAND_COLORS.cobreMetalico.main} 0%, ${BRAND_COLORS.cobreMetalico[80]} 100%)`,
  neutral: `linear-gradient(135deg, ${BRAND_COLORS.platina.main} 0%, ${BRAND_COLORS.brancoAzulado} 100%)`,
  hero: `linear-gradient(135deg, ${BRAND_COLORS.brancoAzulado} 0%, ${BRAND_COLORS.platina[70]} 100%)`
};

export default theme; 