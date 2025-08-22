"""🚀 Pipeline de Automação Completa
Controlador principal para automação end-to-end de produção de vídeos
"""

from flask import Blueprint, request, jsonify
import uuid
import json
import logging
from datetime import datetime, timedelta
import threading
import time
from typing import Dict, Any, Optional
import os
import json

def load_api_keys_from_file():
    """Carrega chaves de API do arquivo JSON"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar chaves de API: {e}")
    return {}

# Configurar logging
logger = logging.getLogger(__name__)

# Criar blueprint
pipeline_complete_bp = Blueprint('pipeline_complete', __name__)

# ================================
# 📊 ESTADO GLOBAL DO PIPELINE
# ================================

# Armazenamento em memória para pipelines ativos
active_pipelines: Dict[str, Dict[str, Any]] = {}
pipeline_logs: Dict[str, list] = {}

class PipelineStatus:
    """Estados possíveis do pipeline"""
    QUEUED = 'queued'
    PROCESSING = 'processing'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class PipelineSteps:
    """Etapas do pipeline"""
    EXTRACTION = 'extraction'
    TITLES = 'titles'
    PREMISES = 'premises'
    SCRIPTS = 'scripts'
    TTS = 'tts'
    IMAGES = 'images'
    VIDEO = 'video'
    CLEANUP = 'cleanup'

# ================================
# 🎯 ENDPOINT PRINCIPAL
# ================================

@pipeline_complete_bp.route('/complete', methods=['POST'])
def start_complete_automation():
    """Iniciar automação completa do pipeline"""
    try:
        data = request.get_json()
        
        # Validar dados de entrada
        if not data or 'channel_url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL do canal é obrigatória'
            }), 400
        
        # Gerar ID único para o pipeline
        pipeline_id = str(uuid.uuid4())
        
        # Configuração padrão
        default_config = {
            'extraction': {
                'method': 'auto',
                'max_titles': 10,
                'min_views': 1000,
                'days_back': 30
            },
            'titles': {
                'provider': 'gemini',
                'custom_prompt': False,
                'count': 5,
                'style': 'viral'
            },
            'premises': {
                'provider': 'gemini',
                'custom_prompt': False,
                'word_count': 200
            },
            'scripts': {
                'chapters': 5,
                'style': 'inicio',
                'duration_target': '5-7 minutes',
                'include_hooks': True
            },
            'tts': {
                'provider': 'kokoro',
                'voice': 'default',
                'speed': 1.0,
                'emotion': 'neutral'
            },
            'images': {
                'provider': 'pollinations',
                'style': 'cinematic',
                'resolution': '1920x1080',
                'per_chapter': 2
            },
            'video': {
                'resolution': '1920x1080',
                'fps': 30,
                'quality': 'high',
                'transitions': True,
                'subtitles': True
            }
        }
        
        # Mesclar configuração fornecida com padrão
        user_config = data.get('config', {})
        config = {**default_config, **user_config}
        
        # Mapear 'provider' para 'method' na configuração de extraction se necessário
        if 'extraction' in user_config and 'provider' in user_config['extraction']:
            config['extraction']['method'] = user_config['extraction']['provider']
        
        # Processar títulos fornecidos para extração manual
        if 'extraction' in user_config and user_config['extraction'].get('method') == 'manual':
            if 'titles' in user_config['extraction']:
                config['extraction']['provided_titles'] = user_config['extraction']['titles']
        
        # Carregar chaves de API do arquivo
        api_keys = load_api_keys_from_file()
        
        # Inicializar estado do pipeline
        pipeline_state = {
            'pipeline_id': pipeline_id,
            'status': PipelineStatus.QUEUED,
            'current_step': None,
            'progress': 0,
            'started_at': datetime.utcnow().isoformat(),
            'estimated_completion': None,
            'completed_at': None,
            'channel_url': data['channel_url'],
            'config': config,
            'api_keys': api_keys,
            'steps': {
                PipelineSteps.EXTRACTION: {'status': 'pending', 'progress': 0, 'result': None, 'error': None},
                PipelineSteps.TITLES: {'status': 'pending', 'progress': 0, 'result': None, 'error': None},
                PipelineSteps.PREMISES: {'status': 'pending', 'progress': 0, 'result': None, 'error': None},
                PipelineSteps.SCRIPTS: {'status': 'pending', 'progress': 0, 'result': None, 'error': None},
                PipelineSteps.TTS: {'status': 'pending', 'progress': 0, 'result': None, 'error': None},
                PipelineSteps.IMAGES: {'status': 'pending', 'progress': 0, 'result': None, 'error': None},
                PipelineSteps.VIDEO: {'status': 'pending', 'progress': 0, 'result': None, 'error': None},
                PipelineSteps.CLEANUP: {'status': 'pending', 'progress': 0, 'result': None, 'error': None}
            },
            'results': {},
            'errors': [],
            'warnings': []
        }
        
        # Armazenar estado
        active_pipelines[pipeline_id] = pipeline_state
        pipeline_logs[pipeline_id] = []
        
        # Adicionar log inicial
        add_pipeline_log(pipeline_id, 'info', 'Pipeline iniciado', {
            'channel_url': data['channel_url'],
            'config_summary': {
                'extraction_method': config['extraction']['method'],
                'ai_provider': config['titles']['provider'],
                'tts_provider': config['tts']['provider'],
                'image_provider': config['images']['provider']
            }
        })
        
        # Calcular tempo estimado (baseado na configuração)
        estimated_time = calculate_estimated_time(config)
        pipeline_state['estimated_completion'] = (
            datetime.utcnow() + timedelta(seconds=estimated_time)
        ).isoformat()
        
        # Iniciar processamento em thread separada
        thread = threading.Thread(
            target=process_complete_pipeline,
            args=(pipeline_id,),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'pipeline_id': pipeline_id,
            'status': PipelineStatus.QUEUED,
            'estimated_time': f"{estimated_time // 60} minutos",
            'steps': list(pipeline_state['steps'].keys()),
            'message': 'Pipeline iniciado com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao iniciar pipeline completo: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# ================================
# 📊 ENDPOINTS DE MONITORAMENTO
# ================================

@pipeline_complete_bp.route('/status/<pipeline_id>', methods=['GET'])
def get_pipeline_status(pipeline_id: str):
    """Obter status do pipeline"""
    try:
        if pipeline_id not in active_pipelines:
            return jsonify({
                'success': False,
                'error': 'Pipeline não encontrado'
            }), 404
        
        pipeline_state = active_pipelines[pipeline_id].copy()
        
        # Incluir logs no estado do pipeline para o frontend
        if pipeline_id in pipeline_logs:
            pipeline_state['logs'] = pipeline_logs[pipeline_id]
        else:
            pipeline_state['logs'] = []
        
        return jsonify({
            'success': True,
            'data': pipeline_state
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status do pipeline {pipeline_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipeline_complete_bp.route('/logs/<pipeline_id>', methods=['GET'])
def get_pipeline_logs(pipeline_id: str):
    """Obter logs do pipeline"""
    try:
        if pipeline_id not in pipeline_logs:
            return jsonify({
                'success': False,
                'error': 'Pipeline não encontrado'
            }), 404
        
        logs = pipeline_logs[pipeline_id]
        
        # Filtros opcionais
        level = request.args.get('level')  # info, warning, error
        limit = request.args.get('limit', type=int, default=100)
        
        filtered_logs = logs
        if level:
            filtered_logs = [log for log in logs if log['level'] == level]
        
        # Limitar quantidade
        filtered_logs = filtered_logs[-limit:]
        
        return jsonify({
            'success': True,
            'data': {
                'pipeline_id': pipeline_id,
                'logs': filtered_logs,
                'total_logs': len(logs)
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter logs do pipeline {pipeline_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipeline_complete_bp.route('/pause/<pipeline_id>', methods=['POST'])
def pause_pipeline(pipeline_id: str):
    """Pausar pipeline"""
    try:
        if pipeline_id not in active_pipelines:
            return jsonify({
                'success': False,
                'error': 'Pipeline não encontrado'
            }), 404
        
        pipeline_state = active_pipelines[pipeline_id]
        
        if pipeline_state['status'] != PipelineStatus.PROCESSING:
            return jsonify({
                'success': False,
                'error': 'Pipeline não está em processamento'
            }), 400
        
        pipeline_state['status'] = PipelineStatus.PAUSED
        add_pipeline_log(pipeline_id, 'warning', 'Pipeline pausado pelo usuário')
        
        return jsonify({
            'success': True,
            'message': 'Pipeline pausado com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao pausar pipeline {pipeline_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipeline_complete_bp.route('/resume/<pipeline_id>', methods=['POST'])
def resume_pipeline(pipeline_id: str):
    """Retomar pipeline pausado"""
    try:
        if pipeline_id not in active_pipelines:
            return jsonify({
                'success': False,
                'error': 'Pipeline não encontrado'
            }), 404
        
        pipeline_state = active_pipelines[pipeline_id]
        
        if pipeline_state['status'] != PipelineStatus.PAUSED:
            return jsonify({
                'success': False,
                'error': 'Pipeline não está pausado'
            }), 400
        
        # Retomar pipeline em thread separada
        pipeline_state['status'] = PipelineStatus.PROCESSING
        add_pipeline_log(pipeline_id, 'info', 'Pipeline retomado pelo usuário')
        
        # Iniciar thread para continuar processamento
        thread = threading.Thread(
            target=process_complete_pipeline,
            args=(pipeline_id,),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Pipeline retomado com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao retomar pipeline {pipeline_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipeline_complete_bp.route('/cancel/<pipeline_id>', methods=['POST'])
def cancel_pipeline(pipeline_id: str):
    """Cancelar pipeline"""
    try:
        if pipeline_id not in active_pipelines:
            return jsonify({
                'success': False,
                'error': 'Pipeline não encontrado'
            }), 404
        
        pipeline_state = active_pipelines[pipeline_id]
        pipeline_state['status'] = PipelineStatus.CANCELLED
        pipeline_state['completed_at'] = datetime.utcnow().isoformat()
        
        add_pipeline_log(pipeline_id, 'warning', 'Pipeline cancelado pelo usuário')
        
        return jsonify({
            'success': True,
            'message': 'Pipeline cancelado com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao cancelar pipeline {pipeline_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# 🔧 FUNÇÕES AUXILIARES
# ================================

def add_pipeline_log(pipeline_id: str, level: str, message: str, data: Optional[Dict] = None):
    """Adicionar log ao pipeline"""
    if pipeline_id not in pipeline_logs:
        pipeline_logs[pipeline_id] = []
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'level': level,
        'message': message,
        'data': data or {}
    }
    
    pipeline_logs[pipeline_id].append(log_entry)
    logger.info(f"Pipeline {pipeline_id} [{level.upper()}]: {message}")

def calculate_estimated_time(config: Dict[str, Any]) -> int:
    """Calcular tempo estimado baseado na configuração"""
    base_time = 300  # 5 minutos base
    
    # Adicionar tempo baseado na configuração com verificações de segurança
    extraction_config = config.get('extraction', {})
    if extraction_config.get('max_titles', 10) > 10:
        base_time += 60
    
    scripts_config = config.get('scripts', {})
    if scripts_config.get('chapters', 5) > 5:
        base_time += 120
    
    images_config = config.get('images', {})
    per_chapter = images_config.get('per_chapter', 2)
    if per_chapter > 2:
        base_time += per_chapter * 30
    
    video_config = config.get('video', {})
    if video_config.get('quality', 'medium') == 'high':
        base_time += 180
    
    return base_time

def update_pipeline_progress(pipeline_id: str, step: str, progress: int, status: str = 'processing'):
    """Atualizar progresso do pipeline"""
    if pipeline_id not in active_pipelines:
        return
    
    pipeline_state = active_pipelines[pipeline_id]
    pipeline_state['current_step'] = step
    pipeline_state['steps'][step]['status'] = status
    pipeline_state['steps'][step]['progress'] = progress
    
    # Calcular progresso geral
    total_steps = len(pipeline_state['steps'])
    completed_steps = sum(1 for s in pipeline_state['steps'].values() if s['status'] == 'completed')
    current_step_progress = progress / 100
    
    overall_progress = int(((completed_steps + current_step_progress) / total_steps) * 100)
    pipeline_state['progress'] = min(overall_progress, 100)

def validate_step_dependencies(pipeline_id: str, current_step: str) -> bool:
    """Validar se as dependências da etapa atual foram atendidas"""
    pipeline_state = active_pipelines[pipeline_id]
    
    # Definir dependências entre etapas
    dependencies = {
        PipelineSteps.EXTRACTION: [],  # Primeira etapa, sem dependências
        PipelineSteps.TITLES: [PipelineSteps.EXTRACTION],  # Precisa dos dados extraídos
        PipelineSteps.PREMISES: [PipelineSteps.TITLES],  # Precisa dos títulos gerados
        PipelineSteps.SCRIPTS: [PipelineSteps.PREMISES],  # Precisa das premissas
        PipelineSteps.TTS: [PipelineSteps.SCRIPTS],  # Precisa dos roteiros
        PipelineSteps.IMAGES: [PipelineSteps.SCRIPTS],  # Precisa dos roteiros (paralelo ao TTS)
        PipelineSteps.VIDEO: [PipelineSteps.TTS, PipelineSteps.IMAGES],  # Precisa de áudio e imagens
        PipelineSteps.CLEANUP: [PipelineSteps.VIDEO]  # Precisa do vídeo finalizado
    }
    
    required_steps = dependencies.get(current_step, [])
    
    for required_step in required_steps:
        step_status = pipeline_state['steps'][required_step]['status']
        if step_status != 'completed':
            error_msg = f'Etapa {current_step} não pode ser executada: dependência {required_step} não foi concluída (status: {step_status})'
            add_pipeline_log(pipeline_id, 'error', error_msg)
            return False
    
    return True

def process_complete_pipeline(pipeline_id: str):
    """Processar pipeline completo (executado em thread separada)"""
    try:
        pipeline_state = active_pipelines[pipeline_id]
        pipeline_state['status'] = PipelineStatus.PROCESSING
        
        add_pipeline_log(pipeline_id, 'info', 'Iniciando processamento do pipeline')
        
        # Importar serviços necessários
        from services.pipeline_service import PipelineService
        
        # Inicializar serviço com configuração do pipeline
        service = PipelineService(pipeline_id)
        
        # Usar sistema de retomada automática com checkpoints
        try:
            result = service.run_with_resume()
            
            # Atualizar estado do pipeline com os resultados
            pipeline_state['results'] = result
            pipeline_state['status'] = PipelineStatus.COMPLETED
            pipeline_state['completed_at'] = datetime.utcnow().isoformat()
            pipeline_state['progress'] = 100
            
            add_pipeline_log(pipeline_id, 'info', 'Pipeline concluído com sucesso!')
            return
            
        except Exception as e:
            # Se houver erro, tentar execução manual das etapas
            add_pipeline_log(pipeline_id, 'warning', f'Erro na execução automática, tentando execução manual: {str(e)}')
        
        # Executar etapas do pipeline manualmente (fallback)
        steps = [
            (PipelineSteps.EXTRACTION, service.run_extraction),
            (PipelineSteps.TITLES, service.run_titles_generation),
            (PipelineSteps.PREMISES, service.run_premises_generation),
            (PipelineSteps.SCRIPTS, service.run_scripts_generation),
            (PipelineSteps.TTS, service.run_tts_generation),
            (PipelineSteps.IMAGES, service.run_images_generation),
            (PipelineSteps.VIDEO, service.run_video_creation),
            (PipelineSteps.CLEANUP, service.run_cleanup)
        ]
        
        for step_name, step_function in steps:
            # Verificar se pipeline foi cancelado ou pausado
            if pipeline_state['status'] in [PipelineStatus.CANCELLED, PipelineStatus.PAUSED]:
                add_pipeline_log(pipeline_id, 'warning', f'Pipeline interrompido na etapa {step_name}')
                return
            
            # Validar dependências da etapa atual
            if not validate_step_dependencies(pipeline_id, step_name):
                pipeline_state['status'] = PipelineStatus.FAILED
                add_pipeline_log(pipeline_id, 'error', f'Pipeline falhou na validação de dependências para {step_name}')
                return
            
            try:
                add_pipeline_log(pipeline_id, 'info', f'Iniciando etapa: {step_name}')
                update_pipeline_progress(pipeline_id, step_name, 0, 'processing')
                
                # Executar etapa
                result = step_function()
                
                # Armazenar resultado
                pipeline_state['steps'][step_name]['result'] = result
                pipeline_state['results'][step_name] = result
                
                update_pipeline_progress(pipeline_id, step_name, 100, 'completed')
                add_pipeline_log(pipeline_id, 'info', f'Etapa {step_name} concluída com sucesso')
                
            except Exception as e:
                error_msg = f'Erro na etapa {step_name}: {str(e)}'
                pipeline_state['steps'][step_name]['error'] = error_msg
                pipeline_state['errors'].append(error_msg)
                
                add_pipeline_log(pipeline_id, 'error', error_msg)
                
                # Decidir se continuar ou parar
                if step_name in [PipelineSteps.EXTRACTION, PipelineSteps.TITLES]:
                    # Etapas críticas - parar pipeline
                    pipeline_state['status'] = PipelineStatus.FAILED
                    add_pipeline_log(pipeline_id, 'error', 'Pipeline falhou em etapa crítica')
                    return
                else:
                    # Etapas não críticas - adicionar warning e continuar
                    pipeline_state['warnings'].append(error_msg)
                    add_pipeline_log(pipeline_id, 'warning', f'Continuando apesar do erro em {step_name}')
        
        # Pipeline concluído com sucesso
        pipeline_state['status'] = PipelineStatus.COMPLETED
        pipeline_state['completed_at'] = datetime.utcnow().isoformat()
        pipeline_state['progress'] = 100
        
        add_pipeline_log(pipeline_id, 'info', 'Pipeline concluído com sucesso!')
        
    except Exception as e:
        logger.error(f"Erro crítico no pipeline {pipeline_id}: {str(e)}")
        pipeline_state = active_pipelines.get(pipeline_id, {})
        pipeline_state['status'] = PipelineStatus.FAILED
        pipeline_state['completed_at'] = datetime.utcnow().isoformat()
        pipeline_state['errors'].append(f'Erro crítico: {str(e)}')
        
        add_pipeline_log(pipeline_id, 'error', f'Erro crítico no pipeline: {str(e)}')