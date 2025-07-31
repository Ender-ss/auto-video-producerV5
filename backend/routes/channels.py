"""
📺 Channels Routes
Rotas para gerenciamento de canais
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

channels_bp = Blueprint('channels', __name__)

@channels_bp.route('/', methods=['GET'])
def get_channels():
    """Listar todos os canais"""
    try:
        from app import Channel
        
        channels = Channel.query.all()
        
        return jsonify({
            'success': True,
            'data': {
                'channels': [channel.to_dict() for channel in channels],
                'total': len(channels),
                'active': len([c for c in channels if c.is_active])
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channels_bp.route('/', methods=['POST'])
def create_channel():
    """Criar novo canal"""
    try:
        from app import Channel, db
        
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['name', 'channel_id', 'url']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo {field} é obrigatório'
                }), 400
        
        # Verificar se canal já existe
        existing_channel = Channel.query.filter_by(channel_id=data['channel_id']).first()
        if existing_channel:
            return jsonify({
                'success': False,
                'error': 'Canal já existe'
            }), 400
        
        # Criar novo canal
        channel = Channel(
            name=data['name'],
            channel_id=data['channel_id'],
            url=data['url'],
            video_style=data.get('video_style', 'motivational'),
            max_videos_per_day=data.get('max_videos_per_day', 2),
            min_views_threshold=data.get('min_views_threshold', 1000)
        )
        
        db.session.add(channel)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': channel.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channels_bp.route('/<int:channel_id>', methods=['GET'])
def get_channel(channel_id):
    """Obter canal específico"""
    try:
        from app import Channel
        
        channel = Channel.query.get_or_404(channel_id)
        
        return jsonify({
            'success': True,
            'data': channel.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channels_bp.route('/<int:channel_id>', methods=['PUT'])
def update_channel(channel_id):
    """Atualizar canal"""
    try:
        from app import Channel, db
        
        channel = Channel.query.get_or_404(channel_id)
        data = request.get_json()
        
        # Atualizar campos permitidos
        allowed_fields = [
            'name', 'url', 'is_active', 'video_style', 
            'max_videos_per_day', 'min_views_threshold'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(channel, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': channel.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channels_bp.route('/<int:channel_id>', methods=['DELETE'])
def delete_channel(channel_id):
    """Deletar canal"""
    try:
        from app import Channel, db
        
        channel = Channel.query.get_or_404(channel_id)
        
        db.session.delete(channel)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Canal deletado com sucesso'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channels_bp.route('/<int:channel_id>/toggle', methods=['POST'])
def toggle_channel_status(channel_id):
    """Ativar/desativar canal"""
    try:
        from app import Channel, db
        
        channel = Channel.query.get_or_404(channel_id)
        channel.is_active = not channel.is_active
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': channel.to_dict(),
            'message': f'Canal {"ativado" if channel.is_active else "desativado"} com sucesso'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channels_bp.route('/<int:channel_id>/stats', methods=['GET'])
def get_channel_stats(channel_id):
    """Obter estatísticas do canal"""
    try:
        from app import Channel, Pipeline, Video
        
        channel = Channel.query.get_or_404(channel_id)
        
        # Estatísticas de pipelines
        total_pipelines = Pipeline.query.filter_by(channel_id=channel_id).count()
        completed_pipelines = Pipeline.query.filter_by(
            channel_id=channel_id, 
            status='completed'
        ).count()
        
        # Estatísticas de vídeos
        total_videos = Video.query.filter_by(channel_id=channel_id).count()
        total_duration = Video.query.filter_by(channel_id=channel_id).with_entities(
            Video.duration
        ).all()
        total_duration = sum([v.duration for v in total_duration]) if total_duration else 0
        
        # Taxa de sucesso
        success_rate = (completed_pipelines / total_pipelines * 100) if total_pipelines > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'channel': channel.to_dict(),
                'statistics': {
                    'total_pipelines': total_pipelines,
                    'completed_pipelines': completed_pipelines,
                    'success_rate': round(success_rate, 2),
                    'total_videos': total_videos,
                    'total_duration_minutes': round(total_duration / 60, 2),
                    'avg_video_duration': round(total_duration / total_videos / 60, 2) if total_videos > 0 else 0
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channels_bp.route('/bulk-import', methods=['POST'])
def bulk_import_channels():
    """Importar múltiplos canais"""
    try:
        from app import Channel, db
        
        data = request.get_json()
        channels_data = data.get('channels', [])
        
        if not channels_data:
            return jsonify({
                'success': False,
                'error': 'Lista de canais é obrigatória'
            }), 400
        
        created_channels = []
        errors = []
        
        for channel_data in channels_data:
            try:
                # Verificar se canal já existe
                existing = Channel.query.filter_by(
                    channel_id=channel_data['channel_id']
                ).first()
                
                if existing:
                    errors.append(f"Canal {channel_data['name']} já existe")
                    continue
                
                # Criar novo canal
                channel = Channel(
                    name=channel_data['name'],
                    channel_id=channel_data['channel_id'],
                    url=channel_data['url'],
                    video_style=channel_data.get('video_style', 'motivational'),
                    max_videos_per_day=channel_data.get('max_videos_per_day', 2),
                    min_views_threshold=channel_data.get('min_views_threshold', 1000)
                )
                
                db.session.add(channel)
                created_channels.append(channel_data['name'])
                
            except Exception as e:
                errors.append(f"Erro ao criar canal {channel_data.get('name', 'desconhecido')}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'created_count': len(created_channels),
                'created_channels': created_channels,
                'errors': errors
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
