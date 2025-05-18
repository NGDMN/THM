@echo off
title Agendar Atualização de Previsões Meteorológicas

REM Diretório base do projeto
set BASE_DIR=%~dp0..

echo =====================================================
echo   AGENDAMENTO DE ATUALIZAÇÃO DE PREVISÕES
echo =====================================================
echo.
echo Este script criará uma tarefa agendada no Windows
echo para atualizar diariamente as previsões meteorológicas
echo e alertas de alagamentos.
echo.
echo A tarefa será executada uma vez por dia às 06:00.
echo.
echo Pressione qualquer tecla para continuar ou CTRL+C para cancelar...
pause > nul

REM Gerar caminho absoluto para o script Python
set SCRIPT_PATH=%BASE_DIR%\scripts\update_previsao.py
set PYTHON_PATH=python

REM Criar a tarefa agendada usando o schtasks
echo Criando tarefa agendada...
schtasks /create /tn "THM_AtualizacaoPrevisoes" /tr "%PYTHON_PATH% %SCRIPT_PATH%" /sc DAILY /st 06:00 /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Tarefa agendada criada com sucesso!
    echo A atualização será executada diariamente às 06:00.
    echo.
    echo Para verificar as tarefas agendadas, use o comando:
    echo schtasks /query /tn "THM_AtualizacaoPrevisoes"
) else (
    echo.
    echo ERRO: Não foi possível criar a tarefa agendada.
    echo Verifique se você tem permissões de administrador.
)

echo.
pause 