import json
import re
import redis
import hashlib
import tiktoken
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class ChapterConfig:
    min_chars: int
    max_chars: int
    target_chars: int
    cliffhanger_prompt: str
    break_patterns: List[str]

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
        self.min_chars = config.get('min_chars', 1500)
        self.max_chars = config.get('max_chars', 4000)
    
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

class StorytellerService:
    """Serviço principal para geração inteligente de roteiros"""
    
    def __init__(self):
        self.chapter_breaker = SmartChapterBreaker()
        self.memory_bridge = MemoryBridge()
        self.token_chunker = TokenChunker()
        self.agent_configs = self._load_agent_configs()
    
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
        
        # Verifica cache de breakpoints
        cached_breakpoints = self.memory_bridge.get_breakpoints(story_id)
        if cached_breakpoints:
            logger.info(f"Usando breakpoints cacheados para story {story_id}")
            breakpoints = cached_breakpoints
        else:
            # Calcula breakpoints e salva no cache
            breakpoints = []
            remaining = content
            
            for i in range(plan['total_chapters']):
                if not remaining:
                    break
                
                target_length = min(plan['target_per_chapter'], len(remaining))
                
                # Encontra ponto natural de quebra
                if len(remaining) > target_length:
                    breaks = self.chapter_breaker.find_natural_breaks(
                        remaining, target_length
                    )
                    
                    if breaks:
                        split_at = breaks[0]
                    else:
                        split_at = target_length
                else:
                    split_at = len(remaining)
                
                breakpoints.append(split_at)
                remaining = remaining[split_at:].strip()
            
            # Salva breakpoints no cache
            self.memory_bridge.save_breakpoints(story_id, breakpoints)
        
        # Processa chunks com cache de contexto
        chapters = []
        remaining = content
        start_pos = 0
        
        for i, split_at in enumerate(breakpoints):
            if not remaining:
                break
            
            actual_split = min(split_at, len(remaining))
            chapter_text = remaining[:actual_split].strip()
            remaining = remaining[actual_split:].strip()
            
            # Verifica se precisa de chunking adicional por tokens
            if self.token_chunker.estimate_tokens(chapter_text) > 8000:
                logger.warning(f"Capítulo {i+1} muito grande, aplicando chunking")
                sub_chunks = self.token_chunker.smart_chunking(chapter_text)
                chapter_text = sub_chunks[0]  # Usa primeiro chunk para validação
            
            # Salva contexto no cache
            context = {
                'story_id': story_id,
                'chapter_num': i + 1,
                'content_preview': chapter_text[:200] + "...",
                'length': len(chapter_text),
                'created_at': datetime.now().isoformat()
            }
            self.memory_bridge.save_context(story_id, i + 1, context)
            
            validator = StoryValidator(plan['config'])
            validation = validator.validate_chapter(chapter_text, i + 1)
            
            chapters.append({
                'number': i + 1,
                'content': chapter_text,
                'start_pos': start_pos,
                'end_pos': start_pos + len(chapter_text),
                'validation': validation,
                'cliffhanger': i < len(breakpoints) - 1,
                'story_id': story_id,
                'cached_context': context
            })
            
            start_pos += len(chapter_text)
        
        return chapters

# Instância global
storyteller_service = StorytellerService()