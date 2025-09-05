import re
import tiktoken
from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ChunkInfo:
    """Informações sobre um chunk de texto."""
    text: str
    start_pos: int
    end_pos: int
    token_count: int
    sentence_count: int
    paragraph_count: int
    quality_score: float

class TokenChunker:
    """
    Divisor de texto baseado em tokens com controle granular.
    Garante divisões precisas respeitando limites de tokens e contexto narrativo.
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Inicializa o TokenChunker.
        
        Args:
            model_name: Nome do modelo para contagem de tokens
        """
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback para encoding padrão
            self.encoding = tiktoken.get_encoding("cl100k_base")
            logger.warning(f"Modelo {model_name} não encontrado, usando encoding padrão")
        
        # Padrões para identificação de estruturas textuais
        self.sentence_endings = re.compile(r'[.!?]+\s+')
        self.paragraph_breaks = re.compile(r'\n\s*\n')
        self.dialogue_markers = re.compile(r'["\"\"\"\'\'\']')
        self.narrative_transitions = re.compile(r'\b(então|depois|em seguida|posteriormente|mais tarde|enquanto isso|nesse momento)\b', re.IGNORECASE)
    
    def count_tokens(self, text: str) -> int:
        """
        Conta tokens no texto.
        
        Args:
            text: Texto para contar tokens
            
        Returns:
            Número de tokens
        """
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.error(f"Erro ao contar tokens: {e}")
            # Fallback: estimativa baseada em palavras
            return len(text.split()) * 1.3
    
    def find_sentence_boundaries(self, text: str) -> List[int]:
        """
        Encontra limites de sentenças no texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Lista de posições dos finais de sentenças
        """
        boundaries = []
        for match in self.sentence_endings.finditer(text):
            boundaries.append(match.end())
        
        # Adiciona final do texto se não termina com pontuação
        if not boundaries or boundaries[-1] < len(text):
            boundaries.append(len(text))
        
        return boundaries
    
    def find_paragraph_boundaries(self, text: str) -> List[int]:
        """
        Encontra limites de parágrafos no texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Lista de posições dos finais de parágrafos
        """
        boundaries = []
        for match in self.paragraph_breaks.finditer(text):
            boundaries.append(match.start())
        
        return boundaries
    
    def calculate_break_quality(self, text: str, break_pos: int) -> float:
        """
        Calcula qualidade de um ponto de quebra (0-1, maior é melhor).
        
        Args:
            text: Texto completo
            break_pos: Posição da quebra
            
        Returns:
            Score de qualidade da quebra
        """
        if break_pos <= 0 or break_pos >= len(text):
            return 0.0
        
        quality = 0.0
        context_before = text[max(0, break_pos-100):break_pos]
        context_after = text[break_pos:min(len(text), break_pos+100)]
        
        # Pontuação: quebra após pontuação final
        if context_before.strip().endswith(('.', '!', '?')):
            quality += 0.4
        
        # Parágrafo: quebra entre parágrafos
        if '\n\n' in context_before[-10:] or '\n\n' in context_after[:10]:
            quality += 0.3
        
        # Diálogo: evita quebrar no meio de diálogos
        dialogue_count_before = len(self.dialogue_markers.findall(context_before))
        dialogue_count_after = len(self.dialogue_markers.findall(context_after))
        if dialogue_count_before % 2 == 0:  # Diálogo fechado
            quality += 0.2
        else:
            quality -= 0.3  # Penaliza quebra no meio de diálogo
        
        # Transição narrativa: favorece quebras após transições
        if self.narrative_transitions.search(context_before):
            quality += 0.1
        
        return min(1.0, max(0.0, quality))
    
    def find_optimal_break_points(self, text: str, target_tokens: int, 
                                 tolerance: float = 0.1) -> List[int]:
        """
        Encontra pontos ótimos de quebra baseados em tokens e qualidade.
        
        Args:
            text: Texto para dividir
            target_tokens: Número alvo de tokens por chunk
            tolerance: Tolerância para variação de tokens (10% por padrão)
            
        Returns:
            Lista de posições ótimas para quebra
        """
        if not text.strip():
            return []
        
        total_tokens = self.count_tokens(text)
        if total_tokens <= target_tokens:
            return [len(text)]  # Texto já é pequeno o suficiente
        
        break_points = []
        current_pos = 0
        min_tokens = int(target_tokens * (1 - tolerance))
        max_tokens = int(target_tokens * (1 + tolerance))
        
        while current_pos < len(text):
            # Encontra posição aproximada baseada em tokens
            remaining_text = text[current_pos:]
            
            # Estimativa inicial baseada em proporção
            estimated_pos = int(len(remaining_text) * (target_tokens / self.count_tokens(remaining_text)))
            estimated_pos = min(estimated_pos, len(remaining_text))
            
            # Busca melhor ponto de quebra na região alvo
            search_start = max(0, int(estimated_pos * 0.8))
            search_end = min(len(remaining_text), int(estimated_pos * 1.2))
            
            best_pos = estimated_pos
            best_quality = 0.0
            
            # Avalia pontos de quebra candidatos
            sentence_boundaries = self.find_sentence_boundaries(remaining_text[search_start:search_end])
            
            for boundary in sentence_boundaries:
                candidate_pos = search_start + boundary
                if candidate_pos > len(remaining_text):
                    break
                
                # Verifica se está dentro dos limites de tokens
                chunk_text = remaining_text[:candidate_pos]
                chunk_tokens = self.count_tokens(chunk_text)
                
                if min_tokens <= chunk_tokens <= max_tokens:
                    quality = self.calculate_break_quality(remaining_text, candidate_pos)
                    if quality > best_quality:
                        best_pos = candidate_pos
                        best_quality = quality
            
            # Se não encontrou ponto ideal, usa estimativa
            if best_quality == 0.0:
                # Busca pelo menos uma quebra de sentença próxima
                all_sentences = self.find_sentence_boundaries(remaining_text)
                for boundary in all_sentences:
                    if boundary >= search_start:
                        best_pos = boundary
                        break
            
            next_break = current_pos + best_pos
            if next_break >= len(text):
                break
            
            break_points.append(next_break)
            current_pos = next_break
        
        return break_points
    
    def chunk_text(self, text: str, target_tokens: int, 
                   tolerance: float = 0.1) -> List[ChunkInfo]:
        """
        Divide texto em chunks com informações detalhadas.
        
        Args:
            text: Texto para dividir
            target_tokens: Número alvo de tokens por chunk
            tolerance: Tolerância para variação de tokens
            
        Returns:
            Lista de ChunkInfo com informações detalhadas
        """
        if not text.strip():
            return []
        
        break_points = self.find_optimal_break_points(text, target_tokens, tolerance)
        chunks = []
        
        start_pos = 0
        for i, break_point in enumerate(break_points + [len(text)]):
            if break_point <= start_pos:
                continue
            
            chunk_text = text[start_pos:break_point].strip()
            if not chunk_text:
                start_pos = break_point
                continue
            
            # Calcula métricas do chunk
            token_count = self.count_tokens(chunk_text)
            sentence_count = len(self.find_sentence_boundaries(chunk_text))
            paragraph_count = len(self.find_paragraph_boundaries(chunk_text)) + 1
            
            # Calcula score de qualidade
            quality_score = 1.0
            if i < len(break_points):
                quality_score = self.calculate_break_quality(text, break_point)
            
            chunk_info = ChunkInfo(
                text=chunk_text,
                start_pos=start_pos,
                end_pos=break_point,
                token_count=token_count,
                sentence_count=sentence_count,
                paragraph_count=paragraph_count,
                quality_score=quality_score
            )
            
            chunks.append(chunk_info)
            start_pos = break_point
        
        return chunks
    
    def get_chunking_stats(self, chunks: List[ChunkInfo]) -> Dict[str, any]:
        """
        Retorna estatísticas sobre os chunks criados.
        
        Args:
            chunks: Lista de chunks
            
        Returns:
            Dicionário com estatísticas
        """
        if not chunks:
            return {}
        
        token_counts = [chunk.token_count for chunk in chunks]
        quality_scores = [chunk.quality_score for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'total_tokens': sum(token_counts),
            'avg_tokens_per_chunk': sum(token_counts) / len(chunks),
            'min_tokens': min(token_counts),
            'max_tokens': max(token_counts),
            'avg_quality_score': sum(quality_scores) / len(quality_scores),
            'min_quality_score': min(quality_scores),
            'max_quality_score': max(quality_scores),
            'total_sentences': sum(chunk.sentence_count for chunk in chunks),
            'total_paragraphs': sum(chunk.paragraph_count for chunk in chunks)
        }

# Instância global do chunker
token_chunker = TokenChunker()