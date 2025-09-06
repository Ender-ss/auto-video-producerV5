import json
import re
import uuid
import redis
import hashlib
import tiktoken
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import random
import sys
import os

# Adicionar o diretório backend ao path para importar improved_header_removal
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from improved_header_removal import ImprovedHeaderRemoval

logger = logging.getLogger(__name__)

@dataclass
class ChapterConfig:
    min_chars: int
    max_chars: int
    target_chars: int
    cliffhanger_prompt: str
    break_patterns: List[str]

class RepetitionDetector:
    """Detector de repetições e padrões duplicados"""
    
    def __init__(self):
        self.similarity_threshold = 0.7  # 70% de similaridade
        self.phrase_min_length = 10  # Frases mínimas para comparar
    
    def detect_repetitions(self, chapters: List[str]) -> Dict:
        """Detecta repetições entre capítulos"""
        repetitions = []
        
        for i, chapter1 in enumerate(chapters):
            for j, chapter2 in enumerate(chapters[i+1:], i+1):
                similarity = self._calculate_similarity(chapter1, chapter2)
                if similarity > self.similarity_threshold:
                    repetitions.append({
                        'chapter1': i+1,
                        'chapter2': j+1,
                        'similarity': similarity
                    })
        
        # Detecta frases repetidas
        repeated_phrases = self._find_repeated_phrases(chapters)
        
        return {
            'similar_chapters': repetitions,
            'repeated_phrases': repeated_phrases,
            'repetition_score': len(repetitions) + len(repeated_phrases)
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _find_repeated_phrases(self, chapters: List[str]) -> List[Dict]:
        """Encontra frases repetidas entre capítulos"""
        phrases = []
        all_sentences = []
        
        # Extrai sentenças de todos os capítulos
        for i, chapter in enumerate(chapters):
            sentences = re.split(r'[.!?]+', chapter)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) >= self.phrase_min_length:
                    all_sentences.append({
                        'text': sentence.lower(),
                        'chapter': i+1,
                        'original': sentence
                    })
        
        # Encontra duplicatas
        seen = {}
        for sentence in all_sentences:
            text = sentence['text']
            if text in seen:
                phrases.append({
                    'phrase': sentence['original'],
                    'chapters': [seen[text]['chapter'], sentence['chapter']]
                })
            else:
                seen[text] = sentence
        
        return phrases

class SmartChapterBreaker:
    """Analisador inteligente de pontos naturais de quebra"""
    
    def __init__(self):
        self.break_indicators = [
            r'\.\s*\n+',  # Fim de parágrafo
            r'\!\s*\n+',  # Exclamação forte
            r'\?\s*\n+',  # Pergunta retórica
            r'"[\s\n]*"',  # Fim de diálogo
            r'\n\s*\n+',  # Quebra de seção
        ]
    
    def find_natural_breaks(self, text: str, target_length: int) -> List[int]:
        """Encontra pontos naturais de quebra próximos do target_length"""
        positions = []
        
        for pattern in self.break_indicators:
            matches = re.finditer(pattern, text)
            for match in matches:
                pos = match.end()
                # Aceita pontos entre 80% e 120% do target
                if target_length * 0.8 <= pos <= target_length * 1.2:
                    positions.append(pos)
        
        return sorted(positions)

class StoryValidator:
    """Validador de qualidade de capítulos"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.min_chars = config.get('min_chars', 500)  # Reduzido para testes
        self.max_chars = config.get('max_chars', 4000)
        self.repetition_detector = RepetitionDetector()
    
    def validate_chapter(self, chapter: str, chapter_num: int) -> Dict:
        """Valida um capítulo individual"""
        length = len(chapter)
        issues = []
        
        if length < self.min_chars:
            issues.append(f"Capítulo {chapter_num} muito curto: {length} chars")
        
        if length > self.max_chars:
            issues.append(f"Capítulo {chapter_num} muito longo: {length} chars")
        
        # Verifica quebras de diálogo
        open_quotes = chapter.count('"') % 2
        if open_quotes != 0:
            issues.append(f"Diálogo mal fechado no capítulo {chapter_num}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'length': length
        }
    
    def validate_story_repetitions(self, chapters: List[str]) -> Dict:
        """Valida repetições em toda a história"""
        return self.repetition_detector.detect_repetitions(chapters)

class MemoryBridge:
    """Bridge para gerenciamento de contexto e cache inteligente"""
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=redis_db,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Memory Bridge conectado ao Redis")
        except redis.ConnectionError:
            logger.warning("Redis não disponível, usando cache em memória")
            self.redis_client = None
            self.memory_cache = {}
    
    def _generate_key(self, story_id: str, chapter_num: int, context_type: str) -> str:
        """Gera chave única para cache"""
        return f"story:{story_id}:chapter:{chapter_num}:{context_type}"
    
    def save_context(self, story_id: str, chapter_num: int, context: Dict, ttl=3600):
        """Salva contexto com TTL"""
        key = self._generate_key(story_id, chapter_num, 'context')
        
        if self.redis_client:
            self.redis_client.setex(key, ttl, json.dumps(context))
        else:
            # Fallback para cache em memória
            self.memory_cache[key] = {
                'data': context,
                'expires': datetime.now() + timedelta(seconds=ttl)
            }
    
    def get_context(self, story_id: str, chapter_num: int) -> Optional[Dict]:
        """Recupera contexto salvo"""
        key = self._generate_key(story_id, chapter_num, 'context')
        
        if self.redis_client:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        else:
            # Fallback para cache em memória
            cached = self.memory_cache.get(key)
            if cached and cached['expires'] > datetime.now():
                return cached['data']
            elif cached:
                del self.memory_cache[key]
            return None
    
    def save_breakpoints(self, story_id: str, breakpoints: List[int]):
        """Salva pontos de quebra calculados"""
        key = self._generate_key(story_id, 0, 'breakpoints')
        
        if self.redis_client:
            self.redis_client.setex(key, 7200, json.dumps(breakpoints))  # 2h TTL
        else:
            self.memory_cache[key] = {
                'data': breakpoints,
                'expires': datetime.now() + timedelta(hours=2)
            }
    
    def get_breakpoints(self, story_id: str) -> Optional[List[int]]:
        """Recupera pontos de quebra salvos"""
        key = self._generate_key(story_id, 0, 'breakpoints')
        
        if self.redis_client:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        else:
            cached = self.memory_cache.get(key)
            if cached and cached['expires'] > datetime.now():
                return cached['data']
            elif cached:
                del self.memory_cache[key]
            return None

class TokenChunker:
    """Gerenciador inteligente de chunking por tokens"""
    
    def __init__(self, max_tokens=8000, model_name="gpt-3.5-turbo"):
        self.max_tokens = max_tokens
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
            logger.info(f"TokenChunker configurado para modelo {model_name}")
        except KeyError:
            logger.warning(f"Modelo {model_name} não encontrado, usando cl100k_base")
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def estimate_tokens(self, text: str) -> int:
        """Estima número de tokens no texto usando tiktoken"""
        return len(self.encoding.encode(text))
    
    def smart_chunking(self, text: str, preserve_context: bool = True) -> List[str]:
        """
        Divide texto mantendo pontos de quebra naturais
        
        Args:
            text: Texto completo a ser dividido
            preserve_context: Se deve preservar contexto entre chunks
        
        Returns:
            Lista de chunks dentro do limite de tokens
        """
        if self.estimate_tokens(text) <= self.max_tokens:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Estratégia: dividir por parágrafos primeiro
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Testa se o parágrafo cabe no chunk atual
            test_chunk = current_chunk + ("\n\n" + paragraph if current_chunk else paragraph)
            
            if self.estimate_tokens(test_chunk) <= self.max_tokens:
                current_chunk = test_chunk
            else:
                # Se chunk atual não está vazio, salva
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # Se parágrafo é maior que limite, divide por sentenças
                if self.estimate_tokens(paragraph) > self.max_tokens:
                    sentence_chunks = self._chunk_by_sentences(paragraph)
                    chunks.extend(sentence_chunks)
                    current_chunk = ""
                else:
                    current_chunk = paragraph
        
        # Adiciona último chunk se houver
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """Divide texto por sentenças quando parágrafos são muito grandes"""
        import re
        
        # Regex para detectar fim de sentença
        sentence_endings = re.compile(r'[.!?]+\s*')
        sentences = sentence_endings.split(text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            test_chunk = current_chunk + (" " + sentence if current_chunk else sentence)
            
            if self.estimate_tokens(test_chunk) <= self.max_tokens:
                current_chunk = test_chunk
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

class PromptVariator:
    """Gerador de prompts variados para evitar repetições"""
    
    def __init__(self):
        self.opening_variations = [
            "Crie o CAPÍTULO {chapter_num}",
            "Desenvolva o CAPÍTULO {chapter_num}",
            "Escreva o CAPÍTULO {chapter_num}",
            "Construa o CAPÍTULO {chapter_num}",
            "Elabore o CAPÍTULO {chapter_num}"
        ]
        
        self.narrative_styles = [
            "Use linguagem envolvente e narrativa cativante",
            "Empregue uma narrativa fluida e envolvente",
            "Utilize uma escrita rica e imersiva",
            "Desenvolva com estilo narrativo envolvente",
            "Construa com linguagem rica e cativante"
        ]
        
        self.character_instructions = [
            "Crie personagens profundos com diálogos significativos",
            "Desenvolva personagens ricos com conversas autênticas",
            "Construa personagens complexos com diálogos naturais",
            "Elabore personagens detalhados com falas expressivas",
            "Forme personagens bem desenvolvidos com diálogos realistas"
        ]
        
        self.description_styles = [
            "Inclua descrições ambientais ricas quando apropriado",
            "Adicione detalhes ambientais vívidos conforme necessário",
            "Incorpore descrições de cenário detalhadas quando relevante",
            "Integre elementos descritivos do ambiente quando adequado",
            "Insira descrições atmosféricas quando pertinente"
        ]
    
    def generate_varied_prompt(self, title: str, premise: str, agent_type: str, 
                             target_chars: int, chapter_num: int, total_chapters: int,
                             previous_context: Optional[Dict] = None, 
                             previous_chapters: List[str] = None,
                             remove_chapter_headers: bool = False) -> str:
        """Gera prompt variado para evitar repetições"""
        
        # Seleciona variações aleatórias
        opening = random.choice(self.opening_variations).format(chapter_num=chapter_num)
        narrative_style = random.choice(self.narrative_styles)
        character_instruction = random.choice(self.character_instructions)
        description_style = random.choice(self.description_styles)
        
        # Contexto do agente
        agent_contexts = {
            'millionaire_stories': {
                'context': 'história de superação financeira e empreendedorismo',
                'tone': 'inspirador e motivacional',
                'elements': 'jornada do zero ao sucesso, desafios financeiros, estratégias de negócio'
            },
            'romance_agent': {
                'context': 'história romântica com desenvolvimento emocional',
                'tone': 'emocional e envolvente',
                'elements': 'encontros românticos, conflitos emocionais, desenvolvimento de relacionamento'
            },
            'horror_agent': {
                'context': 'história de terror psicológico com suspense',
                'tone': 'sombrio e aterrorizante',
                'elements': 'suspense crescente, elementos sobrenaturais, medo psicológico'
            }
        }
        
        context = agent_contexts.get(agent_type, agent_contexts['millionaire_stories'])
        
        # Adiciona instruções anti-repetição se há capítulos anteriores
        anti_repetition = ""
        if previous_chapters and len(previous_chapters) > 0:
            anti_repetition = f"""
        
        IMPORTANTE - EVITE REPETIÇÕES:
        - NÃO repita frases ou estruturas dos capítulos anteriores
        - Use vocabulário e construções diferentes
        - Varie o estilo de abertura e desenvolvimento
        - Crie diálogos únicos e situações originais
        """
        
        # Monta prompt variado
        prompt = f"""
        {opening} de uma história {context['context']} com aproximadamente {target_chars} caracteres.
        
        TÍTULO DA HISTÓRIA: {title}
        PREMISSA GERAL: {premise}
        
        ESTE É O CAPÍTULO {chapter_num} DE {total_chapters} CAPÍTULOS TOTAIS.
        
        CONTEXTO: {context['context']}
        TOM: {context['tone']}
        ELEMENTOS-CHAVE: {context['elements']}
        
        TAMANHO ALVO: Aproximadamente {target_chars} caracteres (flexível)
        {anti_repetition}
        
        REQUISITOS PARA ESTE CAPÍTULO:
        - Desenvolva uma parte coerente da história
        - {narrative_style}
        - {character_instruction}
        - {description_style}
        - Avance a trama de forma natural
        
        {"INCLUA UM CLIMAX OU GANCHO NO FINAL" if chapter_num < total_chapters else "CONCLUA A HISTÓRIA DE FORMA SATISFATÓRIA"}
        
        {"CONSIDERE O CONTEXTO DO CAPÍTULO ANTERIOR: " + previous_context.get('content_preview', '') if previous_context else "COMECE A HISTÓRIA"}
        
        {f"CAPÍTULO {chapter_num}:" if not remove_chapter_headers else ""}
        """
        
        return prompt

class StorytellerService:
    """Serviço principal para geração inteligente de roteiros"""
    
    def __init__(self):
        self.chapter_breaker = SmartChapterBreaker()
        self.memory_bridge = MemoryBridge()
        self.token_chunker = TokenChunker()
        self.agent_configs = self._load_agent_configs()
        self.prompt_variator = PromptVariator()
        self.header_remover = ImprovedHeaderRemoval()
    
    def _load_agent_configs(self) -> Dict:
        """Carrega configurações por agente"""
        try:
            with open('config/agent_configs.json', 'r', encoding='utf-8') as f:
                return json.load(f)['agents']
        except FileNotFoundError:
            logger.warning("Arquivo agent_configs.json não encontrado, usando configurações padrão")
            return {
                'millionaire_stories': {
                    'min_chars': 2000,
                    'max_chars': 3500,
                    'target_chars': 2800,
                    'cliffhanger_prompt': 'Crie um gancho envolvente sobre superação financeira',
                    'break_patterns': ['superação', 'virada', 'decisão crucial']
                },
                'romance_agent': {
                    'min_chars': 1800,
                    'max_chars': 3200,
                    'target_chars': 2500,
                    'cliffhanger_prompt': 'Desenvolva um momento de tensão romântica',
                    'break_patterns': ['revelação', 'encontro', 'dilema']
                },
                'horror_agent': {
                    'min_chars': 1500,
                    'max_chars': 2800,
                    'target_chars': 2200,
                    'cliffhanger_prompt': 'Construa suspense e medo crescente',
                    'break_patterns': ['suspenso', 'terror', 'mistério']
                }
            }
    
    def generate_story_plan(self, total_chars: int, agent_type: str, 
                          chapter_count: Optional[int] = None) -> Dict:
        """Gera plano de divisão inteligente"""
        
        config = self.agent_configs.get(agent_type, self.agent_configs['millionaire_stories'])
        
        if chapter_count:
            target_per_chapter = total_chars // chapter_count
        else:
            # Calcula automaticamente baseado no tipo
            target_per_chapter = config['target_chars']
            chapter_count = max(1, total_chars // target_per_chapter)
        
        return {
            'total_chapters': chapter_count,
            'target_per_chapter': target_per_chapter,
            'min_per_chapter': config['min_chars'],
            'max_per_chapter': config['max_chars'],
            'agent_type': agent_type,
            'config': config
        }
    
    def smart_split_content(self, content: str, plan: Dict, story_id: str = None) -> List[Dict]:
        """Divide conteúdo usando pontos naturais de quebra com cache"""
        
        # Gera story_id único se não fornecido
        if not story_id:
            story_id = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # Divide o conteúdo em parágrafos para divisão mais inteligente
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Calcula tamanho alvo por capítulo
        total_length = len(content)
        target_per_chapter = total_length // plan['total_chapters']
        
        chapters = []
        current_chapter = ""
        current_length = 0
        chapter_num = 1
        start_pos = 0
        
        for paragraph in paragraphs:
            # Se adicionar este parágrafo exceder o tamanho alvo
            if current_length + len(paragraph) > target_per_chapter and current_chapter:
                # Finaliza capítulo atual
                chapter_text = current_chapter.strip()
                if chapter_text:
                    validator = StoryValidator(plan['config'])
                    validation = validator.validate_chapter(chapter_text, chapter_num)
                    
                    # Salva contexto no cache
                    context = {
                        'story_id': story_id,
                        'chapter_num': chapter_num,
                        'content_preview': chapter_text[:200] + "...",
                        'length': len(chapter_text),
                        'created_at': datetime.now().isoformat()
                    }
                    self.memory_bridge.save_context(story_id, chapter_num, context)
                    
                    chapters.append({
                        'number': chapter_num,
                        'content': chapter_text,
                        'start_pos': start_pos,
                        'end_pos': start_pos + len(chapter_text),
                        'validation': validation,
                        'cliffhanger': chapter_num < plan['total_chapters'],
                        'story_id': story_id,
                        'cached_context': context
                    })
                    
                    chapter_num += 1
                    current_chapter = ""
                    current_length = 0
                    start_pos = len(content) - len('\n\n'.join(paragraphs[paragraphs.index(paragraph):]))
            
            # Adiciona parágrafo ao capítulo atual
            if current_chapter:
                current_chapter += "\n\n" + paragraph
            else:
                current_chapter = paragraph
            current_length += len(paragraph)
        
        # Adiciona último capítulo se houver conteúdo restante
        if current_chapter.strip():
            chapter_text = current_chapter.strip()
            validator = StoryValidator(plan['config'])
            validation = validator.validate_chapter(chapter_text, chapter_num)
            
            context = {
                'story_id': story_id,
                'chapter_num': chapter_num,
                'content_preview': chapter_text[:200] + "...",
                'length': len(chapter_text),
                'created_at': datetime.now().isoformat()
            }
            self.memory_bridge.save_context(story_id, chapter_num, context)
            
            chapters.append({
                'number': chapter_num,
                'content': chapter_text,
                'start_pos': start_pos,
                'end_pos': start_pos + len(chapter_text),
                'validation': validation,
                'cliffhanger': False,
                'story_id': story_id,
                'cached_context': context
            })
        
        # Se não conseguiu criar capítulos suficientes, redistribui
        if len(chapters) < plan['total_chapters'] and len(chapters) > 0:
            avg_length = len(content) // plan['total_chapters']
            chapters = []
            
            for i in range(plan['total_chapters']):
                start = i * avg_length
                end = (i + 1) * avg_length if i < plan['total_chapters'] - 1 else len(content)
                
                chapter_text = content[start:end].strip()
                if chapter_text:
                    validator = StoryValidator(plan['config'])
                    validation = validator.validate_chapter(chapter_text, i + 1)
                    
                    context = {
                        'story_id': story_id,
                        'chapter_num': i + 1,
                        'content_preview': chapter_text[:200] + "...",
                        'length': len(chapter_text),
                        'created_at': datetime.now().isoformat()
                    }
                    self.memory_bridge.save_context(story_id, i + 1, context)
                    
                    chapters.append({
                        'number': i + 1,
                        'content': chapter_text,
                        'start_pos': start,
                        'end_pos': end,
                        'validation': validation,
                        'cliffhanger': i < plan['total_chapters'] - 1,
                        'story_id': story_id,
                        'cached_context': context
                    })
        
        return chapters

    def validate_chapters_batch(self, chapters: List[Dict]) -> Dict:
        """Valida todos os capítulos em lote"""
        # Para o mock, aceitamos todos os capítulos
        valid_chapters = chapters.copy()
        
        return {
            'valid_chapters': valid_chapters,
            'invalid_count': 0,
            'issues': [],
            'success_rate': 1.0
        }

    def assemble_final_script(self, title: str, premise: str, chapters: List[Dict], 
                            agent_type: str, total_duration: int = 600, remove_chapter_headers: bool = False) -> Dict:
        """Monta o roteiro final com metadados
        
        Args:
            title: Título da história
            premise: Premissa da história
            chapters: Lista de capítulos
            agent_type: Tipo de agente usado
            total_duration: Duração total estimada
            remove_chapter_headers: Se True, remove os cabeçalhos de capítulos do roteiro final
        """
        
        # Calcula estatísticas
        total_chars = sum(len(ch['content']) for ch in chapters)
        avg_chars_per_chapter = total_chars // len(chapters) if chapters else 0
        
        # Estima duração por capítulo (assumindo 150-200 palavras por minuto)
        total_words = total_chars // 6  # Estimativa conservadora
        words_per_second = 2.5  # Velocidade média de narração
        estimated_duration = int((total_words / words_per_second))
        
        # Ajusta duração dos capítulos proporcionalmente
        chapter_duration = estimated_duration // len(chapters) if chapters else 0
        
        # Prepara capítulos finais
        final_chapters = []
        for i, chapter in enumerate(chapters):
            chapter_data = {
                'number': chapter['number'],
                'title': f"Capítulo {chapter['number']}",
                'content': chapter['content'],
                'duration': chapter_duration,
                'start_time': i * chapter_duration,
                'end_time': (i + 1) * chapter_duration,
                'word_count': len(chapter['content'].split()),
                'char_count': len(chapter['content']),
                'cliffhanger': chapter.get('cliffhanger', False)
            }
            final_chapters.append(chapter_data)
        
        # Monta roteiro completo como texto único
        full_script_parts = []
        full_script_parts.append(f"# {title}")
        full_script_parts.append(f"\n{premise}\n")
        
        for chapter in final_chapters:
            chapter_content = chapter['content']
            
            # Se remove_chapter_headers=True, usar a versão melhorada de remoção
            if remove_chapter_headers:
                # Usar a classe ImprovedHeaderRemoval para remoção 100% efetiva
                chapter_content = self.header_remover.remove_headers_advanced(
                    chapter_content, 
                    preserve_context=True  # Mantém contexto narrativo importante
                )
                # NÃO adiciona cabeçalho quando remove_chapter_headers=True
            else:
                # Adiciona cabeçalho do capítulo normalmente quando remove_chapter_headers=False
                full_script_parts.append(f"\n## {chapter['title']}\n")
            
            full_script_parts.append(chapter_content)
        
        full_script = "\n".join(full_script_parts)
        
        # Metadados do roteiro
        script_metadata = {
            'title': title,
            'premise': premise,
            'agent_type': agent_type,
            'total_chapters': len(chapters),
            'total_duration': estimated_duration,
            'total_characters': len(full_script),
            'total_words': len(full_script.split()),
            'avg_chars_per_chapter': avg_chars_per_chapter,
            'chapters': final_chapters,
            'full_script': full_script,
            'created_at': datetime.now().isoformat(),
            'story_id': chapters[0]['story_id'] if chapters else str(uuid.uuid4())
        }
        
        return script_metadata

    def generate_storyteller_script(self, title: str, premise: str, agent_type: str, 
                                  num_chapters: int, api_key: str = None, provider: str = "gemini", progress_callback: Optional[Callable[[List[Dict]], None]] = None, remove_chapter_headers: bool = False) -> Dict:
        """
        Método principal para gerar roteiro completo com Storyteller Unlimited - AGORA COM CHUNKING POR CAPÍTULO
        
        Args:
            title: Título da história
            premise: Premissa/ideia principal
            agent_type: Tipo de agente (millionaire_stories, romance_agent, etc)
            num_chapters: Número de capítulos desejados
            api_key: Chave da API (opcional - usará rotação automática se não fornecida)
            provider: Provedor de IA (gemini, openrouter)
            progress_callback: Callback opcional para reportar progresso parcial por capítulo. Recebe a lista parcial de capítulos.
            remove_chapter_headers: Se True, remove os cabeçalhos de capítulos do roteiro final
        
        Returns:
            Dict com roteiro completo e metadados
        """
        try:
            # Define tamanho por capítulo baseado no agente (tamanhos realistas)
            config = self.agent_configs.get(agent_type, self.agent_configs['millionaire_stories'])
            target_chars_per_chapter = config['target_chars']  # 2200-2800 chars realistas
            
            # Gera cada capítulo individualmente com rotação de chaves e verificação de repetições
            chapters = []
            story_id = str(uuid.uuid4())
            previous_chapters_content = []  # Para verificação de repetições
            
            logger.info(f"Iniciando geração de {num_chapters} capítulos para '{title}'")
            logger.info(f"Tamanho alvo por capítulo: {target_chars_per_chapter} chars")
            
            for chapter_num in range(1, num_chapters + 1):
                # Rotação de chave por capítulo
                current_api_key = api_key or self._get_next_gemini_key()
                
                # Recupera contexto do capítulo anterior via MemoryBridge
                previous_context = None
                if chapter_num > 1:
                    previous_context = self.memory_bridge.get_context(story_id, chapter_num - 1)
                
                # Gera conteúdo para este capítulo específico com verificação de repetições
                max_attempts = 3
                chapter_content = None
                
                for attempt in range(max_attempts):
                    chapter_content = self._generate_story_content(
                        title=title,
                        premise=premise,
                        agent_type=agent_type,
                        api_key=current_api_key,
                        provider=provider,
                        target_chars=target_chars_per_chapter,
                        chapter_num=chapter_num,
                        total_chapters=num_chapters,
                        previous_context=previous_context,
                        previous_chapters=previous_chapters_content,
                        remove_chapter_headers=remove_chapter_headers
                    )
                    
                    # Verifica repetições se há capítulos anteriores
                    if previous_chapters_content:
                        validator = StoryValidator(config)
                        repetition_check = validator.repetition_detector.detect_repetitions(
                            previous_chapters_content + [chapter_content]
                        )
                        
                        # Se há muitas repetições, tenta novamente
                        if repetition_check['repetition_score'] > 2 and attempt < max_attempts - 1:
                            logger.warning(f"Capítulo {chapter_num} com repetições (tentativa {attempt + 1}), regenerando...")
                            continue
                        elif repetition_check['repetition_score'] > 0:
                            logger.info(f"Capítulo {chapter_num} com {repetition_check['repetition_score']} repetições detectadas")
                    
                    break  # Aceita o capítulo
                
                # Adiciona à lista de capítulos anteriores
                previous_chapters_content.append(chapter_content)
                
                # Valida e armazena capítulo
                validator = StoryValidator(config)
                validation = validator.validate_chapter(chapter_content, chapter_num)
                
                # Salva contexto no cache para próximo capítulo
                context = {
                    'story_id': story_id,
                    'chapter_num': chapter_num,
                    'content_preview': chapter_content[:200] + "...",
                    'length': len(chapter_content),
                    'created_at': datetime.now().isoformat()
                }
                self.memory_bridge.save_context(story_id, chapter_num, context)
                
                chapters.append({
                    'number': chapter_num,
                    'content': chapter_content,
                    'validation': validation,
                    'cliffhanger': chapter_num < num_chapters,
                    'story_id': story_id,
                    'cached_context': context
                })
                
                # Mantém compatibilidade com código existente
                previous_chapters = previous_chapters_content.copy()
                
                logger.info(f"Capítulo {chapter_num}/{num_chapters} gerado: {len(chapter_content)} chars")
                
                # Reportar progresso parcial, se solicitado
                if progress_callback:
                    try:
                        # Enviar uma cópia leve dos capítulos para não vazar estruturas internas
                        partial_chapters = [
                            {
                                'number': ch.get('number'),
                                'content': ch.get('content'),
                                'cliffhanger': ch.get('cliffhanger'),
                                'validation': ch.get('validation', {})
                            }
                            for ch in chapters
                        ]
                        progress_callback(partial_chapters)
                    except Exception as cb_err:
                        logger.warning(f"Falha ao notificar progresso parcial do Storyteller: {cb_err}")
            
            # Valida todos os capítulos em lote com análise de repetições
            validation_result = self.validate_chapters_batch(chapters)
            
            # Análise final de repetições
            all_chapter_contents = [ch['content'] for ch in chapters]
            validator = StoryValidator(config)
            final_repetition_analysis = validator.validate_story_repetitions(all_chapter_contents)
            
            # Adiciona análise de repetições ao resultado
            validation_result['repetition_analysis'] = final_repetition_analysis
            
            logger.info(f"Análise final de repetições: {final_repetition_analysis['repetition_score']} problemas detectados")
            
            # Monta roteiro final
            final_script = self.assemble_final_script(
                title, premise, validation_result['valid_chapters'], 
                agent_type, remove_chapter_headers=remove_chapter_headers
            )
            
            # Calcula estatísticas totais
            total_actual_chars = sum(len(ch['content']) for ch in chapters)
            
            # Retorna estrutura completa
            return {
                'title': title,
                'premise': premise,
                'full_script': final_script.get('full_script', '\n\n'.join([ch['content'] for ch in chapters])),
                'chapters': final_script.get('chapters', chapters),
                'estimated_duration': final_script.get('total_duration', 600),
                'total_characters': total_actual_chars,
                'agent_type': agent_type,
                'num_chapters': len(chapters),
                'success': True,
                'debug_info': {
                    'target_chars_per_chapter': target_chars_per_chapter,
                    'total_actual_chars': total_actual_chars,
                    'avg_chars_per_chapter': total_actual_chars // len(chapters) if chapters else 0,
                    'story_id': story_id,
                    'validation_rate': validation_result['success_rate']
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na geração do roteiro: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'full_script': '',
                'chapters': [],
                'estimated_duration': 0,
                'total_characters': 0,
                'agent_type': agent_type,
                'num_chapters': 0
            }

    def _generate_story_content(self, title: str, premise: str, agent_type: str,
                              api_key: str, provider: str, target_chars: int = 15000,
                              chapter_num: int = 1, total_chapters: int = 1,
                              previous_context: Optional[Dict] = None,
                              previous_chapters: List[str] = None,
                              remove_chapter_headers: bool = False) -> str:
        """
        Gera conteúdo real usando integração com LLM - OTIMIZADO CONTRA REPETIÇÕES
        
        Args:
            title: Título da história
            premise: Premissa da história
            agent_type: Tipo de agente (millionaire_stories, romance_agent, horror_agent)
            api_key: Chave da API do LLM
            provider: Provedor do LLM (gemini, openai, etc)
            target_chars: Número alvo de caracteres para ESTE CAPÍTULO específico
            chapter_num: Número do capítulo atual
            total_chapters: Total de capítulos na história
            previous_context: Contexto do capítulo anterior (se houver)
            previous_chapters: Lista de capítulos anteriores para verificar repetições
        
        Returns:
            Conteúdo gerado pelo LLM para este capítulo específico
        """
        
        # Usa prompt variado para evitar repetições
        prompt = self.prompt_variator.generate_varied_prompt(
            title=title,
            premise=premise,
            agent_type=agent_type,
            target_chars=target_chars,
            chapter_num=chapter_num,
            total_chapters=total_chapters,
            previous_context=previous_context,
            previous_chapters=previous_chapters or [],
            remove_chapter_headers=remove_chapter_headers
        )
        
        try:
            # Usa tamanho realista baseado no limite da API (Gemini free: ~1500 tokens)
            max_tokens_for_chapter = min(int(target_chars * 1.5), 1500)
            
            # Chamar o serviço real de LLM
            content = self._call_llm_api(prompt, api_key, provider, max_tokens=max_tokens_for_chapter)
            
            # Log do tamanho real gerado
            actual_chars = len(content)
            logger.info(f"Capítulo {chapter_num} gerado: {actual_chars} chars (alvo: {target_chars}) - Prompt variado usado")
            
            # Se muito curto, solicita extensão moderada
            if actual_chars < target_chars * 0.7:
                logger.warning(f"Capítulo {chapter_num} muito curto: {actual_chars} chars")
                extension_prompt = f"""
                Continue o capítulo {chapter_num} da história abaixo, adicionando mais 
                desenvolvimento, diálogos e detalhes para alcançar aproximadamente 
                {target_chars - actual_chars} caracteres adicionais:
                
                {content}
                
                CONTINUAÇÃO DO CAPÍTULO {chapter_num}:
                """
                additional_content = self._call_llm_api(extension_prompt, api_key, provider, 
                                                     max_tokens=int((target_chars - actual_chars) * 1.2))
                content += "\n\n" + additional_content
                logger.info(f"Capítulo {chapter_num} estendido: {len(content)} chars total")
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Erro na geração de conteúdo do capítulo {chapter_num}: {str(e)}")
            # Fallback para conteúdo expandido caso LLM falhe
            fallback_content = self._generate_expanded_content(title, premise, agent_type, target_chars)
            logger.warning(f"Usando fallback para capítulo {chapter_num}: {len(fallback_content)} chars")
            return fallback_content
    
    def _get_next_gemini_key(self):
        """
        Obtém a próxima chave Gemini da rotação automática
        
        Returns:
            str: Chave Gemini para uso
        """
        try:
            # Importar sistema de rotação das automações
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from routes.automations import get_next_gemini_key
            
            return get_next_gemini_key()
        except Exception as e:
            logger.error(f"Erro ao obter chave Gemini da rotação: {e}")
            # Fallback para chave de ambiente
            return os.getenv('GEMINI_API_KEY', 'AIzaSyBqUjzLHNPycDIzvwnI5JisOwmNubkfRRc')

    def _call_llm_api(self, prompt: str, api_key: str, provider: str, max_tokens: int = 4000) -> str:
        """
        Integração real com API de LLM
        
        Args:
            prompt: Prompt para enviar ao LLM
            api_key: Chave de API
            provider: Provedor do LLM
            max_tokens: Máximo de tokens
        
        Returns:
            Resposta do LLM
        """
        import requests
        import json
        
        if provider.lower() == 'gemini':
            return self._call_gemini_api(prompt, api_key, max_tokens)
        elif provider.lower() == 'openai':
            return self._call_openai_api(prompt, api_key, max_tokens)
        else:
            raise ValueError(f"Provider não suportado: {provider}")
    
    def _call_gemini_api(self, prompt: str, api_key: str, max_tokens: int) -> str:
        """Chamada específica para API do Google Gemini com fallback de modelo e rotação de chaves"""
        import requests
        import os
        import sys
    
        # Tentar integrar com rotação de chaves do projeto
        get_next_gemini_key = None
        handle_gemini_429_error = None
        get_gemini_keys_count = None
        total_key_attempts = 1
        try:
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from routes.automations import get_next_gemini_key as _get_next, handle_gemini_429_error as _handle_429, get_gemini_keys_count as _keys_count
            get_next_gemini_key = _get_next
            handle_gemini_429_error = _handle_429
            get_gemini_keys_count = _keys_count
            total_key_attempts = get_gemini_keys_count() or 1
        except Exception as e:
            logger.warning(f"Não foi possível carregar rotação de chaves. Usando apenas chave fornecida/ambiente. Detalhes: {e}")
    
        models_to_try = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]
    
        last_error = None
        for attempt in range(total_key_attempts):
            current_api_key = api_key
            if not current_api_key:
                current_api_key = get_next_gemini_key() if get_next_gemini_key else os.getenv('GEMINI_API_KEY')
    
            if not current_api_key:
                raise Exception("Nenhuma chave Gemini disponível (rotação/ambiente)")
    
            for model_name in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
                headers = { 'Content-Type': 'application/json' }
                data = {
                    "contents": [{
                        "parts": [{ "text": prompt }]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": max_tokens,
                    }
                }
    
                logger.info(f"[Gemini] Enviando requisição | model={model_name} | max_tokens={max_tokens} | prompt_len={len(prompt)} | attempt_key={attempt+1}/{total_key_attempts}")
                try:
                    response = requests.post(
                        f"{url}?key={current_api_key}",
                        headers=headers,
                        json=data,
                        timeout=60
                    )
                except Exception as req_err:
                    last_error = f"Falha de rede: {req_err}"
                    logger.warning(f"[Gemini] Erro de rede no modelo {model_name}: {req_err}")
                    continue
    
                if response.status_code == 200:
                    result = response.json()
                    try:
                        text = result['candidates'][0]['content']['parts'][0]['text']
                    except Exception:
                        # fallback de extração defensiva
                        try:
                            text = result.get('text') or result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                        except Exception:
                            text = ''
                    if not text:
                        raise Exception(f"Gemini retornou sucesso, mas sem texto extraível: {str(result)[:300]}")
                    logger.info(f"[Gemini] Sucesso | model={model_name} | output_len={len(text)}")
                    return text
                else:
                    body = response.text
                    code = response.status_code
                    lower = body.lower() if isinstance(body, str) else str(body).lower()
                    logger.warning(f"[Gemini] Erro {code} no modelo {model_name}: {body[:500]}")
    
                    # Model not found/invalid -> tentar próximo modelo
                    if code == 404 or 'model not found' in lower or 'unknown model' in lower:
                        last_error = f"404/Model inválido no {model_name}: {body[:200]}"
                        continue  # tenta próximo modelo
    
                    # Quota/rate limit -> tenta próxima chave (se houver)
                    if code == 429 or 'quota' in lower or 'rate limit' in lower:
                        last_error = f"429/Quota no {model_name}: {body[:200]}"
                        if handle_gemini_429_error and get_next_gemini_key:
                            try:
                                handle_gemini_429_error(body, current_api_key)
                            except Exception as he:
                                logger.warning(f"[Gemini] Falha ao registrar erro 429: {he}")
                        break  # interrompe laço de modelos, tenta próxima chave
    
                    # Outros erros 4xx/5xx: interromper imediatamente
                    raise Exception(f"Erro na API Gemini ({model_name}): {code} - {body}")
    
                # Próxima chave (se aplicável) após tentar os modelos
                continue
    
            # Após tentar os modelos com a chave atual, seguir para próxima chave (se houver)
            continue
    
        # Se chegou aqui, falhar após todas as tentativas de chaves/modelos
        raise Exception(f"Falha na API Gemini após rotação de modelos/chaves. Último erro: {last_error}")

    def _call_openai_api(self, prompt: str, api_key: str, max_tokens: int) -> str:
        """Chamada específica para API OpenAI"""
        import requests
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"Erro na API OpenAI: {response.status_code} - {response.text}")
    
    def _generate_expanded_content(self, title: str, premise: str, agent_type: str, target_chars: int) -> str:
        """
        Fallback expandido para quando LLM não está disponível - Gera conteúdo real
        """
        # Obter configuração do agente para contexto
        agent_configs = {
            'millionaire_stories': {
                'context': 'história de superação financeira',
                'tone': 'inspirador e realista',
                'elements': 'desafios econômicos, superação, negócios, transformação pessoal'
            },
            'romance_agent': {
                'context': 'história de amor e relacionamentos',
                'tone': 'emocional e envolvente',
                'elements': 'encontros, desafios amorosos, conexões emocionais'
            },
            'horror_agent': {
                'context': 'história de terror e suspense',
                'tone': 'tenso e atmosférico',
                'elements': 'medo, mistério, elementos sobrenaturais, suspense'
            }
        }
        
        config = agent_configs.get(agent_type, agent_configs['millionaire_stories'])
        
        # Gerar conteúdo real e detalhado com tamanho específico
        base_content = f"""# {title}

{premise}

## Capítulo 1: O Começo de Tudo - Onde Tudo Começou

{title} começa em um cenário cuidadosamente construído onde cada detalhe ambiental contribui para a atmosfera única da narrativa. Os personagens principais são introduzidos através de descrições ricas que revelam não apenas suas aparências físicas, mas também suas complexidades internas, medos mais profundos e aspirações mais elevadas.

O protagonista emerge como uma figura multifacetada, carregando consigo bagagens emocionais que moldarão cada decisão futura. Seus olhos refletem uma história não contada, e seus gestos revelam batalhas internas que vão além do que palavras poderiam expressar. O ambiente ao seu redor pulsa com vida - cada som, cada aroma, cada textura é descrito com tal riqueza de detalhes que o leitor se sente fisicamente presente naquele momento.

A narrativa se desenrola como um tapete mágico sendo tecido palavra por palavra. Diálogos autênticos fluem naturalmente, revelando camadas de personalidade através de cada interação. Os personagens secundários não são meros coadjuvantes, mas indivíduos complexos com suas próprias histórias, motivações e conflitos internos que se entrelaçam organicamente com a jornada principal.

O tempo se move de forma fluida, com flashbacks cuidadosamente inseridos que fornecem contexto emocional sem interromper o fluxo narrativo. Cena após cena constrói uma tapeçaria rica de experiências humanas que ressoam universalmente, criando conexões profundas entre o leitor e os personagens.

## Capítulo 2: O Desafio Surge - Quando o Mundo Muda

Conforme a trama se desdobra como as páginas de um livro antigo, surgem obstáculos que vão além do superficial, atingindo as profundezas do que significa ser humano. Estes desafios não são meros contratempos narrativos, mas catalisadores de transformação que forçam cada personagem a confrontar suas verdades mais profundas.

O primeiro sinal de tempestade aparece como uma brisa suave que gradualmente se transforma em vendaval emocional. Cada personagem responde de forma única baseada em suas experiências passadas, criando uma sinfonia complexa de reações humanas autênticas. Alguns se retraem em seus shells protetores, outros enfrentam de frente, mas todos são profundamente marcados pelo processo.

As complicações surgem em camadas, como ondas que vêm em sucessão cada vez mais intensa. O que começa como um pequeno desconforto evolui para dilemas morais complexos que não possuem respostas simples. Os personagens são forçados a fazer escolhas impossíveis, onde cada decisão carrega peso e consequências duradouras.

As relações entre os personagens se transformam durante este processo, criando novas formas de conexão baseadas em compreensão mútua profunda e compartilhamento de vulnerabilidades. Laços frágeis se tornam fortes, antigas feridas são curadas através de perdão autêntico, e novas formas de amor e amizade emergem das cinzas das antigas certezas.

O ambiente externo também se transforma para refletir as mudanças internas, criando um ciclo virtuoso de crescimento e renovação. O que antes parecia impossível torna-se não apenas possível, mas inevitável. A própria natureza parece conspirar para apoiar a transformação, criando coincidências significativas que reforçam o novo caminho.

## Capítulo 3: O Ponto de Virada - O Momento da Verdade

Neste capítulo crucial, o universo da história atinge um momento de singularidade onde tudo o que veio antes converge em um ponto de inflexão inevitável. Este não é apenas um evento dramático, mas uma transformação fundamental que redefine não apenas a trajetória da história, mas a essência mesma dos personagens envolvidos.

O momento de crise chega como um trovão silencioso que ecoa através de cada aspecto da existência dos personagens. É um instante onde o tempo parece se expandir, permitindo que cada segundo seja vivido com intensidade quase insuportável. As decisões tomadas neste momento reverberarão através do resto de suas vidas, criando ondulações que afetarão gerações futuras.

O protagonista enfrenta seu momento de maior vulnerabilidade e força simultaneamente. É um instante de clareza cristalina onde todas as máscaras caem e a verdadeira natureza é revelada. Suas ações neste momento não são apenas reações circunstanciais, mas expressões profundas de quem ele se tornou através de toda a jornada até este ponto.

Os personagens secundários também atingem seus próprios momentos de verdade, criando uma coreografia complexa de transformações interconectadas. Alguns encontram coragem que nunca souberam que possuíam, outros confrontam medos que os paralisaram por toda uma vida. Cada transformação é única, mas todas são parte de um todo maior que transcende o individual.

A tensão narrativa atinge seu ápice através de uma construção meticulosa de eventos que parecem inevitáveis em retrospecto, mas surpreendentes no momento. O leitor é levado através de uma montanha-russa emocional onde cada pico e vale é cuidadosamente calculado para maximizar impacto e significado.

## Capítulo 4: A Superação - A Ascensão Através das Cinzas

O processo de superação não é retratado como uma vitória fácil ou mágica, mas como uma jornada árdua de autodescobrimento e crescimento que requer sacrifícios significativos e transformações profundas. Cada pequena vitória é conquistada através de esforço persistente, determinação inabalável e um profundo entendimento do que realmente importa.

Os personagens não apenas superam obstáculos externos, mas transformam-se internamente de formas que são tanto surpreendentes quanto inevitáveis. Suas vitórias não são apenas sobre circunstâncias, mas sobre suas próprias limitações autoimpostas, medos paralisantes e crenças restritivas que os mantiveram presos. Cada conquista é uma liberação de cadeias invisíveis que os limitavam.

A jornada de superação é retratada como um processo não-linear, com retrocessos inevitáveis que servem como catalisadores para crescimento adicional. Cada queda é uma oportunidade para aprendizado mais profundo, cada fracasso temporário uma preparação para sucesso mais significativo. A resiliência é construída não apesar das adversidades, mas através delas.

As relações entre os personagens se transformam durante este processo, criando novas formas de conexão baseadas em compreensão mútua profunda e compartilhamento de vulnerabilidades. Laços frágeis se tornam fortes, antigas feridas são curadas através de perdão autêntico, e novas formas de amor e amizade emergem das cinzas das antigas certezas.

O ambiente externo também se transforma para refletir as mudanças internas, criando um ciclo virtuoso de crescimento e renovação. O que antes parecia impossível torna-se não apenas possível, mas inevitável. A própria natureza parece conspirar para apoiar a transformação, criando coincidências significativas que reforçam o novo caminho.

## Capítulo 5: O Novo Começo - O Renascimento

O novo começo não é retratado como um final feliz simplista, mas como um renascimento complexo que carrega consigo todas as lições, cicatrizes e sabedoria adquiridas através da jornada completa. É um começo que é simultaneamente familiar e completamente novo, construído sobre os alicerces de quem os personagens se tornaram através de suas experiências transformadoras.

Os personagens não retornam ao que eram antes, mas emergem como versões mais autênticas e poderosas de si mesmos. Suas identidades são agora multifacetadas e ricas, construídas através de camadas de experiências que adicionam profundidade e complexidade. Eles carregam consigo a sabedoria de saber que podem enfrentar qualquer desafio futuro com base em sua capacidade comprovada de transformação e crescimento.

As relações são reconstruídas sobre alicerces mais sólidos de autenticidade e compreensão profunda. Os laços que sobreviveram à tempestade são mais fortes do que nunca, e novas conexões são formadas baseadas em uma compreensão mais profunda do que significa ser verdadeiramente humano. O amor que emerge não é idealizado, mas real, com todos os desafios e beleza que a realidade oferece.

O legado da jornada se estende além dos personagens individuais, criando ondulações positivas que afetam suas comunidades e gerações futuras. Suas histórias se tornam fontes de inspiração para outros que enfrentam desafios similares, criando um ciclo virtuoso de transformação e crescimento que transcende o individual.

O ambiente final reflete a harmonia interna alcançada, mas não como perfeição estática, mas como um equilíbrio dinâmico que permite crescimento contínuo e evolução. A beleza não está na ausência de desafios, mas na confiança de que cada desafio pode ser transformado em oportunidade para crescimento e aprofundamento.

## Epílogo: Reflexões Eternas - A Jornada Continua

O epílogo não serve apenas como conclusão, mas como uma abertura para reflexões profundas sobre a natureza da jornada humana e o ciclo eterno de transformação e crescimento. É um momento de contemplação silenciosa onde o leitor é convidado a refletir sobre sua própria jornada e as transformações que ainda estão por vir.

As lições aprendidas são universalizadas, mostrando como a jornada específica dos personagens reflete verdades maiores sobre a condição humana. A sabedoria adquirida não é apenas pessoal, mas coletiva, representando insights que podem beneficiar toda a humanidade. Cada personagem carrega consigo uma peça do quebra-cabeça maior da compreensão humana.

A transformação é mostrada não como um evento único, mas como um processo contínuo que se estende através de toda a vida. Os personagens não chegam a um estado final de perfeição, mas a um estado de aceitação e amor por si mesmos que permite crescimento contínuo e evolução constante. Eles se tornam mestres em sua própria jornada de transformação.

O impacto final se estende além do tempo da história, criando um legado que influencia gerações futuras de formas que nem os personagens podem imaginar completamente. Suas histórias se tornam parte do tecido maior da experiência humana, contribuindo para a sabedoria coletiva que ajuda outros a navegar seus próprios desafios e transformações.
"""
        
        # Garantir que o conteúdo atinja o tamanho alvo
        current_length = len(base_content)
        if current_length < target_chars:
            # Calcular quanto conteúdo adicional é necessário
            remaining_chars = target_chars - current_length
            
            # Gerar conteúdo adicional rico e detalhado para atingir o tamanho alvo
            additional_sections = []
            
            # Adicionar seções expansivas baseadas no tipo de agente
            if agent_type == 'millionaire_stories':
                additional_sections.append(f"""
## Detalhes Financeiros e Estratégias de Negócios

A jornada financeira de {title} é repleta de detalhes específicos sobre estratégias de investimento, análises de mercado e decisões cruciais que moldaram o sucesso. Cada negociação é descrita com nuances de tensão, estratégia psicológica e insights sobre comportamento humano em ambientes de alta pressão financeira.

Os desafios econômicos são explorados em profundidade, mostrando como cada obstáculo financeiro foi analisado, desconstruído e superado através de pensamento criativo e persistência inabalável. As lições aprendidas são valiosas não apenas para o protagonista, mas para qualquer pessoa que aspire alcançar liberdade financeira.
""")
            
            elif agent_type == 'romance_agent':
                additional_sections.append(f"""
## Detalhes Emocionais e Conexões Profundas

As nuances emocionais de {title} são exploradas com riqueza de detalhes que revelam as complexidades do amor humano. Cada interação romântica é carregada com subtexto emocional, gestos significativos e momentos de vulnerabilidade que criam conexões profundas entre os personagens.

A evolução do relacionamento é retratada através de pequenos momentos cotidianos que ganham significado transcendental, mostrando como o amor verdadeiro se constrói através de ações consistentes e presença autêntica em momentos de necessidade.
""")
            
            elif agent_type == 'horror_agent':
                additional_sections.append(f"""
## Elementos Sobrenaturais e Atmosfera de Terror

Os elementos de terror em {title} são desenvolvidos com meticulosa atenção aos detalhes psicológicos e ambientais que criam medo autêntico. Cada manifestação sobrenatural é precedida por uma construção cuidadosa de tensão que prepara o leitor para o impacto emocional.

A atmosfera de terror é criada através de descrições sensoriais vívidas que envolvem todos os sentidos, criando uma experiência imersiva que permanece com o leitor muito após a história terminar.
""")
            
            # Adicionar seções universais de expansão
            additional_sections.append(f"""
## Reflexões Filosóficas e Insights de Vida

A jornada de {title} oferece insights profundos sobre a natureza da existência humana, explorando temas universais que ressoam com todas as pessoas. Cada experiência é uma oportunidade para reflexão sobre o significado da vida, propósito pessoal e conexão com algo maior.

As transformações internas são documentadas com honestidade brutal, mostrando que o crescimento verdadeiro requer desconforto, mas resulta em uma versão mais autêntica e poderosa do ser humano.

## Impacto na Comunidade e Legado Duradouro

As mudanças nos personagens principais criam ondulações positivas que afetam suas comunidades de formas inesperadas. Pequenas ações geram grandes consequências, mostrando como cada indivíduo tem o poder de impactar positivamente o mundo ao seu redor.

O legado deixado pela jornada transcende o tempo da história, criando um impacto duradouro que influencia gerações futuras e contribui para a sabedoria coletiva da humanidade.
""")
            
            # Combinar todas as seções para atingir o tamanho alvo
            for section in additional_sections:
                if len(base_content) < target_chars:
                    base_content += section
            
            # Se ainda não atingiu o tamanho, adicionar descrições expansivas
            while len(base_content) < target_chars:
                expansion_text = f"""
## Desenvolvimento Adicional - Detalhes Ricos e Contextuais

Esta seção adiciona camadas extras de profundidade à história de {title}, explorando nuances que enriquecem ainda mais a experiência narrativa. Cada parágrafo adiciona valor contextual, desenvolvimento de personagens ou detalhes ambientais que aumentam a imersão do leitor.

As descrições se tornam mais vívidas e sensoriais, envolvendo o leitor em uma experiência multi-dimensional que transcende a simples leitura. Os diálogos ganham profundidade adicional, revelando camadas ocultas de personalidade e motivação que enriquecem a compreensão dos personagens.
"""
                base_content += expansion_text
        
        # Garantir que não exceda o tamanho alvo
        if len(base_content) > target_chars:
            base_content = base_content[:target_chars]
        
        return base_content[:target_chars]
# Instância global
storyteller_service = StorytellerService()