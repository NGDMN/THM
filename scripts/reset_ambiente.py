import psycopg2
import os
import shutil

# Configurações do banco de dados
DB_CONFIG = {
    'dbname': 'thm_iy9l',
    'user': 'thm_admin',
    'password': 'fBfTMpHLfe2htlV9fe63mc0v9SmUTStS',
    'host': 'dpg-d0l48cre5dus73c970sg-a.ohio-postgres.render.com',
    'port': '5432'
}

def reset_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute('''\
            TRUNCATE chuvas_diarias, alagamentos, previsoes RESTART IDENTITY CASCADE;
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print('Tabelas truncadas com sucesso!')
    except Exception as e:
        print(f'Erro ao truncar tabelas: {e}')

def limpar_pasta_data():
    pasta = os.path.join(os.path.dirname(__file__), '..', 'data')
    if os.path.exists(pasta):
        for filename in os.listdir(pasta):
            file_path = os.path.join(pasta, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Erro ao remover {file_path}: {e}')
        print('Pasta data/ esvaziada com sucesso!')
    else:
        print('Pasta data/ não existe.')

if __name__ == '__main__':
    reset_db()
    limpar_pasta_data()
    print('Reset do ambiente concluído.') 