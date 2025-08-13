"""
🎥 Videos Routes
Rotas para gerenciamento de vídeos
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import os
import json
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image
import tempfile
import shutil

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


@videos_bp.route('/create', methods=['POST'])
def create_video():
    """Criar vídeo a partir de áudio e imagens"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['audio_file', 'images', 'title']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400
        
        audio_file = data['audio_file']
        images = data['images']  # Lista de caminhos das imagens
        title = data['title']
        
        # Configurações opcionais
        config = data.get('config', {})
        resolution = config.get('resolution', '1920x1080')
        fps = config.get('fps', 30)
        transition_duration = config.get('transition_duration', 0.5)
        
        # Validar se arquivos existem
        if not os.path.exists(audio_file):
            return jsonify({
                'success': False,
                'error': f'Arquivo de áudio não encontrado: {audio_file}'
            }), 400
        
        for img_path in images:
            if not os.path.exists(img_path):
                return jsonify({
                    'success': False,
                    'error': f'Imagem não encontrada: {img_path}'
                }), 400
        
        # Criar vídeo
        video_path = _create_video_from_assets(
            audio_file=audio_file,
            images=images,
            title=title,
            resolution=resolution,
            fps=fps,
            transition_duration=transition_duration
        )
        
        # Salvar no banco de dados
        from app import Video, db
        
        video = Video(
            title=title,
            file_path=video_path,
            duration=_get_video_duration(video_path),
            file_size=os.path.getsize(video_path),
            resolution=resolution,
            fps=fps,
            status='completed'
        )
        
        db.session.add(video)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'video_id': video.id,
                'video_path': video_path,
                'title': title,
                'duration': video.duration,
                'file_size': video.file_size,
                'resolution': resolution,
                'fps': fps
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao criar vídeo: {str(e)}'
        }), 500


def _create_video_from_assets(audio_file, images, title, resolution='1920x1080', fps=30, transition_duration=0.5):
    """Função auxiliar para criar vídeo a partir de áudio e imagens"""
    try:
        # Carregar áudio
        audio = AudioFileClip(audio_file)
        audio_duration = audio.duration
        
        # Calcular duração por imagem
        num_images = len(images)
        if num_images == 0:
            raise ValueError("Nenhuma imagem fornecida")
        
        duration_per_image = audio_duration / num_images
        
        # Processar resolução
        width, height = map(int, resolution.split('x'))
        
        # Criar clips de vídeo para cada imagem
        video_clips = []
        
        for i, img_path in enumerate(images):
            # Redimensionar imagem para a resolução desejada
            img = Image.open(img_path)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Salvar imagem redimensionada temporariamente
            temp_img_path = f"temp_resized_{i}_{os.path.basename(img_path)}"
            img.save(temp_img_path)
            
            # Criar clip de vídeo
            clip = ImageClip(temp_img_path, duration=duration_per_image)
            clip = clip.set_fps(fps)
            
            video_clips.append(clip)
            
            # Limpar arquivo temporário
            os.remove(temp_img_path)
        
        # Concatenar clips
        if transition_duration > 0:
            # Adicionar transições suaves
            final_clips = []
            for i, clip in enumerate(video_clips):
                if i > 0:
                    # Fade in
                    clip = clip.fadein(transition_duration)
                if i < len(video_clips) - 1:
                    # Fade out
                    clip = clip.fadeout(transition_duration)
                final_clips.append(clip)
            
            video = concatenate_videoclips(final_clips, method="compose")
        else:
            video = concatenate_videoclips(video_clips)
        
        # Adicionar áudio
        final_video = video.set_audio(audio)
        
        # Definir caminho de saída
        output_dir = "output/videos"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        output_path = os.path.join(output_dir, f"{safe_title}_{timestamp}.mp4")
        
        # Renderizar vídeo
        final_video.write_videofile(
            output_path,
            fps=fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Limpar recursos
        audio.close()
        video.close()
        final_video.close()
        
        return output_path
    
    except Exception as e:
        raise Exception(f"Erro na criação do vídeo: {str(e)}")


def _get_video_duration(video_path):
    """Obter duração do vídeo em segundos"""
    try:
        from moviepy.editor import VideoFileClip
        with VideoFileClip(video_path) as clip:
            return clip.duration
    except Exception:
        return 0.0
