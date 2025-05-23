#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico avançado para debugging das APIs
"""

import os
import sys
import psycopg2
from datetime import datetime, date, timedelta
import json
from decimal import Decimal
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Configuração do banco usando .env
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT'),
    'sslmode': 'require'
}

def conectar_db():
    """Conecta ao banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def debug_previsao_api():
    """Debug da API de previsão"""
    print("\n🔍 DEBUG: API de Previsão")
    print("=" * 50)
    
    conn = conectar_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Teste 1: Verificar dados disponíveis
    print("📊 Dados disponíveis na tabela previsoes:")
    cursor.execute("""
        SELECT DISTINCT cidade, estado, COUNT(*) as total
        FROM previsoes 
        WHERE data >= CURRENT_DATE
        GROUP BY cidade, estado
        ORDER BY total DESC
        LIMIT 10
    """)
    
    resultados = cursor.fetchall()
    for cidade, estado, total in resultados:
        print(f"   - {cidade}, {estado}: {total} registros")
    
    # Teste 2: Simular chamadas da API
    print("\n🧪 Simulando chamadas da API:")
    
    test_cases = [
        {"cidade": "Rio de Janeiro", "estado": "RJ"},
        {"cidade": "Angra dos Reis", "estado": "RJ"},
        {"cidade": "São Paulo", "estado": "SP"},
        {"cidade": "rio de janeiro", "estado": "rj"},  # Teste case-insensitive
    ]
    
    for caso in test_cases:
        print(f"\n   🔍 Testando: {caso['cidade']}, {caso['estado']}")
        
        # Query exata como na API
        query = """
            SELECT p.*, 
                   COALESCE(a.total_afetados, 0) as historico_afetados
            FROM previsoes p
            LEFT JOIN (
                SELECT municipio, estado, SUM(dh_afetados) as total_afetados
                FROM alagamentos 
                WHERE municipio ILIKE %s AND estado ILIKE %s
                GROUP BY municipio, estado
            ) a ON LOWER(p.cidade) = LOWER(a.municipio) AND LOWER(p.estado) = LOWER(a.estado)
            WHERE LOWER(p.cidade) = LOWER(%s) 
            AND LOWER(p.estado) = LOWER(%s)
            AND p.data >= %s
            ORDER BY p.data
        """
        
        params = (
            caso['cidade'], caso['estado'],
            caso['cidade'], caso['estado'],
            date.today()
        )
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        print(f"      📈 Resultados: {len(resultados)} registros")
        if resultados:
            for i, row in enumerate(resultados[:3]):  # Mostrar apenas os 3 primeiros
                print(f"         {i+1}. Data: {row[3]}, Precipitação: {row[6]}mm")
    
    cursor.close()
    conn.close()

def debug_historico_api():
    """Debug da API de histórico"""
    print("\n🔍 DEBUG: API de Histórico")
    print("=" * 50)
    
    conn = conectar_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Verificar dados de chuvas históricas
    print("📊 Dados de chuvas históricas disponíveis:")
    cursor.execute("""
        SELECT DISTINCT municipio, estado, COUNT(*) as total,
               MIN(data) as data_inicio, MAX(data) as data_fim
        FROM chuvas_diarias 
        GROUP BY municipio, estado
        ORDER BY total DESC
        LIMIT 10
    """)
    
    resultados = cursor.fetchall()
    for municipio, estado, total, inicio, fim in resultados:
        print(f"   - {municipio}, {estado}: {total} registros ({inicio} a {fim})")
    
    # Verificar dados de alagamentos
    print("\n📊 Dados de alagamentos disponíveis:")
    cursor.execute("""
        SELECT DISTINCT municipio, estado, COUNT(*) as total,
               MIN(data) as data_inicio, MAX(data) as data_fim
        FROM alagamentos 
        GROUP BY municipio, estado
        ORDER BY total DESC
    """)
    
    resultados = cursor.fetchall()
    for municipio, estado, total, inicio, fim in resultados:
        print(f"   - {municipio}, {estado}: {total} registros ({inicio} a {fim})")
    
    # Teste de queries do histórico
    print("\n🧪 Testando queries de histórico:")
    
    test_cases = [
        {"cidade": "Rio de Janeiro", "estado": "RJ"},
        {"cidade": "ANGRA DOS REIS", "estado": "RJ"},
        {"cidade": "angra dos reis", "estado": "rj"},
    ]
    
    for caso in test_cases:
        print(f"\n   🔍 Testando: {caso['cidade']}, {caso['estado']}")
        
        # Query de chuvas
        cursor.execute("""
            SELECT data, precipitacao_diaria 
            FROM chuvas_diarias 
            WHERE LOWER(municipio) = LOWER(%s) 
            AND LOWER(estado) = LOWER(%s)
            ORDER BY data DESC 
            LIMIT 30
        """, (caso['cidade'], caso['estado']))
        
        chuvas = cursor.fetchall()
        print(f"      🌧️  Chuvas: {len(chuvas)} registros")
        
        # Query de alagamentos
        cursor.execute("""
            SELECT data, local, dh_afetados 
            FROM alagamentos 
            WHERE LOWER(municipio) = LOWER(%s) 
            AND LOWER(estado) = LOWER(%s)
            ORDER BY data DESC
        """, (caso['cidade'], caso['estado']))
        
        alagamentos = cursor.fetchall()
        print(f"      🌊 Alagamentos: {len(alagamentos)} registros")
    
    cursor.close()
    conn.close()

def verificar_problemas_encoding():
    """Verifica problemas de encoding nos nomes das cidades"""
    print("\n🔍 DEBUG: Problemas de Encoding")
    print("=" * 50)
    
    conn = conectar_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Verificar caracteres especiais
    print("🔤 Cidades com caracteres especiais:")
    cursor.execute("""
        SELECT DISTINCT cidade, estado 
        FROM previsoes 
        WHERE cidade ~ '[^A-Za-z0-9 ]'
        ORDER BY cidade
        LIMIT 10
    """)
    
    resultados = cursor.fetchall()
    for cidade, estado in resultados:
        print(f"   - '{cidade}', {estado} (bytes: {repr(cidade.encode())})")
    
    cursor.close()
    conn.close()

def gerar_dados_teste():
    """Gera dados de teste para debugging"""
    print("\n🔧 Gerando dados de teste...")
    
    conn = conectar_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # Inserir dados de teste para São Paulo
        print("📝 Inserindo dados de teste para São Paulo:")
        
        hoje = date.today()
        for i in range(5):
            data_previsao = hoje + timedelta(days=i)
            cursor.execute("""
                INSERT INTO previsoes 
                (cidade, estado, data, precipitacao, probabilidade_alagamento, nivel_risco, afetados_estimados)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (cidade, estado, data) DO UPDATE SET
                precipitacao = EXCLUDED.precipitacao,
                updated_at = CURRENT_TIMESTAMP
            """, ('São Paulo', 'SP', data_previsao, 10.5 + i*2, 15.0, 'medio', 50))
        
        # Inserir dados históricos de chuva para São Paulo
        for i in range(30):
            data_chuva = hoje - timedelta(days=i+1)
            cursor.execute("""
                INSERT INTO chuvas_diarias 
                (municipio, estado, data, precipitacao_diaria)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (municipio, estado, data) DO UPDATE SET
                precipitacao_diaria = EXCLUDED.precipitacao_diaria,
                updated_at = CURRENT_TIMESTAMP
            """, ('São Paulo', 'SP', data_chuva, 5.5 + i*0.5))
        
        # Inserir alagamento de teste
        cursor.execute("""
            INSERT INTO alagamentos 
            (municipio, estado, data, local, dh_afetados)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (municipio, estado, data, local) DO UPDATE SET
            dh_afetados = EXCLUDED.dh_afetados,
            updated_at = CURRENT_TIMESTAMP
        """, ('São Paulo', 'SP', hoje - timedelta(days=10), 'Centro', 100))
        
        conn.commit()
        print("✅ Dados de teste inseridos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados de teste: {e}")
        conn.rollback()
    
    cursor.close()
    conn.close()

def main():
    """Função principal"""
    print("🩺 DIAGNÓSTICO AVANÇADO DAS APIS")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    print("🔧 Verificando variáveis de ambiente:")
    for key in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_PORT']:
        value = os.getenv(key)
        if key == 'DB_PASSWORD':
            print(f"   {key}: {'***' if value else 'NÃO ENCONTRADO'}")
        else:
            print(f"   {key}: {value if value else 'NÃO ENCONTRADO'}")
    
    if not all([os.getenv(key) for key in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_PORT']]):
        print("❌ Algumas variáveis de ambiente não foram encontradas!")
        print("Certifique-se de que o arquivo .env está no diretório correto.")
        return
    
    # Verificar conexão
    conn = conectar_db()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados!")
        return
    conn.close()
    
    print("✅ Conexão com banco de dados OK!")
    
    # Executar diagnósticos
    debug_previsao_api()
    debug_historico_api()
    verificar_problemas_encoding()
    
    # Perguntar se deve gerar dados de teste
    resposta = input("\n❓ Deseja gerar dados de teste para São Paulo? (s/n): ").lower()
    if resposta == 's':
        gerar_dados_teste()
    
    print("\n✅ Diagnóstico concluído!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Analise os resultados acima")
    print("2. Verifique se há problemas de case-sensitivity")
    print("3. Confirme se os parâmetros estão sendo enviados corretamente do frontend")
    print("4. Se necessário, execute novamente após gerar dados de teste")

if __name__ == "__main__":
    main() 