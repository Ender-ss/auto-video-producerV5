/**
 * 🎬 Pipeline Page
 * 
 * Página de monitoramento do pipeline de produção
 */

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { motion } from 'framer-motion'
import {
  Play,
  Pause,
  Square,
  RefreshCw,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Eye,
  Download,
  Filter,
  Search,
  MoreVertical,
  Zap,
  Activity,
  Settings,
  Youtube,
  Bot,
  Sparkles
} from 'lucide-react'

import ImageGenerationStep from '../components/ImageGenerationStep';
import AutomationCompleteForm from '../components/AutomationCompleteForm';
import PipelineProgress from '../components/PipelineProgress';
import VideoPreview from '../components/VideoPreview';

const Pipeline = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [activePipeline, setActivePipeline] = useState(null)
  const [activeTab, setActiveTab] = useState('automation') // 'monitoring' ou 'automation'
  const [automationPipelines, setAutomationPipelines] = useState([])
  const [isPolling, setIsPolling] = useState(false)

  // Mock data
  const mockPipelines = [
    {
      id: '1',
      title: 'Como Ganhar Dinheiro Online - Método Infalível 2024',
      channel: 'Motivação Viral',
      status: 'generating_audio',
      progress: 75,
      current_step: 'Gerando áudio com ElevenLabs',
      started_at: '2024-01-30T10:30:00',
      estimated_completion: '2024-01-30T11:15:00',
      video_style: 'motivational',
      target_duration: 300,
      logs_count: 12,
      script: 'Roteiro sobre como ganhar dinheiro online...'
    },
    {
      id: '2',
      title: 'Segredos dos Milionários Que Ninguém Te Conta',
      channel: 'Success Stories',
      status: 'generating_images',
      progress: 60,
      current_step: 'Gerando imagens com FLUX',
      started_at: '2024-01-30T10:45:00',
      estimated_completion: '2024-01-30T11:30:00',
      video_style: 'educational',
      target_duration: 420,
      logs_count: 8,
      script: 'Cena 1: Close-up em um gráfico de ações subindo. Narração: Você já se perguntou como os ricos ficam cada vez mais ricos? Cena 2: Uma pessoa sorrindo enquanto usa um laptop em um café. Narração: Não é sorte, é estratégia.'
    },
    {
      id: '3',
      title: 'Transforme Sua Vida em 30 Dias - História Real',
      channel: 'Vida Plena',
      status: 'optimizing',
      progress: 25,
      current_step: 'Otimizando título com Gemini',
      started_at: '2024-01-30T11:00:00',
      estimated_completion: '2024-01-30T11:45:00',
      video_style: 'story',
      target_duration: 360,
      logs_count: 4,
      script: 'Roteiro sobre uma história de transformação de vida...'
    }
  ]

  const getStatusInfo = (status) => {
    const statusMap = {
      'pending': { icon: Clock, color: 'text-gray-400', bg: 'bg-gray-500', label: 'Aguardando' },
      'collecting': { icon: RefreshCw, color: 'text-blue-400', bg: 'bg-blue-500', label: 'Coletando' },
      'optimizing': { icon: Zap, color: 'text-yellow-400', bg: 'bg-yellow-500', label: 'Otimizando' },
      'generating_script': { icon: RefreshCw, color: 'text-purple-400', bg: 'bg-purple-500', label: 'Gerando Roteiro' },
      'generating_audio': { icon: RefreshCw, color: 'text-green-400', bg: 'bg-green-500', label: 'Gerando Áudio' },
      'generating_images': { icon: RefreshCw, color: 'text-pink-400', bg: 'bg-pink-500', label: 'Gerando Imagens' },
      'editing_video': { icon: RefreshCw, color: 'text-red-400', bg: 'bg-red-500', label: 'Editando Vídeo' },
      'completed': { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-500', label: 'Concluído' },
      'failed': { icon: XCircle, color: 'text-red-500', bg: 'bg-red-500', label: 'Falhou' }
    }
    return statusMap[status] || statusMap['pending']
  }

  const formatTime = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Pipeline de Produção</h1>
          <p className="text-gray-400 mt-1">
            Monitore e configure a produção automática de vídeos
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2"
          >
            <RefreshCw size={18} />
            <span>Atualizar</span>
          </button>
          <button 
            onClick={() => setActiveTab('automation')}
            className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-colors flex items-center space-x-2"
          >
            <Bot size={18} />
            <span>Automação Completa</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-800 p-1 rounded-lg border border-gray-700">
        <button
          onClick={() => setActiveTab('monitoring')}
          className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center justify-center space-x-2 ${
            activeTab === 'monitoring'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          <Activity size={16} />
          <span>Monitoramento</span>
        </button>
        <button
          onClick={() => setActiveTab('automation')}
          className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center justify-center space-x-2 ${
            activeTab === 'automation'
              ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
        >
          <Sparkles size={16} />
          <span>Automação Completa</span>
        </button>
      </div>

      {/* Conteúdo baseado na aba ativa */}
      {activeTab === 'monitoring' ? (
        <>
          {/* Queue Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Pipelines Ativos</p>
              <p className="text-2xl font-bold text-white">3</p>
            </div>
            <Zap size={24} className="text-blue-400" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Na Fila</p>
              <p className="text-2xl font-bold text-white">7</p>
            </div>
            <Clock size={24} className="text-yellow-400" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Concluídos Hoje</p>
              <p className="text-2xl font-bold text-white">12</p>
            </div>
            <CheckCircle size={24} className="text-green-400" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Taxa de Sucesso</p>
              <p className="text-2xl font-bold text-white">94%</p>
            </div>
            <Activity size={24} className="text-purple-400" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar pipelines..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-48"
        >
          <option value="all">Todos os Status</option>
          <option value="pending">Aguardando</option>
          <option value="collecting">Coletando</option>
          <option value="optimizing">Otimizando</option>
          <option value="completed">Concluído</option>
          <option value="failed">Falhou</option>
        </select>
      </div>

      {/* Pipelines List */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">Pipelines</h2>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-400">Atualizando em tempo real</span>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {mockPipelines.map((pipeline, index) => {
              const statusInfo = getStatusInfo(pipeline.status)
              const StatusIcon = statusInfo.icon
              
              return (
                <motion.div
                  key={pipeline.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-gray-700 rounded-lg p-6 border border-gray-600 hover:border-gray-500 transition-colors"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      <div className={`p-2 rounded-lg ${statusInfo.bg} bg-opacity-20`}>
                        <StatusIcon size={20} className={statusInfo.color} />
                      </div>
                      <div>
                        <h3 className="font-semibold text-white text-lg">
                          {pipeline.title}
                        </h3>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-gray-400">
                          <span>{pipeline.channel}</span>
                          <span>•</span>
                          <span>{Math.floor(pipeline.target_duration / 60)}min</span>
                          <span>•</span>
                          <span>{formatTime(pipeline.started_at)}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <div className="text-right">
                        <span className={`text-sm font-medium ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                        <p className="text-xs text-gray-500">
                          {pipeline.status === 'completed' ? 'Finalizado' : 
                           pipeline.status === 'failed' ? 'Erro' :
                           'Em andamento'}
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <button className="p-2 rounded-lg hover:bg-gray-600 transition-colors">
                          <Eye size={16} className="text-blue-400" />
                        </button>
                        {pipeline.status === 'completed' && (
                          <button className="p-2 rounded-lg hover:bg-gray-600 transition-colors">
                            <Download size={16} className="text-green-400" />
                          </button>
                        )}
                        <button className="p-2 rounded-lg hover:bg-gray-600 transition-colors">
                          <MoreVertical size={16} className="text-gray-400" />
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  {/* Progress */}
                  <div className="mb-3">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-400">{pipeline.current_step}</span>
                      <span className="text-sm text-gray-400">{pipeline.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-600 rounded-full h-2">
                      <motion.div
                        className={`h-2 rounded-full ${statusInfo.bg}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${pipeline.progress}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                  </div>

                  {/* Etapa de Geração de Imagem */}
                  {pipeline.status === 'generating_images' && (
                    <div className="mt-4">
                      <ImageGenerationStep
                        script={pipeline.script}
                        onComplete={(images) => console.log('Imagens geradas:', images)}
                        onError={(error) => console.error('Erro na geração de imagens:', error)}
                      />
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex items-center justify-between pt-3 border-t border-gray-600">
                    <div className="flex items-center space-x-4 text-sm text-gray-400">
                      <span>{pipeline.logs_count} logs</span>
                      <span>•</span>
                      <span>ID: {pipeline.id}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button className="text-sm text-blue-400 hover:text-blue-300">
                        Ver Logs
                      </button>
                      {pipeline.status !== 'completed' && pipeline.status !== 'failed' && (
                        <button className="text-sm text-red-400 hover:text-red-300">
                          Cancelar
                        </button>
                      )}
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
        </>
      ) : (
        <AutomationSection 
          automationPipelines={automationPipelines}
          setAutomationPipelines={setAutomationPipelines}
          isPolling={isPolling}
          setIsPolling={setIsPolling}
        />
      )}
    </div>
  )
}

// Componente da seção de Automação Completa
const AutomationSection = ({ automationPipelines, setAutomationPipelines, isPolling, setIsPolling }) => {
  const [showForm, setShowForm] = useState(false)
  const [selectedPipeline, setSelectedPipeline] = useState(null)
  const [initialLoadComplete, setInitialLoadComplete] = useState(false)

  // Função para validar se um pipeline é válido
  const isValidPipeline = useCallback((pipeline) => {
    return pipeline && 
           typeof pipeline === 'object' && 
           pipeline.pipeline_id && 
           typeof pipeline.pipeline_id === 'string' && 
           pipeline.pipeline_id.trim() !== '' &&
           pipeline.status &&
           typeof pipeline.status === 'string'
  }, [])

  // Carregar pipelines ativos na inicialização
  useEffect(() => {
    const loadActivePipelines = async () => {
      if (initialLoadComplete) return
      
      try {
        console.log('INIT_LOAD: Carregando pipelines ativos...')
        const response = await fetch('/api/pipeline/active?status=processing,queued,paused,completed,failed&history=true')
        
        if (response.ok) {
          const result = await response.json()
          console.log('INIT_LOAD: Resposta da API:', result)
          
          if (result.success && result.pipelines && Array.isArray(result.pipelines)) {
            const validPipelines = []
            
            // Para cada pipeline encontrado, buscar detalhes completos
            for (const pipeline of result.pipelines) {
              console.log('INIT_LOAD: Processando pipeline:', pipeline)
              if (pipeline.pipeline_id) {
                try {
                  const statusResponse = await fetch(`/api/pipeline/status/${pipeline.pipeline_id}`)
                  if (statusResponse.ok) {
                    const statusResult = await statusResponse.json()
                    console.log('INIT_LOAD: Resposta do status:', statusResult)
                    console.log('INIT_LOAD: Dados do pipeline:', statusResult.data)
                    console.log(`INIT_LOAD: Pipeline ID: ${statusResult.data?.display_name || statusResult.data?.pipeline_id}`)
                    console.log('INIT_LOAD: Pipeline Status:', statusResult.data?.status)
                    console.log('INIT_LOAD: Validação do pipeline:', isValidPipeline(statusResult.data))
                    if (statusResult.success && statusResult.data && isValidPipeline(statusResult.data)) {
        validPipelines.push(statusResult.data)
        console.log(`INIT_LOAD: Pipeline válido carregado: ${statusResult.data.display_name || statusResult.data.pipeline_id}`)
      } else {
        console.log('INIT_LOAD: Pipeline inválido ou dados ausentes')
      }
                  } else {
                    console.log('INIT_LOAD: Erro na resposta do status:', statusResponse.status)
                  }
                } catch (error) {
                  console.error(`INIT_LOAD: Erro ao buscar detalhes do pipeline: ${pipeline.display_name || pipeline.pipeline_id}`, error)
                }
              }
            }
            
            if (validPipelines.length > 0) {
              console.log(`INIT_LOAD: ${validPipelines.length} pipelines ativos encontrados`)
              console.log('INIT_LOAD: Pipelines válidos:', validPipelines)
              setAutomationPipelines(validPipelines)
              setIsPolling(true)
              console.log('INIT_LOAD: Estado atualizado com pipelines:', validPipelines.length)
            } else {
              console.log('INIT_LOAD: Nenhum pipeline ativo encontrado')
            }
          }
        } else {
          console.log('INIT_LOAD: Nenhum pipeline ativo encontrado (resposta não OK)')
        }
      } catch (error) {
        console.error('INIT_LOAD: Erro ao carregar pipelines ativos:', error)
      } finally {
        setInitialLoadComplete(true)
      }
    }
    
    loadActivePipelines()
  }, [initialLoadComplete, setAutomationPipelines, setIsPolling, isValidPipeline])



  // Ref para acessar o estado atual sem criar dependências
  const automationPipelinesRef = useRef(automationPipelines)
  
  // Atualizar ref sempre que o estado mudar
  useEffect(() => {
    automationPipelinesRef.current = automationPipelines
  }, [automationPipelines])
  
  // Função de limpeza com useCallback
  const cleanInvalidPipelinesCallback = useCallback(() => {
    setAutomationPipelines(prev => {
      const validPipelines = prev.filter(pipeline => {
        const isValid = isValidPipeline(pipeline)
        if (!isValid) {
          console.warn('CLEANUP: Removendo pipeline inválido do estado:', pipeline)
        }
        return isValid
      })
      
      if (validPipelines.length !== prev.length) {
        console.log(`CLEANUP: Removidos ${prev.length - validPipelines.length} pipelines inválidos`)
      }
      
      return validPipelines
    })
  }, [setAutomationPipelines, isValidPipeline])
  
  // Polling para atualizar status dos pipelines
  useEffect(() => {
    let interval
    
    if (isPolling) {
      interval = setInterval(async () => {
        try {
          const currentPipelines = automationPipelinesRef.current
          
          if (currentPipelines.length === 0) {
            return
          }
          
          // Limpar pipelines inválidos antes do polling
          cleanInvalidPipelinesCallback()
          
          // Filtrar apenas pipelines válidos e ativos
          const validPipelines = currentPipelines.filter(isValidPipeline)
          const activePipelines = validPipelines.filter(p => 
            !['completed', 'failed', 'cancelled'].includes(p.status)
          )
          
          console.log(`POLLING: Processando ${activePipelines.length} pipelines ativos de ${currentPipelines.length} total`)
          
          for (const pipeline of activePipelines) {
            try {
              console.log(`POLLING: Atualizando status do pipeline: ${pipeline.display_name || pipeline.pipeline_id}`)
              const response = await fetch(`/api/pipeline/status/${pipeline.pipeline_id}`)
              
              if (response.ok) {
                const result = await response.json()
                if (result.success && result.data && isValidPipeline(result.data)) {
                  setAutomationPipelines(prev => 
                    prev.map(p => 
                      p.pipeline_id === pipeline.pipeline_id ? result.data : p
                    )
                  )
                } else {
                  console.warn(`POLLING: Resposta inválida para pipeline: ${pipeline.display_name || pipeline.pipeline_id}`, result)
                }
              } else {
                console.error(`POLLING: Erro HTTP ao buscar status do pipeline: ${pipeline.display_name || pipeline.pipeline_id}`, response.status)
              }
            } catch (pipelineError) {
              console.error(`POLLING: Erro ao processar pipeline: ${pipeline.display_name || pipeline.pipeline_id}`, pipelineError)
            }
          }
        } catch (error) {
          console.error('POLLING: Erro geral no polling:', error)
        }
      }, 3000) // Atualizar a cada 3 segundos
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [isPolling, cleanInvalidPipelinesCallback, setAutomationPipelines])

  const handleStartAutomation = async (config) => {
    try {
      console.log('START_AUTOMATION: Iniciando nova automação com config:', config)
      
      const response = await fetch('/api/pipeline/complete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('START_AUTOMATION: Resposta da API /api/pipeline/complete:', result)
        
        // Validar se a resposta contém pipeline_id válido
        if (!result.pipeline_id || typeof result.pipeline_id !== 'string' || result.pipeline_id.trim() === '') {
          console.error(`START_AUTOMATION: pipeline_id inválido na resposta: ${result.display_name || result.pipeline_id}`, result)
          alert('Erro: Pipeline criado sem ID válido')
          return
        }
        
        console.log(`START_AUTOMATION: Buscando status completo do pipeline: ${result.display_name || result.pipeline_id})`)
        
        // Buscar o pipeline completo
        const statusResponse = await fetch(`/api/pipeline/status/${result.pipeline_id}`)
        if (statusResponse.ok) {
          const statusResult = await statusResponse.json()
          console.log('START_AUTOMATION: Resposta do status:', statusResult)
          
          // Validar pipeline completo antes de adicionar ao estado
          if (statusResult.success && statusResult.data && isValidPipeline(statusResult.data)) {
            console.log(`START_AUTOMATION: Pipeline válido, adicionando ao estado: ${statusResult.data.display_name || statusResult.data.pipeline_id}`)
            
            // Verificar se o pipeline já existe no estado (evitar duplicatas)
            setAutomationPipelines(prev => {
              const exists = prev.some(p => p.pipeline_id === statusResult.data.pipeline_id)
              if (exists) {
                console.warn(`START_AUTOMATION: Pipeline já existe no estado, atualizando: ${statusResult.data.display_name || statusResult.data.pipeline_id}`)
                return prev.map(p => 
                  p.pipeline_id === statusResult.data.pipeline_id ? statusResult.data : p
                )
              } else {
                console.log(`START_AUTOMATION: Adicionando novo pipeline ao estado: ${statusResult.data.display_name || statusResult.data.pipeline_id}`)
                return [...prev, statusResult.data]
              }
            })
            
            setIsPolling(true)
            setShowForm(false)
            console.log('START_AUTOMATION: Automação iniciada com sucesso')
          } else {
            console.error('START_AUTOMATION: Dados do pipeline inválidos:', statusResult)
            alert('Erro: Dados do pipeline são inválidos')
          }
        } else {
          console.error('START_AUTOMATION: Erro ao buscar status do pipeline:', statusResponse.status)
          alert(`Erro ao buscar status do pipeline: ${statusResponse.status}`)
        }
      } else {
        const error = await response.json()
        const errorMessage = error.error || error.message || 'Erro desconhecido'
        console.error('START_AUTOMATION: Erro na API:', errorMessage)
        alert(`Erro ao iniciar automação: ${errorMessage}`)
      }
    } catch (error) {
      console.error('START_AUTOMATION: Erro geral:', error)
      alert('Erro ao conectar com o servidor')
    }
  }

  const handlePausePipeline = async (pipelineId) => {
    try {
      // Encontrar o pipeline atual no estado para obter o display_name
      const currentPipeline = automationPipelines.find(p => p.pipeline_id === pipelineId)
      const displayName = currentPipeline?.display_name || pipelineId
      
      // Validar pipeline_id antes da requisição
      if (!pipelineId || typeof pipelineId !== 'string' || pipelineId.trim() === '') {
        console.error('PAUSE_PIPELINE: pipeline_id inválido:', displayName)
        alert('Erro: ID do pipeline inválido')
        return
      }
      
      if (!currentPipeline) {
        console.error('PAUSE_PIPELINE: Pipeline não encontrado:', displayName)
        alert('Erro: Pipeline não encontrado')
        return
      }
      
      const isPaused = currentPipeline.status === 'paused'
      const action = isPaused ? 'resume' : 'pause'
      const actionText = isPaused ? 'Retomando' : 'Pausando'
      
      console.log(`${action.toUpperCase()}_PIPELINE: ${actionText} pipeline: ${displayName}`)
      
      const response = await fetch(`/api/pipeline/${action}/${pipelineId}`, {
        method: 'POST'
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log(`${action.toUpperCase()}_PIPELINE: Resposta da API:`, result)
        
        if (result.success) {
          // Atualizar status do pipeline localmente
          setAutomationPipelines(prev => 
            prev.map(p => 
              p.pipeline_id === pipelineId 
                ? { ...p, status: isPaused ? 'running' : 'paused' }
                : p
            )
          )
          console.log(`${action.toUpperCase()}_PIPELINE: Pipeline ${isPaused ? 'retomado' : 'pausado'} com sucesso: ${displayName}`)
        } else {
          console.error(`${action.toUpperCase()}_PIPELINE: Erro na resposta:`, result.error)
          alert(`Erro ao ${isPaused ? 'retomar' : 'pausar'} pipeline: ${result.error}`)
        }
      } else {
        console.error(`${action.toUpperCase()}_PIPELINE: Erro HTTP:`, response.status)
        alert(`Erro HTTP ao ${isPaused ? 'retomar' : 'pausar'} pipeline`)
      }
    } catch (error) {
      console.error('PAUSE_PIPELINE: Erro geral:', error)
      alert('Erro inesperado ao processar pipeline')
    }
  }

  const handleCancelPipeline = async (pipelineId) => {
    try {
      // Encontrar o pipeline atual no estado para obter o display_name
      const currentPipeline = automationPipelines.find(p => p.pipeline_id === pipelineId)
      const displayName = currentPipeline?.display_name || pipelineId
      
      // Validar pipeline_id antes da requisição
      if (!pipelineId || typeof pipelineId !== 'string' || pipelineId.trim() === '') {
        console.error('CANCEL_PIPELINE: pipeline_id inválido:', displayName)
        alert('Erro: ID do pipeline inválido')
        return
      }
      
      console.log('CANCEL_PIPELINE: Cancelando pipeline:', displayName)
      
      const response = await fetch(`/api/pipeline/cancel/${pipelineId}`, {
        method: 'POST'
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('CANCEL_PIPELINE: Resposta da API:', result)
        
        if (result.success && result.data && isValidPipeline(result.data)) {
          setAutomationPipelines(prev => 
            prev.map(p => 
              p.pipeline_id === pipelineId ? result.data : p
            )
          )
          console.log('CANCEL_PIPELINE: Pipeline cancelado com sucesso:', displayName)
        } else {
          console.error('CANCEL_PIPELINE: Dados inválidos na resposta:', result)
        }
      } else {
        console.error('CANCEL_PIPELINE: Erro HTTP:', response.status)
      }
    } catch (error) {
      console.error('CANCEL_PIPELINE: Erro geral:', error)
    }
  }

  const handleClearTestPipelines = async () => {
    try {
      // Confirmar ação com o usuário
      const confirmed = window.confirm(
        'Tem certeza que deseja limpar todas as pipelines de teste em aguardo?\n\n' +
        'Esta ação cancelará pipelines que contenham as palavras: teste, test, exemplo, demo, ou que não tenham título.'
      )
      
      if (!confirmed) {
        return
      }
      
      console.log('CLEAR_TEST_PIPELINES: Limpando pipelines de teste...')
      
      const response = await fetch('/api/pipeline/clear-test-pipelines', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('CLEAR_TEST_PIPELINES: Resposta da API:', result)
        
        if (result.success) {
          const { cancelled_count, remaining_pending, cancelled_pipelines } = result.data
          
          // Remover pipelines canceladas do estado local
          if (cancelled_pipelines && cancelled_pipelines.length > 0) {
            const cancelledIds = cancelled_pipelines.map(p => p.pipeline_id)
            setAutomationPipelines(prev => 
              prev.filter(p => !cancelledIds.includes(p.pipeline_id))
            )
          }
          
          // Mostrar mensagem de sucesso
          const message = cancelled_count > 0 
            ? `✅ ${cancelled_count} pipelines de teste foram canceladas com sucesso!\n\n📊 Pipelines restantes em aguardo: ${remaining_pending}`
            : '✅ Nenhuma pipeline de teste encontrada para cancelar.'
          
          alert(message)
          console.log('CLEAR_TEST_PIPELINES: Limpeza concluída com sucesso')
        } else {
          console.error('CLEAR_TEST_PIPELINES: Erro na resposta:', result.error)
          alert(`Erro ao limpar pipelines de teste: ${result.error}`)
        }
      } else {
        console.error('CLEAR_TEST_PIPELINES: Erro HTTP:', response.status)
        alert(`Erro HTTP ao limpar pipelines: ${response.status}`)
      }
    } catch (error) {
      console.error('CLEAR_TEST_PIPELINES: Erro geral:', error)
      alert('Erro ao conectar com o servidor')
    }
  }

  // useEffect para limpeza automática de pipelines inválidos
  useEffect(() => {
    if (automationPipelines.length > 0) {
      const invalidPipelines = automationPipelines.filter(p => !isValidPipeline(p))
      if (invalidPipelines.length > 0) {
        console.warn('AUTO_CLEANUP: Encontrados pipelines inválidos, executando limpeza automática')
        cleanInvalidPipelinesCallback()
      }
    }
  }, [automationPipelines, cleanInvalidPipelinesCallback, isValidPipeline])

  return (
    <div className="space-y-6">
      {/* Header da Automação */}
      <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 rounded-lg p-6 border border-purple-500/30">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center space-x-3">
              <Bot size={28} className="text-purple-400" />
              <span>Automação Completa</span>
            </h2>
            <p className="text-gray-300 mt-2">
              Configure e execute o pipeline completo: YouTube → Títulos → Premissas → Roteiros → TTS → Imagens → Vídeo Final
            </p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-colors flex items-center space-x-2 font-medium"
          >
            <Sparkles size={20} />
            <span>Nova Automação</span>
          </button>
        </div>
      </div>

      {/* Estatísticas da Automação */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Automações Ativas</p>
              <p className="text-2xl font-bold text-white">
                {automationPipelines.filter(p => !['completed', 'failed', 'cancelled'].includes(p.status)).length}
              </p>
            </div>
            <Bot size={24} className="text-purple-400" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Concluídas</p>
              <p className="text-2xl font-bold text-white">
                {automationPipelines.filter(p => p.status === 'completed').length}
              </p>
            </div>
            <CheckCircle size={24} className="text-green-400" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Com Erro</p>
              <p className="text-2xl font-bold text-white">
                {automationPipelines.filter(p => p.status === 'failed').length}
              </p>
            </div>
            <XCircle size={24} className="text-red-400" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Tempo Médio</p>
              <p className="text-2xl font-bold text-white">45min</p>
            </div>
            <Clock size={24} className="text-blue-400" />
          </div>
        </div>
      </div>

      {/* Botões de Ação */}
      <div className="flex items-center justify-between bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-semibold text-white">Gerenciamento</h3>
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <span>
              {automationPipelines.filter(p => ['queued', 'processing', 'paused'].includes(p.status)).length} em aguardo
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleClearTestPipelines}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center space-x-2 text-sm font-medium"
            title="Limpar pipelines de teste em aguardo"
          >
            <XCircle size={16} />
            <span>Limpar Testes</span>
          </button>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg transition-colors flex items-center space-x-2 text-sm"
          >
            <RefreshCw size={16} />
            <span>Atualizar</span>
          </button>
        </div>
      </div>

      {/* Lista de Automações */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold text-white">Automações em Execução</h3>
            {isPolling && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-400">Atualizando em tempo real</span>
              </div>
            )}
          </div>
        </div>
        <div className="p-6">
          {automationPipelines.length === 0 ? (
            <div className="text-center py-12">
              <Bot size={48} className="text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-400 mb-2">Nenhuma automação em execução</h3>
              <p className="text-gray-500 mb-6">Inicie uma nova automação completa para começar</p>
              <button
                onClick={() => setShowForm(true)}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-colors flex items-center space-x-2 mx-auto"
              >
                <Sparkles size={20} />
                <span>Iniciar Primeira Automação</span>
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {automationPipelines
                .filter(pipeline => pipeline.pipeline_id) // Filtrar apenas pipelines com ID válido
                .map((pipeline, index) => (
                  <PipelineProgress
                    key={pipeline.pipeline_id}
                    pipeline={pipeline}
                    onPause={() => handlePausePipeline(pipeline.pipeline_id)}
                    onCancel={() => handleCancelPipeline(pipeline.pipeline_id)}
                    onViewDetails={() => setSelectedPipeline(pipeline)}
                    index={index}
                  />
                ))}
            </div>
          )}
        </div>
      </div>

      {/* Modal do Formulário */}
      {showForm && (
        <AutomationCompleteForm
          onSubmit={handleStartAutomation}
          onClose={() => setShowForm(false)}
        />
      )}

      {/* Modal de Detalhes do Pipeline */}
      {selectedPipeline && (
        <VideoPreview
          pipeline={selectedPipeline}
          onClose={() => setSelectedPipeline(null)}
        />
      )}
    </div>
  )
}

export default Pipeline
