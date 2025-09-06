"""
🎬 Pipelines Routes
Rotas para gerenciamento de pipelines de produção
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

pipelines_bp = Blueprint('pipelines', __name__)

@pipelines_bp.route('/', methods=['GET'])
def get_pipelines():
    """Listar todos os pipelines"""
    try:
        from app import Pipeline
        
        status_filter = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Pipeline.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        pipelines = query.order_by(Pipeline.started_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'pipelines': [pipeline.to_dict() for pipeline in pipelines.items],
                'total': pipelines.total,
                'pages': pipelines.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipelines_bp.route('/<int:pipeline_id>/script/process', methods=['POST'])
def process_script_legacy(pipeline_id):
    """Processar roteiro de um pipeline específico"""
    try:
        from app import Pipeline, db
        from services.script_processing_service import ScriptProcessingService
        
        pipeline = Pipeline.query.filter_by(pipeline_id=pipeline_id).first()
        if not pipeline:
            return jsonify({
                'success': False,
                'error': 'Pipeline não encontrada'
            }), 404
        
        if not pipeline.script_content:
            return jsonify({
                'success': False,
                'error': 'Pipeline não possui roteiro para processar'
            }), 400
        
        data = request.get_json() or {}
        config = {
            'remove_headers': data.get('remove_headers', True),
            'min_length': data.get('min_length', 50),
            'min_preservation_ratio': data.get('min_preservation_ratio', 0.8)
        }
        
        service = ScriptProcessingService()
        result = service.process_script(pipeline.script_content, config)
        
        if result['success']:
            # Atualizar pipeline com script processado
            pipeline.processed_script = result['processed_script']
            pipeline.script_processing_metrics = result['metrics']
            pipeline.script_processing_status = 'completed'
            pipeline.script_processing_completed_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'processed_script': result['processed_script'],
                    'metrics': result['metrics'],
                    'pipeline': pipeline.to_dict()
                }
            })
        else:
            pipeline.script_processing_status = 'failed'
            pipeline.script_processing_error = result['error']
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipelines_bp.route('/<int:pipeline_id>/script/status', methods=['GET'])
def get_script_processing_status_legacy(pipeline_id):
    """Obter status do processamento de roteiro"""
    try:
        from app import Pipeline
        
        pipeline = Pipeline.query.get_or_404(pipeline_id)
        
        return jsonify({
            'success': True,
            'data': {
                'status': pipeline.script_processing_status,
                'metrics': pipeline.script_processing_metrics,
                'error': pipeline.script_processing_error,
                'completed_at': pipeline.script_processing_completed_at.isoformat() if pipeline.script_processing_completed_at else None,
                'has_processed_script': bool(pipeline.processed_script)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipelines_bp.route('/<int:pipeline_id>/script/validate', methods=['POST'])
def validate_processed_script(pipeline_id):
    """Validar roteiro processado"""
    try:
        from app import Pipeline
        from services.script_processing_service import ScriptProcessingService
        
        pipeline = Pipeline.query.get_or_404(pipeline_id)
        
        if not pipeline.processed_script:
            return jsonify({
                'success': False,
                'error': 'Pipeline não possui roteiro processado para validar'
            }), 400
        
        data = request.get_json() or {}
        config = {
            'min_length': data.get('min_length', 50),
            'min_preservation_ratio': data.get('min_preservation_ratio', 0.8)
        }
        
        service = ScriptProcessingService()
        
        # Validar entrada
        input_valid = service.validate_input(pipeline.script_content, config)
        
        # Validar saída
        output_valid = service.validate_output(
            pipeline.processed_script, 
            pipeline.script_content, 
            config
        )
        
        # Obter métricas
        metrics = service.get_processing_metrics(
            pipeline.script_content,
            pipeline.processed_script
        )
        
        return jsonify({
            'success': True,
            'data': {
                'input_valid': input_valid,
                'output_valid': output_valid,
                'overall_valid': input_valid and output_valid,
                'metrics': metrics
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipelines_bp.route('/script/batch-process', methods=['POST'])
def batch_process_scripts():
    """Processar roteiros em lote"""
    try:
        from app import Pipeline, db
        from services.script_processing_service import ScriptProcessingService
        
        data = request.get_json()
        pipeline_ids = data.get('pipeline_ids', [])
        config = data.get('config', {})
        
        if not pipeline_ids:
            return jsonify({
                'success': False,
                'error': 'Lista de pipeline IDs é obrigatória'
            }), 400
        
        service = ScriptProcessingService()
        results = []
        
        for pipeline_id in pipeline_ids:
            try:
                pipeline = Pipeline.query.get(pipeline_id)
                if not pipeline:
                    results.append({
                        'pipeline_id': pipeline_id,
                        'success': False,
                        'error': 'Pipeline não encontrado'
                    })
                    continue
                
                if not pipeline.script_content:
                    results.append({
                        'pipeline_id': pipeline_id,
                        'success': False,
                        'error': 'Pipeline não possui roteiro'
                    })
                    continue
                
                result = service.process_script(pipeline.script_content, config)
                
                if result['success']:
                    pipeline.processed_script = result['processed_script']
                    pipeline.script_processing_metrics = result['metrics']
                    pipeline.script_processing_status = 'completed'
                    pipeline.script_processing_completed_at = datetime.utcnow()
                    
                    results.append({
                        'pipeline_id': pipeline_id,
                        'success': True,
                        'metrics': result['metrics']
                    })
                else:
                    pipeline.script_processing_status = 'failed'
                    pipeline.script_processing_error = result['error']
                    
                    results.append({
                        'pipeline_id': pipeline_id,
                        'success': False,
                        'error': result['error']
                    })
            
            except Exception as e:
                results.append({
                    'pipeline_id': pipeline_id,
                    'success': False,
                    'error': str(e)
                })
        
        db.session.commit()
        
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'summary': {
                    'total': total,
                    'successful': successful,
                    'failed': total - successful,
                    'success_rate': (successful / total * 100) if total > 0 else 0
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipelines_bp.route('/', methods=['POST'])
def create_pipeline():
    """Criar novo pipeline"""
    try:
        from app import Pipeline, db
        
        data = request.get_json()
        
        if not data.get('title'):
            return jsonify({
                'success': False,
                'error': 'Título é obrigatório'
            }), 400
        
        pipeline = Pipeline(
            title=data['title'],
            channel_id=data.get('channel_id'),
            video_style=data.get('video_style', 'motivational'),
            target_duration=data.get('target_duration', 300),
            current_step='Iniciando pipeline...'
        )
        
        db.session.add(pipeline)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': pipeline.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipelines_bp.route('/<int:pipeline_id>', methods=['GET'])
def get_pipeline(pipeline_id):
    """Obter pipeline específico"""
    try:
        from app import Pipeline
        
        pipeline = Pipeline.query.get_or_404(pipeline_id)
        
        return jsonify({
            'success': True,
            'data': pipeline.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipelines_bp.route('/<int:pipeline_id>/status', methods=['PUT'])
def update_pipeline_status(pipeline_id):
    """Atualizar status do pipeline"""
    try:
        from app import Pipeline, db
        
        pipeline = Pipeline.query.get_or_404(pipeline_id)
        data = request.get_json()
        
        if 'status' in data:
            pipeline.status = data['status']
        
        if 'progress' in data:
            pipeline.progress = data['progress']
        
        if 'current_step' in data:
            pipeline.current_step = data['current_step']
        
        if 'error_message' in data:
            pipeline.error_message = data['error_message']
        
        if data.get('status') == 'completed':
            pipeline.completed_at = datetime.utcnow()
            pipeline.progress = 100
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': pipeline.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipelines_bp.route('/<int:pipeline_id>/cancel', methods=['POST'])
def cancel_pipeline(pipeline_id):
    """Cancelar pipeline"""
    try:
        from app import Pipeline, db
        
        pipeline = Pipeline.query.get_or_404(pipeline_id)
        
        if pipeline.status in ['completed', 'failed', 'cancelled']:
            return jsonify({
                'success': False,
                'error': 'Pipeline não pode ser cancelado'
            }), 400
        
        pipeline.status = 'cancelled'
        pipeline.current_step = 'Pipeline cancelado pelo usuário'
        pipeline.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': pipeline.to_dict(),
            'message': 'Pipeline cancelado com sucesso'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipelines_bp.route('/<int:pipeline_id>/process-script', methods=['POST'])
def process_script(pipeline_id):
    """Processar roteiro de uma pipeline específica"""
    try:
        from app import Pipeline, db
        from services.script_processing_service import ScriptProcessingService
        
        pipeline = Pipeline.query.get_or_404(pipeline_id)
        
        # Verificar se pipeline está no status correto
        if not pipeline.scripts_results:
            return jsonify({
                'success': False,
                'error': 'Pipeline não possui roteiro gerado para processar'
            }), 400
        
        # Obter configuração do processamento
        config = request.get_json() or {}
        
        # Obter roteiro dos resultados
        import json
        scripts_data = json.loads(pipeline.scripts_results) if pipeline.scripts_results else {}
        raw_script = scripts_data.get('script', '')
        
        if not raw_script:
            return jsonify({
                'success': False,
                'error': 'Roteiro não encontrado nos resultados da pipeline'
            }), 400
        
        # Processar roteiro
        script_processor = ScriptProcessingService()
        result = script_processor.process_script(
            pipeline_id=str(pipeline.id),
            raw_script=raw_script,
            config=config
        )
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': f"Falha no processamento: {result.get('error', 'Erro desconhecido')}"
            }), 500
        
        # Salvar resultado do processamento
        pipeline.script_processing_results = json.dumps({
            'processed_script': result['processed_script'],
            'original_script': raw_script,
            'processing_applied': True,
            'metrics': result['metrics'],
            'processing_time': result['processing_time'],
            'config_used': result['config_used'],
            'status': 'completed',
            'timestamp': result['timestamp']
        })
        
        # Atualizar roteiro nos scripts_results com versão processada
        scripts_data['script'] = result['processed_script']
        pipeline.scripts_results = json.dumps(scripts_data)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'pipeline_id': pipeline_id,
                'processed_script': result['processed_script'],
                'metrics': result['metrics'],
                'processing_time': result['processing_time']
            },
            'message': 'Roteiro processado com sucesso'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipelines_bp.route('/<pipeline_id>/script-processing-status', methods=['GET'])
def get_script_processing_status(pipeline_id):
    """Obter status do processamento de roteiro"""
    try:
        from app import Pipeline
        import json
        
        pipeline = Pipeline.query.get_or_404(pipeline_id)
        
        if not pipeline.script_processing_results:
            return jsonify({
                'success': True,
                'data': {
                    'status': 'not_processed',
                    'message': 'Roteiro ainda não foi processado'
                }
            })
        
        processing_data = json.loads(pipeline.script_processing_results)
        
        return jsonify({
            'success': True,
            'data': {
                'status': processing_data.get('status', 'unknown'),
                'processing_applied': processing_data.get('processing_applied', False),
                'metrics': processing_data.get('metrics', {}),
                'processing_time': processing_data.get('processing_time', 0),
                'timestamp': processing_data.get('timestamp'),
                'config_used': processing_data.get('config_used', {})
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pipelines_bp.route('/stats', methods=['GET'])
def get_pipeline_stats():
    """Obter estatísticas dos pipelines"""
    try:
        from app import Pipeline
        from sqlalchemy import func
        
        # Estatísticas por status
        status_stats = Pipeline.query.with_entities(
            Pipeline.status,
            func.count(Pipeline.id).label('count')
        ).group_by(Pipeline.status).all()
        
        # Pipelines ativos
        active_pipelines = Pipeline.query.filter(
            Pipeline.status.in_(['pending', 'processing'])
        ).count()
        
        # Taxa de sucesso
        total_pipelines = Pipeline.query.count()
        completed_pipelines = Pipeline.query.filter_by(status='completed').count()
        success_rate = (completed_pipelines / total_pipelines * 100) if total_pipelines > 0 else 0
        
        # Pipelines recentes
        recent_pipelines = Pipeline.query.order_by(
            Pipeline.started_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'status_distribution': {status: count for status, count in status_stats},
                'active_pipelines': active_pipelines,
                'total_pipelines': total_pipelines,
                'success_rate': round(success_rate, 2),
                'recent_pipelines': [p.to_dict() for p in recent_pipelines]
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
