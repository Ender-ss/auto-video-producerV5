/**
 * 🚨 Error Messages Utility
 * 
 * Utilitário para transformar erros técnicos em mensagens amigáveis
 */

// Mapeamento de tipos de erro para mensagens amigáveis
const ERROR_MESSAGES = {
  // Erros de Rede
  'network_error': {
    title: '🌐 Problema de Conexão',
    message: 'Não conseguimos conectar com o servidor.',
    suggestions: [
      'Verifique sua conexão com a internet',
      'Tente recarregar a página',
      'Aguarde alguns minutos e tente novamente'
    ]
  },
  
  'timeout_error': {
    title: '⏱️ Tempo Esgotado',
    message: 'A operação demorou mais que o esperado.',
    suggestions: [
      'Tente novamente em alguns minutos',
      'Verifique sua conexão com a internet',
      'O servidor pode estar sobrecarregado'
    ]
  },
  
  // Erros de API
  'api_error': {
    title: '🔌 Erro na API',
    message: 'Houve um problema ao comunicar com o servidor.',
    suggestions: [
      'Tente novamente em alguns minutos',
      'Verifique se o servidor está funcionando',
      'Entre em contato com o suporte se persistir'
    ]
  },
  
  'rate_limit_error': {
    title: '🚦 Muitas Tentativas',
    message: 'Você fez muitas solicitações muito rapidamente.',
    suggestions: [
      'Aguarde alguns minutos antes de tentar novamente',
      'Reduza a frequência das suas ações',
      'Tente usar a aplicação mais devagar'
    ]
  },
  
  // Erros de Autenticação
  'auth_error': {
    title: '🔐 Problema de Autenticação',
    message: 'Suas credenciais não são válidas ou expiraram.',
    suggestions: [
      'Verifique suas chaves de API nas configurações',
      'Recarregue a página e tente novamente',
      'Entre em contato com o suporte se necessário'
    ]
  },
  
  // Erros de Validação
  'validation_error': {
    title: '⚠️ Dados Inválidos',
    message: 'Alguns dados não estão no formato correto.',
    suggestions: [
      'Verifique se todos os campos estão preenchidos',
      'Confirme se os dados estão no formato esperado',
      'Tente corrigir os campos destacados'
    ]
  },
  
  // Erros de Arquivo
  'file_error': {
    title: '📁 Problema com Arquivo',
    message: 'Houve um erro ao processar o arquivo.',
    suggestions: [
      'Verifique se o arquivo não está corrompido',
      'Tente usar um arquivo diferente',
      'Certifique-se de que o formato é suportado'
    ]
  },
  
  // Erros Gerais
  'unknown_error': {
    title: '❓ Erro Desconhecido',
    message: 'Algo inesperado aconteceu.',
    suggestions: [
      'Tente recarregar a página',
      'Verifique sua conexão com a internet',
      'Entre em contato com o suporte se persistir'
    ]
  }
}

/**
 * Detecta o tipo de erro baseado na mensagem ou código
 */
export const detectErrorType = (error) => {
  if (!error) return 'unknown_error'
  
  const errorMessage = error.message || error.toString().toLowerCase()
  const errorCode = error.code || error.status
  
  // Erros de rede
  if (errorMessage.includes('network') || errorMessage.includes('fetch') || errorCode === 'NETWORK_ERROR') {
    return 'network_error'
  }
  
  if (errorMessage.includes('timeout') || errorCode === 'TIMEOUT') {
    return 'timeout_error'
  }
  
  // Erros HTTP
  if (errorCode === 429 || errorMessage.includes('rate limit') || errorMessage.includes('too many requests')) {
    return 'rate_limit_error'
  }
  
  if (errorCode === 401 || errorCode === 403 || errorMessage.includes('unauthorized') || errorMessage.includes('forbidden')) {
    return 'auth_error'
  }
  
  if (errorCode === 400 || errorMessage.includes('validation') || errorMessage.includes('invalid')) {
    return 'validation_error'
  }
  
  if (errorCode >= 500 || errorMessage.includes('server error') || errorMessage.includes('internal error')) {
    return 'api_error'
  }
  
  // Erros de arquivo
  if (errorMessage.includes('file') || errorMessage.includes('upload') || errorMessage.includes('download')) {
    return 'file_error'
  }
  
  return 'unknown_error'
}

/**
 * Obtém uma mensagem amigável para o erro
 */
export const getFriendlyErrorMessage = (error, context = '') => {
  const errorType = detectErrorType(error)
  const errorInfo = ERROR_MESSAGES[errorType] || ERROR_MESSAGES['unknown_error']
  
  return {
    type: errorType,
    title: errorInfo.title,
    message: context ? `${errorInfo.message} (${context})` : errorInfo.message,
    suggestions: errorInfo.suggestions,
    originalError: error.message || error.toString()
  }
}

/**
 * Formata um erro para exibição em toast/notificação
 */
export const formatErrorForToast = (error, context = '') => {
  const friendlyError = getFriendlyErrorMessage(error, context)
  
  return {
    title: friendlyError.title,
    description: friendlyError.message,
    duration: 5000,
    action: {
      label: 'Ver Detalhes',
      onClick: () => {
        console.group('🚨 Detalhes do Erro')
        console.log('Tipo:', friendlyError.type)
        console.log('Título:', friendlyError.title)
        console.log('Mensagem:', friendlyError.message)
        console.log('Sugestões:', friendlyError.suggestions)
        console.log('Erro Original:', friendlyError.originalError)
        console.groupEnd()
      }
    }
  }
}

/**
 * Hook para lidar com erros de forma consistente
 */
export const useErrorHandler = () => {
  const handleError = (error, context = '', showToast = true) => {
    const friendlyError = getFriendlyErrorMessage(error, context)
    
    // Log do erro para debug
    console.error(`🚨 Erro [${context}]:`, {
      type: friendlyError.type,
      message: friendlyError.message,
      originalError: error
    })
    
    // Mostrar toast se solicitado
    if (showToast && typeof toast !== 'undefined') {
      const toastData = formatErrorForToast(error, context)
      toast.error(toastData.description, {
        duration: toastData.duration
      })
    }
    
    return friendlyError
  }
  
  return { handleError }
}

export default {
  detectErrorType,
  getFriendlyErrorMessage,
  formatErrorForToast,
  useErrorHandler
}