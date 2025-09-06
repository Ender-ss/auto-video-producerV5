#!/usr/bin/env python3
"""
Script para testar a remoção de cabeçalhos de capítulos
Teste com 3 capítulos usando remove_chapter_headers=True
"""

import sys
import os
import json
from datetime import datetime

# Adicionar diretório ao path
sys.path.insert(0, '.')

print('=== TESTE DE REMOÇÃO DE CABEÇALHOS DE CAPÍTULOS ===')

# Importar serviço
try:
    from services.storyteller_service import storyteller_service
    print('✅ Storyteller Service carregado')
except Exception as e:
    print(f'❌ Erro ao carregar serviço: {e}')
    exit(1)

# Configurações do teste
titulo = 'Descalça na Entrevista, Mas o Milionário Mudou Sua Vida Para Sempre!'
premissa = '''Arthur Blackwood, um magnata da tecnologia solitário e obcecado por sucesso, vive em uma mansão imponente, mas sua vida é vazia, apesar da riqueza exorbitante. Sua entrevista para uma vaga de assistente pessoal atrai centenas de candidatos impecavelmente vestidos. Uma única exceção: Maria, uma jovem de origem humilde, descalça e com roupas simples, mas com um sorriso radiante e olhos cheios de determinação.'''

print(f'📋 Título: {titulo}')
print(f'📋 Capítulos: 3')
print(f'📋 Agente: millionaire_stories')
print(f'📋 Remove Chapter Headers: TRUE')

# Gerar roteiro COM remoção de cabeçalhos
print('\n🔄 Gerando roteiro COM remoção de cabeçalhos...')
resultado_com_remocao = storyteller_service.generate_storyteller_script(
    title=titulo,
    premise=premissa,
    agent_type='millionaire_stories',
    num_chapters=3,
    remove_chapter_headers=True  # PARÂMETRO CHAVE
)

# Gerar roteiro SEM remoção de cabeçalhos para comparação
print('\n🔄 Gerando roteiro SEM remoção de cabeçalhos (para comparação)...')
resultado_sem_remocao = storyteller_service.generate_storyteller_script(
    title=titulo,
    premise=premissa,
    agent_type='millionaire_stories',
    num_chapters=3,
    remove_chapter_headers=False  # SEM REMOÇÃO
)

# Criar pasta de teste
pasta_teste = 'teste_remocao_capitulos'
if not os.path.exists(pasta_teste):
    os.makedirs(pasta_teste)
    print(f'📁 Pasta {pasta_teste} criada')

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Salvar resultado COM remoção
if resultado_com_remocao.get('success'):
    arquivo_com_remocao = f'{pasta_teste}/roteiro_COM_remocao_{timestamp}.txt'
    with open(arquivo_com_remocao, 'w', encoding='utf-8') as f:
        f.write('=== ROTEIRO COM REMOÇÃO DE CABEÇALHOS ===\n\n')
        f.write(f'Título: {titulo}\n\n')
        f.write(f'Premissa: {premissa}\n\n')
        f.write('ROTEIRO COMPLETO:\n')
        f.write('='*80 + '\n')
        f.write(resultado_com_remocao.get('full_script', ''))
    print(f'💾 Roteiro COM remoção salvo em: {arquivo_com_remocao}')
else:
    print(f'❌ Erro na geração COM remoção: {resultado_com_remocao.get("error", "Erro desconhecido")}')

# Salvar resultado SEM remoção
if resultado_sem_remocao.get('success'):
    arquivo_sem_remocao = f'{pasta_teste}/roteiro_SEM_remocao_{timestamp}.txt'
    with open(arquivo_sem_remocao, 'w', encoding='utf-8') as f:
        f.write('=== ROTEIRO SEM REMOÇÃO DE CABEÇALHOS ===\n\n')
        f.write(f'Título: {titulo}\n\n')
        f.write(f'Premissa: {premissa}\n\n')
        f.write('ROTEIRO COMPLETO:\n')
        f.write('='*80 + '\n')
        f.write(resultado_sem_remocao.get('full_script', ''))
    print(f'💾 Roteiro SEM remoção salvo em: {arquivo_sem_remocao}')
else:
    print(f'❌ Erro na geração SEM remoção: {resultado_sem_remocao.get("error", "Erro desconhecido")}')

# Análise de cabeçalhos
print('\n📊 ANÁLISE DE CABEÇALHOS:')

def contar_cabecalhos(texto):
    """Conta cabeçalhos de capítulos no texto"""
    import re
    # Padrões de cabeçalhos
    padrao_markdown = re.findall(r'^## Capítulo \d+', texto, re.MULTILINE)
    padrao_caps = re.findall(r'^CAPÍTULO \d+:', texto, re.MULTILINE)
    return len(padrao_markdown), len(padrao_caps)

if resultado_com_remocao.get('success'):
    texto_com_remocao = resultado_com_remocao.get('full_script', '')
    md_headers, caps_headers = contar_cabecalhos(texto_com_remocao)
    print(f'   COM remoção - Cabeçalhos ## Capítulo: {md_headers}')
    print(f'   COM remoção - Cabeçalhos CAPÍTULO: {caps_headers}')
    print(f'   COM remoção - Total caracteres: {len(texto_com_remocao)}')

if resultado_sem_remocao.get('success'):
    texto_sem_remocao = resultado_sem_remocao.get('full_script', '')
    md_headers, caps_headers = contar_cabecalhos(texto_sem_remocao)
    print(f'   SEM remoção - Cabeçalhos ## Capítulo: {md_headers}')
    print(f'   SEM remoção - Cabeçalhos CAPÍTULO: {caps_headers}')
    print(f'   SEM remoção - Total caracteres: {len(texto_sem_remocao)}')

# Relatório final
arquivo_relatorio = f'{pasta_teste}/relatorio_teste_remocao_{timestamp}.txt'
with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
    f.write('=== RELATÓRIO DE TESTE - REMOÇÃO DE CABEÇALHOS ===\n\n')
    f.write(f'Data/Hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
    
    f.write('CONFIGURAÇÃO DO TESTE:\n')
    f.write(f'- Título: {titulo}\n')
    f.write(f'- Capítulos: 3\n')
    f.write(f'- Agente: millionaire_stories\n\n')
    
    f.write('RESULTADOS:\n')
    if resultado_com_remocao.get('success'):
        texto = resultado_com_remocao.get('full_script', '')
        md_h, caps_h = contar_cabecalhos(texto)
        f.write(f'✅ COM remoção (remove_chapter_headers=True):\n')
        f.write(f'   - Cabeçalhos ## Capítulo: {md_h}\n')
        f.write(f'   - Cabeçalhos CAPÍTULO: {caps_h}\n')
        f.write(f'   - Total caracteres: {len(texto)}\n')
        f.write(f'   - Status: {"✅ SUCESSO - SEM CABEÇALHOS" if md_h == 0 else "❌ FALHA - CABEÇALHOS PRESENTES"}\n\n')
    else:
        f.write(f'❌ COM remoção: FALHA - {resultado_com_remocao.get("error", "Erro desconhecido")}\n\n')
    
    if resultado_sem_remocao.get('success'):
        texto = resultado_sem_remocao.get('full_script', '')
        md_h, caps_h = contar_cabecalhos(texto)
        f.write(f'✅ SEM remoção (remove_chapter_headers=False):\n')
        f.write(f'   - Cabeçalhos ## Capítulo: {md_h}\n')
        f.write(f'   - Cabeçalhos CAPÍTULO: {caps_h}\n')
        f.write(f'   - Total caracteres: {len(texto)}\n')
        f.write(f'   - Status: {"✅ ESPERADO - COM CABEÇALHOS" if md_h > 0 else "⚠️ INESPERADO - SEM CABEÇALHOS"}\n\n')
    else:
        f.write(f'❌ SEM remoção: FALHA - {resultado_sem_remocao.get("error", "Erro desconhecido")}\n\n')
    
    # Conclusão
    if (resultado_com_remocao.get('success') and resultado_sem_remocao.get('success')):
        com_headers = contar_cabecalhos(resultado_com_remocao.get('full_script', ''))[0]
        sem_headers = contar_cabecalhos(resultado_sem_remocao.get('full_script', ''))[0]
        
        if com_headers == 0 and sem_headers > 0:
            f.write('🎉 CONCLUSÃO: REMOÇÃO DE CABEÇALHOS FUNCIONANDO CORRETAMENTE!\n')
        elif com_headers == 0 and sem_headers == 0:
            f.write('⚠️ CONCLUSÃO: AMBOS SEM CABEÇALHOS - VERIFICAR IMPLEMENTAÇÃO\n')
        elif com_headers > 0:
            f.write('❌ CONCLUSÃO: REMOÇÃO DE CABEÇALHOS NÃO ESTÁ FUNCIONANDO\n')
        else:
            f.write('❓ CONCLUSÃO: RESULTADO INESPERADO - VERIFICAR MANUALMENTE\n')
    else:
        f.write('❌ CONCLUSÃO: FALHA NA GERAÇÃO - NÃO FOI POSSÍVEL TESTAR\n')

print(f'📊 Relatório completo salvo em: {arquivo_relatorio}')
print('\n✅ TESTE CONCLUÍDO!')
print(f'📁 Todos os arquivos salvos em: {pasta_teste}/')