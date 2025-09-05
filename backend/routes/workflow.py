"""
🔄 Complete Workflow Routes
Rotas para automação completa da esteira de produção
"""

from flask import Blueprint, request, jsonify
import requests
import json
import time
import threading
import os
from collections import deque
from services.title_generator import TitleGenerator

# Sistema de logs em tempo real
workflow_logs = deque(maxlen=1000)  # Manter últimos 1000 logs
log_lock = threading.Lock()

# Estado global para controle de pausa
workflow_paused = False
workflow_cancelled = False
workflow_running = False  # Controle de fila - apenas uma automação por vez

def add_workflow_log(message, level="info", data=None):
    """Adicionar log ao sistema de logs em tempo real"""
    with log_lock:
        log_entry = {
            'timestamp': time.time(),
            'message': message,
            'level': level,
            'data': data
        }
        workflow_logs.append(log_entry)
        print(f"[{level.upper()}] {message}")

def check_workflow_status():
    """Verificar se o workflow deve pausar ou cancelar"""
    global workflow_paused, workflow_cancelled

    print(f"🔍 DEBUG: Verificando status - Pausado: {workflow_paused}, Cancelado: {workflow_cancelled}")

    if workflow_cancelled:
        add_workflow_log("❌ WORKFLOW CANCELADO PELO USUÁRIO!", "error")
        print("❌ CANCELAMENTO DETECTADO - INTERROMPENDO WORKFLOW")
        workflow_cancelled = False  # Reset para próxima execução
        workflow_paused = False
        raise Exception("WORKFLOW CANCELADO PELO USUÁRIO")

    while workflow_paused:
        add_workflow_log("⏸️ Workflow pausado - aguardando retomada...", "warning")
        time.sleep(0.5)  # Aguardar menos tempo para resposta mais rápida

        if workflow_cancelled:
            add_workflow_log("❌ WORKFLOW CANCELADO DURANTE PAUSA!", "error")
            print("❌ CANCELAMENTO DETECTADO DURANTE PAUSA")
            workflow_cancelled = False
            workflow_paused = False
            raise Exception("WORKFLOW CANCELADO DURANTE PAUSA")

workflow_bp = Blueprint('workflow', __name__)

@workflow_bp.route('/logs', methods=['GET'])
def get_workflow_logs():
    """Obter logs do workflow em tempo real"""
    try:
        since = request.args.get('since', type=float, default=0)

        with log_lock:
            # Filtrar logs desde o timestamp especificado
            filtered_logs = [
                log for log in workflow_logs
                if log['timestamp'] > since
            ]

        return jsonify({
            'success': True,
            'logs': list(filtered_logs),
            'total': len(filtered_logs)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workflow_bp.route('/logs/clear', methods=['POST'])
def clear_workflow_logs():
    """Limpar logs do workflow"""
    try:
        with log_lock:
            workflow_logs.clear()

        return jsonify({
            'success': True,
            'message': 'Logs limpos com sucesso'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workflow_bp.route('/pause', methods=['POST'])
def pause_workflow():
    """Pausar workflow em execução"""
    global workflow_paused
    try:
        workflow_paused = True
        add_workflow_log("⏸️ Workflow pausado pelo usuário", "warning")

        return jsonify({
            'success': True,
            'message': 'Workflow pausado'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workflow_bp.route('/resume', methods=['POST'])
def resume_workflow():
    """Retomar workflow pausado"""
    global workflow_paused
    try:
        workflow_paused = False
        add_workflow_log("▶️ Workflow retomado pelo usuário", "info")

        return jsonify({
            'success': True,
            'message': 'Workflow retomado'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workflow_bp.route('/cancel', methods=['POST'])
def cancel_workflow():
    """Cancelar workflow em execução"""
    global workflow_cancelled, workflow_paused, workflow_running
    try:
        workflow_cancelled = True
        workflow_paused = False
        workflow_running = False  # Liberar fila imediatamente
        add_workflow_log("❌ Workflow cancelado pelo usuário", "error")

        return jsonify({
            'success': True,
            'message': 'Workflow cancelado'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workflow_bp.route('/test', methods=['POST'])
def test_workflow():
    """Testar automação completa com dados simulados"""
    global workflow_running

    # Verificar se já há uma automação em execução
    if workflow_running:
        return jsonify({
            'success': False,
            'error': 'Já existe uma automação em execução. Aguarde a conclusão ou cancele a atual.'
        }), 409  # Conflict

    try:
        workflow_running = True  # Marcar como em execução
        data = request.get_json()
        ai_provider = data.get('ai_provider', 'auto')
        openrouter_model = data.get('openrouter_model', 'auto')
        number_of_chapters = data.get('number_of_chapters', 8)
        titles_count = data.get('titles_count', 5)  # Quantidade de títulos a gerar
        use_custom_prompt = data.get('use_custom_prompt', False)  # Se deve usar prompt personalizado
        custom_prompt = data.get('custom_prompt', '')  # Prompt personalizado
        api_keys = data.get('api_keys', {})

        # DEBUG: Verificar parâmetros recebidos
        add_workflow_log(f"🔍 DEBUG: Parâmetros recebidos:")
        add_workflow_log(f"   titles_count: {titles_count}")
        add_workflow_log(f"   use_custom_prompt: {use_custom_prompt}")
        add_workflow_log(f"   custom_prompt: {custom_prompt[:50] if custom_prompt else 'Vazio'}...")

        # SEMPRE carregar do arquivo e mesclar com as chaves do request
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
        file_api_keys = {}

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_api_keys = json.load(f)
            add_workflow_log(f"🔍 DEBUG: Chaves do arquivo: {list(file_api_keys.keys())}")
        else:
            add_workflow_log("⚠️ DEBUG: Arquivo api_keys.json não encontrado")

        # Mesclar: priorizar chaves do arquivo se as do request estiverem vazias
        final_api_keys = {}
        all_keys = set(list(api_keys.keys()) + list(file_api_keys.keys()))

        for key in all_keys:
            request_value = api_keys.get(key, '').strip() if api_keys.get(key) else ''
            file_value = file_api_keys.get(key, '').strip() if file_api_keys.get(key) else ''

            # Usar valor do arquivo se o request estiver vazio
            if file_value and not request_value:
                final_api_keys[key] = file_value
                add_workflow_log(f"🔍 DEBUG: Usando chave do arquivo para {key}: {file_value[:20]}...")
            elif request_value:
                final_api_keys[key] = request_value
                add_workflow_log(f"🔍 DEBUG: Usando chave do request para {key}: {request_value[:20]}...")

        api_keys = final_api_keys

        add_workflow_log("🚀 Iniciando teste de automação completa...")

        # Limpar logs anteriores
        with log_lock:
            workflow_logs.clear()

        # Debug das chaves de API
        add_workflow_log(f"🔍 Chaves recebidas: {list(api_keys.keys())}")
        for key, value in api_keys.items():
            if value and value.strip():
                add_workflow_log(f"✅ {key}: configurado ({value[:10]}...)")
            else:
                add_workflow_log(f"❌ {key}: não configurado ou vazio")

        # Inicializar serviços
        title_generator = TitleGenerator()

        # Configurar APIs
        apis_configured = configure_apis(title_generator, ai_provider, api_keys)

        if not apis_configured:
            raise Exception("Nenhuma API de IA configurada. Configure pelo menos uma chave de API (Gemini, OpenAI ou OpenRouter) nas configurações.")

        # DADOS SIMULADOS para teste
        simulated_extraction = {
            'videos': [
                {'title': 'Como Ganhar Dinheiro Online em 2024', 'number_of_views': 150000, 'like_count': 5000},
                {'title': '10 Dicas Para Ser Mais Produtivo', 'number_of_views': 89000, 'like_count': 3200},
                {'title': 'A Verdade Sobre Investimentos', 'number_of_views': 234000, 'like_count': 8900},
                {'title': 'Transforme Sua Vida em 30 Dias', 'number_of_views': 67000, 'like_count': 2100},
                {'title': 'Segredos dos Milionários Revelados', 'number_of_views': 445000, 'like_count': 15600}
            ],
            'total_videos': 5,
            'total_views': 985000,
            'total_likes': 34800,
            'channel_url': 'teste'
        }

        results = {}
        results['extraction'] = simulated_extraction
        add_workflow_log(f"✅ Dados simulados carregados: {len(simulated_extraction['videos'])} títulos",
                        "success", simulated_extraction['videos'])

        # ETAPA 2: Geração de Títulos
        add_workflow_log("🎯 ETAPA 2: Gerando novos títulos com IA...")
        check_workflow_status()  # Verificar pausa/cancelamento
        titles_result = execute_title_generation(
            title_generator, simulated_extraction['videos'], ai_provider, api_keys, titles_count, use_custom_prompt, custom_prompt
        )

        if not titles_result['success']:
            raise Exception(f"Falha na geração de títulos: {titles_result.get('error', 'Erro desconhecido')}")

        results['titles'] = titles_result['data']
        add_workflow_log(f"✅ {len(titles_result['data']['generated_titles'])} títulos gerados",
                        "success", titles_result['data']['generated_titles'])

        # ETAPA 3: Geração de Premissas
        add_workflow_log("📝 ETAPA 3: Criando premissas envolventes...")
        check_workflow_status()  # Verificar pausa/cancelamento

        # Verificar se há títulos gerados
        generated_titles = titles_result['data'].get('generated_titles', [])
        if not generated_titles:
            raise Exception("Nenhum título foi gerado na etapa anterior. Não é possível criar premissas.")

        selected_titles = generated_titles[:3]
        add_workflow_log(f"📋 Usando {len(selected_titles)} títulos para gerar premissas:")
        for i, title in enumerate(selected_titles, 1):
            add_workflow_log(f"   {i}. {title}", "info")

        premises_result = execute_premise_generation(
            title_generator, selected_titles, ai_provider, openrouter_model, api_keys
        )

        if not premises_result['success']:
            raise Exception(f"Falha na geração de premissas: {premises_result.get('error', 'Erro desconhecido')}")

        results['premises'] = premises_result['premises']
        add_workflow_log(f"✅ {len(premises_result['premises'])} premissas criadas",
                        "success", premises_result['premises'])

        # ETAPA 4: Geração de Roteiros
        add_workflow_log("📖 ETAPA 4: Gerando roteiro completo...")
        check_workflow_status()  # Verificar pausa/cancelamento
        best_title = selected_titles[0] if selected_titles else titles_result['data']['generated_titles'][0]
        best_premise = premises_result['premises'][0] if premises_result['premises'] else None

        if not best_premise:
            raise Exception("Nenhuma premissa disponível para gerar roteiro")

        scripts_result = execute_script_generation(
            title_generator, best_title, best_premise, ai_provider, openrouter_model, number_of_chapters, api_keys,
            agent_config=data.get('agent'), specialized_agents=data.get('specialized_agents')
        )

        if not scripts_result['success']:
            raise Exception(f"Falha na geração de roteiros: {scripts_result.get('error', 'Erro desconhecido')}")

        results['scripts'] = scripts_result['scripts']
        add_workflow_log(f"✅ Roteiro com {len(scripts_result['scripts']['chapters'])} capítulos gerado",
                        "success", scripts_result['scripts'])

        # ETAPA 5: Geração de TTS (opcional)
        tts_provider = data.get('tts_provider', None)
        if tts_provider and tts_provider != 'none':
            add_workflow_log("🎵 ETAPA 5: Gerando áudio TTS...")
            check_workflow_status()  # Verificar pausa/cancelamento

            tts_result = execute_tts_generation(
                scripts_result['scripts'], tts_provider, api_keys, data
            )

            if tts_result['success']:
                results['tts'] = tts_result['tts_data']
                add_workflow_log(f"✅ TTS gerado com sucesso - {len(tts_result['tts_data']['segments'])} segmentos",
                               "success", tts_result['tts_data'])
            else:
                add_workflow_log(f"⚠️ Falha na geração de TTS: {tts_result.get('error', 'Erro desconhecido')}", "warning")
                # TTS é opcional, não falhar o workflow inteiro
                results['tts'] = {'error': tts_result.get('error', 'Erro desconhecido')}

        # Resultado final
        final_result = {
            'extraction': results['extraction'],
            'titles': results['titles'],
            'premises': results['premises'],
            'scripts': results['scripts'],
            'summary': {
                'extracted_videos': len(results['extraction']['videos']),
                'generated_titles': len(results['titles']['generated_titles']),
                'created_premises': len(results['premises']),
                'script_chapters': len(results['scripts']['chapters']),
                'total_words': results['scripts']['total_words'],
                'tts_segments': len(results.get('tts', {}).get('segments', [])) if 'tts' in results and 'segments' in results['tts'] else 0
            },
            'timestamp': time.time()
        }

        print("🎉 Teste de automação completa finalizado com sucesso!")

        return jsonify({
            'success': True,
            'results': final_result,
            'message': 'Teste de automação completa executado com sucesso'
        })

    except Exception as e:
        print(f"❌ Erro no teste de automação: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        workflow_running = False  # Liberar fila

@workflow_bp.route('/complete', methods=['POST'])
def complete_workflow():
    """Executar automação completa: Extração → Títulos → Premissas → Roteiros"""
    global workflow_running

    # Verificar se já há uma automação em execução
    if workflow_running:
        return jsonify({
            'success': False,
            'error': 'Já existe uma automação em execução. Aguarde a conclusão ou cancele a atual.'
        }), 409  # Conflict

    try:
        workflow_running = True  # Marcar como em execução
        data = request.get_json()
        channel_url = data.get('channel_url', '')
        max_titles = data.get('max_titles', 5)
        min_views = data.get('min_views', 1000)
        days = data.get('days', 30)
        ai_provider = data.get('ai_provider', 'auto')
        openrouter_model = data.get('openrouter_model', 'auto')
        number_of_chapters = data.get('number_of_chapters', 8)
        titles_count = data.get('titles_count', 5)  # Quantidade de títulos a gerar
        use_custom_prompt = data.get('use_custom_prompt', False)  # Se deve usar prompt personalizado
        custom_prompt = data.get('custom_prompt', '')  # Prompt personalizado
        auto_select_best = data.get('auto_select_best', True)
        api_keys = data.get('api_keys', {})

        # SEMPRE carregar do arquivo e mesclar com as chaves do request
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.json')
        file_api_keys = {}

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_api_keys = json.load(f)
            print(f"🔍 DEBUG: Chaves do arquivo: {list(file_api_keys.keys())}")
        else:
            print("⚠️ DEBUG: Arquivo api_keys.json não encontrado")

        # Mesclar: priorizar chaves do arquivo se as do request estiverem vazias
        final_api_keys = {}
        all_keys = set(list(api_keys.keys()) + list(file_api_keys.keys()))

        for key in all_keys:
            request_value = api_keys.get(key, '').strip() if api_keys.get(key) else ''
            file_value = file_api_keys.get(key, '').strip() if file_api_keys.get(key) else ''

            # Usar valor do arquivo se o request estiver vazio
            if file_value and not request_value:
                final_api_keys[key] = file_value
                print(f"🔍 DEBUG: Usando chave do arquivo para {key}: {file_value[:20]}...")
            elif request_value:
                final_api_keys[key] = request_value
                print(f"🔍 DEBUG: Usando chave do request para {key}: {request_value[:20]}...")

        api_keys = final_api_keys

        if not channel_url:
            return jsonify({
                'success': False,
                'error': 'URL do canal é obrigatória'
            }), 400

        print("🚀 Iniciando automação completa...")

        # Inicializar serviços
        title_generator = TitleGenerator()

        # Configurar APIs
        configure_apis(title_generator, ai_provider, api_keys)
        
        results = {}
        
        # ETAPA 1: Extração do YouTube
        print("📺 ETAPA 1: Extraindo títulos do YouTube...")
        check_workflow_status()  # Verificar pausa/cancelamento
        extraction_result = execute_youtube_extraction(
            channel_url, max_titles, min_views, days, api_keys
        )
        
        if not extraction_result['success']:
            raise Exception(f"Falha na extração: {extraction_result.get('error', 'Erro desconhecido')}")

        results['extraction'] = extraction_result['data']
        print(f"✅ {len(extraction_result['data']['videos'])} títulos extraídos")
        
        # ETAPA 2: Geração de Títulos
        print("🎯 ETAPA 2: Gerando novos títulos com IA...")
        check_workflow_status()  # Verificar pausa/cancelamento
        titles_result = execute_title_generation(
            title_generator, extraction_result['data']['videos'], ai_provider, api_keys, titles_count, use_custom_prompt, custom_prompt
        )
        
        if not titles_result['success']:
            raise Exception(f"Falha na geração de títulos: {titles_result.get('error', 'Erro desconhecido')}")
        
        results['titles'] = titles_result['data']
        print(f"✅ {len(titles_result['data']['generated_titles'])} títulos gerados")
        
        # ETAPA 3: Geração de Premissas
        print("📝 ETAPA 3: Criando premissas envolventes...")
        check_workflow_status()  # Verificar pausa/cancelamento

        # Verificar se há títulos gerados
        generated_titles = titles_result['data'].get('generated_titles', [])
        if not generated_titles:
            raise Exception("Nenhum título foi gerado na etapa anterior. Não é possível criar premissas.")

        selected_titles = generated_titles[:3] if auto_select_best else generated_titles
        print(f"📋 Usando {len(selected_titles)} títulos para gerar premissas:")
        for i, title in enumerate(selected_titles, 1):
            print(f"   {i}. {title}")

        premises_result = execute_premise_generation(
            title_generator, selected_titles, ai_provider, openrouter_model, api_keys
        )
        
        if not premises_result['success']:
            raise Exception(f"Falha na geração de premissas: {premises_result.get('error', 'Erro desconhecido')}")
        
        results['premises'] = premises_result['premises']
        print(f"✅ {len(premises_result['premises'])} premissas criadas")
        
        # ETAPA 4: Geração de Roteiros
        print("📖 ETAPA 4: Gerando roteiro completo...")
        check_workflow_status()  # Verificar pausa/cancelamento
        best_title = selected_titles[0] if selected_titles else titles_result['data']['generated_titles'][0]
        best_premise = premises_result['premises'][0] if premises_result['premises'] else None
        
        if not best_premise:
            raise Exception("Nenhuma premissa disponível para gerar roteiro")
        
        scripts_result = execute_script_generation(
            title_generator, best_title, best_premise, ai_provider, openrouter_model, number_of_chapters, api_keys,
            agent_config=data.get('agent'), specialized_agents=data.get('specialized_agents')
        )
        
        if not scripts_result['success']:
            raise Exception(f"Falha na geração de roteiros: {scripts_result.get('error', 'Erro desconhecido')}")
        
        results['scripts'] = scripts_result['scripts']
        print(f"✅ Roteiro com {len(scripts_result['scripts']['chapters'])} capítulos gerado")

        # ETAPA 5: Geração de TTS (opcional)
        tts_provider = data.get('tts_provider', None)
        if tts_provider and tts_provider != 'none':
            print("🎵 ETAPA 5: Gerando áudio TTS...")
            check_workflow_status()  # Verificar pausa/cancelamento

            tts_result = execute_tts_generation(
                scripts_result['scripts'], tts_provider, api_keys, data
            )

            if tts_result['success']:
                results['tts'] = tts_result['tts_data']
                print(f"✅ TTS gerado com sucesso - {len(tts_result['tts_data']['segments'])} segmentos")
            else:
                print(f"⚠️ Falha na geração de TTS: {tts_result.get('error', 'Erro desconhecido')}")
                # TTS é opcional, não falhar o workflow inteiro
                results['tts'] = {'error': tts_result.get('error', 'Erro desconhecido')}

        # Resultado final
        final_result = {
            'extraction': results['extraction'],
            'titles': results['titles'],
            'premises': results['premises'],
            'scripts': results['scripts'],
            'summary': {
                'extracted_videos': len(results['extraction']['videos']),
                'generated_titles': len(results['titles']['generated_titles']),
                'created_premises': len(results['premises']),
                'script_chapters': len(results['scripts']['chapters']),
                'total_words': results['scripts']['total_words'],
                'tts_segments': len(results.get('tts', {}).get('segments', [])) if 'tts' in results and 'segments' in results['tts'] else 0
            },
            'timestamp': time.time()
        }
        
        print("🎉 Automação completa finalizada com sucesso!")
        
        return jsonify({
            'success': True,
            'results': final_result,
            'message': 'Automação completa executada com sucesso'
        })

    except Exception as e:
        print(f"❌ Erro na automação completa: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        workflow_running = False  # Liberar fila

def configure_apis(title_generator, ai_provider, api_keys):
    """Configurar APIs baseado no provider"""
    add_workflow_log(f"🔧 Configurando APIs - Provider: {ai_provider}")
    add_workflow_log(f"🔍 DEBUG: Chaves disponíveis: {list(api_keys.keys())}")
    add_workflow_log(f"🔍 DEBUG: Chaves com valores: {[k for k, v in api_keys.items() if v and str(v).strip()]}")

    configured_count = 0

    if ai_provider == 'openai' or ai_provider == 'auto':
        openai_key = api_keys.get('openai')
        add_workflow_log(f"🔍 DEBUG: OpenAI key exists: {bool(openai_key)}, length: {len(str(openai_key)) if openai_key else 0}")
        if openai_key and openai_key.strip():
            try:
                success = title_generator.configure_openai(openai_key)
                if success:
                    add_workflow_log("✅ OpenAI configurado com sucesso")
                    configured_count += 1
                else:
                    add_workflow_log("❌ Falha ao configurar OpenAI")
            except Exception as e:
                add_workflow_log(f"❌ Erro ao configurar OpenAI: {str(e)}")
        else:
            add_workflow_log("⚠️ OpenAI não configurado (chave não encontrada ou vazia)")

    if ai_provider == 'gemini' or ai_provider == 'auto':
        # Verificar tanto 'gemini' quanto 'gemini_1' para compatibilidade
        gemini_key = api_keys.get('gemini') or api_keys.get('gemini_1')
        add_workflow_log(f"🔍 DEBUG: Gemini key exists: {bool(gemini_key)}, length: {len(str(gemini_key)) if gemini_key else 0}")
        if gemini_key and gemini_key.strip():
            try:
                success = title_generator.configure_gemini(gemini_key)
                if success:
                    add_workflow_log("✅ Gemini configurado com sucesso")
                    configured_count += 1
                else:
                    add_workflow_log("❌ Falha ao configurar Gemini")
            except Exception as e:
                add_workflow_log(f"❌ Erro ao configurar Gemini: {str(e)}")
        else:
            add_workflow_log("⚠️ Gemini não configurado (chave não encontrada ou vazia)")

    if ai_provider == 'openrouter' or ai_provider == 'auto':
        openrouter_key = api_keys.get('openrouter')
        add_workflow_log(f"🔍 DEBUG: OpenRouter key exists: {bool(openrouter_key)}, length: {len(str(openrouter_key)) if openrouter_key else 0}")
        if openrouter_key and openrouter_key.strip():
            try:
                success = title_generator.configure_openrouter(openrouter_key)
                if success:
                    add_workflow_log("✅ OpenRouter configurado com sucesso")
                    configured_count += 1
                else:
                    add_workflow_log("❌ Falha ao configurar OpenRouter")
            except Exception as e:
                add_workflow_log(f"❌ Erro ao configurar OpenRouter: {str(e)}")
        else:
            add_workflow_log("⚠️ OpenRouter não configurado (chave não encontrada ou vazia)")

    add_workflow_log(f"📊 Total de APIs configuradas: {configured_count}")

    if configured_count == 0:
        add_workflow_log("❌ NENHUMA API DE IA CONFIGURADA! Configure pelo menos uma chave de API.")
        return False

    return True

def execute_youtube_extraction(channel_url, max_titles, min_views, days, api_keys):
    """Executar extração do YouTube chamando função diretamente"""
    try:
        # Verificar se a chave RapidAPI está disponível
        if not api_keys.get('rapidapi'):
            return {
                'success': False,
                'error': 'Chave RapidAPI não configurada'
            }



        print(f"🔍 DEBUG Workflow: Iniciando extração direta")
        print(f"🔍 DEBUG Workflow: Channel URL: {channel_url}")
        print(f"🔍 DEBUG Workflow: Max titles: {max_titles}")
        print(f"🔍 DEBUG Workflow: Min views: {min_views}")
        print(f"🔍 DEBUG Workflow: Days: {days}")

        # Importar e usar as funções diretamente
        from routes.automations import extract_channel_name_or_id, get_channel_videos_rapidapi

        # Extrair ID do canal
        channel_id = extract_channel_name_or_id(channel_url)
        print(f"🔍 DEBUG Workflow: Channel ID extraído: {channel_id}")

        if not channel_id:
            return {
                'success': False,
                'error': 'URL do canal inválida - não foi possível extrair o ID'
            }

        # Obter vídeos do canal
        videos_result = get_channel_videos_rapidapi(
            channel_id,
            api_keys['rapidapi'],
            max_results=max_titles
        )

        if not videos_result.get('success'):
            return {
                'success': False,
                'error': f"Falha na API RapidAPI: {videos_result.get('error')}"
            }

        videos = videos_result['data']['videos']
        print(f"🔍 DEBUG Workflow: {len(videos)} vídeos obtidos da API")

        # Aplicar filtros
        filtered_videos = []
        for video in videos:
            # Tentar diferentes campos para views
            views = video.get('views', 0) or video.get('view_count', 0) or video.get('viewCount', 0)

            # Converter views para int se for string
            if isinstance(views, str):
                try:
                    import re
                    views_clean = re.sub(r'[^\d]', '', views)
                    views = int(views_clean) if views_clean else 0
                except:
                    views = 0

            # Aplicar filtro de views
            if views >= int(min_views):
                filtered_videos.append({
                    'title': video.get('title', ''),
                    'views': views,
                    'url': f"https://youtube.com/watch?v={video.get('video_id', '')}",
                    'video_id': video.get('video_id', ''),
                    'published_at': video.get('published_at', ''),
                    'duration': video.get('duration', ''),
                    'thumbnail': video.get('thumbnail', '')
                })

        print(f"🔍 DEBUG Workflow: {len(filtered_videos)} vídeos após filtros")

        if len(filtered_videos) == 0:
            return {
                'success': False,
                'error': f"Nenhum vídeo passou no filtro de {min_views} visualizações mínimas. Tente um valor menor."
            }

        final_videos = filtered_videos[:int(max_titles)]

        return {
            'success': True,
            'data': {
                'videos': final_videos,
                'total_found': len(videos),
                'total_filtered': len(filtered_videos),
                'channel_id': channel_id
            }
        }

    except Exception as e:
        print(f"❌ DEBUG Workflow: Exceção: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def execute_title_generation(title_generator, source_videos, ai_provider, api_keys, titles_count=5, use_custom_prompt=False, custom_prompt=''):
    """Executar geração de títulos"""
    try:
        if not source_videos:
            add_workflow_log("❌ Nenhum vídeo fornecido para análise", "error")
            return {
                'success': False,
                'error': 'Nenhum vídeo fornecido para análise'
            }

        source_titles = [video['title'] for video in source_videos]

        add_workflow_log(f"📊 Analisando {len(source_titles)} títulos extraídos...")
        for i, title in enumerate(source_titles, 1):
            add_workflow_log(f"   {i}. {title[:80]}{'...' if len(title) > 80 else ''}", "info")

        add_workflow_log("🤖 Iniciando geração de títulos com IA...")
        add_workflow_log(f"   Provider: {ai_provider}")
        add_workflow_log(f"   Tópico: conteúdo viral")
        add_workflow_log(f"   Quantidade: 5 títulos")
        add_workflow_log(f"   Estilo: viral")

        # Verificar se há APIs configuradas
        has_openai = hasattr(title_generator, 'openai_client') and title_generator.openai_client is not None
        has_gemini = hasattr(title_generator, 'gemini_model') and title_generator.gemini_model is not None
        has_openrouter = hasattr(title_generator, 'openrouter_api_key') and title_generator.openrouter_api_key is not None

        add_workflow_log(f"🔍 Status das APIs:")
        add_workflow_log(f"   OpenAI: {'✅ Configurado' if has_openai else '❌ Não configurado'}")
        add_workflow_log(f"   Gemini: {'✅ Configurado' if has_gemini else '❌ Não configurado'}")
        add_workflow_log(f"   OpenRouter: {'✅ Configurado' if has_openrouter else '❌ Não configurado'}")

        if not (has_openai or has_gemini or has_openrouter):
            add_workflow_log("❌ NENHUMA API DE IA ESTÁ CONFIGURADA!", "error")
            add_workflow_log("💡 Para resolver:", "info")
            add_workflow_log("   1. Vá em Configurações", "info")
            add_workflow_log("   2. Configure pelo menos uma chave de API", "info")
            add_workflow_log("   3. Gemini é gratuito e recomendado", "info")
            add_workflow_log("   4. Clique em 'Salvar Alterações'", "info")
            raise Exception("Nenhuma API de IA configurada. Configure pelo menos uma chave de API (Gemini, OpenAI ou OpenRouter) nas configurações.")

        # Verificar se deve usar prompt personalizado
        if use_custom_prompt and custom_prompt.strip():
            add_workflow_log("🎨 Usando prompt personalizado para geração de títulos...")
            add_workflow_log(f"📝 Prompt: {custom_prompt[:100]}...")
            check_workflow_status()  # Verificar cancelamento antes da geração

            # Implementar fallback automático para prompt personalizado
            result = None
            if ai_provider == 'openai' and has_openai:
                try:
                    result = title_generator.generate_titles_with_custom_prompt(
                        source_titles=source_titles,
                        custom_prompt=custom_prompt,
                        count=titles_count,
                        ai_provider='openai'
                    )
                    add_workflow_log("✅ Títulos gerados com OpenAI (prompt personalizado)", "info")
                except Exception as e:
                    error_msg = str(e).lower()
                    if ('429' in error_msg or 'quota' in error_msg or 'insufficient_quota' in error_msg) and has_gemini:
                        add_workflow_log(f"⚠️ OpenAI quota excedida, tentando Gemini: {e}", "warning")
                        try:
                            result = title_generator.generate_titles_with_custom_prompt(
                                source_titles=source_titles,
                                custom_prompt=custom_prompt,
                                count=titles_count,
                                ai_provider='gemini'
                            )
                            add_workflow_log("✅ Títulos gerados com Gemini (fallback)", "info")
                        except Exception as gemini_error:
                            add_workflow_log(f"❌ Gemini fallback falhou: {gemini_error}", "error")
                            raise e
                    else:
                        raise e
            else:
                # Usar provider especificado ou auto
                result = title_generator.generate_titles_with_custom_prompt(
                    source_titles=source_titles,
                    custom_prompt=custom_prompt,
                    count=titles_count,
                    ai_provider=ai_provider
                )
        else:
            # Gerar títulos usando o método híbrido padrão com fallback
            add_workflow_log("🔄 Usando método padrão para geração de títulos...")
            check_workflow_status()  # Verificar cancelamento antes da geração

            # Extrair tópico principal dos títulos de origem
            main_topic = source_titles[0] if source_titles else "conteúdo viral"
            add_workflow_log(f"🎯 Título de referência: {main_topic}")

            # Implementar fallback automático para método híbrido
            result = None
            if ai_provider == 'openai' and has_openai:
                try:
                    result = title_generator.generate_titles_hybrid(
                        source_titles=source_titles,
                        topic=f"títulos similares e melhorados baseados em: {main_topic}",
                        count=titles_count,
                        style='viral'
                    )
                    add_workflow_log("✅ Títulos gerados com modo híbrido (OpenAI)", "info")
                except Exception as e:
                    error_msg = str(e).lower()
                    if ('429' in error_msg or 'quota' in error_msg or 'insufficient_quota' in error_msg) and has_gemini:
                        add_workflow_log(f"⚠️ Modo híbrido falhou (quota), tentando Gemini: {e}", "warning")
                        try:
                            result = title_generator.generate_titles_gemini(
                                source_titles=source_titles,
                                topic=f"títulos similares e melhorados baseados em: {main_topic}",
                                count=titles_count,
                                style='viral'
                            )
                            # Formatar resultado para compatibilidade
                            if isinstance(result, list):
                                result = {
                                    'success': True,
                                    'combined_titles': result,
                                    'ai_provider_used': 'gemini (fallback)'
                                }
                            add_workflow_log("✅ Títulos gerados com Gemini (fallback)", "info")
                        except Exception as gemini_error:
                            add_workflow_log(f"❌ Gemini fallback falhou: {gemini_error}", "error")
                            raise e
                    else:
                        raise e
            elif ai_provider == 'auto' and has_openai:
                # Modo auto: tentar OpenAI primeiro, depois Gemini
                try:
                    result = title_generator.generate_titles_hybrid(
                        source_titles=source_titles,
                        topic=f"títulos similares e melhorados baseados em: {main_topic}",
                        count=titles_count,
                        style='viral'
                    )
                    add_workflow_log("✅ Títulos gerados com modo híbrido (auto)", "info")
                except Exception as e:
                    error_msg = str(e).lower()
                    if ('429' in error_msg or 'quota' in error_msg or 'insufficient_quota' in error_msg) and has_gemini:
                        add_workflow_log(f"⚠️ Auto-híbrido falhou (quota), tentando Gemini: {e}", "warning")
                        try:
                            result = title_generator.generate_titles_gemini(
                                source_titles=source_titles,
                                topic=f"títulos similares e melhorados baseados em: {main_topic}",
                                count=titles_count,
                                style='viral'
                            )
                            # Formatar resultado para compatibilidade
                            if isinstance(result, list):
                                result = {
                                    'success': True,
                                    'combined_titles': result,
                                    'ai_provider_used': 'gemini (auto-fallback)'
                                }
                            add_workflow_log("✅ Títulos gerados com Gemini (auto-fallback)", "info")
                        except Exception as gemini_error:
                            add_workflow_log(f"❌ Auto-fallback para Gemini falhou: {gemini_error}", "error")
                            raise e
                    else:
                        raise e
            else:
                # Usar método padrão sem fallback
                result = title_generator.generate_titles_hybrid(
                    source_titles=source_titles,
                    topic=f"títulos similares e melhorados baseados em: {main_topic}",
                    count=titles_count,
                    style='viral'
                )

        check_workflow_status()  # Verificar cancelamento após a geração

        add_workflow_log(f"📋 Resultado da geração: success={result.get('success', False)}")
        check_workflow_status()  # Verificar cancelamento após geração

        if result.get('success'):
            # A função de prompt personalizado retorna 'generated_titles', não 'combined_titles'
            generated_titles = result.get('combined_titles', []) or result.get('generated_titles', [])
            add_workflow_log(f"🎯 {len(generated_titles)} títulos gerados com IA:")
            for i, title in enumerate(generated_titles, 1):
                add_workflow_log(f"   {i}. {title}", "success")
                check_workflow_status()  # Verificar cancelamento durante listagem

            # Formatar resultado no formato esperado
            formatted_result = {
                'generated_titles': generated_titles,
                'total_generated': len(generated_titles),
                'patterns_analysis': result.get('patterns_analysis', {}),
                'ai_provider_used': result.get('ai_provider_used', ai_provider)
            }

            return {
                'success': True,
                'data': formatted_result
            }
        else:
            error_msg = result.get('error', 'Erro desconhecido na geração de títulos')
            add_workflow_log(f"❌ Falha na geração: {error_msg}", "error")
            raise Exception(error_msg)

    except Exception as e:
        error_msg = str(e)
        add_workflow_log(f"❌ Erro na geração de títulos: {error_msg}", "error")
        return {
            'success': False,
            'error': error_msg
        }

def execute_premise_generation(title_generator, selected_titles, ai_provider, openrouter_model, api_keys):
    """Executar geração de premissas"""
    try:
        # Usar a mesma lógica do endpoint de premissas
        from routes.premise import generate_premises_openrouter, generate_premises_gemini, generate_premises_openai
        
        default_prompt = """# Gerador de Premissas Profissionais para Vídeos

Você é um especialista em criação de conteúdo e storytelling para YouTube. Sua tarefa é criar premissas envolventes e profissionais baseadas nos títulos fornecidos.

## Instruções:
1. Analise cada título fornecido
2. Crie uma premissa única e cativante para cada um
3. A premissa deve ter entre 100-200 palavras
4. Inclua elementos de storytelling (problema, conflito, resolução)
5. Mantenha o tom adequado ao nicho do título
6. Adicione ganchos emocionais e curiosidade

## Formato de Resposta:
Para cada título, forneça:

**TÍTULO:** [título original]
**PREMISSA:**
[Premissa detalhada com storytelling envolvente]

---

## Títulos para análise:"""

        prompt = f"{default_prompt}\n\n{chr(10).join(f'{i+1}. {title}' for i, title in enumerate(selected_titles))}"
        
        premises = []
        
        if ai_provider == 'auto':
            # Tentar em ordem de prioridade
            providers = ['openrouter', 'gemini', 'openai']
            
            for provider in providers:
                try:
                    if provider == 'openrouter' and api_keys.get('openrouter'):
                        premises = generate_premises_openrouter(selected_titles, prompt, openrouter_model, api_keys['openrouter'])
                        break
                    elif provider == 'gemini' and title_generator.gemini_model:
                        premises = generate_premises_gemini(selected_titles, prompt, title_generator)
                        break
                    elif provider == 'openai' and title_generator.openai_client:
                        premises = generate_premises_openai(selected_titles, prompt, title_generator)
                        break
                except Exception as e:
                    print(f"❌ Erro com {provider}: {e}")
                    continue
        elif ai_provider == 'openrouter':
            premises = generate_premises_openrouter(selected_titles, prompt, openrouter_model, api_keys['openrouter'])
        elif ai_provider == 'gemini':
            premises = generate_premises_gemini(selected_titles, prompt, title_generator)
        elif ai_provider == 'openai':
            premises = generate_premises_openai(selected_titles, prompt, title_generator)
        
        if not premises:
            raise Exception("Falha ao gerar premissas com todos os providers")

        add_workflow_log("📝 Premissas geradas:")
        for i, premise in enumerate(premises, 1):
            add_workflow_log(f"   {i}. TÍTULO: {premise['title']}", "info")
            add_workflow_log(f"      PREMISSA: {premise['premise'][:100]}...", "info")

        return {
            'success': True,
            'premises': premises
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def execute_script_generation(title_generator, selected_title, selected_premise, ai_provider, openrouter_model, number_of_chapters, api_keys, agent_config=None, specialized_agents=None):
    """Executar geração de roteiros com suporte a agentes especializados"""
    try:
        # Verificar se há agente especializado configurado
        use_agent = (agent_config and agent_config.get('type') == 'specialized' and 
                    agent_config.get('specialized_type') and specialized_agents)
        
        if use_agent:
            # Usar gerador de roteiros longos com agente especializado
            # Removido: sistema antigo de geração de roteiros
            
            agent_type = agent_config['specialized_type']
            if agent_type in specialized_agents:
                # Preparar configuração da requisição para agentes especializados
                request_config = {
                    'agent_prompts': specialized_agents[agent_type].get('prompts', {}).get('scripts', {})
                }
                
                add_workflow_log(f"🎆 Usando agente especializado: {specialized_agents[agent_type].get('name', agent_type)}")
                
                # Gerar roteiro usando Storyteller Unlimited
                from services.storyteller_service import StorytellerService
                
                storyteller_service = StorytellerService()
                
                add_workflow_log(f"🎬 [STORYTELLER_WORKFLOW] Gerando roteiro com agente especializado: {agent_type}")
                
                result = storyteller_service.generate_storyteller_script(
                    title=selected_title,
                    premise=selected_premise['premise'],
                    agent_type=agent_type,
                    num_chapters=number_of_chapters,
                    provider='gemini'
                )
                
                if not result:
                    raise Exception("Falha na geração com Storyteller Unlimited")
                
                # Preferir capítulos estruturados retornados pelo Storyteller
                chapters_data = result.get('chapters') or []
                chapters = []
                if chapters_data:
                    for idx, ch in enumerate(chapters_data, 1):
                        chapters.append({
                            'chapter_number': idx,
                            'title': ch.get('title', f'Capítulo {idx}'),
                            'content': ch.get('content', '')
                        })
                    script_content = result.get('full_script', "\n\n".join(ch.get('content', '') for ch in chapters_data))
                else:
                    # Fallback: tentar montar capítulos a partir do full_script
                    script_content = result.get('full_script', '')
                    if script_content:
                        # Dividir o script em capítulos baseado em marcadores comuns
                        chapter_parts = script_content.split('\n\n## Capítulo ')
                        for i, part in enumerate(chapter_parts):
                            if i == 0 and not part.strip().startswith('Capítulo'):
                                continue
                            if part.strip():
                                chapter_num = i + 1
                                chapter_text = part.strip()
                                if not chapter_text.startswith('Capítulo'):
                                    chapter_text = f"Capítulo {chapter_num}\n\n{chapter_text}"
                                chapters.append({
                                    'chapter_number': chapter_num,
                                    'title': f'Capítulo {chapter_num}',
                                    'content': chapter_text
                                })
                
                script_result = {
                    'title': selected_title,
                    'premise': selected_premise['premise'],
                    'chapters': chapters,
                    'total_chapters': len(chapters),
                    'total_words': len(script_content.split()) if chapters else 0,
                    'agent_used': {
                        'type': agent_type,
                        'name': specialized_agents[agent_type].get('name', agent_type)
                    },
                    'system_used': 'storyteller_unlimited'
                }
            else:
                add_workflow_log(f"⚠️ Agente {agent_type} não encontrado, usando método padrão")
                use_agent = False
        
        if not use_agent:
            # Usar Storyteller Unlimited como método padrão
            from services.storyteller_service import StorytellerService
            
            storyteller_service = StorytellerService()
            
            add_workflow_log("🎬 [STORYTELLER_WORKFLOW] Usando Storyteller Unlimited como método padrão")
            
            result = storyteller_service.generate_storyteller_script(
                title=selected_title,
                premise=selected_premise['premise'],
                agent_type='millionaire_stories',
                num_chapters=number_of_chapters,
                provider='gemini'
            )
            
            if not result:
                raise Exception("Falha na geração com Storyteller Unlimited")
            
            # Preferir capítulos estruturados retornados pelo Storyteller
            chapters_data = result.get('chapters') or []
            if chapters_data:
                chapters = []
                for idx, ch in enumerate(chapters_data, 1):
                    chapters.append({
                        'chapter_number': ch.get('chapter_number', idx),
                        'title': ch.get('title', f'Capítulo {idx}'),
                        'content': ch.get('content', '')
                    })
                script_content = result.get('full_script', "\n\n".join(ch.get('content', '') for ch in chapters))
            else:
                # Fallback: dividir texto completo caso capítulos estruturados não estejam presentes
                script_content = result.get('full_script', '')
                chapters = []
                if script_content:
                    chapter_parts = script_content.split('\n\n## Capítulo ')
                    
                    for i, part in enumerate(chapter_parts):
                        if i == 0 and not part.strip().startswith('Capítulo'):
                            continue
                        
                        if part.strip():
                            chapter_num = i + 1
                            chapter_content = part.strip()
                            if not chapter_content.startswith('Capítulo'):
                                chapter_content = f"Capítulo {chapter_num}\n\n{chapter_content}"
                            
                            chapters.append({
                                'chapter_number': chapter_num,
                                'title': f'Capítulo {chapter_num}',
                                'content': chapter_content
                            })
                
                script_result = {
                    'title': selected_title,
                    'premise': selected_premise['premise'],
                    'context': selected_premise['premise'],
                    'narrative_structure': 'Storyteller Unlimited',
                    'chapters': chapters,
                    'total_chapters': len(chapters),
                    'total_words': len(script_content.split()),
                    'system_used': 'storyteller_unlimited'
                }
        
        if not script_result:
            raise Exception("Falha na geração com Storyteller Unlimited")

        add_workflow_log("📖 Roteiro gerado:")
        add_workflow_log(f"   TÍTULO: {script_result['title']}", "info")
        add_workflow_log(f"   PREMISSA: {script_result['premise'][:100]}...", "info")
        add_workflow_log(f"   CAPÍTULOS: {len(script_result['chapters'])}", "info")
        add_workflow_log(f"   PALAVRAS: {script_result['total_words']}", "info")
        add_workflow_log("   CAPÍTULOS:", "info")
        for i, chapter in enumerate(script_result['chapters'][:3], 1):  # Mostrar apenas os 3 primeiros
            chapter_title = chapter.get('title', f'Capítulo {chapter.get("chapter_number", i)}')
            add_workflow_log(f"   {i}. {chapter_title}", "info")
            add_workflow_log(f"      {chapter['content'][:80]}...", "info")
        if len(script_result['chapters']) > 3:
            add_workflow_log(f"   ... e mais {len(script_result['chapters']) - 3} capítulos", "info")

        return {
            'success': True,
            'scripts': script_result
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def execute_tts_generation(scripts_data, tts_provider, api_keys, workflow_data):
    """Executar geração de TTS automática"""
    try:
        from routes.automations import generate_tts_with_elevenlabs, generate_tts_with_gemini, generate_tts_with_kokoro

        add_workflow_log(f"🎵 Iniciando geração de TTS com {tts_provider.upper()}...")

        # Extrair texto completo do roteiro
        full_text = ""
        chapters = scripts_data.get('chapters', [])

        for chapter in chapters:
            if chapter.get('content'):
                full_text += chapter['content'] + "\n\n"

        if not full_text.strip():
            raise Exception("Nenhum conteúdo encontrado no roteiro para gerar TTS")

        add_workflow_log(f"📝 Texto extraído: {len(full_text)} caracteres")

        # Configurar parâmetros baseado no provedor
        segments = []

        if tts_provider == 'elevenlabs':
            # Configurações ElevenLabs
            api_key = api_keys.get('elevenlabs')
            if not api_key:
                raise Exception("Chave da API ElevenLabs não configurada")

            voice_id = workflow_data.get('elevenlabs_voice_id', 'default')
            model_id = workflow_data.get('elevenlabs_model_id', 'eleven_monolingual_v1')

            add_workflow_log(f"🎤 Gerando com ElevenLabs - Voz: {voice_id}")

            result = generate_tts_with_elevenlabs(
                full_text, api_key, voice_id=voice_id, model_id=model_id
            )

            if result.get('success'):
                segments.append({
                    'index': 1,
                    'text': full_text[:100] + '...',
                    'audio': result['data'],
                    'provider': 'elevenlabs'
                })
            else:
                raise Exception(f"Erro no ElevenLabs: {result.get('error', 'Erro desconhecido')}")

        elif tts_provider == 'gemini':
            # Configurações Gemini (usar rotação automática)
            voice_name = workflow_data.get('gemini_voice_name', 'Aoede')
            model = workflow_data.get('gemini_model', 'gemini-2.0-flash-exp')
            speed = workflow_data.get('gemini_speed', 1.0)

            add_workflow_log(f"🤖 Gerando com Gemini TTS - Voz: {voice_name}")

            result = generate_tts_with_gemini(
                full_text, voice_name=voice_name, model=model, speed=speed
            )

            if result.get('success'):
                segments.append({
                    'index': 1,
                    'text': full_text[:100] + '...',
                    'audio': result['data'],
                    'provider': 'gemini'
                })
            else:
                raise Exception(f"Erro no Gemini TTS: {result.get('error', 'Erro desconhecido')}")

        elif tts_provider == 'kokoro':
            # Configurações Kokoro
            voice = workflow_data.get('kokoro_voice', 'af_bella')
            kokoro_url = workflow_data.get('kokoro_url', 'http://localhost:8880')
            language = workflow_data.get('kokoro_language', 'en')
            speed = workflow_data.get('kokoro_speed', 1.0)

            add_workflow_log(f"⚡ Gerando com Kokoro TTS - Voz: {voice}, Idioma: {language}")

            result = generate_tts_with_kokoro(
                full_text, kokoro_url=kokoro_url, voice_name=voice,
                language=language, speed=speed
            )

            if result.get('success'):
                segments.append({
                    'index': 1,
                    'text': full_text[:100] + '...',
                    'audio': result['data'],
                    'provider': 'kokoro'
                })
            else:
                raise Exception(f"Erro no Kokoro TTS: {result.get('error', 'Erro desconhecido')}")

        else:
            raise Exception(f"Provedor TTS não suportado: {tts_provider}")

        add_workflow_log(f"✅ TTS gerado com sucesso - {len(segments)} segmento(s)")

        return {
            'success': True,
            'tts_data': {
                'provider': tts_provider,
                'segments': segments,
                'total_segments': len(segments),
                'text_length': len(full_text)
            }
        }

    except Exception as e:
        add_workflow_log(f"❌ Erro na geração de TTS: {str(e)}", "error")
        return {
            'success': False,
            'error': str(e)
        }
