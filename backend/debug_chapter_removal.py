#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug detalhado da remoção de cabeçalhos de capítulos
"""

import re
from services.storyteller_service import storyteller_service

def debug_chapter_removal():
    """Debug detalhado da remoção de cabeçalhos"""
    
    print("=== DEBUG DETALHADO DA REMOÇÃO DE CABEÇALHOS ===\n")
    
    # Teste com remoção de cabeçalhos
    print("1. GERANDO ROTEIRO COM remove_chapter_headers=True")
    
    try:
        result = storyteller_service.generate_storyteller_script(
            title="Debug Detalhado",
            premise="Uma história para debug detalhado.",
            agent_type="millionaire_stories",
            num_chapters=2,
            remove_chapter_headers=True
        )
        
        if result.get('success'):
            print("   ✅ Geração bem-sucedida")
            
            # Analisar capítulos individuais
            chapters = result.get('chapters', [])
            print(f"   📊 Número de capítulos: {len(chapters)}")
            
            for i, chapter in enumerate(chapters, 1):
                content = chapter.get('content', '')
                print(f"\n   📄 CAPÍTULO {i}:")
                print(f"      Tamanho: {len(content)} caracteres")
                print(f"      Primeiros 200 chars: {repr(content[:200])}")
                
                # Verificar cabeçalhos no conteúdo individual
                headers_in_content = [
                    content.count('## Capítulo'),
                    content.count('# Capítulo'),
                    content.count('CAPÍTULO'),
                    content.count('Capítulo')
                ]
                print(f"      Cabeçalhos encontrados: {headers_in_content}")
            
            # Analisar script final
            full_script = result.get('full_script', '')
            print(f"\n   📜 SCRIPT FINAL:")
            print(f"      Tamanho: {len(full_script)} caracteres")
            print(f"      Primeiros 400 chars: {repr(full_script[:400])}")
            
            # Contar todos os tipos de cabeçalhos
            headers_count = {
                '## Capítulo': full_script.count('## Capítulo'),
                '# Capítulo': full_script.count('# Capítulo'),
                'CAPÍTULO': full_script.count('CAPÍTULO'),
                'Capítulo': full_script.count('Capítulo')
            }
            
            print(f"      Cabeçalhos por tipo: {headers_count}")
            print(f"      Total de cabeçalhos: {sum(headers_count.values())}")
            
            # Testar regex manualmente
            print("\n   🔍 TESTE MANUAL DAS REGEX:")
            test_content = "## Capítulo 1\n\nCAPÍTULO 1: Teste\n\nConteúdo do capítulo..."
            print(f"      Conteúdo de teste: {repr(test_content)}")
            
            # Aplicar as mesmas regex do código
            cleaned = re.sub(r'^##\s*Capítulo\s*\d+[:\s]*.*?\n', '', test_content, flags=re.MULTILINE | re.IGNORECASE)
            print(f"      Após regex 1: {repr(cleaned)}")
            
            cleaned = re.sub(r'^CAPÍTULO\s*\d+[:\s]*.*?\n', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
            print(f"      Após regex 2: {repr(cleaned)}")
            
        else:
            print(f"   ❌ Erro na geração: {result.get('error')}")
            
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_chapter_removal()