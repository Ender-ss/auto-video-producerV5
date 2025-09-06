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

# Importar modelos do banco de dados
try:
    from app import db, Pipeline, PipelineLog
except ImportError:
    # Fallback para caso a importação falhe
    db = None
    Pipeline = None
    PipelineLog = None
    logger.warning("Não foi possível importar modelos do banco de dados")

# ================================
# 📊 ESTADO GLOBAL DO PIPELINE
# ================================

# Armazenamento em memória para pipelines ativos
active_pipelines: Dict[str, Dict[str, Any]] = {}
pipeline_logs: Dict[str, list] = {}

# ================================
# 🗄️ FUNÇÕES DE PERSISTÊNCIA
# ================================

def add_pipeline_log(pipeline_id: str, level: str, message: str, step: str = None, data: dict = None):
    """Adicionar log persistente da pipeline"""
    try:
        if PipelineLog and db:
            log_entry = PipelineLog(
                pipeline_id=pipeline_id,
                level=level,
                step=step,
                message=message,
                data=json.dumps(data) if data else None
            )
            db.session.add(log_entry)
            db.session.commit()
        
        # Também adicionar ao log em memória se pipeline estiver ativa
        if pipeline_id not in pipeline_logs:
            pipeline_logs[pipeline_id] = []
        pipeline_logs[pipeline_id].append({
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'step': step,
            'message': message,
            'data': data
        })
        
        logger.info(f"[{pipeline_id[:8]}] [{level.upper()}] {message}")
        
    except Exception as e:
        logger.error(f"Erro ao salvar log da pipeline {pipeline_id}: {e}")

def save_pipeline_to_db(pipeline_state: dict):
    """Salvar estado da pipeline no banco de dados"""
    try:
        if not Pipeline or not db:
            return None
            
        pipeline_id = pipeline_state['pipeline_id']
        
        # Verificar se já existe
        pipeline = Pipeline.query.filter_by(pipeline_id=pipeline_id).first()
        if not pipeline:
            # Gerar display_name amigável
            display_name = Pipeline.generate_display_name()
            
            pipeline = Pipeline(
                pipeline_id=pipeline_id,
                display_name=display_name,
                title=pipeline_state.get('title') or pipeline_state.get('config', {}).get('titles', {}).get('selected_title', 'Pipeline sem título'),
                channel_url=pipeline_state.get('channel_url'),
                status=pipeline_state.get('status', PipelineStatus.QUEUED),
                config_json=json.dumps(pipeline_state.get('config', {})),
                agent_config=json.dumps(pipeline_state.get('agent', {})),
                estimated_completion=datetime.fromisoformat(pipeline_state['estimated_completion']) if pipeline_state.get('estimated_completion') else None
            )
            db.session.add(pipeline)
        else:
            # Atualizar existente
            pipeline.status = pipeline_state.get('status', pipeline.status)
            pipeline.progress = pipeline_state.get('progress', pipeline.progress)
            pipeline.current_step = pipeline_state.get('current_step')
            
            # Atualizar resultados dos steps
            results = pipeline_state.get('results', {})
            if 'extraction' in results:
                pipeline.extraction_results = json.dumps(results['extraction'])
            if 'titles' in results:
                pipeline.titles_results = json.dumps(results['titles'])
            if 'premises' in results:
                pipeline.premises_results = json.dumps(results['premises'])
            if 'scripts' in results:
                pipeline.scripts_results = json.dumps(results['scripts'])
            if 'tts' in results:
                pipeline.tts_results = json.dumps(results['tts'])
            if 'images' in results:
                pipeline.images_results = json.dumps(results['images'])
            if 'video' in results:
                pipeline.video_results = json.dumps(results['video'])
            
            if pipeline_state.get('status') == PipelineStatus.COMPLETED:
                pipeline.completed_at = datetime.utcnow()
            
            if pipeline_state.get('error_message'):
                pipeline.error_message = pipeline_state['error_message']
            
            if pipeline_state.get('warnings'):
                pipeline.warnings = json.dumps(pipeline_state['warnings'])
        
        db.session.commit()
        return pipeline
        
    except Exception as e:
        logger.error(f"Erro ao salvar pipeline no banco: {e}")
        if db:
            db.session.rollback()
        return None

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
    SCRIPT_PROCESSING = 'script_processing'
    TTS = 'tts'
    IMAGES = 'images'
    VIDEO = 'video'
    CLEANUP = 'cleanup'

# ================================
# 🎯 ENDPOINTS PRINCIPAIS
# ================================

@pipeline_complete_bp.route('/active', methods=['GET'])
def get_active_pipelines():
    """Listar pipelines ativos (memória + banco de dados)"""
    try:
        # Filtrar pipelines por status se especificado
        status_filter = request.args.get('status', '')
        include_history = request.args.get('history', 'false').lower() == 'true'
        limit = request.args.get('limit', 50, type=int)
        
        pipelines_list = []
        
        if include_history and Pipeline:
            # Buscar do banco de dados para histórico
            query = Pipeline.query
            
            if status_filter:
                allowed_statuses = [s.strip() for s in status_filter.split(',')]
                query = query.filter(Pipeline.status.in_(allowed_statuses))
            
            db_pipelines = query.order_by(Pipeline.started_at.desc()).limit(limit).all()
            
            for pipeline in db_pipelines:
                pipeline_dict = pipeline.to_dict()
                
                # Adicionar display_name para compatibilidade com frontend
                pipeline_dict['display_name'] = pipeline.display_name
                
                pipelines_list.append(pipeline_dict)
        else:
            # Buscar apenas da memória (pipelines ativas)
            if status_filter:
                allowed_statuses = [s.strip() for s in status_filter.split(',')]
                filtered_pipelines = {
                    pid: pipeline for pid, pipeline in active_pipelines.items()
                    if pipeline.get('status') in allowed_statuses
                }
            else:
                filtered_pipelines = active_pipelines
            
            for pipeline_id, pipeline_data in filtered_pipelines.items():
                # Buscar display_name do banco se disponível
                display_name = pipeline_id[:8]
                if Pipeline:
                    db_pipeline = Pipeline.query.filter_by(pipeline_id=pipeline_id).first()
                    if db_pipeline:
                        display_name = db_pipeline.display_name
                
                pipelines_list.append({
                    'pipeline_id': pipeline_id,
                    'display_name': display_name,
                    'status': pipeline_data.get('status'),
                    'started_at': pipeline_data.get('started_at'),
                    'progress': pipeline_data.get('progress', 0),
                    'current_step': pipeline_data.get('current_step', ''),
                    'config': pipeline_data.get('config', {}),
                    'results': pipeline_data.get('results', {}),
                    'logs': pipeline_logs.get(pipeline_id, [])
                })
        
        return jsonify({
            'success': True,
            'pipelines': pipelines_list,
            'total': len(pipelines_list)
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar pipelines ativos: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipeline_complete_bp.route('/history', methods=['GET'])
def get_pipeline_history():
    """Obter histórico completo de pipelines"""
    try:
        if not Pipeline:
            return jsonify({
                'success': False,
                'error': 'Banco de dados não disponível'
            }), 500
        
        # Parâmetros de filtragem
        status_filter = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Construir query
        query = Pipeline.query
        
        if status_filter:
            allowed_statuses = [s.strip() for s in status_filter.split(',')]
            query = query.filter(Pipeline.status.in_(allowed_statuses))
        
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from)
                query = query.filter(Pipeline.started_at >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to)
                query = query.filter(Pipeline.started_at <= date_to_obj)
            except ValueError:
                pass
        
        # Executar query com paginação
        pipelines = query.order_by(Pipeline.started_at.desc()).offset(offset).limit(limit).all()
        total_count = query.count()
        
        # Converter para dicionário
        pipelines_list = [pipeline.to_dict() for pipeline in pipelines]
        
        return jsonify({
            'success': True,
            'pipelines': pipelines_list,
            'total': len(pipelines_list),
            'total_count': total_count,
            'offset': offset,
            'limit': limit
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de pipelines: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipeline_complete_bp.route('/stats', methods=['GET'])
def get_pipeline_stats():
    """Obter estatísticas das pipelines"""
    try:
        if not Pipeline:
            return jsonify({
                'success': False,
                'error': 'Banco de dados não disponível'
            }), 500
        
        from sqlalchemy import func
        
        # Estatísticas por status
        status_stats = db.session.query(
            Pipeline.status,
            func.count(Pipeline.id).label('count')
        ).group_by(Pipeline.status).all()
        
        # Pipelines por dia (ultimos 30 dias)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_stats = db.session.query(
            func.date(Pipeline.started_at).label('date'),
            func.count(Pipeline.id).label('count')
        ).filter(
            Pipeline.started_at >= thirty_days_ago
        ).group_by(func.date(Pipeline.started_at)).all()
        
        # Taxa de sucesso
        total_pipelines = Pipeline.query.count()
        completed_pipelines = Pipeline.query.filter_by(status='completed').count()
        success_rate = (completed_pipelines / total_pipelines * 100) if total_pipelines > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'status_distribution': {status: count for status, count in status_stats},
                'daily_stats': [{'date': str(date), 'count': count} for date, count in daily_stats],
                'total_pipelines': total_pipelines,
                'success_rate': round(success_rate, 2),
                'active_pipelines': len(active_pipelines)
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipeline_complete_bp.route('/by-name/<display_name>', methods=['GET'])
def get_pipeline_by_display_name(display_name: str):
    """Buscar pipeline pelo nome amigável (ex: 2025-01-31-001)"""
    try:
        if not Pipeline:
            return jsonify({
                'success': False,
                'error': 'Banco de dados não disponível'
            }), 500
        
        pipeline = Pipeline.query.filter_by(display_name=display_name).first()
        if not pipeline:
            return jsonify({
                'success': False,
                'error': f'Pipeline {display_name} não encontrado'
            }), 404
        
        pipeline_dict = pipeline.to_dict()
        
        # Buscar logs se disponível
        if PipelineLog:
            logs = PipelineLog.query.filter_by(pipeline_id=pipeline.pipeline_id).order_by(PipelineLog.timestamp).all()
            pipeline_dict['logs'] = [log.to_dict() for log in logs]
        else:
            pipeline_dict['logs'] = []
        
        return jsonify({
            'success': True,
            'data': pipeline_dict
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar pipeline por nome {display_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
                'enabled': True,
                'method': 'auto',
                'max_titles': 10,
                'min_views': 1000,
                'days_back': 30
            },
            'titles': {
                'enabled': True,
                'provider': 'gemini',
                'custom_prompt': False,
                'count': 5,
                'style': 'viral'
            },
            'premises': {
                'enabled': True,
                'provider': 'gemini',
                'custom_prompt': False,
                'word_count': 200
            },
            'scripts': {
                'enabled': True,
                'chapters': 5,
                'style': 'inicio',
                'duration_target': '5-7 minutes',
                'include_hooks': True,
                'detailed_prompt_text': '',
                'detailed_prompt': False
            },
            'script_processing': {
                'enabled': True,
                'remove_chapter_markers': True,
                'clean_formatting': True,
                'preserve_structure': True
            },
            'tts': {
                'enabled': True,
                'provider': 'kokoro',
                'voice': 'default',
                'speed': 1.0,
                'emotion': 'neutral'
            },
            'images': {
                'enabled': True,
                'provider': 'pollinations',
                'style': 'cinematic',
                'resolution': '1920x1080',
                'per_chapter': 2
            },
            'video': {
                'enabled': True,
                'resolution': '1920x1080',
                'fps': 30,
                'quality': 'high',
                'transitions': True,
                'subtitles': True
            }
        }
        
        # Mesclar configuração fornecida com padrão (recursivamente)
        user_config = data.get('config', {})
        
        def merge_configs_recursive(default, user):
            """Mescla configurações recursivamente preservando valores padrão"""
            result = default.copy()
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_configs_recursive(result[key], value)
                else:
                    result[key] = value
            return result
        
        config = merge_configs_recursive(default_config, user_config)
        logger.info(f"🔧 Configuração mesclada: script_processing habilitado = {config.get('script_processing', {}).get('enabled', False)}")
        
        # CORREÇÃO: Mapear video_count do frontend para max_titles no backend
        # O frontend envia video_count mas o backend espera max_titles na configuração de extraction
        if 'video_count' in user_config:
            video_count = user_config['video_count']
            if 'extraction' not in config:
                config['extraction'] = {}
            config['extraction']['max_titles'] = video_count
            logger.info(f"🔧 Mapeando video_count={video_count} para extraction.max_titles={video_count}")
        elif user_config.get('extraction', {}).get('max_titles') is None:
            # Se não há video_count nem max_titles, usar padrão de 10
            config['extraction']['max_titles'] = 10
        
        # Processar configuração de agentes especializados
        agent_config = data.get('agent', {})
        specialized_agents = data.get('specialized_agents', {})
        
        # Integrar prompts especializados se agente estiver ativo
        if agent_config.get('type') == 'specialized' and agent_config.get('specialized_type'):
            agent_type = agent_config['specialized_type']
            if agent_type in specialized_agents:
                agent_prompts = specialized_agents[agent_type].get('prompts', {})
                # Aplicar prompts especializados à configuração
                if 'titles' in agent_prompts:
                    config['titles']['agent_prompts'] = agent_prompts['titles']
                if 'premises' in agent_prompts:
                    config['premises']['agent_prompts'] = agent_prompts['premises']
                if 'scripts' in agent_prompts:
                    config['scripts']['agent_prompts'] = agent_prompts['scripts']
                if 'images' in agent_prompts:
                    config['images']['agent_prompts'] = agent_prompts['images']
                
                # Marcar que agente especializado está ativo
                config['agent'] = {
                    'enabled': True,
                    'type': agent_type,
                    'name': specialized_agents[agent_type].get('name', agent_type)
                }
        
        # Mapear 'provider' para 'method' na configuração de extraction se necessário
        if 'extraction' in user_config and 'provider' in user_config['extraction']:
            config['extraction']['method'] = user_config['extraction']['provider']
        
        # Processar títulos fornecidos para extração manual
        if 'extraction' in user_config and user_config['extraction'].get('method') == 'manual':
            if 'titles' in user_config['extraction']:
                config['extraction']['provided_titles'] = user_config['extraction']['titles']
        
        # Carregar chaves de API do arquivo
        api_keys = load_api_keys_from_file()
        
        # Determinar etapas habilitadas baseadas na configuração
        enabled_steps = {}
        
        # Verificar quais etapas estão habilitadas
        if config.get('extraction', {}).get('enabled', True):
            enabled_steps[PipelineSteps.EXTRACTION] = {'status': 'pending', 'progress': 0, 'result': None, 'error': None}
        if config.get('titles', {}).get('enabled', True):
            enabled_steps[PipelineSteps.TITLES] = {'status': 'pending', 'progress': 0, 'result': None, 'error': None}
        if config.get('premises', {}).get('enabled', True):
            enabled_steps[PipelineSteps.PREMISES] = {'status': 'pending', 'progress': 0, 'result': None, 'error': None}
        if config.get('scripts', {}).get('enabled', True):
            enabled_steps[PipelineSteps.SCRIPTS] = {'status': 'pending', 'progress': 0, 'result': None, 'error': None}
        if config.get('script_processing', {}).get('enabled', True):
            enabled_steps[PipelineSteps.SCRIPT_PROCESSING] = {'status': 'pending', 'progress': 0, 'result': None, 'error': None}
        if config.get('tts', {}).get('enabled', True):
            enabled_steps[PipelineSteps.TTS] = {'status': 'pending', 'progress': 0, 'result': None, 'error': None}
        if config.get('images', {}).get('enabled', True):
            enabled_steps[PipelineSteps.IMAGES] = {'status': 'pending', 'progress': 0, 'result': None, 'error': None}
        if config.get('video', {}).get('enabled', True):
            enabled_steps[PipelineSteps.VIDEO] = {'status': 'pending', 'progress': 0, 'result': None, 'error': None}
        
        # Cleanup sempre habilitado se há pelo menos uma etapa
        if enabled_steps:
            enabled_steps[PipelineSteps.CLEANUP] = {'status': 'pending', 'progress': 0, 'result': None, 'error': None}

        # Inicializar estado do pipeline
        pipeline_state = {
            'pipeline_id': pipeline_id,
            'title': data.get('title', 'Pipeline sem título'),  # Adicionar título desde o início
            'status': PipelineStatus.QUEUED,
            'current_step': None,
            'progress': 0,
            'started_at': datetime.utcnow().isoformat(),
            'estimated_completion': None,
            'completed_at': None,
            'channel_url': data['channel_url'],
            'config': config,
            'api_keys': api_keys,
            'steps': enabled_steps,
            'results': {},
            'errors': [],
            'warnings': []
        }
        
        # Armazenar estado
        active_pipelines[pipeline_id] = pipeline_state
        
        # Salvar no banco de dados
        save_pipeline_to_db(pipeline_state)
        
        # Adicionar log inicial
        add_pipeline_log(pipeline_id, 'info', 'Pipeline iniciado', data={
            'channel_url': data['channel_url'],
            'config_summary': {
                'extraction_method': config.get('extraction', {}).get('method', 'auto'),
                'ai_provider': config.get('titles', {}).get('provider', 'gemini'),
                'tts_provider': config.get('tts', {}).get('provider', 'kokoro'),
                'image_provider': config.get('images', {}).get('provider', 'pollinations')
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
    """Obter status do pipeline (memória ou banco)"""
    try:
        # Primeiro tentar da memória (pipelines ativas)
        if pipeline_id in active_pipelines:
            pipeline_state = active_pipelines[pipeline_id].copy()
            
            # Enriquecer com dados do banco (display_name, title, etc.)
            if Pipeline:
                db_pipeline = Pipeline.query.filter_by(pipeline_id=pipeline_id).first()
                if db_pipeline:
                    pipeline_state['display_name'] = db_pipeline.display_name
                    pipeline_state['title'] = db_pipeline.title
                    pipeline_state['channel_url'] = db_pipeline.channel_url
                    pipeline_state['started_at'] = db_pipeline.started_at.isoformat()
                    if db_pipeline.completed_at:
                        pipeline_state['completed_at'] = db_pipeline.completed_at.isoformat()
            
            # Incluir logs no estado do pipeline para o frontend
            pipeline_state['logs'] = pipeline_logs.get(pipeline_id, [])
            
            return jsonify({
                'success': True,
                'data': pipeline_state
            })
        
        # Se não encontrar na memória, buscar no banco
        if Pipeline:
            db_pipeline = Pipeline.query.filter_by(pipeline_id=pipeline_id).first()
            if db_pipeline:
                pipeline_dict = db_pipeline.to_dict()
                
                # Buscar logs do banco também
                if PipelineLog:
                    logs = PipelineLog.query.filter_by(pipeline_id=pipeline_id).order_by(PipelineLog.timestamp).all()
                    pipeline_dict['logs'] = [log.to_dict() for log in logs]
                else:
                    pipeline_dict['logs'] = []
                
                return jsonify({
                    'success': True,
                    'data': pipeline_dict
                })
        
        return jsonify({
            'success': False,
            'error': 'Pipeline não encontrado'
        }), 404
        
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
        
        # Alterar o status para PROCESSING
        pipeline_state['status'] = PipelineStatus.PROCESSING
        add_pipeline_log(pipeline_id, 'info', 'Pipeline retomado pelo usuário')
        
        # Sinalizar retomada para o PipelineService se existir uma instância ativa
        try:
            # Tentar encontrar a instância do PipelineService para este pipeline
            # Isso é feito através do threading local ou global registry se implementado
            # Por enquanto, o PipelineService detectará a mudança de status automaticamente
            pass
        except Exception as signal_error:
            logger.warning(f"Não foi possível sinalizar retomada diretamente: {str(signal_error)}")
        
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

@pipeline_complete_bp.route('/clear-test-pipelines', methods=['POST'])
def clear_test_pipelines():
    """Limpar pipelines de teste em aguardo"""
    try:
        if not Pipeline:
            return jsonify({
                'success': False,
                'error': 'Banco de dados não disponível'
            }), 500
        
        # Buscar pipelines em estado de teste (aguardando, processando, pausadas)
        test_statuses = ['queued', 'processing', 'paused']
        pipelines = Pipeline.query.filter(Pipeline.status.in_(test_statuses)).all()
        
        cancelled_count = 0
        test_pipelines = []
        
        for p in pipelines:
            # Verificar se é pipeline de teste baseado no título ou nome
            is_test = (
                'teste' in (p.title or '').lower() or
                'test' in (p.title or '').lower() or
                'exemplo' in (p.title or '').lower() or
                'demo' in (p.title or '').lower() or
                p.title == 'Pipeline sem título' or  # Pipelines sem título específico
                not p.title or  # Pipelines sem título
                p.title.strip() == ''  # Pipelines com título vazio
            )
            
            if is_test:
                test_pipelines.append(p)
        
        logger.info(f"🔍 Encontradas {len(test_pipelines)} pipelines de teste para cancelar")
        
        # Cancelar pipelines de teste
        for p in test_pipelines:
            # Cancelar no banco de dados
            p.status = 'cancelled'
            p.current_step = 'Pipeline de teste cancelado pelo usuário'
            p.completed_at = datetime.utcnow()
            cancelled_count += 1
            
            # Cancelar na memória se existir
            if p.pipeline_id in active_pipelines:
                pipeline_state = active_pipelines[p.pipeline_id]
                pipeline_state['status'] = PipelineStatus.CANCELLED
                pipeline_state['completed_at'] = datetime.utcnow().isoformat()
                add_pipeline_log(p.pipeline_id, 'warning', 'Pipeline de teste cancelado pelo usuário via limpeza')
        
        if cancelled_count > 0:
            db.session.commit()
            logger.info(f"✅ {cancelled_count} pipelines de teste foram canceladas com sucesso!")
        
        # Verificar quantas pipelines restam aguardando
        remaining = Pipeline.query.filter(Pipeline.status.in_(['queued', 'processing', 'paused'])).count()
        
        return jsonify({
            'success': True,
            'message': f'{cancelled_count} pipelines de teste canceladas com sucesso',
            'data': {
                'cancelled_count': cancelled_count,
                'remaining_pending': remaining,
                'cancelled_pipelines': [{
                    'pipeline_id': p.pipeline_id,
                    'display_name': p.display_name,
                    'title': p.title,
                    'status': 'cancelled'
                } for p in test_pipelines]
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao limpar pipelines de teste: {str(e)}")
        if db:
            db.session.rollback()
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
    per_chapter = images_config.get('per_chapter', 2)  # Manter para compatibilidade
    total_images = images_config.get('total_images', per_chapter * 3)  # Padrão baseado em total
    if total_images > 20:
        base_time += total_images * 15  # 15 segundos por imagem acima de 20
    
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
        logger.info(f"🔧 Inicializando PipelineService para pipeline {pipeline_id}")
        service = PipelineService(pipeline_id)
        
        # Usar sistema de retomada automática com checkpoints
        try:
            logger.info(f"🔧 PipelineService inicializado, executando run_with_resume()")
            result = service.run_with_resume()
            logger.info(f"🔧 Pipeline executada, resultados: {list(result.keys()) if result else 'None'}")
            
            # Atualizar estado do pipeline com os resultados
            pipeline_state['results'] = result
            
            # Atualizar status dos steps individuais baseado nos resultados
            for step_name, step_result in result.items():
                if step_name in pipeline_state['steps']:
                    pipeline_state['steps'][step_name]['result'] = step_result
                    pipeline_state['steps'][step_name]['status'] = 'completed'
                    pipeline_state['steps'][step_name]['progress'] = 100
            
            pipeline_state['status'] = PipelineStatus.COMPLETED
            pipeline_state['completed_at'] = datetime.utcnow().isoformat()
            pipeline_state['progress'] = 100
            
            add_pipeline_log(pipeline_id, 'info', 'Pipeline concluído com sucesso!')
            add_pipeline_log(pipeline_id, 'info', f'Resultados salvos: {list(result.keys())}')
            return
            
        except Exception as e:
            # Se houver erro, tentar execução manual das etapas
            add_pipeline_log(pipeline_id, 'error', f'Erro na execução automática: {str(e)}')
            add_pipeline_log(pipeline_id, 'warning', 'Tentando execução manual das etapas...')
        
        # Executar etapas do pipeline manualmente (fallback)
        # Verificar quais etapas estão habilitadas na configuração
        config = pipeline_state.get('config', {})
        
        steps = [
            (PipelineSteps.EXTRACTION, service.run_extraction, config.get('extraction', {}).get('enabled', True)),
            (PipelineSteps.TITLES, service.run_titles_generation, config.get('titles', {}).get('enabled', True)),
            (PipelineSteps.PREMISES, service.run_premises_generation, config.get('premises', {}).get('enabled', True)),
            (PipelineSteps.SCRIPTS, service.run_scripts_generation, config.get('scripts', {}).get('enabled', True)),
            (PipelineSteps.SCRIPT_PROCESSING, service.run_script_processing, config.get('script_processing', {}).get('enabled', True)),
            (PipelineSteps.TTS, service.run_tts_generation, config.get('tts', {}).get('enabled', True)),
            (PipelineSteps.IMAGES, service.run_images_generation, config.get('images', {}).get('enabled', True)),
            (PipelineSteps.VIDEO, service.run_video_creation, config.get('video', {}).get('enabled', True)),
            (PipelineSteps.CLEANUP, service.run_cleanup, True)  # Cleanup sempre habilitado
        ]
        
        for step_name, step_function, is_enabled in steps:
            # Verificar se pipeline foi cancelado ou pausado
            if pipeline_state['status'] in [PipelineStatus.CANCELLED, PipelineStatus.PAUSED]:
                add_pipeline_log(pipeline_id, 'warning', f'Pipeline interrompido na etapa {step_name}')
                return
            
            # Verificar se a etapa está habilitada
            if not is_enabled:
                add_pipeline_log(pipeline_id, 'info', f'Etapa {step_name} desabilitada na configuração, pulando')
                update_pipeline_progress(pipeline_id, step_name, 100, 'skipped')
                
                # Criar resultado placeholder para compatibilidade
                placeholder_result = {
                    'status': 'skipped',
                    'message': f'Etapa {step_name} desabilitada pelo usuário',
                    'timestamp': datetime.utcnow().isoformat()
                }
                pipeline_state['steps'][step_name]['result'] = placeholder_result
                pipeline_state['results'][step_name] = placeholder_result
                continue
            
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