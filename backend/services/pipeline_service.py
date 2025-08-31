"""🚀 Pipeline Service
Serviço principal de orquestração do pipeline de automação completa
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional

# Adicionar diretório routes ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'routes'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importar serviços necessários
from services.video_creation_service import VideoCreationService
from services.checkpoint_service import CheckpointService

logger = logging.getLogger(__name__)
logger.propagate = True
logger.setLevel(logging.INFO)

def load_custom_prompts() -> Dict[str, Any]:
    """Carregar prompts personalizados do arquivo de configuração"""
    try:
        prompts_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'prompts_config.json')
        
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Retornar prompts padrão se arquivo não existir
            return get_default_prompts()
    except Exception as e:
        logger.warning(f"Erro ao carregar prompts personalizados: {str(e)}. Usando prompts padrão.")
        return get_default_prompts()

def get_default_prompts() -> Dict[str, Any]:
    """Retornar prompts padrão do sistema"""
    return {
        "titles": {
            "viral": "Crie títulos virais e chamativos que gerem curiosidade e cliques. Use técnicas de copywriting, números, palavras de impacto e gatilhos emocionais.",
            "educational": "Crie títulos educativos e informativos que transmitam conhecimento de forma clara e atrativa.",
            "entertainment": "Crie títulos divertidos e envolventes para entretenimento, usando humor e criatividade."
        },
        "premises": {
            "default": "Baseado no título '{title}', crie uma premissa detalhada para um vídeo.\n\nA premissa deve:\n- Ter aproximadamente {word_count} palavras\n- Explicar o conceito principal do vídeo\n- Definir o público-alvo\n- Estabelecer o tom e estilo\n- Incluir pontos-chave a serem abordados\n- Ser envolvente e clara\n\nRetorne apenas a premissa, sem formatação extra."
        },
        "scripts": {
            "default": "Crie um roteiro envolvente com {chapters} capítulos, baseado no título '{title}' e premissa: {premise}. Duração alvo: {duration_target}."
        },
        "images": {
            "default": "Crie uma descrição detalhada para geração de imagem baseada no contexto: {context}. A imagem deve ser visualmente atrativa e relevante ao conteúdo."
        }
    }

class PipelineService:
    """Serviço principal de orquestração do pipeline"""
    
    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
        self.pipeline_state = None
        self.config = None
        self.api_keys = None
        self.results = {}
        self.custom_prompts = None
        
        # Importar estado do pipeline
        self._load_pipeline_state()
        
        # Carregar prompts personalizados
        self._load_custom_prompts()
        
        # Inicializar serviço de checkpoint
        self.checkpoint_service = CheckpointService(pipeline_id)
        self.auto_checkpoint = self.config.get('auto_checkpoint', True) if self.config else True
        
        # Adicionar controle de threading para pausar/retomar
        import threading
        self._pause_event = threading.Event()
        self._pause_event.set()  # Iniciar como não pausado
    
    def _load_custom_prompts(self):
        """Carregar prompts personalizados"""
        try:
            self.custom_prompts = load_custom_prompts()
            self._log('info', 'Prompts personalizados carregados com sucesso')
        except Exception as e:
            self._log('warning', f'Erro ao carregar prompts personalizados: {str(e)}')
            self.custom_prompts = get_default_prompts()
    
    def _load_pipeline_state(self):
        """Carregar estado do pipeline"""
        try:
            from routes.pipeline_complete import active_pipelines
            if self.pipeline_id in active_pipelines:
                self.pipeline_state = active_pipelines[self.pipeline_id]
                self.config = self.pipeline_state.get('config', {})
                self.api_keys = self.pipeline_state.get('api_keys', {})
            else:
                raise Exception(f"Pipeline {self.pipeline_id} não encontrado")
        except Exception as e:
            logger.error(f"Erro ao carregar estado do pipeline: {str(e)}")
            raise
    
    def _log(self, level: str, message: str, data: Optional[Dict] = None):
        """Adicionar log ao pipeline"""
        try:
            from routes.pipeline_complete import add_pipeline_log
            add_pipeline_log(self.pipeline_id, level, message, data)
        except Exception as e:
            logger.error(f"Erro ao adicionar log: {str(e)}")
    
    def _save_checkpoint(self, current_step: str):
        """Salvar checkpoint do estado atual"""
        try:
            success = self.checkpoint_service.save_checkpoint(
                step=current_step,
                results=self.results,
                config=self.config,
                progress=getattr(self, 'progress', {})
            )
            
            if success:
                self._log('info', f'Checkpoint salvo para etapa: {current_step}')
            else:
                self._log('warning', f'Falha ao salvar checkpoint para etapa: {current_step}')
                
        except Exception as e:
            self._log('error', f'Erro ao salvar checkpoint: {str(e)}')
    
    def load_from_checkpoint(self) -> bool:
        """Carregar estado a partir de checkpoint"""
        try:
            checkpoint_data = self.checkpoint_service.load_checkpoint()
            
            if not checkpoint_data:
                return False
            
            # Validar integridade do checkpoint
            if not self.checkpoint_service.validate_checkpoint_integrity(checkpoint_data):
                self._log('error', 'Checkpoint inválido ou corrompido')
                return False
            
            # Restaurar estado
            self.results = checkpoint_data.get('results', {})
            if not hasattr(self, 'progress'):
                self.progress = {}
            self.progress.update(checkpoint_data.get('progress', {}))
            self.config.update(checkpoint_data.get('config', {}))
            
            # Criar relatório de recuperação
            recovery_report = self.checkpoint_service.create_recovery_report(checkpoint_data)
            
            self._log('info', 'Estado restaurado a partir de checkpoint', {
                'completed_steps': recovery_report['completed_steps'],
                'next_step': recovery_report['next_step'],
                'checkpoint_timestamp': recovery_report['checkpoint_timestamp']
            })
            
            return True
            
        except Exception as e:
            self._log('error', f'Erro ao carregar checkpoint: {str(e)}')
            return False
    
    def get_resume_info(self) -> Optional[Dict[str, Any]]:
        """Obter informações para retomada da pipeline"""
        try:
            if not self.checkpoint_service.has_checkpoint():
                return None
            
            checkpoint_data = self.checkpoint_service.load_checkpoint()
            if not checkpoint_data:
                return None
            
            return self.checkpoint_service.create_recovery_report(checkpoint_data)
            
        except Exception as e:
            self._log('error', f'Erro ao obter informações de retomada: {str(e)}')
            return None
    
    def _update_progress(self, step: str, progress: int, status: str = 'processing'):
        """Atualizar progresso do pipeline"""
        try:
            from routes.pipeline_complete import update_pipeline_progress
            update_pipeline_progress(self.pipeline_id, step, progress, status)
            
            # Salvar checkpoint se habilitado
            if self.auto_checkpoint and progress == 100:
                self._save_checkpoint(step)
                
        except Exception as e:
            logger.error(f"Erro ao atualizar progresso: {str(e)}")
    
    # ================================
    # 🎯 ETAPA 1: EXTRAÇÃO DE TÍTULOS
    # ================================
    
    def run_extraction(self) -> Dict[str, Any]:
        """Executar extração de títulos do YouTube"""
        try:
            self._log('info', 'Iniciando extração de títulos do YouTube')
            
            channel_url = self.pipeline_state['channel_url']
            extraction_config = self.config.get('extraction', {})
            
            method = extraction_config.get('method', 'auto')
            max_titles = extraction_config.get('max_titles', 10)
            min_views = extraction_config.get('min_views', 1000)
            
            # Verificar se há títulos pré-fornecidos (método manual)
            if method == 'manual' and 'provided_titles' in extraction_config:
                self._log('info', 'Usando títulos pré-fornecidos (método manual)')
                provided_titles = extraction_config['provided_titles']
                
                # Converter títulos fornecidos para o formato esperado
                titles = []
                for i, title in enumerate(provided_titles[:max_titles]):
                    if isinstance(title, str):
                        titles.append({
                            'title': title,
                            'video_id': f'manual_{i}',
                            'views': min_views + 1000,  # Garantir que passa no filtro
                            'description': '',
                            'thumbnail': '',
                            'duration': '5:00',
                            'likes': 100,
                            'published_at': datetime.utcnow().isoformat(),
                            'url': f'https://youtube.com/watch?v=manual_{i}'
                        })
                    elif isinstance(title, dict):
                        titles.append(title)
                
                self._update_progress('extraction', 100)
                
                extraction_result = {
                    'channel_info': {'name': 'Manual Input', 'id': 'manual'},
                    'titles': titles,
                    'total_extracted': len(titles),
                    'method_used': 'manual',
                    'extraction_time': datetime.utcnow().isoformat()
                }
                
                self.results['extraction'] = extraction_result
                
                self._log('info', f'Extração manual concluída: {len(titles)} títulos fornecidos', {
                    'total_titles': len(titles),
                    'method': 'manual'
                })
                
                return extraction_result
            
            # Importar função de extração para métodos automáticos
            from routes.automations import get_channel_videos_ytdlp, get_channel_videos_rapidapi, get_next_rapidapi_key, extract_channel_id_from_url
            
            self._update_progress('extraction', 25)
            
            # Tentar extração baseada no método configurado
            if method in ['ytdlp', 'yt-dlp'] or method == 'auto':
                self._log('info', 'Tentando extração com yt-dlp')
                result = get_channel_videos_ytdlp(channel_url, max_titles)
                
                if not result.get('success') and method == 'auto':
                    self._log('warning', 'yt-dlp falhou, tentando RapidAPI como fallback')
                    self._update_progress('extraction', 50)
                    # Obter chave RapidAPI e extrair channel_id
                    api_key = get_next_rapidapi_key()
                    if not api_key:
                        raise Exception("Nenhuma chave RapidAPI disponível")
                    channel_id = extract_channel_id_from_url(channel_url, api_key)
                    if not channel_id:
                        raise Exception(f"Não foi possível extrair channel_id da URL: {channel_url}")
                    result = get_channel_videos_rapidapi(channel_id, api_key, max_titles)
            
            elif method == 'rapidapi':
                self._log('info', 'Usando extração com RapidAPI')
                # Obter chave RapidAPI e extrair channel_id
                api_key = get_next_rapidapi_key()
                if not api_key:
                    raise Exception("Nenhuma chave RapidAPI disponível")
                channel_id = extract_channel_id_from_url(channel_url, api_key)
                if not channel_id:
                    raise Exception(f"Não foi possível extrair channel_id da URL: {channel_url}")
                result = get_channel_videos_rapidapi(channel_id, api_key, max_titles)
            
            else:
                raise Exception(f"Método de extração inválido: {method}")
            
            if not result.get('success'):
                raise Exception(f"Falha na extração: {result.get('error', 'Erro desconhecido')}")
            
            # Filtrar por visualizações mínimas
            titles_data = result.get('data', {})
            # Verificar se os dados estão em 'titles' ou 'videos'
            titles = titles_data.get('titles', titles_data.get('videos', []))
            
            if min_views > 0:
                filtered_titles = [
                    title for title in titles 
                    if title.get('views', 0) >= min_views
                ]
                self._log('info', f'Filtrados {len(filtered_titles)} títulos com mais de {min_views} visualizações')
                titles = filtered_titles
            
            # Limitar quantidade
            titles = titles[:max_titles]
            
            self._update_progress('extraction', 100)
            
            extraction_result = {
                'channel_info': titles_data.get('channel_info', {}),
                'titles': titles,
                'total_extracted': len(titles),
                'method_used': result.get('method', method),
                'extraction_time': datetime.utcnow().isoformat()
            }
            
            self.results['extraction'] = extraction_result
            
            self._log('info', f'Extração concluída: {len(titles)} títulos extraídos', {
                'total_titles': len(titles),
                'method': result.get('method', method),
                'channel': titles_data.get('channel_info', {}).get('name', 'Desconhecido')
            })
            
            return extraction_result
            
        except Exception as e:
            self._log('error', f'Erro na extração: {str(e)}')
            raise
    
    # ================================
    # 🎯 ETAPA 2: GERAÇÃO DE TÍTULOS
    # ================================
    
    def run_titles_generation(self) -> Dict[str, Any]:
        """Executar geração de novos títulos"""
        try:
            self._log('info', 'Iniciando geração de novos títulos')
            
            # Verificar se temos títulos extraídos
            if 'extraction' not in self.results:
                raise Exception('Extração de títulos não foi executada')
            
            extracted_titles = self.results['extraction']['titles']
            if not extracted_titles:
                raise Exception('Nenhum título foi extraído')
            
            titles_config = self.config.get('titles', {})
            provider = titles_config.get('provider', 'gemini')
            count = titles_config.get('count', 5)
            style = titles_config.get('style', 'viral')
            custom_prompt = titles_config.get('custom_prompt', False)
            
            self._update_progress('titles', 25)
            
            # Preparar títulos de origem
            source_titles = [title.get('title', '') for title in extracted_titles]
            
            # Usar prompts personalizados ou padrão
            if custom_prompt and 'custom_instructions' in titles_config:
                instructions = titles_config['custom_instructions']
            else:
                # Usar prompts personalizados carregados
                titles_prompts = self.custom_prompts.get('titles', {})
                instructions = titles_prompts.get(style, titles_prompts.get('viral', 'Crie títulos virais e chamativos que gerem curiosidade e cliques'))
            
            self._update_progress('titles', 50)
            
            # Log do provedor sendo usado
            self._log('info', f'Provedor de IA para títulos: {provider}')
            
            # Gerar títulos usando o provedor configurado
            if provider == 'gemini':
                from services.ai_services import generate_titles_with_gemini
                # Forçar reset das chaves Gemini para garantir disponibilidade
                try:
                    from routes.automations import GEMINI_KEYS_ROTATION
                    from datetime import datetime
                    GEMINI_KEYS_ROTATION['usage_count'] = {}
                    GEMINI_KEYS_ROTATION['current_index'] = 0
                    GEMINI_KEYS_ROTATION['last_reset'] = datetime.now().date()
                    self._log('info', 'Reset das chaves Gemini aplicado na pipeline')
                except Exception as reset_error:
                    self._log('warning', f'Erro no reset das chaves Gemini: {reset_error}')
                
                # Usar sistema de rotação de chaves em vez de chave fixa
                api_key = None  # Deixar None para usar get_next_gemini_key() automaticamente
                def update_titles_partial(current_titles):
                    self.results['titles'] = {'generated_titles': current_titles, 'partial': True}
                    progress = int((len(current_titles) / count) * 100)
                    self._update_progress('titles', progress)
                result = generate_titles_with_gemini(source_titles, instructions, api_key, update_callback=update_titles_partial)
            
            elif provider == 'auto':
                # Tentar OpenAI primeiro, depois Gemini em caso de erro
                try:
                    from services.ai_services import generate_titles_with_openai
                    api_key = self.api_keys.get('openai')
                    def update_titles_partial(current_titles):
                        self.results['titles'] = {'generated_titles': current_titles, 'partial': True}
                        progress = int((len(current_titles) / count) * 100)
                        self._update_progress('titles', progress)
                    result = generate_titles_with_openai(source_titles, instructions, api_key, update_callback=update_titles_partial)
                    self._log('info', 'Títulos gerados com OpenAI (auto mode)')
                except Exception as e:
                    error_msg = str(e).lower()
                    if '429' in error_msg or 'quota' in error_msg or 'insufficient_quota' in error_msg:
                        self._log('warning', f'OpenAI falhou (quota excedida), tentando Gemini: {str(e)}')
                        try:
                            from services.ai_services import generate_titles_with_gemini
                            # Forçar reset das chaves Gemini para garantir disponibilidade
                            try:
                                from routes.automations import GEMINI_KEYS_ROTATION
                                from datetime import datetime
                                GEMINI_KEYS_ROTATION['usage_count'] = {}
                                GEMINI_KEYS_ROTATION['current_index'] = 0
                                GEMINI_KEYS_ROTATION['last_reset'] = datetime.now().date()
                                self._log('info', 'Reset das chaves Gemini aplicado na pipeline (fallback)')
                            except Exception as reset_error:
                                self._log('warning', f'Erro no reset das chaves Gemini: {reset_error}')
                            
                            # Usar sistema de rotação de chaves em vez de chave fixa
                            api_key = None  # Deixar None para usar get_next_gemini_key() automaticamente
                            def update_titles_partial(current_titles):
                                self.results['titles'] = {'generated_titles': current_titles, 'partial': True}
                                progress = int((len(current_titles) / count) * 100)
                                self._update_progress('titles', progress)
                            result = generate_titles_with_gemini(source_titles, instructions, api_key, update_callback=update_titles_partial)
                            self._log('info', 'Títulos gerados com Gemini (fallback)')
                        except Exception as gemini_error:
                            self._log('error', f'Gemini também falhou: {str(gemini_error)}')
                            raise Exception(f'Ambos provedores falharam - OpenAI: {str(e)}, Gemini: {str(gemini_error)}')
                    else:
                        raise e
            
            else:
                raise Exception(f"Provedor de IA inválido: {provider}")
            
            if not result.get('success'):
                raise Exception(f"Falha na geração de títulos: {result.get('error', 'Erro desconhecido')}")
            
            self._update_progress('titles', 100)
            
            titles_result = {
                'generated_titles': result['data']['generated_titles'][:count],
                'source_titles_count': len(source_titles),
                'provider_used': provider,
                'style': style,
                'generation_time': datetime.utcnow().isoformat()
            }
            
            self.results['titles'] = titles_result
            
            self._log('info', f'Geração de títulos concluída: {len(titles_result["generated_titles"])} títulos gerados', {
                'provider': provider,
                'style': style,
                'count': len(titles_result['generated_titles'])
            })
            
            return titles_result
            
        except Exception as e:
            self._log('error', f'Erro na geração de títulos: {str(e)}')
            raise
    
    # ================================
    # 🎯 ETAPA 3: GERAÇÃO DE PREMISSAS
    # ================================
    
    def run_premises_generation(self) -> Dict[str, Any]:
        """Executar geração de premissas"""
        try:
            self._log('info', 'Iniciando geração de premissas')
            
            # Verificar se temos títulos gerados
            if 'titles' not in self.results:
                raise Exception('Geração de títulos não foi executada')
            
            generated_titles = self.results['titles']['generated_titles']
            if not generated_titles:
                raise Exception('Nenhum título foi gerado')
            
            premises_config = self.config.get('premises', {})
            provider = premises_config.get('provider', 'gemini')
            word_count = premises_config.get('word_count', 200)
            custom_prompt = premises_config.get('custom_prompt', False)
            
            self._update_progress('premises', 25)
            
            # Selecionar o melhor título (primeiro da lista)
            selected_title = generated_titles[0]
            
            # Preparar prompt para premissas usando prompts personalizados
            if custom_prompt and 'custom_instructions' in premises_config:
                instructions = premises_config['custom_instructions']
            else:
                # Usar prompt personalizado carregado
                premises_prompts = self.custom_prompts.get('premises', {})
                prompt_template = premises_prompts.get('default', 
                    "Baseado no título '{title}', crie uma premissa detalhada para um vídeo.\n\nA premissa deve:\n- Ter aproximadamente {word_count} palavras\n- Explicar o conceito principal do vídeo\n- Definir o público-alvo\n- Estabelecer o tom e estilo\n- Incluir pontos-chave a serem abordados\n- Ser envolvente e clara\n\nRetorne apenas a premissa, sem formatação extra.")
                
                # Substituir variáveis no template
                instructions = prompt_template.format(
                    title=selected_title,
                    word_count=word_count
                )
            
            self._update_progress('premises', 50)
            
            # Gerar premissa usando o provedor configurado
            if provider == 'gemini':
                import google.generativeai as genai
                # Usar sistema de rotação de chaves diretamente
                from routes.automations import get_next_gemini_key, handle_gemini_429_error, get_fallback_provider_info
                api_key = get_next_gemini_key()
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                premise_text = ''
                for chunk in model.generate_content(instructions, stream=True):
                    premise_text += chunk.text
                    self.results['premises'] = {'premise': premise_text, 'partial': True}
                    # Atualizar progresso baseado em comprimento aproximado
                    current_length = len(premise_text.split())
                    progress = min(int((current_length / word_count) * 100), 99)
                    self._update_progress('premises', progress)
            
            elif provider == 'openai':
                import openai
                api_key = self.api_keys.get('openai')
                client = openai.OpenAI(api_key=api_key)
                
                premise_text = ''
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": instructions}],
                    max_tokens=500,
                    temperature=0.7,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        premise_text += chunk.choices[0].delta.content
                        self.results['premises'] = {'premise': premise_text, 'partial': True}
                        current_length = len(premise_text.split())
                        progress = min(int((current_length / word_count) * 100), 99)
                        self._update_progress('premises', progress)
            
            elif provider == 'auto':
                # Tentar OpenAI primeiro, depois Gemini em caso de erro
                try:
                    import openai
                    api_key = self.api_keys.get('openai')
                    client = openai.OpenAI(api_key=api_key)
                    
                    premise_text = ''
                    stream = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": instructions}],
                        max_tokens=500,
                        temperature=0.7,
                        stream=True
                    )
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            premise_text += chunk.choices[0].delta.content
                            self.results['premises'] = {'premise': premise_text, 'partial': True}
                            current_length = len(premise_text.split())
                            progress = min(int((current_length / word_count) * 100), 99)
                            self._update_progress('premises', progress)
                    self._log('info', 'Premissa gerada com OpenAI (auto mode)')
                except Exception as e:
                    error_msg = str(e).lower()
                    if '429' in error_msg or 'quota' in error_msg or 'insufficient_quota' in error_msg:
                        self._log('warning', f'OpenAI falhou (quota excedida), tentando Gemini: {str(e)}')
                        # Tentar Gemini como fallback primário
                        try:
                            import google.generativeai as genai
                            api_key = self.api_keys.get('gemini')
                            if not api_key:
                                api_key = get_next_gemini_key()
                            
                            if not api_key:
                                raise Exception('Nenhuma chave Gemini disponível para fallback.')

                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            premise_text = ''
                            for chunk in model.generate_content(instructions, stream=True):
                                premise_text += chunk.text
                                self.results['premises'] = {'premise': premise_text, 'partial': True}
                                current_length = len(premise_text.split())
                                progress = min(int((current_length / word_count) * 100), 99)
                                self._update_progress('premises', progress)
                            self._log('info', 'Premissa gerada com Gemini (fallback)')
                        except Exception as gemini_error:
                            self._log('error', f'Gemini também falhou: {str(gemini_error)}')
                            # Se Gemini falhar, tentar OpenRouter ou OpenAI
                            fallback_info = get_fallback_provider_info()
                            if fallback_info:
                                fallback_provider = fallback_info['provider']
                                fallback_key = fallback_info['key']
                                self._log('warning', f'Tentando fallback para {fallback_provider}...')
                                try:
                                    if fallback_provider == 'openrouter':
                                        client = openai.OpenAI(
                                            base_url="https://openrouter.ai/api/v1",
                                            api_key=fallback_key,
                                        )
                                        model_name = "mistralai/mistral-7b-instruct"
                                    elif fallback_provider == 'openai':
                                        client = openai.OpenAI(api_key=fallback_key)
                                        model_name = "gpt-3.5-turbo"
                                    
                                    premise_text = ''
                                    stream = client.chat.completions.create(
                                        model=model_name,
                                        messages=[{"role": "user", "content": instructions}],
                                        max_tokens=500,
                                        temperature=0.7,
                                        stream=True
                                    )
                                    for chunk in stream:
                                        if chunk.choices[0].delta.content is not None:
                                            premise_text += chunk.choices[0].delta.content
                                            self.results['premises'] = {'premise': premise_text, 'partial': True}
                                            current_length = len(premise_text.split())
                                            progress = min(int((current_length / word_count) * 100), 99)
                                            self._update_progress('premises', progress)
                                    self._log('info', f'Premissa gerada com {fallback_provider} (fallback)')
                                except Exception as fallback_e:
                                    self._log('error', f'Fallback para {fallback_provider} também falhou: {str(fallback_e)}')
                                    raise Exception(f'Todos os provedores falharam - OpenAI: {str(e)}, Gemini: {str(gemini_error)}, Fallback ({fallback_provider}): {str(fallback_e)}')
                            else:
                                raise Exception(f'Ambos provedores falharam e nenhum fallback disponível - OpenAI: {str(e)}, Gemini: {str(gemini_error)}')
                        except Exception as inner_e:
                            self._log('error', f'Erro no fallback Gemini: {str(inner_e)}')
                            raise e
                    else:
                        raise e
            
            else:
                raise Exception(f"Provedor de IA inválido: {provider}")
            
            self._update_progress('premises', 100)
            
            premises_result = {
                'selected_title': selected_title,
                'premise': premise_text,
                'word_count': len(premise_text.split()),
                'provider_used': provider,
                'generation_time': datetime.utcnow().isoformat()
            }
            
            self.results['premises'] = premises_result
            
            self._log('info', 'Geração de premissas concluída', {
                'title': selected_title,
                'word_count': len(premise_text.split()),
                'provider': provider
            })
            
            return premises_result
            
        except Exception as e:
            self._log('error', f'Erro na geração de premissas: {str(e)}')
            raise
    
    # ================================
    # 🎯 ETAPA 4: GERAÇÃO DE ROTEIROS
    # ================================
    
    def run_scripts_generation(self) -> Dict[str, Any]:
        """Executar geração de roteiros"""
        try:
            self._log('info', 'Iniciando geração de roteiros')
            
            # Verificar se temos premissa
            if 'premises' not in self.results:
                raise Exception('Geração de premissas não foi executada')
            
            premise_data = self.results['premises']
            title = premise_data['selected_title']
            premise = premise_data['premise']
            
            scripts_config = self.config.get('scripts', {})
            chapters = scripts_config.get('chapters', 5)
            style = scripts_config.get('style', 'inicio')
            duration_target = scripts_config.get('duration_target', '5-7 minutes')
            include_hooks = scripts_config.get('include_hooks', True)
            
            self._update_progress('scripts', 25)
            
            # Importar gerador de roteiros
            from routes.scripts import generate_long_script
            
            # Importar funções auxiliares para prompts de roteiro
            from routes.premise import create_inicio_prompt, create_capitulo_prompt, create_final_prompt
            
            # Obter prompts personalizados de roteiros
            scripts_config = self.config.get('scripts', {})
            custom_inicio = scripts_config.get('custom_inicio', '')
            custom_meio = scripts_config.get('custom_meio', '')
            custom_fim = scripts_config.get('custom_fim', '')
            
            # Preparar dados para geração
            script_data = {
                'title': title,
                'premise': premise,
                'chapters': chapters,
                'style': style,
                'duration_target': duration_target,
                'include_hooks': include_hooks,
                'custom_inicio': custom_inicio,
                'custom_meio': custom_meio,
                'custom_fim': custom_fim,
                'detailed_prompt_text': scripts_config.get('detailed_prompt_text', ''),
                'detailed_prompt': scripts_config.get('detailed_prompt', False),
                'contextual_chapters': scripts_config.get('contextual_chapters', False)
            }
            
            self._update_progress('scripts', 50)
            
            def update_scripts_partial(chapters):
                partial_data = {
                    'chapters': chapters,
                    'partial': True,
                    'chapters_generated': len(chapters)
                }
                self.results['scripts'] = partial_data
                if 'results' not in self.pipeline_state:
                    self.pipeline_state['results'] = {}
                self.pipeline_state['results']['scripts'] = partial_data
                progress = int((len(chapters) / scripts_config.get('chapters', 5)) * 100) if len(chapters) > 0 else 0
                self._update_progress('scripts', progress)

            # Verificar se deve usar o novo método de geração com resumos contextuais
            if scripts_config.get('contextual_chapters', False):
                # Usar o novo endpoint de geração de roteiros longos com resumos contextuais
                from routes.long_script_generator import generate_long_script_with_context
                
                # Obter provedor da configuração de scripts (padrão: gemini)
                provider = scripts_config.get('provider', 'gemini')
                
                # Preparar prompts personalizados do config
                custom_prompts = None
                if scripts_config.get('custom_prompt', False):
                    custom_prompts = {
                        'custom_inicio': scripts_config.get('custom_inicio'),
                        'custom_meio': scripts_config.get('custom_meio'), 
                        'custom_fim': scripts_config.get('custom_fim'),
                        'default_prompt_intro': scripts_config.get('default_prompt_intro'),
                        'default_prompt_middle': scripts_config.get('default_prompt_middle'),
                        'default_prompt_conclusion': scripts_config.get('default_prompt_conclusion')
                    }
                
                # Gerar roteiro com resumos contextuais
                # Passando os parâmetros corretamente para a função
                number_of_chapters = scripts_config.get('chapters', 5)
                result = generate_long_script_with_context(
                    titulo=title, 
                    premissa=premise, 
                    numero_capitulos=number_of_chapters, 
                    title_generator=None, 
                    openrouter_api_key=self.api_keys.get('openrouter'), 
                    openrouter_model=scripts_config.get('openrouter_model', 'auto'),
                    update_callback=update_scripts_partial,
                    long_script_prompt=scripts_config.get('custom_instructions'),  # Prompt adicional legado
                    custom_prompts=custom_prompts
                )
            else:
                # Usar o método padrão de geração de roteiros
                result = generate_long_script(script_data, update_scripts_partial)
            
            if not result.get('success'):
                raise Exception(f"Falha na geração de roteiro: {result.get('error', 'Erro desconhecido')}")
            
            self._update_progress('scripts', 100)
            
            scripts_result = {
                'title': title,
                'premise': premise,
                'script': result['data']['script'],
                'chapters': result['data'].get('chapters', []),
                'chapters_generated': len(result['data'].get('chapters', [])),
                'estimated_duration': result['data'].get('estimated_duration', duration_target),
                'style': style,
                'generation_time': datetime.utcnow().isoformat(),
                'partial': False
            }
            
            self.results['scripts'] = scripts_result
            
            self._log('info', 'Geração de roteiros concluída', {
                'chapters': scripts_result['chapters_generated'],
                'style': style,
                'estimated_duration': scripts_result['estimated_duration']
            })
            
            return scripts_result
            
        except Exception as e:
            self._log('error', f'Erro na geração de roteiros: {str(e)}')
            raise
    
    # ================================
    # 🎯 ETAPA 5: GERAÇÃO DE TTS
    # ================================
    
    def run_tts_generation(self) -> Dict[str, Any]:
        """Executar geração de áudio TTS"""
        try:
            self._log('info', 'Iniciando geração de áudio TTS')
            
            # Verificar se TTS está habilitado na configuração
            tts_config = self.config.get('tts', {})
            if not tts_config.get('enabled', True):
                self._log('info', 'TTS desabilitado na configuração, pulando etapa')
                
                # Criar resultado placeholder para compatibilidade
                tts_result = {
                    'audio_file_path': None,
                    'duration': 0,
                    'file_size': 0,
                    'provider_used': 'disabled',
                    'voice': 'none',
                    'speed': 1.0,
                    'emotion': 'neutral',
                    'generation_time': datetime.utcnow().isoformat(),
                    'status': 'skipped',
                    'message': 'TTS desabilitado pelo usuário'
                }
                
                self.results['tts'] = tts_result
                self._update_progress('tts', 100)
                return tts_result
            
            # Verificar se temos roteiro
            if 'scripts' not in self.results:
                raise Exception('Geração de roteiros não foi executada')
            
            script_data = self.results['scripts']
            script_text = script_data['script']
            
            tts_config = self.config.get('tts', {})
            provider = tts_config.get('provider', 'kokoro')
            voice = tts_config.get('voice', 'default')
            language = tts_config.get('language', 'en')  # Adicionar configuração de idioma
            
            # Mapear voz 'default' para vozes válidas por provedor
            if voice == 'default':
                if provider == 'kokoro':
                    voice = 'af_bella'  # Voz padrão válida para Kokoro
                elif provider == 'elevenlabs':
                    voice = 'Rachel'  # Voz padrão válida para ElevenLabs
                elif provider == 'gemini':
                    voice = 'en-US-Journey-F'  # Voz padrão válida para Gemini
            
            speed = tts_config.get('speed', 1.0)
            emotion = tts_config.get('emotion', 'neutral')
            
            self._update_progress('tts', 25)
            
            # Importar serviço de TTS
            from services.tts_service import TTSService
            
            tts_service = TTSService(self.pipeline_id)
            
            self._update_progress('tts', 50)
            
            # Gerar TTS usando o serviço
            result = tts_service.generate_tts_for_script(
                script_text=script_text,
                provider=provider,
                voice_settings={
                    'voice': voice,
                    'speed': speed,
                    'emotion': emotion,
                    'language': language  # Adicionar idioma nas configurações
                }
            )
            
            self._update_progress('tts', 100)
            
            # Verificar se o resultado do TTS foi bem-sucedido
            if not result.get('success'):
                raise Exception(f"Falha na geração de TTS: {result.get('error', 'Erro desconhecido')}")
            
            tts_result = {
                'audio_file_path': result['audio_file_path'],
                'duration': result.get('duration', 0),
                'file_size': result.get('file_size', 0),
                'provider_used': provider,
                'voice': voice,
                'speed': speed,
                'emotion': emotion,
                'generation_time': datetime.utcnow().isoformat()
            }
            
            self.results['tts'] = tts_result
            
            self._log('info', 'Geração de TTS concluída', {
                'provider': provider,
                'duration': result['duration'],
                'file_path': result['audio_file_path']
            })
            
            return tts_result
            
        except Exception as e:
            self._log('error', f'Erro na geração de TTS: {str(e)}')
            raise
    

    
    # ================================
    # 🎯 ETAPA 6: GERAÇÃO DE IMAGENS
    # ================================
    
    def run_images_generation(self) -> Dict[str, Any]:
        """Executar geração de imagens"""
        try:
            self._log('info', 'Iniciando geração de imagens')
            
            # Verificar se geração de imagens está habilitada na configuração
            images_config = self.config.get('images', {})
            if not images_config.get('enabled', True):
                self._log('info', 'Geração de imagens desabilitada na configuração, pulando etapa')
                
                # Criar resultado placeholder para compatibilidade
                images_result = {
                    'generated_images': [],
                    'total_images': 0,
                    'provider_used': 'disabled',
                    'style': 'none',
                    'resolution': 'none',
                    'generation_time': datetime.utcnow().isoformat(),
                    'status': 'skipped',
                    'message': 'Geração de imagens desabilitada pelo usuário'
                }
                
                self.results['images'] = images_result
                self._update_progress('images', 100)
                return images_result
            
            # Verificar se temos roteiro
            if 'scripts' not in self.results:
                raise Exception('Geração de roteiros não foi executada')
            
            script_data = self.results['scripts']
            script_text = script_data['script']
            
            images_config = self.config.get('images', {})
            provider = images_config.get('provider', 'pollinations')
            style = images_config.get('style', 'cinematic')
            resolution = images_config.get('resolution', '1920x1080')
            per_chapter = images_config.get('per_chapter', 2)
            
            self._update_progress('images', 25)
            
            # Obter prompt personalizado para imagens
            images_prompts = self.custom_prompts.get('images', {})
            custom_image_prompt = images_prompts.get('default', 'Crie uma descrição detalhada para geração de imagem baseada no contexto: {context}. A imagem deve ser visualmente atrativa e relevante ao conteúdo.')
            
            # Importar serviço de geração de imagens
            from services.image_generation_service import ImageGenerationService
            
            image_service = ImageGenerationService(self.pipeline_id)
            
            self._update_progress('images', 50)
            
            # Gerar imagens com prompt personalizado
            result = image_service.generate_images_for_script(
                script_text, provider, style, resolution, per_chapter, custom_image_prompt
            )
            
            self._update_progress('images', 100)
            
            images_result = {
                'generated_images': result['images'],
                'total_images': len(result['images']),
                'provider_used': provider,
                'style': style,
                'resolution': resolution,
                'generation_time': datetime.utcnow().isoformat()
            }
            
            self.results['images'] = images_result
            
            self._log('info', 'Geração de imagens concluída', {
                'total_images': len(result['images']),
                'provider': provider,
                'style': style
            })
            
            return images_result
            
        except Exception as e:
            self._log('error', f'Erro na geração de imagens: {str(e)}')
            raise
    
    # ================================
    # 🎯 ETAPA 7: CRIAÇÃO DE VÍDEO
    # ================================
    
    def run_video_creation(self) -> Dict[str, Any]:
        """Executar criação do vídeo final"""
        try:
            self._log('info', 'Iniciando criação do vídeo final')
            
            # Verificar se criação de vídeo está habilitada na configuração
            video_config = self.config.get('video', {})
            if not video_config.get('enabled', True):
                self._log('info', 'Criação de vídeo desabilitada na configuração, pulando etapa')
                
                # Criar resultado placeholder para compatibilidade
                video_result = {
                    'video_file_path': None,
                    'duration': 0,
                    'file_size': 0,
                    'resolution': 'none',
                    'fps': 0,
                    'quality': 'none',
                    'transitions': False,
                    'subtitles': False,
                    'creation_time': datetime.utcnow().isoformat(),
                    'status': 'skipped',
                    'message': 'Criação de vídeo desabilitada pelo usuário'
                }
                
                self.results['video'] = video_result
                self._update_progress('video', 100)
                return video_result
            
            # Verificar quais recursos estão disponíveis baseado nas etapas habilitadas
            available_resources = ['scripts']
            
            # Adicionar TTS se habilitado e executado
            tts_config = self.config.get('tts', {})
            if tts_config.get('enabled', True) and 'tts' in self.results and self.results['tts'].get('status') != 'skipped':
                available_resources.append('tts')
            
            # Adicionar imagens se habilitado e executado
            images_config = self.config.get('images', {})
            if images_config.get('enabled', True) and 'images' in self.results and self.results['images'].get('status') != 'skipped':
                available_resources.append('images')
            
            # Verificar se temos recursos mínimos (pelo menos roteiro)
            for req in ['scripts']:
                if req not in self.results:
                    raise Exception(f'Etapa {req} não foi executada')
            
            video_config = self.config.get('video', {})
            resolution = video_config.get('resolution', '1920x1080')
            fps = video_config.get('fps', 30)
            quality = video_config.get('quality', 'high')
            transitions = video_config.get('transitions', True)
            subtitles = video_config.get('subtitles', True)
            
            self._update_progress('video', 25)
            
            # Criar instância do serviço de criação de vídeo
            video_service = VideoCreationService(self.pipeline_id)
            
            self._update_progress('video', 50)
            
            # Obter segmentos TTS para sincronização precisa
            tts_segments = self.results['tts'].get('segments', [])
            
            # Criar vídeo com sincronização inteligente
            result = video_service.create_video(
                audio_path=self.results['tts']['audio_file_path'],
                images=self.results['images']['generated_images'],
                script_text=self.results['scripts']['script'],
                resolution=resolution,
                fps=fps,
                quality=quality,
                transitions=transitions,
                subtitles=subtitles,
                tts_segments=tts_segments
            )
            
            self._update_progress('video', 100)
            
            video_result = {
                'video_file_path': result['video_path'],
                'duration': result['duration'],
                'file_size': result['file_size'],
                'resolution': resolution,
                'fps': fps,
                'quality': quality,
                'creation_time': datetime.utcnow().isoformat()
            }
            
            self.results['video'] = video_result
            
            self._log('info', 'Criação de vídeo concluída', {
                'video_path': result['video_path'],
                'duration': result['duration'],
                'file_size': result['file_size']
            })
            
            return video_result
            
        except Exception as e:
            self._log('error', f'Erro na criação de vídeo: {str(e)}')
            # Salvar checkpoint mesmo em caso de erro para permitir retomada
            if self.auto_checkpoint:
                self._save_checkpoint('video_failed')
            raise
    
    # ================================
    # 🎯 ETAPA 8: LIMPEZA
    # ================================
    
    def run_cleanup(self) -> Dict[str, Any]:
        """Executar limpeza de arquivos temporários"""
        try:
            self._log('info', 'Iniciando limpeza de arquivos temporários')
            
            self._update_progress('cleanup', 50)
            
            # Limpar arquivos temporários (manter apenas o vídeo final)
            temp_files = []
            
            # Adicionar arquivos temporários à lista de limpeza
            if 'tts' in self.results:
                temp_files.append(self.results['tts']['audio_file_path'])
            
            if 'images' in self.results:
                for image in self.results['images']['generated_images']:
                    if 'temp_path' in image:
                        temp_files.append(image['temp_path'])
            
            # Remover arquivos temporários
            cleaned_files = []
            for file_path in temp_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        cleaned_files.append(file_path)
                except Exception as e:
                    self._log('warning', f'Não foi possível remover arquivo temporário {file_path}: {str(e)}')
            
            self._update_progress('cleanup', 100)
            
            cleanup_result = {
                'cleaned_files': cleaned_files,
                'files_count': len(cleaned_files),
                'cleanup_time': datetime.utcnow().isoformat()
            }
            
            self.results['cleanup'] = cleanup_result
            
            # Remover checkpoint após conclusão bem-sucedida
            if self.checkpoint_service.has_checkpoint():
                self.checkpoint_service.delete_checkpoint()
                self._log('info', 'Checkpoint removido após conclusão bem-sucedida')
                cleanup_result['checkpoint_removed'] = True
            
            self._log('info', f'Limpeza concluída: {len(cleaned_files)} arquivos removidos')
            
            return cleanup_result
            
        except Exception as e:
            self._log('error', f'Erro na limpeza: {str(e)}')
            raise
    
    # ================================
    # 🎯 VERIFICAÇÃO DE STATUS
    # ================================
    
    def _check_pipeline_status(self) -> bool:
        """Verificar se o pipeline foi pausado ou cancelado"""
        try:
            # Importar aqui para evitar dependência circular
            from routes.pipeline_complete import active_pipelines, PipelineStatus
            
            if self.pipeline_id in active_pipelines:
                status = active_pipelines[self.pipeline_id]['status']
                if status == PipelineStatus.PAUSED:
                    self._log('info', 'Pipeline pausado, aguardando retomada...')
                    self._pause_event.clear()  # Pausar a execução
                    
                    # Aguardar até que o pipeline seja retomado ou cancelado
                    while True:
                        # Verificar status a cada segundo
                        if self._pause_event.wait(timeout=1.0):
                            # Event foi setado, verificar se foi retomado
                            current_status = active_pipelines[self.pipeline_id]['status']
                            if current_status == PipelineStatus.PROCESSING:
                                self._log('info', 'Pipeline retomado, continuando execução...')
                                return True
                            elif current_status == PipelineStatus.CANCELLED:
                                self._log('warning', 'Pipeline cancelado durante pausa')
                                return False
                        else:
                            # Timeout, verificar se foi cancelado
                            current_status = active_pipelines[self.pipeline_id]['status']
                            if current_status == PipelineStatus.CANCELLED:
                                self._log('warning', 'Pipeline cancelado durante pausa')
                                return False
                            elif current_status == PipelineStatus.PROCESSING:
                                self._pause_event.set()  # Sinalizar retomada
                                self._log('info', 'Pipeline retomado, continuando execução...')
                                return True
                elif status == PipelineStatus.CANCELLED:
                    self._log('warning', 'Pipeline cancelado pelo usuário')
                    return False
            return True
        except Exception as e:
            self._log('warning', f'Erro ao verificar status do pipeline: {str(e)}')
            return True  # Continuar em caso de erro
    
    def _wait_for_resume(self):
        """Aguardar até que o pipeline seja retomado"""
        # Este método não é mais necessário pois a lógica foi movida para _check_pipeline_status
        pass
    
    # ================================
    # 🎯 EXECUÇÃO COM RETOMADA AUTOMÁTICA
    # ================================
    
    def run_with_resume(self, steps: List[str] = None) -> Dict[str, Any]:
        """Executar pipeline com suporte a retomada automática"""
        try:
            # Verificar se existe checkpoint para retomada
            if self.checkpoint_service.has_checkpoint():
                self._log('info', 'Checkpoint encontrado, retomando pipeline...')
                checkpoint_data = self.load_from_checkpoint()
                
                if checkpoint_data:
                    self._log('info', f'Pipeline retomada a partir da etapa: {checkpoint_data["next_step"]}')
                    # Continuar a partir da próxima etapa
                    remaining_steps = self._get_remaining_steps(checkpoint_data['next_step'], steps)
                else:
                    # Se não conseguir carregar checkpoint, começar do início
                    remaining_steps = steps or self._get_default_steps()
            else:
                # Executar pipeline completa
                remaining_steps = steps or self._get_default_steps()
            
            # Executar etapas restantes
            for step in remaining_steps:
                # Verificar se pipeline foi pausado ou cancelado antes de cada etapa
                if not self._check_pipeline_status():
                    self._log('info', f'Pipeline pausado/cancelado antes da etapa: {step}')
                    return self.results
                
                try:
                    self._log('info', f'Executando etapa: {step}')
                    
                    if step == 'extraction':
                        self.run_extraction()
                    elif step == 'titles':
                        self.run_titles_generation()
                    elif step == 'premises':
                        self.run_premises_generation()
                    elif step == 'scripts':
                        self.run_scripts_generation()
                    elif step == 'tts':
                        self.run_tts_generation()
                    elif step == 'images':
                        self.run_images_generation()
                    elif step == 'video':
                        self.run_video_creation()
                    elif step == 'cleanup':
                        self.run_cleanup()
                    else:
                        self._log('warning', f'Etapa desconhecida: {step}')
                        continue
                    
                    # Verificar novamente após a execução da etapa
                    if not self._check_pipeline_status():
                        self._log('info', f'Pipeline pausado/cancelado após a etapa: {step}')
                        return self.results
                    
                    # Salvar checkpoint após cada etapa bem-sucedida
                    if self.auto_checkpoint and step != 'cleanup':
                        self._save_checkpoint(step)
                    
                except Exception as e:
                    self._log('error', f'Erro na etapa {step}: {str(e)}')
                    # Salvar checkpoint mesmo em caso de erro
                    if self.auto_checkpoint:
                        self._save_checkpoint(f'{step}_failed')
                    raise
            
            self._log('info', 'Pipeline executada com sucesso!')
            return self.results
            
        except Exception as e:
            self._log('error', f'Erro na execução da pipeline: {str(e)}')
            raise
    
    def _get_default_steps(self) -> List[str]:
        """Obter lista padrão de etapas da pipeline baseada na configuração"""
        enabled_steps = []
        
        # Verificar quais etapas estão habilitadas
        if self.config.get('extraction', {}).get('enabled', True):
            enabled_steps.append('extraction')
        if self.config.get('titles', {}).get('enabled', True):
            enabled_steps.append('titles')
        if self.config.get('premises', {}).get('enabled', True):
            enabled_steps.append('premises')
        if self.config.get('scripts', {}).get('enabled', True):
            enabled_steps.append('scripts')
        if self.config.get('tts', {}).get('enabled', True):
            enabled_steps.append('tts')
        if self.config.get('images', {}).get('enabled', True):
            enabled_steps.append('images')
        if self.config.get('video', {}).get('enabled', True):
            enabled_steps.append('video')
        
        # Cleanup sempre habilitado se há pelo menos uma etapa
        if enabled_steps:
            enabled_steps.append('cleanup')
            
        return enabled_steps
    
    def _get_remaining_steps(self, next_step: str, all_steps: List[str] = None) -> List[str]:
        """Obter etapas restantes a partir de uma etapa específica"""
        if not all_steps:
            all_steps = self._get_default_steps()
        
        try:
            start_index = all_steps.index(next_step)
            return all_steps[start_index:]
        except ValueError:
            # Se a etapa não for encontrada, executar todas
            return all_steps