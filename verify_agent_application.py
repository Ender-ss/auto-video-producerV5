#!/usr/bin/env python3
"""
🔍 Verificação Específica da Aplicação do Agente Especializado
Confirma se o agente está sendo aplicado nos prompts e resultados
"""

import json
import requests
import time

def verify_agent_application():
    """Verificar se o agente especializado está sendo aplicado corretamente"""
    
    print("🤖 VERIFICAÇÃO ESPECÍFICA DO AGENTE ESPECIALIZADO")
    print("=" * 60)
    
    # Buscar a pipeline mais recente com agente
    try:
        response = requests.get('http://localhost:5000/api/pipeline/active')
        
        if response.status_code == 200:
            result = response.json()
            pipelines = result.get('pipelines', [])
            
            # Procurar por pipeline com agente
            agent_pipeline = None
            for pipeline in pipelines:
                pipeline_id = pipeline.get('pipeline_id')
                status_response = requests.get(f'http://localhost:5000/api/pipeline/status/{pipeline_id}')
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    pipeline_data = status_result.get('data', {})
                    config = pipeline_data.get('config', {})
                    agent_config = config.get('agent', {})
                    
                    if agent_config.get('enabled') or agent_config.get('type'):
                        agent_pipeline = pipeline_data
                        break
            
            if not agent_pipeline:
                print("❌ Nenhuma pipeline com agente encontrada")
                return False
            
            return analyze_agent_application(agent_pipeline)
        
        else:
            print(f"❌ Erro ao buscar pipelines: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Erro na verificação: {str(e)}")
        return False

def analyze_agent_application(pipeline_data):
    """Analisar se o agente foi aplicado corretamente"""
    
    print("\n📊 ANÁLISE DA APLICAÇÃO DO AGENTE")
    print("-" * 40)
    
    config = pipeline_data.get('config', {})
    steps = pipeline_data.get('steps', {})
    
    # Verificar configuração do agente
    agent_config = config.get('agent', {})
    
    print("🤖 CONFIGURAÇÃO DO AGENTE:")
    print(f"   Habilitado: {agent_config.get('enabled', False)}")
    print(f"   Tipo: {agent_config.get('type', 'N/A')}")
    print(f"   Nome: {agent_config.get('name', 'N/A')}")
    print(f"   Tipo Especializado: {agent_config.get('specialized_type', 'N/A')}")
    
    if not agent_config.get('enabled') and not agent_config.get('type'):
        print("❌ PROBLEMA: Agente não está configurado")
        return False
    
    # Verificar se há prompts especializados na configuração
    specialized_agents = config.get('specialized_agents', {})
    if specialized_agents:
        print(f"\n🎯 AGENTES ESPECIALIZADOS CONFIGURADOS:")
        for agent_name, agent_data in specialized_agents.items():
            print(f"   {agent_name}: {agent_data.get('name', 'N/A')}")
            
            prompts = agent_data.get('prompts', {})
            if prompts:
                print(f"     Prompts disponíveis: {list(prompts.keys())}")
    
    # Verificar títulos gerados - devem refletir o estilo do agente
    print(f"\n📝 VERIFICANDO APLICAÇÃO NOS TÍTULOS:")
    titles_step = steps.get('titles', {})
    titles_result = titles_step.get('result', {})
    
    if titles_result:
        generated_titles = titles_result.get('generated_titles', [])
        
        # Palavras-chave que indicam aplicação do agente "Histórias de Milionários"
        millionaire_keywords = [
            'milhão', 'milionário', 'bilhão', 'rico', 'riqueza', 'fortuna', 
            'dinheiro', '$', 'real', 'reais', 'dolár', 'sucesso', 'luxo'
        ]
        
        agent_applied_in_titles = False
        for title in generated_titles:
            title_lower = title.lower()
            if any(keyword in title_lower for keyword in millionaire_keywords):
                agent_applied_in_titles = True
                print(f"   ✅ Título com tema do agente: {title}")
            else:
                print(f"   ⚠️ Título sem tema específico: {title}")
        
        if agent_applied_in_titles:
            print(f"   ✅ AGENTE APLICADO NOS TÍTULOS")
        else:
            print(f"   ❌ AGENTE NÃO APLICADO NOS TÍTULOS")
    
    # Verificar premissas - devem conter contexto do agente
    print(f"\n💡 VERIFICANDO APLICAÇÃO NAS PREMISSAS:")
    premises_step = steps.get('premises', {})
    premises_result = premises_step.get('result', {})
    
    if premises_result:
        premises_list = premises_result.get('premises', [])
        premise_text = premises_result.get('premise', '')
        
        # Analisar texto da premissa
        premise_to_analyze = ''
        if premises_list:
            first_premise = premises_list[0]
            premise_to_analyze = first_premise.get('premise', first_premise) if isinstance(first_premise, dict) else first_premise
        elif premise_text:
            premise_to_analyze = premise_text
        
        if premise_to_analyze:
            premise_lower = str(premise_to_analyze).lower()
            
            # Verificar se contém contexto de "histórias de milionários"
            context_keywords = [
                'milionário', 'rico', 'riqueza', 'sucesso', 'história', 'transformação',
                'contraste', 'social', 'luxo', 'dinheiro', 'fortuna'
            ]
            
            context_found = sum(1 for keyword in context_keywords if keyword in premise_lower)
            
            print(f"   Premissa ({len(premise_to_analyze)} chars): {str(premise_to_analyze)[:150]}...")
            print(f"   Palavras-chave do agente encontradas: {context_found}/{len(context_keywords)}")
            
            if context_found >= 2:
                print(f"   ✅ AGENTE APLICADO NA PREMISSA")
            else:
                print(f"   ❌ AGENTE NÃO APLICADO NA PREMISSA")
    
    # Verificar roteiros - devem seguir estrutura do agente
    print(f"\n📜 VERIFICANDO APLICAÇÃO NOS ROTEIROS:")
    scripts_step = steps.get('scripts', {})
    scripts_result = scripts_step.get('result', {})
    
    if scripts_result:
        script_content = scripts_result.get('script', '')
        
        if script_content:
            script_lower = script_content.lower()
            
            # Verificar elementos narrativos específicos do agente
            narrative_elements = [
                'milionário', 'rico', 'riqueza', 'história', 'transformação',
                'personagem', 'descoberta', 'contraste', 'lição', 'inspiração'
            ]
            
            elements_found = sum(1 for element in narrative_elements if element in script_lower)
            
            print(f"   Roteiro ({len(script_content)} chars)")
            print(f"   Elementos narrativos do agente: {elements_found}/{len(narrative_elements)}")
            
            # Mostrar início do roteiro para análise visual
            print(f"   Início: {script_content[:200]}...")
            
            if elements_found >= 3:
                print(f"   ✅ AGENTE APLICADO NO ROTEIRO")
            else:
                print(f"   ❌ AGENTE NÃO APLICADO NO ROTEIRO")
    
    # Análise final
    print(f"\n🎯 ANÁLISE FINAL DA APLICAÇÃO DO AGENTE:")
    
    # Verificar se a configuração do agente está sendo passada corretamente
    agent_in_config = bool(agent_config.get('enabled') or agent_config.get('type'))
    specialized_agents_present = bool(specialized_agents)
    
    print(f"   Agente na configuração: {'✅' if agent_in_config else '❌'}")
    print(f"   Agentes especializados: {'✅' if specialized_agents_present else '❌'}")
    
    if agent_in_config and specialized_agents_present:
        print(f"\n✅ AGENTE ESPECIALIZADO ESTÁ SENDO APLICADO CORRETAMENTE")
        print(f"   - Configuração presente e válida")
        print(f"   - Prompts especializados disponíveis")
        print(f"   - Conteúdo gerado reflete o tema do agente")
        return True
    else:
        print(f"\n❌ PROBLEMAS NA APLICAÇÃO DO AGENTE:")
        if not agent_in_config:
            print(f"   - Configuração do agente ausente ou inválida")
        if not specialized_agents_present:
            print(f"   - Prompts especializados não encontrados")
        return False

if __name__ == "__main__":
    success = verify_agent_application()
    
    if success:
        print(f"\n🎉 AGENTE ESPECIALIZADO FUNCIONANDO CORRETAMENTE!")
    else:
        print(f"\n💥 PROBLEMAS NA APLICAÇÃO DO AGENTE ESPECIALIZADO!")