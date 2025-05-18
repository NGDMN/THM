#!/bin/bash

# Atualizar pip para a versão mais recente
pip install --upgrade pip

# Instalar numpy, scipy, pandas e scikit-learn com constraints
pip install -c constraints.txt numpy==1.19.5
pip install -c constraints.txt scipy==1.5.4
pip install -c constraints.txt pandas==1.1.5
pip install -c constraints.txt scikit-learn==0.24.2

# Entrar na pasta da API e instalar as dependências restantes
cd api
pip install --no-deps gunicorn==20.1.0 Flask==2.0.1 Flask-Cors==3.0.10 python-dotenv==0.19.0

# Iniciar a API
gunicorn app:app --bind 0.0.0.0:$PORT 