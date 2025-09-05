"""
🎯 Premise Generation Routes
Rotas para geração de premissas de vídeos
"""

from flask import Blueprint, request, jsonify
import requests
import json
import os
import logging
from services.title_generator import TitleGenerator
from utils.error_messages import auto_format_error, format_error_response

# Configurar logger específico para premissas
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = True

def load_api_keys_from_file():
    """Carrega chaves de API do arquivo JSON"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar chaves de API: {e}")
    return {}

def get_default_premise_prompt():
    """Retorna o prompt padrão para geração de premissas"""
    return """# Gerador de Premissas Profissionais para Vídeos

Você é um especialista em criação de conteúdo e storytelling para YouTube. Sua tarefa é criar premissas envolventes e profissionais baseadas nos títulos fornecidos.

## Instruções:
1. Analise cada título fornecido
2. Crie uma premissa única e cativante para cada um
3. A premissa deve ter entre 100-200 palavras
4. Inclua elementos de storytelling (problema, conflito, resolução)
5. Mantenha o tom adequado ao nicho do título
6. Adicione ganchos emocionais e curiosidade

## Formato de Resposta:
Para cada título, forneça:

**TÍTULO:** [título original]
**PREMISSA:**
[Premissa detalhada com storytelling envolvente]

---"""

premise_bp = Blueprint('premise', __name__)

def get_max_tokens_by_size(script_size):
    """Determinar max_tokens baseado no tamanho do roteiro"""
    size_config = {
        'curto': 4000,   # ~2000-3000 palavras
        'medio': 8000,   # ~4000-6000 palavras  
        'longo': 16000   # ~8000-12000 palavras
    }
    return size_config.get(script_size, 8000)  # Default: médio

def get_chapters_by_size(script_size):
    """Determinar número de capítulos baseado no tamanho do roteiro"""
    chapters_config = {
        'curto': 3,    # 3 capítulos para roteiros curtos
        'medio': 6,    # 6 capítulos para roteiros médios
        'longo': 12    # 12 capítulos para roteiros longos
    }
    return chapters_config.get(script_size, 6)  # Default: médio

def get_tokens_per_chapter(script_size):
    """Determinar tokens por capítulo baseado no tamanho do roteiro"""
    tokens_config = {
        'curto': 3000,   # 3000 tokens por capítulo
        'medio': 4000,   # 4000 tokens por capítulo
        'longo': 5000    # 5000 tokens por capítulo
    }
    return tokens_config.get(script_size, 4000)  # Default: médio

def calculate_dynamic_tokens(script_size, num_chapters):
    """Calcular tokens dinamicamente baseado no tamanho e número de capítulos"""
    base_tokens_per_chapter = get_tokens_per_chapter(script_size)
    
    # Margem de segurança baseada no número de capítulos
    safety_margin = 1.1 if num_chapters <= 5 else 1.2 if num_chapters <= 10 else 1.3
    
    # Cálculo dinâmico com margem de segurança
    dynamic_tokens = int(base_tokens_per_chapter * safety_margin)
    
    # Limites mínimos e máximos por tamanho
    limits = {
        'curto': {'min': 2000, 'max': 4000},
        'medio': {'min': 3000, 'max': 6000},
        'longo': {'min': 4000, 'max': 8000}
    }
    
    script_limits = limits.get(script_size, limits['medio'])
    
    # Aplicar limites
    final_tokens = max(script_limits['min'], min(dynamic_tokens, script_limits['max']))
    
    print(f"📊 [TOKENS] Cálculo dinâmico: {script_size}, {num_chapters} caps, base: {base_tokens_per_chapter}, margem: {safety_margin}, final: {final_tokens}")
    
    return final_tokens

def estimate_script_duration(num_chapters, script_size):
    """Estimar duração do roteiro em minutos baseado no número de capítulos e tamanho"""
    # Duração média por capítulo em minutos
    duration_per_chapter = {
        'curto': 3,   # 3 minutos por capítulo
        'medio': 5,   # 5 minutos por capítulo
        'longo': 8    # 8 minutos por capítulo
    }
    
    base_duration = duration_per_chapter.get(script_size, 5)
    total_duration = num_chapters * base_duration
    
    return total_duration

def validate_chapter_quality(content, min_characters=1000):
    """Validar qualidade do capítulo baseado no número de caracteres"""
    if len(content) < min_characters:
        return False, f"Capítulo muito curto: {len(content)} caracteres (mínimo: {min_characters})"
    return True, f"Capítulo válido: {len(content)} caracteres"

def regenerate_chapter_if_needed(prompt, ai_provider, openrouter_model, api_keys, title_generator, script_size, num_chapters, max_attempts=3):
    """Regenerar capítulo se não atender aos critérios de qualidade"""
    min_characters = {
        'curto': 800,
        'medio': 1200,
        'longo': 1500
    }.get(script_size, 1000)
    
    for attempt in range(max_attempts):
        print(f"🔄 [QUALIDADE] Tentativa {attempt + 1}/{max_attempts}...")
        
        # Gerar conteúdo
        content = generate_script_part(prompt, ai_provider, openrouter_model, api_keys, title_generator, script_size, num_chapters)
        
        # Validar qualidade
        is_valid, message = validate_chapter_quality(content, min_characters)
        print(f"📊 [QUALIDADE] {message}")
        
        if is_valid:
            return content
        
        # Se não for válido e não for a última tentativa, ajustar prompt
        if attempt < max_attempts - 1:
            prompt += f"\n\nIMPORTANTE: O capítulo anterior foi muito curto ({len(content)} caracteres). Gere um capítulo mais extenso e detalhado com pelo menos {min_characters} caracteres. Seja mais descritivo e inclua mais detalhes narrativos."
    
    # Se todas as tentativas falharam, retornar o último conteúdo gerado
    print(f"⚠️ [QUALIDADE] Todas as {max_attempts} tentativas falharam. Usando último conteúdo gerado.")
    return content

@premise_bp.route('/generate', methods=['POST'])
def generate_premises():
    """Gerar premissas baseadas nos títulos fornecidos"""
    try:
        logger.info(f"🎯 [PREMISE] Iniciando geração de premissas...")
        data = request.get_json()
        titles = data.get('titles', [])
        prompt = data.get('prompt', '')
        ai_provider = data.get('ai_provider', 'auto')
        openrouter_model = data.get('openrouter_model', 'auto')
        api_keys = data.get('api_keys', {})
        script_size = data.get('script_size', 'medio')
        use_custom_prompt = data.get('use_custom_prompt', False)
        custom_prompt = data.get('custom_prompt', '')
        
        logger.info(f"🔍 [PREMISE] Parâmetros recebidos: títulos={len(titles)}, provider={ai_provider}, size={script_size}")
        
        # Carregar chaves de API do arquivo se não foram fornecidas
        if not api_keys:
            api_keys = load_api_keys_from_file()
            logger.info(f"🔑 [PREMISE] Chaves carregadas do arquivo: {list(api_keys.keys())}")

        if not titles:
            logger.error(f"❌ [PREMISE] Erro: Nenhum título fornecido")
            return jsonify({
                'success': False,
                'error': 'Nenhum título fornecido'
            }), 400
        
        # Carregar prompt personalizado se solicitado
        if use_custom_prompt and custom_prompt:
            # Usar prompt personalizado fornecido
            final_prompt = custom_prompt
            logger.info(f"🎯 [PREMISE] Usando prompt personalizado fornecido ({len(custom_prompt)} caracteres)")
        elif use_custom_prompt:
            # Carregar prompt personalizado do arquivo de configuração
            try:
                from routes.prompts_config import load_prompts_config
                prompts_config = load_prompts_config()
                premise_config = prompts_config.get('premises', {})
                final_prompt = premise_config.get('prompt', '')
                
                if final_prompt:
                    logger.info(f"🎯 [PREMISE] Usando prompt personalizado do arquivo de configuração")
                else:
                    logger.warning(f"⚠️ [PREMISE] Prompt personalizado não encontrado, usando prompt padrão")
                    final_prompt = prompt or get_default_premise_prompt()
            except Exception as e:
                logger.error(f"❌ [PREMISE] Erro ao carregar prompt personalizado: {e}")
                final_prompt = prompt or get_default_premise_prompt()
        else:
            # Usar prompt fornecido ou padrão
            final_prompt = prompt or get_default_premise_prompt()
            logger.info(f"🎯 [PREMISE] Usando prompt padrão")
        
        # Substituir variáveis no prompt se necessário
        if '{titles}' in final_prompt:
            titles_text = '\n'.join(f'{i+1}. {title}' for i, title in enumerate(titles))
            final_prompt = final_prompt.replace('{titles}', titles_text)
        elif not final_prompt.endswith('\n\n'):
            # Adicionar títulos ao final se não estão incluídos no prompt
            titles_text = '\n'.join(f'{i+1}. {title}' for i, title in enumerate(titles))
            final_prompt = f"{final_prompt}\n\n## Títulos para análise:\n{titles_text}"

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
        
        logger.info(f"🚀 [PREMISE] Iniciando geração com provider: {ai_provider}")
        
        if ai_provider == 'auto':
            # Tentar em ordem de prioridade
            providers = ['openrouter', 'gemini', 'openai']
            success = False
            
            for provider in providers:
                try:
                    logger.info(f"🔄 [PREMISE] Tentando provider: {provider}")
                    if provider == 'openrouter' and api_keys.get('openrouter'):
                        logger.info(f"🔑 [PREMISE] Usando OpenRouter com modelo: {openrouter_model}")
                        premises = generate_premises_openrouter(titles, final_prompt, openrouter_model, api_keys['openrouter'], script_size)
                        logger.info(f"✅ [PREMISE] OpenRouter gerou {len(premises)} premissas")
                        success = True
                        break
                    elif provider == 'gemini' and (api_keys.get('gemini') or api_keys.get('gemini_1')):
                        logger.info(f"🔑 [PREMISE] Usando Gemini")
                        premises = generate_premises_gemini(titles, final_prompt, title_generator, script_size)
                        logger.info(f"✅ [PREMISE] Gemini gerou {len(premises)} premissas")
                        success = True
                        break
                    elif provider == 'openai' and api_keys.get('openai'):
                        logger.info(f"🔑 [PREMISE] Usando OpenAI")
                        premises = generate_premises_openai(titles, final_prompt, title_generator, script_size)
                        logger.info(f"✅ [PREMISE] OpenAI gerou {len(premises)} premissas")
                        success = True
                        break
                    else:
                        logger.warning(f"⚠️ [PREMISE] Provider {provider} não disponível ou sem chave")
                except Exception as e:
                    logger.error(f"❌ [PREMISE] Erro com {provider}: {e}")
                    import traceback
                    logger.error(f"📋 [PREMISE] Traceback: {traceback.format_exc()}")
                    continue
            
            if not success:
                logger.error(f"❌ [PREMISE] Nenhum provider conseguiu gerar premissas")
                return jsonify({
                    'success': False,
                    'error': 'Nenhuma IA disponível conseguiu gerar premissas'
                }), 500
                
        elif ai_provider == 'openrouter':
            if not api_keys.get('openrouter'):
                logger.error(f"❌ [PREMISE] Chave OpenRouter não configurada")
                return jsonify({
                    'success': False,
                    'error': 'Chave da API OpenRouter não configurada'
                }), 400
            logger.info(f"🔑 [PREMISE] Usando OpenRouter exclusivamente")
            premises = generate_premises_openrouter(titles, final_prompt, openrouter_model, api_keys['openrouter'], script_size)
            
        elif ai_provider == 'gemini':
            gemini_key = api_keys.get('gemini') or api_keys.get('gemini_1')
            if not gemini_key:
                logger.error(f"❌ [PREMISE] Chave Gemini não configurada")
                return jsonify({
                    'success': False,
                    'error': 'Chave da API Gemini não configurada'
                }), 400
            print(f"🔑 [PREMISE] Usando Gemini exclusivamente")
            premises = generate_premises_gemini(titles, final_prompt, title_generator, script_size)
            
        elif ai_provider == 'openai':
            if not api_keys.get('openai'):
                print(f"❌ [PREMISE] Chave OpenAI não configurada")
                return jsonify({
                    'success': False,
                    'error': 'Chave da API OpenAI não configurada'
                }), 400
            print(f"🔑 [PREMISE] Usando OpenAI exclusivamente")
            premises = generate_premises_openai(titles, final_prompt, title_generator, script_size)

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
        print(f"❌ [PREMISE] Erro na geração de premissas: {e}")
        import traceback
        print(f"📋 [PREMISE] Traceback completo: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_premises_openrouter(titles, prompt, model, api_key, script_size='medio'):
    """Gerar premissas usando OpenRouter"""
    try:
        # Mapear modelo automático para o melhor disponível
        if model == 'auto':
            model = 'anthropic/claude-3.5-sonnet'
        
        # Determinar max_tokens baseado no tamanho
        max_tokens = get_max_tokens_by_size(script_size)
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5173',
            'X-Title': 'Auto Video Producer'
        }
        
        # Adicionar instruções de tamanho ao prompt do sistema
        size_instructions = {
            'curto': 'Crie um roteiro CURTO de aproximadamente 1500-2000 palavras.',
            'medio': 'Crie um roteiro de tamanho MÉDIO de aproximadamente 3500-5000 palavras.',
            'longo': 'Crie um roteiro LONGO e detalhado de aproximadamente 7000-10000 palavras.'
        }
        
        system_content = f'Você é um especialista em criação de conteúdo e storytelling para YouTube. {size_instructions.get(script_size, size_instructions["medio"])}'
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json={
                'model': model,
                'messages': [
                    {
                        'role': 'system',
                        'content': system_content
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': max_tokens,
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

def generate_content_with_gemini_retry(prompt):
    """Gerar conteúdo usando Gemini com retry automático entre múltiplas chaves"""
    import google.generativeai as genai
    from routes.automations import get_next_gemini_key, handle_gemini_429_error, get_gemini_keys_count
    
    # Tentar múltiplas chaves se necessário
    # Usar a quantidade real de chaves disponíveis
    max_key_attempts = get_gemini_keys_count() if get_gemini_keys_count() > 0 else 1
    print(f"🔑 Usando {max_key_attempts} chaves Gemini para premissas")
    last_error = None
    
    for attempt in range(max_key_attempts):
        try:
            # Obter chave Gemini
            api_key = get_next_gemini_key()
            if not api_key:
                raise Exception('Nenhuma chave Gemini disponível. Configure pelo menos uma chave nas Configurações.')
            
            print(f"🔄 Tentativa {attempt + 1}: Usando chave Gemini para premissas")
            
            # Configurar Gemini diretamente
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            print(f"🔍 DEBUG: Enviando prompt para Gemini ({len(prompt)} chars) - Tentativa {attempt + 1}")
            response = model.generate_content(prompt)
            print(f"🔍 DEBUG: Gemini respondeu com {len(response.text)} caracteres")
            return response.text
            
        except Exception as e:
            error_str = str(e)
            last_error = error_str
            print(f"❌ Tentativa {attempt + 1} falhou: {error_str}")
            
            # Se é erro 429 (quota exceeded), tentar próxima chave
            if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
                print(f"🔄 Erro de cota detectado, tentando próxima chave...")
                handle_gemini_429_error(error_str, api_key)
                continue
            else:
                # Outros erros, não tentar novamente
                print(f"🛑 Erro não relacionado à cota, parando tentativas")
                break
    
    # Se chegou aqui, todas as tentativas falharam
    final_error = f'Todas as {max_key_attempts} chaves Gemini falharam. Último erro: {last_error}'
    print(f"❌ DEBUG: {final_error}")
    raise Exception(f'Erro Gemini: {final_error}')

def generate_premises_gemini(titles, prompt, title_generator, script_size='medio'):
    """Gerar premissas usando Gemini com cache e fallback automático"""
    try:
        from routes.automations import handle_gemini_429_error, check_gemini_availability, get_fallback_provider_info
        import hashlib
        import json
        import os
        from datetime import datetime, timedelta
        
        # Sistema de cache simples
        cache_dir = "cache/gemini_premises"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Gerar hash do prompt + títulos para cache
        cache_key = f"{prompt}_{str(titles)}_{script_size}"
        prompt_hash = hashlib.md5(cache_key.encode()).hexdigest()
        cache_file = os.path.join(cache_dir, f"{prompt_hash}.json")
        
        # Verificar cache (válido por 6 horas para premissas)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cache_time < timedelta(hours=6):
                    print(f"📦 [CACHE] Usando premissas em cache para Gemini ({len(cache_data['premises'])} premissas)")
                    return cache_data['premises']
            except Exception as e:
                print(f"⚠️ [CACHE] Erro ao ler cache de premissas: {e}")
        
        # Verificar disponibilidade do Gemini
        if not check_gemini_availability():
            print("⚠️ [GEMINI] Todas as chaves Gemini esgotadas, usando fallback para premissas")
            fallback_info = get_fallback_provider_info()
            if fallback_info:
                if fallback_info['provider'] == 'openai':
                    return generate_premises_openai(titles, prompt, title_generator, script_size)
                elif fallback_info['provider'] == 'openrouter':
                    return generate_premises_openrouter(titles, prompt, fallback_info['key'], script_size)
            raise Exception('Gemini esgotado e nenhum fallback disponível para premissas')
        
        if not title_generator.gemini_model:
            raise Exception('Gemini não configurado')

        # Adicionar instruções de tamanho ao prompt
        size_instructions = {
            'curto': 'Crie um roteiro CURTO de aproximadamente 1500-2000 palavras.',
            'medio': 'Crie um roteiro de tamanho MÉDIO de aproximadamente 3500-5000 palavras.',
            'longo': 'Crie um roteiro LONGO e detalhado de aproximadamente 7000-10000 palavras.'
        }
        
        enhanced_prompt = f"{size_instructions.get(script_size, size_instructions['medio'])}\n\n{prompt}"
        
        print(f"🔍 DEBUG: Prompt enviado para Gemini (primeiros 500 chars): {enhanced_prompt[:500]}...")

        # Implementar retry automático para Gemini
        content = generate_content_with_gemini_retry(enhanced_prompt)

        premises = parse_premises_response(content, titles)
        
        # Salvar no cache
        try:
            cache_data = {
                'premises': premises,
                'timestamp': datetime.now().isoformat(),
                'prompt_hash': prompt_hash,
                'script_size': script_size
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"📦 [CACHE] Premissas salvas no cache")
        except Exception as e:
            print(f"⚠️ [CACHE] Erro ao salvar cache de premissas: {e}")

        return premises

    except Exception as e:
        error_str = str(e)
        
        # Tratar erro 429 especificamente
        if '429' in error_str or 'quota' in error_str.lower() or 'exceeded' in error_str.lower():
            print(f"🚫 [GEMINI] Erro 429 detectado nas premissas: {error_str}")
            # Nota: O tratamento do erro 429 já é feito internamente pela função generate_content_with_gemini_retry
            # que chama handle_gemini_429_error com a chave correta
            
            # Tentar fallback automático
            try:
                from routes.automations import get_fallback_provider_info
                fallback_info = get_fallback_provider_info()
                if fallback_info:
                    print(f"🔄 [FALLBACK] Usando {fallback_info['provider']} como fallback para premissas")
                    if fallback_info['provider'] == 'openai':
                        return generate_premises_openai(titles, prompt, title_generator, script_size)
                    elif fallback_info['provider'] == 'openrouter':
                        return generate_premises_openrouter(titles, prompt, fallback_info['key'], script_size)
            except Exception as fallback_error:
                print(f"❌ [FALLBACK] Erro no fallback das premissas: {fallback_error}")
        
        raise Exception(f'Erro Gemini: {error_str}')

def generate_premises_openai(titles, prompt, title_generator, script_size='medio'):
    """Gerar premissas usando OpenAI"""
    try:
        if not title_generator.openai_client:
            raise Exception('OpenAI não configurado')
        
        # Determinar max_tokens baseado no tamanho
        max_tokens = get_max_tokens_by_size(script_size)
        
        # Adicionar instruções de tamanho ao prompt do sistema
        size_instructions = {
            'curto': 'Crie um roteiro CURTO de aproximadamente 1500-2000 palavras.',
            'medio': 'Crie um roteiro de tamanho MÉDIO de aproximadamente 3500-5000 palavras.',
            'longo': 'Crie um roteiro LONGO e detalhado de aproximadamente 7000-10000 palavras.'
        }
        
        system_content = f'Você é um especialista em criação de conteúdo e storytelling para YouTube. {size_instructions.get(script_size, size_instructions["medio"])}'
        
        response = title_generator.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
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
def create_inicio_prompt(title, premise, custom_prompt, script_size='medio'):
    """Criar prompt limpo para a parte INÍCIO"""
    duration_instructions = {
        'curto': "Gere uma introdução de 2-3 minutos com apresentação concisa dos elementos principais.",
        'medio': "Gere uma introdução de 4-6 minutos com desenvolvimento adequado dos elementos iniciais.",
        'longo': "Gere uma introdução de 8-12 minutos com apresentação detalhada e extensa dos elementos principais. Seja extremamente detalhado e descritivo."
    }
    
    return f"""## INFORMAÇÕES DO PROJETO:
### TÍTULO: {title}
### PREMISSA: {premise}
### 🎭 Prompt Personalizado do Agente:
{custom_prompt}

## INSTRUÇÃO ESPECÍFICA:
Gere a parte INICIAL do roteiro (aproximadamente 25% do roteiro total) seguindo EXATAMENTE o formato especificado no prompt personalizado acima. Esta é a PRIMEIRA parte de um roteiro maior.

### DURAÇÃO ALVO: {duration_instructions.get(script_size, duration_instructions['medio'])}

**IMPORTANTE:** Seja detalhado, extenso e minucioso na descrição de cenários, personagens, ações e diálogos."""

def create_capitulo_prompt(title, premise, custom_prompt, capitulo_num, total_capitulos, script_size='medio'):
    """Criar prompt limpo para um capítulo"""
    duration_instructions = {
        'curto': "Gere um capítulo de 2-4 minutos com desenvolvimento focado e direto.",
        'medio': "Gere um capítulo de 4-7 minutos com desenvolvimento equilibrado e detalhado.",
        'longo': "Gere um capítulo de 8-12 minutos com desenvolvimento extenso e extremamente detalhado. Inclua descrições minuciosas de cenários, ações, diálogos e elementos visuais."
    }
    
    return f"""## INFORMAÇÕES DO PROJETO:
### TÍTULO: {title}
### PREMISSA: {premise}
### 🎭 Prompt Personalizado do Agente:
{custom_prompt}

## INSTRUÇÃO ESPECÍFICA:
Gere o CAPÍTULO {capitulo_num} de {total_capitulos} do desenvolvimento do roteiro seguindo EXATAMENTE o formato especificado no prompt personalizado acima. Esta é uma parte INTERMEDIÁRIA de um roteiro maior.

### DURAÇÃO ALVO: {duration_instructions.get(script_size, duration_instructions['medio'])}

**IMPORTANTE:** Seja detalhado, extenso e minucioso. Cada capítulo deve ter conteúdo substancial e rico em detalhes."""

def create_final_prompt(title, premise, custom_prompt, script_size='medio'):
    """Criar prompt limpo para a parte FINAL"""
    duration_instructions = {
        'curto': "Gere uma conclusão de 2-3 minutos com fechamento conciso e satisfatório.",
        'medio': "Gere uma conclusão de 4-6 minutos com fechamento bem desenvolvido e completo.",
        'longo': "Gere uma conclusão de 8-12 minutos com fechamento extenso, detalhado e extremamente satisfatório. Inclua todos os elementos de resolução de forma minuciosa."
    }
    
    return f"""## INFORMAÇÕES DO PROJETO:
### TÍTULO: {title}
### PREMISSA: {premise}
### 🎭 Prompt Personalizado do Agente:
{custom_prompt}

## INSTRUÇÃO ESPECÍFICA:
Gere a parte FINAL do roteiro (aproximadamente 25% final do roteiro total) seguindo EXATAMENTE o formato especificado no prompt personalizado acima. Esta é a ÚLTIMA parte que finaliza todo o roteiro.

### DURAÇÃO ALVO: {duration_instructions.get(script_size, duration_instructions['medio'])}

**IMPORTANTE:** Seja detalhado, extenso e minucioso na conclusão. Garanta um fechamento rico e satisfatório."""

def generate_script_part(prompt, ai_provider, openrouter_model, api_keys, title_generator, script_size='medio', num_chapters=6):
    """Gerar uma parte específica do roteiro com tokens dinâmicos"""
    try:
        # Calcular tokens dinamicamente
        dynamic_tokens = calculate_dynamic_tokens(script_size, num_chapters)
        
        if ai_provider == 'openrouter':
            if 'openrouter' not in api_keys:
                raise Exception('Chave OpenRouter não fornecida')
            return generate_script_openrouter_with_tokens(prompt, openrouter_model, api_keys['openrouter'], dynamic_tokens)

        elif ai_provider == 'openai':
            if 'openai' not in api_keys:
                raise Exception('Chave OpenAI não fornecida')
            return generate_script_openai_with_tokens(prompt, title_generator, dynamic_tokens)

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
    🎬 Endpoint específico para Storyteller Unlimited
    Gera roteiros extensos usando agentes especializados com MemoryBridge
    """
    try:
        from services.storyteller_service import StorytellerService
        
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
        detailed_prompt_text = data.get('detailed_prompt_text', '').strip()
        api_keys = data.get('api_keys', {})
        
        # Parâmetros do Storyteller
        agent = data.get('storyteller_agent', 'millionaire_stories')
        num_chapters = data.get('num_chapters', 5)
        target_words = data.get('target_words', 2500)
        script_size = data.get('script_size', 'medio')
        
        print(f"🎬 [STORYTELLER_AGENT] Iniciando geração com Storyteller Unlimited...")
        print(f"📝 Título: {title[:100]}...")
        print(f"🎯 Premissa: {premise[:100]}...")
        print(f"🤖 Agente: {agent}")
        print(f"📚 Capítulos: {num_chapters}")

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

        # Preparar a premissa com contexto para Storyteller
        full_premise = f"""Título: {title}

Premissa: {premise}

{'Contexto Adicional: ' + custom_prompt if custom_prompt else ''}

{'Detalhes Específicos: ' + detailed_prompt_text if detailed_prompt_text else ''}

Crie um roteiro cinematográfico profissional com {num_chapters} capítulos, explorando nuances emocionais e arcos de personagens bem desenvolvidos."""

        # Configurar parâmetros do Storyteller baseado no tamanho
        if script_size == 'curto':
            target_words = 1500
        elif script_size == 'longo':
            target_words = 4000
        elif script_size == 'epico':
            target_words = 6000
        else:  # medio
            target_words = 2500

        # Inicializar Storyteller Service
        from services.storyteller_service import StorytellerService
        storyteller_service = StorytellerService()

        # Gerar roteiro com Storyteller Unlimited
        print(f"🎬 [STORYTELLER_AGENT] Gerando roteiro com agente especializado...")
        script_result = storyteller_service.generate_storyteller_script(
            title=title,
            premise=full_premise,
            agent_type='millionaire_stories',  # Usar agente especializado para roteiros ricos
            num_chapters=num_chapters,
            provider='gemini'
        )

        # Formatar resultado para compatibilidade
        if script_result and script_result.get('full_script'):
            script_content = script_result['full_script']
            chapters = script_result.get('chapters', [])
            
            # Criar estrutura de partes para compatibilidade
            script_parts = []
            if chapters:
                for i, chapter in enumerate(chapters):
                    script_parts.append({
                        'part': f'CAPÍTULO {i+1}',
                        'content': chapter.get('content', ''),
                        'characters': len(chapter.get('content', ''))
                    })
            else:
                # Se não houver capítulos, dividir por parágrafos duplos
                if '\n\n' in script_content:
                    parts = script_content.split('\n\n')
                    for i, part in enumerate(parts):
                        if part.strip():
                            script_parts.append({
                                'part': f'PARTE {i+1}',
                                'content': part.strip(),
                                'characters': len(part.strip())
                            })
                else:
                    script_parts.append({
                        'part': 'ROTEIRO COMPLETO',
                        'content': script_content,
                        'characters': len(script_content)
                    })

            return jsonify({
                'success': True,
                'script': {
                    'title': title,
                    'premise': premise,
                    'content': script_content,
                    'character_count': script_result.get('total_characters', len(script_content)),
                    'word_count': len(script_content.split()),
                    'estimated_duration_minutes': script_result.get('estimated_duration', len(script_content) // 200),
                    'parts': script_parts,
                    'num_chapters': len(script_parts)
                },
                'system_used': 'storyteller_unlimited',
                'generation_method': 'storyteller_agent',
                'agent_used': 'millionaire_stories'
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
                'max_tokens': 12000,  # Máximo aumentado para roteiros extensos
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

def generate_script_openrouter_with_tokens(prompt, model, api_key, max_tokens):
    """Gerar roteiro usando OpenRouter com tokens dinâmicos"""
    try:
        if model == 'auto':
            model = 'anthropic/claude-3.5-sonnet'

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5173',
            'X-Title': 'Auto Video Producer - Dynamic Script Generator'
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
                'max_tokens': max_tokens,
                'temperature': 0.3
            },
             timeout=120  # Timeout maior para roteiros extensos
        )

        if response.status_code != 200:
            raise Exception(f'OpenRouter API error: {response.status_code} - {response.text}')

        data = response.json()
        content = data['choices'][0]['message']['content']

        print(f"🔍 [AGENTE] OpenRouter com tokens dinâmicos gerou {len(content)} caracteres (max_tokens: {max_tokens})")
        return content

    except Exception as e:
        raise Exception(f'Erro OpenRouter dinâmico: {str(e)}')

def generate_script_openai_with_tokens(prompt, title_generator, max_tokens):
    """Gerar roteiro usando OpenAI com tokens dinâmicos"""
    try:
        if not title_generator.openai_client:
            raise Exception('OpenAI não configurado')

        response = title_generator.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um roteirista profissional especializado em seguir EXATAMENTE as instruções de formato fornecidas pelo usuário. Você NUNCA inventa seu próprio formato - sempre segue precisamente o que foi solicitado. Sua especialidade é criar roteiros extensos e detalhados seguindo rigorosamente as especificações fornecidas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3
        )

        content = response.choices[0].message.content
        print(f"🔍 [AGENTE] OpenAI com tokens dinâmicos gerou {len(content)} caracteres (max_tokens: {max_tokens})")
        return content

    except Exception as e:
        raise Exception(f'Erro OpenAI dinâmico: {str(e)}')

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
                'max_tokens': 12000,  # Máximo aumentado para roteiros extensos
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
    """Gerar roteiro extenso usando Gemini com cache e fallback automático"""
    try:
        from routes.automations import handle_gemini_429_error, check_gemini_availability, get_fallback_provider_info
        import hashlib
        import json
        import os
        from datetime import datetime, timedelta
        
        # Sistema de cache simples
        cache_dir = "cache/gemini_scripts"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Gerar hash do prompt para cache
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        cache_file = os.path.join(cache_dir, f"{prompt_hash}.json")
        
        # Verificar cache (válido por 24 horas)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cache_time < timedelta(hours=24):
                    print(f"📦 [CACHE] Usando resposta em cache para Gemini ({len(cache_data['content'])} chars)")
                    return cache_data['content']
            except Exception as e:
                print(f"⚠️ [CACHE] Erro ao ler cache: {e}")
        
        # Verificar disponibilidade do Gemini
        if not check_gemini_availability():
            print("⚠️ [GEMINI] Todas as chaves Gemini esgotadas, usando fallback")
            fallback_info = get_fallback_provider_info()
            if fallback_info:
                print(f"🔄 [FALLBACK] Configurando {fallback_info['provider']} com chave: {fallback_info['key'][:10]}...")
                if fallback_info['provider'] == 'openai':
                    # Configurar TitleGenerator com chave OpenAI do fallback
                    title_generator.configure_openai(fallback_info['key'])
                    return generate_script_openai(prompt, title_generator)
                elif fallback_info['provider'] == 'openrouter':
                    # Configurar TitleGenerator com chave OpenRouter do fallback
                    title_generator.configure_openrouter(fallback_info['key'])
                    return generate_script_openrouter(prompt, 'anthropic/claude-3.5-sonnet', fallback_info['key'])
            raise Exception('Gemini esgotado e nenhum fallback disponível')
        
        if not title_generator.gemini_model:
            raise Exception('Gemini não configurado')

        print(f"🔍 [AGENTE] Enviando prompt para Gemini ({len(prompt)} chars)...")

        content = generate_content_with_gemini_retry(prompt)

        # Salvar no cache
        try:
            cache_data = {
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'prompt_hash': prompt_hash
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"📦 [CACHE] Resposta salva no cache")
        except Exception as e:
            print(f"⚠️ [CACHE] Erro ao salvar cache: {e}")

        print(f"🔍 [AGENTE] Gemini gerou {len(content)} caracteres")
        return content

    except Exception as e:
        error_str = str(e)
        
        # Tratar erro 429 especificamente
        if '429' in error_str or 'quota' in error_str.lower() or 'exceeded' in error_str.lower():
            print(f"🚫 [GEMINI] Erro 429 detectado: {error_str}")
            # Nota: O tratamento do erro 429 já é feito internamente pela função generate_content_with_gemini_retry
            # que chama handle_gemini_429_error com a chave correta
            
            # Tentar fallback automático
            try:
                from routes.automations import get_fallback_provider_info
                fallback_info = get_fallback_provider_info()
                if fallback_info:
                    print(f"🔄 [FALLBACK] Usando {fallback_info['provider']} como fallback com chave: {fallback_info['key'][:10]}...")
                    if fallback_info['provider'] == 'openai':
                        # Configurar TitleGenerator com chave OpenAI do fallback
                        title_generator.configure_openai(fallback_info['key'])
                        return generate_script_openai(prompt, title_generator)
                    elif fallback_info['provider'] == 'openrouter':
                        # Configurar TitleGenerator com chave OpenRouter do fallback
                        title_generator.configure_openrouter(fallback_info['key'])
                        return generate_script_openrouter(prompt, 'anthropic/claude-3.5-sonnet', fallback_info['key'])
            except Exception as fallback_error:
                print(f"❌ [FALLBACK] Erro no fallback: {fallback_error}")
        
        raise Exception(f'Erro Gemini: {error_str}')

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
            max_tokens=12000,  # Máximo aumentado para roteiros extensos
            temperature=0.3  # Menor temperatura para seguir instruções mais fielmente
        )

        content = response.choices[0].message.content

        print(f"🔍 [AGENTE] OpenAI gerou {len(content)} caracteres")
        return content

    except Exception as e:
        raise Exception(f'Erro OpenAI: {str(e)}')


def generate_script_in_parts(title, premise, prompt, ai_provider, openrouter_model, api_keys, script_size='longo'):
    """Gerar roteiro longo dividido em 4 partes para contornar limitações de tokens"""
    try:
        print(f"🔄 [PARTS] Iniciando geração em partes para roteiro longo...")
        
        # Configurar TitleGenerator
        title_generator = TitleGenerator()
        if api_keys:
            if api_keys.get('openai'):
                title_generator.configure_openai(api_keys['openai'])
            if api_keys.get('openrouter'):
                title_generator.configure_openrouter(api_keys['openrouter'])
            gemini_keys = [key for key in api_keys.keys() if key.startswith('gemini')]
            for gemini_key in gemini_keys:
                if title_generator.configure_gemini(api_keys[gemini_key]):
                    break
        
        # Definir estrutura das partes com tokens aumentados para roteiros longos
        parts_config = [
            {
                'name': 'INTRODUÇÃO',
                'percentage': 25,
                'max_tokens': 4000,  # Aumentado para gerar mais conteúdo
                'description': 'Abertura detalhada, contexto extenso e apresentação completa do tema principal. Seja extremamente descritivo e envolvente.'
            },
            {
                'name': 'DESENVOLVIMENTO',
                'percentage': 40,
                'max_tokens': 6000,  # Aumentado significativamente
                'description': 'Desenvolvimento extenso e detalhado do conteúdo principal, argumentos elaborados, exemplos práticos e detalhes minuciosos.'
            },
            {
                'name': 'CLÍMAX',
                'percentage': 25,
                'max_tokens': 4000,  # Aumentado para mais impacto
                'description': 'Ponto alto extremamente detalhado, reviravoltas elaboradas e momentos mais impactantes com descrições ricas.'
            },
            {
                'name': 'CONCLUSÃO',
                'percentage': 10,
                'max_tokens': 2000,  # Dobrado para conclusão mais rica
                'description': 'Fechamento extenso e satisfatório, resumo detalhado e call-to-action envolvente.'
            }
        ]
        
        script_parts = []
        previous_context = ""
        
        for i, part_config in enumerate(parts_config):
            part_name = part_config['name']
            print(f"📝 [PARTS] Gerando {part_name} ({i+1}/4)...")
            
            # Criar prompt específico para esta parte
            part_prompt = create_part_prompt(
                title, premise, prompt, part_config, 
                previous_context, i+1, len(parts_config)
            )
            
            # Gerar conteúdo da parte
            part_content = generate_script_part_with_tokens(
                part_prompt, ai_provider, openrouter_model, 
                api_keys, title_generator, part_config['max_tokens']
            )
            
            # Armazenar parte
            part_data = {
                'name': part_name,
                'content': part_content,
                'characters': len(part_content),
                'words': len(part_content.split()),
                'percentage': part_config['percentage']
            }
            script_parts.append(part_data)
            
            # Atualizar contexto para próxima parte
            previous_context = create_context_summary(part_content, part_name)
            
            print(f"✅ [PARTS] {part_name} gerada: {len(part_content)} caracteres")
        
        # Unir todas as partes
        full_script = join_script_parts(script_parts)
        
        print(f"🎉 [PARTS] Roteiro completo gerado!")
        print(f"📊 [PARTS] Estatísticas:")
        print(f"  - Total de caracteres: {len(full_script)}")
        print(f"  - Total de palavras: {len(full_script.split())}")
        print(f"  - Duração estimada: {len(full_script) // 200} minutos")
        
        return {
            'success': True,
            'script': full_script,
            'parts': script_parts,
            'total_characters': len(full_script),
            'total_words': len(full_script.split()),
            'generation_method': 'parts_generation'
        }
        
    except Exception as e:
        print(f"❌ [PARTS] Erro na geração em partes: {e}")
        raise Exception(f'Erro na geração em partes: {str(e)}')


def join_script_parts(script_parts):
    """Unir as partes do roteiro de forma inteligente"""
    try:
        print(f"🔗 [JOIN] Unindo {len(script_parts)} partes do roteiro...")
        
        joined_content = []
        
        for i, part in enumerate(script_parts):
            part_content = part['content'].strip()
            
            # Adicionar separador visual entre partes (exceto na primeira)
            if i > 0:
                joined_content.append("\n\n" + "="*50 + "\n\n")
            
            # Adicionar título da seção
            joined_content.append(f"## {part['name']}\n\n")
            
            # Adicionar conteúdo da parte
            joined_content.append(part_content)
            
            print(f"🔗 [JOIN] Parte {part['name']} adicionada ({part['characters']} chars)")
        
        full_script = "".join(joined_content)
        
        print(f"✅ [JOIN] Roteiro unido com sucesso: {len(full_script)} caracteres")
        return full_script
        
    except Exception as e:
        print(f"❌ [JOIN] Erro ao unir partes: {e}")
        raise Exception(f'Erro ao unir partes: {str(e)}')


def create_part_prompt(title, premise, base_prompt, part_config, previous_context, part_number, total_parts):
    """Criar prompt específico para uma parte do roteiro"""
    part_name = part_config['name']
    description = part_config['description']
    percentage = part_config['percentage']
    
    context_section = ""
    if previous_context:
        context_section = f"""

📋 CONTEXTO DAS PARTES ANTERIORES:
{previous_context}

IMPORTANTE: Mantenha a continuidade e coerência com o que já foi desenvolvido.
"""
    
    part_prompt = f"""
🎬 GERAÇÃO DE ROTEIRO - PARTE {part_number}/{total_parts}: {part_name}

📝 TÍTULO: {title}

📖 PREMISSA: {premise}

🎯 INSTRUÇÕES ESPECÍFICAS:
{base_prompt}

📋 FOCO DESTA PARTE ({part_name}):
{description}

📊 ESPECIFICAÇÕES:
- Esta é a parte {part_number} de {total_parts} do roteiro completo
- Deve representar aproximadamente {percentage}% do conteúdo total
- Foque especificamente em: {description}
- Mantenha tom e estilo consistentes
{context_section}

🎯 INSTRUÇÕES DE FORMATO:
- Escreva APENAS o conteúdo desta seção específica
- NÃO inclua títulos de seção ou marcadores
- NÃO repita informações das partes anteriores
- Mantenha fluidez narrativa para conectar com próximas partes
- Use linguagem envolvente e adequada para YouTube

📝 GERE AGORA O CONTEÚDO DA {part_name}:
"""
    
    return part_prompt


def create_context_summary(part_content, part_name):
    """Criar resumo do contexto para a próxima parte"""
    try:
        # Pegar os últimos 300 caracteres da parte para contexto
        context_snippet = part_content[-300:] if len(part_content) > 300 else part_content
        
        # Criar resumo estruturado
        summary = f"""
{part_name} (últimos elementos):
{context_snippet.strip()}

Tom estabelecido: Mantenha a mesma linguagem e estilo narrativo.
"""
        
        return summary
        
    except Exception as e:
        print(f"⚠️ [CONTEXT] Erro ao criar resumo: {e}")
        return f"{part_name} foi concluída. Continue com o mesmo tom e estilo."


def generate_script_part_with_tokens(prompt, ai_provider, openrouter_model, api_keys, title_generator, max_tokens):
    """Gerar uma parte específica do roteiro com hierarquia otimizada: Gemini → OpenRouter → OpenAI"""
    try:
        # Executar reset diário automático
        daily_reset_quota()
        
        # Se provider específico foi solicitado, tentar primeiro
        if ai_provider == 'openrouter' and api_keys.get('openrouter'):
            return generate_script_part_openrouter(prompt, openrouter_model, api_keys['openrouter'], max_tokens)
        elif ai_provider == 'gemini' and title_generator.gemini_model:
            return generate_script_part_gemini(prompt, title_generator)
        elif ai_provider == 'openai' and title_generator.openai_client:
            return generate_script_part_openai(prompt, title_generator, max_tokens)
        
        # Sistema de fallback otimizado com hierarquia: Gemini → OpenRouter → OpenAI
        print("🔄 [FALLBACK] Iniciando sistema de fallback otimizado para geração de parte")
        
        # 1. Tentar Gemini primeiro (prioridade 1)
        if title_generator.gemini_model:
            try:
                from routes.automations import check_gemini_availability
                if check_gemini_availability():
                    print("✅ [FALLBACK] Usando Gemini (prioridade 1)")
                    return generate_script_part_gemini(prompt, title_generator)
                else:
                    print("⚠️ [FALLBACK] Gemini esgotado, tentando próximo provider")
            except Exception as e:
                print(f"❌ [FALLBACK] Erro no Gemini: {e}")
        
        # 2. Tentar OpenRouter como fallback secundário (prioridade 2)
        if api_keys.get('openrouter'):
            try:
                print("🔄 [FALLBACK] Usando OpenRouter (prioridade 2)")
                return generate_script_part_openrouter(prompt, openrouter_model, api_keys['openrouter'], max_tokens)
            except Exception as e:
                print(f"❌ [FALLBACK] Erro no OpenRouter: {e}")
        
        # 3. Tentar OpenAI como fallback terciário (prioridade 3)
        if title_generator.openai_client:
            try:
                print("🔄 [FALLBACK] Usando OpenAI (prioridade 3) com prompt otimizado")
                return generate_script_part_openai(prompt, title_generator, max_tokens)
            except Exception as e:
                print(f"❌ [FALLBACK] Erro no OpenAI: {e}")
        
        # Se chegou aqui, nenhum provider está disponível
        raise Exception('Nenhuma IA configurada ou disponível para geração')
                
    except Exception as e:
        print(f"❌ [FALLBACK] Erro crítico na geração da parte: {e}")
        raise Exception(f'Erro na geração da parte: {str(e)}')


def generate_script_part_openrouter(prompt, model, api_key, max_tokens):
    """Gerar parte do roteiro usando OpenRouter com tokens personalizados"""
    try:
        if model == 'auto':
            model = 'anthropic/claude-3.5-sonnet'

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5173',
            'X-Title': 'Auto Video Producer - Parts Generation'
        }

        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json={
                'model': model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Você é um roteirista profissional especializado em criar conteúdo envolvente para YouTube. Siga exatamente as instruções fornecidas e mantenha consistência narrativa.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': max_tokens,
                'temperature': 0.7
            },
            timeout=90
        )

        if response.status_code != 200:
            raise Exception(f'OpenRouter API error: {response.status_code} - {response.text}')

        data = response.json()
        content = data['choices'][0]['message']['content']

        return content.strip()

    except Exception as e:
        raise Exception(f'Erro OpenRouter parte: {str(e)}')


def generate_script_part_gemini(prompt, title_generator):
    """Gerar parte do roteiro usando Gemini com cache e fallback automático"""
    try:
        from routes.automations import handle_gemini_429_error, check_gemini_availability, get_fallback_provider_info
        import hashlib
        import json
        import os
        from datetime import datetime, timedelta
        
        # Sistema de cache simples
        cache_dir = "cache/gemini_parts"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Gerar hash do prompt para cache
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        cache_file = os.path.join(cache_dir, f"{prompt_hash}.json")
        
        # Verificar cache (válido por 12 horas para partes)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cache_time < timedelta(hours=12):
                    print(f"📦 [CACHE] Usando parte em cache para Gemini ({len(cache_data['content'])} chars)")
                    return cache_data['content']
            except Exception as e:
                print(f"⚠️ [CACHE] Erro ao ler cache da parte: {e}")
        
        # Verificar disponibilidade do Gemini
        if not check_gemini_availability():
            print("⚠️ [GEMINI] Todas as chaves Gemini esgotadas, usando fallback para parte")
            fallback_info = get_fallback_provider_info()
            if fallback_info:
                if fallback_info['provider'] == 'openai':
                    return generate_script_part_openai(prompt, title_generator, 4000)
                elif fallback_info['provider'] == 'openrouter':
                    return generate_script_part_openrouter(prompt, 'anthropic/claude-3.5-sonnet', fallback_info['key'], 4000)
            raise Exception('Gemini esgotado e nenhum fallback disponível para parte')
        
        if not title_generator.gemini_model:
            raise Exception('Gemini não configurado')

        content = generate_content_with_gemini_retry(prompt)
        
        # Salvar no cache
        try:
            cache_data = {
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'prompt_hash': prompt_hash
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"📦 [CACHE] Parte salva no cache")
        except Exception as e:
            print(f"⚠️ [CACHE] Erro ao salvar cache da parte: {e}")

        return content.strip()

    except Exception as e:
        error_str = str(e)
        
        # Tratar erro 429 especificamente
        if '429' in error_str or 'quota' in error_str.lower() or 'exceeded' in error_str.lower():
            print(f"🚫 [GEMINI] Erro 429 detectado na parte: {error_str}")
            # Nota: O tratamento do erro 429 já é feito internamente pela função generate_content_with_gemini_retry
            # que chama handle_gemini_429_error com a chave correta
            
            # Tentar fallback automático
            try:
                from routes.automations import get_fallback_provider_info
                fallback_info = get_fallback_provider_info()
                if fallback_info:
                    print(f"🔄 [FALLBACK] Usando {fallback_info['provider']} como fallback para parte")
                    if fallback_info['provider'] == 'openai':
                        return generate_script_part_openai(prompt, title_generator, 4000)
                    elif fallback_info['provider'] == 'openrouter':
                        return generate_script_part_openrouter(prompt, 'anthropic/claude-3.5-sonnet', fallback_info['key'], 4000)
            except Exception as fallback_error:
                print(f"❌ [FALLBACK] Erro no fallback da parte: {fallback_error}")
        
        raise Exception(f'Erro Gemini parte: {error_str}')


def generate_script_part_openai(prompt, title_generator, max_tokens):
    """Gerar parte do roteiro usando OpenAI com tokens personalizados e prompt otimizado"""
    try:
        if not title_generator.openai_client:
            raise Exception('OpenAI não configurado')

        # Otimizar prompt para OpenAI se necessário
        optimized_prompt = optimize_prompt_for_openai(prompt, max_tokens)
        
        response = title_generator.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um roteirista profissional especializado em criar conteúdo envolvente para YouTube. Siga exatamente as instruções fornecidas e mantenha consistência narrativa."},
                {"role": "user", "content": optimized_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )

        content = response.choices[0].message.content
        return content.strip()

    except Exception as e:
        raise Exception(f'Erro OpenAI parte: {str(e)}')


# ===== FUNÇÕES DE OTIMIZAÇÃO TÉCNICA =====

def optimize_prompt_for_openai(prompt, max_tokens=4000):
    """Otimizar prompt para OpenAI reduzindo tamanho com chunking inteligente"""
    try:
        # Limite aproximado de caracteres baseado em max_tokens (1 token ≈ 4 chars)
        char_limit = max_tokens * 3  # Margem de segurança
        
        if len(prompt) <= char_limit:
            return prompt
        
        print(f"🔧 [OPTIMIZE] Prompt muito longo ({len(prompt)} chars), otimizando para {char_limit} chars")
        
        # Aplicar chunking inteligente
        optimized_prompt = intelligent_chunking(prompt, char_limit)
        
        print(f"✅ [OPTIMIZE] Prompt otimizado: {len(prompt)} → {len(optimized_prompt)} chars")
        return optimized_prompt
        
    except Exception as e:
        print(f"⚠️ [OPTIMIZE] Erro na otimização, usando prompt original: {e}")
        return prompt


def intelligent_chunking(text, max_chars):
    """Chunking inteligente que preserva informações essenciais"""
    try:
        if len(text) <= max_chars:
            return text
        
        # Dividir o texto em seções
        lines = text.split('\n')
        
        # Identificar seções importantes (título, instruções, contexto)
        essential_sections = []
        context_sections = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Seções essenciais (sempre manter)
            if any(keyword in line_lower for keyword in [
                'título:', 'premissa:', 'instruções:', 'formato:', 
                'importante:', 'obrigatório:', 'deve:', 'não deve:'
            ]):
                essential_sections.append(line)
            
            # Seções de contexto (podem ser comprimidas)
            elif any(keyword in line_lower for keyword in [
                'contexto:', 'resumo:', 'parte anterior:', 'capítulo anterior:'
            ]):
                context_sections.append(line)
            
            # Outras linhas importantes
            elif line.strip() and not line.startswith(' '):
                essential_sections.append(line)
        
        # Montar prompt otimizado
        optimized_lines = essential_sections.copy()
        
        # Adicionar contexto comprimido se houver espaço
        current_length = len('\n'.join(optimized_lines))
        remaining_chars = max_chars - current_length - 200  # Margem de segurança
        
        if context_sections and remaining_chars > 100:
            compressed_context = compress_context_sections(context_sections, remaining_chars)
            if compressed_context:
                optimized_lines.append(compressed_context)
        
        return '\n'.join(optimized_lines)
        
    except Exception as e:
        print(f"⚠️ [CHUNKING] Erro no chunking inteligente: {e}")
        # Fallback: truncar simples mantendo início e fim
        if len(text) > max_chars:
            keep_start = max_chars // 2
            keep_end = max_chars - keep_start - 50
            return text[:keep_start] + "\n\n[...contexto comprimido...]\n\n" + text[-keep_end:]
        return text


def compress_context_sections(context_sections, max_chars):
    """Comprimir seções de contexto mantendo informações essenciais"""
    try:
        if not context_sections:
            return None
        
        # Juntar todas as seções de contexto
        full_context = '\n'.join(context_sections)
        
        if len(full_context) <= max_chars:
            return full_context
        
        # Extrair informações essenciais do contexto
        essential_info = []
        
        for section in context_sections:
            # Pegar últimas 2 frases de cada seção
            sentences = section.split('.')
            if len(sentences) >= 2:
                essential_info.extend(sentences[-2:])
            else:
                essential_info.append(section)
        
        compressed = '. '.join([s.strip() for s in essential_info if s.strip()])
        
        # Se ainda for muito longo, truncar mantendo o final
        if len(compressed) > max_chars:
            compressed = compressed[-max_chars:]
        
        return f"Contexto resumido: {compressed}"
        
    except Exception as e:
        print(f"⚠️ [COMPRESS] Erro na compressão de contexto: {e}")
        return None


def daily_reset_quota():
    """Reset automático diário das quotas Gemini"""
    try:
        from datetime import datetime, timedelta
        import json
        import os
        
        # Arquivo para controlar último reset
        reset_file = "cache/last_quota_reset.json"
        os.makedirs(os.path.dirname(reset_file), exist_ok=True)
        
        now = datetime.now()
        should_reset = False
        
        # Verificar se precisa resetar
        if os.path.exists(reset_file):
            try:
                with open(reset_file, 'r') as f:
                    data = json.load(f)
                last_reset = datetime.fromisoformat(data['last_reset'])
                
                # Reset se passou mais de 24 horas
                if now - last_reset > timedelta(hours=24):
                    should_reset = True
            except Exception as e:
                print(f"⚠️ [RESET] Erro ao ler arquivo de reset: {e}")
                should_reset = True
        else:
            should_reset = True
        
        if should_reset:
            # Resetar quotas Gemini
            from routes.automations import reset_all_gemini_usage
            reset_all_gemini_usage()
            
            # Salvar timestamp do reset
            reset_data = {
                'last_reset': now.isoformat(),
                'reset_count': data.get('reset_count', 0) + 1 if 'data' in locals() else 1
            }
            
            with open(reset_file, 'w') as f:
                json.dump(reset_data, f, indent=2)
            
            print(f"🔄 [RESET] Reset diário das quotas Gemini executado ({reset_data['reset_count']}º reset)")
            return True
        else:
            hours_until_reset = 24 - (now - last_reset).total_seconds() / 3600
            print(f"⏰ [RESET] Próximo reset em {hours_until_reset:.1f} horas")
            return False
            
    except Exception as e:
        print(f"❌ [RESET] Erro no reset diário: {e}")
        return False


@premise_bp.route('/generate-long-script', methods=['POST'])
def generate_long_script():
    """Gerar roteiro longo usando Storyteller Unlimited (100% integração)"""
    try:
        from services.storyteller_service import StorytellerService
        
        logger.info(f"🚀 [STORYTELLER_LONG] Iniciando geração com Storyteller Unlimited...")
        data = request.get_json()
        
        # Extrair parâmetros obrigatórios
        titulo = data.get('title')
        premissa = data.get('premise', data.get('title', 'Roteiro sem premissa'))
        numero_capitulos = data.get('number_of_chapters', data.get('chapters', 10))
        
        # Parâmetros do Storyteller
        agent = data.get('storyteller_agent', 'millionaire_stories')
        target_words = data.get('target_words', 2500)
        api_keys = data.get('api_keys', {})
        
        logger.info(f"🔍 [STORYTELLER_LONG] Parâmetros: título={titulo}, capítulos={numero_capitulos}, agent={agent}")
        
        # Validar parâmetros obrigatórios
        if not titulo:
            logger.error(f"❌ [STORYTELLER_LONG] Erro: Título não fornecido")
            return jsonify({
                'success': False,
                'error': 'Título não fornecido'
            }), 400
        
        if numero_capitulos < 1:
            logger.error(f"❌ [STORYTELLER_LONG] Erro: Número de capítulos inválido")
            return jsonify({
                'success': False,
                'error': 'Número de capítulos deve ser maior que zero'
            }), 400
        
        # Inicializar Storyteller Service
        storyteller_service = StorytellerService()
        
        # Preparar premissa aprimorada
        enhanced_premise = f"""
        TÍTULO: {titulo}
        
        PREMISSA: {premissa}
        
        OBJETIVO: Criar um roteiro longo e envolvente dividido em {numero_capitulos} capítulos sequenciais.
        
        ESTRUTURA DESEJADA:
        - Capítulo 1: Introdução e gancho inicial
        - Capítulos 2-{numero_capitulos-1}: Desenvolvimento e tensão crescente
        - Capítulo {numero_capitulos}: Conclusão satisfatória
        
        CARACTERÍSTICAS:
        - Cada capítulo: 400-600 palavras
        - Continuidade narrativa entre capítulos
        - Personagens bem desenvolvidos
        - Clímax progressivo
        - Final impactante
        - Linguagem adaptada para público brasileiro
        
        TOM: envolvente, profissional, otimista
        """
        
        # Gerar roteiro com Storyteller Unlimited
        result = storyteller_service.generate_storyteller_script(
            title=titulo,
            premise=enhanced_premise,
            agent_type=agent,
            num_chapters=numero_capitulos,
            provider='gemini'
        )
        
        if not result or not result.get('full_script'):
            raise Exception("Falha na geração com Storyteller Unlimited")
        
        # Formatar resultado no padrão esperado
        chapters = result.get('chapters', [])
        response_data = {
            'success': True,
            'data': {
                'title': titulo,
                'premise': premissa,
                'number_of_chapters': len(chapters) if chapters else result.get('num_chapters', 0),
                'chapters': chapters,
                'word_count': len(result['full_script'].split()),
                'system_used': 'storyteller_unlimited',
                'agent': agent,
                'memory_bridge_active': True
            },
            'system': 'storyteller_unlimited'
        }
        
        logger.info(f"✅ [STORYTELLER_LONG] Sucesso: {len(result['chapters'])} capítulos gerados")
        return jsonify(response_data)
            
    except Exception as e:
        error_msg = f"Erro com Storyteller Unlimited: {str(e)}"
        logger.error(f"❌ [STORYTELLER_LONG] {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg,
            'system': 'storyteller_unlimited'
        }), 500


def get_optimized_fallback_provider():
    """Obter provedor de fallback otimizado com hierarquia: Gemini → OpenRouter → OpenAI"""
    try:
        from routes.automations import check_gemini_availability, get_fallback_provider_info
        
        # Executar reset diário automático
        daily_reset_quota()
        
        # 1. Tentar Gemini primeiro
        if check_gemini_availability():
            return {'provider': 'gemini', 'priority': 1}
        
        # 2. Tentar OpenRouter como fallback secundário
        fallback_info = get_fallback_provider_info()
        if fallback_info and fallback_info['provider'] == 'openrouter':
            return {'provider': 'openrouter', 'key': fallback_info['key'], 'priority': 2}
        
        # 3. OpenAI como último recurso
        if fallback_info and fallback_info['provider'] == 'openai':
            return {'provider': 'openai', 'key': fallback_info['key'], 'priority': 3}
        
        return None
        
    except Exception as e:
        print(f"❌ [FALLBACK] Erro ao obter provedor otimizado: {e}")
        return None
