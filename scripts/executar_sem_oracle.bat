@echo off
title Projeto THM - Teste sem Oracle
echo =====================================================
echo   PROJETO THM - TESTE SEM ORACLE
echo =====================================================
echo.

echo Este script executa o Python sem tentar conectar ao Oracle
echo para identificar se o problema está no script ou na conexão.
echo.

:: Verificar se o Python está disponível
echo [DEBUG] Verificando Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python não encontrado no PATH
    echo        Certifique-se de que o Python está instalado
    echo.
    pause
    exit /b 1
)

:: Verificar se o script principal existe
set SCRIPT_PRINCIPAL="Script de Limpeza e Análise de Dados.py"
echo [DEBUG] Verificando script principal: %SCRIPT_PRINCIPAL%
if not exist %SCRIPT_PRINCIPAL% (
    echo [ERRO] Script principal não encontrado: %SCRIPT_PRINCIPAL%
    echo        Verifique se o arquivo existe no diretório atual
    echo        Diretório atual: %CD%
    dir /b *.py
    echo.
    pause
    exit /b 1
)

echo.
echo =====================================================
echo   INICIANDO PYTHON EM MODO INTERATIVO
echo =====================================================
echo.
echo Por favor, teste o script com os seguintes comandos:
echo.
echo import pandas as pd
echo import numpy as np
echo import cx_Oracle
echo exit()
echo.
echo Pressione qualquer tecla para iniciar o Python...
pause > nul

:: Iniciar Python em modo interativo
python

echo.
echo =====================================================
echo   TESTE DIAGNÓSTICO
echo =====================================================
echo.
echo Agora vamos executar o script de diagnóstico
echo para verificar todos os componentes do sistema.
echo.
echo Pressione qualquer tecla para continuar...
pause > nul

:: Executar diagnóstico
python diagnostico_sistema.py

echo.
echo =====================================================
echo   TESTE CONCLUÍDO
echo =====================================================
echo.
echo Por favor, verifique as mensagens acima para 
echo identificar possíveis problemas.
echo.
pause 