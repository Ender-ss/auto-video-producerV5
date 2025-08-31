#!/usr/bin/env python3
"""
🧹 SCRIPT PARA LIMPAR DIRETÓRIOS TEMPORÁRIOS DO SISTEMA
=====================================

Este script limpa diretórios temporários que podem conter
referências ao nome "Arthur Blackwood" ou outros dados problemáticos.
"""

import os
import shutil
import json
from pathlib import Path

def clear_directory_contents(directory):
    """Limpa todos os arquivos e subdiretórios de um diretório"""
    if not os.path.exists(directory):
        print(f"✅ Diretório não existe: {directory}")
        return True
    
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
                print(f"🗑️  Arquivo removido: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"🗑️  Diretório removido: {item_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao limpar diretório {directory}: {e}")
        return False

def main():
    print("🧹 LIMPANDO DIRETÓRIOS TEMPORÁRIOS DO SISTEMA")
    print("=" * 50)
    
    # Diretórios para limpar
    directories_to_clear = [
        "cache",
        "temp",
        "outputs",
        "backend/cache",
        "backend/temp",
        "backend/outputs",
        "backend/checkpoints",
        "checkpoints",
        ".trae"
    ]
    
    success_count = 0
    total_count = len(directories_to_clear)
    
    for directory in directories_to_clear:
        print(f"\n🔍 Limpando diretório: {directory}")
        if clear_directory_contents(directory):
            success_count += 1
            print(f"✅ Diretório limpo: {directory}")
        else:
            print(f"❌ Falha ao limpar diretório: {directory}")
    
    print(f"\n📊 RESULTADO:")
    print(f"   Diretórios processados: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✅ Todos os diretórios foram limpos com sucesso!")
    else:
        print("⚠️  Alguns diretórios não puderam ser limpos")
    
    print("\n🔄 Reinicie o sistema para garantir que todas as alterações tenham efeito.")

if __name__ == "__main__":
    main()