"""🎨 Image Generation Service
Serviço de geração de imagens usando a mesma lógica da aba de automações
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import quote

# Adicionar diretório routes ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'routes'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importar funções de geração de imagens da aba de automações
try:
    from routes.images import generate_image_pollinations, generate_image_gemini, generate_image_together
except ImportError:
    print("⚠️ Erro ao importar funções de geração de imagens")
    generate_image_pollinations = None
    generate_image_gemini = None
    generate_image_together = None

logger = logging.getLogger(__name__)

class ImageGenerationService:
    """Serviço de geração de imagens"""
    
    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
        self.pollinations_base_url = "https://image.pollinations.ai/prompt"
        self.max_retries = 3
        self.retry_delay = 2
    
    def _log(self, level: str, message: str, data: Optional[Dict] = None):
        """Adicionar log ao pipeline"""
        try:
            from routes.pipeline_complete import add_pipeline_log
            add_pipeline_log(self.pipeline_id, level, message, data)
        except Exception as e:
            logger.error(f"Erro ao adicionar log: {str(e)}")
    
    def _generate_images_with_automation_logic(self, script_text: str, provider: str, 
                                             style: str, resolution: str, image_count: int) -> List[Dict[str, Any]]:
        """Gerar imagens usando a mesma lógica da aba de automações"""
        try:
            # Preparar parâmetros como na aba de automações
            width, height = map(int, resolution.split('x'))
            generated_images = []
            
            # Dividir roteiro em cenas/parágrafos (mesmo método da aba de automações)
            scenes = [scene.strip() for scene in script_text.split('\n\n') if scene.strip()]
            
            if not scenes:
                scenes = [script_text]
            
            # Distribuir cenas uniformemente (função da aba de automações)
            scenes_to_use = self._distribute_scenes_evenly(scenes, image_count)
            
            # Gerar prompts finais com estilo
            prompts_to_generate = []
            for scene_text in scenes_to_use:
                final_prompt = f"{scene_text}, {style}"
                prompts_to_generate.append(final_prompt)
            
            # Gerar imagens para cada prompt
            for i, prompt in enumerate(prompts_to_generate):
                try:
                    self._log('info', f'Gerando imagem {i + 1}/{len(prompts_to_generate)}: {prompt[:50]}...')
                    
                    # Gerar imagem baseado no provedor (usando funções da aba de automações)
                    image_bytes = None
                    
                    if provider == 'pollinations' and generate_image_pollinations:
                        image_bytes = generate_image_pollinations(prompt, width, height, 'standard', 'flux')
                    elif provider == 'gemini' and generate_image_gemini:
                        # Obter chave da API
                        api_key = self._get_api_key('gemini')
                        if api_key:
                            image_bytes = generate_image_gemini(prompt, api_key, width, height, 'standard')
                    elif provider == 'together' and generate_image_together:
                        # Obter chave da API
                        api_key = self._get_api_key('together')
                        if api_key:
                            image_bytes = generate_image_together(prompt, api_key, width, height, 'standard', 'black-forest-labs/FLUX.1-krea-dev')
                    
                    if image_bytes is None:
                        self._log('warning', f'Falha ao gerar imagem {i+1}/{len(prompts_to_generate)}: {prompt[:50]}...')
                        continue
                    
                    # Salvar a imagem (mesmo método da aba de automações)
                    timestamp = int(time.time() * 1000)
                    filename = f"pipeline_{self.pipeline_id}_image_{timestamp}_{i+1}.png"
                    
                    # Criar diretório de output se não existir
                    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'images')
                    os.makedirs(output_dir, exist_ok=True)
                    
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(image_bytes)
                    
                    # URL para acessar a imagem
                    image_url = f"/api/images/view/{filename}"
                    
                    generated_images.append({
                        'file_path': filepath,
                        'filename': filename,
                        'url': image_url,
                        'file_size': len(image_bytes),
                        'resolution': resolution,
                        'prompt_used': prompt,
                        'provider': provider,
                        'generation_time': datetime.utcnow().isoformat()
                    })
                    
                    self._log('info', f'Imagem {i + 1}/{len(prompts_to_generate)} salva com sucesso - {filename}')
                    
                    # Delay entre gerações (mesmo da aba de automações)
                    if i < len(prompts_to_generate) - 1:
                        if provider == 'pollinations':
                            time.sleep(5)  # 5 segundos para Pollinations
                        else:
                            time.sleep(2)  # 2 segundos para outras APIs
                            
                except Exception as e:
                    self._log('warning', f'Erro ao processar imagem {i+1}: {str(e)}')
                    continue
            
            self._log('info', f'Geração concluída: {len(generated_images)}/{len(prompts_to_generate)} imagens')
            return generated_images
            
        except Exception as e:
            self._log('error', f'Erro na geração de imagens com lógica de automações: {str(e)}')
            return []
    
    def _distribute_scenes_evenly(self, scenes: List[str], target_count: int) -> List[str]:
        """Distribuir cenas uniformemente para atingir o número alvo de imagens"""
        if len(scenes) <= target_count:
            return scenes
        
        # Selecionar cenas uniformemente distribuídas
        step = len(scenes) / target_count
        selected_scenes = []
        
        for i in range(target_count):
            index = int(i * step)
            if index < len(scenes):
                selected_scenes.append(scenes[index])
        
        return selected_scenes
    
    def _get_api_key(self, provider: str) -> Optional[str]:
        """Obter chave da API para o provedor especificado"""
        try:
            import os
            if provider == 'gemini':
                return os.getenv('GEMINI_API_KEY')
            elif provider == 'together':
                return os.getenv('TOGETHER_API_KEY')
            return None
        except Exception:
            return None
    
    def generate_images_for_script_total(self, script_text: str, provider: str, style: str, 
                                        resolution: str, total_images: int, custom_image_prompt: str = "") -> Dict[str, Any]:
        """Gerar imagens distribuindo total de imagens ao longo de todo o roteiro"""
        try:
            self._log('info', f'Iniciando geração de {total_images} imagens distribuídas ao longo do roteiro')
            
            # Usar a lógica de distribuição uniforme que já existe nas automações
            generated_images = self._generate_images_with_automation_logic(
                script_text, provider, style, resolution, total_images
            )
            
            return {
                'images': generated_images,
                'total_requested': total_images,
                'total_generated': len(generated_images),
                'distribution_method': 'total_uniform'
            }
            
        except Exception as e:
            self._log('error', f'Erro na geração de imagens por total: {str(e)}')
            raise

    def generate_images_for_script(self, script_text: str, provider: str, style: str, 
                                 resolution: str, per_chapter: int, custom_image_prompt: str = "") -> Dict[str, Any]:
        """Gerar imagens para o roteiro usando a mesma lógica da aba de automações"""
        try:
            self._log('info', 'Iniciando geração de imagens para o roteiro')
            
            # Dividir roteiro em capítulos/seções
            chapters = self._extract_chapters_from_script(script_text)
            
            if not chapters:
                chapters = [script_text]
            
            self._log('info', f'Roteiro dividido em {len(chapters)} capítulos')
            
            # Calcular total de imagens a gerar
            total_images = len(chapters) * per_chapter
            self._log('info', f'Gerando {total_images} imagens ({per_chapter} por capítulo)')
            
            # Gerar imagens usando a lógica da aba de automações
            generated_images = self._generate_images_with_automation_logic(
                script_text, provider, style, resolution, total_images
            )
            
            return {
                'images': generated_images,
                'total_chapters': len(chapters),
                'prompts_generated': total_images,
                'total_generated': len(generated_images)
            }
            
        except Exception as e:
            self._log('error', f'Erro na geração de imagens: {str(e)}')
            raise
    
    def _extract_chapters_from_script(self, script_text: str) -> List[str]:
        """Extrair capítulos do roteiro"""
        try:
            # Tentar dividir por marcadores comuns de capítulos
            chapter_markers = [
                '## Capítulo',
                '## Chapter',
                '# Capítulo',
                '# Chapter',
                'CAPÍTULO',
                'CHAPTER',
                '---',
                '***'
            ]
            
            chapters = []
            current_chapter = ""
            lines = script_text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Verificar se é um marcador de capítulo
                is_chapter_marker = any(marker in line.upper() for marker in chapter_markers)
                
                if is_chapter_marker and current_chapter:
                    # Salvar capítulo anterior
                    chapters.append(current_chapter.strip())
                    current_chapter = line + '\n'
                else:
                    current_chapter += line + '\n'
            
            # Adicionar último capítulo
            if current_chapter.strip():
                chapters.append(current_chapter.strip())
            
            # Se não conseguiu dividir adequadamente, dividir por parágrafos
            if len(chapters) < 2:
                paragraphs = script_text.split('\n\n')
                if len(paragraphs) > 1:
                    chapters = [p.strip() for p in paragraphs if p.strip()]
            
            # Se ainda não conseguiu, dividir por tamanho
            if len(chapters) < 2:
                words = script_text.split()
                chunk_size = max(100, len(words) // 5)  # Pelo menos 5 capítulos
                chapters = []
                
                for i in range(0, len(words), chunk_size):
                    chunk = ' '.join(words[i:i + chunk_size])
                    chapters.append(chunk)
            
            return chapters
            
        except Exception as e:
            self._log('warning', f'Erro ao extrair capítulos: {str(e)}')
            return [script_text]  # Retornar texto completo como fallback
    
    def _generate_prompts_for_chapter(self, chapter_text: str, chapter_num: int, 
                                    per_chapter: int, style: str) -> List[Dict[str, Any]]:
        """Gerar prompts de imagem para um capítulo"""
        try:
            # Usar Gemini para gerar prompts otimizados
            prompts = self._generate_prompts_with_gemini(
                chapter_text, chapter_num, per_chapter, style
            )
            
            return prompts
            
        except Exception as e:
            self._log('warning', f'Erro ao gerar prompts para capítulo {chapter_num}: {str(e)}')
            # Fallback: gerar prompts básicos
            return self._generate_basic_prompts(chapter_text, chapter_num, per_chapter, style)
    
    def _generate_prompts_with_gemini(self, chapter_text: str, chapter_num: int, 
                                    per_chapter: int, style: str) -> List[Dict[str, Any]]:
        """Gerar prompts usando Gemini"""
        try:
            import google.generativeai as genai
            
            # Obter chave da API
            from routes.automations import get_next_gemini_key
            api_key = get_next_gemini_key()
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Definir estilos de prompt
            style_descriptions = {
                'cinematic': 'cinematográfico, iluminação dramática, composição profissional, alta qualidade',
                'realistic': 'fotorrealista, detalhado, natural, alta resolução',
                'artistic': 'artístico, estilizado, criativo, expressivo',
                'minimalist': 'minimalista, limpo, simples, elegante',
                'vibrant': 'vibrante, colorido, energético, dinâmico'
            }
            
            style_desc = style_descriptions.get(style, style_descriptions['cinematic'])
            
            # Prompt para Gemini
            gemini_prompt = f"""
            Baseado no seguinte texto de roteiro do Capítulo {chapter_num}, crie {per_chapter} prompts detalhados para geração de imagens.
            
            Texto do capítulo:
            {chapter_text[:1000]}...
            
            Estilo desejado: {style_desc}
            
            Para cada prompt, você deve:
            1. Identificar os elementos visuais principais do texto
            2. Criar uma descrição visual detalhada e específica
            3. Incluir detalhes de estilo, iluminação e composição
            4. Usar termos técnicos de fotografia/cinema quando apropriado
            5. Manter consistência com o estilo "{style}"
            
            Retorne APENAS um JSON válido no formato:
            {{
                "prompts": [
                    {{
                        "description": "descrição detalhada da imagem",
                        "scene": "resumo da cena",
                        "style_tags": "tags de estilo separadas por vírgula"
                    }}
                ]
            }}
            
            Exemplo de prompt bem detalhado:
            "A professional AI agent working at a modern computer setup, multiple monitors displaying code and data analytics, sleek office environment, soft blue lighting, shallow depth of field, cinematic composition, high-tech atmosphere, 4K quality, photorealistic"
            """
            
            response = model.generate_content(gemini_prompt)
            response_text = response.text.strip()
            
            # Tentar extrair JSON da resposta
            try:
                # Remover markdown se presente
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0]
                elif '```' in response_text:
                    response_text = response_text.split('```')[1].split('```')[0]
                
                result = json.loads(response_text)
                prompts_data = result.get('prompts', [])
                
                # Formatar prompts
                formatted_prompts = []
                for i, prompt_data in enumerate(prompts_data[:per_chapter]):
                    formatted_prompts.append({
                        'chapter': chapter_num,
                        'index': i + 1,
                        'description': prompt_data.get('description', ''),
                        'scene': prompt_data.get('scene', ''),
                        'style_tags': prompt_data.get('style_tags', ''),
                        'full_prompt': self._build_full_prompt(
                            prompt_data.get('description', ''), style
                        )
                    })
                
                return formatted_prompts
                
            except json.JSONDecodeError as e:
                self._log('warning', f'Erro ao parsear JSON do Gemini: {str(e)}')
                # Fallback: usar texto bruto como prompt
                return [{
                    'chapter': chapter_num,
                    'index': 1,
                    'description': response_text[:200],
                    'scene': f'Capítulo {chapter_num}',
                    'style_tags': style,
                    'full_prompt': self._build_full_prompt(response_text[:200], style)
                }]
            
        except Exception as e:
            self._log('warning', f'Erro ao usar Gemini para prompts: {str(e)}')
            raise
    
    def _generate_basic_prompts(self, chapter_text: str, chapter_num: int, 
                              per_chapter: int, style: str) -> List[Dict[str, Any]]:
        """Gerar prompts básicos como fallback"""
        prompts = []
        
        # Extrair palavras-chave do texto
        keywords = self._extract_keywords(chapter_text)
        
        for i in range(per_chapter):
            # Criar prompt básico
            base_description = f"Scene from chapter {chapter_num}, featuring {', '.join(keywords[:3])}"
            full_prompt = self._build_full_prompt(base_description, style)
            
            prompts.append({
                'chapter': chapter_num,
                'index': i + 1,
                'description': base_description,
                'scene': f'Capítulo {chapter_num} - Cena {i + 1}',
                'style_tags': style,
                'full_prompt': full_prompt
            })
        
        return prompts
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrair palavras-chave do texto"""
        # Lista de palavras comuns a ignorar
        stop_words = {
            'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das',
            'em', 'no', 'na', 'nos', 'nas', 'para', 'por', 'com', 'sem', 'sobre', 'entre',
            'que', 'quando', 'onde', 'como', 'por que', 'porque', 'se', 'mas', 'ou', 'e',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extrair palavras
        words = text.lower().split()
        keywords = []
        
        for word in words:
            # Remover pontuação
            clean_word = ''.join(c for c in word if c.isalnum())
            
            # Filtrar palavras muito curtas e stop words
            if len(clean_word) > 3 and clean_word not in stop_words:
                keywords.append(clean_word)
        
        # Retornar palavras únicas, limitadas
        return list(set(keywords))[:10]
    
    def _build_full_prompt(self, description: str, style: str) -> str:
        """Construir prompt completo com modificadores de estilo"""
        style_modifiers = {
            'cinematic': ', cinematic lighting, professional composition, film grain, dramatic shadows, high contrast, 4K quality',
            'realistic': ', photorealistic, highly detailed, natural lighting, sharp focus, professional photography, 8K resolution',
            'artistic': ', artistic style, creative composition, expressive colors, stylized rendering, digital art, concept art',
            'minimalist': ', minimalist style, clean composition, simple colors, negative space, elegant design, modern aesthetic',
            'vibrant': ', vibrant colors, dynamic composition, energetic mood, saturated colors, high contrast, bold visual style'
        }
        
        modifier = style_modifiers.get(style, style_modifiers['cinematic'])
        
        # Adicionar qualificadores técnicos
        technical_tags = ', professional quality, detailed, masterpiece, trending on artstation'
        
        return f"{description}{modifier}{technical_tags}"
    
    def _generate_with_pollinations(self, image_prompts: List[Dict[str, Any]], 
                                  resolution: str, style: str) -> List[Dict[str, Any]]:
        """Gerar imagens usando Pollinations"""
        generated_images = []
        
        for i, prompt_data in enumerate(image_prompts):
            try:
                self._log('info', f'Gerando imagem {i + 1}/{len(image_prompts)}')
                
                # Gerar imagem
                image_result = self._generate_single_image_pollinations(
                    prompt_data['full_prompt'], resolution, i + 1
                )
                
                if image_result:
                    image_result.update({
                        'chapter': prompt_data['chapter'],
                        'index': prompt_data['index'],
                        'description': prompt_data['description'],
                        'scene': prompt_data['scene'],
                        'prompt_used': prompt_data['full_prompt']
                    })
                    generated_images.append(image_result)
                
                # Delay entre requisições
                time.sleep(1)
                
            except Exception as e:
                self._log('warning', f'Erro ao gerar imagem {i + 1}: {str(e)}')
                continue
        
        return generated_images
    
    def _generate_single_image_pollinations(self, prompt: str, resolution: str, 
                                          image_index: int) -> Optional[Dict[str, Any]]:
        """Gerar uma única imagem usando Pollinations"""
        try:
            # Preparar parâmetros
            width, height = resolution.split('x')
            encoded_prompt = quote(prompt)
            
            # URL da API Pollinations
            url = f"{self.pollinations_base_url}/{encoded_prompt}"
            
            # Parâmetros adicionais
            params = {
                'width': width,
                'height': height,
                'seed': int(time.time()) + image_index,  # Seed único
                'model': 'flux',  # Modelo padrão
                'enhance': 'true'
            }
            
            # Fazer requisição
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(url, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        # Salvar imagem
                        image_filename = f"image_{self.pipeline_id}_{image_index}.jpg"
                        image_path = os.path.join('outputs', image_filename)
                        
                        os.makedirs('outputs', exist_ok=True)
                        
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Verificar tamanho do arquivo
                        file_size = os.path.getsize(image_path)
                        
                        return {
                            'file_path': image_path,
                            'filename': image_filename,
                            'url': response.url,
                            'file_size': file_size,
                            'resolution': resolution,
                            'generation_time': datetime.utcnow().isoformat()
                        }
                    
                    else:
                        self._log('warning', f'Pollinations retornou status {response.status_code}')
                        
                except requests.RequestException as e:
                    self._log('warning', f'Erro na requisição (tentativa {attempt + 1}): {str(e)}')
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
            
            return None
            
        except Exception as e:
            self._log('error', f'Erro ao gerar imagem com Pollinations: {str(e)}')
            return None
    
    def generate_thumbnail(self, title: str, style: str = 'youtube') -> Optional[Dict[str, Any]]:
        """Gerar thumbnail para o vídeo"""
        try:
            self._log('info', 'Gerando thumbnail do vídeo')
            
            # Prompt específico para thumbnail
            thumbnail_prompt = f"""
            YouTube thumbnail for video titled "{title}", 
            eye-catching design, bold text overlay, vibrant colors, 
            high contrast, clickbait style, professional quality, 
            1280x720 resolution, engaging composition
            """
            
            # Gerar thumbnail
            result = self._generate_single_image_pollinations(
                thumbnail_prompt, '1280x720', 999
            )
            
            if result:
                result['type'] = 'thumbnail'
                result['title'] = title
                
                self._log('info', 'Thumbnail gerada com sucesso')
                return result
            
            return None
            
        except Exception as e:
            self._log('error', f'Erro ao gerar thumbnail: {str(e)}')
            return None