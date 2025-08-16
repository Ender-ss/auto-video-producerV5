"""
🧪 API Tests Routes
Testes individuais de APIs
"""

from flask import Blueprint, request, jsonify
import requests
import json
import logging

tests_bp = Blueprint('tests', __name__)
logger = logging.getLogger(__name__)

# ================================
# 🧪 TESTES DE API
# ================================

@tests_bp.route('/run-api-test', methods=['POST'])
def run_api_test():
    """Executar teste individual de API"""
    try:
        data = request.get_json()
        api_id = data.get('api_id')
        api_key = data.get('api_key')
        test_name = data.get('test_name')
        endpoint = data.get('endpoint')
        params = data.get('params', {})
        
        logger.info(f"🧪 Executando teste: {api_id} - {test_name}")
        
        if api_id == 'rapidapi':
            return test_rapidapi(api_key, endpoint, params)
        elif api_id == 'openai':
            return test_openai(api_key, endpoint, params)
        elif api_id == 'gemini':
            return test_gemini(api_key, endpoint, params)
        elif api_id == 'elevenlabs':
            return test_elevenlabs(api_key, endpoint, params)
        else:
            return jsonify({
                'success': False,
                'error': f'API não suportada: {api_id}'
            }), 400
            
    except Exception as e:
        logger.error(f"Erro no teste de API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def test_rapidapi(api_key, endpoint, params):
    """Testar RapidAPI YouTube V2 com throttling inteligente"""
    try:
        from .automations import apply_rapidapi_throttle, handle_rapidapi_429, reset_rapidapi_throttle_success
        
        base_url = "https://youtube-v2.p.rapidapi.com"
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "youtube-v2.p.rapidapi.com"
        }
        
        # Mapear endpoints
        endpoint_map = {
            '/channel/id': '/channel/id',
            '/channel/details': '/channel/details', 
            '/channel/videos': '/channel/videos'
        }
        
        if endpoint not in endpoint_map:
            return jsonify({
                'success': False,
                'error': f'Endpoint não suportado: {endpoint}'
            })
        
        url = base_url + endpoint_map[endpoint]
        
        # Aplicar throttling inteligente
        apply_rapidapi_throttle()
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        result = {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'endpoint': endpoint,
            'params': params
        }
        
        if response.status_code == 200:
            reset_rapidapi_throttle_success()
            try:
                result['data'] = response.json()
                result['message'] = 'Teste executado com sucesso'
            except json.JSONDecodeError:
                result['data'] = response.text
                result['message'] = 'Resposta não é JSON válido'
        elif response.status_code == 429:
            handle_rapidapi_429()
            result['error'] = response.text
            result['message'] = 'Rate limit atingido - throttling ativado'
        else:
            result['error'] = response.text
            result['message'] = f'Erro HTTP {response.status_code}'
        
        return jsonify(result)
        
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Timeout na requisição',
            'message': 'A API demorou muito para responder'
        })
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': 'Erro de conexão',
            'message': 'Não foi possível conectar à API'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro interno no teste'
        })

def test_openai(api_key, endpoint, params):
    """Testar OpenAI API"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        if endpoint == '/generate/title':
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": f"Crie um título viral para: {params.get('prompt', '')}"}
                ],
                "max_tokens": 100
            }
        elif endpoint == '/generate/script':
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": f"Crie um roteiro para o vídeo: {params.get('title', '')}"}
                ],
                "max_tokens": 500
            }
        else:
            return jsonify({
                'success': False,
                'error': f'Endpoint não suportado: {endpoint}'
            })
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        result = {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'endpoint': endpoint,
            'params': params
        }
        
        if response.status_code == 200:
            result['data'] = response.json()
            result['message'] = 'Teste executado com sucesso'
        else:
            result['error'] = response.text
            result['message'] = f'Erro HTTP {response.status_code}'
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro interno no teste'
        })

def test_gemini(api_key, endpoint, params):
    """Testar Google Gemini API"""
    try:
        if endpoint == '/generate/title':
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Crie um título viral para: {params.get('prompt', '')}"
                    }]
                }]
            }
        else:
            return jsonify({
                'success': False,
                'error': f'Endpoint não suportado: {endpoint}'
            })
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        result = {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'endpoint': endpoint,
            'params': params
        }
        
        if response.status_code == 200:
            result['data'] = response.json()
            result['message'] = 'Teste executado com sucesso'
        else:
            result['error'] = response.text
            result['message'] = f'Erro HTTP {response.status_code}'
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro interno no teste'
        })

def test_elevenlabs(api_key, endpoint, params):
    """Testar ElevenLabs API"""
    try:
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        if endpoint == '/voices':
            url = "https://api.elevenlabs.io/v1/voices"
            response = requests.get(url, headers=headers, timeout=15)
        elif endpoint == '/text-to-speech':
            voice_id = params.get('voice_id', 'default')
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            payload = {
                "text": params.get('text', 'Teste'),
                "model_id": "eleven_monolingual_v1"
            }
            response = requests.post(url, headers=headers, json=payload, timeout=30)
        else:
            return jsonify({
                'success': False,
                'error': f'Endpoint não suportado: {endpoint}'
            })
        
        result = {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'endpoint': endpoint,
            'params': params
        }
        
        if response.status_code == 200:
            if endpoint == '/text-to-speech':
                result['data'] = {'audio_size': len(response.content)}
                result['message'] = 'Áudio gerado com sucesso'
            else:
                result['data'] = response.json()
                result['message'] = 'Teste executado com sucesso'
        else:
            result['error'] = response.text
            result['message'] = f'Erro HTTP {response.status_code}'
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro interno no teste'
        })

# ================================
# 🔍 DIAGNÓSTICO GERAL
# ================================

@tests_bp.route('/diagnose', methods=['POST'])
def diagnose_system():
    """Executar diagnóstico completo do sistema"""
    try:
        data = request.get_json()
        api_keys = data.get('api_keys', {})
        
        results = {}
        
        # Testar cada API configurada
        for api_id, api_key in api_keys.items():
            if api_key:
                logger.info(f"🔍 Diagnosticando {api_id}")
                
                if api_id == 'rapidapi':
                    test_result = test_rapidapi(api_key, '/channel/details', {'channel_id': 'UCX6OQ3DkcsbYNE6H8uQQuVA'})
                    results[api_id] = test_result.get_json()
                # Adicionar outros testes conforme necessário
        
        return jsonify({
            'success': True,
            'data': results,
            'message': 'Diagnóstico completo executado'
        })
        
    except Exception as e:
        logger.error(f"Erro no diagnóstico: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
