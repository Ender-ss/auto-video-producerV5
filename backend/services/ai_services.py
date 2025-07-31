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

def generate_titles_with_openai(source_titles, instructions, api_key):
    """Gerar títulos usando OpenAI ChatGPT"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
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
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.8
        )
        
        generated_text = response.choices[0].message.content.strip()
        titles = [title.strip() for title in generated_text.split('\n') if title.strip()]
        
        return {
            'success': True,
            'data': {
                'generated_titles': titles[:5],
                'agent': 'OpenAI',
                'processing_time': 0
            }
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao gerar títulos com ChatGPT: {str(e)}'
        }

def generate_titles_with_gemini(source_titles, instructions, api_key):
    """Gerar títulos usando Google Gemini"""
    try:
        if not GEMINI_AVAILABLE:
            return {
                'success': False,
                'error': 'Biblioteca google-generativeai não instalada'
            }
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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
        
        response = model.generate_content(prompt)
        
        if not response.text:
            return {
                'success': False,
                'error': 'Gemini não retornou conteúdo'
            }
        
        generated_text = response.text.strip()
        titles = [title.strip() for title in generated_text.split('\n') if title.strip()]
        
        return {
            'success': True,
            'data': {
                'generated_titles': titles[:5],
                'agent': 'Gemini',
                'processing_time': 0
            }
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
