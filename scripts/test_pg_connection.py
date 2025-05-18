import psycopg2
import sys

def test_connection(password):
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password=password,
            host="localhost",
            port="5432"
        )
        conn.close()
        print(f"Conexão bem-sucedida com a senha: {password}")
        return True
    except Exception as e:
        print(f"Falha com a senha '{password}': {e}")
        return False

# Lista de senhas comuns para o PostgreSQL
common_passwords = [
    "",          # Sem senha
    "postgres",  # Mesma que o usuário
    "admin",     # Senha comum
    "password",  # Senha comum
    "postgres123", # Variação comum
    "admin123",  # Variação comum
    "123456",    # Senha simples
    "postgresql", # Nome do banco
    "root"       # Comum em ambientes Unix
]

print("Testando possíveis senhas para PostgreSQL...")
success = False

for pwd in common_passwords:
    if test_connection(pwd):
        success = True
        print(f"\nSenha encontrada: '{pwd}'")
        
        # Criar arquivo .env com a senha correta
        with open(".env", "w") as f:
            f.write(f"""# Arquivo de configuração PostgreSQL
PG_DBNAME=thm
PG_USER=postgres
PG_PASSWORD={pwd}
PG_HOST=localhost
PG_PORT=5432
USE_MOCK_DATA=False
API_CLIMATEMPO_KEY=
""")
        print("Arquivo .env criado com a senha correta!")
        break

if not success:
    print("\nNenhuma senha comum funcionou. Será necessário resetar a senha do PostgreSQL.")
    print("Instruções para reset da senha:")
    print("1. Pare o serviço do PostgreSQL (usando serviços do Windows ou 'net stop postgresql-x64-17' como administrador)")
    print("2. Edite o arquivo pg_hba.conf (geralmente em C:\\Program Files\\PostgreSQL\\17\\data)")
    print("3. Altere o método de autenticação de 'md5' ou 'scram-sha-256' para 'trust' para o usuário postgres")
    print("4. Reinicie o serviço do PostgreSQL")
    print("5. Execute: psql -U postgres -c \"ALTER USER postgres WITH PASSWORD 'nova_senha';\"")
    print("6. Reverta as alterações no pg_hba.conf")
    print("7. Reinicie o serviço novamente") 