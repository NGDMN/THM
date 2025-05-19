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
   - Mapas e gráficos

## Estrutura do Projeto

```
.
├── api/                    # Backend em Python/Flask
│   ├── app.py             # Aplicação principal
│   ├── config.py          # Configurações
│   ├── models/            # Modelos de dados
│   ├── routes/            # Rotas da API
│   ├── services/          # Serviços
│   └── utils/             # Utilitários
├── frontend/              # Frontend em React
│   ├── public/            # Arquivos públicos
│   └── src/               # Código fonte
├── docs/                  # Documentação
└── scripts/              # Scripts de utilidade
```

## Tecnologias Utilizadas

### Backend (API)
- Python 3.7+
- Flask
- SQLAlchemy
- cx_Oracle
- pandas
- scikit-learn

### Frontend
- React
- Material-UI
- Chart.js
- Axios

## Instalação e Configuração

### Pré-requisitos
- Python 3.7+
- Node.js 14+
- Oracle Client
- Oracle Wallet configurado

### Backend
```bash
# Criar e ativar ambiente virtual
python -m venv venv
.\venv\Scripts\activate  # No Windows

# Instalar dependências
pip install -r api/requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do diretório `api`:
```
FLASK_APP=app.py
FLASK_ENV=development
ORACLE_USER=ADMIN
ORACLE_PASSWORD=SuaSenhaAqui
ORACLE_DSN=chuvasalagamentos_high
TNS_ADMIN=C:\Users\SeuUsuario\OracleWallet
```

## Documentação da API

### Endpoints Disponíveis

#### Previsão de Chuvas
```
GET /api/previsao/chuvas?cidade={cidade}&estado={estado}
```
Retorna a previsão de precipitação para os próximos 7 dias.

#### Histórico de Chuvas
```
GET /api/historico/chuvas?cidade={cidade}&estado={estado}&dataInicio={dataInicio}&dataFim={dataFim}
```
Retorna dados históricos de precipitação.

#### Previsão de Alagamentos
```
GET /api/previsao/alagamentos?cidade={cidade}&estado={estado}
```
Retorna a previsão de risco de alagamentos.

#### Histórico de Alagamentos
```
GET /api/historico/alagamentos?cidade={cidade}&estado={estado}&dataInicio={dataInicio}&dataFim={dataFim}
```
Retorna dados históricos de ocorrências de alagamentos.

#### Pontos de Alagamento
```
GET /api/historico/pontos/alagamentos?cidade={cidade}&estado={estado}
```
Retorna os pontos de alagamento conhecidos.

## Frontend

### Executando o Frontend
```bash
cd frontend
npm start
```
O aplicativo estará disponível em http://localhost:3000

### Principais Funcionalidades
- Dashboard interativo
- Visualização de mapas
- Gráficos de previsão
- Histórico de dados
- Alertas em tempo real

## Banco de Dados

### Estrutura
A API se conecta ao Oracle, acessando as tabelas:
- chuvas_diarias
- alagamentos
- chuvas_alagamentos

### Configuração
1. Instale o Oracle Client
2. Configure o Oracle Wallet
3. Configure as variáveis de ambiente

## Desenvolvimento

### Modo de Desenvolvimento
Para desenvolvimento sem Oracle:
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