#!/usr/bin/env python3
"""
🔍 Análise Detalhada da Última Pipeline
Verificar se o fluxo completo funcionou corretamente
"""

import requests
import json

def analyze_latest_pipeline():
    """Analisar se a última pipeline seguiu o fluxo correto"""
    
    print("🔍 ANÁLISE DA ÚLTIMA PIPELINE")
    print("=" * 50)
    
    try:
        # 1. Buscar a última pipeline
        response = requests.get('http://localhost:5000/api/pipeline/active?history=true')
        if response.status_code != 200:
            print(f"❌ Erro ao buscar pipelines: {response.status_code}")
            return
            
        data = response.json()
        pipelines = data.get('pipelines', [])
        
        if not pipelines:
            print("❌ Nenhuma pipeline encontrada")
            return
            
        latest = pipelines[0]  # Primeira é a mais recente
        pipeline_id = latest.get('pipeline_id')
        
        print(f"📋 PIPELINE ENCONTRADA:")
        print(f"   🆔 ID: {pipeline_id}")
        print(f"   📛 Display Name: {latest.get('display_name')}")
        print(f"   📝 Título: {latest.get('title')}")
        print(f"   📊 Status: {latest.get('status')}")
        print(f"   📺 Canal: {latest.get('channel_url')}")
        
        # 2. Buscar detalhes completos da pipeline
        print(f"\n🔍 ANALISANDO DETALHES DA PIPELINE...")
        status_response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
        
        if status_response.status_code != 200:
            print(f"❌ Erro ao buscar status: {status_response.status_code}")
            return
            
        status_data = status_response.json().get('data', {})
        steps = status_data.get('steps', {})
        config = status_data.get('config', {})
        
        print(f"\n📊 CONFIGURAÇÃO DO AGENTE:")
        agent_config = config.get('agent', {})
        print(f"   🤖 Agente Ativado: {agent_config.get('enabled', False)}")
        print(f"   🎭 Tipo de Agente: {agent_config.get('type', 'N/A')}")
        print(f"   📛 Nome do Agente: {agent_config.get('name', 'N/A')}")
        
        # 3. Analisar cada step do fluxo
        print(f"\n📈 ANÁLISE DO FLUXO:")
        print("-" * 30)
        
        # STEP 1: EXTRAÇÃO
        extraction = steps.get('extraction', {})
        extraction_status = extraction.get('status', 'pending')
        extraction_result = extraction.get('result', {})
        
        print(f"1️⃣ EXTRAÇÃO:")
        print(f"   📊 Status: {extraction_status}")
        
        if extraction_status == 'completed' and extraction_result:
            extracted_titles = extraction_result.get('titles', [])  # Campo correto é 'titles', não 'videos'
            print(f"   📹 Títulos extraídos: {len(extracted_titles)}")
            
            if extracted_titles:
                print(f"   📝 Exemplos de títulos extraídos:")
                for i, video in enumerate(extracted_titles[:3]):
                    title = video.get('title', 'N/A')
                    views = video.get('views', 0)
                    print(f"      {i+1}. {title[:60]}... ({views:,} views)")
        else:
            print(f"   ❌ Extração não completada ou sem resultados")
            
        # STEP 2: GERAÇÃO DE TÍTULOS
        titles = steps.get('titles', {})
        titles_status = titles.get('status', 'pending')
        titles_result = titles.get('result', {})
        
        print(f"\n2️⃣ GERAÇÃO DE TÍTULOS:")
        print(f"   📊 Status: {titles_status}")
        
        if titles_status == 'completed' and titles_result:
            generated_titles = titles_result.get('generated_titles', [])
            source_count = titles_result.get('source_titles_count', 0)
            provider = titles_result.get('provider_used', 'N/A')
            
            print(f"   🧠 Provider usado: {provider}")
            print(f"   📊 Títulos fonte: {source_count}")
            print(f"   📝 Títulos gerados: {len(generated_titles)}")
            
            if generated_titles:
                print(f"   💡 Título criado:")
                for i, title in enumerate(generated_titles):
                    print(f"      {i+1}. {title}")
        else:
            print(f"   ❌ Geração de títulos não completada")
            
        # STEP 3: GERAÇÃO DE PREMISSAS
        premises = steps.get('premises', {})
        premises_status = premises.get('status', 'pending')
        premises_result = premises.get('result', {})
        
        print(f"\n3️⃣ GERAÇÃO DE PREMISSAS:")
        print(f"   📊 Status: {premises_status}")
        
        if premises_status == 'completed' and premises_result:
            selected_title = premises_result.get('selected_title', 'N/A')
            premise = premises_result.get('premise', 'N/A')
            provider = premises_result.get('provider_used', 'N/A')
            word_count = premises_result.get('word_count', 0)
            
            print(f"   🧠 Provider usado: {provider}")
            print(f"   📝 Título base: {selected_title}")
            print(f"   📊 Palavras na premissa: {word_count}")
            print(f"   💭 Premissa gerada:")
            print(f"      {premise[:200]}..." if len(premise) > 200 else f"      {premise}")
        else:
            print(f"   ❌ Geração de premissas não completada")
            
        # 4. VERIFICAR SE O FLUXO FOI CORRETO
        print(f"\n🎯 VERIFICAÇÃO DO FLUXO:")
        print("-" * 30)
        
        fluxo_correto = True
        
        # Verificar se extraiu títulos
        if extraction_status != 'completed':
            print(f"❌ PROBLEMA: Extração não foi completada")
            fluxo_correto = False
        elif not extraction_result.get('titles'):  # Campo correto é 'titles'
            print(f"❌ PROBLEMA: Nenhum título foi extraído")
            fluxo_correto = False
        else:
            extracted_titles = extraction_result.get('titles', [])
            print(f"✅ Extração funcionou corretamente: {len(extracted_titles)} títulos extraídos")
            
        # Verificar se gerou títulos baseado na extração
        if titles_status != 'completed':
            print(f"❌ PROBLEMA: Geração de títulos não foi completada")
            fluxo_correto = False
        elif not titles_result.get('generated_titles'):
            print(f"❌ PROBLEMA: Nenhum título foi gerado")
            fluxo_correto = False
        else:
            print(f"✅ Geração de títulos funcionou corretamente")
            
        # Verificar se gerou premissa baseada no título
        if premises_status != 'completed':
            print(f"❌ PROBLEMA: Geração de premissas não foi completada")
            fluxo_correto = False
        elif not premises_result.get('premise'):
            print(f"❌ PROBLEMA: Nenhuma premissa foi gerada")
            fluxo_correto = False
        else:
            # Verificar se a premissa usa o título gerado
            selected_title = premises_result.get('selected_title', '')
            generated_titles = titles_result.get('generated_titles', [])
            
            if selected_title in generated_titles:
                print(f"✅ Premissa baseada no título gerado corretamente")
            else:
                print(f"⚠️ ATENÇÃO: Premissa pode não estar baseada no título gerado")
                print(f"   Título usado na premissa: {selected_title}")
                print(f"   Títulos gerados: {generated_titles}")
                
        # Verificar configuração do agente
        if agent_config.get('enabled') and agent_config.get('type') == 'millionaire_stories':
            print(f"✅ Agente de milionários ativado corretamente")
        else:
            print(f"⚠️ ATENÇÃO: Agente de milionários pode não estar configurado")
            
        print(f"\n🏁 RESULTADO FINAL:")
        print("=" * 30)
        
        if fluxo_correto:
            print(f"🎉 SUCESSO: Pipeline funcionou conforme esperado!")
            print(f"   ✅ Extraiu títulos do canal")
            print(f"   ✅ Gerou novo título baseado nos extraídos")
            print(f"   ✅ Criou premissa baseada no título gerado")
            print(f"   ✅ Agente de milionários configurado")
        else:
            print(f"❌ PROBLEMAS ENCONTRADOS: Pipeline não funcionou completamente")
            
        return fluxo_correto
        
    except Exception as e:
        print(f"❌ Erro na análise: {str(e)}")
        return False

if __name__ == '__main__':
    analyze_latest_pipeline()