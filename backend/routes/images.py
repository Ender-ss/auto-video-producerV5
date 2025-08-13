"""
🖼️ Image Generation Routes
Rotas para geração de imagens com IA
"""

from flask import Blueprint, request, jsonify
import os
import requests
import base64
import time

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
        image_count = data.get('image_count', 1)
        
        # Validações
        if use_custom_prompt:
            if not custom_prompt:
                return jsonify({'success': False, 'error': 'Prompt personalizado é obrigatório quando selecionado'}), 400
        else:
            if not script:
                return jsonify({'success': False, 'error': 'Roteiro é obrigatório'}), 400

        # Pollinations.ai não requer chave de API (é gratuito)
        if not api_key and provider != 'pollinations':
            return jsonify({'success': False, 'error': f'Chave da API ({provider}) é obrigatória'}), 400

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
                scene_prompts = generate_scene_prompts_with_ai(script, ai_agent_prompt, api_key, provider, image_count)
                if not scene_prompts:
                    return jsonify({'success': False, 'error': 'Erro ao gerar prompts com IA Agent'}), 500
                
                for scene_prompt in scene_prompts:
                    final_prompt = f"{scene_prompt}, {style_prompt}"
                    prompts_to_generate.append(final_prompt)
            else:
                # Dividir roteiro em cenas/parágrafos (modo tradicional)
                scenes = [scene.strip() for scene in script.split('\n\n') if scene.strip()]
                
                if not scenes:
                    return jsonify({'success': False, 'error': 'Não foi possível encontrar cenas no roteiro'}), 400
                
                # Limitar ao número de imagens solicitado
                scenes_to_use = scenes[:image_count] if image_count <= len(scenes) else scenes
                
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
            return jsonify({'success': False, 'error': 'Não foi possível gerar nenhuma imagem'}), 500

        return jsonify({
            'success': True,
            'message': f'{len(generated_images)} imagens geradas com sucesso!',
            'image_urls': generated_images,
            'total_requested': len(prompts_to_generate),
            'total_generated': len(generated_images)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

def generate_scene_prompts_with_ai(script, ai_agent_prompt, api_key, provider, image_count):
    """
    Usa IA para gerar prompts específicos de imagem baseados no roteiro.
    """
    try:
        # Prompt para o IA Agent
        system_prompt = f"""
{ai_agent_prompt}

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
        
        # Fallback: dividir roteiro em partes
        scenes = [scene.strip() for scene in script.split('\n\n') if scene.strip()]
        return scenes[:image_count] if scenes else [script]
        
    except Exception as e:
        print(f"Erro ao gerar prompts com IA Agent: {str(e)}")
        # Fallback: dividir roteiro em partes
        scenes = [scene.strip() for scene in script.split('\n\n') if scene.strip()]
        return scenes[:image_count] if scenes else [script]

@images_bp.route('/view/<filename>')
def serve_image(filename):
    """
    Serve uma imagem gerada a partir do diretório de output.
    """
    try:
        from flask import send_from_directory
        return send_from_directory(OUTPUT_DIR, filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

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
    Generate image using Gemini 2.0 Flash Preview Image Generation
    """
    try:
        from google import genai
        from google.genai import types
        import base64
        from io import BytesIO
        
        # Debug: Check if API key is provided
        # print(f"Gemini API key received: {api_key[:10]}..." if api_key and len(api_key) > 10 else f"Gemini API key: {api_key}")
        
        # Create Gemini client
        client = genai.Client(api_key=api_key)
        
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
                
                return image_bytes
        
        raise Exception("No image data found in Gemini response")
        
    except Exception as e:
        print(f"Error generating image with Gemini: {str(e)}")
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
