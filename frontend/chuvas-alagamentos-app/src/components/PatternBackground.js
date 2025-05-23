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

// ... (restante do código igual ao arquivo original)
// ... existing code ... 