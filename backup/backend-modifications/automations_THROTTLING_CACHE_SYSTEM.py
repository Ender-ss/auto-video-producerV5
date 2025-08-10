"""
🤖 Automations Routes
Rotas para automações de conteúdo com IA
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import requests
import json
import re
import time
import openai
import os
import base64
import wave
import io
import threading

# Importar sistema de logs em tempo real
try:
    from routes.system import add_real_time_log
except ImportError:
    # Fallback se não conseguir importar
    def add_real_time_log(message, level="info", source="automations"):
        print(f"[{level.upper()}] [{source}] {message}")

# Import AI libraries
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Sistema de rotação de chaves Gemini
GEMINI_KEYS_ROTATION = {
    'keys': [],
    'current_index': 0,
    'usage_count': {},
    'last_reset': datetime.now().date()
}

# Sistema de rotação de chaves RapidAPI
RAPIDAPI_KEYS_ROTATION = {
    'keys': [],
    'current_index': 0,
    'failed_keys': set(),  # Chaves que falharam por quota excedida
    'last_reset': datetime.now().date()
}

# Sistema de controle de jobs TTS
TTS_JOBS = {}
TTS_JOB_COUNTER = 0

# Sistema de throttling inteligente para RapidAPI
RAPIDAPI_THROTTLE = {
    'last_request_time': 0,
    'min_delay': 2.0,  # Delay mínimo entre requisições (segundos)
    'adaptive_delay': 2.0,  # Delay adaptativo baseado em rate limiting
    'consecutive_429s': 0,  # Contador de 429s consecutivos
    'lock': threading.Lock()  # Lock para thread safety
}

# Sistema de cache simples para RapidAPI
RAPIDAPI_CACHE = {
    'data': {},  # Cache de dados
    'timestamps': {},  # Timestamps dos dados
    'ttl': 300,  # TTL padrão: 5 minutos
    'lock': threading.Lock()  # Lock para thread safety
}

# Import TitleGenerator
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from services.title_generator import TitleGenerator
    TITLE_GENERATOR_AVAILABLE = True
    print("✅ TitleGenerator importado com sucesso")
except ImportError as e:
    TITLE_GENERATOR_AVAILABLE = False
    print(f"⚠️ TitleGenerator não disponível: {e}")

    # Fallback: criar classe mock
    class TitleGenerator:
        def __init__(self):
            pass
        def configure_openai(self, key):
            return False
        def configure_gemini(self, key):
            return False
        def generate_titles_with_custom_prompt(self, *args, **kwargs):
            return {'success': False, 'error': 'TitleGenerator não disponível'}

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.genai as google_genai
    from google.genai import types
    GOOGLE_GENAI_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_TTS_AVAILABLE = False

automations_bp = Blueprint('automations', __name__)

def load_gemini_keys():
    """Carregar chaves Gemini do arquivo de configuração"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                keys = json.load(f)

            # Coletar todas as chaves Gemini
            gemini_keys = []
            for key, value in keys.items():
                if 'gemini' in key.lower() and value and len(value) > 10:
                    gemini_keys.append(value)

            # Adicionar chave padrão se não houver outras
            default_key = 'AIzaSyBqUjzLHNPycDIzvwnI5JisOwmNubkfRRc'
            if default_key not in gemini_keys:
                gemini_keys.append(default_key)

            GEMINI_KEYS_ROTATION['keys'] = gemini_keys
            print(f"🔑 Carregadas {len(gemini_keys)} chaves Gemini para rotação")
            return gemini_keys
    except Exception as e:
        print(f"❌ Erro ao carregar chaves Gemini: {e}")
        # Usar chave padrão como fallback
        GEMINI_KEYS_ROTATION['keys'] = ['AIzaSyBqUjzLHNPycDIzvwnI5JisOwmNubkfRRc']

    return GEMINI_KEYS_ROTATION['keys']

def load_rapidapi_keys():
    """Carregar chaves RapidAPI do arquivo de configuração"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                keys = json.load(f)

            # Carregar array de chaves RapidAPI
            rapidapi_keys = keys.get('rapidapi_keys', [])
            
            # Adicionar chaves individuais de rotação
            for i in range(1, 11):  # rapidapi_1 até rapidapi_10
                key_name = f'rapidapi_{i}'
                if keys.get(key_name):
                    rapidapi_keys.append(keys.get(key_name))
            
            # Se não houver array, usar a chave única como fallback
            if not rapidapi_keys and keys.get('rapidapi'):
                rapidapi_keys = [keys.get('rapidapi')]

            # Filtrar chaves válidas e remover duplicatas
            valid_keys = list(set([key for key in rapidapi_keys if key and len(key) > 10]))
            
            RAPIDAPI_KEYS_ROTATION['keys'] = valid_keys
            RAPIDAPI_KEYS_ROTATION['failed_keys'] = set()  # Reset das chaves falhadas
            print(f"🔑 Carregadas {len(valid_keys)} chaves RapidAPI para rotação")
            return valid_keys
    except Exception as e:
        print(f"❌ Erro ao carregar chaves RapidAPI: {e}")
        RAPIDAPI_KEYS_ROTATION['keys'] = []

    return RAPIDAPI_KEYS_ROTATION['keys']

def get_next_gemini_key():
    """Obter próxima chave Gemini na rotação"""
    # Carregar chaves se não estiverem carregadas
    if not GEMINI_KEYS_ROTATION['keys']:
        load_gemini_keys()

    # Reset diário do contador
    today = datetime.now().date()
    if GEMINI_KEYS_ROTATION['last_reset'] != today:
        GEMINI_KEYS_ROTATION['usage_count'] = {}
        GEMINI_KEYS_ROTATION['last_reset'] = today
        GEMINI_KEYS_ROTATION['current_index'] = 0
        print("🔄 Reset diário do contador de uso das chaves Gemini")
        add_real_time_log("🔄 Reset diário do contador de uso das chaves Gemini", "info", "gemini-rotation")

    keys = GEMINI_KEYS_ROTATION['keys']
    if not keys:
        return None

    # Encontrar chave com menor uso
    min_usage = float('inf')
    best_key_index = 0

    for i, key in enumerate(keys):
        usage = GEMINI_KEYS_ROTATION['usage_count'].get(key, 0)
        if usage < min_usage:
            min_usage = usage
            best_key_index = i

    # Se todas as chaves atingiram o limite (15 por dia), usar rotação simples
    if min_usage >= 15:
        print("⚠️ Todas as chaves atingiram o limite diário, usando rotação simples")
        add_real_time_log("⚠️ Todas as chaves atingiram o limite diário, usando rotação simples", "warning", "gemini-rotation")
        best_key_index = GEMINI_KEYS_ROTATION['current_index']
        GEMINI_KEYS_ROTATION['current_index'] = (GEMINI_KEYS_ROTATION['current_index'] + 1) % len(keys)

    selected_key = keys[best_key_index]

    # Incrementar contador de uso
    GEMINI_KEYS_ROTATION['usage_count'][selected_key] = GEMINI_KEYS_ROTATION['usage_count'].get(selected_key, 0) + 1

    usage_count = GEMINI_KEYS_ROTATION['usage_count'][selected_key]
    print(f"🔑 Usando chave Gemini {best_key_index + 1}/{len(keys)} (uso: {usage_count}/15)")
    add_real_time_log(f"🔑 Usando chave Gemini {best_key_index + 1}/{len(keys)} (uso: {usage_count}/15)", "info", "gemini-rotation")

    return selected_key

def get_next_rapidapi_key():
    """Obter próxima chave RapidAPI na rotação, evitando chaves que falharam por quota"""
    if not RAPIDAPI_KEYS_ROTATION['keys']:
        load_rapidapi_keys()
    
    if not RAPIDAPI_KEYS_ROTATION['keys']:
        return None
    
    # Reset diário das chaves falhadas
    today = datetime.now().date()
    if RAPIDAPI_KEYS_ROTATION['last_reset'] != today:
        RAPIDAPI_KEYS_ROTATION['failed_keys'] = set()
        RAPIDAPI_KEYS_ROTATION['last_reset'] = today
        print("🔄 Reset diário: chaves RapidAPI falhadas foram limpas")
        add_real_time_log("🔄 Reset diário: chaves RapidAPI falhadas foram limpas", "info", "rapidapi-rotation")
    
    # Filtrar chaves disponíveis (não falhadas)
    available_keys = [key for key in RAPIDAPI_KEYS_ROTATION['keys'] if key not in RAPIDAPI_KEYS_ROTATION['failed_keys']]
    
    if not available_keys:
        print("⚠️ Todas as chaves RapidAPI excederam a quota. Aguarde reset diário.")
        add_real_time_log("⚠️ Todas as chaves RapidAPI excederam a quota. Aguarde reset diário.", "warning", "rapidapi-rotation")
        return None
    
    # Usar índice circular apenas nas chaves disponíveis
    if RAPIDAPI_KEYS_ROTATION['current_index'] >= len(available_keys):
        RAPIDAPI_KEYS_ROTATION['current_index'] = 0
    
    current_key = available_keys[RAPIDAPI_KEYS_ROTATION['current_index']]
    
    # Avançar para próxima chave disponível
    RAPIDAPI_KEYS_ROTATION['current_index'] = (RAPIDAPI_KEYS_ROTATION['current_index'] + 1) % len(available_keys)
    
    print(f"🔑 Usando chave RapidAPI ({len(available_keys)} disponíveis): {current_key[:20]}...")
    add_real_time_log(f"🔑 Usando chave RapidAPI ({len(available_keys)} disponíveis): {current_key[:20]}...", "info", "rapidapi-rotation")
    
    return current_key

def mark_rapidapi_key_failed(api_key):
    """Marcar uma chave RapidAPI como falhada por quota excedida"""
    if api_key:
        RAPIDAPI_KEYS_ROTATION['failed_keys'].add(api_key)
        print(f"❌ Chave RapidAPI marcada como falhada: {api_key[:20]}...")
        add_real_time_log(f"❌ Chave RapidAPI marcada como falhada: {api_key[:20]}...", "error", "rapidapi-rotation")
        print(f"📊 Chaves falhadas: {len(RAPIDAPI_KEYS_ROTATION['failed_keys'])}/{len(RAPIDAPI_KEYS_ROTATION['keys'])}")
        add_real_time_log(f"📊 Chaves falhadas: {len(RAPIDAPI_KEYS_ROTATION['failed_keys'])}/{len(RAPIDAPI_KEYS_ROTATION['keys'])}", "info", "rapidapi-rotation")
        
        # Se todas as chaves falharam, informar
        if len(RAPIDAPI_KEYS_ROTATION['failed_keys']) >= len(RAPIDAPI_KEYS_ROTATION['keys']):
            print("⚠️ ATENÇÃO: Todas as chaves RapidAPI excederam a quota mensal!")

def apply_rapidapi_throttle():
    """Aplicar throttling inteligente para evitar rate limiting da RapidAPI"""
    with RAPIDAPI_THROTTLE['lock']:
        current_time = time.time()
        time_since_last = current_time - RAPIDAPI_THROTTLE['last_request_time']
        
        # Calcular delay necessário
        required_delay = RAPIDAPI_THROTTLE['adaptive_delay']
        
        if time_since_last < required_delay:
            sleep_time = required_delay - time_since_last
            print(f"⏱️ Throttling RapidAPI: aguardando {sleep_time:.2f}s (delay adaptativo: {RAPIDAPI_THROTTLE['adaptive_delay']:.2f}s)")
            add_real_time_log(f"⏱️ Throttling RapidAPI: aguardando {sleep_time:.2f}s", "info", "rapidapi-throttle")
            time.sleep(sleep_time)
        
        RAPIDAPI_THROTTLE['last_request_time'] = time.time()

def handle_rapidapi_429():
    """Lidar com erro 429 (rate limiting) da RapidAPI"""
    with RAPIDAPI_THROTTLE['lock']:
        RAPIDAPI_THROTTLE['consecutive_429s'] += 1
        
        # Aumentar delay adaptativo baseado no número de 429s consecutivos
        if RAPIDAPI_THROTTLE['consecutive_429s'] == 1:
            RAPIDAPI_THROTTLE['adaptive_delay'] = 5.0
        elif RAPIDAPI_THROTTLE['consecutive_429s'] == 2:
            RAPIDAPI_THROTTLE['adaptive_delay'] = 10.0
        elif RAPIDAPI_THROTTLE['consecutive_429s'] >= 3:
            RAPIDAPI_THROTTLE['adaptive_delay'] = 20.0
        
        print(f"🚫 Rate limit detectado! Aumentando delay para {RAPIDAPI_THROTTLE['adaptive_delay']}s (429s consecutivos: {RAPIDAPI_THROTTLE['consecutive_429s']})")
        add_real_time_log(f"🚫 Rate limit detectado! Delay aumentado para {RAPIDAPI_THROTTLE['adaptive_delay']}s", "warning", "rapidapi-throttle")

def reset_rapidapi_throttle_success():
    """Resetar throttling após requisição bem-sucedida"""
    with RAPIDAPI_THROTTLE['lock']:
        if RAPIDAPI_THROTTLE['consecutive_429s'] > 0:
            print(f"✅ Requisição RapidAPI bem-sucedida! Resetando throttling (era {RAPIDAPI_THROTTLE['adaptive_delay']}s)")
            add_real_time_log("✅ Requisição RapidAPI bem-sucedida! Throttling resetado", "info", "rapidapi-throttle")
        
        RAPIDAPI_THROTTLE['consecutive_429s'] = 0
        RAPIDAPI_THROTTLE['adaptive_delay'] = RAPIDAPI_THROTTLE['min_delay']

def get_cache_key(endpoint, params):
    """Gerar chave de cache baseada no endpoint e parâmetros"""
    import hashlib
    # Criar string única baseada no endpoint e parâmetros
    cache_string = f"{endpoint}_{str(sorted(params.items()))}"
    return hashlib.md5(cache_string.encode()).hexdigest()

def get_from_cache(endpoint, params, custom_ttl=None):
    """Obter dados do cache se ainda válidos"""
    with RAPIDAPI_CACHE['lock']:
        cache_key = get_cache_key(endpoint, params)
        
        if cache_key in RAPIDAPI_CACHE['data']:
            timestamp = RAPIDAPI_CACHE['timestamps'].get(cache_key, 0)
            ttl = custom_ttl or RAPIDAPI_CACHE['ttl']
            
            if time.time() - timestamp < ttl:
                print(f"📦 Cache hit para {endpoint} (TTL: {ttl}s)")
                add_real_time_log(f"📦 Cache hit para {endpoint}", "info", "rapidapi-cache")
                return RAPIDAPI_CACHE['data'][cache_key]
            else:
                # Cache expirado, remover
                del RAPIDAPI_CACHE['data'][cache_key]
                del RAPIDAPI_CACHE['timestamps'][cache_key]
                print(f"⏰ Cache expirado para {endpoint}")
        
        return None

def save_to_cache(endpoint, params, data, custom_ttl=None):
    """Salvar dados no cache"""
    with RAPIDAPI_CACHE['lock']:
        cache_key = get_cache_key(endpoint, params)
        RAPIDAPI_CACHE['data'][cache_key] = data
        RAPIDAPI_CACHE['timestamps'][cache_key] = time.time()
        
        ttl = custom_ttl or RAPIDAPI_CACHE['ttl']
        print(f"💾 Dados salvos no cache para {endpoint} (TTL: {ttl}s)")
        add_real_time_log(f"💾 Dados salvos no cache para {endpoint}", "info", "rapidapi-cache")

def clear_expired_cache():
    """Limpar cache expirado"""
    with RAPIDAPI_CACHE['lock']:
        current_time = time.time()
        expired_keys = []
        
        for cache_key, timestamp in RAPIDAPI_CACHE['timestamps'].items():
            if current_time - timestamp >= RAPIDAPI_CACHE['ttl']:
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            del RAPIDAPI_CACHE['data'][key]
            del RAPIDAPI_CACHE['timestamps'][key]
        
        if expired_keys:
            print(f"🧹 Removidas {len(expired_keys)} entradas expiradas do cache")
            add_real_time_log(f"🧹 Cache limpo: {len(expired_keys)} entradas removidas", "info", "rapidapi-cache")
            add_real_time_log("⚠️ ATENÇÃO: Todas as chaves RapidAPI excederam a quota mensal!", "error", "rapidapi-rotation")
            return False
    return True

# ================================
# 🧪 CACHE PARA RAPIDAPI
# ================================

# Cache simples para evitar chamadas desnecessárias
RAPIDAPI_CACHE = {}
CACHE_DURATION = 300  # 5 minutos em segundos

def get_cache_key(endpoint, params):
    """Gerar chave única para cache"""
    import hashlib
    key_string = f"{endpoint}_{str(sorted(params.items()))}"
    return hashlib.md5(key_string.encode()).hexdigest()

def is_cache_valid(cache_entry):
    """Verificar se entrada do cache ainda é válida"""
    import time
    return time.time() - cache_entry['timestamp'] < CACHE_DURATION

def get_from_cache(endpoint, params):
    """Obter dados do cache se disponível e válido"""
    cache_key = get_cache_key(endpoint, params)
    if cache_key in RAPIDAPI_CACHE:
        cache_entry = RAPIDAPI_CACHE[cache_key]
        if is_cache_valid(cache_entry):
            print(f"📋 Cache hit para {endpoint} - evitando chamada à API")
            return cache_entry['data']
        else:
            # Cache expirado, remover
            del RAPIDAPI_CACHE[cache_key]
    return None

def save_to_cache(endpoint, params, data):
    """Salvar dados no cache"""
    import time
    cache_key = get_cache_key(endpoint, params)
    RAPIDAPI_CACHE[cache_key] = {
        'data': data,
        'timestamp': time.time()
    }
    print(f"💾 Dados salvos no cache para {endpoint}")

# ================================
# 🧪 TESTE RAPIDAPI
# ================================

@automations_bp.route('/test-rapidapi', methods=['POST'])
def test_rapidapi():
    """Testar conexão com RapidAPI YouTube V2"""
    import time
    
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Chave da API RapidAPI é obrigatória'
            }), 400

        # Testar com um canal conhecido
        test_channel = "UCX6OQ3DkcsbYNE6H8uQQuVA"  # MrBeast

        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
        }

        # Testar endpoint de detalhes do canal com rate limiting mais agressivo
        max_retries = 3
        base_delay = 10  # Delay inicial maior: 10 segundos
        
        for attempt in range(max_retries):
            if attempt > 0:
                delay = base_delay * (3 ** (attempt - 1))  # Backoff mais agressivo (3x)
                print(f"⏳ Aguardando {delay}s antes da tentativa {attempt + 1}...")
                time.sleep(delay)
            else:
                # Delay inicial mesmo na primeira tentativa
                print(f"⏳ Aguardando {base_delay}s para evitar rate limiting...")
                time.sleep(base_delay)
                
            response = requests.get(
                "https://youtube-v2.p.rapidapi.com/channel/details",
                headers=headers,
                params={"channel_id": test_channel},
                timeout=30
            )
            
            if response.status_code == 429:
                if attempt == max_retries - 1:
                    return jsonify({
                        'success': False,
                        'error': 'Limite de requisições excedido (429). Aguarde alguns minutos e tente novamente.'
                    })
                print(f"⚠️ Rate limit atingido (429), tentando novamente...")
                continue
            elif response.status_code == 200:
                # Resetar throttling após sucesso
                reset_rapidapi_throttle_success()
                break

        return jsonify({
            'success': True,
            'data': {
                'status_code': response.status_code,
                'response': response.json() if response.status_code == 200 else response.text,
                'test_channel': test_channel
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# 📺 EXTRAÇÃO YOUTUBE
# ================================

@automations_bp.route('/extract-youtube', methods=['POST'])
def extract_youtube_channel_content():
    """Extrair conteúdo de canal do YouTube usando RapidAPI"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        api_key = data.get('api_key', '').strip()
        config = data.get('config', {})

        print(f"🔍 DEBUG: Recebida requisição - URL: {url}, Config: {config}")

        if not url:
            return jsonify({
                'success': False,
                'error': 'URL ou ID do canal é obrigatório'
            }), 400

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Chave da API RapidAPI é obrigatória'
            }), 400
        
        # Determinar se é ID do canal ou URL/nome
        channel_id = None
        channel_name = None

        if url.startswith('UC') and len(url) == 24:
            channel_id = url
            print(f"🔍 DEBUG: Usando ID do canal diretamente: {channel_id}")
        else:
            # Tentar extrair ID do canal da URL
            channel_id = extract_channel_id_from_url(url)

            if channel_id:
                print(f"🔍 DEBUG: ID do canal extraído da URL: {channel_id}")
            else:
                # Extrair nome do canal para busca
                channel_name = extract_channel_name_or_id(url)
                print(f"🔍 DEBUG: Nome extraído do canal: {channel_name}")

                if not channel_name:
                    return jsonify({
                        'success': False,
                        'error': 'Formato inválido. Use: Nome do canal, @handle, URL completa ou ID do canal'
                    }), 400

                # Obter ID do canal usando a API
                print(f"🔍 DEBUG: Buscando ID do canal para: {channel_name}")
                channel_id_result = get_channel_id_rapidapi(channel_name, api_key)
                print(f"🔍 DEBUG: Resultado da busca do ID: {channel_id_result}")

                if not channel_id_result['success']:
                    return jsonify(channel_id_result), 400

                channel_id = channel_id_result['data']['channel_id']
                print(f"🔍 DEBUG: ID do canal obtido: {channel_id}")

        # Obter vídeos do canal
        print(f"🔍 DEBUG: Buscando vídeos do canal: {channel_id}")
        videos_result = get_channel_videos_rapidapi(channel_id, api_key)
        print(f"🔍 DEBUG: Resultado da busca de vídeos: {videos_result.get('success', False)}, Total: {len(videos_result.get('data', {}).get('videos', []))}")
        if not videos_result['success']:
            return jsonify(videos_result), 400
        
        # Obter detalhes do canal
        channel_details = get_channel_details_rapidapi(channel_id, api_key)
        
        # Filtrar vídeos baseado na configuração
        original_videos = videos_result['data']['videos']
        print(f"🔍 DEBUG: Vídeos antes do filtro: {len(original_videos)}")
        print(f"🔍 DEBUG: Configuração de filtros: {config}")

        filtered_videos = filter_videos_by_config(original_videos, config)
        print(f"🔍 DEBUG: Vídeos após filtro: {len(filtered_videos)}")

        return jsonify({
            'success': True,
            'data': {
                'channel_id': channel_id,
                'channel_name': channel_details['data']['title'] if channel_details['success'] else (channel_name or channel_id),
                'channel_description': channel_details['data']['description'] if channel_details['success'] else '',
                'videos': filtered_videos,
                'total_videos': len(filtered_videos),
                'total_views': sum(int(video.get('views', 0)) for video in filtered_videos),
                'total_likes': sum(int(video.get('like_count', 0)) for video in filtered_videos)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# ================================
# 🎯 GERAÇÃO DE TÍTULOS
# ================================

@automations_bp.route('/generate-titles', methods=['POST'])
def generate_titles_with_ai():
    """Gerar títulos usando diferentes agentes de IA"""
    try:
        data = request.get_json()
        agent = data.get('agent', 'gemini').lower()
        api_key = data.get('api_key', '').strip()
        instructions = data.get('instructions', '').strip()
        source_titles = data.get('source_titles', [])
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': f'Chave da API {agent.upper()} é obrigatória'
            }), 400
        
        if not source_titles:
            return jsonify({
                'success': False,
                'error': 'Títulos de origem são obrigatórios'
            }), 400
        
        if not instructions:
            instructions = 'Crie títulos virais e chamativos baseados nos títulos fornecidos.'
        
        # Gerar títulos baseado no agente selecionado
        if agent == 'chatgpt' or agent == 'openai':
            result = generate_titles_with_openai(source_titles, instructions, api_key)
        elif agent == 'claude':
            result = generate_titles_with_claude(source_titles, instructions, api_key)
        elif agent == 'gemini':
            result = generate_titles_with_gemini(source_titles, instructions, api_key)
        elif agent == 'openrouter':
            result = generate_titles_with_openrouter(source_titles, instructions, api_key)
        else:
            return jsonify({
                'success': False,
                'error': f'Agente {agent} não suportado'
            }), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# ================================
# 📝 GERAÇÃO DE ROTEIROS
# ================================

@automations_bp.route('/generate-script', methods=['POST'])
def generate_script_chapters():
    """Gerar roteiro completo com múltiplos capítulos"""
    try:
        data = request.get_json()
        agent = data.get('agent', 'openai').lower()
        api_key = data.get('api_key', '').strip()
        title = data.get('title', '').strip()
        context = data.get('context', '').strip()
        num_chapters = data.get('num_chapters', 10)
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': f'Chave da API {agent.upper()} é obrigatória'
            }), 400
        
        if not title:
            return jsonify({
                'success': False,
                'error': 'Título é obrigatório'
            }), 400
        
        # Gerar roteiro baseado no agente selecionado
        if agent == 'chatgpt' or agent == 'openai':
            result = generate_script_chapters_with_openai(title, context, num_chapters, api_key)
        elif agent == 'claude':
            result = generate_script_chapters_with_claude(title, context, num_chapters, api_key)
        elif agent == 'gemini':
            result = generate_script_chapters_with_gemini(title, context, num_chapters, api_key)
        elif agent == 'openrouter':
            result = generate_script_chapters_with_openrouter(title, context, num_chapters, api_key)
        else:
            return jsonify({
                'success': False,
                'error': f'Agente {agent} não suportado'
            }), 400
        
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# ================================
# 🎭 GERAÇÃO DE PREMISSAS
# ================================

@automations_bp.route('/generate-premise', methods=['POST'])
def generate_premise_with_ai():
    """Gerar premissa narrativa usando diferentes agentes de IA"""
    try:
        data = request.get_json()
        agent = data.get('agent', 'gemini').lower()
        api_key = data.get('api_key', '').strip()
        title = data.get('title', '').strip()
        resume = data.get('resume', '').strip()
        agent_prompt = data.get('agent_prompt', '').strip()

        if not api_key:
            return jsonify({
                'success': False,
                'error': f'Chave da API {agent.upper()} é obrigatória'
            }), 400

        if not title:
            return jsonify({
                'success': False,
                'error': 'Título é obrigatório'
            }), 400

        # Usar prompt padrão se não fornecido
        if not agent_prompt:
            agent_prompt = get_default_premise_prompt()

        # Gerar premissa baseado no agente selecionado
        if agent == 'chatgpt' or agent == 'openai':
            result = generate_premise_with_openai(title, resume, agent_prompt, api_key)
        elif agent == 'claude':
            result = generate_premise_with_claude(title, resume, agent_prompt, api_key)
        elif agent == 'gemini':
            result = generate_premise_with_gemini(title, resume, agent_prompt, api_key)
        elif agent == 'openrouter':
            result = generate_premise_with_openrouter(title, resume, agent_prompt, api_key)
        else:
            return jsonify({
                'success': False,
                'error': f'Agente {agent} não suportado'
            }), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# ================================
# 🎤 TEXT-TO-SPEECH
# ================================

@automations_bp.route('/generate-tts', methods=['POST'])
def generate_tts_gemini():
    """Gerar áudio TTS usando Gemini 2.5"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        api_key = data.get('api_key', '').strip()
        voice_name = data.get('voice_name', 'Kore')
        model = data.get('model', 'gemini-2.5-flash-preview-tts')

        if not text:
            return jsonify({
                'success': False,
                'error': 'Texto é obrigatório'
            }), 400

        if not GOOGLE_GENAI_TTS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Biblioteca google-genai não instalada'
            }), 400

        # Parâmetros adicionais para Gemini TTS
        speed = data.get('speed', 1.0)
        pitch = data.get('pitch', 0.0)
        volume_gain_db = data.get('volume_gain_db', 0.0)

        # Criar job ID para controle
        global TTS_JOB_COUNTER
        TTS_JOB_COUNTER += 1
        job_id = f"tts_{TTS_JOB_COUNTER}"

        # Registrar job
        TTS_JOBS[job_id] = {
            'status': 'running',
            'text': text[:50] + '...' if len(text) > 50 else text,
            'start_time': time.time(),
            'cancelled': False
        }

        add_real_time_log(f"🎵 Iniciando TTS Job {job_id} - {len(text)} chars", "info", "tts-gemini")

        # Tentar múltiplas chaves se necessário
        max_key_attempts = 3  # Tentar até 3 chaves diferentes
        last_error = None

        for attempt in range(max_key_attempts):
            # Verificar se job foi cancelado
            if TTS_JOBS.get(job_id, {}).get('cancelled', False):
                add_real_time_log(f"🛑 TTS Job {job_id} cancelado pelo usuário", "warning", "tts-gemini")
                TTS_JOBS[job_id]['status'] = 'cancelled'
                return jsonify({
                    'success': False,
                    'error': 'Geração cancelada pelo usuário',
                    'job_id': job_id
                })

            # Se não foi fornecida chave ou tentativa anterior falhou, usar rotação
            if not api_key or attempt > 0:
                api_key = get_next_gemini_key()
                if not api_key:
                    TTS_JOBS[job_id]['status'] = 'failed'
                    return jsonify({
                        'success': False,
                        'error': 'Nenhuma chave Gemini disponível. Configure pelo menos uma chave nas Configurações.',
                        'job_id': job_id
                    }), 400
                print(f"🔄 Tentativa {attempt + 1}: Usando rotação de chaves Gemini")
                add_real_time_log(f"🔄 Tentativa {attempt + 1}: Usando rotação de chaves Gemini", "info", "tts-gemini")

            # Gerar áudio TTS usando Gemini
            result = generate_tts_with_gemini(
                text, api_key, voice_name, model,
                speed=speed, pitch=pitch, volume_gain_db=volume_gain_db,
                job_id=job_id
            )

            # Verificar se foi bem-sucedido
            if result.get('success', False):
                TTS_JOBS[job_id]['status'] = 'completed'
                add_real_time_log(f"✅ TTS Gemini gerado com sucesso - {len(text)} chars", "success", "tts-gemini")
                result['job_id'] = job_id
                return jsonify(result)

            # Se falhou, verificar o erro
            last_error = result.get('error', 'Erro desconhecido')
            print(f"❌ Tentativa {attempt + 1} falhou: {last_error}")
            add_real_time_log(f"❌ Tentativa {attempt + 1} falhou: {last_error}", "error", "tts-gemini")

            # Se é erro 429 (quota exceeded), tentar próxima chave
            if "429" in last_error or "quota" in last_error.lower() or "exceeded" in last_error.lower():
                print(f"🔄 Erro de cota detectado, tentando próxima chave...")
                add_real_time_log(f"🔄 Erro de cota detectado, tentando próxima chave...", "warning", "tts-gemini")
                api_key = None  # Forçar nova chave na próxima tentativa
                continue
            else:
                # Outros erros, não tentar novamente
                print(f"🛑 Erro não relacionado à cota, parando tentativas")
                break

        # Se chegou aqui, todas as tentativas falharam
        TTS_JOBS[job_id]['status'] = 'failed'
        final_error = f'Todas as {max_key_attempts} chaves Gemini falharam. Último erro: {last_error}'
        add_real_time_log(f"❌ {final_error}", "error", "tts-gemini")
        return jsonify({
            'success': False,
            'error': final_error,
            'job_id': job_id
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@automations_bp.route('/generate-tts-kokoro', methods=['POST'])
def generate_tts_kokoro():
    """Gerar áudio TTS usando Kokoro FastAPI"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        voice_name = data.get('voice', 'af_bella')
        kokoro_url = data.get('kokoro_url', 'http://localhost:8880')
        speed = data.get('speed', 1.0)
        language = data.get('language', 'en')

        if not text:
            return jsonify({
                'success': False,
                'error': 'Texto é obrigatório'
            }), 400

        # Criar job ID para controle
        global TTS_JOB_COUNTER
        TTS_JOB_COUNTER += 1
        job_id = f"kokoro_{TTS_JOB_COUNTER}"

        # Registrar job
        TTS_JOBS[job_id] = {
            'status': 'running',
            'text': text[:50] + '...' if len(text) > 50 else text,
            'start_time': time.time(),
            'cancelled': False
        }

        add_real_time_log(f"🎵 Iniciando Kokoro TTS Job {job_id} - {len(text)} chars", "info", "tts-kokoro")

        try:
            # Gerar áudio TTS usando Kokoro
            result = generate_tts_with_kokoro(
                text, kokoro_url=kokoro_url, voice_name=voice_name,
                speed=speed, language=language, job_id=job_id
            )

            # Verificar se foi bem-sucedido
            if result.get('success', False):
                TTS_JOBS[job_id]['status'] = 'completed'
                add_real_time_log(f"✅ Kokoro TTS gerado com sucesso - {len(text)} chars", "success", "tts-kokoro")
                result['job_id'] = job_id
                return jsonify(result)
            else:
                TTS_JOBS[job_id]['status'] = 'failed'
                return jsonify(result)

        except Exception as e:
            TTS_JOBS[job_id]['status'] = 'failed'
            error_msg = f'Erro ao gerar áudio com Kokoro: {str(e)}'
            add_real_time_log(f"❌ {error_msg}", "error", "tts-kokoro")
            return jsonify({
                'success': False,
                'error': error_msg,
                'job_id': job_id
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@automations_bp.route('/test-kokoro', methods=['POST'])
def test_kokoro():
    """Testar conexão com API Kokoro"""
    try:
        data = request.get_json()
        kokoro_url = data.get('kokoro_url', 'http://localhost:8880')

        # Testar endpoint de vozes
        voices_url = f"{kokoro_url}/v1/audio/voices"

        print(f"🔍 Testando conexão Kokoro: {voices_url}")
        add_real_time_log(f"🔍 Testando conexão Kokoro: {kokoro_url}", "info", "kokoro-test")

        response = requests.get(voices_url, timeout=10)

        if response.status_code == 200:
            voices_data = response.json()
            voices = voices_data.get('voices', [])

            add_real_time_log(f"✅ Kokoro conectado com sucesso - {len(voices)} vozes disponíveis", "success", "kokoro-test")

            return jsonify({
                'success': True,
                'message': f'Conexão com Kokoro estabelecida com sucesso',
                'url': kokoro_url,
                'voices_count': len(voices),
                'voices': voices[:10]  # Mostrar apenas as primeiras 10 vozes
            })
        else:
            error_msg = f"Erro ao conectar com Kokoro: {response.status_code} - {response.text}"
            add_real_time_log(f"❌ {error_msg}", "error", "kokoro-test")
            return jsonify({
                'success': False,
                'error': error_msg
            })

    except requests.exceptions.ConnectionError:
        error_msg = f"Não foi possível conectar com Kokoro em {kokoro_url}. Verifique se o servidor está rodando."
        add_real_time_log(f"❌ {error_msg}", "error", "kokoro-test")
        return jsonify({
            'success': False,
            'error': error_msg
        })
    except Exception as e:
        error_msg = f"Erro ao testar Kokoro: {str(e)}"
        add_real_time_log(f"❌ {error_msg}", "error", "kokoro-test")
        return jsonify({
            'success': False,
            'error': error_msg
        })

@automations_bp.route('/generate-tts-elevenlabs', methods=['POST'])
def generate_tts_elevenlabs():
    """Gerar áudio TTS usando ElevenLabs"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        api_key = data.get('api_key', '').strip()
        voice_id = data.get('voice_id', 'default')
        model_id = data.get('model_id', 'eleven_monolingual_v1')

        if not text:
            return jsonify({
                'success': False,
                'error': 'Texto é obrigatório'
            }), 400

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Chave da API ElevenLabs é obrigatória'
            }), 400

        # Parâmetros adicionais para ElevenLabs
        stability = data.get('stability', 0.5)
        similarity_boost = data.get('similarity_boost', 0.5)
        style = data.get('style', 0.0)
        use_speaker_boost = data.get('use_speaker_boost', True)

        # Gerar áudio TTS usando ElevenLabs
        result = generate_tts_with_elevenlabs(
            text, api_key, voice_id, model_id,
            stability=stability, similarity_boost=similarity_boost,
            style=style, use_speaker_boost=use_speaker_boost
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# Função removida - duplicada mais abaixo

@automations_bp.route('/download/<filename>')
def download_audio(filename):
    """Download de arquivos de áudio gerados"""
    try:
        import os
        from flask import send_file

        temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
        filepath = os.path.join(temp_dir, filename)

        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Arquivo não encontrado'
            }), 404

        return send_file(filepath, as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro no download: {str(e)}'
        }), 500

@automations_bp.route('/join-audio', methods=['POST'])
def join_audio_segments():
    """Juntar múltiplos segmentos de áudio em um arquivo único"""
    try:
        data = request.get_json()
        segments = data.get('segments', [])

        if not segments:
            return jsonify({
                'success': False,
                'error': 'Nenhum segmento fornecido'
            }), 400

        # Juntar áudios usando a função auxiliar
        result = join_audio_files(segments)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# ================================
# 📊 LOGS DE AUTOMAÇÕES
# ================================

@automations_bp.route('/logs', methods=['GET'])
def get_automation_logs():
    """Obter logs de automações"""
    try:
        from app import AutomationLog
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        automation_type = request.args.get('type', None)
        
        query = AutomationLog.query
        
        if automation_type:
            query = query.filter_by(automation_type=automation_type)
        
        logs = query.order_by(AutomationLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'logs': [log.to_dict() for log in logs.items],
                'total': logs.total,
                'pages': logs.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# 🛠️ FUNÇÕES AUXILIARES
# ================================

def extract_channel_id_from_url(url):
    """Extrair ID do canal da URL do YouTube"""
    import re

    # Se já for um ID de canal
    if url.startswith('UC') and len(url) == 24:
        return url

    # Padrão para URL com ID do canal
    channel_id_pattern = r'youtube\.com/channel/(UC[a-zA-Z0-9_-]{22})'
    match = re.search(channel_id_pattern, url)
    if match:
        return match.group(1)

    # Para outros formatos (@handle, /c/, /user/), não podemos extrair o ID diretamente
    # pois a API de busca não está funcionando
    return None

def extract_channel_name_or_id(input_str):
    """Extrair nome ou ID do canal de URL do YouTube"""
    input_str = input_str.strip()
    print(f"🔍 DEBUG: Processando entrada: '{input_str}'")

    if input_str.startswith('UC') and len(input_str) == 24:
        print(f"🔍 DEBUG: ID do canal detectado: {input_str}")
        return input_str

    patterns = [
        r'youtube\.com/@([^/?&\s]+)',
        r'youtube\.com/c/([^/?&\s]+)',
        r'youtube\.com/channel/([^/?&\s]+)',
        r'youtube\.com/user/([^/?&\s]+)',
        r'^@([^/?&\s]+)$',
        r'^([^/?&\s@]+)$'
    ]

    for pattern in patterns:
        match = re.search(pattern, input_str)
        if match:
            extracted = match.group(1)
            print(f"🔍 DEBUG: Padrão '{pattern}' encontrou: '{extracted}'")
            if extracted.startswith('UC') and len(extracted) == 24:
                print(f"🔍 DEBUG: ID do canal válido: {extracted}")
                return extracted
            print(f"🔍 DEBUG: Nome/handle do canal: {extracted}")
            return extracted

    print(f"🔍 DEBUG: Nenhum padrão encontrado para: {input_str}")
    return None

def get_channel_id_rapidapi(channel_name, api_key):
    """Obter ID do canal usando RapidAPI YouTube V2 com rotação de chaves e cache"""
    try:
        # Verificar cache primeiro
        cache_params = {'channel_name': channel_name}
        cached_result = get_from_cache('channel_id', cache_params, custom_ttl=3600)  # Cache por 1 hora
        if cached_result:
            return cached_result
        
        # Limpar cache expirado
        clear_expired_cache()
        
        url = "https://youtube-v2.p.rapidapi.com/channel/id"

        # Carregar chaves RapidAPI para rotação
        load_rapidapi_keys()
        
        # Usar chave fornecida ou obter da rotação
        current_api_key = api_key
        if not current_api_key or len(RAPIDAPI_KEYS_ROTATION['keys']) > 1:
            rotation_key = get_next_rapidapi_key()
            if rotation_key:
                current_api_key = rotation_key
                print(f"🔄 Usando chave da rotação: {current_api_key[:20]}...")

        headers = {
            "X-RapidAPI-Key": current_api_key,
            "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
        }

        params = {"channel_name": channel_name}

        print(f"🔍 DEBUG: Buscando ID do canal para: {channel_name}")
        print(f"🔍 DEBUG: URL: {url}")
        print(f"🔍 DEBUG: Params: {params}")

        # Tentar com retry e backoff exponencial mais agressivo para rate limiting
        max_retries = 3
        base_delay = 10  # Delay inicial maior: 10 segundos
        
        for attempt in range(max_retries):
            try:
                # Aplicar throttling inteligente antes da requisição
                apply_rapidapi_throttle()
                
                # Adicionar delay entre tentativas para evitar rate limiting
                if attempt > 0:
                    delay = base_delay * (3 ** (attempt - 1))  # Backoff mais agressivo (3x)
                    print(f"⏳ Aguardando {delay}s antes da tentativa {attempt + 1}...")
                    time.sleep(delay)
                    
                response = requests.get(url, headers=headers, params=params, timeout=30)
                print(f"🔍 DEBUG: Status da resposta: {response.status_code}")
                
                # Verificar se é erro 429 (Too Many Requests)
                if response.status_code == 429:
                    # Aplicar tratamento de rate limiting
                    handle_rapidapi_429()
                    
                    # Verificar se a resposta contém informação sobre quota excedida
                    try:
                        error_data = response.json()
                        if 'quota' in str(error_data).lower() or 'monthly' in str(error_data).lower():
                            print(f"📊 Quota mensal excedida para chave: {current_api_key[:20]}...")
                            mark_rapidapi_key_failed(current_api_key)
                            
                            # Tentar obter nova chave da rotação
                            new_key = get_next_rapidapi_key()
                            if new_key and new_key != current_api_key:
                                current_api_key = new_key
                                headers["X-RapidAPI-Key"] = current_api_key
                                print(f"🔄 Tentando com nova chave: {current_api_key[:20]}...")
                                continue
                    except:
                        pass
                    
                    if attempt == max_retries - 1:
                        return {
                            'success': False,
                            'error': 'Limite de requisições excedido (429). Tente novamente em alguns minutos.'
                        }
                    print(f"⚠️ Rate limit atingido (429), tentando novamente...")
                    continue
                    
                # Se chegou aqui com status 200, sair do loop
                if response.status_code == 200:
                    # Resetar throttling após sucesso
                    reset_rapidapi_throttle_success()
                    break
                    
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:  # Última tentativa
                    raise
                print(f"🔄 Tentativa {attempt + 1} falhou (timeout), tentando novamente...")
                continue

        if response.status_code != 200:
            print(f"🔍 DEBUG: Erro na resposta: {response.text}")
            
            # Tratamento específico para diferentes códigos de erro
            if response.status_code == 429:
                error_msg = 'Limite de requisições excedido. Aguarde alguns minutos e tente novamente.'
            elif response.status_code == 401:
                error_msg = 'Chave de API inválida ou expirada.'
            elif response.status_code == 403:
                error_msg = 'Acesso negado. Verifique suas permissões da API.'
            elif response.status_code == 404:
                error_msg = 'Canal não encontrado. Verifique o nome do canal.'
            else:
                error_msg = f'Erro na API: {response.status_code} - {response.text}'
                
            return {
                'success': False,
                'error': error_msg
            }

        data = response.json()
        print(f"🔍 DEBUG: Resposta da API: {data}")

        if 'channel_id' not in data:
            return {
                'success': False,
                'error': 'Canal não encontrado'
            }

        result = {
            'success': True,
            'data': {
                'channel_id': data['channel_id'],
                'channel_name': data.get('channel_name', channel_name)
            }
        }
        
        # Salvar no cache
        save_to_cache('channel_id', cache_params, result, custom_ttl=3600)
        
        return result

    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao buscar ID do canal: {str(e)}'
        }

def get_channel_details_rapidapi(channel_id, api_key):
    """Obter detalhes do canal usando RapidAPI YouTube V2 com rate limiting, rotação de chaves e cache"""
    import time
    
    try:
        # Verificar cache primeiro
        cache_params = {'channel_id': channel_id}
        cached_result = get_from_cache('channel_details', cache_params, custom_ttl=1800)  # Cache por 30 minutos
        if cached_result:
            return cached_result
        
        # Limpar cache expirado
        clear_expired_cache()
        
        url = "https://youtube-v2.p.rapidapi.com/channel/details"

        # Carregar chaves RapidAPI para rotação
        load_rapidapi_keys()
        
        # Usar chave fornecida ou obter da rotação
        current_api_key = api_key
        if not current_api_key or len(RAPIDAPI_KEYS_ROTATION['keys']) > 1:
            rotation_key = get_next_rapidapi_key()
            if rotation_key:
                current_api_key = rotation_key
                print(f"🔄 Usando chave da rotação: {current_api_key[:20]}...")

        headers = {
            "X-RapidAPI-Key": current_api_key,
            "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
        }

        params = {"channel_id": channel_id}

        # Retry com backoff exponencial mais agressivo
        max_retries = 3
        base_delay = 10  # Delay inicial maior: 10 segundos
        
        for attempt in range(max_retries):
            # Aplicar throttling inteligente antes da requisição
            apply_rapidapi_throttle()
            
            if attempt > 0:
                delay = base_delay * (3 ** (attempt - 1))  # Backoff mais agressivo (3x)
                print(f"⏳ Aguardando {delay}s antes da tentativa {attempt + 1}...")
                time.sleep(delay)
                
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 429:
                # Aplicar tratamento de rate limiting
                handle_rapidapi_429()
                # Verificar se a resposta contém informação sobre quota excedida
                try:
                    error_data = response.json()
                    if 'quota' in str(error_data).lower() or 'monthly' in str(error_data).lower():
                        print(f"📊 Quota mensal excedida para chave: {current_api_key[:20]}...")
                        mark_rapidapi_key_failed(current_api_key)
                        
                        # Tentar obter nova chave da rotação
                        new_key = get_next_rapidapi_key()
                        if new_key and new_key != current_api_key:
                            current_api_key = new_key
                            headers["X-RapidAPI-Key"] = current_api_key
                            print(f"🔄 Tentando com nova chave: {current_api_key[:20]}...")
                            continue
                except:
                    pass
                
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'error': 'Limite de requisições excedido. Aguarde alguns minutos e tente novamente.'
                    }
                print(f"⚠️ Rate limit atingido (429), tentando novamente...")
                continue
            elif response.status_code == 200:
                break

        if response.status_code != 200:
            if response.status_code == 429:
                error_msg = 'Limite de requisições excedido. Aguarde alguns minutos e tente novamente.'
            elif response.status_code == 401:
                error_msg = 'Chave de API inválida ou expirada.'
            elif response.status_code == 403:
                error_msg = 'Acesso negado. Verifique suas permissões da API.'
            elif response.status_code == 404:
                error_msg = 'Canal não encontrado. Verifique o ID do canal.'
            else:
                error_msg = f'Erro na API: {response.status_code}'
                
            return {
                'success': False,
                'error': error_msg
            }

        data = response.json()

        result = {
            'success': True,
            'data': {
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'subscriber_count': data.get('subscriber_count', 0),
                'video_count': data.get('video_count', 0)
            }
        }
        
        # Salvar no cache
        save_to_cache('channel_details', cache_params, result, custom_ttl=1800)
        
        return result

    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao buscar detalhes do canal: {str(e)}'
        }

def get_channel_videos_rapidapi(channel_id, api_key, max_results=50):
    """Obter vídeos do canal usando RapidAPI YouTube V2 com rate limiting, cache e rotação de chaves"""
    import time
    
    try:
        # Verificar cache primeiro
        cache_params = {
            'channel_id': channel_id,
            'max_results': min(max_results, 50)
        }
        cached_result = get_from_cache('channel_videos', cache_params, custom_ttl=600)  # Cache por 10 minutos
        if cached_result:
            return cached_result
        
        # Limpar cache expirado
        clear_expired_cache()
        
        url = "https://youtube-v2.p.rapidapi.com/channel/videos"
        print(f"🔍 DEBUG: Fazendo requisição para: {url}")
        print(f"🔍 DEBUG: Channel ID: {channel_id}")

        # Carregar chaves RapidAPI para rotação
        load_rapidapi_keys()
        
        # Usar chave fornecida ou obter da rotação
        current_api_key = api_key
        if not current_api_key or len(RAPIDAPI_KEYS_ROTATION['keys']) > 1:
            rotation_key = get_next_rapidapi_key()
            if rotation_key:
                current_api_key = rotation_key
                print(f"🔄 Usando chave da rotação: {current_api_key[:20]}...")

        headers = {
            "X-RapidAPI-Key": current_api_key,
            "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
        }

        print(f"🔍 DEBUG: Parâmetros: {params}")
        print(f"🔍 DEBUG: API Key presente: {'Sim' if current_api_key else 'Não'}")
        print(f"🔍 DEBUG: API Key length: {len(current_api_key) if current_api_key else 0}")

        # Tentar com retry e backoff exponencial mais agressivo para rate limiting
        max_retries = 3  # Reduzir tentativas para evitar spam
        base_delay = 10  # Delay inicial maior: 10 segundos
        
        for attempt in range(max_retries):
            try:
                # Aplicar throttling inteligente antes da requisição
                apply_rapidapi_throttle()
                
                # Adicionar delay entre tentativas para evitar rate limiting
                if attempt > 0:
                    delay = base_delay * (3 ** (attempt - 1))  # Backoff mais agressivo (3x)
                    print(f"⏳ Aguardando {delay}s antes da tentativa {attempt + 1}...")
                    time.sleep(delay)
                
                response = requests.get(url, headers=headers, params=params, timeout=30)
                print(f"🔍 DEBUG: Status da resposta: {response.status_code}")
                
                # Verificar se é erro 429 (Too Many Requests)
                if response.status_code == 429:
                    # Aplicar tratamento de rate limiting
                    handle_rapidapi_429()
                    # Verificar se a resposta contém informação sobre quota excedida
                    try:
                        error_data = response.json()
                        if 'quota' in str(error_data).lower() or 'monthly' in str(error_data).lower():
                            print(f"📊 Quota mensal excedida para chave: {current_api_key[:20]}...")
                            mark_rapidapi_key_failed(current_api_key)
                            
                            # Tentar obter nova chave da rotação
                            new_key = get_next_rapidapi_key()
                            if new_key and new_key != current_api_key:
                                current_api_key = new_key
                                headers["X-RapidAPI-Key"] = current_api_key
                                print(f"🔄 Tentando com nova chave: {current_api_key[:20]}...")
                                continue
                    except:
                        pass
                    
                    if attempt == max_retries - 1:
                        return {
                            'success': False,
                            'error': 'Limite de requisições excedido (429). Tente novamente em alguns minutos.'
                        }
                    print(f"⚠️ Rate limit atingido (429), tentando novamente em {base_delay * (3 ** attempt)}s...")
                    continue
                
                # Se chegou aqui com status 200, sair do loop
                if response.status_code == 200:
                    # Resetar throttling após sucesso
                    reset_rapidapi_throttle_success()
                    break
                    
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:  # Última tentativa
                    print(f"🔍 DEBUG: Timeout após {max_retries} tentativas")
                    raise
                print(f"🔄 Tentativa {attempt + 1} falhou (timeout), tentando novamente...")
                continue

        if response.status_code != 200:
            print(f"🔍 DEBUG: Erro na resposta: {response.text}")
            
            # Tratamento específico para diferentes códigos de erro
            if response.status_code == 429:
                error_msg = 'Limite de requisições excedido. Aguarde alguns minutos e tente novamente.'
            elif response.status_code == 401:
                error_msg = 'Chave de API inválida ou expirada.'
            elif response.status_code == 403:
                error_msg = 'Acesso negado. Verifique suas permissões da API.'
            elif response.status_code == 404:
                error_msg = 'Canal não encontrado. Verifique o ID do canal.'
            else:
                error_msg = f'Erro na API: {response.status_code}'
                
            return {
                'success': False,
                'error': error_msg
            }

        data = response.json()
        print(f"🔍 DEBUG: Resposta da API (primeiros 500 chars): {str(data)[:500]}...")

        if 'videos' not in data:
            print(f"🔍 DEBUG: Chaves disponíveis na resposta: {list(data.keys())}")
            # Verificar se há erro na resposta da API
            if 'error' in data:
                print(f"🔍 DEBUG: Erro da API: {data['error']}")
                return {
                    'success': False,
                    'error': f'Erro da API RapidAPI: {data["error"]}'
                }
            return {
                'success': False,
                'error': 'Nenhum vídeo encontrado no canal - verifique se o ID do canal está correto'
            }

        print(f"🔍 DEBUG: Encontrados {len(data['videos'])} vídeos na resposta")

        # Processar dados dos vídeos
        videos = []
        for i, video in enumerate(data['videos']):
            if i < 3:  # Log apenas os primeiros 3 vídeos para debug
                print(f"🔍 DEBUG: Vídeo {i+1}: {video}")

            # A API RapidAPI retorna 'number_of_views' como inteiro
            processed_video = {
                'video_id': video.get('video_id', ''),
                'title': video.get('title', ''),
                'description': video.get('description', ''),
                'thumbnail': video.get('thumbnail', ''),
                'duration': video.get('video_length', ''),  # API usa 'video_length'
                'views': parse_view_count(video.get('number_of_views', 0)),  # API usa 'number_of_views'
                'likes': parse_count(video.get('likes', '0')),
                'published_at': video.get('published_time', ''),  # API usa 'published_time'
                'url': f"https://youtube.com/watch?v={video.get('video_id', '')}"
            }
            videos.append(processed_video)

            if i < 3:  # Log apenas os primeiros 3 vídeos processados
                print(f"🔍 DEBUG: Vídeo processado {i+1}: views={processed_video['views']}, title={processed_video['title'][:50]}...")

        result = {
            'success': True,
            'data': {
                'videos': videos,
                'total_videos': len(videos),
                'total_count': len(videos),
                'message': f'✅ {len(videos)} títulos extraídos com sucesso!'
            }
        }
        
        # Salvar no cache para evitar chamadas futuras
        save_to_cache('channel_videos', cache_params, result, custom_ttl=600)
        
        return result

    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao buscar vídeos: {str(e)}'
        }

def filter_videos_by_config(videos, config):
    """Filtrar vídeos baseado na configuração fornecida"""
    if not videos:
        print("🔍 DEBUG: Nenhum vídeo para filtrar")
        return []

    print(f"🔍 DEBUG: Iniciando filtros com {len(videos)} vídeos")
    filtered = videos.copy()

    # Filtro por views mínimas
    min_views = config.get('min_views', 0)
    print(f"🔍 DEBUG: Filtro min_views: {min_views}")
    if min_views > 0:
        before_count = len(filtered)
        filtered = [v for v in filtered if v.get('views', 0) >= min_views]
        print(f"🔍 DEBUG: Após filtro min_views: {before_count} -> {len(filtered)}")
        if len(filtered) > 0:
            print(f"🔍 DEBUG: Exemplo de vídeo que passou: views={filtered[0].get('views', 0)}")

    # Filtro por views máximas (só aplicar se for maior que 0)
    max_views = config.get('max_views', 0)
    if max_views > 0:
        print(f"🔍 DEBUG: Filtro max_views: {max_views}")
        before_count = len(filtered)
        filtered = [v for v in filtered if v.get('views', 0) <= max_views]
        print(f"🔍 DEBUG: Após filtro max_views: {before_count} -> {len(filtered)}")
    else:
        print(f"🔍 DEBUG: Filtro max_views: {max_views} (ignorado - sem limite máximo)")

    # Filtro por dias (DESABILITADO - API usa formato relativo como "20 hours ago")
    days_filter = config.get('days', 0)
    print(f"🔍 DEBUG: Filtro de dias: {days_filter} (DESABILITADO)")
    print(f"🔍 DEBUG: Após filtro de dias: {len(filtered)} (todos mantidos)")

    # Limitar número máximo de títulos
    max_titles = config.get('max_titles', 50)
    if max_titles > 0:
        before_limit = len(filtered)
        filtered = filtered[:max_titles]
        print(f"🔍 DEBUG: Limitando títulos: {before_limit} -> {len(filtered)} (max: {max_titles})")

    print(f"🔍 DEBUG: RESULTADO FINAL: {len(filtered)} vídeos")
    if filtered:
        print(f"🔍 DEBUG: Primeiro título: {filtered[0].get('title', 'N/A')}")
        print(f"🔍 DEBUG: Primeiros 3 títulos:")
        for i, video in enumerate(filtered[:3]):
            print(f"🔍 DEBUG: {i+1}. {video.get('title', 'N/A')} ({video.get('views', 0)} views)")
    else:
        print(f"🔍 DEBUG: ❌ NENHUM VÍDEO NO RESULTADO FINAL!")

    return filtered

def parse_view_count(view_input):
    """Converter string ou número de views para número inteiro"""
    if not view_input:
        return 0

    # Se já for um número inteiro, retornar diretamente
    if isinstance(view_input, int):
        return view_input

    # Se for float, converter para int
    if isinstance(view_input, float):
        return int(view_input)

    # Converter para string e processar
    view_str = str(view_input).lower().replace(',', '').replace('.', '')

    # Extrair apenas números e multiplicadores
    import re
    match = re.search(r'([\d,\.]+)\s*([kmb]?)', view_str)
    if not match:
        return 0

    number_str, multiplier = match.groups()
    try:
        number = float(number_str.replace(',', ''))

        if multiplier == 'k':
            return int(number * 1000)
        elif multiplier == 'm':
            return int(number * 1000000)
        elif multiplier == 'b':
            return int(number * 1000000000)
        else:
            return int(number)
    except ValueError:
        return 0

def parse_count(count_str):
    """Converter string de contagem para número"""
    if not count_str:
        return 0

    try:
        # Remover caracteres não numéricos exceto pontos e vírgulas
        clean_str = re.sub(r'[^\d,\.]', '', str(count_str))
        if clean_str:
            return int(float(clean_str.replace(',', '')))
    except ValueError:
        pass

    return 0

@automations_bp.route('/generate-titles', methods=['POST'])
def generate_titles():
    """Gerar títulos virais baseados em títulos extraídos"""
    try:
        data = request.get_json()

        # Validar dados de entrada
        source_titles = data.get('source_titles', [])
        topic = data.get('topic', '')
        count = data.get('count', 10)
        style = data.get('style', 'viral')
        ai_provider = data.get('ai_provider', 'auto')  # 'openai', 'gemini', 'auto'

        if not source_titles:
            return jsonify({
                'success': False,
                'error': 'Títulos de origem são obrigatórios'
            }), 400

        if not topic:
            return jsonify({
                'success': False,
                'error': 'Tópico é obrigatório'
            }), 400

        # Carregar chaves de API
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
        api_keys = {}

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                api_keys = json.load(f)

        # Inicializar gerador de títulos
        title_generator = TitleGenerator()

        # Configurar IAs disponíveis
        openai_configured = False
        gemini_configured = False
        openrouter_configured = False

        if api_keys.get('openai'):
            openai_configured = title_generator.configure_openai(api_keys['openai'])

        if api_keys.get('gemini'):
            gemini_configured = title_generator.configure_gemini(api_keys['gemini'])

        if api_keys.get('openrouter'):
            openrouter_configured = title_generator.configure_openrouter(api_keys['openrouter'])

        if not openai_configured and not gemini_configured and not openrouter_configured:
            return jsonify({
                'success': False,
                'error': 'Nenhuma IA configurada. Configure OpenAI, Gemini ou OpenRouter nas configurações.'
            }), 400

        print(f"🤖 Gerando títulos sobre '{topic}' baseado em {len(source_titles)} títulos de referência")

        # Gerar títulos baseado no provider escolhido
        if ai_provider == 'openai' and openai_configured:
            generated_titles = title_generator.generate_titles_openai(source_titles, topic, count, style)
            results = {
                'generated_titles': generated_titles,
                'ai_provider_used': 'openai',
                'patterns_analysis': title_generator.analyze_viral_patterns(source_titles)
            }
        elif ai_provider == 'gemini' and gemini_configured:
            generated_titles = title_generator.generate_titles_gemini(source_titles, topic, count, style)
            results = {
                'generated_titles': generated_titles,
                'ai_provider_used': 'gemini',
                'patterns_analysis': title_generator.analyze_viral_patterns(source_titles)
            }
        else:
            # Modo automático - usar híbrido ou o que estiver disponível
            results = title_generator.generate_titles_hybrid(source_titles, topic, count, style)

        if results.get('success', True) and (results.get('generated_titles') or results.get('combined_titles')):
            final_titles = results.get('combined_titles') or results.get('generated_titles', [])

            return jsonify({
                'success': True,
                'data': {
                    'generated_titles': final_titles,
                    'total_generated': len(final_titles),
                    'ai_provider_used': results.get('ai_provider_used', 'hybrid'),
                    'patterns_analysis': results.get('patterns_analysis', {}),
                    'source_titles_count': len(source_titles),
                    'topic': topic,
                    'style': style
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': results.get('error', 'Falha na geração de títulos')
            }), 500

    except Exception as e:
        print(f"❌ Erro na geração de títulos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automations_bp.route('/analyze-titles', methods=['POST'])
def analyze_titles():
    """Analisar padrões virais em uma lista de títulos"""
    try:
        data = request.get_json()
        titles = data.get('titles', [])

        if not titles:
            return jsonify({
                'success': False,
                'error': 'Lista de títulos é obrigatória'
            }), 400

        # Inicializar gerador para usar a análise
        title_generator = TitleGenerator()
        patterns = title_generator.analyze_viral_patterns(titles)

        return jsonify({
            'success': True,
            'data': {
                'patterns': patterns,
                'total_titles_analyzed': len(titles),
                'analysis_summary': {
                    'most_common_triggers': patterns['emotional_triggers'][:5],
                    'popular_numbers': patterns['numbers'][:3],
                    'effective_structures': patterns['structures'],
                    'optimal_length': f"{patterns['length_stats']['min']}-{patterns['length_stats']['max']} chars"
                }
            }
        })

    except Exception as e:
        print(f"❌ Erro na análise de títulos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automations_bp.route('/generate-titles-custom', methods=['POST'])
def generate_titles_custom():
    """Gerar títulos usando prompt personalizado baseado em títulos extraídos"""
    try:
        data = request.get_json()

        # Validar dados de entrada
        source_titles = data.get('source_titles', [])
        custom_prompt = data.get('custom_prompt', '')
        count = data.get('count', 10)
        ai_provider = data.get('ai_provider', 'auto')  # 'openai', 'gemini', 'auto'

        if not source_titles:
            return jsonify({
                'success': False,
                'error': 'Títulos de origem são obrigatórios'
            }), 400

        if not custom_prompt.strip():
            return jsonify({
                'success': False,
                'error': 'Prompt personalizado é obrigatório'
            }), 400

        # Carregar chaves de API
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
        api_keys = {}

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                api_keys = json.load(f)

        # Inicializar gerador de títulos
        title_generator = TitleGenerator()

        # Configurar IAs disponíveis
        openai_configured = False
        gemini_configured = False
        openrouter_configured = False

        if api_keys.get('openai'):
            openai_configured = title_generator.configure_openai(api_keys['openai'])

        if api_keys.get('gemini'):
            gemini_configured = title_generator.configure_gemini(api_keys['gemini'])

        if api_keys.get('openrouter'):
            openrouter_configured = title_generator.configure_openrouter(api_keys['openrouter'])

        if not openai_configured and not gemini_configured and not openrouter_configured:
            return jsonify({
                'success': False,
                'error': 'Nenhuma IA configurada. Configure OpenAI, Gemini ou OpenRouter nas configurações.'
            }), 400

        print(f"🎨 Gerando títulos com prompt personalizado baseado em {len(source_titles)} títulos")
        print(f"📝 Prompt: {custom_prompt[:100]}...")

        # Gerar títulos com prompt personalizado
        results = title_generator.generate_titles_with_custom_prompt(
            source_titles,
            custom_prompt,
            count,
            ai_provider
        )

        if results.get('success', False):
            return jsonify({
                'success': True,
                'data': {
                    'generated_titles': results['generated_titles'],
                    'total_generated': len(results['generated_titles']),
                    'ai_provider_used': results['ai_provider_used'],
                    'patterns_analysis': results['patterns_analysis'],
                    'source_titles_count': len(source_titles),
                    'custom_prompt_used': results['custom_prompt_used']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': results.get('error', 'Falha na geração de títulos com prompt personalizado')
            }), 500

    except Exception as e:
        print(f"❌ Erro na geração com prompt personalizado: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# 🎵 FUNÇÕES DE TTS
# ================================

def generate_tts_with_kokoro(text, kokoro_url='http://localhost:8880', voice_name='af_bella', language='en', job_id=None, **kwargs):
    """Gerar áudio TTS usando API Kokoro FastAPI"""
    try:
        print(f"🎵 Iniciando TTS com Kokoro - Texto: {len(text)} chars, Voz: {voice_name}, Idioma: {language}")
        add_real_time_log(f"🎵 Iniciando TTS com Kokoro - Texto: {len(text)} chars, Voz: {voice_name}, Idioma: {language}", "info", "tts-kokoro")

        # Verificar se job foi cancelado
        if job_id and TTS_JOBS.get(job_id, {}).get('cancelled', False):
            add_real_time_log(f"🛑 TTS Kokoro - Job {job_id} cancelado antes do início", "warning", "tts-kokoro")
            raise Exception("Geração cancelada pelo usuário")

        # Configurar URL da API Kokoro
        url = f"{kokoro_url}/v1/audio/speech"

        # Preparar payload compatível com OpenAI
        payload = {
            "model": "kokoro",
            "input": text,
            "voice": voice_name,
            "response_format": "wav",
            "speed": kwargs.get('speed', 1.0),
            "language": language
        }

        headers = {
            'Content-Type': 'application/json'
        }

        print(f"🔍 Enviando requisição para Kokoro TTS API...")
        print(f"🔍 URL: {url}")
        print(f"🔍 Voz: {voice_name}")
        add_real_time_log(f"🔍 Enviando requisição para Kokoro TTS: {voice_name}", "info", "tts-kokoro")

        # Fazer requisição com timeout otimizado
        timeout = 60  # Timeout de 60 segundos para Kokoro

        # Verificar cancelamento antes da requisição
        if job_id and TTS_JOBS.get(job_id, {}).get('cancelled', False):
            add_real_time_log(f"🛑 TTS Kokoro - Job {job_id} cancelado durante requisição", "warning", "tts-kokoro")
            raise Exception("Geração cancelada pelo usuário")

        response = requests.post(url, json=payload, headers=headers, timeout=timeout)

        print(f"🔍 Status da resposta: {response.status_code}")
        add_real_time_log(f"✅ Kokoro TTS - Resposta recebida (status: {response.status_code})", "success", "tts-kokoro")

        if response.status_code != 200:
            error_msg = f"Erro da API Kokoro TTS: {response.status_code} - {response.text}"
            print(f"❌ {error_msg}")
            add_real_time_log(f"❌ {error_msg}", "error", "tts-kokoro")
            raise Exception(error_msg)

        # Verificar cancelamento após resposta
        if job_id and TTS_JOBS.get(job_id, {}).get('cancelled', False):
            add_real_time_log(f"🛑 TTS Kokoro - Job {job_id} cancelado após resposta", "warning", "tts-kokoro")
            raise Exception("Geração cancelada pelo usuário")

        # Salvar áudio diretamente (Kokoro retorna áudio binário)
        audio_bytes = response.content

        temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        timestamp = int(time.time())
        filename = f"tts_kokoro_{timestamp}.wav"
        filepath = os.path.join(temp_dir, filename)

        print(f"🔍 Salvando áudio em: {filepath}")
        add_real_time_log(f"🔍 Salvando áudio Kokoro: {filename}", "info", "tts-kokoro")

        with open(filepath, 'wb') as f:
            f.write(audio_bytes)

        print(f"✅ Áudio TTS Kokoro gerado com sucesso: {filepath}")
        add_real_time_log(f"✅ Áudio Kokoro salvo com sucesso: {filename} ({len(audio_bytes)} bytes)", "success", "tts-kokoro")

        return {
            'success': True,
            'data': {
                'audio_url': f'/api/automations/audio/{filename}',
                'filename': filename,
                'voice_used': voice_name,
                'language_used': language,
                'text_length': len(text),
                'kokoro_url': kokoro_url,
                'size': len(audio_bytes),
                'duration': 0  # Kokoro não fornece duração, mas adicionamos para compatibilidade
            },
            'message': 'Áudio gerado com sucesso usando Kokoro TTS'
        }

    except Exception as e:
        error_msg = f"Erro no TTS Kokoro: {str(e)}"
        print(f"❌ {error_msg}")
        add_real_time_log(f"❌ {error_msg}", "error", "tts-kokoro")
        return {
            'success': False,
            'error': error_msg
        }

def generate_tts_with_gemini(text, api_key=None, voice_name='Aoede', model='gemini-2.5-flash-preview-tts', job_id=None, **kwargs):
    """Gerar áudio TTS usando API Gemini nativa com rotação de chaves"""
    try:
        print(f"🎵 Iniciando TTS com Gemini - Texto: {len(text)} chars, Voz: {voice_name}")

        # Usar rotação de chaves se não foi fornecida uma chave específica
        if not api_key:
            api_key = get_next_gemini_key()
            if not api_key:
                raise Exception("Nenhuma chave Gemini disponível")

        import requests
        import json
        import time

        # Limitar o texto para evitar timeouts (Gemini TTS tem limite menor)
        max_chars = 2000  # Limite mais conservador para TTS
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            print(f"⚠️ Texto truncado para {len(text)} caracteres (limite TTS: {max_chars})")

        # Usar API REST do Gemini para TTS
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [{
                    "text": text
                }]
            }],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": voice_name
                        }
                    }
                }
            }
        }

        print(f"🔍 Enviando requisição para Gemini TTS API...")
        print(f"🔍 URL: {url}")
        print(f"🔍 Voz: {voice_name}")

        # Implementar retry com timeout otimizado
        max_retries = 2  # Reduzir para 2 tentativas para ser mais rápido
        timeouts = [45, 90]  # Timeouts otimizados

        for attempt in range(max_retries):
            # Verificar se job foi cancelado
            if job_id and TTS_JOBS.get(job_id, {}).get('cancelled', False):
                add_real_time_log(f"🛑 TTS Gemini - Job {job_id} cancelado durante retry", "warning", "tts-gemini")
                raise Exception("Geração cancelada pelo usuário")

            try:
                timeout = timeouts[attempt]
                print(f"🔄 Tentativa {attempt + 1}/{max_retries} - Timeout: {timeout}s")
                add_real_time_log(f"🔄 TTS Gemini - Tentativa {attempt + 1}/{max_retries} (timeout: {timeout}s)", "info", "tts-gemini")

                response = requests.post(url, json=payload, headers=headers, timeout=timeout)
                add_real_time_log(f"✅ TTS Gemini - Resposta recebida (status: {response.status_code})", "success", "tts-gemini")
                break  # Se chegou aqui, a requisição foi bem-sucedida

            except requests.exceptions.Timeout:
                print(f"⏰ Timeout na tentativa {attempt + 1}")
                add_real_time_log(f"⏰ TTS Gemini - Timeout na tentativa {attempt + 1}", "warning", "tts-gemini")
                if attempt == max_retries - 1:
                    error_msg = f"Timeout após {max_retries} tentativas. Tente novamente ou use ElevenLabs."
                    add_real_time_log(f"❌ TTS Gemini - {error_msg}", "error", "tts-gemini")
                    raise Exception(error_msg)
                print(f"🔄 Tentando novamente em 3 segundos...")
                time.sleep(3)
            except Exception as e:
                print(f"❌ Erro na tentativa {attempt + 1}: {str(e)}")
                add_real_time_log(f"❌ TTS Gemini - Erro tentativa {attempt + 1}: {str(e)}", "error", "tts-gemini")
                if attempt == max_retries - 1:
                    raise
                print(f"🔄 Tentando novamente em 3 segundos...")
                time.sleep(3)

        print(f"🔍 Status da resposta: {response.status_code}")

        if response.status_code != 200:
            error_msg = f"Erro da API Gemini TTS: {response.status_code} - {response.text}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)

        result = response.json()
        print(f"🔍 Resposta recebida: {result.keys() if isinstance(result, dict) else 'não é dict'}")
        add_real_time_log(f"🔍 Processando resposta da API Gemini TTS", "info", "tts-gemini")

        # Extrair dados do áudio da resposta Gemini
        if 'candidates' not in result or not result['candidates']:
            error_msg = "Resposta não contém candidates"
            add_real_time_log(f"❌ {error_msg}", "error", "tts-gemini")
            raise Exception(error_msg)

        candidate = result['candidates'][0]
        if 'content' not in candidate or 'parts' not in candidate['content']:
            error_msg = "Resposta não contém content/parts"
            add_real_time_log(f"❌ {error_msg}", "error", "tts-gemini")
            raise Exception(error_msg)

        parts = candidate['content']['parts']
        if not parts or 'inlineData' not in parts[0]:
            error_msg = "Resposta não contém inlineData"
            add_real_time_log(f"❌ {error_msg}", "error", "tts-gemini")
            raise Exception(error_msg)

        audio_data = parts[0]['inlineData']['data']
        add_real_time_log(f"✅ Dados de áudio extraídos com sucesso", "success", "tts-gemini")

        # Salvar arquivo temporário
        import tempfile
        import os
        import base64

        temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        timestamp = int(time.time())
        filename = f"tts_gemini_{timestamp}.wav"
        filepath = os.path.join(temp_dir, filename)

        print(f"🔍 Salvando áudio em: {filepath}")
        add_real_time_log(f"🔍 Salvando áudio TTS: {filename}", "info", "tts-gemini")

        # Decodificar base64 e salvar
        audio_bytes = base64.b64decode(audio_data)
        with open(filepath, 'wb') as f:
            f.write(audio_bytes)

        print(f"✅ Áudio TTS gerado com sucesso: {filepath}")
        add_real_time_log(f"✅ Áudio TTS salvo com sucesso: {filename} ({len(audio_bytes)} bytes)", "success", "tts-gemini")

        # URL para acessar o áudio
        audio_url = f"/api/automations/audio/{filename}"

        return {
            'success': True,
            'data': {
                'audio_file': filepath,
                'filename': filename,
                'audio_url': audio_url,
                'duration': get_audio_duration(filepath),
                'size': len(audio_bytes),
                'voice_used': voice_name,
                'model_used': model,
                'text_length': len(text)
            }
        }

    except Exception as e:
        print(f"❌ Erro no TTS Gemini: {e}")
        return {
            'success': False,
            'error': f'Erro ao gerar áudio com Gemini: {str(e)}'
        }

@automations_bp.route('/tts/jobs', methods=['GET'])
def get_tts_jobs():
    """Obter lista de jobs TTS ativos"""
    try:
        # Limpar jobs antigos (mais de 1 hora)
        current_time = time.time()
        jobs_to_remove = []
        for job_id, job_data in TTS_JOBS.items():
            if current_time - job_data['start_time'] > 3600:  # 1 hora
                jobs_to_remove.append(job_id)

        for job_id in jobs_to_remove:
            del TTS_JOBS[job_id]

        return jsonify({
            'success': True,
            'jobs': TTS_JOBS
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automations_bp.route('/tts/jobs/<job_id>/cancel', methods=['POST'])
def cancel_tts_job(job_id):
    """Cancelar job TTS específico"""
    try:
        if job_id in TTS_JOBS:
            TTS_JOBS[job_id]['cancelled'] = True
            TTS_JOBS[job_id]['status'] = 'cancelled'
            add_real_time_log(f"🛑 TTS Job {job_id} cancelado via API", "warning", "tts-control")
            return jsonify({
                'success': True,
                'message': f'Job {job_id} cancelado'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Job não encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automations_bp.route('/audio/<filename>')
def serve_tts_audio(filename):
    """Servir arquivos de áudio gerados"""
    try:
        import os
        from flask import send_file

        temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
        filepath = os.path.join(temp_dir, filename)

        print(f"🔍 Tentando servir áudio: {filepath}")
        add_real_time_log(f"🔍 Servindo áudio: {filename}", "info", "audio-server")

        if os.path.exists(filepath):
            print(f"✅ Arquivo encontrado, servindo: {filename}")
            add_real_time_log(f"✅ Áudio servido com sucesso: {filename}", "success", "audio-server")
            return send_file(filepath, as_attachment=False, mimetype='audio/wav')
        else:
            print(f"❌ Arquivo não encontrado: {filepath}")
            add_real_time_log(f"❌ Arquivo de áudio não encontrado: {filename}", "error", "audio-server")
            return jsonify({'error': 'Arquivo não encontrado'}), 404

    except Exception as e:
        print(f"❌ Erro ao servir áudio: {str(e)}")
        add_real_time_log(f"❌ Erro ao servir áudio: {str(e)}", "error", "audio-server")
        return jsonify({'error': f'Erro ao servir áudio: {str(e)}'}), 500

def get_audio_duration(filepath):
    """Obter duração do arquivo de áudio"""
    try:
        # Tentar usar mutagen para MP3
        try:
            from mutagen.mp3 import MP3
            audio = MP3(filepath)
            return round(audio.info.length, 2)
        except ImportError:
            # Fallback: estimar duração baseado no tamanho do arquivo
            import os
            file_size = os.path.getsize(filepath)
            # Estimativa: ~1KB por segundo para MP3 de qualidade média
            estimated_duration = file_size / 1024
            return round(estimated_duration, 2)
        except:
            # Se for WAV, usar wave
            import wave
            with wave.open(filepath, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate)
                return round(duration, 2)
    except Exception as e:
        print(f"⚠️ Erro ao obter duração do áudio: {e}")
        return 0.0

def generate_tts_with_elevenlabs(text, api_key, voice_id='default', model_id='eleven_monolingual_v1', **kwargs):
    """Gerar áudio TTS usando ElevenLabs"""
    try:
        print(f"🎵 Iniciando TTS com ElevenLabs - Texto: {len(text)} chars, Voz: {voice_id}")

        # Se voice_id for 'default', usar uma voz padrão conhecida
        if voice_id == 'default':
            voice_id = '21m00Tcm4TlvDq8ikWAM'  # Rachel (voz feminina em inglês)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }

        # Configurações de voz mais avançadas
        voice_settings = {
            "stability": kwargs.get('stability', 0.5),
            "similarity_boost": kwargs.get('similarity_boost', 0.5),
            "style": kwargs.get('style', 0.0),
            "use_speaker_boost": kwargs.get('use_speaker_boost', True)
        }

        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings
        }

        print(f"🔍 DEBUG: Fazendo requisição para ElevenLabs...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)

        if response.status_code != 200:
            error_msg = f"Erro ElevenLabs: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('detail', response.text)}"
            except:
                error_msg += f" - {response.text}"

            return {
                'success': False,
                'error': error_msg
            }

        # Salvar arquivo de áudio
        import tempfile
        import os

        temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        timestamp = int(time.time())
        filename = f"tts_elevenlabs_{timestamp}.mp3"
        filepath = os.path.join(temp_dir, filename)

        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"✅ Áudio TTS ElevenLabs gerado com sucesso: {filepath}")

        return {
            'success': True,
            'data': {
                'audio_file': filepath,
                'filename': filename,
                'size': len(response.content),
                'voice_used': voice_id,
                'model_used': model_id,
                'text_length': len(text),
                'format': 'mp3'
            }
        }

    except Exception as e:
        print(f"❌ Erro no TTS ElevenLabs: {e}")
        return {
            'success': False,
            'error': f'Erro ao gerar áudio com ElevenLabs: {str(e)}'
        }

def join_audio_files(segments):
    """Juntar múltiplos arquivos de áudio em um só"""
    try:
        print(f"🔗 Juntando {len(segments)} segmentos de áudio...")

        import os
        from pydub import AudioSegment

        temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')

        # Carregar todos os segmentos
        audio_segments = []
        total_duration = 0
        total_size = 0

        for segment in sorted(segments, key=lambda x: x.get('index', 0)):
            filename = segment.get('filename')
            if not filename:
                continue

            filepath = os.path.join(temp_dir, filename)
            if not os.path.exists(filepath):
                print(f"⚠️ Arquivo não encontrado: {filepath}")
                continue

            # Carregar segmento de áudio
            if filename.endswith('.mp3'):
                audio_seg = AudioSegment.from_mp3(filepath)
            elif filename.endswith('.wav'):
                audio_seg = AudioSegment.from_wav(filepath)
            else:
                # Tentar detectar formato automaticamente
                audio_seg = AudioSegment.from_file(filepath)

            audio_segments.append(audio_seg)
            total_duration += len(audio_seg) / 1000.0  # pydub usa milissegundos
            total_size += os.path.getsize(filepath)

            print(f"✅ Carregado segmento: {filename} ({len(audio_seg)/1000:.1f}s)")

        if not audio_segments:
            return {
                'success': False,
                'error': 'Nenhum segmento de áudio válido encontrado'
            }

        # Juntar todos os segmentos
        print("🔗 Concatenando segmentos...")
        final_audio = audio_segments[0]
        for segment in audio_segments[1:]:
            final_audio += segment

        # Salvar arquivo final
        timestamp = int(time.time())
        final_filename = f"audio_final_{timestamp}.mp3"
        final_filepath = os.path.join(temp_dir, final_filename)

        # Exportar como MP3 com qualidade alta
        final_audio.export(
            final_filepath,
            format="mp3",
            bitrate="192k",
            parameters=["-q:a", "0"]
        )

        final_size = os.path.getsize(final_filepath)
        final_duration = len(final_audio) / 1000.0

        print(f"✅ Áudio final criado: {final_filename} ({final_duration:.1f}s, {final_size} bytes)")

        return {
            'success': True,
            'data': {
                'audio_file': final_filepath,
                'filename': final_filename,
                'duration': final_duration,
                'size': final_size,
                'segments_count': len(audio_segments),
                'format': 'mp3',
                'bitrate': '192k'
            }
        }

    except ImportError:
        return {
            'success': False,
            'error': 'Biblioteca pydub não instalada. Execute: pip install pydub'
        }
    except Exception as e:
        print(f"❌ Erro ao juntar áudios: {e}")
        return {
            'success': False,
            'error': f'Erro ao juntar áudios: {str(e)}'
        }

@automations_bp.route('/rapidapi/status', methods=['GET'])
def get_rapidapi_status():
    """Obter status do throttling e cache da RapidAPI"""
    try:
        with RAPIDAPI_THROTTLE['lock']:
            throttle_status = {
                'last_request_time': RAPIDAPI_THROTTLE['last_request_time'],
                'min_delay': RAPIDAPI_THROTTLE['min_delay'],
                'adaptive_delay': RAPIDAPI_THROTTLE['adaptive_delay'],
                'consecutive_429s': RAPIDAPI_THROTTLE['consecutive_429s'],
                'time_since_last_request': time.time() - RAPIDAPI_THROTTLE['last_request_time'] if RAPIDAPI_THROTTLE['last_request_time'] > 0 else 0
            }
        
        with RAPIDAPI_CACHE['lock']:
            cache_status = {
                'total_entries': len(RAPIDAPI_CACHE['data']),
                'ttl': RAPIDAPI_CACHE['ttl'],
                'entries': []
            }
            
            current_time = time.time()
            for cache_key, timestamp in RAPIDAPI_CACHE['timestamps'].items():
                age = current_time - timestamp
                remaining_ttl = max(0, RAPIDAPI_CACHE['ttl'] - age)
                cache_status['entries'].append({
                    'key': cache_key[:16] + '...',  # Mostrar apenas parte da chave
                    'age_seconds': round(age, 2),
                    'remaining_ttl': round(remaining_ttl, 2),
                    'expired': remaining_ttl <= 0
                })
        
        # Status das chaves RapidAPI
        keys_status = {
            'total_keys': len(RAPIDAPI_KEYS_ROTATION['keys']),
            'failed_keys': len(RAPIDAPI_KEYS_ROTATION['failed_keys']),
            'current_index': RAPIDAPI_KEYS_ROTATION['current_index'],
            'last_reset': RAPIDAPI_KEYS_ROTATION['last_reset']
        }
        
        return jsonify({
            'success': True,
            'data': {
                'throttling': throttle_status,
                'cache': cache_status,
                'keys_rotation': keys_status,
                'timestamp': time.time()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao obter status: {str(e)}'
        })

@automations_bp.route('/rapidapi/cache/clear', methods=['POST'])
def clear_rapidapi_cache():
    """Limpar cache da RapidAPI"""
    try:
        with RAPIDAPI_CACHE['lock']:
            entries_count = len(RAPIDAPI_CACHE['data'])
            RAPIDAPI_CACHE['data'].clear()
            RAPIDAPI_CACHE['timestamps'].clear()
        
        add_real_time_log(f"🧹 Cache RapidAPI limpo manualmente: {entries_count} entradas removidas", "info", "rapidapi-cache")
        
        return jsonify({
            'success': True,
            'message': f'Cache limpo com sucesso! {entries_count} entradas removidas.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao limpar cache: {str(e)}'
        })

@automations_bp.route('/rapidapi/throttle/reset', methods=['POST'])
def reset_rapidapi_throttle():
    """Resetar throttling da RapidAPI"""
    try:
        with RAPIDAPI_THROTTLE['lock']:
            old_delay = RAPIDAPI_THROTTLE['adaptive_delay']
            old_429s = RAPIDAPI_THROTTLE['consecutive_429s']
            
            RAPIDAPI_THROTTLE['consecutive_429s'] = 0
            RAPIDAPI_THROTTLE['adaptive_delay'] = RAPIDAPI_THROTTLE['min_delay']
            RAPIDAPI_THROTTLE['last_request_time'] = 0
        
        add_real_time_log(f"🔄 Throttling RapidAPI resetado manualmente (era {old_delay}s, {old_429s} 429s)", "info", "rapidapi-throttle")
        
        return jsonify({
            'success': True,
            'message': f'Throttling resetado com sucesso! (era {old_delay}s, {old_429s} 429s consecutivos)'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao resetar throttling: {str(e)}'
        })
