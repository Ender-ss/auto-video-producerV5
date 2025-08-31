#!/usr/bin/env python3
"""
Script para investigar os problemas reportados pelo usuário
"""

import json
import requests
import os
from pathlib import Path

def investigate_extraction_config():
    """Investigar problema de configuração de extração"""
    print("🔍 INVESTIGANDO PROBLEMAS DE CONFIGURAÇÃO")
    print("=" * 50)
    
    # 1. Verificar o problema de extração (1 vs 10 títulos)
    print("\n1. PROBLEMA DE CONFIGURAÇÃO DE EXTRAÇÃO")
    print("-" * 30)
    
    # Verificar configuração padrão
    try:
        response = requests.get('http://localhost:5000/api/health')
        if response.status_code == 200:
            print("✅ Backend está rodando")
        else:
            print("❌ Backend não está respondendo")
            return
    except:
        print("❌ Backend não está acessível")
        return
    
    # Buscar última pipeline para ver configuração
    try:
        response = requests.get('http://localhost:5000/api/pipeline/list')
        if response.status_code == 200:
            pipelines = response.json().get('data', [])
            if pipelines:
                latest = pipelines[0]
                print(f"📋 Última pipeline: {latest.get('pipeline_id', 'N/A')}")
                
                config = latest.get('config', {})
                extraction_config = config.get('extraction', {})
                
                print(f"📥 Configuração de extração encontrada:")
                print(f"   - enabled: {extraction_config.get('enabled', 'N/A')}")
                print(f"   - method: {extraction_config.get('method', 'N/A')}")
                print(f"   - max_titles: {extraction_config.get('max_titles', 'N/A')}")
                print(f"   - min_views: {extraction_config.get('min_views', 'N/A')}")
                
                # Verificar se há discrepância
                max_titles = extraction_config.get('max_titles', 10)
                if max_titles != 1:
                    print(f"⚠️ PROBLEMA IDENTIFICADO: max_titles está configurado como {max_titles}, mas usuário disse ter configurado 1")
                
                # Verificar resultados da extração
                steps = latest.get('steps', {})
                extraction_step = steps.get('extraction', {})
                extraction_result = extraction_step.get('result', {})
                
                if extraction_result:
                    titles = extraction_result.get('titles', [])
                    print(f"📊 Títulos extraídos na última execução: {len(titles)}")
                    
                    if len(titles) > max_titles:
                        print(f"❌ PROBLEMA: Extraiu {len(titles)} títulos mas deveria extrair no máximo {max_titles}")
                    
            else:
                print("📭 Nenhuma pipeline encontrada")
        else:
            print("❌ Erro ao buscar pipelines")
    except Exception as e:
        print(f"❌ Erro ao investigar configuração: {e}")

def investigate_arthur_blackwood():
    """Investigar problema do nome Arthur Blackwood"""
    print("\n2. PROBLEMA DO NOME 'ARTHUR BLACKWOOD'")
    print("-" * 30)
    
    # Verificar arquivos com Arthur Blackwood
    backend_dir = Path("backend")
    arthur_files = []
    
    for file_path in backend_dir.rglob("*.txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "Arthur Blackwood" in content:
                    arthur_files.append(file_path)
                    print(f"📄 Encontrado em: {file_path}")
        except:
            continue
    
    print(f"\n📊 Total de arquivos com 'Arthur Blackwood': {len(arthur_files)}")
    
    if arthur_files:
        print("\n🔍 ANÁLISE DOS ARQUIVOS:")
        for file_path in arthur_files[:3]:  # Mostrar apenas os 3 primeiros
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Contar ocorrências
                    count = content.count("Arthur Blackwood")
                    print(f"   {file_path.name}: {count} ocorrências")
            except:
                continue
        
        print("\n❓ POSSÍVEIS CAUSAS:")
        print("   - Arthur Blackwood pode estar em prompts de exemplo ou templates")
        print("   - Pode estar em cache de resultados anteriores")
        print("   - Agente especializado pode ter esse nome como padrão")

def investigate_script_formatting():
    """Investigar problema de formatação de roteiro"""
    print("\n3. PROBLEMA DE FORMATAÇÃO DE ROTEIRO")
    print("-" * 30)
    
    # Verificar função de limpeza de conteúdo narrativo
    script_generator_path = Path("backend/routes/long_script_generator.py")
    
    if script_generator_path.exists():
        try:
            with open(script_generator_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Verificar se a função de limpeza existe
                if "_clean_narrative_content" in content:
                    print("✅ Função _clean_narrative_content encontrada")
                    
                    # Extrair a função para análise
                    lines = content.split('\n')
                    in_function = False
                    function_lines = []
                    
                    for line in lines:
                        if "def _clean_narrative_content" in line:
                            in_function = True
                        
                        if in_function:
                            function_lines.append(line)
                            
                            # Verificar se chegou ao fim da função
                            if line.strip() and not line.startswith(' ') and not line.startswith('\t') and "def _clean_narrative_content" not in line:
                                break
                    
                    print("\n📋 FUNÇÃO DE LIMPEZA ATUAL:")
                    for line in function_lines[:15]:  # Mostrar apenas as primeiras 15 linhas
                        print(f"   {line}")
                    
                    # Verificar padrões de limpeza
                    function_text = '\n'.join(function_lines)
                    
                    patterns_to_check = [
                        "câmera",
                        "sussurrando",
                        "paneo", 
                        "A câmera",
                        "Arthur:",
                        "\\(.*\\)"
                    ]
                    
                    print("\n🔍 PADRÕES DE LIMPEZA VERIFICADOS:")
                    for pattern in patterns_to_check:
                        if pattern.lower() in function_text.lower():
                            print(f"   ✅ Padrão '{pattern}' está sendo tratado")
                        else:
                            print(f"   ❌ Padrão '{pattern}' NÃO está sendo tratado")
                
                else:
                    print("❌ Função _clean_narrative_content NÃO encontrada")
        except Exception as e:
            print(f"❌ Erro ao analisar script generator: {e}")
    else:
        print("❌ Arquivo long_script_generator.py não encontrado")

def check_agent_prompts():
    """Verificar configuração de prompts do agente milionário"""
    print("\n4. VERIFICAÇÃO DE PROMPTS DO AGENTE")
    print("-" * 30)
    
    # Verificar arquivos de configuração de agentes
    frontend_dir = Path("frontend/src/components")
    
    for file_path in frontend_dir.rglob("*.jsx"):
        if "AutomationCompleteForm" in file_path.name:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Verificar se há configuração de agente milionário
                    if "millionaire" in content.lower():
                        print(f"✅ Configuração de agente milionário encontrada em: {file_path.name}")
                        
                        # Verificar se há prompt narrativo
                        if "narrative" in content.lower():
                            print("   ✅ Opção 'narrative' encontrada no formulário")
                        else:
                            print("   ❌ Opção 'narrative' NÃO encontrada no formulário")
                        
                        # Buscar por Arthur Blackwood no prompt
                        if "Arthur Blackwood" in content:
                            print("   ⚠️ Nome 'Arthur Blackwood' encontrado no código do formulário")
                            
            except Exception as e:
                continue

def generate_recommendations():
    """Gerar recomendações para corrigir os problemas"""
    print("\n🔧 RECOMENDAÇÕES PARA CORREÇÃO")
    print("=" * 50)
    
    print("\n1. PROBLEMA DE CONFIGURAÇÃO DE EXTRAÇÃO:")
    print("   - Verificar se o formulário está enviando o valor correto de max_titles")
    print("   - Verificar se há configuração padrão sobrescrevendo o valor do usuário")
    print("   - Verificar se o backend está respeitando a configuração enviada")
    
    print("\n2. PROBLEMA DO NOME 'ARTHUR BLACKWOOD':")
    print("   - Limpar arquivos de cache que contenham esse nome")
    print("   - Verificar se há prompts padrão com esse nome")
    print("   - Verificar se o agente especializado tem esse nome hardcoded")
    
    print("\n3. PROBLEMA DE FORMATAÇÃO DE ROTEIRO:")
    print("   - Melhorar a função _clean_narrative_content")
    print("   - Adicionar mais padrões de limpeza para remover marcações")
    print("   - Verificar se a função está sendo chamada corretamente")
    
    print("\n4. AÇÕES RECOMENDADAS:")
    print("   - Atualizar função de limpeza de roteiro")
    print("   - Limpar arquivos de cache com Arthur Blackwood")
    print("   - Verificar configuração de formulário de extração")
    print("   - Testar pipeline completa após correções")

if __name__ == "__main__":
    print("🔍 INVESTIGAÇÃO DE PROBLEMAS REPORTADOS")
    print("Problemas reportados pelo usuário:")
    print("1. Extração ignorando configuração (extraindo 10 ao invés de 1)")
    print("2. Nome 'Arthur Blackwood' sempre aparecendo nas premissas") 
    print("3. Roteiro incluindo marcações mesmo sendo instruído para não ter")
    print()
    
    investigate_extraction_config()
    investigate_arthur_blackwood()
    investigate_script_formatting()
    check_agent_prompts()
    generate_recommendations()
    
    print("\n✅ INVESTIGAÇÃO CONCLUÍDA")
    print("Verifique as recomendações acima para corrigir os problemas identificados.")