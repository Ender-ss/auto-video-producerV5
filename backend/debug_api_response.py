#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug da resposta da API para verificar o que está sendo retornado
"""

import requests
import json

def debug_api_response():
    """Debug da resposta da API"""
    
    api_url = "http://localhost:5000/api/storyteller/generate-script"
    
    test_data = {
        "title": "Debug Test",
        "premise": "Uma história simples para debug.",
        "agent_type": "millionaire_stories",
        "num_chapters": 2,
        "remove_chapter_headers": True
    }
    
    print("=== DEBUG DA RESPOSTA DA API ===")
    
    try:
        response = requests.post(api_url, json=test_data, timeout=120)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n=== ESTRUTURA DA RESPOSTA ===")
            print(f"Chaves disponíveis: {list(result.keys())}")
            
            for key, value in result.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"{key}: {type(value).__name__} (tamanho: {len(value)})")
                    print(f"  Primeiros 200 chars: {repr(value[:200])}")
                else:
                    print(f"{key}: {repr(value)}")
            
            # Verificar se há campo 'script' ou similar
            script_fields = [k for k in result.keys() if 'script' in k.lower() or 'content' in k.lower() or 'story' in k.lower()]
            print(f"\nCampos relacionados a script/conteúdo: {script_fields}")
            
        else:
            print(f"Erro HTTP: {response.text}")
            
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    debug_api_response()