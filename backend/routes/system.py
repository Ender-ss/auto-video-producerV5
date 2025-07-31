"""
🔧 System Routes
Sistema de logs e monitoramento
"""

from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime
import logging

system_bp = Blueprint('system', __name__)

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

# ================================
# 📋 LOGS
# ================================

@system_bp.route('/logs', methods=['GET'])
def get_logs():
    """Obter logs do sistema"""
    try:
        logs = []
        
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Processar últimas 100 linhas
            for line in lines[-100:]:
                if line.strip():
                    try:
                        # Parse do formato de log
                        parts = line.strip().split(' - ', 2)
                        if len(parts) >= 3:
                            timestamp = parts[0]
                            level = parts[1].lower()
                            message = parts[2]
                            
                            logs.append({
                                'timestamp': timestamp,
                                'level': level,
                                'message': message,
                                'source': 'system'
                            })
                    except Exception:
                        # Se não conseguir parsear, adiciona como info
                        logs.append({
                            'timestamp': datetime.now().isoformat(),
                            'level': 'info',
                            'message': line.strip(),
                            'source': 'system'
                        })
        
        # Ordenar por timestamp (mais recentes primeiro)
        logs.reverse()
        
        return jsonify({
            'success': True,
            'data': {
                'logs': logs,
                'total': len(logs)
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/logs', methods=['DELETE'])
def clear_logs():
    """Limpar logs do sistema"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w') as f:
                f.write('')
        
        logger.info("Logs limpos pelo usuário")
        
        return jsonify({
            'success': True,
            'message': 'Logs limpos com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao limpar logs: {str(e)}")
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
        
        # Log usando o logger configurado
        if level == 'error':
            logger.error(f"[{source}] {message}")
        elif level == 'warning':
            logger.warning(f"[{source}] {message}")
        elif level == 'success':
            logger.info(f"[{source}] ✅ {message}")
        else:
            logger.info(f"[{source}] {message}")
        
        return jsonify({
            'success': True,
            'message': 'Log adicionado'
        })
        
    except Exception as e:
        logger.error(f"Erro ao adicionar log: {str(e)}")
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
