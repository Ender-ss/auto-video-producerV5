#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.automations import GEMINI_KEYS_ROTATION
from datetime import datetime

print("🔄 Reset do Contador de Uso das Chaves Gemini")
print("=" * 50)

print(f"\n📊 Estado atual:")
print(f"   Keys: {len(GEMINI_KEYS_ROTATION['keys'])}")
print(f"   Usage count: {GEMINI_KEYS_ROTATION['usage_count']}")
print(f"   Current index: {GEMINI_KEYS_ROTATION['current_index']}")
print(f"   Last reset: {GEMINI_KEYS_ROTATION['last_reset']}")

# Reset manual
GEMINI_KEYS_ROTATION['usage_count'] = {}
GEMINI_KEYS_ROTATION['current_index'] = 0
GEMINI_KEYS_ROTATION['last_reset'] = datetime.now().date()

print(f"\n✅ Reset realizado!")
print(f"   Usage count: {GEMINI_KEYS_ROTATION['usage_count']}")
print(f"   Current index: {GEMINI_KEYS_ROTATION['current_index']}")
print(f"   Last reset: {GEMINI_KEYS_ROTATION['last_reset']}")

print("\n🏁 Reset concluído! As chaves Gemini estão prontas para uso.")