import React from 'react';
import { Alert, Box, Typography } from '@mui/material';

const Diagnostico = ({ nome, dados, erro }) => {
  if (erro) {
    return (
      <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
        <Typography variant="subtitle1" component="div">
          ⚠️ Erro ao carregar {nome}:
        </Typography>
        <Typography variant="body2" component="pre" sx={{ mt: 1, fontFamily: 'monospace' }}>
          {erro}
        </Typography>
      </Alert>
    );
  }

  if (!dados || (Array.isArray(dados) && dados.length === 0)) {
    return (
      <Alert severity="warning" sx={{ mt: 2, mb: 2 }}>
        <Typography variant="subtitle1" component="div">
          ⚠️ {nome} não carregado corretamente
        </Typography>
        <Typography variant="body2" component="pre" sx={{ mt: 1, fontFamily: 'monospace' }}>
          {JSON.stringify(dados, null, 2)}
        </Typography>
      </Alert>
    );
  }

  return null;
};

export default Diagnostico; 