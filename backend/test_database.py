#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar os dados no banco de dados
Execute: python backend/test_database.py
"""

from api import fetch_data
import json

def test_database():
    print("=" * 60)
    print("TESTE DE DIAGNÓSTICO DO BANCO DE DADOS B3")
    print("=" * 60)
    
    # 1. Total de registros
    print("\n1. Total de registros no banco:")
    total_query = "SELECT COUNT(*) as total FROM cotacoes"
    total_result = fetch_data(total_query)
    if total_result:
        print(f"   Total: {total_result[0]['total']} registros")
    else:
        print("   ERRO: Não foi possível conectar ao banco")
        return
    
    # 2. Datas disponíveis
    print("\n2. Datas disponíveis (últimas 10):")
    dates_query = """
        SELECT 
            DataPregao, 
            COUNT(*) as quantidade,
            COUNT(DISTINCT Ativo) as ativos_distintos
        FROM cotacoes 
        GROUP BY DataPregao 
        ORDER BY DataPregao DESC
        LIMIT 10
    """
    dates_result = fetch_data(dates_query)
    if dates_result:
        for row in dates_result:
            print(f"   {row['DataPregao']}: {row['quantidade']} registros, {row['ativos_distintos']} ativos distintos")
    else:
        print("   Nenhuma data encontrada")
    
    # 3. Teste com PETR4
    print("\n3. Teste de busca para PETR4:")
    ativo_query = "SELECT * FROM cotacoes WHERE UPPER(TRIM(Ativo)) = 'PETR4' ORDER BY DataPregao DESC"
    petr4_result = fetch_data(ativo_query)
    if petr4_result:
        print(f"   Total de registros para PETR4: {len(petr4_result)}")
        if len(petr4_result) > 0:
            print(f"   Primeira data: {petr4_result[0]['DataPregao']}")
            print(f"   Última data: {petr4_result[-1]['DataPregao']}")
            
            # Agrupar por data
            dates_petr4 = {}
            for row in petr4_result:
                data = str(row['DataPregao'])
                if data not in dates_petr4:
                    dates_petr4[data] = 0
                dates_petr4[data] += 1
            
            print(f"\n   Registros por data (últimas 10):")
            for i, (data, count) in enumerate(list(dates_petr4.items())[:10]):
                print(f"   {data}: {count} registro(s)")
    else:
        print("   Nenhum registro encontrado para PETR4")
    
    # 4. Verificar se há dados de múltiplos dias
    print("\n4. Verificação de múltiplas datas:")
    distinct_dates_query = "SELECT COUNT(DISTINCT DataPregao) as total_datas FROM cotacoes"
    distinct_dates_result = fetch_data(distinct_dates_query)
    if distinct_dates_result:
        total_datas = distinct_dates_result[0]['total_datas']
        print(f"   Total de datas distintas no banco: {total_datas}")
        if total_datas == 1:
            print("   ⚠️  ATENÇÃO: Apenas 1 data encontrada! Pode haver problema na extração.")
        else:
            print(f"   ✓ Múltiplas datas encontradas ({total_datas} datas)")
    
    # 5. Range de datas
    print("\n5. Range de datas:")
    range_query = """
        SELECT 
            MIN(DataPregao) as data_minima,
            MAX(DataPregao) as data_maxima
        FROM cotacoes
    """
    range_result = fetch_data(range_query)
    if range_result and range_result[0]['data_minima']:
        print(f"   Data mínima: {range_result[0]['data_minima']}")
        print(f"   Data máxima: {range_result[0]['data_maxima']}")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    test_database()

