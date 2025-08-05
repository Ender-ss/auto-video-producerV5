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
  Hash
} from 'lucide-react'

const Automations = () => {
  const [currentStep, setCurrentStep] = useState(0)
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
                <div>
                  <h4 className="font-semibold text-blue-400 mb-2">Áudio Gerado</h4>
                  {workflowData.generatedAudio ? (
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
                  ) : (
                    <p className="text-gray-400">Nenhum áudio gerado ainda. Execute este passo para gerar.</p>
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

        {/* Prompt Editor Area */}
        <div className="bg-gray-800 rounded-lg p-6">
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
