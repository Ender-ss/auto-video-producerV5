#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(__file__))

from routes.automations import GEMINI_KEYS_ROTATION, load_gemini_keys

print("=== RESET FORÇADO DAS CHAVES GEMINI ===")

# Carregar chaves
keys = load_gemini_keys()
print(f"Chaves carregadas: {len(keys)}")

# Estado atual
print(f"\nEstado antes do reset:")
print(f"  Keys: {len(GEMINI_KEYS_ROTATION['keys'])}")
print(f"  Usage count: {GEMINI_KEYS_ROTATION['usage_count']}")
print(f"  Current index: {GEMINI_KEYS_ROTATION['current_index']}")
print(f"  Last reset: {GEMINI_KEYS_ROTATION['last_reset']}")

# Reset forçado
GEMINI_KEYS_ROTATION['usage_count'] = {}
GEMINI_KEYS_ROTATION['current_index'] = 0
GEMINI_KEYS_ROTATION['last_reset'] = datetime.now().date()

print(f"\nEstado após reset forçado:")
print(f"  Keys: {len(GEMINI_KEYS_ROTATION['keys'])}")
print(f"  Usage count: {GEMINI_KEYS_ROTATION['usage_count']}")
print(f"  Current index: {GEMINI_KEYS_ROTATION['current_index']}")
print(f"  Last reset: {GEMINI_KEYS_ROTATION['last_reset']}")

# Testar obtenção de chave
from routes.automations import get_next_gemini_key
next_key = get_next_gemini_key()
print(f"\nPróxima chave disponível: {next_key[:20] if next_key else 'None'}...")

if next_key:
    print("✅ Reset bem-sucedido! Chaves disponíveis para uso.")
else:
    print("❌ Reset falhou. Ainda não há chaves disponíveis.")