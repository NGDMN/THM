@echo off
title Projeto THM - Execução Simplificada

echo =====================================================
echo   PROJETO THM - ANALISE DE CHUVAS E ALAGAMENTOS
echo =====================================================
echo.

echo Configurando ambiente Oracle...
set PATH=C:\Oracle\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8;%PATH%
set TNS_ADMIN=C:\Users\Neil\OracleWallet
echo Ambiente configurado!

echo.
echo Executando script principal (versão simplificada)...
echo.

python script_principal.py

echo.
echo =====================================================
echo   PROCESSAMENTO CONCLUIDO
echo =====================================================
echo.
pause 