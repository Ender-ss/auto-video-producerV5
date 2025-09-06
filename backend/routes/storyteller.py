from flask import Blueprint, request, jsonify
from services.storyteller_service import storyteller_service
from services.storyteller_service_advanced import advanced_storyteller_service
import logging

logger = logging.getLogger(__name__)
storyteller_bp = Blueprint('storyteller', __name__, url_prefix='/api/storyteller')

@storyteller_bp.route('/generate-plan', methods=['POST'])
def generate_story_plan():
    """Gera plano de divisão inteligente com recursos avançados"""
    try:
        data = request.json
        total_chars = data.get('total_chars', 20000)
        agent_type = data.get('agent_type', 'millionaire_stories')
        chapter_count = data.get('chapter_count')
        use_advanced = data.get('use_advanced', True)  # Usar recursos avançados por padrão
        
        if use_advanced:
            plan = advanced_storyteller_service.generate_advanced_story_plan(
                total_chars=total_chars,
                agent_type=agent_type,
                chapter_count=chapter_count
            )
        else:
            plan = storyteller_service.generate_story_plan(
                total_chars=total_chars,
                agent_type=agent_type,
                chapter_count=chapter_count
            )
        
        return jsonify({
            'success': True,
            'plan': plan,
            'advanced_features_used': use_advanced,
            'message': 'Plano gerado com sucesso' + (' (recursos avançados)' if use_advanced else '')
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar plano: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao gerar plano de história'
        }), 500

@storyteller_bp.route('/split-content', methods=['POST'])
def split_content():
    """Divide conteúdo em capítulos inteligentes com recursos avançados"""
    try:
        data = request.json
        content = data.get('content', '')
        agent_type = data.get('agent_type', 'millionaire_stories')
        chapter_count = data.get('chapter_count')
        story_id = data.get('story_id')
        use_advanced = data.get('use_advanced', True)  # Usar recursos avançados por padrão
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Conteúdo é obrigatório',
                'message': 'Por favor, forneça o conteúdo a ser dividido'
            }), 400
        
        if use_advanced:
            # Usar serviço avançado
            plan = advanced_storyteller_service.generate_advanced_story_plan(
                total_chars=len(content),
                agent_type=agent_type,
                chapter_count=chapter_count
            )
            
            chapters = advanced_storyteller_service.smart_split_content_advanced(
                content=content,
                plan=plan,
                story_id=story_id
            )
            
            cache_hit = bool(advanced_storyteller_service.memory_bridge.get_breakpoints(story_id))
        else:
            # Usar serviço tradicional
            plan = storyteller_service.generate_story_plan(
                total_chars=len(content),
                agent_type=agent_type,
                chapter_count=chapter_count
            )
            
            chapters = storyteller_service.smart_split_content(
                content=content,
                plan=plan,
                story_id=story_id
            )
            
            cache_hit = bool(storyteller_service.memory_bridge.get_breakpoints(story_id))
        
        return jsonify({
            'success': True,
            'chapters': chapters,
            'plan': plan,
            'cache_hit': cache_hit,
            'advanced_features_used': use_advanced,
            'features_info': {
                'redis_cache': use_advanced,
                'token_chunker': use_advanced,
                'smart_chapter_breaker': use_advanced
            } if use_advanced else None,
            'message': f'Conteúdo dividido em {len(chapters)} capítulos' + (' (recursos avançados)' if use_advanced else '')
        })
        
    except Exception as e:
        logger.error(f"Erro ao dividir conteúdo: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao dividir conteúdo em capítulos'
        }), 500

@storyteller_bp.route('/validate-chapter', methods=['POST'])
def validate_chapter():
    """Valida um capítulo individual"""
    try:
        data = request.json
        chapter_content = data.get('chapter_content', '')
        chapter_num = data.get('chapter_num', 1)
        agent_type = data.get('agent_type', 'millionaire_stories')
        
        config = storyteller_service.agent_configs.get(
            agent_type, 
            storyteller_service.agent_configs['millionaire_stories']
        )
        
        from services.storyteller_service import StoryValidator
        from services.storyteller_service_advanced import StoryValidator as AdvancedStoryValidator
        
        use_advanced = data.get('use_advanced', True)
        
        if use_advanced:
            validator = AdvancedStoryValidator(config)
        else:
            validator = StoryValidator(config)
            
        validation = validator.validate_chapter(chapter_content, chapter_num)
        
        return jsonify({
            'success': True,
            'validation': validation,
            'message': 'Capítulo validado com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao validar capítulo: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao validar capítulo'
        }), 500

@storyteller_bp.route('/cache/context/<story_id>/<int:chapter_num>', methods=['GET'])
def get_cached_context(story_id, chapter_num):
    """Recupera contexto cacheado de um capítulo"""
    try:
        context = storyteller_service.memory_bridge.get_context(story_id, chapter_num)
        
        if context:
            return jsonify({
                'success': True,
                'context': context,
                'cached': True
            })
        else:
            return jsonify({
                'success': True,
                'context': None,
                'cached': False,
                'message': 'Contexto não encontrado no cache'
            })
            
    except Exception as e:
        logger.error(f"Erro ao recuperar contexto: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao recuperar contexto do cache'
        }), 500

@storyteller_bp.route('/cache/breakpoints/<story_id>', methods=['GET'])
def get_cached_breakpoints(story_id):
    """Recupera breakpoints cacheados de uma história"""
    try:
        breakpoints = storyteller_service.memory_bridge.get_breakpoints(story_id)
        
        if breakpoints:
            return jsonify({
                'success': True,
                'breakpoints': breakpoints,
                'cached': True
            })
        else:
            return jsonify({
                'success': True,
                'breakpoints': None,
                'cached': False,
                'message': 'Breakpoints não encontrados no cache'
            })
            
    except Exception as e:
        logger.error(f"Erro ao recuperar breakpoints: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao recuperar breakpoints do cache'
        }), 500

@storyteller_bp.route('/agents', methods=['GET'])
def get_agents():
    """Retorna lista de agentes disponíveis"""
    try:
        agents = []
        for key, config in storyteller_service.agent_configs.items():
            agents.append({
                'id': key,
                'name': config['name'],
                'min_chars': config['min_chars'],
                'max_chars': config['max_chars'],
                'target_chars': config['target_chars'],
                'story_types': config['story_types']
            })
        
        return jsonify({
            'success': True,
            'agents': agents,
            'message': f'{len(agents)} agentes disponíveis'
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar agentes: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao listar agentes'
        }), 500

@storyteller_bp.route('/generate-script', methods=['POST'])
def generate_storyteller_script():
    """Gera roteiro completo usando Storyteller Unlimited para integração com pipeline"""
    try:
        data = request.json
        
        # Validar dados obrigatórios
        title = data.get('title', '').strip()
        premise = data.get('premise', '').strip()
        agent_type = data.get('agent_type', 'millionaire_stories')
        num_chapters = data.get('num_chapters', 10)
        
        if not title:
            return jsonify({
                'success': False,
                'error': 'Título é obrigatório',
                'message': 'Por favor, forneça um título para a história'
            }), 400
            
        if not premise:
            return jsonify({
                'success': False,
                'error': 'Premissa é obrigatória',
                'message': 'Por favor, forneça uma premissa para a história'
            }), 400
            
        # Validar número de capítulos
        if not isinstance(num_chapters, int) or num_chapters < 1 or num_chapters > 50:
            return jsonify({
                'success': False,
                'error': 'Número de capítulos inválido',
                'message': 'O número de capítulos deve ser entre 1 e 50'
            }), 400
            
        # Validar agent_type
        if agent_type not in storyteller_service.agent_configs:
            return jsonify({
                'success': False,
                'error': 'Tipo de agente inválido',
                'message': f'Agente "{agent_type}" não é válido. Use um dos agentes disponíveis.'
            }), 400
        
        # Extrair parâmetro de remoção de cabeçalhos (padrão False para compatibilidade)
        remove_chapter_headers = data.get('remove_chapter_headers', False)
        
        # Usar o serviço para gerar o roteiro completo
        result = storyteller_service.generate_storyteller_script(
            title=title,
            premise=premise,
            agent_type=agent_type,
            num_chapters=num_chapters,
            provider='gemini',
            remove_chapter_headers=remove_chapter_headers
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao gerar roteiro com Storyteller: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao gerar roteiro com Storyteller Unlimited'
        }), 500

@storyteller_bp.route('/advanced-stats/<story_id>', methods=['GET'])
def get_advanced_stats(story_id):
    """Retorna estatísticas avançadas sobre uma história"""
    try:
        stats = advanced_storyteller_service.get_advanced_stats(story_id)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'story_id': story_id,
            'message': 'Estatísticas avançadas recuperadas com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas avançadas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao obter estatísticas avançadas'
        }), 500

@storyteller_bp.route('/cache-status', methods=['GET'])
def get_cache_status():
    """Retorna status do cache Redis e estatísticas gerais"""
    try:
        cache_stats = advanced_storyteller_service.memory_bridge.cache_service.get_cache_stats()
        
        return jsonify({
            'success': True,
            'cache_stats': cache_stats,
            'advanced_features': {
                'redis_cache': True,
                'token_chunker': True,
                'smart_chapter_breaker': True
            },
            'message': 'Status do cache recuperado com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status do cache: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao obter status do cache'
        }), 500

@storyteller_bp.route('/health', methods=['GET'])
def health_check():
    """Verifica saúde do serviço Storyteller"""
    try:
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'storyteller',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500