#!/bin/bash

# Definir flag para usar versões binárias do numpy e outras bibliotecas
export PIP_ONLY_BINARY=numpy,scipy,pandas,scikit-learn

# Atualizar pip e instalar dependências
pip install --upgrade pip

# Entrar na pasta da API e instalar dependências
cd api
pip install -r requirements.txt

# Iniciar a API
gunicorn app:app --bind 0.0.0.0:$PORT 