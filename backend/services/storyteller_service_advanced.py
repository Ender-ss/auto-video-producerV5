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

# Importar os novos recursos avançados
from .redis_cache_service import cache_service
from .token_chunker import token_chunker, ChunkInfo
from .smart_chapter_breaker import smart_chapter_breaker, BreakPoint, BreakType

logger = logging.getLogger(__name__)

@dataclass
class ChapterConfig:
    min_chars: int
    max_chars: int
    target_chars: int
    cliffhanger_prompt: str
    break_patterns: List[str]

class StoryValidator:
    """Validador de qualidade de capítulos com recursos avançados."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.min_chars = config.get('min_chars', 500)
        self.max_chars = config.get('max_chars', 4000)
        self.token_chunker = token_chunker
    
    def validate_chapter(self, chapter: str, chapter_num: int) -> Dict:
        """Valida um capítulo individual com análise de tokens."""
        length = len(chapter)
        token_count = self.token_chunker.count_tokens(chapter)
        issues = []
        
        if length < self.min_chars:
            issues.append(f"Capítulo {chapter_num} muito curto: {length} chars")
        
        if length > self.max_chars:
            issues.append(f"Capítulo {chapter_num} muito longo: {length} chars")
        
        # Verifica quebras de diálogo
        open_quotes = chapter.count('"') % 2
        if open_quotes != 0:
            issues.append(f"Diálogo mal fechado no capítulo {chapter_num}")
        
        # Análise de tokens
        if token_count > 4000:  # Limite típico para LLMs
            issues.append(f"Capítulo {chapter_num} excede limite de tokens: {token_count}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'length': length,
            'token_count': token_count,
            'quality_score': 1.0 - (len(issues) * 0.2)
        }

class AdvancedMemoryBridge:
    """Bridge avançado para gerenciamento de contexto com cache Redis."""
    
    def __init__(self):
        self.cache_service = cache_service
        self.chapter_breaker = smart_chapter_breaker
        logger.info("AdvancedMemoryBridge inicializado com recursos avançados")
    
    def _generate_key(self, story_id: str, chapter_num: int, context_type: str) -> str:
        """Gera chave única para cache."""
        return f"story:{story_id}:chapter:{chapter_num}:{context_type}"
    
    def save_context(self, story_id: str, chapter_num: int, context: Dict, ttl=3600):
        """Salva contexto usando RedisCacheService avançado."""
        # Adaptar para usar a API do RedisCacheService
        key = f"{story_id}_context_{chapter_num}"
        # Usar set_breakpoints como método genérico de armazenamento
        self.cache_service.set_breakpoints(key, 1, [json.dumps(context)], "context", ttl)
        logger.debug(f"Contexto salvo: {key}")
    
    def get_context(self, story_id: str, chapter_num: int) -> Optional[Dict]:
        """Recupera contexto usando RedisCacheService avançado."""
        key = f"{story_id}_context_{chapter_num}"
        # Usar get_breakpoints como método genérico de recuperação
        context_data = self.cache_service.get_breakpoints(key, 1, "context")
        if context_data and len(context_data) > 0:
            try:
                context = json.loads(context_data[0])
                logger.debug(f"Contexto recuperado: {key}")
                return context
            except:
                pass
        return None
    
    def save_breakpoints(self, story_id: str, breakpoints: List[BreakPoint]):
        """Salva pontos de quebra avançados usando cache."""
        # Extrair apenas as posições para usar com a API do RedisCacheService
        positions = [bp.position for bp in breakpoints]
        # Salvar as posições usando a API padrão
        self.cache_service.set_breakpoints(story_id, len(breakpoints), positions, "smart", 7200)
        
        # Salvar dados detalhados dos breakpoints separadamente
        detailed_data = [
            {
                'position': bp.position,
                'break_type': bp.break_type.value,
                'confidence': bp.confidence,
                'narrative_score': bp.narrative_score,
                'reason': bp.reason
            }
            for bp in breakpoints
        ]
        detail_key = f"{story_id}_details"
        self.cache_service.set_breakpoints(detail_key, 1, [json.dumps(detailed_data)], "details", 7200)
        logger.info(f"Breakpoints avançados salvos: {len(breakpoints)} pontos")
    
    def get_breakpoints(self, story_id: str) -> Optional[List[Dict]]:
        """Recupera pontos de quebra avançados do cache."""
        # Tentar recuperar dados detalhados primeiro
        detail_key = f"{story_id}_details"
        detail_data = self.cache_service.get_breakpoints(detail_key, 1, "details")
        if detail_data and len(detail_data) > 0:
            try:
                breakpoints = json.loads(detail_data[0])
                logger.info(f"Breakpoints avançados recuperados: {len(breakpoints)} pontos")
                return breakpoints
            except:
                pass
        
        # Fallback: recuperar apenas posições
        positions = self.cache_service.get_breakpoints(story_id, 0, "smart")
        if positions:
            # Converter posições simples em formato de breakpoint
            breakpoints = [{'position': pos, 'break_type': 'scene', 'confidence': 0.5} for pos in positions]
            logger.info(f"Breakpoints básicos recuperados: {len(breakpoints)} pontos")
            return breakpoints
        
        return None
    
    def find_similar_stories(self, premise: str, agent_type: str) -> List[Dict]:
        """Busca histórias similares no cache para reutilização de breakpoints."""
        # Usar get_similar_breakpoints com parâmetros apropriados
        content_length = len(premise)
        similar_breakpoints = self.cache_service.get_similar_breakpoints(
            content_length, 
            3,  # chapter_count padrão
            agent_type,
            similarity_threshold=0.7
        )
        
        if similar_breakpoints:
            # Converter para formato esperado
            similar_stories = [{
                'breakpoints': similar_breakpoints,
                'agent_type': agent_type,
                'content_length': content_length
            }]
            logger.info(f"Encontradas {len(similar_stories)} histórias similares")
            return similar_stories
        
        return []

class AdvancedStorytellerService:
    """Serviço avançado para geração inteligente de roteiros com recursos premium."""
    
    def __init__(self):
        # Usar os novos recursos avançados
        self.chapter_breaker = smart_chapter_breaker
        self.memory_bridge = AdvancedMemoryBridge()
        self.token_chunker = token_chunker
        self.agent_configs = self._load_agent_configs()
        
        logger.info("AdvancedStorytellerService inicializado com recursos premium:")
        logger.info("✓ Cache Redis para breakpoints calculados")
        logger.info("✓ TokenChunker para divisão precisa por tokens")
        logger.info("✓ SmartChapterBreaker para pontos naturais")
    
    def _load_agent_configs(self) -> Dict:
        """Carrega configurações por agente com suporte a tokens."""
        try:
            with open('config/agent_configs.json', 'r', encoding='utf-8') as f:
                return json.load(f)['agents']
        except FileNotFoundError:
            logger.warning("Arquivo agent_configs.json não encontrado, usando configurações avançadas")
            return {
                'millionaire_stories': {
                    'min_chars': 2000,
                    'max_chars': 3500,
                    'target_chars': 2800,
                    'target_tokens': 700,  # Novo: controle por tokens
                    'cliffhanger_prompt': 'Crie um gancho envolvente sobre superação financeira',
                    'break_patterns': ['superação', 'virada', 'decisão crucial']
                },
                'romance_agent': {
                    'min_chars': 1800,
                    'max_chars': 3200,
                    'target_chars': 2500,
                    'target_tokens': 625,
                    'cliffhanger_prompt': 'Desenvolva um momento de tensão romântica',
                    'break_patterns': ['revelação', 'encontro', 'dilema']
                },
                'horror_agent': {
                    'min_chars': 1500,
                    'max_chars': 2800,
                    'target_chars': 2200,
                    'target_tokens': 550,
                    'cliffhanger_prompt': 'Construa suspense e medo crescente',
                    'break_patterns': ['suspenso', 'terror', 'mistério']
                }
            }
    
    def generate_advanced_story_plan(self, total_chars: int, agent_type: str, 
                                   chapter_count: Optional[int] = None) -> Dict:
        """Gera plano de divisão inteligente com análise de tokens."""
        config = self.agent_configs.get(agent_type, self.agent_configs['millionaire_stories'])
        
        if chapter_count:
            target_per_chapter = total_chars // chapter_count
            target_tokens_per_chapter = config.get('target_tokens', 600)
        else:
            target_per_chapter = config['target_chars']
            target_tokens_per_chapter = config.get('target_tokens', 600)
            chapter_count = max(1, total_chars // target_per_chapter)
        
        return {
            'total_chapters': chapter_count,
            'target_per_chapter': target_per_chapter,
            'target_tokens_per_chapter': target_tokens_per_chapter,
            'min_per_chapter': config['min_chars'],
            'max_per_chapter': config['max_chars'],
            'agent_type': agent_type,
            'config': config,
            'advanced_features': {
                'smart_breaking': True,
                'token_chunking': True,
                'redis_caching': True
            }
        }
    
    def smart_split_content_advanced(self, content: str, plan: Dict, 
                                   story_id: str = None) -> List[Dict]:
        """Divide conteúdo usando recursos avançados: SmartChapterBreaker + TokenChunker + Cache."""
        if not story_id:
            story_id = hashlib.md5(content.encode()).hexdigest()[:8]
        
        logger.info(f"Iniciando divisão avançada para story_id: {story_id}")
        
        # 1. Verificar cache para breakpoints similares
        cached_breakpoints = self.memory_bridge.get_breakpoints(story_id)
        if cached_breakpoints:
            logger.info("Reutilizando breakpoints do cache")
            return self._create_chapters_from_cached_breakpoints(content, cached_breakpoints, plan, story_id)
        
        # 2. Buscar histórias similares para reutilização
        similar_stories = self.memory_bridge.find_similar_stories(content[:500], plan['agent_type'])
        if similar_stories:
            logger.info(f"Encontradas {len(similar_stories)} histórias similares")
            # Adaptar breakpoints similares (implementação simplificada)
            adapted_breakpoints = self._adapt_similar_breakpoints(content, similar_stories[0])
            if adapted_breakpoints:
                return self._create_chapters_from_breakpoints(content, adapted_breakpoints, plan, story_id)
        
        # 3. Usar SmartChapterBreaker para encontrar pontos naturais
        target_chapters = plan['total_chapters']
        min_distance = len(content) // (target_chapters * 2)  # Distância mínima entre quebras
        
        natural_breakpoints = self.chapter_breaker.find_natural_break_points(
            content, 
            target_count=target_chapters - 1,  # -1 porque não precisamos quebrar no final
            min_distance=min_distance
        )
        
        logger.info(f"SmartChapterBreaker encontrou {len(natural_breakpoints)} pontos naturais")
        
        # 4. Salvar breakpoints no cache para reutilização
        self.memory_bridge.save_breakpoints(story_id, natural_breakpoints)
        
        # 5. Criar capítulos usando os breakpoints naturais
        chapters = self._create_chapters_from_breakpoints(content, natural_breakpoints, plan, story_id)
        
        # 6. Aplicar TokenChunker se algum capítulo exceder limites
        optimized_chapters = self._optimize_chapters_with_tokens(chapters, plan)
        
        logger.info(f"Divisão avançada concluída: {len(optimized_chapters)} capítulos")
        return optimized_chapters
    
    def _create_chapters_from_breakpoints(self, content: str, breakpoints: List[BreakPoint], 
                                        plan: Dict, story_id: str) -> List[Dict]:
        """Cria capítulos a partir de breakpoints do SmartChapterBreaker."""
        chapters = []
        start_pos = 0
        
        # Ordenar breakpoints por posição
        sorted_breakpoints = sorted(breakpoints, key=lambda x: x.position)
        
        for i, breakpoint in enumerate(sorted_breakpoints):
            chapter_content = content[start_pos:breakpoint.position].strip()
            
            if chapter_content:
                # Validar capítulo
                validator = StoryValidator(plan['config'])
                validation = validator.validate_chapter(chapter_content, i + 1)
                
                # Salvar contexto
                context = {
                    'story_id': story_id,
                    'chapter_num': i + 1,
                    'content_preview': chapter_content[:200] + "...",
                    'length': len(chapter_content),
                    'break_info': {
                        'type': breakpoint.break_type.value,
                        'confidence': breakpoint.confidence,
                        'reason': breakpoint.reason
                    },
                    'created_at': datetime.now().isoformat()
                }
                self.memory_bridge.save_context(story_id, i + 1, context)
                
                chapters.append({
                    'number': i + 1,
                    'content': chapter_content,
                    'start_pos': start_pos,
                    'end_pos': breakpoint.position,
                    'validation': validation,
                    'cliffhanger': i < len(sorted_breakpoints) - 1,
                    'story_id': story_id,
                    'break_info': {
                        'type': breakpoint.break_type.value,
                        'confidence': breakpoint.confidence,
                        'narrative_score': breakpoint.narrative_score,
                        'reason': breakpoint.reason
                    },
                    'cached_context': context
                })
            
            start_pos = breakpoint.position
        
        # Último capítulo
        if start_pos < len(content):
            final_content = content[start_pos:].strip()
            if final_content:
                validator = StoryValidator(plan['config'])
                validation = validator.validate_chapter(final_content, len(chapters) + 1)
                
                context = {
                    'story_id': story_id,
                    'chapter_num': len(chapters) + 1,
                    'content_preview': final_content[:200] + "...",
                    'length': len(final_content),
                    'created_at': datetime.now().isoformat()
                }
                self.memory_bridge.save_context(story_id, len(chapters) + 1, context)
                
                chapters.append({
                    'number': len(chapters) + 1,
                    'content': final_content,
                    'start_pos': start_pos,
                    'end_pos': len(content),
                    'validation': validation,
                    'cliffhanger': False,
                    'story_id': story_id,
                    'break_info': None,  # Último capítulo
                    'cached_context': context
                })
        
        return chapters
    
    def _optimize_chapters_with_tokens(self, chapters: List[Dict], plan: Dict) -> List[Dict]:
        """Otimiza capítulos usando TokenChunker para controle granular."""
        target_tokens = plan.get('target_tokens_per_chapter', 600)
        optimized_chapters = []
        
        for chapter in chapters:
            content = chapter['content']
            token_count = self.token_chunker.count_tokens(content)
            
            # Se capítulo está dentro do limite, manter como está
            if token_count <= target_tokens * 1.2:  # 20% de tolerância
                optimized_chapters.append(chapter)
                continue
            
            # Se excede muito o limite, dividir usando TokenChunker
            logger.info(f"Capítulo {chapter['number']} excede tokens ({token_count}), dividindo...")
            
            chunks = self.token_chunker.chunk_text(content, target_tokens, tolerance=0.2)
            
            # Criar novos capítulos a partir dos chunks
            for i, chunk_info in enumerate(chunks):
                new_chapter = chapter.copy()
                new_chapter.update({
                    'number': len(optimized_chapters) + 1,
                    'content': chunk_info.text,
                    'validation': {
                        'valid': True,
                        'issues': [],
                        'length': len(chunk_info.text),
                        'token_count': chunk_info.token_count,
                        'quality_score': chunk_info.quality_score
                    },
                    'chunk_info': {
                        'original_chapter': chapter['number'],
                        'chunk_index': i + 1,
                        'total_chunks': len(chunks),
                        'token_count': chunk_info.token_count,
                        'sentence_count': chunk_info.sentence_count,
                        'quality_score': chunk_info.quality_score
                    }
                })
                optimized_chapters.append(new_chapter)
        
        return optimized_chapters
    
    def _create_chapters_from_cached_breakpoints(self, content: str, cached_breakpoints: List[Dict], 
                                               plan: Dict, story_id: str) -> List[Dict]:
        """Cria capítulos a partir de breakpoints em cache."""
        # Converter breakpoints do cache de volta para objetos
        breakpoints = []
        for bp_data in cached_breakpoints:
            # Simular BreakPoint a partir dos dados em cache
            breakpoints.append(type('BreakPoint', (), {
                'position': bp_data['position'],
                'break_type': type('BreakType', (), {'value': bp_data['break_type']})(),
                'confidence': bp_data['confidence'],
                'narrative_score': bp_data['narrative_score'],
                'reason': bp_data['reason']
            })())
        
        return self._create_chapters_from_breakpoints(content, breakpoints, plan, story_id)
    
    def _adapt_similar_breakpoints(self, content: str, similar_story: Dict) -> Optional[List[BreakPoint]]:
        """Adapta breakpoints de histórias similares para o conteúdo atual."""
        # Implementação simplificada - em produção seria mais sofisticada
        if not similar_story or 'breakpoints' not in similar_story:
            return None
        
        # Adaptar proporcionalmente os breakpoints
        content_length = len(content)
        similar_length = similar_story.get('content_length', content_length)
        
        if similar_length == 0:
            return None
        
        ratio = content_length / similar_length
        adapted_breakpoints = []
        
        for bp_data in similar_story['breakpoints']:
            adapted_position = int(bp_data['position'] * ratio)
            if 0 < adapted_position < content_length:
                # Criar BreakPoint adaptado
                adapted_bp = type('BreakPoint', (), {
                    'position': adapted_position,
                    'break_type': type('BreakType', (), {'value': bp_data['break_type']})(),
                    'confidence': bp_data['confidence'] * 0.8,  # Reduzir confiança
                    'narrative_score': bp_data['narrative_score'],
                    'reason': f"Adaptado de história similar: {bp_data['reason']}"
                })()
                adapted_breakpoints.append(adapted_bp)
        
        return adapted_breakpoints if adapted_breakpoints else None
    
    def get_advanced_stats(self, story_id: str) -> Dict:
        """Retorna estatísticas avançadas sobre uma história."""
        stats = {
            'cache_stats': self.memory_bridge.cache_service.get_cache_stats(),
            'story_contexts': [],
            'breakpoint_quality': None
        }
        
        # Recuperar contextos dos capítulos
        chapter_num = 1
        while True:
            context = self.memory_bridge.get_context(story_id, chapter_num)
            if not context:
                break
            stats['story_contexts'].append(context)
            chapter_num += 1
        
        # Recuperar qualidade dos breakpoints
        breakpoints = self.memory_bridge.get_breakpoints(story_id)
        if breakpoints:
            confidences = [bp['confidence'] for bp in breakpoints]
            stats['breakpoint_quality'] = {
                'total_breakpoints': len(breakpoints),
                'avg_confidence': sum(confidences) / len(confidences),
                'high_quality_count': len([c for c in confidences if c > 0.7]),
                'break_types': list(set(bp['break_type'] for bp in breakpoints))
            }
        
        return stats

# Instância global do serviço avançado
advanced_storyteller_service = AdvancedStorytellerService()