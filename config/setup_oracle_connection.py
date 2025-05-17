"""
Script de configuração da conexão com Oracle Database
Realiza verificações e testes de conexão com o banco de dados
"""

import os
import sys
import cx_Oracle
import traceback
import ctypes
import logging
import platform
import subprocess
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("oracle_setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("setup_oracle")

# Configurações do Oracle
ORACLE_CLIENT_PATH = r'C:\Oracle\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8'
WALLET_PATH = r'C:\Users\Neil\OracleWallet'
USERNAME = 'ADMIN'
PASSWORD = 'Chuvas1Alagamentos'
DSN = 'chuvasalagamentos_high'

def is_admin():
    """Verifica se o script está sendo executado como administrador"""
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0  # Verificação para sistemas Unix-like
    except Exception as e:
        logger.warning(f"Erro ao verificar privilégios administrativos: {str(e)}")
        return False

def set_environment_variables():
    """Configura variáveis de ambiente para a sessão atual"""
    try:
        # Adicionar Oracle Client ao PATH
        if ORACLE_CLIENT_PATH not in os.environ.get('PATH', ''):
            os.environ['PATH'] = ORACLE_CLIENT_PATH + os.pathsep + os.environ['PATH']
            logger.info(f"Oracle Client adicionado ao PATH: {ORACLE_CLIENT_PATH}")
        
        # Configurar TNS_ADMIN
        os.environ['TNS_ADMIN'] = WALLET_PATH
        logger.info(f"TNS_ADMIN configurado: {WALLET_PATH}")
        
        return True
    except Exception as e:
        logger.error(f"Erro ao configurar variáveis de ambiente: {str(e)}")
        return False

def check_wallet():
    """Verifica se o Oracle Wallet está configurado corretamente"""
    try:
        if not os.path.exists(WALLET_PATH):
            logger.error(f"Diretório do wallet não existe: {WALLET_PATH}")
            return False
        
        # Arquivos necessários no wallet
        required_files = ['tnsnames.ora', 'sqlnet.ora', 'cwallet.sso']
        missing_files = [f for f in required_files if not os.path.exists(os.path.join(WALLET_PATH, f))]
        
        if missing_files:
            logger.error(f"Arquivos faltando no wallet: {', '.join(missing_files)}")
            return False
        
        # Verificar conteúdo do sqlnet.ora
        sqlnet_path = os.path.join(WALLET_PATH, 'sqlnet.ora')
        with open(sqlnet_path, 'r') as f:
            sqlnet_content = f.read()
            
        if 'WALLET_LOCATION' not in sqlnet_content:
            logger.warning("O arquivo sqlnet.ora não contém a configuração WALLET_LOCATION")
            logger.warning("Isso pode causar problemas de conexão")
            
        logger.info(f"Oracle Wallet verificado em: {WALLET_PATH}")
        return True
    except Exception as e:
        logger.error(f"Erro ao verificar Oracle Wallet: {str(e)}")
        return False

def check_oracle_client():
    """Verifica se o Oracle Instant Client está instalado corretamente"""
    try:
        dll_path = os.path.join(ORACLE_CLIENT_PATH, 'oci.dll')
        if not os.path.exists(dll_path):
            logger.error(f"Oracle Client não encontrado: {dll_path}")
            return False
        
        logger.info(f"Oracle Client encontrado: {ORACLE_CLIENT_PATH}")
        return True
    except Exception as e:
        logger.error(f"Erro ao verificar Oracle Client: {str(e)}")
        return False

def init_oracle_client():
    """Inicializa o cliente Oracle explicitamente"""
    try:
        # Tentar inicializar o cliente
        cx_Oracle.init_oracle_client(lib_dir=ORACLE_CLIENT_PATH)
        logger.info("Oracle Client inicializado com sucesso")
        return True
    except Exception as e:
        error_msg = str(e)
        if "already initialized" in error_msg:
            logger.info("Oracle Client já estava inicializado")
            return True
        else:
            logger.error(f"Erro ao inicializar Oracle Client: {error_msg}")
            return False

def test_connection():
    """Testa a conexão com o Oracle Database"""
    connection = None
    cursor = None
    try:
        # Montar string de conexão
        connection_string = f"{USERNAME}/{PASSWORD}@{DSN}"
        
        # Tentar conectar
        logger.info("Testando conexão com Oracle Database...")
        connection = cx_Oracle.connect(connection_string)
        
        # Verificar versão do banco
        version = connection.version
        logger.info(f"Conexão bem-sucedida! Versão do banco: {version}")
        
        # Testar consulta simples
        cursor = connection.cursor()
        cursor.execute("SELECT SYSDATE FROM DUAL")
        date = cursor.fetchone()[0]
        logger.info(f"Data atual no banco: {date}")
        
        # Verificar tabelas existentes
        try:
            # Listar tabelas do usuário
            cursor.execute("""
                SELECT table_name 
                FROM user_tables 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            if tables:
                logger.info(f"Tabelas existentes ({len(tables)}):")
                for table in tables:
                    logger.info(f"  - {table[0]}")
            else:
                logger.info("Não existem tabelas no esquema atual")
                
        except Exception as table_e:
            logger.warning(f"Erro ao listar tabelas: {str(table_e)}")
        
        return True
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Erro ao conectar ao Oracle Database: {error_msg}")
        
        # Diagnosticar problemas comuns
        if "DPI-1047" in error_msg:
            logger.error("Causa: Oracle Client não encontrado")
            logger.info("Soluções possíveis:")
            logger.info("1. Verifique se o caminho do cliente está correto")
            logger.info("2. Reinicie seu terminal/prompt de comando")
            logger.info("3. Adicione o caminho ao PATH do sistema")
        elif "ORA-01017" in error_msg:
            logger.error("Causa: Nome de usuário ou senha incorretos")
            logger.info("Solução: Verifique as credenciais")
        elif "ORA-12154" in error_msg:
            logger.error("Causa: TNS não conseguiu resolver o identificador de conexão")
            logger.info("Soluções possíveis:")
            logger.info("1. Verifique se TNS_ADMIN está configurado corretamente")
            logger.info("2. Verifique se tnsnames.ora contém a entrada correta")
        elif "ORA-28759" in error_msg:
            logger.error("Causa: Falha ao abrir arquivo do wallet")
            logger.info("Soluções possíveis:")
            logger.info("1. Verifique se todos os arquivos do wallet foram extraídos")
            logger.info("2. Verifique permissões dos arquivos no wallet")
            logger.info("3. Verifique o caminho do wallet na variável TNS_ADMIN")
        return False
    finally:
        # Fechar recursos
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            logger.info("Conexão fechada")

def create_batch_file():
    """Cria arquivo batch para execução automatizada"""
    try:
        batch_file = "executar_script_principal.bat"
        
        # Conteúdo do batch file
        content = f"""@echo off
title Projeto THM - Análise de Chuvas e Alagamentos
echo =====================================================
echo   PROJETO THM - ANÁLISE DE CHUVAS E ALAGAMENTOS
echo =====================================================
echo.

:: Verificar ambiente Oracle
echo [INFO] Configurando ambiente Oracle...
set ORACLE_CLIENT_PATH={ORACLE_CLIENT_PATH}
set WALLET_PATH={WALLET_PATH}
set CONNECTION_STRING={USERNAME}/{PASSWORD}@{DSN}

:: Configurar variáveis de ambiente
set PATH=%ORACLE_CLIENT_PATH%;%PATH%
set TNS_ADMIN=%WALLET_PATH%

:: Verificar se o Oracle Client existe
if not exist "%ORACLE_CLIENT_PATH%\\oci.dll" (
    echo [ERRO] Oracle Client não encontrado em: %ORACLE_CLIENT_PATH%
    echo        Por favor, verifique a instalação do Oracle Instant Client
    echo        Consulte o README.md para instruções
    goto :fim
)

:: Verificar se o Oracle Wallet existe
if not exist "%WALLET_PATH%\\sqlnet.ora" (
    echo [ERRO] Oracle Wallet não configurado corretamente em: %WALLET_PATH%
    echo        O arquivo sqlnet.ora não foi encontrado
    echo        Consulte o README.md para instruções
    goto :fim
)

echo [OK] Ambiente Oracle configurado com sucesso!
echo     - Oracle Client: %ORACLE_CLIENT_PATH%
echo     - Oracle Wallet: %WALLET_PATH%
echo.

:: Verificar se o Python está disponível
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python não encontrado no PATH
    echo        Certifique-se de que o Python está instalado e disponível no PATH
    goto :fim
)

:: Verificar se o script principal existe
set SCRIPT_PRINCIPAL="Script de Limpeza e Análise de Dados.py"
if not exist %SCRIPT_PRINCIPAL% (
    echo [ERRO] Script principal não encontrado: %SCRIPT_PRINCIPAL%
    echo        Verifique se o arquivo existe no diretório atual
    goto :fim
)

echo [INFO] Executando script principal...
echo.
echo =====================================================
echo   INICIANDO PROCESSAMENTO DE DADOS
echo =====================================================
echo.

python %SCRIPT_PRINCIPAL%

:fim
echo.
echo =====================================================
echo   PROCESSAMENTO CONCLUÍDO
echo =====================================================
echo.
pause
"""
        
        # Salvar o arquivo
        with open(batch_file, 'w') as f:
            f.write(content)
            
        logger.info(f"Arquivo batch criado: {batch_file}")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar arquivo batch: {str(e)}")
        return False

def set_permanent_environment_variables():
    """Tenta configurar variáveis de ambiente permanentemente (requer privilégios administrativos)"""
    if not is_admin():
        logger.warning("Configuração permanente de variáveis de ambiente requer privilégios administrativos")
        return False
    
    try:
        # No Windows, usar setx
        if platform.system() == 'Windows':
            # Adicionar Oracle Client ao PATH
            subprocess.call(['setx', 'PATH', f"{ORACLE_CLIENT_PATH};%PATH%"])
            
            # Configurar TNS_ADMIN
            subprocess.call(['setx', 'TNS_ADMIN', WALLET_PATH])
            
            logger.info("Variáveis de ambiente configuradas permanentemente")
            logger.info("IMPORTANTE: Reinicie o terminal para aplicar as alterações")
            return True
        else:
            logger.warning("Configuração permanente automática não implementada para este sistema operacional")
            return False
    except Exception as e:
        logger.error(f"Erro ao configurar variáveis de ambiente permanentemente: {str(e)}")
        return False

def main():
    """Função principal"""
    logger.info("="*60)
    logger.info(" CONFIGURAÇÃO DE CONEXÃO COM ORACLE DATABASE ")
    logger.info("="*60)
    logger.info(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Sistema: {platform.system()} {platform.release()}")
    logger.info(f"Python: {platform.python_version()}")
    
    # Verificar privilégios administrativos
    admin_status = is_admin()
    logger.info(f"Privilégios administrativos: {'Sim' if admin_status else 'Não'}")
    
    # Verificar componentes
    client_ok = check_oracle_client()
    wallet_ok = check_wallet()
    env_vars_ok = set_environment_variables()
    
    # Verificar se todos os componentes estão OK
    components_ok = client_ok and wallet_ok and env_vars_ok
    
    if not components_ok:
        logger.warning("Alguns componentes não estão configurados corretamente")
        
        if not client_ok:
            logger.info("\nPara instalar o Oracle Instant Client:")
            logger.info("1. Baixe o pacote Basic de: https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html")
            logger.info(f"2. Extraia para: {ORACLE_CLIENT_PATH}")
            
        if not wallet_ok:
            logger.info("\nPara configurar o Oracle Wallet:")
            logger.info("1. No console do OCI, navegue até seu banco de dados autônomo")
            logger.info("2. Clique em 'DB Connection' e depois em 'Download Wallet'")
            logger.info(f"3. Extraia o conteúdo para: {WALLET_PATH}")
        
        # Perguntar se deseja continuar mesmo com problemas
        continue_option = input("\nDeseja continuar mesmo com problemas de configuração? (s/n): ")
        if continue_option.lower() != 's':
            logger.info("Operação cancelada pelo usuário")
            return False
    
    # Inicializar cliente Oracle
    init_ok = init_oracle_client()
    if not init_ok:
        logger.warning("Falha ao inicializar Oracle Client")
        continue_option = input("\nDeseja continuar mesmo assim? (s/n): ")
        if continue_option.lower() != 's':
            logger.info("Operação cancelada pelo usuário")
            return False
    
    # Testar conexão
    logger.info("\n" + "="*60)
    logger.info(" TESTANDO CONEXÃO COM ORACLE DATABASE ")
    logger.info("="*60)
    
    conn_ok = test_connection()
    
    # Ações baseadas no resultado do teste
    if conn_ok:
        logger.info("\n" + "="*60)
        logger.info(" CONEXÃO BEM-SUCEDIDA! ")
        logger.info("="*60)
        
        # Criar arquivo batch para execução automatizada
        batch_ok = create_batch_file()
        if batch_ok:
            logger.info("\nPara executar o script principal com o ambiente Oracle configurado:")
            logger.info("- Execute o arquivo 'executar_script_principal.bat'")
        
        # Perguntar se deseja configurar variáveis de ambiente permanentemente
        if is_admin():
            permanent_env_option = input("\nDeseja configurar as variáveis de ambiente permanentemente? (s/n): ")
            if permanent_env_option.lower() == 's':
                set_permanent_environment_variables()
        else:
            logger.info("\nPara configurar variáveis de ambiente permanentemente:")
            logger.info("- Execute este script como administrador")
    else:
        logger.error("\n" + "="*60)
        logger.error(" PROBLEMAS DE CONEXÃO ")
        logger.error("="*60)
        logger.info("\nRecomendações:")
        logger.info("1. Verifique as credenciais (USERNAME, PASSWORD, DSN)")
        logger.info("2. Verifique a configuração do Oracle Wallet")
        logger.info("3. Certifique-se de que o banco de dados está acessível")
        logger.info("4. Reinicie seu computador para aplicar alterações nas variáveis de ambiente")
    
    # Instruções finais
    logger.info("\n" + "="*60)
    logger.info(" FIM DA VERIFICAÇÃO ")
    logger.info("="*60)
    logger.info(f"Log completo salvo em: oracle_setup.log")
    
    return conn_ok

if __name__ == "__main__":
    # Executar função principal com tratamento de exceções
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\nOperação cancelada pelo usuário")
    except Exception as e:
        logger.critical(f"Erro não tratado: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 