import React from 'react';
import { Box } from '@mui/material';

// SVG Pattern inline (baseado no manual de identidade)
const HexagonPattern = ({ opacity = 0.1, size = 80, variant = 'default' }) => {
  const getSizeVariation = () => {
    switch (variant) {
      case 'hero': return size * 1.5;
      case 'dense': return size * 0.75;
      case 'sparse': return size * 1.25;
      default: return size;
    }
  };
  
  const actualSize = getSizeVariation();
  
  return (
    <Box
      sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: -1,
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3e%3cpolygon points='50,15 75,30 75,60 50,75 25,60 25,30' fill='none' stroke='%23${variant === 'hero' ? '1B4F72' : 'CB6D51'}' stroke-width='0.8' opacity='${opacity}'/%3e%3c/svg%3e")`,
          backgroundSize: `${actualSize}px ${actualSize}px`,
          backgroundRepeat: 'repeat',
          animation: variant === 'hero' ? 'patternFloat 20s linear infinite' : 'none',
        },
        '@keyframes patternFloat': {
          '0%': {
            transform: 'translateX(0) translateY(0)',
          },
          '100%': {
            transform: `translateX(-${actualSize}px) translateY(-${actualSize}px)`,
          },
        },
      }}
    />
  );
};

// Componente principal PatternBackground
const PatternBackground = ({ 
  children, 
  variant = 'default', 
  opacity = 0.1, 
  size = 80,
  overlay = false,
  overlayColor = 'rgba(255, 255, 255, 0.05)'
}) => {
  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: '100vh',
        width: '100%',
      }}
    >
      <HexagonPattern variant={variant} opacity={opacity} size={size} />
      
      {overlay && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: overlayColor,
            zIndex: 0,
          }}
        />
      )}
      
      <Box sx={{ position: 'relative', zIndex: 1 }}>
        {children}
      </Box>
    </Box>
  );
};

// Presets para diferentes seções
export const PATTERN_PRESETS = {
  hero: {
    variant: 'hero',
    opacity: 0.15,
    size: 120,
    overlay: true,
    overlayColor: 'rgba(27, 79, 114, 0.02)'
  },
  content: {
    variant: 'default',
    opacity: 0.08,
    size: 80,
    overlay: false
  },
  dense: {
    variant: 'dense',
    opacity: 0.05,
    size: 60,
    overlay: false
  },
  sparse: {
    variant: 'sparse',
    opacity: 0.12,
    size: 100,
    overlay: true,
    overlayColor: 'rgba(203, 109, 81, 0.02)'
  }
};

// Export padrão
export default PatternBackground;