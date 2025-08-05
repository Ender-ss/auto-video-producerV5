#!/usr/bin/env python3
"""
Auto Video Producer - Startup Script
Script para inicializar o sistema completo
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def print_banner():
    """Exibir banner do sistema"""
    banner = """
    ================================================================
    |                                                              |
    |                  AUTO VIDEO PRODUCER                         |
    |                                                              |
    |          Sistema Completo de Producao Automatica             |
    |                    de Videos com IA                          |
    |                                                              |
    |                      Versao 1.0.0                            |
    |                                                              |
    ================================================================
    """
    print(banner)

def check_python_version():
    """Verificar versão do Python"""
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8+ é necessário!")
        sys.exit(1)
    print(f"[OK] Python {sys.version.split()[0]} detectado")

def check_node_version():
    """Verificar se Node.js está instalado"""
    is_windows = sys.platform.startswith('win')
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=is_windows)
        if result.returncode == 0:
            print(f"[OK] Node.js {result.stdout.strip()} detectado")
            return True
        else:
            print("[ERROR] Node.js não encontrado!")
            return False
    except FileNotFoundError:
        print("[ERROR] Node.js não encontrado!")
        return False

def install_backend_dependencies():
    """Instalar dependências do backend"""
    print("\n[INFO] Instalando dependências do backend...")
    
    backend_dir = Path(__file__).parent / "backend"
    requirements_file = backend_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print("[ERROR] Arquivo requirements.txt não encontrado!")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, cwd=backend_dir)
        print("[OK] Dependências do backend instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] Erro ao instalar dependências do backend!")
        return False

def install_frontend_dependencies():
    """Instalar dependências do frontend"""
    print("\n[INFO] Instalando dependências do frontend...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    is_windows = sys.platform.startswith('win')

    if not frontend_dir.exists():
        print("[ERROR] Diretório frontend não encontrado!")
        return False
    
    try:
        subprocess.run(["npm", "install"], check=True, cwd=frontend_dir, shell=is_windows)
        print("[OK] Dependências do frontend instaladas com sucesso!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] Erro ao instalar dependências do frontend!")
        return False

def start_backend():
    """Iniciar servidor backend"""
    print("\n[INFO] Iniciando servidor backend...")
    
    backend_dir = Path(__file__).parent / "backend"
    app_file = backend_dir / "app.py"
    
    if not app_file.exists():
        print("[ERROR] Arquivo app.py não encontrado!")
        return None
    
    try:
        process = subprocess.Popen([
            sys.executable, str(app_file)
        ], cwd=backend_dir)
        
        time.sleep(3)
        
        if process.poll() is None:
            print("[OK] Servidor backend iniciado com sucesso!")
            print("[INFO] Backend disponível em: http://localhost:5000")
            return process
        else:
            print("[ERROR] Erro ao iniciar servidor backend!")
            return None
    except Exception as e:
        print(f"[ERROR] Erro ao iniciar backend: {e}")
        return None

def start_frontend():
    """Iniciar servidor frontend"""
    print("\n[INFO] Iniciando servidor frontend...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    is_windows = sys.platform.startswith('win')
    
    try:
        process = subprocess.Popen(
            ["npm", "run", "dev"], cwd=frontend_dir, shell=is_windows
        )
        
        time.sleep(5)
        
        if process.poll() is None:
            print("[OK] Servidor frontend iniciado com sucesso!")
            print("[INFO] Frontend disponível em: http://localhost:5173")
            return process
        else:
            print("[ERROR] Erro ao iniciar servidor frontend!")
            return None
    except Exception as e:
        print(f"[ERROR] Erro ao iniciar frontend: {e}")
        return None

def create_directories():
    """Criar diretórios necessários"""
    print("\n[INFO] Criando diretórios necessários...")
    
    directories = [
        "backend/uploads",
        "backend/outputs",
        "backend/temp",
        "backend/logs"
    ]
    
    for directory in directories:
        dir_path = Path(__file__).parent / directory
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("[OK] Diretórios criados com sucesso!")

def show_next_steps():
    """Mostrar próximos passos"""
    next_steps = """
    
    SISTEMA INICIADO COM SUCESSO!
    
    PROXIMOS PASSOS:
    
    1. Acesse a interface web em: http://localhost:5173
    
    2. Configure suas APIs na página "Configurações":
       - OpenAI (para geração de títulos e roteiros)
       - Google Gemini (alternativa gratuita)
       - RapidAPI YouTube V2 (para extração de conteúdo)
       - ElevenLabs (para text-to-speech)
    
    3. Adicione canais para monitoramento na página "Canais"
    
    4. Teste as automações na página "Automações":
       - Extração de conteúdo do YouTube
       - Geração de títulos virais
       - Criação de roteiros com IA
       - Geração de premissas narrativas
    
    5. Execute pipelines completos na página "Pipeline"
    
    DOCUMENTAÇÃO:
    - README.md - Guia completo de uso
    - /api/docs - Documentação da API
    
    SUPORTE:
    - Verifique os logs em caso de erro
    - Backend: http://localhost:5000
    - Frontend: http://localhost:5173
    
    IMPORTANTE:
    - Mantenha ambos os terminais abertos
    - Configure suas chaves de API antes de usar
    - Teste as conexões na página de configurações
    
    """
    print(next_steps)

def main():
    """Função principal"""
    print_banner()
    
    check_python_version()
    
    if not check_node_version():
        print("\n[ERROR] Node.js é necessário para o frontend!")
        print("Baixe em: https://nodejs.org/")
        sys.exit(1)
    
    create_directories()
    
    if not install_backend_dependencies():
        sys.exit(1)
    
    if not install_frontend_dependencies():
        sys.exit(1)
    
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)
    
    show_next_steps()
    
    try:
        print("[INFO] Sistema rodando... Pressione Ctrl+C para parar")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Parando sistema...")
        
        if backend_process:
            backend_process.terminate()
            print("[OK] Backend parado")
        
        if frontend_process:
            frontend_process.terminate()
            print("[OK] Frontend parado")
        
        print("[INFO] Sistema parado com sucesso!")

if __name__ == "__main__":
    main()