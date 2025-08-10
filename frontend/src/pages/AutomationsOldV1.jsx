/**
 * 🤖 Automations Page
 * 
 * Página de automações completas de conteúdo
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Play,
  Pause,
  Square,
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
  Loader2,
  FileAudio,
  User,
  Volume2,
  Sparkles,
  Target,
  Layers,
  Workflow,
  XCircle,
  Copy,
  Calendar,
  Terminal,
  AlertTriangle,
  Languages,
  BookOpen,
  Hash,
  Edit3
} from 'lucide-react'

const Automations = () => {
  const [currentStep, setCurrentStep] = useState(5)
  
  // Debug: verificar se estamos no passo correto
  console.log('Current step:', currentStep)
  const [workflowData, setWorkflowData] = useState({
    originalScript: '',
    translatedScript: '',
    narrativeChapters: [],
    rewrittenScript: '',
    finalChapters: [],
    finalScript: '',
    generatedImages: [],
    generatedAudio: null
  })
  
  const [prompts, setPrompts] = useState({
    translation: `# Prompt de Tradução Profissional

Você é um tradutor especializado em roteiros e storytelling. Sua tarefa é traduzir o roteiro mantendo:

## Instruções:
1. Mantenha a estrutura original
2. Preserve os ganchos emocionais
3. Adapte expressões culturais
4. Mantenha o tom e ritmo
5. Preserve formatação de capítulos

## Roteiro para traduzir:`,

    narrative: `# Prompt Narrativo por Capítulo

Você é um especialista em storytelling cinematográfico. Transforme cada capítulo em uma narrativa envolvente:

## Instruções:
1. Crie narrativa fluida e cinematográfica
2. Adicione descrições visuais detalhadas
3. Desenvolva diálogos naturais
4. Mantenha tensão e ritmo
5. Conecte com próximo capítulo

## Capítulo para desenvolver:`,

    rewrite: `# Prompt de Reescrita com Gancho Sensacional

Você é um roteirista especializado em criar ganchos irresistíveis. Reescreva o roteiro com:

## Instruções:
1. Adicione ganchos emocionais poderosos
2. Crie momentos de tensão e surpresa
3. Desenvolva reviravoltas impactantes
4. Mantenha o leitor grudado na tela
5. Intensifique conflitos e resoluções

## Roteiro para reescrever:`,

    chapters: `# Prompt de Geração de 8 Capítulos

Você é um roteirista experiente. Divida e desenvolva o roteiro em exatamente 8 capítulos:

## Instruções:
1. Divida em 8 capítulos equilibrados
2. Cada capítulo deve ter 3-5 minutos de conteúdo
3. Crie arco narrativo completo
4. Mantenha tensão crescente
5. Final impactante no último capítulo

## Formato de resposta:
**CAPÍTULO 1:**
[Conteúdo do capítulo 1]

**CAPÍTULO 2:**
[Conteúdo do capítulo 2]

... (continue até capítulo 8)

## Roteiro base:`,

    final: `# Prompt Final - Polimento e Otimização

Você é um editor de roteiros profissional. Faça o polimento final:

## Instruções:
1. Revise gramática e ortografia
2. Otimize fluxo narrativo
3. Ajuste ritmo e timing
4. Fortaleça ganchos emocionais
5. Garanta coesão total

## Roteiro para polir:`,

    images: `# Prompt de Geração de Imagens

Você é um especialista em criar prompts para geração de imagens. Crie prompts detalhados baseados no roteiro:

## Instruções:
1. Crie prompts visuais descritivos para cada cena importante
2. Inclua detalhes de ambiente, personagens e emoções
3. Use linguagem que gere imagens impactantes
4. Mantenha coerência visual com o roteiro
5. Formate cada prompt separadamente

## Formato de resposta:
**IMAGEM 1:**
[Prompt detalhado para imagem 1]

**IMAGEM 2:**
[Prompt detalhado para imagem 2]

... (continue para cada cena importante)

## Roteiro base:`,

    tts: `# Prompt de Text-to-Speech

Você é um especialista em preparar roteiros para narração por voz. Adapte o roteiro para TTS:

## Instruções:
1. Ajuste o texto para narração natural
2. Adicione marcações de pausa e ênfase
3. Simplifique estruturas complexas
4. Otimize para clareza na fala
5. Mantenha o impacto emocional

## Roteiro para adaptar:`
  })

  const [customPrompts, setCustomPrompts] = useState({ ...prompts })
  const [isProcessing, setIsProcessing] = useState(false)
  const [showPromptEditor, setShowPromptEditor] = useState(false)
  const [editingPrompt, setEditingPrompt] = useState('')
  const [logs, setLogs] = useState([])

  // Estados para TTS integrado
  const [ttsProvider, setTtsProvider] = useState('elevenlabs')
  const [isGeneratingTTS, setIsGeneratingTTS] = useState(false)
  const [ttsSegments, setTtsSegments] = useState([])
  const [finalTTSAudio, setFinalTTSAudio] = useState(null)
  const [ttsError, setTtsError] = useState('')
  const [segmentAudio, setSegmentAudio] = useState(true)
  const [maxCharsPerSegment, setMaxCharsPerSegment] = useState(2000)
  const [isJoiningAudio, setIsJoiningAudio] = useState(false)

  const [ttsSettings, setTtsSettings] = useState({
    elevenlabs: {
      voice_id: 'default',
      model_id: 'eleven_multilingual_v2',
      stability: 0.5,
      similarity_boost: 0.5,
      style: 0.0,
      use_speaker_boost: true
    },
    gemini: {
      voice_name: 'Aoede',
      model: 'gemini-2.5-flash-preview-tts',
      speed: 1.0,
      pitch: 0.0,
      volume_gain_db: 0.0
    },
    kokoro: {
      voice: 'af_bella',
      kokoro_url: 'http://localhost:8880',
      speed: 1.0,
      language: 'en'
    }
  })
  
  // Estados para configuração de automação
  const [automationConfig, setAutomationConfig] = useState({
    channel_url: '',
    max_titles: 5,
    min_views: 1000,
    days: 30,
    ai_provider: 'auto',
    openrouter_model: 'auto',
    number_of_chapters: 8,
    titles_count: 5,
    use_custom_prompt: false,
    custom_prompt: '',
    auto_select_best: true,
    generate_images: true,
    generate_audio: false,
    tts_provider: 'gemini'
  })

  const workflowSteps = [
    {
      id: 'input',
      title: 'Roteiro Original',
      description: 'Cole o roteiro original aqui',
      icon: FileText,
      color: 'blue'
    },
    {
      id: 'translation',
      title: 'Tradução',
      description: 'Traduzir roteiro se necessário',
      icon: Languages,
      color: 'green'
    },
    {
      id: 'narrative',
      title: 'Narrativa por Capítulo',
      description: 'Desenvolver narrativa detalhada',
      icon: BookOpen,
      color: 'purple'
    },
    {
      id: 'rewrite',
      title: 'Reescrita com Gancho',
      description: 'Adicionar ganchos sensacionais',
      icon: Zap,
      color: 'yellow'
    },
    {
      id: 'chapters',
      title: 'Gerar 8 Capítulos',
      description: 'Dividir em 8 capítulos estruturados',
      icon: Hash,
      color: 'red'
    },
    {
      id: 'tts',
      title: 'Text-to-Speech',
      description: 'Preparar para narração por voz',
      icon: Mic,
      color: 'blue'
    },
    {
      id: 'images',
      title: 'Geração de Imagens',
      description: 'Criar prompts para imagens',
      icon: Image,
      color: 'orange'
    },
    {
      id: 'final',
      title: 'Polimento Final',
      description: 'Revisão e otimização final',
      icon: CheckCircle,
      color: 'emerald'
    }
  ]

  const handleConfigChange = (field, value) => {
    setAutomationConfig(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleStepProcess = async (stepId) => {
    setIsProcessing(true)
    addLog(`▶️ Iniciando processamento: ${workflowSteps.find(s => s.id === stepId)?.title}`, 'info')
    
    try {
      const response = await fetch('http://localhost:5000/api/automations/process-step', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          step_id: stepId,
          workflow_data: workflowData,
          config: automationConfig,
          prompt: prompts[stepId]
        })
      })

      const data = await response.json()

      if (data.success) {
        // Atualizar dados do workflow com base no passo processado
        switch(stepId) {
          case 'translation':
            setWorkflowData(prev => ({
              ...prev,
              translatedScript: data.result.translated_script || `[TRADUZIDO] ${prev.originalScript}`
            }))
            break
          case 'narrative':
            setWorkflowData(prev => ({
              ...prev,
              narrativeChapters: data.result.narrative_chapters || ['Capítulo 1 narrativo...', 'Capítulo 2 narrativo...']
            }))
            break
          case 'rewrite':
            setWorkflowData(prev => ({
              ...prev,
              rewrittenScript: data.result.rewritten_script || `[REESCRITO COM GANCHOS] ${prev.translatedScript || prev.originalScript}`
            }))
            break
          case 'chapters':
            setWorkflowData(prev => ({
              ...prev,
              finalChapters: data.result.final_chapters || Array.from({length: 8}, (_, i) => `Capítulo ${i+1}: Conteúdo desenvolvido...`)
            }))
            break
          case 'tts':
            setWorkflowData(prev => ({
              ...prev,
              generatedAudio: data.result.audio_url || null
            }))
            break
          case 'images':
            setWorkflowData(prev => ({
              ...prev,
              generatedImages: data.result.image_prompts || []
            }))
            break
          case 'final':
            setWorkflowData(prev => ({
              ...prev,
              finalScript: data.result.final_script || `[ROTEIRO FINAL POLIDO]\n\n${prev.finalChapters.join('\n\n')}`
            }))
            break
        }
        addLog(`✅ ${workflowSteps.find(s => s.id === stepId)?.title} concluído com sucesso!`, 'success')
      } else {
        addLog(`❌ Erro: ${data.error}`, 'error')
      }
    } catch (error) {
      addLog(`❌ Erro de conexão: ${error.message}`, 'error')
    } finally {
      setIsProcessing(false)
      if (currentStep < workflowSteps.length - 1) {
        setCurrentStep(currentStep + 1)
      }
    }
  }

  const openPromptEditor = (promptKey) => {
    setEditingPrompt(promptKey)
    setShowPromptEditor(true)
  }

  const savePrompt = () => {
    setPrompts(prev => ({
      ...prev,
      [editingPrompt]: customPrompts[editingPrompt]
    }))
    setShowPromptEditor(false)
  }

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [...prev, { timestamp, message, type }])
  }

  const clearLogs = () => {
    setLogs([])
  }

  // Função para segmentar texto
  const segmentText = (text, maxChars = 4000) => {
    const segments = []
    const sentences = text.split(/[.!?]+/).filter(s => s.trim())

    let currentSegment = ''

    for (const sentence of sentences) {
      const trimmedSentence = sentence.trim()
      if (!trimmedSentence) continue

      const potentialSegment = currentSegment + (currentSegment ? '. ' : '') + trimmedSentence

      if (potentialSegment.length <= maxChars) {
        currentSegment = potentialSegment
      } else {
        if (currentSegment) {
          segments.push(currentSegment + '.')
          currentSegment = trimmedSentence
        } else {
          // Frase muito longa, dividir por palavras
          const words = trimmedSentence.split(' ')
          let wordSegment = ''

          for (const word of words) {
            const potentialWordSegment = wordSegment + (wordSegment ? ' ' : '') + word
            if (potentialWordSegment.length <= maxChars) {
              wordSegment = potentialWordSegment
            } else {
              if (wordSegment) {
                segments.push(wordSegment)
                wordSegment = word
              } else {
                segments.push(word)
              }
            }
          }

          if (wordSegment) {
            currentSegment = wordSegment
          }
        }
      }
    }

    if (currentSegment) {
      segments.push(currentSegment + '.')
    }

    return segments.filter(s => s.trim())
  }

  // Função para gerar TTS
  const generateTTSAudio = async () => {
    if (!workflowData.finalScript && !workflowData.rewrittenScript) {
      setTtsError('Nenhum roteiro encontrado para gerar áudio')
      return
    }

    setIsGeneratingTTS(true)
    setTtsError('')
    setTtsSegments([])
    setFinalTTSAudio(null)

    try {
      // Obter chaves de API
      let apiKeys = JSON.parse(localStorage.getItem('api_keys') || '{}')
      
      const hasElevenLabs = !!apiKeys.elevenlabs
      const hasGemini = !!(apiKeys.gemini_1 || apiKeys.gemini)

      // Preparar texto do roteiro
      let fullText = workflowData.finalScript || workflowData.rewrittenScript || workflowData.originalScript

      if (!fullText.trim()) {
        throw new Error('Nenhum texto encontrado para gerar áudio')
      }

      // Segmentar texto se necessário
      const textSegments = segmentAudio ? segmentText(fullText, maxCharsPerSegment) : [fullText]

      console.log(`🎵 Gerando ${textSegments.length} segmentos de áudio...`)

      // Determinar configurações baseado no provider
      let endpoint, apiKey, baseRequestData

      if (ttsProvider === 'elevenlabs') {
        if (!apiKeys.elevenlabs) {
          throw new Error('Chave da API ElevenLabs não configurada')
        }

        endpoint = '/api/automations/generate-tts-elevenlabs'
        apiKey = apiKeys.elevenlabs
        baseRequestData = {
          api_key: apiKey,
          voice_id: ttsSettings.elevenlabs.voice_id,
          model_id: ttsSettings.elevenlabs.model_id,
          stability: ttsSettings.elevenlabs.stability,
          similarity_boost: ttsSettings.elevenlabs.similarity_boost,
          style: ttsSettings.elevenlabs.style,
          use_speaker_boost: ttsSettings.elevenlabs.use_speaker_boost
        }
      } else if (ttsProvider === 'gemini') {
        endpoint = '/api/automations/generate-tts'
        baseRequestData = {
          voice_name: ttsSettings.gemini.voice_name,
          model: ttsSettings.gemini.model,
          speed: ttsSettings.gemini.speed,
          pitch: ttsSettings.gemini.pitch,
          volume_gain_db: ttsSettings.gemini.volume_gain_db
        }
      } else if (ttsProvider === 'kokoro') {
        endpoint = '/api/automations/generate-tts-kokoro'
        baseRequestData = {
          voice: ttsSettings.kokoro.voice,
          kokoro_url: ttsSettings.kokoro.kokoro_url,
          speed: ttsSettings.kokoro.speed,
          language: ttsSettings.kokoro.language
        }
      }

      // Gerar áudio para cada segmento
      const segments = []
      for (let i = 0; i < textSegments.length; i++) {
        const segment = textSegments[i]

        console.log(`🎵 Gerando segmento ${i + 1}/${textSegments.length}...`)

        const requestData = {
          ...baseRequestData,
          text: segment
        }

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })

        const result = await response.json()

        if (result.success) {
          segments.push({
            index: i + 1,
            text: segment.substring(0, 100) + (segment.length > 100 ? '...' : ''),
            filename: result.data.filename,
            audio_url: result.data.audio_url,
            duration: result.data.duration,
            size: result.data.size
          })
        } else {
          throw new Error(`Erro no segmento ${i + 1}: ${result.error}`)
        }
      }

      setTtsSegments(segments)
      addLog(`✅ ${segments.length} segmentos de áudio gerados com sucesso!`, 'success')

    } catch (error) {
      console.error('❌ Erro na geração de TTS:', error)
      setTtsError(error.message)
      addLog(`❌ Erro na geração de TTS: ${error.message}`, 'error')
    } finally {
      setIsGeneratingTTS(false)
    }
  }

  // Função para juntar áudios
  const joinTTSAudio = async () => {
    if (ttsSegments.length === 0) return

    setIsJoiningAudio(true)
    setTtsError('')

    try {
      const response = await fetch('/api/automations/join-audio', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          segments: ttsSegments.map(seg => ({
            filename: seg.filename,
            audio_url: seg.audio_url
          }))
        })
      })

      const result = await response.json()

      if (result.success) {
        setFinalTTSAudio(result.data)
        addLog('✅ Áudios unidos com sucesso!', 'success')
      } else {
        throw new Error(result.error)
      }
    } catch (error) {
      console.error('❌ Erro ao unir áudios:', error)
      setTtsError(error.message)
      addLog(`❌ Erro ao unir áudios: ${error.message}`, 'error')
    } finally {
      setIsJoiningAudio(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">🤖 Automações de Conteúdo</h1>
        <p className="text-gray-400">Fluxos automatizados completos para criação de conteúdo para YouTube</p>
      </div>

      {/* Configurações Globais */}
      <div className="bg-gray-800 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Settings size={20} />
          <span>Configurações da Automação</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Canal do YouTube
            </label>
            <input
              type="text"
              value={automationConfig.channel_url}
              onChange={(e) => handleConfigChange('channel_url', e.target.value)}
              placeholder="@MrBeast ou UCX6OQ3DkcsbYNE6H8uQQuVA"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Provedor IA
            </label>
            <select
              value={automationConfig.ai_provider}
              onChange={(e) => handleConfigChange('ai_provider', e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            >
              <option value="auto">Automático</option>
              <option value="gemini">Google Gemini</option>
              <option value="openrouter">OpenRouter</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Número de capítulos
            </label>
            <input
              type="number"
              value={automationConfig.number_of_chapters}
              onChange={(e) => handleConfigChange('number_of_chapters', parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
              min="3"
              max="20"
            />
          </div>
        </div>

        <div className="mt-4 flex items-center space-x-6">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={automationConfig.generate_images}
              onChange={(e) => handleConfigChange('generate_images', e.target.checked)}
              className="rounded"
            />
            <span className="text-gray-300">Gerar imagens</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={automationConfig.generate_audio}
              onChange={(e) => handleConfigChange('generate_audio', e.target.checked)}
              className="rounded"
            />
            <span className="text-gray-300">Gerar áudio</span>
          </label>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          {workflowSteps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`
                w-10 h-10 rounded-full flex items-center justify-center
                ${index <= currentStep 
                  ? `bg-${step.color}-600 text-white` 
                  : 'bg-gray-700 text-gray-400'
                }`}
                onClick={() => !isProcessing && setCurrentStep(index)}
                style={{ cursor: isProcessing ? 'default' : 'pointer' }}
              >
                <step.icon size={20} />
              </div>
              {index < workflowSteps.length - 1 && (
                <div className={`
                  w-16 h-1 mx-2
                  ${index < currentStep ? `bg-${step.color}-600` : 'bg-gray-700'}
                `} />
              )}
            </div>
          ))}
        </div>
        
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-1">
            {workflowSteps[currentStep]?.title}
          </h2>
          <p className="text-gray-400">
            {workflowSteps[currentStep]?.description}
          </p>
        </div>
      </div>

      {/* Current Step Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input/Output Area */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <FileText className="mr-2" size={20} />
            {currentStep === 0 ? 'Entrada' : 'Resultado'}
          </h3>
          
          {currentStep === 0 ? (
            <textarea
              value={workflowData.originalScript}
              onChange={(e) => setWorkflowData(prev => ({
                ...prev,
                originalScript: e.target.value
              }))}
              placeholder="Cole seu roteiro original aqui..."
              className="w-full h-64 bg-gray-700 text-white p-4 rounded-lg resize-none"
            />
          ) : (
            <div className="bg-gray-700 p-4 rounded-lg h-64 overflow-y-auto">
              {currentStep === 1 && workflowData.translatedScript && (
                <pre className="whitespace-pre-wrap">{workflowData.translatedScript}</pre>
              )}
              {currentStep === 2 && workflowData.narrativeChapters.length > 0 && (
                <div>
                  {workflowData.narrativeChapters.map((chapter, i) => (
                    <div key={i} className="mb-4">
                      <h4 className="font-semibold text-blue-400">Capítulo {i+1}</h4>
                      <p>{chapter}</p>
                    </div>
                  ))}
                </div>
              )}
              {currentStep === 3 && workflowData.rewrittenScript && (
                <pre className="whitespace-pre-wrap">{workflowData.rewrittenScript}</pre>
              )}
              {currentStep === 4 && workflowData.finalChapters.length > 0 && (
                <div>
                  {workflowData.finalChapters.map((chapter, i) => (
                    <div key={i} className="mb-4">
                      <h4 className="font-semibold text-red-400">Capítulo {i+1}</h4>
                      <p>{chapter}</p>
                    </div>
                  ))}
                </div>
              )}
              {currentStep === 5 && (
                <div className="space-y-4">
                  <h4 className="font-semibold text-blue-400 mb-2">📊 Resultados do TTS</h4>
                  
                  {/* Erro de TTS */}
                  {ttsError && (
                    <div className="p-4 bg-red-900/30 border border-red-600 rounded-lg">
                      <span className="text-red-200">{ttsError}</span>
                    </div>
                  )}

                  {/* Segmentos gerados */}
                  {ttsSegments.length > 0 && (
                    <div className="space-y-3">
                      <div className="p-4 bg-green-900/30 border border-green-600 rounded-lg">
                        <div className="flex items-center space-x-2 text-green-200">
                          <CheckCircle className="w-5 h-5" />
                          <span>{ttsSegments.length} segmentos gerados com sucesso!</span>
                        </div>
                      </div>

                      {ttsSegments.length > 1 && (
                        <button
                          onClick={joinTTSAudio}
                          disabled={isJoiningAudio}
                          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                        >
                          {isJoiningAudio ? (
                            <>
                              <Loader2 className="w-4 h-4 animate-spin" />
                              <span>Unindo Áudios...</span>
                            </>
                          ) : (
                            <>
                              <Volume2 className="w-4 h-4" />
                              <span>Unir Todos os Segmentos</span>
                            </>
                          )}
                        </button>
                      )}

                      {/* Lista de segmentos */}
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {ttsSegments.map((segment, index) => (
                          <div key={index} className="p-3 bg-gray-700 rounded-lg">
                            <div className="flex items-center justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-1">
                                  <span className="text-sm font-medium text-white">Segmento {segment.index}</span>
                                  <span className="text-xs text-gray-400">({segment.duration || 'N/A'}s)</span>
                                </div>
                                <p className="text-xs text-gray-300 truncate">{segment.text}</p>
                              </div>
                              <div className="flex items-center space-x-2">
                                <button
                                  onClick={() => {
                                    const audio = new Audio(segment.audio_url)
                                    audio.play()
                                  }}
                                  className="p-2 bg-green-600 text-white rounded hover:bg-green-700"
                                >
                                  <Play className="w-4 h-4" />
                                </button>
                                <a
                                  href={`/api/automations/download/${segment.filename}`}
                                  download={segment.filename}
                                  className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                                >
                                  <Download className="w-4 h-4" />
                                </a>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Áudio final */}
                  {finalTTSAudio && (
                    <div className="p-4 bg-green-900/30 border border-green-600 rounded-lg">
                      <h5 className="text-lg font-medium text-green-200 mb-3">🎵 Áudio Final Gerado</h5>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">Tamanho:</span>
                          <span className="ml-2 text-white">{finalTTSAudio.size ? `${(finalTTSAudio.size / 1024 / 1024).toFixed(1)} MB` : 'N/A'}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Duração:</span>
                          <span className="ml-2 text-white">{finalTTSAudio.duration ? `${Math.floor(finalTTSAudio.duration / 60)}:${Math.floor(finalTTSAudio.duration % 60).toString().padStart(2, '0')}` : 'N/A'}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Segmentos:</span>
                          <span className="ml-2 text-white">{finalTTSAudio.segments_count} segmentos</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Provedor:</span>
                          <span className="ml-2 text-white">{ttsProvider}</span>
                        </div>
                      </div>
                      <div className="flex space-x-3 mt-4">
                        <button
                          onClick={() => {
                            const audio = new Audio(`/api/automations/audio/${finalTTSAudio.filename}`)
                            audio.play()
                          }}
                          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2"
                        >
                          <Play className="w-4 h-4" />
                          <span>Reproduzir</span>
                        </button>
                        <a
                          href={`/api/automations/download/${finalTTSAudio.filename}`}
                          download={finalTTSAudio.filename}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
                        >
                          <Download className="w-4 h-4" />
                          <span>Download</span>
                        </a>
                      </div>
                    </div>
                  )}

                  {/* Fallback para áudio gerado pelo workflow */}
                  {!ttsSegments.length && !finalTTSAudio && workflowData.generatedAudio && (
                    <div>
                      <h4 className="font-semibold text-blue-400 mb-2">Áudio Gerado</h4>
                      <div>
                        <audio controls className="w-full mb-4">
                          <source src={workflowData.generatedAudio} type="audio/mp3" />
                          Seu navegador não suporta o elemento de áudio.
                        </audio>
                        <button className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm flex items-center">
                          <Download size={14} className="mr-1" />
                          Baixar Áudio
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Mensagem quando nenhum áudio foi gerado */}
                  {!ttsSegments.length && !finalTTSAudio && !workflowData.generatedAudio && (
                    <p className="text-gray-400">Nenhum áudio gerado ainda. Use as configurações ao lado para gerar áudio TTS.</p>
                  )}
                </div>
              )}
              {currentStep === 6 && (
                <div>
                  <h4 className="font-semibold text-orange-400 mb-2">Prompts para Imagens</h4>
                  {workflowData.generatedImages.length > 0 ? (
                    <div className="space-y-4">
                      {workflowData.generatedImages.map((prompt, i) => (
                        <div key={i} className="p-3 bg-gray-800 rounded-lg">
                          <h5 className="text-sm font-medium text-orange-300 mb-1">Imagem {i+1}</h5>
                          <p className="text-sm">{prompt}</p>
                          <button className="mt-2 px-2 py-1 bg-gray-700 text-xs text-gray-300 rounded hover:bg-gray-600 flex items-center">
                            <Copy size={12} className="mr-1" />
                            Copiar Prompt
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400">Nenhum prompt de imagem gerado ainda. Execute este passo para gerar.</p>
                  )}
                </div>
              )}
              {currentStep === 7 && workflowData.finalScript && (
                <pre className="whitespace-pre-wrap">{workflowData.finalScript}</pre>
              )}
            </div>
          )}
        </div>

        {/* Prompt Editor Area / TTS Configuration */}
        <div className="bg-gray-800 rounded-lg p-6">
          {currentStep === 5 ? (
            /* TTS Configuration */
            <div>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                <Mic size={20} />
                <span>Configurações de TTS</span>
              </h3>
              
              <div className="space-y-4">
                {/* Provedor de TTS */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Provedor de TTS
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    <div
                      onClick={() => setTtsProvider('elevenlabs')}
                      className={`bg-gray-700 border rounded-lg p-3 cursor-pointer transition-colors ${
                        ttsProvider === 'elevenlabs'
                          ? 'border-purple-500 bg-purple-900/30'
                          : 'border-gray-600 hover:border-purple-500'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <Mic className="w-4 h-4 text-purple-400" />
                        <span className="text-white font-medium">ElevenLabs</span>
                      </div>
                      <p className="text-xs text-gray-400 mt-1">Melhor qualidade</p>
                    </div>
                    <div
                      onClick={() => setTtsProvider('gemini')}
                      className={`bg-gray-700 border rounded-lg p-3 cursor-pointer transition-colors ${
                        ttsProvider === 'gemini'
                          ? 'border-blue-500 bg-blue-900/30'
                          : 'border-gray-600 hover:border-blue-500'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <Bot className="w-4 h-4 text-blue-400" />
                        <span className="text-white font-medium">Gemini TTS</span>
                      </div>
                      <p className="text-xs text-gray-400 mt-1">Gratuito</p>
                    </div>
                    <div
                      onClick={() => setTtsProvider('kokoro')}
                      className={`bg-gray-700 border rounded-lg p-3 cursor-pointer transition-colors ${
                        ttsProvider === 'kokoro'
                          ? 'border-green-500 bg-green-900/30'
                          : 'border-gray-600 hover:border-green-500'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <Zap className="w-4 h-4 text-green-400" />
                        <span className="text-white font-medium">Kokoro TTS</span>
                      </div>
                      <p className="text-xs text-gray-400 mt-1">Local/Rápido</p>
                    </div>
                  </div>
                </div>

                {/* Configurações de Segmentação */}
                <div className="space-y-3">
                  <div className="flex items-center space-x-3 p-3 bg-blue-900/30 border border-blue-600 rounded-lg">
                    <input
                      type="checkbox"
                      id="segmentAudio"
                      checked={segmentAudio}
                      onChange={(e) => setSegmentAudio(e.target.checked)}
                      className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="segmentAudio" className="text-sm font-medium text-blue-200">
                      Segmentar áudio (recomendado para textos longos)
                    </label>
                  </div>

                  {segmentAudio && (
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Máximo de caracteres por segmento
                      </label>
                      <select
                        value={maxCharsPerSegment}
                        onChange={(e) => setMaxCharsPerSegment(parseInt(e.target.value))}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value={2000}>2.000 caracteres (mais seguro)</option>
                        <option value={3000}>3.000 caracteres (balanceado)</option>
                        <option value={4000}>4.000 caracteres (máximo recomendado)</option>
                        <option value={5000}>5.000 caracteres (pode dar erro)</option>
                      </select>
                      <p className="text-xs text-gray-400 mt-1">
                        Textos muito longos podem causar erro nas APIs. Segmentar é mais seguro.
                      </p>
                    </div>
                  )}
                </div>

                {/* Configurações específicas do provedor */}
                {ttsProvider === 'elevenlabs' && (
                  <div className="space-y-3">
                    <h5 className="text-md font-medium text-white">🎤 Configurações ElevenLabs</h5>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Voz</label>
                      <select
                        value={ttsSettings.elevenlabs.voice_id}
                        onChange={(e) => setTtsSettings(prev => ({
                          ...prev,
                          elevenlabs: { ...prev.elevenlabs, voice_id: e.target.value }
                        }))}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="default">Rachel (Padrão)</option>
                        <option value="21m00Tcm4TlvDq8ikWAM">Rachel - Feminina Americana</option>
                        <option value="AZnzlk1XvdvUeBnXmlld">Domi - Feminina Jovem</option>
                        <option value="EXAVITQu4vr4xnSDxMaL">Bella - Feminina Suave</option>
                        <option value="ErXwobaYiN019PkySvjV">Antoni - Masculina Americana</option>
                        <option value="VR6AewLTigWG4xSOukaG">Arnold - Masculina Grave</option>
                        <option value="pNInz6obpgDQGcFmaJgB">Adam - Masculina Profunda</option>
                      </select>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Estabilidade: {ttsSettings.elevenlabs.stability}
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={ttsSettings.elevenlabs.stability}
                          onChange={(e) => setTtsSettings(prev => ({
                            ...prev,
                            elevenlabs: { ...prev.elevenlabs, stability: parseFloat(e.target.value) }
                          }))}
                          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Similaridade: {ttsSettings.elevenlabs.similarity_boost}
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={ttsSettings.elevenlabs.similarity_boost}
                          onChange={(e) => setTtsSettings(prev => ({
                            ...prev,
                            elevenlabs: { ...prev.elevenlabs, similarity_boost: parseFloat(e.target.value) }
                          }))}
                          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {ttsProvider === 'gemini' && (
                  <div className="space-y-3">
                    <h5 className="text-md font-medium text-white">🤖 Configurações Gemini TTS</h5>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Voz</label>
                      <select
                        value={ttsSettings.gemini.voice_name}
                        onChange={(e) => setTtsSettings(prev => ({
                          ...prev,
                          gemini: { ...prev.gemini, voice_name: e.target.value }
                        }))}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="Aoede">Aoede - Feminina Suave</option>
                        <option value="Charon">Charon - Masculina Grave</option>
                        <option value="Fenrir">Fenrir - Masculina Forte</option>
                        <option value="Kore">Kore - Feminina Jovem</option>
                        <option value="Puck">Puck - Masculina Alegre</option>
                        <option value="Sage">Sage - Feminina Sábia</option>
                      </select>
                    </div>

                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Velocidade: {ttsSettings.gemini.speed}x
                        </label>
                        <input
                          type="range"
                          min="0.5"
                          max="2.0"
                          step="0.1"
                          value={ttsSettings.gemini.speed}
                          onChange={(e) => setTtsSettings(prev => ({
                            ...prev,
                            gemini: { ...prev.gemini, speed: parseFloat(e.target.value) }
                          }))}
                          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Tom: {ttsSettings.gemini.pitch > 0 ? '+' : ''}{ttsSettings.gemini.pitch}
                        </label>
                        <input
                          type="range"
                          min="-20"
                          max="20"
                          step="1"
                          value={ttsSettings.gemini.pitch}
                          onChange={(e) => setTtsSettings(prev => ({
                            ...prev,
                            gemini: { ...prev.gemini, pitch: parseFloat(e.target.value) }
                          }))}
                          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Volume: {ttsSettings.gemini.volume_gain_db > 0 ? '+' : ''}{ttsSettings.gemini.volume_gain_db}dB
                        </label>
                        <input
                          type="range"
                          min="-96"
                          max="16"
                          step="1"
                          value={ttsSettings.gemini.volume_gain_db}
                          onChange={(e) => setTtsSettings(prev => ({
                            ...prev,
                            gemini: { ...prev.gemini, volume_gain_db: parseFloat(e.target.value) }
                          }))}
                          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {ttsProvider === 'kokoro' && (
                  <div className="space-y-3">
                    <h5 className="text-md font-medium text-white">⚡ Configurações Kokoro TTS</h5>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">URL do Servidor Kokoro</label>
                      <input
                        type="text"
                        value={ttsSettings.kokoro.kokoro_url}
                        onChange={(e) => setTtsSettings(prev => ({
                          ...prev,
                          kokoro: { ...prev.kokoro, kokoro_url: e.target.value }
                        }))}
                        placeholder="http://localhost:8880"
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                      <p className="text-xs text-gray-400 mt-1">URL onde o servidor Kokoro FastAPI está rodando</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Idioma</label>
                      <select
                        value={ttsSettings.kokoro.language}
                        onChange={(e) => {
                          const newLanguage = e.target.value
                          let defaultVoice = 'af_bella'
                          if (newLanguage === 'pt') defaultVoice = 'pf_dora'
                          else if (newLanguage === 'zh') defaultVoice = 'zf_xiaobei'
                          else if (newLanguage === 'ja') defaultVoice = 'jf_alpha'

                          setTtsSettings(prev => ({
                            ...prev,
                            kokoro: {
                              ...prev.kokoro,
                              language: newLanguage,
                              voice: defaultVoice
                            }
                          }))
                        }}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        <option value="en">🇺🇸 Inglês (English)</option>
                        <option value="pt">🇵🇹 Português (Portuguese)</option>
                        <option value="zh">🇨🇳 Chinês (Chinese)</option>
                        <option value="ja">🇯🇵 Japonês (Japanese)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Voz</label>
                      <select
                        value={ttsSettings.kokoro.voice}
                        onChange={(e) => setTtsSettings(prev => ({
                          ...prev,
                          kokoro: { ...prev.kokoro, voice: e.target.value }
                        }))}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        {ttsSettings.kokoro.language === 'pt' ? (
                          <>
                            <option value="pf_dora">🇵🇹 pf_dora - Feminina Portuguesa</option>
                            <option value="pm_alex">🇵🇹 pm_alex - Masculina Portuguesa</option>
                            <option value="pm_santa">🇵🇹 pm_santa - Masculina Portuguesa (Santa)</option>
                          </>
                        ) : ttsSettings.kokoro.language === 'zh' ? (
                          <>
                            <option value="zf_xiaobei">🇨🇳 zf_xiaobei - Feminina Chinesa</option>
                            <option value="zf_xiaoni">🇨🇳 zf_xiaoni - Feminina Chinesa</option>
                            <option value="zf_xiaoxiao">🇨🇳 zf_xiaoxiao - Feminina Chinesa</option>
                            <option value="zm_yunjian">🇨🇳 zm_yunjian - Masculina Chinesa</option>
                            <option value="zm_yunxi">🇨🇳 zm_yunxi - Masculina Chinesa</option>
                          </>
                        ) : ttsSettings.kokoro.language === 'ja' ? (
                          <>
                            <option value="jf_alpha">🇯🇵 jf_alpha - Feminina Japonesa</option>
                            <option value="jf_gongitsune">🇯🇵 jf_gongitsune - Feminina Japonesa</option>
                            <option value="jf_nezumi">🇯🇵 jf_nezumi - Feminina Japonesa</option>
                            <option value="jm_kumo">🇯🇵 jm_kumo - Masculina Japonesa</option>
                          </>
                        ) : (
                          <>
                            <option value="af_bella">af_bella - Feminina Americana</option>
                            <option value="af_sarah">af_sarah - Feminina Americana</option>
                            <option value="af_nicole">af_nicole - Feminina Americana</option>
                            <option value="af_sky">af_sky - Feminina Americana</option>
                            <option value="af_heart">af_heart - Feminina Americana</option>
                            <option value="am_adam">am_adam - Masculina Americana</option>
                            <option value="am_michael">am_michael - Masculina Americana</option>
                            <option value="bf_emma">bf_emma - Feminina Britânica</option>
                            <option value="bf_isabella">bf_isabella - Feminina Britânica</option>
                            <option value="bm_george">bm_george - Masculina Britânica</option>
                            <option value="bm_lewis">bm_lewis - Masculina Britânica</option>
                          </>
                        )}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Velocidade: {ttsSettings.kokoro.speed}x
                      </label>
                      <input
                        type="range"
                        min="0.5"
                        max="2.0"
                        step="0.1"
                        value={ttsSettings.kokoro.speed}
                        onChange={(e) => setTtsSettings(prev => ({
                          ...prev,
                          kokoro: { ...prev.kokoro, speed: parseFloat(e.target.value) }
                        }))}
                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                      />
                    </div>
                  </div>
                )}

                {/* Botão para gerar TTS */}
                <div className="mt-6">
                  <button
                    onClick={generateTTSAudio}
                    disabled={isGeneratingTTS}
                    className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {isGeneratingTTS ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Gerando Áudio...</span>
                      </>
                    ) : (
                      <>
                        <Volume2 className="w-5 h-5" />
                        <span>Gerar Áudio TTS</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          ) : (
            /* Prompt Editor */
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold flex items-center">
                  <Settings className="mr-2" size={20} />
                  Prompt Personalizado
                </h3>
                {currentStep > 0 && (
                  <button
                    onClick={() => openPromptEditor(workflowSteps[currentStep].id)}
                    className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                  >
                    Editar Prompt
                  </button>
                )}
              </div>
              
              {currentStep > 0 && (
                <div className="bg-gray-700 p-4 rounded-lg h-64 overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm">
                    {prompts[workflowSteps[currentStep].id]}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-8 flex justify-center space-x-4">
        {currentStep > 0 && (
          <button
            onClick={() => setCurrentStep(currentStep - 1)}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Voltar
          </button>
        )}
        
        {currentStep === 0 ? (
          <button
            onClick={() => setCurrentStep(1)}
            disabled={!workflowData.originalScript.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Iniciar Workflow
          </button>
        ) : (
          <button
            onClick={() => handleStepProcess(workflowSteps[currentStep].id)}
            disabled={isProcessing}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center"
          >
            {isProcessing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Processando...
              </>
            ) : (
              <>
                <Play className="mr-2" size={16} />
                Executar {workflowSteps[currentStep].title}
              </>
            )}
          </button>
        )}
      </div>

      {/* Logs */}
      {logs.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6 mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Terminal size={20} />
              <span>Logs da Automação</span>
            </h3>
            <button
              onClick={clearLogs}
              className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
            >
              Limpar
            </button>
          </div>
          
          <div className="bg-gray-900 rounded-lg p-4 max-h-64 overflow-y-auto">
            {logs.map((log, index) => (
              <div key={index} className="flex items-start space-x-2 mb-2">
                <span className="text-gray-500 text-xs font-mono">{log.timestamp}</span>
                <span className={`text-sm ${
                  log.type === 'success' ? 'text-green-400' :
                  log.type === 'error' ? 'text-red-400' :
                  log.type === 'warning' ? 'text-yellow-400' :
                  'text-gray-300'
                }`}>
                  {log.message}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Prompt Editor Modal */}
      {showPromptEditor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold">
                Editar Prompt - {workflowSteps.find(s => s.id === editingPrompt)?.title}
              </h3>
              <button
                onClick={() => setShowPromptEditor(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            
            <textarea
              value={customPrompts[editingPrompt] || ''}
              onChange={(e) => setCustomPrompts(prev => ({
                ...prev,
                [editingPrompt]: e.target.value
              }))}
              className="w-full h-96 bg-gray-700 text-white p-4 rounded-lg resize-none"
              placeholder="Digite seu prompt personalizado..."
            />
            
            <div className="flex justify-end space-x-4 mt-4">
              <button
                onClick={() => setShowPromptEditor(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Cancelar
              </button>
              <button
                onClick={savePrompt}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Salvar Prompt
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  )
}

export default Automations
