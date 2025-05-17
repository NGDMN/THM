#!/bin/bash

# Atualizar sistema e instalar dependências
apt-get update -y
apt-get install -y build-essential python3-dev

# Atualizar pip e instalar wheel
pip install --upgrade pip
pip install wheel setuptools

# Instalar numpy separadamente com --only-binary
pip install --only-binary=numpy numpy==1.21.6

# Instalar as demais dependências
pip install --no-build-isolation -r requirements.txt 