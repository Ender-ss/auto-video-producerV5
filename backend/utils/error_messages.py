#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Mensagens de Erro Amigáveis
Transforma erros técnicos em mensagens compreensíveis para o usuário final
"""

def get_user_friendly_error(error_type, original_error="", context=""):
    """
    Converte erros técnicos em mensagens amigáveis para o usuário
    
    Args:
        error_type (str): Tipo do erro (api_key, quota, network, etc.)
        original_error (str): Mensagem de erro original
        context (str): Contexto onde o erro ocorreu
    
    Returns:
        dict: Mensagem estruturada com título, descrição e sugestões
    """
    
    error_messages = {
        # Erros de API Key
        'api_key_missing': {
            'title': '🔑 Chave de API Necessária',
            'message': 'Para usar este recurso, você precisa configurar uma chave de API válida.',
            'suggestions': [
                'Vá para Configurações → Chaves de API',
                'Adicione sua chave de API para o serviço selecionado',
                'Verifique se a chave está correta e ativa'
            ]
        },
        
        'api_key_invalid': {
            'title': '❌ Chave de API Inválida',
            'message': 'A chave de API fornecida não é válida ou expirou.',
            'suggestions': [
                'Verifique se a chave foi copiada corretamente',
                'Confirme se a chave não expirou',
                'Gere uma nova chave no painel do provedor'
            ]
        },
        
        # Erros de Quota
        'quota_exceeded': {
            'title': '📊 Limite de Uso Atingido',
            'message': 'Você atingiu o limite de uso da sua conta para este serviço.',
            'suggestions': [
                'Aguarde até o próximo período de renovação',
                'Considere fazer upgrade do seu plano',
                'Use um provedor alternativo temporariamente'
            ]
        },
        
        'rate_limit': {
            'title': '⏱️ Muitas Requisições',
            'message': 'Você está fazendo muitas requisições muito rapidamente.',
            'suggestions': [
                'Aguarde alguns minutos antes de tentar novamente',
                'Reduza a quantidade de conteúdo gerado por vez',
                'O sistema tentará automaticamente em alguns instantes'
            ]
        },
        
        # Erros de Rede
        'network_error': {
            'title': '🌐 Problema de Conexão',
            'message': 'Não foi possível conectar com o serviço externo.',
            'suggestions': [
                'Verifique sua conexão com a internet',
                'Tente novamente em alguns minutos',
                'O serviço pode estar temporariamente indisponível'
            ]
        },
        
        'timeout_error': {
            'title': '⏰ Tempo Limite Excedido',
            'message': 'A operação demorou mais tempo que o esperado.',
            'suggestions': [
                'Tente novamente com um conteúdo menor',
                'Verifique sua conexão com a internet',
                'O serviço pode estar sobrecarregado'
            ]
        },
        
        # Erros de Conteúdo
        'content_blocked': {
            'title': '🚫 Conteúdo Bloqueado',
            'message': 'O conteúdo foi bloqueado pelas políticas de segurança do provedor.',
            'suggestions': [
                'Revise o conteúdo para remover termos sensíveis',
                'Tente reformular o texto de forma mais neutra',
                'Use um provedor alternativo'
            ]
        },
        
        'content_too_long': {
            'title': '📏 Conteúdo Muito Longo',
            'message': 'O conteúdo excede o limite máximo permitido.',
            'suggestions': [
                'Divida o conteúdo em partes menores',
                'Reduza o tamanho do texto',
                'Use um modelo que suporte mais tokens'
            ]
        },
        
        # Erros de Validação
        'validation_error': {
            'title': '⚠️ Dados Inválidos',
            'message': 'Alguns dados fornecidos não estão no formato correto.',
            'suggestions': [
                'Verifique se todos os campos obrigatórios estão preenchidos',
                'Confirme se os dados estão no formato esperado',
                'Tente recarregar a página e tentar novamente'
            ]
        },
        
        # Erros de Sistema
        'internal_error': {
            'title': '🔧 Erro Interno',
            'message': 'Ocorreu um erro interno no sistema.',
            'suggestions': [
                'Tente novamente em alguns minutos',
                'Se o problema persistir, reporte o erro',
                'Verifique se todos os serviços estão funcionando'
            ]
        },
        
        # Erros de Pipeline
        'pipeline_dependency': {
            'title': '🔗 Dependência Não Atendida',
            'message': 'Esta etapa depende de outras etapas que ainda não foram concluídas.',
            'suggestions': [
                'Complete as etapas anteriores primeiro',
                'Verifique se não há erros nas etapas anteriores',
                'Reinicie o pipeline se necessário'
            ]
        },
        
        'pipeline_failed': {
            'title': '⚙️ Falha no Pipeline',
            'message': 'O pipeline de automação encontrou um erro e foi interrompido.',
            'suggestions': [
                'Verifique os logs para mais detalhes',
                'Corrija os problemas identificados',
                'Reinicie o pipeline após as correções'
            ]
        }
    }
    
    # Retorna a mensagem correspondente ou uma mensagem genérica
    if error_type in error_messages:
        error_info = error_messages[error_type].copy()
        if context:
            error_info['context'] = context
        if original_error:
            error_info['technical_details'] = original_error
        return error_info
    else:
        return {
            'title': '❓ Erro Desconhecido',
            'message': 'Ocorreu um erro inesperado.',
            'suggestions': [
                'Tente novamente em alguns minutos',
                'Verifique sua conexão e configurações',
                'Se o problema persistir, reporte o erro'
            ],
            'technical_details': original_error if original_error else 'Erro não especificado'
        }

def detect_error_type(error_message):
    """
    Detecta o tipo de erro baseado na mensagem de erro original
    
    Args:
        error_message (str): Mensagem de erro original
    
    Returns:
        str: Tipo do erro detectado
    """
    error_message_lower = error_message.lower()
    
    # Erros de API Key
    if any(keyword in error_message_lower for keyword in ['api key', 'unauthorized', 'invalid key', 'authentication']):
        if 'missing' in error_message_lower or 'required' in error_message_lower:
            return 'api_key_missing'
        else:
            return 'api_key_invalid'
    
    # Erros de Quota
    if any(keyword in error_message_lower for keyword in ['quota', 'limit', 'exceeded', 'insufficient']):
        return 'quota_exceeded'
    
    # Erros de Rate Limit
    if any(keyword in error_message_lower for keyword in ['429', 'too many requests', 'rate limit']):
        return 'rate_limit'
    
    # Erros de Rede
    if any(keyword in error_message_lower for keyword in ['connection', 'network', 'unreachable', 'dns']):
        return 'network_error'
    
    # Erros de Timeout
    if any(keyword in error_message_lower for keyword in ['timeout', 'timed out', 'time limit']):
        return 'timeout_error'
    
    # Erros de Conteúdo
    if any(keyword in error_message_lower for keyword in ['safety', 'blocked', 'policy', 'inappropriate']):
        return 'content_blocked'
    
    if any(keyword in error_message_lower for keyword in ['too long', 'max tokens', 'length']):
        return 'content_too_long'
    
    # Erros de Validação
    if any(keyword in error_message_lower for keyword in ['validation', 'invalid', 'required', 'missing']):
        return 'validation_error'
    
    # Erros de Pipeline
    if any(keyword in error_message_lower for keyword in ['dependency', 'prerequisite', 'depends']):
        return 'pipeline_dependency'
    
    if any(keyword in error_message_lower for keyword in ['pipeline', 'workflow', 'automation']):
        return 'pipeline_failed'
    
    # Erro genérico
    return 'internal_error'

def format_error_response(error_type, original_error="", context=""):
    """
    Formata uma resposta de erro completa para APIs
    
    Args:
        error_type (str): Tipo do erro
        original_error (str): Mensagem de erro original
        context (str): Contexto onde o erro ocorreu
    
    Returns:
        dict: Resposta formatada para API
    """
    error_info = get_user_friendly_error(error_type, original_error, context)
    
    return {
        'success': False,
        'error': error_info['message'],
        'error_details': {
            'title': error_info['title'],
            'message': error_info['message'],
            'suggestions': error_info['suggestions'],
            'type': error_type
        },
        'technical_details': error_info.get('technical_details', ''),
        'context': error_info.get('context', '')
    }

def auto_format_error(original_error, context=""):
    """
    Detecta automaticamente o tipo de erro e formata a resposta
    
    Args:
        original_error (str): Mensagem de erro original
        context (str): Contexto onde o erro ocorreu
    
    Returns:
        dict: Resposta formatada para API
    """
    error_type = detect_error_type(str(original_error))
    return format_error_response(error_type, str(original_error), context)