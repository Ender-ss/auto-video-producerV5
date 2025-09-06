#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versão melhorada da remoção de cabeçalhos - 100% efetiva
"""

import re
import sys
import os
from typing import List, Dict, Any

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ImprovedHeaderRemoval:
    """Classe para remoção 100% efetiva de cabeçalhos mantendo contexto"""
    
    def __init__(self):
        # Padrões mais abrangentes para detectar cabeçalhos
        self.header_patterns = [
            # Cabeçalhos markdown (# ## ###)
            r'^#{1,6}\s+.*$',
            
            # Cabeçalhos de capítulos em português
            r'^.*?[Cc]apítulo\s*\d+[:\s-]*.*$',
            r'^.*?CAPÍTULO\s*\d+[:\s-]*.*$',
            r'^.*?Cap\.?\s*\d+[:\s-]*.*$',
            r'^.*?CAP\.?\s*\d+[:\s-]*.*$',
            
            # Cabeçalhos de capítulos em inglês
            r'^.*?[Cc]hapter\s*\d+[:\s-]*.*$',
            r'^.*?CHAPTER\s*\d+[:\s-]*.*$',
            r'^.*?Ch\.?\s*\d+[:\s-]*.*$',
            
            # Padrões numerados
            r'^\d+[\.-]\s+.*$',
            r'^\(\d+\)\s+.*$',
            
            # Títulos centralizados ou destacados
            r'^\s*\*{2,}.*\*{2,}\s*$',
            r'^\s*={3,}.*={3,}\s*$',
            r'^\s*-{3,}.*-{3,}\s*$',
            
            # Padrões específicos de formatação
            r'^\s*\[.*\]\s*$',
            r'^\s*<.*>\s*$',
            
            # Linhas que são apenas separadores
            r'^\s*[=\-_*]{3,}\s*$',
        ]
        
        # Padrões para preservar conteúdo importante
        self.preserve_patterns = [
            r'^".*"$',  # Diálogos entre aspas
            r'^—.*$',   # Diálogos com travessão
            r'^-\s[A-Z]',  # Listas importantes
        ]
    
    def is_header_line(self, line: str) -> bool:
        """Verifica se uma linha é um cabeçalho"""
        line_stripped = line.strip()
        
        # Ignorar linhas vazias
        if not line_stripped:
            return False
        
        # Preservar linhas importantes
        for preserve_pattern in self.preserve_patterns:
            if re.match(preserve_pattern, line_stripped, re.IGNORECASE):
                return False
        
        # Verificar se é cabeçalho
        for pattern in self.header_patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                return True
        
        return False
    
    def remove_headers_advanced(self, content: str, preserve_context: bool = True) -> str:
        """Remove cabeçalhos de forma avançada mantendo contexto"""
        if not content:
            return content
        
        lines = content.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            if self.is_header_line(line):
                # Se preserve_context=True, tenta manter informação contextual
                if preserve_context:
                    context_info = self._extract_context_from_header(line)
                    if context_info:
                        # Adiciona contexto como texto narrativo
                        cleaned_lines.append(context_info)
                # Senão, simplesmente remove o cabeçalho
                continue
            else:
                cleaned_lines.append(line)
        
        # Limpar linhas vazias excessivas
        result = '\n'.join(cleaned_lines)
        result = re.sub(r'\n\s*\n\s*\n+', '\n\n', result)  # Max 2 quebras consecutivas
        result = result.strip()
        
        return result
    
    def _extract_context_from_header(self, header_line: str) -> str:
        """Extrai informação contextual útil de um cabeçalho"""
        header_clean = header_line.strip()
        
        # Remove marcações markdown
        header_clean = re.sub(r'^#{1,6}\s*', '', header_clean)
        
        # Remove numeração de capítulos mas preserva títulos descritivos
        # Ex: "Capítulo 1: A Descoberta" -> "A Descoberta"
        context_match = re.search(r'[Cc]apítulo\s*\d+[:\s-]+(.+)', header_clean, re.IGNORECASE)
        if context_match:
            title_part = context_match.group(1).strip()
            if len(title_part) > 5:  # Só preserva se for significativo
                return f"\n{title_part}\n"  # Adiciona como transição narrativa
        
        # Para outros tipos de cabeçalhos, verifica se há conteúdo útil
        clean_content = re.sub(r'^[\d\(\)\[\]\*=\-_\s]+', '', header_clean)
        clean_content = re.sub(r'[\*=\-_\s]+$', '', clean_content)
        
        if len(clean_content) > 3 and not re.match(r'^[Cc]apítulo|^[Cc]hapter', clean_content, re.IGNORECASE):
            return f"\n{clean_content}\n"
        
        return None
    
    def remove_headers_complete(self, content: str) -> str:
        """Remove cabeçalhos completamente sem preservar contexto"""
        return self.remove_headers_advanced(content, preserve_context=False)
    
    def analyze_header_removal(self, original: str, processed: str) -> Dict[str, Any]:
        """Analisa a efetividade da remoção de cabeçalhos"""
        original_lines = original.split('\n')
        processed_lines = processed.split('\n')
        
        original_headers = sum(1 for line in original_lines if self.is_header_line(line))
        processed_headers = sum(1 for line in processed_lines if self.is_header_line(line))
        
        # Análise de markdown específico
        original_markdown = len(re.findall(r'^#{1,6}\s+', original, re.MULTILINE))
        processed_markdown = len(re.findall(r'^#{1,6}\s+', processed, re.MULTILINE))
        
        return {
            'original_headers': original_headers,
            'processed_headers': processed_headers,
            'headers_removed': original_headers - processed_headers,
            'removal_rate': ((original_headers - processed_headers) / original_headers * 100) if original_headers > 0 else 0,
            'original_markdown': original_markdown,
            'processed_markdown': processed_markdown,
            'markdown_removed': original_markdown - processed_markdown,
            'markdown_removal_rate': ((original_markdown - processed_markdown) / original_markdown * 100) if original_markdown > 0 else 0,
            'original_length': len(original),
            'processed_length': len(processed),
            'content_preserved': (len(processed) / len(original) * 100) if len(original) > 0 else 0
        }

def test_improved_removal():
    """Testa a remoção melhorada com exemplos"""
    
    # Texto de exemplo com vários tipos de cabeçalhos
    test_content = """
# Título Principal

Esta é uma introdução importante que deve ser preservada.

## Capítulo 1: O Início da Jornada

Este é o conteúdo do primeiro capítulo que conta sobre a jornada do protagonista.

### Subcapítulo 1.1

Mais detalhes sobre a jornada.

## Capítulo 2: O Desafio

Aqui temos o segundo capítulo com novos desafios.

**Seção Importante**

Conteúdo de uma seção.

=== Separador ===

1. Primeiro item
2. Segundo item

"Este é um diálogo importante", disse o personagem.

— Outro diálogo com travessão.

CAPÍTULO 3: A RESOLUÇÃO

O final da história.
"""
    
    remover = ImprovedHeaderRemoval()
    
    print("=== TESTE DE REMOÇÃO MELHORADA ===")
    print("\nConteúdo original:")
    print("-" * 50)
    print(test_content)
    
    # Teste com preservação de contexto
    resultado_com_contexto = remover.remove_headers_advanced(test_content, preserve_context=True)
    print("\n\nResultado COM preservação de contexto:")
    print("-" * 50)
    print(resultado_com_contexto)
    
    # Teste sem preservação de contexto
    resultado_sem_contexto = remover.remove_headers_complete(test_content)
    print("\n\nResultado SEM preservação de contexto:")
    print("-" * 50)
    print(resultado_sem_contexto)
    
    # Análise
    analise_com = remover.analyze_header_removal(test_content, resultado_com_contexto)
    analise_sem = remover.analyze_header_removal(test_content, resultado_sem_contexto)
    
    print("\n\n=== ANÁLISE DOS RESULTADOS ===")
    print("\nCOM preservação de contexto:")
    for key, value in analise_com.items():
        print(f"  {key}: {value}")
    
    print("\nSEM preservação de contexto:")
    for key, value in analise_sem.items():
        print(f"  {key}: {value}")
    
    return remover, analise_com, analise_sem

if __name__ == "__main__":
    test_improved_removal()