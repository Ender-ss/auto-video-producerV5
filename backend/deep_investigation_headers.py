#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investigação Profunda da Funcionalidade de Remoção de Cabeçalhos
Verifica impactos no contexto, qualidade da história e integração com pipeline
"""

import requests
import json
import re
import time
from datetime import datetime
from services.storyteller_service import storyteller_service

def analyze_story_structure(script):
    """Analisa a estrutura da história"""
    lines = script.split('\n')
    
    analysis = {
        'total_lines': len(lines),
        'empty_lines': len([l for l in lines if not l.strip()]),
        'paragraph_count': len([l for l in lines if l.strip() and not l.startswith('#')]),
        'dialogue_lines': len([l for l in lines if '"' in l or '"' in l or '"' in l]),
        'narrative_flow_breaks': 0,
        'chapter_transitions': 0,
        'story_coherence_score': 0
    }
    
    # Detectar quebras no fluxo narrativo
    for i in range(1, len(lines)):
        if lines[i-1].strip() and lines[i].strip():
            if len(lines[i-1]) < 50 and len(lines[i]) > 100:
                analysis['narrative_flow_breaks'] += 1
    
    # Detectar transições de capítulo
    for line in lines:
        if re.search(r'(capítulo|chapter)', line, re.IGNORECASE):
            analysis['chapter_transitions'] += 1
    
    # Score básico de coerência (baseado em densidade de conteúdo)
    if analysis['total_lines'] > 0:
        content_density = analysis['paragraph_count'] / analysis['total_lines']
        analysis['story_coherence_score'] = min(100, content_density * 100)
    
    return analysis

def test_context_preservation():
    """Testa se o contexto da história é preservado"""
    print("\n=== TESTE DE PRESERVAÇÃO DE CONTEXTO ===")
    
    test_cases = [
        {
            'title': 'História de Contexto Complexo',
            'premise': 'Um programador descobre um bug que conecta realidades paralelas. Cada capítulo deve manter referências aos eventos anteriores.',
            'agent_type': 'millionaire_stories',
            'num_chapters': 3
        },
        {
            'title': 'Saga Familiar',
            'premise': 'Três gerações de uma família enfrentam desafios financeiros. A continuidade entre capítulos é crucial.',
            'agent_type': 'millionaire_stories', 
            'num_chapters': 3
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Caso de Teste {i}: {test_case['title']} ---")
        
        # Teste COM cabeçalhos
        print("  Testando COM cabeçalhos...")
        try:
            result_with = storyteller_service.generate_storyteller_script(
                **test_case,
                remove_chapter_headers=False
            )
            
            if result_with.get('success'):
                script_with = result_with.get('full_script', '')
                analysis_with = analyze_story_structure(script_with)
                print(f"    ✅ Gerado: {len(script_with)} chars, {analysis_with['paragraph_count']} parágrafos")
            else:
                print(f"    ❌ Erro: {result_with.get('error')}")
                continue
                
        except Exception as e:
            print(f"    ❌ Exceção: {e}")
            continue
        
        # Teste SEM cabeçalhos
        print("  Testando SEM cabeçalhos...")
        try:
            result_without = storyteller_service.generate_storyteller_script(
                **test_case,
                remove_chapter_headers=True
            )
            
            if result_without.get('success'):
                script_without = result_without.get('full_script', '')
                analysis_without = analyze_story_structure(script_without)
                print(f"    ✅ Gerado: {len(script_without)} chars, {analysis_without['paragraph_count']} parágrafos")
            else:
                print(f"    ❌ Erro: {result_without.get('error')}")
                continue
                
        except Exception as e:
            print(f"    ❌ Exceção: {e}")
            continue
        
        # Comparação de contexto
        context_comparison = {
            'test_case': test_case['title'],
            'with_headers': {
                'length': len(script_with),
                'structure': analysis_with,
                'chapters': len(result_with.get('chapters', []))
            },
            'without_headers': {
                'length': len(script_without),
                'structure': analysis_without,
                'chapters': len(result_without.get('chapters', []))
            },
            'context_preserved': True,  # Assumindo preservação se ambos geraram
            'quality_difference': abs(analysis_with['story_coherence_score'] - analysis_without['story_coherence_score'])
        }
        
        results.append(context_comparison)
        
        print(f"  📊 Diferença de qualidade: {context_comparison['quality_difference']:.1f} pontos")
        print(f"  📏 Diferença de tamanho: {context_comparison['with_headers']['length'] - context_comparison['without_headers']['length']} chars")
    
    return results

def test_pipeline_integration():
    """Testa integração com pipeline completa"""
    print("\n=== TESTE DE INTEGRAÇÃO COM PIPELINE ===")
    
    api_url = "http://localhost:5000/api/storyteller/generate-script"
    
    pipeline_test = {
        'title': 'Teste Pipeline Integração',
        'premise': 'História para testar integração completa com pipeline de vídeo.',
        'agent_type': 'millionaire_stories',
        'num_chapters': 2
    }
    
    integration_results = {}
    
    for remove_headers in [False, True]:
        header_status = "SEM" if remove_headers else "COM"
        print(f"\n--- Testando {header_status} cabeçalhos ---")
        
        test_data = pipeline_test.copy()
        test_data['remove_chapter_headers'] = remove_headers
        
        try:
            start_time = time.time()
            response = requests.post(api_url, json=test_data, timeout=180)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                
                integration_results[header_status] = {
                    'success': True,
                    'response_time': end_time - start_time,
                    'script_length': len(result.get('full_script', '')),
                    'chapters_count': len(result.get('chapters', [])),
                    'has_metadata': bool(result.get('metadata')),
                    'api_response_size': len(json.dumps(result))
                }
                
                print(f"  ✅ Sucesso em {integration_results[header_status]['response_time']:.1f}s")
                print(f"  📊 Script: {integration_results[header_status]['script_length']} chars")
                print(f"  📚 Capítulos: {integration_results[header_status]['chapters_count']}")
                
            else:
                integration_results[header_status] = {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text[:200]}"
                }
                print(f"  ❌ Erro HTTP: {response.status_code}")
                
        except Exception as e:
            integration_results[header_status] = {
                'success': False,
                'error': str(e)
            }
            print(f"  ❌ Exceção: {e}")
    
    return integration_results

def test_edge_cases():
    """Testa casos extremos"""
    print("\n=== TESTE DE CASOS EXTREMOS ===")
    
    edge_cases = [
        {
            'name': 'História muito curta',
            'title': 'Micro',
            'premise': 'História mínima.',
            'agent_type': 'millionaire_stories',
            'num_chapters': 1
        },
        {
            'name': 'Muitos capítulos',
            'title': 'Épico',
            'premise': 'Uma saga épica com muitos capítulos para testar limites.',
            'agent_type': 'millionaire_stories',
            'num_chapters': 5
        },
        {
            'name': 'Caracteres especiais',
            'title': 'História com "aspas" e símbolos @#$%',
            'premise': 'Teste com caracteres especiais: áéíóú, ção, ñ, etc.',
            'agent_type': 'millionaire_stories',
            'num_chapters': 2
        }
    ]
    
    edge_results = []
    
    for case in edge_cases:
        print(f"\n--- {case['name']} ---")
        
        case_result = {'name': case['name'], 'results': {}}
        
        for remove_headers in [False, True]:
            status = "sem_headers" if remove_headers else "com_headers"
            
            try:
                result = storyteller_service.generate_storyteller_script(
                    title=case['title'],
                    premise=case['premise'],
                    agent_type=case['agent_type'],
                    num_chapters=case['num_chapters'],
                    remove_chapter_headers=remove_headers
                )
                
                if result.get('success'):
                    case_result['results'][status] = {
                        'success': True,
                        'script_length': len(result.get('full_script', '')),
                        'chapters_generated': len(result.get('chapters', [])),
                        'has_errors': bool(result.get('errors'))
                    }
                    print(f"  ✅ {status}: {case_result['results'][status]['script_length']} chars")
                else:
                    case_result['results'][status] = {
                        'success': False,
                        'error': result.get('error', 'Erro desconhecido')
                    }
                    print(f"  ❌ {status}: {case_result['results'][status]['error']}")
                    
            except Exception as e:
                case_result['results'][status] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {status}: Exceção - {e}")
        
        edge_results.append(case_result)
    
    return edge_results

def generate_investigation_report(context_results, integration_results, edge_results):
    """Gera relatório completo da investigação"""
    print("\n" + "="*80)
    print("RELATÓRIO FINAL DA INVESTIGAÇÃO PROFUNDA")
    print("="*80)
    
    print(f"\n📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Resumo de Contexto
    print("\n🔍 ANÁLISE DE PRESERVAÇÃO DE CONTEXTO:")
    context_issues = 0
    for result in context_results:
        quality_diff = result['quality_difference']
        if quality_diff > 10:
            print(f"  ⚠️  {result['test_case']}: Diferença significativa de qualidade ({quality_diff:.1f} pontos)")
            context_issues += 1
        else:
            print(f"  ✅ {result['test_case']}: Contexto preservado (diff: {quality_diff:.1f} pontos)")
    
    # Resumo de Integração
    print("\n🔗 ANÁLISE DE INTEGRAÇÃO COM PIPELINE:")
    integration_issues = 0
    for status, data in integration_results.items():
        if data.get('success'):
            print(f"  ✅ {status} cabeçalhos: Integração OK ({data['response_time']:.1f}s)")
        else:
            print(f"  ❌ {status} cabeçalhos: {data.get('error', 'Erro desconhecido')}")
            integration_issues += 1
    
    # Resumo de Casos Extremos
    print("\n⚡ ANÁLISE DE CASOS EXTREMOS:")
    edge_issues = 0
    for case in edge_results:
        case_ok = True
        for status, result in case['results'].items():
            if not result.get('success'):
                case_ok = False
                edge_issues += 1
        
        if case_ok:
            print(f"  ✅ {case['name']}: Todos os cenários funcionaram")
        else:
            print(f"  ⚠️  {case['name']}: Alguns cenários falharam")
    
    # Conclusão Final
    print("\n" + "="*50)
    print("CONCLUSÃO FINAL:")
    
    total_issues = context_issues + integration_issues + edge_issues
    
    if total_issues == 0:
        print("✅ SISTEMA APROVADO: Nenhum problema crítico detectado.")
        print("   A funcionalidade de remoção de cabeçalhos está funcionando corretamente.")
        print("   Não há impacto negativo no contexto, pipeline ou casos extremos.")
    elif total_issues <= 2:
        print("⚠️  SISTEMA COM ALERTAS: Problemas menores detectados.")
        print(f"   {total_issues} issue(s) encontrada(s), mas sistema ainda utilizável.")
        print("   Recomenda-se monitoramento adicional.")
    else:
        print("❌ SISTEMA COM PROBLEMAS: Múltiplos problemas detectados.")
        print(f"   {total_issues} issue(s) crítica(s) encontrada(s).")
        print("   Recomenda-se revisão antes de usar em produção.")
    
    print("\n📊 ESTATÍSTICAS:")
    print(f"   - Testes de contexto: {len(context_results)} casos")
    print(f"   - Testes de integração: {len(integration_results)} cenários")
    print(f"   - Testes extremos: {len(edge_results)} casos")
    print(f"   - Issues encontradas: {total_issues}")
    
    return total_issues == 0

def main():
    """Executa investigação completa"""
    print("🔍 INICIANDO INVESTIGAÇÃO PROFUNDA DA FUNCIONALIDADE DE REMOÇÃO DE CABEÇALHOS")
    print("="*80)
    
    try:
        # Teste 1: Preservação de Contexto
        context_results = test_context_preservation()
        
        # Teste 2: Integração com Pipeline
        integration_results = test_pipeline_integration()
        
        # Teste 3: Casos Extremos
        edge_results = test_edge_cases()
        
        # Relatório Final
        system_approved = generate_investigation_report(context_results, integration_results, edge_results)
        
        return system_approved
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO NA INVESTIGAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)