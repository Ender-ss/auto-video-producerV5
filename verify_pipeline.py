#!/usr/bin/env python3
"""
🔍 Verificação da Última Pipeline
Analisa se a pipeline mais recente funcionou corretamente
"""

import json
import requests
import time
from datetime import datetime

def verify_latest_pipeline():
    """Verificar a última pipeline executada"""
    
    print("🔍 VERIFICAÇÃO DA ÚLTIMA PIPELINE")
    print("=" * 50)
    
    try:
        # 1. Buscar pipelines ativas/recentes
        print("📋 Buscando pipelines recentes...")
        response = requests.get('http://localhost:5000/api/pipeline/active')
        
        if response.status_code != 200:
            print(f"❌ ERRO: Falha ao buscar pipelines: {response.status_code}")
            return False
            
        result = response.json()
        
        if not result.get('success') or not result.get('pipelines'):
            print("⚠️ Nenhuma pipeline ativa encontrada")
            print("🔍 Tentando buscar a última pipeline executada...")
            
            # Tentar buscar através de logs ou histórico
            # Por enquanto, vamos verificar se há alguma pipeline no sistema
            return False
            
        pipelines = result['pipelines']
        print(f"📊 Encontradas {len(pipelines)} pipelines")
        
        # Pegar a pipeline mais recente
        latest_pipeline = None
        if pipelines:
            # Se há múltiplas, pegar a primeira (assumindo que está ordenada)
            pipeline_id = pipelines[0].get('pipeline_id')
            if pipeline_id:
                print(f"🎯 Analisando pipeline: {pipeline_id}")
                
                # Buscar detalhes completos da pipeline
                status_response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    if status_result.get('success') and status_result.get('data'):
                        latest_pipeline = status_result['data']
                    else:
                        print("❌ ERRO: Não foi possível obter dados da pipeline")
                        return False
                else:
                    print(f"❌ ERRO: Falha ao buscar status da pipeline: {status_response.status_code}")
                    return False
        
        if not latest_pipeline:
            print("❌ ERRO: Não foi possível encontrar uma pipeline para analisar")
            return False
            
        # 2. Analisar a configuração da pipeline
        print("\n📊 ANÁLISE DA CONFIGURAÇÃO")
        print("-" * 30)
        
        config = latest_pipeline.get('config', {})
        steps = latest_pipeline.get('steps', {})
        status = latest_pipeline.get('status', 'desconhecido')
        
        print(f"🔄 Status da Pipeline: {status}")
        print(f"🆔 Pipeline ID: {latest_pipeline.get('pipeline_id', 'N/A')}")
        
        # 3. Verificar configurações do formulário
        print("\n🔧 CONFIGURAÇÕES DO FORMULÁRIO")
        print("-" * 30)
        
        # Extraction
        extraction_config = config.get('extraction', {})
        extraction_enabled = extraction_config.get('enabled', False)
        max_titles_config = extraction_config.get('max_titles', 'não definido')
        
        print(f"📥 Extraction habilitada: {extraction_enabled}")
        print(f"📥 Máximo de títulos para extrair: {max_titles_config}")
        
        # Titles
        titles_config = config.get('titles', {})
        titles_enabled = titles_config.get('enabled', False)
        titles_count_config = titles_config.get('count', 'não definido')
        titles_provider = titles_config.get('provider', 'não definido')
        
        print(f"📝 Geração de títulos habilitada: {titles_enabled}")
        print(f"📝 Quantidade de títulos a gerar: {titles_count_config}")
        print(f"📝 Provider de títulos: {titles_provider}")
        
        # Premises
        premises_config = config.get('premises', {})
        premises_enabled = premises_config.get('enabled', False)
        premises_provider = premises_config.get('provider', 'não definido')
        premises_word_count = premises_config.get('word_count', 'não definido')
        
        print(f"💡 Geração de premissas habilitada: {premises_enabled}")
        print(f"💡 Provider de premissas: {premises_provider}")
        print(f"💡 Contagem de palavras das premissas: {premises_word_count}")
        
        # Scripts
        scripts_config = config.get('scripts', {})
        scripts_enabled = scripts_config.get('enabled', False)
        scripts_provider = scripts_config.get('provider', 'não definido')
        scripts_chapters = scripts_config.get('chapters', 'não definido')
        
        print(f"📜 Geração de roteiros habilitada: {scripts_enabled}")
        print(f"📜 Provider de roteiros: {scripts_provider}")
        print(f"📜 Número de capítulos: {scripts_chapters}")
        
        # 4. Verificar execução dos steps
        print("\n⚙️ EXECUÇÃO DOS STEPS")
        print("-" * 30)
        
        # Extraction step
        extraction_step = steps.get('extraction', {})
        extraction_status = extraction_step.get('status', 'não executado')
        extraction_results = extraction_step.get('results', {})
        
        print(f"📥 Step Extraction - Status: {extraction_status}")
        extracted_titles = []
        if extraction_results:
            extracted_titles = extraction_results.get('titles', [])
            print(f"📥 Títulos extraídos: {len(extracted_titles) if extracted_titles else 0}")
            if extracted_titles:
                print("📥 Primeiros títulos extraídos:")
                for i, title in enumerate(extracted_titles[:3]):
                    print(f"   {i+1}. {title.get('title', 'N/A') if isinstance(title, dict) else title}")
        else:
            print("📥 Nenhum resultado de extração encontrado")
        
        # Titles step
        titles_step = steps.get('titles', {})
        titles_status = titles_step.get('status', 'não executado')
        titles_results = titles_step.get('results', {})
        
        print(f"📝 Step Titles - Status: {titles_status}")
        generated_titles = []
        if titles_results:
            generated_titles = titles_results.get('generated_titles', [])
            print(f"📝 Títulos gerados: {len(generated_titles) if generated_titles else 0}")
            if generated_titles:
                print("📝 Títulos gerados:")
                for i, title in enumerate(generated_titles[:3]):
                    print(f"   {i+1}. {title}")
        else:
            print("📝 Nenhum resultado de geração de títulos encontrado")
        
        # Premises step
        premises_step = steps.get('premises', {})
        premises_status = premises_step.get('status', 'não executado')
        premises_results = premises_step.get('results', {})
        
        print(f"💡 Step Premises - Status: {premises_status}")
        generated_premises = []
        if premises_results:
            generated_premises = premises_results.get('premises', [])
            print(f"💡 Premissas geradas: {len(generated_premises) if generated_premises else 0}")
            if generated_premises:
                print("💡 Premissas geradas:")
                for i, premise in enumerate(generated_premises[:2]):
                    premise_text = premise.get('premise', premise) if isinstance(premise, dict) else premise
                    print(f"   {i+1}. {premise_text[:100]}..." if len(str(premise_text)) > 100 else f"   {i+1}. {premise_text}")
        else:
            print("💡 Nenhum resultado de geração de premissas encontrado")
        
        # Scripts step
        scripts_step = steps.get('scripts', {})
        scripts_status = scripts_step.get('status', 'não executado')
        scripts_results = scripts_step.get('results', {})
        
        print(f"📜 Step Scripts - Status: {scripts_status}")
        generated_scripts = []
        if scripts_results:
            generated_scripts = scripts_results.get('scripts', [])
            print(f"📜 Roteiros gerados: {len(generated_scripts) if generated_scripts else 0}")
            if generated_scripts:
                print("📜 Roteiro(s) gerados:")
                for i, script in enumerate(generated_scripts[:1]):
                    script_content = script.get('content', script) if isinstance(script, dict) else script
                    script_title = script.get('title', f'Roteiro {i+1}') if isinstance(script, dict) else f'Roteiro {i+1}'
                    print(f"   {script_title}: {str(script_content)[:150]}...")
        else:
            print("📜 Nenhum resultado de geração de roteiros encontrado")
        
        # 5. Análise de problemas
        print("\n🔍 ANÁLISE DE PROBLEMAS")
        print("-" * 30)
        
        problems = []
        
        # Verificar se extraction respeitou configuração
        if extraction_enabled and extraction_status != 'completed':
            problems.append(f"❌ Extraction configurada mas não completada (status: {extraction_status})")
        
        if extraction_enabled and extracted_titles and max_titles_config != 'não definido':
            if len(extracted_titles) != max_titles_config:
                problems.append(f"⚠️ Configuração pedia {max_titles_config} títulos, mas extraiu {len(extracted_titles)}")
        
        # Verificar se titles respeitou configuração
        if titles_enabled and titles_status != 'completed':
            problems.append(f"❌ Geração de títulos configurada mas não completada (status: {titles_status})")
            
        if titles_enabled and generated_titles and titles_count_config != 'não definido':
            if len(generated_titles) != titles_count_config:
                problems.append(f"⚠️ Configuração pedia {titles_count_config} títulos gerados, mas criou {len(generated_titles)}")
        
        # Verificar se premises funcionou
        if premises_enabled and premises_status != 'completed':
            problems.append(f"❌ Geração de premissas configurada mas não completada (status: {premises_status})")
        
        if premises_enabled and not generated_premises:
            problems.append("❌ Premissas habilitadas mas nenhuma foi gerada")
        
        # Verificar se scripts usou título e premissa
        if scripts_enabled and scripts_status != 'completed':
            problems.append(f"❌ Geração de roteiros configurada mas não completada (status: {scripts_status})")
        
        # Verificar dependências entre steps
        if scripts_enabled and generated_scripts and (not generated_titles or not generated_premises):
            problems.append("⚠️ Roteiro gerado mas sem títulos ou premissas como base")
        
        # 6. Relatório final
        print("\n📊 RELATÓRIO FINAL")
        print("=" * 50)
        
        if not problems:
            print("✅ SUCESSO: Pipeline executada corretamente!")
            print("✅ Todas as configurações foram respeitadas")
            print("✅ Sequência de execução funcionou adequadamente")
            
            if premises_enabled and generated_premises and scripts_enabled and generated_scripts:
                print("✅ Premissas foram geradas e utilizadas para criar roteiros")
            
            return True
        else:
            print("❌ PROBLEMAS ENCONTRADOS:")
            for problem in problems:
                print(f"   {problem}")
            
            # Verificar especificamente o problema das premissas
            if premises_enabled and (premises_status != 'completed' or not generated_premises):
                print("\n🚨 PROBLEMA ESPECÍFICO: PREMISSAS")
                print("A geração de premissas não funcionou corretamente.")
                print(f"Status das premissas: {premises_status}")
                print(f"Resultados das premissas: {bool(generated_premises)}")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao backend. Verifique se o servidor está rodando.")
        return False
    except Exception as e:
        print(f"❌ ERRO: Exceção durante a verificação: {str(e)}")
        return False

if __name__ == "__main__":
    success = verify_latest_pipeline()
    
    if success:
        print("\n🎉 VERIFICAÇÃO COMPLETA: Pipeline funcionando corretamente!")
    else:
        print("\n💥 VERIFICAÇÃO INDICA PROBLEMAS: Há questões na execução da pipeline!")