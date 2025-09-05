import redis
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RedisCacheService:
    """
    Serviço de cache Redis para breakpoints calculados e outros dados do Storyteller.
    Permite reutilização eficiente de breakpoints similares entre roteiros.
    """
    
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        """
        Inicializa conexão com Redis.
        
        Args:
            host: Host do Redis
            port: Porta do Redis
            db: Número do banco de dados
            password: Senha do Redis (opcional)
        """
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Testa conexão
            self.redis_client.ping()
            self.connected = True
            logger.info("Conexão Redis estabelecida com sucesso")
        except Exception as e:
            logger.warning(f"Redis não disponível, usando cache em memória: {e}")
            self.connected = False
            self._memory_cache = {}
    
    def _generate_cache_key(self, content: str, chapter_count: int, agent_type: str = "") -> str:
        """
        Gera chave única para cache baseada no conteúdo e parâmetros.
        
        Args:
            content: Conteúdo do roteiro
            chapter_count: Número de capítulos
            agent_type: Tipo do agente (opcional)
            
        Returns:
            Chave única para cache
        """
        # Cria hash do conteúdo para chave única
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
        return f"breakpoints:{agent_type}:{chapter_count}:{content_hash}"
    
    def get_breakpoints(self, content: str, chapter_count: int, agent_type: str = "") -> Optional[List[int]]:
        """
        Recupera breakpoints do cache.
        
        Args:
            content: Conteúdo do roteiro
            chapter_count: Número de capítulos
            agent_type: Tipo do agente
            
        Returns:
            Lista de breakpoints ou None se não encontrado
        """
        cache_key = self._generate_cache_key(content, chapter_count, agent_type)
        
        try:
            if self.connected:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    logger.info(f"Breakpoints recuperados do cache Redis: {cache_key}")
                    return data.get('breakpoints')
            else:
                # Cache em memória como fallback
                if cache_key in self._memory_cache:
                    data = self._memory_cache[cache_key]
                    # Verifica se não expirou (1 hora)
                    if datetime.now() - data['timestamp'] < timedelta(hours=1):
                        logger.info(f"Breakpoints recuperados do cache em memória: {cache_key}")
                        return data['breakpoints']
                    else:
                        del self._memory_cache[cache_key]
        except Exception as e:
            logger.error(f"Erro ao recuperar breakpoints do cache: {e}")
        
        return None
    
    def set_breakpoints(self, content: str, chapter_count: int, breakpoints: List[int], 
                       agent_type: str = "", ttl: int = 3600) -> bool:
        """
        Armazena breakpoints no cache.
        
        Args:
            content: Conteúdo do roteiro
            chapter_count: Número de capítulos
            breakpoints: Lista de breakpoints
            agent_type: Tipo do agente
            ttl: Tempo de vida em segundos (padrão: 1 hora)
            
        Returns:
            True se armazenado com sucesso
        """
        cache_key = self._generate_cache_key(content, chapter_count, agent_type)
        
        cache_data = {
            'breakpoints': breakpoints,
            'chapter_count': chapter_count,
            'agent_type': agent_type,
            'created_at': datetime.now().isoformat(),
            'content_length': len(content)
        }
        
        try:
            if self.connected:
                self.redis_client.setex(
                    cache_key, 
                    ttl, 
                    json.dumps(cache_data)
                )
                logger.info(f"Breakpoints armazenados no cache Redis: {cache_key}")
            else:
                # Cache em memória como fallback
                self._memory_cache[cache_key] = {
                    'breakpoints': breakpoints,
                    'timestamp': datetime.now()
                }
                logger.info(f"Breakpoints armazenados no cache em memória: {cache_key}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao armazenar breakpoints no cache: {e}")
            return False
    
    def get_similar_breakpoints(self, content_length: int, chapter_count: int, 
                               agent_type: str = "", similarity_threshold: float = 0.1) -> Optional[List[int]]:
        """
        Busca breakpoints similares baseado no tamanho do conteúdo.
        
        Args:
            content_length: Tamanho do conteúdo
            chapter_count: Número de capítulos
            agent_type: Tipo do agente
            similarity_threshold: Threshold de similaridade (10% por padrão)
            
        Returns:
            Lista de breakpoints similares ou None
        """
        try:
            if self.connected:
                # Busca todas as chaves de breakpoints do mesmo tipo
                pattern = f"breakpoints:{agent_type}:{chapter_count}:*"
                keys = self.redis_client.keys(pattern)
                
                for key in keys:
                    cached_data = self.redis_client.get(key)
                    if cached_data:
                        data = json.loads(cached_data)
                        cached_length = data.get('content_length', 0)
                        
                        # Verifica similaridade de tamanho
                        if cached_length > 0:
                            similarity = abs(content_length - cached_length) / max(content_length, cached_length)
                            if similarity <= similarity_threshold:
                                logger.info(f"Breakpoints similares encontrados: {key} (similaridade: {1-similarity:.2%})")
                                return data.get('breakpoints')
            
        except Exception as e:
            logger.error(f"Erro ao buscar breakpoints similares: {e}")
        
        return None
    
    def clear_cache(self, pattern: str = "breakpoints:*") -> int:
        """
        Limpa cache baseado em padrão.
        
        Args:
            pattern: Padrão para limpeza
            
        Returns:
            Número de chaves removidas
        """
        try:
            if self.connected:
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted = self.redis_client.delete(*keys)
                    logger.info(f"Cache limpo: {deleted} chaves removidas")
                    return deleted
            else:
                # Limpa cache em memória
                keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith("breakpoints:")]
                for key in keys_to_delete:
                    del self._memory_cache[key]
                logger.info(f"Cache em memória limpo: {len(keys_to_delete)} chaves removidas")
                return len(keys_to_delete)
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
        
        return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache.
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {
            'connected': self.connected,
            'type': 'Redis' if self.connected else 'Memory',
            'breakpoint_keys': 0
        }
        
        try:
            if self.connected:
                keys = self.redis_client.keys("breakpoints:*")
                stats['breakpoint_keys'] = len(keys)
                stats['redis_info'] = {
                    'used_memory': self.redis_client.info().get('used_memory_human', 'N/A'),
                    'connected_clients': self.redis_client.info().get('connected_clients', 0)
                }
            else:
                breakpoint_keys = [k for k in self._memory_cache.keys() if k.startswith("breakpoints:")]
                stats['breakpoint_keys'] = len(breakpoint_keys)
                stats['memory_keys'] = len(self._memory_cache)
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do cache: {e}")
        
        return stats

# Instância global do serviço de cache
cache_service = RedisCacheService()