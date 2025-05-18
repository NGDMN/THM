# Sistema de Previsão de Alagamentos (RJ/SP)

Sistema completo para processamento de dados, análise e previsão de alagamentos nos estados do Rio de Janeiro e São Paulo, incluindo backend em Python, API REST com Flask e frontend em React.

## Visão Geral

Este projeto:
- Processa dados históricos de precipitação para RJ e SP
- Analisa registros de alagamentos 
- Correlaciona chuvas com ocorrências de alagamentos
- Armazena os dados processados em PostgreSQL
- Fornece API REST para acesso aos dados e previsões
- Apresenta interface web interativa com visualizações e mapas

## Arquitetura do Sistema

O sistema é composto por três componentes principais:

1. **Backend Python de Processamento de Dados**
   - Scripts para processamento e análise de dados
   - Conexão com banco de dados PostgreSQL
   - Geração de insights e correlações estatísticas

2. **API REST**
   - Intermediária entre o banco de dados e o frontend
   - Endpoints para previsão e histórico
   - Suporte a modo simulado para desenvolvimento

3. **Frontend React**
   - Dashboard interativo com Material UI
   - Mapas de pontos de alagamento com Leaflet
   - Gráficos de previsão com Chart.js

## Estrutura de Diretórios

```
thm/
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
│   │   ├── contexts/       # Contextos React
│   │   ├── hooks/          # Hooks customizados
│   │   ├── pages/          # Páginas da aplicação 
│   │   ├── utils/          # Funções utilitárias
│   │   └── App.js          # Componente principal
│   └── package.json        # Dependências
├── scripts/                # Scripts de processamento
│   ├── schema_pg.sql       # Esquema do banco PostgreSQL
│   ├── import_data.py      # Importação de dados históricos
│   ├── update_previsao.py  # Atualização de previsões
│   ├── encontrar_relacao.py # Análise de correlação 
│   ├── setup_db.bat        # Configuração do banco
│   └── thm_executor.bat    # Script unificado
├── data/                   # Dados processados
│   ├── graficos/           # Visualizações geradas
│   └── amostras/           # Amostras de dados
└── README.md               # Documentação
```

## Pré-requisitos

### Geral
- Python 3.8+
- Node.js 14+ e npm
- Git

### Backend e API
- PostgreSQL 12+
- Bibliotecas Python: psycopg2, Flask, pandas, scikit-learn

### Frontend
- Navegador moderno com suporte a ES6+

## Instalação e Configuração

### 1. Configuração do Backend e API

#### 1.1 Instalação do PostgreSQL

1. Baixe e instale o PostgreSQL em [postgresql.org/download](https://www.postgresql.org/download/)
2. Crie um banco de dados chamado "thm"
3. Execute o script `scripts/setup_db.bat` para configurar o banco

Ou use o script unificado:
```bash
# Executar o script unificado
cd scripts
thm_executor.bat
# Selecione a opção 1 para configurar o banco
```

#### 1.2 Instalação de Dependências Python

```bash
# Navegar até o diretório raiz
cd thm

# Instalar dependências
pip install -r api/requirements.txt
```

#### 1.3 Importação de Dados Históricos

```bash
# Usar o script unificado
cd scripts
thm_executor.bat
# Selecione a opção 2 para importar dados
```

#### 1.4 Análise de Relação Chuvas-Alagamentos

```bash
# Usar o script unificado
cd scripts
thm_executor.bat
# Selecione a opção 3 para analisar
```

### 2. Configuração do Frontend

```bash
# Navegar até o diretório do frontend
cd frontend/chuvas-alagamentos-app

# Instalar dependências
npm install
```

## Executando o Sistema

### Iniciar a API

```bash
# Usar o script unificado
cd scripts
thm_executor.bat
# Selecione a opção 5 (modo normal) ou 6 (modo simulação)
```

Ou para deploy:

```bash
# Executar diretamente com gunicorn
gunicorn api.app:app --bind 0.0.0.0:$PORT
```

### Iniciar o Frontend

```bash
cd frontend/chuvas-alagamentos-app
npm start
```

O aplicativo será aberto em http://localhost:3000

## Endpoints da API

- `GET /api/previsao/chuvas?cidade={cidade}&estado={estado}`
- `GET /api/previsao/alagamentos?cidade={cidade}&estado={estado}`
- `GET /api/historico/chuvas?cidade={cidade}&estado={estado}&dataInicio={dataInicio}&dataFim={dataFim}`
- `GET /api/historico/alagamentos?cidade={cidade}&estado={estado}&dataInicio={dataInicio}&dataFim={dataFim}`
- `GET /api/pontos/alagamentos?cidade={cidade}&estado={estado}`

## Deploy

O projeto está configurado para deploy no Render.com, utilizando a seguinte configuração:

1. **Configuração do banco de dados:**
   - Banco PostgreSQL no Render ou em outro provedor
   - Variáveis de ambiente para conexão

2. **Deploy da API:**
   - Build Command: `pip install -r api/requirements.txt`
   - Start Command: `gunicorn api.app:app --bind 0.0.0.0:$PORT`

3. **Variáveis de ambiente:**
   - `PG_DBNAME`: Nome do banco PostgreSQL
   - `PG_USER`: Usuário PostgreSQL
   - `PG_PASSWORD`: Senha PostgreSQL
   - `PG_HOST`: Endereço do servidor PostgreSQL
   - `PG_PORT`: Porta PostgreSQL (padrão 5432)
   - `USE_MOCK_DATA`: "True" para usar dados simulados

## Modo Simulação

O sistema possui um modo de simulação para funcionar mesmo sem acesso ao banco de dados, útil para:

1. Desenvolvimento e testes locais
2. Deploy em ambientes sem acesso a banco de dados
3. Demostração da aplicação

Para ativar, defina a variável de ambiente `USE_MOCK_DATA=True`

## Banco de Dados

O projeto utiliza as seguintes tabelas no PostgreSQL:

1. **chuvas_diarias**:
   - Armazena dados de precipitação por cidade/data
   - Usado para previsões e análise histórica

2. **alagamentos**:
   - Registra ocorrências de alagamentos
   - Inclui localização, gravidade e impactos

3. **parametros_alagamento**:
   - Armazena resultados da análise de correlação
   - Contém limiares e coeficientes por cidade

## Atualização de Dados

O sistema pode ser atualizado diariamente com novos dados:

1. **Dados de previsão de chuva:**
   - Use o script `update_previsao.py`
   - Configure com chave API do Climatempo (opcional)
   - Agende execução diária com agendador de tarefas

2. **Novos registros de alagamentos:**
   - Importe usando `import_data.py`
   - Reanalise relações com `encontrar_relacao.py`

## Modelo Preditivo

O sistema analisa a relação entre precipitação e ocorrência de alagamentos usando:

1. Regressão logística para probabilidade de alagamento
2. Análise de séries temporais para padrões sazonais
3. Cálculo de limiares críticos de precipitação por região

## Sistema de Previsão e Alertas de Alagamentos

O sistema de previsão e alertas de alagamentos é composto por:

1. **Atualização Diária de Previsões**: Uma vez por dia, o sistema busca dados de previsão de chuva da API do Climatempo para os próximos 7 dias (dia atual + 6 dias) e atualiza o banco de dados.

2. **Verificação de Alertas**: Durante a atualização, o sistema verifica se a quantidade de chuva prevista está abaixo ou acima do nível de alerta. Caso a previsão indique precipitação igual ou acima do limiar configurado (atualmente 30mm/dia), o sistema gera um alerta de risco de alagamento para o município.

3. **Exibição de Alertas no Site**: O site consulta a API que, por sua vez, verifica no banco de dados se existem alertas ativos para a região solicitada. Se houver, exibe um aviso de alerta na página inicial.

### Configuração e Execução

Para configurar o sistema de atualização diária:

1. Certifique-se de ter uma chave de API válida do Climatempo e configure-a no arquivo `.env` ou como variável de ambiente:
   ```
   API_CLIMATEMPO_KEY=sua_chave_aqui
   ```

2. Execute o script `scripts/agendar_atualizacao.bat` para agendar a execução diária no Windows Task Scheduler.

3. Para executar a atualização manualmente, use:
   ```
   cd scripts
   python update_previsao.py
   ```

### Parâmetros Configuráveis

Os seguintes parâmetros podem ser ajustados no arquivo `scripts/update_previsao.py`:

- `LIMIAR_ALERTA_CHUVA`: Quantidade de chuva (em mm/dia) que dispara um alerta de alagamento (padrão: 30mm)
- `CIDADES`: Lista de cidades monitoradas com seus respectivos IDs na API do Climatempo

## Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request 