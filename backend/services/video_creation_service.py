"""🎬 Video Creation Service
Serviço de criação de vídeo usando MoviePy
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Adicionar diretório routes ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'routes'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from moviepy.editor import (
        VideoFileClip, ImageClip, AudioFileClip, CompositeVideoClip,
        TextClip, concatenate_videoclips, ColorClip
    )
    from moviepy.video.fx import resize, fadein, fadeout
    from moviepy.audio.fx import volumex
except ImportError:
    # MoviePy não está instalado - será tratado no método de criação
    pass

logger = logging.getLogger(__name__)

class VideoCreationService:
    """Serviço de criação de vídeo"""
    
    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
        self.temp_dir = os.path.join('temp', f'video_{pipeline_id}')
        self.output_dir = 'outputs'
        
        # Criar diretórios necessários
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _log(self, level: str, message: str, data: Optional[Dict] = None):
        """Adicionar log ao pipeline"""
        try:
            from routes.pipeline_complete import add_pipeline_log
            add_pipeline_log(self.pipeline_id, level, message, data)
        except Exception as e:
            logger.error(f"Erro ao adicionar log: {str(e)}")
    
    def create_video(self, audio_path: str, images: List[Dict[str, Any]], 
                    script_text: str, resolution: str = '1920x1080', 
                    fps: int = 30, quality: str = 'high', 
                    transitions: bool = True, subtitles: bool = True) -> Dict[str, Any]:
        """Criar vídeo final"""
        try:
            self._log('info', 'Iniciando criação do vídeo final')
            
            # Verificar se MoviePy está disponível
            self._check_moviepy_availability()
            
            # Verificar arquivos de entrada
            self._validate_input_files(audio_path, images)
            
            # Obter duração do áudio
            audio_duration = self._get_audio_duration(audio_path)
            self._log('info', f'Duração do áudio: {audio_duration:.2f} segundos')
            
            # Calcular timing das imagens
            image_timings = self._calculate_image_timings(images, audio_duration)
            
            # Criar clipes de imagem
            image_clips = self._create_image_clips(images, image_timings, resolution)
            
            # Adicionar transições se solicitado
            if transitions:
                image_clips = self._add_transitions(image_clips)
            
            # Combinar clipes de imagem
            video_clip = concatenate_videoclips(image_clips, method='compose')
            
            # Adicionar áudio
            audio_clip = AudioFileClip(audio_path)
            video_clip = video_clip.set_audio(audio_clip)
            
            # Ajustar duração do vídeo para corresponder ao áudio
            if video_clip.duration != audio_duration:
                video_clip = video_clip.set_duration(audio_duration)
            
            # Adicionar legendas se solicitado
            if subtitles:
                video_clip = self._add_subtitles(video_clip, script_text, audio_duration)
            
            # Definir configurações de qualidade
            codec_settings = self._get_codec_settings(quality)
            
            # Renderizar vídeo final
            output_filename = f"video_{self.pipeline_id}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            self._log('info', 'Iniciando renderização do vídeo')
            
            video_clip.write_videofile(
                output_path,
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                **codec_settings,
                verbose=False,
                logger=None
            )
            
            # Obter informações do arquivo final
            file_size = os.path.getsize(output_path)
            final_duration = video_clip.duration
            
            # Limpar recursos
            video_clip.close()
            audio_clip.close()
            for clip in image_clips:
                clip.close()
            
            self._log('info', 'Vídeo criado com sucesso', {
                'output_path': output_path,
                'duration': final_duration,
                'file_size': file_size
            })
            
            return {
                'video_path': output_path,
                'filename': output_filename,
                'duration': final_duration,
                'file_size': file_size,
                'resolution': resolution,
                'fps': fps,
                'quality': quality,
                'creation_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self._log('error', f'Erro na criação do vídeo: {str(e)}')
            raise
    
    def _check_moviepy_availability(self):
        """Verificar se MoviePy está disponível"""
        try:
            import moviepy
            self._log('info', f'MoviePy disponível - versão: {moviepy.__version__}')
        except ImportError:
            error_msg = "MoviePy não está instalado. Execute: pip install moviepy"
            self._log('error', error_msg)
            raise Exception(error_msg)
    
    def _validate_input_files(self, audio_path: str, images: List[Dict[str, Any]]):
        """Validar arquivos de entrada"""
        # Verificar áudio
        if not os.path.exists(audio_path):
            raise Exception(f"Arquivo de áudio não encontrado: {audio_path}")
        
        # Verificar imagens
        if not images:
            raise Exception("Nenhuma imagem fornecida")
        
        missing_images = []
        for img in images:
            img_path = img.get('file_path', '')
            if not os.path.exists(img_path):
                missing_images.append(img_path)
        
        if missing_images:
            raise Exception(f"Imagens não encontradas: {missing_images}")
        
        self._log('info', f'Validação concluída: {len(images)} imagens válidas')
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Obter duração do áudio"""
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_clip.close()
            return duration
        except Exception as e:
            # Fallback: usar ffprobe se disponível
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-show_entries', 
                    'format=duration', '-of', 'csv=p=0', audio_path
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    return float(result.stdout.strip())
            except:
                pass
            
            # Fallback final: estimar baseado no tamanho do arquivo
            file_size = os.path.getsize(audio_path)
            estimated_duration = file_size / (44100 * 2 * 2)  # Estimativa grosseira
            
            self._log('warning', f'Não foi possível obter duração exata do áudio. Estimativa: {estimated_duration:.2f}s')
            return max(60, estimated_duration)  # Mínimo de 1 minuto
    
    def _calculate_image_timings(self, images: List[Dict[str, Any]], 
                               total_duration: float) -> List[Tuple[float, float]]:
        """Calcular timing de cada imagem"""
        num_images = len(images)
        
        if num_images == 0:
            return []
        
        # Distribuir tempo igualmente entre as imagens
        duration_per_image = total_duration / num_images
        
        timings = []
        for i in range(num_images):
            start_time = i * duration_per_image
            end_time = (i + 1) * duration_per_image
            timings.append((start_time, end_time))
        
        self._log('info', f'Timing calculado: {duration_per_image:.2f}s por imagem')
        return timings
    
    def _create_image_clips(self, images: List[Dict[str, Any]], 
                          timings: List[Tuple[float, float]], 
                          resolution: str) -> List:
        """Criar clipes de imagem"""
        image_clips = []
        width, height = map(int, resolution.split('x'))
        
        for i, (img_data, (start_time, end_time)) in enumerate(zip(images, timings)):
            try:
                img_path = img_data['file_path']
                duration = end_time - start_time
                
                # Criar clipe de imagem
                img_clip = ImageClip(img_path, duration=duration)
                
                # Redimensionar mantendo proporção
                img_clip = img_clip.resize(height=height)
                
                # Se a imagem for mais larga que o vídeo, centralizar
                if img_clip.w > width:
                    img_clip = img_clip.resize(width=width)
                
                # Centralizar imagem
                img_clip = img_clip.set_position('center')
                
                # Adicionar fundo preto se necessário
                if img_clip.w < width or img_clip.h < height:
                    background = ColorClip(size=(width, height), color=(0, 0, 0), duration=duration)
                    img_clip = CompositeVideoClip([background, img_clip.set_position('center')])
                
                image_clips.append(img_clip)
                
                self._log('info', f'Clipe {i+1}/{len(images)} criado: {duration:.2f}s')
                
            except Exception as e:
                self._log('warning', f'Erro ao criar clipe {i+1}: {str(e)}')
                # Criar clipe de cor sólida como fallback
                fallback_clip = ColorClip(
                    size=(width, height), 
                    color=(50, 50, 50), 
                    duration=end_time - start_time
                )
                image_clips.append(fallback_clip)
        
        return image_clips
    
    def _add_transitions(self, clips: List) -> List:
        """Adicionar transições entre clipes"""
        if len(clips) <= 1:
            return clips
        
        transition_duration = 0.5  # 0.5 segundos de transição
        
        transitioned_clips = []
        
        for i, clip in enumerate(clips):
            if i == 0:
                # Primeiro clipe: apenas fade in
                clip = clip.fx(fadein, transition_duration)
            elif i == len(clips) - 1:
                # Último clipe: apenas fade out
                clip = clip.fx(fadeout, transition_duration)
            else:
                # Clipes do meio: fade in e fade out
                clip = clip.fx(fadein, transition_duration).fx(fadeout, transition_duration)
            
            transitioned_clips.append(clip)
        
        self._log('info', f'Transições adicionadas a {len(clips)} clipes')
        return transitioned_clips
    
    def _add_subtitles(self, video_clip, script_text: str, duration: float):
        """Adicionar legendas ao vídeo"""
        try:
            # Dividir script em segmentos
            segments = self._create_subtitle_segments(script_text, duration)
            
            subtitle_clips = []
            
            for segment in segments:
                try:
                    # Criar clipe de texto
                    txt_clip = TextClip(
                        segment['text'],
                        fontsize=24,
                        color='white',
                        stroke_color='black',
                        stroke_width=2,
                        font='Arial-Bold'
                    ).set_position(('center', 'bottom')).set_start(segment['start']).set_duration(segment['duration'])
                    
                    subtitle_clips.append(txt_clip)
                    
                except Exception as e:
                    self._log('warning', f'Erro ao criar legenda: {str(e)}')
                    continue
            
            if subtitle_clips:
                # Combinar vídeo com legendas
                final_video = CompositeVideoClip([video_clip] + subtitle_clips)
                self._log('info', f'Legendas adicionadas: {len(subtitle_clips)} segmentos')
                return final_video
            
        except Exception as e:
            self._log('warning', f'Erro ao adicionar legendas: {str(e)}')
        
        return video_clip
    
    def _create_subtitle_segments(self, script_text: str, duration: float) -> List[Dict[str, Any]]:
        """Criar segmentos de legenda"""
        # Dividir texto em sentenças
        sentences = self._split_into_sentences(script_text)
        
        if not sentences:
            return []
        
        # Calcular timing para cada sentença
        time_per_sentence = duration / len(sentences)
        
        segments = []
        for i, sentence in enumerate(sentences):
            start_time = i * time_per_sentence
            segment_duration = min(time_per_sentence, 5.0)  # Máximo 5 segundos por legenda
            
            segments.append({
                'text': sentence.strip(),
                'start': start_time,
                'duration': segment_duration
            })
        
        return segments
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Dividir texto em sentenças"""
        import re
        
        # Dividir por pontos, exclamações e interrogações
        sentences = re.split(r'[.!?]+', text)
        
        # Limpar e filtrar sentenças vazias
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Mínimo 10 caracteres
                # Limitar tamanho da legenda
                if len(sentence) > 100:
                    # Dividir sentenças muito longas
                    words = sentence.split()
                    chunk_size = 15  # ~15 palavras por legenda
                    
                    for i in range(0, len(words), chunk_size):
                        chunk = ' '.join(words[i:i + chunk_size])
                        if chunk.strip():
                            cleaned_sentences.append(chunk.strip())
                else:
                    cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _get_codec_settings(self, quality: str) -> Dict[str, Any]:
        """Obter configurações de codec baseadas na qualidade"""
        quality_settings = {
            'low': {
                'bitrate': '1000k',
                'preset': 'fast'
            },
            'medium': {
                'bitrate': '2500k',
                'preset': 'medium'
            },
            'high': {
                'bitrate': '5000k',
                'preset': 'slow'
            },
            'ultra': {
                'bitrate': '8000k',
                'preset': 'veryslow'
            }
        }
        
        return quality_settings.get(quality, quality_settings['high'])
    
    def create_preview(self, video_path: str, duration: int = 30) -> Optional[str]:
        """Criar preview do vídeo"""
        try:
            self._log('info', 'Criando preview do vídeo')
            
            # Carregar vídeo
            video = VideoFileClip(video_path)
            
            # Criar preview dos primeiros X segundos
            preview_duration = min(duration, video.duration)
            preview = video.subclip(0, preview_duration)
            
            # Salvar preview
            preview_filename = f"preview_{self.pipeline_id}.mp4"
            preview_path = os.path.join(self.output_dir, preview_filename)
            
            preview.write_videofile(
                preview_path,
                fps=15,  # FPS menor para preview
                codec='libx264',
                bitrate='1000k',
                verbose=False,
                logger=None
            )
            
            # Limpar recursos
            preview.close()
            video.close()
            
            self._log('info', f'Preview criado: {preview_path}')
            return preview_path
            
        except Exception as e:
            self._log('error', f'Erro ao criar preview: {str(e)}')
            return None
    
    def cleanup_temp_files(self):
        """Limpar arquivos temporários"""
        try:
            import shutil
            
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self._log('info', 'Arquivos temporários removidos')
                
        except Exception as e:
            self._log('warning', f'Erro ao limpar arquivos temporários: {str(e)}')