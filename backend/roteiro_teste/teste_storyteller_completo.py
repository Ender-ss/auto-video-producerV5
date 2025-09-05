#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Completo do Sistema StorytellerService
Testa geração de roteiro com 10 capítulos usando rotação de chaves Gemini
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.storyteller_service import storyteller_service
from routes.automations import get_next_gemini_key, get_gemini_keys_count

class StorytellerTester:
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'test_config': {
                'num_chapters': 10,
                'agent_type': 'millionaire_stories',
                'provider': 'gemini',
                'title': 'A Faxineira e o Segredo do Milionário',
                'premise': 'Uma faxineira humilde descobre um segredo que mudará sua vida para sempre quando encontra uma criança abandonada na mansão onde trabalha.'
            },
            'gemini_rotation': {
                'keys_used': [],
                'rotation_count': 0,
                'errors': []
            },
            'chapters_generated': [],
            'quality_analysis': {},
            'errors': [],
            'success': False,
            'execution_time': 0
        }
        
    def log_message(self, message, level='INFO'):
        """Log de mensagens com timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
        
    def test_gemini_rotation(self):
        """Testa o sistema de rotação de chaves Gemini"""
        self.log_message("Testando sistema de rotação de chaves Gemini...")
        
        try:
            # Verifica quantas chaves estão disponíveis
            keys_count = get_gemini_keys_count()
            self.log_message(f"Chaves Gemini disponíveis: {keys_count}")
            
            # Testa obtenção de chaves
            for i in range(3):
                key = get_next_gemini_key()
                if key:
                    self.test_results['gemini_rotation']['keys_used'].append(key[:10] + '...')
                    self.log_message(f"Chave {i+1} obtida: {key[:10]}...")
                else:
                    self.log_message("Erro ao obter chave Gemini", 'ERROR')
                    
            return True
            
        except Exception as e:
            self.log_message(f"Erro no teste de rotação: {str(e)}", 'ERROR')
            self.test_results['gemini_rotation']['errors'].append(str(e))
            return False
    
    def analyze_chapter_quality(self, chapter, chapter_num):
        """Analisa a qualidade de um capítulo"""
        analysis = {
            'chapter_number': chapter_num,
            'word_count': len(chapter.split()),
            'character_count': len(chapter),
            'has_dialogue': '"' in chapter or '"' in chapter or '"' in chapter,
            'has_narrative_flow': any(word in chapter.lower() for word in ['então', 'depois', 'enquanto', 'quando', 'mas', 'porém', 'entretanto']),
            'emotional_content': any(word in chapter.lower() for word in ['lágrimas', 'sorriso', 'medo', 'alegria', 'tristeza', 'amor', 'raiva']),
            'descriptive_content': any(word in chapter.lower() for word in ['olhos', 'rosto', 'casa', 'quarto', 'porta', 'janela']),
            'quality_score': 0
        }
        
        # Calcula score de qualidade
        score = 0
        if analysis['word_count'] >= 200: score += 2
        if analysis['has_dialogue']: score += 2
        if analysis['has_narrative_flow']: score += 2
        if analysis['emotional_content']: score += 2
        if analysis['descriptive_content']: score += 2
        
        analysis['quality_score'] = score
        return analysis
    
    def progress_callback(self, chapter_num, total_chapters, chapter_content):
        """Callback de progresso da geração"""
        self.log_message(f"Capítulo {chapter_num}/{total_chapters} gerado ({len(chapter_content)} caracteres)")
        
        # Analisa qualidade do capítulo
        quality = self.analyze_chapter_quality(chapter_content, chapter_num)
        self.test_results['chapters_generated'].append({
            'chapter_num': chapter_num,
            'content': chapter_content,
            'quality': quality
        })
        
    def run_storyteller_test(self):
        """Executa o teste principal do StorytellerService"""
        self.log_message("Iniciando teste do StorytellerService...")
        
        try:
            start_time = time.time()
            
            # Configuração do teste
            config = self.test_results['test_config']
            
            self.log_message(f"Configuração: {config['num_chapters']} capítulos, agente: {config['agent_type']}")
            self.log_message(f"Título: {config['title']}")
            self.log_message(f"Premissa: {config['premise']}")
            
            # Gera o roteiro
            result = storyteller_service.generate_storyteller_script(
                title=config['title'],
                premise=config['premise'],
                agent_type=config['agent_type'],
                num_chapters=config['num_chapters'],
                provider=config['provider'],
                progress_callback=self.progress_callback
            )
            
            end_time = time.time()
            self.test_results['execution_time'] = end_time - start_time
            
            if result and 'full_script' in result:
                self.log_message(f"Roteiro gerado com sucesso! ({len(result['full_script'])} caracteres)")
                self.test_results['success'] = True
                self.test_results['full_script'] = result['full_script']
                self.test_results['script_metadata'] = result.get('metadata', {})
                
                # Salva o roteiro gerado
                self.save_generated_script(result['full_script'])
                
                return True
            else:
                self.log_message("Falha na geração do roteiro", 'ERROR')
                self.test_results['errors'].append("Roteiro não foi gerado")
                return False
                
        except Exception as e:
            self.log_message(f"Erro durante teste: {str(e)}", 'ERROR')
            self.test_results['errors'].append(str(e))
            return False
    
    def save_generated_script(self, script_content):
        """Salva o roteiro gerado"""
        timestamp = self.test_results['timestamp']
        filename = f"roteiro_gerado_{timestamp}.txt"
        filepath = Path(__file__).parent / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(script_content)
            self.log_message(f"Roteiro salvo em: {filepath}")
        except Exception as e:
            self.log_message(f"Erro ao salvar roteiro: {str(e)}", 'ERROR')
    
    def analyze_overall_quality(self):
        """Analisa a qualidade geral do roteiro"""
        if not self.test_results['chapters_generated']:
            return
            
        chapters = self.test_results['chapters_generated']
        
        # Estatísticas gerais
        total_words = sum(ch['quality']['word_count'] for ch in chapters)
        total_chars = sum(ch['quality']['character_count'] for ch in chapters)
        avg_quality_score = sum(ch['quality']['quality_score'] for ch in chapters) / len(chapters)
        
        # Análise de fluidez
        has_good_flow = all(ch['quality']['has_narrative_flow'] for ch in chapters)
        has_emotional_depth = sum(1 for ch in chapters if ch['quality']['emotional_content']) >= len(chapters) * 0.7
        has_dialogue_variety = sum(1 for ch in chapters if ch['quality']['has_dialogue']) >= len(chapters) * 0.6
        
        self.test_results['quality_analysis'] = {
            'total_words': total_words,
            'total_characters': total_chars,
            'average_words_per_chapter': total_words / len(chapters),
            'average_quality_score': avg_quality_score,
            'narrative_flow_consistency': has_good_flow,
            'emotional_depth_coverage': has_emotional_depth,
            'dialogue_variety': has_dialogue_variety,
            'overall_rating': 'EXCELENTE' if avg_quality_score >= 8 else 'BOM' if avg_quality_score >= 6 else 'REGULAR' if avg_quality_score >= 4 else 'RUIM'
        }
    
    def generate_report(self):
        """Gera relatório completo do teste"""
        self.analyze_overall_quality()
        
        timestamp = self.test_results['timestamp']
        report_filename = f"relatorio_teste_storyteller_{timestamp}.json"
        report_filepath = Path(__file__).parent / report_filename
        
        # Salva relatório JSON
        try:
            with open(report_filepath, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            self.log_message(f"Relatório JSON salvo em: {report_filepath}")
        except Exception as e:
            self.log_message(f"Erro ao salvar relatório JSON: {str(e)}", 'ERROR')
        
        # Gera relatório texto
        text_report = self.generate_text_report()
        text_filename = f"relatorio_teste_storyteller_{timestamp}.txt"
        text_filepath = Path(__file__).parent / text_filename
        
        try:
            with open(text_filepath, 'w', encoding='utf-8') as f:
                f.write(text_report)
            self.log_message(f"Relatório texto salvo em: {text_filepath}")
        except Exception as e:
            self.log_message(f"Erro ao salvar relatório texto: {str(e)}", 'ERROR')
            
        return text_report
    
    def generate_text_report(self):
        """Gera relatório em formato texto"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO COMPLETO - TESTE STORYTELLER SERVICE")
        report.append("=" * 80)
        report.append(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report.append(f"Timestamp: {self.test_results['timestamp']}")
        report.append("")
        
        # Configuração do teste
        config = self.test_results['test_config']
        report.append("CONFIGURAÇÃO DO TESTE:")
        report.append("-" * 40)
        report.append(f"Número de Capítulos: {config['num_chapters']}")
        report.append(f"Tipo de Agente: {config['agent_type']}")
        report.append(f"Provider: {config['provider']}")
        report.append(f"Título: {config['title']}")
        report.append(f"Premissa: {config['premise']}")
        report.append("")
        
        # Status do teste
        report.append("STATUS DO TESTE:")
        report.append("-" * 40)
        report.append(f"Sucesso: {'✓ SIM' if self.test_results['success'] else '✗ NÃO'}")
        report.append(f"Tempo de Execução: {self.test_results['execution_time']:.2f} segundos")
        report.append(f"Capítulos Gerados: {len(self.test_results['chapters_generated'])}")
        report.append("")
        
        # Rotação de chaves
        rotation = self.test_results['gemini_rotation']
        report.append("SISTEMA DE ROTAÇÃO GEMINI:")
        report.append("-" * 40)
        report.append(f"Chaves Utilizadas: {len(rotation['keys_used'])}")
        for i, key in enumerate(rotation['keys_used'], 1):
            report.append(f"  {i}. {key}")
        if rotation['errors']:
            report.append("Erros de Rotação:")
            for error in rotation['errors']:
                report.append(f"  - {error}")
        report.append("")
        
        # Análise de qualidade
        if 'quality_analysis' in self.test_results:
            qa = self.test_results['quality_analysis']
            report.append("ANÁLISE DE QUALIDADE:")
            report.append("-" * 40)
            report.append(f"Total de Palavras: {qa.get('total_words', 'N/A')}")
            report.append(f"Total de Caracteres: {qa.get('total_characters', 'N/A')}")
            report.append(f"Média de Palavras por Capítulo: {qa.get('average_words_per_chapter', 'N/A')}")
            report.append(f"Score Médio de Qualidade: {qa.get('average_quality_score', 'N/A')}/10")
            report.append(f"Fluidez Narrativa: {'✓' if qa.get('narrative_flow_consistency', False) else '✗'}")
            report.append(f"Profundidade Emocional: {'✓' if qa.get('emotional_depth_coverage', False) else '✗'}")
            report.append(f"Variedade de Diálogos: {'✓' if qa.get('dialogue_variety', False) else '✗'}")
            report.append(f"Avaliação Geral: {qa.get('overall_rating', 'N/A')}")
            report.append("")
        
        # Detalhes dos capítulos
        if self.test_results['chapters_generated']:
            report.append("DETALHES DOS CAPÍTULOS:")
            report.append("-" * 40)
            for chapter in self.test_results['chapters_generated']:
                q = chapter['quality']
                report.append(f"Capítulo {q['chapter_number']}:")
                report.append(f"  Palavras: {q['word_count']} | Caracteres: {q['character_count']}")
                report.append(f"  Diálogo: {'✓' if q['has_dialogue'] else '✗'} | Fluidez: {'✓' if q['has_narrative_flow'] else '✗'}")
                report.append(f"  Emoção: {'✓' if q['emotional_content'] else '✗'} | Descrição: {'✓' if q['descriptive_content'] else '✗'}")
                report.append(f"  Score: {q['quality_score']}/10")
                report.append("")
        
        # Erros
        if self.test_results['errors']:
            report.append("ERROS ENCONTRADOS:")
            report.append("-" * 40)
            for error in self.test_results['errors']:
                report.append(f"- {error}")
            report.append("")
        
        # Conclusões e recomendações
        report.append("CONCLUSÕES E RECOMENDAÇÕES:")
        report.append("-" * 40)
        
        if self.test_results['success']:
            report.append("✓ O sistema StorytellerService está funcionando corretamente")
            report.append("✓ A rotação de chaves Gemini está operacional")
            report.append("✓ Os capítulos foram gerados com sucesso")
            
            if 'quality_analysis' in self.test_results:
                qa = self.test_results['quality_analysis']
                if qa.get('overall_rating', '') in ['EXCELENTE', 'BOM']:
                    report.append("✓ A qualidade do roteiro está satisfatória")
                else:
                    report.append("⚠ A qualidade do roteiro pode ser melhorada")
                    report.append("  Recomendações:")
                    if not qa['narrative_flow_consistency']:
                        report.append("  - Melhorar conectores narrativos entre capítulos")
                    if not qa['emotional_depth_coverage']:
                        report.append("  - Adicionar mais conteúdo emocional")
                    if not qa['dialogue_variety']:
                        report.append("  - Incluir mais diálogos nos capítulos")
        else:
            report.append("✗ O teste falhou - investigação necessária")
            report.append("  Possíveis causas:")
            report.append("  - Problemas com as chaves da API Gemini")
            report.append("  - Erros na configuração do StorytellerService")
            report.append("  - Problemas de conectividade")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def run_complete_test(self):
        """Executa o teste completo"""
        self.log_message("=" * 60)
        self.log_message("INICIANDO TESTE COMPLETO DO STORYTELLER SERVICE")
        self.log_message("=" * 60)
        
        # Teste 1: Rotação de chaves
        self.log_message("\n[FASE 1] Testando rotação de chaves Gemini...")
        rotation_ok = self.test_gemini_rotation()
        
        # Teste 2: Geração de roteiro
        self.log_message("\n[FASE 2] Testando geração de roteiro...")
        generation_ok = self.run_storyteller_test()
        
        # Gera relatório
        self.log_message("\n[FASE 3] Gerando relatório...")
        report = self.generate_report()
        
        # Exibe resumo
        self.log_message("\n" + "=" * 60)
        self.log_message("RESUMO DO TESTE")
        self.log_message("=" * 60)
        self.log_message(f"Rotação de Chaves: {'✓ OK' if rotation_ok else '✗ FALHA'}")
        self.log_message(f"Geração de Roteiro: {'✓ OK' if generation_ok else '✗ FALHA'}")
        self.log_message(f"Status Geral: {'✓ SUCESSO' if self.test_results['success'] else '✗ FALHA'}")
        
        if 'quality_analysis' in self.test_results:
            qa = self.test_results['quality_analysis']
            self.log_message(f"Qualidade: {qa['overall_rating']} ({qa['average_quality_score']:.1f}/10)")
        
        return report

def main():
    """Função principal"""
    tester = StorytellerTester()
    report = tester.run_complete_test()
    
    print("\n" + "=" * 80)
    print("RELATÓRIO COMPLETO:")
    print("=" * 80)
    print(report)
    
    return tester.test_results['success']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)