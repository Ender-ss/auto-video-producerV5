"""
🎯 Premise Generation Routes
Rotas para geração de premissas de vídeos
"""

from flask import Blueprint, request, jsonify
import requests
import json
import os
from services.title_generator import TitleGenerator

premise_bp = Blueprint('premise', __name__)

@premise_bp.route('/generate', methods=['POST'])
def generate_premises():
    """Gerar premissas baseadas nos títulos fornecidos"""
    try:
        data = request.get_json()
        titles = data.get('titles', [])
        prompt = data.get('prompt', '')
        ai_provider = data.get('ai_provider', 'auto')
        openrouter_model = data.get('openrouter_model', 'auto')
        api_keys = data.get('api_keys', {})

        if not titles:
            return jsonify({
                'success': False,
                'error': 'Nenhum título fornecido'
            }), 400

        # Inicializar o gerador de títulos (que também pode gerar premissas)
        title_generator = TitleGenerator()
        
        # Configurar APIs baseado no provider
        if ai_provider == 'openai' or ai_provider == 'auto':
            if api_keys.get('openai'):
                title_generator.configure_openai(api_keys['openai'])
        
        if ai_provider == 'gemini' or ai_provider == 'auto':
            if api_keys.get('gemini'):
                title_generator.configure_gemini(api_keys['gemini'])
        
        if ai_provider == 'openrouter' or ai_provider == 'auto':
            if api_keys.get('openrouter'):
                title_generator.configure_openrouter(api_keys['openrouter'])

        # Gerar premissas usando o provider especificado
        premises = []
        
        if ai_provider == 'auto':
            # Tentar em ordem de prioridade
            providers = ['openrouter', 'gemini', 'openai']
            success = False
            
            for provider in providers:
                try:
                    if provider == 'openrouter' and api_keys.get('openrouter'):
                        premises = generate_premises_openrouter(titles, prompt, openrouter_model, api_keys['openrouter'])
                        success = True
                        break
                    elif provider == 'gemini' and api_keys.get('gemini'):
                        premises = generate_premises_gemini(titles, prompt, title_generator)
                        success = True
                        break
                    elif provider == 'openai' and api_keys.get('openai'):
                        premises = generate_premises_openai(titles, prompt, title_generator)
                        success = True
                        break
                except Exception as e:
                    print(f"❌ Erro com {provider}: {e}")
                    continue
            
            if not success:
                return jsonify({
                    'success': False,
                    'error': 'Nenhuma IA disponível conseguiu gerar premissas'
                }), 500
                
        elif ai_provider == 'openrouter':
            if not api_keys.get('openrouter'):
                return jsonify({
                    'success': False,
                    'error': 'Chave da API OpenRouter não configurada'
                }), 400
            premises = generate_premises_openrouter(titles, prompt, openrouter_model, api_keys['openrouter'])
            
        elif ai_provider == 'gemini':
            if not api_keys.get('gemini'):
                return jsonify({
                    'success': False,
                    'error': 'Chave da API Gemini não configurada'
                }), 400
            premises = generate_premises_gemini(titles, prompt, title_generator)
            
        elif ai_provider == 'openai':
            if not api_keys.get('openai'):
                return jsonify({
                    'success': False,
                    'error': 'Chave da API OpenAI não configurada'
                }), 400
            premises = generate_premises_openai(titles, prompt, title_generator)

        return jsonify({
            'success': True,
            'premises': premises,
            'provider_used': ai_provider,
            'count': len(premises)
        })

    except Exception as e:
        print(f"❌ Erro na geração de premissas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_premises_openrouter(titles, prompt, model, api_key):
    """Gerar premissas usando OpenRouter"""
    try:
        # Mapear modelo automático para o melhor disponível
        if model == 'auto':
            model = 'anthropic/claude-3.5-sonnet'
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5173',
            'X-Title': 'Auto Video Producer'
        }
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json={
                'model': model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Você é um especialista em criação de conteúdo e storytelling para YouTube.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.8
            },
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f'OpenRouter API error: {response.status_code} - {response.text}')
        
        data = response.json()
        content = data['choices'][0]['message']['content']
        
        return parse_premises_response(content, titles)
        
    except Exception as e:
        raise Exception(f'Erro OpenRouter: {str(e)}')

def generate_premises_gemini(titles, prompt, title_generator):
    """Gerar premissas usando Gemini"""
    try:
        if not title_generator.gemini_model:
            raise Exception('Gemini não configurado')
        
        response = title_generator.gemini_model.generate_content(prompt)
        content = response.text
        
        return parse_premises_response(content, titles)
        
    except Exception as e:
        raise Exception(f'Erro Gemini: {str(e)}')

def generate_premises_openai(titles, prompt, title_generator):
    """Gerar premissas usando OpenAI"""
    try:
        if not title_generator.openai_client:
            raise Exception('OpenAI não configurado')
        
        response = title_generator.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em criação de conteúdo e storytelling para YouTube."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.8
        )
        
        content = response.choices[0].message.content
        
        return parse_premises_response(content, titles)
        
    except Exception as e:
        raise Exception(f'Erro OpenAI: {str(e)}')

def parse_premises_response(content, titles):
    """Parsear resposta da IA para extrair premissas"""
    premises = []
    
    try:
        # Dividir por seções
        sections = content.split('---')
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Procurar por padrões de título e premissa
            lines = section.split('\n')
            current_title = None
            current_premise = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detectar título
                if line.startswith('**TÍTULO:**') or line.startswith('TÍTULO:'):
                    current_title = line.replace('**TÍTULO:**', '').replace('TÍTULO:', '').strip()
                elif line.startswith('**PREMISSA:**') or line.startswith('PREMISSA:'):
                    current_premise = []
                elif current_title and line:
                    current_premise.append(line)
            
            if current_title and current_premise:
                premises.append({
                    'title': current_title,
                    'premise': '\n'.join(current_premise).strip()
                })
        
        # Se não conseguiu parsear, tentar método alternativo
        if not premises and titles:
            # Dividir por títulos conhecidos
            for title in titles:
                if title in content:
                    # Encontrar a seção deste título
                    start_idx = content.find(title)
                    if start_idx != -1:
                        # Procurar próximo título ou fim
                        end_idx = len(content)
                        for other_title in titles:
                            if other_title != title:
                                other_idx = content.find(other_title, start_idx + len(title))
                                if other_idx != -1 and other_idx < end_idx:
                                    end_idx = other_idx
                        
                        section = content[start_idx:end_idx].strip()
                        # Extrair premissa (tudo após o título)
                        premise_text = section.replace(title, '').strip()
                        
                        # Limpar marcadores
                        premise_text = premise_text.replace('**PREMISSA:**', '').replace('PREMISSA:', '').strip()
                        
                        if premise_text:
                            premises.append({
                                'title': title,
                                'premise': premise_text
                            })
        
        return premises
        
    except Exception as e:
        print(f"❌ Erro ao parsear premissas: {e}")
        # Fallback: criar uma premissa genérica para cada título
        return [
            {
                'title': title,
                'premise': f"Premissa gerada para: {title}\n\nEsta é uma premissa de exemplo que seria desenvolvida com base no título fornecido."
            }
            for title in titles
        ]
