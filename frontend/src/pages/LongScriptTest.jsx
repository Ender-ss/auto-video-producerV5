import { useState, useEffect } from 'react'
import { Film, Settings, Play, Download, Sparkles, AlertCircle, CheckCircle, Code2, List, Plus, FileText, Clock, BarChart3 } from 'lucide-react'
import toast from 'react-hot-toast'

const LongScriptTest = () => {
  const [config, setConfig] = useState({
    title: '',
    premise: '',
    chapters: 7,
    provider: 'openai',
    apiKey: ''
  })

  const [script, setScript] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [apiKeys, setApiKeys] = useState({})
  const [showStats, setShowStats] = useState(false)
  const [debugInfo, setDebugInfo] = useState('')

  // Carregar chaves de API das configurações
  const loadApiKeys = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/settings/api-keys')
      if (response.ok) {
        const data = await response.json()
        if (data.success && data.keys) {
          setApiKeys(data.keys)
          // Usar a primeira chave disponível como padrão
          if (data.keys.openai && !config.apiKey) {
            setConfig(prev => ({ ...prev, apiKey: data.keys.openai, provider: 'openai' }))
          } else if (data.keys.gemini_1 && !config.apiKey) {
            setConfig(prev => ({ ...prev, apiKey: data.keys.gemini_1, provider: 'gemini' }))
          } else if (data.keys.openrouter && !config.apiKey) {
            setConfig(prev => ({ ...prev, apiKey: data.keys.openrouter, provider: 'openrouter' }))
          }
        }
      }
    } catch (error) {
      console.error('Erro ao carregar chaves de API:', error)
      setDebugInfo(prev => prev + '\nErro ao carregar chaves: ' + error.message)
    }
  }

  useEffect(() => {
    loadApiKeys()
  }, [])

  const handleGenerateScript = async () => {
    if (!config.title || !config.premise) {
      toast.error('Por favor, preencha título e premissa')
      return
    }

    // Usar chave de API das configurações baseada no provedor selecionado
    let apiKey = ''
    if (config.provider === 'openai' && apiKeys.openai) {
      apiKey = apiKeys.openai
    } else if (config.provider === 'gemini' && apiKeys.gemini_1) {
      apiKey = apiKeys.gemini_1
    } else if (config.provider === 'openrouter' && apiKeys.openrouter) {
      apiKey = apiKeys.openrouter
    } else {
      toast.error('Chave de API não encontrada para o provedor selecionado')
      return
    }

    setIsGenerating(true)
    setProgress(0)
    setScript(null)
    setDebugInfo('Iniciando geração de roteiro...\n')

    try {
      // Simular progresso
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval)
            return 95
          }
          return prev + 5
        })
      }, 500)

      setDebugInfo(prev => prev + `Enviando requisição para /api/premise/generate-long-script\n`)
      setDebugInfo(prev => prev + `Parâmetros: title=${config.title}, chapters=${config.chapters}, provider=${config.provider}\n`)
      
      const response = await fetch('http://localhost:5000/api/premise/generate-long-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: config.title,
          premise: config.premise,
          number_of_chapters: config.chapters,
          provider: config.provider,
          api_key: apiKey
        })
      })

      clearInterval(progressInterval)
      setProgress(100)
      
      setDebugInfo(prev => prev + `Status da resposta: ${response.status} ${response.statusText}\n`)
      
      const responseText = await response.text()
      setDebugInfo(prev => prev + `Resposta bruta: ${responseText}\n`)
      
      let data
      try {
        data = JSON.parse(responseText)
      } catch (e) {
        setDebugInfo(prev => prev + `Erro ao parsear JSON: ${e.message}\n`)
        throw new Error('Resposta inválida do servidor')
      }

      if (response.ok) {
        if (data.success) {
          setScript(data.data)
          toast.success('Roteiro gerado com sucesso!')
          setDebugInfo(prev => prev + `Roteiro gerado com sucesso: ${data.data.chapters.length} capítulos, ${data.data.word_count} palavras\n`)
        } else {
          const errorMsg = data.error || 'Erro desconhecido'
          toast.error('Erro ao gerar roteiro: ' + errorMsg)
          setDebugInfo(prev => prev + `Erro na geração: ${errorMsg}\n`)
        }
      } else {
        const errorData = data || {}
        const errorMsg = errorData.error || 'Erro desconhecido'
        toast.error('Erro ao gerar roteiro: ' + errorMsg)
        setDebugInfo(prev => prev + `Erro na requisição: ${errorMsg}\n`)
      }
    } catch (error) {
      console.error('Erro ao gerar roteiro:', error)
      const errorMsg = error.message || 'Erro desconhecido'
      toast.error('Erro ao gerar roteiro: ' + errorMsg)
      setDebugInfo(prev => prev + `Exceção capturada: ${errorMsg}\n`)
    } finally {
      setIsGenerating(false)
    }
  }

  const exportScript = () => {
    if (!script || !script.script) return

    const blob = new Blob([script.script], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${(config.title || 'roteiro').replace(/\s+/g, '_')}_roteiro.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  const sendToTTS = () => {
    if (!script || !script.chapters) {
      alert('Nenhum roteiro foi gerado ainda!')
      return
    }

    // Preparar dados no formato esperado pelo TTS
    const ttsData = {
      title: config.title || 'Roteiro Gerado',
      chapters: script.chapters.map((chapter, index) => ({
        id: index,
        title: `Capítulo ${index + 1}`,
        content: chapter.content || chapter,
        wordCount: (chapter.content || chapter).split(/\s+/).length
      })),
      total_words: script.word_count || 0,
      timestamp: new Date().toISOString(),
      source: 'LongScriptTest'
    }
    
    localStorage.setItem('ttsScreenplayData', JSON.stringify(ttsData))
    
    alert('Roteiro enviado para Text-to-Speech! Acesse a aba TTS para processar o áudio.')
    
    console.log('✅ Roteiro enviado para TTS:', ttsData)
  }

  return (
    <div className="min-h-screen p-6 bg-gradient-to-b from-gray-900 to-gray-800">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-yellow-500/10 text-yellow-400"><Film size={24} /></div>
            <div>
              <h1 className="text-2xl font-bold">Teste de Geração de Roteiros Longos</h1>
              <p className="text-gray-400 text-sm">Página de teste para diagnosticar problemas na geração de roteiros</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowStats(!showStats)}
              disabled={!script}
              className="px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 disabled:opacity-50 flex items-center gap-2"
            >
              <BarChart3 size={16} /> Estatísticas
            </button>
            <button
              onClick={exportScript}
              disabled={!script}
              className="px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 disabled:opacity-50 flex items-center gap-2"
            >
              <Download size={16} /> Exportar
            </button>
            <button
              onClick={sendToTTS}
              disabled={!script}
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Play size={16} /> Enviar para TTS
            </button>
            <button
              onClick={handleGenerateScript}
              disabled={isGenerating}
              className="px-4 py-2 rounded-lg bg-yellow-500 hover:bg-yellow-600 text-black font-semibold flex items-center gap-2 disabled:opacity-50"
            >
              <Sparkles size={16} /> {isGenerating ? 'Gerando Roteiro...' : 'Gerar Roteiro'}
            </button>
          </div>
        </div>

        {/* Progress */}
        {isGenerating && (
          <div className="bg-gray-800/60 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between text-sm text-gray-300 mb-2">
              <span>Progresso</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full h-2 bg-gray-700 rounded">
              <div className="h-2 bg-yellow-500 rounded" style={{ width: `${progress}%` }} />
            </div>
          </div>
        )}

        {/* Config */}
        <div className="bg-gray-800/60 rounded-lg p-6 border border-gray-700">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Título</label>
              <input
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                placeholder="Ex: A Jornada de Orion"
                value={config.title}
                onChange={(e) => setConfig({ ...config, title: e.target.value })}
                disabled={isGenerating}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">Provedor de IA</label>
              <select
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                value={config.provider}
                onChange={(e) => setConfig({ ...config, provider: e.target.value })}
                disabled={isGenerating}
              >
                <option value="openai">OpenAI</option>
                <option value="gemini">Google Gemini</option>
                <option value="openrouter">OpenRouter</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">Número de Capítulos</label>
              <input
                type="number"
                min="3"
                max="20"
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                value={config.chapters}
                onChange={(e) => setConfig({ ...config, chapters: parseInt(e.target.value) })}
                disabled={isGenerating}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">Chave de API</label>
              <input
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                placeholder="Chave de API (será preenchida automaticamente)"
                value={config.apiKey}
                onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
                disabled={isGenerating}
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm text-gray-300 mb-1">Premissa</label>
              <textarea
                rows={4}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                placeholder="Descreva a premissa principal da história..."
                value={config.premise}
                onChange={(e) => setConfig({ ...config, premise: e.target.value })}
                disabled={isGenerating}
              />
            </div>
          </div>
        </div>

        {/* Debug Info */}
        {debugInfo && (
          <div className="bg-gray-800/60 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Code2 size={20} /> Informações de Depuração
            </h2>
            <div className="bg-gray-900/50 p-4 rounded-lg font-mono text-sm text-gray-300 whitespace-pre-wrap max-h-60 overflow-y-auto">
              {debugInfo}
            </div>
          </div>
        )}

        {/* Stats Panel */}
        {showStats && script && script.performance_stats && (
          <div className="bg-gray-800/60 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <BarChart3 size={20} /> Estatísticas de Performance
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-900/50 p-4 rounded-lg">
                <div className="text-sm text-gray-400">Tempo Total</div>
                <div className="text-2xl font-bold">{script.performance_stats.total_generation_time?.toFixed(2) || '0.00'}s</div>
              </div>
              <div className="bg-gray-900/50 p-4 rounded-lg">
                <div className="text-sm text-gray-400">Tempo Médio por Capítulo</div>
                <div className="text-2xl font-bold">{script.performance_stats.avg_chapter_time?.toFixed(2) || '0.00'}s</div>
              </div>
              <div className="bg-gray-900/50 p-4 rounded-lg">
                <div className="text-sm text-gray-400">Tempo Médio por Resumo</div>
                <div className="text-2xl font-bold">{script.performance_stats.avg_summary_time?.toFixed(2) || '0.00'}s</div>
              </div>
            </div>
          </div>
        )}

        {/* Generated Script */}
        {script && (
          <div className="bg-gray-800/60 rounded-lg border border-gray-700">
            <div className="p-4 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-xl font-bold">Roteiro Gerado</h2>
              <div className="text-sm text-gray-400">
                {script.word_count} palavras • {script.chapters ? script.chapters.length : 0} capítulos
              </div>
            </div>
            
            <div className="p-4 max-h-96 overflow-y-auto">
              {script.script && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2">Roteiro Completo</h3>
                  <div className="bg-gray-900/50 p-4 rounded-lg whitespace-pre-wrap text-gray-300">
                    {script.script}
                  </div>
                </div>
              )}
              
              {script.chapters && script.chapters.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">Capítulos</h3>
                  <div className="space-y-4">
                    {script.chapters.map((chapter, index) => (
                      <div key={index} className="bg-gray-900/50 p-4 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold">Capítulo {index + 1}</h4>
                          <div className="text-sm text-gray-400">
                            {(chapter.content || chapter).split(/\s+/).length} palavras
                          </div>
                        </div>
                        <div className="text-gray-300 whitespace-pre-wrap">
                          {chapter.content || chapter}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {script.summaries && script.summaries.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-2">Resumos Contextuais</h3>
                  <div className="space-y-4">
                    {script.summaries.map((summary, index) => (
                      <div key={index} className="bg-gray-900/50 p-4 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold">Resumo do Capítulo {index + 1}</h4>
                          <div className="text-sm text-gray-400">
                            {summary.split(/\s+/).length} palavras
                          </div>
                        </div>
                        <div className="text-gray-300 whitespace-pre-wrap">
                          {summary}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default LongScriptTest