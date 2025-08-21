"""🎨 Image Queue Routes
Sistema de fila para geração de imagens e prompts automáticos
"""

from flask import Blueprint, request, jsonify, current_app
import os
import json
import time
import threading
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .images import generate_image_pollinations, generate_image_together, generate_image_gemini
from utils.error_messages import auto_format_error, format_error_response

image_queue_bp = Blueprint('image_queue', __name__)

# Diretório para salvar as imagens geradas
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output', 'images')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================================
# 🎯 ROTAS DA FILA DE IMAGENS
# ================================

@image_queue_bp.route('/queue', methods=['POST'])
def create_image_queue():
    """Criar nova fila de geração de imagens"""
    try:
        # Importar modelos dentro da função para evitar importação circular
        from database import db, ImageQueue
        
        data = request.get_json()
        title = data.get('title', '').strip()
        prompts = data.get('prompts', [])
        provider = data.get('provider', 'pollinations')
        model = data.get('model', 'flux')
        style = data.get('style', 'cinematic, high detail, 4k')
        format_size = data.get('format', '1024x1024')
        quality = data.get('quality', 'standard')
        
        if not title:
            return jsonify({'success': False, 'error': 'Título é obrigatório'}), 400
            
        if not prompts or len(prompts) == 0:
            return jsonify({'success': False, 'error': 'Lista de prompts é obrigatória'}), 400
        
        # Processar prompts se for string
        if isinstance(prompts, str):
            prompts = [p.strip() for p in prompts.split('\n') if p.strip()]
        
        # Criar nova fila
        queue = ImageQueue(
            title=title,
            prompts=json.dumps(prompts),
            total_prompts=len(prompts),
            provider=provider,
            model=model,
            style=style,
            format_size=format_size,
            quality=quality,
            generated_images=json.dumps([])
        )
        
        db.session.add(queue)
        db.session.commit()
        
        # Iniciar processamento em background
        from flask import current_app
        threading.Thread(target=process_image_queue, args=(queue.id, current_app._get_current_object()), daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': 'Fila de imagens criada com sucesso!',
            'queue_id': queue.id,
            'data': queue.to_dict()
        })
        
    except Exception as e:
        error_response = auto_format_error(str(e), 'Fila de Imagens')
        return jsonify(error_response), 500

@image_queue_bp.route('/queue/<int:queue_id>', methods=['GET'])
def get_queue_status(queue_id):
    """Obter status de uma fila específica"""
    try:
        # Importar modelos dentro da função para evitar importação circular
        from database import db, ImageQueue
        
        queue = ImageQueue.query.get_or_404(queue_id)
        return jsonify({
            'success': True,
            'data': queue.to_dict()
        })
    except Exception as e:
        error_response = auto_format_error(str(e), 'Fila de Imagens')
        return jsonify(error_response), 500

@image_queue_bp.route('/queue', methods=['GET'])
def list_queues():
    """Listar todas as filas de imagens"""
    try:
        # Importar modelos dentro da função para evitar importação circular
        from database import db, ImageQueue
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Consultar filas do banco de dados
        queues_query = ImageQueue.query.order_by(ImageQueue.created_at.desc())
        total = queues_query.count()
        
        # Paginação
        queues = queues_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'queues': [queue.to_dict() for queue in queues.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': queues.pages
                }
            }
        })
    except Exception as e:
        error_response = auto_format_error(str(e), 'Geração de Prompts')
        return jsonify(error_response), 500

@image_queue_bp.route('/queue/<int:queue_id>', methods=['DELETE'])
def delete_queue(queue_id):
    """Deletar uma fila de imagens"""
    try:
        # Importar modelos dentro da função para evitar importação circular
        from flask import current_app
        db = current_app.extensions['sqlalchemy'].db
        from database import ImageQueue
        
        queue = ImageQueue.query.get_or_404(queue_id)
        
        # Deletar imagens associadas
        if queue.generated_images:
            images = json.loads(queue.generated_images)
            for image_url in images:
                filename = image_url.split('/')[-1]
                filepath = os.path.join(OUTPUT_DIR, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        db.session.delete(queue)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Fila deletada com sucesso!'
        })
    except Exception as e:
        error_response = auto_format_error(str(e), 'Prompts de Roteiro')
        return jsonify(error_response), 500

# ================================
# 🤖 ROTAS DE GERAÇÃO AUTOMÁTICA
# ================================

@image_queue_bp.route('/script-to-prompts', methods=['POST'])
def script_to_prompts():
    """Gerar prompts automaticamente a partir de um roteiro"""
    try:
        # Importar modelos dentro da função para evitar importação circular
        from database import db, ScriptPrompt
        
        data = request.get_json()
        title = data.get('title', '').strip()
        script = data.get('script', '').strip()
        ai_model = data.get('ai_model', 'gpt-3.5-turbo')
        auto_queue = data.get('auto_queue', False)
        
        # Configurações da fila (se auto_queue for True)
        provider = data.get('provider', 'pollinations')
        model = data.get('model', 'flux')
        style = data.get('style', 'cinematic, high detail, 4k')
        format_size = data.get('format', '1024x1024')
        quality = data.get('quality', 'standard')
        
        if not title:
            return jsonify({'success': False, 'error': 'Título é obrigatório'}), 400
            
        if not script:
            return jsonify({'success': False, 'error': 'Roteiro é obrigatório'}), 400
        
        # Criar registro de processamento de prompts (modelo atual)
        script_prompt = ScriptPrompt(
            title=title,
            script_content=script,
            generated_prompts=json.dumps([]),
            total_prompts=0,
            provider=provider,
            model=model,
            style=style,
            format_size=format_size,
            quality=quality
        )
        
        db.session.add(script_prompt)
        db.session.commit()
        
        # Processar em background
        threading.Thread(
            target=process_script_to_prompts, 
            args=(script_prompt.id, auto_queue, provider, model, style, format_size, quality), 
            daemon=True
        ).start()
        
        return jsonify({
            'success': True,
            'message': 'Processamento iniciado! Os prompts serão gerados automaticamente.',
            'script_prompt_id': script_prompt.id,
            'data': script_prompt.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

@image_queue_bp.route('/script-prompts/<int:script_id>', methods=['GET'])
def get_script_prompts(script_id):
    """Obter prompts gerados a partir de um roteiro"""
    try:
        # Importar modelos dentro da função para evitar importação circular
        from database import db, ScriptPrompt
        
        script_prompt = ScriptPrompt.query.get_or_404(script_id)
        return jsonify({
            'success': True,
            'data': script_prompt.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

@image_queue_bp.route('/script-prompts', methods=['GET'])
def list_script_prompts():
    """Listar todos os prompts gerados a partir de roteiros"""
    try:
        # Importar modelos dentro da função para evitar importação circular
        from database import db, ScriptPrompt
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = ScriptPrompt.query.order_by(ScriptPrompt.created_at.desc())
        total = query.count()
        items = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'script_prompts': [sp.to_dict() for sp in items.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': items.pages
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

# ================================
# 🔧 FUNÇÕES DE PROCESSAMENTO
# ================================

def process_image_queue(queue_id, app):
    """Processar fila de imagens em background"""
    try:
        with app.app_context():
            # Importar modelos e db dentro da função para evitar importação circular
            from database import db, ImageQueue
            
            queue = ImageQueue.query.get(queue_id)
            if not queue:
                return
            
            # Atualizar status
            queue.status = 'processing'
            queue.started_at = datetime.utcnow()
            db.session.commit()
            
            prompts = json.loads(queue.prompts)
            generated_images = []
            
            for i, prompt in enumerate(prompts):
                try:
                    # Atualizar progresso
                    queue.current_prompt_index = i
                    queue.progress = int((i / len(prompts)) * 100)
                    db.session.commit()
                    
                    # Processar formato da imagem
                    try:
                        width, height = map(int, queue.format_size.split('x'))
                    except ValueError:
                        width, height = 1024, 1024
                    
                    # Gerar imagem baseado no provedor
                    image_bytes = None
                    full_prompt = f"{prompt}, {queue.style}"
                    
                    if queue.provider == 'gemini':
                        image_bytes = generate_image_pollinations(full_prompt, width, height, queue.quality, queue.model)
                    elif queue.provider == 'together':
                        image_bytes = generate_image_pollinations(full_prompt, width, height, queue.quality, queue.model)
                    else:  # pollinations
                        image_bytes = generate_image_pollinations(full_prompt, width, height, queue.quality, queue.model)
                    
                    if image_bytes:
                        # Salvar a imagem
                        timestamp = int(time.time() * 1000)
                        filename = f"queue_{queue_id}_{timestamp}_{i+1}.png"
                        filepath = os.path.join(OUTPUT_DIR, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(image_bytes)
                        
                        # URL para acessar a imagem
                        image_url = f"/api/images/view/{filename}"
                        generated_images.append(image_url)
                    else:
                        generated_images.append(None)
                        
                except Exception as e:
                    print(f"Erro ao processar prompt {i+1}: {str(e)}")
                    generated_images.append(None)
            
            # Finalizar processamento
            queue.status = 'completed'
            queue.progress = 100
            queue.current_prompt_index = len(prompts)
            queue.generated_images = json.dumps(generated_images)
            queue.completed_at = datetime.utcnow()
            db.session.commit()
            
    except Exception as e:
        # Marcar como erro
        with app.app_context():
            from database import db, ImageQueue
            queue = ImageQueue.query.get(queue_id)
            if queue:
                queue.status = 'failed'
                queue.error_message = str(e)
                db.session.commit()

def process_script_to_prompts(script_id, auto_queue=False, provider='pollinations', model='flux', style='cinematic, high detail, 4k', format_size='1024x1024', quality='standard', app=None):
    """Processar roteiro para gerar prompts automaticamente"""
    try:
        if app is None:
            from flask import current_app
            app = current_app._get_current_object()
        
        with app.app_context():
            # Importar modelos e db dentro da função para evitar importação circular
            from database import db, ScriptPrompt, ImageQueue
            
            script_prompt = ScriptPrompt.query.get(script_id)
            if not script_prompt:
                return
            
            start_time = time.time()
            
            # Dividir roteiro em cenas
            script = script_prompt.script_content
            scenes = [scene.strip() for scene in script.split('\n\n') if scene.strip()]
            
            if not scenes:
                # Tentar dividir por parágrafos ou frases
                scenes = [scene.strip() for scene in script.split('.') if scene.strip() and len(scene.strip()) > 20]
            
            # Gerar prompts para cada cena
            generated_prompts = []
            for i, scene in enumerate(scenes):
                prompt = generate_visual_prompt_from_scene(scene)
                generated_prompts.append({
                    'index': i + 1,
                    'scene': scene[:100] + '...' if len(scene) > 100 else scene,
                    'prompt': prompt
                })
            
            # Atualizar registro
            script_prompt.generated_prompts = json.dumps(generated_prompts)
            script_prompt.total_prompts = len(generated_prompts)
            
            # Se auto_queue for True, criar fila automaticamente
            if auto_queue and generated_prompts:
                prompts_only = [p['prompt'] for p in generated_prompts]
                
                queue = ImageQueue(
                    title=f"Auto: {script_prompt.title}",
                    prompts=json.dumps(prompts_only),
                    total_prompts=len(prompts_only),
                    provider=provider,
                    model=model,
                    style=style,
                    format_size=format_size,
                    quality=quality,
                    generated_images=json.dumps([])
                )
                
                db.session.add(queue)
                db.session.commit()
                
                # Iniciar processamento da fila
                threading.Thread(target=process_image_queue, args=(queue.id, app), daemon=True).start()
            
            db.session.commit()
            
    except Exception as e:
        # Em caso de erro, apenas registrar a mensagem de erro padrão
        if app is None:
            from flask import current_app
            app = current_app._get_current_object()
        
        with app.app_context():
            from database import db, ScriptPrompt
            sp = ScriptPrompt.query.get(script_id)
            if sp:
                # Não há campos de status/erro no modelo atual, então apenas manter os dados existentes
                pass

def generate_visual_prompt_from_scene(scene_text):
    """Gerar prompt visual a partir de uma cena de texto"""
    # Simplificação: extrair elementos visuais básicos
    # Em uma implementação mais avançada, usaria um LLM para isso
    
    scene_lower = scene_text.lower()
    
    # Detectar ambiente/cenário
    environments = {
        'casa': 'cozy home interior',
        'escritório': 'modern office space',
        'rua': 'urban street scene',
        'parque': 'beautiful park landscape',
        'praia': 'stunning beach scenery',
        'montanha': 'majestic mountain landscape',
        'cidade': 'bustling cityscape',
        'floresta': 'enchanted forest scene',
        'noite': 'atmospheric night scene',
        'dia': 'bright daylight scene'
    }
    
    # Detectar emoções/mood
    moods = {
        'feliz': 'joyful, bright, cheerful',
        'triste': 'melancholic, somber, emotional',
        'tenso': 'dramatic, intense, suspenseful',
        'calmo': 'peaceful, serene, tranquil',
        'romântico': 'romantic, warm, intimate',
        'misterioso': 'mysterious, dark, intriguing'
    }
    
    # Detectar pessoas/personagens
    characters = {
        'homem': 'man',
        'mulher': 'woman',
        'criança': 'child',
        'pessoa': 'person',
        'pessoas': 'people',
        'família': 'family'
    }
    
    prompt_parts = []
    
    # Adicionar ambiente
    for keyword, description in environments.items():
        if keyword in scene_lower:
            prompt_parts.append(description)
            break
    
    # Adicionar personagens
    for keyword, description in characters.items():
        if keyword in scene_lower:
            prompt_parts.append(description)
            break
    
    # Adicionar mood
    for keyword, description in moods.items():
        if keyword in scene_lower:
            prompt_parts.append(description)
            break
    
    # Se não encontrou nada específico, usar o texto da cena diretamente (limitado)
    if not prompt_parts:
        # Pegar as primeiras palavras importantes
        words = scene_text.split()[:10]
        prompt_parts.append(' '.join(words))
    
    return ', '.join(prompt_parts)