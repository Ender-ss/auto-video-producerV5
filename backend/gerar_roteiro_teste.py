#!/usr/bin/env python3
"""
Script para gerar roteiro de teste com Storyteller Unlimited
Agente: millionaire_stories
Capítulos: 5
"""

import sys
import os
import json
from datetime import datetime

# Adicionar diretório ao path
sys.path.insert(0, '.')

print('=== CRIANDO ROTEIRO DE TESTE COM STORYTELLER ===')

# Importar serviço
try:
    from services.storyteller_service import storyteller_service
    print('✅ Storyteller Service carregado')
except Exception as e:
    print(f'❌ Erro ao carregar serviço: {e}')
    exit(1)

# Configurações do teste seguindo STORYTELLER_UNLIMITED_IMPLEMENTATION.md
titulo = 'De Mendigo a Magnata: A Jornada de Rafael Silva'
premissa = '''
Rafael Silva era um jovem de 22 anos que vivia nas ruas de São Paulo, 
survindo de esmolas e recolhendo latinhas. Após salvar um empresário 
bilionário de um assalto, ele recebe uma oportunidade única: trabalhar 
como office-boy na maior empresa do país. A história acompanha sua 
jornada desde a vida nas ruas até se tornar o CEO de um império 
financeiro, enfrentando corrupção, traições e desafios inimagináveis.
'''

print(f'📋 Título: {titulo}')
print(f'📋 Capítulos: 5')
print(f'📋 Agente: millionaire_stories')
print(f'📋 Configuração: {storyteller_service.agent_configs["millionaire_stories"]}')

# Gerar roteiro
print('\n🔄 Gerando roteiro com Storyteller...')
resultado = storyteller_service.generate_storyteller_script(
    title=titulo,
    premise=premissa,
    agent_type='millionaire_stories',
    num_chapters=5
)

if resultado.get('success'):
    print('✅ ROTEIRO GERADO COM SUCESSO!')
    
    # Criar pasta de teste
    pasta_teste = 'roteiro_teste'
    if not os.path.exists(pasta_teste):
        os.makedirs(pasta_teste)
        print(f'📁 Pasta {pasta_teste} criada')
    
    # Salvar roteiro completo em JSON
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_roteiro = f'{pasta_teste}/roteiro_milionario_5cap_{timestamp}.json'
    
    with open(arquivo_roteiro, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print(f'💾 Roteiro JSON salvo em: {arquivo_roteiro}')
    
    # Criar versão legível em texto
    arquivo_txt = f'{pasta_teste}/roteiro_milionario_5cap_{timestamp}.txt'
    with open(arquivo_txt, 'w', encoding='utf-8') as f:
        f.write(f'=== ROTEIRO: {titulo} ===\n\n')
        f.write(f'Premissa: {premissa.strip()}\n\n')
        f.write(f'Total de caracteres: {len(resultado.get("full_script", ""))}\n')
        f.write(f'Número de capítulos: {len(resultado.get("chapters", []))}\n')
        
        # Detalhes de configuração
        config = storyteller_service.agent_configs['millionaire_stories']
        f.write(f'Configuração usada: {config}\n\n')
        
        # Detalhes de cada capítulo
        for i, cap in enumerate(resultado.get('chapters', []), 1):
            f.write(f'\n--- CAPÍTULO {i} ---\n')
            f.write(f'Tamanho: {len(cap.get("content", ""))} caracteres\n')
            f.write(f'Validação: {cap.get("validation", {})}\n')
            f.write('\nCONTEÚDO:\n')
            f.write(cap.get('content', ''))
            f.write('\n' + '='*80 + '\n')
    
    print(f'💾 Versão legível salva em: {arquivo_txt}')
    
    # Criar relatório de verificação
    arquivo_relatorio = f'{pasta_teste}/relatorio_verificacao_{timestamp}.txt'
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write('=== RELATÓRIO DE VERIFICAÇÃO ===\n\n')
        f.write('Verificação baseada em STORYTELLER_UNLIMITED_IMPLEMENTATION.md:\n\n')
        
        # Verificar estrutura
        f.write('1. ESTRUTURA DO ROTEIRO:\n')
        f.write(f'   ✓ Título presente: {bool(resultado.get("title"))}\n')
        f.write(f'   ✓ Premissa presente: {bool(resultado.get("premise"))}\n')
        f.write(f'   ✓ Conteúdo completo: {bool(resultado.get("full_script"))}\n')
        f.write(f'   ✓ Capítulos divididos: {len(resultado.get("chapters", []))}\n')
        
        # Verificar configurações do agente
        chapters = resultado.get('chapters', [])
        if chapters:
            f.write('\n2. CONFIGURAÇÕES DO AGENTE MILIONÁRIO:\n')
            config = storyteller_service.agent_configs['millionaire_stories']
            f.write(f'   - Min chars por capítulo: {config["min_chars"]}\n')
            f.write(f'   - Max chars por capítulo: {config["max_chars"]}\n')
            f.write(f'   - Target chars por capítulo: {config["target_chars"]}\n')
            
            # Verificar tamanhos dos capítulos
            f.write('\n3. ANÁLISE DE TAMANHO DOS CAPÍTULOS:\n')
            for i, cap in enumerate(chapters, 1):
                length = len(cap.get('content', ''))
                status = "✓ OK" if config['min_chars'] <= length <= config['max_chars'] else "❌ FORA DO LIMITE"
                f.write(f'   Capítulo {i}: {length} chars - {status}\n')
        
        # Verificar validação
        f.write('\n4. VALIDAÇÃO DE CAPÍTULOS:\n')
        all_valid = True
        for i, cap in enumerate(chapters, 1):
            validation = cap.get('validation', {})
            is_valid = validation.get('valid', False)
            status = "✓ VÁLIDO" if is_valid else "❌ PROBLEMAS"
            f.write(f'   Capítulo {i}: {status}\n')
            if not is_valid:
                f.write(f'     Issues: {validation.get("issues", [])}\n')
                all_valid = False
        
        f.write(f'\n5. STATUS FINAL: {"✅ ROTEIRO VÁLIDO" if all_valid else "❌ NECESSITA AJUSTES"}\n')
        
        # Informações técnicas
        f.write('\n6. INFORMAÇÕES TÉCNICAS:\n')
        f.write(f'   - API Key usada: {resultado.get("api_key_used", "N/A")[:15]}...\n')
        f.write(f'   - Timestamp: {timestamp}\n')
        f.write(f'   - Total caracteres: {len(resultado.get("full_script", ""))}\n')
    
    print(f'📊 Relatório de verificação salvo em: {arquivo_relatorio}')
    
    # Resumo final
    print('\n📊 RESUMO DO TESTE:')
    print(f'   ✅ Título: {resultado.get("title", "N/A")}')
    print(f'   ✅ Capítulos: {len(resultado.get("chapters", []))}')
    print(f'   ✅ Total caracteres: {len(resultado.get("full_script", ""))}')
    print(f'   ✅ API Key: {resultado.get("api_key_used", "N/A")[:15]}...')
    print(f'   ✅ Arquivos salvos em: {pasta_teste}/')
    
else:
    print(f'❌ Erro na geração: {resultado.get("error", "Erro desconhecido")}')
    if 'traceback' in resultado:
        print('Detalhes:', resultado.get('traceback'))