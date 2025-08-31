#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Script para mudar o limite de requisições por chave Gemini de 8 para 40
def find_quota_limit_locations():
    print("==== LOCALIZAÇÃO DO LIMITE DE QUOTA GEMINI ====")
    print("\nO sistema está configurado com limite de 8 requisições por chave por dia.")
    print("Para alterá-lo para 40, é necessário modificar esses locais:")
    
    print("\n1. No arquivo routes/automations.py:")
    print("   - Na função handle_gemini_429_error: if GEMINI_KEYS_ROTATION['usage_count'].get(key, 0) < 8:")
    print("   - Na função check_gemini_availability: if usage < 8:  # Limite de 8 por chave")
    
    print("\n2. No arquivo fix_gemini_key_quota.py:")
    print("   - Marca chaves esgotadas como 8 usos: GEMINI_KEYS_ROTATION['usage_count'][gemini_2_key] = 8")
    
    print("\n3. No arquivo routes/settings.py:")
    print("   - Na rota /gemini-quota-status: 'usage_limit': 8,")
    
    print("\n4. No arquivo check_gemini_keys_status.py:")
    print("   - Definição do limite: key_limit = 8")
    
    print("\n❌ Por que a alteração para 40 não surtiu efeito?")
    print("- O limite de 8 está hardcoded em vários lugares do código")
    print("- A alteração não foi feita em todos esses pontos")
    print("- O sistema continua a verificar se a chave tem menos de 8 usos")
    
    print("\n🛠️  COMO MUDAR PARA 40 REQUISIÇÕES:")
    print("1. Abra cada um dos arquivos listados acima")
    print("2. Substitua todas as ocorrências de '8' (relacionadas ao limite Gemini) por '40'")
    print("3. Salve as alterações")
    print("4. Reinicie o backend (python app.py)")
    print("\n⚠️  NOTA IMPORTANTE:")
    print("- Certifique-se de alterar apenas os valores que se referem ao limite de quota, não outros números no código!")
    print("- Recomendado fazer backup dos arquivos antes de modificar")
    
    print("\n📊 BENEFÍCIOS DA ALTERAÇÃO:")
    print("- Menos falhas de pipeline devido a quota esgotada")
    print("- Mais tentativas reais com cada chave")
    print("- Melhor utilização das chaves disponíveis")
    
    print("\n=============================================")

if __name__ == "__main__":
    find_quota_limit_locations()