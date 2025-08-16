/**
 * 🤖 Automations Page
 * 
 * Página de automações de conteúdo
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import CustomPromptManager from '../components/CustomPromptManager'
import SavedChannelsManager from '../components/SavedChannelsManager'
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
  X,
  Save
} from 'lucide-react'
import AutomationResults from '../components/AutomationResults'

const AutomationsDev = () => {
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
  const [showPromptManager, setShowPromptManager] = useState(false)
  const [showChannelsManager, setShowChannelsManager] = useState(false)

  // Estado para o formulário de extração do YouTube
  const [formData, setFormData] = useState({
    url: '',
    channel_id: '',
    input_type: 'url',
    max_titles: 10,
    min_views: 1000,
    max_views: '',
    days: 30
  })

  const [apiKeys, setApiKeys] = useState({})
  const [apiStatus, setApiStatus] = useState({
    rapidapi: 'unknown',
    gemini_tts: 'unknown',
    kokoro_tts: 'unknown'
  })

  // Estados para teste TTS Gemini
  const [ttsTestText, setTtsTestText] = useState('Olá, este é um teste de áudio com Gemini TTS. A qualidade do áudio é excelente!')
  const [ttsTestResult, setTtsTestResult] = useState(null)

  // Estados para player de áudio
  const [generatedAudios, setGeneratedAudios] = useState([])

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

  // Estados para geração de imagens
  const [isGeneratingImages, setIsGeneratingImages] = useState(false)
  const [generatedImages, setGeneratedImages] = useState([])
  const [imageGenerationScript, setImageGenerationScript] = useState('')
  const [imageStyle, setImageStyle] = useState('cinematic, high detail, 4k')
  const [togetherApiKey, setTogetherApiKey] = useState('')
  const [imageGenerationError, setImageGenerationError] = useState('')
  
  // Novos estados para o sistema expandido
  const [useAiAgent, setUseAiAgent] = useState(true)
  const [imageCount, setImageCount] = useState(5)
  const [imageProvider, setImageProvider] = useState('pollinations')
  const [imageFormat, setImageFormat] = useState('1024x1024')
  const [imageQuality, setImageQuality] = useState('standard')
  const [pollinationsModel, setPollinationsModel] = useState('flux')
  const [aiAgentPrompt, setAiAgentPrompt] = useState('Você é um especialista em criação de prompts visuais para IA. Analise o roteiro fornecido e crie prompts detalhados e específicos para gerar imagens que representem as principais cenas e momentos do conteúdo.\n\nREGRAS IMPORTANTES:\n- Cada prompt deve ter pelo menos 25 palavras\n- Inclua detalhes sobre cenário, personagens, emoções, iluminação e estilo visual\n- Não inclua títulos, cabeçalhos ou numeração\n- Cada prompt deve ser uma descrição visual completa e independente\n- Separe cada prompt por uma linha em branco\n\nFormato: Um prompt visual detalhado por parágrafo, separados por quebras de linha duplas.')
  const [aiAgentProvider, setAiAgentProvider] = useState('openai')
  const [imageQueue, setImageQueue] = useState([])
  const [queueStatus, setQueueStatus] = useState('idle') // idle, processing, completed, error

  // Estados para o Agente IA Personalizado
  const [agentPrompt, setAgentPrompt] = useState('')
  const [agentContextFiles, setAgentContextFiles] = useState([])
  const [agentContextText, setAgentContextText] = useState('')
  const [selectedAgentTitle, setSelectedAgentTitle] = useState('')
  const [selectedAgentPremise, setSelectedAgentPremise] = useState('')
  const [agentAiProvider, setAgentAiProvider] = useState('auto')
  const [agentOpenRouterModel, setAgentOpenRouterModel] = useState('auto')
  const [isGeneratingAgentScript, setIsGeneratingAgentScript] = useState(false)
  const [agentGeneratedScript, setAgentGeneratedScript] = useState(null)
  const [agentInstructions, setAgentInstructions] = useState('')
  const [agentScriptSize, setAgentScriptSize] = useState('medio') // curto, medio, longo
  const [agentNumberOfChapters, setAgentNumberOfChapters] = useState(8) // Número de capítulos para o agente IA
  const [agentProgress, setAgentProgress] = useState({ current: 0, total: 0, stage: '' }) // Progresso detalhado do agente
  const [usePartsGeneration, setUsePartsGeneration] = useState(false) // Geração em partes para roteiros longos

  // Estados para criação de vídeo
  const [isCreatingVideo, setIsCreatingVideo] = useState(false)
  const [videoConfig, setVideoConfig] = useState({
    resolution: '1920x1080',
    fps: 30,
    transition_duration: 0.5
  })
  const [createdVideo, setCreatedVideo] = useState(null)
  const [videoCreationProgress, setVideoCreationProgress] = useState({
    stage: '',
    progress: 0
  })

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
    url: '',
    channel_id: '',
    input_type: 'url',
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

  // Carregar dados quando a aba TTS for selecionada
  useEffect(() => {
    if (activeTab === 'tts') {
      console.log('🎵 DEBUG: Carregando dados para aba TTS...')

      // 1. Tentar carregar dados específicos do TTS (vindos do botão "Gerar Áudio")
      const ttsScriptData = localStorage.getItem('tts_script_data')
      if (ttsScriptData && !generatedScripts) {
        const parsed = JSON.parse(ttsScriptData)
        console.log('🎵 Dados TTS específicos carregados:', parsed)
        setGeneratedScripts(parsed)
      }

      // 2. Carregar títulos gerados se não existirem
      if (!generatedTitles) {
        const savedTitles = localStorage.getItem('generated_titles')
        if (savedTitles) {
          const parsed = JSON.parse(savedTitles)
          console.log('🎯 Títulos carregados para TTS:', parsed)
          setGeneratedTitles(parsed)
        }
      }

      // 3. Carregar premissas geradas se não existirem
      if (!generatedPremises) {
        const savedPremises = localStorage.getItem('generated_premises')
        if (savedPremises) {
          const parsed = JSON.parse(savedPremises)
          console.log('💡 Premissas carregadas para TTS:', parsed)
          setGeneratedPremises(parsed)
        }
      }

      // 4. Carregar roteiros gerados se não existirem
      if (!generatedScripts) {
        const savedScripts = localStorage.getItem('generated_scripts')
        if (savedScripts) {
          const parsed = JSON.parse(savedScripts)
          console.log('📝 Roteiros carregados para TTS:', parsed)
          setGeneratedScripts(parsed)
        }
      }

      // Debug dos estados
      setTimeout(() => {
        console.log('🔍 DEBUG TTS: Estados atuais:', {
          generatedTitles: !!generatedTitles,
          generatedPremises: !!generatedPremises,
          generatedScripts: !!generatedScripts,
          scriptsData: generatedScripts
        })
      }, 100)
    }
  }, [activeTab])

  // Carregar dados quando a aba de imagens for selecionada
  useEffect(() => {
    if (activeTab === 'images') {
      console.log('🖼️ DEBUG: Carregando dados para aba de imagens...')

      // Carregar chave da API Together
      const loadTogetherApiKey = async () => {
        try {
          const response = await fetch('/api/settings/api-keys/together')
          if (response.ok) {
            const data = await response.json()
            if (data.success && data.api_key) {
              setTogetherApiKey(data.api_key)
            }
          }
        } catch (error) {
          console.error('Erro ao carregar chave Together API:', error)
        }
      }

      loadTogetherApiKey()

      // Carregar roteiros gerados se não existirem
      if (!generatedScripts) {
        const savedScripts = localStorage.getItem('generated_scripts')
        if (savedScripts) {
          const parsed = JSON.parse(savedScripts)
          console.log('📝 Roteiros carregados para imagens:', parsed)
          setGeneratedScripts(parsed)
        }
      }

      // Definir script para geração de imagens baseado nos roteiros disponíveis
      if (generatedScripts && generatedScripts.chapters) {
        const scriptText = generatedScripts.chapters.map(chapter => chapter.content).join('\n\n')
        setImageGenerationScript(scriptText)
      }
    }
  }, [activeTab, generatedScripts])

  // Escutar evento customizado para mudança de aba
  useEffect(() => {
    const handleChangeTab = (event) => {
      if (event.detail === 'tts') {
        setActiveTab('tts')
      }
    }

    window.addEventListener('changeTab', handleChangeTab)
    return () => window.removeEventListener('changeTab', handleChangeTab)
  }, [])

  // Carregar prompt padrão para o agente IA personalizado
  useEffect(() => {
    const defaultAgentPrompt = `# 🎬 AGENTE IA ESPECIALISTA EM ROTEIROS PROFISSIONAIS

Você é um roteirista profissional especializado em criar roteiros envolventes e virais para YouTube. Sua missão é transformar o título e premissa fornecidos em um roteiro completo, estruturado e cativante.

## 🎯 OBJETIVOS:
1. Criar um roteiro completo baseado no título e premissa
2. Desenvolver uma narrativa envolvente do início ao fim
3. Incluir diálogos naturais e descrições vívidas
4. Manter o espectador interessado a cada momento
5. Usar técnicas de storytelling profissional

## 📝 ESTRUTURA DO ROTEIRO:
- **ABERTURA:** Gancho inicial impactante
- **DESENVOLVIMENTO:** Construção da tensão e personagens
- **CLÍMAX:** Momento de maior impacto emocional
- **RESOLUÇÃO:** Conclusão satisfatória e memorável

## 🎭 ELEMENTOS OBRIGATÓRIOS:
- Personagens bem desenvolvidos e realistas
- Diálogos naturais e envolventes
- Descrições cinematográficas das cenas
- Ganchos emocionais ao longo do roteiro
- Ritmo dinâmico que prende a atenção
- Reviravoltas e momentos de surpresa

## 📺 FORMATO PARA YOUTUBE:
- Linguagem acessível ao público brasileiro
- Momentos de suspense estratégicos
- Elementos virais e compartilháveis
- Estrutura que mantém o engajamento

## 🎪 INSTRUÇÕES ESPECIAIS:
- Use o contexto fornecido nos arquivos (se houver)
- Siga as instruções específicas do usuário
- Mantenha coerência com o título e premissa
- Crie um roteiro pronto para produção

---

**IMPORTANTE:** Gere um roteiro COMPLETO e DETALHADO, não apenas um resumo ou esboço. O resultado deve estar pronto para ser usado na produção do vídeo.`

    // Carregar prompt padrão se estiver vazio
    if (!agentPrompt) {
      setAgentPrompt(defaultAgentPrompt)
    }
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
          api_key: keys.rapidapi,
          url: '@eusouodh',
          max_titles: 5,
          min_views: 1000,
          max_views: 0,
          days: 30
        })
      })

      const data = await response.json()

      if (data.success) {
        setApiStatus(prev => ({ ...prev, rapidapi: 'connected' }))
      } else {
        setApiStatus(prev => ({ ...prev, rapidapi: 'error' }))
        // Se for erro de quota, mostrar mensagem específica
        if (data.error && (data.error.includes('quota') || data.error.includes('limit') || data.error.includes('429') || data.error.includes('Too Many Requests'))) {
          console.warn('🚫 RapidAPI: Limite de quota excedido -', data.error)
        }
      }
    } catch (error) {
      setApiStatus(prev => ({ ...prev, rapidapi: 'error' }))
      console.error('❌ Erro ao verificar status RapidAPI:', error)
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

  // Função para testar Kokoro TTS
  const handleTestKokoroTTS = async () => {
    const kokoroUrl = ttsSettings.kokoro.kokoro_url

    if (!kokoroUrl.trim()) {
      alert('Configure a URL do Kokoro TTS primeiro')
      return
    }

    setApiStatus(prev => ({ ...prev, kokoro_tts: 'testing' }))

    try {
      console.log('🎵 Testando Kokoro TTS...')

      const response = await fetch('/api/automations/test-kokoro', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          kokoro_url: kokoroUrl
        })
      })

      const result = await response.json()
      console.log('🔍 Resultado do teste Kokoro:', result)

      if (result.success) {
        setApiStatus(prev => ({ ...prev, kokoro_tts: 'connected' }))
        alert(`✅ Kokoro conectado com sucesso!\n\nURL: ${result.url}\nVozes disponíveis: ${result.voices_count}`)
      } else {
        setApiStatus(prev => ({ ...prev, kokoro_tts: 'error' }))
        alert(`❌ Erro ao conectar com Kokoro:\n\n${result.error}`)
      }
    } catch (error) {
      console.error('❌ Erro no teste Kokoro:', error)
      setApiStatus(prev => ({ ...prev, kokoro_tts: 'error' }))
      alert(`❌ Erro de conexão com Kokoro:\n\n${error.message}`)
    }
  }

  // Função para testar TTS Gemini
  const handleTestGeminiTTS = async () => {
    const geminiKey = apiKeys.gemini_1 || apiKeys.gemini || apiKeys['gemini_1'] || apiKeys['gemini'] || 'AIzaSyBqUjzLHNPycDIzvwnI5JisOwmNubkfRRc'

    if (!geminiKey || geminiKey.length < 10) {
      alert('Configure a chave Gemini nas Configurações primeiro')
      return
    }

    if (!ttsTestText.trim()) {
      alert('Digite um texto para testar')
      return
    }

    setApiStatus(prev => ({ ...prev, gemini_tts: 'testing' }))
    setTtsTestResult(null)

    try {
      console.log('🎵 Testando TTS Gemini...')

      const response = await fetch('/api/automations/generate-tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: ttsTestText,
          api_key: geminiKey,
          voice_name: ttsSettings.gemini.voice_name,
          model: ttsSettings.gemini.model
        })
      })

      const result = await response.json()
      console.log('🔍 Resultado do teste TTS:', result)

      if (result.success) {
        setApiStatus(prev => ({ ...prev, gemini_tts: 'connected' }))
        setTtsTestResult({
          success: true,
          data: result.data,
          message: `✅ Áudio gerado com sucesso! Arquivo: ${result.data.filename} (${result.data.size} bytes)`
        })
      } else {
        setApiStatus(prev => ({ ...prev, gemini_tts: 'error' }))
        setTtsTestResult({
          success: false,
          error: result.error,
          message: `❌ Erro: ${result.error}`
        })
      }
    } catch (error) {
      console.error('❌ Erro no teste TTS:', error)
      setApiStatus(prev => ({ ...prev, gemini_tts: 'error' }))
      setTtsTestResult({
        success: false,
        error: error.message,
        message: `❌ Erro de conexão: ${error.message}`
      })
    }
  }

  const handleExtractContent = async () => {
    if (!formData.url.trim()) {
      alert('Por favor, insira o nome ou ID do canal do YouTube')
      return
    }

    setIsProcessing(true)
    setResults(null) // Limpar resultados anteriores

    try {
      // Timeout maior para a requisição (5 minutos)
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 300000) // 5 minutos

      // Preparar payload baseado no tipo de entrada
      const payload = {
        config: {
          max_titles: parseInt(formData.max_titles),
          min_views: parseInt(formData.min_views),
          max_views: formData.max_views ? parseInt(formData.max_views) : 0,
          days: parseInt(formData.days)
        }
      }

      // Adicionar URL ou channel_id baseado no tipo
      if (formData.input_type === 'channel_id' && formData.channel_id) {
        payload.channel_id = formData.channel_id
      } else {
        payload.url = formData.url
      }

      const response = await fetch('http://localhost:5000/api/automations/extract-youtube', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
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
        // Verificar se é erro de quota/limite da API
        if (data.error && (data.error.includes('quota') || data.error.includes('limit') || data.error.includes('429') || data.error.includes('Too Many Requests'))) {
          alert(`🚫 Limite de Quota Excedido!\n\n❌ ${data.error}\n\n💡 Soluções:\n• Configure múltiplas chaves RapidAPI nas Configurações\n• Aguarde o reset diário da quota\n• Verifique o status das chaves na aba Configurações`)
        } else {
          alert(`❌ Erro: ${data.error}`)
        }
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        alert('⏱️ Operação cancelada por timeout. A API está demorando muito para responder.')
      } else {
        // Verificar se é erro relacionado a quota/limite
        if (error.message && (error.message.includes('400') || error.message.includes('BAD REQUEST'))) {
          alert(`🚫 Erro de Quota da API!\n\n❌ A API RapidAPI retornou erro 400 (BAD REQUEST)\n\n💡 Isso geralmente indica:\n• Limite de quota mensal excedido\n• Chave de API inválida ou expirada\n• Muitas requisições em pouco tempo\n\n🔧 Soluções:\n• Configure múltiplas chaves RapidAPI nas Configurações\n• Verifique o status das suas chaves\n• Aguarde o reset da quota (geralmente mensal)`)
        } else {
          showNotification(`Erro de conexão: ${error.message}`, 'error')
        }
      }
    } finally {
      setIsProcessing(false)
    }
  }

  // Função para selecionar um prompt salvo
  const handleSelectPrompt = (prompt) => {
    setCustomPrompt(prompt.prompt_text)
    setUseCustomPrompt(true)
    setShowPromptManager(false)

    // Também atualizar o prompt do workflow se estiver na aba de fluxos completos
    if (activeTab === 'complete') {
      setWorkflowConfig(prev => ({
        ...prev,
        custom_prompt: prompt.prompt_text,
        use_custom_prompt: true
      }))
    }
  }

  // Função para selecionar um canal salvo
  const handleSelectChannel = (channel) => {
    setFormData(prev => ({
      ...prev,
      url: channel.url,
      channel_id: channel.channel_id || '',
      input_type: channel.input_type || 'url'
    }))
    setShowChannelsManager(false)

    // Também atualizar o canal do workflow se estiver na aba de fluxos completos
    if (activeTab === 'complete') {
      setWorkflowConfig(prev => ({
        ...prev,
        channel_url: channel.url,
        channel_id: channel.channel_id || '',
        input_type: channel.input_type || 'url'
      }))
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
      const defaultPrompt = `# Gerador de Premissas Profissionais e Diversas para Vídeos

Você é um especialista em criação de conteúdo e storytelling para YouTube. Sua tarefa é criar premissas envolventes e profissionais baseadas nos títulos fornecidos.

## Instruções IMPORTANTES:
1. Analise cada título fornecido
2. Crie uma premissa única e cativante para cada um
3. A premissa deve ter entre 100-200 palavras
4. Inclua elementos de storytelling (problema, conflito, resolução)
5. Mantenha o tom adequado ao nicho do título
6. Adicione ganchos emocionais e curiosidade

## DIVERSIDADE OBRIGATÓRIA:
- NUNCA use "Em uma pequena vila" ou "Em uma pequena cidade"
- VARIE os locais: grandes cidades, metrópoles, bairros, empresas, escolas, hospitais, etc.
- VARIE os inícios: "Durante uma noite", "No meio de", "Quando", "Após anos", "Em pleno", etc.
- EVITE repetir padrões de início entre diferentes premissas
- Use cenários modernos e contemporâneos
- Seja criativo com os ambientes e situações

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

  const copyScriptConcatenatedToClipboard = (script) => {
    // Concatenar apenas o conteúdo dos capítulos, sem títulos nem separadores
    const concatenatedScript = script.chapters.map(chapter =>
      chapter.content.trim()
    ).join(' ')

    navigator.clipboard.writeText(concatenatedScript)
    alert('Roteiro concatenado (sequência completa) copiado para a área de transferência!')
  }

  const downloadScriptAsTxt = (script, format = 'chapters') => {
    let content = ''
    let filename = ''

    if (format === 'chapters') {
      // Formato com capítulos
      content = `${script.title}\n\n${script.chapters.map((chapter, i) =>
        `CAPÍTULO ${i + 1}:\n${chapter.content}\n\n`
      ).join('')}`
      filename = `roteiro_${script.title.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 50)}_com_capitulos.txt`
    } else {
      // Formato concatenado (sequência completa)
      content = script.chapters.map(chapter =>
        chapter.content.trim()
      ).join(' ')
      filename = `roteiro_${script.title.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 50)}_sequencia_completa.txt`
    }

    // Criar blob e fazer download
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    alert(`📄 Roteiro baixado como: ${filename}`)
  }

  const copyChapterToClipboard = (chapter, index) => {
    navigator.clipboard.writeText(`CAPÍTULO ${index + 1}:\n${chapter.content}`)
    alert(`Capítulo ${index + 1} copiado para a área de transferência!`)
  }

  // ========== FUNÇÕES DE CRIAÇÃO DE VÍDEO ==========

  // Helper function to validate file existence
  const validateFileExists = async (filePath) => {
    try {
      const response = await fetch('/api/system/files/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file_path: filePath })
      })
      const data = await response.json()
      return data.exists || false
    } catch (error) {
      console.error('Erro ao validar arquivo:', error)
      return false
    }
  }

  // Notification helper
  const showNotification = (message, type = 'info') => {
    if (type === 'error') {
      alert('❌ ' + message)
    } else if (type === 'success') {
      alert('✅ ' + message)
    } else if (type === 'warning') {
      alert('⚠️ ' + message)
    } else {
      alert('ℹ️ ' + message)
    }
  }

  // Função para verificar o status dos áudios gerados
  const checkAudioStatus = () => {
    const audioFiles = JSON.parse(localStorage.getItem('generated_audio_files') || '[]')
    
    if (audioFiles.length === 0) {
      return { status: 'none', message: 'Nenhum áudio gerado' }
    } else if (audioFiles.length === 1) {
      return { status: 'single', message: 'Um áudio disponível' }
    } else {
      const hasFinal = audioFiles.some(audio => audio.is_final)
      if (hasFinal) {
        return { status: 'unified', message: 'Áudio unificado pronto' }
      } else {
        return { status: 'multiple', message: `${audioFiles.length} segmentos - Recomendado juntar` }
      }
    }
  }

  const handleCreateVideo = async () => {
    if (!generatedScripts || !generatedScripts.chapters || generatedScripts.chapters.length === 0) {
      alert('Nenhum roteiro encontrado. Gere um roteiro primeiro.')
      return
    }

    const audioFiles = localStorage.getItem('generated_audio_files')
    const imageFiles = localStorage.getItem('generated_images')
    
    if (!audioFiles) {
      showNotification('Nenhum arquivo de áudio encontrado. Gere o áudio primeiro.', 'error')
      return
    }
    
    if (!imageFiles) {
      showNotification('Nenhuma imagem encontrada. Gere as imagens primeiro.', 'error')
      return
    }

    setIsCreatingVideo(true)
    setVideoCreationProgress({ stage: 'Iniciando criação do vídeo...', progress: 0 })

    try {
      const parsedAudioFiles = JSON.parse(audioFiles)
      const parsedImageFiles = JSON.parse(imageFiles)

      // ✅ CORREÇÃO: Verificar se há áudio final unificado
      let audioFile = null
      if (parsedAudioFiles && parsedAudioFiles.length > 0) {
        // Procurar por áudio final unificado primeiro
        const finalAudio = parsedAudioFiles.find(audio => audio.is_final === true)
        
        if (finalAudio) {
          // Usar áudio final unificado
          const filename = finalAudio.filename
          if (filename) {
            audioFile = `C:\\Users\\Enderson\\Documents\\APP\\auto-video-producer\\backend\\temp\\${filename}`
            console.log('✅ Usando áudio final unificado:', finalAudio)
            showNotification(`Usando áudio final unificado (${finalAudio.segments_count} segmentos)`, 'success')
          } else {
            audioFile = finalAudio.audio_url
          }
        } else if (parsedAudioFiles.length > 1) {
          // Se há múltiplos áudios mas nenhum unificado, alertar usuário
          alert(`⚠️ Encontrados ${parsedAudioFiles.length} segmentos de áudio.\n\nPara criar o vídeo com todos os áudios, clique em "Juntar Áudios" na seção TTS primeiro.\n\nOu o sistema usará apenas o primeiro segmento.`)
          
          // Usar primeiro áudio como fallback
          const firstAudio = parsedAudioFiles[0]
          audioFile = firstAudio.filename || firstAudio.audio_url
          if (audioFile && !audioFile.includes('\\')) {
            audioFile = `C:\\Users\\Enderson\\Documents\\APP\\auto-video-producer\\backend\\temp\\${audioFile}`
          }
          console.log('🎵 Usando primeiro segmento de áudio:', firstAudio)
        } else {
          // Apenas um áudio, usar diretamente
          const firstAudio = parsedAudioFiles[0]
          audioFile = firstAudio.filename || firstAudio.audio_url
          if (audioFile && !audioFile.includes('\\')) {
            audioFile = `C:\\Users\\Enderson\\Documents\\APP\\auto-video-producer\\backend\\temp\\${audioFile}`
          }
          console.log('🎵 Usando áudio único:', firstAudio)
        }
      }

      // Verificar se há imagens disponíveis
      let imagePaths = []
      if (parsedImageFiles && parsedImageFiles.length > 0) {
        imagePaths = parsedImageFiles.map(img => {
          // Se a imagem tem URL (formato /api/images/view/filename), extrair o filename e construir caminho completo
          if (img.url && img.url.includes('/api/images/view/')) {
            const filename = img.url.split('/api/images/view/')[1]
            return `C:\\Users\\Enderson\\Documents\\APP\\auto-video-producer\\backend\\output\\images\\${filename}`
          }
          // Fallback para outros formatos
          return img.file_path || img.url || img.image_url
        })
      }

      if (!audioFile) {
        showNotification('❌ Nenhum arquivo de áudio válido encontrado', 'error')
        return
      }

      if (imagePaths.length === 0) {
        showNotification('❌ Nenhuma imagem válida encontrada', 'error')
        return
      }

      // Validar existência dos arquivos antes de enviar para o backend
      setVideoCreationProgress({ stage: 'Validando arquivos...', progress: 10 })
      
      const audioExists = await validateFileExists(audioFile)
      if (!audioExists) {
        showNotification(`❌ Arquivo de áudio não encontrado: ${audioFile}`, 'error')
        setIsCreatingVideo(false)
        return
      }

      // Validar algumas imagens (não todas para não sobrecarregar)
      const imagesToValidate = imagePaths.slice(0, 3) // Validar apenas as 3 primeiras
      for (const imagePath of imagesToValidate) {
        const imageExists = await validateFileExists(imagePath)
        if (!imageExists) {
          showNotification(`❌ Arquivo de imagem não encontrado: ${imagePath}`, 'error')
          setIsCreatingVideo(false)
          return
        }
      }

      // Preparar dados para a API (formato correto esperado pelo backend)
      const videoData = {
        title: generatedScripts.title || 'Vídeo Gerado',
        audio_file: audioFile,  // Backend espera 'audio_file' (string)
        images: imagePaths,     // Backend espera 'images' (array de strings)
        config: {
          resolution: videoConfig.resolution,
          fps: videoConfig.fps,
          transition_duration: videoConfig.transition_duration
        }
      }

      console.log('🔍 Debug - Dados enviados para criação do vídeo:', videoData)

      setVideoCreationProgress({ stage: 'Enviando dados para o servidor...', progress: 20 })

      const response = await fetch('http://localhost:5000/api/videos/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(videoData)
      })

      const data = await response.json()

      if (data.success) {
        setVideoCreationProgress({ stage: 'Vídeo criado com sucesso!', progress: 100 })
        setCreatedVideo(data.data)
        
        // Salvar informações do vídeo no localStorage
        localStorage.setItem('created_video', JSON.stringify(data.data))
        
        showNotification(`Vídeo criado com sucesso! Duração: ${data.data.duration}s, Resolução: ${data.data.resolution}`, 'success')
      } else {
        showNotification(`Erro ao criar vídeo: ${data.error}`, 'error')
      }
    } catch (error) {
      console.error('Erro ao criar vídeo:', error)
      alert(`❌ Erro de conexão: ${error.message}`)
    } finally {
      setIsCreatingVideo(false)
      setVideoCreationProgress({ stage: '', progress: 0 })
    }
  }

  const updateVideoConfig = (key, value) => {
    setVideoConfig(prev => ({
      ...prev,
      [key]: value
    }))
  }

  // ========== FUNÇÕES DO AGENTE IA PERSONALIZADO ==========

  // Função para ler arquivos TXT
  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files)

    files.forEach(file => {
      if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          const content = e.target.result
          setAgentContextFiles(prev => [...prev, {
            name: file.name,
            content: content,
            size: file.size
          }])
        }
        reader.readAsText(file, 'UTF-8')
      } else {
        alert('Por favor, selecione apenas arquivos .txt')
      }
    })
  }

  // Função para remover arquivo de contexto
  const removeContextFile = (index) => {
    setAgentContextFiles(prev => prev.filter((_, i) => i !== index))
  }

  // Função para gerar roteiro com o agente personalizado
  const handleGenerateAgentScript = async () => {
    if (!selectedAgentTitle.trim()) {
      alert('Selecione um título')
      return
    }

    if (!selectedAgentPremise.trim()) {
      alert('Selecione uma premissa')
      return
    }

    if (!agentPrompt.trim()) {
      alert('Digite um prompt personalizado')
      return
    }

    setIsGeneratingAgentScript(true)
    setAgentProgress({ current: 0, total: agentNumberOfChapters, stage: 'Iniciando geração...' })

    try {
      // Simular progresso de capítulos
      const progressInterval = setInterval(() => {
        setAgentProgress(prev => {
          if (prev.current < prev.total) {
            const newCurrent = prev.current + 1
            return {
              current: newCurrent,
              total: prev.total,
              stage: `Gerando Capítulo ${newCurrent} de ${prev.total}...`
            }
          }
          return prev
        })
      }, 2000) // Atualizar a cada 2 segundos

      // Limpar intervalo após 30 segundos ou quando terminar
      setTimeout(() => clearInterval(progressInterval), 30000)
      // Construir o prompt completo
      let fullPrompt = agentPrompt

      // Adicionar instruções se fornecidas
      if (agentInstructions.trim()) {
        fullPrompt += `\n\n## INSTRUÇÕES ESPECÍFICAS:\n${agentInstructions}`
      }

      // Adicionar contexto dos arquivos
      if (agentContextFiles.length > 0) {
        fullPrompt += `\n\n## CONTEXTO DOS ARQUIVOS:\n`
        agentContextFiles.forEach(file => {
          fullPrompt += `\n### ${file.name}:\n${file.content}\n`
        })
      }

      // Adicionar contexto adicional se fornecido
      if (agentContextText.trim()) {
        fullPrompt += `\n\n## CONTEXTO ADICIONAL:\n${agentContextText}`
      }

      // Adicionar título e premissa
      fullPrompt += `\n\n## DADOS PARA O ROTEIRO:\n`
      fullPrompt += `**TÍTULO:** ${selectedAgentTitle}\n`
      fullPrompt += `**PREMISSA:** ${selectedAgentPremise}`

      // Usar endpoint específico para geração de roteiros com agente
      const endpoint = 'http://localhost:5000/api/premise/generate-agent-script'
      const requestBody = {
        title: selectedAgentTitle,
        premise: selectedAgentPremise,
        custom_prompt: fullPrompt,
        ai_provider: agentAiProvider,
        api_keys: apiKeys,
        script_size: agentScriptSize,
        num_chapters: agentNumberOfChapters,
        use_parts_generation: usePartsGeneration,
        openrouter_model: agentOpenRouterModel
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      })

      const data = await response.json()

      if (data.success) {
        let generatedContent = ''

        if (data.script && data.script.content) {
          generatedContent = data.script.content
        } else {
          throw new Error('Nenhum conteúdo gerado')
        }

        setAgentGeneratedScript({
          title: selectedAgentTitle,
          premise: selectedAgentPremise,
          content: generatedContent,
          prompt: fullPrompt,
          provider: agentAiProvider,
          model: agentOpenRouterModel,
          timestamp: new Date().toISOString()
        })

        alert('✅ Roteiro gerado com sucesso!')
      } else {
        throw new Error(data.error || 'Erro na geração do roteiro')
      }
    } catch (error) {
      console.error('Erro na geração do roteiro:', error)
      alert('❌ Erro na geração: ' + error.message)
    } finally {
      setIsGeneratingAgentScript(false)
      setAgentProgress({ current: 0, total: 0, stage: '' })
    }
  }

  // Função para baixar roteiro gerado
  const downloadAgentScript = () => {
    if (!agentGeneratedScript) return

    const content = `TÍTULO: ${agentGeneratedScript.title}

PREMISSA: ${agentGeneratedScript.premise}

ROTEIRO GERADO:
${agentGeneratedScript.content}

---
Gerado em: ${new Date(agentGeneratedScript.timestamp).toLocaleString()}
Provider: ${agentGeneratedScript.provider}
${agentGeneratedScript.model !== 'auto' ? `Modelo: ${agentGeneratedScript.model}` : ''}
`

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `roteiro_agente_${agentGeneratedScript.title.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 30)}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  // Função para resetar o agente
  const resetAgent = () => {
    setAgentPrompt('')
    setAgentContextFiles([])
    setAgentContextText('')
    setSelectedAgentTitle('')
    setSelectedAgentPremise('')
    setAgentGeneratedScript(null)
    setAgentInstructions('')
  }

  // ========== FIM DAS FUNÇÕES DO AGENTE ==========

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
    if (!workflowConfig.url.trim()) {
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
          url: workflowConfig.url,
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
    { id: 'images', label: 'Geração de Imagens', icon: Image, color: 'emerald' },
    { id: 'video-edit', label: 'Editar Vídeo', icon: Video, color: 'pink' },
    { id: 'workflow', label: 'Fluxos Completos', icon: Workflow, color: 'indigo' },
    { id: 'api-tests', label: 'Testes de API', icon: Settings, color: 'cyan' }
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
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-300">
                  Canal do YouTube
                </label>
                <button
                  onClick={() => setShowChannelsManager(true)}
                  className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 transition-colors flex items-center space-x-1"
                >
                  <Youtube size={12} />
                  <span>Canais Salvos</span>
                </button>
              </div>
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
                <div className="flex items-center justify-between mt-2">
                  <p className="text-xs text-gray-400">
                    💡 Descreva como você quer que os títulos sejam remodelados baseado nos títulos extraídos
                  </p>
                  <button
                    type="button"
                    onClick={() => setShowPromptManager(true)}
                    className="text-xs bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 flex items-center gap-1"
                  >
                    <Save className="w-3 h-3" />
                    Prompts Salvos
                  </button>
                </div>

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

          {/* Priorizar títulos gerados, senão usar originais */}
          {generatedTitles && generatedTitles.generated_titles && generatedTitles.generated_titles.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              <div className="mb-3 p-2 bg-green-900/30 border border-green-700 rounded-lg">
                <p className="text-green-300 text-sm font-medium">
                  ✨ Usando títulos gerados pela IA ({generatedTitles.generated_titles.length} disponíveis)
                </p>
              </div>
              {generatedTitles.generated_titles.slice(0, 15).map((title, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    selectedTitles.includes(title)
                      ? 'border-purple-400 bg-purple-900/30'
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
                  onClick={() => toggleTitleSelection(title)}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`w-4 h-4 rounded border-2 mt-1 flex items-center justify-center ${
                      selectedTitles.includes(title)
                        ? 'border-purple-400 bg-purple-400'
                        : 'border-gray-500'
                    }`}>
                      {selectedTitles.includes(title) && (
                        <CheckCircle className="w-3 h-3 text-white" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-white line-clamp-2">
                        {title}
                      </p>
                      <p className="text-xs text-green-400 mt-1">
                        🤖 Título gerado pela IA
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : results && results.videos && results.videos.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              <div className="mb-3 p-2 bg-yellow-900/30 border border-yellow-700 rounded-lg">
                <p className="text-yellow-300 text-sm font-medium">
                  ⚠️ Usando títulos originais - Recomendamos gerar títulos primeiro
                </p>
              </div>
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
                Extraia títulos primeiro na aba "Extração YouTube" e gere títulos na aba "Geração de Títulos"
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
          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-gray-400">
              💡 Prompt personalizado para gerar premissas específicas para seu nicho
            </p>
            <button
              type="button"
              onClick={() => setShowPromptManager(true)}
              className="text-xs bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 flex items-center gap-1"
            >
              <Save className="w-3 h-3" />
              Prompts Salvos
            </button>
          </div>
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

        {/* ========== AGENTE IA PERSONALIZADO ========== */}
        <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h4 className="text-xl font-bold text-white flex items-center space-x-2">
              <span className="text-2xl">🤖</span>
              <span>Agente IA Personalizado</span>
              <span className="text-sm bg-purple-600 px-2 py-1 rounded-full">AVANÇADO</span>
            </h4>
            <button
              onClick={resetAgent}
              className="flex items-center space-x-2 px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
            >
              <span>🔄</span>
              <span>Resetar</span>
            </button>
          </div>

          {/* Seleção de Título e Premissa para o Agente */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Seleção de Título */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                📝 Selecionar Título
              </label>
              {generatedTitles && generatedTitles.generated_titles ? (
                <select
                  value={selectedAgentTitle}
                  onChange={(e) => setSelectedAgentTitle(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Selecione um título...</option>
                  {generatedTitles.generated_titles.slice(0, 10).map((title, index) => (
                    <option key={index} value={title}>
                      {title.length > 60 ? title.substring(0, 60) + '...' : title}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="p-4 bg-gray-700 border border-gray-600 rounded-lg text-gray-400 text-center">
                  Gere títulos primeiro na aba "Geração de Títulos"
                </div>
              )}
            </div>

            {/* Seleção de Premissa */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                🎯 Selecionar Premissa
              </label>
              {generatedPremises && generatedPremises.length > 0 ? (
                <select
                  value={selectedAgentPremise}
                  onChange={(e) => setSelectedAgentPremise(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Selecione uma premissa...</option>
                  {generatedPremises.map((premise, index) => (
                    <option key={index} value={premise.premise}>
                      {premise.title.length > 60 ? premise.title.substring(0, 60) + '...' : premise.title}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="p-4 bg-gray-700 border border-gray-600 rounded-lg text-gray-400 text-center">
                  Gere premissas primeiro na aba "Premissas"
                </div>
              )}
            </div>
          </div>

          {/* Prompt Personalizado */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              🎭 Prompt Personalizado do Agente
            </label>
            <textarea
              value={agentPrompt}
              onChange={(e) => setAgentPrompt(e.target.value)}
              placeholder="Digite seu prompt personalizado para o agente IA..."
              rows={12}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none font-mono text-sm"
            />
          </div>

          {/* Instruções Específicas */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              📋 Instruções Específicas (Opcional)
            </label>
            <textarea
              value={agentInstructions}
              onChange={(e) => setAgentInstructions(e.target.value)}
              placeholder="Ex: Foque em drama familiar, use linguagem jovem, inclua reviravoltas, etc..."
              rows={3}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Upload de Arquivos TXT */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              📁 Arquivos de Contexto (.txt)
            </label>
            <div className="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center">
              <input
                type="file"
                multiple
                accept=".txt"
                onChange={handleFileUpload}
                className="hidden"
                id="context-files"
              />
              <label
                htmlFor="context-files"
                className="cursor-pointer flex flex-col items-center space-y-2"
              >
                <span className="text-4xl">📄</span>
                <span className="text-white">Clique para selecionar arquivos .txt</span>
                <span className="text-gray-400 text-sm">Os arquivos serão usados como contexto para o agente</span>
              </label>
            </div>

            {/* Lista de arquivos carregados */}
            {agentContextFiles.length > 0 && (
              <div className="mt-4 space-y-2">
                <h6 className="text-sm font-medium text-gray-300">Arquivos Carregados:</h6>
                {agentContextFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <span className="text-blue-400">📄</span>
                      <span className="text-white text-sm">{file.name}</span>
                      <span className="text-gray-400 text-xs">({(file.size / 1024).toFixed(1)} KB)</span>
                    </div>
                    <button
                      onClick={() => removeContextFile(index)}
                      className="text-red-400 hover:text-red-300 text-sm"
                    >
                      ❌
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Contexto Adicional */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              💭 Contexto Adicional (Opcional)
            </label>
            <textarea
              value={agentContextText}
              onChange={(e) => setAgentContextText(e.target.value)}
              placeholder="Digite qualquer contexto adicional que o agente deve considerar..."
              rows={4}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Configurações de IA */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Provider de IA */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                🤖 Provider de IA
              </label>
              <select
                value={agentAiProvider}
                onChange={(e) => setAgentAiProvider(e.target.value)}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="auto">🎯 Automático (Gemini)</option>
                <option value="gemini">💎 Gemini</option>
                <option value="openai">🧠 OpenAI</option>
                <option value="openrouter">🌐 OpenRouter</option>
              </select>
            </div>

            {/* Modelo OpenRouter */}
            {agentAiProvider === 'openrouter' && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  🎛️ Modelo OpenRouter
                </label>
                <select
                  value={agentOpenRouterModel}
                  onChange={(e) => setAgentOpenRouterModel(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="auto">Automático</option>
                  <option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet</option>
                  <option value="openai/gpt-4o">GPT-4o</option>
                  <option value="google/gemini-pro-1.5">Gemini Pro 1.5</option>
                  <option value="meta-llama/llama-3.1-405b-instruct">Llama 3.1 405B</option>
                </select>
              </div>
            )}
          </div>

          {/* Configuração de Tamanho do Roteiro */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              📏 Tamanho do Roteiro
            </label>
            <div className="grid grid-cols-3 gap-3">
              <button
                onClick={() => setAgentScriptSize('curto')}
                className={`px-4 py-3 rounded-lg border transition-all text-sm font-medium ${
                  agentScriptSize === 'curto'
                    ? 'border-blue-400 bg-blue-900/30 text-blue-300'
                    : 'border-gray-600 bg-gray-700 text-gray-300 hover:border-gray-500'
                }`}
              >
                <div className="text-center">
                  <div className="text-lg mb-1">📄</div>
                  <div>Curto</div>
                  <div className="text-xs text-gray-400 mt-1">1.5-2K palavras</div>
                </div>
              </button>
              <button
                onClick={() => setAgentScriptSize('medio')}
                className={`px-4 py-3 rounded-lg border transition-all text-sm font-medium ${
                  agentScriptSize === 'medio'
                    ? 'border-green-400 bg-green-900/30 text-green-300'
                    : 'border-gray-600 bg-gray-700 text-gray-300 hover:border-gray-500'
                }`}
              >
                <div className="text-center">
                  <div className="text-lg mb-1">📃</div>
                  <div>Médio</div>
                  <div className="text-xs text-gray-400 mt-1">3.5-5K palavras</div>
                </div>
              </button>
              <button
                onClick={() => setAgentScriptSize('longo')}
                className={`px-4 py-3 rounded-lg border transition-all text-sm font-medium ${
                  agentScriptSize === 'longo'
                    ? 'border-purple-400 bg-purple-900/30 text-purple-300'
                    : 'border-gray-600 bg-gray-700 text-gray-300 hover:border-gray-500'
                }`}
              >
                <div className="text-center">
                  <div className="text-lg mb-1">📋</div>
                  <div>Longo</div>
                  <div className="text-xs text-gray-400 mt-1">7-10K palavras</div>
                </div>
              </button>
            </div>
            <div className="mt-2 text-xs text-gray-400 text-center">
              {agentScriptSize === 'curto' && 'Roteiro conciso e direto, ideal para conteúdo rápido'}
              {agentScriptSize === 'medio' && 'Roteiro equilibrado com boa profundidade de conteúdo'}
              {agentScriptSize === 'longo' && 'Roteiro detalhado e abrangente para conteúdo extenso'}
            </div>
          </div>

          {/* Configuração de Geração em Partes */}
          {agentScriptSize === 'longo' && (
            <div className="mb-6">
              <div className="flex items-center space-x-3 p-4 bg-purple-900/20 border border-purple-500/30 rounded-lg">
                <input
                  type="checkbox"
                  id="usePartsGeneration"
                  checked={usePartsGeneration}
                  onChange={(e) => setUsePartsGeneration(e.target.checked)}
                  className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500 focus:ring-2"
                />
                <label htmlFor="usePartsGeneration" className="flex-1">
                  <div className="text-sm font-medium text-purple-300 mb-1">
                    🔄 Geração em Partes
                  </div>
                  <div className="text-xs text-gray-400">
                    Divide roteiros longos em 4 partes para contornar limites de tokens das IAs
                  </div>
                </label>
              </div>
              {usePartsGeneration && (
                <div className="mt-3 p-3 bg-gray-800/50 rounded-lg">
                  <div className="text-xs text-gray-400 mb-2">📋 Estrutura das Partes:</div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                    <div className="p-2 bg-blue-900/30 rounded text-blue-300">
                      <div className="font-medium">1. Introdução</div>
                      <div className="text-gray-400">25% (~2K tokens)</div>
                    </div>
                    <div className="p-2 bg-green-900/30 rounded text-green-300">
                      <div className="font-medium">2. Desenvolvimento</div>
                      <div className="text-gray-400">40% (~3K tokens)</div>
                    </div>
                    <div className="p-2 bg-orange-900/30 rounded text-orange-300">
                      <div className="font-medium">3. Clímax</div>
                      <div className="text-gray-400">25% (~2K tokens)</div>
                    </div>
                    <div className="p-2 bg-purple-900/30 rounded text-purple-300">
                      <div className="font-medium">4. Conclusão</div>
                      <div className="text-gray-400">10% (~1K tokens)</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Controle de Número de Capítulos */}
          <div className="mb-6">
            <div className="p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="text-sm font-medium text-blue-300 mb-1">
                    📚 Número de Capítulos
                  </div>
                  <div className="text-xs text-gray-400">
                    Controle a estrutura e duração do roteiro
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-blue-300">{agentNumberOfChapters}</div>
                  <div className="text-xs text-gray-400">
                    {(agentNumberOfChapters * 4.5).toFixed(1)}-{(agentNumberOfChapters * 6).toFixed(1)} min
                  </div>
                </div>
              </div>
              
              <div className="mb-4">
                <input
                  type="range"
                  min="1"
                  max="15"
                  value={agentNumberOfChapters}
                  onChange={(e) => setAgentNumberOfChapters(parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                  style={{
                    background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${((agentNumberOfChapters - 1) / 14) * 100}%, #374151 ${((agentNumberOfChapters - 1) / 14) * 100}%, #374151 100%)`
                  }}
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>1</span>
                  <span>8</span>
                  <span>15</span>
                </div>
              </div>
              
              <div className="text-xs text-gray-400">
                {agentNumberOfChapters <= 3 && (
                  <div className="flex items-center space-x-2 text-yellow-400">
                    <span>⚠️</span>
                    <span>Roteiro muito curto - Recomendado para conteúdo rápido</span>
                  </div>
                )}
                {agentNumberOfChapters >= 4 && agentNumberOfChapters <= 8 && (
                  <div className="flex items-center space-x-2 text-green-400">
                    <span>✅</span>
                    <span>Duração ideal para a maioria dos conteúdos</span>
                  </div>
                )}
                {agentNumberOfChapters >= 9 && agentNumberOfChapters <= 12 && (
                  <div className="flex items-center space-x-2 text-blue-400">
                    <span>📚</span>
                    <span>Roteiro extenso - Ideal para conteúdo educativo</span>
                  </div>
                )}
                {agentNumberOfChapters >= 13 && (
                  <div className="flex items-center space-x-2 text-purple-400">
                    <span>🎬</span>
                    <span>Roteiro muito longo - Para documentários ou análises profundas</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Botão de Geração */}
          <button
            onClick={handleGenerateAgentScript}
            disabled={isGeneratingAgentScript || !selectedAgentTitle || !selectedAgentPremise || !agentPrompt.trim()}
            className={`w-full flex items-center justify-center space-x-2 px-6 py-4 rounded-lg font-medium transition-all text-lg ${
              isGeneratingAgentScript || !selectedAgentTitle || !selectedAgentPremise || !agentPrompt.trim()
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 hover:shadow-lg transform hover:scale-105'
            }`}
          >
            {isGeneratingAgentScript ? (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                <div className="flex flex-col items-center">
                  <span>Gerando Roteiro...</span>
                  {agentProgress.stage && (
                    <span className="text-sm text-gray-300 mt-1">{agentProgress.stage}</span>
                  )}
                  {agentProgress.total > 0 && (
                    <div className="w-48 bg-gray-700 rounded-full h-2 mt-2">
                      <div 
                        className="bg-blue-400 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${(agentProgress.current / agentProgress.total) * 100}%` }}
                      ></div>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                <span className="text-2xl">🎬</span>
                <span>Gerar Roteiro com Agente IA ({agentNumberOfChapters} capítulos)</span>
              </>
            )}
          </button>

          {/* Resultado do Agente */}
          {agentGeneratedScript && (
            <div className="mt-8 p-6 bg-gradient-to-r from-green-900/20 to-blue-900/20 border border-green-500/30 rounded-xl">
              <div className="flex items-center justify-between mb-4">
                <h5 className="text-xl font-bold text-white flex items-center space-x-2">
                  <span className="text-2xl">✨</span>
                  <span>Roteiro Gerado pelo Agente IA</span>
                </h5>
                <div className="flex space-x-2">
                  <button
                    onClick={() => navigator.clipboard.writeText(agentGeneratedScript.content)}
                    className="flex items-center space-x-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    <span>📋</span>
                    <span>Copiar</span>
                  </button>
                  <button
                    onClick={downloadAgentScript}
                    className="flex items-center space-x-1 px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
                  >
                    <span>💾</span>
                    <span>Baixar</span>
                  </button>
                </div>
              </div>

              {/* Informações do Roteiro */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="p-4 bg-gray-800/50 rounded-lg">
                  <h6 className="text-sm font-medium text-blue-400 mb-2">📝 Título:</h6>
                  <p className="text-white text-sm">{agentGeneratedScript.title}</p>
                </div>
                <div className="p-4 bg-gray-800/50 rounded-lg">
                  <h6 className="text-sm font-medium text-purple-400 mb-2">🎯 Premissa:</h6>
                  <p className="text-white text-sm max-h-20 overflow-y-auto">{agentGeneratedScript.premise}</p>
                </div>
              </div>

              {/* Roteiro Gerado */}
              <div className="p-4 bg-gray-800/50 rounded-lg">
                <h6 className="text-sm font-medium text-green-400 mb-3 flex items-center justify-between">
                  <span>🎬 Roteiro Completo:</span>
                  <div className="flex items-center space-x-2 text-xs text-gray-400">
                    <span>Provider: {agentGeneratedScript.provider}</span>
                    {agentGeneratedScript.model !== 'auto' && (
                      <span>| Modelo: {agentGeneratedScript.model}</span>
                    )}
                  </div>
                </h6>
                <div className="max-h-96 overflow-y-auto">
                  <p className="text-white text-sm whitespace-pre-wrap leading-relaxed">
                    {agentGeneratedScript.content}
                  </p>
                </div>
              </div>

              {/* Estatísticas */}
              <div className="mt-4 flex items-center justify-between text-xs text-gray-400">
                <span>Gerado em: {new Date(agentGeneratedScript.timestamp).toLocaleString()}</span>
                <span>Caracteres: {agentGeneratedScript.content.length.toLocaleString()}</span>
              </div>
            </div>
          )}

        </div>

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
              📊 Número de Capítulos
            </label>
            <div className="bg-gray-700 border border-gray-600 rounded-lg p-4">
              {/* Slider */}
              <div className="mb-3">
                <input
                  type="range"
                  min="1"
                  max="15"
                  value={numberOfChapters}
                  onChange={(e) => setNumberOfChapters(parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
                  style={{
                    background: `linear-gradient(to right, #10b981 0%, #10b981 ${((numberOfChapters - 1) / 14) * 100}%, #4b5563 ${((numberOfChapters - 1) / 14) * 100}%, #4b5563 100%)`
                  }}
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>1</span>
                  <span>5</span>
                  <span>10</span>
                  <span>15</span>
                </div>
              </div>
              
              {/* Valor atual e estimativa */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-white font-medium text-lg">{numberOfChapters}</span>
                  <span className="text-gray-400 text-sm">capítulos</span>
                </div>
                <div className="text-right">
                  <div className="text-green-400 font-medium text-sm">
                    ⏱️ {Math.round(numberOfChapters * 4.5)} - {Math.round(numberOfChapters * 6)} min
                  </div>
                  <div className="text-gray-400 text-xs">
                    Duração estimada
                  </div>
                </div>
              </div>
              
              {/* Validação e recomendações */}
              <div className="mt-3 p-2 rounded-lg text-xs">
                {numberOfChapters <= 3 && (
                  <div className="text-yellow-400 bg-yellow-900/20 p-2 rounded">
                    ⚠️ Poucos capítulos podem resultar em conteúdo superficial
                  </div>
                )}
                {numberOfChapters >= 4 && numberOfChapters <= 8 && (
                  <div className="text-green-400 bg-green-900/20 p-2 rounded">
                    ✅ Quantidade ideal para conteúdo equilibrado
                  </div>
                )}
                {numberOfChapters >= 9 && numberOfChapters <= 12 && (
                  <div className="text-blue-400 bg-blue-900/20 p-2 rounded">
                    📚 Ótimo para conteúdo detalhado e abrangente
                  </div>
                )}
                {numberOfChapters > 12 && (
                  <div className="text-orange-400 bg-orange-900/20 p-2 rounded">
                    🔥 Muitos capítulos podem tornar o conteúdo extenso demais
                  </div>
                )}
              </div>
            </div>
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
            <div className="flex items-center space-x-2 flex-wrap">
              {/* Botões de Copiar */}
              <button
                onClick={() => copyScriptToClipboard(generatedScripts)}
                className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
              >
                <Copy size={14} />
                <span>Copiar com Capítulos</span>
              </button>
              <button
                onClick={() => copyScriptConcatenatedToClipboard(generatedScripts)}
                className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
              >
                <Copy size={14} />
                <span>Copiar Sequência</span>
              </button>

              {/* Botões de Download */}
              <button
                onClick={() => downloadScriptAsTxt(generatedScripts, 'chapters')}
                className="flex items-center space-x-2 px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
              >
                <Download size={14} />
                <span>Baixar com Capítulos</span>
              </button>
              <button
                onClick={() => downloadScriptAsTxt(generatedScripts, 'concatenated')}
                className="flex items-center space-x-2 px-3 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm"
              >
                <Download size={14} />
                <span>Baixar Sequência</span>
              </button>
            </div>
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
                  value={workflowConfig.url}
                  onChange={(e) => setWorkflowConfig(prev => ({ ...prev, url: e.target.value }))}
                  placeholder="CanalClaYOliveiraOficial ou UCykzGI8qdfLywefslXnnyGw"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                <div className="flex justify-end mt-2">
                  <button
                    type="button"
                    onClick={() => setShowChannelsManager(true)}
                    className="text-xs bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 flex items-center gap-1"
                  >
                    <Youtube className="w-3 h-3" />
                    Canais Salvos
                  </button>
                </div>
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
                    <div className="flex items-center justify-between mt-2">
                      <p className="text-xs text-gray-400">
                        💡 Descreva como você quer que os títulos sejam remodelados
                      </p>
                      <button
                        type="button"
                        onClick={() => setShowPromptManager(true)}
                        className="text-xs bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 flex items-center gap-1"
                      >
                        <Save className="w-3 h-3" />
                        Prompts Salvos
                      </button>
                    </div>
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
            disabled={isRunningWorkflow || !workflowConfig.url.trim()}
            className={`flex items-center justify-center space-x-2 px-6 py-4 rounded-lg font-medium transition-all ${
              isRunningWorkflow || !workflowConfig.url.trim()
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
                <div className="flex items-center space-x-1 flex-wrap">
                  {/* Botões de Copiar */}
                  <button
                    onClick={() => copyScriptToClipboard(workflowResults.scripts)}
                    className="flex items-center space-x-1 px-2 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors text-xs"
                  >
                    <Copy size={12} />
                    <span>Copiar</span>
                  </button>
                  <button
                    onClick={() => copyScriptConcatenatedToClipboard(workflowResults.scripts)}
                    className="flex items-center space-x-1 px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-xs"
                  >
                    <Copy size={12} />
                    <span>Sequência</span>
                  </button>

                  {/* Botões de Download */}
                  <button
                    onClick={() => downloadScriptAsTxt(workflowResults.scripts, 'chapters')}
                    className="flex items-center space-x-1 px-2 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors text-xs"
                  >
                    <Download size={12} />
                    <span>TXT</span>
                  </button>
                  <button
                    onClick={() => downloadScriptAsTxt(workflowResults.scripts, 'concatenated')}
                    className="flex items-center space-x-1 px-2 py-1 bg-orange-600 text-white rounded hover:bg-orange-700 transition-colors text-xs"
                  >
                    <Download size={12} />
                    <span>TXT Seq</span>
                  </button>
                </div>
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
      language: 'en'  // 'en' para inglês, 'pt' para português
    }
  })

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

    return segments
  }

  // Função para recarregar chaves de API (solução simplificada)
  const reloadApiKeys = async () => {
    try {
      console.log('🔄 Recarregando chaves de API...')

      // Primeiro, tentar carregar do localStorage atual
      let apiKeys = JSON.parse(localStorage.getItem('api_keys') || '{}')
      console.log('🔍 Chaves atuais no localStorage:', apiKeys)

      // Se não tiver chaves ou não tiver Gemini, criar um conjunto padrão
      if (!apiKeys.gemini_1 && !apiKeys.gemini) {
        console.log('🔄 Criando chaves padrão...')

        // Tentar diferentes fontes de dados
        const sources = [
          'api_keys',
          'settings_api_keys',
          'user_api_keys',
          'config_api_keys'
        ]

        for (const source of sources) {
          try {
            const data = localStorage.getItem(source)
            if (data) {
              const parsed = JSON.parse(data)
              console.log(`🔍 Dados encontrados em ${source}:`, parsed)

              if (parsed.gemini || parsed.gemini_1) {
                apiKeys = {
                  ...apiKeys,
                  ...parsed,
                  gemini_1: parsed.gemini || parsed.gemini_1,
                  gemini: parsed.gemini || parsed.gemini_1
                }
                break
              }
            }
          } catch (e) {
            console.log(`❌ Erro ao ler ${source}:`, e)
          }
        }

        // Se ainda não tiver, criar com chaves conhecidas do arquivo
        if (!apiKeys.gemini_1 && !apiKeys.gemini) {
          console.log('🔧 Usando chaves conhecidas do backend...')
          apiKeys = {
            openai: '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',
            gemini_1: 'AIzaSyBqUjzLHNPycDIzvwnI5JisOwmNubkfRRc',
            gemini: 'AIzaSyBqUjzLHNPycDIzvwnI5JisOwmNubkfRRc',
            openrouter: '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',
            elevenlabs: '',
            together: '',
            rapidapi: '77322fda67msh6bbb767e727a6ebp147c75jsn5b47d75dfb80'
          }
        }

        // Salvar no localStorage
        localStorage.setItem('api_keys', JSON.stringify(apiKeys))
        console.log('✅ Chaves sincronizadas:', apiKeys)
      }

      return apiKeys

    } catch (error) {
      console.error('❌ Erro ao recarregar chaves:', error)
      throw error
    }
  }

  // Função para gerar TTS
  const generateTTSAudio = async () => {
    if (!generatedScripts) {
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
      console.log('🔑 DEBUG: Chaves de API disponíveis:', Object.keys(apiKeys))
      console.log('🔑 DEBUG: Chaves completas:', apiKeys)

      // Se não tiver chaves ou não tiver a chave necessária, tentar recarregar do backend
      const hasElevenLabs = !!apiKeys.elevenlabs
      const hasGemini = !!(apiKeys.gemini_1 || apiKeys.gemini)

      if ((!hasElevenLabs && ttsProvider === 'elevenlabs') || (!hasGemini && ttsProvider === 'gemini')) {
        console.log('🔄 Chave não encontrada, tentando recarregar do backend...')
        try {
          apiKeys = await reloadApiKeys()
          console.log('✅ Chaves recarregadas:', apiKeys)
        } catch (reloadError) {
          console.error('❌ Erro ao recarregar chaves:', reloadError)
        }
      }

      // Preparar texto do roteiro
      let fullText = ''
      if (generatedScripts.chapters) {
        fullText = generatedScripts.chapters
          .map(chapter => chapter.content || '')
          .join('\n\n')
      } else if (typeof generatedScripts === 'string') {
        fullText = generatedScripts
      }

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
        console.log('🔄 Usando rotação automática de chaves Gemini')

        endpoint = '/api/automations/generate-tts'
        baseRequestData = {
          // NÃO enviar api_key - deixar o backend usar rotação automática
          voice_name: ttsSettings.gemini.voice_name,
          model: ttsSettings.gemini.model,
          speed: ttsSettings.gemini.speed,
          pitch: ttsSettings.gemini.pitch,
          volume_gain_db: ttsSettings.gemini.volume_gain_db
        }
      } else if (ttsProvider === 'kokoro') {
        console.log('🔄 Usando Kokoro TTS local')

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

        // Construir URL completa para debug
        const fullUrl = window.location.origin.replace(':5173', ':5000') + endpoint
        console.log(`🔍 URL completa: ${fullUrl}`)
        console.log(`🔍 Endpoint: ${endpoint}`)
        console.log(`🔍 Dados da requisição:`, requestData)

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })

        console.log(`🔍 Status da resposta: ${response.status}`)
        console.log(`🔍 Headers da resposta:`, response.headers)

        // Verificar se a resposta é válida
        if (!response.ok) {
          const errorText = await response.text()
          console.log(`❌ Erro HTTP ${response.status}:`, errorText)
          throw new Error(`HTTP ${response.status}: ${errorText}`)
        }

        // Verificar se a resposta tem conteúdo
        const responseText = await response.text()
        console.log(`🔍 Resposta bruta (${responseText.length} chars):`, responseText.substring(0, 500))

        if (!responseText || responseText.trim() === '') {
          throw new Error(`Resposta vazia do servidor para segmento ${i + 1}`)
        }

        // Tentar fazer parse do JSON
        let result
        try {
          result = JSON.parse(responseText)
        } catch (parseError) {
          console.log(`❌ Erro ao fazer parse do JSON:`, parseError)
          console.log(`🔍 Resposta que causou erro:`, responseText)
          throw new Error(`Resposta inválida do servidor: ${parseError.message}`)
        }

        console.log(`🔍 Resultado parseado:`, result)

        if (!result.success) {
          throw new Error(`Erro no segmento ${i + 1}: ${result.error}`)
        }

        segments.push({
          index: i + 1,
          text: segment,
          audio: result.data || result,
          duration: (result.data && result.data.duration) || (result.duration) || 0
        })

        // Adicionar áudio gerado à lista para exibição
        const audioData = result.data || result
        if (audioData.audio_url) {
          const newAudio = {
            id: Date.now() + i,
            filename: audioData.filename || `audio_${Date.now()}.wav`,
            url: audioData.audio_url,
            text: segment.substring(0, 100) + (segment.length > 100 ? '...' : ''),
            voice: audioData.voice_used || audioData.voice || 'unknown',
            size: audioData.size || 'N/A',
            timestamp: new Date().toLocaleTimeString()
          }

          setGeneratedAudios(prev => [newAudio, ...prev.slice(0, 9)]) // Manter apenas os 10 mais recentes
          console.log(`🎵 Áudio adicionado à lista:`, newAudio)
        }

        // Pequena pausa entre requisições para não sobrecarregar a API
        if (i < textSegments.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
      }

      setTtsSegments(segments)
      
      // Salvar dados de áudio no localStorage para uso na criação de vídeo
      const audioData = segments.map(segment => ({
        filename: segment.audio.filename,
        audio_url: segment.audio.audio_url,
        duration: segment.duration,
        size: segment.audio.size,
        voice_used: segment.audio.voice_used,
        provider: ttsProvider,
        text_segment: segment.text.substring(0, 100) + (segment.text.length > 100 ? '...' : '')
      }))
      
      localStorage.setItem('generated_audio_files', JSON.stringify(audioData))
      console.log('💾 Dados de áudio salvos no localStorage:', audioData)
      
      console.log(`✅ ${segments.length} segmentos de áudio gerados com sucesso!`)

    } catch (err) {
      console.error('❌ Erro na geração de áudio:', err)
      setTtsError(err.message)
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
      console.log('🔗 Juntando segmentos de áudio...')

      const response = await fetch('/api/automations/join-audio', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          segments: ttsSegments.map(seg => ({
            filename: seg.audio.filename,
            index: seg.index
          }))
        })
      })

      const result = await response.json()

      if (!result.success) {
        throw new Error(result.error || 'Erro ao juntar áudios')
      }

      setFinalTTSAudio(result.data)
      
      // Salvar áudio final no localStorage
      const finalAudioData = [{
        filename: result.data.filename,
        audio_url: `/api/audio/${result.data.filename}`,
        duration: result.data.duration,
        size: result.data.size,
        voice_used: ttsSegments[0]?.audio.voice_used || 'unknown',
        provider: ttsProvider,
        text_segment: 'Áudio final unificado',
        is_final: true,
        segments_count: result.data.segments_count
      }]
      
      localStorage.setItem('generated_audio_files', JSON.stringify(finalAudioData))
      console.log('💾 Áudio final salvo no localStorage:', finalAudioData)
      
      console.log('✅ Áudios unidos com sucesso:', result.data)

    } catch (err) {
      console.error('❌ Erro ao juntar áudios:', err)
      setTtsError(err.message)
    } finally {
      setIsJoiningAudio(false)
    }
  }

  const renderTTSGeneration = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Mic size={24} className="text-yellow-400" />
          <span>Geração de Áudio TTS</span>
        </h3>

        {/* Status dos Pré-requisitos */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Títulos</h4>
              {generatedTitles ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <AlertCircle className="w-5 h-5 text-gray-400" />
              )}
            </div>
            <p className="text-sm text-gray-400">
              {generatedTitles ? 'Disponíveis' : 'Necessários'}
            </p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Premissas</h4>
              {generatedPremises ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <AlertCircle className="w-5 h-5 text-gray-400" />
              )}
            </div>
            <p className="text-sm text-gray-400">
              {generatedPremises ? 'Disponíveis' : 'Necessárias'}
            </p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Roteiros</h4>
              {generatedScripts ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-400" />
              )}
            </div>
            <p className="text-sm text-gray-400">
              {generatedScripts ? 'Prontos para TTS' : 'Obrigatórios'}
            </p>
          </div>
        </div>

        {/* DEBUG TEMPORÁRIO */}
        <div className="mb-4 p-3 bg-yellow-900 border border-yellow-600 rounded-lg">
          <h4 className="text-yellow-300 font-medium mb-2">🔍 DEBUG TTS</h4>
          <div className="text-xs text-yellow-200 space-y-1">
            <p>generatedScripts: {generatedScripts ? 'SIM' : 'NÃO'}</p>
            <p>Capítulos: {generatedScripts?.chapters?.length || 0}</p>
            <p>Título: {generatedScripts?.title || 'N/A'}</p>
            <p>TTS Segments: {ttsSegments.length}</p>
            <p>Final Audio: {finalTTSAudio ? 'SIM' : 'NÃO'}</p>
            <p>API Keys: {(() => {
              const keys = JSON.parse(localStorage.getItem('api_keys') || '{}')
              return Object.keys(keys).join(', ')
            })()}</p>
            <div className="flex gap-2 mt-2">
              <button
                onClick={() => {
                  console.log('🔍 DEBUG MANUAL:', { generatedScripts, ttsSegments, finalTTSAudio })
                  const saved = localStorage.getItem('generated_scripts')
                  const ttsData = localStorage.getItem('tts_script_data')
                  console.log('🔍 DEBUG localStorage:', {
                    scripts: saved ? JSON.parse(saved) : null,
                    ttsData: ttsData ? JSON.parse(ttsData) : null
                  })
                }}
                className="px-2 py-1 bg-yellow-600 text-white rounded text-xs"
              >
                Debug Console
              </button>
              <button
                onClick={() => {
                  const saved = localStorage.getItem('generated_scripts')
                  const ttsData = localStorage.getItem('tts_script_data')
                  if (saved) {
                    setGeneratedScripts(JSON.parse(saved))
                    console.log('🔄 Dados recarregados do localStorage')
                  } else if (ttsData) {
                    setGeneratedScripts(JSON.parse(ttsData))
                    console.log('🔄 Dados TTS recarregados')
                  }
                }}
                className="px-2 py-1 bg-blue-600 text-white rounded text-xs"
              >
                Recarregar Dados
              </button>
              <button
                onClick={() => {
                  // Redirecionar para configurações
                  window.location.href = '/settings'
                }}
                className="px-2 py-1 bg-green-600 text-white rounded text-xs"
              >
                Configurar APIs
              </button>
              <button
                onClick={async () => {
                  try {
                    const keys = await reloadApiKeys()
                    alert('✅ Chaves sincronizadas com sucesso!')
                    console.log('🔄 Chaves sincronizadas:', keys)
                    // Forçar re-render
                    window.location.reload()
                  } catch (error) {
                    alert('❌ Erro ao sincronizar chaves: ' + error.message)
                    console.error('Erro detalhado:', error)
                  }
                }}
                className="px-2 py-1 bg-purple-600 text-white rounded text-xs"
              >
                Sincronizar Chaves
              </button>
              <button
                onClick={async () => {
                  try {
                    console.log('🔍 Testando rota TTS...')
                    const response = await fetch('/api/automations/generate-tts', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({
                        text: 'teste',
                        api_key: 'AIzaSyBqUjzLHNPycDIzvwnI5JisOwmNubkfRRc',
                        voice_name: 'Aoede'
                      })
                    })
                    console.log('🔍 Status:', response.status)
                    const result = await response.text()
                    console.log('🔍 Resposta:', result)
                    alert(`Status: ${response.status}\nResposta: ${result.substring(0, 200)}`)
                  } catch (error) {
                    console.error('❌ Erro no teste:', error)
                    alert('❌ Erro: ' + error.message)
                  }
                }}
                className="px-2 py-1 bg-yellow-600 text-white rounded text-xs"
              >
                Testar Rota
              </button>
              <button
                onClick={() => {
                  // Solução alternativa: abrir configurações em nova aba e instruir o usuário
                  window.open('/settings', '_blank')
                  alert('📋 INSTRUÇÕES:\n\n1. Configure suas chaves na aba que abriu\n2. Clique "Salvar"\n3. Volte para esta aba\n4. Clique "Recarregar Dados"\n5. Teste novamente')
                }}
                className="px-2 py-1 bg-orange-600 text-white rounded text-xs"
              >
                Abrir Configurações
              </button>
              <button
                onClick={() => {
                  // Forçar criação das chaves conhecidas
                  const knownKeys = {
                    openai: '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',
                    gemini_1: 'AIzaSyBqUjzLHNPycDIzvwnI5JisOwmNubkfRRc',
                    gemini: 'AIzaSyBqUjzLHNPycDIzvwnI5JisOwmNubkfRRc',
                    openrouter: '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',
                    elevenlabs: '',
                    together: '',
                    rapidapi: '77322fda67msh6bbb767e727a6ebp147c75jsn5b47d75dfb80'
                  }
                  localStorage.setItem('api_keys', JSON.stringify(knownKeys))
                  alert('✅ Chaves forçadas! Teste agora.')
                  window.location.reload()
                }}
                className="px-2 py-1 bg-red-600 text-white rounded text-xs"
              >
                Forçar Chaves
              </button>
            </div>
          </div>
        </div>

        {/* Conteúdo Principal */}
        {generatedScripts ? (
          <div className="space-y-6">
            {/* Configurações de TTS */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Configurações */}
              <div className="space-y-4">
                <h4 className="text-lg font-semibold text-white mb-3">⚙️ Configurações de TTS</h4>

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
                          let defaultVoice = 'af_bella' // Inglês padrão
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
                          // Vozes em Português (reais disponíveis no Kokoro)
                          <>
                            <option value="pf_dora">🇵🇹 pf_dora - Feminina Portuguesa</option>
                            <option value="pm_alex">🇵🇹 pm_alex - Masculina Portuguesa</option>
                            <option value="pm_santa">🇵🇹 pm_santa - Masculina Portuguesa (Santa)</option>
                          </>
                        ) : ttsSettings.kokoro.language === 'zh' ? (
                          // Vozes em Chinês
                          <>
                            <option value="zf_xiaobei">🇨🇳 zf_xiaobei - Feminina Chinesa</option>
                            <option value="zf_xiaoni">🇨🇳 zf_xiaoni - Feminina Chinesa</option>
                            <option value="zf_xiaoxiao">🇨🇳 zf_xiaoxiao - Feminina Chinesa</option>
                            <option value="zm_yunjian">🇨🇳 zm_yunjian - Masculina Chinesa</option>
                            <option value="zm_yunxi">🇨🇳 zm_yunxi - Masculina Chinesa</option>
                          </>
                        ) : ttsSettings.kokoro.language === 'ja' ? (
                          // Vozes em Japonês
                          <>
                            <option value="jf_alpha">🇯🇵 jf_alpha - Feminina Japonesa</option>
                            <option value="jf_gongitsune">🇯🇵 jf_gongitsune - Feminina Japonesa</option>
                            <option value="jf_nezumi">🇯🇵 jf_nezumi - Feminina Japonesa</option>
                            <option value="jm_kumo">🇯🇵 jm_kumo - Masculina Japonesa</option>
                          </>
                        ) : (
                          // Vozes em Inglês
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

                    <div className="p-3 bg-green-900/20 border border-green-600 rounded-lg">
                      <div className="flex items-center gap-2 text-green-300 mb-2">
                        <Zap className="w-4 h-4" />
                        <span className="font-semibold">Teste de Conexão</span>
                      </div>
                      <p className="text-sm text-green-200 mb-3">
                        Teste se o servidor Kokoro está rodando e acessível.
                      </p>
                      <button
                        onClick={handleTestKokoroTTS}
                        disabled={apiStatus.kokoro_tts === 'testing'}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                      >
                        {apiStatus.kokoro_tts === 'testing' ? 'Testando...' : 'Testar Conexão'}
                      </button>
                      {apiStatus.kokoro_tts === 'connected' && (
                        <div className="mt-2 text-sm text-green-300">
                          ✅ Conectado com sucesso!
                        </div>
                      )}
                      {apiStatus.kokoro_tts === 'error' && (
                        <div className="mt-2 text-sm text-red-300">
                          ❌ Erro de conexão
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Verificação de API Keys */}
                {(() => {
                  const apiKeys = JSON.parse(localStorage.getItem('api_keys') || '{}')
                  const hasElevenLabs = !!apiKeys.elevenlabs
                  const hasGemini = !!(apiKeys.gemini_1 || apiKeys.gemini)
                  const hasKokoro = true // Kokoro não precisa de chave de API

                  let hasSelectedProviderKey = false
                  if (ttsProvider === 'elevenlabs') {
                    hasSelectedProviderKey = hasElevenLabs
                  } else if (ttsProvider === 'gemini') {
                    hasSelectedProviderKey = hasGemini
                  } else if (ttsProvider === 'kokoro') {
                    hasSelectedProviderKey = hasKokoro
                  }

                  console.log('🔍 Verificação de chaves:', {
                    ttsProvider,
                    hasElevenLabs,
                    hasGemini,
                    hasKokoro,
                    hasSelectedProviderKey,
                    availableKeys: Object.keys(apiKeys),
                    gemini_1: !!apiKeys.gemini_1,
                    gemini: !!apiKeys.gemini,
                    elevenlabs: !!apiKeys.elevenlabs
                  })

                  if (!hasSelectedProviderKey) {
                    return (
                      <div className="p-4 bg-red-900/30 border border-red-600 rounded-lg">
                        <div className="flex items-center gap-3 text-red-300 mb-3">
                          <AlertCircle className="w-5 h-5" />
                          <span className="font-semibold">
                            {ttsProvider === 'elevenlabs' && 'Chave da API ElevenLabs não configurada'}
                            {ttsProvider === 'gemini' && 'Chave da API Gemini não configurada'}
                            {ttsProvider === 'kokoro' && 'Servidor Kokoro não configurado'}
                          </span>
                        </div>
                        <p className="text-sm text-red-200 mb-3">
                          {ttsProvider === 'kokoro'
                            ? 'Para usar o Kokoro TTS, você precisa ter o servidor rodando localmente.'
                            : 'Para usar o TTS, você precisa configurar a chave da API do provedor selecionado.'
                          }
                        </p>
                        <div className="text-xs text-red-300 mb-3 p-2 bg-red-800/30 rounded">
                          <p>Debug: Chaves disponíveis: {Object.keys(apiKeys).join(', ') || 'Nenhuma'}</p>
                          <p>Procurando por: {
                            ttsProvider === 'elevenlabs' ? 'elevenlabs' :
                            ttsProvider === 'gemini' ? 'gemini_1 ou gemini' :
                            'servidor kokoro local'
                          }</p>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => window.location.href = '/settings'}
                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                          >
                            Configurar Chaves
                          </button>
                          <button
                            onClick={async () => {
                              try {
                                await reloadApiKeys()
                                window.location.reload()
                              } catch (error) {
                                alert('Erro ao sincronizar: ' + error.message)
                              }
                            }}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            Sincronizar Chaves
                          </button>
                        </div>
                      </div>
                    )
                  }

                  return (
                    <button
                      onClick={generateTTSAudio}
                      disabled={isGeneratingTTS}
                      className="w-full px-4 py-3 bg-gradient-to-r from-yellow-600 to-orange-600 text-white rounded-lg hover:from-yellow-700 hover:to-orange-700 transition-all flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isGeneratingTTS ? (
                        <>
                          <Loader2 size={18} className="animate-spin" />
                          <span>Gerando Áudio...</span>
                        </>
                      ) : (
                        <>
                          <Mic size={18} />
                          <span>Gerar Áudio TTS</span>
                        </>
                      )}
                    </button>
                  )
                })()}
              </div>

              {/* Áudios Gerados */}
              {generatedAudios.length > 0 && (
                <div className="bg-gray-700 rounded-lg p-4 mb-4">
                  <h4 className="font-medium text-white mb-3">🎵 Áudios Gerados Recentemente</h4>
                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {generatedAudios.map((audio) => (
                      <div key={audio.id} className="bg-gray-800 rounded-lg p-3 border border-gray-600">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <span className="text-blue-400">🎵</span>
                            <span className="text-sm font-medium text-white">{audio.filename}</span>
                            <span className="text-xs text-gray-400">({(audio.size / 1024).toFixed(1)} KB)</span>
                          </div>
                          <span className="text-xs text-gray-400">{audio.timestamp}</span>
                        </div>

                        <div className="text-xs text-gray-300 mb-2">
                          <strong>Voz:</strong> {audio.voice} | <strong>Texto:</strong> {audio.text}
                        </div>

                        <audio
                          controls
                          className="w-full h-8"
                          style={{ filter: 'invert(1) hue-rotate(180deg)' }}
                        >
                          <source src={audio.url} type="audio/wav" />
                          Seu navegador não suporta o elemento de áudio.
                        </audio>
                      </div>
                    ))}
                  </div>

                  <div className="mt-3 flex justify-between items-center">
                    <span className="text-xs text-gray-400">
                      Mostrando {generatedAudios.length} áudio(s) mais recente(s)
                    </span>
                    <button
                      onClick={() => setGeneratedAudios([])}
                      className="text-xs text-red-400 hover:text-red-300 transition-colors"
                    >
                      Limpar Lista
                    </button>
                  </div>
                </div>
              )}

              {/* Preview do Roteiro */}
              <div className="bg-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-white mb-3">📝 Preview do Roteiro</h4>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  <div className="text-sm text-gray-300">
                    <strong>Título:</strong> {generatedScripts.title || 'Sem título'}
                  </div>
                  <div className="text-sm text-gray-300">
                    <strong>Capítulos:</strong> {generatedScripts.chapters?.length || 0}
                  </div>
                  <div className="text-sm text-gray-300">
                    <strong>Palavras totais:</strong> {generatedScripts.total_words || 'N/A'}
                  </div>

                  {generatedScripts.chapters && generatedScripts.chapters.slice(0, 3).map((chapter, index) => (
                    <div key={index} className="bg-gray-600 rounded p-3">
                      <div className="text-sm font-medium text-white mb-1">
                        Capítulo {index + 1}: {chapter.title}
                      </div>
                      <div className="text-xs text-gray-300 line-clamp-3">
                        {chapter.content?.substring(0, 150)}...
                      </div>
                    </div>
                  ))}

                  {generatedScripts.chapters && generatedScripts.chapters.length > 3 && (
                    <div className="text-center text-sm text-gray-400">
                      ... e mais {generatedScripts.chapters.length - 3} capítulos
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Erro de TTS */}
            {ttsError && (
              <div className="flex items-center gap-3 p-4 bg-red-900/30 border border-red-600 rounded-lg text-red-300">
                <AlertCircle className="w-5 h-5" />
                <span>{ttsError}</span>
              </div>
            )}

            {/* Segmentos de Áudio Gerados */}
            {ttsSegments.length > 0 && (
              <div className="space-y-4">
                <div className="p-4 bg-green-900/30 border border-green-600 rounded-lg">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3 text-green-300">
                      <CheckCircle className="w-5 h-5" />
                      <span className="font-semibold">
                        {ttsSegments.length} segmentos gerados com sucesso!
                      </span>
                    </div>

                    {ttsSegments.length > 1 && (
                      <button
                        onClick={joinTTSAudio}
                        disabled={isJoiningAudio}
                        className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
                      >
                        {isJoiningAudio ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Juntando...
                          </>
                        ) : (
                          <>
                            <Download className="w-4 h-4" />
                            Juntar Áudios
                          </>
                        )}
                      </button>
                    )}
                  </div>

                  {/* Lista de Segmentos */}
                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {ttsSegments.map((segment, index) => (
                      <div key={index} className="bg-gray-700 p-3 rounded-lg border border-gray-600">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-sm text-white">
                            Segmento {segment.index}
                          </span>
                          <div className="flex gap-2">
                            <button
                              onClick={() => {
                                const audio = new Audio(`/api/automations/audio/${segment.audio.filename}`)
                                audio.play()
                              }}
                              className="p-1 text-green-400 hover:bg-green-900/30 rounded"
                              title="Reproduzir segmento"
                            >
                              <Play className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => {
                                const link = document.createElement('a')
                                link.href = `/api/automations/download/${segment.audio.filename}`
                                link.download = segment.audio.filename
                                document.body.appendChild(link)
                                link.click()
                                document.body.removeChild(link)
                              }}
                              className="p-1 text-blue-400 hover:bg-blue-900/30 rounded"
                              title="Download segmento"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <div className="text-xs text-gray-400 mb-2">
                          {segment.audio.size ? `${(segment.audio.size / 1024).toFixed(1)} KB` : 'N/A'} • {segment.duration ? `${segment.duration.toFixed(1)}s` : 'N/A'}
                        </div>
                        <div className="text-xs text-gray-500 line-clamp-2">
                          {segment.text.substring(0, 100)}...
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Áudio Final Unificado */}
            {finalTTSAudio && (
              <div className="p-4 bg-purple-900/30 border border-purple-600 rounded-lg">
                <div className="flex items-center gap-3 text-purple-300 mb-4">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-semibold">Áudio final unificado!</span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                  <div className="flex items-center gap-2 text-gray-300">
                    <FileAudio className="w-4 h-4" />
                    <span>{finalTTSAudio.size ? `${(finalTTSAudio.size / 1024 / 1024).toFixed(1)} MB` : 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-300">
                    <Clock className="w-4 h-4" />
                    <span>{finalTTSAudio.duration ? `${Math.floor(finalTTSAudio.duration / 60)}:${Math.floor(finalTTSAudio.duration % 60).toString().padStart(2, '0')}` : 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-300">
                    <User className="w-4 h-4" />
                    <span>{finalTTSAudio.segments_count} segmentos</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-300">
                    <Mic className="w-4 h-4" />
                    <span>{ttsProvider}</span>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      const audio = new Audio(`/api/automations/audio/${finalTTSAudio.filename}`)
                      audio.play()
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    <Play className="w-4 h-4" />
                    Reproduzir Final
                  </button>

                  <button
                    onClick={() => {
                      const link = document.createElement('a')
                      link.href = `/api/automations/download/${finalTTSAudio.filename}`
                      link.download = finalTTSAudio.filename
                      document.body.appendChild(link)
                      link.click()
                      document.body.removeChild(link)
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Download Final
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <Mic size={48} className="mx-auto mb-4 text-gray-500 opacity-50" />
            <h3 className="text-lg font-medium text-white mb-2">🎵 Geração de Áudio TTS</h3>
            <p className="text-gray-400 text-sm mb-4">
              Primeiro você precisa gerar um roteiro para converter em áudio
            </p>
            <div className="text-xs text-gray-500 space-y-1">
              <p>1. 📺 Extraia títulos do YouTube</p>
              <p>2. 🎯 Gere novos títulos</p>
              <p>3. 💡 Crie premissas</p>
              <p>4. 📝 Gere roteiros</p>
              <p>5. 🎵 Converta em áudio</p>
            </div>
            <div className="mt-6 flex justify-center space-x-3">
              <button
                onClick={() => setActiveTab('youtube')}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
              >
                Começar Extração
              </button>
              <button
                onClick={() => setActiveTab('workflow')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm"
              >
                Automação Completa
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )

  // Função para gerar imagens a partir do roteiro
  const handleGenerateImages = async () => {
    // Validações iniciais
    if (imageProvider !== 'pollinations' && !togetherApiKey) {
      setImageGenerationError(`A chave da API do ${imageProvider === 'gemini' ? 'Gemini' : 'Together.ai'} não está configurada. Vá em Configurações e salve sua chave.`)
      return
    }

    let contentToProcess = ''
    
    if (useCustomPrompt && customPrompt.trim()) {
      contentToProcess = customPrompt.trim()
    } else {
      const scriptText = imageGenerationScript?.trim() || (() => {
        if (!generatedScripts) return ''
        if (typeof generatedScripts === 'string') {
          try { return JSON.parse(generatedScripts) } catch { return '' }
        }
        if (generatedScripts?.chapters?.length) {
          return generatedScripts.chapters.map(ch => ch.content).join('\n\n')
        }
        if (generatedScripts?.final_script) return generatedScripts.final_script
        return ''
      })()
      
      if (!scriptText) {
        setImageGenerationError('Não há roteiro disponível para gerar imagens.')
        return
      }
      
      contentToProcess = scriptText
    }

    setIsGeneratingImages(true)
    setImageGenerationError('')
    setGeneratedImages([])
    setImageQueue([])
    setQueueStatus('processing')

    try {
      let prompts = []
      
      if (useAiAgent && !useCustomPrompt) {
        // Usar IA Agent para criar prompts baseados no roteiro
        const agentResponse = await fetch('/api/premise/generate-agent-script', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: 'Geração de Prompts para Imagens',
            premise: contentToProcess,
            custom_prompt: aiAgentPrompt,
            ai_provider: aiAgentProvider || 'openai',
            openrouter_model: 'auto',
            num_chapters: 1,
            api_keys: apiKeys
          })
        })
        
        const agentData = await agentResponse.json()
        if (!agentData.success) {
          throw new Error(agentData.error || 'Falha ao processar roteiro com IA Agent')
        }
        
        // Extrair o conteúdo do script corretamente
        let agentResult = ''
        if (agentData.script && typeof agentData.script === 'object') {
          agentResult = agentData.script.content || ''
        } else if (typeof agentData.script === 'string') {
          agentResult = agentData.script
        } else if (agentData.final_script) {
          agentResult = agentData.final_script
        }
        
        // Verificar se agentResult é uma string antes de usar split
        if (typeof agentResult !== 'string' || !agentResult.trim()) {
          throw new Error('IA Agent não retornou conteúdo de texto válido')
        }
        
        prompts = agentResult.split('\n\n')
          .filter(p => {
            const cleaned = p.trim()
            return cleaned && 
                   cleaned.length > 15 && 
                   !cleaned.match(/^[\s\n\r<>br/]*$/) &&
                   !cleaned.match(/^\*\*[^*]+\*\*:?\s*$/) && // Remove títulos
                   cleaned.split(' ').length > 3 // Mínimo 3 palavras
          })
          .slice(0, imageCount)
        
        if (prompts.length === 0) {
          throw new Error('IA Agent não conseguiu gerar prompts válidos')
        }
      } else {
        // Usar prompt customizado ou dividir roteiro em cenas
        if (useCustomPrompt) {
          prompts = [contentToProcess]
        } else {
          prompts = contentToProcess.split('\n\n')
            .filter(p => {
              const cleaned = p.trim()
              return cleaned && 
                     cleaned.length > 15 && 
                     !cleaned.match(/^[\s\n\r<>br/]*$/) &&
                     !cleaned.match(/^\*\*[^*]+\*\*:?\s*$/) && // Remove títulos
                     cleaned.split(' ').length > 3 // Mínimo 3 palavras
            })
            .slice(0, imageCount)
        }
      }
      
      // Validação final: garantir que temos prompts suficientes
      if (prompts.length < imageCount) {
        const genericPrompt = useAiAgent ? 
          'Uma cena cinematográfica profissional com boa iluminação e composição visual interessante' :
          'Imagem relacionada ao conteúdo do roteiro'
        
        while (prompts.length < imageCount) {
          prompts.push(`${genericPrompt} ${prompts.length + 1}`)
        }
      }
      
      // Adicionar estilo aos prompts se especificado
      if (imageStyle.trim()) {
        prompts = prompts.map(prompt => `${prompt}, ${imageStyle}`)
      }
      
      // Criar fila de imagens
      const queue = prompts.map((prompt, index) => ({
        id: `img_${Date.now()}_${index}`,
        prompt,
        status: 'pending',
        url: null,
        error: null
      }))
      
      setImageQueue(queue)
      
      // Processar fila com delay para respeitar rate limits
      const generatedUrls = []
      const delay = imageProvider === 'pollinations' ? 5000 : 2000 // 5s para Pollinations, 2s para outros
      
      for (let i = 0; i < queue.length; i++) {
        const item = queue[i]
        
        // Atualizar status para processando
        setImageQueue(prev => prev.map(q => 
          q.id === item.id ? { ...q, status: 'processing' } : q
        ))
        
        try {
          const response = await fetch('/api/images/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              script: item.prompt,
              api_key: togetherApiKey,
              style: '',
              provider: imageProvider,
              format: imageFormat,
              quality: imageQuality,
              pollinations_model: pollinationsModel
            })
          })
          
          const data = await response.json()
          
          if (data.success && data.image_urls?.length > 0) {
            const imageUrl = data.image_urls[0]
            generatedUrls.push(imageUrl)
            
            // Atualizar status para concluído
            setImageQueue(prev => prev.map(q => 
              q.id === item.id ? { ...q, status: 'completed', url: imageUrl } : q
            ))
          } else {
            throw new Error(data.error || 'Falha ao gerar imagem')
          }
        } catch (err) {
          // Atualizar status para erro
          setImageQueue(prev => prev.map(q => 
            q.id === item.id ? { ...q, status: 'error', error: err.message } : q
          ))
        }
        
        // Delay entre requisições (exceto na última)
        if (i < queue.length - 1) {
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      }
      
      setGeneratedImages(generatedUrls)
      
      // Salvar imagens no localStorage para uso na criação de vídeos
      if (generatedUrls.length > 0) {
        const existingImages = JSON.parse(localStorage.getItem('generated_images') || '[]')
        const imagesToSave = generatedUrls.map((url, index) => ({
          id: Date.now() + index,
          url: url,
          filename: `imagem_automacao_${Date.now()}_${index + 1}.png`,
          prompt: queue[index]?.prompt?.substring(0, 100) + (queue[index]?.prompt?.length > 100 ? '...' : '') || 'Prompt automático',
          style: imageStyle,
          provider: imageProvider,
          format: imageFormat,
          quality: imageQuality,
          timestamp: new Date().toISOString(),
          source: 'automation',
          size: 'unknown'
        }))
        
        const updatedImages = [...existingImages, ...imagesToSave]
        localStorage.setItem('generated_images', JSON.stringify(updatedImages))
        
        console.log('✅ Imagens da automação salvas no localStorage:', imagesToSave)
      }
      
      setQueueStatus('completed')
      
    } catch (err) {
      setImageGenerationError(err.message)
      setQueueStatus('error')
    } finally {
      setIsGeneratingImages(false)
    }
  }

  // UI da aba de geração de imagens
  const renderImageGeneration = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Image size={24} className="text-purple-400" />
          <span>Geração de Imagens com IA Agent</span>
        </h3>

        {/* Status dos Pré-requisitos */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Roteiros</h4>
              {generatedScripts ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <Clock className="w-5 h-5 text-yellow-400" />
              )}
            </div>
            <p className="text-sm text-gray-400">
              {generatedScripts ? 'Roteiros disponíveis' : 'Gere roteiros primeiro'}
            </p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">API</h4>
              {(imageProvider === 'pollinations' || togetherApiKey) ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <Clock className="w-5 h-5 text-yellow-400" />
              )}
            </div>
            <p className="text-sm text-gray-400">
              {imageProvider === 'pollinations' ? 'Pollinations (gratuito)' : 
               togetherApiKey ? 'API configurada' : 'Configure a chave da API'}
            </p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">IA Agent</h4>
              {useAiAgent ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <Clock className="w-5 h-5 text-yellow-400" />
              )}
            </div>
            <p className="text-sm text-gray-400">
              {useAiAgent ? 'Agent ativo' : 'Agent desativado'}
            </p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Fila</h4>
              {queueStatus === 'completed' ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : queueStatus === 'processing' ? (
                <Loader2 className="w-5 h-5 text-yellow-400 animate-spin" />
              ) : queueStatus === 'error' ? (
                <AlertCircle className="w-5 h-5 text-red-400" />
              ) : (
                <Clock className="w-5 h-5 text-gray-400" />
              )}
            </div>
            <p className="text-sm text-gray-400">
              {queueStatus === 'completed' ? 'Concluída' :
               queueStatus === 'processing' ? 'Processando' :
               queueStatus === 'error' ? 'Erro' : 'Aguardando'}
            </p>
          </div>
        </div>

        {/* Configurações Principais */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Coluna 1: Configurações de Geração */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Provedor de IA
              </label>
              <select
                value={imageProvider}
                onChange={(e) => setImageProvider(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="pollinations">Pollinations.ai (Gratuito)</option>
                <option value="together">Together.ai</option>
                <option value="gemini">Gemini</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Quantidade de Imagens
              </label>
              <input
                type="number"
                min="1"
                max="20"
                value={imageCount}
                onChange={(e) => setImageCount(parseInt(e.target.value) || 1)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Formato da Imagem
              </label>
              <select
                value={imageFormat}
                onChange={(e) => setImageFormat(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="1024x1024">1024x1024 (Quadrado)</option>
                <option value="1920x1080">1920x1080 (16:9)</option>
                <option value="1080x1920">1080x1920 (9:16)</option>
                <option value="1536x1024">1536x1024 (3:2)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Qualidade
              </label>
              <select
                value={imageQuality}
                onChange={(e) => setImageQuality(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="standard">Padrão</option>
                <option value="hd">Alta Definição</option>
              </select>
            </div>
          </div>

          {/* Coluna 2: Configurações de Conteúdo */}
          <div className="space-y-4">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <input
                  type="checkbox"
                  id="useAiAgent"
                  checked={useAiAgent}
                  onChange={(e) => setUseAiAgent(e.target.checked)}
                  className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
                />
                <label htmlFor="useAiAgent" className="text-sm font-medium text-gray-300">
                  Usar IA Agent para criar prompts
                </label>
              </div>
              <p className="text-xs text-gray-500">
                O agent analisará o roteiro e criará prompts específicos para cada cena
              </p>
            </div>

            <div>
              <div className="flex items-center space-x-3 mb-2">
                <input
                  type="checkbox"
                  id="useCustomPrompt"
                  checked={useCustomPrompt}
                  onChange={(e) => setUseCustomPrompt(e.target.checked)}
                  className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
                />
                <label htmlFor="useCustomPrompt" className="text-sm font-medium text-gray-300">
                  Usar prompt personalizado
                </label>
              </div>
              <p className="text-xs text-gray-500">
                Ignore o roteiro e use um prompt específico
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Estilo das Imagens
              </label>
              <textarea
                value={imageStyle}
                onChange={(e) => setImageStyle(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                rows={2}
                placeholder="Ex: cinematic, high detail, 4k, dramatic lighting"
              />
            </div>
          </div>
        </div>

        {/* Prompt Personalizado */}
        {useCustomPrompt && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Prompt Personalizado
            </label>
            <textarea
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              rows={3}
              placeholder="Descreva exatamente a imagem que você quer gerar..."
            />
          </div>
        )}

        {/* Configuração do IA Agent */}
        {useAiAgent && !useCustomPrompt && (
          <div className="mb-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Provedor de IA do Agent
              </label>
              <select
                value={aiAgentProvider}
                onChange={(e) => setAiAgentProvider(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="openai">OpenAI (GPT-4)</option>
                <option value="gemini">Google Gemini</option>
                <option value="openrouter">OpenRouter (Claude)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Prompt do IA Agent
              </label>
              <textarea
                value={aiAgentPrompt}
                onChange={(e) => setAiAgentPrompt(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                rows={4}
                placeholder="Instruções para o IA Agent sobre como criar prompts de imagem..."
              />
            </div>
          </div>
        )}

        {/* Roteiro para Geração */}
        {!useCustomPrompt && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Roteiro para Geração de Imagens
            </label>
            <textarea
              value={imageGenerationScript}
              onChange={(e) => setImageGenerationScript(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              rows={3}
              placeholder="O roteiro será carregado automaticamente dos roteiros gerados"
            />
          </div>
        )}

        {/* Erro */}
        {imageGenerationError && (
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 mb-4">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-400" />
              <span className="text-red-400">{imageGenerationError}</span>
            </div>
          </div>
        )}

        {/* Botões */}
        <div className="flex space-x-4 mb-6">
          <button
            onClick={handleGenerateImages}
            disabled={isGeneratingImages}
            className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
          >
            {isGeneratingImages ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Gerando Imagens...</span>
              </>
            ) : (
              <>
                <Image className="w-5 h-5" />
                <span>Gerar Imagens</span>
              </>
            )}
          </button>

          <button
            onClick={async () => {
              // Recarregar chave Together
              try {
                const resp = await fetch('/api/settings/api-keys/together')
                const data = await resp.json()
                if (data.success && data.api_key) {
                  setTogetherApiKey(data.api_key)
                  alert('✅ Chave Together sincronizada!')
                } else {
                  alert('❌ Não foi possível carregar a chave Together.')
                }
              } catch (e) {
                alert('❌ Erro ao sincronizar chave Together: ' + e.message)
              }
            }}
            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center space-x-2"
          >
            <RefreshCw className="w-5 h-5" />
            <span>Sincronizar Chave</span>
          </button>
        </div>

        {/* Fila de Processamento */}
        {imageQueue.length > 0 && (
          <div className="mb-6">
            <h4 className="text-lg font-medium text-white mb-4 flex items-center space-x-2">
              <Clock className="w-5 h-5 text-blue-400" />
              <span>Fila de Processamento ({imageQueue.length} imagens)</span>
            </h4>
            <div className="space-y-2">
              {imageQueue.map((item, idx) => (
                <div key={item.id} className="bg-gray-700 rounded-lg p-3 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      {item.status === 'pending' && <Clock className="w-4 h-4 text-gray-400" />}
                      {item.status === 'processing' && <Loader2 className="w-4 h-4 text-yellow-400 animate-spin" />}
                      {item.status === 'completed' && <CheckCircle className="w-4 h-4 text-green-400" />}
                      {item.status === 'error' && <AlertCircle className="w-4 h-4 text-red-400" />}
                    </div>
                    <div>
                      <p className="text-sm text-white font-medium">Imagem {idx + 1}</p>
                      <p className="text-xs text-gray-400 truncate max-w-md">{item.prompt}</p>
                      {item.error && <p className="text-xs text-red-400">{item.error}</p>}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 capitalize">
                    {item.status === 'pending' && 'Aguardando'}
                    {item.status === 'processing' && 'Processando'}
                    {item.status === 'completed' && 'Concluída'}
                    {item.status === 'error' && 'Erro'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Imagens Geradas */}
        {generatedImages.length > 0 && (
          <div>
            <h4 className="text-lg font-medium text-white mb-4 flex items-center space-x-2">
              <Image className="w-5 h-5 text-green-400" />
              <span>Imagens Geradas ({generatedImages.length})</span>
              <button
                onClick={() => {
                  generatedImages.forEach((url, idx) => {
                    const link = document.createElement('a')
                    link.href = url
                    link.download = `imagem_${idx + 1}.png`
                    link.click()
                  })
                }}
                className="ml-auto px-3 py-1 bg-emerald-600 text-white text-xs rounded hover:bg-emerald-700 transition-colors"
              >
                Baixar Todas
              </button>
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {generatedImages.map((url, idx) => (
                <div key={idx} className="bg-gray-700 rounded-lg overflow-hidden border border-gray-600">
                  <div className="aspect-square bg-gray-800">
                    <img src={url} alt={`Cena ${idx+1}`} className="w-full h-full object-cover" />
                  </div>
                  <div className="p-3 flex justify-between items-center">
                    <span className="text-sm text-gray-300">Cena {idx+1}</span>
                    <a href={url} download className="text-xs text-emerald-400 hover:text-emerald-300">Baixar</a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {!generatedScripts && (
          <div className="text-center py-12">
            <Image size={48} className="mx-auto mb-4 text-gray-500 opacity-50" />
            <h3 className="text-lg font-medium text-white mb-2">🖼️ Geração de Imagens</h3>
            <p className="text-gray-400 text-sm mb-4">Primeiro gere um roteiro para usar como base das cenas</p>
            <div className="text-xs text-gray-500 space-y-1">
              <p>1. 📺 Extraia títulos do YouTube</p>
              <p>2. 🎯 Gere novos títulos</p>
              <p>3. 💡 Crie premissas</p>
              <p>4. 📝 Gere roteiros</p>
              <p>5. 🖼️ Gere imagens das cenas</p>
            </div>
            <div className="mt-6 flex justify-center space-x-3">
              <button onClick={() => setActiveTab('youtube')} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm">Começar Extração</button>
              <button onClick={() => setActiveTab('workflow')} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm">Automação Completa</button>
            </div>
          </div>
        )}
      </div>
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
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Títulos</h4>
              {generatedTitles && generatedTitles.length > 0 ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <Clock className="w-5 h-5 text-yellow-400" />
              )}
            </div>
            <p className="text-sm text-gray-400">
              {generatedTitles && generatedTitles.length > 0 ? `${generatedTitles.length} títulos` : 'Aguardando'}
            </p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Premissas</h4>
              {generatedPremises && generatedPremises.length > 0 ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <Clock className="w-5 h-5 text-yellow-400" />
              )}
            </div>
            <p className="text-sm text-gray-400">
              {generatedPremises && generatedPremises.length > 0 ? `${generatedPremises.length} premissas` : 'Aguardando'}
            </p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Roteiros</h4>
              {generatedScripts && generatedScripts.chapters && generatedScripts.chapters.length > 0 ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <Clock className="w-5 h-5 text-yellow-400" />
              )}
            </div>
            <p className="text-sm text-gray-400">
              {generatedScripts && generatedScripts.chapters && generatedScripts.chapters.length > 0 ? `${generatedScripts.chapters.length} capítulos` : 'Aguardando'}
            </p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Áudio</h4>
              {(() => {
                const audioFiles = localStorage.getItem('generated_audio_files')
                const hasSessionAudio = (ttsSegments && ttsSegments.length > 0) || finalTTSAudio
                let hasAudio = false
                
                try {
                  if (audioFiles) {
                    const parsedAudio = JSON.parse(audioFiles)
                    hasAudio = Array.isArray(parsedAudio) && parsedAudio.length > 0
                  }
                } catch (e) {
                  console.error('❌ Erro ao fazer parse dos áudios na seção de status:', e)
                }
                
                // Se há áudios na sessão atual, considerar como disponível
                if (hasSessionAudio) {
                  hasAudio = true
                }
                
                return hasAudio ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <Clock className="w-5 h-5 text-yellow-400" />
                )
              })()}
            </div>
            <p className="text-sm text-gray-400">
              {(() => {
                const audioFiles = localStorage.getItem('generated_audio_files')
                const hasSessionAudio = (ttsSegments && ttsSegments.length > 0) || finalTTSAudio
                let audioCount = 0
                
                try {
                  if (audioFiles) {
                    const parsedAudio = JSON.parse(audioFiles)
                    audioCount = Array.isArray(parsedAudio) ? parsedAudio.length : 0
                  }
                } catch (e) {
                  console.error('❌ Erro ao fazer parse dos áudios na seção de status:', e)
                }
                
                // Se há áudios na sessão atual, usar essa contagem
                if (hasSessionAudio) {
                  if (finalTTSAudio) {
                    audioCount = 1 // Áudio final unificado
                  } else if (ttsSegments && ttsSegments.length > 0) {
                    audioCount = ttsSegments.length // Segmentos individuais
                  }
                }
                
                return audioCount > 0 ? `${audioCount} áudios` : 'Aguardando'
              })()}
            </p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-white">Imagens</h4>
              {(() => {
                const imageFiles = localStorage.getItem('generated_images')
                const hasImages = imageFiles && JSON.parse(imageFiles).length > 0
                return hasImages ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <Clock className="w-5 h-5 text-yellow-400" />
                )
              })()}
            </div>
            <p className="text-sm text-gray-400">
              {(() => {
                const imageFiles = localStorage.getItem('generated_images')
                if (imageFiles) {
                  const parsedImages = JSON.parse(imageFiles)
                  return parsedImages.length > 0 ? `${parsedImages.length} imagens` : 'Aguardando'
                }
                return 'Aguardando'
              })()}
            </p>
          </div>
        </div>

        {/* Seção de Geração de Vídeo */}
        {(() => {
          const audioFiles = localStorage.getItem('generated_audio_files')
          const imageFiles = localStorage.getItem('generated_images')
          
          // Debug logs
          console.log('🔍 Debug - audioFiles raw:', audioFiles)
          console.log('🔍 Debug - imageFiles raw:', imageFiles)
          console.log('🔍 Debug - ttsSegments:', ttsSegments)
          console.log('🔍 Debug - finalTTSAudio:', finalTTSAudio)
          
          let hasAudio = false
          let hasImages = false
          
          // Verificar se há áudios gerados na sessão atual
          const hasSessionAudio = (ttsSegments && ttsSegments.length > 0) || finalTTSAudio
          console.log('🔍 Debug - hasSessionAudio:', hasSessionAudio)
          
          try {
            if (audioFiles) {
              const parsedAudio = JSON.parse(audioFiles)
              console.log('🔍 Debug - parsedAudio:', parsedAudio)
              hasAudio = Array.isArray(parsedAudio) && parsedAudio.length > 0
              console.log('🔍 Debug - hasAudio from localStorage:', hasAudio)
            }
          } catch (e) {
            console.error('❌ Erro ao fazer parse dos áudios:', e)
          }
          
          // Se há áudios na sessão atual, considerar como disponível
          if (hasSessionAudio) {
            hasAudio = true
            console.log('🔍 Debug - hasAudio definido como true devido à sessão atual')
          }
          
          try {
            if (imageFiles) {
              const parsedImages = JSON.parse(imageFiles)
              console.log('🔍 Debug - parsedImages:', parsedImages)
              hasImages = Array.isArray(parsedImages) && parsedImages.length > 0
              console.log('🔍 Debug - hasImages:', hasImages)
            }
          } catch (e) {
            console.error('❌ Erro ao fazer parse das imagens:', e)
          }
          
          const hasScripts = generatedScripts && generatedScripts.chapters && generatedScripts.chapters.length > 0
          console.log('🔍 Debug - hasScripts:', hasScripts)
          
          const allReady = hasAudio && hasImages && hasScripts
          console.log('🔍 Debug - allReady:', allReady)
          
          return (
            <div className={`mb-6 p-6 rounded-lg border-2 ${
              allReady 
                ? 'bg-green-900/20 border-green-500' 
                : 'bg-gray-800/50 border-gray-600'
            }`}>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">
                    {allReady ? '🎬 Pronto para Gerar Vídeo!' : '⏳ Aguardando Elementos'}
                  </h3>
                  <p className="text-gray-400">
                    {allReady 
                      ? 'Todos os elementos necessários foram gerados. Você pode configurar e gerar seu vídeo agora.' 
                      : 'Gere roteiros, áudios e imagens antes de criar o vídeo.'}
                  </p>
                </div>
                {allReady && (
                  <button
                    onClick={handleCreateVideo}
                    disabled={isCreatingVideo}
                    className="px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-medium rounded-lg hover:from-pink-600 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {isCreatingVideo ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Gerando...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        Gerar Vídeo
                      </>
                    )}
                  </button>
                )}
              </div>
              
              {/* Checklist de elementos */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className={`flex items-center gap-3 p-3 rounded-lg ${
                  hasScripts ? 'bg-green-900/30' : 'bg-gray-700/50'
                }`}>
                  {hasScripts ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <Clock className="w-5 h-5 text-yellow-400" />
                  )}
                  <span className="text-white font-medium">Roteiros</span>
                  <span className="text-gray-400 text-sm ml-auto">
                    {hasScripts ? `${generatedScripts.chapters.length} prontos` : 'Pendente'}
                  </span>
                </div>
                
                <div className={`flex items-center gap-3 p-3 rounded-lg ${
                  hasAudio ? 'bg-green-900/30' : 'bg-gray-700/50'
                }`}>
                  {hasAudio ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <Clock className="w-5 h-5 text-yellow-400" />
                  )}
                  <span className="text-white font-medium">Áudios</span>
                  <span className="text-gray-400 text-sm ml-auto">
                    {hasAudio ? `${JSON.parse(audioFiles).length} prontos` : 'Pendente'}
                  </span>
                </div>
                
                <div className={`flex items-center gap-3 p-3 rounded-lg ${
                  hasImages ? 'bg-green-900/30' : 'bg-gray-700/50'
                }`}>
                  {hasImages ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <Clock className="w-5 h-5 text-yellow-400" />
                  )}
                  <span className="text-white font-medium">Imagens</span>
                  <span className="text-gray-400 text-sm ml-auto">
                    {hasImages ? `${JSON.parse(imageFiles).length} prontas` : 'Pendente'}
                  </span>
                </div>
              </div>
            </div>
          )
        })()}

        {/* Configurações de Vídeo */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <h4 className="text-lg font-medium text-white mb-3">Configurações de Vídeo</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Resolução
                </label>
                <select 
                  value={videoConfig.resolution}
                  onChange={(e) => updateVideoConfig('resolution', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                >
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
                  FPS (Quadros por Segundo)
                </label>
                <select 
                  value={videoConfig.fps}
                  onChange={(e) => updateVideoConfig('fps', parseInt(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                >
                  <option value={24}>24 FPS (Cinema)</option>
                  <option value={30}>30 FPS (Padrão)</option>
                  <option value={60}>60 FPS (Suave)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Duração da Transição (segundos)
                </label>
                <input 
                  type="number"
                  min="0"
                  max="5"
                  step="0.1"
                  value={videoConfig.transition_duration}
                  onChange={(e) => updateVideoConfig('transition_duration', parseFloat(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                  placeholder="0.5"
                />
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
            onClick={handleCreateVideo}
            disabled={isCreatingVideo}
            className={`px-8 py-3 rounded-lg font-medium flex items-center space-x-2 mx-auto transition-colors ${
              isCreatingVideo
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white'
            }`}
          >
            <Video className="w-5 h-5" />
            <span>{isCreatingVideo ? 'Criando Vídeo...' : 'Gerar Vídeo'}</span>
          </button>
          {isCreatingVideo && videoCreationProgress.stage && (
            <div className="mt-4">
              <p className="text-sm text-gray-400 text-center mb-2">{videoCreationProgress.stage}</p>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-pink-500 to-purple-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${videoCreationProgress.progress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Preview Area */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h4 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
          <Eye className="text-pink-400" />
          <span>Preview do Vídeo</span>
        </h4>

        <div className="bg-gray-900 rounded-lg p-8 text-center">
          {createdVideo ? (
            <div className="space-y-4">
              <div className="w-full max-w-md mx-auto aspect-video bg-gray-700 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <Video size={48} className="text-green-400 mx-auto mb-3" />
                  <p className="text-green-400 font-medium">Vídeo Criado com Sucesso!</p>
                  <p className="text-sm text-gray-400 mt-1">{createdVideo.title}</p>
                </div>
              </div>
              
              <div className="bg-gray-800 rounded-lg p-4 text-left max-w-md mx-auto">
                <h5 className="text-white font-medium mb-2">Informações do Vídeo:</h5>
                <div className="space-y-1 text-sm">
                  <p className="text-gray-300"><span className="text-gray-400">Duração:</span> {createdVideo.duration}s</p>
                  <p className="text-gray-300"><span className="text-gray-400">Resolução:</span> {createdVideo.resolution}</p>
                  <p className="text-gray-300"><span className="text-gray-400">FPS:</span> {createdVideo.fps}</p>
                  <p className="text-gray-300"><span className="text-gray-400">Status:</span> {createdVideo.status}</p>
                  <p className="text-gray-300"><span className="text-gray-400">Arquivo:</span> {createdVideo.file_path}</p>
                </div>
                
                <button 
                  onClick={() => {
                    // Abrir pasta do vídeo ou fazer download
                    window.open(`http://localhost:5000/api/videos/${createdVideo.video_id}/download`, '_blank')
                  }}
                  className="mt-3 w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors"
                >
                  Baixar Vídeo
                </button>
              </div>
            </div>
          ) : (
            <div className="w-full max-w-md mx-auto aspect-video bg-gray-700 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <Video size={48} className="text-gray-500 mx-auto mb-3" />
                <p className="text-gray-400">Preview será exibido aqui</p>
                <p className="text-sm text-gray-500 mt-1">Após gerar o vídeo</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Automações de Conteúdo <span className="text-yellow-400 text-lg">[TESTE - ROTEIROS]</span></h1>
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
          {activeTab === 'tts' && renderTTSGeneration()}
          {activeTab === 'images' && renderImageGeneration()}
          {activeTab === 'video-edit' && renderVideoEditor()}
          {activeTab === 'workflow' && renderCompleteWorkflow()}
          {activeTab === 'api-tests' && renderAPITests()}
          {activeTab !== 'youtube' && activeTab !== 'titles' && activeTab !== 'premise' && activeTab !== 'scripts' && activeTab !== 'tts' && activeTab !== 'video-edit' && activeTab !== 'workflow' && activeTab !== 'api-tests' && (
            <div className="text-center py-12">
              <Target size={48} className="text-purple-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Em desenvolvimento</h3>
              <p className="text-gray-400">Esta funcionalidade será implementada em breve.</p>
            </div>
          )}
        </div>
      </div>

      {/* Modal do Gerenciador de Prompts */}
      {showPromptManager && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-xl font-semibold text-gray-900">📝 Gerenciador de Prompts</h2>
              <button
                onClick={() => setShowPromptManager(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-4 overflow-y-auto max-h-[calc(90vh-80px)]">
              <CustomPromptManager
                onSelectPrompt={handleSelectPrompt}
                showInModal={true}
              />
            </div>
          </div>
        </div>
      )}

      {/* Modal do Gerenciador de Canais */}
      {showChannelsManager && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-xl font-semibold text-gray-900">📺 Gerenciador de Canais</h2>
              <button
                onClick={() => setShowChannelsManager(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-4 overflow-y-auto max-h-[calc(90vh-80px)]">
              <SavedChannelsManager
                onSelectChannel={handleSelectChannel}
                showInModal={true}
              />
            </div>
          </div>
        </div>
      )}

      {/* Modal de Resultados */}
      <AutomationResults
        results={automationResults}
        isVisible={showResults}
        onClose={() => setShowResults(false)}
      />
    </div>
  )
}

export default AutomationsDev
