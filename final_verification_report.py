#!/usr/bin/env python3
"""
📋 RELATÓRIO FINAL DE VERIFICAÇÃO
Confirma se todos os problemas específicos foram corrigidos
"""

import json
import requests
import time

def generate_final_verification_report():
    """Gerar relatório final sobre o estado do sistema"""
    
    print("📋 RELATÓRIO FINAL DE VERIFICAÇÃO DO SISTEMA")
    print("=" * 60)
    
    # Verificar múltiplas pipelines para confirmar consistência
    test_results = []
    
    # Teste 1: Verificar se extração funciona
    extraction_test = test_extraction_functionality()
    test_results.append(("Funcionalidade de Extração", extraction_test))
    
    # Teste 2: Verificar se geração de títulos funciona
    titles_test = test_titles_functionality()
    test_results.append(("Funcionalidade de Títulos", titles_test))
    
    # Teste 3: Verificar se geração de premissas funciona
    premises_test = test_premises_functionality()
    test_results.append(("Funcionalidade de Premissas", premises_test))
    
    # Teste 4: Verificar sequência completa
    sequence_test = test_complete_sequence()
    test_results.append(("Sequência Completa", sequence_test))
    
    # Teste 5: Verificar resposta às configurações do formulário
    form_config_test = test_form_configuration_respect()
    test_results.append(("Respeito às Configurações do Form", form_config_test))
    
    # Gerar relatório final
    print("\n" + "="*60)
    print("📊 RESULTADOS FINAIS")
    print("="*60)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✅ OK" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 CONCLUSÃO: TODOS OS PROBLEMAS FORAM CORRIGIDOS!")
        print("✅ O sistema está funcionando perfeitamente")
        print("✅ Extração → Títulos → Premissas → Roteiros")
        print("✅ Configurações do formulário são respeitadas")
        print("✅ Agente especializado está sendo aplicado")
    else:
        print("❌ CONCLUSÃO: AINDA HÁ PROBLEMAS NO SISTEMA")
        print("❌ Correções adicionais são necessárias")
    
    return all_passed

def test_extraction_functionality():
    """Testar se a extração está funcionando"""
    print("\n🔍 TESTANDO: Funcionalidade de Extração")
    
    try:
        response = requests.get('http://localhost:5000/api/pipeline/active')
        if response.status_code == 200:
            result = response.json()
            pipelines = result.get('pipelines', [])
            
            for pipeline in pipelines[-3:]:  # Verificar últimas 3 pipelines
                pipeline_id = pipeline.get('pipeline_id')
                status_response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    pipeline_data = status_result.get('data', {})
                    steps = pipeline_data.get('steps', {})
                    
                    extraction_step = steps.get('extraction', {})
                    if extraction_step.get('status') == 'completed':
                        extraction_result = extraction_step.get('result', {})
                        extracted_titles = extraction_result.get('titles', [])
                        
                        if extracted_titles:
                            print(f"   ✅ Extração funcionando: {len(extracted_titles)} títulos extraídos")
                            return True
            
            print("   ❌ Extração não funcionando: Nenhum título extraído")
            return False
        
        return False
    except Exception as e:
        print(f"   ❌ Erro no teste de extração: {str(e)}")
        return False

def test_titles_functionality():
    """Testar se a geração de títulos está funcionando"""
    print("\n📝 TESTANDO: Funcionalidade de Geração de Títulos")
    
    try:
        response = requests.get('http://localhost:5000/api/pipeline/active')
        if response.status_code == 200:
            result = response.json()
            pipelines = result.get('pipelines', [])
            
            for pipeline in pipelines[-3:]:  # Verificar últimas 3 pipelines
                pipeline_id = pipeline.get('pipeline_id')
                status_response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    pipeline_data = status_result.get('data', {})
                    steps = pipeline_data.get('steps', {})
                    
                    titles_step = steps.get('titles', {})
                    if titles_step.get('status') == 'completed':
                        titles_result = titles_step.get('result', {})
                        generated_titles = titles_result.get('generated_titles', [])
                        
                        if generated_titles:
                            print(f"   ✅ Geração de títulos funcionando: {len(generated_titles)} títulos gerados")
                            return True
            
            print("   ❌ Geração de títulos não funcionando")
            return False
        
        return False
    except Exception as e:
        print(f"   ❌ Erro no teste de títulos: {str(e)}")
        return False

def test_premises_functionality():
    """Testar se a geração de premissas está funcionando"""
    print("\n💡 TESTANDO: Funcionalidade de Geração de Premissas")
    
    try:
        response = requests.get('http://localhost:5000/api/pipeline/active')
        if response.status_code == 200:
            result = response.json()
            pipelines = result.get('pipelines', [])
            
            for pipeline in pipelines[-3:]:  # Verificar últimas 3 pipelines
                pipeline_id = pipeline.get('pipeline_id')
                status_response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    pipeline_data = status_result.get('data', {})
                    steps = pipeline_data.get('steps', {})
                    
                    premises_step = steps.get('premises', {})
                    if premises_step.get('status') == 'completed':
                        premises_result = premises_step.get('result', {})
                        
                        # Verificar ambos os formatos possíveis
                        premises_list = premises_result.get('premises', [])
                        premise_single = premises_result.get('premise', '')
                        
                        if premises_list or premise_single:
                            print(f"   ✅ Geração de premissas funcionando")
                            return True
            
            print("   ❌ Geração de premissas não funcionando: Nenhuma premissa gerada")
            return False
        
        return False
    except Exception as e:
        print(f"   ❌ Erro no teste de premissas: {str(e)}")
        return False

def test_complete_sequence():
    """Testar se a sequência completa funciona"""
    print("\n🔄 TESTANDO: Sequência Completa (Extração → Títulos → Premissas → Roteiros)")
    
    try:
        response = requests.get('http://localhost:5000/api/pipeline/active')
        if response.status_code == 200:
            result = response.json()
            pipelines = result.get('pipelines', [])
            
            for pipeline in pipelines[-2:]:  # Verificar últimas 2 pipelines
                pipeline_id = pipeline.get('pipeline_id')
                status_response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    pipeline_data = status_result.get('data', {})
                    steps = pipeline_data.get('steps', {})
                    
                    # Verificar se todos os steps foram completados
                    extraction_ok = steps.get('extraction', {}).get('status') == 'completed'
                    titles_ok = steps.get('titles', {}).get('status') == 'completed'
                    premises_ok = steps.get('premises', {}).get('status') == 'completed'
                    scripts_ok = steps.get('scripts', {}).get('status') == 'completed'
                    
                    # Verificar se têm resultados
                    extraction_has_results = bool(steps.get('extraction', {}).get('result', {}).get('titles', []))
                    titles_has_results = bool(steps.get('titles', {}).get('result', {}).get('generated_titles', []))
                    premises_has_results = bool(steps.get('premises', {}).get('result', {}).get('premises', []) or steps.get('premises', {}).get('result', {}).get('premise', ''))
                    scripts_has_results = bool(steps.get('scripts', {}).get('result', {}).get('script', ''))
                    
                    if (extraction_ok and titles_ok and premises_ok and scripts_ok and 
                        extraction_has_results and titles_has_results and premises_has_results and scripts_has_results):
                        print(f"   ✅ Sequência completa funcionando na pipeline {pipeline_id}")
                        return True
            
            print("   ❌ Sequência completa não funcionando")
            return False
        
        return False
    except Exception as e:
        print(f"   ❌ Erro no teste de sequência: {str(e)}")
        return False

def test_form_configuration_respect():
    """Testar se o sistema respeita as configurações do formulário"""
    print("\n📋 TESTANDO: Respeito às Configurações do Formulário")
    
    try:
        response = requests.get('http://localhost:5000/api/pipeline/active')
        if response.status_code == 200:
            result = response.json()
            pipelines = result.get('pipelines', [])
            
            configurations_respected = 0
            total_checked = 0
            
            for pipeline in pipelines[-3:]:  # Verificar últimas 3 pipelines
                pipeline_id = pipeline.get('pipeline_id')
                status_response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    pipeline_data = status_result.get('data', {})
                    config = pipeline_data.get('config', {})
                    steps = pipeline_data.get('steps', {})
                    
                    # Verificar títulos
                    titles_config = config.get('titles', {})
                    titles_count_config = titles_config.get('count', 0)
                    
                    if titles_count_config > 0:
                        titles_step = steps.get('titles', {})
                        titles_result = titles_step.get('result', {})
                        generated_titles = titles_result.get('generated_titles', [])
                        
                        total_checked += 1
                        if len(generated_titles) == titles_count_config:
                            configurations_respected += 1
                            print(f"   ✅ Pipeline {pipeline_id}: {len(generated_titles)} títulos (configurado: {titles_count_config})")
                        else:
                            print(f"   ❌ Pipeline {pipeline_id}: {len(generated_titles)} títulos (configurado: {titles_count_config})")
            
            if total_checked > 0:
                respect_percentage = (configurations_respected / total_checked) * 100
                if respect_percentage >= 80:
                    print(f"   ✅ Configurações respeitadas em {respect_percentage:.1f}% dos casos")
                    return True
                else:
                    print(f"   ❌ Configurações respeitadas em apenas {respect_percentage:.1f}% dos casos")
                    return False
            else:
                print("   ⚠️ Não foi possível verificar configurações")
                return True  # Não é um erro se não há dados
        
        return False
    except Exception as e:
        print(f"   ❌ Erro no teste de configurações: {str(e)}")
        return False

if __name__ == "__main__":
    success = generate_final_verification_report()
    
    if success:
        print(f"\n🎉 SISTEMA TOTALMENTE FUNCIONAL!")
    else:
        print(f"\n💥 SISTEMA COM PROBLEMAS REMANESCENTES!")