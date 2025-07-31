#!/usr/bin/env python3
"""
🔄 Sistema de Backup Automatizado
Auto Video Producer - Sistema completo de backup
"""

import os
import shutil
import zipfile
import datetime
import json
import subprocess
import sys
from pathlib import Path

class BackupSystem:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backup_dir = self.project_root.parent / "BACKUPS" / "auto-video-producer"
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def create_backup_directory(self):
        """Criar diretório de backup se não existir"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Diretório de backup: {self.backup_dir}")
        
    def backup_source_code(self):
        """Backup completo do código fonte"""
        print("📦 Criando backup do código fonte...")
        
        backup_name = f"auto-video-producer_SOURCE_{self.timestamp}.zip"
        backup_path = self.backup_dir / backup_name
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.project_root):
                # Ignorar diretórios desnecessários
                dirs[:] = [d for d in dirs if d not in [
                    'node_modules', '__pycache__', '.git', 'venv', 'env',
                    '.vscode', '.idea', 'dist', 'build'
                ]]
                
                for file in files:
                    # Ignorar arquivos desnecessários
                    if file.endswith(('.pyc', '.log', '.tmp', '.temp')):
                        continue
                    if file in ['api_keys.json', '.env']:
                        continue
                        
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.project_root)
                    zipf.write(file_path, arcname)
                    
        print(f"✅ Backup do código criado: {backup_name}")
        return backup_path
        
    def backup_database(self):
        """Backup do banco de dados"""
        print("🗄️ Criando backup do banco de dados...")
        
        db_files = [
            self.project_root / "backend" / "app.db",
            self.project_root / "backend" / "database.db",
            self.project_root / "backend" / "instance" / "app.db"
        ]
        
        backup_name = f"auto-video-producer_DATABASE_{self.timestamp}.zip"
        backup_path = self.backup_dir / backup_name
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for db_file in db_files:
                if db_file.exists():
                    zipf.write(db_file, db_file.name)
                    print(f"  📄 Incluído: {db_file.name}")
                    
        print(f"✅ Backup do banco criado: {backup_name}")
        return backup_path
        
    def backup_config(self):
        """Backup das configurações (sem chaves sensíveis)"""
        print("⚙️ Criando backup das configurações...")
        
        config_backup = {
            "timestamp": self.timestamp,
            "project_structure": self.get_project_structure(),
            "dependencies": self.get_dependencies(),
            "git_info": self.get_git_info()
        }
        
        backup_name = f"auto-video-producer_CONFIG_{self.timestamp}.json"
        backup_path = self.backup_dir / backup_name
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(config_backup, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Backup de configuração criado: {backup_name}")
        return backup_path
        
    def get_project_structure(self):
        """Obter estrutura do projeto"""
        structure = {}
        for root, dirs, files in os.walk(self.project_root):
            # Ignorar diretórios desnecessários
            dirs[:] = [d for d in dirs if d not in [
                'node_modules', '__pycache__', '.git', 'venv', 'env'
            ]]
            
            rel_path = Path(root).relative_to(self.project_root)
            structure[str(rel_path)] = {
                "directories": dirs,
                "files": [f for f in files if not f.endswith(('.pyc', '.log'))]
            }
        return structure
        
    def get_dependencies(self):
        """Obter informações das dependências"""
        deps = {}
        
        # Python dependencies
        requirements_file = self.project_root / "backend" / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                deps["python"] = f.read().splitlines()
                
        # Node.js dependencies
        package_json = self.project_root / "frontend" / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                package_data = json.load(f)
                deps["nodejs"] = {
                    "dependencies": package_data.get("dependencies", {}),
                    "devDependencies": package_data.get("devDependencies", {})
                }
                
        return deps
        
    def get_git_info(self):
        """Obter informações do Git"""
        try:
            # Obter commit atual
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            current_commit = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            # Obter branch atual
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            current_branch = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            # Obter remote URL
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            remote_url = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            return {
                "commit": current_commit,
                "branch": current_branch,
                "remote": remote_url
            }
        except:
            return {"error": "Git information not available"}
            
    def create_full_backup(self):
        """Criar backup completo"""
        print("🔄 Iniciando backup completo...")
        print("=" * 60)
        
        self.create_backup_directory()
        
        backups_created = []
        
        # Backup do código fonte
        source_backup = self.backup_source_code()
        backups_created.append(source_backup)
        
        # Backup do banco de dados
        db_backup = self.backup_database()
        backups_created.append(db_backup)
        
        # Backup das configurações
        config_backup = self.backup_config()
        backups_created.append(config_backup)
        
        # Criar backup consolidado
        consolidated_backup = self.create_consolidated_backup(backups_created)
        
        print("=" * 60)
        print("🎉 BACKUP COMPLETO CRIADO COM SUCESSO!")
        print(f"📁 Localização: {self.backup_dir}")
        print(f"📦 Backup consolidado: {consolidated_backup.name}")
        print(f"⏰ Timestamp: {self.timestamp}")
        
        return consolidated_backup
        
    def create_consolidated_backup(self, backup_files):
        """Criar um backup consolidado com todos os arquivos"""
        print("📦 Criando backup consolidado...")
        
        consolidated_name = f"auto-video-producer_FULL_BACKUP_{self.timestamp}.zip"
        consolidated_path = self.backup_dir / consolidated_name
        
        with zipfile.ZipFile(consolidated_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for backup_file in backup_files:
                if backup_file.exists():
                    zipf.write(backup_file, backup_file.name)
                    
            # Adicionar README do backup
            readme_content = self.create_backup_readme()
            zipf.writestr("BACKUP_README.txt", readme_content)
            
        print(f"✅ Backup consolidado criado: {consolidated_name}")
        return consolidated_path
        
    def create_backup_readme(self):
        """Criar README para o backup"""
        return f"""
🔄 AUTO VIDEO PRODUCER - BACKUP COMPLETO
========================================

📅 Data do Backup: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
🏷️ Timestamp: {self.timestamp}

📦 CONTEÚDO DO BACKUP:
- auto-video-producer_SOURCE_{self.timestamp}.zip (Código fonte completo)
- auto-video-producer_DATABASE_{self.timestamp}.zip (Banco de dados)
- auto-video-producer_CONFIG_{self.timestamp}.json (Configurações)

🔧 COMO RESTAURAR:
1. Extrair o arquivo auto-video-producer_SOURCE_{self.timestamp}.zip
2. Instalar dependências:
   - Backend: pip install -r backend/requirements.txt
   - Frontend: cd frontend && npm install
3. Restaurar banco de dados (se necessário)
4. Configurar chaves de API
5. Executar: python start.py

🌐 REPOSITÓRIO GITHUB:
https://github.com/Ender-ss/auto-video-producer.git

⚠️ IMPORTANTE:
- Este backup NÃO inclui chaves de API por segurança
- Configure novamente as chaves em backend/config/api_keys.json
- Verifique se todas as dependências estão instaladas

✅ SISTEMA FUNCIONANDO NO MOMENTO DO BACKUP:
- Extração de títulos do YouTube ✅
- Interface React + Tailwind ✅
- Backend Flask ✅
- RapidAPI YouTube V2 ✅
"""

def main():
    """Função principal"""
    print("🔄 AUTO VIDEO PRODUCER - SISTEMA DE BACKUP")
    print("=" * 50)
    
    backup_system = BackupSystem()
    
    try:
        backup_file = backup_system.create_full_backup()
        
        print("\n🎯 BACKUP CONCLUÍDO!")
        print(f"📁 Arquivo: {backup_file}")
        print(f"📊 Tamanho: {backup_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Listar todos os backups existentes
        print("\n📋 BACKUPS DISPONÍVEIS:")
        backup_files = list(backup_system.backup_dir.glob("*.zip"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for i, backup in enumerate(backup_files[:5], 1):
            size_mb = backup.stat().st_size / 1024 / 1024
            mtime = datetime.datetime.fromtimestamp(backup.stat().st_mtime)
            print(f"  {i}. {backup.name} ({size_mb:.2f} MB) - {mtime.strftime('%d/%m/%Y %H:%M')}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o backup: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
