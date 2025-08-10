/**
 * ⚙️ Settings Page
 * 
 * Página de configurações do sistema
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Key,
  Eye,
  EyeOff,
  CheckCircle,
  XCircle,
  RefreshCw,
  AlertCircle,
  Save,
  Zap,
  Volume2,
  Image,
  Youtube,
  Settings as SettingsIcon,
  TestTube,
  FileText
} from 'lucide-react'

const Settings = () => {
  const [activeTab, setActiveTab] = useState('apis')
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    gemini_1: '',
    gemini_2: '',
    gemini_3: '',
    gemini_4: '',
    gemini_5: '',
    gemini_6: '',
    gemini_7: '',
    gemini_8: '',
    gemini_9: '',
    gemini_10: '',
    openrouter: '',
    elevenlabs: '',
    together: '',
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
  const [apiStatus, setApiStatus] = useState({
    openai: 'unknown',
    gemini_1: 'unknown',
    gemini_2: 'unknown',
    gemini_3: 'unknown',
    gemini_4: 'unknown',
    gemini_5: 'unknown',
    gemini_6: 'unknown',
    gemini_7: 'unknown',
    gemini_8: 'unknown',
    gemini_9: 'unknown',
    gemini_10: 'unknown',
    openrouter: 'unknown',
    elevenlabs: 'unknown',
    together: 'unknown',
    rapidapi: 'unknown',
    rapidapi_1: 'unknown',
    rapidapi_2: 'unknown',
    rapidapi_3: 'unknown',
    rapidapi_4: 'unknown',
    rapidapi_5: 'unknown',
    rapidapi_6: 'unknown',
    rapidapi_7: 'unknown',
    rapidapi_8: 'unknown',
    rapidapi_9: 'unknown',
    rapidapi_10: 'unknown'
  })
  const [showPasswords, setShowPasswords] = useState({})
  const [testingApi, setTestingApi] = useState(null)
  const [unsavedChanges, setUnsavedChanges] = useState(false)

  const tabs = [
    { id: 'apis', label: 'APIs de IA', icon: Key },
    { id: 'system', label: 'Sistema', icon: SettingsIcon },
    { id: 'logs', label: 'Logs', icon: FileText },
    { id: 'tests', label: 'Testes de API', icon: TestTube }
  ]

  // Carregar configurações salvas
  useEffect(() => {
    const savedKeys = localStorage.getItem('api_keys')
    if (savedKeys) {
      setApiKeys(JSON.parse(savedKeys))
    }
  }, [])

  const testApiConnection = async (apiName, showAlert = true) => {
    if (!apiKeys[apiName]) {
      if (showAlert) alert('Por favor, insira a chave da API primeiro')
      return
    }

    setTestingApi(apiName)
    setApiStatus(prev => ({ ...prev, [apiName]: 'testing' }))

    try {
      const response = await fetch('http://localhost:5000/api/settings/test-api', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_name: apiName,
          api_key: apiKeys[apiName]
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setApiStatus(prev => ({ ...prev, [apiName]: 'connected' }))
        if (showAlert) alert(`✅ ${apiName.toUpperCase()}: ${data.message}`)
      } else {
        setApiStatus(prev => ({ ...prev, [apiName]: 'error' }))
        if (showAlert) alert(`❌ ${apiName.toUpperCase()}: ${data.message}`)
      }
    } catch (error) {
      setApiStatus(prev => ({ ...prev, [apiName]: 'error' }))
      if (showAlert) alert(`❌ Erro de conexão: ${error.message}`)
    } finally {
      setTestingApi(null)
    }
  }

  const saveApiKeys = async () => {
    try {
      // Salvar no localStorage
      localStorage.setItem('api_keys', JSON.stringify(apiKeys))
      
      // Salvar no backend
      const response = await fetch('http://localhost:5000/api/settings/api-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiKeys)
      })

      const data = await response.json()
      
      if (data.success) {
        setUnsavedChanges(false)
        alert('✅ Configurações salvas com sucesso!')
      } else {
        alert(`❌ Erro ao salvar: ${data.error}`)
      }
    } catch (error) {
      alert(`❌ Erro de conexão: ${error.message}`)
    }
  }

  const handleApiKeyChange = (apiName, value) => {
    setApiKeys(prev => ({ ...prev, [apiName]: value }))
    setUnsavedChanges(true)
    setApiStatus(prev => ({ ...prev, [apiName]: 'unknown' }))
  }

  const togglePasswordVisibility = (key) => {
    setShowPasswords(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  console.log('🔍 Renderizando Settings.jsx com múltiplas chaves Gemini')

  const apiSections = [
    {
      title: 'Extração de Conteúdo (Chave Principal)',
      icon: Youtube,
      apis: [
        { key: 'rapidapi', name: 'RapidAPI YouTube V2 (Principal)', description: 'Chave principal para extração de dados do YouTube', required: true }
      ]
    },
    {
      title: 'RapidAPI (Rotação de Chaves)',
      icon: Youtube,
      description: '🔄 Configure múltiplas chaves RapidAPI para evitar rate limiting (erro 429). O sistema rotacionará automaticamente.',
      apis: [
        { key: 'rapidapi_1', name: 'RapidAPI Chave 1', description: 'Primeira chave RapidAPI para rotação' },
        { key: 'rapidapi_2', name: 'RapidAPI Chave 2', description: 'Segunda chave para rotação' },
        { key: 'rapidapi_3', name: 'RapidAPI Chave 3', description: 'Terceira chave para rotação' },
        { key: 'rapidapi_4', name: 'RapidAPI Chave 4', description: 'Quarta chave para rotação' },
        { key: 'rapidapi_5', name: 'RapidAPI Chave 5', description: 'Quinta chave para rotação' },
        { key: 'rapidapi_6', name: 'RapidAPI Chave 6', description: 'Sexta chave para rotação' },
        { key: 'rapidapi_7', name: 'RapidAPI Chave 7', description: 'Sétima chave para rotação' },
        { key: 'rapidapi_8', name: 'RapidAPI Chave 8', description: 'Oitava chave para rotação' },
        { key: 'rapidapi_9', name: 'RapidAPI Chave 9', description: 'Nona chave para rotação' },
        { key: 'rapidapi_10', name: 'RapidAPI Chave 10', description: 'Décima chave para rotação' }
      ]
    },
    {
      title: 'Modelos de Texto/Roteiro',
      icon: Zap,
      apis: [
        { key: 'openai', name: 'OpenAI GPT-4', description: 'Melhor qualidade para títulos e roteiros' },
        { key: 'openrouter', name: 'OpenRouter', description: 'Acesso a múltiplos modelos (Claude, Llama, etc.)' }
      ]
    },
    {
      title: 'Google Gemini (Rotação de Chaves)',
      icon: Zap,
      description: '🔄 Configure múltiplas chaves para evitar limites de cota. O sistema rotacionará automaticamente.',
      apis: [
        { key: 'gemini_1', name: 'Gemini Chave 1', description: 'Primeira chave Gemini (principal)' },
        { key: 'gemini_2', name: 'Gemini Chave 2', description: 'Segunda chave para rotação' },
        { key: 'gemini_3', name: 'Gemini Chave 3', description: 'Terceira chave para rotação' },
        { key: 'gemini_4', name: 'Gemini Chave 4', description: 'Quarta chave para rotação' },
        { key: 'gemini_5', name: 'Gemini Chave 5', description: 'Quinta chave para rotação' },
        { key: 'gemini_6', name: 'Gemini Chave 6', description: 'Sexta chave para rotação' },
        { key: 'gemini_7', name: 'Gemini Chave 7', description: 'Sétima chave para rotação' },
        { key: 'gemini_8', name: 'Gemini Chave 8', description: 'Oitava chave para rotação' },
        { key: 'gemini_9', name: 'Gemini Chave 9', description: 'Nona chave para rotação' },
        { key: 'gemini_10', name: 'Gemini Chave 10', description: 'Décima chave para rotação' }
      ]
    },
    {
      title: 'Text-to-Speech (TTS)',
      icon: Volume2,
      apis: [
        { key: 'elevenlabs', name: 'ElevenLabs', description: 'Melhor qualidade de voz' }
      ]
    },
    {
      title: 'Geração de Imagens',
      icon: Image,
      apis: [
        { key: 'together', name: 'Together.ai FLUX', description: 'Gratuito - Recomendado' }
      ]
    }
  ]

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckCircle size={16} className="text-green-400" />
      case 'error':
        return <XCircle size={16} className="text-red-400" />
      case 'testing':
        return <RefreshCw size={16} className="text-blue-400 animate-spin" />
      default:
        return <AlertCircle size={16} className="text-gray-400" />
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'connected':
        return 'Conectado'
      case 'error':
        return 'Erro'
      case 'testing':
        return 'Testando...'
      default:
        return 'Não testado'
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Configurações</h1>
            <p className="text-gray-400 mt-1">
              Configure APIs, preferências e parâmetros do sistema
            </p>
          </div>
          {unsavedChanges && (
            <button
              onClick={saveApiKeys}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
            >
              <Save size={18} />
              <span>Salvar Alterações</span>
            </button>
          )}
        </div>

      {/* Tabs */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="border-b border-gray-700">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-400'
                      : 'border-transparent text-gray-400 hover:text-gray-300'
                  }`}
                >
                  <Icon size={18} />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* APIs Tab */}
          {activeTab === 'apis' && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-white mb-2">🔧 Configuração de APIs - ATUALIZADO</h2>
                <p className="text-gray-400">
                  Configure suas chaves de API para habilitar todas as funcionalidades.
                  <span className="text-yellow-400">🔄 Agora com suporte para múltiplas chaves Gemini!</span>
                </p>
              </div>
              
              {/* DEBUG: Mostrando total de seções */}
              <div className="mb-4 p-3 bg-yellow-900 border border-yellow-600 rounded">
                <p className="text-yellow-200">🔍 DEBUG: Total de seções: {apiSections.length}</p>
                <p className="text-yellow-200">📝 Seções: {apiSections.map(s => s.title).join(', ')}</p>
              </div>

              {apiSections.map((section, index) => (
                <div key={section.title} className="mb-8">
                  <div className="flex items-center space-x-2 mb-4">
                    <section.icon size={20} className="text-blue-400" />
                    <h3 className="text-lg font-semibold text-white">
                      {section.title} {section.title.includes('Gemini') && '🎯 NOVA SEÇÃO!'}
                    </h3>
                  </div>
                  {section.description && (
                    <p className="text-gray-400 mb-4">{section.description}</p>
                  )}
                  <div className="space-y-4">
                    {section.apis.map((api) => (
                      <div key={api.key} className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <div className="flex items-center space-x-2">
                              <h4 className="font-medium text-white">{api.name}</h4>
                              {api.required && <span className="text-xs bg-red-600 text-white px-2 py-1 rounded">Obrigatório</span>}
                              {getStatusIcon(apiStatus[api.key])}
                              <span className="text-xs text-gray-400">{getStatusText(apiStatus[api.key])}</span>
                            </div>
                            <p className="text-sm text-gray-400 mt-1">{api.description}</p>
                          </div>
                          <button
                            onClick={() => testApiConnection(api.key, true)}
                            disabled={testingApi === api.key}
                            className="px-3 py-1 bg-gray-600 text-gray-300 rounded-lg hover:bg-gray-500 transition-colors text-sm flex items-center space-x-1 disabled:opacity-50"
                          >
                            <TestTube size={14} />
                            <span>{testingApi === api.key ? 'Testando...' : 'Testar'}</span>
                          </button>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="relative flex-1">
                            <input
                              type={showPasswords[api.key] ? 'text' : 'password'}
                              placeholder={`Chave da API ${api.name}`}
                              value={apiKeys[api.key]}
                              onChange={(e) => handleApiKeyChange(api.key, e.target.value)}
                              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-10"
                            />
                            <button
                              type="button"
                              onClick={() => togglePasswordVisibility(api.key)}
                              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                            >
                              {showPasswords[api.key] ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}

              {/* Status da Rotação de Chaves Gemini */}
              <div className="mt-8 bg-gray-700 rounded-lg p-4 border border-gray-600">
                <div className="flex items-center space-x-2 mb-4">
                  <RefreshCw size={20} className="text-cyan-400" />
                  <h3 className="text-lg font-semibold text-white">Status da Rotação Gemini</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-800 rounded p-3">
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Chaves Configuradas</h4>
                    <div className="space-y-1">
                      {[1,2,3,4,5,6,7,8,9,10].map(num => {
                        const key = `gemini_${num}`
                        const hasKey = apiKeys[key] && apiKeys[key].length > 10
                        return (
                          <div key={key} className="flex items-center space-x-2 text-xs">
                            {hasKey ? (
                              <CheckCircle size={12} className="text-green-400" />
                            ) : (
                              <XCircle size={12} className="text-gray-500" />
                            )}
                            <span className={hasKey ? 'text-green-300' : 'text-gray-500'}>
                              Chave {num}: {hasKey ? 'Configurada' : 'Não configurada'}
                            </span>
                          </div>
                        )
                      })}
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded p-3">
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Informações</h4>
                    <div className="space-y-1 text-xs text-gray-400">
                      <div>• Limite por chave: 15 requisições/dia</div>
                      <div>• Rotação automática por uso</div>
                      <div>• Reset diário às 00:00</div>
                      <div>• Usado para TTS Gemini</div>
                    </div>
                  </div>
                </div>

                <div className="mt-3 text-xs text-gray-400">
                  💡 <strong>Dica:</strong> Configure pelo menos 3-5 chaves para evitar limites de cota durante uso intenso.
                </div>
              </div>
            </div>
          )}

          {/* Other Tabs */}
          {activeTab === 'system' && (
            <div className="text-center py-12">
              <SettingsIcon size={48} className="text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Configurações do Sistema</h3>
              <p className="text-gray-400">Em desenvolvimento</p>
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="text-center py-12">
              <FileText size={48} className="text-blue-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Logs do Sistema</h3>
              <p className="text-gray-400 mb-4">Acesse a página dedicada de logs</p>
              <button
                onClick={() => window.location.href = '/logs'}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Ir para Logs
              </button>
            </div>
          )}

          {activeTab === 'tests' && (
            <div className="text-center py-12">
              <TestTube size={48} className="text-green-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Testes de API</h3>
              <p className="text-gray-400 mb-4">Acesse a página dedicada para testes</p>
              <button
                onClick={() => window.location.href = '/api-tests'}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Ir para Testes
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Settings
