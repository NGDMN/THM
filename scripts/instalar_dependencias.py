import sys
import subprocess
import os
import platform
import ctypes

def is_admin():
    """Verifica se o script está sendo executado como administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def instalar_vcredist():
    """Instala o Visual C++ Redistributable necessário para o cx_Oracle"""
    print("\n=== INSTALANDO VISUAL C++ REDISTRIBUTABLE ===\n")
    
    try:
        # Verificar se estamos no Windows
        if platform.system() != "Windows":
            print("Esta funcionalidade só está disponível no Windows.")
            return False
        
        # URL do Visual C++ Redistributable
        url = 'https://aka.ms/vs/16/release/vc_redist.x64.exe'
        output_file = 'vc_redist.x64.exe'
        
        # Download do arquivo
        print(f"Baixando Visual C++ Redistributable de {url}...")
        try:
            import urllib.request
            urllib.request.urlretrieve(url, output_file)
        except:
            print("Erro ao baixar o arquivo. Tentando com PowerShell...")
            powershell_cmd = f'powershell -Command "& {{Invoke-WebRequest -Uri \'{url}\' -OutFile \'{output_file}\'}}"'
            subprocess.call(powershell_cmd, shell=True)
        
        # Verificar se o download foi bem-sucedido
        if not os.path.exists(output_file):
            print("ERRO: Falha ao baixar o arquivo.")
            print(f"Por favor, baixe manualmente de: {url}")
            return False
        
        # Instalar o pacote
        print("Instalando Visual C++ Redistributable...")
        subprocess.call([output_file, '/install', '/quiet', '/norestart'])
        
        print("✓ Visual C++ Redistributable instalado com sucesso!")
        return True
    
    except Exception as e:
        print(f"Erro ao instalar Visual C++ Redistributable: {str(e)}")
        print(f"Por favor, baixe e instale manualmente de: {url}")
        return False

def instalar_pacote(pacote):
    """Instala um pacote Python usando pip"""
    print(f"Instalando {pacote}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar {pacote}: {str(e)}")
        return False

def verificar_instalacao(pacote):
    """Verifica se um pacote está instalado"""
    try:
        __import__(pacote)
        print(f"✓ {pacote} já está instalado.")
        return True
    except ImportError:
        print(f"✗ {pacote} não está instalado.")
        return False

def main():
    """Função principal"""
    print("\n=== INSTALAÇÃO DE DEPENDÊNCIAS DO PROJETO THM ===\n")
    
    # Verificar se estamos no Windows
    if platform.system() == "Windows":
        print("Sistema operacional: Windows")
        
        # Verificar privilégios de administrador para instalação do VC++
        if not is_admin():
            print("AVISO: Este script não está sendo executado como administrador.")
            print("Para instalar o Visual C++ Redistributable, execute como administrador.")
            instalar_vcredist_option = input("Deseja tentar instalar o Visual C++ Redistributable mesmo assim? (s/n): ")
            if instalar_vcredist_option.lower() == 's':
                instalar_vcredist()
        else:
            print("Executando como administrador.")
            vcredist_option = input("Deseja instalar o Visual C++ Redistributable necessário para o cx_Oracle? (s/n): ")
            if vcredist_option.lower() == 's':
                instalar_vcredist()
    else:
        print(f"Sistema operacional: {platform.system()}")
    
    # Lista de pacotes necessários
    pacotes = [
        "cx_Oracle",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn"
    ]
    
    # Verificar e instalar cada pacote
    print("\n=== INSTALANDO BIBLIOTECAS PYTHON ===\n")
    pacotes_instalados = 0
    pacotes_falha = 0
    
    for pacote in pacotes:
        base_pacote = pacote.split("==")[0]
        if not verificar_instalacao(base_pacote):
            if instalar_pacote(pacote):
                print(f"✓ {pacote} instalado com sucesso!")
                pacotes_instalados += 1
            else:
                print(f"✗ Falha ao instalar {pacote}.")
                pacotes_falha += 1
    
    # Resumo da instalação
    print("\n=== RESUMO DA INSTALAÇÃO ===")
    print(f"Pacotes já instalados: {len(pacotes) - pacotes_instalados - pacotes_falha}")
    print(f"Pacotes instalados com sucesso: {pacotes_instalados}")
    print(f"Pacotes com falha na instalação: {pacotes_falha}")
    
    # Instruções finais
    print("\n=== PRÓXIMOS PASSOS ===")
    if pacotes_falha == 0:
        print("1. Todas as dependências foram instaladas com sucesso!")
        print("2. Execute: python setup_oracle_connection.py")
    else:
        print("1. Alguns pacotes não puderam ser instalados automaticamente.")
        print("2. Tente instalar manualmente os pacotes que falharam.")
        print("3. Após instalar todas as dependências, execute: python setup_oracle_connection.py")

if __name__ == "__main__":
    main() 