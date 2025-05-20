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
echo [1] Resetar ambiente (limpar banco e data/)
echo [2] Ingestão de alagamentos
echo [3] Ingestão de chuvas
echo [4] Calcular índice de risco
echo [5] Coletar previsões (OpenWeather, todos municípios RJ/SP)
echo [0] Sair
echo.
set /p opcao="Digite o número da opção desejada: "

if "%opcao%"=="1" goto resetar_ambiente
if "%opcao%"=="2" goto ingestao_alagamentos
if "%opcao%"=="3" goto ingestao_chuvas
if "%opcao%"=="4" goto calcular_indice
if "%opcao%"=="5" goto coletar_previsoes
if "%opcao%"=="0" goto fim

echo.
echo Opção inválida. Por favor, tente novamente.
timeout /t 2 >nul
goto menu

:resetar_ambiente
cls
echo =====================================================
echo   RESETANDO AMBIENTE
echo =====================================================
echo.
cd %BASE_DIR%\scripts
python reset_ambiente.py
echo.
pause
goto menu

:ingestao_alagamentos
cls
echo =====================================================
echo   INGESTÃO DE ALAGAMENTOS
echo =====================================================
echo.
cd %BASE_DIR%\scripts
python ingestao_alagamentos.py
echo.
pause
goto menu

:ingestao_chuvas
cls
echo =====================================================
echo   INGESTÃO DE CHUVAS
echo =====================================================
echo.
cd %BASE_DIR%\scripts
python ingestao_chuvas.py
echo.
pause
goto menu

:calcular_indice
cls
echo =====================================================
echo   CALCULANDO ÍNDICE DE RISCO
echo =====================================================
echo.
cd %BASE_DIR%\scripts
python calcular_indice_risco.py
echo.
pause
goto menu

:coletar_previsoes
cls
echo =====================================================
echo   COLETANDO PREVISÕES (OpenWeather)
echo =====================================================
echo.
echo Informe o caminho do CSV com todos os municípios de RJ e SP (colunas: municipio,uf,lat,lon):
set /p municipios_csv="Caminho do CSV: "
cd %BASE_DIR%\scripts
python coletar_previsoes.py "%municipios_csv%"
echo.
pause
goto menu

:fim
echo.
echo =====================================================
echo   Sistema THM encerrado
echo =====================================================
exit /b 0 