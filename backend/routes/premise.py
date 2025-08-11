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
            gemini_key = api_keys.get('gemini') or api_keys.get('gemini_1')
            if gemini_key:
                title_generator.configure_gemini(gemini_key)
        
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
                    elif provider == 'gemini' and (api_keys.get('gemini') or api_keys.get('gemini_1')):
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
            gemini_key = api_keys.get('gemini') or api_keys.get('gemini_1')
            if not gemini_key:
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

# Funções auxiliares para geração em partes
def create_inicio_prompt(title, premise, custom_prompt):
    """Criar prompt limpo para a parte INÍCIO"""
    return f"""## INFORMAÇÕES DO PROJETO:
### TÍTULO: {title}
### PREMISSA: {premise}
### 🎭 Prompt Personalizado do Agente:
{custom_prompt}

## INSTRUÇÃO ESPECÍFICA:
Gere a parte INICIAL do roteiro (aproximadamente 25% do roteiro total) seguindo EXATAMENTE o formato especificado no prompt personalizado acima. Esta é a PRIMEIRA parte de um roteiro maior."""

def create_capitulo_prompt(title, premise, custom_prompt, capitulo_num, total_capitulos):
    """Criar prompt limpo para um capítulo"""
    return f"""## INFORMAÇÕES DO PROJETO:
### TÍTULO: {title}
### PREMISSA: {premise}
### 🎭 Prompt Personalizado do Agente:
{custom_prompt}

## INSTRUÇÃO ESPECÍFICA:
Gere o CAPÍTULO {capitulo_num} de {total_capitulos} do desenvolvimento do roteiro seguindo EXATAMENTE o formato especificado no prompt personalizado acima. Esta é uma parte INTERMEDIÁRIA de um roteiro maior."""

def create_final_prompt(title, premise, custom_prompt):
    """Criar prompt limpo para a parte FINAL"""
    return f"""## INFORMAÇÕES DO PROJETO:
### TÍTULO: {title}
### PREMISSA: {premise}
### 🎭 Prompt Personalizado do Agente:
{custom_prompt}

## INSTRUÇÃO ESPECÍFICA:
Gere a parte FINAL do roteiro (aproximadamente 25% final do roteiro total) seguindo EXATAMENTE o formato especificado no prompt personalizado acima. Esta é a ÚLTIMA parte que finaliza todo o roteiro."""

def generate_script_part(prompt, ai_provider, openrouter_model, api_keys, title_generator):
    """Gerar uma parte específica do roteiro"""
    try:
        if ai_provider == 'openrouter':
            if 'openrouter' not in api_keys:
                raise Exception('Chave OpenRouter não fornecida')
            return generate_script_openrouter(prompt, openrouter_model, api_keys['openrouter'])

        elif ai_provider == 'openai':
            if 'openai' not in api_keys:
                raise Exception('Chave OpenAI não fornecida')
            return generate_script_openai(prompt, title_generator)

        else:  # gemini (padrão)
            # Verificar se o Gemini foi configurado corretamente
            if not title_generator.gemini_model:
                gemini_keys = [key for key in api_keys.keys() if key.startswith('gemini')]
                if not gemini_keys:
                    raise Exception('Nenhuma chave Gemini encontrada')
                else:
                    raise Exception('Gemini não foi configurado corretamente')
            return generate_script_gemini(prompt, title_generator)

    except Exception as e:
        print(f"❌ [AGENTE] Erro ao gerar parte: {e}")
        return f"[ERRO NA GERAÇÃO DESTA PARTE: {str(e)}]"

@premise_bp.route('/generate-agent-script', methods=['POST'])
def generate_agent_script():
    """
    🎬 Endpoint específico para o Agente IA de Roteiros
    Gera roteiros extensos baseados em título, premissa e prompt personalizado
    """
    try:
        data = request.get_json()

        # Validar dados obrigatórios
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400

        title = data.get('title', '').strip()
        premise = data.get('premise', '').strip()
        custom_prompt = data.get('custom_prompt', '').strip()
        ai_provider = data.get('ai_provider', 'gemini').lower()
        openrouter_model = data.get('openrouter_model', 'auto')
        api_keys = data.get('api_keys', {})
        num_chapters = data.get('num_chapters', 3)  # Número de capítulos (1-8)

        print(f"🎬 [AGENTE] Iniciando geração de roteiro extenso em partes...")
        print(f"📝 [AGENTE] Título: {title[:100]}...")
        print(f"🎯 [AGENTE] Premissa: {premise[:100]}...")
        print(f"📄 [AGENTE] Prompt personalizado: {len(custom_prompt)} caracteres")
        print(f"📚 [AGENTE] Número de capítulos: {num_chapters}")
        print(f"🤖 [AGENTE] Provider: {ai_provider}")

        if not title:
            return jsonify({
                'success': False,
                'error': 'Título é obrigatório'
            }), 400

        if not premise:
            return jsonify({
                'success': False,
                'error': 'Premissa é obrigatória'
            }), 400

        if not custom_prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt personalizado é obrigatório'
            }), 400

        # Gerar roteiro em partes para contornar limitações de tokens
        print(f"🔄 [AGENTE] Iniciando geração em {2 + num_chapters} partes...")

        script_parts = []
        total_characters = 0

        # Configurar TitleGenerator para usar as chaves fornecidas
        title_generator = TitleGenerator()

        # Configurar chaves de API individualmente
        if api_keys:
            if api_keys.get('openai'):
                title_generator.configure_openai(api_keys['openai'])
            if api_keys.get('openrouter'):
                title_generator.configure_openrouter(api_keys['openrouter'])
            # Configurar Gemini (tentar todas as chaves disponíveis)
            gemini_keys = [key for key in api_keys.keys() if key.startswith('gemini')]
            for gemini_key in gemini_keys:
                if title_generator.configure_gemini(api_keys[gemini_key]):
                    break  # Usar a primeira chave que funcionar

        # PARTE 1: INÍCIO (Abertura + Introdução)
        print(f"📝 [AGENTE] Gerando PARTE 1: INÍCIO...")
        inicio_prompt = create_inicio_prompt(title, premise, custom_prompt)
        inicio_content = generate_script_part(inicio_prompt, ai_provider, openrouter_model, api_keys, title_generator)
        script_parts.append({
            'part': 'INÍCIO',
            'content': inicio_content,
            'characters': len(inicio_content)
        })
        total_characters += len(inicio_content)
        print(f"✅ [AGENTE] INÍCIO gerado: {len(inicio_content)} caracteres")

        # PARTES 2 a N: CAPÍTULOS
        for i in range(1, num_chapters + 1):
            print(f"📖 [AGENTE] Gerando CAPÍTULO {i}/{num_chapters}...")
            capitulo_prompt = create_capitulo_prompt(title, premise, custom_prompt, i, num_chapters)
            capitulo_content = generate_script_part(capitulo_prompt, ai_provider, openrouter_model, api_keys, title_generator)
            script_parts.append({
                'part': f'CAPÍTULO {i}',
                'content': capitulo_content,
                'characters': len(capitulo_content)
            })
            total_characters += len(capitulo_content)
            print(f"✅ [AGENTE] CAPÍTULO {i} gerado: {len(capitulo_content)} caracteres")

        # PARTE FINAL: CONCLUSÃO
        print(f"🏁 [AGENTE] Gerando PARTE FINAL: CONCLUSÃO...")
        final_prompt = create_final_prompt(title, premise, custom_prompt)
        final_content = generate_script_part(final_prompt, ai_provider, openrouter_model, api_keys, title_generator)
        script_parts.append({
            'part': 'CONCLUSÃO',
            'content': final_content,
            'characters': len(final_content)
        })
        total_characters += len(final_content)
        print(f"✅ [AGENTE] CONCLUSÃO gerada: {len(final_content)} caracteres")

        # CONCATENAR TODAS AS PARTES
        print(f"🔗 [AGENTE] Concatenando {len(script_parts)} partes...")
        full_script = "\n\n".join([part['content'] for part in script_parts])

        print(f"🎉 [AGENTE] ROTEIRO COMPLETO GERADO!")
        print(f"📊 [AGENTE] Estatísticas finais:")
        print(f"  - Total de partes: {len(script_parts)}")
        print(f"  - Caracteres totais: {len(full_script)}")
        print(f"  - Palavras estimadas: {len(full_script.split())}")
        print(f"  - Duração estimada: {len(full_script) // 200} minutos")

        for part in script_parts:
            print(f"    • {part['part']}: {part['characters']} chars")

        return jsonify({
            'success': True,
            'script': {
                'title': title,
                'premise': premise,
                'content': full_script,
                'character_count': len(full_script),
                'word_count': len(full_script.split()),
                'estimated_duration_minutes': len(full_script) // 200,
                'parts': script_parts,
                'num_chapters': num_chapters
            },
            'provider_used': ai_provider,
            'generation_method': 'multi_part'
        })

    except Exception as e:
        print(f"❌ [AGENTE] Erro na geração do roteiro: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro na geração do roteiro: {str(e)}'
        }), 500



def generate_script_openrouter(prompt, model, api_key):
    """Gerar roteiro extenso usando OpenRouter"""
    try:
        if model == 'auto':
            model = 'anthropic/claude-3.5-sonnet'

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5173',
            'X-Title': 'Auto Video Producer - Agent Script Generator'
        }

        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json={
                'model': model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Você é um roteirista profissional especializado em seguir EXATAMENTE as instruções de formato fornecidas pelo usuário. Você NUNCA inventa seu próprio formato - sempre segue precisamente o que foi solicitado. Sua especialidade é criar roteiros extensos e detalhados seguindo rigorosamente as especificações fornecidas.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 8000,  # Máximo para roteiros extensos
                'temperature': 0.3  # Menor temperatura para seguir instruções mais fielmente
            },
            timeout=120  # Timeout maior para roteiros extensos
        )

        if response.status_code != 200:
            raise Exception(f'OpenRouter API error: {response.status_code} - {response.text}')

        data = response.json()
        content = data['choices'][0]['message']['content']

        print(f"🔍 [AGENTE] OpenRouter gerou {len(content)} caracteres")
        return content

    except Exception as e:
        raise Exception(f'Erro OpenRouter: {str(e)}')

def generate_script_gemini(prompt, title_generator):
    """Gerar roteiro extenso usando Gemini"""
    try:
        if not title_generator.gemini_model:
            raise Exception('Gemini não configurado')

        print(f"🔍 [AGENTE] Enviando prompt para Gemini ({len(prompt)} chars)...")

        response = title_generator.gemini_model.generate_content(prompt)
        content = response.text

        print(f"🔍 [AGENTE] Gemini gerou {len(content)} caracteres")
        return content

    except Exception as e:
        raise Exception(f'Erro Gemini: {str(e)}')

def generate_script_openai(prompt, title_generator):
    """Gerar roteiro extenso usando OpenAI"""
    try:
        if not title_generator.openai_client:
            raise Exception('OpenAI não configurado')

        response = title_generator.openai_client.chat.completions.create(
            model="gpt-4",  # Usar GPT-4 para roteiros mais extensos
            messages=[
                {"role": "system", "content": "Você é um roteirista profissional especializado em seguir EXATAMENTE as instruções de formato fornecidas pelo usuário. Você NUNCA inventa seu próprio formato - sempre segue precisamente o que foi solicitado. Sua especialidade é criar roteiros extensos e detalhados seguindo rigorosamente as especificações fornecidas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000,  # Máximo para roteiros extensos
            temperature=0.3  # Menor temperatura para seguir instruções mais fielmente
        )

        content = response.choices[0].message.content

        print(f"🔍 [AGENTE] OpenAI gerou {len(content)} caracteres")
        return content

    except Exception as e:
        raise Exception(f'Erro OpenAI: {str(e)}')
