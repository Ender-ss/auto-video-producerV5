#!/usr/bin/env python3
"""
🔍 Análise Detalhada da Pipeline
Busca logs e detalhes da execução
"""

import json
import requests
import time

def analyze_pipeline_details():
    """Analisar detalhes da pipeline em execução"""
    
    print("🔍 ANÁLISE DETALHADA DA PIPELINE")
    print("=" * 50)
    
    try:
        pipeline_id = "61469e86-ad58-45ab-9302-73d830944ffc"
        
        # 1. Buscar status detalhado
        print(f"📊 Buscando detalhes da pipeline: {pipeline_id}")
        response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
        
        if response.status_code != 200:
            print(f"❌ ERRO: Falha ao buscar status: {response.status_code}")
            return False
            
        result = response.json()
        
        if not result.get('success') or not result.get('data'):
            print("❌ ERRO: Dados da pipeline não encontrados")
            return False
            
        pipeline_data = result['data']
        
        # 2. Mostrar informações básicas
        print(f"\n📋 INFORMAÇÕES BÁSICAS")
        print("-" * 30)
        print(f"🆔 ID: {pipeline_data.get('pipeline_id', 'N/A')}")
        print(f"🔄 Status: {pipeline_data.get('status', 'N/A')}")
        print(f"⏰ Criado em: {pipeline_data.get('created_at', 'N/A')}")
        print(f"⏰ Atualizado em: {pipeline_data.get('updated_at', 'N/A')}")
        
        # 3. Analisar configuração completa
        config = pipeline_data.get('config', {})
        print(f"\n🔧 CONFIGURAÇÃO COMPLETA")
        print("-" * 30)
        print(json.dumps(config, indent=2, ensure_ascii=False))
        
        # 4. Analisar steps em detalhes
        steps = pipeline_data.get('steps', {})
        print(f"\n⚙️ DETALHES DOS STEPS")
        print("-" * 30)
        
        for step_name, step_data in steps.items():
            print(f"\n📋 STEP: {step_name.upper()}")
            print(f"   Status: {step_data.get('status', 'N/A')}")
            print(f"   Iniciado em: {step_data.get('started_at', 'N/A')}")
            print(f"   Completado em: {step_data.get('completed_at', 'N/A')}")
            
            # Mostrar resultados se existirem
            results = step_data.get('results', {})
            if results:
                print(f"   Resultados:")
                for key, value in results.items():
                    if isinstance(value, list):
                        print(f"     {key}: {len(value)} items")
                        if value:
                            # Mostrar primeiro item como exemplo
                            first_item = value[0]
                            if isinstance(first_item, dict):
                                print(f"       Exemplo: {list(first_item.keys())}")
                            else:
                                print(f"       Exemplo: {str(first_item)[:100]}...")
                    else:
                        print(f"     {key}: {value}")
            else:
                print(f"   Nenhum resultado disponível")
            
            # Mostrar erros se existirem
            error = step_data.get('error', None)
            if error:
                print(f"   ❌ Erro: {error}")
        
        # 5. Buscar logs da pipeline
        print(f"\n📝 LOGS DA PIPELINE")
        print("-" * 30)
        
        try:
            logs_response = requests.get(f'http://localhost:5000/api/pipeline/logs/{pipeline_id}')
            if logs_response.status_code == 200:
                logs_result = logs_response.json()
                if logs_result.get('success') and logs_result.get('logs'):
                    logs = logs_result['logs']
                    print(f"📊 Total de logs: {len(logs)}")
                    
                    # Mostrar últimos logs
                    print("\n📋 ÚLTIMOS LOGS:")
                    for log in logs[-10:]:  # Últimos 10 logs
                        timestamp = log.get('timestamp', 'N/A')
                        level = log.get('level', 'INFO')
                        message = log.get('message', 'N/A')
                        step = log.get('step', 'N/A')
                        print(f"   [{timestamp}] [{level}] [{step}] {message}")
                else:
                    print("⚠️ Nenhum log encontrado")
            else:
                print(f"⚠️ Não foi possível buscar logs: {logs_response.status_code}")
        except:
            print("⚠️ Erro ao buscar logs")
        
        # 6. Análise específica do problema
        print(f"\n🔍 ANÁLISE DO PROBLEMA")
        print("-" * 30)
        
        # Verificar se todos os steps estão em processing
        all_processing = True
        completed_steps = []
        processing_steps = []
        
        for step_name, step_data in steps.items():
            status = step_data.get('status', 'unknown')
            if status == 'completed':
                completed_steps.append(step_name)
                all_processing = False
            elif status == 'processing':
                processing_steps.append(step_name)
            elif status in ['failed', 'error']:
                print(f"❌ Step {step_name} falhou: {step_data.get('error', 'Erro desconhecido')}")
                all_processing = False
        
        print(f"📊 Steps completados: {len(completed_steps)}")
        print(f"📊 Steps em processamento: {len(processing_steps)}")
        
        if completed_steps:
            print(f"✅ Completados: {', '.join(completed_steps)}")
        
        if processing_steps:
            print(f"⏳ Em processamento: {', '.join(processing_steps)}")
        
        if all_processing and len(processing_steps) > 0:
            print("\n⚠️ POSSÍVEL PROBLEMA:")
            print("Todos os steps estão em 'processing' há muito tempo.")
            print("Isso pode indicar que o processo travou ou há um deadlock.")
            print("\nSugestões:")
            print("1. Verificar se o backend está funcionando corretamente")
            print("2. Verificar logs do servidor para erros")
            print("3. Considerar reiniciar a pipeline se necessário")
        
        # 7. Verificar configuração vs execução
        print(f"\n🔧 VALIDAÇÃO: CONFIGURAÇÃO vs EXECUÇÃO")
        print("-" * 30)
        
        extraction_config = config.get('extraction', {})
        titles_config = config.get('titles', {})
        premises_config = config.get('premises', {})
        scripts_config = config.get('scripts', {})
        
        if extraction_config.get('enabled') and 'extraction' not in steps:
            print("❌ Extraction habilitada mas step não criado")
        
        if titles_config.get('enabled') and 'titles' not in steps:
            print("❌ Títulos habilitados mas step não criado")
        
        if premises_config.get('enabled') and 'premises' not in steps:
            print("❌ Premissas habilitadas mas step não criado")
        
        if scripts_config.get('enabled') and 'scripts' not in steps:
            print("❌ Roteiros habilitados mas step não criado")
        
        # Verificar quantidade configurada vs gerada
        titles_count_config = titles_config.get('count', 0)
        if titles_count_config and 'titles' in steps:
            titles_results = steps['titles'].get('results', {})
            generated_titles = titles_results.get('generated_titles', [])
            if generated_titles and len(generated_titles) != titles_count_config:
                print(f"⚠️ Configuração: {titles_count_config} títulos, Gerado: {len(generated_titles)} títulos")
        
        print(f"\n✅ ANÁLISE COMPLETA")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao backend.")
        return False
    except Exception as e:
        print(f"❌ ERRO: Exceção durante a análise: {str(e)}")
        return False

if __name__ == "__main__":
    analyze_pipeline_details()