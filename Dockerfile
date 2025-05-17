FROM python:3.9-slim

WORKDIR /app

# Copiar apenas os arquivos necessários para instalar dependências
COPY requirements.txt .

# Instalar dependências
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código
COPY . .

# Expor a porta que será usada pelo Gunicorn
EXPOSE 8000

# Definir variáveis de ambiente
ENV FLASK_APP=api/app.py
ENV FLASK_ENV=production
ENV USE_MOCK_DATA=True

# Comando para iniciar a aplicação
CMD gunicorn --chdir api app:app --bind 0.0.0.0:$PORT 