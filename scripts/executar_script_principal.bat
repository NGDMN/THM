@echo off
title Projeto THM - Análise de Chuvas e Alagamentos
echo =====================================================
echo   PROJETO THM - ANALISE DE CHUVAS E ALAGAMENTOS
echo =====================================================
echo.

:: Verificar ambiente Oracle
echo [INFO] Configurando ambiente Oracle...
set ORACLE_CLIENT_PATH=C:\Oracle\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8
set WALLET_PATH=C:\Users\Neil\OracleWallet
set CONNECTION_STRING=ADMIN/Chuvas1Alagamentos@chuvasalagamentos_high

:: Configurar variáveis de ambiente
set PATH=%ORACLE_CLIENT_PATH%;%PATH%
set TNS_ADMIN=%WALLET_PATH%
echo [DEBUG] PATH = %PATH%
echo [DEBUG] TNS_ADMIN = %TNS_ADMIN%

:: Verificar se o Oracle Client existe
if not exist "%ORACLE_CLIENT_PATH%\oci.dll" (
    echo [ERRO] Oracle Client não encontrado em: %ORACLE_CLIENT_PATH%
    echo        Por favor, verifique a instalação do Oracle Instant Client
    echo        Consulte o README.md para instruções
    echo.
    echo Pressione qualquer tecla para continuar...
    pause > nul
    goto :fim
)

:: Verificar se o Oracle Wallet existe
if not exist "%WALLET_PATH%\sqlnet.ora" (
    echo [ERRO] Oracle Wallet não configurado corretamente em: %WALLET_PATH%
    echo        O arquivo sqlnet.ora não foi encontrado
    echo        Consulte o README.md para instruções
    echo.
    echo Pressione qualquer tecla para continuar...
    pause > nul
    goto :fim
)

echo [OK] Ambiente Oracle configurado com sucesso!
echo     - Oracle Client: %ORACLE_CLIENT_PATH%
echo     - Oracle Wallet: %WALLET_PATH%
echo.

:: Verificar se o Python está disponível
echo [DEBUG] Verificando Python...
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python não encontrado no PATH
    echo        Certifique-se de que o Python está instalado e disponível no PATH
    echo.
    echo Pressione qualquer tecla para continuar...
    pause > nul
    goto :fim
)
echo [OK] Python encontrado: 
python --version

:: Verificar se o script principal existe usando um método alternativo
echo [DEBUG] Procurando pelo script principal...

:: Usar o comando DIR para encontrar o arquivo que começa com "Script" e termina com ".py"
for /f "tokens=*" %%F in ('dir /b Script*.py 2^>nul') do (
    set SCRIPT_PRINCIPAL="%%F"
    echo [INFO] Script principal encontrado: "%%F"
    goto execute_script
)

:: Se não encontrar o arquivo, tentar sem aspas
for /f "tokens=*" %%F in ('dir /b Script*.py 2^>nul') do (
    set SCRIPT_PRINCIPAL=%%F
    echo [INFO] Script principal encontrado: %%F
    goto execute_script
)

:: Se ainda não encontrar, mostrar erro
echo [ERRO] Script principal não encontrado.
echo        Diretório atual: %CD%
echo        Arquivos Python disponíveis:
dir /b *.py
echo.
echo Pressione qualquer tecla para continuar...
pause > nul
goto :fim

:execute_script
echo [INFO] Executando script principal...
echo.
echo =====================================================
echo   INICIANDO PROCESSAMENTO DE DADOS
echo =====================================================
echo.

:: Executar o script Python e capturar erros
python %SCRIPT_PRINCIPAL% 2> python_error.log
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] O script Python encontrou um erro durante a execução!
    echo        Verifique o arquivo python_error.log para mais detalhes:
    type python_error.log
    echo.
    echo Pressione qualquer tecla para continuar...
    pause > nul
)

:fim
echo.
echo =====================================================
echo   PROCESSAMENTO CONCLUÍDO
echo =====================================================
echo.
echo Pressione qualquer tecla para sair...
pause > nul 