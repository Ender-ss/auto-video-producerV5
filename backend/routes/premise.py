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

        print(f"🔍 DEBUG: Premissas geradas: {len(premises)}")
        for i, premise in enumerate(premises):
            print(f"🔍 DEBUG: Premissa {i+1}: título='{premise.get('title', 'N/A')}', premissa_len={len(premise.get('premise', ''))}")

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

        print(f"🔍 DEBUG: Prompt enviado para Gemini (primeiros 500 chars): {prompt[:500]}...")

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

    print(f"🔍 DEBUG: Parseando resposta da IA...")
    print(f"🔍 DEBUG: Títulos fornecidos: {titles}")
    print(f"🔍 DEBUG: Conteúdo da resposta (primeiros 500 chars): {content[:500]}...")

    try:
        # MÉTODO 1: Tentar parsing estruturado primeiro
        sections = content.split('---')
        print(f"🔍 DEBUG: Método 1 - Encontradas {len(sections)} seções")

        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue

            print(f"🔍 DEBUG: Processando seção {i+1}: {section[:100]}...")

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
                    print(f"🔍 DEBUG: Título encontrado: '{current_title}'")
                elif line.startswith('**PREMISSA:**') or line.startswith('PREMISSA:'):
                    current_premise = []
                    print(f"🔍 DEBUG: Início de premissa detectado")
                elif current_title and line:
                    current_premise.append(line)

            if current_title and current_premise:
                premise_text = '\n'.join(current_premise).strip()
                print(f"🔍 DEBUG: Premissa encontrada - Título: '{current_title}', Premissa: {len(premise_text)} chars")
                premises.append({
                    'title': current_title,
                    'premise': premise_text
                })

        # MÉTODO 2: Se não encontrou nada, tentar parsing mais flexível
        if not premises:
            print(f"🔍 DEBUG: Método 1 falhou, tentando método 2 - parsing flexível...")

            # Tentar encontrar qualquer padrão de título seguido de texto
            lines = content.split('\n')
            current_title = None
            current_premise = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Procurar por qualquer linha que contenha um dos títulos fornecidos
                title_found = None
                for title in titles:
                    if title.lower() in line.lower() or line.lower() in title.lower():
                        title_found = title
                        break

                if title_found:
                    # Salvar premissa anterior se existir
                    if current_title and current_premise:
                        premise_text = '\n'.join(current_premise).strip()
                        print(f"🔍 DEBUG: Método 2 - Premissa encontrada: '{current_title}', {len(premise_text)} chars")
                        premises.append({
                            'title': current_title,
                            'premise': premise_text
                        })

                    current_title = title_found
                    current_premise = []
                    print(f"🔍 DEBUG: Método 2 - Novo título: '{current_title}'")
                elif current_title and line and not line.startswith('#'):
                    current_premise.append(line)

            # Adicionar última premissa
            if current_title and current_premise:
                premise_text = '\n'.join(current_premise).strip()
                print(f"🔍 DEBUG: Método 2 - Última premissa: '{current_title}', {len(premise_text)} chars")
                premises.append({
                    'title': current_title,
                    'premise': premise_text
                })
        
        # MÉTODO 3: Se ainda não encontrou nada, criar premissas baseadas no conteúdo completo
        if not premises and titles:
            print(f"🔍 DEBUG: Métodos 1 e 2 falharam, tentando método 3 - divisão por títulos...")
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
                            print(f"🔍 DEBUG: Método 3 - Premissa criada: '{title}', {len(premise_text)} chars")
                            premises.append({
                                'title': title,
                                'premise': premise_text
                            })

        # MÉTODO 4: Se ainda não tem premissas, criar uma genérica baseada no conteúdo completo
        if not premises and titles and content.strip():
            print(f"🔍 DEBUG: Método 4 - Criando premissas genéricas baseadas no conteúdo...")
            # Dividir o conteúdo em partes iguais para cada título
            content_clean = content.strip()
            content_per_title = len(content_clean) // len(titles)

            for i, title in enumerate(titles):
                start_pos = i * content_per_title
                end_pos = (i + 1) * content_per_title if i < len(titles) - 1 else len(content_clean)
                premise_text = content_clean[start_pos:end_pos].strip()

                if premise_text:
                    print(f"🔍 DEBUG: Método 4 - Premissa genérica: '{title}', {len(premise_text)} chars")
                    premises.append({
                        'title': title,
                        'premise': premise_text
                    })

        print(f"🔍 DEBUG: Total de premissas parseadas: {len(premises)}")
        return premises

    except Exception as e:
        print(f"❌ Erro ao parsear premissas: {e}")
        print(f"🔍 DEBUG: Usando fallback - criando premissas genéricas para {len(titles)} títulos")
        # Fallback: criar uma premissa genérica para cada título
        fallback_premises = [
            {
                'title': title,
                'premise': f"Premissa gerada para: {title}\n\nEsta é uma premissa de exemplo que seria desenvolvida com base no título fornecido."
            }
            for title in titles
        ]
        print(f"🔍 DEBUG: Fallback criou {len(fallback_premises)} premissas")
        return fallback_premises
