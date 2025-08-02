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

  // Estados para teste Kokoro TTS
  const [kokoroUrl, setKokoroUrl] = useState('http://localhost:8880')
  const [kokoroVoice, setKokoroVoice] = useState('af_bella')
  const [kokoroLanguage, setKokoroLanguage] = useState('en')
  const [kokoroText, setKokoroText] = useState('Olá! Este é um teste do Kokoro TTS. A qualidade do áudio é excelente e funciona 100% local!')
  const [kokoroResult, setKokoroResult] = useState(null)
  const [kokoroLoading, setKokoroLoading] = useState(false)

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
    },
    {
      id: 'gemini_tts',
      name: 'Gemini TTS',
      icon: Volume2,
      color: 'cyan',
      description: 'Teste de síntese de voz com Google Gemini',
      tests: [
        {
          name: 'Teste Básico',
          endpoint: '/api/automations/generate-tts',
          params: {
            text: 'Olá, este é um teste de áudio com Gemini TTS. A qualidade do áudio é excelente!',
            voice_name: 'Aoede',
            model: 'gemini-2.5-flash-preview-tts'
          }
        },
        {
          name: 'Teste com Voz Masculina',
          endpoint: '/api/automations/generate-tts',
          params: {
            text: 'Este é um teste com voz masculina do Gemini TTS.',
            voice_name: 'Charon',
            model: 'gemini-2.5-flash-preview-tts'
          }
        },
        {
          name: 'Teste Texto Longo',
          endpoint: '/api/automations/generate-tts',
          params: {
            text: 'Este é um teste com texto mais longo para verificar a qualidade e estabilidade do Gemini TTS. O sistema deve processar este texto corretamente e gerar um áudio de alta qualidade. Vamos testar diferentes aspectos da síntese de voz.',
            voice_name: 'Kore',
            model: 'gemini-2.5-flash-preview-tts'
          }
        }
      ]
    },
    {
      id: 'kokoro',
      name: 'Kokoro TTS',
      icon: Zap,
      color: 'green',
      description: 'Teste de síntese de voz local com Kokoro FastAPI',
      tests: [
        {
          name: 'Teste de Conexão',
          endpoint: '/api/automations/test-kokoro',
          params: {
            kokoro_url: 'http://localhost:8880'
          }
        },
        {
          name: 'Gerar Áudio Básico',
          endpoint: '/api/automations/generate-tts-kokoro',
          params: {
            text: 'Olá! Este é um teste do Kokoro TTS. A qualidade do áudio é excelente e funciona 100% local!',
            voice: 'af_bella',
            kokoro_url: 'http://localhost:8880',
            speed: 1.0
          }
        },
        {
          name: 'Teste com Voz Masculina',
          endpoint: '/api/automations/generate-tts-kokoro',
          params: {
            text: 'Este é um teste com voz masculina do Kokoro TTS. O sistema funciona completamente offline.',
            voice: 'am_adam',
            kokoro_url: 'http://localhost:8880',
            speed: 1.0
          }
        },
        {
          name: 'Teste Velocidade Rápida',
          endpoint: '/api/automations/generate-tts-kokoro',
          params: {
            text: 'Este teste verifica a síntese de voz em velocidade acelerada. Kokoro TTS é rápido e eficiente!',
            voice: 'af_sarah',
            kokoro_url: 'http://localhost:8880',
            speed: 1.5
          }
        },
        {
          name: 'Teste Português Feminino',
          endpoint: '/api/automations/generate-tts-kokoro',
          params: {
            text: 'Olá! Este é um teste em português. O Kokoro TTS suporta múltiplos idiomas com excelente qualidade.',
            voice: 'pf_dora',
            kokoro_url: 'http://localhost:8880',
            speed: 1.0,
            language: 'pt'
          }
        },
        {
          name: 'Teste Português Masculino',
          endpoint: '/api/automations/generate-tts-kokoro',
          params: {
            text: 'Bem-vindos ao sistema de síntese de voz em português. Esta é uma demonstração da voz masculina portuguesa.',
            voice: 'pm_alex',
            kokoro_url: 'http://localhost:8880',
            speed: 1.0,
            language: 'pt'
          }
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
    // Para Gemini TTS, usar a chave gemini_1 ou gemini
    let apiKey = apiKeys[apiId]
    if (apiId === 'gemini_tts') {
      apiKey = apiKeys.gemini_1 || apiKeys.gemini || apiKeys['gemini_1'] || apiKeys['gemini'] || 'AIzaSyBqUjzLHNPycDIzvwnI5JisOwmNubkfRRc'
    }

    // Kokoro TTS não precisa de chave de API
    if (apiId !== 'kokoro' && !apiKey) {
      alert(`Configure a chave da API ${apiId === 'gemini_tts' ? 'Gemini' : apiId} primeiro nas Configurações`)
      return
    }

    setTesting(true)
    const testKey = `${apiId}_${test.name}`

    try {
      let response, data

      // Tratamento especial para Kokoro TTS
      if (apiId === 'kokoro') {
        console.log('🎵 Testando Kokoro TTS...')

        // Usar configurações dinâmicas do usuário
        let requestParams = { ...test.params }
        if (test.name !== 'Teste de Conexão') {
          requestParams = {
            ...requestParams,
            text: kokoroText,
            voice: kokoroVoice,
            kokoro_url: kokoroUrl,
            language: kokoroLanguage
          }
        } else {
          requestParams.kokoro_url = kokoroUrl
        }

        response = await fetch(test.endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestParams)
        })
        data = await response.json()

        // Adicionar informações extras para Kokoro TTS
        if (data.success) {
          if (test.name === 'Teste de Conexão') {
            data.connection_info = {
              url: data.url,
              voices_count: data.voices_count,
              status: 'Conectado com sucesso'
            }
          } else if (data.filename) {
            data.audio_info = {
              filename: data.filename,
              voice_used: kokoroVoice,
              text_length: kokoroText.length,
              kokoro_url: kokoroUrl,
              local_generation: true
            }
          }
        }
      }
      // Tratamento especial para Gemini TTS
      else if (apiId === 'gemini_tts') {
        console.log('🎵 Testando Gemini TTS...')
        response = await fetch(test.endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ...test.params,
            api_key: apiKey
          })
        })
        data = await response.json()

        // Adicionar informações extras para TTS
        if (data.success && data.data) {
          data.audio_info = {
            filename: data.data.filename,
            size_kb: Math.round(data.data.size / 1024),
            voice: data.data.voice_used,
            model: data.data.model_used,
            text_length: data.data.text_length
          }
        }
      } else {
        // Teste padrão para outras APIs
        response = await fetch('http://localhost:5000/api/tests/run-api-test', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            api_id: apiId,
            api_key: apiKey,
            test_name: test.name,
            endpoint: test.endpoint,
            params: test.params
          })
        })
        data = await response.json()
      }

      setTestResults(prev => ({
        ...prev,
        [testKey]: {
          ...data,
          timestamp: new Date().toISOString()
        }
      }))

    } catch (error) {
      console.error(`❌ Erro no teste ${apiId}:`, error)
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
                    currentApi.id === 'kokoro'
                      ? 'bg-blue-600 text-white'
                      : apiKeys[currentApi.id]
                        ? 'bg-green-600 text-white'
                        : 'bg-red-600 text-white'
                  }`}>
                    {currentApi.id === 'kokoro'
                      ? 'Servidor Local (http://localhost:8880)'
                      : apiKeys[currentApi.id]
                        ? 'API Configurada'
                        : 'API Não Configurada'
                    }
                  </span>
                </div>
              </div>

              {/* Configuração especial para Kokoro TTS */}
              {currentApi.id === 'kokoro' && (
                <div className="bg-blue-900/20 border border-blue-600 rounded-lg p-4 mb-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Zap className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-semibold text-white">Configuração Kokoro TTS</h3>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        URL do Servidor Kokoro
                      </label>
                      <input
                        type="text"
                        value={kokoroUrl}
                        onChange={(e) => setKokoroUrl(e.target.value)}
                        placeholder="http://localhost:8880"
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Idioma
                        </label>
                        <select
                          value={kokoroLanguage}
                          onChange={(e) => {
                            const newLanguage = e.target.value
                            const defaultVoice = newLanguage === 'pt' ? 'pf_dora' : 'af_bella'
                            const defaultText = newLanguage === 'pt'
                              ? 'Olá! Este é um teste do Kokoro TTS em português. A qualidade é excelente!'
                              : 'Hello! This is a Kokoro TTS test in English. The quality is excellent!'
                            setKokoroLanguage(newLanguage)
                            setKokoroVoice(defaultVoice)
                            setKokoroText(defaultText)
                          }}
                          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="en">🇺🇸 Inglês</option>
                          <option value="pt">🇧🇷 Português</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Voz para Teste
                        </label>
                        <select
                          value={kokoroVoice}
                          onChange={(e) => setKokoroVoice(e.target.value)}
                          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          {kokoroLanguage === 'pt' ? (
                            <>
                              <option value="pf_dora">🇵🇹 pf_dora - Feminina Portuguesa</option>
                              <option value="pm_alex">🇵🇹 pm_alex - Masculina Portuguesa</option>
                              <option value="pm_santa">🇵🇹 pm_santa - Masculina Portuguesa (Santa)</option>
                            </>
                          ) : (
                            <>
                              <option value="af_bella">af_bella - Feminina Americana</option>
                              <option value="af_sarah">af_sarah - Feminina Americana</option>
                              <option value="af_nicole">af_nicole - Feminina Americana</option>
                              <option value="af_sky">af_sky - Feminina Americana</option>
                              <option value="am_adam">am_adam - Masculina Americana</option>
                              <option value="am_michael">am_michael - Masculina Americana</option>
                              <option value="bf_emma">bf_emma - Feminina Britânica</option>
                              <option value="bm_george">bm_george - Masculina Britânica</option>
                            </>
                          )}
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Texto para Teste
                        </label>
                        <input
                          type="text"
                          value={kokoroText}
                          onChange={(e) => setKokoroText(e.target.value)}
                          placeholder="Texto para testar..."
                          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>

                    <div className="bg-gray-800 rounded-lg p-3">
                      <h4 className="text-sm font-medium text-white mb-2">📋 Como instalar Kokoro TTS:</h4>
                      <div className="text-xs text-gray-300 space-y-1">
                        <p><strong>Opção 1 (Docker CPU):</strong></p>
                        <code className="bg-gray-900 px-2 py-1 rounded text-green-400">
                          docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
                        </code>
                        <p><strong>Opção 2 (Docker GPU):</strong></p>
                        <code className="bg-gray-900 px-2 py-1 rounded text-green-400">
                          docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest
                        </code>
                      </div>
                    </div>
                  </div>
                </div>
              )}

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

                            {/* Informações específicas do TTS */}
                            {currentApi.id === 'gemini_tts' && result.success && result.audio_info && (
                              <div className="mb-3 bg-green-900/20 border border-green-500/30 rounded p-3">
                                <h5 className="text-sm font-medium text-green-300 mb-2">🎵 Áudio Gerado:</h5>
                                <div className="grid grid-cols-2 gap-2 text-xs text-green-200">
                                  <div>📁 <strong>Arquivo:</strong> {result.audio_info.filename}</div>
                                  <div>📏 <strong>Tamanho:</strong> {result.audio_info.size_kb} KB</div>
                                  <div>🎵 <strong>Voz:</strong> {result.audio_info.voice}</div>
                                  <div>🤖 <strong>Modelo:</strong> {result.audio_info.model}</div>
                                  <div className="col-span-2">📝 <strong>Caracteres:</strong> {result.audio_info.text_length}</div>
                                </div>
                              </div>
                            )}

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
