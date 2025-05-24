import psycopg2
import os
from dotenv import load_dotenv
import sys
import traceback

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Carregar variáveis de ambiente
load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def test_connection():
    """Testa a conexão com o banco de dados"""
    print("Testando conexão com o banco de dados...")
    print(f"Configurações:")
    print(f"DB_NAME: {DB_CONFIG['dbname']}")
    print(f"DB_USER: {DB_CONFIG['user']}")
    print(f"DB_HOST: {DB_CONFIG['host']}")
    print(f"DB_PORT: {DB_CONFIG['port']}")
    
    try:
        # Tentar conexão
        conn = psycopg2.connect(**DB_CONFIG)
        print("\nConexão estabelecida com sucesso!")
        
        # Testar query simples
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"\nVersão do PostgreSQL: {version[0]}")
        
        # Testar tabelas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        print("\nTabelas encontradas:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Contar registros em cada tabela
            cur.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cur.fetchone()
            print(f"  Registros: {count[0]}")
        
        cur.close()
        conn.close()
        print("\nTeste concluído com sucesso!")
        
    except Exception as e:
        print("\nERRO ao conectar ao banco de dados:")
        print(str(e))
        print("\nDetalhes do erro:")
        traceback.print_exc()

if __name__ == "__main__":
    test_connection() 