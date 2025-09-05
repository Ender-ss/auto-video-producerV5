#!/usr/bin/env python3
"""
Teste simples de integração do Storyteller com rotação de chaves Gemini
"""
import sys
import os
sys.path.insert(0, '.')

print("=== TESTE DE INTEGRAÇÃO STORYTELLER ===")

# 1. Verificar chaves
print("\n1. Verificando chaves Gemini...")
try:
    import json
    with open('config/api_keys.json', 'r') as f:
        keys = json.load(f)
    
    gemini_keys = {k: v for k, v in keys.items() if 'gemini' in k.lower()}
    print(f"   ✅ {len(gemini_keys)} chaves encontradas")
    
    for key_name, key_value in gemini_keys.items():
        print(f"   - {key_name}: {key_value[:15]}...")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 2. Testar rotação de chaves
print("\n2. Testando rotação de chaves...")
try:
    from routes.automations import get_next_gemini_key
    key = get_next_gemini_key()
    if key:
        print(f"   ✅ Rotação funcionando: {key[:15]}...")
    else:
        print("   ❌ Nenhuma chave disponível")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 3. Testar serviço
print("\n3. Testando Storyteller Service...")
try:
    from services.storyteller_service import storyteller_service
    print("   ✅ Serviço importado com sucesso")
    
    # Teste rápido de geração
    print("\n4. Testando geração de roteiro...")
    result = storyteller_service.generate_storyteller_script(
        "Teste Rápido",
        "Como um jovem empreendedor superou desafios",
        "millionaire_stories",
        1
    )
    
    if result.get('success'):
        print("   ✅ ROTEIRO GERADO COM SUCESSO!")
        print(f"   - Título: {result.get('title', 'N/A')}")
        print(f"   - Capítulos: {len(result.get('chapters', []))}")
        print(f"   - Caracteres: {len(result.get('full_script', ''))}")
        
        # Verificar se usou chave real
        if hasattr(storyteller_service, '_get_next_gemini_key'):
            key_used = storyteller_service._get_next_gemini_key()
            print(f"   - Chave usada: {key_used[:15]}...")
    else:
        print(f"   ❌ Erro: {result.get('error', 'Erro desconhecido')}")
        
except Exception as e:
    print(f"   ❌ Erro crítico: {e}")

print("\n=== TESTE CONCLUÍDO ===")