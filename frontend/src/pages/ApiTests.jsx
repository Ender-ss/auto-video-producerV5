/**
 * 🧪 API Tests Page
 * 
 * Página para testar APIs individualmente
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Play,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle,
  Copy,
  Download,
  Youtube,
  Zap,
  Volume2,
  Image,
  TestTube,
  Code,
  Clock
} from 'lucide-react'

const ApiTests = () => {
  const [activeTest, setActiveTest] = useState('rapidapi')
  const [testResults, setTestResults] = useState({})
  const [testing, setTesting] = useState(false)
  const [apiKeys, setApiKeys] = useState({})

  const apiTests = [
    {
      id: 'rapidapi',
      name: 'RapidAPI YouTube V2',
      icon: Youtube,
      color: 'red',
      description: 'Teste de extração de dados do YouTube',
      tests: [
        {
          name: 'Buscar ID do Canal',
          endpoint: '/channel/id',
          params: { channel_name: 'MrBeast' }
        },
        {
          name: 'Detalhes do Canal',
          endpoint: '/channel/details',
          params: { channel_id: 'UCX6OQ3DkcsbYNE6H8uQQuVA' }
        },
        {
          name: 'Vídeos do Canal',
          endpoint: '/channel/videos',
          params: { channel_id: 'UCX6OQ3DkcsbYNE6H8uQQuVA', max_results: 5 }
        }
      ]
    },
    {
      id: 'openai',
      name: 'OpenAI GPT-4',
      icon: Zap,
      color: 'green',
      description: 'Teste de geração de texto com IA',
      tests: [
        {
          name: 'Geração de Título',
          endpoint: '/generate/title',
          params: { prompt: 'Como ganhar dinheiro online' }
        },
        {
          name: 'Geração de Roteiro',
          endpoint: '/generate/script',
          params: { title: 'Como Ganhar R$ 10.000 Por Mês', chapters: 5 }
        }
      ]
    },
    {
      id: 'gemini',
      name: 'Google Gemini',
      icon: Zap,
      color: 'blue',
      description: 'Teste de geração de texto com Gemini',
      tests: [
        {
          name: 'Geração de Título',
          endpoint: '/generate/title',
          params: { prompt: 'Motivação para empreendedores' }
        }
      ]
    },
    {
      id: 'elevenlabs',
      name: 'ElevenLabs TTS',
      icon: Volume2,
      color: 'purple',
      description: 'Teste de síntese de voz',
      tests: [
        {
          name: 'Listar Vozes',
          endpoint: '/voices',
          params: {}
        },
        {
          name: 'Gerar Áudio',
          endpoint: '/text-to-speech',
          params: { text: 'Olá, este é um teste de voz.', voice_id: 'default' }
        }
      ]
    }
  ]

  useEffect(() => {
    // Carregar chaves de API salvas
    const savedKeys = localStorage.getItem('api_keys')
    if (savedKeys) {
      setApiKeys(JSON.parse(savedKeys))
    }
  }, [])

  const runTest = async (apiId, test) => {
    if (!apiKeys[apiId]) {
      alert('Configure a chave da API primeiro nas Configurações')
      return
    }

    setTesting(true)
    const testKey = `${apiId}_${test.name}`

    try {
      const response = await fetch('http://localhost:5000/api/tests/run-api-test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_id: apiId,
          api_key: apiKeys[apiId],
          test_name: test.name,
          endpoint: test.endpoint,
          params: test.params
        })
      })

      const data = await response.json()
      
      setTestResults(prev => ({
        ...prev,
        [testKey]: {
          ...data,
          timestamp: new Date().toISOString()
        }
      }))

    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [testKey]: {
          success: false,
          error: error.message,
          timestamp: new Date().toISOString()
        }
      }))
    } finally {
      setTesting(false)
    }
  }

  const runAllTests = async (apiId) => {
    const api = apiTests.find(a => a.id === apiId)
    if (!api) return

    for (const test of api.tests) {
      await runTest(apiId, test)
      // Pequena pausa entre testes
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
  }

  const copyResult = (result) => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2))
    alert('Resultado copiado para a área de transferência!')
  }

  const downloadResults = () => {
    const results = JSON.stringify(testResults, null, 2)
    const blob = new Blob([results], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `api-test-results-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const getStatusIcon = (success) => {
    if (success === undefined) return <AlertCircle size={16} className="text-gray-400" />
    return success ? 
      <CheckCircle size={16} className="text-green-400" /> : 
      <XCircle size={16} className="text-red-400" />
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('pt-BR')
  }

  const currentApi = apiTests.find(api => api.id === activeTest)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Testes de API</h1>
          <p className="text-gray-400 mt-1">
            Teste individualmente cada API para diagnosticar problemas
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => runAllTests(activeTest)}
            disabled={testing}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 disabled:opacity-50"
          >
            <Play size={18} />
            <span>Executar Todos</span>
          </button>
          <button
            onClick={downloadResults}
            className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2"
          >
            <Download size={18} />
            <span>Baixar Resultados</span>
          </button>
        </div>
      </div>

      {/* API Tabs */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="border-b border-gray-700">
          <nav className="flex space-x-8 px-6">
            {apiTests.map((api) => {
              const Icon = api.icon
              return (
                <button
                  key={api.id}
                  onClick={() => setActiveTest(api.id)}
                  className={`flex items-center space-x-2 py-4 border-b-2 font-medium text-sm transition-colors ${
                    activeTest === api.id
                      ? `border-${api.color}-500 text-${api.color}-400`
                      : 'border-transparent text-gray-400 hover:text-gray-300'
                  }`}
                >
                  <Icon size={18} />
                  <span>{api.name}</span>
                </button>
              )
            })}
          </nav>
        </div>

        <div className="p-6">
          {currentApi && (
            <div className="space-y-6">
              {/* API Info */}
              <div className="bg-gray-700 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-2">
                  <currentApi.icon size={24} className={`text-${currentApi.color}-400`} />
                  <h2 className="text-xl font-semibold text-white">{currentApi.name}</h2>
                </div>
                <p className="text-gray-400">{currentApi.description}</p>
                <div className="mt-3">
                  <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${
                    apiKeys[currentApi.id] 
                      ? 'bg-green-600 text-white' 
                      : 'bg-red-600 text-white'
                  }`}>
                    {apiKeys[currentApi.id] ? 'API Configurada' : 'API Não Configurada'}
                  </span>
                </div>
              </div>

              {/* Tests */}
              <div className="space-y-4">
                {currentApi.tests.map((test, index) => {
                  const testKey = `${currentApi.id}_${test.name}`
                  const result = testResults[testKey]
                  
                  return (
                    <motion.div
                      key={test.name}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="bg-gray-700 rounded-lg border border-gray-600"
                    >
                      <div className="p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <TestTube size={20} className="text-blue-400" />
                            <div>
                              <h3 className="font-medium text-white">{test.name}</h3>
                              <p className="text-sm text-gray-400">
                                {test.endpoint} • {Object.keys(test.params).length} parâmetros
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            {result && (
                              <div className="flex items-center space-x-2">
                                {getStatusIcon(result.success)}
                                <span className="text-xs text-gray-400">
                                  <Clock size={12} className="inline mr-1" />
                                  {formatTimestamp(result.timestamp)}
                                </span>
                              </div>
                            )}
                            <button
                              onClick={() => runTest(currentApi.id, test)}
                              disabled={testing}
                              className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm disabled:opacity-50"
                            >
                              {testing ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} />}
                            </button>
                          </div>
                        </div>

                        {/* Parameters */}
                        <div className="mb-3">
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Parâmetros:</h4>
                          <div className="bg-gray-800 rounded p-3">
                            <pre className="text-xs text-gray-300 font-mono">
                              {JSON.stringify(test.params, null, 2)}
                            </pre>
                          </div>
                        </div>

                        {/* Result */}
                        {result && (
                          <div>
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="text-sm font-medium text-gray-300">Resultado:</h4>
                              <button
                                onClick={() => copyResult(result)}
                                className="text-gray-400 hover:text-white"
                              >
                                <Copy size={14} />
                              </button>
                            </div>
                            <div className={`bg-gray-800 rounded p-3 border-l-4 ${
                              result.success ? 'border-green-400' : 'border-red-400'
                            }`}>
                              <pre className="text-xs text-gray-300 font-mono max-h-40 overflow-y-auto">
                                {JSON.stringify(result, null, 2)}
                              </pre>
                            </div>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ApiTests
