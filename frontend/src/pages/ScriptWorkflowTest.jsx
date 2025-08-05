import React, { useState } from 'react'
import { 
  Play, 
  FileText, 
  Languages, 
  BookOpen, 
  Zap, 
  Hash,
  CheckCircle,
  Settings,
  Copy,
  Download
} from 'lucide-react'

const ScriptWorkflowTest = () => {
  const [currentStep, setCurrentStep] = useState(0)
  const [workflowData, setWorkflowData] = useState({
    originalScript: '',
    translatedScript: '',
    narrativeChapters: [],
    rewrittenScript: '',
    finalChapters: [],
    finalScript: ''
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

## Roteiro para polir:`
  })

  const [customPrompts, setCustomPrompts] = useState({ ...prompts })
  const [isProcessing, setIsProcessing] = useState(false)
  const [showPromptEditor, setShowPromptEditor] = useState(false)
  const [editingPrompt, setEditingPrompt] = useState('')

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
      id: 'final',
      title: 'Polimento Final',
      description: 'Revisão e otimização final',
      icon: CheckCircle,
      color: 'emerald'
    }
  ]

  const handleStepProcess = async (stepId) => {
    setIsProcessing(true)
    
    // Simular processamento (aqui você faria a chamada real para a API)
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Simular resultado baseado no step
    switch(stepId) {
      case 'translation':
        setWorkflowData(prev => ({
          ...prev,
          translatedScript: `[TRADUZIDO] ${prev.originalScript}`
        }))
        break
      case 'narrative':
        setWorkflowData(prev => ({
          ...prev,
          narrativeChapters: ['Capítulo 1 narrativo...', 'Capítulo 2 narrativo...']
        }))
        break
      case 'rewrite':
        setWorkflowData(prev => ({
          ...prev,
          rewrittenScript: `[REESCRITO COM GANCHOS] ${prev.translatedScript || prev.originalScript}`
        }))
        break
      case 'chapters':
        setWorkflowData(prev => ({
          ...prev,
          finalChapters: Array.from({length: 8}, (_, i) => `Capítulo ${i+1}: Conteúdo desenvolvido...`)
        }))
        break
      case 'final':
        setWorkflowData(prev => ({
          ...prev,
          finalScript: `[ROTEIRO FINAL POLIDO]\n\n${prev.finalChapters.join('\n\n')}`
        }))
        break
    }
    
    setIsProcessing(false)
    if (currentStep < workflowSteps.length - 1) {
      setCurrentStep(currentStep + 1)
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

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">🎬 Workflow de Roteiros - Teste</h1>
          <p className="text-gray-400">Sistema de prompts especializados para criação de roteiros</p>
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
                  }
                `}>
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
                {currentStep === 5 && workflowData.finalScript && (
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

export default ScriptWorkflowTest
