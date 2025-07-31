/**
 * 🤖 Automations Page
 * 
 * Página de automações de conteúdo
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Play,
  Pause,
  Settings,
  Youtube,
  Wand2,
  FileText,
  Mic,
  Image,
  Video,
  Download,
  RefreshCw,
  Plus,
  Trash2,
  Edit,
  Eye,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
  Bot,
  Sparkles,
  Target,
  Layers,
  Workflow,
  XCircle,
  Copy,
  Calendar
} from 'lucide-react'

const Automations = () => {
  const [activeTab, setActiveTab] = useState('youtube')
  const [isProcessing, setIsProcessing] = useState(false)
  const [results, setResults] = useState(null)

  // Estados para geração de títulos
  const [isGeneratingTitles, setIsGeneratingTitles] = useState(false)
  const [generatedTitles, setGeneratedTitles] = useState(null)
  const [titleGenerationConfig, setTitleGenerationConfig] = useState({
    topic: '',
    count: 10,
    style: 'viral',
    ai_provider: 'auto'
  })
  const [useCustomPrompt, setUseCustomPrompt] = useState(false)
  const [customPrompt, setCustomPrompt] = useState('')

  // Estado para o formulário de extração do YouTube
  const [formData, setFormData] = useState({
    url: '',
    max_titles: 10,
    min_views: 1000,
    max_views: '',
    days: 30
  })

  const [apiKeys, setApiKeys] = useState({})
  const [apiStatus, setApiStatus] = useState({
    rapidapi: 'unknown'
  })

  // Carregar chaves de API do backend
  useEffect(() => {
    const loadApiKeys = async () => {
      try {
        // Primeiro tentar carregar do localStorage
        const savedKeys = localStorage.getItem('api_keys')
        if (savedKeys) {
          const keys = JSON.parse(savedKeys)
          setApiKeys(keys)

          if (keys.rapidapi) {
            checkApiStatus()
            return
          }
        }

        // Se não tiver no localStorage, carregar do backend
        const response = await fetch('http://localhost:5000/api/settings/api-keys')
        if (response.ok) {
          const data = await response.json()
          if (data.success && data.keys) {
            setApiKeys(data.keys)

            // Salvar no localStorage para próximas vezes
            localStorage.setItem('api_keys', JSON.stringify(data.keys))

            if (data.keys.rapidapi) {
              checkApiStatus()
            }
          }
        }
      } catch (error) {
        console.error('Erro ao carregar chaves da API:', error)
      }
    }

    loadApiKeys()
  }, [])

  const checkApiStatus = async () => {
    const savedKeys = localStorage.getItem('api_keys')
    if (!savedKeys) return

    const keys = JSON.parse(savedKeys)
    if (!keys.rapidapi) return

    setApiStatus(prev => ({ ...prev, rapidapi: 'testing' }))

    try {
      const response = await fetch('http://localhost:5000/api/automations/test-rapidapi', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: keys.rapidapi
        })
      })

      const data = await response.json()

      setApiStatus(prev => ({
        ...prev,
        rapidapi: data.success ? 'connected' : 'error'
      }))
    } catch (error) {
      setApiStatus(prev => ({ ...prev, rapidapi: 'error' }))
    }
  }

  // Função para formatar números
  const formatNumber = (num) => {
    if (!num) return '0'
    
    const number = parseInt(num)
    if (number >= 1000000000) {
      return (number / 1000000000).toFixed(1) + 'B'
    } else if (number >= 1000000) {
      return (number / 1000000).toFixed(1) + 'M'
    } else if (number >= 1000) {
      return (number / 1000).toFixed(1) + 'K'
    }
    return number.toString()
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleTestAPI = async () => {
    if (!apiKeys.rapidapi) {
      alert('Configure a chave RapidAPI nas Configurações primeiro')
      return
    }

    await checkApiStatus()
  }

  const handleExtractContent = async () => {
    if (!formData.url.trim()) {
      alert('Por favor, insira o nome ou ID do canal do YouTube')
      return
    }

    if (!apiKeys.rapidapi) {
      alert('Configure a chave RapidAPI nas Configurações primeiro')
      return
    }

    setIsProcessing(true)
    setResults(null) // Limpar resultados anteriores

    try {
      // Timeout maior para a requisição (2 minutos)
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 120000) // 2 minutos

      const response = await fetch('http://localhost:5000/api/automations/extract-youtube', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: formData.url,
          api_key: apiKeys.rapidapi,
          config: {
            max_titles: parseInt(formData.max_titles),
            min_views: parseInt(formData.min_views),
            max_views: formData.max_views ? parseInt(formData.max_views) : 0,
            days: parseInt(formData.days)
          }
        }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)
      const data = await response.json()

      if (data.success) {
        setResults(data.data)
        if (data.data.total_videos === 0) {
          alert('⚠️ Nenhum vídeo encontrado com os filtros aplicados. Tente diminuir o filtro de views mínimas.')
        }
      } else {
        alert(`❌ Erro: ${data.error}`)
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        alert('⏱️ Operação cancelada por timeout. A API está demorando muito para responder.')
      } else {
        alert(`❌ Erro de conexão: ${error.message}`)
      }
    } finally {
      setIsProcessing(false)
    }
  }

  const handleGenerateTitles = async () => {
    // Validações
    if (useCustomPrompt) {
      if (!customPrompt.trim()) {
        alert('Por favor, insira o prompt personalizado')
        return
      }
    } else {
      if (!titleGenerationConfig.topic.trim()) {
        alert('Por favor, insira o tópico para geração de títulos')
        return
      }
    }

    if (!results || !results.videos || results.videos.length === 0) {
      alert('Primeiro extraia títulos do YouTube para usar como base')
      return
    }

    setIsGeneratingTitles(true)
    setGeneratedTitles(null)

    try {
      // Extrair títulos dos resultados para usar como base
      const sourceTitles = results.videos.map(video => video.title)

      // Escolher endpoint baseado no tipo de geração
      const endpoint = useCustomPrompt
        ? 'http://localhost:5000/api/automations/generate-titles-custom'
        : 'http://localhost:5000/api/automations/generate-titles'

      // Preparar payload baseado no tipo
      const payload = useCustomPrompt
        ? {
            source_titles: sourceTitles,
            custom_prompt: customPrompt,
            count: parseInt(titleGenerationConfig.count),
            ai_provider: titleGenerationConfig.ai_provider
          }
        : {
            source_titles: sourceTitles,
            topic: titleGenerationConfig.topic,
            count: parseInt(titleGenerationConfig.count),
            style: titleGenerationConfig.style,
            ai_provider: titleGenerationConfig.ai_provider
          }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      })

      const data = await response.json()

      if (data.success) {
        setGeneratedTitles(data.data)
        alert(`✅ ${data.data.total_generated} títulos gerados com sucesso!`)
      } else {
        alert(`❌ Erro: ${data.error}`)
      }
    } catch (error) {
      alert(`❌ Erro de conexão: ${error.message}`)
    } finally {
      setIsGeneratingTitles(false)
    }
  }

  const handleTitleConfigChange = (field, value) => {
    setTitleGenerationConfig(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const copyTitleToClipboard = (title) => {
    navigator.clipboard.writeText(title)
    alert('Título copiado para a área de transferência!')
  }

  // Mock data para demonstração
  const automationTabs = [
    { id: 'youtube', label: 'Extração YouTube', icon: Youtube, color: 'red' },
    { id: 'titles', label: 'Geração de Títulos', icon: Wand2, color: 'blue' },
    { id: 'scripts', label: 'Roteiros IA', icon: FileText, color: 'green' },
    { id: 'premise', label: 'Premissas', icon: Target, color: 'purple' },
    { id: 'tts', label: 'Text-to-Speech', icon: Mic, color: 'yellow' },
    { id: 'workflow', label: 'Fluxos Completos', icon: Workflow, color: 'indigo' }
  ]

  const aiAgents = [
    { id: 'gemini', name: 'Google Gemini', status: 'connected', cost: 'Gratuito' },
    { id: 'openai', name: 'OpenAI GPT-4', status: 'connected', cost: '$0.03/1K tokens' },
    { id: 'claude', name: 'Anthropic Claude', status: 'disconnected', cost: '$0.015/1K tokens' },
    { id: 'openrouter', name: 'OpenRouter', status: 'connected', cost: 'Variável' }
  ]

  const renderYouTubeExtraction = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Youtube size={24} className="text-red-400" />
          <span>Extração de Conteúdo do YouTube</span>
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Canal do YouTube
              </label>
              <input
                type="text"
                value={formData.url}
                onChange={(e) => handleInputChange('url', e.target.value)}
                placeholder="CanalClaYOliveiraOficial ou UCykzGI8qdfLywefslXnnyGw"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
              />
              <div className="mt-2 p-3 bg-green-900/30 border border-green-700 rounded-lg">
                <p className="text-green-300 text-sm font-medium mb-1">
                  ✅ Você pode usar:
                </p>
                <ul className="text-green-200 text-xs space-y-1">
                  <li>• <strong>Nome do canal:</strong> CanalClaYOliveiraOficial</li>
                  <li>• <strong>Handle:</strong> @CanalClaYOliveiraOficial</li>
                  <li>• <strong>ID do canal:</strong> UCykzGI8qdfLywefslXnnyGw</li>
                  <li>• <strong>URL completa:</strong> https://youtube.com/@CanalClaYOliveiraOficial</li>
                </ul>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Status da API RapidAPI
              </label>
              <div className="flex items-center justify-between bg-gray-700 border border-gray-600 rounded-lg p-3">
                <div className="flex items-center space-x-3">
                  {apiStatus.rapidapi === 'connected' && (
                    <>
                      <CheckCircle size={20} className="text-green-400" />
                      <span className="text-green-400 font-medium">Conectado</span>
                    </>
                  )}
                  {apiStatus.rapidapi === 'error' && (
                    <>
                      <XCircle size={20} className="text-red-400" />
                      <span className="text-red-400 font-medium">Erro de conexão</span>
                    </>
                  )}
                  {apiStatus.rapidapi === 'testing' && (
                    <>
                      <RefreshCw size={20} className="text-blue-400 animate-spin" />
                      <span className="text-blue-400 font-medium">Testando...</span>
                    </>
                  )}
                  {apiStatus.rapidapi === 'unknown' && (
                    <>
                      <AlertCircle size={20} className="text-gray-400" />
                      <span className="text-gray-400 font-medium">
                        {apiKeys.rapidapi ? 'Não testado' : 'Não configurado'}
                      </span>
                    </>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  {!apiKeys.rapidapi && (
                    <button
                      onClick={() => window.location.href = '/settings'}
                      className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
                    >
                      Configurar
                    </button>
                  )}
                  {apiKeys.rapidapi && (
                    <button
                      onClick={handleTestAPI}
                      disabled={apiStatus.rapidapi === 'testing'}
                      className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-500 transition-colors disabled:opacity-50"
                    >
                      Testar
                    </button>
                  )}
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Máx. Títulos
                </label>
                <input
                  type="number"
                  value={formData.max_titles}
                  onChange={(e) => handleInputChange('max_titles', e.target.value)}
                  min="1"
                  max="50"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Últimos Dias
                </label>
                <input
                  type="number"
                  value={formData.days}
                  onChange={(e) => handleInputChange('days', e.target.value)}
                  min="1"
                  max="365"
                  placeholder="30"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Min. Views
                </label>
                <input
                  type="number"
                  value={formData.min_views}
                  onChange={(e) => handleInputChange('min_views', e.target.value)}
                  min="0"
                  placeholder="1000"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Máx. Views
                </label>
                <input
                  type="number"
                  value={formData.max_views}
                  onChange={(e) => handleInputChange('max_views', e.target.value)}
                  min="0"
                  placeholder="Opcional"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <button
              onClick={handleExtractContent}
              disabled={isProcessing}
              className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {isProcessing ? (
                <>
                  <RefreshCw size={18} className="animate-spin" />
                  <span>Extraindo... (pode demorar até 2 min)</span>
                </>
              ) : (
                <>
                  <Youtube size={18} />
                  <span>Extrair Conteúdo</span>
                </>
              )}
            </button>
          </div>
          
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="font-medium text-white mb-3">Resultados da Extração</h4>
            {results ? (
              <div className="space-y-4">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Canal:</span>
                    <span className="text-white">{results.channel_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Títulos extraídos:</span>
                    <span className="text-green-400">{results.total_videos}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total de views:</span>
                    <span className="text-white">{formatNumber(results.total_views)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total de likes:</span>
                    <span className="text-white">{formatNumber(results.total_likes)}</span>
                  </div>
                </div>
                
                {results.videos && results.videos.length > 0 && (
                  <div className="mt-4">
                    <div className="flex items-center justify-between mb-3">
                      <h5 className="text-white font-medium">📝 Títulos Extraídos ({results.videos.length}):</h5>
                      <button
                        onClick={() => {
                          const titles = results.videos.map(v => v.title).join('\n')
                          navigator.clipboard.writeText(titles)
                          alert('✅ Todos os títulos copiados para a área de transferência!')
                        }}
                        className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 transition-colors flex items-center space-x-1"
                      >
                        <Copy size={12} />
                        <span>Copiar Todos</span>
                      </button>
                    </div>
                    <div className="max-h-80 overflow-y-auto space-y-2">
                      {results.videos.map((video, index) => (
                        <div key={index} className="bg-gray-600 rounded p-3 group hover:bg-gray-500 transition-colors">
                          <div className="flex items-start justify-between">
                            <div className="flex-1 pr-3">
                              <p className="text-white text-sm font-medium leading-relaxed mb-2">
                                {index + 1}. {video.title}
                              </p>
                              <div className="flex items-center space-x-3 text-xs text-gray-300">
                                <span className="flex items-center space-x-1">
                                  <Eye size={12} />
                                  <span>{formatNumber(video.views)} views</span>
                                </span>
                                {video.duration && (
                                  <span className="flex items-center space-x-1">
                                    <Clock size={12} />
                                    <span>{video.duration}</span>
                                  </span>
                                )}
                                {video.published_at && (
                                  <span className="flex items-center space-x-1">
                                    <Calendar size={12} />
                                    <span>{video.published_at}</span>
                                  </span>
                                )}
                              </div>
                            </div>
                            <button
                              onClick={() => {
                                navigator.clipboard.writeText(video.title)
                                alert('✅ Título copiado!')
                              }}
                              className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-white transition-all"
                              title="Copiar este título"
                            >
                              <Copy size={14} />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {results.videos && results.videos.length === 0 && (
                  <div className="mt-4 text-center py-8">
                    <FileText size={48} className="mx-auto mb-3 text-gray-500 opacity-50" />
                    <p className="text-gray-400 text-lg font-medium mb-2">Nenhum título encontrado</p>
                    <p className="text-gray-500 text-sm">
                      Tente ajustar os filtros:<br/>
                      • Diminuir views mínimas<br/>
                      • Aumentar período de busca<br/>
                      • Verificar se o canal tem vídeos recentes
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12">
                <FileText size={48} className="mx-auto mb-4 text-gray-500 opacity-50" />
                <h3 className="text-lg font-medium text-white mb-2">📝 Extrair Títulos de Vídeos</h3>
                <p className="text-gray-400 text-sm mb-4">
                  Configure os parâmetros e clique em "Extrair Conteúdo" para obter títulos de vídeos populares
                </p>
                <div className="text-xs text-gray-500 space-y-1">
                  <p>💡 <strong>Dica:</strong> Use os títulos extraídos como inspiração para criar seu próprio conteúdo</p>
                  <p>🎯 <strong>Objetivo:</strong> Encontrar títulos que performam bem no seu nicho</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )

  const renderTitleGeneration = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Wand2 size={24} className="text-blue-400" />
          <span>Geração de Títulos com IA</span>
        </h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Configuração */}
          <div className="space-y-4">
            {/* Toggle para prompt personalizado */}
            <div className="flex items-center space-x-3 p-3 bg-gray-700 rounded-lg border border-gray-600">
              <input
                type="checkbox"
                id="useCustomPrompt"
                checked={useCustomPrompt}
                onChange={(e) => setUseCustomPrompt(e.target.checked)}
                className="w-4 h-4 text-blue-600 bg-gray-600 border-gray-500 rounded focus:ring-blue-500"
              />
              <label htmlFor="useCustomPrompt" className="text-sm font-medium text-gray-300">
                🎨 Usar Prompt Personalizado (Remodelagem Avançada)
              </label>
            </div>

            {useCustomPrompt ? (
              /* Prompt Personalizado */
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Prompt Personalizado para Remodelagem
                </label>
                <textarea
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  placeholder="Ex: Transforme esses títulos em títulos mais chamativos para o nicho fitness, usando números específicos e palavras de urgência..."
                  rows={4}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
                <p className="text-xs text-gray-400 mt-1">
                  💡 Descreva como você quer que os títulos sejam remodelados baseado nos títulos extraídos
                </p>

                {/* Exemplos de prompts */}
                <div className="mt-2">
                  <p className="text-xs text-gray-500 mb-1">Exemplos de prompts:</p>
                  <div className="space-y-1">
                    <button
                      type="button"
                      onClick={() => setCustomPrompt("Transforme esses títulos em títulos mais chamativos para o nicho fitness, usando números específicos e palavras de urgência como 'RÁPIDO', 'SEGREDO', 'INCRÍVEL'")}
                      className="text-xs text-blue-400 hover:text-blue-300 block text-left"
                    >
                      • Fitness com urgência e números
                    </button>
                    <button
                      type="button"
                      onClick={() => setCustomPrompt("Reescreva esses títulos para o nicho de negócios online, focando em resultados financeiros específicos e usando palavras como 'LUCRO', 'FATURAMENTO', 'GANHAR'")}
                      className="text-xs text-blue-400 hover:text-blue-300 block text-left"
                    >
                      • Negócios online com foco financeiro
                    </button>
                    <button
                      type="button"
                      onClick={() => setCustomPrompt("Adapte esses títulos para o público jovem, usando gírias atuais, emojis e linguagem descontraída, mantendo o apelo viral")}
                      className="text-xs text-blue-400 hover:text-blue-300 block text-left"
                    >
                      • Linguagem jovem e descontraída
                    </button>
                    <button
                      type="button"
                      onClick={() => setCustomPrompt("Transforme em títulos educacionais sérios, removendo sensacionalismo e focando no valor educativo e aprendizado")}
                      className="text-xs text-blue-400 hover:text-blue-300 block text-left"
                    >
                      • Estilo educacional sério
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              /* Configuração Padrão */
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Tópico do Vídeo
                </label>
                <input
                  type="text"
                  value={titleGenerationConfig.topic}
                  onChange={(e) => handleTitleConfigChange('topic', e.target.value)}
                  placeholder="Ex: Como ganhar dinheiro online, Receitas fitness, etc."
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Quantidade
                </label>
                <input
                  type="number"
                  value={titleGenerationConfig.count}
                  onChange={(e) => handleTitleConfigChange('count', e.target.value)}
                  min="1"
                  max="20"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {!useCustomPrompt && (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Estilo
                  </label>
                  <select
                    value={titleGenerationConfig.style}
                    onChange={(e) => handleTitleConfigChange('style', e.target.value)}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="viral">Viral</option>
                    <option value="educational">Educacional</option>
                    <option value="entertainment">Entretenimento</option>
                    <option value="news">Notícias</option>
                  </select>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                IA Provider
              </label>
              <select
                value={titleGenerationConfig.ai_provider}
                onChange={(e) => handleTitleConfigChange('ai_provider', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="auto">Automático (Híbrido)</option>
                <option value="openai">OpenAI GPT</option>
                <option value="gemini">Google Gemini</option>
              </select>
            </div>

            {!results && (
              <div className="p-4 bg-yellow-900/30 border border-yellow-700 rounded-lg">
                <p className="text-yellow-300 text-sm">
                  💡 <strong>Dica:</strong> Primeiro extraia títulos do YouTube para usar como base de {useCustomPrompt ? 'remodelagem' : 'análise'}.
                </p>
              </div>
            )}

            {useCustomPrompt && (
              <div className="p-4 bg-blue-900/30 border border-blue-700 rounded-lg">
                <p className="text-blue-300 text-sm">
                  🎨 <strong>Modo Personalizado:</strong> A IA vai remodelar os títulos extraídos seguindo suas instruções específicas.
                </p>
              </div>
            )}

            <button
              onClick={handleGenerateTitles}
              disabled={isGeneratingTitles || !results}
              className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
            >
              {isGeneratingTitles ? (
                <>
                  <RefreshCw size={18} className="animate-spin" />
                  <span>{useCustomPrompt ? 'Remodelando títulos...' : 'Gerando títulos...'}</span>
                </>
              ) : (
                <>
                  <Wand2 size={18} />
                  <span>{useCustomPrompt ? 'Remodelar Títulos' : 'Gerar Títulos'}</span>
                </>
              )}
            </button>
          </div>

          {/* Resultados */}
          <div>
            {generatedTitles ? (
              <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                <h4 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                  <FileText size={20} />
                  <span>Títulos Gerados ({generatedTitles.total_generated})</span>
                </h4>

                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {generatedTitles.generated_titles.map((title, index) => (
                    <div key={index} className="bg-gray-600 rounded p-3 group hover:bg-gray-500 transition-colors">
                      <div className="flex items-start justify-between">
                        <p className="text-white text-sm font-medium flex-1 mr-2">
                          {index + 1}. {title}
                        </p>
                        <button
                          onClick={() => copyTitleToClipboard(title)}
                          className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-400 rounded"
                          title="Copiar título"
                        >
                          <Copy size={14} className="text-gray-300" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {generatedTitles.patterns_analysis && (
                  <div className="mt-4 p-3 bg-blue-900/30 border border-blue-700 rounded-lg">
                    <p className="text-blue-300 text-sm font-medium mb-2">
                      {generatedTitles.custom_prompt_used ? '🎨 Remodelagem Personalizada:' : '📊 Análise dos Padrões:'}
                    </p>
                    <div className="text-blue-200 text-xs space-y-1">
                      {generatedTitles.custom_prompt_used ? (
                        <>
                          <p><strong>Prompt usado:</strong> {generatedTitles.custom_prompt_used.substring(0, 100)}...</p>
                          <p><strong>IA usada:</strong> {generatedTitles.ai_provider_used}</p>
                          <p><strong>Baseado em:</strong> {generatedTitles.source_titles_count} títulos extraídos</p>
                        </>
                      ) : (
                        <>
                          <p><strong>Gatilhos emocionais:</strong> {generatedTitles.patterns_analysis.emotional_triggers?.slice(0, 5).join(', ')}</p>
                          <p><strong>IA usada:</strong> {generatedTitles.ai_provider_used}</p>
                          <p><strong>Baseado em:</strong> {generatedTitles.source_titles_count} títulos de referência</p>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12">
                <Wand2 size={48} className="mx-auto mb-4 text-gray-500 opacity-50" />
                <h4 className="text-lg font-medium text-white mb-2">🤖 Gerar Títulos Virais</h4>
                <p className="text-gray-400 text-sm">
                  Configure o tópico e clique em "Gerar Títulos"
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Automações de Conteúdo</h1>
          <p className="text-gray-400 mt-1">
            Ferramentas de IA para criação automática de conteúdo
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2">
            <Settings size={18} />
            <span>Configurar APIs</span>
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <Plus size={18} />
            <span>Nova Automação</span>
          </button>
        </div>
      </div>

      {/* AI Agents Status */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Status dos Agentes de IA</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {aiAgents.map((agent) => (
            <div key={agent.id} className="bg-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-white">{agent.name}</h3>
                <div className={`w-2 h-2 rounded-full ${
                  agent.status === 'connected' ? 'bg-green-400' : 'bg-red-400'
                }`} />
              </div>
              <p className="text-sm text-gray-400">{agent.cost}</p>
              <p className={`text-xs mt-1 ${
                agent.status === 'connected' ? 'text-green-400' : 'text-red-400'
              }`}>
                {agent.status === 'connected' ? 'Conectado' : 'Desconectado'}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="border-b border-gray-700">
          <nav className="flex space-x-8 px-6">
            {automationTabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? `border-${tab.color}-500 text-${tab.color}-400`
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
          {activeTab === 'youtube' && renderYouTubeExtraction()}
          {activeTab === 'titles' && renderTitleGeneration()}
          {activeTab !== 'youtube' && activeTab !== 'titles' && (
            <div className="text-center py-12">
              <Target size={48} className="text-purple-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Em desenvolvimento</h3>
              <p className="text-gray-400">Esta funcionalidade será implementada em breve.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Automations
