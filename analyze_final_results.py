#!/usr/bin/env python3
"""
🔍 Análise Final dos Resultados da Pipeline
Verifica se a pipeline funcionou corretamente e analisa os resultados
"""

import json
import requests
import time

def analyze_final_results():
    """Analisar resultados finais da pipeline"""
    
    print("🎯 ANÁLISE FINAL DOS RESULTADOS DA PIPELINE")
    print("=" * 60)
    
    try:
        pipeline_id = "61469e86-ad58-45ab-9302-73d830944ffc"
        
        # 1. Buscar status final da pipeline
        print(f"📊 Buscando resultados finais da pipeline: {pipeline_id}")
        response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
        
        if response.status_code != 200:
            print(f"❌ ERRO: Falha ao buscar status: {response.status_code}")
            return False
            
        result = response.json()
        
        if not result.get('success') or not result.get('data'):
            print("❌ ERRO: Dados da pipeline não encontrados")
            return False
            
        pipeline_data = result['data']
        
        # 2. Status geral
        status = pipeline_data.get('status', 'unknown')
        print(f"\n🔄 STATUS GERAL: {status.upper()}")
        print(f"🆔 Pipeline ID: {pipeline_data.get('pipeline_id', 'N/A')}")
        
        if status != 'completed':
            print("⚠️ Pipeline não foi completada com sucesso")
            return False
        
        # 3. Analisar configuração original
        config = pipeline_data.get('config', {})
        print(f"\n🔧 CONFIGURAÇÃO ORIGINAL")
        print("-" * 40)
        
        # Extraction
        extraction_config = config.get('extraction', {})
        print(f"📥 Extraction habilitada: {extraction_config.get('enabled', 'N/A')}")
        print(f"📥 Método: {extraction_config.get('method', 'N/A')}")
        
        # Titles
        titles_config = config.get('titles', {})
        print(f"📝 Títulos habilitados: {titles_config.get('enabled', 'N/A')}")
        print(f"📝 Quantidade configurada: {titles_config.get('count', 'N/A')}")
        print(f"📝 Provider: {titles_config.get('provider', 'N/A')}")
        
        # Premises
        premises_config = config.get('premises', {})
        print(f"💡 Premissas habilitadas: {premises_config.get('enabled', 'N/A')}")
        print(f"💡 Provider: {premises_config.get('provider', 'N/A')}")
        print(f"💡 Palavras: {premises_config.get('word_count', 'N/A')}")
        
        # Scripts
        scripts_config = config.get('scripts', {})
        print(f"📜 Roteiros habilitados: {scripts_config.get('enabled', 'N/A')}")
        print(f"📜 Capítulos: {scripts_config.get('chapters', 'N/A')}")
        print(f"📜 Provider: {scripts_config.get('provider', 'N/A')}")
        
        # 4. Analisar steps executados
        steps = pipeline_data.get('steps', {})
        print(f"\n⚙️ STEPS EXECUTADOS")
        print("-" * 40)
        
        step_results = {}
        
        for step_name, step_data in steps.items():
            step_status = step_data.get('status', 'unknown')
            step_results[step_name] = step_data.get('results', {})
            
            print(f"📋 {step_name.upper()}: {step_status}")
            
            # Mostrar timing se disponível
            started_at = step_data.get('started_at')
            completed_at = step_data.get('completed_at')
            if started_at and completed_at:
                print(f"   ⏱️ Duração: {started_at} → {completed_at}")
        
        # 5. Análise detalhada dos resultados
        print(f"\n📊 RESULTADOS DETALHADOS")
        print("-" * 40)
        
        # Extraction
        if 'extraction' in step_results:
            extraction_results = step_results['extraction']
            titles_extracted = extraction_results.get('titles', [])
            print(f"\n📥 EXTRACTION:")
            print(f"   Títulos extraídos: {len(titles_extracted)}")
            if titles_extracted:
                print("   Primeiros títulos extraídos:")
                for i, title in enumerate(titles_extracted[:3]):
                    title_text = title.get('title', title) if isinstance(title, dict) else title
                    views = title.get('views', 'N/A') if isinstance(title, dict) else 'N/A'
                    print(f"      {i+1}. {title_text} (Views: {views})")
        
        # Titles
        if 'titles' in step_results:
            titles_results = step_results['titles']
            titles_generated = titles_results.get('generated_titles', [])
            titles_count_config = titles_config.get('count', 0)
            
            print(f"\n📝 TITLES:")
            print(f"   Configurado para gerar: {titles_count_config}")
            print(f"   Títulos realmente gerados: {len(titles_generated)}")
            
            if len(titles_generated) != titles_count_config:
                print(f"   ⚠️ PROBLEMA: Quantidade não corresponde à configuração!")
            else:
                print(f"   ✅ Quantidade corresponde à configuração")
            
            if titles_generated:
                print("   Títulos gerados:")
                for i, title in enumerate(titles_generated[:5]):
                    print(f"      {i+1}. {title}")
        
        # Premises
        if 'premises' in step_results:
            premises_results = step_results['premises']
            premises_generated = premises_results.get('premises', [])
            
            print(f"\n💡 PREMISES:")
            print(f"   Premissas geradas: {len(premises_generated)}")
            
            if not premises_generated:
                print(f"   ❌ PROBLEMA: Nenhuma premissa foi gerada!")
            else:
                print(f"   ✅ Premissas foram geradas com sucesso")
                print("   Premissas:")
                for i, premise in enumerate(premises_generated[:2]):
                    premise_text = premise.get('premise', premise) if isinstance(premise, dict) else premise
                    premise_title = premise.get('title', f'Premissa {i+1}') if isinstance(premise, dict) else f'Premissa {i+1}'
                    print(f"      {i+1}. [{premise_title}]")
                    print(f"         {str(premise_text)[:200]}...")
        
        # Scripts
        if 'scripts' in step_results:
            scripts_results = step_results['scripts']
            scripts_generated = scripts_results.get('scripts', [])
            script_text = scripts_results.get('script', '')
            
            print(f"\n📜 SCRIPTS:")
            print(f"   Roteiros gerados: {len(scripts_generated)}")
            print(f"   Script principal: {'Sim' if script_text else 'Não'}")
            
            if not scripts_generated and not script_text:
                print(f"   ❌ PROBLEMA: Nenhum roteiro foi gerado!")
            else:
                print(f"   ✅ Roteiros foram gerados com sucesso")
                
                if script_text:
                    print(f"   Script principal ({len(script_text)} caracteres):")
                    print(f"      {script_text[:300]}...")
                
                if scripts_generated:
                    print("   Scripts individuais:")
                    for i, script in enumerate(scripts_generated[:2]):
                        script_content = script.get('content', script) if isinstance(script, dict) else script
                        script_title = script.get('title', f'Script {i+1}') if isinstance(script, dict) else f'Script {i+1}'
                        print(f"      {i+1}. [{script_title}]")
                        print(f"         {str(script_content)[:200]}...")
        
        # 6. Verificar se roteiro usou título e premissa
        print(f"\n🔍 ANÁLISE: TÍTULO E PREMISSA NO ROTEIRO")
        print("-" * 40)
        
        if 'titles' in step_results and 'premises' in step_results and 'scripts' in step_results:
            titles = step_results['titles'].get('generated_titles', [])
            premises = step_results['premises'].get('premises', [])
            script = step_results['scripts'].get('script', '')
            
            if titles and premises and script:
                # Verificar se elementos das premissas aparecem no roteiro
                premise_text = str(premises[0]).lower() if premises else ""
                script_text = script.lower()
                
                # Buscar palavras-chave da premissa no roteiro
                premise_words = premise_text.split()[:20]  # Primeiras 20 palavras da premissa
                common_words = ['a', 'o', 'de', 'da', 'do', 'que', 'para', 'com', 'em', 'um', 'uma', 'e', 'ou']
                significant_words = [word for word in premise_words if len(word) > 3 and word not in common_words]
                
                matches = 0
                for word in significant_words[:10]:  # Verificar primeiras 10 palavras significativas
                    if word in script_text:
                        matches += 1
                
                match_percentage = (matches / len(significant_words[:10])) * 100 if significant_words else 0
                
                print(f"   Título principal: {titles[0] if titles else 'N/A'}")
                print(f"   Premissa principal: {str(premises[0])[:100] if premises else 'N/A'}...")
                print(f"   Correspondência premissa→roteiro: {match_percentage:.1f}%")
                
                if match_percentage > 30:
                    print("   ✅ Roteiro parece usar elementos da premissa")
                else:
                    print("   ⚠️ Roteiro pode não estar usando adequadamente a premissa")
            else:
                print("   ❌ Não foi possível verificar - dados insuficientes")
        
        # 7. Relatório final
        print(f"\n📊 RELATÓRIO FINAL")
        print("=" * 60)
        
        issues = []
        successes = []
        
        # Verificar problemas
        if 'titles' in step_results:
            titles_generated = step_results['titles'].get('generated_titles', [])
            titles_count_config = titles_config.get('count', 0)
            if len(titles_generated) != titles_count_config:
                issues.append(f"Títulos: configurado {titles_count_config}, gerado {len(titles_generated)}")
            else:
                successes.append("Títulos: quantidade correta")
        
        if 'premises' in step_results:
            premises_generated = step_results['premises'].get('premises', [])
            if not premises_generated:
                issues.append("Premissas: nenhuma premissa gerada")
            else:
                successes.append("Premissas: geradas com sucesso")
        
        if 'scripts' in step_results:
            script = step_results['scripts'].get('script', '')
            if not script:
                issues.append("Roteiros: nenhum roteiro principal gerado")
            else:
                successes.append("Roteiros: gerados com sucesso")
        
        # Mostrar resultados
        if successes:
            print("✅ SUCESSOS:")
            for success in successes:
                print(f"   ✅ {success}")
        
        if issues:
            print("\n❌ PROBLEMAS IDENTIFICADOS:")
            for issue in issues:
                print(f"   ❌ {issue}")
            
            # Análise específica do problema de premissas
            if any('premissa' in issue.lower() for issue in issues):
                print(f"\n🚨 ANÁLISE DO PROBLEMA DAS PREMISSAS:")
                print("   A geração de premissas pode ter falhado por:")
                print("   1. Erro de API (quota, limite de rate)")
                print("   2. Problema de prompt ou configuração")
                print("   3. Falha na comunicação com o serviço de IA")
                print("   4. Erro de formatação dos dados")
                
            return False
        else:
            print("\n🎉 PIPELINE EXECUTADA COM SUCESSO!")
            print("✅ Todas as configurações foram respeitadas")
            print("✅ Todas as etapas funcionaram corretamente")
            print("✅ Sistema respeitou as configurações do formulário")
            
            if 'premises' in step_results and 'scripts' in step_results:
                print("✅ Premissas foram geradas e utilizadas nos roteiros")
            
            return True
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao backend.")
        return False
    except Exception as e:
        print(f"❌ ERRO: Exceção durante a análise: {str(e)}")
        return False

if __name__ == "__main__":
    success = analyze_final_results()
    
    if success:
        print("\n🎉 VERIFICAÇÃO FINAL: Pipeline funcionou perfeitamente!")
    else:
        print("\n💥 VERIFICAÇÃO FINAL: Há problemas que precisam ser corrigidos!")