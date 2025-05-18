@echo off
chcp 65001
title Sistema THM - Execução Unificada

REM Diretório base do projeto
set BASE_DIR=%~dp0..

:menu
cls
echo =====================================================
echo   SISTEMA THM - ANÁLISE DE CHUVAS E ALAGAMENTOS
echo =====================================================
echo.
echo Escolha uma opção:
echo.
echo [1] Configurar banco de dados PostgreSQL
echo [2] Importar dados históricos
echo [3] Analisar relação entre chuvas e alagamentos
echo [4] Atualizar previsões de chuva
echo [5] Iniciar API (modo normal)
echo [6] Iniciar API (modo simulação)
echo [7] Verificar ambiente
echo [0] Sair
echo.
set /p opcao="Digite o número da opção desejada: "

if "%opcao%"=="1" goto configurar_banco
if "%opcao%"=="2" goto importar_dados
if "%opcao%"=="3" goto analisar_relacao
if "%opcao%"=="4" goto atualizar_previsoes
if "%opcao%"=="5" goto iniciar_api
if "%opcao%"=="6" goto iniciar_api_simulacao
if "%opcao%"=="7" goto verificar_ambiente
if "%opcao%"=="0" goto fim

echo.
echo Opção inválida. Por favor, tente novamente.
timeout /t 2 >nul
goto menu

:configurar_banco
cls
echo =====================================================
echo   CONFIGURANDO BANCO DE DADOS POSTGRESQL
echo =====================================================
echo.

cd %BASE_DIR%\scripts
call setup_db.bat

echo.
pause
goto menu

:importar_dados
cls
echo =====================================================
echo   IMPORTAR DADOS HISTÓRICOS
echo =====================================================
echo.

cd %BASE_DIR%\scripts

echo Selecione o tipo de dados a importar:
echo [1] Dados de chuvas
echo [2] Dados de alagamentos
echo [0] Voltar
echo.
set /p tipo_dados="Escolha: "

if "%tipo_dados%"=="1" (
    set /p arquivo="Digite o caminho do arquivo CSV de chuvas: "
    python import_data.py chuvas "%arquivo%"
) else if "%tipo_dados%"=="2" (
    set /p arquivo="Digite o caminho do arquivo CSV de alagamentos: "
    python import_data.py alagamentos "%arquivo%"
) else if "%tipo_dados%"=="0" (
    goto menu
) else (
    echo Opção inválida!
)

echo.
pause
goto menu

:analisar_relacao
cls
echo =====================================================
echo   ANALISAR RELAÇÃO ENTRE CHUVAS E ALAGAMENTOS
echo =====================================================
echo.

cd %BASE_DIR%\scripts
python encontrar_relacao.py

echo.
pause
goto menu

:atualizar_previsoes
cls
echo =====================================================
echo   ATUALIZAR PREVISÕES DE CHUVA
echo =====================================================
echo.

cd %BASE_DIR%\scripts
python update_previsao.py

echo.
pause
goto menu

:iniciar_api
cls
echo =====================================================
echo   INICIANDO API (MODO NORMAL)
echo =====================================================
echo.

cd %BASE_DIR%\api

REM Verificar se o ambiente virtual existe
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Instalando dependências...
pip install -r requirements.txt

echo.
echo Configurando variáveis de ambiente...
set FLASK_APP=app.py 
set FLASK_ENV=development
set USE_MOCK_DATA=False

echo.
echo API iniciada com sucesso! Acesse: http://localhost:5000
echo Para interromper, pressione CTRL+C
echo.

python -m flask run
goto menu

:iniciar_api_simulacao
cls
echo =====================================================
echo   INICIANDO API (MODO SIMULAÇÃO)
echo =====================================================
echo.
echo [AVISO] Esta API usará dados simulados ao invés de
echo         dados reais do banco de dados.
echo.

cd %BASE_DIR%\api

REM Verificar se o ambiente virtual existe
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Instalando dependências (modo simulação)...
pip install flask flask-cors pandas numpy python-dotenv scikit-learn gunicorn

echo.
echo Configurando variáveis de ambiente...
set FLASK_APP=app.py 
set FLASK_ENV=development
set USE_MOCK_DATA=True

echo.
echo API iniciada em MODO SIMULAÇÃO com sucesso! Acesse: http://localhost:5000
echo Para interromper, pressione CTRL+C
echo.

python -m flask run
goto menu

:verificar_ambiente
cls
echo =====================================================
echo   VERIFICAÇÃO DO AMBIENTE
echo =====================================================
echo.

echo [INFO] Verificando PostgreSQL...
where psql >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] psql não encontrado no PATH
    echo         A configuração do banco de dados precisará ser manual
    echo.
) else (
    echo [OK] PostgreSQL encontrado
)

echo.
echo [INFO] Verificando Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python não encontrado no PATH!
) else (
    echo [INFO] Verificando pacotes instalados...
    python -m pip list
)

echo.
echo Verificação concluída.
pause
goto menu

:fim
echo.
echo =====================================================
echo   Sistema THM encerrado
echo =====================================================
exit /b 0 