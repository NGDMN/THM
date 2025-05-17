@echo off
echo Iniciando a API do Sistema de Previsao de Alagamentos RJ/SP...
echo.

REM Verificar se o Python esta instalado
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Python nao encontrado! Instale o Python 3.7 ou superior.
    echo.
    pause
    exit /b 1
)

REM Verificar se o ambiente virtual existe, se nao, criar
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

REM Definir variaveis de ambiente
set FLASK_APP=app.py 
set FLASK_ENV=development

echo.
echo API iniciada com sucesso! Acesse: http://localhost:5000
echo Para interromper, pressione CTRL+C
echo.

REM Iniciar a API
python -m flask run 