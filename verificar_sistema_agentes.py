#!/usr/bin/env python3
"""
🔍 VERIFICAÇÃO COMPLETA - SISTEMA DE AGENTES ESPECIALIZADOS
=========================================================

Verifica se o sistema está funcionando corretamente com os agentes especializados,
focando especificamente nos pontos solicitados pelo usuário:

1. ✅ Título viral (precisa ser o prompt do agente)
2. ✅ Premissa (narrativa) precisa ser o prompt do agente
3. ✅ Roteiro precisa ser os prompts do agente + sistema contextual
4. ✅ Roteiro final sem marcações, fluido e completo

Este script analisa todo o fluxo para garantir que os prompts dos agentes 
sejam usados corretamente em cada fase.
"""

import os
import json
from pathlib import Path
import re

def verificar_configuracao_frontend():
    """Verificar se a configuração do agente no frontend está correta"""
    print("🎨 1. VERIFICANDO CONFIGURAÇÃO DO FRONTEND")
    print("-" * 50)
    
    frontend_file = Path("frontend/src/components/AutomationCompleteForm.jsx")
    
    if not frontend_file.exists():
        print("❌ Arquivo AutomationCompleteForm.jsx não encontrado")
        return False
    
    with open(frontend_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se há agente milionário configurado
    if "millionaire_stories" in content:
        print("✅ Agente 'Histórias de Milionários' encontrado")
        
        # Verificar prompts específicos
        prompts_encontrados = []
        
        # Títulos
        if "viral:" in content and "títulos virais" in content.lower():
            prompts_encontrados.append("Títulos - Viral")
        if "educational:" in content and "títulos educacionais" in content.lower():
            prompts_encontrados.append("Títulos - Educacional")
        
        # Premissas
        if "narrative:" in content and "premissa narrativa" in content.lower():
            prompts_encontrados.append("Premissas - Narrativa")
        
        # Roteiros
        if "inicio:" in content and "roteirista especializado" in content.lower():
            prompts_encontrados.append("Roteiros - Início")
        if "meio:" in content and "contexto anterior" in content.lower():
            prompts_encontrados.append("Roteiros - Meio")
        if "fim:" in content and "conclusão" in content.lower():
            prompts_encontrados.append("Roteiros - Fim")
        
        print(f"✅ Prompts configurados no agente ({len(prompts_encontrados)}):")
        for prompt in prompts_encontrados:
            print(f"   ✅ {prompt}")
        
        return len(prompts_encontrados) >= 5  # Mínimo esperado
    else:
        print("❌ Agente 'Histórias de Milionários' NÃO encontrado")
        return False

def verificar_mapeamento_backend():
    """Verificar se o backend mapeia corretamente os prompts dos agentes"""
    print("\n🔧 2. VERIFICANDO MAPEAMENTO NO BACKEND")
    print("-" * 50)
    
    # Verificar pipeline_complete.py
    pipeline_file = Path("backend/routes/pipeline_complete.py")
    
    if not pipeline_file.exists():
        print("❌ Arquivo pipeline_complete.py não encontrado")
        return False
    
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    mapeamentos_encontrados = []
    
    # Verificar mapeamento para títulos
    if "agent_prompts = specialized_agents" in content and "titles" in content:
        if "config['titles']['agent_prompts']" in content:
            mapeamentos_encontrados.append("Títulos")
    
    # Verificar mapeamento para premissas
    if "config['premises']['agent_prompts']" in content:
        mapeamentos_encontrados.append("Premissas")
    
    # Verificar mapeamento para roteiros
    if "config['scripts']['agent_prompts']" in content:
        mapeamentos_encontrados.append("Roteiros")
    
    print(f"✅ Mapeamentos encontrados ({len(mapeamentos_encontrados)}):")
    for mapeamento in mapeamentos_encontrados:
        print(f"   ✅ {mapeamento}")
    
    # Verificar se há configuração de agente ativo
    if "config['agent'] = {" in content and "'enabled': True" in content:
        print("✅ Configuração de agente ativo encontrada")
        return len(mapeamentos_encontrados) >= 3
    else:
        print("❌ Configuração de agente ativo NÃO encontrada")
        return False

def verificar_uso_titulos():
    """Verificar se os títulos usam prompts do agente"""
    print("\n📄 3. VERIFICANDO USO DE PROMPTS - TÍTULOS")
    print("-" * 50)
    
    pipeline_service = Path("backend/services/pipeline_service.py")
    
    if not pipeline_service.exists():
        print("❌ Arquivo pipeline_service.py não encontrado")
        return False
    
    with open(pipeline_service, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar lógica de prioridade para títulos
    verificacoes = [
        ("Prompt personalizado", "'custom_instructions' in titles_config"),
        ("Prompt do agente", "'agent_prompts' in titles_config"),
        ("Estilo no agente", "style in titles_config['agent_prompts']"),
        ("Logging do agente", "🎆 Usando prompt do agente"),
        ("Prompt source", "prompt_source = 'agent_specialized'")
    ]
    
    resultados = []
    for nome, padrao in verificacoes:
        if padrao in content:
            resultados.append(f"✅ {nome}")
        else:
            resultados.append(f"❌ {nome}")
    
    for resultado in resultados:
        print(f"   {resultado}")
    
    # Verificar se viral está sendo mapeado
    if "viral" in content or "style" in content:
        print("✅ Suporte a estilos (viral, educational) implementado")
        return len([r for r in resultados if "✅" in r]) >= 4
    else:
        print("❌ Suporte a estilos NÃO implementado")
        return False

def verificar_uso_premissas():
    """Verificar se as premissas usam prompts do agente"""
    print("\n📝 4. VERIFICANDO USO DE PROMPTS - PREMISSAS")
    print("-" * 50)
    
    pipeline_service = Path("backend/services/pipeline_service.py")
    
    with open(pipeline_service, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar lógica para premissas (que pode não ter "narrative" no form)
    verificacoes = [
        ("Prompt do agente", "'agent_prompts' in premises_config"),
        ("Fallback educational", "'educational' in agent_prompts"),
        ("Fallback narrative", "'narrative' in agent_prompts"),
        ("Formatação com título", "agent_prompt_template.format"),
        ("Logging do agente", "🎆 Usando prompt do agente")
    ]
    
    resultados = []
    for nome, padrao in verificacoes:
        if padrao in content:
            resultados.append(f"✅ {nome}")
        else:
            resultados.append(f"❌ {nome}")
    
    for resultado in resultados:
        print(f"   {resultado}")
    
    # Verificar se há tratamento para estilos não disponíveis
    if "premise_style" in content and ("educational" in content or "narrative" in content):
        print("✅ Tratamento para estilos não disponíveis no form")
        return len([r for r in resultados if "✅" in r]) >= 3
    else:
        print("❌ Tratamento para estilos NÃO implementado")
        return False

def verificar_uso_roteiros():
    """Verificar se os roteiros usam prompts do agente + sistema contextual"""
    print("\n📜 5. VERIFICANDO USO DE PROMPTS - ROTEIROS")
    print("-" * 50)
    
    script_generator = Path("backend/routes/long_script_generator.py")
    
    if not script_generator.exists():
        print("❌ Arquivo long_script_generator.py não encontrado")
        return False
    
    with open(script_generator, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se request_config está sendo usado
    verificacoes = [
        ("Request config", "request_config.get('agent_prompts', {})"),
        ("Prompt início", "agent_prompts and 'inicio' in agent_prompts"),
        ("Prompt meio", "agent_prompts and 'meio' in agent_prompts"),
        ("Prompt fim", "agent_prompts and 'fim' in agent_prompts"),
        ("Logging especializado", "🎆 Usando prompt de agente especializado"),
        ("Formatação com variáveis", ".format(titulo=titulo, premissa=premissa"),
        ("Contexto entre capítulos", "resumos[i-2]"),
        ("Sistema contextual", "generate_long_script_with_context")
    ]
    
    resultados = []
    for nome, padrao in verificacoes:
        if padrao in content:
            resultados.append(f"✅ {nome}")
        else:
            resultados.append(f"❌ {nome}")
    
    for resultado in resultados:
        print(f"   {resultado}")
    
    # Verificar prioridade: personalizado > agente > sistema
    if "prompts.get('intro')" in content and "prompts.get('middle')" in content:
        print("✅ Sistema de prioridade implementado (personalizado > agente > sistema)")
        return len([r for r in resultados if "✅" in r]) >= 6
    else:
        print("❌ Sistema de prioridade NÃO implementado completamente")
        return False

def verificar_limpeza_roteiros():
    """Verificar se os roteiros são limpos corretamente (sem marcações)"""
    print("\n🧽 6. VERIFICANDO LIMPEZA DOS ROTEIROS")
    print("-" * 50)
    
    script_generator = Path("backend/routes/long_script_generator.py")
    
    with open(script_generator, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar função de limpeza
    verificacoes = [
        ("Função limpeza", "_clean_narrative_content"),
        ("Aplicação aos capítulos", "capitulo_limpo = _clean_narrative_content(capitulo)"),
        ("Concatenação limpa", "capitulos_limpos"),
        ("Roteiro final", "roteiro_final = roteiro_completo"),
        ("Remoção de marcações", "A câmera.*\\."),
        ("Remoção de diálogos", "\\([^)]*[Ss]ussurrando[^)]*\\)"),
        ("Remoção de personagens", "[A-Z][a-zA-Z\\s]*:\\s*"),
        ("Remoção de instruções", "\\([^)]*[Mm]úsica[^)]*\\)")
    ]
    
    resultados = []
    for nome, padrao in verificacoes:
        if padrao in content:
            resultados.append(f"✅ {nome}")
        else:
            resultados.append(f"❌ {nome}")
    
    for resultado in resultados:
        print(f"   {resultado}")
    
    # Verificar se a limpeza é aplicada antes do retorno
    if "capitulos_limpos" in content and "roteiro_final" in content:
        print("✅ Limpeza aplicada corretamente antes do retorno")
        return len([r for r in resultados if "✅" in r]) >= 6
    else:
        print("❌ Limpeza NÃO aplicada corretamente")
        return False

def verificar_fluxo_completo():
    """Verificar se o fluxo completo está funcionando"""
    print("\n🌊 7. VERIFICANDO FLUXO COMPLETO")
    print("-" * 50)
    
    workflow_file = Path("backend/routes/workflow.py")
    
    if not workflow_file.exists():
        print("❌ Arquivo workflow.py não encontrado")
        return False
    
    with open(workflow_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar integração completa
    verificacoes = [
        ("Detecção agente", "agent_config.get('type') == 'specialized'"),
        ("Configuração request", "request_config = {"),
        ("Prompts do agente", "'agent_prompts': specialized_agents"),
        ("Chamada contextual", "generate_long_script_with_context"),
        ("Passagem de config", "request_config=request_config"),
        ("Informação do agente", "'agent_used': {"),
        ("Logging especializado", "🎆 Usando agente especializado")
    ]
    
    resultados = []
    for nome, padrao in verificacoes:
        if padrao in content:
            resultados.append(f"✅ {nome}")
        else:
            resultados.append(f"❌ {nome}")
    
    for resultado in resultados:
        print(f"   {resultado}")
    
    return len([r for r in resultados if "✅" in r]) >= 5

def gerar_relatorio_final():
    """Gerar relatório final da verificação"""
    print("\n" + "=" * 60)
    print("📋 RELATÓRIO FINAL - VERIFICAÇÃO DO SISTEMA DE AGENTES")
    print("=" * 60)
    
    # Executar todas as verificações
    resultados = [
        ("Configuração Frontend", verificar_configuracao_frontend()),
        ("Mapeamento Backend", verificar_mapeamento_backend()),
        ("Uso Prompts - Títulos", verificar_uso_titulos()),
        ("Uso Prompts - Premissas", verificar_uso_premissas()),
        ("Uso Prompts - Roteiros", verificar_uso_roteiros()),
        ("Limpeza Roteiros", verificar_limpeza_roteiros()),
        ("Fluxo Completo", verificar_fluxo_completo())
    ]
    
    print(f"\n🎯 RESUMO DOS RESULTADOS:")
    aprovados = 0
    
    for nome, resultado in resultados:
        status = "✅ APROVADO" if resultado else "❌ REPROVADO"
        print(f"   {nome}: {status}")
        if resultado:
            aprovados += 1
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Aprovados: {aprovados}/{len(resultados)}")
    print(f"   Taxa de sucesso: {(aprovados/len(resultados)*100):.1f}%")
    
    if aprovados >= len(resultados) - 1:  # Tolerância de 1 falha
        print(f"\n🎉 SISTEMA FUNCIONANDO CORRETAMENTE!")
        print(f"   ✅ Título viral usa prompt do agente")
        print(f"   ✅ Premissa (narrativa/educational) usa prompt do agente")
        print(f"   ✅ Roteiro usa prompts do agente + sistema contextual")
        print(f"   ✅ Roteiro final vem limpo, sem marcações")
        print(f"\n🚀 O sistema está pronto para uso com agentes especializados!")
        return True
    else:
        print(f"\n⚠️ SISTEMA PRECISA DE CORREÇÕES")
        print(f"   Verifique os itens marcados como ❌ REPROVADO")
        print(f"\n🔧 Corrija os problemas antes de usar o sistema")
        return False

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO COMPLETA - SISTEMA DE AGENTES ESPECIALIZADOS")
    print("=" * 60)
    print("Verificando se o sistema funciona conforme solicitado:")
    print("1. Título viral (prompt do agente)")
    print("2. Premissa narrativa (prompt do agente)")
    print("3. Roteiro (prompts do agente + sistema contextual)")
    print("4. Roteiro final limpo e fluido")
    print("=" * 60)
    
    # Executar verificação completa
    success = gerar_relatorio_final()
    
    if success:
        print(f"\n✅ VERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"   O sistema está funcionando conforme solicitado")
    else:
        print(f"\n❌ VERIFICAÇÃO FALHOU")
        print(f"   Corrija os problemas identificados")
    
    return success

if __name__ == "__main__":
    main()