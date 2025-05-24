#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico simples - teste rápido das APIs
"""

import os
import psycopg2
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Verificar se as variáveis foram carregadas
print("🔧 Verificando variáveis de ambiente:")
print(f"DB_NAME: {os.getenv('DB_NAME', 'NÃO ENCONTRADO')}")
print(f"DB_USER: {os.getenv('DB_USER', 'NÃO ENCONTRADO')}")
print(f"DB_HOST: {os.getenv('DB_HOST', 'NÃO ENCONTRADO')}")
print(f"DB_PORT: {os.getenv('DB_PORT', 'NÃO ENCONTRADO')}")
print(f"DB_PASSWORD: {'***' if os.getenv('DB_PASSWORD') else 'NÃO ENCONTRADO'}")
print()

def test_connection():
    """Teste básico de conexão"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT'),
            sslmode='require'
        )
        print("✅ Conexão OK!")
        return conn
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None

def debug_previsao_simples():
    """Debug simples da API de previsão"""
    print("\n🔍 DEBUG: Previsão de Chuvas")
    print("=" * 40)
    
    conn = test_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Teste 1: Ver quais cidades existem
    print("📊 Cidades disponíveis:")
    cursor.execute("""
        SELECT DISTINCT cidade, estado, COUNT(*) as total
        FROM previsoes 
        WHERE data >= CURRENT_DATE
        GROUP BY cidade, estado
        ORDER BY total DESC
        LIMIT 5
    """)
    
    cidades = cursor.fetchall()
    for cidade, estado, total in cidades:
        print(f"   - {cidade}, {estado}: {total} registros")
    
    # Teste 2: Simular a query exata da API
    print(f"\n🧪 Testando query para Rio de Janeiro, RJ:")
    
    query = """
        SELECT cidade, estado, data, precipitacao, nivel_risco
        FROM previsoes 
        WHERE LOWER(TRIM(cidade)) = LOWER(TRIM(%s)) 
        AND LOWER(TRIM(estado)) = LOWER(TRIM(%s))
        AND data >= %s
        ORDER BY data
    """
    
    cursor.execute(query, ('Rio de Janeiro', 'RJ', date.today()))
    resultados = cursor.fetchall()
    
    print(f"   📈 Resultados: {len(resultados)}")
    for i, (cidade, estado, data, precip, risco) in enumerate(resultados[:3]):
        print(f"      {i+1}. {data}: {precip}mm - {risco}")
    
    # Teste 3: Verificar se problema é case-sensitivity
    print(f"\n🧪 Testando diferentes variações do nome:")
    
    test_cases = [
        ('Rio de Janeiro', 'RJ'),
        ('rio de janeiro', 'rj'),
        ('RIO DE JANEIRO', 'RJ'),
        ('Rio de Janeiro', 'rj')
    ]
    
    for cidade_test, estado_test in test_cases:
        cursor.execute(query, (cidade_test, estado_test, date.today()))
        count = len(cursor.fetchall())
        print(f"      '{cidade_test}', '{estado_test}': {count} resultados")
    
    cursor.close()
    conn.close()

def debug_historico_simples():
    """Debug simples do histórico"""
    print("\n🔍 DEBUG: Histórico de Chuvas")
    print("=" * 40)
    
    conn = test_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Ver cidades no histórico
    cursor.execute("""
        SELECT DISTINCT municipio, estado, COUNT(*) as total
        FROM chuvas_diarias 
        GROUP BY municipio, estado
        ORDER BY total DESC
        LIMIT 5
    """)
    
    cidades = cursor.fetchall()
    print("📊 Cidades com histórico:")
    for municipio, estado, total in cidades:
        print(f"   - {municipio}, {estado}: {total} registros")
    
    # Testar query do histórico
    cursor.execute("""
        SELECT municipio, estado, data, precipitacao_diaria
        FROM chuvas_diarias 
        WHERE LOWER(TRIM(municipio)) = LOWER(TRIM(%s)) 
        AND LOWER(TRIM(estado)) = LOWER(TRIM(%s))
        ORDER BY data DESC 
        LIMIT 5
    """, ('ANGRA DOS REIS', 'RJ'))
    
    resultados = cursor.fetchall()
    print(f"\n🧪 Histórico Angra dos Reis: {len(resultados)} resultados")
    for municipio, estado, data, precip in resultados:
        print(f"   {data}: {precip}mm")
    
    cursor.close()
    conn.close()

def inserir_dados_teste():
    """Insere dados de teste para São Paulo"""
    print("\n🔧 Inserindo dados de teste...")
    
    conn = test_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # Dados de previsão para São Paulo
        hoje = date.today()
        for i in range(5):
            data_prev = hoje + timedelta(days=i)
            cursor.execute("""
                INSERT INTO previsoes 
                (cidade, estado, data, precipitacao, probabilidade_alagamento, nivel_risco, afetados_estimados)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (cidade, estado, data) DO UPDATE SET
                precipitacao = EXCLUDED.precipitacao,
                updated_at = CURRENT_TIMESTAMP
            """, ('São Paulo', 'SP', data_prev, 10.0 + i*5, 20.0, 'medio', 100))
        
        conn.commit()
        print("✅ Dados de teste inseridos!")
        
        # Verificar se foram inseridos
        cursor.execute("""
            SELECT data, precipitacao FROM previsoes 
            WHERE cidade = 'São Paulo' AND estado = 'SP'
            ORDER BY data
        """)
        resultados = cursor.fetchall()
        print(f"   📊 {len(resultados)} registros criados para São Paulo")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    
    cursor.close()
    conn.close()

def main():
    print("🩺 DIAGNÓSTICO SIMPLES - APIS")
    print("=" * 50)
    
    debug_previsao_simples()
    debug_historico_simples()
    
    resposta = input("\n❓ Inserir dados de teste para São Paulo? (s/n): ")
    if resposta.lower() == 's':
        inserir_dados_teste()
    
    print("\n✅ Diagnóstico concluído!")

if __name__ == "__main__":
    main() 