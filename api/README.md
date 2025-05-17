# API - Sistema de Previsão de Alagamentos RJ/SP

API RESTful para fornecer dados processados sobre previsões de chuvas e alagamentos para o frontend.

## Tecnologias

- **Python 3.7+** - Linguagem de programação principal
- **Flask** - Framework web para desenvolvimento da API
- **SQLAlchemy** - ORM para comunicação com o banco de dados Oracle
- **cx_Oracle** - Driver de conexão Oracle
- **pandas** - Processamento de dados
- **scikit-learn** - Modelos de previsão

## Estrutura da API

```
api/
├── app.py                   # Aplicação principal Flask
├── config.py                # Configurações
├── models/                  # Modelos de dados
│   ├── __init__.py
│   ├── chuvas.py
│   └── alagamentos.py
├── routes/                  # Rotas da API
│   ├── __init__.py
│   ├── previsao.py
│   └── historico.py
├── services/                # Serviços de processamento
│   ├── __init__.py
│   ├── meteo_service.py
│   └── previsao_service.py
├── utils/                   # Utilitários
│   ├── __init__.py
│   └── db_utils.py
└── requirements.txt         # Dependências
```

## Endpoints da API

### Previsão de Chuvas

```
GET /api/previsao/chuvas?cidade={cidade}&estado={estado}
```

Retorna a previsão de precipitação para os próximos 7 dias na cidade/estado especificados.

### Histórico de Chuvas

```
GET /api/historico/chuvas?cidade={cidade}&estado={estado}&dataInicio={dataInicio}&dataFim={dataFim}
```

Retorna dados históricos de precipitação para o período especificado.

### Previsão de Alagamentos

```
GET /api/previsao/alagamentos?cidade={cidade}&estado={estado}
```

Retorna a previsão de risco de alagamentos para a cidade/estado especificados.

### Histórico de Alagamentos

```
GET /api/historico/alagamentos?cidade={cidade}&estado={estado}&dataInicio={dataInicio}&dataFim={dataFim}
```

Retorna dados históricos de ocorrências de alagamentos para o período especificado.

### Pontos de Alagamento

```
GET /api/historico/pontos/alagamentos?cidade={cidade}&estado={estado}
```

Retorna os pontos de alagamento conhecidos com seus respectivos níveis de risco.

## Configuração do Ambiente

### Pré-requisitos

- Python 3.7+
- Oracle Client instalado
- Oracle Wallet configurado

### Instalação

```bash
# Criar e ativar ambiente virtual
python -m venv venv
.\venv\Scripts\activate  # No Windows

# Instalar dependências
pip install -r requirements.txt
```

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do diretório `api` com as seguintes variáveis:

```
FLASK_APP=app.py
FLASK_ENV=development
ORACLE_USER=ADMIN
ORACLE_PASSWORD=SuaSenhaAqui
ORACLE_DSN=chuvasalagamentos_high
TNS_ADMIN=C:\Users\SeuUsuario\OracleWallet
```

### Executando a API

```bash
# Iniciar a API em modo desenvolvimento
flask run
```

A API estará disponível em http://localhost:5000

## Integração com o Banco de Dados

Esta API se conecta ao banco de dados Oracle configurado anteriormente, acessando as tabelas:

1. **chuvas_diarias** - Dados diários de precipitação
2. **alagamentos** - Registros de ocorrências de alagamentos
3. **chuvas_alagamentos** - Dados correlacionados

## Desenvolvimento e Testes

Durante o desenvolvimento, a API pode funcionar sem conexão real ao banco de dados, usando dados simulados gerados pelos modelos. Isso facilita o desenvolvimento enquanto a infraestrutura de banco de dados está sendo configurada.

### Executando sem Oracle (modo de desenvolvimento)

Se você não tiver a configuração Oracle completa, a API ainda funcionará com dados simulados:

```bash
# Definir FLAG de dados simulados
set USE_MOCK_DATA=True
flask run
```

## Integrando com o Frontend

Para integrar a API com o frontend React, atualize o arquivo `frontend/src/services/api.js` alterando a constante `USE_MOCK_DATA` para `false`:

```javascript
// Alterar de true para false quando a API estiver pronta
const USE_MOCK_DATA = false;
```

## Modelo Preditivo

O sistema utiliza machine learning para prever probabilidades de alagamentos baseado em:

1. Dados históricos de precipitação
2. Ocorrências passadas de alagamentos
3. Características geográficas das regiões
4. Padrões sazonais

Os modelos são treinados periodicamente com novos dados para melhorar a precisão das previsões. 