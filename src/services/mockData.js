// Mock data para teste do frontend

// Dados de previsão de chuvas (7 dias)
export const mockPrevisaoChuvas = {
  'RJ': {
    'Rio de Janeiro': [
      { data: '2025-05-18', precipitacao: 15.2 },
      { data: '2025-05-19', precipitacao: 32.7 },
      { data: '2025-05-20', precipitacao: 45.1 },
      { data: '2025-05-21', precipitacao: 60.3 },
      { data: '2025-05-22', precipitacao: 25.8 },
      { data: '2025-05-23', precipitacao: 12.4 },
      { data: '2025-05-24', precipitacao: 8.6 }
    ],
    'Niterói': [
      { data: '2025-05-18', precipitacao: 12.5 },
      { data: '2025-05-19', precipitacao: 30.2 },
      { data: '2025-05-20', precipitacao: 42.7 },
      { data: '2025-05-21', precipitacao: 55.1 },
      { data: '2025-05-22', precipitacao: 22.4 },
      { data: '2025-05-23', precipitacao: 10.6 },
      { data: '2025-05-24', precipitacao: 7.8 }
    ]
  },
  'SP': {
    'São Paulo': [
      { data: '2025-05-18', precipitacao: 5.2 },
      { data: '2025-05-19', precipitacao: 22.7 },
      { data: '2025-05-20', precipitacao: 38.1 },
      { data: '2025-05-21', precipitacao: 42.3 },
      { data: '2025-05-22', precipitacao: 15.8 },
      { data: '2025-05-23', precipitacao: 8.4 },
      { data: '2025-05-24', precipitacao: 2.6 }
    ],
    'Campinas': [
      { data: '2025-05-18', precipitacao: 3.2 },
      { data: '2025-05-19', precipitacao: 18.7 },
      { data: '2025-05-20', precipitacao: 35.1 },
      { data: '2025-05-21', precipitacao: 38.3 },
      { data: '2025-05-22', precipitacao: 12.8 },
      { data: '2025-05-23', precipitacao: 6.4 },
      { data: '2025-05-24', precipitacao: 1.6 }
    ]
  }
};

// Pontos de alagamento
export const mockPontosAlagamento = {
  'RJ': {
    'Rio de Janeiro': [
      {
        latitude: -22.9068,
        longitude: -43.1729,
        local: 'Centro - Praça da Bandeira',
        nivelRisco: 'alto',
        precipitacaoPrevista: 60.3,
        ultimoAlagamento: '2025-04-15',
        raioAfetado: 350
      },
      {
        latitude: -22.9340,
        longitude: -43.1865,
        local: 'Botafogo - Rua São Clemente',
        nivelRisco: 'médio',
        precipitacaoPrevista: 32.7,
        ultimoAlagamento: '2025-03-22',
        raioAfetado: 250
      },
      {
        latitude: -22.9771,
        longitude: -43.3958,
        local: 'Barra da Tijuca - Av. Ayrton Senna',
        nivelRisco: 'baixo',
        precipitacaoPrevista: 25.8,
        ultimoAlagamento: '2025-02-10',
        raioAfetado: 200
      }
    ],
    'Niterói': [
      {
        latitude: -22.8859,
        longitude: -43.1152,
        local: 'Centro - Rua da Conceição',
        nivelRisco: 'médio',
        precipitacaoPrevista: 42.7,
        ultimoAlagamento: '2025-04-02',
        raioAfetado: 280
      }
    ]
  },
  'SP': {
    'São Paulo': [
      {
        latitude: -23.5505,
        longitude: -46.6333,
        local: 'Centro - Praça da Sé',
        nivelRisco: 'alto',
        precipitacaoPrevista: 42.3,
        ultimoAlagamento: '2025-04-10',
        raioAfetado: 400
      },
      {
        latitude: -23.5990,
        longitude: -46.6821,
        local: 'Pinheiros - Av. Rebouças',
        nivelRisco: 'médio',
        precipitacaoPrevista: 38.1,
        ultimoAlagamento: '2025-03-15',
        raioAfetado: 300
      }
    ],
    'Campinas': [
      {
        latitude: -22.9071,
        longitude: -47.0625,
        local: 'Centro - Av. Francisco Glicério',
        nivelRisco: 'baixo',
        precipitacaoPrevista: 35.1,
        ultimoAlagamento: '2025-02-28',
        raioAfetado: 180
      }
    ]
  }
};

// Previsão de alagamentos
export const mockPrevisaoAlagamentos = {
  'RJ': {
    'Rio de Janeiro': {
      probabilidade: 0.85,
      nivelRisco: 'alto',
      recomendacoes: [
        'Evite áreas marcadas em vermelho no mapa',
        'Mantenha-se informado sobre alertas da Defesa Civil',
        'Tenha um plano de emergência preparado'
      ],
      areasAfetadas: [
        'Praça da Bandeira', 
        'Maracanã', 
        'Tijuca (Parte baixa)'
      ]
    },
    'Niterói': {
      probabilidade: 0.65,
      nivelRisco: 'médio',
      recomendacoes: [
        'Esteja atento às previsões meteorológicas',
        'Evite áreas com histórico de alagamentos'
      ],
      areasAfetadas: [
        'Centro',
        'São Domingos'
      ]
    }
  },
  'SP': {
    'São Paulo': {
      probabilidade: 0.70,
      nivelRisco: 'médio',
      recomendacoes: [
        'Evite cruzar áreas alagadas',
        'Mantenha-se informado sobre alertas da Defesa Civil'
      ],
      areasAfetadas: [
        'Pinheiros',
        'Sé',
        'Lapa'
      ]
    },
    'Campinas': {
      probabilidade: 0.40,
      nivelRisco: 'baixo',
      recomendacoes: [
        'Esteja atento às previsões meteorológicas'
      ],
      areasAfetadas: [
        'Centro'
      ]
    }
  }
}; 