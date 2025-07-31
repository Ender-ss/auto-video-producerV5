"""
🤖 Serviço de Geração de Títulos com IA
Auto Video Producer - Geração inteligente de títulos virais
"""

import openai
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
        
    def configure_openai(self, api_key: str):
        """Configurar cliente OpenAI"""
        try:
            openai.api_key = api_key
            self.openai_client = openai
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar OpenAI: {e}")
            return False
            
    def configure_gemini(self, api_key: str):
        """Configurar cliente Google Gemini"""
        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar Gemini: {e}")
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
        prompt = self.create_openai_prompt(source_titles, topic, patterns, style)
        
        try:
            response = self.openai_client.ChatCompletion.create(
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
        """Gerar títulos usando Google Gemini"""
        if not self.gemini_model:
            raise Exception("Gemini não configurado")
        
        # Analisar padrões dos títulos de origem
        patterns = self.analyze_viral_patterns(source_titles)
        
        # Criar prompt baseado nos padrões encontrados
        prompt = self.create_gemini_prompt(source_titles, topic, patterns, style)
        
        try:
            response = self.gemini_model.generate_content(prompt)
            titles = self.parse_generated_titles(response.text)
            
            return titles[:count]
            
        except Exception as e:
            print(f"❌ Erro na geração Gemini: {e}")
            return []
    
    def create_openai_prompt(self, source_titles: List[str], topic: str, patterns: Dict, style: str) -> str:
        """Criar prompt otimizado para OpenAI"""
        prompt = f"""
Analise estes títulos virais de YouTube e crie novos títulos sobre "{topic}":

TÍTULOS DE REFERÊNCIA:
{chr(10).join([f"• {title}" for title in source_titles[:5]])}

PADRÕES IDENTIFICADOS:
• Gatilhos emocionais: {', '.join(patterns['emotional_triggers'][:10])}
• Números populares: {', '.join(patterns['numbers'][:5])}
• Estruturas: {', '.join(patterns['structures'])}
• Comprimento médio: {patterns['length_stats']['avg']:.0f} caracteres

INSTRUÇÕES:
1. Crie 15 títulos únicos sobre "{topic}"
2. Use os padrões identificados acima
3. Estilo: {style}
4. Mantenha entre {patterns['length_stats']['min']} e {patterns['length_stats']['max']} caracteres
5. Use gatilhos emocionais e números quando apropriado
6. Foque em curiosidade, urgência e benefício claro

FORMATO DE RESPOSTA:
1. [TÍTULO 1]
2. [TÍTULO 2]
...

Títulos:
"""
        return prompt
    
    def create_gemini_prompt(self, source_titles: List[str], topic: str, patterns: Dict, style: str) -> str:
        """Criar prompt otimizado para Gemini"""
        prompt = f"""
Você é um especialista em marketing digital e criação de conteúdo viral para YouTube.

TAREFA: Criar títulos virais sobre "{topic}" baseado nos padrões dos títulos de sucesso abaixo.

TÍTULOS DE REFERÊNCIA (alta performance):
{chr(10).join([f"• {title}" for title in source_titles[:5]])}

ANÁLISE DOS PADRÕES:
• Palavras-chave emocionais mais usadas: {', '.join(patterns['emotional_triggers'][:8])}
• Números que geram engajamento: {', '.join(patterns['numbers'][:5])}
• Estruturas eficazes: {', '.join(patterns['structures'])}
• Comprimento ideal: {patterns['length_stats']['min']}-{patterns['length_stats']['max']} caracteres

DIRETRIZES PARA CRIAÇÃO:
1. Tópico principal: "{topic}"
2. Estilo desejado: {style}
3. Quantidade: 15 títulos únicos
4. Use gatilhos psicológicos (curiosidade, urgência, exclusividade)
5. Inclua números específicos quando relevante
6. Mantenha o comprimento otimizado para YouTube
7. Foque no benefício claro para o viewer

FORMATO DE RESPOSTA:
Liste apenas os títulos numerados, um por linha:

1. [TÍTULO]
2. [TÍTULO]
...

Gere os títulos agora:
"""
        return prompt
    
    def parse_generated_titles(self, content: str) -> List[str]:
        """Extrair títulos do texto gerado pela IA"""
        titles = []
        
        # Dividir por linhas
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Remover numeração (1., 2., etc.)
            line = re.sub(r'^\d+\.?\s*', '', line)
            
            # Remover marcadores (-, •, etc.)
            line = re.sub(r'^[-•*]\s*', '', line)
            
            # Remover colchetes se existirem
            line = re.sub(r'^\[|\]$', '', line)
            
            # Verificar se é um título válido
            if line and len(line) > 10 and not line.startswith('Título'):
                titles.append(line.strip())
        
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
                                         ai_provider: str = "auto") -> Dict:
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
            final_prompt = self.create_custom_prompt(source_titles, custom_prompt, count)

            # Tentar gerar com a IA escolhida
            if ai_provider == "openai" and self.openai_client:
                titles = self.generate_with_openai_custom(final_prompt)
                results['ai_provider_used'] = 'openai'
            elif ai_provider == "gemini" and self.gemini_model:
                titles = self.generate_with_gemini_custom(final_prompt)
                results['ai_provider_used'] = 'gemini'
            else:
                # Modo automático - tentar OpenAI primeiro, depois Gemini
                titles = []
                if self.openai_client:
                    try:
                        titles = self.generate_with_openai_custom(final_prompt)
                        results['ai_provider_used'] = 'openai'
                    except Exception as e:
                        print(f"⚠️ OpenAI falhou: {e}")

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

    def create_custom_prompt(self, source_titles: List[str], custom_prompt: str, count: int) -> str:
        """Criar prompt final combinando títulos originais com prompt personalizado"""
        prompt = f"""
TÍTULOS ORIGINAIS EXTRAÍDOS DO YOUTUBE:
{chr(10).join([f"• {title}" for title in source_titles])}

INSTRUÇÃO PERSONALIZADA:
{custom_prompt}

TAREFA:
Com base nos títulos originais acima e seguindo a instrução personalizada, crie {count} novos títulos únicos e otimizados.

DIRETRIZES:
1. Use os títulos originais como inspiração e referência
2. Siga exatamente a instrução personalizada fornecida
3. Mantenha a essência viral dos títulos originais
4. Crie títulos únicos e atraentes
5. Foque em gerar curiosidade e engajamento

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
            response = self.openai_client.ChatCompletion.create(
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
        """Gerar títulos com Gemini usando prompt personalizado"""
        if not self.gemini_model:
            raise Exception("Gemini não configurado")

        try:
            response = self.gemini_model.generate_content(prompt)
            titles = self.parse_generated_titles(response.text)

            return titles

        except Exception as e:
            print(f"❌ Erro na geração Gemini: {e}")
            raise e
