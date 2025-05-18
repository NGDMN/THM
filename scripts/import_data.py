#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para importar dados históricos de chuvas e alagamentos para o banco PostgreSQL
"""

import os
import sys
import csv
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import pandas as pd

# Adicionar diretório pai ao path para importar módulos da API
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar configurações do banco
from api.config import DB_CONFIG

def conectar_banco():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        sys.exit(1)

def importar_chuvas(arquivo_csv):
    """Importa dados de chuvas de um arquivo CSV"""
    conn = conectar_banco()
    cursor = conn.cursor()

    try:
        # Ler o arquivo CSV usando pandas para lidar com diferentes formatos de data
        df = pd.read_csv(arquivo_csv)
        
        # Verificar as colunas necessárias
        colunas_necessarias = ['municipio', 'estado', 'data', 'precipitacao']
        for coluna in colunas_necessarias:
            if coluna not in df.columns:
                print(f"Erro: Coluna '{coluna}' não encontrada no arquivo CSV.")
                return False
        
        # Formatar e preparar dados
        registros = []
        for _, row in df.iterrows():
            # Converter string de data para objeto date
            try:
                if isinstance(row['data'], str):
                    data = datetime.strptime(row['data'], '%Y-%m-%d').date()
                else:
                    data = row['data']
            except ValueError:
                print(f"Erro ao converter data: {row['data']}. Pulando registro.")
                continue
                
            # Criar tupla de dados
            registros.append((
                row['municipio'],
                row['estado'],
                data,
                float(row['precipitacao']),
                row.get('fonte', 'IMPORTAÇÃO CSV')
            ))
        
        # Inserir dados usando execute_values para melhor performance
        query = """
        INSERT INTO chuvas_diarias 
            (municipio, estado, data, precipitacao_diaria, fonte)
        VALUES %s
        ON CONFLICT (municipio, data) DO UPDATE SET
            precipitacao_diaria = EXCLUDED.precipitacao_diaria,
            fonte = EXCLUDED.fonte,
            data_atualizacao = CURRENT_TIMESTAMP
        """
        
        execute_values(cursor, query, registros)
        conn.commit()
        print(f"Importados {len(registros)} registros de chuvas com sucesso!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao importar dados de chuvas: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def importar_alagamentos(arquivo_csv):
    """Importa dados de alagamentos de um arquivo CSV"""
    conn = conectar_banco()
    cursor = conn.cursor()

    try:
        # Ler o arquivo CSV usando pandas
        df = pd.read_csv(arquivo_csv)
        
        # Verificar as colunas necessárias
        colunas_necessarias = ['municipio', 'estado', 'data', 'local']
        for coluna in colunas_necessarias:
            if coluna not in df.columns:
                print(f"Erro: Coluna '{coluna}' não encontrada no arquivo CSV.")
                return False
        
        # Formatar e preparar dados
        registros = []
        for _, row in df.iterrows():
            # Converter string de data para objeto date
            try:
                if isinstance(row['data'], str):
                    data = datetime.strptime(row['data'], '%Y-%m-%d').date()
                else:
                    data = row['data']
            except ValueError:
                print(f"Erro ao converter data: {row['data']}. Pulando registro.")
                continue
                
            # Criar tupla de dados
            registros.append((
                row['municipio'],
                row['estado'],
                data,
                row['local'],
                row.get('latitude', None),
                row.get('longitude', None),
                row.get('nivel_gravidade', 'médio'),
                int(row.get('mortos', 0)),
                int(row.get('afetados', 0)),
                row.get('descricao', None),
                row.get('fonte', 'IMPORTAÇÃO CSV')
            ))
        
        # Inserir dados
        query = """
        INSERT INTO alagamentos 
            (municipio, estado, data, local, latitude, longitude, 
             nivel_gravidade, dh_mortos, dh_afetados, descricao, fonte)
        VALUES %s
        """
        
        execute_values(cursor, query, registros)
        conn.commit()
        print(f"Importados {len(registros)} registros de alagamentos com sucesso!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao importar dados de alagamentos: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def imprimir_uso():
    """Imprime instruções de uso do script"""
    print("Uso: python import_data.py [chuvas|alagamentos] arquivo.csv")
    print("Exemplo: python import_data.py chuvas ../data/historico_chuvas.csv")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        imprimir_uso()
        sys.exit(1)
        
    tipo = sys.argv[1].lower()
    arquivo = sys.argv[2]
    
    if not os.path.exists(arquivo):
        print(f"Erro: Arquivo {arquivo} não encontrado.")
        sys.exit(1)
        
    if tipo == "chuvas":
        sucesso = importar_chuvas(arquivo)
    elif tipo == "alagamentos":
        sucesso = importar_alagamentos(arquivo)
    else:
        print(f"Erro: Tipo inválido '{tipo}'. Use 'chuvas' ou 'alagamentos'.")
        imprimir_uso()
        sys.exit(1)
        
    sys.exit(0 if sucesso else 1) 