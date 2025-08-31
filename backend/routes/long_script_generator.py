import time
import json
import requests
import os
import sys
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
import pickle
from routes.automations import get_next_gemini_key, handle_gemini_429_error
from routes.automations import save_to_cache, get_from_cache, get_gemini_keys_count

def gerar_com_gemini(prompt, title_generator=None):
    """Função para gerar conteúdo usando API do Gemini com tratamento de erros e rotação natural de chaves"""
    import google.generativeai as genai
    from routes.automations import get_next_gemini_key, handle_gemini_429_error, get_gemini_keys_count
    
    # Usar a quantidade real de chaves disponíveis
    max_retries = get_gemini_keys_count() if get_gemini_keys_count() > 0 else 1
    print(f"🔑 Usando {max_retries} chaves Gemini para scripts longos")
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Obter a próxima chave Gemini disponível
            api_key = get_next_gemini_key()
            if not api_key:
                raise Exception("Nenhuma chave Gemini disponível")
            
            print(f"🔑 Tentativa {attempt + 1}/{max_retries} com chave Gemini: {api_key[:20]}...")
            
            # Configurar a API do Gemini
            genai.configure(api_key=api_key)
            
            # Usar o modelo Gemini 1.5 Flash
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Gerar conteúdo
            response = model.generate_content(prompt)
            
            if response and hasattr(response, 'text') and response.text:
                print(f"✅ Conteúdo gerado com sucesso na tentativa {attempt + 1}")
                return response.text
            else:
                raise Exception("Resposta vazia da API Gemini")
                
        except Exception as e:
            last_error = e
            error_str = str(e)
            print(f"❌ Erro na tentativa {attempt + 1}/{max_retries}: {e}")
            
            # Verificar se é um erro 429 (quota excedida)
            if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
                print(f"⚠️ Erro 429/quota na tentativa {attempt + 1}/{max_retries}: {e}")
                # Tentar obter uma nova chave, passando a chave atual como parâmetro
                handle_gemini_429_error(error_str, api_key)
                time.sleep(1)  # Pausa otimizada antes de tentar novamente
                continue
            else:
                # Para outros erros, registrar e tentar próxima chave
                print(f"⚠️ Erro não relacionado à quota, tentando próxima chave...")
                if attempt < max_retries - 1:
                    continue
                else:
                    break
    
    # Se todas as tentativas falharam, lançar o último erro
    raise Exception(f"Falha ao gerar conteúdo com Gemini após {max_retries} tentativas. Último erro: {last_error}")

def gerar_com_openai(prompt, title_generator=None):
    """Função para gerar conteúdo usando API do OpenAI como fallback"""
    if not title_generator or not title_generator.openai_client:
        raise Exception("Cliente OpenAI não configurado")
    
    try:
        response = title_generator.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um roteirista profissional especializado em conteúdo para YouTube."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.8
        )
        
        if response and response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            raise Exception("Resposta vazia da API OpenAI")
    except Exception as e:
        print(f"❌ Erro na API OpenAI: {e}")
        raise Exception(f"Falha ao gerar conteúdo com OpenAI: {e}")

def gerar_com_openrouter(prompt, model, api_key):
    """Função para gerar conteúdo usando API do OpenRouter como fallback"""
    try:
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
                    {'role': 'system', 'content': 'Você é um roteirista profissional especializado em conteúdo para YouTube.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 1000,
                'temperature': 0.8
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            return content
        else:
            raise Exception(f'OpenRouter API error: {response.status_code}')
    except Exception as e:
        print(f"❌ Erro na API OpenRouter: {e}")
        raise Exception(f"Falha ao gerar conteúdo com OpenRouter: {e}")

def gerar_conteudo(prompt, title_generator=None, openrouter_api_key=None, openrouter_model='auto'):
    """Função unificada para gerar conteúdo com fallback entre provedores"""
    erros = []
    
    # Tentar primeiro com Gemini
    try:
        print("🔍 [GEMINI] Tentando gerar conteúdo com Gemini...")
        return gerar_com_gemini(prompt, title_generator)
    except Exception as e:
        erro_gemini = str(e)
        erros.append(f"Gemini: {erro_gemini}")
        print(f"⚠️ [GEMINI] Falha: {erro_gemini}")
        
        # Verificar se foi falha de quota/esgotamento
        if "429" in erro_gemini or "quota" in erro_gemini.lower() or "exceeded" in erro_gemini.lower() or "esgotad" in erro_gemini.lower():
            print("⚠️ [GEMINI] Falha por quota esgotada. Tentando fallback para outros provedores...")
    
    # Fallback para OpenAI
    try:
        print("🔍 [OPENAI] Tentando gerar conteúdo com OpenAI...")
        return gerar_com_openai(prompt, title_generator)
    except Exception as e:
        erro_openai = str(e)
        erros.append(f"OpenAI: {erro_openai}")
        print(f"⚠️ [OPENAI] Falha: {erro_openai}")
    
    # Fallback para OpenRouter
    if openrouter_api_key:
        try:
            print("🔍 [OPENROUTER] Tentando gerar conteúdo com OpenRouter...")
            return gerar_com_openrouter(prompt, openrouter_model, openrouter_api_key)
        except Exception as e:
            erro_openrouter = str(e)
            erros.append(f"OpenRouter: {erro_openrouter}")
            print(f"⚠️ [OPENROUTER] Falha: {erro_openrouter}")
    
    # Se todos falharam, fornecer detalhes dos erros
    detalhes_erros = "\n".join(erros)
    print(f"❌ [FALHA GERAL] Todos os provedores de IA falharam. Detalhes:\n{detalhes_erros}")
    
    # Verificar se a falha principal foi do Gemini (quota)
    gemini_quota_error = any("429" in erro or "quota" in erro.lower() or "exceeded" in erro.lower() for erro in erros if "Gemini:" in erro)
    
    if gemini_quota_error:
        mensagem_erro = f"Falha na geração de roteiro: O Gemini atingiu o limite de quota diário. Tente novamente mais tarde ou configure mais chaves Gemini.\n\nDetalhes dos erros:\n{detalhes_erros}"
    else:
        mensagem_erro = f"Falha na geração de roteiro: Todos os provedores de IA falharam.\n\nDetalhes dos erros:\n{detalhes_erros}"
    
    raise Exception(mensagem_erro)

def validar_capitulo(capitulo, min_palavras=350, max_palavras=650):
    """Valida se o capítulo atende aos requisitos mínimos"""
    if not capitulo or not isinstance(capitulo, str):
        return False, "Capítulo inválido ou vazio"
    
    # Verificar tamanho aproximado (500 palavras com margem mais flexível)
    palavras = capitulo.split()
    if len(palavras) < min_palavras:  # Mínimo de 350 palavras
        return False, f"Capítulo muito curto: {len(palavras)} palavras (mínimo: {min_palavras})"
    
    if len(palavras) > max_palavras:  # Máximo de 650 palavras
        return False, f"Capítulo muito longo: {len(palavras)} palavras (máximo: {max_palavras})"
    
    # Verificar coerência básica (se tem frases completas) - critério mais flexível
    frases = [f.strip() for f in capitulo.split('.') if f.strip()]
    if len(frases) < 3:  # Mínimo de 3 frases
        return False, f"Capítulo com poucas frases: {len(frases)} frases (mínimo: 3)"
    
    # Verificar se há parágrafos estruturados - critério mais flexível
    paragrafos = [p.strip() for p in capitulo.split('\n\n') if p.strip()]
    if len(paragrafos) < 1:  # Mínimo de 1 parágrafo
        return False, f"Capítulo com pouca estrutura: {len(paragrafos)} parágrafos (mínimo: 1)"
    
    return True, f"Capítulo válido: {len(palavras)} palavras, {len(frases)} frases, {len(paragrafos)} parágrafos"

def gerar_resumo_capitulo(capitulo):
    """Gera um resumo conciso com 3-4 frases de um capítulo"""
    prompt_resumo = f"""
    Analise o seguinte capítulo e crie um resumo conciso com 3-4 frases:
    
    {capitulo}
    
    O resumo deve focar nos eventos principais e ações dos personagens,
    sem incluir detalhes excessivos. Será usado como contexto para o próximo capítulo.
    """
    
    return prompt_resumo

def get_chapter_summary_cache_dir() -> str:
    """
    Retorna o diretório de cache para resumos de capítulos.
    
    Returns:
        str: Caminho para o diretório de cache
    """
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache", "chapter_summaries")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def clear_chapter_summary_cache(max_age_hours: int = 24) -> int:
    """
    Limpa o cache de resumos de capítulos mais antigos que max_age_hours.
    
    Args:
        max_age_hours: Idade máxima em horas para manter os itens no cache
        
    Returns:
        int: Número de itens removidos do cache
    """
    cache_dir = get_chapter_summary_cache_dir()
    removed_count = 0
    
    if not os.path.exists(cache_dir):
        return removed_count
    
    current_time = datetime.now()
    max_age = timedelta(hours=max_age_hours)
    
    for filename in os.listdir(cache_dir):
        file_path = os.path.join(cache_dir, filename)
        if os.path.isfile(file_path):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if current_time - file_mtime > max_age:
                os.remove(file_path)
                removed_count += 1
    
    return removed_count

def generate_long_script_with_context(titulo, premissa, numero_capitulos, title_generator=None, openrouter_api_key=None, openrouter_model='auto', update_callback=None, long_script_prompt=None, custom_prompts=None, request_config=None):
    """
    Gera um roteiro longo com capítulos sequenciais e resumos contextuais entre capítulos.
    
    Args:
        titulo (str): Título do roteiro
        premissa (str): Premissa do roteiro
        numero_capitulos (int): Número de capítulos a serem gerados
        title_generator: Objeto com configurações de IA
        openrouter_api_key (str): Chave da API do OpenRouter
        openrouter_model (str): Modelo do OpenRouter a ser usado
        update_callback (function): Função de callback para atualizações de progresso
        long_script_prompt (str): Prompt personalizado adicional (antigo método)
        custom_prompts (dict): Prompts personalizados por fase {'intro': str, 'middle': str, 'conclusion': str, 'default_prompts': dict}
        request_config (dict): Configuração da requisição incluindo agent_prompts para agentes especializados
        
    Returns:
        dict: Dicionário com o roteiro gerado e informações adicionais
    """
    # Iniciar medição de performance
    start_time = time.time()
    
    # Inicializar request_config se não fornecido
    if request_config is None:
        request_config = {}
    
    try:
        print(f"🚀 Iniciando geração de roteiro longo: {titulo}")
        print(f"📖 Número de capítulos: {numero_capitulos}")
        print(f"📊 Título: {titulo}")
        print(f"📝 Premissa: {premissa[:100]}{'...' if len(premissa) > 100 else ''}")
        
        # Inicializar arrays para armazenar capítulos e resumos
        capitulos = []
        resumos = []
        chapter_generation_times = []
        summary_generation_times = []
        
        # Processar prompts personalizados
        prompts = {
            'intro': None,
            'middle': None, 
            'conclusion': None,
            'use_default': True
        }
        
        if custom_prompts:
            # Usar prompts personalizados por fase se fornecidos
            if custom_prompts.get('custom_inicio'):
                prompts['intro'] = custom_prompts['custom_inicio']
                prompts['use_default'] = False
            if custom_prompts.get('custom_meio'):
                prompts['middle'] = custom_prompts['custom_meio']
                prompts['use_default'] = False
            if custom_prompts.get('custom_fim'):
                prompts['conclusion'] = custom_prompts['custom_fim']
                prompts['use_default'] = False
                
            # Usar prompts padrão editados se fornecidos
            if custom_prompts.get('default_prompt_intro'):
                prompts['default_intro'] = custom_prompts['default_prompt_intro']
            if custom_prompts.get('default_prompt_middle'):
                prompts['default_middle'] = custom_prompts['default_prompt_middle']
            if custom_prompts.get('default_prompt_conclusion'):
                prompts['default_conclusion'] = custom_prompts['default_prompt_conclusion']
        
        # Limpar cache antigo antes de começar
        cleared_cache = clear_chapter_summary_cache(max_age_hours=48)
        if cleared_cache > 0:
            print(f"🧹 Limpos {cleared_cache} itens do cache antigo")
        
        # 2.2. Geração do Capítulo 1 (Introdução)
        print("📝 Gerando Capítulo 1 (Introdução)")
        
        # Escolher prompt para introdução
        if prompts.get('intro'):  # Prompt personalizado de introdução
            prompt_base = prompts['intro']
            prompt_capitulo_1 = prompt_base.format(
                titulo=titulo, 
                premissa=premissa,
                i=1
            )
            print("✨ Usando prompt personalizado para introdução")
        elif prompts.get('default_intro'):  # Prompt padrão editado
            prompt_capitulo_1 = prompts['default_intro'].format(
                titulo=titulo,
                premissa=premissa
            )
            print("🔧 Usando prompt padrão editado para introdução")
        else:  # Prompt padrão do sistema ou agente especializado
            # Verificar se há agente especializado ativo
            agent_prompts = request_config.get('agent_prompts', {})
            if agent_prompts and 'inicio' in agent_prompts:
                prompt_capitulo_1 = agent_prompts['inicio'].format(
                    titulo=titulo,
                    premissa=premissa
                )
                print("🎆 Usando prompt de agente especializado para introdução")
            else:
                prompt_capitulo_1 = f"""
        Você é um roteirista profissional especializado em conteúdo para YouTube.
        
        TÍTULO: {titulo}
        PREMISSA: {premissa}
        
        INSTRUÇÕES:
        - Escreva o primeiro capítulo (introdução) deste roteiro
        - O capítulo deve ter aproximadamente 500 palavras
        - Estabeleça os personagens principais, cenário e conflito inicial
        - Use uma linguagem envolvente adequada para vídeos do YouTube
        - Escreva apenas o conteúdo do capítulo, sem títulos ou marcações
        {f'\n        {long_script_prompt}' if long_script_prompt else ''}
        """
                print("📄 Usando prompt padrão do sistema para introdução")
        
        # Gerar Capítulo 1 com validação e retentativas
        max_tentativas = get_gemini_keys_count() if get_gemini_keys_count() > 0 else 3
        print(f"🔑 Usando {max_tentativas} chaves Gemini disponíveis para geração do Capítulo 1")
        capitulo_1_valido = False
        tentativa = 0
        chapter_start_time = time.time()
        
        while not capitulo_1_valido and tentativa < max_tentativas:
            print(f"📝 Gerando Capítulo 1 (Tentativa {tentativa + 1}/{max_tentativas})")
            attempt_start_time = time.time()
            
            capitulo_1 = gerar_conteudo(prompt_capitulo_1, title_generator, openrouter_api_key, openrouter_model)
            
            # Medir tempo de geração
            attempt_time = time.time() - attempt_start_time
            print(f"⏱️ Capítulo 1 (tentativa {tentativa + 1}) gerado em {attempt_time:.2f} segundos")
            
            # Validar capítulo
            capitulo_valido, mensagem = validar_capitulo(capitulo_1)
            if capitulo_valido:
                capitulo_1_valido = True
                print(f"✅ Capítulo 1 validado: {mensagem}")
            else:
                print(f"❌ Capítulo 1 inválido: {mensagem}")
                tentativa += 1
                if tentativa < max_tentativas:
                    print("🔄 Tentando gerar novamente...")
                    time.sleep(1)  # Pausa otimizada antes de tentar novamente
        
        if not capitulo_1_valido:
            raise Exception(f"Não foi possível gerar um Capítulo 1 válido após {max_tentativas} tentativas")
        
        # Medir tempo total de geração do capítulo
        chapter_total_time = time.time() - chapter_start_time
        chapter_generation_times.append(chapter_total_time)
        print(f"⏱️ Capítulo 1 gerado em {chapter_total_time:.2f} segundos (total com {tentativa + 1} tentativas)")
        
        capitulos.append(capitulo_1)
        
        if update_callback:
            progress = (1 / numero_capitulos) * 100
            update_callback({
                'progress': progress,
                'current_chapter': 1,
                'total_chapters': numero_capitulos,
                'chapters': [{'chapter_number': 1, 'title': 'Introdução', 'content': capitulo_1}]
            })
        
        # 2.3. Geração do Resumo do Capítulo 1 com cache
        print("📝 Gerando Resumo do Capítulo 1")
        summary_start_time = time.time()
        
        # Verificar cache para resumo do capítulo 1
        hash_capitulo_1 = hashlib.md5(capitulo_1.encode()).hexdigest()
        cache_key = f"chapter_summary_{hash_capitulo_1}"
        
        resumo_1 = get_from_cache(cache_key, {}, cache_subdir="chapter_summaries")
        
        if resumo_1 is None:
            print("🔄 Cache não encontrado, gerando novo resumo")
            prompt_resumo_1 = gerar_resumo_capitulo(capitulo_1)
            resumo_1 = gerar_conteudo(prompt_resumo_1, title_generator, openrouter_api_key, openrouter_model)
            
            # Salvar no cache
            save_to_cache(cache_key, {}, resumo_1, cache_subdir="chapter_summaries")
            print("💾 Resumo salvo no cache")
        else:
            print("✅ Resumo recuperado do cache")
        
        # Medir tempo de geração do resumo
        summary_time = time.time() - summary_start_time
        summary_generation_times.append(summary_time)
        print(f"⏱️ Resumo do Capítulo 1 gerado em {summary_time:.2f} segundos")
        
        resumos.append(resumo_1)
        
        # Pausa para evitar limite de taxa
        time.sleep(3)
        
        # 2.4. Loop para Capítulos Seguintes (2 a N-1)
        for i in range(2, numero_capitulos):
            print(f"📝 Gerando Capítulo {i}")
            
            # Escolher prompt para desenvolvimento
            if prompts.get('middle'):  # Prompt personalizado para meio
                prompt_base = prompts['middle']
                prompt_capitulo = prompt_base.format(
                    titulo=titulo,
                    premissa=premissa,
                    i=i,
                    resumo_anterior=resumos[i-2]
                )
                print(f"✨ Usando prompt personalizado para Capítulo {i}")
            elif prompts.get('default_middle'):  # Prompt padrão editado
                prompt_capitulo = prompts['default_middle'].format(
                    titulo=titulo,
                    premissa=premissa,
                    i=i,
                    resumo_anterior=resumos[i-2]
                )
                print(f"🔧 Usando prompt padrão editado para Capítulo {i}")
            else:  # Prompt padrão do sistema ou agente especializado
                # Verificar se há agente especializado ativo
                agent_prompts = request_config.get('agent_prompts', {})
                if agent_prompts and 'meio' in agent_prompts:
                    # Substituir variáveis contextuais no prompt do agente
                    prompt_capitulo = agent_prompts['meio'].format(
                        titulo=titulo,
                        premissa=premissa
                    )
                    # Substituir manualmente a variável de resumo contextual
                    prompt_capitulo = prompt_capitulo.replace('{resumos[i-2]}', resumos[i-2])
                    print(f"🎆 Usando prompt de agente especializado para Capítulo {i}")
                else:
                    prompt_capitulo = f"""
            Você é um roteirista profissional especializado em conteúdo para YouTube.
            
            TÍTULO: {titulo}
            PREMISSA: {premissa}
            
            CONTEXTO DO CAPÍTULO ANTERIOR:
            {resumos[i-2]}
            
            INSTRUÇÕES:
            - Escreva o capítulo {i} deste roteiro, continuando a história
            - O capítulo deve ter aproximadamente 500 palavras
            - Mantenha coerência com o contexto fornecido
            - Desenvolva a narrativa de forma orgânica
            - Use uma linguagem envolvente adequada para vídeos do YouTube
            - Escreva apenas o conteúdo do capítulo, sem títulos ou marcações
            {f'\n            {long_script_prompt}' if long_script_prompt else ''}
            """
                    print(f"📄 Usando prompt padrão do sistema para Capítulo {i}")
            
            # Gerar capítulo atual com validação e retentativas
            capitulo_valido = False
            tentativa = 0
            max_tentativas = get_gemini_keys_count() if get_gemini_keys_count() > 0 else 3
            print(f"🔑 Usando {max_tentativas} chaves Gemini disponíveis para geração do Capítulo {i}")
            chapter_start_time = time.time()
            
            while not capitulo_valido and tentativa < max_tentativas:
                print(f"📝 Gerando Capítulo {i} (Tentativa {tentativa + 1}/{max_tentativas})")
                attempt_start_time = time.time()
                
                capitulo_atual = gerar_conteudo(prompt_capitulo, title_generator, openrouter_api_key, openrouter_model)
                
                # Medir tempo de geração
                attempt_time = time.time() - attempt_start_time
                print(f"⏱️ Capítulo {i} (tentativa {tentativa + 1}) gerado em {attempt_time:.2f} segundos")
                
                # Validar capítulo
                capitulo_valido, mensagem = validar_capitulo(capitulo_atual)
                if capitulo_valido:
                    print(f"✅ Capítulo {i} validado: {mensagem}")
                else:
                    print(f"❌ Capítulo {i} inválido: {mensagem}")
                    tentativa += 1
                    if tentativa < max_tentativas:
                        print("🔄 Tentando gerar novamente...")
                        time.sleep(1)  # Pausa otimizada antes de tentar novamente
            
            if not capitulo_valido:
                raise Exception(f"Não foi possível gerar um Capítulo {i} válido após {max_tentativas} tentativas")
            
            # Medir tempo total de geração do capítulo
            chapter_total_time = time.time() - chapter_start_time
            chapter_generation_times.append(chapter_total_time)
            print(f"⏱️ Capítulo {i} gerado em {chapter_total_time:.2f} segundos (total com {tentativa + 1} tentativas)")
            
            capitulos.append(capitulo_atual)
            
            # Gerar resumo do capítulo atual com cache
            summary_start_time = time.time()
            
            hash_capitulo_atual = hashlib.md5(capitulo_atual.encode()).hexdigest()
            cache_key = f"chapter_summary_{hash_capitulo_atual}"
            
            resumo_atual = get_from_cache(cache_key, {}, cache_subdir="chapter_summaries")
            
            if resumo_atual is None:
                print(f"🔄 Cache não encontrado para Capítulo {i}, gerando novo resumo")
                prompt_resumo = gerar_resumo_capitulo(capitulo_atual)
                resumo_atual = gerar_conteudo(prompt_resumo, title_generator, openrouter_api_key, openrouter_model)
                
                # Salvar no cache
                save_to_cache(cache_key, {}, resumo_atual, cache_subdir="chapter_summaries")
                print(f"💾 Resumo do Capítulo {i} salvo no cache")
            else:
                print(f"✅ Resumo do Capítulo {i} recuperado do cache")
            
            # Medir tempo de geração do resumo
            summary_time = time.time() - summary_start_time
            summary_generation_times.append(summary_time)
            print(f"⏱️ Resumo do Capítulo {i} gerado em {summary_time:.2f} segundos")
            
            resumos.append(resumo_atual)
            
            if update_callback:
                progress = (i / numero_capitulos) * 100
                chapters_data = []
                for j, cap in enumerate(capitulos):
                    chapters_data.append({
                        'chapter_number': j + 1,
                        'title': f"Capítulo {j + 1}",
                        'content': cap
                    })
                
                update_callback({
                    'progress': progress,
                    'current_chapter': i,
                    'total_chapters': numero_capitulos,
                    'chapters': chapters_data
                })
            
            # Pausa para evitar limite de taxa
            time.sleep(3)
        
        # 2.5. Geração do Capítulo Final (Conclusão)
        if numero_capitulos > 1:
            print(f"📝 Gerando Capítulo Final (Conclusão)")
            
            # Escolher prompt para conclusão
            if prompts.get('conclusion'):  # Prompt personalizado para conclusão
                prompt_base = prompts['conclusion']
                prompt_conclusao = prompt_base.format(
                    titulo=titulo,
                    premissa=premissa,
                    resumo_anterior=resumos[-1]
                )
                print("✨ Usando prompt personalizado para conclusão")
            elif prompts.get('default_conclusion'):  # Prompt padrão editado
                prompt_conclusao = prompts['default_conclusion'].format(
                    titulo=titulo,
                    premissa=premissa,
                    resumo_anterior=resumos[-1]
                )
                print("🔧 Usando prompt padrão editado para conclusão")
            else:  # Prompt padrão do sistema ou agente especializado
                # Verificar se há agente especializado ativo
                agent_prompts = request_config.get('agent_prompts', {})
                if agent_prompts and 'fim' in agent_prompts:
                    # Substituir variáveis contextuais no prompt do agente
                    prompt_conclusao = agent_prompts['fim'].format(
                        titulo=titulo,
                        premissa=premissa
                    )
                    # Substituir manualmente a variável de resumo contextual
                    prompt_conclusao = prompt_conclusao.replace('{resumos[-1]}', resumos[-1])
                    print("🎆 Usando prompt de agente especializado para conclusão")
                else:
                    prompt_conclusao = f"""
            Você é um roteirista profissional especializado em conteúdo para YouTube.
            
            TÍTULO: {titulo}
            PREMISSA: {premissa}
            
            CONTEXTO DO CAPÍTULO ANTERIOR:
            {resumos[-1]}
            
            INSTRUÇÕES:
            - Escreva o capítulo final (conclusão) deste roteiro
            - O capítulo deve ter aproximadamente 500 palavras
            - Amarre todas as pontas soltas da história
            - Proporcione um fechamento satisfatório para os personagens
            - Use uma linguagem envolvente adequada para vídeos do YouTube
            - Escreva apenas o conteúdo do capítulo, sem títulos ou marcações
            {f'\n            {long_script_prompt}' if long_script_prompt else ''}
            """
                    print("📄 Usando prompt padrão do sistema para conclusão")
            
            # Gerar Capítulo Final com validação e retentativas
            capitulo_final_valido = False
            tentativa = 0
            max_tentativas = get_gemini_keys_count() if get_gemini_keys_count() > 0 else 3
            print(f"🔑 Usando {max_tentativas} chaves Gemini disponíveis para geração do Capítulo Final")
            chapter_start_time = time.time()
            
            while not capitulo_final_valido and tentativa < max_tentativas:
                print(f"📝 Gerando Capítulo Final (Tentativa {tentativa + 1}/{max_tentativas})")
                attempt_start_time = time.time()
                
                capitulo_final = gerar_conteudo(prompt_conclusao, title_generator, openrouter_api_key, openrouter_model)
                
                # Medir tempo de geração
                attempt_time = time.time() - attempt_start_time
                print(f"⏱️ Capítulo Final (tentativa {tentativa + 1}) gerado em {attempt_time:.2f} segundos")
                
                # Validar capítulo final
                capitulo_valido, mensagem = validar_capitulo(capitulo_final)
                if capitulo_valido:
                    capitulo_final_valido = True
                    print(f"✅ Capítulo Final validado: {mensagem}")
                else:
                    print(f"❌ Capítulo Final inválido: {mensagem}")
                    tentativa += 1
                    if tentativa < max_tentativas:
                        print("🔄 Tentando gerar novamente...")
                        time.sleep(1)  # Pausa otimizada antes de tentar novamente
            
            if not capitulo_final_valido:
                raise Exception(f"Não foi possível gerar um Capítulo Final válido após {max_tentativas} tentativas")
            
            # Medir tempo total de geração do capítulo
            chapter_total_time = time.time() - chapter_start_time
            chapter_generation_times.append(chapter_total_time)
            print(f"⏱️ Capítulo Final gerado em {chapter_total_time:.2f} segundos (total com {tentativa + 1} tentativas)")
            
            capitulos.append(capitulo_final)
        
        # 2.6. Concatenação Final com Limpeza
        # Aplicar limpeza em cada capítulo antes de concatenar
        capitulos_limpos = []
        for capitulo in capitulos:
            capitulo_limpo = _clean_narrative_content(capitulo)
            capitulos_limpos.append(capitulo_limpo)
        
        # Unir todos os capítulos limpos em um único roteiro
        roteiro_completo = "\n\n".join(capitulos_limpos)
        
        # Roteiro final sem cabeçalho técnico (narrativa limpa)
        roteiro_final = roteiro_completo
        
        # Preparar dados de retorno
        chapters_data = []
        for i, cap_limpo in enumerate(capitulos_limpos):
            chapters_data.append({
                'chapter_number': i + 1,
                'title': f"Capítulo {i + 1}",
                'content': cap_limpo,
                'word_count': len(cap_limpo.split())
            })
        
        # Calcular estatísticas
        word_count = len(roteiro_completo.split())
        estimated_duration = max(word_count / 150, numero_capitulos * 2)  # em minutos
        
        # Calcular estatísticas de performance
        total_time = time.time() - start_time
        avg_chapter_time = sum(chapter_generation_times) / len(chapter_generation_times) if chapter_generation_times else 0
        avg_summary_time = sum(summary_generation_times) / len(summary_generation_times) if summary_generation_times else 0
        
        # Exibir estatísticas de performance
        print("📊 Estatísticas de Performance:")
        print(f"⏱️ Tempo total de geração: {total_time:.2f} segundos")
        print(f"⏱️ Tempo médio por capítulo: {avg_chapter_time:.2f} segundos")
        print(f"⏱️ Tempo médio por resumo: {avg_summary_time:.2f} segundos")
        print(f"📝 Total de capítulos gerados: {len(capitulos)}")
        print(f"📝 Total de resumos gerados/cached: {len(resumos)}")
        print(f"⏱️ Duração estimada do vídeo: {estimated_duration}")
        
        print(f"✅ Roteiro longo gerado com sucesso: {numero_capitulos} capítulos, {word_count} palavras")
        
        return {
            'success': True,
            'data': {
                'script': roteiro_final.strip(),
                'chapters': chapters_data,
                'estimated_duration': estimated_duration,
                'word_count': word_count,
                'summaries': resumos,
                'title': titulo,
                'premise': premissa,
                'number_of_chapters': numero_capitulos,
                'performance_stats': {
                    'total_generation_time': total_time,
                    'avg_chapter_time': avg_chapter_time,
                    'avg_summary_time': avg_summary_time,
                    'chapter_generation_times': chapter_generation_times,
                    'summary_generation_times': summary_generation_times
                }
            }
        }
        
    except Exception as e:
        print(f"❌ Erro na geração de roteiro longo: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def _clean_narrative_content(content: str) -> str:
    """Limpar conteúdo narrativo de marcações técnicas para narrativa fluída
    
    Reutiliza a lógica de limpeza do simple_script_generator.py para manter consistência
    conforme especificação do projeto de reutilizar funções de limpeza existentes.
    """
    
    import re
    
    # Remover marcações de formatação
    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # **texto**
    content = re.sub(r'\*([^*]+)\*', r'\1', content)      # *texto*
    content = re.sub(r'"([^"]+)"', r'\1', content)        # "texto"
    content = re.sub(r'`([^`]+)`', r'\1', content)        # `texto`
    
    # Remover marcações de narrador e direções
    content = re.sub(r'Narrador:\s*', '', content, flags=re.IGNORECASE)  # Narrador:
    content = re.sub(r'NARRADOR:\s*', '', content)        # NARRADOR:
    content = re.sub(r'\(Narrador[^)]*\)', '', content, flags=re.IGNORECASE)  # (Narrador...)
    content = re.sub(r'\*\*Narrador[^*]*\*\*', '', content, flags=re.IGNORECASE)  # **Narrador**
    
    # Remover direções de câmera e stage directions
    content = re.sub(r'A câmera[^.]*\.', '', content, flags=re.IGNORECASE)  # A câmera faz um paneo.
    content = re.sub(r'\([^)]*câmera[^)]*\)', '', content, flags=re.IGNORECASE)  # (câmera...)
    content = re.sub(r'\([^)]*[Pp]aneo[^)]*\)', '', content)  # (paneo...)
    content = re.sub(r'\([^)]*[Ss]ussurrando[^)]*\)', '', content)  # (Sussurrando)
    content = re.sub(r'\([^)]*[Cc]lose[^)]*\)', '', content)  # (Close...)
    content = re.sub(r'\([^)]*[Zz]oom[^)]*\)', '', content)  # (Zoom...)
    
    # Remover marcações de personagem (Nome:)
    content = re.sub(r'\n[A-Z][a-zA-Z\s]*:\s*\([^)]*\)', '', content)  # Arthur: (Sussurrando)
    content = re.sub(r'\n[A-Z][a-zA-Z\s]*:\s*', '\n', content)  # Arthur: 
    content = re.sub(r'^[A-Z][a-zA-Z\s]*:\s*\([^)]*\)', '', content)  # No início
    content = re.sub(r'^[A-Z][a-zA-Z\s]*:\s*', '', content)  # No início
    
    # Remover notas técnicas e direções de produção
    content = re.sub(r'\([^)]*[Mm]úsica[^)]*\)', '', content)  # (Música...)
    content = re.sub(r'\([^)]*[Ss]om[^)]*\)', '', content)     # (Som...)
    content = re.sub(r'\([^)]*[Ff]ade[^)]*\)', '', content)    # (Fade...)
    content = re.sub(r'\([^)]*[Cc]orte[^)]*\)', '', content)   # (Corte...)
    content = re.sub(r'\([^)]*[Cc]âmera[^)]*\)', '', content)  # (Câmera...)
    content = re.sub(r'\([^)]*[Cc]ena[^)]*\)', '', content)    # (Cena...)
    content = re.sub(r'\([^)]*[Ii]magen[^)]*\)', '', content)  # (Imagens...)
    content = re.sub(r'\([^)]*[Ff]oco[^)]*\)', '', content)    # (Foco...)
    content = re.sub(r'\([^)]*[Vv]oz[^)]*\)', '', content)     # (Voz...)
    
    # Remover instruções técnicas genéricas entre parênteses
    content = re.sub(r'\([^)]*[Ii]nicia[^)]*\)', '', content)  # (Inicia...)
    content = re.sub(r'\([^)]*[Mm]ostra[^)]*\)', '', content)  # (Mostra...)
    content = re.sub(r'\([^)]*[Aa]parece[^)]*\)', '', content) # (Aparece...)
    
    # Remover colchetes com instruções
    content = re.sub(r'\[[^]]*\]', '', content)  # [instrução]
    
    # Remover títulos de capítulos explícitos
    content = re.sub(r'^Capítulo \d+:.*$', '', content, flags=re.MULTILINE)  # Capítulo X:
    content = re.sub(r'^CAPÍTULO \d+:.*$', '', content, flags=re.MULTILINE)  # CAPÍTULO X:
    content = re.sub(r'^Capítulo \d+ -.*$', '', content, flags=re.MULTILINE) # Capítulo X - Título
    
    # Remover informações de duração e estatísticas
    content = re.sub(r'NÚMERO DE CAPÍTULOS:.*\n', '', content)
    content = re.sub(r'ESTIMATIVA DE DURAÇÃO:.*\n', '', content)
    content = re.sub(r'TÍTULO:.*\n', '', content)
    content = re.sub(r'PREMISSA:.*\n', '', content)
    
    # Limpar quebras de linha excessivas
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Múltiplas quebras -> 2 quebras
    content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)  # Espaços no início das linhas
    
    # Limpar espaços extras
    content = re.sub(r' {2,}', ' ', content)  # Múltiplos espaços -> 1 espaço
    
    # Garantir que frases comecem com maiúscula após ponto
    content = re.sub(r'\. +([a-z])', lambda m: '. ' + m.group(1).upper(), content)
    
    return content.strip()