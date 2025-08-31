"""
🤖 AI Services
Serviços de integração com APIs de IA
"""

import openai
import requests
import json
import time
from datetime import datetime

# Import AI libraries
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# ================================
# 🎯 GERAÇÃO DE TÍTULOS
# ================================

def generate_titles_with_openai(source_titles, instructions, api_key, update_callback=None):
    """Gerar títulos usando OpenAI ChatGPT com fallback para Gemini, gerando um por vez com callback"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        titles_text = '\n'.join([f"- {title}" for title in source_titles])
        
        generated_titles = []
        for i in range(5):
            prompt = f"""
            {instructions}
            
            Títulos de origem:
            {titles_text}
            
            Gere 1 novo título viral baseado nos títulos acima. O título deve:
            - Ter entre 60-100 caracteres
            - Ser chamativo e viral
            - Manter o tema dos títulos originais
            - Usar técnicas de copywriting para YouTube
            - Ser adequado para o público brasileiro
            
            Retorne apenas o título, sem formatação extra.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.8
            )
            
            title = response.choices[0].message.content.strip()
            generated_titles.append(title)
            
            if update_callback:
                update_callback(generated_titles)
        
        return {
            'success': True,
            'data': {
                'generated_titles': generated_titles,
                'agent': 'OpenAI',
                'processing_time': 0
            }
        }
    
    except Exception as e:
        error_str = str(e)
        print(f"❌ Erro OpenAI: {error_str}")
        
        # Verificar se é erro de quota (429)
        if "429" in error_str or "quota" in error_str.lower() or "insufficient_quota" in error_str.lower():
            print("🔄 Erro de quota OpenAI detectado, tentando fallback para Gemini...")
            
            # Tentar fallback para Gemini
            try:
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'routes'))
                from routes.automations import get_next_gemini_key
                
                gemini_key = get_next_gemini_key()
                if gemini_key:
                    print("🔄 Usando Gemini como fallback...")
                    gemini_result = generate_titles_with_gemini(source_titles, instructions, gemini_key)
                    if gemini_result['success']:
                        print("✅ Fallback para Gemini bem-sucedido!")
                        gemini_result['data']['agent'] = 'Gemini (Fallback)'
                        return gemini_result
                    else:
                        print(f"❌ Fallback Gemini também falhou: {gemini_result['error']}")
                else:
                    print("❌ Nenhuma chave Gemini disponível para fallback")
            except Exception as fallback_error:
                print(f"❌ Erro no fallback para Gemini: {str(fallback_error)}")
        
        return {
            'success': False,
            'error': f'Erro ao gerar títulos com ChatGPT: {error_str}'
        }

def generate_titles_with_gemini(source_titles, instructions, api_key, update_callback=None, count=5):
    """Gerar títulos usando Google Gemini com retry automático, gerando todos de uma vez (otimizado)"""
    import sys
    import os
    
    try:
        if not GEMINI_AVAILABLE:
            return {
                'success': False,
                'error': 'Biblioteca google-generativeai não instalada'
            }
        
        # Importar diretamente para usar a mesma instância global
        from routes.automations import get_next_gemini_key, handle_gemini_429_error, get_gemini_keys_count
        
        # Usar a quantidade real de chaves disponíveis
        max_retries = get_gemini_keys_count() if get_gemini_keys_count() > 0 else 1
        print(f"🔑 Usando {max_retries} chaves Gemini para títulos")
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
                    print(f"🔄 Tentativa {attempt + 1}/{max_retries}: Usando rotação de chaves Gemini para títulos")
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                titles_text = '\n'.join([f"- {title}" for title in source_titles])
                
                # OTIMIZAÇÃO: Gerar todos os títulos em uma única chamada API
                prompt = f"""
                {instructions}
                
                Títulos de origem:
                {titles_text}
                
                Gere {count} novos títulos virais baseados nos títulos acima. Cada título deve:
                - Ter entre 60-100 caracteres
                - Ser chamativo e viral
                - Manter o tema dos títulos originais
                - Usar técnicas de copywriting para YouTube
                - Ser adequado para o público brasileiro
                
                Retorne APENAS os {count} títulos, um por linha, sem numeração, sem formatação extra, sem explicações.
                """
                
                response = model.generate_content(prompt)
                
                if not response.text:
                    return {
                        'success': False,
                        'error': 'Gemini não retornou conteúdo'
                    }
                
                # Processar a resposta para extrair os títulos
                response_text = response.text.strip()
                generated_titles = []
                
                # Dividir por linhas e limpar cada título
                lines = response_text.split('\n')
                for line in lines:
                    title = line.strip()
                    # Remover numeração se existir (1., 2., -, *, etc.)
                    title = __import__('re').sub(r'^[\d\-\*\.\)\]\}\s]+', '', title).strip()
                    # Remover aspas se existir
                    title = title.strip('"\'"`')
                    
                    if title and len(title) > 10:  # Filtrar títulos muito curtos
                        generated_titles.append(title)
                    
                    # Parar se já temos a quantidade solicitada
                    if len(generated_titles) >= count:
                        break
                
                # Garantir que temos pelo menos alguns títulos
                if not generated_titles:
                    # Fallback: se não conseguiu parsear, usar o texto completo
                    generated_titles = [response_text[:100]] if response_text else []
                
                # Limitar ao número solicitado
                generated_titles = generated_titles[:count]
                
                # Callback para progresso (simular progresso incremental)
                if update_callback:
                    for i in range(1, len(generated_titles) + 1):
                        update_callback(generated_titles[:i])
                
                print(f"✅ Sucesso na geração de títulos com Gemini na tentativa {attempt + 1}")
                
                return {
                    'success': True,
                    'data': {
                        'generated_titles': generated_titles,
                        'agent': 'Gemini',
                        'processing_time': 0
                    }
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
        final_error = f'Falha na geração de títulos com Gemini após todas as {max_retries} tentativas. Último erro: {last_error}'
        return {
            'success': False,
            'error': final_error
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao gerar títulos com Gemini: {str(e)}'
        }

def generate_titles_with_claude(source_titles, instructions, api_key):
    """Gerar títulos usando Anthropic Claude"""
    try:
        if not ANTHROPIC_AVAILABLE:
            return {
                'success': False,
                'error': 'Biblioteca anthropic não instalada'
            }
        
        client = anthropic.Anthropic(api_key=api_key)
        
        titles_text = '\n'.join([f"- {title}" for title in source_titles])
        
        prompt = f"""
        {instructions}
        
        Títulos de origem:
        {titles_text}
        
        Gere 5 novos títulos virais baseados nos títulos acima. Cada título deve:
        - Ter entre 60-100 caracteres
        - Ser chamativo e viral
        - Manter o tema dos títulos originais
        - Usar técnicas de copywriting para YouTube
        - Ser adequado para o público brasileiro
        
        Retorne apenas os 5 títulos, um por linha, sem numeração ou formatação extra.
        """
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        generated_text = response.content[0].text.strip()
        titles = [title.strip() for title in generated_text.split('\n') if title.strip()]
        
        return {
            'success': True,
            'data': {
                'generated_titles': titles[:5],
                'agent': 'Claude',
                'processing_time': 0
            }
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao gerar títulos com Claude: {str(e)}'
        }

def generate_titles_with_openrouter(source_titles, instructions, api_key):
    """Gerar títulos usando OpenRouter"""
    try:
        titles_text = '\n'.join([f"- {title}" for title in source_titles])
        
        prompt = f"""
        {instructions}
        
        Títulos de origem:
        {titles_text}
        
        Gere 5 novos títulos virais baseados nos títulos acima. Cada título deve:
        - Ter entre 60-100 caracteres
        - Ser chamativo e viral
        - Manter o tema dos títulos originais
        - Usar técnicas de copywriting para YouTube
        - Ser adequado para o público brasileiro
        
        Retorne apenas os 5 títulos, um por linha, sem numeração ou formatação extra.
        """
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "anthropic/claude-3-sonnet",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.8
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code}")
        
        result = response.json()
        generated_text = result['choices'][0]['message']['content'].strip()
        titles = [title.strip() for title in generated_text.split('\n') if title.strip()]
        
        return {
            'success': True,
            'data': {
                'generated_titles': titles[:5],
                'agent': 'OpenRouter',
                'processing_time': 0
            }
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao gerar títulos com OpenRouter: {str(e)}'
        }

# ================================
# 📝 GERAÇÃO DE ROTEIROS
# ================================

def generate_script_chapters_with_openai(title, context, num_chapters, api_key):
    """Gerar roteiro completo com múltiplos capítulos usando OpenAI"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        base_prompt = f"""
        Você é um roteirista especializado em conteúdo viral para YouTube.
        
        Título: {title}
        Contexto: {context}
        
        Escreva uma história de aproximadamente 500 palavras que seja o primeiro capítulo desta narrativa. 
        A história deve começar com uma versão sensacionalista do gancho baseada no título. 
        
        O tom da escrita deve ser simples, direto e emocional, como se a história estivesse sendo contada 
        por um amigo em uma conversa informal. Use palavras fáceis, frases curtas e um ritmo leve.
        
        Regras importantes:
        1. Intensidade Emotiva - Cada frase deve transmitir emoção
        2. Urgência e Ritmo - Intercale frases curtas de ação
        3. Sensação Cinematográfica - Altere o foco entre close-ups e planos gerais
        4. Narrador Observador e Próximo - Terceira pessoa com tom coloquial
        5. Linguagem de Choque - Termos impactantes
        6. Proximidade com a Dor - Retrate de forma direta a dor física e emocional
        
        Forneça apenas o texto da história, sem explicações ou comentários adicionais.
        """
        
        # Gerar primeiro capítulo
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Forneça o texto em Português brasileiro."},
                {"role": "user", "content": base_prompt}
            ],
            max_tokens=1000,
            temperature=0.8
        )
        
        chapters = []
        current_story = response.choices[0].message.content.strip()
        chapters.append({
            'chapter_number': 1,
            'content': current_story,
            'word_count': len(current_story.split())
        })
        
        # Gerar capítulos subsequentes
        for i in range(2, num_chapters + 1):
            continuation_prompt = f"""
            {current_story}
            
            Escreva um novo capítulo, de aproximadamente 500 palavras, que continue os eventos descritos acima, 
            introduzindo uma reviravolta extremamente chocante e impactante que transforme completamente a narrativa.
            
            {"Se este for o último capítulo, encerre definitivamente a história e adicione uma mensagem urgente de CTA." if i == num_chapters else "Não finalize a trama, mas use essa reviravolta para criar um gancho ainda mais poderoso."}
            
            Forneça apenas o novo capítulo, sem explicações ou comentários adicionais.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Forneça o texto em Português brasileiro."},
                    {"role": "user", "content": continuation_prompt}
                ],
                max_tokens=1000,
                temperature=0.8
            )
            
            new_chapter = response.choices[0].message.content.strip()
            chapters.append({
                'chapter_number': i,
                'content': new_chapter,
                'word_count': len(new_chapter.split())
            })
            
            current_story += "\n\n" + new_chapter
        
        total_words = sum(chapter['word_count'] for chapter in chapters)
        
        return {
            'success': True,
            'data': {
                'chapters': chapters,
                'total_chapters': len(chapters),
                'total_words': total_words,
                'agent': 'OpenAI',
                'title': title
            }
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao gerar roteiro com ChatGPT: {str(e)}'
        }

def generate_script_chapters_with_gemini(title, context, num_chapters, api_key=None):
    """Gerar roteiro completo com múltiplos capítulos usando Gemini com retry automático"""
    import google.generativeai as genai
    import sys
    import os
    
    # Adicionar o diretório routes ao path para importar funções
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'routes'))
    from routes.automations import get_next_gemini_key, handle_gemini_429_error, get_gemini_keys_count
    
    # Usar a quantidade real de chaves disponíveis
    max_retries = get_gemini_keys_count() if get_gemini_keys_count() > 0 else 1
    print(f"🔑 Usando {max_retries} chaves Gemini para roteiro")
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
                print(f"🔄 Tentativa {attempt + 1}/{max_retries}: Usando rotação de chaves Gemini para roteiro")
            
            # Configurar Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            base_prompt = f"""
Você é um roteirista especializado em conteúdo viral para YouTube.

Título: {title}
Contexto: {context}

Escreva uma história de aproximadamente 500 palavras que seja o primeiro capítulo desta narrativa. 
A história deve começar com uma versão sensacionalista do gancho baseada no título. 

O tom da escrita deve ser simples, direto e emocional, como se a história estivesse sendo contada 
por um amigo em uma conversa informal. Use palavras fáceis, frases curtas e um ritmo leve.

Regras importantes:
1. Intensidade Emotiva - Cada frase deve transmitir emoção
2. Urgência e Ritmo - Intercale frases curtas de ação
3. Sensação Cinematográfica - Altere o foco entre close-ups e planos gerais
4. Narrador Observador e Próximo - Terceira pessoa com tom coloquial
5. Linguagem de Choque - Termos impactantes
6. Proximidade com a Dor - Retrate de forma direta a dor física e emocional

Forneça apenas o texto da história, sem explicações ou comentários adicionais.
"""
            
            # Gerar primeiro capítulo
            response = model.generate_content(base_prompt)
            
            chapters = []
            current_story = response.text.strip()
            chapters.append({
                'chapter_number': 1,
                'content': current_story,
                'word_count': len(current_story.split())
            })
            
            # Gerar capítulos subsequentes
            for i in range(2, num_chapters + 1):
                continuation_prompt = f"""
{current_story}

Escreva um novo capítulo, de aproximadamente 500 palavras, que continue os eventos descritos acima, 
introduzindo uma reviravolta extremamente chocante e impactante que transforme completamente a narrativa.

{"Se este for o último capítulo, encerre definitivamente a história e adicione uma mensagem urgente de CTA." if i == num_chapters else "Não finalize a trama, mas use essa reviravolta para criar um gancho ainda mais poderoso."}

Forneça apenas o novo capítulo, sem explicações ou comentários adicionais.
"""
                
                response = model.generate_content(continuation_prompt)
                
                new_chapter = response.text.strip()
                chapters.append({
                    'chapter_number': i,
                    'content': new_chapter,
                    'word_count': len(new_chapter.split())
                })
                
                current_story += "\n\n" + new_chapter
            
            total_words = sum(chapter['word_count'] for chapter in chapters)
            print(f"✅ Sucesso na geração de roteiro com Gemini na tentativa {attempt + 1}")
            
            return {
                'success': True,
                'data': {
                    'chapters': chapters,
                    'total_chapters': len(chapters),
                    'total_words': total_words,
                    'agent': 'Gemini',
                    'title': title
                }
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
    final_error = f'Falha na geração de roteiro com Gemini após todas as {max_retries} tentativas. Último erro: {last_error}'
    return {
        'success': False,
        'error': final_error
    }

def generate_script_chapters_with_claude(title, context, num_chapters, api_key):
    """Gerar roteiro completo com múltiplos capítulos usando Claude da Anthropic"""
    try:
        if not ANTHROPIC_AVAILABLE:
            return {
                'success': False,
                'error': 'Biblioteca anthropic não instalada'
            }
        
        client = anthropic.Anthropic(api_key=api_key)
        
        base_prompt = f"""
        Você é um roteirista especializado em conteúdo viral para YouTube.
        
        Título: {title}
        Contexto: {context}
        
        Escreva uma história de aproximadamente 500 palavras que seja o primeiro capítulo desta narrativa. 
        A história deve começar com uma versão sensacionalista do gancho baseada no título. 
        
        O tom da escrita deve ser simples, direto e emocional, como se a história estivesse sendo contada 
        por um amigo em uma conversa informal. Use palavras fáceis, frases curtas e um ritmo leve.
        
        Regras importantes:
        1. Intensidade Emotiva - Cada frase deve transmitir emoção
        2. Urgência e Ritmo - Intercale frases curtas de ação
        3. Sensação Cinematográfica - Altere o foco entre close-ups e planos gerais
        4. Narrador Observador e Próximo - Terceira pessoa com tom coloquial
        5. Linguagem de Choque - Termos impactantes
        6. Proximidade com a Dor - Retrate de forma direta a dor física e emocional
        
        Forneça apenas o texto da história, sem explicações ou comentários adicionais.
        """
        
        # Gerar primeiro capítulo
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": base_prompt}]
        )
        
        chapters = []
        current_story = response.content[0].text.strip()
        chapters.append({
            'chapter_number': 1,
            'content': current_story,
            'word_count': len(current_story.split())
        })
        
        # Gerar capítulos subsequentes
        for i in range(2, num_chapters + 1):
            continuation_prompt = f"""
            {current_story}
            
            Escreva um novo capítulo, de aproximadamente 500 palavras, que continue os eventos descritos acima, 
            introduzindo uma reviravolta extremamente chocante e impactante que transforme completamente a narrativa.
            
            {"Se este for o último capítulo, encerre definitivamente a história e adicione uma mensagem urgente de CTA." if i == num_chapters else "Não finalize a trama, mas use essa reviravolta para criar um gancho ainda mais poderoso."}
            
            Forneça apenas o novo capítulo, sem explicações ou comentários adicionais.
            """
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": continuation_prompt}]
            )
            
            new_chapter = response.content[0].text.strip()
            chapters.append({
                'chapter_number': i,
                'content': new_chapter,
                'word_count': len(new_chapter.split())
            })
            
            current_story += "\n\n" + new_chapter
        
        total_words = sum(chapter['word_count'] for chapter in chapters)
        
        return {
            'success': True,
            'data': {
                'chapters': chapters,
                'total_chapters': len(chapters),
                'total_words': total_words,
                'agent': 'Claude',
                'title': title
            }
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao gerar roteiro com Claude: {str(e)}'
        }

def generate_script_chapters_with_openrouter(title, context, num_chapters, api_key):
    """Gerar roteiro completo com múltiplos capítulos usando OpenRouter"""
    try:
        base_prompt = f"""
        Você é um roteirista especializado em conteúdo viral para YouTube.
        
        Título: {title}
        Contexto: {context}
        
        Escreva uma história de aproximadamente 500 palavras que seja o primeiro capítulo desta narrativa. 
        A história deve começar com uma versão sensacionalista do gancho baseada no título. 
        
        O tom da escrita deve ser simples, direto e emocional, como se a história estivesse sendo contada 
        por um amigo em uma conversa informal. Use palavras fáceis, frases curtas e um ritmo leve.
        
        Regras importantes:
        1. Intensidade Emotiva - Cada frase deve transmitir emoção
        2. Urgência e Ritmo - Intercale frases curtas de ação
        3. Sensação Cinematográfica - Altere o foco entre close-ups e planos gerais
        4. Narrador Observador e Próximo - Terceira pessoa com tom coloquial
        5. Linguagem de Choque - Termos impactantes
        6. Proximidade com a Dor - Retrate de forma direta a dor física e emocional
        
        Forneça apenas o texto da história, sem explicações ou comentários adicionais.
        """
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "Auto Video Producer"
        }
        
        # Gerar primeiro capítulo
        data = {
            "model": "anthropic/claude-3-sonnet",
            "messages": [{"role": "user", "content": base_prompt}],
            "max_tokens": 1000,
            "temperature": 0.8
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code}")
        
        result = response.json()
        current_story = result['choices'][0]['message']['content'].strip()
        
        chapters = []
        chapters.append({
            'chapter_number': 1,
            'content': current_story,
            'word_count': len(current_story.split())
        })
        
        # Gerar capítulos subsequentes
        for i in range(2, num_chapters + 1):
            continuation_prompt = f"""
            {current_story}
            
            Escreva um novo capítulo, de aproximadamente 500 palavras, que continue os eventos descritos acima, 
            introduzindo uma reviravolta extremamente chocante e impactante que transforme completamente a narrativa.
            
            {"Se este for o último capítulo, encerre definitivamente a história e adicione uma mensagem urgente de CTA." if i == num_chapters else "Não finalize a trama, mas use essa reviravolta para criar um gancho ainda mais poderoso."}
            
            Forneça apenas o novo capítulo, sem explicações ou comentários adicionais.
            """
            
            data = {
                "model": "anthropic/claude-3-sonnet",
                "messages": [{"role": "user", "content": continuation_prompt}],
                "max_tokens": 1000,
                "temperature": 0.8
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code}")
            
            result = response.json()
            new_chapter = result['choices'][0]['message']['content'].strip()
            chapters.append({
                'chapter_number': i,
                'content': new_chapter,
                'word_count': len(new_chapter.split())
            })
            
            current_story += "\n\n" + new_chapter
        
        total_words = sum(chapter['word_count'] for chapter in chapters)
        
        return {
            'success': True,
            'data': {
                'chapters': chapters,
                'total_chapters': len(chapters),
                'total_words': total_words,
                'agent': 'OpenRouter',
                'title': title
            }
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao gerar roteiro com OpenRouter: {str(e)}'
        }
