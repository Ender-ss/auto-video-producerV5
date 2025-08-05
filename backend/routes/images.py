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
    Gera imagens a partir de um roteiro usando uma API de IA (ex: Together.ai).
    """
    try:
        data = request.get_json()
        script = data.get('script', '').strip()
        api_key = data.get('api_key', '').strip()
        model = data.get('model', 'stabilityai/stable-diffusion-3-medium')
        style_prompt = data.get('style', 'cinematic, high detail, 4k')

        if not script:
            return jsonify({'success': False, 'error': 'Roteiro é obrigatório'}), 400

        if not api_key:
            return jsonify({'success': False, 'error': 'Chave da API (Together.ai) é obrigatória'}), 400

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

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model,
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024" # ou "1024x576" para formato de vídeo
            }

            response = requests.post("https://api.together.xyz/v1/images/generations", headers=headers, json=payload, timeout=120)

            if response.status_code != 200:
                error_details = response.json().get('error', {}).get('message', response.text)
                return jsonify({'success': False, 'error': f'Erro na API Together.ai (cena {i+1}): {error_details}'}), 500

            # A API retorna os dados da imagem em base64
            image_data_b64 = response.json()['data'][0]['b64_json']
            image_bytes = base64.b64decode(image_data_b64)

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
