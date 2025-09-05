#!/usr/bin/env python3
"""
Exemplo de uso do Storyteller Unlimited no pipeline
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.storyteller_service import storyteller_service

def exemplo_storyteller_millionaire():
    """Exemplo de uso com história de empreendedorismo"""
    
    print("🏆 Exemplo: História de Empreendedorismo")
    print("=" * 50)
    
    result = storyteller_service.generate_storyteller_script(
        title="De Falência à Liberdade Financeira",
        premise="Como Maria Silva saiu das dívidas e construiu um império digital em 18 meses",
        api_key="demo_key",
        provider="demo",
        agent_type="millionaire_stories",
        num_chapters=4
    )
    
    print(f"✅ Roteiro gerado: {result['title']}")
    print(f"📊 {result['num_chapters']} capítulos")
    print(f"⏱️  Duração: {result['estimated_duration']} segundos")
    print(f"📄 {result['total_characters']} caracteres")
    
    return result

def exemplo_storyteller_romance():
    """Exemplo de uso com história de romance"""
    
    print("\n💕 Exemplo: História de Romance")
    print("=" * 50)
    
    result = storyteller_service.generate_storyteller_script(
        title="Amor em Tempos de Chuva",
        premise="Dois estranhos que se encontram em uma estação de metrô durante uma tempestade",
        api_key="demo_key",
        provider="demo",
        agent_type="romance_agent",
        num_chapters=3
    )
    
    print(f"✅ Roteiro gerado: {result['title']}")
    print(f"📊 {result['num_chapters']} capítulos")
    print(f"⏱️  Duração: {result['estimated_duration']} segundos")
    
    return result

def exemplo_storyteller_horror():
    """Exemplo de uso com história de terror"""
    
    print("\n👻 Exemplo: História de Terror")
    print("=" * 50)
    
    result = storyteller_service.generate_storyteller_script(
        title="A Mansão das Sombras",
        premise="Uma família se muda para uma casa antiga e descobre segredos sombrios",
        api_key="demo_key",
        provider="demo",
        agent_type="horror_agent",
        num_chapters=5
    )
    
    print(f"✅ Roteiro gerado: {result['title']}")
    print(f"📊 {result['num_chapters']} capítulos")
    print(f"⏱️  Duração: {result['estimated_duration']} segundos")
    
    return result

def salvar_exemplos():
    """Salva exemplos em arquivos para visualização"""
    
    # Criar diretório de exemplos
    examples_dir = os.path.join(os.path.dirname(__file__), 'examples')
    os.makedirs(examples_dir, exist_ok=True)
    
    # Gerar e salvar exemplos
    exemplos = [
        exemplo_storyteller_millionaire(),
        exemplo_storyteller_romance(),
        exemplo_storyteller_horror()
    ]
    
    for i, exemplo in enumerate(exemplos, 1):
        filename = f"storyteller_example_{i}.md"
        filepath = os.path.join(examples_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(exemplo['full_script'])
        
        print(f"📄 Salvo: {filename}")
    
    print(f"\n📁 Todos os exemplos salvos em: {examples_dir}")

if __name__ == "__main__":
    print("🎬 Storyteller Unlimited - Exemplos de Uso")
    print("=" * 60)
    
    try:
        salvar_exemplos()
        print("\n🎉 Todos os exemplos gerados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()