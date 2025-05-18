@echo off
chcp 65001
title Sistema THM - Execução Unificada

REM Configurações globais
set ORACLE_CLIENT_PATH=C:\Oracle\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8
set WALLET_PATH=C:\Users\Neil\OracleWallet
set PATH=%ORACLE_CLIENT_PATH%;%PATH%
set TNS_ADMIN=%WALLET_PATH%
set SCRIPT_PRINCIPAL=script_principal.py

:menu
cls
echo =====================================================
echo   SISTEMA THM - ANÁLISE DE CHUVAS E ALAGAMENTOS
echo =====================================================
echo.
echo Escolha uma opção:
echo.
echo [1] Executar script principal (com Oracle)
echo [2] Executar script simplificado
echo [3] Executar sem Oracle (diagnóstico)
echo [4] Iniciar API (modo normal)
echo [5] Iniciar API (modo simulação)
echo [6] Verificar ambiente
echo [0] Sair
echo.
set /p opcao="Digite o número da opção desejada: "

if "%opcao%"=="1" goto executar_principal
if "%opcao%"=="2" goto executar_simplificado
if "%opcao%"=="3" goto executar_sem_oracle
if "%opcao%"=="4" goto iniciar_api
if "%opcao%"=="5" goto iniciar_api_simulacao
if "%opcao%"=="6" goto verificar_ambiente
if "%opcao%"=="0" goto fim

echo.
echo Opção inválida. Por favor, tente novamente.
timeout /t 2 >nul
goto menu

:executar_principal
cls
echo =====================================================
echo   EXECUTANDO SCRIPT PRINCIPAL COM ORACLE
echo =====================================================
echo.

call :configurar_oracle

echo [INFO] Executando script principal...
echo.
python %SCRIPT_PRINCIPAL% 2> python_error.log
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] O script Python encontrou um erro durante a execução!
    echo        Verifique o arquivo python_error.log para mais detalhes:
    type python_error.log
    echo.
    pause
)

echo.
echo Processamento concluído.
pause
goto menu

:executar_simplificado
cls
echo =====================================================
echo   EXECUTANDO SCRIPT SIMPLIFICADO
echo =====================================================
echo.

call :configurar_oracle

echo [INFO] Executando script em modo simplificado...
echo.
python %SCRIPT_PRINCIPAL% --simple 2> python_error.log
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] O script Python encontrou um erro!
    type python_error.log
    echo.
    pause
)

echo.
echo Processamento concluído.
pause
goto menu

:executar_sem_oracle
cls
echo =====================================================
echo   DIAGNÓSTICO SEM ORACLE
echo =====================================================
echo.
echo Este modo executa testes sem tentar conectar ao Oracle
echo para identificar se o problema está no script ou na conexão.
echo.

echo [INFO] Verificando Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python não encontrado no PATH!
    pause
    goto menu
)

echo.
echo [INFO] Executando script de diagnóstico...
cd ..\scripts
python diagnostico_sistema.py

echo.
echo Diagnóstico concluído.
pause
goto menu

:iniciar_api
cls
echo =====================================================
echo   INICIANDO API (MODO NORMAL)
echo =====================================================
echo.

cd ..\api

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
echo         dados reais do Oracle Database.
echo.

cd ..\api

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

echo [INFO] Verificando Oracle Client...
if not exist "%ORACLE_CLIENT_PATH%\oci.dll" (
    echo [ERRO] Oracle Client não encontrado em: %ORACLE_CLIENT_PATH%
    echo        Por favor, verifique a instalação do Oracle Instant Client
    echo.
) else (
    echo [OK] Oracle Client encontrado: %ORACLE_CLIENT_PATH%
)

echo.
echo [INFO] Verificando Oracle Wallet...
if not exist "%WALLET_PATH%\sqlnet.ora" (
    echo [ERRO] Oracle Wallet não configurado corretamente em: %WALLET_PATH%
    echo        O arquivo sqlnet.ora não foi encontrado
    echo.
) else (
    echo [OK] Oracle Wallet encontrado: %WALLET_PATH%
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

:configurar_oracle
echo [INFO] Configurando ambiente Oracle...
set PATH=%ORACLE_CLIENT_PATH%;%PATH%
set TNS_ADMIN=%WALLET_PATH%

if not exist "%ORACLE_CLIENT_PATH%\oci.dll" (
    echo [AVISO] Oracle Client não encontrado em: %ORACLE_CLIENT_PATH%
)

if not exist "%WALLET_PATH%\sqlnet.ora" (
    echo [AVISO] Oracle Wallet não configurado corretamente em: %WALLET_PATH%
)

echo [OK] Ambiente Oracle configurado!
echo.
exit /b 0

:fim
echo.
echo Obrigado por usar o Sistema THM!
echo.
exit 