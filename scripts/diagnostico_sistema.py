"""
Script de diagnóstico para o Projeto THM
Verifica todos os componentes e dependências do sistema
"""

import os
import sys
import platform
import subprocess
import importlib
import traceback

def imprimir_cabecalho(texto):
    """Imprime um cabeçalho formatado"""
    print("\n" + "="*70)
    print(f" {texto} ".center(70, "="))
    print("="*70 + "\n")

def verificar_sistema():
    """Verifica informações do sistema operacional"""
    imprimir_cabecalho("INFORMAÇÕES DO SISTEMA")
    
    try:
        print(f"Sistema: {platform.system()} {platform.release()} {platform.version()}")
        print(f"Arquitetura: {platform.machine()}")
        print(f"Processador: {platform.processor()}")
        print(f"Python: {platform.python_version()} ({sys.executable})")
        print(f"Diretório atual: {os.getcwd()}")
        
        # Verificar variáveis de ambiente importantes
        print("\nVariáveis de ambiente:")
        for var in ['PATH', 'TNS_ADMIN', 'ORACLE_HOME']:
            valor = os.environ.get(var, 'Não definido')
            if var == 'PATH':
                valor = f"{len(valor)} caracteres (muito longo para exibir)"
            print(f"  {var}: {valor}")
            
    except Exception as e:
        print(f"Erro ao verificar sistema: {str(e)}")

def verificar_python_dependencias():
    """Verifica pacotes Python instalados"""
    imprimir_cabecalho("DEPENDÊNCIAS PYTHON")
    
    dependencias = [
        ("cx_Oracle", "Conexão com Oracle Database"),
        ("pandas", "Processamento de dados"),
        ("numpy", "Computação numérica"),
        ("matplotlib", "Visualização de dados"),
        ("seaborn", "Visualização estatística")
    ]
    
    for pacote, descricao in dependencias:
        try:
            modulo = importlib.import_module(pacote)
            versao = getattr(modulo, "__version__", "Desconhecida")
            print(f"✓ {pacote}: Instalado (versão {versao}) - {descricao}")
        except ImportError:
            print(f"✗ {pacote}: NÃO INSTALADO - {descricao}")
        except Exception as e:
            print(f"? {pacote}: ERRO AO VERIFICAR - {str(e)}")

def verificar_oracle_client():
    """Verifica instalação do Oracle Client"""
    imprimir_cabecalho("ORACLE CLIENT")
    
    oracle_client_path = r'C:\Oracle\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8'
    
    print(f"Caminho configurado: {oracle_client_path}")
    
    if os.path.exists(oracle_client_path):
        print(f"✓ Diretório encontrado")
        
        # Verificar arquivos principais
        arquivos_essenciais = ['oci.dll', 'oraocci23.dll', 'sqlplus.exe']
        for arquivo in arquivos_essenciais:
            caminho = os.path.join(oracle_client_path, arquivo)
            if os.path.exists(caminho):
                print(f"  ✓ {arquivo}: Encontrado")
            else:
                print(f"  ✗ {arquivo}: NÃO ENCONTRADO")
                
        # Verificar se está no PATH
        path_vars = os.environ.get('PATH', '').split(os.pathsep)
        if oracle_client_path in path_vars:
            print("✓ Oracle Client está no PATH do sistema")
        else:
            print("✗ Oracle Client NÃO está no PATH do sistema")
    else:
        print(f"✗ Diretório não encontrado: {oracle_client_path}")
        
    try:
        # Tentar carregar cx_Oracle para verificar se ele pode encontrar o Client
        import cx_Oracle
        print(f"\nInformações do cx_Oracle:")
        print(f"  Versão: {cx_Oracle.version}")
        try:
            print(f"  Cliente Oracle: {'.'.join(map(str, cx_Oracle.clientversion()))}")
        except Exception as e:
            print(f"  Erro ao obter versão do cliente: {str(e)}")
    except Exception as e:
        print(f"\nErro ao carregar cx_Oracle: {str(e)}")

def verificar_oracle_wallet():
    """Verifica instalação do Oracle Wallet"""
    imprimir_cabecalho("ORACLE WALLET")
    
    wallet_path = r'C:\Users\Neil\OracleWallet'
    
    print(f"Caminho configurado: {wallet_path}")
    
    if os.path.exists(wallet_path):
        print(f"✓ Diretório encontrado")
        
        # Verificar arquivos essenciais do wallet
        arquivos_essenciais = ['sqlnet.ora', 'tnsnames.ora', 'cwallet.sso']
        for arquivo in arquivos_essenciais:
            caminho = os.path.join(wallet_path, arquivo)
            if os.path.exists(caminho):
                print(f"  ✓ {arquivo}: Encontrado")
                
                # Verificar conteúdo dos arquivos de configuração
                if arquivo == 'sqlnet.ora':
                    try:
                        with open(caminho, 'r') as f:
                            conteudo = f.read()
                            print(f"    Conteúdo: {conteudo[:100]}...")
                            if 'WALLET_LOCATION' in conteudo:
                                print(f"    ✓ Configuração WALLET_LOCATION encontrada")
                            else:
                                print(f"    ✗ Configuração WALLET_LOCATION NÃO encontrada")
                    except Exception as e:
                        print(f"    Erro ao ler arquivo: {str(e)}")
                
                elif arquivo == 'tnsnames.ora':
                    try:
                        with open(caminho, 'r') as f:
                            conteudo = f.read()
                            if 'chuvasalagamentos' in conteudo:
                                print(f"    ✓ Configuração de serviço 'chuvasalagamentos' encontrada")
                            else:
                                print(f"    ✗ Configuração de serviço 'chuvasalagamentos' NÃO encontrada")
                    except Exception as e:
                        print(f"    Erro ao ler arquivo: {str(e)}")
            else:
                print(f"  ✗ {arquivo}: NÃO ENCONTRADO")
        
        # Verificar variável de ambiente TNS_ADMIN
        tns_admin = os.environ.get('TNS_ADMIN', '')
        if tns_admin == wallet_path:
            print(f"✓ Variável TNS_ADMIN configurada corretamente: {tns_admin}")
        else:
            print(f"✗ Variável TNS_ADMIN não configurada corretamente:")
            print(f"  Atual: {tns_admin}")
            print(f"  Esperado: {wallet_path}")
    else:
        print(f"✗ Diretório não encontrado: {wallet_path}")

def verificar_arquivos_projeto():
    """Verifica arquivos do projeto"""
    imprimir_cabecalho("ARQUIVOS DO PROJETO")
    
    # Lista de arquivos essenciais
    arquivos_essenciais = [
        "Script de Limpeza e Análise de Dados.py",
        "setup_oracle_connection.py",
        "instalar_dependencias.py",
        "executar_script_principal.bat",
        "sqlnet.ora",
        "README.md"
    ]
    
    for arquivo in arquivos_essenciais:
        if os.path.exists(arquivo):
            tamanho = os.path.getsize(arquivo)
            data_modificacao = os.path.getmtime(arquivo)
            print(f"✓ {arquivo}: Encontrado ({tamanho} bytes)")
        else:
            print(f"✗ {arquivo}: NÃO ENCONTRADO")
    
    # Verificar diretórios de dados
    diretorios = ['Chuvas', 'Alagamentos']
    print("\nDiretórios de dados:")
    for dir in diretorios:
        if os.path.exists(dir) and os.path.isdir(dir):
            num_arquivos = len([f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))])
            print(f"✓ {dir}: Encontrado ({num_arquivos} arquivos)")
        else:
            print(f"✗ {dir}: NÃO ENCONTRADO")

def testar_conexao_oracle():
    """Testa a conexão com o Oracle Database"""
    imprimir_cabecalho("TESTE DE CONEXÃO ORACLE")
    
    # Configurações do Oracle
    username = 'ADMIN'
    password = 'Chuvas1Alagamentos'
    dsn = 'chuvasalagamentos_high'
    
    print(f"Conectando como: {username} no serviço: {dsn}")
    print(f"TNS_ADMIN: {os.environ.get('TNS_ADMIN', 'Não definido')}")
    
    try:
        import cx_Oracle
        
        # Tentar conexão
        connection_string = f"{username}/{password}@{dsn}"
        print("Tentando conectar...")
        
        connection = cx_Oracle.connect(connection_string)
        print(f"✓ Conexão bem-sucedida!")
        print(f"  Versão do banco: {connection.version}")
        
        # Testar consulta simples
        cursor = connection.cursor()
        cursor.execute("SELECT SYSDATE FROM DUAL")
        date = cursor.fetchone()[0]
        print(f"✓ Consulta executada com sucesso")
        print(f"  Data do servidor: {date}")
        
        # Verificar tabelas
        cursor.execute("""
            SELECT table_name 
            FROM user_tables 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        if tables:
            print(f"✓ Tabelas encontradas: {len(tables)}")
            for table in tables[:5]:  # Mostra até 5 tabelas
                print(f"  - {table[0]}")
            if len(tables) > 5:
                print(f"  - ... e mais {len(tables) - 5} tabelas")
        else:
            print("✗ Nenhuma tabela encontrada no esquema atual")
        
        # Fechar recursos
        cursor.close()
        connection.close()
        print("✓ Conexão fechada com sucesso")
        
    except ImportError:
        print("✗ Módulo cx_Oracle não está disponível")
    except Exception as e:
        print(f"✗ Erro ao conectar: {str(e)}")
        
        # Diagnóstico adicional
        if "DPI-1047" in str(e):
            print("\nDiagnóstico para DPI-1047:")
            print("1. Verifique se o Oracle Client está instalado e no PATH")
            print("2. Tente definir a variável LD_LIBRARY_PATH (Linux) ou PATH (Windows)")
            print("3. Verifique permissões dos arquivos no diretório do cliente")
        
        elif "ORA-01017" in str(e):
            print("\nDiagnóstico para ORA-01017:")
            print("1. Nome de usuário ou senha incorretos")
            print("2. Verifique se as credenciais estão corretas")
        
        elif "ORA-12154" in str(e):
            print("\nDiagnóstico para ORA-12154:")
            print("1. TNS não conseguiu resolver o identificador de conexão")
            print("2. Verifique se TNS_ADMIN está configurado corretamente")
            print("3. Verifique se o arquivo tnsnames.ora contém a entrada correta")
        
        print("\nRastreamento de pilha:")
        traceback.print_exc()

def main():
    """Função principal"""
    imprimir_cabecalho("DIAGNÓSTICO DE SISTEMA - PROJETO THM")
    
    try:
        # Coletar informações do sistema
        verificar_sistema()
        
        # Verificar dependências Python
        verificar_python_dependencias()
        
        # Verificar Oracle Client
        verificar_oracle_client()
        
        # Verificar Oracle Wallet
        verificar_oracle_wallet()
        
        # Verificar arquivos do projeto
        verificar_arquivos_projeto()
        
        # Testar conexão Oracle
        testar_conexao_oracle()
        
        # Resumo do diagnóstico
        imprimir_cabecalho("RESUMO DO DIAGNÓSTICO")
        print("O diagnóstico foi concluído. Revise as informações acima para identificar possíveis problemas.")
        print("\nRecomendações comuns:")
        print("1. Verifique se o Oracle Client está instalado corretamente e no PATH")
        print("2. Certifique-se de que o Oracle Wallet está configurado corretamente")
        print("3. Verifique se as credenciais de banco de dados estão corretas")
        print("4. Reinicie o terminal/computador após alterações em variáveis de ambiente")
        
    except Exception as e:
        print(f"Erro durante diagnóstico: {str(e)}")
        traceback.print_exc()
    
    input("\nPressione ENTER para sair...")

if __name__ == "__main__":
    main() 