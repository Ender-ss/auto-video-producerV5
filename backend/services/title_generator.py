"""
🤖 Serviço de Geração de Títulos com IA
Auto Video Producer - Geração inteligente de títulos virais
"""

import google.generativeai as genai
import json
import re
import random
from typing import List, Dict, Optional
import requests
import time

class TitleGenerator:
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        self.openrouter_api_key = None
        
    def configure_openai(self, api_key: str):
        """Configurar cliente OpenAI"""
        try:
            print(f"🔍 DEBUG: Tentando configurar OpenAI com chave: {api_key[:20]}...")
            from openai import OpenAI
            print("🔍 DEBUG: Biblioteca OpenAI importada com sucesso")

            # Validar formato da chave
            if not api_key.startswith('sk-'):
                print(f"❌ Chave OpenAI inválida: deve começar com 'sk-'")
                return False

            self.openai_client = OpenAI(api_key=api_key)
            print("🔍 DEBUG: Cliente OpenAI criado com sucesso")

            # Testar a conexão fazendo uma chamada simples
            try:
                models = self.openai_client.models.list()
                print("🔍 DEBUG: Teste de conexão OpenAI bem-sucedido")
                return True
            except Exception as test_error:
                print(f"❌ Erro no teste de conexão OpenAI: {test_error}")
                self.openai_client = None
                return False

        except ImportError as e:
            print(f"❌ Erro de importação OpenAI: {e}")
            print("💡 Instale a biblioteca: pip install openai")
            return False
        except Exception as e:
            print(f"❌ Erro ao configurar OpenAI: {e}")
            print(f"🔍 DEBUG: Tipo do erro: {type(e)}")
            self.openai_client = None
            return False
            
    def configure_gemini(self, api_key: str):
        """Configurar cliente Google Gemini"""
        try:
            print(f"🔍 DEBUG: Tentando configurar Gemini com chave: {api_key[:20]}...")
            genai.configure(api_key=api_key)
            print("🔍 DEBUG: Gemini configurado com sucesso")
            # Usar o modelo mais recente disponível
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini configurado com modelo: gemini-1.5-flash")
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar Gemini: {e}")
            print(f"🔍 DEBUG: Tipo do erro: {type(e)}")
            self.gemini_model = None
            # Tentar modelo alternativo
            try:
                self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
                print("✅ Gemini configurado com modelo alternativo: gemini-1.5-pro")
                return True
            except Exception as e2:
                print(f"❌ Erro ao configurar Gemini (modelo alternativo): {e2}")
                self.gemini_model = None
                return False

    def configure_openrouter(self, api_key: str):
        """Configurar cliente OpenRouter"""
        try:
            self.openrouter_api_key = api_key
            print("✅ OpenRouter configurado com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar OpenRouter: {e}")
            self.openrouter_api_key = None
            return False
    
    def analyze_viral_patterns(self, titles: List[str]) -> Dict:
        """Analisar padrões virais nos títulos extraídos"""
        patterns = {
            'emotional_triggers': [],
            'numbers': [],
            'power_words': [],
            'structures': [],
            'length_stats': {
                'min': 0,
                'max': 0,
                'avg': 0
            }
        }
        
        # Palavras-chave emocionais comuns
        emotional_words = [
            'INCRÍVEL', 'CHOCANTE', 'SEGREDO', 'REVELADO', 'NUNCA', 'SEMPRE',
            'MELHOR', 'PIOR', 'ÚNICO', 'EXCLUSIVO', 'URGENTE', 'ÚLTIMO',
            'PRIMEIRO', 'NOVO', 'ANTIGO', 'RÁPIDO', 'FÁCIL', 'DIFÍCIL',
            'GRÁTIS', 'CARO', 'BARATO', 'RICO', 'POBRE', 'FAMOSO'
        ]
        
        # Analisar cada título
        lengths = []
        for title in titles:
            title_upper = title.upper()
            lengths.append(len(title))
            
            # Buscar gatilhos emocionais
            for word in emotional_words:
                if word in title_upper:
                    patterns['emotional_triggers'].append(word)
            
            # Buscar números
            numbers = re.findall(r'\d+', title)
            patterns['numbers'].extend(numbers)
            
            # Buscar estruturas comuns
            if title.startswith('COMO'):
                patterns['structures'].append('COMO_FAZER')
            elif '?' in title:
                patterns['structures'].append('PERGUNTA')
            elif title.count('|') > 0:
                patterns['structures'].append('SEPARADOR')
            elif title.isupper():
                patterns['structures'].append('MAIUSCULA')
        
        # Calcular estatísticas de comprimento
        if lengths:
            patterns['length_stats'] = {
                'min': min(lengths),
                'max': max(lengths),
                'avg': sum(lengths) / len(lengths)
            }
        
        # Remover duplicatas e contar frequências
        patterns['emotional_triggers'] = list(set(patterns['emotional_triggers']))
        patterns['numbers'] = list(set(patterns['numbers']))
        patterns['structures'] = list(set(patterns['structures']))
        
        return patterns
    
    def generate_titles_openai(self, 
                              source_titles: List[str], 
                              topic: str, 
                              count: int = 10,
                              style: str = "viral") -> List[str]:
        """Gerar títulos usando OpenAI GPT"""
        if not self.openai_client:
            raise Exception("OpenAI não configurado")
        
        # Analisar padrões dos títulos de origem
        patterns = self.analyze_viral_patterns(source_titles)
        
        # Criar prompt baseado nos padrões encontrados
        prompt = self.create_openai_prompt(source_titles, topic, patterns, style, count)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em criação de títulos virais para YouTube."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.8
            )

            content = response.choices[0].message.content
            titles = self.parse_generated_titles(content)

            return titles[:count]
            
        except Exception as e:
            print(f"❌ Erro na geração OpenAI: {e}")
            return []
    
    def generate_titles_gemini(self, 
                              source_titles: List[str], 
                              topic: str, 
                              count: int = 10,
                              style: str = "viral") -> List[str]:
        """Gerar títulos usando Google Gemini com cache e fallback automático"""
        try:
            from routes.automations import handle_gemini_429_error, check_gemini_availability, get_fallback_provider_info
            import hashlib
            import json
            import os
            from datetime import datetime, timedelta
            
            # Sistema de cache simples
            cache_dir = "cache/gemini_titles"
            os.makedirs(cache_dir, exist_ok=True)
            
            # Gerar hash do prompt para cache
            cache_key = f"{str(source_titles)}_{topic}_{count}_{style}"
            prompt_hash = hashlib.md5(cache_key.encode()).hexdigest()
            cache_file = os.path.join(cache_dir, f"{prompt_hash}.json")
            
            # Verificar cache (válido por 4 horas para títulos)
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    if datetime.now() - cache_time < timedelta(hours=4):
                        print(f"📦 [CACHE] Usando títulos em cache para Gemini ({len(cache_data['titles'])} títulos)")
                        return cache_data['titles']
                except Exception as e:
                    print(f"⚠️ [CACHE] Erro ao ler cache de títulos: {e}")
            
            # Verificar disponibilidade do Gemini
            if not check_gemini_availability():
                print("⚠️ [GEMINI] Todas as chaves Gemini esgotadas, usando fallback para títulos")
                fallback_info = get_fallback_provider_info()
                if fallback_info:
                    if fallback_info['provider'] == 'openai':
                        return self.generate_titles_openai(source_titles, topic, count, style)
                    elif fallback_info['provider'] == 'openrouter':
                        # Implementar fallback para OpenRouter se necessário
                        print("⚠️ [FALLBACK] OpenRouter não implementado para títulos, retornando lista vazia")
                        return []
                print("⚠️ [FALLBACK] Nenhum fallback disponível para títulos")
                return []
            
            if not self.gemini_model:
                raise Exception("Gemini não configurado")
            
            # Analisar padrões dos títulos de origem
            patterns = self.analyze_viral_patterns(source_titles)
            
            # Criar prompt baseado nos padrões encontrados
            prompt = self.create_gemini_prompt(source_titles, topic, patterns, style, count)
            
            print(f"🔍 DEBUG: Enviando prompt para Gemini...")
            print(f"🔍 DEBUG: Títulos de origem: {source_titles}")
            print(f"🔍 DEBUG: Quantidade solicitada: {count}")

            # Verificar cancelamento antes de chamar a IA
            try:
                from routes.workflow import check_workflow_status
                check_workflow_status()
            except:
                pass  # Se não conseguir importar, continua

            # Usar função centralizada de retry
            from routes.automations import generate_content_with_gemini_retry
            response_text = generate_content_with_gemini_retry(prompt)
            print(f"🔍 DEBUG: Resposta bruta do Gemini: {response_text[:200]}...")

            titles = self.parse_generated_titles(response_text)
            print(f"🔍 DEBUG: Títulos parseados ({len(titles)}): {titles}")
            print(f"🔍 DEBUG: Limitando para {count} títulos")

            limited_titles = titles[:count]
            print(f"🔍 DEBUG: Títulos finais ({len(limited_titles)}): {limited_titles}")
            
            # Salvar no cache
            try:
                cache_data = {
                    'titles': limited_titles,
                    'timestamp': datetime.now().isoformat(),
                    'prompt_hash': prompt_hash,
                    'count': count,
                    'style': style
                }
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
                print(f"📦 [CACHE] Títulos salvos no cache")
            except Exception as e:
                print(f"⚠️ [CACHE] Erro ao salvar cache de títulos: {e}")

            return limited_titles

        except Exception as e:
            error_str = str(e)
            
            # Tratar erro 429 especificamente
            if '429' in error_str or 'quota' in error_str.lower() or 'exceeded' in error_str.lower():
                print(f"🚫 [GEMINI] Erro 429 detectado nos títulos: {error_str}")
                # Obter a chave atual para passar para handle_gemini_429_error
                from routes.automations import GEMINI_KEYS_ROTATION
                current_key = None
                if GEMINI_KEYS_ROTATION['keys'] and GEMINI_KEYS_ROTATION['current_index'] < len(GEMINI_KEYS_ROTATION['keys']):
                    current_key = GEMINI_KEYS_ROTATION['keys'][GEMINI_KEYS_ROTATION['current_index']]
                handle_gemini_429_error(error_str, current_key)
                
                # Tentar fallback automático
                try:
                    from routes.automations import get_fallback_provider_info
                    fallback_info = get_fallback_provider_info()
                    if fallback_info:
                        print(f"🔄 [FALLBACK] Usando {fallback_info['provider']} como fallback para títulos")
                        if fallback_info['provider'] == 'openai':
                            return self.generate_titles_openai(source_titles, topic, count, style)
                        elif fallback_info['provider'] == 'openrouter':
                            print("⚠️ [FALLBACK] OpenRouter não implementado para títulos, retornando lista vazia")
                            return []
                except Exception as fallback_error:
                    print(f"❌ [FALLBACK] Erro no fallback dos títulos: {fallback_error}")
            
            print(f"❌ Erro na geração Gemini: {error_str}")
            return []
    
    def create_openai_prompt(self, source_titles: List[str], topic: str, patterns: Dict, style: str, count: int = 10) -> str:
        """Criar prompt otimizado para OpenAI"""
        prompt = f"""
Você é um especialista em marketing digital para YouTube. Analise os títulos de referência abaixo e crie NOVOS títulos SIMILARES mas MELHORADOS sobre o mesmo tema.

TÍTULOS DE REFERÊNCIA (extraídos de canal de sucesso):
{chr(10).join([f"• {title}" for title in source_titles[:5]])}

PADRÕES IDENTIFICADOS:
• Gatilhos emocionais: {', '.join(patterns['emotional_triggers'][:10])}
• Números populares: {', '.join(patterns['numbers'][:5])}
• Estruturas: {', '.join(patterns['structures'])}
• Comprimento médio: {patterns['length_stats']['avg']:.0f} caracteres

INSTRUÇÕES ESPECÍFICAS:
1. 🎯 MANTENHA o mesmo NICHO/TEMA dos títulos de referência
2. 🚀 Crie 15 títulos SIMILARES mas MELHORADOS
3. 📈 Use os padrões identificados para otimizar engajamento
4. 🎪 Aplique gatilhos psicológicos mais fortes (curiosidade, urgência, exclusividade)
5. 🔥 Mantenha entre {patterns['length_stats']['min']} e {patterns['length_stats']['max']} caracteres
6. 💡 Varie as estruturas mas mantenha o estilo {style}
7. 📊 Foque em títulos que superem os originais em atratividade

IMPORTANTE: Os novos títulos devem ser sobre o MESMO TEMA dos títulos de referência, mas mais otimizados para cliques.

FORMATO DE RESPOSTA:
1. [TÍTULO 1]
2. [TÍTULO 2]
...

IMPORTANTE: Gere EXATAMENTE {count} títulos, nem mais nem menos.

Títulos ({count} títulos):
"""
        return prompt
    
    def create_gemini_prompt(self, source_titles: List[str], topic: str, patterns: Dict, style: str, count: int = 10) -> str:
        """Criar prompt otimizado para Gemini"""
        prompt = f"""
Você é um especialista em marketing digital e criação de conteúdo viral para YouTube.

TAREFA: Analisar os títulos de referência abaixo e criar NOVOS títulos SIMILARES mas MELHORADOS sobre o mesmo tema/nicho.

TÍTULOS DE REFERÊNCIA (extraídos de canal de sucesso):
{chr(10).join([f"• {title}" for title in source_titles[:5]])}

ANÁLISE DOS PADRÕES IDENTIFICADOS:
• Palavras-chave emocionais: {', '.join(patterns['emotional_triggers'][:8])}
• Números eficazes: {', '.join(patterns['numbers'][:5])}
• Estruturas que funcionam: {', '.join(patterns['structures'])}
• Comprimento ideal: {patterns['length_stats']['min']}-{patterns['length_stats']['max']} caracteres

INSTRUÇÕES ESPECÍFICAS:
1. 🎯 MANTENHA o mesmo NICHO/TEMA dos títulos de referência
2. 🚀 MELHORE usando gatilhos psicológicos mais fortes
3. 📈 OTIMIZE para maior engajamento e cliques
4. 🎪 Use elementos de curiosidade, urgência, exclusividade
5. 🔥 Inclua emojis estratégicos quando apropriado
6. 💡 Varie as estruturas mas mantenha o estilo viral
7. 📊 Crie títulos que superem os originais em atratividade

IMPORTANTE: Os novos títulos devem ser sobre o MESMO TEMA dos títulos de referência, mas mais atrativos e otimizados.

FORMATO DE RESPOSTA:
Liste apenas os títulos numerados, um por linha:

1. [TÍTULO MELHORADO]
2. [TÍTULO MELHORADO]
...

IMPORTANTE: Gere EXATAMENTE {count} títulos, nem mais nem menos.

Gere os {count} títulos agora:
"""
        return prompt
    
    def parse_generated_titles(self, content: str) -> List[str]:
        """Extrair títulos do texto gerado pela IA"""
        titles = []

        print(f"🔍 DEBUG: Parseando conteúdo: {content[:200]}...")

        # Dividir por linhas
        lines = content.strip().split('\n')
        print(f"🔍 DEBUG: {len(lines)} linhas encontradas")

        for i, line in enumerate(lines):
            original_line = line
            line = line.strip()

            # Remover numeração (1., 2., etc.)
            line = re.sub(r'^\d+\.?\s*', '', line)

            # Remover marcadores (-, •, etc.)
            line = re.sub(r'^[-•*]\s*', '', line)

            # Remover colchetes se existirem
            line = re.sub(r'^\[|\]$', '', line)

            print(f"🔍 DEBUG: Linha {i+1}: '{original_line}' -> '{line}' (len: {len(line)})")

            # Verificar se é um título válido
            if line and len(line) > 10 and not line.startswith('Título'):
                titles.append(line.strip())
                print(f"✅ DEBUG: Título aceito: '{line.strip()}'")
            else:
                print(f"❌ DEBUG: Título rejeitado: '{line}' (muito curto ou inválido)")

        print(f"🔍 DEBUG: Total de títulos extraídos: {len(titles)}")
        return titles
    
    def generate_titles_hybrid(self, 
                              source_titles: List[str], 
                              topic: str, 
                              count: int = 10,
                              style: str = "viral") -> Dict:
        """Gerar títulos usando múltiplas IAs e combinar resultados"""
        results = {
            'openai_titles': [],
            'gemini_titles': [],
            'combined_titles': [],
            'patterns_analysis': {},
            'success': False,
            'error': None
        }
        
        try:
            # Analisar padrões primeiro
            results['patterns_analysis'] = self.analyze_viral_patterns(source_titles)
            
            # Tentar OpenAI primeiro
            if self.openai_client:
                try:
                    openai_titles = self.generate_titles_openai(source_titles, topic, count, style)
                    results['openai_titles'] = openai_titles
                except Exception as e:
                    print(f"⚠️ OpenAI falhou: {e}")
            
            # Tentar Gemini como backup/complemento
            if self.gemini_model:
                try:
                    gemini_titles = self.generate_titles_gemini(source_titles, topic, count, style)
                    results['gemini_titles'] = gemini_titles
                except Exception as e:
                    print(f"⚠️ Gemini falhou: {e}")
            
            # Combinar e diversificar resultados
            all_titles = results['openai_titles'] + results['gemini_titles']
            
            if all_titles:
                # Remover duplicatas e selecionar os melhores
                unique_titles = list(dict.fromkeys(all_titles))  # Remove duplicatas mantendo ordem
                results['combined_titles'] = unique_titles[:count]
                results['success'] = True
            else:
                results['error'] = "Nenhuma IA conseguiu gerar títulos"
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            return results
    
    def score_title_quality(self, title: str, patterns: Dict) -> float:
        """Pontuar qualidade de um título baseado nos padrões virais"""
        score = 0.0
        title_upper = title.upper()

        # Pontuação por gatilhos emocionais
        for trigger in patterns['emotional_triggers']:
            if trigger in title_upper:
                score += 2.0

        # Pontuação por números
        if re.search(r'\d+', title):
            score += 1.5

        # Pontuação por comprimento ideal
        length = len(title)
        ideal_min = patterns['length_stats']['min']
        ideal_max = patterns['length_stats']['max']

        if ideal_min <= length <= ideal_max:
            score += 2.0
        elif abs(length - patterns['length_stats']['avg']) <= 10:
            score += 1.0

        # Pontuação por estruturas eficazes
        if title.startswith('COMO'):
            score += 1.0
        if '?' in title:
            score += 0.5
        if title.count('|') > 0:
            score += 0.5

        return score

    def generate_titles_with_custom_prompt(self,
                                         source_titles: List[str],
                                         custom_prompt: str,
                                         count: int = 10,
                                         ai_provider: str = "auto",
                                         script_size: str = "medio") -> Dict:
        """Gerar títulos usando prompt personalizado"""
        results = {
            'generated_titles': [],
            'ai_provider_used': '',
            'patterns_analysis': {},
            'success': False,
            'error': None,
            'custom_prompt_used': custom_prompt
        }

        try:
            # Analisar padrões dos títulos originais
            results['patterns_analysis'] = self.analyze_viral_patterns(source_titles)

            # Criar prompt final combinando o personalizado com os títulos
            final_prompt = self.create_custom_prompt(source_titles, custom_prompt, count, script_size)

            # Tentar gerar com a IA escolhida
            if ai_provider == "openai" and self.openai_client:
                titles = self.generate_with_openai_custom(final_prompt)
                results['ai_provider_used'] = 'openai'
            elif ai_provider == "gemini" and self.gemini_model:
                titles = self.generate_with_gemini_custom(final_prompt)
                results['ai_provider_used'] = 'gemini'
            elif ai_provider == "openrouter" and self.openrouter_api_key:
                titles = self.generate_with_openrouter_custom(final_prompt, "anthropic/claude-3.5-sonnet")
                results['ai_provider_used'] = 'openrouter'
            else:
                # Modo automático - tentar OpenAI primeiro, depois OpenRouter, depois Gemini
                titles = []

                # Tentar OpenAI primeiro
                if self.openai_client:
                    try:
                        titles = self.generate_with_openai_custom(final_prompt)
                        results['ai_provider_used'] = 'openai'
                    except Exception as e:
                        print(f"⚠️ OpenAI falhou: {e}")

                # Tentar OpenRouter se OpenAI falhou
                if not titles and self.openrouter_api_key:
                    try:
                        titles = self.generate_with_openrouter_custom(final_prompt, "anthropic/claude-3.5-sonnet")
                        results['ai_provider_used'] = 'openrouter'
                    except Exception as e:
                        print(f"⚠️ OpenRouter falhou: {e}")

                # Tentar Gemini como último recurso
                if not titles and self.gemini_model:
                    try:
                        titles = self.generate_with_gemini_custom(final_prompt)
                        results['ai_provider_used'] = 'gemini'
                    except Exception as e:
                        print(f"⚠️ Gemini falhou: {e}")

                if not titles:
                    results['error'] = "Nenhuma IA conseguiu processar o prompt personalizado"
                    return results

            if titles:
                results['generated_titles'] = titles[:count]
                results['success'] = True
            else:
                results['error'] = "Nenhum título foi gerado"

            return results

        except Exception as e:
            results['error'] = str(e)
            return results

    def create_custom_prompt(self, source_titles: List[str], custom_prompt: str, count: int, script_size: str = "medio") -> str:
        """Criar prompt final combinando títulos originais com prompt personalizado"""
        
        # Definir instruções específicas de tamanho
        size_instructions = {
            'curto': "Crie títulos para roteiros CURTOS (1.500-2.000 palavras). Foque em temas diretos, tutoriais rápidos, dicas práticas e conteúdo conciso.",
            'medio': "Crie títulos para roteiros MÉDIOS (3.500-5.000 palavras). Equilibre profundidade e acessibilidade, permitindo desenvolvimento moderado dos temas.",
            'longo': "Crie títulos para roteiros LONGOS (7.000-10.000 palavras). Foque em análises profundas, estudos de caso detalhados, tutoriais completos e conteúdo abrangente."
        }
        
        size_instruction = size_instructions.get(script_size, size_instructions['medio'])
        
        prompt = f"""
TÍTULOS ORIGINAIS EXTRAÍDOS DO YOUTUBE:
{chr(10).join([f"• {title}" for title in source_titles])}

INSTRUÇÃO PERSONALIZADA:
{custom_prompt}

INSTRUÇÃO DE TAMANHO:
{size_instruction}

TAREFA:
Com base nos títulos originais acima e seguindo a instrução personalizada, crie {count} novos títulos únicos e otimizados.

DIRETRIZES:
1. Use os títulos originais como inspiração e referência
2. Siga exatamente a instrução personalizada fornecida
3. Considere o tamanho do roteiro especificado na criação dos títulos
4. Mantenha a essência viral dos títulos originais
5. Crie títulos únicos e atraentes
6. Foque em gerar curiosidade e engajamento

FORMATO DE RESPOSTA:
Liste apenas os títulos numerados, um por linha:

1. [TÍTULO]
2. [TÍTULO]
...

Gere os {count} títulos agora:
"""
        return prompt

    def generate_with_openai_custom(self, prompt: str) -> List[str]:
        """Gerar títulos com OpenAI usando prompt personalizado"""
        if not self.openai_client:
            raise Exception("OpenAI não configurado")

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em criação de títulos virais para YouTube. Siga exatamente as instruções fornecidas."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.8
            )

            content = response.choices[0].message.content
            titles = self.parse_generated_titles(content)

            return titles

        except Exception as e:
            print(f"❌ Erro na geração OpenAI: {e}")
            raise e

    def generate_with_gemini_custom(self, prompt: str) -> List[str]:
        """Gerar títulos com Gemini usando prompt personalizado com sistema de retry automático"""
        if not self.gemini_model:
            raise Exception("Gemini não configurado")

        try:
            from routes.automations import get_next_gemini_key, handle_gemini_429_error, get_gemini_keys_count
            
            # Usar a quantidade real de chaves disponíveis
            max_retries = get_gemini_keys_count() if get_gemini_keys_count() > 0 else 1
            print(f"🔑 Usando {max_retries} chaves Gemini para geração de títulos")
            
            for attempt in range(max_retries):
                try:
                    print(f"🔍 DEBUG: Tentativa {attempt + 1}/{max_retries} - Enviando prompt personalizado para Gemini...")
                    response = self.gemini_model.generate_content(prompt)
                    print(f"🔍 DEBUG: Resposta bruta do Gemini: {response.text[:300]}...")

                    titles = self.parse_generated_titles(response.text)
                    print(f"🔍 DEBUG: Títulos parseados do Gemini: {titles}")
                    print(f"✅ Sucesso na geração de títulos com Gemini na tentativa {attempt + 1}")

                    return titles

                except Exception as e:
                    error_str = str(e)
                    print(f"❌ Erro na tentativa {attempt + 1}: {error_str}")
                    
                    # Check if it's a quota error (429)
                    if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                        if attempt < max_retries - 1:  # Not the last attempt
                            print(f"🔄 Erro de quota detectado, tentando próxima chave Gemini...")
                            handle_gemini_429_error(error_str)
                            new_api_key = get_next_gemini_key()
                            if new_api_key:
                                print(f"🔑 Nova chave Gemini obtida, reconfigurando...")
                                self.configure_gemini(new_api_key)
                                continue
                            else:
                                print("❌ Nenhuma chave Gemini disponível")
                                break
                        else:
                            print("❌ Todas as tentativas de retry falharam")
                            handle_gemini_429_error(error_str)
                    else:
                        # For non-quota errors, don't retry
                        print(f"❌ Erro não relacionado à quota, parando tentativas: {error_str}")
                        raise e
            
            raise Exception("Falha na geração de títulos com Gemini após todas as tentativas")

        except Exception as e:
            print(f"❌ Erro na geração Gemini: {e}")
            raise e

    def generate_with_openrouter_custom(self, prompt: str, model: str = "anthropic/claude-3.5-sonnet") -> List[str]:
        """Gerar títulos com OpenRouter usando prompt personalizado"""
        if not self.openrouter_api_key:
            raise Exception("OpenRouter não configurado")

        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5173",
                "X-Title": "Auto Video Producer"
            }

            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "Você é um especialista em criação de títulos virais para YouTube. Siga exatamente as instruções fornecidas."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.8
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                titles = self.parse_generated_titles(content)
                return titles
            else:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"❌ Erro na geração OpenRouter: {e}")
            raise e
