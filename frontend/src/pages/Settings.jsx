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
    elevenlabs: '',
    together: '',
    rapidapi: ''
  })
  const [apiStatus, setApiStatus] = useState({
    openai: 'unknown',
    gemini_1: 'unknown', 
    elevenlabs: 'unknown',
    together: 'unknown',
    rapidapi: 'unknown'
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
      const response = await fetch('http://localhost:5000/api/settings/save-apis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_keys: apiKeys })
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

  const apiSections = [
    {
      title: 'Extração de Conteúdo',
      icon: Youtube,
      apis: [
        { key: 'rapidapi', name: 'RapidAPI YouTube V2', description: 'Extração de títulos e dados do YouTube', required: true }
      ]
    },
    {
      title: 'Modelos de Texto/Roteiro',
      icon: Zap,
      apis: [
        { key: 'openai', name: 'OpenAI GPT-4', description: 'Melhor qualidade para títulos e roteiros' },
        { key: 'gemini_1', name: 'Google Gemini', description: 'Gratuito - Recomendado' }
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
    <div className="space-y-6">
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
                <h2 className="text-2xl font-bold text-white mb-2">Configuração de APIs</h2>
                <p className="text-gray-400">
                  Configure suas chaves de API para habilitar todas as funcionalidades
                </p>
              </div>
              
              {apiSections.map((section) => (
                <div key={section.title} className="mb-8">
                  <div className="flex items-center space-x-2 mb-4">
                    <section.icon size={20} className="text-blue-400" />
                    <h3 className="text-lg font-semibold text-white">{section.title}</h3>
                  </div>
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
