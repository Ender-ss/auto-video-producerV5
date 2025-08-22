"""🎵 TTS Service
Serviço de geração de áudio Text-to-Speech para a pipeline
"""

import os
import sys
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Adicionar diretório routes ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'routes'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importar funções de TTS da aba de automações
try:
    from routes.automations import (
        generate_tts_with_gemini,
        generate_tts_with_elevenlabs,
        generate_tts_with_kokoro
    )
except ImportError as e:
    logging.warning(f"Erro ao importar funções de TTS: {e}")
    generate_tts_with_gemini = None
    generate_tts_with_elevenlabs = None
    generate_tts_with_kokoro = None

logger = logging.getLogger(__name__)

class TTSService:
    """Serviço de geração de TTS para a pipeline"""
    
    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
    
    def _log(self, level: str, message: str, data: Optional[Dict] = None):
        """Adicionar log ao pipeline"""
        try:
            from routes.pipeline_complete import add_pipeline_log
            add_pipeline_log(self.pipeline_id, level, message, data)
        except Exception as e:
            logger.error(f"Erro ao adicionar log: {str(e)}")
    
    def generate_tts_for_script(self, script_text: str, provider: str, 
                               voice_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Gerar TTS para o roteiro usando a lógica da aba de automações"""
        try:
            self._log('info', f'Iniciando geração de TTS com {provider}')
            
            if not script_text.strip():
                raise Exception("Texto do roteiro está vazio")
            
            # Segmentar texto se necessário (limite de caracteres por segmento)
            max_chars_per_segment = voice_settings.get('max_chars_per_segment', 2000)
            text_segments = self._segment_text(script_text, max_chars_per_segment)
            
            self._log('info', f'Texto dividido em {len(text_segments)} segmentos')
            
            # Gerar áudio para cada segmento
            audio_segments = []
            
            for i, segment_text in enumerate(text_segments):
                try:
                    self._log('info', f'Gerando áudio {i + 1}/{len(text_segments)}: {segment_text[:50]}...')
                    
                    # Gerar áudio baseado no provedor
                    audio_result = self._generate_audio_segment(
                        segment_text, provider, voice_settings
                    )
                    
                    if audio_result and audio_result.get('success'):
                        # As funções de TTS já salvam o arquivo, usar dados existentes
                        audio_data = audio_result['data']
                        
                        # Obter informações do arquivo já salvo
                        # Diferentes provedores retornam chaves diferentes:
                        # - ElevenLabs: 'audio_file'
                        # - Kokoro: 'filename' (precisa construir o caminho)
                        # - Gemini: 'audio_file'
                        audio_file_path = audio_data.get('audio_file') or audio_data.get('audio_file_path')
                        filename = audio_data.get('filename', '')
                        file_size = audio_data.get('size', 0)
                        
                        # Se não temos audio_file_path mas temos filename, construir o caminho
                        if not audio_file_path and filename:
                            temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
                            audio_file_path = os.path.join(temp_dir, filename)
                        
                        # Verificar se o arquivo foi encontrado
                        if not audio_file_path:
                            self._log('error', f'Caminho do arquivo de áudio não encontrado nos dados: {audio_data}')
                            self._log('error', f'Chaves disponíveis nos dados: {list(audio_data.keys()) if audio_data else "Nenhuma"}')
                            continue
                        
                        # URL para acessar o áudio (usar rota de automações)
                        audio_url = f"/api/automations/audio/{filename}"
                        
                        audio_segments.append({
                            'index': i + 1,
                            'text': segment_text[:100] + '...' if len(segment_text) > 100 else segment_text,
                            'file_path': audio_file_path,
                            'filename': filename,
                            'url': audio_url,
                            'file_size': file_size,
                            'provider': provider,
                            'generation_time': datetime.utcnow().isoformat()
                        })
                        
                        self._log('info', f'Áudio {i + 1}/{len(text_segments)} gerado com sucesso - {filename}')
                    else:
                        self._log('warning', f'Falha ao gerar segmento {i + 1}: {audio_result.get("error", "Erro desconhecido")}')
                        
                    # Delay entre gerações
                    if i < len(text_segments) - 1:
                        time.sleep(2)
                        
                except Exception as e:
                    self._log('warning', f'Erro ao processar segmento {i + 1}: {str(e)}')
                    continue
            
            if not audio_segments:
                raise Exception("Nenhum segmento de áudio foi gerado com sucesso")
            
            self._log('info', f'TTS concluído: {len(audio_segments)}/{len(text_segments)} segmentos')
            
            # Concatenar todos os segmentos em um único arquivo
            if len(audio_segments) > 1:
                self._log('info', 'Concatenando segmentos de áudio...')
                concatenated_result = self._concatenate_audio_segments(audio_segments)
                if concatenated_result['success']:
                    main_audio_file = concatenated_result['data']['audio_file']
                    total_duration = concatenated_result['data']['duration']
                    total_size = concatenated_result['data']['size']
                    self._log('info', f'Áudio concatenado com sucesso: {total_duration:.1f}s')
                else:
                    self._log('warning', f'Falha na concatenação: {concatenated_result["error"]}. Usando primeiro segmento.')
                    main_audio_file = audio_segments[0]['file_path']
                    total_duration = 0
                    total_size = audio_segments[0]['file_size']
            else:
                main_audio_file = audio_segments[0]['file_path']
                total_duration = 0
                total_size = audio_segments[0]['file_size']
            
            return {
                'success': True,
                'audio_file_path': main_audio_file,
                'duration': total_duration,
                'file_size': total_size,
                'provider': provider,
                'segments': audio_segments,
                'total_segments': len(audio_segments),
                'text_length': len(script_text),
                'generation_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self._log('error', f'Erro na geração de TTS: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def _segment_text(self, text: str, max_chars: int) -> List[str]:
        """Dividir texto em segmentos menores"""
        if len(text) <= max_chars:
            return [text]
        
        segments = []
        current_segment = ""
        
        # Dividir por parágrafos primeiro
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            if len(current_segment + paragraph) <= max_chars:
                current_segment += paragraph + '\n\n'
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                    current_segment = ""
                
                # Se o parágrafo é muito longo, dividir por frases
                if len(paragraph) > max_chars:
                    sentences = paragraph.split('. ')
                    for sentence in sentences:
                        if len(current_segment + sentence) <= max_chars:
                            current_segment += sentence + '. '
                        else:
                            if current_segment:
                                segments.append(current_segment.strip())
                            current_segment = sentence + '. '
                else:
                    current_segment = paragraph + '\n\n'
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments
    
    def _generate_audio_segment(self, text: str, provider: str, 
                               voice_settings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Gerar áudio para um segmento de texto"""
        try:
            if provider == 'gemini' and generate_tts_with_gemini:
                api_key = self._get_api_key('gemini')
                voice_name = voice_settings.get('voice_name', 'Aoede')
                model = voice_settings.get('model', 'gemini-2.5-flash-preview-tts')
                speed = voice_settings.get('speed', 1.0)
                pitch = voice_settings.get('pitch', 0.0)
                volume_gain_db = voice_settings.get('volume_gain_db', 0.0)
                
                return generate_tts_with_gemini(
                    text, api_key=api_key, voice_name=voice_name, model=model,
                    speed=speed, pitch=pitch, volume_gain_db=volume_gain_db
                )
                
            elif provider == 'elevenlabs' and generate_tts_with_elevenlabs:
                api_key = self._get_api_key('elevenlabs')
                if not api_key:
                    raise Exception("Chave da API ElevenLabs não configurada")
                
                voice_id = voice_settings.get('voice_id', 'default')
                model_id = voice_settings.get('model_id', 'eleven_monolingual_v1')
                stability = voice_settings.get('stability', 0.5)
                similarity_boost = voice_settings.get('similarity_boost', 0.5)
                style = voice_settings.get('style', 0.0)
                use_speaker_boost = voice_settings.get('use_speaker_boost', True)
                
                return generate_tts_with_elevenlabs(
                    text, api_key, voice_id=voice_id, model_id=model_id,
                    stability=stability, similarity_boost=similarity_boost,
                    style=style, use_speaker_boost=use_speaker_boost
                )
                
            elif provider == 'kokoro' and generate_tts_with_kokoro:
                kokoro_url = voice_settings.get('kokoro_url', 'http://localhost:8880')
                voice_name = voice_settings.get('voice', 'af_bella')
                
                # Mapear voz 'default' para voz válida do Kokoro
                if voice_name == 'default':
                    voice_name = 'af_bella'
                
                language = voice_settings.get('language', 'en')
                speed = voice_settings.get('speed', 1.0)
                
                return generate_tts_with_kokoro(
                    text, kokoro_url=kokoro_url, voice_name=voice_name,
                    language=language, speed=speed
                )
            
            else:
                raise Exception(f"Provedor TTS não suportado ou não disponível: {provider}")
                
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _save_audio_file(self, audio_data: bytes, provider: str, segment_index: int) -> Dict[str, Any]:
        """Salvar arquivo de áudio"""
        try:
            # Criar diretório de output se não existir
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'audio')
            os.makedirs(output_dir, exist_ok=True)
            
            # Nome do arquivo
            timestamp = int(time.time() * 1000)
            filename = f"pipeline_{self.pipeline_id}_audio_{timestamp}_{segment_index}.wav"
            filepath = os.path.join(output_dir, filename)
            
            # Salvar arquivo
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            
            # URL para acessar o áudio
            audio_url = f"/api/audio/view/{filename}"
            
            return {
                'file_path': filepath,
                'filename': filename,
                'url': audio_url,
                'file_size': len(audio_data)
            }
            
        except Exception as e:
            raise Exception(f"Erro ao salvar arquivo de áudio: {str(e)}")
    
    def _concatenate_audio_segments(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Concatenar múltiplos segmentos de áudio em um único arquivo"""
        try:
            import os
            import subprocess
            import tempfile
            import time
            
            self._log('info', f'Concatenando {len(segments)} segmentos de áudio...')
            
            # Verificar se temos segmentos válidos
            valid_files = []
            total_size = 0
            
            for segment in sorted(segments, key=lambda x: x.get('index', 0)):
                filepath = segment.get('file_path')
                if not filepath or not os.path.exists(filepath):
                    self._log('warning', f'Arquivo não encontrado: {filepath}')
                    continue
                
                valid_files.append(filepath)
                total_size += os.path.getsize(filepath)
                self._log('info', f'Arquivo válido encontrado: {os.path.basename(filepath)}')
            
            if not valid_files:
                return {
                    'success': False,
                    'error': 'Nenhum segmento de áudio válido encontrado'
                }
            
            # Criar diretório de output se não existir
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'audio')
            os.makedirs(output_dir, exist_ok=True)
            
            # Nome do arquivo final
            timestamp = int(time.time())
            final_filename = f"pipeline_{self.pipeline_id}_audio_final_{timestamp}.mp3"
            final_filepath = os.path.join(output_dir, final_filename)
            
            # Usar ffmpeg para concatenar os arquivos
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for file_path in valid_files:
                    f.write(f"file '{file_path}'\n")
                concat_file = f.name
            
            try:
                # Comando ffmpeg para concatenação
                cmd = [
                    'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                    '-i', concat_file,
                    '-c', 'copy',
                    final_filepath
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutos de timeout
                )
                
                if result.returncode != 0:
                    # Se ffmpeg falhar, tentar com pydub como fallback
                    self._log('warning', 'FFmpeg falhou, tentando com pydub...')
                    return self._concatenate_with_pydub(valid_files, final_filepath)
                
            finally:
                # Limpar arquivo temporário
                if os.path.exists(concat_file):
                    os.remove(concat_file)
            
            # Verificar se o arquivo foi criado
            if not os.path.exists(final_filepath):
                return {
                    'success': False,
                    'error': 'Arquivo concatenado não foi criado'
                }
            
            # Obter informações do arquivo final
            final_size = os.path.getsize(final_filepath)
            
            # Calcular duração usando ffprobe
            try:
                duration_cmd = [
                    'ffprobe', '-v', 'quiet', '-show_entries',
                    'format=duration', '-of', 'csv=p=0', final_filepath
                ]
                duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
                final_duration = float(duration_result.stdout.strip()) if duration_result.returncode == 0 else 0
            except:
                final_duration = 0
            
            self._log('info', f'Áudio concatenado criado: {final_filename} ({final_duration:.1f}s, {final_size} bytes)')
            
            return {
                'success': True,
                'data': {
                    'audio_file': final_filepath,
                    'filename': final_filename,
                    'duration': final_duration,
                    'size': final_size,
                    'segments_count': len(valid_files),
                    'format': 'mp3'
                }
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Timeout na concatenação de áudio. Arquivos muito grandes.'
            }
        except Exception as e:
            self._log('error', f'Erro ao concatenar áudios: {e}')
            return {
                'success': False,
                'error': f'Erro ao concatenar áudios: {str(e)}'
            }
    
    def _concatenate_with_pydub(self, valid_files: List[str], output_path: str) -> Dict[str, Any]:
        """Fallback para concatenação usando pydub"""
        try:
            from pydub import AudioSegment
            import time
            
            self._log('info', 'Usando pydub para concatenação...')
            
            # Carregar todos os segmentos
            audio_segments = []
            total_duration = 0
            
            for filepath in valid_files:
                if filepath.endswith('.mp3'):
                    audio_seg = AudioSegment.from_mp3(filepath)
                elif filepath.endswith('.wav'):
                    audio_seg = AudioSegment.from_wav(filepath)
                else:
                    audio_seg = AudioSegment.from_file(filepath)
                
                audio_segments.append(audio_seg)
                total_duration += len(audio_seg) / 1000.0  # pydub usa milissegundos
                self._log('info', f'Carregado segmento: {os.path.basename(filepath)} ({len(audio_seg)/1000:.1f}s)')
            
            # Concatenar todos os segmentos
            self._log('info', 'Concatenando segmentos com pydub...')
            final_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                final_audio += segment
            
            # Exportar como MP3
            final_audio.export(
                output_path,
                format="mp3",
                bitrate="192k",
                parameters=["-q:a", "0"]
            )
            
            final_size = os.path.getsize(output_path)
            final_duration = len(final_audio) / 1000.0
            
            return {
                'success': True,
                'data': {
                    'audio_file': output_path,
                    'filename': os.path.basename(output_path),
                    'duration': final_duration,
                    'size': final_size,
                    'segments_count': len(valid_files),
                    'format': 'mp3'
                }
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'Biblioteca pydub não instalada. Execute: pip install pydub'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao concatenar com pydub: {str(e)}'
            }
    
    def _get_api_key(self, provider: str) -> Optional[str]:
        """Obter chave da API para o provedor especificado"""
        try:
            if provider == 'gemini':
                return os.getenv('GEMINI_API_KEY')
            elif provider == 'elevenlabs':
                return os.getenv('ELEVENLABS_API_KEY')
            return None
        except Exception:
            return None