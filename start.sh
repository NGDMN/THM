#!/bin/bash

# Atualizar pip e instalar dependências binarias
pip install --upgrade pip
pip install -r requirements-deploy.txt

# Iniciar a API
cd api
gunicorn app:app --bind 0.0.0.0:$PORT 