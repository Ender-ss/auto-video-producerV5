#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(__file__))

from routes.automations import GEMINI_KEYS_ROTATION, get_next_gemini_key

print("=== ESTADO ATUAL DAS CHAVES GEMINI ===")
print(f"Keys carregadas: {len(GEMINI_KEYS_ROTATION['keys'])}")
print(f"Usage count: {GEMINI_KEYS_ROTATION['usage_count']}")
print(f"Current index: {GEMINI_KEYS_ROTATION['current_index']}")
print(f"Last reset: {GEMINI_KEYS_ROTATION['last_reset']}")

print("\n=== TESTE DE OBTENÇÃO DE CHAVE ===")
key = get_next_gemini_key()
if key:
    print(f"✅ Chave obtida: {key[:20]}...")
    print(f"Novo usage count: {GEMINI_KEYS_ROTATION['usage_count']}")
else:
    print("❌ Nenhuma chave disponível")
    print("Motivo: Todas as chaves atingiram o limite diário")