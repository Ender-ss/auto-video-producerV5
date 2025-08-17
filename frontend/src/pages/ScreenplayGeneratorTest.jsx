import React, { useState } from 'react'
import { Film, Settings, Play, Download, Sparkles, AlertCircle, CheckCircle, Code2 } from 'lucide-react'
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
  const [activeTab, setActiveTab] = useState('basic') // 'basic' | 'prompts'

  const getStructureForChapter = (chapterIndex, totalChapters) => {
    if (chapterIndex === 0) return 'inicio'
    if (chapterIndex === totalChapters - 1) return 'fim'
    return 'meio'
  }

  const generateChapter = async (chapterIndex, previousChapter) => {
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
      apiKey: config.apiKey
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
    if (!config.title || !config.premise || !config.apiKey) {
      toast.error('Preencha todos os campos obrigatórios: Título, Premissa e API Key')
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
        const chapter = await generateChapter(i, previousChapter)
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
          </div>

          {activeTab === 'basic' && (
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-300 mb-1">Título</label>
                <input
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                  placeholder="Ex: A Jornada de Orion"
                  value={config.title}
                  onChange={(e) => setConfig({ ...config, title: e.target.value })}
                />
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
                <textarea
                  rows={4}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                  placeholder="Descreva a premissa principal da história..."
                  value={config.premise}
                  onChange={(e) => setConfig({ ...config, premise: e.target.value })}
                />
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
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">API Key</label>
                <input
                  type="password"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg"
                  placeholder={config.apiProvider === 'openai' ? 'sk-...' : 'AIza...'}
                  value={config.apiKey}
                  onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
                />
                <p className="text-xs text-gray-500 mt-1 flex items-center gap-1"><AlertCircle size={12}/> A chave é usada apenas localmente no navegador.</p>
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
        </div>

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