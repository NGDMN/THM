#!/bin/bash

# Instalar todas as dependências do backend
pip install --upgrade pip
pip install -r requirements.txt

# Instalar pacotes específicos (caso precise garantir versões)
pip install numpy>=1.22.0
pip install scipy>=1.8.0
pip install pandas>=1.4.0
pip install scikit-learn>=1.0.0
pip install markupsafe
pip install werkzeug==2.0.3
pip install requests>=2.28.0

# Instalar psycopg2 (necessário para acessar o banco PostgreSQL)
pip install psycopg2-binary || echo "psycopg2 não instalado. Usar modo simulação."

# Entrar na pasta da API e instalar as dependências do Flask com suas dependências
cd api
pip install Flask==2.0.1 Flask-Cors==3.0.10 python-dotenv==0.19.0 gunicorn==20.1.0

# Configurar variáveis de ambiente para modo simulação caso não seja possível instalar psycopg2
if ! python -c "import psycopg2" &> /dev/null; then
    echo "psycopg2 não disponível. Ativando modo de simulação."
    export USE_MOCK_DATA=True
fi

# Iniciar a API usando o módulo api.app
cd ..
export PYTHONPATH=$PYTHONPATH:$(pwd)
gunicorn api.app:app --bind 0.0.0.0:$PORT 