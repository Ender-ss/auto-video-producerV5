#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da API para verificar se a remoção de cabeçalhos de capítulos funciona via HTTP
"""

import requests
import json
import os
from datetime import datetime

def test_api_chapter_removal():
    """Testa a remoção de cabeçalhos via API HTTP"""
    
    # URL da API (assumindo que está rodando localmente)
    api_url = "http://localhost:5000/api/storyteller/generate-script"
    
    # Dados de teste
    test_data = {
        "title": "Teste API - Remoção de Cabeçalhos",
        "premise": "Uma história sobre um jovem empreendedor que descobre o segredo do sucesso através de uma experiência transformadora.",
        "agent_type": "millionaire_stories",
        "num_chapters": 3,
        "remove_chapter_headers": True  # PARÂMETRO CRÍTICO
    }
    
    print("=== TESTE DA API - REMOÇÃO DE CABEÇALHOS ===")
    print(f"URL: {api_url}")
    print(f"Dados: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    print("\n" + "="*50)
    
    try:
        # Fazer requisição POST
        print("Enviando requisição...")
        response = requests.post(api_url, json=test_data, timeout=300)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                script_content = result.get('script', '')
                
                # Criar pasta para resultados
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = f"teste_api_remocao_{timestamp}"
                os.makedirs(output_dir, exist_ok=True)
                
                # Salvar roteiro
                script_file = os.path.join(output_dir, f"roteiro_api_teste_{timestamp}.txt")
                with open(script_file, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                
                # Analisar cabeçalhos
                chapter_headers = script_content.count('## Capítulo')
                internal_chapters = script_content.count('CAPÍTULO')
                
                # Gerar relatório
                report = f"""=== RELATÓRIO DO TESTE DA API ===
Timestamp: {timestamp}
URL Testada: {api_url}
Parâmetro remove_chapter_headers: {test_data['remove_chapter_headers']}

=== ANÁLISE DE CABEÇALHOS ===
Cabeçalhos '## Capítulo': {chapter_headers}
Marcações 'CAPÍTULO': {internal_chapters}

=== RESULTADO ===
{'✅ SUCESSO: Nenhum cabeçalho encontrado!' if chapter_headers == 0 and internal_chapters == 0 else '❌ FALHA: Cabeçalhos ainda presentes!'}

=== ARQUIVOS GERADOS ===
- Roteiro: {script_file}
- Relatório: {os.path.join(output_dir, f'relatorio_api_teste_{timestamp}.txt')}

=== DETALHES DA RESPOSTA ===
Sucesso: {result.get('success')}
Mensagem: {result.get('message', 'N/A')}
Tamanho do script: {len(script_content)} caracteres
"""
                
                report_file = os.path.join(output_dir, f"relatorio_api_teste_{timestamp}.txt")
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                print("\n" + "="*50)
                print(report)
                print("="*50)
                
                return chapter_headers == 0 and internal_chapters == 0
                
            else:
                print(f"❌ Erro na API: {result.get('error', 'Erro desconhecido')}")
                print(f"Mensagem: {result.get('message', 'N/A')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar à API.")
        print("Certifique-se de que o servidor está rodando em http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_api_chapter_removal()
    exit(0 if success else 1)