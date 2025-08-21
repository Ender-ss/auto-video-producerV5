"""
🔧 System Routes
Sistema de logs e monitoramento
"""

from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime
import logging
import time
import threading
from collections import deque

system_bp = Blueprint('system', __name__)

# Sistema de logs em tempo real
real_time_logs = deque(maxlen=1000)  # Manter últimos 1000 logs
log_lock = threading.Lock()

# Configurar logging
LOG_FILE = 'logs/system.log'
os.makedirs('logs', exist_ok=True)

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.propagate = True
logger.setLevel(logging.INFO)

def add_real_time_log(message, level="info", source="system"):
    """Adicionar log ao sistema em tempo real"""
    with log_lock:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level.lower(),
            'message': message,
            'source': source,
            'unix_timestamp': time.time()
        }
        real_time_logs.append(log_entry)

        # Também logar no sistema tradicional
        if level.lower() == 'error':
            logger.error(f"[{source}] {message}")
        elif level.lower() == 'warning':
            logger.warning(f"[{source}] {message}")
        elif level.lower() == 'success':
            logger.info(f"[{source}] [SUCCESS] {message}")
        else:
            logger.info(f"[{source}] {message}")

# ================================
# 📋 LOGS
# ================================

@system_bp.route('/logs', methods=['GET'])
def get_logs():
    """Obter logs do sistema em tempo real"""
    try:
        since = request.args.get('since', type=float, default=0)

        with log_lock:
            # Filtrar logs desde o timestamp especificado
            if since > 0:
                filtered_logs = [
                    log for log in real_time_logs
                    if log['unix_timestamp'] > since
                ]
            else:
                # Se não especificou 'since', retornar todos os logs
                filtered_logs = list(real_time_logs)

        # Ordenar por timestamp (mais recentes primeiro)
        filtered_logs.sort(key=lambda x: x['unix_timestamp'], reverse=True)

        return jsonify({
            'success': True,
            'data': {
                'logs': filtered_logs,
                'total': len(filtered_logs),
                'server_time': time.time()
            }
        })

    except Exception as e:
        add_real_time_log(f"Erro ao obter logs: {str(e)}", "error", "system")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/logs', methods=['DELETE'])
def clear_logs():
    """Limpar logs do sistema"""
    try:
        with log_lock:
            real_time_logs.clear()

        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w') as f:
                f.write('')

        add_real_time_log("Logs limpos pelo usuário", "info", "system")

        return jsonify({
            'success': True,
            'message': 'Logs limpos com sucesso'
        })

    except Exception as e:
        add_real_time_log(f"Erro ao limpar logs: {str(e)}", "error", "system")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/log', methods=['POST'])
def add_log():
    """Adicionar entrada de log"""
    try:
        data = request.get_json()
        level = data.get('level', 'info')
        message = data.get('message', '')
        source = data.get('source', 'frontend')

        # Adicionar ao sistema de logs em tempo real
        add_real_time_log(message, level, source)

        return jsonify({
            'success': True,
            'message': 'Log adicionado'
        })

    except Exception as e:
        add_real_time_log(f"Erro ao adicionar log: {str(e)}", "error", "system")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# ⚙️ CONFIGURAÇÕES
# ================================

SETTINGS_FILE = 'config/settings.json'
os.makedirs('config', exist_ok=True)

@system_bp.route('/settings', methods=['GET'])
def get_settings():
    """Obter configurações do sistema"""
    try:
        settings = {}
        
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        
        return jsonify({
            'success': True,
            'data': settings
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter configurações: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/settings', methods=['POST'])
def save_settings():
    """Salvar configurações do sistema"""
    try:
        data = request.get_json()
        
        # Salvar configurações
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info("Configurações salvas")
        
        return jsonify({
            'success': True,
            'message': 'Configurações salvas com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao salvar configurações: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# 📊 STATUS DO SISTEMA
# ================================

@system_bp.route('/status', methods=['GET'])
def get_system_status():
    """Obter status do sistema"""
    try:
        import psutil
        import platform
        
        # Informações do sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = {
            'system': {
                'platform': platform.system(),
                'python_version': platform.python_version(),
                'uptime': datetime.now().isoformat()
            },
            'resources': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used': memory.used,
                'memory_total': memory.total,
                'disk_percent': disk.percent,
                'disk_used': disk.used,
                'disk_total': disk.total
            },
            'services': {
                'backend': 'running',
                'logs': 'active' if os.path.exists(LOG_FILE) else 'inactive'
            }
        }
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# 🧪 HEALTH CHECK
# ================================

@system_bp.route('/health', methods=['GET'])
def health_check():
    """Health check do sistema"""
    try:
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'message': 'Sistema funcionando normalmente'
        })
        
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# Adicionar ao final do arquivo system.py

@system_bp.route('/files/validate', methods=['POST'])
def validate_file():
    """Validar se um arquivo existe no sistema"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({
                'success': False,
                'exists': False,
                'error': 'Caminho do arquivo não fornecido'
            }), 400
        
        # Verificar se o arquivo existe
        exists = os.path.exists(file_path) and os.path.isfile(file_path)
        
        logger.info(f"Validação de arquivo: {file_path} - Existe: {exists}")
        
        return jsonify({
            'success': True,
            'exists': exists,
            'file_path': file_path
        })
        
    except Exception as e:
        logger.error(f"Erro ao validar arquivo: {str(e)}")
        return jsonify({
            'success': False,
            'exists': False,
            'error': str(e)
        }), 500
