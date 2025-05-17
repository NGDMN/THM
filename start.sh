#!/bin/bash

# Atualizar pip para a versão mais recente
pip install --upgrade pip

# Instalar numpy com constraints para forçar binário
pip install -c constraints.txt numpy==1.19.5

# Entrar na pasta da API e instalar dependências (sem numpy que já foi instalado)
cd api
pip install --no-deps -r requirements.txt

# Iniciar a API
gunicorn app:app --bind 0.0.0.0:$PORT 