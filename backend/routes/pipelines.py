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
