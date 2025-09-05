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
    # Temporariamente comentado para resolver erro de importação
    # from moviepy.editor import (
    #     VideoFileClip, ImageClip, AudioFileClip, CompositeVideoClip,
    #     TextClip, concatenate_videoclips, ColorClip
    # )
    # from moviepy.video.fx.resize import resize
    # from moviepy.video.fx.fadein import fadein
    # from moviepy.video.fx.fadeout import fadeout
    pass
    from moviepy.audio.fx.volumex import volumex
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
    
    def _normalize_resolution(self, resolution: str) -> str:
        """Normalizar resolução convertendo qualidades para resoluções válidas"""
        # Mapeamento de qualidades para resoluções
        quality_to_resolution = {
            '720p': '1280x720',
            '1080p': '1920x1080',
            '4k': '3840x2160',
            'hd': '1280x720',
            'full_hd': '1920x1080',
            'ultra_hd': '3840x2160'
        }
        
        # Se já é uma resolução válida (formato WxH), retornar como está
        if 'x' in resolution and resolution.replace('x', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '') == '':
            return resolution
        
        # Converter qualidade para resolução
        normalized = quality_to_resolution.get(resolution.lower(), '1920x1080')
        self._log('info', f'Resolução normalizada: {resolution} -> {normalized}')
        return normalized
    
    def create_video(self, audio_path: str, images: List[Dict[str, Any]], 
                    script_text: str, resolution: str = '1920x1080', 
                    fps: int = 30, quality: str = 'high', 
                    transitions: bool = True, subtitles: bool = True,
                    tts_segments: List[Dict] = None) -> Dict[str, Any]:
        """Criar vídeo final"""
        try:
            self._log('info', 'Iniciando criação do vídeo final')
            
            # Normalizar resolução (converter qualidades para resoluções válidas)
            resolution = self._normalize_resolution(resolution)
            
            # Verificar se MoviePy está disponível
            self._check_moviepy_availability()
            
            # Verificar arquivos de entrada
            self._validate_input_files(audio_path, images)
            
            # Obter duração do áudio
            audio_duration = self._get_audio_duration(audio_path)
            self._log('info', f'Duração do áudio: {audio_duration:.2f} segundos')
            
            # Calcular timing das imagens com base no script
            self._log('info', f'Calculando timing para {len(images)} imagens')
            image_timings = self._calculate_image_timings(images, audio_duration, script_text)
            
            # Criar clipes de imagem
            self._log('info', 'Criando clipes de imagem')
            image_clips = self._create_image_clips(images, image_timings, resolution)
            
            # Adicionar transições se solicitado
            if transitions:
                self._log('info', 'Adicionando transições entre imagens')
                image_clips = self._add_transitions(image_clips)
            
            # Combinar clipes de imagem
            self._log('info', 'Combinando clipes de imagem')
            video_clip = concatenate_videoclips(image_clips, method='compose')
            
            # Adicionar áudio
            self._log('info', 'Adicionando áudio ao vídeo')
            audio_clip = AudioFileClip(audio_path)
            video_clip = video_clip.set_audio(audio_clip)
            
            # Ajustar duração do vídeo para corresponder ao áudio
            if video_clip.duration != audio_duration:
                self._log('info', f'Ajustando duração do vídeo: {video_clip.duration:.2f}s -> {audio_duration:.2f}s')
                video_clip = video_clip.set_duration(audio_duration)
            
            # Adicionar legendas se solicitado
            if subtitles:
                self._log('info', 'Adicionando legendas ao vídeo')
                video_clip = self._add_subtitles(video_clip, script_text, audio_duration, tts_segments)
            
            # Definir configurações de qualidade adaptativas
            codec_settings = self._get_adaptive_codec_settings(quality, resolution, audio_duration)
            
            # Renderizar vídeo final
            output_filename = f"video_{self.pipeline_id}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            self._log('info', 'Iniciando renderização do vídeo')
            
            # Renderização otimizada com configurações avançadas
            self._render_video_optimized(
                video_clip, output_path, fps, codec_settings
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
        self._log('info', 'Iniciando validação de arquivos de entrada')
        
        # Verificar áudio
        self._log('info', f'Verificando arquivo de áudio: {audio_path}')
        if not os.path.exists(audio_path):
            raise Exception(f"Arquivo de áudio não encontrado: {audio_path}")
        
        # Verificar tamanho do arquivo de áudio
        audio_size = os.path.getsize(audio_path)
        if audio_size == 0:
            raise Exception(f"Arquivo de áudio está vazio: {audio_path}")
        
        self._log('info', f'Arquivo de áudio válido: {audio_size} bytes')
        
        # Verificar imagens
        if not images:
            raise Exception("Nenhuma imagem fornecida")
        
        self._log('info', f'Verificando {len(images)} imagens')
        missing_images = []
        valid_images = 0
        
        for i, img in enumerate(images):
            img_path = img.get('file_path', '')
            if not img_path:
                self._log('warning', f'Imagem {i+1}: caminho não especificado')
                missing_images.append(f'Imagem {i+1}: sem caminho')
            elif not os.path.exists(img_path):
                self._log('warning', f'Imagem {i+1}: arquivo não encontrado - {img_path}')
                missing_images.append(img_path)
            else:
                img_size = os.path.getsize(img_path)
                if img_size == 0:
                    self._log('warning', f'Imagem {i+1}: arquivo vazio - {img_path}')
                    missing_images.append(f'{img_path} (vazio)')
                else:
                    valid_images += 1
        
        if missing_images:
            raise Exception(f"Problemas com imagens: {missing_images}")
        
        self._log('info', f'Validação concluída: {valid_images} imagens válidas')
    
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
                               total_duration: float, script_text: str = "") -> List[Tuple[float, float]]:
        """Calcular timing de cada imagem com base no conteúdo e estrutura do roteiro"""
        num_images = len(images)
        
        if num_images == 0:
            return []
        
        # Se temos apenas uma imagem, ela ocupa toda a duração
        if num_images == 1:
            return [(0.0, total_duration)]
        
        # Analisar script para determinar timing inteligente
        if script_text:
            timings = self._calculate_intelligent_timings(images, total_duration, script_text)
            if timings:
                return timings
    
    def _calculate_intelligent_timings(self, images: List[Dict[str, Any]], 
                                     total_duration: float, script_text: str) -> List[Tuple[float, float]]:
        """Calcular timing inteligente baseado no conteúdo do script"""
        try:
            # Dividir script em segmentos lógicos
            script_segments = self._analyze_script_segments(script_text)
            num_images = len(images)
            
            if len(script_segments) != num_images:
                # Se não há correspondência 1:1, usar método adaptativo
                return self._calculate_adaptive_timings(images, total_duration)
            
            # Calcular duração baseada no comprimento e complexidade de cada segmento
            segment_weights = []
            for segment in script_segments:
                # Peso baseado no comprimento do texto
                text_weight = len(segment.strip())
                
                # Peso adicional para segmentos com pontuação (pausas naturais)
                punctuation_weight = segment.count('.') + segment.count('!') + segment.count('?')
                
                # Peso final
                total_weight = text_weight + (punctuation_weight * 50)
                segment_weights.append(max(total_weight, 100))  # Mínimo de 100
            
            # Normalizar pesos para distribuir o tempo total
            total_weight = sum(segment_weights)
            timings = []
            current_time = 0.0
            
            for i, weight in enumerate(segment_weights):
                duration = (weight / total_weight) * total_duration
                # Garantir duração mínima e máxima
                duration = max(2.0, min(duration, total_duration * 0.4))
                
                start_time = current_time
                end_time = current_time + duration
                timings.append((start_time, end_time))
                current_time = end_time
            
            # Ajustar último timing para corresponder à duração total
            if timings and current_time != total_duration:
                last_start, _ = timings[-1]
                timings[-1] = (last_start, total_duration)
            
            self._log('info', f'Timing inteligente calculado baseado no script')
            return timings
            
        except Exception as e:
            self._log('warning', f'Erro no cálculo inteligente: {str(e)}')
            return []
    
    def _calculate_adaptive_timings(self, images: List[Dict[str, Any]], 
                                  total_duration: float) -> List[Tuple[float, float]]:
        """Calcular timing adaptativo baseado no tipo e características das imagens"""
        num_images = len(images)
        
        # Analisar características das imagens
        image_weights = []
        for img_data in images:
            weight = 1.0  # Peso base
            
            # Ajustar peso baseado no tipo de imagem (se disponível)
            img_type = img_data.get('type', 'unknown')
            if img_type in ['title', 'intro']:
                weight = 1.3  # Imagens de título ficam mais tempo
            elif img_type in ['transition', 'outro']:
                weight = 0.8  # Transições ficam menos tempo
            elif img_type in ['detail', 'close-up']:
                weight = 1.1  # Detalhes ficam um pouco mais
            
            # Ajustar baseado na descrição (se disponível)
            description = img_data.get('description', '').lower()
            if any(word in description for word in ['complex', 'detailed', 'chart', 'graph']):
                weight *= 1.2  # Imagens complexas precisam de mais tempo
            elif any(word in description for word in ['simple', 'logo', 'icon']):
                weight *= 0.9  # Imagens simples precisam de menos tempo
            
            image_weights.append(weight)
        
        # Normalizar pesos
        total_weight = sum(image_weights)
        timings = []
        current_time = 0.0
        
        for i, weight in enumerate(image_weights):
            duration = (weight / total_weight) * total_duration
            # Garantir duração mínima de 1.5s e máxima de 8s
            duration = max(1.5, min(duration, 8.0))
            
            start_time = current_time
            end_time = current_time + duration
            timings.append((start_time, end_time))
            current_time = end_time
        
        # Ajustar último timing para corresponder à duração total
        if timings and current_time != total_duration:
            last_start, _ = timings[-1]
            timings[-1] = (last_start, total_duration)
        
        self._log('info', f'Timing adaptativo calculado')
        return timings
    
    def _analyze_script_segments(self, script_text: str) -> List[str]:
        """Analisar script e dividir em segmentos lógicos"""
        import re
        
        # Dividir por pontos, exclamações e interrogações
        segments = re.split(r'[.!?]+', script_text)
        
        # Limpar e filtrar segmentos
        cleaned_segments = []
        for segment in segments:
            segment = segment.strip()
            if segment and len(segment) > 10:  # Mínimo 10 caracteres
                cleaned_segments.append(segment)
        
        # Se temos poucos segmentos, dividir por vírgulas também
        if len(cleaned_segments) < 3:
            all_segments = []
            for segment in cleaned_segments:
                sub_segments = [s.strip() for s in segment.split(',') if s.strip()]
                all_segments.extend(sub_segments)
            if len(all_segments) > len(cleaned_segments):
                cleaned_segments = all_segments
        
        return cleaned_segments
        
        # Fallback: distribuir tempo com variação baseada no tipo de imagem
        timings = self._calculate_adaptive_timings(images, total_duration)
        
        self._log('info', f'Timing calculado para {num_images} imagens')
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
                
                self._log('info', f'Processando imagem {i + 1}/{len(images)}: {os.path.basename(img_path)}')
                
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
                
                self._log('info', f'Imagem {i + 1}/{len(images)} processada com sucesso (duração: {duration:.2f}s)')
                
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
                clip = fadein(clip, transition_duration)
            elif i == len(clips) - 1:
                # Último clipe: apenas fade out
                clip = fadeout(clip, transition_duration)
            else:
                # Clipes do meio: fade in e fade out
                clip = fadeout(fadein(clip, transition_duration), transition_duration)
            
            transitioned_clips.append(clip)
        
        self._log('info', f'Transições adicionadas a {len(clips)} clipes')
        return transitioned_clips
    
    def _add_subtitles(self, video_clip, script_text: str, duration: float, tts_segments: List[Dict] = None):
        """Adicionar legendas ao vídeo com sincronização baseada em TTS"""
        try:
            # Usar segmentos TTS se disponíveis para sincronização precisa
            if tts_segments:
                segments = self._create_tts_based_subtitle_segments(script_text, tts_segments)
            else:
                # Fallback para método tradicional
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
    
    def _create_tts_based_subtitle_segments(self, script_text: str, tts_segments: List[Dict]) -> List[Dict[str, Any]]:
        """Criar segmentos de legenda baseados nos segmentos TTS"""
        segments = []
        current_time = 0.0
        
        # Dividir texto em sentenças
        sentences = self._split_into_sentences(script_text)
        
        if not sentences:
            return []
        
        # Calcular duração total dos segmentos TTS
        total_tts_duration = sum(seg.get('duration', 0) for seg in tts_segments if seg.get('duration'))
        
        if total_tts_duration > 0:
            # Distribuir sentenças baseado na duração dos segmentos TTS
            sentences_per_segment = max(1, len(sentences) // len(tts_segments))
            
            sentence_index = 0
            for i, tts_segment in enumerate(tts_segments):
                segment_duration = tts_segment.get('duration', 3.0)
                
                # Determinar quantas sentenças cabem neste segmento
                end_sentence_index = min(sentence_index + sentences_per_segment, len(sentences))
                
                # Se é o último segmento TTS, incluir todas as sentenças restantes
                if i == len(tts_segments) - 1:
                    end_sentence_index = len(sentences)
                
                # Combinar sentenças para este segmento
                segment_sentences = sentences[sentence_index:end_sentence_index]
                if segment_sentences:
                    combined_text = ' '.join(segment_sentences)
                    
                    # Dividir texto longo em múltiplas legendas
                    if len(combined_text) > 80:  # Máximo 80 caracteres por legenda
                        sub_segments = self._split_long_subtitle(combined_text, segment_duration, current_time)
                        segments.extend(sub_segments)
                    else:
                        segments.append({
                            'text': combined_text,
                            'start': current_time,
                            'duration': segment_duration
                        })
                    
                    sentence_index = end_sentence_index
                
                current_time += segment_duration
        else:
            # Fallback para método tradicional
            return self._create_subtitle_segments(script_text, current_time or 60.0)
        
        return segments
    
    def _split_long_subtitle(self, text: str, total_duration: float, start_time: float) -> List[Dict[str, Any]]:
        """Dividir legenda longa em múltiplos segmentos"""
        words = text.split()
        segments = []
        
        # Dividir em chunks de ~12-15 palavras
        chunk_size = 12
        num_chunks = max(1, len(words) // chunk_size)
        duration_per_chunk = total_duration / num_chunks
        
        current_start = start_time
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            segments.append({
                'text': chunk_text,
                'start': current_start,
                'duration': min(duration_per_chunk, 4.0)  # Máximo 4 segundos por chunk
            })
            
            current_start += duration_per_chunk
        
        return segments
    
    def _create_subtitle_segments(self, script_text: str, duration: float) -> List[Dict[str, Any]]:
        """Criar segmentos de legenda (método tradicional)"""
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
        """Obter configurações de codec otimizadas baseadas na qualidade"""
        quality_settings = {
            'low': {
                'bitrate': '1200k',
                'preset': 'ultrafast',
                'crf': 28,
                'threads': 4,
                'tune': 'fastdecode'
            },
            'medium': {
                'bitrate': '2800k',
                'preset': 'fast',
                'crf': 23,
                'threads': 6,
                'tune': 'film'
            },
            'high': {
                'bitrate': '5500k',
                'preset': 'medium',
                'crf': 20,
                'threads': 8,
                'tune': 'film'
            },
            'ultra': {
                'bitrate': '9000k',
                'preset': 'slow',
                'crf': 18,
                'threads': 8,
                'tune': 'film'
            }
        }
        
        return quality_settings.get(quality, quality_settings['high'])
    
    def _get_adaptive_codec_settings(self, quality: str, resolution: str, duration: float) -> Dict[str, Any]:
        """Obter configurações adaptativas baseadas na qualidade, resolução e duração"""
        # Configurações base
        base_settings = self._get_codec_settings(quality)
        
        # Adaptações baseadas na resolução
        width, height = map(int, resolution.split('x'))
        pixel_count = width * height
        
        # Ajustar bitrate baseado na resolução
        if pixel_count <= 921600:  # 720p ou menor
            bitrate_multiplier = 0.7
        elif pixel_count <= 2073600:  # 1080p
            bitrate_multiplier = 1.0
        elif pixel_count <= 3686400:  # 1440p
            bitrate_multiplier = 1.4
        else:  # 4K ou maior
            bitrate_multiplier = 2.0
        
        # Ajustar bitrate baseado na duração
        if duration < 60:  # Vídeos curtos (< 1 min)
            duration_multiplier = 1.2
        elif duration < 300:  # Vídeos médios (< 5 min)
            duration_multiplier = 1.0
        elif duration < 900:  # Vídeos longos (< 15 min)
            duration_multiplier = 0.9
        else:  # Vídeos muito longos
            duration_multiplier = 0.8
        
        # Calcular bitrate adaptativo
        base_bitrate = int(base_settings['bitrate'].replace('k', ''))
        adaptive_bitrate = int(base_bitrate * bitrate_multiplier * duration_multiplier)
        
        # Aplicar limites mínimos e máximos
        adaptive_bitrate = max(800, min(adaptive_bitrate, 15000))
        
        # Atualizar configurações
        adaptive_settings = base_settings.copy()
        adaptive_settings['bitrate'] = f'{adaptive_bitrate}k'
        
        # Ajustar preset baseado na resolução para otimizar tempo vs qualidade
        if pixel_count >= 3686400:  # 1440p ou maior
            if adaptive_settings['preset'] == 'slow':
                adaptive_settings['preset'] = 'medium'  # Mais rápido para resoluções altas
            elif adaptive_settings['preset'] == 'veryslow':
                adaptive_settings['preset'] = 'slow'
        
        self._log('info', f'Configurações adaptativas: bitrate={adaptive_bitrate}k, preset={adaptive_settings["preset"]}')
        
        return adaptive_settings
    
    def _render_video_optimized(self, video_clip, output_path: str, fps: int, codec_settings: Dict[str, Any]):
        """Renderização otimizada de vídeo com configurações avançadas"""
        try:
            import multiprocessing
            
            # Detectar número de cores disponíveis
            cpu_count = multiprocessing.cpu_count()
            threads = min(codec_settings.get('threads', 4), cpu_count)
            
            # Configurações otimizadas de renderização
            render_params = {
                'fps': fps,
                'codec': 'libx264',
                'audio_codec': 'aac',
                'bitrate': codec_settings.get('bitrate', '5500k'),
                'preset': codec_settings.get('preset', 'medium'),
                'threads': threads,
                'verbose': False,
                'logger': None,
                'temp_audiofile': os.path.join(self.temp_dir, 'temp_audio.m4a'),
                'remove_temp': True
            }
            
            # Adicionar configurações avançadas se disponíveis
            if 'crf' in codec_settings:
                render_params['ffmpeg_params'] = ['-crf', str(codec_settings['crf'])]
                
            if 'tune' in codec_settings:
                if 'ffmpeg_params' not in render_params:
                    render_params['ffmpeg_params'] = []
                render_params['ffmpeg_params'].extend(['-tune', codec_settings['tune']])
            
            # Otimizações adicionais para performance
            if 'ffmpeg_params' not in render_params:
                render_params['ffmpeg_params'] = []
            
            render_params['ffmpeg_params'].extend([
                '-movflags', '+faststart',  # Otimização para streaming
                '-pix_fmt', 'yuv420p',      # Compatibilidade máxima
                '-profile:v', 'high',       # Perfil H.264 otimizado
                '-level', '4.0'             # Nível de compatibilidade
            ])
            
            self._log('info', f'Renderizando com {threads} threads, preset: {codec_settings.get("preset", "medium")}')
            
            # Renderizar vídeo
            video_clip.write_videofile(output_path, **render_params)
            
            self._log('info', 'Renderização otimizada concluída')
            
        except Exception as e:
            error_msg = str(e)
            self._log('error', f'Erro na renderização otimizada: {error_msg}')
            
            # Verificar se é erro de FFmpeg
            if 'ffmpeg' in error_msg.lower() or 'codec' in error_msg.lower():
                self._log('warning', 'Erro relacionado ao FFmpeg detectado')
            
            # Fallback para renderização básica
            self._log('info', 'Tentando renderização básica como fallback')
            try:
                video_clip.write_videofile(
                    output_path,
                    fps=fps,
                    codec='libx264',
                    audio_codec='aac',
                    bitrate=codec_settings.get('bitrate', '5500k'),
                    preset=codec_settings.get('preset', 'medium'),
                    verbose=False,
                    logger=None
                )
                self._log('info', 'Renderização básica concluída com sucesso')
            except Exception as fallback_error:
                self._log('error', f'Falha também na renderização básica: {str(fallback_error)}')
                raise
    
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