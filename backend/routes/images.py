"""
🖼️ Image Generation Routes
Rotas para geração de imagens com IA
"""

from flask import Blueprint, request, jsonify
import os
import requests
import base64
import time
from utils.error_messages import auto_format_error, format_error_response
from routes.prompts_config import load_prompts_config

images_bp = Blueprint('images', __name__)

# Diretório para salvar as imagens geradas
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output', 'images')
os.makedirs(OUTPUT_DIR, exist_ok=True)

@images_bp.route('/generate', methods=['POST'])
def generate_images_route():
    """
    Gera imagens a partir de um roteiro usando uma API de IA com suporte a IA Agent e processamento em fila.
    """
    try:
        data = request.get_json()
        
        # Parâmetros básicos
        script = data.get('script', '').strip()
        api_key = data.get('api_key', '').strip()
        provider = data.get('provider', 'pollinations')  # pollinations, together, gemini
        model = data.get('model', 'black-forest-labs/FLUX.1-krea-dev')
        style_prompt = data.get('style', 'cinematic, high detail, 4k')
        format_size = data.get('format', '1024x1024')
        quality = data.get('quality', 'standard')
        pollinations_model = data.get('pollinations_model', 'flux')  # flux ou gpt
        
        # Novos parâmetros
        use_ai_agent = data.get('use_ai_agent', False)
        ai_agent_prompt = data.get('ai_agent_prompt', '')
        use_custom_prompt = data.get('use_custom_prompt', False)
        custom_prompt = data.get('custom_prompt', '').strip()
        use_custom_image_prompt = data.get('use_custom_image_prompt', False)
        custom_image_prompt = data.get('custom_image_prompt', '').strip()
        image_count = data.get('image_count', 1)
        
        # Validações
        if use_custom_prompt:
            if not custom_prompt:
                error_response = format_error_response('validation_error', 'Prompt personalizado é obrigatório quando selecionado', 'Geração de Imagens')
                return jsonify(error_response), 400
        else:
            if not script:
                error_response = format_error_response('validation_error', 'Roteiro é obrigatório para gerar imagens baseadas no conteúdo', 'Geração de Imagens')
                return jsonify(error_response), 400

        # Pollinations.ai não requer chave de API (é gratuito)
        if not api_key and provider != 'pollinations':
            error_response = format_error_response('api_key_missing', f'Chave da API ({provider}) é obrigatória', 'Geração de Imagens')
            return jsonify(error_response), 400

        # Processar formato da imagem
        try:
            width, height = map(int, format_size.split('x'))
        except ValueError:
            width, height = 1024, 1024

        generated_images = []
        prompts_to_generate = []

        # Determinar prompts baseado no modo selecionado
        if use_custom_prompt:
            # Modo: Prompt personalizado
            for i in range(image_count):
                final_prompt = f"{custom_prompt}, {style_prompt}"
                prompts_to_generate.append(final_prompt)
        else:
            # Modo: Baseado em roteiro
            if use_ai_agent and ai_agent_prompt:
                # Usar IA Agent para criar prompts específicos
                scene_prompts = generate_scene_prompts_with_ai(script, ai_agent_prompt, api_key, provider, image_count, use_custom_image_prompt, custom_image_prompt)
                if not scene_prompts:
                    error_response = format_error_response('internal_error', 'Não foi possível gerar prompts automaticamente com IA', 'IA Agent para Imagens')
                    return jsonify(error_response), 500
                
                for scene_prompt in scene_prompts:
                    final_prompt = f"{scene_prompt}, {style_prompt}"
                    prompts_to_generate.append(final_prompt)
            else:
                # Dividir roteiro em cenas/parágrafos (modo tradicional)
                scenes = [scene.strip() for scene in script.split('\n\n') if scene.strip()]
                
                if not scenes:
                    error_response = format_error_response('content_too_long', 'O roteiro precisa ter parágrafos separados para gerar imagens', 'Análise de Roteiro')
                    return jsonify(error_response), 400
                
                # Distribuir cenas uniformemente ao longo do roteiro completo
                scenes_to_use = distribute_scenes_evenly(scenes, image_count)
                
                for scene_text in scenes_to_use:
                    final_prompt = f"{scene_text}, {style_prompt}"
                    prompts_to_generate.append(final_prompt)

        # Gerar imagens para cada prompt
        for i, prompt in enumerate(prompts_to_generate):
            try:
                # Gerar imagem baseado no provedor
                if provider == 'gemini':
                    image_bytes = generate_image_gemini(prompt, api_key, width, height, quality)
                elif provider == 'pollinations':
                    image_bytes = generate_image_pollinations(prompt, width, height, quality, pollinations_model)
                else:  # together
                    image_bytes = generate_image_together(prompt, api_key, width, height, quality, model)
                
                if image_bytes is None:
                    print(f"Erro ao gerar imagem {i+1}: {prompt[:50]}...")
                    continue

                # Salvar a imagem
                timestamp = int(time.time() * 1000)
                filename = f"image_{timestamp}_{i+1}.png"
                filepath = os.path.join(OUTPUT_DIR, filename)

                with open(filepath, 'wb') as f:
                    f.write(image_bytes)

                # URL para acessar a imagem
                image_url = f"/api/images/view/{filename}"
                generated_images.append(image_url)
                
                # Delay entre gerações para respeitar limites de taxa
                if i < len(prompts_to_generate) - 1:  # Não aguardar após a última imagem
                    if provider == 'pollinations':
                        time.sleep(5)  # 5 segundos para Pollinations
                    else:
                        time.sleep(2)  # 2 segundos para outras APIs
                        
            except Exception as e:
                print(f"Erro ao processar imagem {i+1}: {str(e)}")
                continue

        if not generated_images:
            error_response = format_error_response('internal_error', 'Todas as tentativas de geração de imagem falharam', 'Geração de Imagens')
            return jsonify(error_response), 500

        return jsonify({
            'success': True,
            'message': f'{len(generated_images)} imagens geradas com sucesso!',
            'image_urls': generated_images,
            'total_requested': len(prompts_to_generate),
            'total_generated': len(generated_images)
        })

    except Exception as e:
        error_response = auto_format_error(str(e), 'Geração de Imagens')
        return jsonify(error_response), 500

def distribute_scenes_evenly(scenes, image_count):
    """
    Distribui cenas uniformemente ao longo do roteiro completo.
    Evita repetições desnecessárias e garante distribuição inteligente.
    """
    total_scenes = len(scenes)
    
    if image_count <= 0:
        return []
    
    if image_count <= total_scenes:
        # Se queremos menos ou igual imagens que cenas, selecionar uniformemente
        selected_scenes = []
        step = total_scenes / image_count
        
        for i in range(image_count):
            scene_index = int(i * step)
            # Garantir que não exceda o índice
            scene_index = min(scene_index, total_scenes - 1)
            selected_scenes.append(scenes[scene_index])
        
        return selected_scenes
    else:
        # Se queremos mais imagens que cenas, usar estratégia inteligente
        selected_scenes = []
        
        # Primeiro, incluir todas as cenas originais
        for scene in scenes:
            selected_scenes.append(scene)
        
        # Calcular quantas imagens extras precisamos
        remaining_images = image_count - total_scenes
        
        # Distribuir as imagens extras uniformemente entre as cenas
        if remaining_images > 0:
            # Lista de variações para tornar cada prompt único
            variations = [
                "different angle and perspective",
                "close-up shot", 
                "wide angle view",
                "dramatic lighting",
                "soft lighting",
                "from above perspective",
                "from below perspective",
                "side view",
                "detailed focus",
                "atmospheric mood",
                "golden hour lighting",
                "blue hour ambiance",
                "high contrast",
                "soft focus background",
                "dynamic composition"
            ]
            
            for i in range(remaining_images):
                scene_index = i % total_scenes
                variation_index = i % len(variations)
                
                # Adicionar variação ao prompt para evitar imagens idênticas
                original_scene = scenes[scene_index]
                variation = variations[variation_index]
                varied_scene = f"{original_scene}, {variation}"
                selected_scenes.append(varied_scene)
        
        return selected_scenes

def generate_scene_prompts_with_ai(script, ai_agent_prompt, api_key, provider, image_count, use_custom_image_prompt=False, custom_image_prompt=None):
    """
    Usa IA para gerar prompts específicos de imagem baseados no roteiro.
    """
    try:
        # Carregar prompt personalizado se solicitado
        if use_custom_image_prompt and custom_image_prompt:
            base_prompt = custom_image_prompt
        elif use_custom_image_prompt:
            # Carregar prompt personalizado do arquivo de configuração
            try:
                prompts_config = load_prompts_config()
                image_config = prompts_config.get('image_prompts', {})
                base_prompt = image_config.get('prompt', ai_agent_prompt)
                print(f"Usando prompt personalizado de imagem: {base_prompt[:100]}...")
            except Exception as e:
                print(f"Erro ao carregar prompt personalizado de imagem: {e}")
                base_prompt = ai_agent_prompt
        else:
            base_prompt = ai_agent_prompt
        
        # Prompt para o IA Agent
        system_prompt = f"""
{base_prompt}

Roteiro:
{script}

Gere exatamente {image_count} prompts de imagem baseados neste roteiro. Cada prompt deve:
1. Descrever uma cena visual específica
2. Ser detalhado e cinematográfico
3. Incluir elementos visuais importantes
4. Ser adequado para geração de imagem por IA

Retorne apenas os prompts, um por linha, sem numeração ou formatação extra.
        """
        
        if provider == 'together' and api_key:
            # Usar Together.ai para gerar os prompts
            import requests
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
                "messages": [
                    {"role": "system", "content": "Você é um especialista em criação de prompts para geração de imagens por IA."},
                    {"role": "user", "content": system_prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    content = response_data['choices'][0]['message']['content']
                    # Dividir em linhas e limpar
                    prompts = [line.strip() for line in content.split('\n') if line.strip()]
                    return prompts[:image_count]  # Garantir que não exceda o número solicitado
        
        # Fallback: dividir roteiro em partes e distribuir uniformemente
        scenes = [scene.strip() for scene in script.split('\n\n') if scene.strip()]
        if scenes:
            return distribute_scenes_evenly(scenes, image_count)
        else:
            return [script] * min(image_count, 1)
        
    except Exception as e:
        print(f"Erro ao gerar prompts com IA Agent: {str(e)}")
        # Fallback: dividir roteiro em partes e distribuir uniformemente
        scenes = [scene.strip() for scene in script.split('\n\n') if scene.strip()]
        if scenes:
            return distribute_scenes_evenly(scenes, image_count)
        else:
            return [script] * min(image_count, 1)

@images_bp.route('/view/<filename>')
def serve_image(filename):
    """
    Serve uma imagem gerada a partir do diretório de output.
    """
    try:
        from flask import send_from_directory
        return send_from_directory(OUTPUT_DIR, filename)
    except Exception as e:
        error_response = auto_format_error(str(e), 'Visualização de Imagem')
        return jsonify(error_response), 404

@images_bp.route('/list-generated', methods=['GET'])
def list_generated_content():
    """
    Lista todos os conteúdos gerados (imagens, áudios, vídeos)
    """
    try:
        import glob
        from datetime import datetime
        
        # Diretórios de conteúdo
        base_dir = os.path.join(os.path.dirname(__file__), '..')
        images_dir = os.path.join(base_dir, 'output', 'images')
        audio_dir = os.path.join(base_dir, 'output', 'audio')
        videos_dir = os.path.join(base_dir, 'output', 'videos')
        outputs_dir = os.path.join(base_dir, 'outputs')
        temp_dir = os.path.join(base_dir, 'temp')
        
        content = {
            'images': [],
            'audios': [],
            'videos': [],
            'total_files': 0
        }
        
        # Listar imagens
        if os.path.exists(images_dir):
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp']:
                for filepath in glob.glob(os.path.join(images_dir, ext)):
                    filename = os.path.basename(filepath)
                    file_stats = os.stat(filepath)
                    content['images'].append({
                        'filename': filename,
                        'path': filepath,
                        'url': f'/api/images/view/{filename}',
                        'size': file_stats.st_size,
                        'created_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                        'modified_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                    })
        
        # Listar áudios (verificar múltiplos diretórios)
        audio_dirs = [audio_dir, temp_dir]
        audio_files_seen = set()  # Para evitar duplicatas
        
        for audio_search_dir in audio_dirs:
            if os.path.exists(audio_search_dir):
                for ext in ['*.wav', '*.mp3', '*.m4a', '*.ogg', '*.flac']:
                    for filepath in glob.glob(os.path.join(audio_search_dir, ext)):
                        filename = os.path.basename(filepath)
                        
                        # Evitar duplicatas baseadas no nome do arquivo
                        if filename not in audio_files_seen:
                            audio_files_seen.add(filename)
                            file_stats = os.stat(filepath)
                            content['audios'].append({
                                'filename': filename,
                                'path': filepath,
                                'directory': os.path.basename(audio_search_dir),
                                'size': file_stats.st_size,
                                'created_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                                'modified_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                            })
        
        # Listar vídeos (verificar múltiplos diretórios)
        video_dirs = [videos_dir, outputs_dir]
        for video_search_dir in video_dirs:
            if os.path.exists(video_search_dir):
                for ext in ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.webm']:
                    for filepath in glob.glob(os.path.join(video_search_dir, ext)):
                        filename = os.path.basename(filepath)
                        file_stats = os.stat(filepath)
                        content['videos'].append({
                            'filename': filename,
                            'path': filepath,
                            'directory': os.path.basename(video_search_dir),
                            'size': file_stats.st_size,
                            'created_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                            'modified_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                        })
        
        # Ordenar por data de criação (mais recentes primeiro)
        content['images'].sort(key=lambda x: x['created_at'], reverse=True)
        content['audios'].sort(key=lambda x: x['created_at'], reverse=True)
        content['videos'].sort(key=lambda x: x['created_at'], reverse=True)
        
        # Calcular total
        content['total_files'] = len(content['images']) + len(content['audios']) + len(content['videos'])
        
        return jsonify({
            'success': True,
            'content': content,
            'summary': {
                'total_images': len(content['images']),
                'total_audios': len(content['audios']),
                'total_videos': len(content['videos']),
                'total_files': content['total_files']
            }
        })
        
    except Exception as e:
        error_response = auto_format_error(str(e), 'Listagem de Conteúdos')
        return jsonify(error_response), 500

def generate_image_together(prompt, api_key, width, height, quality, model):
    """
    Gera imagem usando a API Together.ai
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "prompt": prompt,
            "width": width,
            "height": height
        }

        response = requests.post("https://api.together.xyz/v1/images/generations", headers=headers, json=payload, timeout=120)

        if response.status_code != 200:
            return None

        # A API Together.ai retorna uma URL para a imagem
        response_data = response.json()
        
        if 'data' in response_data and len(response_data['data']) > 0:
            image_item = response_data['data'][0]
            if 'url' in image_item:
                # Baixar a imagem da URL fornecida
                img_response = requests.get(image_item['url'])
                if img_response.status_code == 200:
                    return img_response.content
        
        return None
    except Exception as e:
        print(f"Erro na API Together.ai: {str(e)}")
        return None

def generate_image_gemini(prompt, api_key, width, height, quality):
    """
    Generate image using Gemini 2.0 Flash Preview Image Generation with automatic retry system
    """
    from routes.automations import get_next_gemini_key, handle_gemini_429_error, get_gemini_keys_count
    
    # Usar a quantidade real de chaves disponíveis
    max_retries = get_gemini_keys_count() if get_gemini_keys_count() > 0 else 1
    print(f"🔑 Usando {max_retries} chaves Gemini para imagens")
    current_api_key = api_key
    
    for attempt in range(max_retries):
        try:
            from google import genai
            from google.genai import types
            import base64
            from io import BytesIO
            
            print(f"🎨 Tentativa {attempt + 1}/{max_retries} - Gerando imagem com Gemini")
            
            # Create Gemini client
            client = genai.Client(api_key=current_api_key)
            
            # Prepare the prompt with size specifications
            enhanced_prompt = f"{prompt}. Generate a {width}x{height} image."
            if quality == "hd":
                enhanced_prompt += " High quality, detailed, professional."
            
            # Generate content with image output using new API
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=enhanced_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"]
                )
            )
            
            # Extract image from response
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    # Get image data
                    image_data = part.inline_data.data
                    
                    # Convert to bytes if needed
                    if isinstance(image_data, str):
                        image_bytes = base64.b64decode(image_data)
                    else:
                        image_bytes = image_data
                    
                    print(f"✅ Sucesso! Imagem gerada com Gemini na tentativa {attempt + 1}")
                    return image_bytes
            
            raise Exception("No image data found in Gemini response")
            
        except Exception as e:
            error_str = str(e)
            print(f"❌ Erro na tentativa {attempt + 1}: {error_str}")
            
            # Check if it's a quota error (429)
            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                if attempt < max_retries - 1:  # Not the last attempt
                    print(f"🔄 Erro de quota detectado, tentando próxima chave Gemini...")
                    handle_gemini_429_error(error_str, current_api_key)
                    current_api_key = get_next_gemini_key()
                    if current_api_key:
                        print(f"🔑 Nova chave Gemini obtida para tentativa {attempt + 2}")
                        continue
                    else:
                        print("❌ Nenhuma chave Gemini disponível")
                        break
                else:
                    print("❌ Todas as tentativas de retry falharam")
                    handle_gemini_429_error(error_str, current_api_key)
            else:
                # For non-quota errors, don't retry
                print(f"❌ Erro não relacionado à quota, parando tentativas: {error_str}")
                break
    
    print("❌ Falha na geração de imagem com Gemini após todas as tentativas")
    return None

def generate_image_pollinations(prompt, width, height, quality, model='flux'):
    """
    Gera imagem usando Pollinations.ai com implementação melhorada e múltiplas estratégias
    Suporta modelos Flux e GPT para diferentes tipos de imagem
    """
    try:
        import urllib.parse
        import time
        import random
        
        print(f"🎨 Iniciando geração com Pollinations.ai")
        print(f"📝 Prompt: {prompt[:50]}...")
        print(f"📏 Dimensões: {width}x{height}")
        print(f"🤖 Modelo: {model}")
        
        # Melhorar o prompt baseado no modelo
        if model == 'gpt':
            enhanced_prompt = f"{prompt}, photorealistic, high quality, detailed, realistic"
        else:  # flux
            enhanced_prompt = f"{prompt}, artistic, creative, high quality"
        
        # Codificar o prompt para URL
        encoded_prompt = urllib.parse.quote(enhanced_prompt, safe='')
        
        # Headers melhorados com rotação de User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Estratégias de URL melhoradas
        base_urls = [
            "https://image.pollinations.ai/prompt",
            "https://pollinations.ai/p"
        ]
        
        # Parâmetros otimizados por modelo - PRIORIDADE PARA NOLOGO
        if model == 'gpt':
            param_sets = [
                f"?width={width}&height={height}&nologo=true&model=openai&enhance=true",
                f"?width={width}&height={height}&nologo=true&model=dalle&quality=hd",
                f"?width={width}&height={height}&nologo=true&enhance=true&realistic=true",
                f"?width={width}&height={height}&model=openai&enhance=true",
                f"?width={width}&height={height}&model=dalle&quality=hd",
                f"?width={width}&height={height}&enhance=true&realistic=true",
                f"?width={width}&height={height}&model=openai",
                f"?width={width}&height={height}"
            ]
        else:  # flux
            param_sets = [
                f"?width={width}&height={height}&nologo=true&model=flux&enhance=true",
                f"?width={width}&height={height}&nologo=true&model=flux-dev&quality=hd",
                f"?width={width}&height={height}&nologo=true&enhance=true",
                f"?width={width}&height={height}&nologo=true&model=flux",
                f"?width={width}&height={height}&model=flux&enhance=true",
                f"?width={width}&height={height}&model=flux-dev&quality=hd",
                f"?width={width}&height={height}&model=flux",
                f"?width={width}&height={height}"
            ]
        
        # Gerar todas as combinações de URLs
        urls_to_try = []
        for base_url in base_urls:
            for params in param_sets:
                urls_to_try.append(f"{base_url}/{encoded_prompt}{params}")
        
        # Tentar cada URL com estratégia melhorada
        for i, url in enumerate(urls_to_try, 1):
            try:
                print(f"🎨 Tentativa {i}/{len(urls_to_try)} - Pollinations.ai")
                print(f"🔗 URL: {url[:80]}...")
                
                # Timeout progressivo (mais tempo para tentativas posteriores)
                timeout = min(30 + (i * 5), 60)
                
                response = requests.get(
                    url, 
                    headers=headers, 
                    timeout=timeout,
                    allow_redirects=True,
                    stream=False,  # Não usar stream para evitar problemas
                    verify=True
                )
                
                print(f"📊 Status: {response.status_code} | Tamanho: {len(response.content)} bytes")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    content_length = len(response.content)
                    
                    # Validação melhorada de imagem
                    is_valid_image = (
                        content_length > 2000 and  # Limite mínimo reduzido
                        (
                            'image' in content_type or
                            response.content.startswith(b'\x89PNG') or  # PNG
                            response.content.startswith(b'\xff\xd8\xff') or  # JPEG
                            response.content.startswith(b'GIF8') or  # GIF
                            (response.content.startswith(b'RIFF') and b'WEBP' in response.content[:20]) or  # WebP
                            response.content.startswith(b'\x00\x00\x01\x00')  # ICO
                        )
                    )
                    
                    # Verificação anti-HTML melhorada
                    is_html = (
                        'text/html' in content_type or
                        b'<html' in response.content[:200].lower() or
                        b'<!doctype' in response.content[:200].lower() or
                        b'<body' in response.content[:500].lower()
                    )
                    
                    if is_valid_image and not is_html:
                        print(f"✅ Sucesso! Imagem gerada com Pollinations.ai")
                        print(f"📏 Dimensões solicitadas: {width}x{height}")
                        print(f"💾 Tamanho do arquivo: {content_length:,} bytes")
                        print(f"🤖 Modelo usado: {model}")
                        print(f"📝 Prompt final: {enhanced_prompt[:100]}...")
                        print(f"🔗 URL bem-sucedida: {url[:100]}...")
                        
                        # Tentar remover marca d'água por pós-processamento se necessário
                        processed_content = remove_watermark_if_needed(response.content, width, height)
                        return processed_content
                    else:
                        print(f"❌ Resposta inválida na tentativa {i}")
                        print(f"🔍 Content-Type: {content_type}")
                        print(f"📊 Tamanho: {content_length} bytes")
                        if is_html:
                            print("⚠️ Detectada resposta HTML")
                            html_preview = response.content[:300].decode('utf-8', errors='ignore')
                            print(f"🔍 HTML Preview: {html_preview}")
                        else:
                            print(f"⚠️ Imagem muito pequena ou formato inválido")
                        continue
                        
                elif response.status_code == 502:
                    print(f"🔄 Erro 502 (Bad Gateway) - Servidor sobrecarregado")
                    # Aguardar um pouco antes da próxima tentativa
                    time.sleep(2)
                    continue
                elif response.status_code == 503:
                    print(f"🔄 Erro 503 (Service Unavailable) - Serviço temporariamente indisponível")
                    time.sleep(3)
                    continue
                else:
                    print(f"❌ Erro HTTP {response.status_code}")
                    continue
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout na tentativa {i} (após {timeout}s)")
                continue
            except requests.exceptions.ConnectionError:
                print(f"🔌 Erro de conexão na tentativa {i}")
                time.sleep(1)  # Pequena pausa antes da próxima tentativa
                continue
            except Exception as e:
                print(f"❌ Erro na tentativa {i}: {str(e)}")
                continue
        
        # Fallbacks melhorados
        print(f"🔄 Tentando fallbacks...")
        
        # Fallback 1: Lorem Picsum (mais confiável)
        fallback_urls = [
            f"https://picsum.photos/{width}/{height}?random={int(time.time())}",
            f"https://picsum.photos/{width}/{height}",
            f"https://source.unsplash.com/{width}x{height}/?nature"
        ]
        
        for fallback_url in fallback_urls:
            try:
                print(f"🔄 Tentando fallback: {fallback_url}")
                response = requests.get(fallback_url, timeout=20, headers={'User-Agent': headers['User-Agent']})
                if response.status_code == 200 and len(response.content) > 1000:
                    print(f"✅ Fallback bem-sucedido: {len(response.content)} bytes")
                    return response.content
            except Exception as e:
                print(f"❌ Fallback falhou: {str(e)}")
                continue
        
        # Placeholder final melhorado
        print(f"⚠️ Gerando placeholder personalizado...")
        return generate_placeholder_image(width, height, prompt)
        
    except Exception as e:
        print(f"❌ Erro crítico: {str(e)}")
        return generate_placeholder_image(width, height, prompt)

def remove_watermark_if_needed(image_content, width, height):
    """
    Remove marca d'água cortando os últimos 45 pixels da parte inferior da imagem
    se detectar possível marca d'água do Pollinations.ai
    """
    try:
        from PIL import Image
        import io
        
        # Carregar a imagem
        img = Image.open(io.BytesIO(image_content))
        img_width, img_height = img.size
        
        # Verificar se a imagem tem dimensões que podem conter marca d'água
        # Pollinations.ai adiciona marca d'água principalmente em imagens menores
        if img_height > 100 and img_width >= 512:  # Só processar se for grande o suficiente
            # Cortar os últimos 45 pixels da parte inferior
            watermark_height = min(45, img_height // 10)  # Máximo 10% da altura
            cropped_img = img.crop((0, 0, img_width, img_height - watermark_height))
            
            # Redimensionar de volta para as dimensões originais se necessário
            if width and height and (cropped_img.width != width or cropped_img.height != height):
                cropped_img = cropped_img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Converter de volta para bytes
            output = io.BytesIO()
            cropped_img.save(output, format='PNG', optimize=True)
            
            print(f"🔧 Marca d'água removida: cortados {watermark_height}px da parte inferior")
            return output.getvalue()
        
        # Se não precisar de processamento, retornar original
        return image_content
        
    except Exception as e:
        print(f"⚠️ Erro ao processar remoção de marca d'água: {str(e)}")
        # Em caso de erro, retornar imagem original
        return image_content

def generate_placeholder_image(width, height, prompt):
    """
    Gera uma imagem placeholder quando todas as APIs falham
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Criar imagem placeholder
        img = Image.new('RGB', (width, height), color='#2D3748')
        draw = ImageDraw.Draw(img)
        
        # Tentar usar fonte padrão
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Texto do placeholder
        text_lines = [
            "🖼️ Imagem Placeholder",
            f"Prompt: {prompt[:50]}...",
            f"Tamanho: {width}x{height}",
            "APIs temporariamente indisponíveis"
        ]
        
        # Desenhar texto centralizado
        y_offset = height // 2 - (len(text_lines) * 30) // 2
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y_offset), line, fill='white', font=font)
            y_offset += 35
        
        # Converter para bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
        
    except Exception as e:
        print(f"❌ Erro ao gerar placeholder: {str(e)}")
        # Retornar uma imagem mínima se tudo falhar
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x04\x00\x00\x00\x04\x00\x08\x02\x00\x00\x00\x91\x5c\xef\x1f\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
