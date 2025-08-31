#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.automations import GEMINI_KEYS_ROTATION, load_gemini_keys

def fix_gemini_quota_issue():
    """Corrigir problema de quota da chave gemini_2"""
    print("🔧 Correção de Quota - Chaves Gemini")
    print("=" * 50)
    
    # Carregar chaves
    load_gemini_keys()
    
    print(f"\n📊 Estado atual:")
    print(f"   Keys: {len(GEMINI_KEYS_ROTATION['keys'])}")
    print(f"   Usage count: {GEMINI_KEYS_ROTATION['usage_count']}")
    print(f"   Current index: {GEMINI_KEYS_ROTATION['current_index']}")
    print(f"   Last reset: {GEMINI_KEYS_ROTATION['last_reset']}")
    
    # Carregar configuração para identificar a chave problemática
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'api_keys.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return
    
    # Identificar a chave gemini_2 que está com problema
    gemini_2_key = config.get('gemini_2')
    
    if gemini_2_key:
        print(f"\n🔍 Chave gemini_2 identificada: {gemini_2_key[:20]}...")
        
        # Marcar como esgotada (8 usos = limite)
        GEMINI_KEYS_ROTATION['usage_count'][gemini_2_key] = 40
        
        print(f"✅ Chave gemini_2 marcada como esgotada (8/8 usos)")
        
        # Mostrar estado atualizado
        print(f"\n📊 Estado após correção:")
        for i, key in enumerate(GEMINI_KEYS_ROTATION['keys']):
            usage = GEMINI_KEYS_ROTATION['usage_count'].get(key, 0)
            key_name = f"gemini_{i+1}"
            status = "🔴 ESGOTADA" if usage >= 8 else "🟢 DISPONÍVEL"
            print(f"   {key_name}: {usage}/8 usos - {status}")
        
        # Verificar quantas chaves ainda estão disponíveis
        available_keys = 0
        for key in GEMINI_KEYS_ROTATION['keys']:
            if GEMINI_KEYS_ROTATION['usage_count'].get(key, 0) < 40:
                available_keys += 1
        
        print(f"\n📈 Resumo:")
        print(f"   Total de chaves: {len(GEMINI_KEYS_ROTATION['keys'])}")
        print(f"   Chaves disponíveis: {available_keys}")
        print(f"   Chaves esgotadas: {len(GEMINI_KEYS_ROTATION['keys']) - available_keys}")
        
        if available_keys > 0:
            print(f"\n✅ Sistema funcionando! {available_keys} chaves ainda disponíveis.")
        else:
            print(f"\n⚠️  Todas as chaves esgotadas! Fallback será ativado.")
            
    else:
        print("❌ Chave gemini_2 não encontrada na configuração")
    
    print("\n" + "=" * 50)
    print("🏁 Correção concluída!")
    print("📋 O sistema agora evitará usar a chave com problema de quota.")

if __name__ == "__main__":
    fix_gemini_quota_issue()