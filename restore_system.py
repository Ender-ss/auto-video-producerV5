#!/usr/bin/env python3
"""
🔄 Sistema de Restauração de Backup
Auto Video Producer - Restaurar projeto a partir de backup
"""

import os
import shutil
import zipfile
import json
import subprocess
import sys
from pathlib import Path

class RestoreSystem:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backup_dir = self.project_root.parent / "BACKUPS" / "auto-video-producer"
        
    def list_available_backups(self):
        """Listar backups disponíveis"""
        if not self.backup_dir.exists():
            print("❌ Diretório de backup não encontrado!")
            return []
            
        backup_files = list(self.backup_dir.glob("*_FULL_BACKUP_*.zip"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print("📋 BACKUPS DISPONÍVEIS:")
        print("=" * 60)
        
        for i, backup in enumerate(backup_files, 1):
            size_mb = backup.stat().st_size / 1024 / 1024
            mtime = backup.stat().st_mtime
            date_str = Path(backup).stem.split('_')[-2] + '_' + Path(backup).stem.split('_')[-1]
            
            print(f"{i}. {backup.name}")
            print(f"   📅 Data: {date_str}")
            print(f"   📊 Tamanho: {size_mb:.2f} MB")
            print()
            
        return backup_files
        
    def restore_from_backup(self, backup_file):
        """Restaurar projeto a partir de backup"""
        print(f"🔄 Restaurando a partir de: {backup_file.name}")
        print("=" * 60)
        
        # Criar diretório temporário para extração
        temp_dir = self.project_root / "temp_restore"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Extrair backup consolidado
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(temp_dir)
                
            # Restaurar código fonte
            source_backup = None
            for file in temp_dir.glob("*_SOURCE_*.zip"):
                source_backup = file
                break
                
            if source_backup:
                print("📦 Restaurando código fonte...")
                self.restore_source_code(source_backup)
            else:
                print("⚠️ Backup do código fonte não encontrado!")
                
            # Restaurar banco de dados
            db_backup = None
            for file in temp_dir.glob("*_DATABASE_*.zip"):
                db_backup = file
                break
                
            if db_backup:
                print("🗄️ Restaurando banco de dados...")
                self.restore_database(db_backup)
            else:
                print("⚠️ Backup do banco de dados não encontrado!")
                
            # Mostrar informações de configuração
            config_backup = None
            for file in temp_dir.glob("*_CONFIG_*.json"):
                config_backup = file
                break
                
            if config_backup:
                print("⚙️ Carregando informações de configuração...")
                self.show_config_info(config_backup)
                
            print("✅ Restauração concluída!")
            
        finally:
            # Limpar diretório temporário
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                
    def restore_source_code(self, source_backup):
        """Restaurar código fonte"""
        # Fazer backup do projeto atual (se existir)
        if (self.project_root / "backend").exists():
            backup_current = self.project_root / f"backup_current_{int(os.time())}"
            print(f"📁 Fazendo backup do projeto atual em: {backup_current.name}")
            shutil.copytree(self.project_root, backup_current, ignore=shutil.ignore_patterns(
                'node_modules', '__pycache__', '.git', 'venv', 'env', 'temp_*', 'backup_*'
            ))
            
        # Extrair código fonte
        with zipfile.ZipFile(source_backup, 'r') as zipf:
            zipf.extractall(self.project_root)
            
        print("✅ Código fonte restaurado!")
        
    def restore_database(self, db_backup):
        """Restaurar banco de dados"""
        backend_dir = self.project_root / "backend"
        
        with zipfile.ZipFile(db_backup, 'r') as zipf:
            for file_info in zipf.filelist:
                if file_info.filename.endswith('.db'):
                    # Extrair para o diretório backend
                    zipf.extract(file_info, backend_dir)
                    print(f"  📄 Restaurado: {file_info.filename}")
                    
        print("✅ Banco de dados restaurado!")
        
    def show_config_info(self, config_backup):
        """Mostrar informações de configuração"""
        with open(config_backup, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        print("📋 INFORMAÇÕES DO BACKUP:")
        print(f"  📅 Timestamp: {config.get('timestamp', 'N/A')}")
        
        if 'git_info' in config:
            git_info = config['git_info']
            print(f"  🌐 Branch: {git_info.get('branch', 'N/A')}")
            print(f"  📝 Commit: {git_info.get('commit', 'N/A')[:8]}...")
            print(f"  🔗 Remote: {git_info.get('remote', 'N/A')}")
            
        if 'dependencies' in config:
            deps = config['dependencies']
            if 'python' in deps:
                print(f"  🐍 Python packages: {len(deps['python'])}")
            if 'nodejs' in deps:
                node_deps = deps['nodejs'].get('dependencies', {})
                print(f"  📦 Node.js packages: {len(node_deps)}")
                
    def setup_environment(self):
        """Configurar ambiente após restauração"""
        print("🔧 CONFIGURANDO AMBIENTE...")
        print("=" * 60)
        
        # Instalar dependências Python
        requirements_file = self.project_root / "backend" / "requirements.txt"
        if requirements_file.exists():
            print("🐍 Instalando dependências Python...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True)
                print("✅ Dependências Python instaladas!")
            except subprocess.CalledProcessError:
                print("⚠️ Erro ao instalar dependências Python. Execute manualmente:")
                print(f"   pip install -r {requirements_file}")
                
        # Instalar dependências Node.js
        package_json = self.project_root / "frontend" / "package.json"
        if package_json.exists():
            print("📦 Instalando dependências Node.js...")
            try:
                subprocess.run([
                    "npm", "install"
                ], cwd=self.project_root / "frontend", check=True)
                print("✅ Dependências Node.js instaladas!")
            except subprocess.CalledProcessError:
                print("⚠️ Erro ao instalar dependências Node.js. Execute manualmente:")
                print(f"   cd frontend && npm install")
                
        # Criar arquivo de configuração de API (vazio)
        api_config_dir = self.project_root / "backend" / "config"
        api_config_dir.mkdir(exist_ok=True)
        
        api_keys_file = api_config_dir / "api_keys.json"
        if not api_keys_file.exists():
            default_config = {
                "rapidapi": "",
                "openai": "",
                "note": "Configure suas chaves de API aqui"
            }
            with open(api_keys_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print("⚙️ Arquivo de configuração de API criado (configure suas chaves)")
            
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Configure suas chaves de API em: backend/config/api_keys.json")
        print("2. Execute o sistema: python start.py")
        print("3. Acesse: http://localhost:5173")

def main():
    """Função principal"""
    print("🔄 AUTO VIDEO PRODUCER - SISTEMA DE RESTAURAÇÃO")
    print("=" * 60)
    
    restore_system = RestoreSystem()
    
    # Listar backups disponíveis
    backups = restore_system.list_available_backups()
    
    if not backups:
        print("❌ Nenhum backup encontrado!")
        return False
        
    # Solicitar seleção do backup
    try:
        choice = input("\n🔢 Digite o número do backup para restaurar (ou 'q' para sair): ").strip()
        
        if choice.lower() == 'q':
            print("👋 Operação cancelada.")
            return True
            
        backup_index = int(choice) - 1
        
        if 0 <= backup_index < len(backups):
            selected_backup = backups[backup_index]
            
            # Confirmar restauração
            confirm = input(f"\n⚠️ Confirma a restauração de '{selected_backup.name}'? (s/N): ").strip().lower()
            
            if confirm in ['s', 'sim', 'y', 'yes']:
                restore_system.restore_from_backup(selected_backup)
                
                # Perguntar se quer configurar ambiente
                setup = input("\n🔧 Deseja configurar o ambiente automaticamente? (S/n): ").strip().lower()
                
                if setup not in ['n', 'no', 'não']:
                    restore_system.setup_environment()
                    
                print("\n🎉 RESTAURAÇÃO CONCLUÍDA COM SUCESSO!")
                return True
            else:
                print("👋 Operação cancelada.")
                return True
        else:
            print("❌ Número inválido!")
            return False
            
    except ValueError:
        print("❌ Entrada inválida!")
        return False
    except KeyboardInterrupt:
        print("\n👋 Operação cancelada pelo usuário.")
        return True
    except Exception as e:
        print(f"❌ Erro durante a restauração: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
