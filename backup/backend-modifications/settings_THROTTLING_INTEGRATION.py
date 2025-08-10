"""
⚙️ Settings Routes
Rotas para configurações do sistema
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import os
import json
import requests
import logging

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/api-keys', methods=['GET'])
def get_api_keys():
    """Obter chaves de API do arquivo de configuração"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                keys = json.load(f)

            return jsonify({
                'success': True,
                'keys': keys
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Arquivo de configuração não encontrado'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api-keys/<api_name>', methods=['GET'])
def get_single_api_key(api_name):
    """Obter uma chave de API específica."""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                keys = json.load(f)
            
            key_value = keys.get(api_name)
            
            if key_value:
                return jsonify({'success': True, 'api_key': key_value})
            else:
                return jsonify({'success': False, 'error': f'Chave para {api_name} não encontrada'}), 404
        else:
            return jsonify({'success': False, 'error': 'Arquivo de configuração não encontrado'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/apis', methods=['GET'])
def get_api_configs():
    """Obter configurações de APIs"""
    try:
        from app import APIConfig
        
        apis = APIConfig.query.all()
        
        return jsonify({
            'success': True,
            'data': {
                'apis': [api.to_dict() for api in apis]
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/apis/<api_name>', methods=['PUT'])
def update_api_config(api_name):
    """Atualizar configuração de API"""
    try:
        from app import APIConfig, db
        
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Chave da API é obrigatória'
            }), 400
        
        # Buscar ou criar configuração da API
        api_config = APIConfig.query.filter_by(api_name=api_name).first()
        if not api_config:
            api_config = APIConfig(api_name=api_name)
            db.session.add(api_config)
        
        # Atualizar configuração
        api_config.api_key = api_key
        api_config.is_configured = True
        api_config.last_used = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': api_config.to_dict(),
            'message': f'API {api_name} configurada com sucesso'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/apis/<api_name>/test', methods=['POST'])
def test_api_config(api_name):
    """Testar configuração de API"""
    try:
        from app import APIConfig
        
        api_config = APIConfig.query.filter_by(api_name=api_name).first()
        if not api_config or not api_config.is_configured:
            return jsonify({
                'success': False,
                'error': f'API {api_name} não configurada'
            }), 400
        
        # Testar API baseado no tipo
        test_result = test_api_connection(api_name, api_config.api_key)
        
        return jsonify(test_result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/apis/<api_name>', methods=['DELETE'])
def delete_api_config(api_name):
    """Deletar configuração de API"""
    try:
        from app import APIConfig, db
        
        api_config = APIConfig.query.filter_by(api_name=api_name).first()
        if not api_config:
            return jsonify({
                'success': False,
                'error': 'Configuração de API não encontrada'
            }), 404
        
        api_config.api_key = None
        api_config.is_configured = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Configuração da API {api_name} removida com sucesso'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/system', methods=['GET'])
def get_system_settings():
    """Obter configurações do sistema"""
    try:
        # Configurações padrão do sistema
        system_settings = {
            'max_concurrent_pipelines': int(os.getenv('MAX_CONCURRENT_PIPELINES', 3)),
            'default_video_quality': os.getenv('DEFAULT_VIDEO_QUALITY', '1080p'),
            'auto_retry_failed': os.getenv('AUTO_RETRY_FAILED', 'true').lower() == 'true',
            'max_video_duration': int(os.getenv('MAX_VIDEO_DURATION', 600)),
            'storage_path': os.getenv('STORAGE_PATH', './outputs'),
            'temp_path': os.getenv('TEMP_PATH', './temp'),
            'log_level': os.getenv('LOG_LEVEL', 'INFO')
        }
        
        return jsonify({
            'success': True,
            'data': {
                'system_settings': system_settings
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/system', methods=['PUT'])
def update_system_settings():
    """Atualizar configurações do sistema"""
    try:
        data = request.get_json()
        
        # Validar e atualizar configurações
        updated_settings = {}
        
        if 'max_concurrent_pipelines' in data:
            value = int(data['max_concurrent_pipelines'])
            if 1 <= value <= 10:
                os.environ['MAX_CONCURRENT_PIPELINES'] = str(value)
                updated_settings['max_concurrent_pipelines'] = value
        
        if 'default_video_quality' in data:
            quality = data['default_video_quality']
            if quality in ['720p', '1080p', '4k']:
                os.environ['DEFAULT_VIDEO_QUALITY'] = quality
                updated_settings['default_video_quality'] = quality
        
        if 'auto_retry_failed' in data:
            value = bool(data['auto_retry_failed'])
            os.environ['AUTO_RETRY_FAILED'] = str(value).lower()
            updated_settings['auto_retry_failed'] = value
        
        if 'max_video_duration' in data:
            value = int(data['max_video_duration'])
            if 60 <= value <= 1800:  # 1 min a 30 min
                os.environ['MAX_VIDEO_DURATION'] = str(value)
                updated_settings['max_video_duration'] = value
        
        return jsonify({
            'success': True,
            'data': {
                'updated_settings': updated_settings
            },
            'message': 'Configurações do sistema atualizadas com sucesso'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/backup', methods=['POST'])
def create_backup():
    """Criar backup das configurações"""
    try:
        from app import APIConfig, Channel
        import json
        import tempfile
        from flask import send_file
        
        # Coletar dados para backup
        backup_data = {
            'created_at': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'apis': [api.to_dict() for api in APIConfig.query.all()],
            'channels': [channel.to_dict() for channel in Channel.query.all()]
        }
        
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            delete=False, 
            suffix='.json'
        )
        
        json.dump(backup_data, temp_file, indent=2, ensure_ascii=False)
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/backup/restore', methods=['POST'])
def restore_backup():
    """Restaurar backup das configurações"""
    try:
        from app import APIConfig, Channel, db
        import json
        
        if 'backup_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Arquivo de backup é obrigatório'
            }), 400
        
        backup_file = request.files['backup_file']
        
        try:
            backup_data = json.load(backup_file)
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'error': 'Arquivo de backup inválido'
            }), 400
        
        restored_count = 0
        
        # Restaurar configurações de APIs
        if 'apis' in backup_data:
            for api_data in backup_data['apis']:
                api_config = APIConfig.query.filter_by(
                    api_name=api_data['api_name']
                ).first()
                
                if not api_config:
                    api_config = APIConfig(api_name=api_data['api_name'])
                    db.session.add(api_config)
                
                if api_data.get('is_configured'):
                    api_config.is_configured = True
                    restored_count += 1
        
        # Restaurar canais
        if 'channels' in backup_data:
            for channel_data in backup_data['channels']:
                existing_channel = Channel.query.filter_by(
                    channel_id=channel_data['channel_id']
                ).first()
                
                if not existing_channel:
                    channel = Channel(
                        name=channel_data['name'],
                        channel_id=channel_data['channel_id'],
                        url=channel_data['url'],
                        video_style=channel_data.get('video_style', 'motivational'),
                        is_active=channel_data.get('is_active', True)
                    )
                    db.session.add(channel)
                    restored_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'restored_count': restored_count
            },
            'message': f'Backup restaurado com sucesso. {restored_count} itens restaurados.'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def test_api_connection(api_name, api_key):
    """Testar conexão com API"""
    try:
        if api_name == 'openai':
            import openai
            client = openai.OpenAI(api_key=api_key)
            response = client.models.list()
            return {
                'success': True,
                'message': 'Conexão com OpenAI estabelecida com sucesso'
            }
        
        elif api_name == 'gemini':
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            models = genai.list_models()
            return {
                'success': True,
                'message': 'Conexão com Gemini estabelecida com sucesso'
            }
        
        elif api_name == 'rapidapi':
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
            }
            response = requests.get(
                "https://youtube-v2.p.rapidapi.com/channel/id",
                headers=headers,
                params={"channel_name": "test"},
                timeout=10
            )
            return {
                'success': response.status_code in [200, 400],  # 400 é esperado para teste
                'message': 'Conexão com RapidAPI estabelecida com sucesso'
            }
        
        else:
            return {
                'success': False,
                'message': f'Teste não implementado para API {api_name}'
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Erro ao testar API {api_name}: {str(e)}'
        }

# ================================
# 🔑 GERENCIAMENTO DE CHAVES DE API
# ================================

logger = logging.getLogger(__name__)

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')
API_KEYS_FILE = os.path.join(CONFIG_DIR, 'api_keys.json')

# Criar diretório se não existir
os.makedirs(CONFIG_DIR, exist_ok=True)

@settings_bp.route('/save-apis', methods=['POST'])
def save_api_keys():
    """Salvar chaves de API"""
    try:
        data = request.get_json()
        api_keys = data.get('api_keys', {})

        # Salvar no arquivo
        with open(API_KEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(api_keys, f, indent=2, ensure_ascii=False)

        logger.info("Chaves de API salvas")

        return jsonify({
            'success': True,
            'message': 'Chaves de API salvas com sucesso'
        })

    except Exception as e:
        logger.error(f"Erro ao salvar chaves de API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api-keys', methods=['POST'])
def save_api_keys_new():
    """Salvar chaves de API - Nova rota para compatibilidade com frontend"""
    try:
        data = request.get_json()

        print(f"🔍 DEBUG: Dados recebidos no POST: {data}")
        print(f"🔍 DEBUG: Tipo dos dados: {type(data)}")
        logger.info(f"🔍 DEBUG: Dados recebidos no POST: {data}")
        logger.info(f"🔍 DEBUG: Tipo dos dados: {type(data)}")

        if not data:
            print("❌ Nenhum dado recebido")
            logger.error("❌ Nenhum dado recebido")
            return jsonify({
                'success': False,
                'error': 'Nenhum dado recebido'
            }), 400

        # Extrair as chaves do formato complexo do frontend
        api_keys = {}

        # Mapear os nomes das chaves do frontend para o formato esperado
        key_mapping = {
            'openai_key': 'openai',
            'google_key': 'gemini',
            'rapidapi': 'rapidapi',
            'openai': 'openai',
            'gemini_1': 'gemini_1',
            'gemini_2': 'gemini_2',
            'gemini_3': 'gemini_3',
            'gemini_4': 'gemini_4',
            'gemini_5': 'gemini_5',
            'gemini_6': 'gemini_6',
            'gemini_7': 'gemini_7',
            'gemini_8': 'gemini_8',
            'gemini_9': 'gemini_9',
            'gemini_10': 'gemini_10',
            'rapidapi_1': 'rapidapi_1',
            'rapidapi_2': 'rapidapi_2',
            'rapidapi_3': 'rapidapi_3',
            'rapidapi_4': 'rapidapi_4',
            'rapidapi_5': 'rapidapi_5',
            'rapidapi_6': 'rapidapi_6',
            'rapidapi_7': 'rapidapi_7',
            'rapidapi_8': 'rapidapi_8',
            'rapidapi_9': 'rapidapi_9',
            'rapidapi_10': 'rapidapi_10',
            'openrouter': 'openrouter',
            'elevenlabs': 'elevenlabs',
            'together': 'together'
        }

        # SIMPLIFICADO: Processar diretamente as chaves do frontend
        print(f"🔍 DEBUG: Chaves recebidas: {list(data.keys())}")

        # Processar cada chave diretamente
        for frontend_key, backend_key in key_mapping.items():
            if frontend_key in data and data[frontend_key]:
                clean_key = str(data[frontend_key]).strip()
                if clean_key and clean_key != '':
                    api_keys[backend_key] = clean_key
                    print(f"✅ DEBUG: {frontend_key} -> {backend_key}: {clean_key[:20]}...")

        print(f"🔍 DEBUG: Total de chaves processadas: {len(api_keys)}")
        print(f"🔍 DEBUG: Chaves finais: {list(api_keys.keys())}")
        logger.info(f"🔍 DEBUG: Chaves a serem salvas: {api_keys}")

        # Garantir que o diretório existe
        os.makedirs(CONFIG_DIR, exist_ok=True)
        print(f"🔍 DEBUG: Salvando em: {API_KEYS_FILE}")

        # Salvar no arquivo
        with open(API_KEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(api_keys, f, indent=2, ensure_ascii=False)

        print("✅ DEBUG: Arquivo salvo com sucesso!")
        logger.info("✅ Chaves de API salvas via nova rota")

        return jsonify({
            'success': True,
            'message': 'Chaves de API salvas com sucesso'
        })

    except Exception as e:
        logger.error(f"❌ Erro ao salvar chaves de API via nova rota: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/test-api', methods=['POST'])
def test_api_endpoint():
    """Testar conexão com API"""
    try:
        data = request.get_json()
        api_name = data.get('api_name')
        api_key = data.get('api_key')

        if not api_name or not api_key:
            return jsonify({
                'success': False,
                'message': 'Nome da API e chave são obrigatórios'
            }), 400

        logger.info(f"🧪 Testando API: {api_name}")

        if api_name == 'rapidapi':
            result = test_rapidapi_connection(api_key)
        elif api_name == 'openai':
            result = test_openai_connection(api_key)
        elif api_name == 'gemini_1':
            result = test_gemini_connection(api_key)
        elif api_name == 'elevenlabs':
            result = test_elevenlabs_connection(api_key)
        elif api_name == 'together':
            result = test_together_connection(api_key)
        else:
            return jsonify({
                'success': False,
                'message': f'API não suportada: {api_name}'
            }), 400

        return jsonify(result)

    except Exception as e:
        logger.error(f"Erro no teste de API: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

def test_rapidapi_connection(api_key):
    """Testar RapidAPI YouTube V2 com throttling inteligente"""
    import time
    from .automations import apply_rapidapi_throttle, handle_rapidapi_429, reset_rapidapi_throttle_success
    
    try:
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
        }

        # Testar com canal conhecido - usar timeout maior e retry com rate limiting mais agressivo
        max_retries = 3
        base_delay = 10  # Delay inicial maior: 10 segundos
        
        for attempt in range(max_retries):
            try:
                # Aplicar throttling inteligente
                apply_rapidapi_throttle()
                
                # Adicionar delay entre tentativas para evitar rate limiting
                if attempt > 0:
                    delay = base_delay * (3 ** (attempt - 1))  # Backoff mais agressivo (3x)
                    print(f"⏳ Aguardando {delay}s antes da tentativa {attempt + 1}...")
                    time.sleep(delay)
                    
                response = requests.get(
                    "https://youtube-v2.p.rapidapi.com/channel/details",
                    headers=headers,
                    params={"channel_id": "UCX6OQ3DkcsbYNE6H8uQQuVA"},  # MrBeast
                    timeout=30  # Aumentar timeout para 30 segundos
                )
                
                # Verificar se é erro 429 (Too Many Requests)
                if response.status_code == 429:
                    handle_rapidapi_429()
                    if attempt == max_retries - 1:
                        return {
                            'success': False,
                            'message': 'Limite de requisições excedido (429). Aguarde alguns minutos e tente novamente.'
                        }
                    print(f"⚠️ Rate limit atingido (429), tentando novamente...")
                    continue
                    
                # Se chegou aqui com status 200, sair do loop
                if response.status_code == 200:
                    reset_rapidapi_throttle_success()
                    break
                    
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:  # Última tentativa
                    raise
                print(f"🔄 Tentativa {attempt + 1} falhou (timeout), tentando novamente...")
                continue

        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'message': f'Conectado! Canal: {data.get("title", "Desconhecido")}'
            }
        elif response.status_code == 401:
            return {
                'success': False,
                'message': 'Chave de API inválida'
            }
        elif response.status_code == 403:
            return {
                'success': False,
                'message': 'Acesso negado - verifique sua assinatura RapidAPI'
            }
        else:
            return {
                'success': False,
                'message': f'Erro HTTP {response.status_code}: {response.text}'
            }

    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': 'Timeout - API demorou muito para responder'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'message': 'Erro de conexão - verifique sua internet'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Erro: {str(e)}'
        }

def test_openai_connection(api_key):
    """Testar OpenAI API"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Teste"}],
            "max_tokens": 5
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code == 200:
            return {
                'success': True,
                'message': 'Conectado com sucesso!'
            }
        elif response.status_code == 401:
            return {
                'success': False,
                'message': 'Chave de API inválida'
            }
        else:
            return {
                'success': False,
                'message': f'Erro HTTP {response.status_code}'
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'Erro: {str(e)}'
        }

def test_gemini_connection(api_key):
    """Testar Google Gemini API"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

        payload = {
            "contents": [{
                "parts": [{"text": "Teste"}]
            }]
        }

        response = requests.post(url, json=payload, timeout=15)

        if response.status_code == 200:
            return {
                'success': True,
                'message': 'Conectado com sucesso!'
            }
        elif response.status_code == 400:
            return {
                'success': False,
                'message': 'Chave de API inválida'
            }
        else:
            return {
                'success': False,
                'message': f'Erro HTTP {response.status_code}'
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'Erro: {str(e)}'
        }

def test_elevenlabs_connection(api_key):
    """Testar ElevenLabs API"""
    try:
        headers = {"xi-api-key": api_key}

        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            voices_count = len(data.get('voices', []))
            return {
                'success': True,
                'message': f'Conectado! {voices_count} vozes disponíveis'
            }
        elif response.status_code == 401:
            return {
                'success': False,
                'message': 'Chave de API inválida'
            }
        else:
            return {
                'success': False,
                'message': f'Erro HTTP {response.status_code}'
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'Erro: {str(e)}'
        }

def test_together_connection(api_key):
    """Testar Together.ai API"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            "https://api.together.xyz/models",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return {
                'success': True,
                'message': 'Conectado com sucesso!'
            }
        elif response.status_code == 401:
            return {
                'success': False,
                'message': 'Chave de API inválida'
            }
        else:
            return {
                'success': False,
                'message': f'Erro HTTP {response.status_code}'
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'Erro: {str(e)}'
        }

# ================================
# 📝 GERENCIAMENTO DE PROMPTS PERSONALIZADOS
# ================================

def get_db_connection():
    """Obter conexão com banco de dados SQLite"""
    import sqlite3
    db_path = os.path.join(CONFIG_DIR, 'prompts.db')
    conn = sqlite3.connect(db_path)

    # Criar tabela se não existir
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            prompt_text TEXT NOT NULL,
            category TEXT DEFAULT 'geral',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    conn.commit()

    return conn

@settings_bp.route('/custom-prompts', methods=['GET'])
def get_custom_prompts():
    """Obter todos os prompts personalizados salvos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, prompt_text, category, created_at, updated_at
            FROM custom_prompts
            ORDER BY category, name
        ''')

        prompts = []
        for row in cursor.fetchall():
            prompts.append({
                'id': row[0],
                'name': row[1],
                'prompt_text': row[2],
                'category': row[3],
                'created_at': row[4],
                'updated_at': row[5]
            })

        conn.close()

        return jsonify({
            'success': True,
            'prompts': prompts
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/custom-prompts', methods=['POST'])
def save_custom_prompt():
    """Salvar um novo prompt personalizado"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        prompt_text = data.get('prompt_text', '').strip()
        category = data.get('category', 'geral').strip()

        if not name or not prompt_text:
            return jsonify({
                'success': False,
                'error': 'Nome e texto do prompt são obrigatórios'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar se já existe um prompt com esse nome
        cursor.execute('SELECT id FROM custom_prompts WHERE name = ?', (name,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Já existe um prompt com o nome "{name}"'
            }), 400

        # Inserir novo prompt
        from datetime import datetime
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO custom_prompts (name, prompt_text, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, prompt_text, category, now, now))

        prompt_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Prompt "{name}" salvo com sucesso',
            'prompt_id': prompt_id
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/custom-prompts/<int:prompt_id>', methods=['PUT'])
def update_custom_prompt(prompt_id):
    """Atualizar um prompt personalizado existente"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        prompt_text = data.get('prompt_text', '').strip()
        category = data.get('category', 'geral').strip()

        if not name or not prompt_text:
            return jsonify({
                'success': False,
                'error': 'Nome e texto do prompt são obrigatórios'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar se o prompt existe
        cursor.execute('SELECT id FROM custom_prompts WHERE id = ?', (prompt_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Prompt não encontrado'
            }), 404

        # Verificar se já existe outro prompt com esse nome
        cursor.execute('SELECT id FROM custom_prompts WHERE name = ? AND id != ?', (name, prompt_id))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Já existe outro prompt com o nome "{name}"'
            }), 400

        # Atualizar prompt
        from datetime import datetime
        now = datetime.now().isoformat()
        cursor.execute('''
            UPDATE custom_prompts
            SET name = ?, prompt_text = ?, category = ?, updated_at = ?
            WHERE id = ?
        ''', (name, prompt_text, category, now, prompt_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Prompt "{name}" atualizado com sucesso'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/custom-prompts/<int:prompt_id>', methods=['DELETE'])
def delete_custom_prompt(prompt_id):
    """Deletar um prompt personalizado"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar se o prompt existe e obter o nome
        cursor.execute('SELECT name FROM custom_prompts WHERE id = ?', (prompt_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Prompt não encontrado'
            }), 404

        prompt_name = result[0]

        # Deletar prompt
        cursor.execute('DELETE FROM custom_prompts WHERE id = ?', (prompt_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Prompt "{prompt_name}" deletado com sucesso'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# 📺 GERENCIAMENTO DE CANAIS SALVOS
# ================================

def get_channels_db_connection():
    """Obter conexão com banco de dados SQLite para canais"""
    import sqlite3
    db_path = os.path.join(CONFIG_DIR, 'channels.db')
    conn = sqlite3.connect(db_path)

    # Criar tabela se não existir
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'geral',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    conn.commit()

    return conn

@settings_bp.route('/saved-channels', methods=['GET'])
def get_saved_channels():
    """Obter todos os canais salvos"""
    try:
        conn = get_channels_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, url, description, category, created_at, updated_at
            FROM saved_channels
            ORDER BY category, name
        ''')

        channels = []
        for row in cursor.fetchall():
            channels.append({
                'id': row[0],
                'name': row[1],
                'url': row[2],
                'description': row[3],
                'category': row[4],
                'created_at': row[5],
                'updated_at': row[6]
            })

        conn.close()

        return jsonify({
            'success': True,
            'channels': channels
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/saved-channels', methods=['POST'])
def save_channel():
    """Salvar um novo canal"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        url = data.get('url', '').strip()
        description = data.get('description', '').strip()
        category = data.get('category', 'geral').strip()

        if not name or not url:
            return jsonify({
                'success': False,
                'error': 'Nome e URL do canal são obrigatórios'
            }), 400

        # Validar URL do YouTube
        if 'youtube.com' not in url and 'youtu.be' not in url:
            return jsonify({
                'success': False,
                'error': 'URL deve ser de um canal do YouTube'
            }), 400

        conn = get_channels_db_connection()
        cursor = conn.cursor()

        # Verificar se já existe um canal com esse nome
        cursor.execute('SELECT id FROM saved_channels WHERE name = ?', (name,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Já existe um canal com o nome "{name}"'
            }), 400

        # Inserir novo canal
        from datetime import datetime
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO saved_channels (name, url, description, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, url, description, category, now, now))

        channel_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Canal "{name}" salvo com sucesso',
            'channel_id': channel_id
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/saved-channels/<int:channel_id>', methods=['DELETE'])
def delete_saved_channel(channel_id):
    """Deletar um canal salvo"""
    try:
        conn = get_channels_db_connection()
        cursor = conn.cursor()

        # Verificar se o canal existe e obter o nome
        cursor.execute('SELECT name FROM saved_channels WHERE id = ?', (channel_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Canal não encontrado'
            }), 404

        channel_name = result[0]

        # Deletar canal
        cursor.execute('DELETE FROM saved_channels WHERE id = ?', (channel_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Canal "{channel_name}" deletado com sucesso'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
