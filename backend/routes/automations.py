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
from utils.error_messages import auto_format_error, format_error_response

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

# Sistema de throttling inteligente para RapidAPI (OTIMIZADO)
RAPIDAPI_THROTTLE = {
    'last_request_time': 0,
    'min_delay': 1.0,  # Delay mínimo otimizado para 1s entre requisições
    'adaptive_delay': 1.0,  # Delay adaptativo otimizado baseado em rate limiting
    'max_delay': 60.0,  # Delay máximo de 60s
    'consecutive_429s': 0,  # Contador de 429s consecutivos
    'sequential_delay': 1.0,  # Delay adicional otimizado entre chamadas sequenciais
    'lock': threading.Lock()  # Lock para thread safety
}

# Sistema de cache otimizado para RapidAPI com persistência
RAPIDAPI_CACHE = {
    'data': {},  # Cache de dados
    'timestamps': {},  # Timestamps dos dados
    'ttl': 3600,  # TTL padrão aumentado para 1 hora (3600s)
    'channel_ttl': 7200,  # TTL para dados de canal: 2 horas
    'video_ttl': 1800,  # TTL para vídeos: 30 minutos
    'file_path': os.path.join(os.path.dirname(__file__), '..', 'cache', 'rapidapi_cache.json'),
    'lock': threading.Lock()  # Lock para thread safety
}

# Sistema de rate limiting global para RapidAPI
RAPIDAPI_RATE_LIMIT = {
    'requests_per_minute': 0,  # Contador de requisições por minuto
    'requests_per_hour': 0,    # Contador de requisições por hora
    'minute_window_start': 0,  # Timestamp do início da janela de minuto
    'hour_window_start': 0,    # Timestamp do início da janela de hora
    'max_requests_per_minute': 50,  # Limite máximo por minuto (ajustado para 1000/hora)
    'max_requests_per_hour': 900,   # Limite máximo por hora (margem de segurança para 1000/hora)
    'pause_until': 0,          # Timestamp até quando pausar requisições
    'total_requests_today': 0, # Total de requisições hoje
    'last_reset_date': datetime.now().date(),  # Data do último reset
    'lock': threading.Lock()   # Lock para thread safety
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

# Import AI Services functions
try:
    from services.ai_services import (
        generate_script_chapters_with_openai,
        generate_script_chapters_with_gemini,
        generate_script_chapters_with_claude,
        generate_script_chapters_with_openrouter
    )
    AI_SERVICES_AVAILABLE = True
    print("✅ AI Services importado com sucesso")
except ImportError as e:
    AI_SERVICES_AVAILABLE = False
    print(f"⚠️ AI Services não disponível: {e}")
    
    # Fallback: criar funções mock
    def generate_script_chapters_with_openai(*args, **kwargs):
        return {'success': False, 'error': 'AI Services não disponível'}
    
    def generate_script_chapters_with_gemini(*args, **kwargs):
        return {'success': False, 'error': 'AI Services não disponível'}
    
    def generate_script_chapters_with_claude(*args, **kwargs):
        return {'success': False, 'error': 'AI Services não disponível'}
    
    def generate_script_chapters_with_openrouter(*args, **kwargs):
        return {'success': False, 'error': 'AI Services não disponível'}

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
            
            # Logs detalhados para debug
            for i, key in enumerate(gemini_keys):
                print(f"🔍 [DEBUG] Chave {i+1}: {key[:20]}... (tamanho: {len(key)})")
            
            add_real_time_log(f"🔑 Carregadas {len(gemini_keys)} chaves Gemini", "info", "gemini-load")
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
            
            # Adicionar chave principal se existir
            if keys.get('rapidapi'):
                rapidapi_keys.append(keys.get('rapidapi'))
            
            # Adicionar chaves individuais de rotação
            for i in range(1, 11):  # rapidapi_1 até rapidapi_10
                key_name = f'rapidapi_{i}'
                if keys.get(key_name):
                    rapidapi_keys.append(keys.get(key_name))

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

    # Se todas as chaves atingiram o limite (8 por dia para respeitar limite de 50 do Free Tier), retornar None
    if min_usage >= 8:
        print("⚠️ Todas as chaves Gemini atingiram o limite diário (8/8). Limite Free Tier: 50 req/dia")
        add_real_time_log("⚠️ Todas as chaves Gemini atingiram o limite diário. Fallback necessário", "warning", "gemini-rotation")
        return None  # Retornar None para forçar fallback

    selected_key = keys[best_key_index]

    # Incrementar contador de uso
    GEMINI_KEYS_ROTATION['usage_count'][selected_key] = GEMINI_KEYS_ROTATION['usage_count'].get(selected_key, 0) + 1

    usage_count = GEMINI_KEYS_ROTATION['usage_count'][selected_key]
    
    # Logs detalhados para debug
    print(f"🔑 Usando chave Gemini {best_key_index + 1}/{len(keys)} (uso: {usage_count}/8) - Free Tier: 50 req/dia")
    print(f"🔍 [DEBUG] Chave selecionada: {selected_key[:20]}... (índice: {best_key_index})")
    print(f"🔍 [DEBUG] Estado das chaves: {[(i, GEMINI_KEYS_ROTATION['usage_count'].get(key, 0)) for i, key in enumerate(keys)]}")
    
    add_real_time_log(f"🔑 Usando chave Gemini {best_key_index + 1}/{len(keys)} (uso: {usage_count}/8)", "info", "gemini-rotation")
    add_real_time_log(f"🔍 Chave: {selected_key[:20]}... (índice: {best_key_index})", "debug", "gemini-key-detail")

    return selected_key

def handle_gemini_429_error(error_message, current_key=None):
    """Tratar erro 429 específico do Gemini com logs detalhados"""
    print(f"🚫 ERRO 429 GEMINI: {error_message}")
    add_real_time_log(f"🚫 ERRO 429 GEMINI: Quota excedida - {error_message}", "error", "gemini-429")
    
    # Log detalhado sobre o estado atual das chaves
    total_usage = sum(GEMINI_KEYS_ROTATION['usage_count'].values())
    num_keys = len(GEMINI_KEYS_ROTATION['keys'])
    
    print(f"📊 Estado das chaves Gemini: {total_usage} requisições usadas com {num_keys} chaves")
    add_real_time_log(f"📊 Estado Gemini: {total_usage} req usadas, {num_keys} chaves disponíveis", "info", "gemini-status")
    
    # Marcar apenas a chave atual como esgotada, não todas
    if current_key and current_key in GEMINI_KEYS_ROTATION['keys']:
        GEMINI_KEYS_ROTATION['usage_count'][current_key] = 8  # Marcar como limite atingido
        print(f"⚠️ Chave Gemini {current_key[:20]}... marcada como esgotada.")
        add_real_time_log(f"⚠️ Chave Gemini marcada como esgotada: {current_key[:20]}...", "warning", "gemini-key-exhausted")
    
    # Verificar se ainda há chaves disponíveis
    available_keys = 0
    for key in GEMINI_KEYS_ROTATION['keys']:
        if GEMINI_KEYS_ROTATION['usage_count'].get(key, 0) < 8:
            available_keys += 1
    
    if available_keys == 0:
        print("⚠️ Todas as chaves Gemini esgotadas. Fallback automático ativado.")
        add_real_time_log("⚠️ Fallback automático ativado para Gemini", "warning", "gemini-fallback")
        return False
    else:
        print(f"✅ Ainda há {available_keys} chaves Gemini disponíveis.")
        add_real_time_log(f"✅ {available_keys} chaves Gemini ainda disponíveis", "info", "gemini-available")
        return True

def check_gemini_availability():
    """Verificar se há chaves Gemini disponíveis"""
    if not GEMINI_KEYS_ROTATION['keys']:
        load_gemini_keys()
    
    # Reset diário
    today = datetime.now().date()
    if GEMINI_KEYS_ROTATION['last_reset'] != today:
        GEMINI_KEYS_ROTATION['usage_count'] = {}
        GEMINI_KEYS_ROTATION['last_reset'] = today
    
    # Verificar se alguma chave ainda tem quota disponível
    for key in GEMINI_KEYS_ROTATION['keys']:
        usage = GEMINI_KEYS_ROTATION['usage_count'].get(key, 0)
        if usage < 8:  # Limite de 8 por chave
            return True
    
    return False

def get_fallback_provider_info():
    """Obter informações sobre provedores de fallback disponíveis com hierarquia: Gemini → OpenRouter → OpenAI"""
    try:
        print("🔍 [FALLBACK DEBUG] Iniciando verificação de provedores de fallback...")
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
        print(f"🔍 [FALLBACK DEBUG] Caminho do arquivo de configuração: {config_path}")
        
        if os.path.exists(config_path):
            print("🔍 [FALLBACK DEBUG] Arquivo de configuração encontrado, carregando...")
            with open(config_path, 'r') as f:
                keys = json.load(f)
            
            print(f"🔍 [FALLBACK DEBUG] Chaves carregadas: {list(keys.keys()) if keys else 'Nenhuma'}")
            
            # Verificar OpenRouter primeiro (fallback secundário preferido)
            openrouter_key = keys.get('openrouter', '')
            print(f"🔍 [FALLBACK DEBUG] Chave OpenRouter: {'Presente' if openrouter_key else 'Ausente'} (tamanho: {len(openrouter_key)})")
            if openrouter_key and len(openrouter_key) > 10:
                print(f"✅ [FALLBACK DEBUG] OpenRouter disponível como fallback secundário (chave: {openrouter_key[:10]}...)")
                add_real_time_log("🔄 OpenRouter disponível como fallback secundário", "info", "fallback")
                return {
                    'provider': 'openrouter',
                    'key': openrouter_key,
                    'available': ['openrouter'],
                    'priority': 2
                }
            else:
                print("❌ [FALLBACK DEBUG] OpenRouter não disponível (chave inválida ou muito curta)")
            
            # Verificar OpenAI como terceira opção (fallback terciário)
            openai_key = keys.get('openai', '')
            print(f"🔍 [FALLBACK DEBUG] Chave OpenAI: {'Presente' if openai_key else 'Ausente'} (tamanho: {len(openai_key)})")
            if openai_key and len(openai_key) > 10:
                print(f"✅ [FALLBACK DEBUG] OpenAI disponível como fallback terciário (chave: {openai_key[:10]}...)")
                add_real_time_log("🔄 OpenAI disponível como fallback terciário", "info", "fallback")
                return {
                    'provider': 'openai',
                    'key': openai_key,
                    'available': ['openai'],
                    'priority': 3
                }
            else:
                print("❌ [FALLBACK DEBUG] OpenAI não disponível (chave inválida ou muito curta)")
        else:
            print("❌ [FALLBACK DEBUG] Arquivo de configuração não encontrado")
                
        print(f"❌ [FALLBACK DEBUG] Nenhum provedor de fallback disponível")
        add_real_time_log("❌ Nenhum provedor de fallback disponível", "error", "fallback")
        return None
        
    except Exception as e:
        print(f"❌ [FALLBACK DEBUG] Erro ao verificar provedores: {e}")
        import traceback
        print(f"❌ [FALLBACK DEBUG] Traceback: {traceback.format_exc()}")
        add_real_time_log(f"❌ Erro ao verificar provedores de fallback: {e}", "error", "fallback")
        return None

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
    """Aplicar throttling mínimo para máxima velocidade"""
    print(f"🔍 DEBUG THROTTLE: Throttling mínimo aplicado")
    
    with RAPIDAPI_THROTTLE['lock']:
        current_time = time.time()
        time_since_last = current_time - RAPIDAPI_THROTTLE['last_request_time']
        
        # Delay mínimo apenas se necessário (máximo 0.5s)
        min_delay = 0.5
        
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            print(f"⏱️ Delay mínimo: {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        RAPIDAPI_THROTTLE['last_request_time'] = time.time()

def handle_rapidapi_429():
    """Lidar com erro 429 (rate limiting) da RapidAPI - VERSÃO OTIMIZADA"""
    with RAPIDAPI_THROTTLE['lock']:
        RAPIDAPI_THROTTLE['consecutive_429s'] += 1
        
        # Aumentar delay adaptativo de forma mais conservadora
        if RAPIDAPI_THROTTLE['consecutive_429s'] == 1:
            RAPIDAPI_THROTTLE['adaptive_delay'] = 10.0  # Primeiro 429: 10s
        elif RAPIDAPI_THROTTLE['consecutive_429s'] == 2:
            RAPIDAPI_THROTTLE['adaptive_delay'] = 20.0  # Segundo 429: 20s
        elif RAPIDAPI_THROTTLE['consecutive_429s'] == 3:
            RAPIDAPI_THROTTLE['adaptive_delay'] = 40.0  # Terceiro 429: 40s
        else:
            RAPIDAPI_THROTTLE['adaptive_delay'] = min(60.0, RAPIDAPI_THROTTLE['adaptive_delay'] * 1.5)  # Máximo 60s
        
        print(f"🚫 Rate limit detectado! Aumentando delay para {RAPIDAPI_THROTTLE['adaptive_delay']}s (429s consecutivos: {RAPIDAPI_THROTTLE['consecutive_429s']})")
        add_real_time_log(f"🚫 Rate limit detectado! Delay aumentado para {RAPIDAPI_THROTTLE['adaptive_delay']}s", "warning", "rapidapi-throttle")

def reset_rapidapi_throttle_success():
    """Resetar throttling após requisição bem-sucedida e incrementar rate limiting global"""
    # Incrementar contador de rate limiting global
    increment_rate_limit()
    
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
    """Obter dados do cache se ainda válidos - VERSÃO SEM LOCK"""
    try:
        print(f"💾 CACHE DEBUG: Iniciando verificação de cache para {endpoint}")
        cache_key = get_cache_key(endpoint, params)
        print(f"💾 CACHE DEBUG: Cache key gerada: {cache_key[:20]}...")
        
        if cache_key in RAPIDAPI_CACHE['data']:
            print(f"💾 CACHE DEBUG: Cache encontrado para {endpoint}")
            timestamp = RAPIDAPI_CACHE['timestamps'].get(cache_key, 0)
            
            # Determinar TTL baseado no tipo de endpoint
            if custom_ttl:
                ttl = custom_ttl
            elif 'channel' in endpoint.lower():
                ttl = RAPIDAPI_CACHE['channel_ttl']  # 2 horas para dados de canal
            elif 'video' in endpoint.lower():
                ttl = RAPIDAPI_CACHE['video_ttl']  # 30 minutos para vídeos
            else:
                ttl = RAPIDAPI_CACHE['ttl']  # 1 hora padrão
            
            current_time = time.time()
            age = current_time - timestamp
            
            print(f"💾 CACHE DEBUG: Age: {age:.0f}s, TTL: {ttl}s")
            
            if age < ttl:
                remaining_time = ttl - age
                print(f"📦 Cache hit para {endpoint} (restam: {remaining_time:.0f}s)")
                return RAPIDAPI_CACHE['data'][cache_key]
            else:
                # Cache expirado, remover
                print(f"💾 CACHE DEBUG: Removendo cache expirado")
                del RAPIDAPI_CACHE['data'][cache_key]
                del RAPIDAPI_CACHE['timestamps'][cache_key]
                print(f"⏰ Cache expirado para {endpoint}")
        else:
            print(f"💾 CACHE DEBUG: Nenhum cache encontrado para {endpoint}")
        
        print(f"💾 CACHE DEBUG: Retornando None para {endpoint}")
        return None
        
    except Exception as e:
        print(f"❌ Erro em get_from_cache: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def save_to_cache(endpoint, params, data, custom_ttl=None):
    """Salvar dados no cache - VERSÃO OTIMIZADA"""
    print(f"🔍 DEBUG: Iniciando save_to_cache para {endpoint}")
    
    try:
        print(f"🔍 DEBUG: Adquirindo lock do cache...")
        with RAPIDAPI_CACHE['lock']:
            print(f"🔍 DEBUG: Lock adquirido, gerando cache_key...")
            cache_key = get_cache_key(endpoint, params)
            print(f"🔍 DEBUG: Cache key gerada: {cache_key[:20]}...")
            
            print(f"🔍 DEBUG: Salvando dados no cache...")
            RAPIDAPI_CACHE['data'][cache_key] = data
            RAPIDAPI_CACHE['timestamps'][cache_key] = time.time()
            print(f"🔍 DEBUG: Dados salvos no cache interno")
            
            # Determinar TTL baseado no tipo de endpoint
            if custom_ttl:
                ttl = custom_ttl
            elif 'channel' in endpoint.lower():
                ttl = RAPIDAPI_CACHE['channel_ttl']  # 2 horas para dados de canal
            elif 'video' in endpoint.lower():
                ttl = RAPIDAPI_CACHE['video_ttl']  # 30 minutos para vídeos
            else:
                ttl = RAPIDAPI_CACHE['ttl']  # 1 hora padrão
                
            print(f"💾 Dados salvos no cache para {endpoint} (TTL: {ttl}s = {ttl/3600:.1f}h)")
            add_real_time_log(f"[CACHE] Cache salvo para {endpoint} (TTL: {ttl/3600:.1f}h)", "info", "rapidapi-cache")
        
        print(f"🔍 DEBUG: Lock liberado, chamando save_persistent_cache...")
        # Salvar cache persistente após cada operação
        save_persistent_cache()
        print(f"🔍 DEBUG: save_to_cache concluído com sucesso para {endpoint}")
        
    except Exception as e:
        print(f"❌ ERRO em save_to_cache: {e}")
        raise

def load_persistent_cache():
    """Carregar cache persistente do arquivo"""
    try:
        cache_file = RAPIDAPI_CACHE['file_path']
        cache_dir = os.path.dirname(cache_file)
        
        # Criar diretório se não existir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            print(f"📁 Diretório de cache criado: {cache_dir}")
            return
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            with RAPIDAPI_CACHE['lock']:
                RAPIDAPI_CACHE['data'] = cache_data.get('data', {})
                RAPIDAPI_CACHE['timestamps'] = cache_data.get('timestamps', {})
            
            # Limpar cache expirado após carregar
            clear_expired_cache()
            
            print(f"📦 Cache persistente carregado: {len(RAPIDAPI_CACHE['data'])} itens")
            add_real_time_log(f"📦 Cache persistente carregado: {len(RAPIDAPI_CACHE['data'])} itens", "info", "rapidapi-cache")
        else:
            print("📦 Arquivo de cache não encontrado, iniciando com cache vazio")
            
    except Exception as e:
        print(f"❌ Erro ao carregar cache persistente: {e}")
        add_real_time_log(f"❌ Erro ao carregar cache persistente: {e}", "error", "rapidapi-cache")

def save_persistent_cache():
    """Salvar cache persistente no arquivo"""
    print(f"🔍 DEBUG: Iniciando save_persistent_cache")
    
    try:
        print(f"🔍 DEBUG: Obtendo caminho do arquivo de cache...")
        cache_file = RAPIDAPI_CACHE['file_path']
        cache_dir = os.path.dirname(cache_file)
        print(f"🔍 DEBUG: Cache file: {cache_file}")
        
        # Criar diretório se não existir
        print(f"🔍 DEBUG: Verificando se diretório existe...")
        if not os.path.exists(cache_dir):
            print(f"🔍 DEBUG: Criando diretório: {cache_dir}")
            os.makedirs(cache_dir)
        
        print(f"🔍 DEBUG: Adquirindo lock para leitura dos dados...")
        with RAPIDAPI_CACHE['lock']:
            print(f"🔍 DEBUG: Lock adquirido, preparando dados...")
            cache_data = {
                'data': RAPIDAPI_CACHE['data'],
                'timestamps': RAPIDAPI_CACHE['timestamps'],
                'saved_at': time.time()
            }
            print(f"🔍 DEBUG: Dados preparados: {len(cache_data['data'])} itens")
        
        print(f"🔍 DEBUG: Lock liberado, abrindo arquivo para escrita...")
        with open(cache_file, 'w', encoding='utf-8') as f:
            print(f"🔍 DEBUG: Arquivo aberto, salvando JSON...")
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
            print(f"🔍 DEBUG: JSON salvo com sucesso")
        
        print(f"💾 Cache persistente salvo: {len(cache_data['data'])} itens")
        add_real_time_log(f"💾 Cache persistente salvo: {len(cache_data['data'])} itens", "info", "rapidapi-cache")
        print(f"🔍 DEBUG: save_persistent_cache concluído com sucesso")
        
    except Exception as e:
        print(f"❌ ERRO em save_persistent_cache: {e}")
        add_real_time_log(f"❌ Erro ao salvar cache persistente: {e}", "error", "rapidapi-cache")
        raise

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
    
    return True

def check_rate_limit():
    """Verificar se pode fazer requisição baseado no rate limiting global"""
    with RAPIDAPI_RATE_LIMIT['lock']:
        current_time = time.time()
        
        # Reset diário
        today = datetime.now().date()
        if RAPIDAPI_RATE_LIMIT['last_reset_date'] != today:
            RAPIDAPI_RATE_LIMIT['total_requests_today'] = 0
            RAPIDAPI_RATE_LIMIT['last_reset_date'] = today
            print("🔄 Reset diário do contador de requisições RapidAPI")
            add_real_time_log("🔄 Reset diário do contador de requisições RapidAPI", "info", "rapidapi-rate-limit")
        
        # Verificar se está em pausa forçada
        if current_time < RAPIDAPI_RATE_LIMIT['pause_until']:
            remaining = int(RAPIDAPI_RATE_LIMIT['pause_until'] - current_time)
            print(f"⏸️ Rate limit ativo: aguardando {remaining}s")
            return False, f"Rate limit ativo. Aguarde {remaining} segundos."
        
        # Reset da janela de minuto
        if current_time - RAPIDAPI_RATE_LIMIT['minute_window_start'] >= 60:
            RAPIDAPI_RATE_LIMIT['requests_per_minute'] = 0
            RAPIDAPI_RATE_LIMIT['minute_window_start'] = current_time
        
        # Reset da janela de hora
        if current_time - RAPIDAPI_RATE_LIMIT['hour_window_start'] >= 3600:
            RAPIDAPI_RATE_LIMIT['requests_per_hour'] = 0
            RAPIDAPI_RATE_LIMIT['hour_window_start'] = current_time
        
        # Verificar limites
        if RAPIDAPI_RATE_LIMIT['requests_per_minute'] >= RAPIDAPI_RATE_LIMIT['max_requests_per_minute']:
            # Pausar até o próximo minuto
            pause_time = 60 - (current_time - RAPIDAPI_RATE_LIMIT['minute_window_start'])
            RAPIDAPI_RATE_LIMIT['pause_until'] = current_time + pause_time
            print(f"🚫 Limite por minuto atingido: pausando por {int(pause_time)}s")
            add_real_time_log(f"🚫 Limite por minuto atingido: pausando por {int(pause_time)}s", "warning", "rapidapi-rate-limit")
            return False, f"Limite de {RAPIDAPI_RATE_LIMIT['max_requests_per_minute']} requisições por minuto atingido."
        
        if RAPIDAPI_RATE_LIMIT['requests_per_hour'] >= RAPIDAPI_RATE_LIMIT['max_requests_per_hour']:
            # Pausar até a próxima hora
            pause_time = 3600 - (current_time - RAPIDAPI_RATE_LIMIT['hour_window_start'])
            RAPIDAPI_RATE_LIMIT['pause_until'] = current_time + pause_time
            print(f"🚫 Limite por hora atingido: pausando por {int(pause_time/60)}min")
            add_real_time_log(f"🚫 Limite por hora atingido: pausando por {int(pause_time/60)}min", "warning", "rapidapi-rate-limit")
            return False, f"Limite de {RAPIDAPI_RATE_LIMIT['max_requests_per_hour']} requisições por hora atingido."
        
        return True, "OK"

def increment_rate_limit():
    """Incrementar contadores de rate limiting após requisição bem-sucedida"""
    with RAPIDAPI_RATE_LIMIT['lock']:
        RAPIDAPI_RATE_LIMIT['requests_per_minute'] += 1
        RAPIDAPI_RATE_LIMIT['requests_per_hour'] += 1
        RAPIDAPI_RATE_LIMIT['total_requests_today'] += 1
        
        print(f"📊 Rate limit: {RAPIDAPI_RATE_LIMIT['requests_per_minute']}/min, {RAPIDAPI_RATE_LIMIT['requests_per_hour']}/h, {RAPIDAPI_RATE_LIMIT['total_requests_today']} hoje")
        add_real_time_log(f"📊 Requisições: {RAPIDAPI_RATE_LIMIT['requests_per_minute']}/min, {RAPIDAPI_RATE_LIMIT['requests_per_hour']}/h", "info", "rapidapi-rate-limit")

def get_rate_limit_status():
    """Obter status atual do rate limiting"""
    with RAPIDAPI_RATE_LIMIT['lock']:
        current_time = time.time()
        
        # Calcular tempo restante nas janelas
        minute_remaining = 60 - (current_time - RAPIDAPI_RATE_LIMIT['minute_window_start'])
        hour_remaining = 3600 - (current_time - RAPIDAPI_RATE_LIMIT['hour_window_start'])
        
        return {
            'requests_per_minute': RAPIDAPI_RATE_LIMIT['requests_per_minute'],
            'max_requests_per_minute': RAPIDAPI_RATE_LIMIT['max_requests_per_minute'],
            'requests_per_hour': RAPIDAPI_RATE_LIMIT['requests_per_hour'],
            'max_requests_per_hour': RAPIDAPI_RATE_LIMIT['max_requests_per_hour'],
            'total_requests_today': RAPIDAPI_RATE_LIMIT['total_requests_today'],
            'minute_window_remaining': max(0, int(minute_remaining)),
            'hour_window_remaining': max(0, int(hour_remaining/60)),
            'is_paused': current_time < RAPIDAPI_RATE_LIMIT['pause_until'],
            'pause_remaining': max(0, int(RAPIDAPI_RATE_LIMIT['pause_until'] - current_time))
        }



# ================================
# 📊 MONITORAMENTO RAPIDAPI
# ================================

@automations_bp.route('/rapidapi-status', methods=['GET'])
def get_rapidapi_status():
    """Obter status atual do RapidAPI incluindo rate limiting"""
    try:
        # Status do rate limiting
        rate_limit_status = get_rate_limit_status()
        
        # Status do throttling
        throttle_status = {
            'adaptive_delay': RAPIDAPI_THROTTLE['adaptive_delay'],
            'min_delay': RAPIDAPI_THROTTLE['min_delay'],
            'consecutive_429s': RAPIDAPI_THROTTLE['consecutive_429s'],
            'last_request_time': RAPIDAPI_THROTTLE['last_request_time']
        }
        
        # Status do cache
        cache_status = {
            'total_items': len(RAPIDAPI_CACHE['data']),
            'ttl_default': RAPIDAPI_CACHE['ttl'],
            'ttl_channel': RAPIDAPI_CACHE['channel_ttl'],
            'ttl_video': RAPIDAPI_CACHE['video_ttl']
        }
        
        # Adicionar informação sobre o método usado
        result_data = {
            'videos': filtered_videos,
            'total_videos': len(filtered_videos),
            'channel_details': channel_details.get('data', {}),
            'extraction_method': 'RapidAPI',
            'extraction_time': f'{extraction_time:.2f}s'
        }
        
        return jsonify({
            'success': True,
            'data': {
                'rate_limit': rate_limit_status,
                'throttle': throttle_status,
                'cache': cache_status,
                'timestamp': time.time()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automations_bp.route('/rapidapi-cache/clear', methods=['POST'])
def clear_rapidapi_cache():
    """Limpar cache do RapidAPI"""
    try:
        with RAPIDAPI_CACHE['lock']:
            items_count = len(RAPIDAPI_CACHE['data'])
            RAPIDAPI_CACHE['data'].clear()
            RAPIDAPI_CACHE['timestamps'].clear()
        
        # Salvar cache vazio
        save_persistent_cache()
        
        print(f"🧹 Cache RapidAPI limpo: {items_count} itens removidos")
        add_real_time_log(f"🧹 Cache RapidAPI limpo: {items_count} itens removidos", "info", "rapidapi-cache")
        
        return jsonify({
            'success': True,
            'message': f'Cache limpo com sucesso. {items_count} itens removidos.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automations_bp.route('/rapidapi-throttle/reset', methods=['POST'])
def reset_rapidapi_throttle():
    """Resetar throttling do RapidAPI"""
    try:
        with RAPIDAPI_THROTTLE['lock']:
            old_delay = RAPIDAPI_THROTTLE['adaptive_delay']
            RAPIDAPI_THROTTLE['adaptive_delay'] = RAPIDAPI_THROTTLE['min_delay']
            RAPIDAPI_THROTTLE['consecutive_429s'] = 0
        
        print(f"🔄 Throttling RapidAPI resetado: {old_delay}s → {RAPIDAPI_THROTTLE['min_delay']}s")
        add_real_time_log(f"🔄 Throttling RapidAPI resetado: {old_delay}s → {RAPIDAPI_THROTTLE['min_delay']}s", "info", "rapidapi-throttle")
        
        return jsonify({
            'success': True,
            'message': f'Throttling resetado de {old_delay}s para {RAPIDAPI_THROTTLE["min_delay"]}s'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# 🧪 TESTE RAPIDAPI
# ================================

@automations_bp.route('/test-rapidapi-manual', methods=['POST'])
def test_rapidapi_manual():
    """Testar conexão com RapidAPI YouTube V2 com chave manual"""
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

        # Testar endpoint de detalhes do canal com delays otimizados
        max_retries = 2
        base_delay = 1  # Delay mínimo: 1 segundo
        
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
    import time
    import threading
    
    # Timeout global usando threading (compatível com Windows)
    extraction_start_time = time.time()
    timeout_occurred = threading.Event()
    
    def timeout_handler():
        time.sleep(120)  # 120 segundos
        timeout_occurred.set()
    
    # Iniciar thread de timeout
    timeout_thread = threading.Thread(target=timeout_handler, daemon=True)
    timeout_thread.start()
    
    try:
        print(f"🚀 Iniciando extração do YouTube às {time.strftime('%H:%M:%S')}")
        print(f"🔍 DEBUG: Iniciando extract_youtube_channel_content")
        
        # Verificar se há dados JSON válidos
        try:
            data = request.get_json()
            if data is None:
                print(f"❌ DEBUG: Dados JSON inválidos ou ausentes")
                return jsonify({
                    'success': False,
                    'error': 'Dados JSON inválidos ou ausentes'
                }), 400
        except Exception as json_error:
            print(f"❌ DEBUG: Erro ao processar JSON: {str(json_error)}")
            return jsonify({
                'success': False,
                'error': f'Erro ao processar JSON: {str(json_error)}'
            }), 400
        
        url = data.get('url', '').strip()
        channel_id_input = data.get('channel_id', '').strip()
        config = data.get('config', {})
        extraction_method = data.get('extraction_method', 'auto')  # auto, rapidapi, ytdlp

        print(f"🔍 DEBUG: Recebida requisição - URL: {url}, Channel ID: {channel_id_input}, Config: {config}, Método: {extraction_method}")
        
        # Priorizar channel_id se fornecido, senão usar url
        input_value = channel_id_input if channel_id_input else url
        input_type = 'channel_id' if channel_id_input else 'url'
        
        print(f"🔍 DEBUG: Usando {input_type}: {input_value}")

        if not input_value:
            print(f"❌ DEBUG: URL ou Channel ID vazio ou ausente")
            return jsonify({
                'success': False,
                'error': 'URL ou ID do canal é obrigatório'
            }), 400

        print(f"🚀 DEBUG EXTRAÇÃO: Iniciando extração do YouTube às {time.strftime('%H:%M:%S')}")
        print(f"📊 DEBUG EXTRAÇÃO: Input type: {input_type}, Input value: {input_value}")
        print(f"⚙️ DEBUG EXTRAÇÃO: Configuração: {config}")
        print(f"🔧 DEBUG EXTRAÇÃO: Método de extração: {extraction_method}")
        
        # Se método for apenas yt-dlp, usar diretamente
        if extraction_method == 'ytdlp':
            print(f"🛡️ Usando yt-dlp diretamente (método selecionado)")
            try:
                ytdlp_result = get_channel_videos_ytdlp(input_value, config.get('max_titles', 10))
                if ytdlp_result.get('success'):
                    # Aplicar filtros se especificados
                    videos = ytdlp_result['data']['videos']
                    if config:
                        videos = filter_videos_by_config(videos, config)
                    
                    # Adicionar informação sobre o método usado
                    result_data = ytdlp_result['data']
                    result_data['extraction_method'] = 'yt-dlp'
                    result_data['videos'] = videos
                    result_data['total_videos'] = len(videos)
                    result_data['extraction_time'] = time.time() - extraction_start_time
                    
                    return jsonify({
                        'success': True,
                        'data': result_data,
                        'message': f'✅ Extração concluída via yt-dlp. {len(videos)} vídeos encontrados.'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Erro no yt-dlp: {ytdlp_result.get("error", "Erro desconhecido")}'
                    }), 400
            except Exception as ytdlp_error:
                return jsonify({
                    'success': False,
                    'error': f'Erro no yt-dlp: {str(ytdlp_error)}'
                }), 400
        
        # Para métodos 'rapidapi' e 'auto', precisamos de chave RapidAPI
        api_key = get_next_rapidapi_key()
        if not api_key and extraction_method == 'rapidapi':
            return jsonify({
                'success': False,
                'error': 'Nenhuma chave RapidAPI disponível. Verifique as configurações.'
            }), 400
        elif not api_key and extraction_method == 'auto':
            # Se não há chave RapidAPI no modo auto, usar yt-dlp diretamente
            print(f"⚠️ Nenhuma chave RapidAPI disponível, usando yt-dlp diretamente")
            try:
                ytdlp_result = get_channel_videos_ytdlp(input_value, config.get('max_titles', 10))
                if ytdlp_result.get('success'):
                    videos = ytdlp_result['data']['videos']
                    if config:
                        videos = filter_videos_by_config(videos, config)
                    
                    result_data = ytdlp_result['data']
                    result_data['extraction_method'] = 'yt-dlp (sem chave RapidAPI)'
                    result_data['videos'] = videos
                    result_data['total_videos'] = len(videos)
                    result_data['extraction_time'] = time.time() - extraction_start_time
                    
                    return jsonify({
                        'success': True,
                        'data': result_data,
                        'message': f'✅ Extração concluída via yt-dlp (sem chave RapidAPI). {len(videos)} vídeos encontrados.'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Erro no yt-dlp: {ytdlp_result.get("error", "Erro desconhecido")}'
                    }), 400
            except Exception as ytdlp_error:
                return jsonify({
                    'success': False,
                    'error': f'Erro no yt-dlp: {str(ytdlp_error)}'
                }), 400
        
        print(f"🔑 DEBUG: Usando chave RapidAPI: {api_key[:10]}...")
        
        # Definir número máximo de tentativas com chaves diferentes
        max_key_attempts = 3
        
        # Determinar se é ID do canal ou URL/nome
        channel_id = None
        channel_name = None

        # Se foi fornecido channel_id diretamente, usar ele
        if input_type == 'channel_id' and input_value.startswith('UC') and len(input_value) == 24:
            channel_id = input_value
            print(f"🔍 DEBUG: Usando ID do canal fornecido diretamente: {channel_id}")
        elif input_value.startswith('UC') and len(input_value) == 24:
            channel_id = input_value
            print(f"🔍 DEBUG: Detectado ID do canal na entrada: {channel_id}")
        else:
            # Tentar extrair ID do canal da URL
            channel_id = extract_channel_id_from_url(input_value, api_key)

            if channel_id:
                print(f"🔍 DEBUG: ID do canal extraído da URL: {channel_id}")
            else:
                # Extrair nome do canal para busca
                channel_name = extract_channel_name_or_id(input_value)
                print(f"🔍 DEBUG: Nome extraído do canal: {channel_name}")

                if not channel_name:
                    return jsonify({
                        'success': False,
                        'error': 'Formato inválido. Use: Nome do canal, @handle, URL completa ou ID do canal'
                    }), 400

                # Verificar timeout antes de buscar ID do canal
                if timeout_occurred.is_set():
                    elapsed_time = time.time() - extraction_start_time
                    print(f"⏱️ TIMEOUT: Operação cancelada durante busca de ID após {elapsed_time:.2f}s")
                    return jsonify({
                        'success': False,
                        'error': '⏱️ Operação cancelada por timeout. A busca do canal está demorando muito.'
                    }), 408
                
                # Obter ID do canal usando a API com rotação de chaves
                print(f"🔍 DEBUG EXTRAÇÃO: Iniciando busca de ID do canal para: {channel_name}")
                print(f"⏱️ DEBUG EXTRAÇÃO: Tempo decorrido até agora: {time.time() - extraction_start_time:.2f}s")
                
                # Tentar até 3 vezes com diferentes chaves se necessário
                channel_id_result = None
                
                for key_attempt in range(max_key_attempts):
                    current_key = get_next_rapidapi_key()
                    if not current_key:
                        return jsonify({
                            'success': False,
                            'error': 'Nenhuma chave RapidAPI disponível'
                        }), 400
                    
                    print(f"🔑 DEBUG: Tentativa {key_attempt + 1} com chave: {current_key[:10]}...")
                    channel_id_result = get_channel_id_rapidapi(channel_name, current_key)
                    
                    if channel_id_result['success']:
                        break
                    elif 'quota' in channel_id_result.get('error', '').lower() or 'monthly' in channel_id_result.get('error', '').lower():
                        print(f"⚠️ Quota excedida para chave {current_key[:10]}..., tentando próxima chave")
                        mark_rapidapi_key_failed(current_key)
                        continue
                    elif 'chave rapidapi inválida' in channel_id_result.get('error', '').lower() or 'sem permissões' in channel_id_result.get('error', '').lower():
                        print(f"🚫 Chave RapidAPI inválida: {current_key[:10]}..., tentando próxima chave")
                        mark_rapidapi_key_failed(current_key)
                        continue
                    else:
                        # Erro não relacionado à quota ou chave inválida, parar tentativas
                        break
        
        print(f"🔍 DEBUG: Resultado da busca do ID: {channel_id_result}")
        
        if not channel_id_result['success']:
            # Se RapidAPI falhou e estamos no modo auto, tentar yt-dlp como fallback
            if extraction_method == 'auto':
                print(f"⚠️ RapidAPI falhou para busca de ID, tentando yt-dlp como fallback...")
                try:
                    ytdlp_result = get_channel_videos_ytdlp(input_value, config.get('max_titles', 10))
                    if ytdlp_result.get('success'):
                        print(f"✅ yt-dlp funcionou como fallback!")
                        # Aplicar filtros se especificados
                        videos = ytdlp_result['data']['videos']
                        if config:
                            videos = filter_videos_by_config(videos, config)
                        
                        # Adicionar informação sobre o método usado
                        result_data = ytdlp_result['data']
                        result_data['extraction_method'] = 'yt-dlp (fallback)'
                        result_data['videos'] = videos
                        result_data['total_videos'] = len(videos)
                        result_data['extraction_time'] = time.time() - extraction_start_time
                        
                        return jsonify({
                            'success': True,
                            'data': result_data,
                            'message': f'✅ Extração concluída via yt-dlp (fallback). {len(videos)} vídeos encontrados.'
                        })
                    else:
                        print(f"❌ yt-dlp também falhou: {ytdlp_result.get('error', 'Erro desconhecido')}")
                except Exception as ytdlp_error:
                    print(f"❌ Erro no fallback yt-dlp: {str(ytdlp_error)}")
            
            return jsonify(channel_id_result), 400
        
        channel_id = channel_id_result['data']['channel_id']
        print(f"🔍 DEBUG: ID do canal obtido: {channel_id}")
        
        # Delay removido para acelerar extração
        print(f"⚡ Delay sequencial removido após get_channel_id_rapidapi")

        # Verificar timeout antes de buscar vídeos
        if timeout_occurred.is_set():
            elapsed_time = time.time() - extraction_start_time
            print(f"⏱️ TIMEOUT: Operação cancelada antes da busca de vídeos após {elapsed_time:.2f}s")
            return jsonify({
                'success': False,
                'error': '⏱️ Operação cancelada por timeout. A busca está demorando muito.'
            }), 408
        
        # Obter vídeos do canal com rotação de chaves
        print(f"🎬 DEBUG EXTRAÇÃO: Iniciando busca de vídeos do canal: {channel_id}")
        print(f"⏱️ DEBUG EXTRAÇÃO: Tempo decorrido até busca de vídeos: {time.time() - extraction_start_time:.2f}s")
        
        # Tentar até 3 vezes com diferentes chaves se necessário
        videos_result = None
        
        for key_attempt in range(max_key_attempts):
            current_key = get_next_rapidapi_key()
            if not current_key:
                return jsonify({
                    'success': False,
                    'error': 'Nenhuma chave RapidAPI disponível para buscar vídeos'
                }), 400
            
            print(f"🔑 DEBUG: Tentativa {key_attempt + 1} para vídeos com chave: {current_key[:10]}...")
            videos_result = get_channel_videos_rapidapi(channel_id, current_key)
            
            if videos_result['success']:
                break
            elif 'quota' in videos_result.get('error', '').lower() or 'monthly' in videos_result.get('error', '').lower():
                print(f"⚠️ Quota excedida para chave {current_key[:10]}..., tentando próxima chave")
                mark_rapidapi_key_failed(current_key)
                continue
            else:
                # Erro não relacionado à quota, parar tentativas
                break
        
        print(f"✅ DEBUG EXTRAÇÃO: Loop de detalhes do canal concluído")
        print(f"⏱️ DEBUG EXTRAÇÃO: Tempo após detalhes do canal: {time.time() - extraction_start_time:.2f}s")
        
        print(f"✅ DEBUG EXTRAÇÃO: Busca de vídeos concluída - Sucesso: {videos_result.get('success', False)}, Total: {len(videos_result.get('data', {}).get('videos', []))}")
        print(f"⏱️ DEBUG EXTRAÇÃO: Tempo decorrido após busca de vídeos: {time.time() - extraction_start_time:.2f}s")
        print(f"🔍 DEBUG EXTRAÇÃO: Continuando para próxima etapa...")
        if not videos_result['success']:
            # Se RapidAPI falhou e estamos no modo auto, tentar yt-dlp como fallback
            if extraction_method == 'auto':
                print(f"⚠️ RapidAPI falhou para busca de vídeos, tentando yt-dlp como fallback...")
                try:
                    ytdlp_result = get_channel_videos_ytdlp(input_value, config.get('max_titles', 10))
                    if ytdlp_result.get('success'):
                        print(f"✅ yt-dlp funcionou como fallback!")
                        # Aplicar filtros se especificados
                        videos = ytdlp_result['data']['videos']
                        if config:
                            videos = filter_videos_by_config(videos, config)
                        
                        # Adicionar informação sobre o método usado
                        result_data = ytdlp_result['data']
                        result_data['extraction_method'] = 'yt-dlp (fallback)'
                        result_data['videos'] = videos
                        result_data['total_videos'] = len(videos)
                        result_data['extraction_time'] = time.time() - extraction_start_time
                        
                        return jsonify({
                            'success': True,
                            'data': result_data,
                            'message': f'✅ Extração concluída via yt-dlp (fallback). {len(videos)} vídeos encontrados.'
                        })
                    else:
                        print(f"❌ yt-dlp também falhou: {ytdlp_result.get('error', 'Erro desconhecido')}")
                except Exception as ytdlp_error:
                    print(f"❌ Erro no fallback yt-dlp: {str(ytdlp_error)}")
            
            return jsonify(videos_result), 400
        
        # Delay removido para acelerar extração
        print(f"⚡ DEBUG EXTRAÇÃO: Delay sequencial removido após get_channel_videos_rapidapi")
        print(f"⏱️ DEBUG EXTRAÇÃO: Tempo total sem delay: {time.time() - extraction_start_time:.2f}s")
        print(f"🔍 DEBUG EXTRAÇÃO: Verificando timeout antes de buscar detalhes do canal...")
        
        # Verificar timeout antes de buscar detalhes do canal
        if timeout_occurred.is_set():
            elapsed_time = time.time() - extraction_start_time
            print(f"⏱️ TIMEOUT: Operação cancelada antes da busca de detalhes após {elapsed_time:.2f}s")
            return jsonify({
                'success': False,
                'error': '⏱️ Operação cancelada por timeout. A busca está demorando muito.'
            }), 408
        
        # Verificar timeout antes de buscar detalhes do canal
        if timeout_occurred.is_set():
            elapsed_time = time.time() - extraction_start_time
            print(f"⏱️ TIMEOUT: Operação cancelada antes da busca de detalhes após {elapsed_time:.2f}s")
            return jsonify({
                'success': False,
                'error': '⏱️ Operação cancelada por timeout. A extração está demorando muito.'
            }), 408
        
        # Obter detalhes do canal com rotação de chaves
        print(f"📋 DEBUG EXTRAÇÃO: Iniciando busca de detalhes do canal: {channel_id}")
        print(f"⏱️ DEBUG EXTRAÇÃO: Tempo decorrido até busca de detalhes: {time.time() - extraction_start_time:.2f}s")
        print(f"🔍 DEBUG EXTRAÇÃO: Entrando no loop de tentativas para detalhes do canal...")
        channel_details = None
        
        for key_attempt in range(max_key_attempts):
            current_key = get_next_rapidapi_key()
            if not current_key:
                # Se não conseguir chave para detalhes, continuar sem eles
                channel_details = {'success': False}
                break
            
            print(f"🔑 DEBUG: Tentativa {key_attempt + 1} para detalhes com chave: {current_key[:10]}...")
            channel_details = get_channel_details_rapidapi(channel_id, current_key)
            
            if channel_details['success']:
                break
            elif 'quota' in channel_details.get('error', '').lower() or 'monthly' in channel_details.get('error', '').lower():
                print(f"⚠️ Quota excedida para chave {current_key[:10]}..., tentando próxima chave")
                mark_rapidapi_key_failed(current_key)
                continue
            else:
                # Erro não relacionado à quota, parar tentativas
                break
        
        # Verificar timeout antes de filtrar vídeos
        if timeout_occurred.is_set():
            elapsed_time = time.time() - extraction_start_time
            print(f"⏱️ TIMEOUT: Operação cancelada antes do filtro após {elapsed_time:.2f}s")
            return jsonify({
                'success': False,
                'error': '⏱️ Operação cancelada por timeout. A extração está demorando muito.'
            }), 408
        
        # Filtrar vídeos baseado na configuração
        print(f"🔧 DEBUG EXTRAÇÃO: Iniciando filtro de vídeos")
        print(f"⏱️ DEBUG EXTRAÇÃO: Tempo decorrido até filtro: {time.time() - extraction_start_time:.2f}s")
        print(f"🔍 DEBUG EXTRAÇÃO: Chamando filter_videos_by_config...")
        original_videos = videos_result['data']['videos']
        print(f"📊 DEBUG EXTRAÇÃO: Vídeos antes do filtro: {len(original_videos)}")
        print(f"⚙️ DEBUG EXTRAÇÃO: Configuração de filtros: {config}")

        filtered_videos = filter_videos_by_config(original_videos, config)
        print(f"✅ DEBUG EXTRAÇÃO: Vídeos após filtro: {len(filtered_videos)}")
        print(f"⏱️ DEBUG EXTRAÇÃO: Tempo decorrido após filtro: {time.time() - extraction_start_time:.2f}s")

        # Verificar timeout antes de retornar
        if timeout_occurred.is_set():
            elapsed_time = time.time() - extraction_start_time
            print(f"⏱️ TIMEOUT GLOBAL: Operação cancelada após {elapsed_time:.2f}s")
            return jsonify({
                'success': False,
                'error': '⏱️ Operação cancelada por timeout global (120s). A extração está demorando muito para responder.'
            }), 408
        
        extraction_time = time.time() - extraction_start_time
        print(f"✅ Extração concluída em {extraction_time:.2f}s às {time.strftime('%H:%M:%S')}")
        
        # Adicionar dados adicionais ao result_data
        result_data.update({
            'channel_id': channel_id,
            'channel_name': channel_details['data']['title'] if channel_details['success'] else (channel_name or channel_id),
            'channel_description': channel_details['data']['description'] if channel_details['success'] else '',
            'total_views': sum(int(video.get('views', 0)) for video in filtered_videos),
            'total_likes': sum(int(video.get('like_count', 0)) for video in filtered_videos)
        })
        
        return jsonify({
            'success': True,
            'data': result_data,
            'message': f'✅ Extração concluída via RapidAPI. {len(filtered_videos)} vídeos encontrados.'
        })
    
    except Exception as e:
        extraction_time = time.time() - extraction_start_time
        print(f"❌ Erro na extração após {extraction_time:.2f}s: {str(e)}")
        
        # Verificar se foi timeout
        if timeout_occurred.is_set():
            return jsonify({
                'success': False,
                'error': '⏱️ Operação cancelada por timeout global (120s). A extração está demorando muito para responder.'
            }), 408
        
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# ================================
# 🎯 GERAÇÃO DE TÍTULOS
# ================================

# ENDPOINT ANTIGO COMENTADO - USAR O NOVO ENDPOINT NA LINHA 2626
# @automations_bp.route('/generate-titles', methods=['POST'])
# def generate_titles_with_ai():
#     """Gerar títulos usando diferentes agentes de IA"""
#     try:
#         data = request.get_json()
#         agent = data.get('agent', 'gemini').lower()
#         api_key = data.get('api_key', '').strip()
#         instructions = data.get('instructions', '').strip()
#         source_titles = data.get('source_titles', [])
#         
#         if not api_key:
#             return jsonify({
#                 'success': False,
#                 'error': f'Chave da API {agent.upper()} é obrigatória'
#             }), 400
#         
#         if not source_titles:
#             return jsonify({
#                 'success': False,
#                 'error': 'Títulos de origem são obrigatórios'
#             }), 400
#         
#         if not instructions:
#             instructions = 'Crie títulos virais e chamativos baseados nos títulos fornecidos.'
#         
#         # Gerar títulos baseado no agente selecionado
#         if agent == 'chatgpt' or agent == 'openai':
#             result = generate_titles_with_openai(source_titles, instructions, api_key)
#         elif agent == 'claude':
#             result = generate_titles_with_claude(source_titles, instructions, api_key)
#         elif agent == 'gemini':
#             result = generate_titles_with_gemini(source_titles, instructions, api_key)
#         elif agent == 'openrouter':
#             result = generate_titles_with_openrouter(source_titles, instructions, api_key)
#         else:
#             return jsonify({
#                 'success': False,
#                 'error': f'Agente {agent} não suportado'
#             }), 400
#         
#         return jsonify(result)
#     
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': f'Erro interno: {str(e)}'
#         }), 500

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
        
        # Para Gemini, usar rotação de chaves se não fornecida
        if not api_key and agent == 'gemini':
            api_key = get_next_gemini_key()
            if not api_key:
                return jsonify({
                    'success': False,
                    'error': 'Nenhuma chave Gemini disponível. Configure pelo menos uma chave nas Configurações.'
                }), 400
            print(f"🔄 Usando rotação de chaves Gemini para generate-premise")
            add_real_time_log(f"🔄 Usando rotação de chaves Gemini para generate-premise", "info", "gemini-rotation")
        elif not api_key:
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
            # Implementar retry automático para Gemini
            result = generate_script_chapters_with_gemini_retry(title, context, num_chapters, api_key)
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

        # Para Gemini, usar rotação de chaves se não fornecida
        if not api_key and agent == 'gemini':
            api_key = get_next_gemini_key()
            if not api_key:
                return jsonify({
                    'success': False,
                    'error': 'Nenhuma chave Gemini disponível. Configure pelo menos uma chave nas Configurações.'
                }), 400
            print(f"🔄 Usando rotação de chaves Gemini para generate-premise")
            add_real_time_log(f"🔄 Usando rotação de chaves Gemini para generate-premise", "info", "gemini-rotation")
        elif not api_key:
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
            agent_prompt = "Crie uma premissa narrativa envolvente e criativa baseada no título e resumo fornecidos. A premissa deve ser clara, interessante e adequada para um vídeo educativo."

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

def generate_premise_with_gemini(title, resume, prompt, api_key=None):
    """Gerar premissa usando Gemini com rotação de chaves e retry automático"""
    import google.generativeai as genai
    
    # Tentar múltiplas chaves se necessário
    max_retries = 3  # Tentar até 3 chaves diferentes
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Se não foi fornecida chave ou tentativa anterior falhou, usar rotação
            if not api_key or attempt > 0:
                api_key = get_next_gemini_key()
                if not api_key:
                    return {
                        'success': False,
                        'error': 'Nenhuma chave Gemini disponível. Configure pelo menos uma chave nas Configurações.'
                    }
                print(f"🔄 Tentativa {attempt + 1}/{max_retries}: Usando rotação de chaves Gemini para premissa")
            
            # Configurar Gemini diretamente
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Criar prompt completo
            full_prompt = f"""
{prompt}

Título: {title}
Resumo: {resume}

Por favor, crie uma premissa narrativa envolvente baseada no título e resumo fornecidos.
"""
            
            # Gerar conteúdo diretamente com Gemini
            response = model.generate_content(full_prompt)
            premise_text = response.text.strip()
            print(f"✅ Sucesso na geração de premissa com Gemini na tentativa {attempt + 1}")
            
            return {
                'success': True,
                'premise': premise_text,
                'title': title,
                'resume': resume
            }
            
        except Exception as e:
            error_str = str(e)
            last_error = error_str
            print(f"❌ Erro na tentativa {attempt + 1}: {error_str}")
            
            # Check if it's a quota error (429)
            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                if attempt < max_retries - 1:  # Not the last attempt
                    print(f"🔄 Erro de quota detectado, tentando próxima chave Gemini...")
                    handle_gemini_429_error(error_str, api_key)
                    api_key = None  # Forçar nova chave na próxima tentativa
                    continue
                else:
                    print("❌ Todas as tentativas de retry falharam")
                    handle_gemini_429_error(error_str, api_key)
            else:
                # For non-quota errors, don't retry
                print(f"❌ Erro não relacionado à quota, parando tentativas: {error_str}")
                break
    
    # Se chegou aqui, todas as tentativas falharam
    final_error = f'Falha na geração de premissa com Gemini após todas as {max_retries} tentativas. Último erro: {last_error}'
    return {
        'success': False,
        'error': final_error
    }

def generate_script_chapters_with_gemini_retry(title, context, num_chapters, api_key=None):
    """Gerar roteiro usando Gemini com rotação de chaves e retry automático"""
    # Tentar múltiplas chaves se necessário
    max_key_attempts = 3  # Tentar até 3 chaves diferentes
    last_error = None
    
    for attempt in range(max_key_attempts):
        try:
            # Se não foi fornecida chave ou tentativa anterior falhou, usar rotação
            if not api_key or attempt > 0:
                api_key = get_next_gemini_key()
                if not api_key:
                    return {
                        'success': False,
                        'error': 'Nenhuma chave Gemini disponível. Configure pelo menos uma chave nas Configurações.'
                    }
                print(f"🔄 Tentativa {attempt + 1}: Usando rotação de chaves Gemini para roteiro")
                add_real_time_log(f"🔄 Tentativa {attempt + 1}: Usando rotação de chaves Gemini para roteiro", "info", "gemini-rotation")
            
            # Chamar função original do ai_services com retry
            result = generate_script_chapters_with_gemini(title, context, num_chapters, api_key)
            
            # Se sucesso, retornar resultado
            if result.get('success'):
                return result
            
            # Se falha, verificar se é erro de quota
            error_str = result.get('error', '')
            last_error = error_str
            print(f"❌ Tentativa {attempt + 1} falhou: {error_str}")
            
            # Se é erro 429 (quota exceeded), tentar próxima chave
            if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
                print(f"🔄 Erro de cota detectado, tentando próxima chave...")
                handle_gemini_429_error(error_str, api_key)
                api_key = None  # Forçar nova chave na próxima tentativa
                continue
            else:
                # Outros erros, não tentar novamente
                print(f"🛑 Erro não relacionado à cota, parando tentativas")
                break
                
        except Exception as e:
            error_str = str(e)
            last_error = error_str
            print(f"❌ Tentativa {attempt + 1} falhou com exceção: {error_str}")
            
            # Se é erro 429 (quota exceeded), tentar próxima chave
            if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
                print(f"🔄 Erro de cota detectado, tentando próxima chave...")
                handle_gemini_429_error(error_str, api_key)
                api_key = None  # Forçar nova chave na próxima tentativa
                continue
            else:
                # Outros erros, não tentar novamente
                print(f"🛑 Erro não relacionado à cota, parando tentativas")
                break
    
    # Se chegou aqui, todas as tentativas falharam
    final_error = f'Todas as {max_key_attempts} chaves Gemini falharam. Último erro: {last_error}'
    return {
        'success': False,
        'error': final_error
    }

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

def convert_to_youtube_url(input_str):
    """Converter nome do canal ou URL incompleta para URL completa do YouTube"""
    import re
    
    input_str = input_str.strip()
    print(f"🔍 DEBUG: Convertendo entrada: '{input_str}'")
    
    # Se já é uma URL completa do YouTube, retornar como está
    if input_str.startswith(('https://www.youtube.com/', 'https://youtube.com/', 'http://www.youtube.com/', 'http://youtube.com/')):
        print(f"✅ URL completa detectada: {input_str}")
        return input_str
    
    # Se é um ID de canal (UC...)
    if input_str.startswith('UC') and len(input_str) == 24:
        url = f"https://www.youtube.com/channel/{input_str}"
        print(f"🆔 ID do canal convertido para: {url}")
        return url
    
    # Se contém apenas o nome do canal (ex: 'MrBeast', '@MrBeast')
    # Remover @ se presente
    channel_name = input_str.lstrip('@')
    
    # Verificar se é um nome de canal válido (apenas letras, números, underscore, hífen)
    if re.match(r'^[a-zA-Z0-9_-]+$', channel_name):
        # Tentar formato @username primeiro (mais moderno)
        url = f"https://www.youtube.com/@{channel_name}"
        print(f"📺 Nome do canal convertido para: {url}")
        return url
    
    # Se não conseguiu processar, tentar como está
    print(f"⚠️ Não foi possível processar '{input_str}', usando como está")
    return input_str

def get_channel_id_from_handle(handle, api_key):
    """Converter handle (@MrBeast) em channel ID usando YouTube API"""
    try:
        from googleapiclient.discovery import build
        
        # Remover @ se presente
        handle = handle.lstrip('@')
        
        # Construir serviço YouTube API
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Buscar canal por handle
        search_response = youtube.search().list(
            q=handle,
            type='channel',
            part='id,snippet',
            maxResults=5
        ).execute()
        
        # Procurar canal que corresponde exatamente ao handle
        for item in search_response.get('items', []):
            channel_title = item['snippet']['title'].lower()
            if handle.lower() in channel_title or channel_title in handle.lower():
                return item['id']['channelId']
        
        # Se não encontrou correspondência exata, tentar o primeiro resultado
        if search_response.get('items'):
            return search_response['items'][0]['id']['channelId']
            
        return None
        
    except Exception as e:
        print(f"❌ Erro ao buscar channel ID para handle {handle}: {e}")
        return None

def extract_channel_id_from_url(url, api_key=None):
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

    # Para handles (@handle), tentar converter usando RapidAPI
    if api_key:
        # Extrair handle da URL ou usar diretamente
        handle_patterns = [
            r'youtube\.com/@([^/?&\s]+)',
            r'^@([^/?&\s]+)$',
            r'^([^/?&\s@]+)$'  # Nome simples como 'MrBeast'
        ]
        
        for pattern in handle_patterns:
            match = re.search(pattern, url)
            if match:
                handle = match.group(1)
                print(f"🔍 Tentando converter handle '{handle}' em channel ID usando RapidAPI...")
                # Usar RapidAPI para converter handle em channel ID
                result = get_channel_id_rapidapi(handle, api_key)
                if result and result.get('success'):
                    channel_id = result['data']['channel_id']
                    print(f"✅ Handle '{handle}' convertido para channel ID: {channel_id}")
                    return channel_id
                else:
                    print(f"❌ Erro ao converter handle '{handle}': {result.get('error', 'Erro desconhecido')}")
                break
    
    # Se não conseguiu converter, retornar None
    print(f"❌ Não foi possível extrair channel ID de: {url}")
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
        print(f"🔑 SELEÇÃO: Determinando qual chave usar...")
        current_api_key = api_key
        if not current_api_key or len(RAPIDAPI_KEYS_ROTATION['keys']) > 1:
            print(f"🔄 ROTAÇÃO: Obtendo próxima chave da rotação")
            rotation_key = get_next_rapidapi_key()
            if rotation_key:
                current_api_key = rotation_key
                print(f"✅ ROTAÇÃO: Usando chave da rotação: {current_api_key[:20]}...")
            else:
                print(f"❌ ROTAÇÃO: Nenhuma chave disponível na rotação")
        else:
            print(f"✅ FORNECIDA: Usando chave fornecida: {current_api_key[:20]}...")
        
        if not current_api_key:
            print(f"❌ ERRO: Nenhuma chave API disponível")
            return {
                'success': False,
                'error': 'Nenhuma chave RapidAPI disponível'
            }

        headers = {
            "X-RapidAPI-Key": current_api_key,
            "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
        }

        params = {"channel_name": channel_name}

        print(f"🔍 DEBUG: Buscando ID do canal para: {channel_name}")
        print(f"🔍 DEBUG: URL: {url}")
        print(f"🔍 DEBUG: Params: {params}")

        # Retry otimizado com delays mínimos
        max_retries = 2  # Máximo 2 tentativas
        base_delay = 1   # Delay mínimo: 1 segundo
        
        for attempt in range(max_retries):
            try:
                # Aplicar throttling inteligente antes da requisição
                apply_rapidapi_throttle()
                
                # Adicionar delay entre tentativas para evitar rate limiting
                if attempt > 0:
                    delay = base_delay * (2 ** (attempt - 1))  # Backoff mais conservador (2x)
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
                    
                # Verificar se é erro 403 (Forbidden) - chave inválida
                elif response.status_code == 403:
                    print(f"🚫 Chave RapidAPI inválida ou sem permissões: {current_api_key[:20]}...")
                    mark_rapidapi_key_failed(current_api_key)
                    
                    # Tentar obter nova chave da rotação
                    new_key = get_next_rapidapi_key()
                    if new_key and new_key != current_api_key:
                        current_api_key = new_key
                        headers["X-RapidAPI-Key"] = current_api_key
                        print(f"🔄 Tentando com nova chave após 403: {current_api_key[:20]}...")
                        continue
                    else:
                        return {
                            'success': False,
                            'error': 'Todas as chaves RapidAPI estão inválidas ou sem permissões. Verifique suas chaves na configuração.'
                        }
                    
                # Se chegou aqui com status 200, sair do loop
                if response.status_code == 200:
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
                error_msg = 'Limite de requisições excedido (100/mês ou 1000/hora). Aguarde alguns minutos e tente novamente.'
            elif response.status_code == 401:
                error_msg = 'Chave de API inválida ou expirada. Verifique suas chaves RapidAPI.'
            elif response.status_code == 403:
                error_msg = 'Chave RapidAPI inválida ou sem permissões. Todas as chaves configuradas estão com problema. Verifique suas chaves na configuração.'
            elif response.status_code == 404:
                error_msg = 'Canal não encontrado. Verifique o nome do canal.'
            else:
                error_msg = f'Erro na API RapidAPI: {response.status_code} - {response.text}'
                
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

        # Retry otimizado com delays mínimos
        max_retries = 2  # Máximo 2 tentativas
        base_delay = 1   # Delay mínimo: 1 segundo
        
        for attempt in range(max_retries):
            # Aplicar throttling inteligente antes da requisição
            apply_rapidapi_throttle()
            
            if attempt > 0:
                delay = base_delay * (2 ** (attempt - 1))  # Backoff mais conservador (2x)
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
                        'error': 'Limite de requisições excedido (429). Tente novamente em alguns minutos.'
                    }
                print(f"⚠️ Rate limit atingido (429), tentando novamente...")
                continue
                
            # Verificar se é erro 403 (Forbidden) - chave inválida
            elif response.status_code == 403:
                print(f"🚫 Chave RapidAPI inválida ou sem permissões: {current_api_key[:20]}...")
                mark_rapidapi_key_failed(current_api_key)
                
                # Tentar obter nova chave da rotação
                new_key = get_next_rapidapi_key()
                if new_key and new_key != current_api_key:
                    current_api_key = new_key
                    headers["X-RapidAPI-Key"] = current_api_key
                    print(f"🔄 Tentando com nova chave após 403: {current_api_key[:20]}...")
                    continue
                else:
                    return {
                        'success': False,
                        'error': 'Todas as chaves RapidAPI estão inválidas ou sem permissões. Verifique suas chaves na configuração.'
                    }
            
            # Se chegou aqui com status 200, sair do loop
            if response.status_code == 200:
                # Resetar throttling após sucesso
                reset_rapidapi_throttle_success()
                break

        if response.status_code != 200:
            if response.status_code == 429:
                error_msg = 'Limite de requisições excedido (100/mês ou 1000/hora). Aguarde alguns minutos e tente novamente.'
            elif response.status_code == 401:
                error_msg = 'Chave de API inválida ou expirada. Verifique suas chaves RapidAPI.'
            elif response.status_code == 403:
                error_msg = 'Chave RapidAPI inválida ou sem permissões. Todas as chaves configuradas estão com problema. Verifique suas chaves na configuração.'
            elif response.status_code == 404:
                error_msg = 'Canal não encontrado. Verifique o ID do canal.'
            else:
                error_msg = f'Erro na API RapidAPI: {response.status_code}'
                
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
    """Obter vídeos do canal usando RapidAPI YouTube V2 - versão simplificada"""
    import time
    import requests
    
    try:
        print(f"🚀 INÍCIO: get_channel_videos_rapidapi chamada com channel_id={channel_id}, max_results={max_results}")
        print(f"🔑 API Key fornecida: {'Sim' if api_key else 'Não'} (length: {len(api_key) if api_key else 0})")
        
        # Verificar cache primeiro
        print(f"💾 CACHE: Verificando cache para channel_id={channel_id}")
        cache_params = {
            'channel_id': channel_id,
            'max_results': min(max_results, 50)
        }
        cached_result = get_from_cache('channel_videos', cache_params, custom_ttl=600)  # Cache por 10 minutos
        if cached_result:
            print(f"✅ CACHE: Resultado encontrado no cache, retornando dados salvos")
            return cached_result
        
        print(f"❌ CACHE: Nenhum resultado no cache, prosseguindo com requisição à API")
        
        # Limpar cache expirado
        print(f"🧹 CACHE: Limpando cache expirado")
        clear_expired_cache()
        
        # Usar chave fornecida ou obter da rotação
        current_api_key = api_key
        if not current_api_key:
            load_rapidapi_keys()
            current_api_key = get_next_rapidapi_key()
        
        if not current_api_key:
            print(f"❌ ERRO: Nenhuma chave RapidAPI disponível")
            return {
                'success': False,
                'error': 'Nenhuma chave RapidAPI disponível'
            }
        
        print(f"🔑 CHAVE: Usando chave: {current_api_key[:20]}...")
        
        # Fazer requisição HTTP direta (similar ao endpoint debug-extract-simple que funcionou)
        url = "https://youtube-v2.p.rapidapi.com/channel/videos"
        headers = {
            "X-RapidAPI-Key": current_api_key,
            "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
        }
        params = {
            "channel_id": channel_id,
            "max_results": min(max_results, 50)
        }
        
        print(f"📡 REQUISIÇÃO: Fazendo requisição para {url}")
        print(f"📋 PARÂMETROS: {params}")
        
        start_time = time.time()
        response = requests.get(url, headers=headers, params=params, timeout=30)
        elapsed_time = time.time() - start_time
        
        print(f"✅ RESPOSTA: Requisição concluída em {elapsed_time:.2f}s")
        print(f"📊 STATUS: {response.status_code}")
        print(f"📏 TAMANHO: {len(response.content)} bytes")
        
        # Verificar se a resposta foi bem-sucedida
        if response.status_code != 200:
            print(f"❌ ERRO: Status {response.status_code}: {response.text[:200]}")
            return {
                'success': False,
                'error': f'Erro na API RapidAPI ({response.status_code}): {response.text[:200]}'
            }
        
        # Parse da resposta JSON
        print(f"📄 JSON: Iniciando parse da resposta JSON")
        try:
            data = response.json()
            print(f"✅ JSON: Parse bem-sucedido")
            print(f"📊 JSON: Tamanho dos dados: {len(str(data))} caracteres")
            print(f"🔑 JSON: Chaves principais: {list(data.keys()) if isinstance(data, dict) else 'Não é dict'}")
        except Exception as e:
            print(f"❌ JSON: Falha no parse da resposta")
            print(f"❌ JSON: Erro: {str(e)}")
            print(f"❌ JSON: Tipo da resposta: {type(response.content)}")
            print(f"❌ JSON: Primeiros 200 chars: {response.text[:200]}")
            return {
                'success': False,
                'error': f'Falha ao processar resposta JSON: {str(e)}'
            }

        print(f"\n🔍 VALIDAÇÃO: Verificando estrutura dos dados")
        if 'videos' not in data:
            print(f"❌ VALIDAÇÃO: Chave 'videos' não encontrada")
            print(f"🔑 VALIDAÇÃO: Chaves disponíveis na resposta: {list(data.keys())}")
            # Verificar se há erro na resposta da API
            if 'error' in data:
                print(f"❌ VALIDAÇÃO: Erro da API encontrado: {data['error']}")
                return {
                    'success': False,
                    'error': f'Erro da API RapidAPI: {data["error"]}'
                }
            print(f"❌ VALIDAÇÃO: Nenhum vídeo encontrado - estrutura inesperada")
            return {
                'success': False,
                'error': 'Nenhum vídeo encontrado no canal - verifique se o ID do canal está correto'
            }
        
        print(f"✅ VALIDAÇÃO: Chave 'videos' encontrada")

        print(f"🔍 DEBUG: Encontrados {len(data['videos'])} vídeos na resposta")
        print(f"✅ PROGRESSO: {len(data['videos'])} vídeos encontrados, iniciando processamento...")

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
        
        print(f"🎉 PROGRESSO: Processamento concluído com sucesso!")
        print(f"📊 PROGRESSO: Total de vídeos processados: {len(videos)}")
        
        # Salvar no cache para evitar chamadas futuras
        save_to_cache('channel_videos', cache_params, result, custom_ttl=600)
        
        return result

    except Exception as e:
        print(f"❌ PROGRESSO: Erro durante busca de vídeos: {str(e)}")
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
    if max_views is not None and max_views > 0:
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

def get_channel_videos_youtube_api(channel_id, api_key, max_results=50):
    """Obter vídeos do canal usando YouTube Data API v3 oficial"""
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        import isodate
        from datetime import datetime
        
        print(f"🚀 INÍCIO: get_channel_videos_youtube_api chamada com channel_id={channel_id}, max_results={max_results}")
        print(f"🔑 API Key fornecida: {'Sim' if api_key else 'Não'} (length: {len(api_key) if api_key else 0})")
        
        if not api_key:
            return {
                'success': False,
                'error': 'Chave da YouTube API é obrigatória'
            }
        
        # Verificar cache primeiro
        cache_params = {
            'channel_id': channel_id,
            'max_results': min(max_results, 50),
            'api_type': 'youtube_official'
        }
        cached_result = get_from_cache('channel_videos_youtube', cache_params, custom_ttl=600)
        if cached_result:
            print(f"✅ CACHE: Resultado encontrado no cache, retornando dados salvos")
            return cached_result
        
        # Construir serviço da YouTube API
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Buscar vídeos do canal
        search_response = youtube.search().list(
            part='id,snippet',
            channelId=channel_id,
            type='video',
            order='date',
            maxResults=min(max_results, 50)
        ).execute()
        
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        
        if not video_ids:
            return {
                'success': False,
                'error': 'Nenhum vídeo encontrado no canal'
            }
        
        # Obter estatísticas detalhadas dos vídeos
        videos_response = youtube.videos().list(
            part='statistics,contentDetails,snippet',
            id=','.join(video_ids)
        ).execute()
        
        videos = []
        for video in videos_response['items']:
            # Converter duração ISO 8601 para formato legível
            duration_iso = video['contentDetails']['duration']
            duration = isodate.parse_duration(duration_iso)
            duration_str = str(duration).replace('0:', '')
            
            # Processar dados do vídeo
            processed_video = {
                'video_id': video['id'],
                'title': video['snippet']['title'],
                'description': video['snippet']['description'][:500],  # Limitar descrição
                'thumbnail': video['snippet']['thumbnails'].get('high', {}).get('url', ''),
                'duration': duration_str,
                'views': int(video['statistics'].get('viewCount', 0)),
                'likes': int(video['statistics'].get('likeCount', 0)),
                'published_at': video['snippet']['publishedAt'],
                'url': f"https://youtube.com/watch?v={video['id']}"
            }
            videos.append(processed_video)
        
        result = {
            'success': True,
            'data': {
                'videos': videos,
                'total_videos': len(videos),
                'total_count': len(videos),
                'message': f'✅ {len(videos)} títulos extraídos com sucesso via YouTube API oficial!'
            }
        }
        
        # Salvar no cache
        save_to_cache('channel_videos_youtube', cache_params, result, custom_ttl=600)
        
        print(f"🎉 PROGRESSO: YouTube API - {len(videos)} vídeos processados com sucesso!")
        return result
        
    except HttpError as e:
        error_msg = f'Erro da YouTube API: {str(e)}'
        print(f"❌ ERRO YouTube API: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = f'Erro ao buscar vídeos via YouTube API: {str(e)}'
        print(f"❌ ERRO: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }

def get_channel_videos_ytdlp(channel_url, max_results=50):
    """Obter vídeos do canal usando yt-dlp"""
    try:
        import yt_dlp
        
        print(f"🚀 INÍCIO: get_channel_videos_ytdlp chamada com channel_url={channel_url}, max_results={max_results}")
        
        # Converter nome do canal para URL completa se necessário
        processed_url = convert_to_youtube_url(channel_url)
        print(f"🔗 URL processada: {processed_url}")
        
        # Verificar cache primeiro
        cache_params = {
            'channel_url': processed_url,
            'max_results': min(max_results, 50),
            'api_type': 'ytdlp'
        }
        cached_result = get_from_cache('channel_videos_ytdlp', cache_params, custom_ttl=600)
        if cached_result:
            print(f"✅ CACHE: Resultado encontrado no cache, retornando dados salvos")
            return cached_result
        
        # Configurar yt-dlp para extrair vídeos do canal
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',  # Extrair metadados da playlist diretamente
            'playlistend': min(max_results, 50),
            'ignoreerrors': True,
            'socket_timeout': 20,
            'retries': 1,
        }
        
        # Garantir que estamos acessando a página de vídeos do canal
        if processed_url.startswith('https://www.youtube.com/@'):
            # Se já é um handle, adicionar /videos
            if not processed_url.endswith('/videos'):
                processed_url = f"{processed_url}/videos"
        elif processed_url.startswith('@'):
            # Converter handle para URL completa
            channel_name = processed_url.lstrip('@')
            processed_url = f"https://www.youtube.com/@{channel_name}/videos"
        elif 'youtube.com/channel/' in processed_url:
            # Se é channel ID, adicionar /videos
            if not processed_url.endswith('/videos'):
                processed_url = f"{processed_url}/videos"
        
        possible_urls = [processed_url]
        print(f"🔍 DEBUG: URL final para extração: {processed_url}")
        
        # Extrair informações do canal
        print(f"🔍 DEBUG: Criando instância YoutubeDL com opts: {ydl_opts}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            channel_info = None
            last_error = None
            
            for i, url in enumerate(possible_urls):
                try:
                    print(f"🔄 Tentando URL {i+1}/{len(possible_urls)}: {url}")
                    print(f"🔍 DEBUG: Iniciando extract_info para {url}...")
                    
                    # Usar timeout manual com threading
                    import threading
                    import time
                    
                    try:
                        print(f"🔍 DEBUG: Iniciando extract_info diretamente para {url}")
                        channel_info = ydl.extract_info(url, download=False)
                        print(f"🔍 DEBUG: extract_info concluído com sucesso")
                    except Exception as e:
                        print(f"❌ Erro em extract_info: {str(e)}")
                        last_error = str(e)
                        continue
                    
                    # Handle channel redirect to playlist
                    if channel_info and channel_info.get('_type') == 'url':
                        playlist_url = channel_info['url']
                        print(f"🔄 Detectado redirecionamento para playlist: {playlist_url}")
                        try:
                            channel_info = ydl.extract_info(playlist_url, download=False)
                            print(f"🔍 DEBUG: extract_info da playlist concluído com sucesso")
                        except Exception as e:
                            print(f"❌ Erro ao extrair playlist: {str(e)}")
                            last_error = str(e)
                            continue
                    
                    if channel_info and 'entries' in channel_info:
                        print(f"✅ Sucesso com URL: {url}")
                        break
                    else:
                        print(f"⚠️ URL {url} não retornou entries válidas")
                        
                except Exception as e:
                    last_error = str(e)
                    print(f"❌ Tentativa falhou para URL {url}: {last_error}")
                    continue
            
            if channel_info:
                print(f"DEBUG: Channel info type: {channel_info.get('_type')}")
                print(f"DEBUG: Keys in channel_info: {list(channel_info.keys())}")
                print(f"DEBUG: Has entries: {'entries' in channel_info}")
                print(f"DEBUG: Number of entries: {len(channel_info.get('entries', []))}")
            if not channel_info or 'entries' not in channel_info:
                error_msg = f'Não foi possível extrair informações do canal. Último erro: {last_error}'
                print(f"❌ ERRO: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
            
            videos = []
            entries_list = list(channel_info['entries'])[:max_results]
            print(f"📊 Processando {len(entries_list)} entradas...")
            
            for i, entry in enumerate(entries_list):
                if not entry:  # Pular entradas vazias
                    print(f"  ⚠️ Entrada {i+1} vazia, pulando...")
                    continue
                
                try:
                    print(f"  🔄 Processando entrada {i+1}/{len(entries_list)}...")
                    print(f"  🔍 DEBUG: Dados da entrada: {entry}")
                    
                    # Com extract_flat=True, os dados vêm em formato diferente
                    title = entry.get('title', '') if entry.get('title') else ''
                    video_id = entry.get('id', '')
                    
                    # Para extract_flat, precisamos extrair informações adicionais se necessário
                    if not title and entry.get('url'):
                        # Se não temos título, tentar extrair da URL
                        title = f"Vídeo {video_id}"
                    
                    processed_video = {
                        'video_id': video_id,
                        'title': title,
                        'description': entry.get('description', '')[:500] if entry.get('description') else '',
                        'thumbnail': entry.get('thumbnail', ''),
                        'duration': str(entry.get('duration', 0)) + 's' if entry.get('duration') else '',
                        'views': entry.get('view_count', 0) or 0,
                        'likes': entry.get('like_count', 0) or 0,
                        'published_at': entry.get('upload_date', ''),
                        'url': entry.get('url', f"https://youtube.com/watch?v={video_id}")
                    }
                    
                    videos.append(processed_video)
                    print(f"  ✅ Entrada {i+1} processada: {title[:50]}...")
                    
                except Exception as e:
                    print(f"  ❌ Erro na entrada {i+1}: {str(e)[:100]}...")
                    continue
            
            result = {
                'success': True,
                'data': {
                    'videos': videos,
                    'total_videos': len(videos),
                    'total_count': len(videos),
                    'message': f'✅ {len(videos)} títulos extraídos com sucesso via yt-dlp!'
                }
            }
            
            # Salvar no cache
            save_to_cache('channel_videos_ytdlp', cache_params, result, custom_ttl=600)
            
            print(f"🎉 PROGRESSO: yt-dlp - {len(videos)} vídeos processados com sucesso!")
            return result
            
    except ImportError:
        error_msg = 'yt-dlp não está instalado'
        print(f"❌ ERRO: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = f'Erro ao buscar vídeos via yt-dlp: {str(e)}'
        print(f"❌ ERRO: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }

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

        # Carregar chaves de API - priorizar as enviadas pelo frontend
        api_keys = data.get('api_keys', {})
        
        # Se não foram enviadas chaves pelo frontend, carregar do arquivo
        if not api_keys:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
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

        gemini_key = api_keys.get('gemini') or api_keys.get('gemini_1')
        if gemini_key:
            gemini_configured = title_generator.configure_gemini(gemini_key)

        if api_keys.get('openrouter'):
            openrouter_configured = title_generator.configure_openrouter(api_keys['openrouter'])

        if not openai_configured and not gemini_configured and not openrouter_configured:
            return jsonify({
                'success': False,
                'error': 'Nenhuma IA configurada. Configure OpenAI, Gemini ou OpenRouter nas configurações.'
            }), 400

        print(f"🤖 Gerando títulos sobre '{topic}' baseado em {len(source_titles)} títulos de referência")

        # Gerar títulos baseado no provider escolhido com fallback automático
        results = None
        
        if ai_provider == 'openai' and openai_configured:
            try:
                generated_titles = title_generator.generate_titles_openai(source_titles, topic, count, style)
                results = {
                    'generated_titles': generated_titles,
                    'ai_provider_used': 'openai',
                    'patterns_analysis': title_generator.analyze_viral_patterns(source_titles)
                }
                add_real_time_log("✅ Títulos gerados com OpenAI", "info", "titles-openai")
            except Exception as e:
                error_msg = str(e).lower()
                if '429' in error_msg or 'quota' in error_msg or 'insufficient_quota' in error_msg:
                    add_real_time_log(f"⚠️ OpenAI quota excedida, tentando Gemini como fallback: {e}", "warning", "titles-fallback")
                    if gemini_configured:
                        try:
                            generated_titles = title_generator.generate_titles_gemini(source_titles, topic, count, style)
                            results = {
                                'generated_titles': generated_titles,
                                'ai_provider_used': 'gemini (fallback)',
                                'patterns_analysis': title_generator.analyze_viral_patterns(source_titles)
                            }
                            add_real_time_log("✅ Títulos gerados com Gemini (fallback)", "info", "titles-gemini-fallback")
                        except Exception as gemini_error:
                            add_real_time_log(f"❌ Gemini fallback também falhou: {gemini_error}", "error", "titles-fallback-failed")
                            raise e  # Re-raise o erro original do OpenAI
                    else:
                        add_real_time_log("❌ Gemini não configurado para fallback", "error", "titles-no-fallback")
                        raise e
                else:
                    add_real_time_log(f"❌ Erro OpenAI (não quota): {e}", "error", "titles-openai-error")
                    raise e
        elif ai_provider == 'gemini' and gemini_configured:
            generated_titles = title_generator.generate_titles_gemini(source_titles, topic, count, style)
            results = {
                'generated_titles': generated_titles,
                'ai_provider_used': 'gemini',
                'patterns_analysis': title_generator.analyze_viral_patterns(source_titles)
            }
            add_real_time_log("✅ Títulos gerados com Gemini", "info", "titles-gemini")
        else:
            # Modo automático - tentar OpenAI primeiro, depois Gemini se falhar
            if openai_configured:
                try:
                    results = title_generator.generate_titles_hybrid(source_titles, topic, count, style)
                    add_real_time_log("✅ Títulos gerados com modo híbrido (OpenAI)", "info", "titles-hybrid")
                except Exception as e:
                    error_msg = str(e).lower()
                    if ('429' in error_msg or 'quota' in error_msg or 'insufficient_quota' in error_msg) and gemini_configured:
                        add_real_time_log(f"⚠️ Modo híbrido falhou (quota), tentando Gemini: {e}", "warning", "titles-hybrid-fallback")
                        try:
                            generated_titles = title_generator.generate_titles_gemini(source_titles, topic, count, style)
                            results = {
                                'generated_titles': generated_titles,
                                'ai_provider_used': 'gemini (auto-fallback)',
                                'patterns_analysis': title_generator.analyze_viral_patterns(source_titles)
                            }
                            add_real_time_log("✅ Títulos gerados com Gemini (auto-fallback)", "info", "titles-auto-fallback")
                        except Exception as gemini_error:
                            add_real_time_log(f"❌ Auto-fallback para Gemini falhou: {gemini_error}", "error", "titles-auto-fallback-failed")
                            raise e
                    else:
                        raise e
            elif gemini_configured:
                # Se só Gemini estiver configurado
                generated_titles = title_generator.generate_titles_gemini(source_titles, topic, count, style)
                results = {
                    'generated_titles': generated_titles,
                    'ai_provider_used': 'gemini (only available)',
                    'patterns_analysis': title_generator.analyze_viral_patterns(source_titles)
                }
                add_real_time_log("✅ Títulos gerados com Gemini (única opção)", "info", "titles-gemini-only")
            else:
                # Usar híbrido como último recurso
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
        script_size = data.get('script_size', 'medio')  # 'curto', 'medio', 'longo'

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

        gemini_key = api_keys.get('gemini') or api_keys.get('gemini_1')
        if gemini_key:
            gemini_configured = title_generator.configure_gemini(gemini_key)

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
            ai_provider,
            script_size
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
            error_response = format_error_response('validation_error', 'Arquivo de áudio não encontrado', 'Servidor de Áudio')
            return jsonify(error_response), 404

    except Exception as e:
        print(f"❌ Erro ao servir áudio: {str(e)}")
        add_real_time_log(f"❌ Erro ao servir áudio: {str(e)}", "error", "audio-server")
        error_response = auto_format_error(str(e), 'Servidor de Áudio')
        return jsonify(error_response), 500

@automations_bp.route('/video/<filename>')
def serve_video(filename):
    """Servir arquivos de vídeo gerados"""
    try:
        import os
        from flask import send_file

        # Verificar em múltiplos diretórios onde os vídeos podem estar
        possible_dirs = [
            os.path.join(os.path.dirname(__file__), '..', 'temp'),
            os.path.join(os.path.dirname(__file__), '..', 'outputs'),
            os.path.join(os.path.dirname(__file__), '..', 'temp', 'videos')
        ]
        
        filepath = None
        for temp_dir in possible_dirs:
            potential_path = os.path.join(temp_dir, filename)
            if os.path.exists(potential_path):
                filepath = potential_path
                break

        print(f"🔍 Tentando servir vídeo: {filename}")
        add_real_time_log(f"🔍 Servindo vídeo: {filename}", "info", "video-server")

        if filepath and os.path.exists(filepath):
            print(f"✅ Arquivo encontrado, servindo: {filename}")
            add_real_time_log(f"✅ Vídeo servido com sucesso: {filename}", "success", "video-server")
            return send_file(filepath, as_attachment=False, mimetype='video/mp4')
        else:
            print(f"❌ Arquivo não encontrado: {filename}")
            add_real_time_log(f"❌ Arquivo de vídeo não encontrado: {filename}", "error", "video-server")
            error_response = format_error_response('validation_error', 'Arquivo de vídeo não encontrado', 'Servidor de Vídeo')
            return jsonify(error_response), 404

    except Exception as e:
        print(f"❌ Erro ao servir vídeo: {str(e)}")
        add_real_time_log(f"❌ Erro ao servir vídeo: {str(e)}", "error", "video-server")
        error_response = auto_format_error(str(e), 'Servidor de Vídeo')
        return jsonify(error_response), 500

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
        import numpy as np
        import soundfile as sf
        import subprocess
        import tempfile

        temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')

        # Verificar se temos segmentos válidos
        valid_files = []
        total_size = 0

        for segment in sorted(segments, key=lambda x: x.get('index', 0)):
            filename = segment.get('filename')
            if not filename:
                continue

            filepath = os.path.join(temp_dir, filename)
            if not os.path.exists(filepath):
                print(f"⚠️ Arquivo não encontrado: {filepath}")
                continue

            valid_files.append(filepath)
            total_size += os.path.getsize(filepath)
            print(f"✅ Arquivo válido encontrado: {filename}")

        if not valid_files:
            return {
                'success': False,
                'error': 'Nenhum segmento de áudio válido encontrado'
            }

        # Usar ffmpeg para concatenar os arquivos (mais eficiente e compatível)
        timestamp = int(time.time())
        final_filename = f"audio_final_{timestamp}.mp3"
        final_filepath = os.path.join(temp_dir, final_filename)

        # Criar arquivo de lista para ffmpeg
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for filepath in valid_files:
                # Escapar aspas no caminho do arquivo
                escaped_path = filepath.replace('\\', '/').replace("'", "'\"'\"'")
                f.write(f"file '{escaped_path}'\n")
            list_file = f.name

        try:
            # Comando ffmpeg para concatenar
            cmd = [
                'ffmpeg', '-y',  # -y para sobrescrever arquivo existente
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',  # Copiar streams sem recodificar
                final_filepath
            ]

            print(f"🔗 Executando concatenação com ffmpeg...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                # Se falhar com copy, tentar recodificar
                print("⚠️ Falha com copy, tentando recodificar...")
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', list_file,
                    '-acodec', 'mp3',
                    '-ab', '192k',
                    final_filepath
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                raise Exception(f"Erro do ffmpeg: {result.stderr}")

        finally:
            # Limpar arquivo temporário
            try:
                os.unlink(list_file)
            except:
                pass

        # Verificar se o arquivo foi criado
        if not os.path.exists(final_filepath):
            raise Exception("Arquivo final não foi criado")

        final_size = os.path.getsize(final_filepath)
        
        # Tentar obter duração usando soundfile
        try:
            with sf.SoundFile(final_filepath) as f:
                final_duration = len(f) / f.samplerate
        except:
            # Fallback: estimar duração baseada no número de arquivos
            final_duration = len(valid_files) * 10  # Estimativa de 10s por arquivo

        print(f"✅ Áudio final criado: {final_filename} ({final_duration:.1f}s, {final_size} bytes)")

        return {
            'success': True,
            'data': {
                'audio_file': final_filepath,
                'filename': final_filename,
                'duration': final_duration,
                'size': final_size,
                'segments_count': len(valid_files),
                'format': 'mp3',
                'bitrate': '192k'
            }
        }

    except ImportError as e:
        return {
            'success': False,
            'error': f'Biblioteca necessária não instalada: {str(e)}. Execute: pip install soundfile'
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Timeout na concatenação de áudio. Arquivos muito grandes.'
        }
    except Exception as e:
        print(f"❌ Erro ao juntar áudios: {e}")
        return {
            'success': False,
            'error': f'Erro ao juntar áudios: {str(e)}'
        }

@automations_bp.route('/rapidapi-keys/reload', methods=['POST'])
def reload_rapidapi_keys():
    """Forçar reload das chaves RapidAPI do arquivo de configuração"""
    try:
        # Forçar reload das chaves
        old_count = len(RAPIDAPI_KEYS_ROTATION['keys'])
        load_rapidapi_keys()
        new_count = len(RAPIDAPI_KEYS_ROTATION['keys'])
        
        # Reset das chaves falhadas para dar uma nova chance
        RAPIDAPI_KEYS_ROTATION['failed_keys'] = set()
        RAPIDAPI_KEYS_ROTATION['current_index'] = 0
        
        print(f"🔄 Reload das chaves RapidAPI: {old_count} -> {new_count} chaves")
        add_real_time_log(f"🔄 Reload das chaves RapidAPI: {old_count} -> {new_count} chaves", "info", "rapidapi-reload")
        
        return jsonify({
            'success': True,
            'message': f'Chaves RapidAPI recarregadas com sucesso',
            'old_count': old_count,
            'new_count': new_count,
            'keys_loaded': new_count,
            'failed_keys_reset': True
        })
        
    except Exception as e:
        print(f"❌ Erro ao recarregar chaves RapidAPI: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao recarregar chaves: {str(e)}'
        }), 500

# Função get_rapidapi_status removida para evitar conflito de rotas
# A função principal está definida na linha 574 com rota '/rapidapi-status'

# Função clear_rapidapi_cache removida para evitar conflito de rotas
# A função principal está definida na linha 613

# Função reset_rapidapi_throttle removida para evitar conflito de rotas
# A função principal está definida na linha 639

@automations_bp.route('/debug-video-search', methods=['POST'])
def debug_video_search():
    """Endpoint de debug para testar get_channel_videos_rapidapi isoladamente"""
    try:
        data = request.get_json()
        channel_id = data.get('channel_id', 'UCX6OQ3DkcsbYNE6H8uQQuVA')  # MrBeast por padrão
        
        print(f"🔍 DEBUG: Testando get_channel_videos_rapidapi com channel_id: {channel_id}")
        
        # Configuração de teste
        config = {
            'max_videos': 5,
            'min_views': 1000000,
            'max_days_old': 30
        }
        
        start_time = time.time()
        
        # Testar a função diretamente
        result = get_channel_videos_rapidapi(channel_id, config)
        
        elapsed_time = time.time() - start_time
        
        print(f"🔍 DEBUG: get_channel_videos_rapidapi completou em {elapsed_time:.2f}s")
        
        if result['success']:
            videos = result['data']
            print(f"✅ DEBUG: Encontrados {len(videos)} vídeos")
            
            return jsonify({
                'success': True,
                'data': {
                    'channel_id': channel_id,
                    'videos_found': len(videos),
                    'elapsed_time': elapsed_time,
                    'videos': videos[:3],  # Apenas os primeiros 3 para debug
                    'config_used': config
                }
            })
        else:
            print(f"❌ DEBUG: Erro na busca de vídeos: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error'),
                'elapsed_time': elapsed_time,
                'channel_id': channel_id
            }), 500
            
    except Exception as e:
        print(f"❌ DEBUG: Erro no endpoint de debug: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro no debug: {str(e)}'
        }), 500

@automations_bp.route('/debug-extract-simple', methods=['POST'])
def debug_extract_simple():
    """Endpoint de debug super simples para testar requisição HTTP direta"""
    try:
        data = request.get_json()
        channel_id = data.get('channel_id', 'UCX6OQ3DkcsbYNE6H8uQQuVA')  # Default MrBeast
        
        print(f"🔍 DEBUG SIMPLES: Testando requisição HTTP direta para channel_id: {channel_id}")
        
        # Carregar chaves RapidAPI
        load_rapidapi_keys()
        api_key = get_next_rapidapi_key()
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Nenhuma chave RapidAPI disponível'
            }), 500
        
        print(f"🔑 DEBUG SIMPLES: Usando chave: {api_key[:20]}...")
        
        # Fazer requisição HTTP direta sem cache ou retry
        url = "https://youtube-v2.p.rapidapi.com/channel/videos"
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
        }
        params = {
            "channel_id": channel_id,
            "max_results": 5
        }
        
        print(f"📡 DEBUG SIMPLES: Fazendo requisição para {url}")
        print(f"📋 DEBUG SIMPLES: Parâmetros: {params}")
        
        import requests
        import time
        
        start_time = time.time()
        response = requests.get(url, headers=headers, params=params, timeout=30)
        elapsed_time = time.time() - start_time
        
        print(f"✅ DEBUG SIMPLES: Resposta recebida em {elapsed_time:.2f}s")
        print(f"📊 DEBUG SIMPLES: Status: {response.status_code}")
        print(f"📏 DEBUG SIMPLES: Tamanho: {len(response.content)} bytes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"🎉 DEBUG SIMPLES: Sucesso! Dados recebidos")
            return jsonify({
                'success': True,
                'status_code': response.status_code,
                'response_time': elapsed_time,
                'data_size': len(response.content),
                'data': data
            })
        else:
            print(f"❌ DEBUG SIMPLES: Erro {response.status_code}: {response.text[:200]}")
            return jsonify({
                'success': False,
                'status_code': response.status_code,
                'response_time': elapsed_time,
                'error': response.text[:500]
            })
        
    except Exception as e:
        print(f"❌ ERRO no debug_extract_simple: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@automations_bp.route('/debug-rapidapi-keys', methods=['GET'])
def debug_rapidapi_keys():
    """Endpoint de debug para verificar o status das chaves RapidAPI"""
    try:
        # Carregar chaves do arquivo de configuração
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
        file_keys = {}
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_keys = json.load(f)
        
        # Extrair todas as chaves RapidAPI do arquivo
        file_rapidapi_keys = []
        
        # Chave principal
        if file_keys.get('rapidapi'):
            file_rapidapi_keys.append({
                'name': 'rapidapi',
                'key': file_keys['rapidapi'][:20] + '...',
                'full_key': file_keys['rapidapi']
            })
        
        # Chaves numeradas (rapidapi_1, rapidapi_2, etc.)
        for i in range(1, 11):
            key_name = f'rapidapi_{i}'
            if file_keys.get(key_name):
                file_rapidapi_keys.append({
                    'name': key_name,
                    'key': file_keys[key_name][:20] + '...',
                    'full_key': file_keys[key_name]
                })
        
        # Array de chaves (se existir)
        if file_keys.get('rapidapi_keys') and isinstance(file_keys['rapidapi_keys'], list):
            for i, key in enumerate(file_keys['rapidapi_keys']):
                file_rapidapi_keys.append({
                    'name': f'rapidapi_keys[{i}]',
                    'key': key[:20] + '...',
                    'full_key': key
                })
        
        # Status das chaves no sistema de rotação
        rotation_keys = RAPIDAPI_KEYS_ROTATION.get('keys', [])
        failed_keys = RAPIDAPI_KEYS_ROTATION.get('failed_keys', set())
        current_index = RAPIDAPI_KEYS_ROTATION.get('current_index', 0)
        
        # Verificar status de cada chave
        keys_status = []
        for file_key in file_rapidapi_keys:
            full_key = file_key['full_key']
            is_loaded = full_key in rotation_keys
            is_failed = full_key in failed_keys
            is_current = is_loaded and rotation_keys[current_index % len(rotation_keys)] == full_key if rotation_keys else False
            
            keys_status.append({
                'name': file_key['name'],
                'key_preview': file_key['key'],
                'is_loaded_in_rotation': is_loaded,
                'is_failed': is_failed,
                'is_current': is_current,
                'status': 'FAILED' if is_failed else ('CURRENT' if is_current else ('LOADED' if is_loaded else 'NOT_LOADED'))
            })
        
        # Estatísticas
        total_keys_in_file = len(file_rapidapi_keys)
        total_keys_loaded = len(rotation_keys)
        total_keys_failed = len(failed_keys)
        total_keys_available = total_keys_loaded - total_keys_failed
        
        print(f"🔍 DEBUG RAPIDAPI KEYS:")
        print(f"   📁 Chaves no arquivo: {total_keys_in_file}")
        print(f"   🔄 Chaves carregadas: {total_keys_loaded}")
        print(f"   ❌ Chaves falhadas: {total_keys_failed}")
        print(f"   ✅ Chaves disponíveis: {total_keys_available}")
        print(f"   📍 Índice atual: {current_index}")
        
        for key_status in keys_status:
            print(f"   🔑 {key_status['name']}: {key_status['status']} ({key_status['key_preview']})")
        
        return jsonify({
            'success': True,
            'data': {
                'summary': {
                    'total_keys_in_file': total_keys_in_file,
                    'total_keys_loaded': total_keys_loaded,
                    'total_keys_failed': total_keys_failed,
                    'total_keys_available': total_keys_available,
                    'current_index': current_index
                },
                'keys_status': keys_status,
                'rotation_system': {
                    'keys_count': len(rotation_keys),
                    'failed_keys_count': len(failed_keys),
                    'current_index': current_index,
                    'next_key_preview': rotation_keys[(current_index + 1) % len(rotation_keys)][:20] + '...' if rotation_keys else None
                },
                'file_path': config_path,
                'file_exists': os.path.exists(config_path)
            }
        })
        
    except Exception as e:
        print(f"❌ Erro no debug das chaves RapidAPI: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro no debug: {str(e)}'
        }), 500

@automations_bp.route('/reset-rapidapi-failed-keys', methods=['POST'])
def reset_rapidapi_failed_keys():
    """Resetar manualmente as chaves RapidAPI falhadas"""
    try:
        # Backup do estado anterior
        old_failed_count = len(RAPIDAPI_KEYS_ROTATION.get('failed_keys', set()))
        old_failed_keys = list(RAPIDAPI_KEYS_ROTATION.get('failed_keys', set()))
        
        # Resetar chaves falhadas
        RAPIDAPI_KEYS_ROTATION['failed_keys'] = set()
        RAPIDAPI_KEYS_ROTATION['current_index'] = 0
        
        # Recarregar chaves do arquivo
        load_rapidapi_keys()
        
        new_available_count = len(RAPIDAPI_KEYS_ROTATION.get('keys', [])) - len(RAPIDAPI_KEYS_ROTATION.get('failed_keys', set()))
        
        print(f"🔄 Reset manual das chaves RapidAPI:")
        print(f"   ❌ Chaves falhadas removidas: {old_failed_count}")
        print(f"   ✅ Chaves disponíveis agora: {new_available_count}")
        print(f"   🔄 Índice resetado para: 0")
        
        add_real_time_log(f"🔄 Reset manual: {old_failed_count} chaves falhadas removidas, {new_available_count} disponíveis", "info", "rapidapi-reset")
        
        return jsonify({
            'success': True,
            'message': 'Chaves RapidAPI falhadas resetadas com sucesso',
            'data': {
                'old_failed_count': old_failed_count,
                'old_failed_keys_preview': [key[:20] + '...' for key in old_failed_keys],
                'new_available_count': new_available_count,
                'total_keys_loaded': len(RAPIDAPI_KEYS_ROTATION.get('keys', [])),
                'current_index_reset_to': 0
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao resetar chaves RapidAPI falhadas: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao resetar chaves: {str(e)}'
        }), 500

# ================================
# 🧪 ENDPOINTS DE TESTE PARA EXTRAÇÃO
# ================================

@automations_bp.route('/test-rapidapi', methods=['POST'])
def test_rapidapi_extraction():
    """Endpoint de teste para extração via RapidAPI"""
    print("🔍 DEBUG: Endpoint /test-rapidapi foi chamado!")
    try:
        data = request.get_json()
        print(f"🔍 DEBUG: Dados recebidos: {data}")
        url = data.get('url', '')
        max_titles = data.get('max_titles', 30)
        min_views = data.get('min_views', 0)
        max_views = data.get('max_views', None)
        days = data.get('days', None)
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL é obrigatória'
            }), 400
        
        print(f"🧪 TESTE RapidAPI: Iniciando extração para {url}")
        
        # Debug: verificar estado do sistema de rotação
        print(f"🔍 DEBUG: RAPIDAPI_KEYS_ROTATION = {RAPIDAPI_KEYS_ROTATION}")
        
        # Obter chave RapidAPI do sistema de rotação
        rapidapi_key = get_next_rapidapi_key()
        print(f"🔍 DEBUG: Chave obtida = {rapidapi_key[:20] if rapidapi_key else 'None'}...")
        
        if not rapidapi_key:
            print("❌ DEBUG: Nenhuma chave RapidAPI disponível")
            return jsonify({
                'success': False,
                'error': 'Chave da API RapidAPI é obrigatória'
            }), 400
        
        # Extrair channel_id da URL
        channel_id = extract_channel_id_from_url(url, rapidapi_key)
        if not channel_id:
            return jsonify({
                'success': False,
                'error': 'Não foi possível extrair o ID do canal da URL'
            }), 400
        
        # Chamar função RapidAPI
        start_time = time.time()
        result = get_channel_videos_rapidapi(channel_id, rapidapi_key, max_titles)
        end_time = time.time()
        
        if result.get('success'):
            # Aplicar filtros se especificados
            videos = result['data']['videos']
            if min_views or (max_views is not None and max_views > 0) or days:
                config = {
                    'min_views': min_views,
                    'max_views': max_views,
                    'days': days,
                    'max_titles': max_titles
                }
                videos = filter_videos_by_config(videos, config)
            
            return jsonify({
                'success': True,
                'method': 'RapidAPI',
                'response_time': round(end_time - start_time, 2),
                'data': {
                    'videos': videos,
                    'total_videos': len(videos),
                    'message': f'✅ {len(videos)} vídeos extraídos via RapidAPI!'
                }
            })
        else:
            return jsonify({
                'success': False,
                'method': 'RapidAPI',
                'response_time': round(end_time - start_time, 2),
                'error': result.get('error', 'Erro desconhecido')
            }), 500
            
    except Exception as e:
        print(f"❌ Erro no teste RapidAPI: {e}")
        return jsonify({
            'success': False,
            'method': 'RapidAPI',
            'error': str(e)
        }), 500

@automations_bp.route('/test-youtube-api', methods=['POST'])
def test_youtube_api_extraction():
    """Endpoint de teste para extração via YouTube Data API v3"""
    try:
        data = request.get_json()
        url = data.get('url', '')
        max_titles = data.get('max_titles', 30)
        min_views = data.get('min_views', 0)
        max_views = data.get('max_views', None)
        days = data.get('days', None)
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL é obrigatória'
            }), 400
        
        print(f"🧪 TESTE YouTube API: Iniciando extração para {url}")
        
        # Carregar chave da API do arquivo de configuração
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    api_keys = json.load(f)
                youtube_api_key = api_keys.get('youtube_api')
            else:
                return jsonify({
                    'success': False,
                    'error': 'Arquivo api_keys.json não encontrado'
                }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro ao carregar api_keys.json: {str(e)}'
            }), 400
        
        if not youtube_api_key:
            return jsonify({
                'success': False,
                'error': 'Chave da YouTube API não configurada no arquivo api_keys.json'
            }), 400
        
        # Extrair channel_id da URL (agora com suporte a handles)
        channel_id = extract_channel_id_from_url(url, youtube_api_key)
        if not channel_id:
            return jsonify({
                'success': False,
                'error': 'Não foi possível extrair o ID do canal da URL'
            }), 400
        
        # Chamar função YouTube API
        start_time = time.time()
        result = get_channel_videos_youtube_api(channel_id, youtube_api_key, max_titles)
        end_time = time.time()
        
        if result.get('success'):
            # Aplicar filtros se especificados
            videos = result['data']['videos']
            if min_views or (max_views is not None and max_views > 0) or days:
                config = {
                    'min_views': min_views,
                    'max_views': max_views,
                    'days': days,
                    'max_titles': max_titles
                }
                videos = filter_videos_by_config(videos, config)
            
            return jsonify({
                'success': True,
                'method': 'YouTube API Official',
                'response_time': round(end_time - start_time, 2),
                'data': {
                    'videos': videos,
                    'total_videos': len(videos),
                    'message': f'✅ {len(videos)} vídeos extraídos via YouTube API oficial!'
                }
            })
        else:
            return jsonify({
                'success': False,
                'method': 'YouTube API Official',
                'response_time': round(end_time - start_time, 2),
                'error': result.get('error', 'Erro desconhecido')
            }), 500
            
    except Exception as e:
        print(f"❌ Erro no teste YouTube API: {e}")
        return jsonify({
            'success': False,
            'method': 'YouTube API Official',
            'error': str(e)
        }), 500

@automations_bp.route('/extract-youtube-ytdlp', methods=['POST'])
def extract_youtube_ytdlp_endpoint():
    """Endpoint dedicado para extração via yt-dlp"""
    try:
        print("🛡️ DEBUG: Iniciando endpoint /extract-youtube-ytdlp")
        data = request.get_json()
        print(f"🛡️ DEBUG: Dados recebidos: {data}")
        
        url = data.get('url', '').strip()
        config = data.get('config', {})
        
        print(f"🛡️ DEBUG: URL: {url}, Config: {config}")
        
        if not url:
            print("❌ DEBUG: URL não fornecida")
            return jsonify({
                'success': False,
                'error': 'URL ou ID do canal é obrigatório'
            }), 400
        
        print(f"🛡️ EXTRAÇÃO yt-dlp: Iniciando extração para {url}")
        
        # Chamar função yt-dlp
        extraction_start_time = time.time()
        result = get_channel_videos_ytdlp(url, config.get('max_titles', 10))
        
        print(f"🛡️ DEBUG: Resultado da função yt-dlp: {result.get('success', False)}")
        
        if result.get('success'):
            # Aplicar filtros se especificados
            videos = result['data']['videos']
            if config:
                videos = filter_videos_by_config(videos, config)
            
            # Preparar dados de resposta
            result_data = result['data']
            result_data['extraction_method'] = 'yt-dlp'
            result_data['videos'] = videos
            result_data['total_videos'] = len(videos)
            result_data['extraction_time'] = time.time() - extraction_start_time
            
            # Calcular totais
            total_views = sum(video.get('views', 0) for video in videos)
            total_likes = sum(video.get('likes', 0) for video in videos)
            result_data['total_views'] = total_views
            result_data['total_likes'] = total_likes
            
            print(f"✅ yt-dlp: {len(videos)} vídeos extraídos com sucesso!")
            
            return jsonify({
                'success': True,
                'data': result_data,
                'message': f'✅ Extração concluída via yt-dlp. {len(videos)} vídeos encontrados.'
            })
        else:
            print(f"❌ yt-dlp falhou: {result.get('error', 'Erro desconhecido')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Erro na extração via yt-dlp')
            }), 500
            
    except Exception as e:
        print(f"❌ Erro no endpoint yt-dlp: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@automations_bp.route('/test-ytdlp', methods=['POST'])
def test_ytdlp_extraction():
    """Endpoint de teste para extração via yt-dlp"""
    try:
        print("🔍 DEBUG: Iniciando endpoint /test-ytdlp")
        data = request.get_json()
        print(f"🔍 DEBUG: Dados recebidos: {data}")
        
        url = data.get('channel_url', '') or data.get('url', '')
        max_titles = data.get('max_titles', 30)
        min_views = data.get('min_views', 0)
        max_views = data.get('max_views', None)
        days = data.get('max_days', None) or data.get('days', None)
        
        print(f"🔍 DEBUG: Parâmetros processados - URL: {url}, max_titles: {max_titles}, min_views: {min_views}, days: {days}")
        
        if not url:
            print("❌ DEBUG: URL não fornecida")
            return jsonify({
                'success': False,
                'error': 'URL é obrigatória'
            }), 400
        
        print(f"🧪 TESTE yt-dlp: Iniciando extração para {url}")
        print("🔍 DEBUG: Chamando get_channel_videos_ytdlp...")
        
        # Chamar função yt-dlp
        start_time = time.time()
        result = get_channel_videos_ytdlp(url, max_titles)
        end_time = time.time()
        
        print(f"🔍 DEBUG: Resultado da função yt-dlp: {result}")
        print(f"🔍 DEBUG: Tempo de execução: {round(end_time - start_time, 2)}s")
        
        if result.get('success'):
            # Aplicar filtros se especificados
            videos = result['data']['videos']
            if min_views or (max_views is not None and max_views > 0) or days:
                config = {
                    'min_views': min_views,
                    'max_views': max_views,
                    'days': days,
                    'max_titles': max_titles
                }
                videos = filter_videos_by_config(videos, config)
            
            return jsonify({
                'success': True,
                'method': 'yt-dlp',
                'response_time': round(end_time - start_time, 2),
                'data': {
                    'videos': videos,
                    'total_videos': len(videos),
                    'message': f'✅ {len(videos)} vídeos extraídos via yt-dlp!'
                }
            })
        else:
            return jsonify({
                'success': False,
                'method': 'yt-dlp',
                'response_time': round(end_time - start_time, 2),
                'error': result.get('error', 'Erro desconhecido')
            }), 500
            
    except Exception as e:
        print(f"❌ Erro no teste yt-dlp: {e}")
        return jsonify({
            'success': False,
            'method': 'yt-dlp',
            'error': str(e)
        }), 500

# ================================
# 🚀 INICIALIZAÇÃO DO SISTEMA
# ================================

# Função debug_extract_simple removida (duplicata) - mantida apenas a primeira definição na linha 737

# Carregar cache persistente na inicialização
try:
    load_persistent_cache()
except Exception as e:
    print(f"⚠️ Erro ao carregar cache persistente na inicialização: {e}")



# Carregar chaves RapidAPI na inicialização
try:
    load_rapidapi_keys()
    print(f"✅ Chaves RapidAPI carregadas na inicialização: {len(RAPIDAPI_KEYS_ROTATION.get('keys', []))} chaves")
except Exception as e:
    print(f"⚠️ Erro ao carregar chaves RapidAPI na inicialização: {e}")

# Carregar chaves Gemini na inicialização
try:
    load_gemini_keys()
    print(f"✅ Chaves Gemini carregadas na inicialização: {len(GEMINI_KEYS_ROTATION.get('keys', []))} chaves")
except Exception as e:
    print(f"⚠️ Erro ao carregar chaves Gemini na inicialização: {e}")

# ================================
# 🔄 SISTEMA DE RETRY AUTOMÁTICO GEMINI
# ================================

def generate_content_with_gemini_retry(prompt, max_retries=3):
    """Gerar conteúdo usando Gemini com retry automático entre múltiplas chaves"""
    import google.generativeai as genai
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Obter chave Gemini
            api_key = get_next_gemini_key()
            if not api_key:
                raise Exception('Nenhuma chave Gemini disponível. Configure pelo menos uma chave nas Configurações.')
            
            print(f"🔄 Tentativa {attempt + 1}/{max_retries}: Usando chave Gemini")
            
            # Configurar Gemini diretamente
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            print(f"🔍 DEBUG: Enviando prompt para Gemini ({len(prompt)} chars) - Tentativa {attempt + 1}/{max_retries}")
            response = model.generate_content(prompt)
            print(f"✅ Gemini respondeu com sucesso na tentativa {attempt + 1}")
            return response.text
            
        except Exception as e:
            error_str = str(e)
            last_error = error_str
            print(f"❌ Tentativa {attempt + 1}/{max_retries} falhou: {error_str}")
            
            # Se é erro 429 (quota exceeded) e não é a última tentativa, tentar próxima chave
            if ("429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower()) and attempt < max_retries - 1:
                print(f"🔄 Erro de cota detectado, tentando próxima chave...")
                # Não temos acesso à api_key específica aqui, então passamos None
                handle_gemini_429_error(error_str, None)
                continue
            else:
                # Outros erros ou última tentativa, parar
                if attempt == max_retries - 1:
                    print(f"🛑 Última tentativa falhou, parando retries")
                else:
                    print(f"🛑 Erro não relacionado à cota, parando tentativas")
                break
    
    # Se chegou aqui, todas as tentativas falharam
    final_error = f'Todas as {max_retries} tentativas Gemini falharam. Último erro: {last_error}'
    print(f"❌ DEBUG: {final_error}")
    raise Exception(f'Erro Gemini: {final_error}')
