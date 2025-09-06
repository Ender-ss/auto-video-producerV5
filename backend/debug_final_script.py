#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug final da montagem do roteiro completo
"""

import sys
sys.path.insert(0, '.')

from services.storyteller_service import StorytellerService
import re

def debug_final_script():
    """Debug da montagem final do roteiro"""
    
    print("🔍 DEBUG DA MONTAGEM FINAL DO ROTEIRO")
    print("=" * 50)
    
    service = StorytellerService()
    
    # TESTE 1: COM remoção de cabeçalhos
    print("\n1️⃣ TESTANDO COM remove_chapter_headers=True")
    print("-" * 40)
    
    result_with_removal = service.generate_storyteller_script(
        title="Debug Final",
        premise="Uma história para debug final",
        agent_type="millionaire_stories",
        num_chapters=2,
        remove_chapter_headers=True  # PARÂMETRO CRÍTICO
    )
    
    script_with_removal = result_with_removal.get('full_script', '')
    
    print(f"📝 ROTEIRO COM REMOÇÃO:")
    print(f"Tamanho: {len(script_with_removal)} caracteres")
    
    # Contar cabeçalhos markdown
    markdown_headers = len(re.findall(r'^##\s*.*?[Cc]apítulo', script_with_removal, re.MULTILINE | re.IGNORECASE))
    internal_headers = len(re.findall(r'CAPÍTULO\s*\d+', script_with_removal, re.IGNORECASE))
    
    print(f"Cabeçalhos markdown (## Capítulo): {markdown_headers}")
    print(f"Cabeçalhos internos (CAPÍTULO X:): {internal_headers}")
    print(f"Total de cabeçalhos: {markdown_headers + internal_headers}")
    
    print(f"\nPrimeiros 500 caracteres:")
    print(f"'{script_with_removal[:500]}'")
    
    # TESTE 2: SEM remoção de cabeçalhos
    print("\n\n2️⃣ TESTANDO COM remove_chapter_headers=False")
    print("-" * 40)
    
    result_without_removal = service.generate_storyteller_script(
        title="Debug Final",
        premise="Uma história para debug final",
        agent_type="millionaire_stories",
        num_chapters=2,
        remove_chapter_headers=False  # PARÂMETRO CRÍTICO
    )
    
    script_without_removal = result_without_removal.get('full_script', '')
    
    print(f"📝 ROTEIRO SEM REMOÇÃO:")
    print(f"Tamanho: {len(script_without_removal)} caracteres")
    
    # Contar cabeçalhos markdown
    markdown_headers = len(re.findall(r'^##\s*.*?[Cc]apítulo', script_without_removal, re.MULTILINE | re.IGNORECASE))
    internal_headers = len(re.findall(r'CAPÍTULO\s*\d+', script_without_removal, re.IGNORECASE))
    
    print(f"Cabeçalhos markdown (## Capítulo): {markdown_headers}")
    print(f"Cabeçalhos internos (CAPÍTULO X:): {internal_headers}")
    print(f"Total de cabeçalhos: {markdown_headers + internal_headers}")
    
    print(f"\nPrimeiros 500 caracteres:")
    print(f"'{script_without_removal[:500]}'")
    
    # ANÁLISE COMPARATIVA
    print("\n\n🔍 ANÁLISE COMPARATIVA DETALHADA")
    print("=" * 50)
    
    with_removal_total = len(re.findall(r'^##\s*.*?[Cc]apítulo', script_with_removal, re.MULTILINE | re.IGNORECASE)) + len(re.findall(r'CAPÍTULO\s*\d+', script_with_removal, re.IGNORECASE))
    without_removal_total = len(re.findall(r'^##\s*.*?[Cc]apítulo', script_without_removal, re.MULTILINE | re.IGNORECASE)) + len(re.findall(r'CAPÍTULO\s*\d+', script_without_removal, re.IGNORECASE))
    
    print(f"COM remoção: {with_removal_total} cabeçalhos")
    print(f"SEM remoção: {without_removal_total} cabeçalhos")
    
    if with_removal_total < without_removal_total:
        print("✅ SUCESSO: A remoção de cabeçalhos está funcionando!")
        print(f"   Redução de {without_removal_total - with_removal_total} cabeçalhos")
    elif with_removal_total == without_removal_total:
        print("⚠️ NEUTRO: Mesmo número de cabeçalhos em ambos os casos")
    else:
        print("❌ PROBLEMA: COM remoção tem MAIS cabeçalhos que SEM remoção")
        print("   Isso indica um problema na lógica")
    
    # Salvar para análise
    with open('debug_script_with_removal.txt', 'w', encoding='utf-8') as f:
        f.write("ROTEIRO COM REMOÇÃO DE CABEÇALHOS (remove_chapter_headers=True)\n")
        f.write("=" * 60 + "\n\n")
        f.write(script_with_removal)
    
    with open('debug_script_without_removal.txt', 'w', encoding='utf-8') as f:
        f.write("ROTEIRO SEM REMOÇÃO DE CABEÇALHOS (remove_chapter_headers=False)\n")
        f.write("=" * 60 + "\n\n")
        f.write(script_without_removal)
    
    print("\n💾 Roteiros salvos em:")
    print("   - debug_script_with_removal.txt")
    print("   - debug_script_without_removal.txt")
    
    print("\n🎯 CONCLUSÃO:")
    if with_removal_total == 0:
        print("   ✅ PERFEITO: Remoção completa de cabeçalhos funcionando!")
    elif with_removal_total < without_removal_total:
        print("   ✅ BOM: Remoção parcial funcionando, mas pode ser melhorada")
    else:
        print("   ❌ PROBLEMA: Lógica de remoção não está funcionando corretamente")

if __name__ == "__main__":
    debug_final_script()