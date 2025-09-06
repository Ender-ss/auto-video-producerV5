#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug do retorno do StorytellerService
Verifica o que exatamente o método retorna
"""

import sys
sys.path.insert(0, '.')

from services.storyteller_service import StorytellerService
import json

def debug_storyteller_return():
    """Debug do retorno do StorytellerService"""
    
    print("🔍 DEBUG: RETORNO DO STORYTELLER")
    print("=" * 40)
    
    storyteller = StorytellerService()
    
    print("🔄 Executando generate_storyteller_script...")
    
    try:
        result = storyteller.generate_storyteller_script(
            title="Teste Debug",
            premise="Uma história simples para debug.",
            agent_type="millionaire_stories",
            num_chapters=2,
            remove_chapter_headers=False
        )
        
        print(f"\n✅ RESULTADO OBTIDO:")
        print(f"   Tipo: {type(result)}")
        
        if result is None:
            print("   ❌ Resultado é None")
        elif isinstance(result, dict):
            print(f"   📋 Chaves disponíveis: {list(result.keys())}")
            
            for key, value in result.items():
                if isinstance(value, str):
                    print(f"   📝 {key}: {len(value)} chars - '{value[:100]}...'")
                else:
                    print(f"   📊 {key}: {type(value)} - {value}")
        else:
            print(f"   📄 Conteúdo: {str(result)[:200]}...")
        
        # Salvar resultado completo para análise
        with open('debug_storyteller_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Resultado completo salvo em: debug_storyteller_result.json")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_storyteller_return()