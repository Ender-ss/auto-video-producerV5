import React, { useState, useEffect } from 'react'
import { Zap, RefreshCw, TestTube, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

const SettingsDebug = () => {
  const [rapidApiStatus, setRapidApiStatus] = useState(null)
  const [isLoadingRapidApiStatus, setIsLoadingRapidApiStatus] = useState(false)
  const [apiKeys, setApiKeys] = useState({
    rapidapi: '',
    rapidapi_1: '',
    rapidapi_2: '',
    rapidapi_3: '',
    rapidapi_4: '',
    rapidapi_5: '',
    rapidapi_6: '',
    rapidapi_7: '',
    rapidapi_8: '',
    rapidapi_9: '',
    rapidapi_10: ''
  })

  // Função para buscar status da rotação RapidAPI
  const fetchRapidApiStatus = async () => {
    console.log('🔍 Iniciando fetch do status RapidAPI...')
    setIsLoadingRapidApiStatus(true)
    try {
      const response = await fetch('http://localhost:5000/api/automations/rapidapi-status')
      console.log('🔍 Response status:', response.status)
      const data = await response.json()
      console.log('🔍 RapidAPI Status Response:', data)
      setRapidApiStatus(data)
    } catch (error) {
      console.error('❌ Erro ao buscar status RapidAPI:', error)
      setRapidApiStatus(null)
    } finally {
      setIsLoadingRapidApiStatus(false)
    }
  }

  // Carregar status ao montar o componente
  useEffect(() => {
    console.log('🔍 Componente montado, carregando status...')
    fetchRapidApiStatus()
  }, [])

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-6">Debug - Rotação RapidAPI</h1>
        
        {/* Debug Info */}
        <div className="mb-6 p-4 bg-yellow-900 border border-yellow-600 rounded">
          <h3 className="text-yellow-200 font-bold mb-2">🔍 Informações de Debug</h3>
          <p className="text-yellow-200">🔄 RapidAPI Status: {rapidApiStatus ? 'Carregado' : 'Não carregado'}</p>
          <p className="text-yellow-200">⏳ Loading: {isLoadingRapidApiStatus ? 'Sim' : 'Não'}</p>
          <p className="text-yellow-200">📊 Status Data: {JSON.stringify(rapidApiStatus, null, 2)}</p>
          <button 
            onClick={() => {
              console.log('🔍 Teste manual do fetch')
              fetchRapidApiStatus()
            }}
            className="mt-2 px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
          >
            Testar Fetch Manual
          </button>
        </div>

        {/* Status da Rotação RapidAPI */}
        <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Zap size={20} className="text-yellow-400" />
              <h3 className="text-lg font-semibold text-white">Status da Rotação RapidAPI</h3>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={fetchRapidApiStatus}
                disabled={isLoadingRapidApiStatus}
                className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-1"
              >
                <RefreshCw size={14} className={isLoadingRapidApiStatus ? 'animate-spin' : ''} />
                <span>Atualizar</span>
              </button>
            </div>
          </div>

          {isLoadingRapidApiStatus ? (
            <div className="text-center py-4">
              <RefreshCw size={24} className="text-blue-400 animate-spin mx-auto mb-2" />
              <p className="text-gray-400">Carregando status...</p>
            </div>
          ) : rapidApiStatus ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Status Geral */}
              <div className="bg-gray-800 rounded p-3">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Status Geral</h4>
                <div className="space-y-1 text-xs">
                  <div className="flex items-center space-x-2">
                    {rapidApiStatus.rotation_enabled ? (
                      <CheckCircle size={12} className="text-green-400" />
                    ) : (
                      <XCircle size={12} className="text-red-400" />
                    )}
                    <span className={rapidApiStatus.rotation_enabled ? 'text-green-300' : 'text-red-300'}>
                      Rotação: {rapidApiStatus.rotation_enabled ? 'Ativa' : 'Inativa'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-400">Chave atual:</span>
                    <span className="text-white font-mono">{rapidApiStatus.current_key_index || 0}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-400">Total de chaves:</span>
                    <span className="text-white">{rapidApiStatus.total_keys || 0}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-400">Chaves ativas:</span>
                    <span className="text-green-300">{rapidApiStatus.active_keys || 0}</span>
                  </div>
                </div>
              </div>

              {/* Throttling e Cache */}
              <div className="bg-gray-800 rounded p-3">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Throttling & Cache</h4>
                <div className="space-y-1 text-xs">
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-400">Throttling ativo:</span>
                    <span className={rapidApiStatus.throttling_active ? 'text-yellow-300' : 'text-green-300'}>
                      {rapidApiStatus.throttling_active ? 'Sim' : 'Não'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-400">Itens em cache:</span>
                    <span className="text-blue-300">{rapidApiStatus.cache_size || 0}</span>
                  </div>
                </div>
              </div>

              {/* Estatísticas */}
              <div className="bg-gray-800 rounded p-3">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Estatísticas</h4>
                <div className="space-y-1 text-xs">
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-400">Requisições hoje:</span>
                    <span className="text-blue-300">{rapidApiStatus.requests_today || 0}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-400">Erros 429:</span>
                    <span className="text-red-300">{rapidApiStatus.rate_limit_errors || 0}</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <AlertCircle size={24} className="text-yellow-400 mx-auto mb-2" />
              <p className="text-gray-400">Não foi possível carregar o status da rotação RapidAPI</p>
              <button
                onClick={fetchRapidApiStatus}
                className="mt-2 px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                Tentar novamente
              </button>
            </div>
          )}

          {/* Chaves Configuradas */}
          {rapidApiStatus && (
            <div className="mt-4 bg-gray-800 rounded p-3">
              <h4 className="text-sm font-medium text-gray-300 mb-2">Chaves Configuradas</h4>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                {[0,1,2,3,4,5,6,7,8,9,10].map(num => {
                  const key = num === 0 ? 'rapidapi' : `rapidapi_${num}`
                  const hasKey = apiKeys[key] && apiKeys[key].length > 10
                  const isActive = rapidApiStatus.current_key_index === num
                  const isFailed = rapidApiStatus.failed_keys && rapidApiStatus.failed_keys.includes(num)
                  return (
                    <div key={key} className={`flex items-center space-x-2 text-xs p-2 rounded ${
                      isActive ? 'bg-blue-900 border border-blue-600' : 
                      isFailed ? 'bg-red-900 border border-red-600' :
                      hasKey ? 'bg-green-900 border border-green-600' : 'bg-gray-700'
                    }`}>
                      {hasKey ? (
                        isActive ? (
                          <Zap size={12} className="text-blue-400" />
                        ) : isFailed ? (
                          <XCircle size={12} className="text-red-400" />
                        ) : (
                          <CheckCircle size={12} className="text-green-400" />
                        )
                      ) : (
                        <XCircle size={12} className="text-gray-500" />
                      )}
                      <span className={`${
                        isActive ? 'text-blue-300 font-semibold' :
                        isFailed ? 'text-red-300' :
                        hasKey ? 'text-green-300' : 'text-gray-500'
                      }`}>
                        {num === 0 ? 'Principal' : `Chave ${num}`}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          <div className="mt-3 text-xs text-gray-400">
            💡 <strong>Dica:</strong> Configure múltiplas chaves RapidAPI para evitar limites de rate. O sistema rotaciona automaticamente quando uma chave atinge o limite.
          </div>
        </div>
      </div>
    </div>
  )
}

export default SettingsDebug