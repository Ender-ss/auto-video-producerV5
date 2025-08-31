#!/usr/bin/env python3
"""
🔍 INVESTIGAÇÃO DA FALHA NA GERAÇÃO DE TÍTULOS
============================================

Script para investigar o problema específico na geração de títulos:
"Falha na geração de títulos com Gemini após todas as 7 tentativas. 
Último erro: 429 You exceeded your current quota"

O problema pode estar em:
1. Sistema de rotação de chaves não funcionando corretamente
2. Todas as chaves realmente esgotadas no mesmo dia
3. Bug no mecanismo de retry
4. Chaves sendo reutilizadas incorretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def investigar_estado_chaves():
    """Investigar o estado atual das chaves Gemini"""
    print("🔍 INVESTIGANDO ESTADO DAS CHAVES GEMINI")
    print("-" * 50)
    
    try:
        from routes.automations import (
            GEMINI_KEYS_ROTATION, 
            get_gemini_keys_count, 
            get_next_gemini_key,
            load_gemini_keys
        )
        
        # 1. Verificar quantas chaves estão carregadas
        keys_count = get_gemini_keys_count()
        print(f"📊 Total de chaves carregadas: {keys_count}")
        
        # 2. Verificar estado da rotação
        print(f"\n🔄 Estado da rotação:")
        print(f"   Índice atual: {GEMINI_KEYS_ROTATION.get('current_index', 'N/A')}")
        print(f"   Último reset: {GEMINI_KEYS_ROTATION.get('last_reset', 'N/A')}")
        print(f"   Total de chaves: {len(GEMINI_KEYS_ROTATION.get('keys', []))}")
        
        # 3. Verificar contadores de uso
        usage_count = GEMINI_KEYS_ROTATION.get('usage_count', {})
        print(f"\n📈 Contadores de uso por chave:")
        for i, key in enumerate(GEMINI_KEYS_ROTATION.get('keys', [])):
            key_short = key[:20] + "..." if len(key) > 20 else key
            count = usage_count.get(key, 0)
            print(f"   Chave {i+1}: {key_short} -> {count} usos")
        
        # 4. Testar rotação de chaves
        print(f"\n🔄 Testando rotação de chaves:")
        for i in range(min(keys_count, 5)):  # Testar até 5 chaves
            try:
                next_key = get_next_gemini_key()
                if next_key:
                    key_short = next_key[:20] + "..." if len(next_key) > 20 else next_key
                    print(f"   Tentativa {i+1}: {key_short}")
                else:
                    print(f"   Tentativa {i+1}: NENHUMA CHAVE DISPONÍVEL")
            except Exception as e:
                print(f"   Tentativa {i+1}: ERRO - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao investigar chaves: {e}")
        return False

def simular_geração_titulo():
    """Simular exatamente o processo de geração de títulos"""
    print(f"\n🎯 SIMULANDO GERAÇÃO DE TÍTULOS")
    print("-" * 50)
    
    try:
        from services.ai_services import generate_titles_with_gemini
        from routes.automations import get_gemini_keys_count
        
        # Dados de teste similares ao que a pipeline usa
        source_titles = ["Como GANHAR DINHEIRO na internet", "SEGREDO dos MILIONÁRIOS revelado"]
        instructions = "Crie títulos virais para histórias de milionários sobre contraste social"
        
        print(f"📝 Títulos de origem: {source_titles}")
        print(f"📝 Instruções: {instructions}")
        print(f"🔑 Chaves disponíveis: {get_gemini_keys_count()}")
        
        # Simular geração
        print(f"\n🚀 Iniciando geração...")
        
        def callback_update(current_titles):
            print(f"   📊 Progresso: {len(current_titles)} títulos gerados")
        
        result = generate_titles_with_gemini(
            source_titles=source_titles,
            instructions=instructions,
            api_key=None,  # Deixar None para usar rotação automática
            update_callback=callback_update
        )
        
        print(f"\n📋 RESULTADO:")
        if result.get('success'):
            print(f"✅ Sucesso!")
            generated = result.get('data', {}).get('generated_titles', [])
            print(f"📝 Títulos gerados ({len(generated)}):")
            for i, title in enumerate(generated, 1):
                print(f"   {i}. {title}")
        else:
            print(f"❌ Falha!")
            error = result.get('error', 'Erro desconhecido')
            print(f"💥 Erro: {error}")
            
            # Analisar o tipo de erro
            if "429" in error or "quota" in error.lower():
                print(f"🔍 DIAGNÓSTICO: Erro de quota detectado!")
                print(f"   Todas as chaves parecem ter atingido o limite diário")
                print(f"   Ou há um bug no sistema de rotação")
            elif "7 tentativas" in error:
                print(f"🔍 DIAGNÓSTICO: Sistema tentou todas as 7 chaves disponíveis")
                print(f"   Confirma que o sistema está usando as chaves corretamente")
            else:
                print(f"🔍 DIAGNÓSTICO: Erro não relacionado à quota")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
        return None

def verificar_quotas_reais():
    """Verificar as quotas reais das chaves Gemini"""
    print(f"\n💰 VERIFICANDO QUOTAS REAIS DAS CHAVES")
    print("-" * 50)
    
    try:
        import google.generativeai as genai
        from routes.automations import GEMINI_KEYS_ROTATION
        from datetime import datetime
        
        keys = GEMINI_KEYS_ROTATION.get('keys', [])
        
        for i, api_key in enumerate(keys, 1):
            print(f"\n🔑 Testando Chave {i}:")
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Teste simples
                response = model.generate_content("Diga apenas 'teste'")
                
                if response and response.text:
                    print(f"   ✅ Funcionando - Resposta: {response.text.strip()}")
                else:
                    print(f"   ⚠️ Resposta vazia")
                    
            except Exception as e:
                error_str = str(e)
                if "429" in error_str:
                    print(f"   ❌ QUOTA EXCEDIDA - {error_str}")
                elif "quota" in error_str.lower():
                    print(f"   ❌ PROBLEMA DE QUOTA - {error_str}")
                else:
                    print(f"   ❌ OUTRO ERRO - {error_str}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar quotas: {e}")
        return False

def analisar_logs_pipeline():
    """Analisar logs da pipeline para entender a falha"""
    print(f"\n📊 ANÁLISE DE LOGS DA PIPELINE")
    print("-" * 50)
    
    # Verificar se há logs de falha recentes
    logs_dir = "logs"
    if os.path.exists(logs_dir):
        print(f"📂 Diretório de logs encontrado: {logs_dir}")
        
        # Listar arquivos de log recentes
        try:
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
            if log_files:
                print(f"📋 Arquivos de log encontrados:")
                for log_file in sorted(log_files)[-3:]:  # Últimos 3 arquivos
                    print(f"   📄 {log_file}")
            else:
                print(f"📋 Nenhum arquivo de log encontrado")
        except Exception as e:
            print(f"❌ Erro ao listar logs: {e}")
    else:
        print(f"📂 Diretório de logs não encontrado")
    
    # Verificar se há cache relacionado a falhas
    cache_dir = "cache"
    if os.path.exists(cache_dir):
        print(f"\n📦 Verificando cache...")
        
        try:
            for root, dirs, files in os.walk(cache_dir):
                if files:
                    print(f"   📂 {root}: {len(files)} arquivos")
        except Exception as e:
            print(f"❌ Erro ao verificar cache: {e}")

def gerar_relatorio_diagnostico():
    """Gerar relatório completo do diagnóstico"""
    print(f"\n" + "=" * 60)
    print(f"📋 RELATÓRIO DE DIAGNÓSTICO - FALHA NA GERAÇÃO DE TÍTULOS")
    print(f"=" * 60)
    
    # Executar todas as investigações
    resultados = {
        'chaves_ok': investigar_estado_chaves(),
        'simulacao_ok': simular_geração_titulo() is not None,
        'quotas_ok': verificar_quotas_reais()
    }
    
    analisar_logs_pipeline()
    
    print(f"\n🎯 CONCLUSÕES:")
    
    if resultados['chaves_ok']:
        print(f"✅ Sistema de chaves carregado corretamente")
    else:
        print(f"❌ Problema no carregamento das chaves")
    
    if resultados['simulacao_ok']:
        print(f"✅ Simulação executada (verificar resultado acima)")
    else:
        print(f"❌ Falha na simulação da geração")
    
    if resultados['quotas_ok']:
        print(f"✅ Verificação de quotas executada (verificar resultado acima)")
    else:
        print(f"❌ Falha na verificação de quotas")
    
    print(f"\n💡 PRÓXIMOS PASSOS:")
    print(f"1. Se todas as chaves estão com quota excedida:")
    print(f"   - Aguardar reset diário (meia-noite PST)")
    print(f"   - Ou adicionar mais chaves Gemini")
    
    print(f"2. Se há bug no sistema de rotação:")
    print(f"   - Forçar reset das chaves")
    print(f"   - Verificar implementação do get_next_gemini_key()")
    
    print(f"3. Se há problema na pipeline:")
    print(f"   - Verificar logs detalhados")
    print(f"   - Testar com provider diferente temporariamente")

def main():
    """Função principal"""
    print("🔍 INVESTIGAÇÃO COMPLETA - FALHA NA GERAÇÃO DE TÍTULOS")
    print("=" * 60)
    print("Analisando o erro: 'Falha na geração de títulos com Gemini após")
    print("todas as 7 tentativas. Último erro: 429 You exceeded your current quota'")
    print("=" * 60)
    
    gerar_relatorio_diagnostico()
    
    print(f"\n🎯 INVESTIGAÇÃO CONCLUÍDA!")
    print(f"Verifique os resultados acima para identificar a causa da falha.")

if __name__ == "__main__":
    main()