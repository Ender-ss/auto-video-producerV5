#!/usr/bin/env python3
"""
Script para diagnosticar múltiplas instâncias da variável GEMINI_KEYS_ROTATION
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

print("=== DIAGNÓSTICO DE INSTÂNCIAS GEMINI ===")

# Teste 1: Importar diretamente de routes.automations
print("\n1. Importando de routes.automations:")
from routes.automations import GEMINI_KEYS_ROTATION as rotation1, get_next_gemini_key
print(f"   ID da variável: {id(rotation1)}")
print(f"   Keys: {len(rotation1['keys'])}")
print(f"   Usage count: {rotation1['usage_count']}")

# Teste 2: Importar como faz ai_services.py
print("\n2. Importando como ai_services.py:")
sys.path.append(os.path.join(os.path.dirname(__file__), 'routes'))
from automations import GEMINI_KEYS_ROTATION as rotation2, get_next_gemini_key as get_key2
print(f"   ID da variável: {id(rotation2)}")
print(f"   Keys: {len(rotation2['keys'])}")
print(f"   Usage count: {rotation2['usage_count']}")

# Teste 3: Verificar se são a mesma instância
print("\n3. Comparação de instâncias:")
print(f"   São a mesma instância? {rotation1 is rotation2}")
print(f"   IDs iguais? {id(rotation1) == id(rotation2)}")

# Teste 4: Testar get_next_gemini_key
print("\n4. Teste de obtenção de chave:")
key1 = get_next_gemini_key()
key2 = get_key2()
print(f"   Chave 1: {key1[:20] if key1 else 'None'}...")
print(f"   Chave 2: {key2[:20] if key2 else 'None'}...")
print(f"   São iguais? {key1 == key2}")

# Teste 5: Verificar estado após obtenção
print("\n5. Estado após obtenção:")
print(f"   rotation1 usage: {rotation1['usage_count']}")
print(f"   rotation2 usage: {rotation2['usage_count']}")

# Teste 6: Simular importação da pipeline
print("\n6. Simulando importação da pipeline:")
try:
    # Simular o que acontece em services/ai_services.py
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'routes'))
    from automations import get_next_gemini_key as pipeline_get_key
    
    pipeline_key = pipeline_get_key()
    print(f"   Chave da pipeline: {pipeline_key[:20] if pipeline_key else 'None'}...")
    
    # Verificar se afetou as outras instâncias
    print(f"   rotation1 após pipeline: {rotation1['usage_count']}")
    print(f"   rotation2 após pipeline: {rotation2['usage_count']}")
    
except Exception as e:
    print(f"   Erro na simulação: {e}")

print("\n=== FIM DO DIAGNÓSTICO ===")