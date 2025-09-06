#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug específico da geração de prompts para identificar o problema
"""

import sys
sys.path.insert(0, '.')

from services.storyteller_service import PromptVariator

def debug_prompt_generation():
    """Debug da geração de prompts"""
    
    print("🔍 DEBUG DA GERAÇÃO DE PROMPTS")
    print("=" * 50)
    
    prompt_variator = PromptVariator()
    
    # TESTE 1: COM remoção de cabeçalhos
    print("\n1️⃣ TESTANDO PROMPT COM remove_chapter_headers=True")
    print("-" * 40)
    
    prompt_with_removal = prompt_variator.generate_varied_prompt(
        title="Teste Debug",
        premise="Uma história para debug",
        agent_type="millionaire_stories",
        target_chars=2500,
        chapter_num=1,
        total_chapters=3,
        previous_context=None,
        previous_chapters=[],
        remove_chapter_headers=True  # PARÂMETRO CRÍTICO
    )
    
    print(f"📝 PROMPT GERADO (COM REMOÇÃO):")
    print(f"Tamanho: {len(prompt_with_removal)} caracteres")
    print(f"Contém 'CAPÍTULO 1:': {'CAPÍTULO 1:' in prompt_with_removal}")
    print(f"\nÚltimas 200 caracteres do prompt:")
    print(f"'{prompt_with_removal[-200:]}'")
    
    # TESTE 2: SEM remoção de cabeçalhos
    print("\n\n2️⃣ TESTANDO PROMPT COM remove_chapter_headers=False")
    print("-" * 40)
    
    prompt_without_removal = prompt_variator.generate_varied_prompt(
        title="Teste Debug",
        premise="Uma história para debug",
        agent_type="millionaire_stories",
        target_chars=2500,
        chapter_num=1,
        total_chapters=3,
        previous_context=None,
        previous_chapters=[],
        remove_chapter_headers=False  # PARÂMETRO CRÍTICO
    )
    
    print(f"📝 PROMPT GERADO (SEM REMOÇÃO):")
    print(f"Tamanho: {len(prompt_without_removal)} caracteres")
    print(f"Contém 'CAPÍTULO 1:': {'CAPÍTULO 1:' in prompt_without_removal}")
    print(f"\nÚltimas 200 caracteres do prompt:")
    print(f"'{prompt_without_removal[-200:]}'")
    
    # COMPARAÇÃO
    print("\n\n🔍 ANÁLISE COMPARATIVA")
    print("=" * 50)
    
    print(f"Prompt COM remoção contém 'CAPÍTULO 1:': {'CAPÍTULO 1:' in prompt_with_removal}")
    print(f"Prompt SEM remoção contém 'CAPÍTULO 1:': {'CAPÍTULO 1:' in prompt_without_removal}")
    
    if 'CAPÍTULO 1:' in prompt_with_removal:
        print("❌ PROBLEMA IDENTIFICADO: O prompt COM remoção ainda contém 'CAPÍTULO 1:'")
        print("   Isso significa que a condição na linha 431 não está funcionando corretamente.")
    else:
        print("✅ CORRETO: O prompt COM remoção NÃO contém 'CAPÍTULO 1:'")
    
    if 'CAPÍTULO 1:' not in prompt_without_removal:
        print("❌ PROBLEMA: O prompt SEM remoção deveria conter 'CAPÍTULO 1:'")
    else:
        print("✅ CORRETO: O prompt SEM remoção contém 'CAPÍTULO 1:'")
    
    # Salvar prompts para análise
    with open('debug_prompt_with_removal.txt', 'w', encoding='utf-8') as f:
        f.write("PROMPT COM REMOÇÃO DE CABEÇALHOS (remove_chapter_headers=True)\n")
        f.write("=" * 60 + "\n\n")
        f.write(prompt_with_removal)
    
    with open('debug_prompt_without_removal.txt', 'w', encoding='utf-8') as f:
        f.write("PROMPT SEM REMOÇÃO DE CABEÇALHOS (remove_chapter_headers=False)\n")
        f.write("=" * 60 + "\n\n")
        f.write(prompt_without_removal)
    
    print("\n💾 Prompts salvos em:")
    print("   - debug_prompt_with_removal.txt")
    print("   - debug_prompt_without_removal.txt")
    
    print("\n🎯 CONCLUSÃO:")
    if 'CAPÍTULO 1:' in prompt_with_removal:
        print("   A lógica da condição na linha 431 precisa ser corrigida.")
        print("   Atualmente: {f'CAPÍTULO {chapter_num}:' if not remove_chapter_headers else ''}")
        print("   Isso significa: SE remove_chapter_headers=True, NÃO incluir cabeçalho")
        print("   Mas o cabeçalho ainda está aparecendo, indicando problema na lógica.")
    else:
        print("   A lógica do prompt está correta. O problema pode estar em outro lugar.")

if __name__ == "__main__":
    debug_prompt_generation()