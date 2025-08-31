#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import fileinput
import shutil

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Script para atualizar automaticamente o limite de quota do Gemini de 8 para 40

def backup_file(file_path):
    """Criar backup de um arquivo antes de modificá-lo"""
    backup_path = file_path + '.backup'
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        print(f"🔐 Backup criado: {backup_path}")
    return backup_path


def replace_quota_limit(file_path, old_limit=8, new_limit=40):
    """Substituir todas as ocorrências do limite de quota em um arquivo"""
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False
    
    # Criar backup
    backup_file(file_path)
    
    # Mapeamento de padrões específicos para evitar alterar números que não são do limite de quota
    patterns_to_replace = [
        # Padrões exatos para procurar
        f"if GEMINI_KEYS_ROTATION['usage_count'].get(key, 0) < {old_limit}:",
        f"if usage < {old_limit}:  # Limite de {old_limit} por chave",
        f"GEMINI_KEYS_ROTATION['usage_count'][gemini_2_key] = {old_limit}",
        f"'usage_limit': {old_limit},",
        f"key_limit = {old_limit}",
        f"if usage >= {old_limit}:",
        f"if usage < {old_limit}:"
    ]
    
    # Contador de substituições
    replacements = 0
    
    try:
        # Ler todo o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Fazer as substituições para cada padrão
        for pattern in patterns_to_replace:
            if pattern in content:
                content = content.replace(pattern, pattern.replace(str(old_limit), str(new_limit)))
                replacements += 1
                print(f"✅ Substituído no arquivo {os.path.basename(file_path)}: '{pattern}'")
        
        # Escrever o conteúdo modificado de volta
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Se não houve substituições usando os padrões exatos, procurar por números soltos
        if replacements == 0:
            print(f"🔍 Procurando por valores numéricos soltos de '{old_limit}' no arquivo {os.path.basename(file_path)}...")
            
            # Seguir um padrão mais abrangente mas com cautela
            lines = content.split('\n')
            for i, line in enumerate(lines):
                # Ignorar linhas que contêm datas, contagens de versão ou números que não sejam do limite
                if '#' in line and ('limite' in line.lower() or 'quota' in line.lower() or 'usage' in line.lower()):
                    if str(old_limit) in line:
                        lines[i] = line.replace(str(old_limit), str(new_limit))
                        replacements += 1
                        print(f"✅ Substituído linha {i+1} no arquivo {os.path.basename(file_path)}: '{line.strip()}'")
            
            # Escrever de volta se houver substituições
            if replacements > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
        
        if replacements > 0:
            print(f"✅ Concluído: {replacements} substituições feitas no arquivo {os.path.basename(file_path)}")
        else:
            print(f"ℹ️  Nenhuma substituição necessária no arquivo {os.path.basename(file_path)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao modificar o arquivo {file_path}: {str(e)}")
        return False


def main():
    print("==== ATUALIZAÇÃO DO LIMITE DE QUOTA GEMINI ====")
    print("\nEste script irá:")
    print(f"1. Criar backups de todos os arquivos alterados")
    print(f"2. Substituir o limite de {old_limit} para {new_limit} requisições por chave Gemini")
    print(f"3. Atualizar todos os pontos no sistema que controlam a quota")
    
    # Arquivos a serem alterados
    files_to_update = [
        os.path.join(os.path.dirname(__file__), 'routes', 'automations.py'),
        os.path.join(os.path.dirname(__file__), 'fix_gemini_key_quota.py'),
        os.path.join(os.path.dirname(__file__), 'routes', 'settings.py'),
        os.path.join(os.path.dirname(__file__), 'check_gemini_keys_status.py')
    ]
    
    # Executar a substituição em cada arquivo
    success_count = 0
    for file_path in files_to_update:
        print(f"\n🔄 Processando arquivo: {os.path.basename(file_path)}")
        if replace_quota_limit(file_path, old_limit, new_limit):
            success_count += 1
    
    print(f"\n📊 RESULTADO:")
    print(f"- {success_count} arquivos atualizados com sucesso")
    print(f"- {len(files_to_update) - success_count} arquivos não puderam ser atualizados")
    
    if success_count > 0:
        print("\n✅ PROCEDIMENTO CONCLUÍDO!")
        print(f"\n💡 AGORA O SISTEMA ESTÁ CONFIGURADO PARA:")
        print(f"- Limite de {new_limit} requisições por chave Gemini por dia")
        print(f"- Mais tentativas reais com cada chave")
        print(f"- Menos falhas de pipeline devido a quota esgotada")
        print("\n⚠️  PRÓXIMOS PASSOS:")
        print("1. Reinicie o backend: python app.py")
        print("2. Verifique se o limite foi atualizado executando: python check_gemini_keys_status.py")
        print("3. Os backups dos arquivos originais estão disponíveis com extensão .backup")
    else:
        print("\n❌ NENHUMA ALTERAÇÃO FOI FEITA!")
        print("- Verifique se os arquivos estão corretos")
        print("- Tente alterar manualmente usando as indicações do script change_gemini_quota_limit.py")
    
    print("\n=============================================")

if __name__ == "__main__":
    # Defina os limites aqui
    old_limit = 8
    new_limit = 40
    main()