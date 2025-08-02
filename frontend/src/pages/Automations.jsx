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
  Sparkles,
  Target,
  Layers,
  Workflow,
  XCircle,
  Copy,
  Calendar,
  Terminal,
  AlertTriangle
} from 'lucide-react'
import AutomationResults from '../components/AutomationResults'

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

  // Estados para geração de premissas
  const [isGeneratingPremises, setIsGeneratingPremises] = useState(false)
  const [generatedPremises, setGeneratedPremises] = useState(null)
  const [selectedTitles, setSelectedTitles] = useState([])
  const [premisePrompt, setPremisePrompt] = useState('')
  const [premiseAiProvider, setPremiseAiProvider] = useState('auto')
  const [openRouterModel, setOpenRouterModel] = useState('auto')

  // Estados para geração de roteiros
  const [isGeneratingScripts, setIsGeneratingScripts] = useState(false)
  const [generatedScripts, setGeneratedScripts] = useState(null)
  const [selectedPremise, setSelectedPremise] = useState(null)
  const [selectedTitle, setSelectedTitle] = useState('')
  const [scriptAiProvider, setScriptAiProvider] = useState('auto')
  const [scriptOpenRouterModel, setScriptOpenRouterModel] = useState('auto')
  const [numberOfChapters, setNumberOfChapters] = useState(8)
  const [scriptProgress, setScriptProgress] = useState({ current: 0, total: 0, stage: '' })

  // Estados para automação completa
  const [isRunningWorkflow, setIsRunningWorkflow] = useState(false)
  const [workflowProgress, setWorkflowProgress] = useState({
    current: 0,
    total: 4,
    stage: '',
    details: '',
    completed: []
  })
  const [workflowConfig, setWorkflowConfig] = useState({
    channel_url: '',
    max_titles: 5,
    min_views: 50,  // Reduzido de 1000 para 50
    days: 30,
    ai_provider: 'auto',
    openrouter_model: 'auto',
    number_of_chapters: 8,
    titles_count: 5,  // Quantidade de títulos a gerar
    use_custom_prompt: false,  // Se deve usar prompt personalizado
    custom_prompt: '',  // Prompt personalizado
    auto_select_best: true
  })
  const [workflowResults, setWorkflowResults] = useState(null)
  const [workflowLogs, setWorkflowLogs] = useState([])
  const [showLogs, setShowLogs] = useState(false)
  const [lastLogTimestamp, setLastLogTimestamp] = useState(0)

  // Estados para exibição de resultados
  const [showResults, setShowResults] = useState(false)
  const [automationResults, setAutomationResults] = useState(null)

  // Estados para controle de pausa
  const [isPaused, setIsPaused] = useState(false)

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

  // Carregar dados quando a aba de roteiros for selecionada
  useEffect(() => {
    if (activeTab === 'scripts') {
      // Carregar títulos gerados se não existirem
      if (!generatedTitles) {
        const savedTitles = localStorage.getItem('generated_titles')
        if (savedTitles) {
          setGeneratedTitles(JSON.parse(savedTitles))
        }
      }

      // Carregar premissas geradas se não existirem
      if (!generatedPremises) {
        const savedPremises = localStorage.getItem('generated_premises')
        if (savedPremises) {
          setGeneratedPremises(JSON.parse(savedPremises))
        }
      }

      // Carregar roteiros gerados se não existirem
      if (!generatedScripts) {
        const savedScripts = localStorage.getItem('generated_scripts')
        if (savedScripts) {
          setGeneratedScripts(JSON.parse(savedScripts))
        }
      }
    }
  }, [activeTab])

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

        // Limpar geração anterior para preparar nova remodelagem
        setGeneratedTitles(null)

        if (data.data.total_videos === 0) {
          alert('⚠️ Nenhum vídeo encontrado com os filtros aplicados. Tente diminuir o filtro de views mínimas.')
        } else {
          alert(`✅ Extração concluída! ${data.data.videos.length} vídeos encontrados.\n\n🎯 Títulos prontos para remodelagem na aba "Geração de Títulos"!`)
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
        // Salvar no localStorage
        localStorage.setItem('generated_titles', JSON.stringify(data.data))
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

  // Funções para geração de premissas
  const handleGeneratePremises = async () => {
    if (selectedTitles.length === 0) {
      alert('Selecione pelo menos um título para gerar premissas')
      return
    }

    setIsGeneratingPremises(true)

    try {
      const defaultPrompt = `# Gerador de Premissas Profissionais para Vídeos

Você é um especialista em criação de conteúdo e storytelling para YouTube. Sua tarefa é criar premissas envolventes e profissionais baseadas nos títulos fornecidos.

## Instruções:
1. Analise cada título fornecido
2. Crie uma premissa única e cativante para cada um
3. A premissa deve ter entre 100-200 palavras
4. Inclua elementos de storytelling (problema, conflito, resolução)
5. Mantenha o tom adequado ao nicho do título
6. Adicione ganchos emocionais e curiosidade

## Formato de Resposta:
Para cada título, forneça:

**TÍTULO:** [título original]
**PREMISSA:**
[Premissa detalhada com storytelling envolvente]

---

## Títulos para análise:`

      const prompt = premisePrompt || defaultPrompt
      const finalPrompt = `${prompt}\n\n${selectedTitles.map((title, i) => `${i + 1}. ${title}`).join('\n')}`

      const response = await fetch('http://localhost:5000/api/premise/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          titles: selectedTitles,
          prompt: finalPrompt,
          ai_provider: premiseAiProvider,
          openrouter_model: openRouterModel,
          api_keys: apiKeys
        })
      })

      const data = await response.json()

      if (data.success) {
        setGeneratedPremises(data.premises)
        // Salvar no localStorage
        localStorage.setItem('generated_premises', JSON.stringify(data.premises))
        alert(`✅ ${data.premises.length} premissas geradas com sucesso!`)
      } else {
        alert(`❌ Erro: ${data.error}`)
      }
    } catch (error) {
      alert(`❌ Erro de conexão: ${error.message}`)
    } finally {
      setIsGeneratingPremises(false)
    }
  }

  const toggleTitleSelection = (title) => {
    setSelectedTitles(prev =>
      prev.includes(title)
        ? prev.filter(t => t !== title)
        : [...prev, title]
    )
  }

  const copyPremiseToClipboard = (premise) => {
    navigator.clipboard.writeText(`${premise.title}\n\n${premise.premise}`)
    alert('Premissa copiada para a área de transferência!')
  }

  // Funções para geração de roteiros
  const handleGenerateScripts = async () => {
    if (!selectedTitle || !selectedPremise) {
      alert('Selecione um título e uma premissa para gerar o roteiro')
      return
    }

    setIsGeneratingScripts(true)
    setScriptProgress({ current: 0, total: numberOfChapters, stage: 'Iniciando...' })

    try {
      const response = await fetch('http://localhost:5000/api/scripts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: selectedTitle,
          premise: selectedPremise,
          ai_provider: scriptAiProvider,
          openrouter_model: scriptOpenRouterModel,
          number_of_chapters: numberOfChapters,
          api_keys: apiKeys
        })
      })

      const data = await response.json()

      if (data.success) {
        setGeneratedScripts(data.scripts)
        // Salvar no localStorage
        localStorage.setItem('generated_scripts', JSON.stringify(data.scripts))
        alert(`✅ Roteiro com ${data.scripts.chapters.length} capítulos gerado com sucesso!`)
      } else {
        alert(`❌ Erro: ${data.error}`)
      }
    } catch (error) {
      alert(`❌ Erro de conexão: ${error.message}`)
    } finally {
      setIsGeneratingScripts(false)
      setScriptProgress({ current: 0, total: 0, stage: '' })
    }
  }

  const copyScriptToClipboard = (script) => {
    const fullScript = `${script.title}\n\n${script.chapters.map((chapter, i) =>
      `CAPÍTULO ${i + 1}:\n${chapter.content}\n\n`
    ).join('')}`
    navigator.clipboard.writeText(fullScript)
    alert('Roteiro completo copiado para a área de transferência!')
  }

  const copyChapterToClipboard = (chapter, index) => {
    navigator.clipboard.writeText(`CAPÍTULO ${index + 1}:\n${chapter.content}`)
    alert(`Capítulo ${index + 1} copiado para a área de transferência!`)
  }

  // Função para buscar logs em tempo real
  const fetchWorkflowLogs = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/workflow/logs?since=${lastLogTimestamp}`)
      const data = await response.json()

      if (data.success && data.logs.length > 0) {
        setWorkflowLogs(prev => [...prev, ...data.logs])
        setLastLogTimestamp(data.logs[data.logs.length - 1].timestamp)
      }
    } catch (error) {
      console.error('Erro ao buscar logs:', error)
    }
  }

  // Polling de logs durante execução
  useEffect(() => {
    let interval
    if (isRunningWorkflow) {
      interval = setInterval(fetchWorkflowLogs, 1000) // Buscar logs a cada segundo
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [isRunningWorkflow, lastLogTimestamp])

  // Funções para automação completa
  const handleTestWorkflow = async () => {
    setIsRunningWorkflow(true)
    setIsPaused(false) // Reset estado de pausa
    setWorkflowProgress({
      current: 0,
      total: 4,
      stage: 'Iniciando teste de automação...',
      details: 'Usando dados simulados',
      completed: []
    })
    setWorkflowResults(null)
    setWorkflowLogs([])
    setLastLogTimestamp(0)
    setShowLogs(true) // Mostrar logs automaticamente

    // Limpar logs no backend
    try {
      await fetch('http://localhost:5000/api/workflow/logs/clear', { method: 'POST' })
    } catch (error) {
      console.error('Erro ao limpar logs:', error)
    }

    try {
      // Simular progresso visual
      const progressInterval = setInterval(() => {
        setWorkflowProgress(prev => {
          if (prev.current < prev.total) {
            const stages = [
              'Carregando dados simulados...',
              'Gerando títulos com IA...',
              'Criando premissas envolventes...',
              'Gerando roteiro completo...'
            ]
            return {
              ...prev,
              current: prev.current + 1,
              stage: stages[prev.current] || 'Processando...',
              details: `Etapa ${prev.current + 1} de ${prev.total}`
            }
          }
          return prev
        })
      }, 2000) // Atualiza a cada 2 segundos

      // Chamar endpoint de teste
      const response = await fetch('http://localhost:5000/api/workflow/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ai_provider: workflowConfig.ai_provider,
          openrouter_model: workflowConfig.openrouter_model,
          number_of_chapters: workflowConfig.number_of_chapters,
          titles_count: workflowConfig.titles_count || 5,
          use_custom_prompt: workflowConfig.use_custom_prompt || false,
          custom_prompt: workflowConfig.custom_prompt || '',
          api_keys: apiKeys
        })
      })

      clearInterval(progressInterval)

      const data = await response.json()

      if (data.success) {
        // Atualizar progresso final
        setWorkflowProgress({
          current: 4,
          total: 4,
          stage: 'Teste concluído com sucesso!',
          details: `Roteiro com ${data.results.scripts.chapters.length} capítulos gerado`,
          completed: ['extraction', 'titles', 'premises', 'scripts']
        })

        // Salvar resultados
        setWorkflowResults(data.results)
        localStorage.setItem('workflow_results', JSON.stringify(data.results))

        // Atualizar estados individuais
        setResults(data.results.extraction)
        setGeneratedTitles(data.results.titles)
        setGeneratedPremises(data.results.premises)
        setGeneratedScripts(data.results.scripts)

        // Salvar no localStorage
        localStorage.setItem('extracted_titles', JSON.stringify(data.results.extraction))
        localStorage.setItem('generated_titles', JSON.stringify(data.results.titles))
        localStorage.setItem('generated_premises', JSON.stringify(data.results.premises))
        localStorage.setItem('generated_scripts', JSON.stringify(data.results.scripts))

        // Preparar dados para exibição
        setAutomationResults(data.results)
        setShowResults(true)

        alert('🎉 Teste de automação finalizado com sucesso! Clique em "Ver Resultados" para visualizar.')
      } else {
        throw new Error(data.error || 'Erro desconhecido no teste')
      }

    } catch (error) {
      console.error('Erro no teste:', error)
      setWorkflowProgress(prev => ({
        ...prev,
        stage: 'Erro no teste',
        details: error.message
      }))
      alert(`❌ Erro no teste: ${error.message}`)
    } finally {
      setIsRunningWorkflow(false)
    }
  }

  const handleCompleteWorkflow = async () => {
    if (!workflowConfig.channel_url.trim()) {
      alert('Por favor, insira o nome ou ID do canal do YouTube')
      return
    }

    setIsRunningWorkflow(true)
    setIsPaused(false) // Reset estado de pausa
    setWorkflowProgress({
      current: 0,
      total: 4,
      stage: 'Iniciando automação completa...',
      details: '',
      completed: []
    })
    setWorkflowResults(null)

    try {
      // Simular progresso visual enquanto o backend processa
      const progressInterval = setInterval(() => {
        setWorkflowProgress(prev => {
          if (prev.current < prev.total) {
            const stages = [
              'Extraindo títulos do YouTube...',
              'Gerando novos títulos com IA...',
              'Criando premissas envolventes...',
              'Gerando roteiro completo...'
            ]
            return {
              ...prev,
              current: prev.current + 1,
              stage: stages[prev.current] || 'Processando...',
              details: `Etapa ${prev.current + 1} de ${prev.total}`
            }
          }
          return prev
        })
      }, 3000) // Atualiza a cada 3 segundos

      // Chamar endpoint de automação completa
      const response = await fetch('http://localhost:5000/api/workflow/complete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          channel_url: workflowConfig.channel_url,
          max_titles: workflowConfig.max_titles,
          min_views: workflowConfig.min_views,
          days: workflowConfig.days,
          ai_provider: workflowConfig.ai_provider,
          openrouter_model: workflowConfig.openrouter_model,
          number_of_chapters: workflowConfig.number_of_chapters,
          titles_count: workflowConfig.titles_count || 5,
          use_custom_prompt: workflowConfig.use_custom_prompt || false,
          custom_prompt: workflowConfig.custom_prompt || '',
          auto_select_best: workflowConfig.auto_select_best,
          api_keys: apiKeys
        })
      })

      clearInterval(progressInterval)

      const data = await response.json()

      if (data.success) {
        // Atualizar progresso final
        setWorkflowProgress({
          current: 4,
          total: 4,
          stage: 'Automação concluída com sucesso!',
          details: `Roteiro com ${data.results.scripts.chapters.length} capítulos gerado`,
          completed: ['extraction', 'titles', 'premises', 'scripts']
        })

        // Salvar resultados
        setWorkflowResults(data.results)
        localStorage.setItem('workflow_results', JSON.stringify(data.results))

        // Atualizar estados individuais para que apareçam nas outras abas
        setResults(data.results.extraction)
        setGeneratedTitles(data.results.titles)
        setGeneratedPremises(data.results.premises)
        setGeneratedScripts(data.results.scripts)

        // Salvar no localStorage
        localStorage.setItem('extracted_titles', JSON.stringify(data.results.extraction))
        localStorage.setItem('generated_titles', JSON.stringify(data.results.titles))
        localStorage.setItem('generated_premises', JSON.stringify(data.results.premises))
        localStorage.setItem('generated_scripts', JSON.stringify(data.results.scripts))

        // Preparar dados para exibição
        setAutomationResults(data.results)
        setShowResults(true)

        alert('🎉 Automação completa finalizada com sucesso! Clique em "Ver Resultados" para visualizar.')
      } else {
        throw new Error(data.error || 'Erro desconhecido na automação')
      }

    } catch (error) {
      console.error('Erro na automação:', error)
      setWorkflowProgress(prev => ({
        ...prev,
        stage: 'Erro na automação',
        details: error.message
      }))
      alert(`❌ Erro na automação: ${error.message}`)
    } finally {
      setIsRunningWorkflow(false)
      setIsPaused(false)
    }
  }

  // Funções de controle de workflow
  const pauseWorkflow = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/workflow/pause', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        setIsPaused(true)
      }
    } catch (error) {
      console.error('Erro ao pausar workflow:', error)
    }
  }

  const resumeWorkflow = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/workflow/resume', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        setIsPaused(false)
      }
    } catch (error) {
      console.error('Erro ao retomar workflow:', error)
    }
  }

  const cancelWorkflow = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/workflow/cancel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        setIsRunningWorkflow(false)
        setIsPaused(false)
        setWorkflowProgress({
          current: 0,
          total: 4,
          stage: 'Cancelado pelo usuário',
          details: '',
          completed: []
        })
      }
    } catch (error) {
      console.error('Erro ao cancelar workflow:', error)
    }
  }



  // Mock data para demonstração
  const automationTabs = [
    { id: 'youtube', label: 'Extração YouTube', icon: Youtube, color: 'red' },
    { id: 'titles', label: 'Geração de Títulos', icon: Wand2, color: 'blue' },
    { id: 'premise', label: 'Premissas', icon: Target, color: 'purple' },
    { id: 'scripts', label: 'Roteiros IA', icon: FileText, color: 'green' },
    { id: 'tts', label: 'Text-to-Speech', icon: Mic, color: 'yellow' },
    { id: 'video-edit', label: 'Editar Vídeo', icon: Video, color: 'pink' },
    { id: 'workflow', label: 'Fluxos Completos', icon: Workflow, color: 'indigo' }
  ]

  const aiAgents = [
    { id: 'gemini', name: 'Google Gemini', status: 'connected', cost: 'Gratuito' },
    { id: 'openai', name: 'OpenAI GPT-4', status: 'connected', cost: '$0.03/1K tokens' },
    { id: 'claude', name: 'Anthropic Claude', status: 'disconnected', cost: '$0.015/1K tokens' },
    { id: 'openrouter', name: 'OpenRouter', status: 'connected', cost: 'Variável' }
  ]

  // Modelos OpenRouter disponíveis
  const openRouterModels = [
    { id: 'auto', name: 'Automático (Melhor disponível)', free: true },
    { id: 'anthropic/claude-3.5-sonnet', name: 'Claude 3.5 Sonnet', free: false },
    { id: 'anthropic/claude-3-haiku', name: 'Claude 3 Haiku', free: false },
    { id: 'openai/gpt-4o', name: 'GPT-4o', free: false },
    { id: 'openai/gpt-4o-mini', name: 'GPT-4o Mini', free: false },
    { id: 'openai/gpt-3.5-turbo', name: 'GPT-3.5 Turbo', free: false },
    { id: 'google/gemini-pro-1.5', name: 'Gemini Pro 1.5', free: false },
    { id: 'meta-llama/llama-3.1-8b-instruct:free', name: 'Llama 3.1 8B', free: true },
    { id: 'meta-llama/llama-3.1-70b-instruct', name: 'Llama 3.1 70B', free: false },
    { id: 'mistralai/mistral-7b-instruct:free', name: 'Mistral 7B', free: true },
    { id: 'mistralai/mixtral-8x7b-instruct', name: 'Mixtral 8x7B', free: false },
    { id: 'qwen/qwen-2-7b-instruct:free', name: 'Qwen 2 7B', free: true },
    { id: 'microsoft/phi-3-medium-128k-instruct:free', name: 'Phi-3 Medium', free: true }
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
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setActiveTab('titles')}
                          className="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 transition-colors flex items-center space-x-1"
                        >
                          <Wand2 size={12} />
                          <span>Remodelar Títulos</span>
                        </button>
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
                <option value="auto">🤖 Automático (Híbrido)</option>
                <option value="openai">🧠 OpenAI GPT</option>
                <option value="openrouter">🌐 OpenRouter (Claude/Llama)</option>
                <option value="gemini">💎 Google Gemini</option>
              </select>
              <p className="text-xs text-gray-400 mt-1">
                💡 Automático tenta OpenAI → OpenRouter → Gemini
              </p>
            </div>

            {!results ? (
              <div className="p-4 bg-yellow-900/30 border border-yellow-700 rounded-lg">
                <p className="text-yellow-300 text-sm">
                  💡 <strong>Dica:</strong> Primeiro extraia títulos do YouTube para usar como base de {useCustomPrompt ? 'remodelagem' : 'análise'}.
                </p>
              </div>
            ) : (
              <div className="p-4 bg-green-900/30 border border-green-700 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-green-300 text-sm font-medium">
                    ✅ <strong>Fila de Remodelagem:</strong> {results.videos.length} títulos prontos
                  </p>
                  <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">
                    Em Fila
                  </span>
                </div>
                <div className="text-green-200 text-xs">
                  <p><strong>Canal:</strong> {results.channel_name || 'Canal extraído'}</p>
                  <p><strong>Títulos na fila:</strong></p>
                  <div className="mt-2 space-y-1 max-h-32 overflow-y-auto bg-green-800/20 rounded p-2">
                    {results.videos.map((video, index) => (
                      <div key={index} className="flex items-start space-x-2 text-green-100 text-xs">
                        <span className="text-green-400 font-mono">{index + 1}.</span>
                        <span className="flex-1">{video.title}</span>
                        <span className="text-green-300 text-xs">
                          {video.views ? `${video.views} views` : ''}
                        </span>
                      </div>
                    ))}
                  </div>
                  <p className="text-green-300 text-xs mt-2">
                    🎯 Estes títulos serão usados como base para remodelagem
                  </p>
                </div>
              </div>
            )}

            {useCustomPrompt && (
              <div className="p-4 bg-blue-900/30 border border-blue-700 rounded-lg">
                <p className="text-blue-300 text-sm">
                  🎨 <strong>Modo Personalizado:</strong> A IA vai remodelar os títulos extraídos seguindo suas instruções específicas.
                </p>
              </div>
            )}

            {results && (
              <div className="p-3 bg-purple-900/30 border border-purple-700 rounded-lg">
                <p className="text-purple-300 text-sm font-medium mb-1">📊 Estatísticas da Fila:</p>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div className="text-center">
                    <span className="block text-purple-200 font-mono text-lg">{results.videos.length}</span>
                    <span className="text-purple-400">Títulos</span>
                  </div>
                  <div className="text-center">
                    <span className="block text-purple-200 font-mono text-lg">
                      {Math.round(results.videos.reduce((acc, v) => acc + (v.title?.length || 0), 0) / results.videos.length)}
                    </span>
                    <span className="text-purple-400">Chars Médio</span>
                  </div>
                  <div className="text-center">
                    <span className="block text-purple-200 font-mono text-lg">
                      {titleGenerationConfig.count}
                    </span>
                    <span className="text-purple-400">A Gerar</span>
                  </div>
                </div>
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

  const renderPremiseGeneration = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Target size={24} className="text-purple-400" />
          <span>Geração de Premissas</span>
        </h3>

        {/* Seleção de Títulos */}
        <div className="mb-6">
          <h4 className="text-lg font-medium text-white mb-3">Títulos Disponíveis</h4>
          {results && results.videos && results.videos.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {results.videos.slice(0, 10).map((video, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    selectedTitles.includes(video.title)
                      ? 'border-purple-400 bg-purple-900/30'
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
                  onClick={() => toggleTitleSelection(video.title)}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`w-4 h-4 rounded border-2 mt-1 flex items-center justify-center ${
                      selectedTitles.includes(video.title)
                        ? 'border-purple-400 bg-purple-400'
                        : 'border-gray-500'
                    }`}>
                      {selectedTitles.includes(video.title) && (
                        <CheckCircle className="w-3 h-3 text-white" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-white line-clamp-2">
                        {video.title}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {video.number_of_views?.toLocaleString()} visualizações
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-400">Nenhum título encontrado</p>
              <p className="text-sm text-gray-500 mt-1">
                Extraia títulos primeiro na aba "Extração YouTube"
              </p>
            </div>
          )}
        </div>

        {/* Configurações de IA */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Provider de IA
            </label>
            <select
              value={premiseAiProvider}
              onChange={(e) => setPremiseAiProvider(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="auto">🤖 Automático (Melhor disponível)</option>
              <option value="openai">🧠 OpenAI GPT</option>
              <option value="gemini">💎 Google Gemini</option>
              <option value="openrouter">🌐 OpenRouter</option>
            </select>
          </div>

          {premiseAiProvider === 'openrouter' && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Modelo OpenRouter
              </label>
              <select
                value={openRouterModel}
                onChange={(e) => setOpenRouterModel(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                {openRouterModels.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name} {model.free ? '(Gratuito)' : '(Pago)'}
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-400 mt-1">
                Modelos gratuitos têm limitações de uso
              </p>
            </div>
          )}
        </div>

        {/* Prompt Personalizado */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Prompt Personalizado (Opcional)
          </label>
          <textarea
            value={premisePrompt}
            onChange={(e) => setPremisePrompt(e.target.value)}
            placeholder="Digite seu prompt personalizado aqui... (deixe vazio para usar o padrão)"
            className="w-full h-32 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
          />
          <p className="text-xs text-gray-400 mt-1">
            Prompt personalizado para gerar premissas específicas para seu nicho
          </p>
        </div>

        {/* Botão de Geração */}
        <button
          onClick={handleGeneratePremises}
          disabled={isGeneratingPremises || selectedTitles.length === 0}
          className={`w-full flex items-center justify-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all ${
            isGeneratingPremises || selectedTitles.length === 0
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-purple-600 text-white hover:bg-purple-700 hover:shadow-lg'
          }`}
        >
          {isGeneratingPremises ? (
            <>
              <RefreshCw className="w-5 h-5 animate-spin" />
              <span>Gerando Premissas...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              <span>Gerar Premissas ({selectedTitles.length} selecionados)</span>
            </>
          )}
        </button>
      </div>

      {/* Resultados */}
      {generatedPremises && generatedPremises.length > 0 && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h4 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <Sparkles className="text-purple-400" />
            <span>Premissas Geradas ({generatedPremises.length})</span>
          </h4>

          <div className="space-y-6">
            {generatedPremises.map((premise, index) => (
              <div key={index} className="border border-gray-600 rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <h5 className="font-medium text-white flex-1 pr-4">
                    {premise.title}
                  </h5>
                  <button
                    onClick={() => copyPremiseToClipboard(premise)}
                    className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <Copy size={14} />
                    <span>Copiar</span>
                  </button>
                </div>
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-300 whitespace-pre-wrap leading-relaxed">
                    {premise.premise}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )

  const renderScriptGeneration = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <FileText size={24} className="text-green-400" />
          <span>Geração de Roteiros IA</span>
        </h3>

        {/* Seleção de Título e Premissa */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Títulos Disponíveis */}
          <div>
            <h4 className="text-lg font-medium text-white mb-3">Selecionar Título</h4>
            {generatedTitles && generatedTitles.generated_titles ? (
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {generatedTitles.generated_titles.slice(0, 10).map((title, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      selectedTitle === title
                        ? 'border-green-400 bg-green-900/30'
                        : 'border-gray-600 hover:border-gray-500'
                    }`}
                    onClick={() => setSelectedTitle(title)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`w-4 h-4 rounded border-2 mt-1 flex items-center justify-center ${
                        selectedTitle === title
                          ? 'border-green-400 bg-green-400'
                          : 'border-gray-500'
                      }`}>
                        {selectedTitle === title && (
                          <CheckCircle className="w-3 h-3 text-white" />
                        )}
                      </div>
                      <p className="text-sm font-medium text-white line-clamp-2">
                        {title}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-400">Nenhum título encontrado</p>
                <p className="text-sm text-gray-500 mt-1">
                  Gere títulos primeiro na aba "Geração de Títulos"
                </p>
              </div>
            )}
          </div>

          {/* Premissas Disponíveis */}
          <div>
            <h4 className="text-lg font-medium text-white mb-3">Selecionar Premissa</h4>
            {generatedPremises && generatedPremises.length > 0 ? (
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {generatedPremises.slice(0, 10).map((premise, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      selectedPremise === premise.premise
                        ? 'border-green-400 bg-green-900/30'
                        : 'border-gray-600 hover:border-gray-500'
                    }`}
                    onClick={() => setSelectedPremise(premise.premise)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`w-4 h-4 rounded border-2 mt-1 flex items-center justify-center ${
                        selectedPremise === premise.premise
                          ? 'border-green-400 bg-green-400'
                          : 'border-gray-500'
                      }`}>
                        {selectedPremise === premise.premise && (
                          <CheckCircle className="w-3 h-3 text-white" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-white line-clamp-1 mb-1">
                          {premise.title}
                        </p>
                        <p className="text-xs text-gray-400 line-clamp-2">
                          {premise.premise.substring(0, 100)}...
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-400">Nenhuma premissa encontrada</p>
                <p className="text-sm text-gray-500 mt-1">
                  Gere premissas primeiro na aba "Premissas"
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Configurações de Geração */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Provider de IA
            </label>
            <select
              value={scriptAiProvider}
              onChange={(e) => setScriptAiProvider(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="auto">🤖 Automático (Melhor disponível)</option>
              <option value="openai">🧠 OpenAI GPT</option>
              <option value="gemini">💎 Google Gemini</option>
              <option value="openrouter">🌐 OpenRouter</option>
            </select>
          </div>

          {scriptAiProvider === 'openrouter' && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Modelo OpenRouter
              </label>
              <select
                value={scriptOpenRouterModel}
                onChange={(e) => setScriptOpenRouterModel(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                {openRouterModels.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name} {model.free ? '(Gratuito)' : '(Pago)'}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Número de Capítulos
            </label>
            <select
              value={numberOfChapters}
              onChange={(e) => setNumberOfChapters(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value={4}>4 Capítulos</option>
              <option value={6}>6 Capítulos</option>
              <option value={8}>8 Capítulos (Recomendado)</option>
              <option value={10}>10 Capítulos</option>
              <option value={12}>12 Capítulos</option>
            </select>
          </div>
        </div>

        {/* Pipeline de Processamento */}
        <div className="mb-6">
          <h4 className="text-lg font-medium text-white mb-3">Pipeline de Processamento</h4>
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center mb-2">
                  <span className="text-white font-bold">1</span>
                </div>
                <p className="text-sm text-white font-medium">Tradução & Contexto</p>
                <p className="text-xs text-gray-400">Adapta para português</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center mb-2">
                  <span className="text-white font-bold">2</span>
                </div>
                <p className="text-sm text-white font-medium">Estrutura Narrativa</p>
                <p className="text-xs text-gray-400">Cria prompts dos capítulos</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-green-600 flex items-center justify-center mb-2">
                  <span className="text-white font-bold">3</span>
                </div>
                <p className="text-sm text-white font-medium">Geração Final</p>
                <p className="text-xs text-gray-400">Gera {numberOfChapters} capítulos</p>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        {isGeneratingScripts && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-white">{scriptProgress.stage}</span>
              <span className="text-sm text-gray-400">
                {scriptProgress.current}/{scriptProgress.total}
              </span>
            </div>
            <div className="w-full bg-gray-600 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(scriptProgress.current / scriptProgress.total) * 100}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Botão de Geração */}
        <button
          onClick={handleGenerateScripts}
          disabled={isGeneratingScripts || !selectedTitle || !selectedPremise}
          className={`w-full flex items-center justify-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all ${
            isGeneratingScripts || !selectedTitle || !selectedPremise
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-green-600 text-white hover:bg-green-700 hover:shadow-lg'
          }`}
        >
          {isGeneratingScripts ? (
            <>
              <RefreshCw className="w-5 h-5 animate-spin" />
              <span>Gerando Roteiro...</span>
            </>
          ) : (
            <>
              <FileText className="w-5 h-5" />
              <span>Gerar Roteiro ({numberOfChapters} capítulos)</span>
            </>
          )}
        </button>
      </div>

      {/* Resultados */}
      {generatedScripts && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-white flex items-center space-x-2">
              <FileText className="text-green-400" />
              <span>Roteiro Gerado</span>
            </h4>
            <button
              onClick={() => copyScriptToClipboard(generatedScripts)}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Copy size={16} />
              <span>Copiar Roteiro Completo</span>
            </button>
          </div>

          {/* Informações do Roteiro */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-700 rounded-lg p-4">
              <h5 className="font-medium text-white mb-1">Título</h5>
              <p className="text-sm text-gray-300">{generatedScripts.title}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <h5 className="font-medium text-white mb-1">Capítulos</h5>
              <p className="text-sm text-gray-300">{generatedScripts.chapters?.length || 0}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <h5 className="font-medium text-white mb-1">Palavras Estimadas</h5>
              <p className="text-sm text-gray-300">
                {generatedScripts.chapters?.reduce((acc, ch) => acc + (ch.content?.split(' ').length || 0), 0) || 0}
              </p>
            </div>
          </div>

          {/* Capítulos */}
          <div className="space-y-4">
            {generatedScripts.chapters?.map((chapter, index) => (
              <div key={index} className="border border-gray-600 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h5 className="font-medium text-white">
                    Capítulo {index + 1}
                  </h5>
                  <button
                    onClick={() => copyChapterToClipboard(chapter, index)}
                    className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <Copy size={14} />
                    <span>Copiar</span>
                  </button>
                </div>
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-300 whitespace-pre-wrap leading-relaxed text-sm">
                    {chapter.content}
                  </p>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  {chapter.content?.split(' ').length || 0} palavras
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )

  const renderCompleteWorkflow = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Workflow size={24} className="text-indigo-400" />
          <span>Automação Completa</span>
        </h3>
        <p className="text-gray-400 mb-6">
          Execute toda a esteira de produção automaticamente: Extração → Títulos → Premissas → Roteiros
        </p>

        {/* Configurações da Automação */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Configurações do Canal */}
          <div>
            <h4 className="text-lg font-medium text-white mb-3">Configurações do Canal</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Canal do YouTube
                </label>
                <input
                  type="text"
                  value={workflowConfig.channel_url}
                  onChange={(e) => setWorkflowConfig(prev => ({ ...prev, channel_url: e.target.value }))}
                  placeholder="CanalClaYOliveiraOficial ou UCykzGI8qdfLywefslXnnyGw"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Máx. Títulos
                  </label>
                  <input
                    type="number"
                    value={workflowConfig.max_titles}
                    onChange={(e) => setWorkflowConfig(prev => ({ ...prev, max_titles: parseInt(e.target.value) }))}
                    min="1"
                    max="20"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Período (dias)
                  </label>
                  <input
                    type="number"
                    value={workflowConfig.days}
                    onChange={(e) => setWorkflowConfig(prev => ({ ...prev, days: parseInt(e.target.value) }))}
                    min="1"
                    max="365"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Mín. Visualizações
                </label>
                <input
                  type="number"
                  value={workflowConfig.min_views}
                  onChange={(e) => setWorkflowConfig(prev => ({ ...prev, min_views: parseInt(e.target.value) }))}
                  min="0"
                  placeholder="1000"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Configurações de Geração */}
          <div>
            <h4 className="text-lg font-medium text-white mb-3">Configurações de Geração</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  🎯 Quantidade de Títulos a Gerar
                </label>
                <input
                  type="number"
                  value={workflowConfig.titles_count}
                  onChange={(e) => setWorkflowConfig(prev => ({ ...prev, titles_count: parseInt(e.target.value) }))}
                  min="1"
                  max="10"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Quantos títulos novos a IA deve gerar baseado nos títulos extraídos
                </p>
              </div>

              {/* Prompt Personalizado */}
              <div>
                <div className="flex items-center space-x-3 mb-3">
                  <input
                    type="checkbox"
                    id="useCustomPromptWorkflow"
                    checked={workflowConfig.use_custom_prompt}
                    onChange={(e) => setWorkflowConfig(prev => ({ ...prev, use_custom_prompt: e.target.checked }))}
                    className="w-4 h-4 text-purple-600 bg-gray-600 border-gray-500 rounded focus:ring-purple-500"
                  />
                  <label htmlFor="useCustomPromptWorkflow" className="text-sm font-medium text-gray-300">
                    🎨 Usar Prompt Personalizado
                  </label>
                </div>

                {workflowConfig.use_custom_prompt && (
                  <div>
                    <textarea
                      value={workflowConfig.custom_prompt}
                      onChange={(e) => setWorkflowConfig(prev => ({ ...prev, custom_prompt: e.target.value }))}
                      placeholder="Ex: Transforme esses títulos em títulos mais chamativos para o nicho fitness, usando números específicos e palavras de urgência..."
                      rows={3}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                    />
                    <p className="text-xs text-gray-400 mt-1">
                      💡 Descreva como você quer que os títulos sejam remodelados
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Configurações de IA */}
          <div>
            <h4 className="text-lg font-medium text-white mb-3">Configurações de IA</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Provider de IA
                </label>
                <select
                  value={workflowConfig.ai_provider}
                  onChange={(e) => setWorkflowConfig(prev => ({ ...prev, ai_provider: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="auto">🤖 Automático (Melhor disponível)</option>
                  <option value="openai">🧠 OpenAI GPT</option>
                  <option value="gemini">💎 Google Gemini</option>
                  <option value="openrouter">🌐 OpenRouter</option>
                </select>
              </div>

              {workflowConfig.ai_provider === 'openrouter' && (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Modelo OpenRouter
                  </label>
                  <select
                    value={workflowConfig.openrouter_model}
                    onChange={(e) => setWorkflowConfig(prev => ({ ...prev, openrouter_model: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    {openRouterModels.map(model => (
                      <option key={model.id} value={model.id}>
                        {model.name} {model.free ? '(Gratuito)' : '(Pago)'}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Capítulos do Roteiro
                </label>
                <select
                  value={workflowConfig.number_of_chapters}
                  onChange={(e) => setWorkflowConfig(prev => ({ ...prev, number_of_chapters: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value={4}>4 Capítulos</option>
                  <option value={6}>6 Capítulos</option>
                  <option value={8}>8 Capítulos (Recomendado)</option>
                  <option value={10}>10 Capítulos</option>
                  <option value={12}>12 Capítulos</option>
                </select>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="auto_select_best"
                  checked={workflowConfig.auto_select_best}
                  onChange={(e) => setWorkflowConfig(prev => ({ ...prev, auto_select_best: e.target.checked }))}
                  className="w-4 h-4 text-indigo-600 bg-gray-600 border-gray-500 rounded focus:ring-indigo-500"
                />
                <label htmlFor="auto_select_best" className="text-sm text-gray-300">
                  Selecionar automaticamente os melhores resultados
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Pipeline Visual */}
        <div className="mb-6">
          <h4 className="text-lg font-medium text-white mb-3">Pipeline de Automação</h4>
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[
                { id: 'extraction', label: 'Extração YouTube', icon: Youtube, color: 'red' },
                { id: 'titles', label: 'Geração Títulos', icon: Wand2, color: 'blue' },
                { id: 'premises', label: 'Criação Premissas', icon: Target, color: 'purple' },
                { id: 'scripts', label: 'Roteiro Completo', icon: FileText, color: 'green' }
              ].map((step, index) => {
                const Icon = step.icon
                const isCompleted = workflowProgress.completed.includes(step.id)
                const isCurrent = workflowProgress.current === index + 1
                const isActive = isCompleted || isCurrent

                return (
                  <div key={step.id} className="flex flex-col items-center text-center">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all ${
                      isCompleted
                        ? `bg-${step.color}-600 text-white`
                        : isCurrent
                          ? `bg-${step.color}-600 text-white animate-pulse`
                          : 'bg-gray-600 text-gray-400'
                    }`}>
                      {isCompleted ? (
                        <CheckCircle className="w-6 h-6" />
                      ) : (
                        <Icon className="w-6 h-6" />
                      )}
                    </div>
                    <p className={`text-sm font-medium ${isActive ? 'text-white' : 'text-gray-400'}`}>
                      {step.label}
                    </p>
                    {isCurrent && (
                      <p className="text-xs text-gray-300 mt-1">
                        Em andamento...
                      </p>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        {isRunningWorkflow && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-white font-medium">{workflowProgress.stage}</span>
              <span className="text-sm text-gray-400">
                {workflowProgress.current}/{workflowProgress.total}
              </span>
            </div>
            {workflowProgress.details && (
              <p className="text-xs text-gray-400 mb-2">{workflowProgress.details}</p>
            )}
            <div className="w-full bg-gray-600 rounded-full h-3">
              <div
                className="bg-indigo-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${(workflowProgress.current / workflowProgress.total) * 100}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Aviso sobre configuração de APIs */}
        {(!apiKeys.openai && !apiKeys.gemini_1 && !apiKeys.openrouter) && (
          <div className="bg-yellow-900/20 border border-yellow-600 rounded-lg p-4 mb-6">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-yellow-400 font-medium mb-2">⚠️ Configuração Necessária</h3>
                <p className="text-yellow-200 text-sm mb-3">
                  Para usar a automação, você precisa configurar pelo menos uma chave de API de IA:
                </p>
                <ul className="text-yellow-200 text-sm space-y-1 mb-3">
                  <li>• <strong>Google Gemini</strong> - Gratuito (Recomendado)</li>
                  <li>• <strong>OpenAI GPT-4</strong> - Melhor qualidade</li>
                  <li>• <strong>OpenRouter</strong> - Acesso a múltiplos modelos</li>
                </ul>
                <button
                  onClick={() => setActiveTab('settings')}
                  className="bg-yellow-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-yellow-700 transition-colors"
                >
                  Ir para Configurações
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Botões de Execução */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={handleTestWorkflow}
            disabled={isRunningWorkflow}
            className={`flex items-center justify-center space-x-2 px-6 py-4 rounded-lg font-medium transition-all ${
              isRunningWorkflow
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700 hover:shadow-lg'
            }`}
          >
            {isRunningWorkflow ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Testando...</span>
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                <span>🧪 Teste Rápido (Dados Simulados)</span>
              </>
            )}
          </button>

          <button
            onClick={handleCompleteWorkflow}
            disabled={isRunningWorkflow || !workflowConfig.channel_url.trim()}
            className={`flex items-center justify-center space-x-2 px-6 py-4 rounded-lg font-medium transition-all ${
              isRunningWorkflow || !workflowConfig.channel_url.trim()
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-lg'
            }`}
          >
            {isRunningWorkflow ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Executando Automação...</span>
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                <span>🚀 Automação Completa (Canal Real)</span>
              </>
            )}
          </button>
        </div>

        {/* Botões de Controle durante execução */}
        {isRunningWorkflow && (
          <div className="flex justify-center gap-4">
            {!isPaused ? (
              <button
                onClick={pauseWorkflow}
                className="flex items-center space-x-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
              >
                <Pause className="w-4 h-4" />
                <span>⏸️ Pausar</span>
              </button>
            ) : (
              <button
                onClick={resumeWorkflow}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <Play className="w-4 h-4" />
                <span>▶️ Retomar</span>
              </button>
            )}
            <button
              onClick={cancelWorkflow}
              className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <Square className="w-4 h-4" />
              <span>⏹️ Cancelar</span>
            </button>
          </div>
        )}

        {/* Botão Ver Resultados */}
        {automationResults && (
          <div className="flex justify-center">
            <button
              onClick={() => setShowResults(true)}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg"
            >
              <Eye className="w-5 h-5" />
              <span>👁️ Ver Resultados Completos</span>
            </button>
          </div>
        )}

        {/* Botão para mostrar/ocultar logs */}
        {(isRunningWorkflow || workflowLogs.length > 0) && (
          <div className="flex justify-center">
            <button
              onClick={() => setShowLogs(!showLogs)}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              <Terminal className="w-4 h-4" />
              <span>{showLogs ? 'Ocultar Logs' : 'Mostrar Logs'}</span>
              <span className="bg-gray-600 px-2 py-1 rounded text-xs">{workflowLogs.length}</span>
            </button>
          </div>
        )}

        {/* Área de Logs em Tempo Real */}
        {showLogs && (
          <div className="bg-gray-900 rounded-lg p-4 max-h-96 overflow-y-auto">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-medium flex items-center space-x-2">
                <Terminal className="w-4 h-4" />
                <span>Logs em Tempo Real</span>
              </h3>
              <button
                onClick={() => setWorkflowLogs([])}
                className="text-gray-400 hover:text-white text-sm"
              >
                Limpar
              </button>
            </div>

            <div className="space-y-1 font-mono text-sm max-h-80 overflow-y-auto">
              {workflowLogs.length === 0 ? (
                <div className="text-gray-500 italic">Aguardando logs...</div>
              ) : (
                workflowLogs.map((log, index) => (
                  <div
                    key={index}
                    className={`flex items-start space-x-2 ${
                      log.level === 'error' ? 'text-red-400' :
                      log.level === 'success' ? 'text-green-400' :
                      log.level === 'warning' ? 'text-yellow-400' :
                      'text-gray-300'
                    }`}
                  >
                    <span className="text-gray-500 text-xs whitespace-nowrap">
                      {new Date(log.timestamp * 1000).toLocaleTimeString()}
                    </span>
                    <span className="flex-1 break-words">
                      {log.message}
                    </span>
                  </div>
                ))
              )}
            </div>

            {/* Auto-scroll para o final */}
            {workflowLogs.length > 0 && (
              <script>
                {setTimeout(() => {
                  const logsContainer = document.querySelector('.max-h-80.overflow-y-auto');
                  if (logsContainer) {
                    logsContainer.scrollTop = logsContainer.scrollHeight;
                  }
                }, 100)}
              </script>
            )}
          </div>
        )}
      </div>

      {/* Resultados */}
      {workflowResults && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h4 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <CheckCircle className="text-green-400" />
            <span>Automação Concluída</span>
          </h4>

          {/* Resumo dos Resultados */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-700 rounded-lg p-4">
              <h5 className="font-medium text-white mb-1">Títulos Extraídos</h5>
              <p className="text-2xl font-bold text-red-400">{workflowResults.extraction?.videos?.length || 0}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <h5 className="font-medium text-white mb-1">Títulos Gerados</h5>
              <p className="text-2xl font-bold text-blue-400">{workflowResults.titles?.generated_titles?.length || 0}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <h5 className="font-medium text-white mb-1">Premissas</h5>
              <p className="text-2xl font-bold text-purple-400">{workflowResults.premises?.length || 0}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <h5 className="font-medium text-white mb-1">Capítulos</h5>
              <p className="text-2xl font-bold text-green-400">{workflowResults.scripts?.chapters?.length || 0}</p>
            </div>
          </div>

          {/* Roteiro Final */}
          {workflowResults.scripts && (
            <div className="border border-gray-600 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h5 className="font-medium text-white">
                  Roteiro Final: {workflowResults.scripts.title}
                </h5>
                <button
                  onClick={() => copyScriptToClipboard(workflowResults.scripts)}
                  className="flex items-center space-x-2 px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Copy size={14} />
                  <span>Copiar Roteiro</span>
                </button>
              </div>
              <div className="text-sm text-gray-400 mb-2">
                {workflowResults.scripts.total_words} palavras • {workflowResults.scripts.chapters.length} capítulos
              </div>
              <div className="max-h-64 overflow-y-auto">
                <p className="text-gray-300 text-sm">
                  {workflowResults.scripts.chapters?.[0]?.content?.substring(0, 300)}...
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )

  const renderVideoEditor = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Video size={24} className="text-pink-400" />
          <span>Editor de Vídeo IA</span>
        </h3>

        {/* Status da Pipeline */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Títulos</h4>
              <CheckCircle className="w-5 h-5 text-green-400" />
            </div>
            <p className="text-sm text-gray-400">Prontos para uso</p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Premissas</h4>
              <CheckCircle className="w-5 h-5 text-green-400" />
            </div>
            <p className="text-sm text-gray-400">Geradas com IA</p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Roteiros</h4>
              <Clock className="w-5 h-5 text-yellow-400" />
            </div>
            <p className="text-sm text-gray-400">Em desenvolvimento</p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Áudio</h4>
              <Clock className="w-5 h-5 text-yellow-400" />
            </div>
            <p className="text-sm text-gray-400">Em desenvolvimento</p>
          </div>
        </div>

        {/* Configurações de Vídeo */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <h4 className="text-lg font-medium text-white mb-3">Configurações de Vídeo</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Resolução
                </label>
                <select className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                  <option value="1920x1080">1920x1080 (Full HD)</option>
                  <option value="1280x720">1280x720 (HD)</option>
                  <option value="3840x2160">3840x2160 (4K)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Formato
                </label>
                <select className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                  <option value="16:9">16:9 (YouTube Padrão)</option>
                  <option value="9:16">9:16 (Shorts/TikTok)</option>
                  <option value="1:1">1:1 (Instagram)</option>
                  <option value="4:3">4:3 (Clássico)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Duração Estimada
                </label>
                <select className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                  <option value="short">Curto (30s - 2min)</option>
                  <option value="medium">Médio (2min - 10min)</option>
                  <option value="long">Longo (10min+)</option>
                </select>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-lg font-medium text-white mb-3">Estilo Visual</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Template
                </label>
                <select className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                  <option value="modern">Moderno e Limpo</option>
                  <option value="dynamic">Dinâmico com Animações</option>
                  <option value="minimal">Minimalista</option>
                  <option value="corporate">Corporativo</option>
                  <option value="creative">Criativo e Colorido</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Paleta de Cores
                </label>
                <div className="grid grid-cols-4 gap-2">
                  <div className="w-full h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded cursor-pointer border-2 border-transparent hover:border-white"></div>
                  <div className="w-full h-8 bg-gradient-to-r from-red-500 to-orange-500 rounded cursor-pointer border-2 border-transparent hover:border-white"></div>
                  <div className="w-full h-8 bg-gradient-to-r from-green-500 to-teal-500 rounded cursor-pointer border-2 border-transparent hover:border-white"></div>
                  <div className="w-full h-8 bg-gradient-to-r from-gray-700 to-gray-900 rounded cursor-pointer border-2 border-white"></div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Fonte Principal
                </label>
                <select className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                  <option value="roboto">Roboto (Moderno)</option>
                  <option value="montserrat">Montserrat (Elegante)</option>
                  <option value="opensans">Open Sans (Legível)</option>
                  <option value="poppins">Poppins (Amigável)</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Elementos do Vídeo */}
        <div className="mb-6">
          <h4 className="text-lg font-medium text-white mb-3">Elementos do Vídeo</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 text-pink-600 bg-gray-600 border-gray-500 rounded focus:ring-pink-500" defaultChecked />
              <span className="text-gray-300">Intro Animada</span>
            </label>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 text-pink-600 bg-gray-600 border-gray-500 rounded focus:ring-pink-500" defaultChecked />
              <span className="text-gray-300">Legendas</span>
            </label>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 text-pink-600 bg-gray-600 border-gray-500 rounded focus:ring-pink-500" />
              <span className="text-gray-300">Música de Fundo</span>
            </label>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 text-pink-600 bg-gray-600 border-gray-500 rounded focus:ring-pink-500" />
              <span className="text-gray-300">Efeitos Sonoros</span>
            </label>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 text-pink-600 bg-gray-600 border-gray-500 rounded focus:ring-pink-500" defaultChecked />
              <span className="text-gray-300">Transições</span>
            </label>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 text-pink-600 bg-gray-600 border-gray-500 rounded focus:ring-pink-500" />
              <span className="text-gray-300">Call-to-Action</span>
            </label>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 text-pink-600 bg-gray-600 border-gray-500 rounded focus:ring-pink-500" />
              <span className="text-gray-300">Logo/Marca</span>
            </label>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 text-pink-600 bg-gray-600 border-gray-500 rounded focus:ring-pink-500" defaultChecked />
              <span className="text-gray-300">Outro Final</span>
            </label>
          </div>
        </div>

        {/* Botão de Geração */}
        <div className="text-center">
          <button
            disabled={true}
            className="px-8 py-3 bg-gray-600 text-gray-400 rounded-lg font-medium cursor-not-allowed flex items-center space-x-2 mx-auto"
          >
            <Video className="w-5 h-5" />
            <span>Gerar Vídeo (Em Desenvolvimento)</span>
          </button>
          <p className="text-sm text-gray-500 mt-2">
            Esta funcionalidade será implementada após a conclusão dos roteiros e áudio
          </p>
        </div>
      </div>

      {/* Preview Area */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h4 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
          <Eye className="text-pink-400" />
          <span>Preview do Vídeo</span>
        </h4>

        <div className="bg-gray-900 rounded-lg p-8 text-center">
          <div className="w-full max-w-md mx-auto aspect-video bg-gray-700 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <Video size={48} className="text-gray-500 mx-auto mb-3" />
              <p className="text-gray-400">Preview será exibido aqui</p>
              <p className="text-sm text-gray-500 mt-1">Após gerar o vídeo</p>
            </div>
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
          {activeTab === 'premise' && renderPremiseGeneration()}
          {activeTab === 'scripts' && renderScriptGeneration()}
          {activeTab === 'video-edit' && renderVideoEditor()}
          {activeTab === 'workflow' && renderCompleteWorkflow()}
          {activeTab !== 'youtube' && activeTab !== 'titles' && activeTab !== 'premise' && activeTab !== 'scripts' && activeTab !== 'video-edit' && activeTab !== 'workflow' && (
            <div className="text-center py-12">
              <Target size={48} className="text-purple-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Em desenvolvimento</h3>
              <p className="text-gray-400">Esta funcionalidade será implementada em breve.</p>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Resultados */}
      <AutomationResults
        results={automationResults}
        isVisible={showResults}
        onClose={() => setShowResults(false)}
      />
    </div>
  )
}

export default Automations
