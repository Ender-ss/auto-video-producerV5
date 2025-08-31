#!/usr/bin/env python3
"""
🔍 Verificação Completa e Detalhada do Sistema
Testa múltiplas pipelines para confirmar se todos os problemas foram corrigidos
"""

import json
import requests
import time
from datetime import datetime

def test_comprehensive_pipeline_verification():
    """Verificação completa de múltiplas pipelines"""
    
    print("🔍 VERIFICAÇÃO COMPLETA DO SISTEMA")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%H:%M:%S')}")
    
    # Teste 1: Pipeline com agente especializado
    print("\n" + "="*50)
    print("📋 TESTE 1: PIPELINE COM AGENTE ESPECIALIZADO")
    print("="*50)
    
    test1_success = test_agent_specialized_pipeline()
    
    # Teste 2: Pipeline sem agente (padrão)
    print("\n" + "="*50)
    print("📋 TESTE 2: PIPELINE PADRÃO (SEM AGENTE)")
    print("="*50)
    
    test2_success = test_standard_pipeline()
    
    # Teste 3: Verificar pipeline anterior que estava com problemas
    print("\n" + "="*50)
    print("📋 TESTE 3: VERIFICAR PIPELINE ANTERIOR")
    print("="*50)
    
    test3_success = verify_previous_pipeline()
    
    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL DA VERIFICAÇÃO")
    print("="*60)
    
    results = [
        ("Pipeline com Agente Especializado", test1_success),
        ("Pipeline Padrão", test2_success),
        ("Pipeline Anterior", test3_success)
    ]
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\n🎯 RESULTADO GERAL:")
    if all_passed:
        print("✅ TODOS OS PROBLEMAS FORAM CORRIGIDOS COM SUCESSO!")
        print("✅ Sistema funcionando perfeitamente em todos os cenários")
        return True
    else:
        print("❌ AINDA HÁ PROBLEMAS NO SISTEMA")
        print("❌ Correções adicionais são necessárias")
        return False

def test_agent_specialized_pipeline():
    """Testar pipeline com agente especializado"""
    
    print("🤖 Testando pipeline com agente 'Histórias de Milionários'")
    
    config = {
        "channel_url": "https://www.youtube.com/@MrBeast",
        "agent": {
            "type": "specialized",
            "specialized_type": "millionaire_stories"
        },
        "config": {
            "extraction": {
                "enabled": True,
                "method": "yt-dlp", 
                "max_titles": 3
            },
            "titles": {
                "enabled": True,
                "provider": "gemini",
                "count": 3,
                "style": "viral"
            },
            "premises": {
                "enabled": True,
                "provider": "gemini",
                "word_count": 150
            },
            "scripts": {
                "enabled": True,
                "chapters": 3,
                "provider": "gemini"
            },
            "tts": {"enabled": False},
            "images": {"enabled": False},
            "video": {"enabled": False}
        }
    }
    
    return execute_pipeline_test("AGENTE ESPECIALIZADO", config)

def test_standard_pipeline():
    """Testar pipeline padrão sem agente"""
    
    print("⚙️ Testando pipeline padrão sem agente")
    
    config = {
        "channel_url": "https://www.youtube.com/@MrBeast",
        "config": {
            "extraction": {
                "enabled": True,
                "method": "yt-dlp",
                "max_titles": 2
            },
            "titles": {
                "enabled": True,
                "provider": "gemini",
                "count": 2,
                "style": "viral"
            },
            "premises": {
                "enabled": True,
                "provider": "gemini",
                "word_count": 100
            },
            "scripts": {
                "enabled": True,
                "chapters": 2,
                "provider": "gemini"
            },
            "tts": {"enabled": False},
            "images": {"enabled": False},
            "video": {"enabled": False}
        }
    }
    
    return execute_pipeline_test("PADRÃO", config)

def execute_pipeline_test(test_name, config):
    """Executar teste de pipeline e verificar resultados"""
    
    try:
        print(f"📤 Criando pipeline {test_name}...")
        response = requests.post('http://localhost:5000/api/pipeline/complete', json=config)
        
        if response.status_code != 200:
            print(f"❌ Erro ao criar pipeline: {response.status_code}")
            return False
        
        result = response.json()
        pipeline_id = result.get('pipeline_id')
        
        if not pipeline_id:
            print("❌ Pipeline criada mas sem ID")
            return False
        
        print(f"✅ Pipeline criada: {pipeline_id}")
        
        # Aguardar conclusão
        for i in range(15):  # 75 segundos máximo
            time.sleep(5)
            status_response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                pipeline_data = status_result.get('data', {})
                current_status = pipeline_data.get('status', 'unknown')
                
                print(f"⏳ Status {i+1}/15: {current_status}")
                
                if current_status == 'completed':
                    print(f"✅ Pipeline {test_name} concluída!")
                    return analyze_pipeline_results(pipeline_id, test_name, config)
                elif current_status == 'failed':
                    print(f"❌ Pipeline {test_name} falhou!")
                    return False
            else:
                print(f"❌ Erro ao verificar status: {status_response.status_code}")
        
        print(f"⏰ Timeout na pipeline {test_name}")
        return False
        
    except Exception as e:
        print(f"❌ Exceção no teste {test_name}: {str(e)}")
        return False

def analyze_pipeline_results(pipeline_id, test_name, original_config):
    """Analisar resultados detalhados da pipeline"""
    
    try:
        print(f"\n📊 ANÁLISE DETALHADA - {test_name}")
        print("-" * 40)
        
        response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
        if response.status_code != 200:
            print("❌ Erro ao buscar resultados")
            return False
        
        result = response.json()
        pipeline_data = result['data']
        
        # Verificar configuração vs execução
        config = pipeline_data.get('config', {})
        steps = pipeline_data.get('steps', {})
        results = pipeline_data.get('results', {})
        
        success = True
        
        # 1. Verificar EXTRACTION
        print("📥 VERIFICANDO EXTRAÇÃO:")
        extraction_step = steps.get('extraction', {})
        extraction_status = extraction_step.get('status', 'N/A')
        extraction_result = extraction_step.get('result', {})
        
        extraction_config = original_config['config']['extraction']
        max_titles_config = extraction_config.get('max_titles', 0)
        
        print(f"   Status: {extraction_status}")
        
        if extraction_status != 'completed':
            print(f"   ❌ PROBLEMA: Status não é 'completed'")
            success = False
        elif not extraction_result:
            print(f"   ❌ PROBLEMA: Nenhum resultado de extração")
            success = False
        else:
            extracted_titles = extraction_result.get('titles', [])
            print(f"   Configurado: {max_titles_config} títulos")
            print(f"   Extraído: {len(extracted_titles)} títulos")
            
            if len(extracted_titles) == 0:
                print(f"   ❌ PROBLEMA: Nenhum título foi extraído")
                success = False
            elif len(extracted_titles) != max_titles_config:
                print(f"   ⚠️ AVISO: Quantidade diferente da configurada")
            else:
                print(f"   ✅ EXTRAÇÃO OK: {len(extracted_titles)} títulos extraídos")
            
            if extracted_titles:
                print(f"   Exemplos extraídos:")
                for i, title in enumerate(extracted_titles[:2]):
                    title_text = title.get('title', title) if isinstance(title, dict) else title
                    print(f"      {i+1}. {title_text[:60]}...")
        
        # 2. Verificar TITLES
        print("\n📝 VERIFICANDO GERAÇÃO DE TÍTULOS:")
        titles_step = steps.get('titles', {})
        titles_status = titles_step.get('status', 'N/A')
        titles_result = titles_step.get('result', {})
        
        titles_config = original_config['config']['titles']
        count_config = titles_config.get('count', 0)
        
        print(f"   Status: {titles_status}")
        
        if titles_status != 'completed':
            print(f"   ❌ PROBLEMA: Status não é 'completed'")
            success = False
        elif not titles_result:
            print(f"   ❌ PROBLEMA: Nenhum resultado de geração de títulos")
            success = False
        else:
            generated_titles = titles_result.get('generated_titles', [])
            print(f"   Configurado: {count_config} títulos")
            print(f"   Gerado: {len(generated_titles)} títulos")
            
            if len(generated_titles) == 0:
                print(f"   ❌ PROBLEMA: Nenhum título foi gerado")
                success = False
            elif len(generated_titles) != count_config:
                print(f"   ❌ PROBLEMA: Quantidade não corresponde à configuração")
                success = False
            else:
                print(f"   ✅ TÍTULOS OK: {len(generated_titles)} títulos gerados")
            
            if generated_titles:
                print(f"   Títulos gerados:")
                for i, title in enumerate(generated_titles[:2]):
                    print(f"      {i+1}. {title}")
        
        # 3. Verificar PREMISES
        print("\n💡 VERIFICANDO GERAÇÃO DE PREMISSAS:")
        premises_step = steps.get('premises', {})
        premises_status = premises_step.get('status', 'N/A')
        premises_result = premises_step.get('result', {})
        
        print(f"   Status: {premises_status}")
        
        if premises_status != 'completed':
            print(f"   ❌ PROBLEMA: Status não é 'completed'")
            success = False
        elif not premises_result:
            print(f"   ❌ PROBLEMA: Nenhum resultado de geração de premissas")
            success = False
        else:
            # Verificar ambos os formatos possíveis
            premises_list = premises_result.get('premises', [])
            premise_single = premises_result.get('premise', '')
            
            if premises_list:
                print(f"   ✅ PREMISSAS OK: {len(premises_list)} premissa(s) gerada(s)")
                premise_text = premises_list[0].get('premise', '') if isinstance(premises_list[0], dict) else premises_list[0]
                print(f"   Exemplo: {str(premise_text)[:100]}...")
            elif premise_single:
                print(f"   ✅ PREMISSA OK: Premissa gerada ({len(premise_single)} chars)")
                print(f"   Exemplo: {premise_single[:100]}...")
            else:
                print(f"   ❌ PROBLEMA: Nenhuma premissa foi gerada")
                success = False
        
        # 4. Verificar SCRIPTS
        print("\n📜 VERIFICANDO GERAÇÃO DE ROTEIROS:")
        scripts_step = steps.get('scripts', {})
        scripts_status = scripts_step.get('status', 'N/A')
        scripts_result = scripts_step.get('result', {})
        
        print(f"   Status: {scripts_status}")
        
        if scripts_status != 'completed':
            print(f"   ❌ PROBLEMA: Status não é 'completed'")
            success = False
        elif not scripts_result:
            print(f"   ❌ PROBLEMA: Nenhum resultado de geração de roteiros")
            success = False
        else:
            script_content = scripts_result.get('script', '')
            scripts_list = scripts_result.get('scripts', [])
            
            if script_content:
                print(f"   ✅ ROTEIRO OK: {len(script_content)} caracteres gerados")
                print(f"   Início: {script_content[:150]}...")
            elif scripts_list:
                print(f"   ✅ ROTEIROS OK: {len(scripts_list)} roteiro(s) gerado(s)")
            else:
                print(f"   ❌ PROBLEMA: Nenhum roteiro foi gerado")
                success = False
        
        # 5. Verificar AGENTE (se aplicável)
        agent_config = config.get('agent', {})
        if agent_config:
            print(f"\n🤖 VERIFICANDO AGENTE ESPECIALIZADO:")
            agent_enabled = agent_config.get('enabled', False)
            agent_type = agent_config.get('type', 'N/A')
            agent_name = agent_config.get('name', 'N/A')
            
            print(f"   Habilitado: {agent_enabled}")
            print(f"   Tipo: {agent_type}")
            print(f"   Nome: {agent_name}")
            
            if agent_enabled:
                print(f"   ✅ AGENTE OK: Configurado e ativo")
            else:
                print(f"   ⚠️ AGENTE: Não está ativo")
        
        # Resultado final do teste
        print(f"\n🎯 RESULTADO DO TESTE {test_name}:")
        if success:
            print(f"✅ TODOS OS COMPONENTES FUNCIONARAM CORRETAMENTE")
        else:
            print(f"❌ HÁ PROBLEMAS QUE PRECISAM SER CORRIGIDOS")
        
        return success
        
    except Exception as e:
        print(f"❌ Erro na análise: {str(e)}")
        return False

def verify_previous_pipeline():
    """Verificar se pipelines anteriores que estavam com problemas agora funcionam"""
    
    print("🔍 Verificando pipelines anteriores...")
    
    try:
        response = requests.get('http://localhost:5000/api/pipeline/active')
        
        if response.status_code != 200:
            print("❌ Erro ao buscar pipelines ativas")
            return False
        
        result = response.json()
        pipelines = result.get('pipelines', [])
        
        if not pipelines:
            print("⚠️ Nenhuma pipeline anterior encontrada")
            return True  # Não é um erro
        
        # Verificar a pipeline mais recente
        latest_pipeline = pipelines[0]
        pipeline_id = latest_pipeline.get('pipeline_id')
        
        print(f"🔍 Verificando pipeline anterior: {pipeline_id}")
        
        status_response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
        
        if status_response.status_code != 200:
            print("❌ Erro ao buscar status da pipeline anterior")
            return False
        
        status_result = status_response.json()
        pipeline_data = status_result['data']
        
        status = pipeline_data.get('status', 'unknown')
        steps = pipeline_data.get('steps', {})
        
        print(f"   Status geral: {status}")
        
        # Verificar se tem resultados
        has_results = False
        for step_name in ['extraction', 'titles', 'premises', 'scripts']:
            step_data = steps.get(step_name, {})
            step_result = step_data.get('result', {})
            if step_result:
                has_results = True
                break
        
        if has_results:
            print("✅ Pipeline anterior agora tem resultados")
            return True
        else:
            print("❌ Pipeline anterior ainda sem resultados")
            return False
    
    except Exception as e:
        print(f"❌ Erro na verificação: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_comprehensive_pipeline_verification()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 VERIFICAÇÃO COMPLETA: TODOS OS PROBLEMAS CORRIGIDOS!")
        print("✅ Sistema totalmente funcional")
    else:
        print("💥 VERIFICAÇÃO COMPLETA: AINDA HÁ PROBLEMAS!")
        print("❌ Correções adicionais necessárias")
    print(f"{'='*60}")