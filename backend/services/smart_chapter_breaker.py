import re
import logging
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BreakType(Enum):
    """Tipos de quebras narrativas."""
    SCENE_CHANGE = "scene_change"  # Mudança de cenário
    TIME_JUMP = "time_jump"        # Salto temporal
    POV_SHIFT = "pov_shift"        # Mudança de perspectiva
    DIALOGUE_END = "dialogue_end"  # Final de diálogo importante
    ACTION_PEAK = "action_peak"    # Pico de ação/tensão
    REFLECTION = "reflection"      # Momento de reflexão
    TRANSITION = "transition"      # Transição narrativa

@dataclass
class BreakPoint:
    """Informações sobre um ponto de quebra narrativo."""
    position: int
    break_type: BreakType
    confidence: float
    context_before: str
    context_after: str
    narrative_score: float
    transition_quality: str
    reason: str

class SmartChapterBreaker:
    """
    Identificador inteligente de pontos naturais para quebra de capítulos.
    Analisa estrutura narrativa para encontrar transições fluidas.
    """
    
    def __init__(self):
        """Inicializa o SmartChapterBreaker com padrões narrativos."""
        
        # Padrões para mudanças de cenário
        self.scene_patterns = [
            r'\b(chegou|chegaram|entrou|entraram|saiu|saíram)\s+(em|no|na|para|de)\b',
            r'\b(casa|escritório|escola|hospital|restaurante|parque|rua|cidade)\b',
            r'\b(manhã|tarde|noite|madrugada)\s+(seguinte|anterior|de)\b',
            r'\b(dentro|fora|longe|perto)\s+(de|da|do)\b'
        ]
        
        # Padrões para saltos temporais
        self.time_patterns = [
            r'\b(depois|após|antes|durante)\s+(de|da|do)?\s*(alguns?|muitos?|várias?)\s*(dias?|semanas?|meses?|anos?)\b',
            r'\b(na|no)\s+(próxima?|seguinte|anterior)\s+(semana|mês|ano|dia)\b',
            r'\b(horas?|minutos?)\s+(depois|mais tarde|antes)\b',
            r'\b(ontem|hoje|amanhã|anteontem)\b',
            r'\b(enquanto isso|nesse meio tempo|simultaneamente)\b'
        ]
        
        # Padrões para mudança de perspectiva
        self.pov_patterns = [
            r'\b(enquanto|ao mesmo tempo)\s+.{0,50}\s+(ele|ela|eles|elas)\b',
            r'\b(do outro lado|em outro lugar|longe dali)\b',
            r'\b(pensou|refletiu|lembrou|imaginou)\s+(ele|ela)\b',
            r'\b(na perspectiva|do ponto de vista)\s+de\b'
        ]
        
        # Padrões para finais de diálogo
        self.dialogue_patterns = [
            r'["\'][^"\']*[.!?]["\']\\s*[,.]?\\s*(disse|falou|respondeu|perguntou|gritou|sussurrou)',
            r'(disse|falou|respondeu|perguntou|gritou|sussurrou)[^.!?]*[.!?]\s*$',
            r'["\'][^"\']*[.!?]["\']\\s*$'
        ]
        
        # Padrões para picos de ação
        self.action_patterns = [
            r'\b(correu|gritou|pulou|caiu|bateu|explodiu|quebrou)\b',
            r'\b(subitamente|de repente|inesperadamente|rapidamente)\b',
            r'\b(perigo|medo|terror|pânico|desespero)\b',
            r'[!]{2,}|[.]{3,}'
        ]
        
        # Padrões para reflexão
        self.reflection_patterns = [
            r'\b(pensou|refletiu|considerou|ponderou|meditou)\b',
            r'\b(lembrou|recordou|relembrou)\s+(de|que)\b',
            r'\b(percebia|sentia|sabia|entendia)\s+que\b',
            r'\b(talvez|provavelmente|possivelmente|certamente)\b'
        ]
        
        # Padrões para transições
        self.transition_patterns = [
            r'\b(então|assim|portanto|consequentemente|por isso)\b',
            r'\b(finalmente|enfim|por fim|ao final)\b',
            r'\b(primeiro|segundo|terceiro|último|final)\b',
            r'\b(começou|iniciou|terminou|acabou|concluiu)\b'
        ]
        
        # Compilar padrões para eficiência
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compila todos os padrões regex para melhor performance."""
        self.compiled_patterns = {
            BreakType.SCENE_CHANGE: [re.compile(p, re.IGNORECASE) for p in self.scene_patterns],
            BreakType.TIME_JUMP: [re.compile(p, re.IGNORECASE) for p in self.time_patterns],
            BreakType.POV_SHIFT: [re.compile(p, re.IGNORECASE) for p in self.pov_patterns],
            BreakType.DIALOGUE_END: [re.compile(p, re.IGNORECASE) for p in self.dialogue_patterns],
            BreakType.ACTION_PEAK: [re.compile(p, re.IGNORECASE) for p in self.action_patterns],
            BreakType.REFLECTION: [re.compile(p, re.IGNORECASE) for p in self.reflection_patterns],
            BreakType.TRANSITION: [re.compile(p, re.IGNORECASE) for p in self.transition_patterns]
        }
    
    def find_sentence_boundaries(self, text: str) -> List[int]:
        """Encontra limites de sentenças no texto."""
        sentence_pattern = re.compile(r'[.!?]+\s+')
        boundaries = []
        
        for match in sentence_pattern.finditer(text):
            boundaries.append(match.end())
        
        if not boundaries or boundaries[-1] < len(text):
            boundaries.append(len(text))
        
        return boundaries
    
    def analyze_narrative_patterns(self, text: str, position: int, 
                                 context_size: int = 200) -> Dict[BreakType, float]:
        """
        Analisa padrões narrativos em torno de uma posição.
        
        Args:
            text: Texto completo
            position: Posição para análise
            context_size: Tamanho do contexto para análise
            
        Returns:
            Dicionário com scores para cada tipo de quebra
        """
        start = max(0, position - context_size)
        end = min(len(text), position + context_size)
        context = text[start:end]
        
        scores = {}
        
        for break_type, patterns in self.compiled_patterns.items():
            score = 0.0
            matches = 0
            
            for pattern in patterns:
                pattern_matches = pattern.findall(context)
                matches += len(pattern_matches)
                
                # Score baseado na proximidade da posição
                for match in pattern.finditer(context):
                    match_pos = start + match.start()
                    distance = abs(match_pos - position)
                    proximity_score = max(0, 1 - (distance / context_size))
                    score += proximity_score
            
            # Normaliza score
            if matches > 0:
                score = score / matches
            
            scores[break_type] = min(1.0, score)
        
        return scores
    
    def calculate_transition_quality(self, text: str, position: int) -> Tuple[float, str]:
        """
        Calcula qualidade da transição em uma posição.
        
        Args:
            text: Texto completo
            position: Posição da quebra
            
        Returns:
            Tuple com score de qualidade e descrição
        """
        if position <= 0 or position >= len(text):
            return 0.0, "Posição inválida"
        
        context_before = text[max(0, position-100):position]
        context_after = text[position:min(len(text), position+100)]
        
        quality = 0.0
        reasons = []
        
        # Verifica final de parágrafo
        if context_before.strip().endswith('\n') or '\n\n' in context_before[-10:]:
            quality += 0.3
            reasons.append("quebra de parágrafo")
        
        # Verifica pontuação final
        if context_before.strip().endswith(('.', '!', '?')):
            quality += 0.2
            reasons.append("pontuação final")
        
        # Verifica início de novo parágrafo
        if context_after.strip().startswith('\n') or context_after.startswith('    '):
            quality += 0.2
            reasons.append("início de parágrafo")
        
        # Penaliza quebra no meio de diálogo
        dialogue_before = context_before.count('"') + context_before.count('"') + context_before.count('"')
        dialogue_after = context_after.count('"') + context_after.count('"') + context_after.count('"')
        
        if dialogue_before % 2 != 0:  # Diálogo aberto
            quality -= 0.4
            reasons.append("meio de diálogo")
        
        # Verifica continuidade de frase
        if context_before.strip().endswith(',') or context_after.strip().startswith(('e', 'mas', 'porém', 'contudo')):
            quality -= 0.3
            reasons.append("continuidade de frase")
        
        quality = max(0.0, min(1.0, quality))
        description = ", ".join(reasons) if reasons else "transição neutra"
        
        return quality, description
    
    def find_natural_break_points(self, text: str, target_count: int = 10, 
                                min_distance: int = 500) -> List[BreakPoint]:
        """
        Encontra pontos naturais para quebra de capítulos.
        
        Args:
            text: Texto para análise
            target_count: Número alvo de pontos de quebra
            min_distance: Distância mínima entre quebras
            
        Returns:
            Lista de BreakPoint ordenada por qualidade
        """
        if not text.strip():
            return []
        
        sentence_boundaries = self.find_sentence_boundaries(text)
        candidates = []
        
        for boundary in sentence_boundaries:
            if boundary < min_distance or boundary > len(text) - min_distance:
                continue
            
            # Analisa padrões narrativos
            pattern_scores = self.analyze_narrative_patterns(text, boundary)
            
            # Calcula qualidade da transição
            transition_quality, transition_desc = self.calculate_transition_quality(text, boundary)
            
            # Determina tipo de quebra dominante
            best_type = max(pattern_scores.items(), key=lambda x: x[1])
            break_type = best_type[0]
            pattern_confidence = best_type[1]
            
            # Score narrativo combinado
            narrative_score = sum(pattern_scores.values()) / len(pattern_scores)
            
            # Score final combina padrões narrativos e qualidade de transição
            final_confidence = (pattern_confidence * 0.6) + (transition_quality * 0.4)
            
            # Contexto para análise
            context_before = text[max(0, boundary-50):boundary]
            context_after = text[boundary:min(len(text), boundary+50)]
            
            # Razão da quebra
            reason = f"Padrão {break_type.value} detectado com {transition_desc}"
            
            break_point = BreakPoint(
                position=boundary,
                break_type=break_type,
                confidence=final_confidence,
                context_before=context_before.strip(),
                context_after=context_after.strip(),
                narrative_score=narrative_score,
                transition_quality=transition_desc,
                reason=reason
            )
            
            candidates.append(break_point)
        
        # Ordena por confiança
        candidates.sort(key=lambda x: x.confidence, reverse=True)
        
        # Filtra por distância mínima
        selected = []
        for candidate in candidates:
            if len(selected) >= target_count:
                break
            
            # Verifica distância mínima dos já selecionados
            too_close = False
            for selected_point in selected:
                if abs(candidate.position - selected_point.position) < min_distance:
                    too_close = True
                    break
            
            if not too_close:
                selected.append(candidate)
        
        # Ordena por posição
        selected.sort(key=lambda x: x.position)
        
        return selected
    
    def create_chapters(self, text: str, break_points: List[BreakPoint]) -> List[Dict[str, any]]:
        """
        Cria capítulos baseados nos pontos de quebra.
        
        Args:
            text: Texto completo
            break_points: Pontos de quebra identificados
            
        Returns:
            Lista de capítulos com metadados
        """
        if not break_points:
            return [{
                'chapter_number': 1,
                'content': text,
                'start_pos': 0,
                'end_pos': len(text),
                'word_count': len(text.split()),
                'break_info': None
            }]
        
        chapters = []
        start_pos = 0
        
        for i, break_point in enumerate(break_points):
            chapter_content = text[start_pos:break_point.position].strip()
            
            if chapter_content:
                chapters.append({
                    'chapter_number': len(chapters) + 1,
                    'content': chapter_content,
                    'start_pos': start_pos,
                    'end_pos': break_point.position,
                    'word_count': len(chapter_content.split()),
                    'break_info': {
                        'type': break_point.break_type.value,
                        'confidence': break_point.confidence,
                        'reason': break_point.reason,
                        'transition_quality': break_point.transition_quality
                    }
                })
            
            start_pos = break_point.position
        
        # Último capítulo
        if start_pos < len(text):
            final_content = text[start_pos:].strip()
            if final_content:
                chapters.append({
                    'chapter_number': len(chapters) + 1,
                    'content': final_content,
                    'start_pos': start_pos,
                    'end_pos': len(text),
                    'word_count': len(final_content.split()),
                    'break_info': None  # Último capítulo
                })
        
        return chapters
    
    def get_breaking_stats(self, break_points: List[BreakPoint]) -> Dict[str, any]:
        """
        Retorna estatísticas sobre os pontos de quebra.
        
        Args:
            break_points: Lista de pontos de quebra
            
        Returns:
            Dicionário com estatísticas
        """
        if not break_points:
            return {}
        
        type_counts = {}
        confidences = []
        narrative_scores = []
        
        for bp in break_points:
            type_counts[bp.break_type.value] = type_counts.get(bp.break_type.value, 0) + 1
            confidences.append(bp.confidence)
            narrative_scores.append(bp.narrative_score)
        
        return {
            'total_break_points': len(break_points),
            'break_types': type_counts,
            'avg_confidence': sum(confidences) / len(confidences),
            'min_confidence': min(confidences),
            'max_confidence': max(confidences),
            'avg_narrative_score': sum(narrative_scores) / len(narrative_scores),
            'high_quality_breaks': len([bp for bp in break_points if bp.confidence > 0.7]),
            'medium_quality_breaks': len([bp for bp in break_points if 0.4 <= bp.confidence <= 0.7]),
            'low_quality_breaks': len([bp for bp in break_points if bp.confidence < 0.4])
        }

# Instância global do chapter breaker
smart_chapter_breaker = SmartChapterBreaker()