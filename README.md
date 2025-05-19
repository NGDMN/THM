# Sistema de Previsão de Alagamentos RJ/SP

Sistema completo para previsão de chuvas e alagamentos nas regiões do Rio de Janeiro e São Paulo.

## Índice
- [Visão Geral](#visão-geral)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação e Configuração](#instalação-e-configuração)
- [Documentação da API](#documentação-da-api)
- [Frontend](#frontend)
- [Banco de Dados](#banco-de-dados)
- [Desenvolvimento](#desenvolvimento)
- [Deploy](#deploy)
- [Contribuição](#contribuição)

## Visão Geral

O sistema é composto por três componentes principais:

1. **Backend Python**
   - Processamento de dados meteorológicos
   - Análise estatística
   - Modelos preditivos

2. **API REST**
   - Interface entre frontend e backend
   - Endpoints para dados e previsões
   - Suporte a modo simulado

3. **Frontend React**
   - Dashboard interativo
   - Visualizações em tempo real
   - Gráficos de previsão e histórico
   - Alertas em tempo real
   - Seleção de cidade e estado para análise

## Estrutura do Projeto

```
.
├── api/                    # Backend em Python/Flask
│   ├── app.py             # Aplicação principal
│   ├── models/            # Modelos de dados
│   ├── routes/            # Rotas da API
│   ├── services/          # Serviços
│   └── utils/             # Utilitários
├── frontend/              # Frontend em React
│   ├── public/            # Arquivos públicos
│   └── src/               # Código fonte
├── scripts/               # Scripts de utilidade
└── README.md              # Documentação principal
```

## Tecnologias Utilizadas

### Backend (API)
- Python 3.7+
- Flask
- pandas
- scikit-learn
- psycopg2-binary
- APScheduler

### Frontend
- React
- Material-UI
- Chart.js / Recharts
- Axios
- React Router
- Date-fns

## Instalação e Configuração

### Pré-requisitos
- Python 3.7+
- Node.js 14+
- PostgreSQL (produção)

### Backend
```bash
# Criar e ativar ambiente virtual
python -m venv venv
.\venv\Scripts\activate  # No Windows

# Instalar dependências
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend/chuvas-alagamentos-app
npm install
```

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto (UTF-8):
```
DB_NAME=thm_iy9l
DB_USER=thm_admin
DB_PASSWORD=SuaSenhaAqui
DB_HOST=dpg-d0l48cre5dus73c970sg-a.ohio-postgres.render.com
DB_PORT=5432
OPENWEATHER_API_KEY=SuaChaveAqui
FLASK_APP=api/app.py
FLASK_ENV=production
PORT=10000
```

## Documentação da API

### Endpoints Disponíveis

#### Previsão de Chuvas
```
GET /previsao/chuvas?cidade={cidade}&estado={estado}
```
Retorna a previsão de precipitação para os próximos 7 dias.

#### Histórico de Chuvas
```
GET /historico/chuvas?cidade={cidade}&estado={estado}&dataInicio={dataInicio}&dataFim={dataFim}
```
Retorna dados históricos de precipitação.

#### Previsão de Alagamentos
```
GET /previsao/alagamentos?cidade={cidade}&estado={estado}
```
Retorna a previsão de risco de alagamentos.

#### Histórico de Alagamentos
```
GET /historico/alagamentos?cidade={cidade}&estado={estado}&dataInicio={dataInicio}&dataFim={dataFim}
```
Retorna dados históricos de ocorrências de alagamentos.

#### Pontos de Alagamento
```
GET /historico/pontos/alagamentos?cidade={cidade}&estado={estado}
```
Retorna os pontos de alagamento conhecidos.

## Frontend

### Executando o Frontend
```bash
cd frontend/chuvas-alagamentos-app
npm start
```
O aplicativo estará disponível em http://localhost:3000

### Principais Funcionalidades
- Dashboard interativo
- Gráficos de previsão e histórico
- Seleção dinâmica de cidade e estado
- Recomendações em caso de risco
- Alertas em tempo real

### Build para Produção
```bash
npm run build
```

## Banco de Dados

### Estrutura
A API se conecta ao PostgreSQL, acessando as tabelas:
- chuvas_diarias
- alagamentos
- previsoes

## Desenvolvimento

### Modo de Desenvolvimento
Para desenvolvimento sem banco de dados:
```bash
set USE_MOCK_DATA=True
flask run
```

### Testes
```bash
# Backend
pytest

# Frontend
npm test
```

## Deploy

### Backend
```bash
gunicorn api.app:app --bind 0.0.0.0:$PORT
```

### Frontend
```bash
npm run build
```

## Contribuição

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request 