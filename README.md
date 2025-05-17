# Sistema de Previsão de Alagamentos (RJ/SP)

Sistema completo para processamento de dados, análise e previsão de alagamentos nos estados do Rio de Janeiro e São Paulo, incluindo backend em Python, API REST com Flask e frontend em React.

## Visão Geral

Este projeto:
- Processa dados históricos de precipitação do INMET para RJ e SP
- Analisa registros de alagamentos do S2iD
- Correlaciona chuvas com ocorrências de alagamentos
- Armazena os dados processados em Oracle Database
- Fornece API REST para acesso aos dados e previsões
- Apresenta interface web interativa com visualizações e mapas

## Arquitetura do Sistema

O sistema é composto por três componentes principais:

1. **Backend Python de Processamento de Dados**
   - Scripts para processamento e análise de dados
   - Conexão com banco de dados Oracle
   - Geração de insights e correlações estatísticas

2. **API REST**
   - Intermediária entre o banco Oracle e o frontend
   - Endpoints para previsão e histórico
   - Suporte a modo simulado para desenvolvimento

3. **Frontend React**
   - Dashboard interativo com Material UI
   - Mapas de pontos de alagamento com Leaflet
   - Gráficos de previsão com Chart.js

## Estrutura de Diretórios

```
sistema-alagamentos/
├── api/                    # API REST em Flask
│   ├── app.py              # Aplicação principal
│   ├── config.py           # Configurações
│   ├── models/             # Modelos de dados
│   ├── routes/             # Rotas da API
│   ├── services/           # Serviços de processamento
│   ├── utils/              # Utilitários
│   └── requirements.txt    # Dependências
├── frontend/               # Frontend React
│   ├── public/             # Arquivos públicos
│   ├── src/                # Código fonte
│   │   ├── components/     # Componentes React
│   │   ├── services/       # Comunicação com API
│   │   └── App.js          # Componente principal
│   └── package.json        # Dependências
├── scripts/                # Scripts de processamento
│   ├── instalar_dependencias.py
│   ├── script_principal.py
│   └── executar_*.bat      # Scripts batch
├── config/                 # Configurações Oracle
│   ├── setup_oracle_connection.py
│   └── sqlnet.ora
├── data/                   # Dados processados
│   ├── alagamentos_com_precipitacao.csv
│   └── previsoes_chuva.csv
└── README.md               # Documentação
```

## Pré-requisitos

### Geral
- Python 3.7+
- Node.js 14+ e npm
- Git

### Backend e API
- Oracle Instant Client 23.8+
- Oracle Wallet configurado
- Acesso a um Oracle Database (nível gratuito é suficiente)

### Frontend
- Navegador moderno com suporte a ES6+

## Instalação e Configuração

### 1. Configuração do Backend e API

#### 1.1 Instalação de Dependências Python

```bash
# Navegar até o diretório raiz
cd sistema-alagamentos

# Instalar dependências
python scripts/instalar_dependencias.py
```

#### 1.2 Configuração do Oracle Database

1. Crie uma conta na [Oracle Cloud](https://www.oracle.com/br/cloud/free/)
2. Configure um Banco de Dados Autônomo
3. Baixe o Oracle Wallet para seu diretório local
4. Configure as credenciais:

```bash
# Configurar conexão Oracle
python config/setup_oracle_connection.py
```

#### 1.3 Configuração da API

```bash
# Navegar até o diretório da API
cd api

# Criar e ativar ambiente virtual
python -m venv venv
.\venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

Crie um arquivo `.env` na pasta `api/` com:

```
FLASK_APP=app.py
FLASK_ENV=development
ORACLE_USER=ADMIN
ORACLE_PASSWORD=SuaSenhaAqui
ORACLE_DSN=chuvasalagamentos_high
TNS_ADMIN=C:\Users\SeuUsuario\OracleWallet
```

### 2. Configuração do Frontend

```bash
# Navegar até o diretório do frontend
cd frontend/chuvas-alagamentos-app

# Instalar dependências
npm install
```

## Executando o Sistema

### Iniciar o Backend de Processamento

```bash
# Executar scripts de processamento
python scripts/script_principal.py
```

### Iniciar a API

```bash
# Modo com Banco Oracle
cd api
.\venv\Scripts\activate
flask run

# OU Modo Simulação (sem Oracle)
cd api
.\venv\Scripts\activate
set USE_MOCK_DATA=True
flask run
```

### Iniciar o Frontend

```bash
cd frontend/chuvas-alagamentos-app
npm start
```

O aplicativo será aberto em http://localhost:3000

## Endpoints da API

Todos os endpoints disponíveis:

- `GET /api/previsao/chuvas?cidade={cidade}&estado={estado}`
- `GET /api/previsao/alagamentos?cidade={cidade}&estado={estado}`
- `GET /api/historico/chuvas?cidade={cidade}&estado={estado}&dataInicio={dataInicio}&dataFim={dataFim}`
- `GET /api/historico/alagamentos?cidade={cidade}&estado={estado}&dataInicio={dataInicio}&dataFim={dataFim}`
- `GET /api/historico/pontos/alagamentos?cidade={cidade}&estado={estado}`

## Deploy

### Deploy da API

A API Flask pode ser hospedada em:
- Heroku
- PythonAnywhere
- Azure App Service
- AWS Elastic Beanstalk

### Deploy do Frontend

O frontend React pode ser facilmente implantado no Vercel:

```bash
# Instalar Vercel CLI
npm install -g vercel

# Navegue até o diretório do frontend
cd frontend/chuvas-alagamentos-app

# Fazer deploy
vercel
```

## Banco de Dados

O projeto utiliza três tabelas principais no Oracle Database:

1. **chuvas_diarias**:
   - `municipio VARCHAR2(100)`
   - `data DATE`
   - `precipitacao_diaria NUMBER`

2. **alagamentos**:
   - `municipio VARCHAR2(100)`
   - `data DATE`
   - `populacao NUMBER`
   - `dh_mortos NUMBER`

3. **chuvas_alagamentos**:
   - `municipio VARCHAR2(100)`
   - `data DATE`
   - `precipitacao_diaria NUMBER`
   - `populacao NUMBER`
   - `dh_mortos NUMBER`

## Modelo Preditivo

O sistema utiliza modelos estatísticos para prever probabilidades de alagamentos baseado em:
1. Dados históricos de precipitação
2. Ocorrências passadas de alagamentos
3. Características geográficas das regiões
4. Padrões sazonais

## Principais Funcionalidades do Frontend

1. **Dashboard Interativo**
   - Visão geral dos dados de precipitação e risco de alagamentos
   - Seleção de cidade e estado para análise específica

2. **Mapa de Pontos de Alagamento**
   - Visualização geográfica de pontos críticos
   - Níveis de risco codificados por cores

3. **Gráficos de Previsão**
   - Previsão de precipitação para os próximos 7 dias
   - Histórico de chuvas para análise

4. **Análise de Risco**
   - Indicadores de probabilidade de alagamento
   - Recomendações baseadas nos níveis de risco

## Solução de Problemas

### Erros comuns de conexão Oracle:

- **DPI-1047: Cannot locate Oracle Client**  
  Verifique se o Oracle Instant Client está no PATH

- **ORA-01017: invalid username/password**  
  Verifique as credenciais no arquivo .env

- **ORA-28759: failure to open file**  
  Verifique a configuração do Oracle Wallet

## Contribuições e Desenvolvimento

1. Clone o repositório
2. Crie um branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça suas alterações
4. Commit e push (`git push origin feature/nova-funcionalidade`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT. 