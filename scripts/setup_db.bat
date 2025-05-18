@echo off
setlocal enabledelayedexpansion

echo ===== Configurando banco de dados PostgreSQL para o sistema THM =====

:: Configurações do PostgreSQL
set PG_USER=postgres
set PG_DATABASE=thm
set PG_HOST=localhost
set PG_PORT=5432

echo.
echo Verificando conexao com PostgreSQL...

:: Verificar se psql está no PATH
where psql >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: psql nao encontrado. Verifique se o PostgreSQL esta instalado e no PATH.
    echo Voce pode baixar o PostgreSQL em: https://www.postgresql.org/download/windows/
    goto :EOF
)

:: Solicitar senha do PostgreSQL
set /p PG_PASSWORD=Digite a senha do usuario postgres: 

:: Definir PGPASSWORD para autenticação
set PGPASSWORD=%PG_PASSWORD%

echo.
echo Criando banco de dados %PG_DATABASE%...

:: Verificar se o banco já existe
psql -h %PG_HOST% -p %PG_PORT% -U %PG_USER% -c "SELECT 1 FROM pg_database WHERE datname='%PG_DATABASE%'" | findstr /r /c:"1 row" >nul
if %ERRORLEVEL% EQU 0 (
    echo O banco de dados %PG_DATABASE% ja existe.
) else (
    psql -h %PG_HOST% -p %PG_PORT% -U %PG_USER% -c "CREATE DATABASE %PG_DATABASE%;"
    if %ERRORLEVEL% NEQ 0 (
        echo ERRO: Falha ao criar o banco de dados.
        goto :EOF
    ) else (
        echo Banco de dados %PG_DATABASE% criado com sucesso.
    )
)

echo.
echo Criando estrutura de tabelas...

:: Executar script de schema
psql -h %PG_HOST% -p %PG_PORT% -U %PG_USER% -d %PG_DATABASE% -f %~dp0schema_pg.sql
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha ao criar as tabelas.
    goto :EOF
) else (
    echo Tabelas criadas com sucesso.
)

echo.
echo Salvando configuracoes no arquivo .env...

:: Criar arquivo .env na raiz do projeto
(
    echo # Arquivo de configuracao gerado automaticamente
    echo PG_DBNAME=%PG_DATABASE%
    echo PG_USER=%PG_USER%
    echo PG_PASSWORD=%PG_PASSWORD%
    echo PG_HOST=%PG_HOST%
    echo PG_PORT=%PG_PORT%
    echo USE_MOCK_DATA=False
    echo API_CLIMATEMPO_KEY=
) > %~dp0..\.env

echo Configuracoes salvas em .env

echo.
echo ===== Banco de dados configurado com sucesso! =====
echo.
echo Proximos passos:
echo 1. Importe dados historicos com: python scripts\import_data.py
echo 2. Obtenha uma chave da API Climatempo e adicione-a no arquivo .env
echo 3. Configure a atualizacao diaria com: python scripts\update_previsao.py
echo.

:: Limpar PGPASSWORD por segurança
set PGPASSWORD=

endlocal 