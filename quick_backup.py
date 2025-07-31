#!/usr/bin/env python3
"""
⚡ Backup Rápido
Auto Video Producer - Backup rápido para desenvolvimento
"""

import os
import shutil
import zipfile
import datetime
from pathlib import Path

def quick_backup():
    """Criar backup rápido do projeto"""
    project_root = Path(__file__).parent
    backup_dir = project_root.parent / "BACKUPS" / "auto-video-producer" / "quick"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"quick_backup_{timestamp}.zip"
    backup_path = backup_dir / backup_name
    
    print(f"⚡ Criando backup rápido...")
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Incluir apenas arquivos essenciais
        essential_files = [
            "backend/app.py",
            "backend/routes/*.py",
            "backend/services/*.py",
            "backend/requirements.txt",
            "frontend/src/**/*.jsx",
            "frontend/src/**/*.js",
            "frontend/src/**/*.css",
            "frontend/package.json",
            "frontend/vite.config.js",
            "start.py",
            "README.md"
        ]
        
        for pattern in essential_files:
            if '*' in pattern:
                # Usar glob para padrões
                for file_path in project_root.glob(pattern):
                    if file_path.is_file():
                        arcname = file_path.relative_to(project_root)
                        zipf.write(file_path, arcname)
            else:
                # Arquivo específico
                file_path = project_root / pattern
                if file_path.exists():
                    arcname = file_path.relative_to(project_root)
                    zipf.write(file_path, arcname)
    
    size_mb = backup_path.stat().st_size / 1024 / 1024
    print(f"✅ Backup rápido criado: {backup_name} ({size_mb:.2f} MB)")
    
    # Manter apenas os 10 backups mais recentes
    quick_backups = list(backup_dir.glob("quick_backup_*.zip"))
    quick_backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for old_backup in quick_backups[10:]:
        old_backup.unlink()
        print(f"🗑️ Removido backup antigo: {old_backup.name}")
    
    return backup_path

if __name__ == "__main__":
    try:
        backup_file = quick_backup()
        print(f"🎯 Backup salvo em: {backup_file}")
    except Exception as e:
        print(f"❌ Erro no backup: {e}")
