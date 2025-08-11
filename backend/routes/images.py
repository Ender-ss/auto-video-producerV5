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
    Gera imagens a partir de um roteiro usando uma API de IA (Together.ai ou Gemini).
    """
    try:
        data = request.get_json()
        script = data.get('script', '').strip()
        api_key = data.get('api_key', '').strip()
        provider = data.get('provider', 'together')  # together ou gemini
        model = data.get('model', 'black-forest-labs/FLUX.1-krea-dev')
        style_prompt = data.get('style', 'cinematic, high detail, 4k')
        format_size = data.get('format', '1024x1024')
        quality = data.get('quality', 'standard')

        if not script:
            return jsonify({'success': False, 'error': 'Roteiro é obrigatório'}), 400

        if not api_key:
            return jsonify({'success': False, 'error': f'Chave da API ({provider}) é obrigatória'}), 400

        # Processar formato da imagem
        try:
            width, height = map(int, format_size.split('x'))
        except ValueError:
            width, height = 1024, 1024

        # 1. Dividir o roteiro em cenas/parágrafos
        scenes = [scene.strip() for scene in script.split('\n\n') if scene.strip()]
        
        if not scenes:
            return jsonify({'success': False, 'error': 'Não foi possível encontrar cenas no roteiro'}), 400

        generated_images = []

        # 2. Gerar uma imagem para cada cena
        for i, scene_text in enumerate(scenes):
            # Etapa futura: Usar um LLM para criar um prompt melhor a partir da cena
            # Por agora, usamos o texto da cena diretamente com um prompt de estilo
            
            prompt = f"{scene_text}, {style_prompt}"
            
            # Gerar imagem baseado no provedor
            if provider == 'gemini':
                image_bytes = generate_image_gemini(prompt, api_key, width, height, quality)
            else:  # together
                image_bytes = generate_image_together(prompt, api_key, width, height, quality, model)
            
            if image_bytes is None:
                return jsonify({'success': False, 'error': f'Erro ao gerar imagem para cena {i+1}'}), 500

            # Salvar a imagem
            timestamp = int(time.time() * 1000)
            filename = f"image_{timestamp}_{i+1}.png"
            filepath = os.path.join(OUTPUT_DIR, filename)

            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            # URL para acessar a imagem
            image_url = f"/api/images/view/{filename}"
            generated_images.append(image_url)

        return jsonify({
            'success': True,
            'message': f'{len(generated_images)} imagens geradas com sucesso!',
            'image_urls': generated_images
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

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
