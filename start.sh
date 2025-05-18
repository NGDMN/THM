#!/bin/bash

# Atualizar pip para a versão mais recente
pip install --upgrade pip

# Instalar pacotes com versões compatíveis com Python 3.11
pip install numpy>=1.22.0
pip install scipy>=1.8.0
pip install pandas>=1.4.0
pip install scikit-learn>=1.0.0
pip install markupsafe
pip install werkzeug==2.0.3

# Entrar na pasta da API e instalar as dependências do Flask com suas dependências
cd api
pip install Flask==2.0.1 Flask-Cors==3.0.10 python-dotenv==0.19.0 gunicorn==20.1.0

# Iniciar a API usando o módulo api.app
cd ..
export PYTHONPATH=$PYTHONPATH:$(pwd)
gunicorn api.app:app --bind 0.0.0.0:$PORT 