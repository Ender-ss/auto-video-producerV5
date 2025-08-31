#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.automations import GEMINI_KEYS_ROTATION, load_gemini_keys, get_gemini_keys_count
from datetime import datetime

# Carregar as chaves
def check_gemini_keys_status():
    print("==== STATUS DAS CHAVES GEMINI ====")
    
    # Carregar chaves
    load_gemini_keys()
    
    print(f"\n📊 INFORMAÇÕES GERAIS:")
    print(f"Total de chaves carregadas: {get_gemini_keys_count()}")
    print(f"Data do último reset: {GEMINI_KEYS_ROTATION['last_reset']}")
    print(f"Data atual: {datetime.now().date()}")
    
    # Verificar se houve reset hoje
    if GEMINI_KEYS_ROTATION['last_reset'] != datetime.now().date():
        print("⚠️  O sistema não resetou as contagens hoje! Isso pode causar problemas.")
    
    print(f"\n📋 DETALHES DAS CHAVES:")
    
    # Contadores
    total_requests = 0
    available_keys = 0
    exhausted_keys = 0
    
    # Limite por chave definido no sistema
    key_limit = 40
    
    # Verificar cada chave
    for i, key in enumerate(GEMINI_KEYS_ROTATION['keys']):
        usage = GEMINI_KEYS_ROTATION['usage_count'].get(key, 0)
        total_requests += usage
        
        # Status da chave
        if usage >= key_limit:
            status = "🔴 ESGOTADA"
            exhausted_keys += 1
        else:
            status = "🟢 DISPONÍVEL"
            available_keys += 1
        
        # Nome da chave no arquivo de configuração
        key_name = f"gemini_{i+1}"
        
        # Porcentagem de uso
        usage_percentage = (usage / key_limit) * 100 if key_limit > 0 else 0
        
        print(f"{key_name}: {usage}/{key_limit} requisições ({usage_percentage:.1f}%) - {status}")
    
    print(f"\n📈 RESUMO:")
    print(f"Total de requisições hoje: {total_requests}")
    print(f"Chaves disponíveis: {available_keys}")
    print(f"Chaves esgotadas: {exhausted_keys}")
    print(f"Limite diário por chave: {key_limit}")
    
    # Verificar se o número de chaves disponíveis corresponde ao número de tentativas que o sistema está usando
    print(f"\n🔍 MÁXIMO DE TENTATIVAS PREVISTO:")
    print(f"get_gemini_keys_count() retorna: {get_gemini_keys_count()}")
    print(f"No entanto, apenas {available_keys} chaves estão realmente disponíveis para uso")
    
    # Sugestão
    if available_keys < get_gemini_keys_count():
        print("\n💡 SUGESTÃO:")
        print("O sistema está limitado pelo número de chaves disponíveis (não esgotadas), não pelo total de chaves.")
        print("Para usar mais chaves, você pode:")
        print("1. Aguardar o reset automático (meia-noite UTC)")
        print("2. Executar manualmente: python reset_gemini_usage.py")
    
    print("\n===================================")

if __name__ == "__main__":
    check_gemini_keys_status()