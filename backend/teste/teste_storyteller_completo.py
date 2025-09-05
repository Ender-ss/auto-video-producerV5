#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Completo do Sistema Storyteller Unlimited
Gera roteiro de 10 capítulos usando o sistema implementado
Analisa fluidez narrativa e performance
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Adiciona o diretório backend ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.storyteller_service import storyteller_service
import services.ai_services as ai_services

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('teste_storyteller.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StorytellerTester:
    """Classe para testar o sistema Storyteller completo"""
    
    def __init__(self):
        self.storyteller = storyteller_service
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'test_config': {},
            'execution_results': {},
            'narrative_analysis': {},
            'performance_metrics': {},
            'errors': [],
            'success': False
        }
        
    def setup_test_config(self):
        """Configura parâmetros do teste"""
        self.test_config = {
            'title': 'A Faxineira e o Segredo do Milionário',
            'premise': '''Uma faxineira humilde precisa levar seu filho doente ao trabalho na mansão de um milionário. 
            Quando o patrão descobre a criança, fica em choque ao reconhecer uma marca de nascença idêntica à de sua ex-namorada. 
            Ele percebe que pode ser o pai da criança e decide ajudar, mas descobre segredos familiares que mudarão suas vidas para sempre. 
            Uma história de superação, amor perdido, responsabilidade paterna e a descoberta de que o dinheiro não compra a felicidade, 
            mas pode ser usado para fazer o bem.''',
            'agent_type': 'millionaire_stories',
            'num_chapters': 10,
            'provider': 'gemini',
            'target_narrative_style': 'fluido_emocional_detalhado'
        }
        
        self.test_results['test_config'] = self.test_config
        logger.info(f"Configuração do teste: {self.test_config}")
        
    def load_api_keys(self):
        """Carrega chaves da API do arquivo de configuração"""
        try:
            config_path = Path('../config/api_keys.json')
            if not config_path.exists():
                # Tenta caminho alternativo
                config_path = Path('config/api_keys.json')
                
            with open(config_path, 'r', encoding='utf-8') as f:
                api_config = json.load(f)
                
            # Extrai chaves Gemini do formato atual
            gemini_keys = []
            for key, value in api_config.items():
                if key.startswith('gemini_') and value:
                    gemini_keys.append(value)
            
            if not gemini_keys:
                raise ValueError("Nenhuma chave Gemini encontrada")
                
            logger.info(f"Carregadas {len(gemini_keys)} chaves Gemini")
            return gemini_keys
            
        except Exception as e:
            error_msg = f"Erro ao carregar chaves da API: {e}"
            logger.error(error_msg)
            self.test_results['errors'].append(error_msg)
            return []
    
    def execute_storyteller_generation(self):
        """Executa a geração do roteiro usando o Storyteller"""
        logger.info("🚀 Iniciando geração do roteiro com Storyteller...")
        
        start_time = time.time()
        
        try:
            # Carrega chaves da API
            api_keys = self.load_api_keys()
            if not api_keys:
                raise ValueError("Nenhuma chave API disponível")
            
            # Usa primeira chave disponível
            api_key = api_keys[0]
            
            # Gera o roteiro usando o storyteller service
            result = self.storyteller.generate_storyteller_script(
                title=self.test_config['title'],
                premise=self.test_config['premise'],
                agent_type=self.test_config['agent_type'],
                num_chapters=self.test_config['num_chapters'],
                api_key=api_key,
                provider=self.test_config['provider']
            )
            
            execution_time = time.time() - start_time
            
            # Salva resultados
            self.test_results['execution_results'] = {
                'success': True,
                'execution_time': execution_time,
                'total_chapters': len(result.get('chapters', [])),
                'total_characters': len(result.get('full_script', '')),
                'script_data': result
            }
            
            logger.info(f"✅ Roteiro gerado com sucesso em {execution_time:.2f}s")
            logger.info(f"📊 {len(result.get('chapters', []))} capítulos, {len(result.get('full_script', ''))} caracteres")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Erro na geração do roteiro: {str(e)}"
            logger.error(error_msg)
            
            self.test_results['execution_results'] = {
                'success': False,
                'execution_time': execution_time,
                'error': error_msg
            }
            self.test_results['errors'].append(error_msg)
            
            return None
    
    def analyze_narrative_quality(self, script_result):
        """Analisa a qualidade narrativa do roteiro gerado"""
        logger.info("📝 Analisando qualidade narrativa...")
        
        if not script_result:
            self.test_results['narrative_analysis'] = {
                'success': False,
                'error': 'Nenhum roteiro para analisar'
            }
            return
        
        try:
            full_script = script_result.get('full_script', '')
            chapters = script_result.get('chapters', [])
            
            # Análise básica de estrutura
            analysis = {
                'total_words': len(full_script.split()),
                'total_characters': len(full_script),
                'chapter_count': len(chapters),
                'average_chapter_length': 0,
                'narrative_flow_indicators': {},
                'dialogue_presence': False,
                'emotional_depth_indicators': {},
                'structural_quality': {}
            }
            
            if chapters:
                chapter_lengths = [len(ch.get('content', '')) for ch in chapters]
                analysis['average_chapter_length'] = sum(chapter_lengths) / len(chapter_lengths)
                analysis['chapter_length_variance'] = max(chapter_lengths) - min(chapter_lengths)
            
            # Verifica fluidez narrativa
            narrative_indicators = {
                'dialogue_count': full_script.count('"'),
                'paragraph_breaks': full_script.count('\n\n'),
                'emotional_words': sum(1 for word in ['coração', 'lágrimas', 'emoção', 'sentimento', 'amor', 'medo', 'alegria'] 
                                     if word.lower() in full_script.lower()),
                'transition_words': sum(1 for word in ['então', 'depois', 'enquanto', 'quando', 'mas', 'porém', 'entretanto'] 
                                      if word.lower() in full_script.lower())
            }
            
            analysis['narrative_flow_indicators'] = narrative_indicators
            analysis['dialogue_presence'] = narrative_indicators['dialogue_count'] > 20
            
            # Análise de profundidade emocional
            emotional_indicators = {
                'descriptive_passages': full_script.count('.') - full_script.count('...'),
                'internal_thoughts': full_script.lower().count('pensou') + full_script.lower().count('refletiu'),
                'sensory_descriptions': sum(1 for word in ['viu', 'ouviu', 'sentiu', 'tocou', 'cheiro'] 
                                          if word.lower() in full_script.lower())
            }
            
            analysis['emotional_depth_indicators'] = emotional_indicators
            
            # Avaliação estrutural
            structural_quality = {
                'has_introduction': len(chapters) > 0 and len(chapters[0].get('content', '')) > 500,
                'has_development': len(chapters) > 5,
                'has_climax': len(chapters) > 7,
                'has_resolution': len(chapters) == self.test_config['num_chapters']
            }
            
            analysis['structural_quality'] = structural_quality
            
            # Calcula score geral
            quality_score = 0
            if analysis['dialogue_presence']: quality_score += 20
            if narrative_indicators['emotional_words'] > 10: quality_score += 20
            if narrative_indicators['transition_words'] > 15: quality_score += 20
            if all(structural_quality.values()): quality_score += 25
            if analysis['average_chapter_length'] > 1500: quality_score += 15
            
            analysis['overall_quality_score'] = quality_score
            analysis['quality_rating'] = (
                'Excelente' if quality_score >= 80 else
                'Bom' if quality_score >= 60 else
                'Regular' if quality_score >= 40 else
                'Precisa Melhorar'
            )
            
            self.test_results['narrative_analysis'] = analysis
            
            logger.info(f"📊 Análise concluída - Score: {quality_score}/100 ({analysis['quality_rating']})")
            
        except Exception as e:
            error_msg = f"Erro na análise narrativa: {str(e)}"
            logger.error(error_msg)
            self.test_results['narrative_analysis'] = {
                'success': False,
                'error': error_msg
            }
            self.test_results['errors'].append(error_msg)
    
    def save_generated_script(self, script_result):
        """Salva o roteiro gerado em arquivo"""
        if not script_result:
            return None
            
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'roteiro_storyteller_{timestamp}.txt'
            filepath = Path(filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {script_result.get('title', 'Roteiro Gerado')}\n\n")
                f.write(f"**Premissa:** {script_result.get('premise', '')}\n\n")
                f.write(f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
                f.write(f"**Sistema:** Storyteller Unlimited\n\n")
                f.write("=" * 80 + "\n\n")
                
                # Escreve roteiro completo
                full_script = script_result.get('full_script', '')
                if full_script:
                    f.write(full_script)
                else:
                    # Se não tiver script completo, monta dos capítulos
                    chapters = script_result.get('chapters', [])
                    for i, chapter in enumerate(chapters, 1):
                        f.write(f"\n\n## CAPÍTULO {i}\n\n")
                        f.write(chapter.get('content', ''))
                
                f.write("\n\n" + "=" * 80)
                f.write(f"\n\n**Estatísticas:**\n")
                f.write(f"- Total de capítulos: {len(script_result.get('chapters', []))}\n")
                f.write(f"- Total de caracteres: {len(full_script)}\n")
                f.write(f"- Palavras aproximadas: {len(full_script.split())}\n")
            
            logger.info(f"💾 Roteiro salvo em: {filepath.absolute()}")
            return str(filepath.absolute())
            
        except Exception as e:
            error_msg = f"Erro ao salvar roteiro: {str(e)}"
            logger.error(error_msg)
            self.test_results['errors'].append(error_msg)
            return None
    
    def generate_test_report(self):
        """Gera relatório completo do teste"""
        logger.info("📋 Gerando relatório do teste...")
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_filename = f'relatorio_teste_storyteller_{timestamp}.json'
            
            # Determina sucesso geral
            execution_success = self.test_results['execution_results'].get('success', False)
            narrative_quality = self.test_results.get('narrative_analysis', {}).get('overall_quality_score', 0)
            
            self.test_results['success'] = execution_success and narrative_quality >= 60
            
            # Adiciona resumo executivo
            self.test_results['executive_summary'] = {
                'test_passed': self.test_results['success'],
                'execution_successful': execution_success,
                'narrative_quality_score': narrative_quality,
                'total_errors': len(self.test_results['errors']),
                'recommendations': self._generate_recommendations()
            }
            
            # Salva relatório JSON
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            
            # Gera relatório em texto legível
            text_report = self._generate_text_report()
            text_filename = f'relatorio_teste_storyteller_{timestamp}.txt'
            
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(text_report)
            
            logger.info(f"📊 Relatório salvo em: {report_filename} e {text_filename}")
            
            return {
                'json_report': report_filename,
                'text_report': text_filename,
                'success': self.test_results['success']
            }
            
        except Exception as e:
            error_msg = f"Erro ao gerar relatório: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg}
    
    def _generate_recommendations(self):
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        execution_results = self.test_results.get('execution_results', {})
        narrative_analysis = self.test_results.get('narrative_analysis', {})
        
        if not execution_results.get('success', False):
            recommendations.append("Verificar configuração das chaves API do Gemini")
            recommendations.append("Validar conectividade com serviços de IA")
            recommendations.append("Revisar logs de erro para problemas específicos")
        
        quality_score = narrative_analysis.get('overall_quality_score', 0)
        if quality_score < 60:
            recommendations.append("Melhorar prompts para maior profundidade narrativa")
            recommendations.append("Ajustar configurações de capítulos por agente")
            
        if narrative_analysis.get('average_chapter_length', 0) < 1500:
            recommendations.append("Aumentar tamanho mínimo de capítulos")
            
        if not narrative_analysis.get('dialogue_presence', False):
            recommendations.append("Incluir mais diálogos nos prompts de geração")
        
        if len(self.test_results.get('errors', [])) > 0:
            recommendations.append("Implementar tratamento de erro mais robusto")
        
        return recommendations
    
    def _generate_text_report(self):
        """Gera relatório em formato texto legível"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE TESTE - STORYTELLER UNLIMITED")
        report.append("=" * 80)
        report.append(f"Data/Hora: {self.test_results['timestamp']}")
        report.append(f"Status Geral: {'✅ SUCESSO' if self.test_results['success'] else '❌ FALHA'}")
        report.append("")
        
        # Configuração do teste
        report.append("📋 CONFIGURAÇÃO DO TESTE")
        report.append("-" * 40)
        config = self.test_results['test_config']
        report.append(f"Título: {config.get('title', 'N/A')}")
        report.append(f"Agente: {config.get('agent_type', 'N/A')}")
        report.append(f"Capítulos: {config.get('num_chapters', 'N/A')}")
        report.append(f"Provedor: {config.get('provider', 'N/A')}")
        report.append("")
        
        # Resultados da execução
        report.append("🚀 RESULTADOS DA EXECUÇÃO")
        report.append("-" * 40)
        exec_results = self.test_results.get('execution_results', {})
        report.append(f"Sucesso: {'Sim' if exec_results.get('success') else 'Não'}")
        report.append(f"Tempo de execução: {exec_results.get('execution_time', 0):.2f}s")
        report.append(f"Capítulos gerados: {exec_results.get('total_chapters', 0)}")
        report.append(f"Caracteres totais: {exec_results.get('total_characters', 0)}")
        report.append("")
        
        # Análise narrativa
        report.append("📝 ANÁLISE NARRATIVA")
        report.append("-" * 40)
        narrative = self.test_results.get('narrative_analysis', {})
        report.append(f"Score de qualidade: {narrative.get('overall_quality_score', 0)}/100")
        report.append(f"Avaliação: {narrative.get('quality_rating', 'N/A')}")
        report.append(f"Palavras totais: {narrative.get('total_words', 0)}")
        report.append(f"Tamanho médio por capítulo: {narrative.get('average_chapter_length', 0):.0f} chars")
        report.append(f"Presença de diálogos: {'Sim' if narrative.get('dialogue_presence') else 'Não'}")
        report.append("")
        
        # Erros
        if self.test_results.get('errors'):
            report.append("❌ ERROS ENCONTRADOS")
            report.append("-" * 40)
            for i, error in enumerate(self.test_results['errors'], 1):
                report.append(f"{i}. {error}")
            report.append("")
        
        # Recomendações
        recommendations = self.test_results.get('executive_summary', {}).get('recommendations', [])
        if recommendations:
            report.append("💡 RECOMENDAÇÕES")
            report.append("-" * 40)
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def run_complete_test(self):
        """Executa o teste completo do Storyteller"""
        logger.info("🎬 Iniciando teste completo do Storyteller Unlimited")
        
        try:
            # 1. Configuração
            self.setup_test_config()
            
            # 2. Execução
            script_result = self.execute_storyteller_generation()
            
            # 3. Análise
            self.analyze_narrative_quality(script_result)
            
            # 4. Salvamento
            script_file = self.save_generated_script(script_result)
            
            # 5. Relatório
            report_info = self.generate_test_report()
            
            # Log final
            if self.test_results['success']:
                logger.info("🎉 Teste concluído com SUCESSO!")
            else:
                logger.warning("⚠️ Teste concluído com PROBLEMAS")
            
            return {
                'success': self.test_results['success'],
                'script_file': script_file,
                'report_files': report_info,
                'test_results': self.test_results
            }
            
        except Exception as e:
            error_msg = f"Erro crítico no teste: {str(e)}"
            logger.error(error_msg)
            self.test_results['errors'].append(error_msg)
            self.test_results['success'] = False
            
            return {
                'success': False,
                'error': error_msg,
                'test_results': self.test_results
            }

def main():
    """Função principal"""
    print("🎬 TESTE STORYTELLER UNLIMITED")
    print("=" * 50)
    
    tester = StorytellerTester()
    results = tester.run_complete_test()
    
    print("\n" + "=" * 50)
    if results['success']:
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print(f"📄 Roteiro salvo: {results.get('script_file', 'N/A')}")
    else:
        print("❌ TESTE FALHOU!")
        print(f"🔍 Erro: {results.get('error', 'Verifique os logs')}")
    
    print(f"📊 Relatórios: {results.get('report_files', {})}")
    print("=" * 50)
    
    return results

if __name__ == "__main__":
    main()