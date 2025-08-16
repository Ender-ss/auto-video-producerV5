"""
📝 Script Generation Routes
Rotas para geração de roteiros com pipeline de 3 prompts
"""

from flask import Blueprint, request, jsonify
import requests
import json
import time
from services.title_generator import TitleGenerator

scripts_bp = Blueprint('scripts', __name__)

@scripts_bp.route('/generate', methods=['POST'])
def generate_scripts():
    """Gerar roteiros usando pipeline de 3 prompts"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        premise = data.get('premise', '')
        ai_provider = data.get('ai_provider', 'auto')
        openrouter_model = data.get('openrouter_model', 'auto')
        number_of_chapters = data.get('number_of_chapters', 8)
        api_keys = data.get('api_keys', {})

        if not title or not premise:
            return jsonify({
                'success': False,
                'error': 'Título e premissa são obrigatórios'
            }), 400

        # Inicializar o gerador
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

        # Pipeline de 3 prompts
        print("🎬 Iniciando pipeline de geração de roteiros...")
        
        # PROMPT 1: Tradução e Contexto
        print("📝 Executando Prompt 1: Tradução e Contexto")
        context_result = execute_prompt_1(title, premise, ai_provider, openrouter_model, api_keys, title_generator)
        
        if not context_result:
            raise Exception("Falha no Prompt 1: Tradução e Contexto")
        
        # PROMPT 2: Estrutura Narrativa
        print("📖 Executando Prompt 2: Estrutura Narrativa")
        narrative_result = execute_prompt_2(title, context_result, ai_provider, openrouter_model, api_keys, title_generator)
        
        if not narrative_result:
            raise Exception("Falha no Prompt 2: Estrutura Narrativa")
        
        # PROMPT 3: Geração dos Capítulos
        print(f"✍️ Executando Prompt 3: Geração de {number_of_chapters} Capítulos")
        chapters = execute_prompt_3(title, context_result, narrative_result, number_of_chapters, ai_provider, openrouter_model, api_keys, title_generator)
        
        if not chapters:
            raise Exception("Falha no Prompt 3: Geração dos Capítulos")

        # Resultado final
        script_result = {
            'title': title,
            'premise': premise,
            'context': context_result,
            'narrative_structure': narrative_result,
            'chapters': chapters,
            'total_chapters': len(chapters),
            'total_words': sum(len(ch['content'].split()) for ch in chapters if ch.get('content'))
        }

        return jsonify({
            'success': True,
            'scripts': script_result,
            'provider_used': ai_provider,
            'chapters_generated': len(chapters)
        })

    except Exception as e:
        print(f"❌ Erro na geração de roteiros: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def execute_prompt_1(title, premise, ai_provider, openrouter_model, api_keys, title_generator):
    """Prompt 1: Tradução e Contexto"""
    prompt = f"""Por favor, forneça o texto acima em Português, utilizando nomes e expressões comuns entre os falantes de Português em diferentes países, adaptado de forma a refletir a cultura compartilhada pelos diversos povos que falam a língua. Adapte nomes, locais e referências culturais de forma a serem naturais e reconhecíveis no idioma Português, garantindo que mantenham relevância e ressoem com o público.

A saída deve ter o seguinte formato:

{{
    "Contexto": "{premise}"
}}

Certifique-se de que a chave gerada siga o padrão exigido."""

    try:
        if ai_provider == 'auto':
            providers = ['openrouter', 'gemini', 'openai']
            for provider in providers:
                try:
                    if provider == 'openrouter' and api_keys.get('openrouter'):
                        return call_openrouter(prompt, openrouter_model, api_keys['openrouter'])
                    elif provider == 'gemini' and title_generator.gemini_model:
                        return call_gemini(prompt, title_generator)
                    elif provider == 'openai' and title_generator.openai_client:
                        return call_openai(prompt, title_generator)
                except Exception as e:
                    print(f"❌ Erro com {provider}: {e}")
                    continue
        elif ai_provider == 'openrouter':
            return call_openrouter(prompt, openrouter_model, api_keys['openrouter'])
        elif ai_provider == 'gemini':
            return call_gemini(prompt, title_generator)
        elif ai_provider == 'openai':
            return call_openai(prompt, title_generator)
            
        return None
    except Exception as e:
        print(f"❌ Erro no Prompt 1: {e}")
        return None

def execute_prompt_2(title, context, ai_provider, openrouter_model, api_keys, title_generator):
    """Prompt 2: Estrutura Narrativa"""
    prompt = f"""# Objetivo Principal: 

Transformar qualquer tema em um único prompt narrativo para o primeiro capítulo, sem finalizar a história. O resultado será um array JSON chamado `Prompts`, que conterá exatamente 1 objeto, com o campo `prompt`.

## Tema: "{title}"
### Contexto: "{context}"

## Estrutura Base do Prompt  
Cada prompt deve começar com: "Escreva uma história de aproximadamente 500 palavras sobre..."  

## Especificações Técnicas do JSON

```json
{{
  "Prompts": [
    {{
      "prompt": "Escreva uma história de aproximadamente 500 palavras sobre..."
    }}
  ]
}}
```

## Requisitos Técnicos 

- Apenas um objeto no array `Prompts`  
- Cadeia com aspas duplas  
- Indentação: 2 espaços  
- Sem quebras de linha no conteúdo de `prompt`  
- JSON válido e com caracteres especiais escapados  

## Estrutura Narrativa Detalhada (Apenas Primeiro Capítulo)

1. **Apresentação do Protagonista**  
   - Nome e características principais  
   - Contexto social/profissional  
   - Estado emocional inicial  

2. **Cenário Principal**  
   - Localização temporal e espacial  
   - Atmosfera e ambiente  
   - Elementos únicos do mundo da história  

3. **Ativador da História**  
   - Evento catalisador que rompa a normalidade  
   - Inicie o conflito inicial ou dilema principal  

4. **Gancho Narrativo**  
   - Elemento de mistério ou tensão que deixe clara a continuação  
   - Pergunta não resolvida  
   - Termine sem concluir o conflito, mantendo a história incompleta 

## Checklist de Validação

1. **JSON**  
   - [ ] Apenas 1 objeto dentro de "Prompts"  
   - [ ] Campo "prompt" sem quebras de linha  
   - [ ] Cadeias com aspas duplas, sem caracteres especiais 

2. **Narrativa**  
   - [ ] História NÃO finalizada (o capítulo fica em aberto)    
   - [ ] Inclui ganchos, sem resolver o conflito  
   - [ ] Não conclua a trama nem resolva o conflito principal. Em vez disso, crie um problema a partir de cada solução, fazendo o leitor sentir que a história ainda precisa continuar. A sensação final deve ser de que há mais por vir, nunca uma conclusão definitiva.  
   - [ ] Certifique-se de que o capítulo termine com um gancho intrigante, criando um mistério ou uma dúvida que deixe o leitor ansioso pelo próximo capítulo, sem conseguir parar de ler.  
   - [ ] Mantenha um equilíbrio entre ação e reflexão, permitindo que o personagem evolua, mas sem dar respostas definitivas ou conclusões que resolvam os dilemas abertos.

## Observação Final

- Não conclua a trama nem resolva o conflito principal. Em vez disso, crie um problema a partir de cada solução, fazendo o leitor sentir que a história ainda precisa continuar. A sensação final deve ser que há mais por vir, nunca uma conclusão definitiva.  
- Certifique-se de que o capítulo termine com um gancho intrigante, criando um mistério ou uma dúvida que deixe o leitor ansioso pelo próximo capítulo, sem conseguir parar de ler.  
- Mantenha um equilíbrio entre ação e reflexão, permitindo que o personagem evolua, mas sem dar respostas definitivas ou conclusões que resolvam os dilemas abertos."""

    try:
        if ai_provider == 'auto':
            providers = ['openrouter', 'gemini', 'openai']
            for provider in providers:
                try:
                    if provider == 'openrouter' and api_keys.get('openrouter'):
                        return call_openrouter(prompt, openrouter_model, api_keys['openrouter'])
                    elif provider == 'gemini' and title_generator.gemini_model:
                        return call_gemini(prompt, title_generator)
                    elif provider == 'openai' and title_generator.openai_client:
                        return call_openai(prompt, title_generator)
                except Exception as e:
                    print(f"❌ Erro com {provider}: {e}")
                    continue
        elif ai_provider == 'openrouter':
            return call_openrouter(prompt, openrouter_model, api_keys['openrouter'])
        elif ai_provider == 'gemini':
            return call_gemini(prompt, title_generator)
        elif ai_provider == 'openai':
            return call_openai(prompt, title_generator)
            
        return None
    except Exception as e:
        print(f"❌ Erro no Prompt 2: {e}")
        return None

def execute_prompt_3(title, context, narrative_structure, number_of_chapters, ai_provider, openrouter_model, api_keys, title_generator):
    """Prompt 3: Geração dos Capítulos"""
    chapters = []

    try:
        print(f"🔍 DEBUG: Iniciando geração de {number_of_chapters} capítulos")
        print(f"🔍 DEBUG: AI Provider: {ai_provider}")
        print(f"🔍 DEBUG: APIs disponíveis: {list(api_keys.keys())}")

        # Verificar se há pelo menos uma API configurada
        has_openrouter = api_keys.get('openrouter') is not None
        has_gemini = title_generator.gemini_model is not None
        has_openai = title_generator.openai_client is not None

        print(f"🔍 DEBUG: OpenRouter: {'✅' if has_openrouter else '❌'}")
        print(f"🔍 DEBUG: Gemini: {'✅' if has_gemini else '❌'}")
        print(f"🔍 DEBUG: OpenAI: {'✅' if has_openai else '❌'}")

        if not (has_openrouter or has_gemini or has_openai):
            print("❌ ERRO: Nenhuma API de IA configurada para geração de roteiros")
            return []

        # Extrair o prompt base da estrutura narrativa
        base_prompt = extract_base_prompt(narrative_structure)
        print(f"🔍 DEBUG: Base prompt extraído: {base_prompt[:100]}...")
        
        for i in range(number_of_chapters):
            print(f"📖 Gerando Capítulo {i + 1}/{number_of_chapters}")
            
            if i == 0:
                # Primeiro capítulo usa o prompt base
                chapter_prompt = base_prompt
            else:
                # Capítulos seguintes continuam a história
                previous_chapter = chapters[i-1]['content'] if chapters else ""
                chapter_prompt = f"""Continue a história a partir do capítulo anterior. Escreva o próximo capítulo de aproximadamente 500 palavras.

Capítulo anterior:
{previous_chapter}

Instruções:
- Continue a narrativa de forma natural
- Mantenha a consistência dos personagens
- Adicione novos elementos de tensão
- Termine com um gancho para o próximo capítulo
- NÃO resolva o conflito principal ainda"""

            # Gerar o capítulo
            chapter_content = None
            print(f"🔍 DEBUG: Gerando capítulo {i+1} com prompt de {len(chapter_prompt)} caracteres")

            if ai_provider == 'auto':
                providers = ['openrouter', 'gemini', 'openai']
                for provider in providers:
                    try:
                        print(f"🔍 DEBUG: Tentando provider {provider}")
                        if provider == 'openrouter' and api_keys.get('openrouter'):
                            print(f"🔍 DEBUG: Chamando OpenRouter...")
                            chapter_content = call_openrouter(chapter_prompt, openrouter_model, api_keys['openrouter'])
                            print(f"✅ DEBUG: OpenRouter retornou {len(chapter_content) if chapter_content else 0} caracteres")
                            break
                        elif provider == 'gemini' and title_generator.gemini_model:
                            print(f"🔍 DEBUG: Chamando Gemini...")
                            chapter_content = call_gemini(chapter_prompt, title_generator)
                            print(f"✅ DEBUG: Gemini retornou {len(chapter_content) if chapter_content else 0} caracteres")
                            break
                        elif provider == 'openai' and title_generator.openai_client:
                            print(f"🔍 DEBUG: Chamando OpenAI...")
                            chapter_content = call_openai(chapter_prompt, title_generator)
                            print(f"✅ DEBUG: OpenAI retornou {len(chapter_content) if chapter_content else 0} caracteres")
                            break
                        else:
                            print(f"⚠️ DEBUG: Provider {provider} não disponível")
                    except Exception as e:
                        print(f"❌ Erro com {provider}: {e}")
                        continue
            elif ai_provider == 'openrouter':
                chapter_content = call_openrouter(chapter_prompt, openrouter_model, api_keys['openrouter'])
            elif ai_provider == 'gemini':
                chapter_content = call_gemini(chapter_prompt, title_generator)
            elif ai_provider == 'openai':
                chapter_content = call_openai(chapter_prompt, title_generator)
            
            if chapter_content:
                # Gerar título do capítulo baseado no conteúdo
                chapter_title = f"Capítulo {i + 1}"
                if len(chapter_content) > 50:
                    # Tentar extrair uma frase inicial como título
                    first_sentence = chapter_content.split('.')[0][:50]
                    if len(first_sentence) > 10:
                        chapter_title = f"Capítulo {i + 1}: {first_sentence}..."

                chapters.append({
                    'chapter_number': i + 1,
                    'title': chapter_title,
                    'content': chapter_content,
                    'word_count': len(chapter_content.split())
                })
            else:
                print(f"❌ Falha ao gerar capítulo {i + 1}")
                # Se é o primeiro capítulo e falhou, retornar erro
                if i == 0:
                    print(f"❌ ERRO CRÍTICO: Falha ao gerar o primeiro capítulo")
                    return []
                # Se não é o primeiro, continuar com os capítulos já gerados
                break

            # Pequena pausa entre capítulos para evitar rate limiting
            time.sleep(1)

        print(f"✅ DEBUG: Gerados {len(chapters)} capítulos com sucesso")
        return chapters
        
    except Exception as e:
        print(f"❌ Erro no Prompt 3: {e}")
        return []

def extract_base_prompt(narrative_structure):
    """Extrair o prompt base da estrutura narrativa"""
    try:
        if isinstance(narrative_structure, str):
            # Tentar parsear como JSON
            import json
            data = json.loads(narrative_structure)
            if 'Prompts' in data and len(data['Prompts']) > 0:
                return data['Prompts'][0].get('prompt', narrative_structure)
        return narrative_structure
    except:
        return narrative_structure

def call_openrouter(prompt, model, api_key):
    """Chamar OpenRouter API"""
    try:
        print(f"🔍 DEBUG: Enviando prompt para OpenRouter ({len(prompt)} chars)")
        if model == 'auto':
            model = 'anthropic/claude-3.5-sonnet'
        print(f"🔍 DEBUG: Usando modelo: {model}")
        
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
                    {'role': 'system', 'content': 'Você é um especialista em criação de roteiros e storytelling.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.8
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"🔍 DEBUG: OpenRouter respondeu com {len(content)} caracteres")
            return content
        else:
            print(f"❌ DEBUG: OpenRouter erro {response.status_code}: {response.text}")
            raise Exception(f'OpenRouter API error: {response.status_code}')

    except Exception as e:
        print(f"❌ DEBUG: Erro detalhado no OpenRouter: {str(e)}")
        raise Exception(f'Erro OpenRouter: {str(e)}')

def call_gemini(prompt, title_generator=None):
    """Chamar Gemini API com retry automático entre múltiplas chaves"""
    import google.generativeai as genai
    from routes.automations import get_next_gemini_key, handle_gemini_429_error
    
    # Tentar múltiplas chaves se necessário
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Obter próxima chave Gemini
            api_key = get_next_gemini_key()
            if not api_key:
                raise Exception('Nenhuma chave Gemini disponível. Configure pelo menos uma chave nas Configurações.')
            
            print(f"🔍 DEBUG: Tentativa {attempt + 1}/{max_retries}: Enviando prompt para Gemini ({len(prompt)} chars)")
            
            # Configurar Gemini diretamente
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Gerar conteúdo
            response = model.generate_content(prompt)
            content = response.text.strip()
            
            print(f"🔍 DEBUG: Gemini respondeu com {len(content)} caracteres na tentativa {attempt + 1}")
            return content
            
        except Exception as e:
            error_str = str(e)
            last_error = error_str
            print(f"❌ DEBUG: Erro na tentativa {attempt + 1}: {error_str}")
            
            # Check if it's a quota error (429)
            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                if attempt < max_retries - 1:  # Not the last attempt
                    print(f"🔄 Erro de quota detectado, tentando próxima chave Gemini...")
                    handle_gemini_429_error(error_str)
                    continue
                else:
                    print("❌ Todas as tentativas de retry falharam")
                    handle_gemini_429_error(error_str)
            else:
                # For non-quota errors, don't retry
                print(f"❌ Erro não relacionado à quota, parando tentativas: {error_str}")
                break
    
    # Se chegou aqui, todas as tentativas falharam
    final_error = f'Falha na geração com Gemini após todas as {max_retries} tentativas. Último erro: {last_error}'
    raise Exception(final_error)

def call_openai(prompt, title_generator):
    """Chamar OpenAI API"""
    try:
        print(f"🔍 DEBUG: Enviando prompt para OpenAI ({len(prompt)} chars)")
        response = title_generator.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em criação de roteiros e storytelling."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.8
        )
        content = response.choices[0].message.content
        print(f"🔍 DEBUG: OpenAI respondeu com {len(content)} caracteres")
        return content
    except Exception as e:
        print(f"❌ DEBUG: Erro detalhado no OpenAI: {str(e)}")
        raise Exception(f'Erro OpenAI: {str(e)}')
