"""
🎥 Videos Routes
Rotas para gerenciamento de vídeos
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import os

videos_bp = Blueprint('videos', __name__)

@videos_bp.route('/', methods=['GET'])
def get_videos():
    """Listar todos os vídeos"""
    try:
        from app import Video
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')
        
        query = Video.query
        
        # Ordenação
        if hasattr(Video, sort_by):
            if order == 'desc':
                query = query.order_by(getattr(Video, sort_by).desc())
            else:
                query = query.order_by(getattr(Video, sort_by).asc())
        
        videos = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'videos': [video.to_dict() for video in videos.items],
                'total': videos.total,
                'pages': videos.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@videos_bp.route('/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """Obter vídeo específico"""
    try:
        from app import Video
        
        video = Video.query.get_or_404(video_id)
        
        return jsonify({
            'success': True,
            'data': video.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@videos_bp.route('/<int:video_id>/download', methods=['GET'])
def download_video(video_id):
    """Download do vídeo"""
    try:
        from app import Video, db
        
        video = Video.query.get_or_404(video_id)
        
        if not os.path.exists(video.file_path):
            return jsonify({
                'success': False,
                'error': 'Arquivo de vídeo não encontrado'
            }), 404
        
        # Incrementar contador de downloads
        video.download_count += 1
        db.session.commit()
        
        return send_file(
            video.file_path,
            as_attachment=True,
            download_name=f"{video.title}.mp4"
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@videos_bp.route('/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Deletar vídeo"""
    try:
        from app import Video, db
        
        video = Video.query.get_or_404(video_id)
        
        # Deletar arquivo físico se existir
        if os.path.exists(video.file_path):
            os.remove(video.file_path)
        
        # Deletar registro do banco
        db.session.delete(video)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vídeo deletado com sucesso'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@videos_bp.route('/stats', methods=['GET'])
def get_video_stats():
    """Obter estatísticas dos vídeos"""
    try:
        from app import Video
        from sqlalchemy import func
        
        # Estatísticas gerais
        total_videos = Video.query.count()
        total_duration = Video.query.with_entities(
            func.sum(Video.duration)
        ).scalar() or 0
        total_size = Video.query.with_entities(
            func.sum(Video.file_size)
        ).scalar() or 0
        total_downloads = Video.query.with_entities(
            func.sum(Video.download_count)
        ).scalar() or 0
        
        # Estatísticas por estilo
        style_stats = Video.query.with_entities(
            Video.video_style,
            func.count(Video.id).label('count')
        ).group_by(Video.video_style).all()
        
        # Vídeos mais baixados
        top_downloads = Video.query.order_by(
            Video.download_count.desc()
        ).limit(10).all()
        
        # Vídeos recentes
        recent_videos = Video.query.order_by(
            Video.created_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_videos': total_videos,
                'total_duration_minutes': round(total_duration / 60, 2),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_downloads': total_downloads,
                'avg_duration_minutes': round(total_duration / total_videos / 60, 2) if total_videos > 0 else 0,
                'style_distribution': {style: count for style, count in style_stats},
                'top_downloads': [v.to_dict() for v in top_downloads],
                'recent_videos': [v.to_dict() for v in recent_videos]
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@videos_bp.route('/bulk-download', methods=['POST'])
def bulk_download_videos():
    """Download em lote de vídeos"""
    try:
        from app import Video, db
        import zipfile
        import tempfile
        
        data = request.get_json()
        video_ids = data.get('video_ids', [])
        
        if not video_ids:
            return jsonify({
                'success': False,
                'error': 'Lista de IDs de vídeos é obrigatória'
            }), 400
        
        videos = Video.query.filter(Video.id.in_(video_ids)).all()
        
        if not videos:
            return jsonify({
                'success': False,
                'error': 'Nenhum vídeo encontrado'
            }), 404
        
        # Criar arquivo ZIP temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        with zipfile.ZipFile(temp_file.name, 'w') as zip_file:
            for video in videos:
                if os.path.exists(video.file_path):
                    zip_file.write(
                        video.file_path,
                        f"{video.title}.mp4"
                    )
                    # Incrementar contador de downloads
                    video.download_count += 1
        
        db.session.commit()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f"videos_bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
