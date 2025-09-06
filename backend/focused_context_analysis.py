#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Focada do Impacto da Remoção de Cabeçalhos no Contexto
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.storyteller_service import storyteller_service
import re
import time

def analyze_story_continuity(script):
    """Analisa a continuidade narrativa do script"""
    lines = [line.strip() for line in script.split('\n') if line.strip()]
    
    analysis = {
        'total_content_lines': len(lines),
        'chapter_markers': 0,
        'narrative_transitions': 0,
        'context_references': 0,
        'dialogue_consistency': 0,
        'story_flow_score': 0
    }
    
    # Contar marcadores de capítulo
    for line in lines:
        if re.search(r'^##\s*(capítulo|chapter)', line, re.IGNORECASE):
            analysis['chapter_markers'] += 1
    
    # Detectar transições narrativas
    transition_words = ['então', 'depois', 'em seguida', 'posteriormente', 'mais tarde', 'enquanto isso']
    for line in lines:
        for word in transition_words:
            if word.lower() in line.lower():
                analysis['narrative_transitions'] += 1
                break
    
    # Detectar referências de contexto
    context_words = ['anteriormente', 'como visto', 'lembrando', 'conforme', 'já mencionado']
    for line in lines:
        for word in context_words:
            if word.lower() in line.lower():
                analysis['context_references'] += 1
                break
    
    # Calcular score de fluxo narrativo
    if analysis['total_content_lines'] > 0:
        flow_ratio = (analysis['narrative_transitions'] + analysis['context_references']) / analysis['total_content_lines']
        analysis['story_flow_score'] = min(100, flow_ratio * 100)
    
    return analysis

def test_context_impact():
    """Testa o impacto específico no contexto da história"""
    print("🔍 ANÁLISE DE IMPACTO NO CONTEXTO DA HISTÓRIA")
    print("=" * 60)
    
    test_story = {
        'title': 'O Programador e o Bug Interdimensional',
        'premise': 'Um desenvolvedor descobre que um bug em seu código está abrindo portais para outras dimensões. Cada capítulo deve manter continuidade com os eventos anteriores.',
        'agent_type': 'millionaire_stories',
        'num_chapters': 3
    }
    
    results = {}
    
    for remove_headers in [False, True]:
        status = "sem_cabecalhos" if remove_headers else "com_cabecalhos"
        print(f"\n--- Testando {status.replace('_', ' ').upper()} ---")
        
        try:
            start_time = time.time()
            result = storyteller_service.generate_storyteller_script(
                **test_story,
                remove_chapter_headers=remove_headers
            )
            end_time = time.time()
            
            if result.get('success'):
                script = result.get('full_script', '')
                chapters = result.get('chapters', [])
                
                # Análise de continuidade
                continuity = analyze_story_continuity(script)
                
                results[status] = {
                    'success': True,
                    'generation_time': end_time - start_time,
                    'script_length': len(script),
                    'chapters_count': len(chapters),
                    'continuity_analysis': continuity,
                    'script_preview': script[:500] + '...' if len(script) > 500 else script
                }
                
                print(f"  ✅ Geração bem-sucedida em {results[status]['generation_time']:.1f}s")
                print(f"  📊 Script: {results[status]['script_length']} caracteres")
                print(f"  📚 Capítulos: {results[status]['chapters_count']}")
                print(f"  🔗 Marcadores de capítulo: {continuity['chapter_markers']}")
                print(f"  🌊 Transições narrativas: {continuity['narrative_transitions']}")
                print(f"  📖 Referências de contexto: {continuity['context_references']}")
                print(f"  📈 Score de fluxo: {continuity['story_flow_score']:.1f}")
                
            else:
                results[status] = {
                    'success': False,
                    'error': result.get('error', 'Erro desconhecido')
                }
                print(f"  ❌ Erro: {results[status]['error']}")
                
        except Exception as e:
            results[status] = {
                'success': False,
                'error': str(e)
            }
            print(f"  ❌ Exceção: {e}")
    
    return results

def compare_context_preservation(results):
    """Compara a preservação de contexto entre as duas versões"""
    print("\n" + "=" * 60)
    print("COMPARAÇÃO DE PRESERVAÇÃO DE CONTEXTO")
    print("=" * 60)
    
    if not all(results[key].get('success') for key in results):
        print("❌ Não foi possível comparar - algum teste falhou")
        return False
    
    com = results['com_cabecalhos']['continuity_analysis']
    sem = results['sem_cabecalhos']['continuity_analysis']
    
    print(f"\n📊 MÉTRICAS DE CONTINUIDADE:")
    print(f"  Linhas de conteúdo:")
    print(f"    COM cabeçalhos: {com['total_content_lines']}")
    print(f"    SEM cabeçalhos: {sem['total_content_lines']}")
    print(f"    Diferença: {sem['total_content_lines'] - com['total_content_lines']}")
    
    print(f"\n  Marcadores de capítulo:")
    print(f"    COM cabeçalhos: {com['chapter_markers']}")
    print(f"    SEM cabeçalhos: {sem['chapter_markers']}")
    print(f"    Diferença: {sem['chapter_markers'] - com['chapter_markers']}")
    
    print(f"\n  Transições narrativas:")
    print(f"    COM cabeçalhos: {com['narrative_transitions']}")
    print(f"    SEM cabeçalhos: {sem['narrative_transitions']}")
    print(f"    Diferença: {sem['narrative_transitions'] - com['narrative_transitions']}")
    
    print(f"\n  Referências de contexto:")
    print(f"    COM cabeçalhos: {com['context_references']}")
    print(f"    SEM cabeçalhos: {sem['context_references']}")
    print(f"    Diferença: {sem['context_references'] - com['context_references']}")
    
    print(f"\n  Score de fluxo narrativo:")
    print(f"    COM cabeçalhos: {com['story_flow_score']:.1f}")
    print(f"    SEM cabeçalhos: {sem['story_flow_score']:.1f}")
    print(f"    Diferença: {sem['story_flow_score'] - com['story_flow_score']:.1f}")
    
    # Análise de impacto
    print(f"\n🎯 ANÁLISE DE IMPACTO:")
    
    # Verificar se cabeçalhos foram realmente removidos
    headers_removed = com['chapter_markers'] > sem['chapter_markers']
    if headers_removed:
        print(f"  ✅ Cabeçalhos foram removidos corretamente ({com['chapter_markers']} → {sem['chapter_markers']})")
    else:
        print(f"  ⚠️  Cabeçalhos não foram removidos adequadamente")
    
    # Verificar preservação de contexto
    context_preserved = abs(sem['context_references'] - com['context_references']) <= 1
    if context_preserved:
        print(f"  ✅ Contexto preservado (referências mantidas)")
    else:
        print(f"  ⚠️  Possível perda de contexto")
    
    # Verificar fluxo narrativo
    flow_maintained = abs(sem['story_flow_score'] - com['story_flow_score']) <= 5
    if flow_maintained:
        print(f"  ✅ Fluxo narrativo mantido")
    else:
        print(f"  ⚠️  Fluxo narrativo pode ter sido afetado")
    
    # Conclusão
    print(f"\n" + "=" * 40)
    print("CONCLUSÃO:")
    
    if headers_removed and context_preserved and flow_maintained:
        print("✅ APROVADO: A remoção de cabeçalhos funciona corretamente")
        print("   - Cabeçalhos removidos sem afetar o contexto")
        print("   - Continuidade narrativa preservada")
        print("   - Fluxo da história mantido")
        return True
    else:
        issues = []
        if not headers_removed:
            issues.append("Cabeçalhos não removidos")
        if not context_preserved:
            issues.append("Contexto afetado")
        if not flow_maintained:
            issues.append("Fluxo narrativo comprometido")
        
        print(f"⚠️  ATENÇÃO: Problemas detectados")
        for issue in issues:
            print(f"   - {issue}")
        return False

def show_script_samples(results):
    """Mostra amostras dos scripts para comparação visual"""
    print(f"\n" + "=" * 60)
    print("AMOSTRAS DOS SCRIPTS GERADOS")
    print("=" * 60)
    
    for status, data in results.items():
        if data.get('success'):
            print(f"\n--- {status.replace('_', ' ').upper()} ---")
            preview = data.get('script_preview', 'Não disponível')
            print(preview)
            print(f"\n[... restante do script: {data['script_length'] - len(preview)} caracteres]")

def main():
    """Executa análise focada"""
    print("🎯 ANÁLISE FOCADA: IMPACTO DA REMOÇÃO DE CABEÇALHOS NO CONTEXTO")
    print("=" * 80)
    
    try:
        # Executar testes
        results = test_context_impact()
        
        # Comparar resultados
        context_ok = compare_context_preservation(results)
        
        # Mostrar amostras
        show_script_samples(results)
        
        return context_ok
        
    except Exception as e:
        print(f"\n❌ ERRO NA ANÁLISE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'='*40}")
    if success:
        print("🎉 ANÁLISE CONCLUÍDA: Sistema aprovado")
    else:
        print("⚠️  ANÁLISE CONCLUÍDA: Requer atenção")
    
    exit(0 if success else 1)