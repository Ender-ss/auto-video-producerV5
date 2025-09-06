import requests
import json
import os

def execute_pipeline_test():
    """Executa teste da pipeline com configurações específicas"""
    
    # Carrega configuração do arquivo JSON
    config_path = os.path.join(os.path.dirname(__file__), 'test_storyteller_config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("Configuração carregada:")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        print("\n" + "="*50)
        
        # Executa requisição para gerar roteiro com Storyteller
        url = 'http://localhost:5000/api/storyteller/generate-script'
        print(f"Enviando requisição para: {url}")
        
        response = requests.post(url, json=config, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Roteiro gerado com sucesso!")
            print(f"\nRESULTADO COMPLETO:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Verificar se o roteiro contém cabeçalhos de capítulos
            script_content = result.get('data', {}).get('script', '')
            if script_content:
                print(f"\n{'='*60}")
                print("ANÁLISE DO ROTEIRO GERADO:")
                print(f"{'='*60}")
                print(f"Tamanho do roteiro: {len(script_content)} caracteres")
                
                # Verificar presença de cabeçalhos
                chapter_headers = ['## Capítulo', '## CAPÍTULO', 'Capítulo 1', 'Capítulo 2', 'Capítulo 3']
                headers_found = []
                for header in chapter_headers:
                    if header in script_content:
                        headers_found.append(header)
                
                if headers_found:
                    print(f"❌ PROBLEMA: Cabeçalhos encontrados no roteiro: {headers_found}")
                    print("   O parâmetro remove_chapter_headers=True NÃO está funcionando!")
                else:
                    print("✅ SUCESSO: Nenhum cabeçalho de capítulo encontrado no roteiro")
                    print("   O parâmetro remove_chapter_headers=True está funcionando corretamente!")
                
                # Mostrar primeiros 500 caracteres do roteiro
                print(f"\nPRIMEIROS 500 CARACTERES DO ROTEIRO:")
                print("-" * 50)
                print(script_content[:500] + "..." if len(script_content) > 500 else script_content)
                print("-" * 50)
            
            return result
        else:
            print(f"Erro {response.status_code}: {response.text}")
            return None
            
    except FileNotFoundError:
        print(f"Arquivo de configuração não encontrado: {config_path}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

if __name__ == "__main__":
    result = execute_pipeline_test()
    if result:
        print("\nTeste executado com sucesso!")
    else:
        print("\nFalha na execução do teste.")