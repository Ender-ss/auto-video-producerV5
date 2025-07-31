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

# Import AI libraries
try:
    import google.generativeai as genai
    from ..services.title_generator import TitleGenerator
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

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

# ================================
# 🧪 TESTE RAPIDAPI
# ================================

@automations_bp.route('/test-rapidapi', methods=['POST'])
def test_rapidapi():
    """Testar conexão com RapidAPI YouTube V2"""
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

        # Testar endpoint de detalhes do canal
        response = requests.get(
            "https://youtube-v2.p.rapidapi.com/channel/details",
            headers=headers,
            params={"channel_id": test_channel},
            timeout=10
        )

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

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Chave da API Gemini é obrigatória'
            }), 400

        if not GOOGLE_GENAI_TTS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Biblioteca google-genai não instalada'
            }), 400

        # Gerar áudio TTS usando Gemini
        result = generate_tts_with_gemini(text, api_key, voice_name, model)
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

    if input_str.startswith('UC') and len(input_str) == 24:
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
            if extracted.startswith('UC') and len(extracted) == 24:
                return extracted
            return extracted

    return None

def get_channel_id_rapidapi(channel_name, api_key):
    """Obter ID do canal usando RapidAPI YouTube V2"""
    try:
        url = "https://youtube-v2.p.rapidapi.com/channel/id"

        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
        }

        params = {"channel_name": channel_name}

        print(f"🔍 DEBUG: Buscando ID do canal para: {channel_name}")
        print(f"🔍 DEBUG: URL: {url}")
        print(f"🔍 DEBUG: Params: {params}")

        # Tentar com retry em caso de timeout
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                print(f"🔍 DEBUG: Status da resposta: {response.status_code}")
                break  # Se chegou aqui, a requisição foi bem-sucedida
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:  # Última tentativa
                    raise
                print(f"🔄 Tentativa {attempt + 1} falhou (timeout), tentando novamente...")
                continue

        if response.status_code != 200:
            print(f"🔍 DEBUG: Erro na resposta: {response.text}")
            return {
                'success': False,
                'error': f'Erro na API RapidAPI: {response.status_code} - {response.text}'
            }

        data = response.json()
        print(f"🔍 DEBUG: Resposta da API: {data}")

        if 'channel_id' not in data:
            return {
                'success': False,
                'error': 'Canal não encontrado'
            }

        return {
            'success': True,
            'data': {
                'channel_id': data['channel_id'],
                'channel_name': data.get('channel_name', channel_name)
            }
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao buscar ID do canal: {str(e)}'
        }

def get_channel_details_rapidapi(channel_id, api_key):
    """Obter detalhes do canal usando RapidAPI YouTube V2"""
    try:
        url = "https://youtube-v2.p.rapidapi.com/channel/details"

        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
        }

        params = {"channel_id": channel_id}

        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code != 200:
            return {
                'success': False,
                'error': f'Erro ao buscar detalhes do canal: {response.status_code}'
            }

        data = response.json()

        return {
            'success': True,
            'data': {
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'subscriber_count': data.get('subscriber_count', 0),
                'video_count': data.get('video_count', 0)
            }
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao buscar detalhes do canal: {str(e)}'
        }

def get_channel_videos_rapidapi(channel_id, api_key, max_results=50):
    """Obter vídeos do canal usando RapidAPI YouTube V2"""
    try:
        url = "https://youtube-v2.p.rapidapi.com/channel/videos"
        print(f"🔍 DEBUG: Fazendo requisição para: {url}")
        print(f"🔍 DEBUG: Channel ID: {channel_id}")

        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
        }

        params = {
            "channel_id": channel_id,
            "max_results": min(max_results, 50)  # Limite da API
        }
        print(f"🔍 DEBUG: Parâmetros: {params}")

        # Tentar com retry em caso de timeout
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                print(f"🔍 DEBUG: Status da resposta: {response.status_code}")
                break  # Se chegou aqui, a requisição foi bem-sucedida
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:  # Última tentativa
                    print(f"🔍 DEBUG: Timeout após {max_retries} tentativas")
                    raise
                print(f"🔄 Tentativa {attempt + 1} falhou (timeout), tentando novamente...")
                continue

        if response.status_code != 200:
            print(f"🔍 DEBUG: Erro na resposta: {response.text}")
            return {
                'success': False,
                'error': f'Erro ao buscar vídeos do canal: {response.status_code}'
            }

        data = response.json()
        print(f"🔍 DEBUG: Resposta da API: {data}")

        if 'videos' not in data:
            print(f"🔍 DEBUG: Chaves disponíveis na resposta: {list(data.keys())}")
            return {
                'success': False,
                'error': 'Nenhum vídeo encontrado no canal'
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

        return {
            'success': True,
            'data': {
                'videos': videos,
                'total_videos': len(videos),
                'total_count': len(videos),
                'message': f'✅ {len(videos)} títulos extraídos com sucesso!'
            }
        }

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

        if api_keys.get('openai'):
            openai_configured = title_generator.configure_openai(api_keys['openai'])

        if api_keys.get('gemini'):
            gemini_configured = title_generator.configure_gemini(api_keys['gemini'])

        if not openai_configured and not gemini_configured:
            return jsonify({
                'success': False,
                'error': 'Nenhuma IA configurada. Configure OpenAI ou Gemini nas configurações.'
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

        if api_keys.get('openai'):
            openai_configured = title_generator.configure_openai(api_keys['openai'])

        if api_keys.get('gemini'):
            gemini_configured = title_generator.configure_gemini(api_keys['gemini'])

        if not openai_configured and not gemini_configured:
            return jsonify({
                'success': False,
                'error': 'Nenhuma IA configurada. Configure OpenAI ou Gemini nas configurações.'
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
