# Frontend - Sistema de Previsão de Alagamentos RJ/SP

Interface de usuário para o sistema de previsão de alagamentos nos estados do Rio de Janeiro e São Paulo, baseado em dados históricos de chuvas e ocorrências de alagamentos.

## Tecnologias Utilizadas

- **React** - Biblioteca JavaScript para construção de interfaces
- **Material UI** - Framework de componentes para design moderno
- **React Router** - Gerenciamento de rotas
- **Chart.js** - Visualização de dados e gráficos
- **Leaflet** - Mapas interativos
- **Axios** - Cliente HTTP para comunicação com o backend

## Estrutura do Projeto

```
frontend/
├── public/                  # Arquivos públicos
├── src/                     # Código fonte
│   ├── assets/              # Imagens e recursos estáticos
│   ├── components/          # Componentes React
│   │   ├── Charts/          # Gráficos e visualizações
│   │   ├── Dashboard/       # Layout principal do dashboard
│   │   ├── Layout/          # Componentes de layout
│   │   └── Map/             # Componentes de mapa
│   ├── services/            # Serviços e comunicação com API
│   └── App.js               # Componente principal
└── README.md                # Este arquivo
```

## Principais Funcionalidades

1. **Dashboard Interativo**
   - Visão geral dos dados de precipitação e risco de alagamentos
   - Seleção de cidade e estado para análise específica

2. **Mapa de Pontos de Alagamento**
   - Visualização geográfica de pontos críticos
   - Níveis de risco codificados por cores
   - Informações detalhadas por ponto

3. **Gráficos de Previsão**
   - Previsão de precipitação para os próximos 7 dias
   - Histórico de chuvas para análise

4. **Análise de Risco**
   - Indicadores de probabilidade de alagamento
   - Recomendações baseadas nos níveis de risco

## Iniciando o Projeto

### Instalação

```bash
# Navegar até o diretório do frontend
cd frontend/chuvas-alagamentos-app

# Instalar dependências
npm install
```

### Executando em Desenvolvimento

```bash
# Iniciar servidor de desenvolvimento
npm start
```

O aplicativo será aberto em http://localhost:3000

### Construindo para Produção

```bash
# Construir versão otimizada para produção
npm run build
```

## Integração com o Backend

O frontend se comunica com o backend Python através de uma API REST. Durante o desenvolvimento, estamos usando dados simulados (mock) que podem ser encontrados em `src/services/mockData.js`.

Para alternar entre dados mock e a API real, modifique a constante `USE_MOCK_DATA` em `src/services/api.js`:

```javascript
// True para usar dados de teste, false para usar a API real
const USE_MOCK_DATA = true;
```

## Próximos Passos

- Implementação de autenticação de usuários
- Visualizações comparativas entre diferentes regiões
- Notificações em tempo real sobre riscos iminentes
- Dashboard administrativo para gestão de dados 