import React, { useState, useEffect } from 'react'
import { Film, Settings, Play, Download, Sparkles, AlertCircle, CheckCircle, Code2, List, Plus, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import AIService from '../utils/aiExternalService'

const ScreenplayGeneratorTest = () => {
  const [config, setConfig] = useState({
    title: '',
    genre: '',
    premise: '',
    totalChapters: 7,
    targetWords: 7674,
    apiProvider: 'openai',
    apiKey: '',
    generatedTitle: '',
    generatedPremise: '',
    prompts: {
      inicio: `Escreva uma narrativa de {genre} intitulada "{title}".
      
Premissa: {premise}

Este é o INÍCIO da história. Deve estabelecer:
- Personagens principais e suas motivações
- Cenário e atmosfera da história
- Conflito principal que moverá a narrativa
- Tom e estilo da narrativa
- Gancho inicial que prenda o leitor

IMPORTANTE: Escreva APENAS o texto da narrativa, sem títulos, sem "Capítulo X", sem marcações. Apenas o conteúdo fluido da história.

Formato: Narrativa fluida em texto corrido
Extensão: Aproximadamente {wordsPerChapter} palavras

Escreva como uma narrativa envolvente, sem marcações técnicas, com descrições ricas e diálogos integrados naturalmente no texto.`,
      
      meio: `Continue a narrativa de {genre} intitulada "{title}".

CONTEXTO ANTERIOR:
"{previousContent}"...

Esta é a continuação do MEIO da história. Deve:
- Continuar a narrativa de forma orgânica e coerente
- Desenvolver os personagens e suas relações
- Intensificar o conflito principal
- Introduzir obstáculos e complicações
- Manter o ritmo e a tensão narrativa
- Conectar-se naturalmente com o texto anterior

IMPORTANTE: Escreva APENAS o texto da narrativa, sem títulos, sem "Capítulo X", sem marcações. Continue diretamente a história.

Formato: Narrativa fluida em texto corrido
Extensão: Aproximadamente {wordsPerChapter} palavras

Escreva como uma narrativa envolvente, sem marcações técnicas, com descrições ricas e diálogos integrados naturalmente no texto.`,
      
      fim: `Continue a narrativa de {genre} intitulada "{title}".

CONTEXTO ANTERIOR:
"{previousContent}"...

Este é o FIM da história. Deve:
- Resolver o conflito principal estabelecido no início
- Proporcionar conclusão satisfatória para todos os personagens principais
- Entregar o clímax emocional da história
- Fechar todas as subtramas abertas
- Deixar uma impressão duradoura no leitor

IMPORTANTE: Escreva APENAS o texto da narrativa, sem títulos, sem "Capítulo X", sem marcações. Continue diretamente a história.

Formato: Narrativa fluida em texto corrido
Extensão: Aproximadamente {wordsPerChapter} palavras

Escreva como uma narrativa envolvente, sem marcações técnicas, com descrições ricas e diálogos integrados naturalmente no texto.`
    }
  })

  const [chapters, setChapters] = useState([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [currentChapter, setCurrentChapter] = useState(0)
  const [activeTab, setActiveTab] = useState('basic') // 'basic' | 'prompts' | 'generated'
  const [generatedTitles, setGeneratedTitles] = useState([])
  const [generatedPremises, setGeneratedPremises] = useState([])
  const [apiKeys, setApiKeys] = useState({})
  const [showTitleSelector, setShowTitleSelector] = useState(false)
  const [showPremiseSelector, setShowPremiseSelector] = useState(false)
  const [storedTitles, setStoredTitles] = useState([])
  const [storedPremises, setStoredPremises] = useState([])
  const [showStoredTitleSelector, setShowStoredTitleSelector] = useState(false)
  const [showStoredPremiseSelector, setShowStoredPremiseSelector] = useState(false)
  const [savedScreenplays, setSavedScreenplays] = useState([])
  const [showSavedScreenplaySelector, setShowSavedScreenplaySelector] = useState(false)

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
            setConfig(prev => ({ ...prev, apiKey: data.keys.openai, apiProvider: 'openai' }))
          } else if (data.keys.gemini_1 && !config.apiKey) {
            setConfig(prev => ({ ...prev, apiKey: data.keys.gemini_1, apiProvider: 'gemini' }))
          } else if (data.keys.openrouter && !config.apiKey) {
            setConfig(prev => ({ ...prev, apiKey: data.keys.openrouter, apiProvider: 'openrouter' }))
          }
        }
      }
    } catch (error) {
      console.error('Erro ao carregar chaves de API:', error)
    }
  }

  // Carregar dados salvos do localStorage
  const loadStoredData = () => {
    try {
      // Carregar títulos salvos (usando a chave correta do AutomationsDev)
      const storedTitlesData = localStorage.getItem('generated_titles')
      if (storedTitlesData) {
        const titlesData = JSON.parse(storedTitlesData)
        if (titlesData && titlesData.generated_titles && titlesData.generated_titles.length > 0) {
          setStoredTitles(titlesData.generated_titles)
          console.log('✅ Títulos carregados do localStorage:', titlesData.generated_titles.length)
        }
      }

      // Carregar premissas salvas (usando a chave correta do AutomationsDev)
      const storedPremisesData = localStorage.getItem('generated_premises')
      if (storedPremisesData) {
        const premisesData = JSON.parse(storedPremisesData)
        if (premisesData && premisesData.length > 0) {
          setStoredPremises(premisesData)
          console.log('✅ Premissas carregadas do localStorage:', premisesData.length)
        }
      }

      // Carregar roteiros salvos
      const savedScreenplaysData = localStorage.getItem('saved_screenplays')
      if (savedScreenplaysData) {
        const screenplaysData = JSON.parse(savedScreenplaysData)
        if (screenplaysData && screenplaysData.length > 0) {
          setSavedScreenplays(screenplaysData)
          console.log('✅ Roteiros salvos carregados do localStorage:', screenplaysData.length)
        }
      }
    } catch (error) {
      console.error('Erro ao carregar dados do localStorage:', error)
    }
  }

  useEffect(() => {
    loadApiKeys()
    loadStoredData()
  }, [])

  // Gerar títulos
  const generateTitles = async () => {
    if (!config.genre) {
      toast.error('Por favor, especifique um gênero primeiro')
      return
    }

    try {
      const response = await fetch('http://localhost:5000/api/automations/generate-titles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          genre: config.genre,
          provider: config.apiProvider
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success && data.titles) {
          setGeneratedTitles(data.titles)
          setShowTitleSelector(true)
          toast.success('Títulos gerados com sucesso!')
        }
      } else {
        toast.error('Erro ao gerar títulos')
      }
    } catch (error) {
      console.error('Erro ao gerar títulos:', error)
      toast.error('Erro ao gerar títulos')
    }
  }

  // Funções para selecionar dados salvos
  const selectStoredTitle = (title) => {
    setConfig(prev => ({ ...prev, title }))
    setShowStoredTitleSelector(false)
  }

  const selectStoredPremise = (premise) => {
    setConfig(prev => ({ ...prev, premise }))
    setShowStoredPremiseSelector(false)
  }

  // Função para salvar roteiro completo
  const saveScreenplay = () => {
    if (chapters.length === 0) {
      toast.error('Nenhum roteiro para salvar')
      return
    }

    const screenplayData = {
      id: Date.now().toString(),
      title: config.title || 'Roteiro Sem Título',
      premise: config.premise || '',
      chapters: chapters,
      totalWords: chapters.reduce((acc, ch) => acc + ch.wordCount, 0),
      totalChapters: chapters.length,
      createdAt: new Date().toISOString(),
      apiProvider: config.apiProvider
    }

    try {
      const existingScreenplays = JSON.parse(localStorage.getItem('saved_screenplays') || '[]')
      const updatedScreenplays = [screenplayData, ...existingScreenplays]
      localStorage.setItem('saved_screenplays', JSON.stringify(updatedScreenplays))
      setSavedScreenplays(updatedScreenplays)
      toast.success('Roteiro salvo com sucesso!')
      console.log('✅ Roteiro salvo:', screenplayData)
    } catch (error) {
      console.error('Erro ao salvar roteiro:', error)
      toast.error('Erro ao salvar roteiro')
    }
  }

  // Função para carregar roteiro salvo
  const loadSavedScreenplay = (screenplay) => {
    setConfig(prev => ({
      ...prev,
      title: screenplay.title,
      premise: screenplay.premise,
      totalChapters: screenplay.totalChapters
    }))
    setChapters(screenplay.chapters)
    setShowSavedScreenplaySelector(false)
    toast.success('Roteiro carregado com sucesso!')
  }

  // Função para deletar roteiro salvo
  const deleteSavedScreenplay = (screenplayId) => {
    try {
      const updatedScreenplays = savedScreenplays.filter(s => s.id !== screenplayId)
      localStorage.setItem('saved_screenplays', JSON.stringify(updatedScreenplays))
      setSavedScreenplays(updatedScreenplays)
      toast.success('Roteiro deletado')
    } catch (error) {
      console.error('Erro ao deletar roteiro:', error)
      toast.error('Erro ao deletar roteiro')
    }
  }

  // Gerar premissas
  const generatePremises = async () => {
    if (!config.title || !config.genre) {
      toast.error('Por favor, especifique título e gênero primeiro')
      return
    }

    try {
      const response = await fetch('http://localhost:5000/api/premise/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: config.title,
          genre: config.genre,
          provider: config.apiProvider
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success && data.premises) {
          setGeneratedPremises(data.premises)
          setShowPremiseSelector(true)
          toast.success('Premissas geradas com sucesso!')
        }
      } else {
        toast.error('Erro ao gerar premissas')
      }
    } catch (error) {
      console.error('Erro ao gerar premissas:', error)
      toast.error('Erro ao gerar premissas')
    }
  }

  const getStructureForChapter = (chapterIndex, totalChapters) => {
    if (chapterIndex === 0) return 'inicio'
    if (chapterIndex === totalChapters - 1) return 'fim'
    return 'meio'
  }

  const generateChapter = async (chapterIndex, previousChapter, apiKey) => {
    const structure = getStructureForChapter(chapterIndex, config.totalChapters)
    const wordsPerChapter = Math.floor(config.targetWords / config.totalChapters)
    let prompt = ''

    if (chapterIndex === 0) {
      prompt = config.prompts.inicio
        .replace('{genre}', (config.genre || '').toLowerCase())
        .replace('{title}', config.title || '')
        .replace('{premise}', config.premise || '')
        .replace('{wordsPerChapter}', String(wordsPerChapter))
    } else if (structure === 'fim') {
      prompt = config.prompts.fim
        .replace('{genre}', (config.genre || '').toLowerCase())
        .replace('{title}', config.title || '')
        .replace('{previousContent}', previousChapter?.content?.substring(0, 800) || '')
        .replace('{wordsPerChapter}', String(wordsPerChapter))
    } else {
      prompt = config.prompts.meio
        .replace('{genre}', (config.genre || '').toLowerCase())
        .replace('{title}', config.title || '')
        .replace('{previousContent}', previousChapter?.content?.substring(0, 800) || '')
        .replace('{wordsPerChapter}', String(wordsPerChapter))
    }

    const aiService = new AIService({
      provider: config.apiProvider,
      apiKey: apiKey
    })

    const maxTokens = config.apiProvider === 'openai' ? 3000 : 2000

    const generatedContent = await aiService.generateText({
      prompt,
      maxTokens,
      temperature: 0.8,
    })

    const wordCount = generatedContent.split(/\s+/).length

    return {
      id: chapterIndex,
      title: `Capítulo ${chapterIndex + 1} - ${
        structure === 'inicio' ? 'O Início' : structure === 'fim' ? 'O Final' : `Desenvolvimento ${chapterIndex}`
      }`,
      content: generatedContent,
      structure,
      wordCount,
    }
  }

  const handleGenerateScreenplay = async () => {
    if (!config.title || !config.premise) {
      toast.error('Por favor, preencha título e premissa')
      return
    }

    // Usar chave de API das configurações baseada no provedor selecionado
    let apiKey = ''
    if (config.apiProvider === 'openai' && apiKeys.openai) {
      apiKey = apiKeys.openai
    } else if (config.apiProvider === 'gemini' && apiKeys.gemini_1) {
      apiKey = apiKeys.gemini_1
    } else if (config.apiProvider === 'openrouter' && apiKeys.openrouter) {
      apiKey = apiKeys.openrouter
    } else {
      toast.error('Chave de API não encontrada para o provedor selecionado')
      return
    }

    setIsGenerating(true)
    setChapters([])
    setCurrentChapter(0)

    try {
      const newChapters = []
      for (let i = 0; i < config.totalChapters; i++) {
        setCurrentChapter(i + 1)
        const previousChapter = newChapters[i - 1]
        const chapter = await generateChapter(i, previousChapter, apiKey)
        newChapters.push(chapter)
        setChapters([...newChapters])
        toast.success(`Capítulo ${i + 1} concluído • ${chapter.wordCount} palavras`)
      }
      toast.success(`Roteiro concluído! ${newChapters.reduce((acc, ch) => acc + ch.wordCount, 0)} palavras em ${config.totalChapters} capítulos`)
    } catch (e) {
      console.error(e)
      toast.error('Ocorreu um erro ao gerar o roteiro')
    } finally {
      setIsGenerating(false)
    }
  }

  const exportScreenplay = () => {
    const fullScreenplay = chapters.map((c) => c.content).join('\n\n')
    const blob = new Blob([fullScreenplay], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${(config.title || 'roteiro').replace(/\s+/g, '_')}_roteiro.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Função para enviar roteiro para Text-to-Speech
  const sendToTTS = () => {
    const fullScreenplay = chapters.map(chapter => chapter.content).join('\n\n')
    
    if (!fullScreenplay.trim()) {
      alert('Nenhum roteiro foi gerado ainda!')
      return
    }

    // Salvar o roteiro no localStorage para a aba TTS na estrutura esperada
    const ttsData = {
      title: config.title || 'Roteiro Gerado',
      chapters: chapters, // Enviar os capítulos na estrutura original
      total_words: chapters.reduce((acc, ch) => acc + ch.wordCount, 0),
      timestamp: new Date().toISOString(),
      source: 'ScreenplayGeneratorTest'
    }
    
    localStorage.setItem('ttsScreenplayData', JSON.stringify(ttsData))
    
    // Notificar o usuário
    alert('Roteiro enviado para Text-to-Speech! Acesse a aba TTS para processar o áudio.')
    
    console.log('✅ Roteiro enviado para TTS:', ttsData)
  }

  const totalWords = chapters.reduce((acc, c) => acc + c.wordCount, 0)
  const progress = config.totalChapters > 0 ? (chapters.length / config.totalChapters) * 100 : 0

  return (
    <div className="min-h-screen p-6 bg-gradient-to-b from-gray-900 to-gray-800">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-yellow-500/10 text-yellow-400"><Film size={24} /></div>
            <div>
              <h1 className="text-2xl font-bold">Gerador de Roteiros Longos (Teste)</h1>
              <p className="text-gray-400 text-sm">Crie narrativas em capítulos usando OpenAI ou Gemini</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={exportScreenplay}
              disabled={chapters.length === 0}
              className="px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 disabled:opacity-50 flex items-center gap-2"
            >
              <Download size={16} /> Exportar
            </button>
            <button
              onClick={sendToTTS}
              disabled={chapters.length === 0}
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Play size={16} /> Enviar para TTS
            </button>
            <button
              onClick={handleGenerateScreenplay}
              disabled={isGenerating}
              className="px-4 py-2 rounded-lg bg-yellow-500 hover:bg-yellow-600 text-black font-semibold flex items-center gap-2 disabled:opacity-50"
            >
              <Sparkles size={16} /> {isGenerating ? `Gerando capítulo ${currentChapter}/${config.totalChapters}` : 'Gerar Roteiro'}
            </button>
          </div>
        </div>

        {/* Progress */}
        <div className="bg-gray-800/60 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between text-sm text-gray-300 mb-2">
            <span>Progresso</span>
            <span>{chapters.length}/{config.totalChapters} capítulos • {totalWords} palavras</span>
          </div>
          <div className="w-full h-2 bg-gray-700 rounded">
            <div className="h-2 bg-yellow-500 rounded" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-gray-800/60 rounded-lg border border-gray-700">
          <div className="flex border-b border-gray-700">
            <button onClick={() => setActiveTab('basic')} className={`px-4 py-2 text-sm ${activeTab==='basic' ? 'bg-gray-700 text-white' : 'text-gray-300 hover:text-white'}`}>Básico</button>
            <button onClick={() => setActiveTab('prompts')} className={`px-4 py-2 text-sm ${activeTab==='prompts' ? 'bg-gray-700 text-white' : 'text-gray-300 hover:text-white'}`}>Prompts</button>
            <button onClick={() => setActiveTab('saved')} className={`px-4 py-2 text-sm ${activeTab==='saved' ? 'bg-gray-700 text-white' : 'text-gray-300 hover:text-white'}`}>Salvos</button>
          </div>

          {activeTab === 'basic' && (
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-300 mb-1">Título</label>
                <div className="flex gap-2">
                  <input
                    className="flex-1 px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                    placeholder="Ex: A Jornada de Orion"
                    value={config.title}
                    onChange={(e) => setConfig({ ...config, title: e.target.value })}
                  />
                  <button
                    onClick={generateTitles}
                    className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-1"
                  >
                    <Sparkles size={16} /> Gerar
                  </button>
                  {storedTitles.length > 0 && (
                    <button
                      onClick={() => setShowStoredTitleSelector(true)}
                      className="px-3 py-2 bg-green-600 hover:bg-green-700 rounded-lg flex items-center gap-1"
                      title="Selecionar título salvo"
                    >
                      <FileText size={16} /> Salvos
                    </button>
                  )}

        {/* Stored Title Selector Modal */}
        {showStoredTitleSelector && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <h3 className="text-lg font-semibold mb-4">Selecione um Título Salvo</h3>
              <div className="space-y-2 mb-4">
                {storedTitles.map((title, index) => (
                  <button
                    key={index}
                    onClick={() => selectStoredTitle(title)}
                    className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded-lg"
                  >
                    {title}
                  </button>
                ))}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowStoredTitleSelector(false)}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Stored Premise Selector Modal */}
        {showStoredPremiseSelector && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <h3 className="text-lg font-semibold mb-4">Selecione uma Premissa Salva</h3>
              <div className="space-y-2 mb-4">
                {storedPremises.map((premise, index) => (
                  <button
                    key={index}
                    onClick={() => selectStoredPremise(premise.premise)}
                    className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded-lg"
                  >
                    <div className="font-medium text-white mb-1">{premise.title}</div>
                    <div className="text-sm text-gray-300 line-clamp-2">{premise.premise}</div>
                  </button>
                ))}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowStoredPremiseSelector(false)}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Gênero</label>
                <input
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                  placeholder="Ex: Ficção científica"
                  value={config.genre}
                  onChange={(e) => setConfig({ ...config, genre: e.target.value })}
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Premissa</label>
                <div className="space-y-2">
                  <textarea
                    rows={4}
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                    placeholder="Descreva a premissa principal da história..."
                    value={config.premise}
                    onChange={(e) => setConfig({ ...config, premise: e.target.value })}
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={generatePremises}
                      className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-1"
                    >
                      <Sparkles size={16} /> Gerar Premissas
                    </button>
                    {storedPremises.length > 0 && (
                      <button
                        onClick={() => setShowStoredPremiseSelector(true)}
                        className="px-3 py-2 bg-green-600 hover:bg-green-700 rounded-lg flex items-center gap-1"
                        title="Selecionar premissa salva"
                      >
                        <FileText size={16} /> Salvos
                      </button>
                    )}
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Capítulos</label>
                <input
                  type="number"
                  min={1}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                  value={config.totalChapters}
                  onChange={(e) => setConfig({ ...config, totalChapters: Math.max(1, parseInt(e.target.value || '1', 10)) })}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Palavras Alvo</label>
                <input
                  type="number"
                  min={100}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                  value={config.targetWords}
                  onChange={(e) => setConfig({ ...config, targetWords: Math.max(100, parseInt(e.target.value || '100', 10)) })}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Provedor</label>
                <select
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                  value={config.apiProvider}
                  onChange={(e) => setConfig({ ...config, apiProvider: e.target.value })}
                >
                  <option value="openai">OpenAI</option>
                  <option value="gemini">Gemini</option>
                  <option value="openrouter">OpenRouter</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Status da API</label>
                <div className="text-sm text-gray-300">
                  {config.apiProvider === 'openai' && apiKeys.openai && (
                    <span className="text-green-400">✓ OpenAI configurada</span>
                  )}
                  {config.apiProvider === 'gemini' && apiKeys.gemini_1 && (
                    <span className="text-green-400">✓ Gemini configurada</span>
                  )}
                  {config.apiProvider === 'openrouter' && apiKeys.openrouter && (
                    <span className="text-green-400">✓ OpenRouter configurada</span>
                  )}
                  {((config.apiProvider === 'openai' && !apiKeys.openai) ||
                    (config.apiProvider === 'gemini' && !apiKeys.gemini_1) ||
                    (config.apiProvider === 'openrouter' && !apiKeys.openrouter)) && (
                    <span className="text-red-400">✗ Chave não configurada - Configure nas Configurações</span>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'prompts' && (
            <div className="p-4 grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm text-gray-300 mb-2 flex items-center gap-2"><Settings size={16}/> Prompt — Início</label>
                <textarea
                  rows={8}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg font-mono text-sm"
                  value={config.prompts.inicio}
                  onChange={(e) => setConfig({ ...config, prompts: { ...config.prompts, inicio: e.target.value } })}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-2 flex items-center gap-2"><Code2 size={16}/> Prompt — Meio</label>
                <textarea
                  rows={8}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg font-mono text-sm"
                  value={config.prompts.meio}
                  onChange={(e) => setConfig({ ...config, prompts: { ...config.prompts, meio: e.target.value } })}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-2 flex items-center gap-2"><CheckCircle size={16}/> Prompt — Fim</label>
                <textarea
                  rows={8}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg font-mono text-sm"
                  value={config.prompts.fim}
                  onChange={(e) => setConfig({ ...config, prompts: { ...config.prompts, fim: e.target.value } })}
                />
              </div>
            </div>
          )}

          {activeTab === 'saved' && (
            <div className="p-4 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-white">
                  Roteiros Salvos ({savedScreenplays.length})
                </h3>
                {chapters.length > 0 && (
                  <button
                    onClick={saveScreenplay}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                  >
                    <Plus size={16} /> Salvar Roteiro Atual
                  </button>
                )}
              </div>

              {savedScreenplays.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <p>Nenhum roteiro salvo ainda.</p>
                  <p className="text-sm mt-2">Gere um roteiro e clique em "Salvar Roteiro Atual" para salvá-lo.</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {savedScreenplays.map((screenplay) => (
                    <div key={screenplay.id} className="border border-gray-700 rounded-lg p-4 bg-gray-800">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium text-white">{screenplay.title}</h4>
                        <div className="flex gap-2">
                          <button
                            onClick={() => loadSavedScreenplay(screenplay)}
                            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors flex items-center gap-1"
                          >
                            <FileText size={14} /> Carregar
                          </button>
                          <button
                            onClick={() => deleteSavedScreenplay(screenplay.id)}
                            className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
                          >
                            🗑️ Deletar
                          </button>
                        </div>
                      </div>
                      <p className="text-sm text-gray-400 mb-2">
                        {screenplay.premise.substring(0, 100)}...
                      </p>
                      <div className="flex gap-4 text-xs text-gray-500">
                        <span>📖 {screenplay.totalChapters} capítulos</span>
                        <span>📝 {screenplay.totalWords.toLocaleString()} palavras</span>
                        <span>📅 {new Date(screenplay.createdAt).toLocaleDateString('pt-BR')}</span>
                        <span>🤖 {screenplay.apiProvider}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Title Selector Modal */}
        {showTitleSelector && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <h3 className="text-lg font-semibold mb-4">Selecione um Título</h3>
              <div className="space-y-2 mb-4">
                {generatedTitles.map((title, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setConfig({ ...config, title })
                      setShowTitleSelector(false)
                    }}
                    className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded-lg"
                  >
                    {title}
                  </button>
                ))}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowTitleSelector(false)}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Premise Selector Modal */}
        {showPremiseSelector && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <h3 className="text-lg font-semibold mb-4">Selecione uma Premissa</h3>
              <div className="space-y-2 mb-4">
                {generatedPremises.map((premise, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setConfig({ ...config, premise })
                      setShowPremiseSelector(false)
                    }}
                    className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded-lg"
                  >
                    <div className="text-sm text-gray-300">{premise}</div>
                  </button>
                ))}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowPremiseSelector(false)}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Chapters */}
        <div className="space-y-4">
          {chapters.map((ch) => (
            <div key={ch.id} className="bg-gray-800/60 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold">{ch.title}</h3>
                <span className="text-xs text-gray-400">{ch.wordCount} palavras</span>
              </div>
              <div className="prose prose-invert max-w-none text-gray-200 whitespace-pre-wrap">{ch.content}</div>
            </div>
          ))}

          {isGenerating && (
            <div className="text-sm text-gray-300">Gerando capítulo {currentChapter} de {config.totalChapters}...</div>
          )}

          {!isGenerating && chapters.length === 0 && (
            <div className="text-sm text-gray-400">Preencha as configurações e clique em "Gerar Roteiro".</div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ScreenplayGeneratorTest