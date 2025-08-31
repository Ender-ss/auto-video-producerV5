#!/usr/bin/env python3
"""
🔍 Análise Final da Pipeline Atual
"""

import requests
import json

def analyze_current_pipeline():
    pipeline_id = '495e103f-c094-410f-9212-2d2fddceca9b'
    response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')

    if response.status_code == 200:
        result = response.json()
        pipeline_data = result['data']
        
        print('📊 ANÁLISE FINAL DOS RESULTADOS')
        print('=' * 50)
        
        # Status geral
        print(f'Status: {pipeline_data.get("status", "N/A")}')
        
        # Verificar steps e resultados
        steps = pipeline_data.get('steps', {})
        
        for step_name in ['extraction', 'titles', 'premises', 'scripts']:
            step_data = steps.get(step_name, {})
            step_status = step_data.get('status', 'N/A')
            step_results = step_data.get('results', {})
            
            print(f'\n📋 {step_name.upper()}:')
            print(f'   Status: {step_status}')
            
            if step_results:
                if step_name == 'extraction':
                    titles = step_results.get('titles', [])
                    print(f'   Títulos extraídos: {len(titles)}')
                    if titles:
                        for i, title in enumerate(titles[:2]):
                            title_text = title.get('title', title) if isinstance(title, dict) else title
                            print(f'      {i+1}. {title_text}')
                
                elif step_name == 'titles':
                    generated_titles = step_results.get('generated_titles', [])
                    print(f'   Títulos gerados: {len(generated_titles)}')
                    if generated_titles:
                        for i, title in enumerate(generated_titles[:2]):
                            print(f'      {i+1}. {title}')
                
                elif step_name == 'premises':
                    premises = step_results.get('premises', [])
                    print(f'   Premissas geradas: {len(premises)}')
                    if premises:
                        for i, premise in enumerate(premises[:1]):
                            premise_text = premise.get('premise', premise) if isinstance(premise, dict) else premise
                            print(f'      {i+1}. {str(premise_text)[:150]}...')
                
                elif step_name == 'scripts':
                    script = step_results.get('script', '')
                    scripts_list = step_results.get('scripts', [])
                    print(f'   Script principal: {"Sim" if script else "Não"} ({len(script)} chars)')
                    print(f'   Scripts lista: {len(scripts_list)} items')
                    if script:
                        print(f'   Início: {script[:200]}...')
            else:
                print('   ❌ Nenhum resultado')
        
        # Verificar agente
        config = pipeline_data.get('config', {})
        agent_config = config.get('agent', {})
        print(f'\n🤖 AGENTE:')
        print(f'   Habilitado: {agent_config.get("enabled", False)}')
        print(f'   Tipo: {agent_config.get("type", "N/A")}')
        print(f'   Nome: {agent_config.get("name", "N/A")}')
        
        # Conclusão
        print(f'\n🎯 ANÁLISE:')
        extraction_results = steps.get('extraction', {}).get('results', {})
        titles_results = steps.get('titles', {}).get('results', {})
        premises_results = steps.get('premises', {}).get('results', {})
        scripts_results = steps.get('scripts', {}).get('results', {})
        
        extraction_ok = extraction_results.get('titles', []) if extraction_results else []
        titles_ok = titles_results.get('generated_titles', []) if titles_results else []
        premises_ok = premises_results.get('premises', []) if premises_results else []
        scripts_ok = scripts_results.get('script', '') if scripts_results else ''
        
        if extraction_ok and titles_ok and premises_ok and scripts_ok:
            print('✅ SEQUÊNCIA COMPLETA: Extração → Títulos → Premissas → Roteiros')
            
            # Verificar se agente foi aplicado
            if agent_config.get('enabled'):
                print('✅ Agente especializado foi aplicado')
            
            # Verificar se elementos da premissa aparecem no roteiro
            if premises_ok and scripts_ok:
                premise_text = str(premises_ok[0]).lower()
                script_text = scripts_ok.lower()
                
                # Buscar palavras da premissa no roteiro
                premise_words = premise_text.split()[:15]
                common_words = ['a', 'o', 'de', 'da', 'do', 'que', 'para', 'com', 'em', 'um', 'uma', 'e', 'ou']
                significant_words = [word for word in premise_words if len(word) > 3 and word not in common_words]
                
                matches = sum(1 for word in significant_words[:8] if word in script_text)
                match_percentage = (matches / len(significant_words[:8])) * 100 if significant_words else 0
                
                print(f'🔗 Correspondência premissa→roteiro: {match_percentage:.1f}%')
                if match_percentage > 25:
                    print('✅ Roteiro usa elementos da premissa')
                else:
                    print('⚠️ Roteiro pode não estar usando adequadamente a premissa')
            
            return True
        else:
            print('❌ SEQUÊNCIA INCOMPLETA:')
            if not extraction_ok: print('   - Extração falhou ou não retornou títulos')
            if not titles_ok: print('   - Geração de títulos falhou')
            if not premises_ok: print('   - Geração de premissas falhou')
            if not scripts_ok: print('   - Geração de roteiros falhou')
            return False
    else:
        print('❌ Erro ao buscar status da pipeline')
        return False

if __name__ == "__main__":
    success = analyze_current_pipeline()
    if success:
        print('\n🎉 SISTEMA FUNCIONANDO CORRETAMENTE!')
    else:
        print('\n💥 SISTEMA COM PROBLEMAS!')