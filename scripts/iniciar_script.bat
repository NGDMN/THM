@echo off
chcp 65001
title Iniciar Script Principal

echo Configurando ambiente Oracle...
set PATH=C:\Oracle\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8;%PATH%
set TNS_ADMIN=C:\Users\Neil\OracleWallet

:: Encontrar o script principal
echo Procurando pelo script principal...
set ARQUIVO_ENCONTRADO=0

:: Listar todos os arquivos Python
for %%f in (*.py) do (
    echo Verificando: %%f
    
    :: Verificar se contém "Script" no nome
    echo.%%f | findstr /i "Script" > nul
    if not errorlevel 1 (
        echo Executando: %%f
        set ARQUIVO_ENCONTRADO=1
        python "%%f"
        goto fim
    )
)

:: Se não encontrou o arquivo
if %ARQUIVO_ENCONTRADO%==0 (
    echo Nenhum arquivo com "Script" no nome foi encontrado.
    echo Arquivos disponíveis:
    dir /b *.py
    
    echo.
    echo Execute manualmente um destes arquivos:
    echo python "Script de Limpeza e Análise de Dados.py"
)

:fim
echo.
echo Pressione qualquer tecla para sair...
pause > nul 