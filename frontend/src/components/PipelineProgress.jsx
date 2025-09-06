import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Play,
  Pause,
  Square,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Eye,
  Download,
  MoreVertical,
  Youtube,
  FileText,
  Mic,
  Image,
  Video,
  Loader,
  ChevronDown,
  ChevronUp,
  Activity
} from 'lucide-react'

import PromptSourceIndicator from './PromptSourceIndicator'

// Componente auxiliar para seções de conteúdo
const ContentSection = ({ title, icon, content, downloadData, filename }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  const downloadContent = () => {
    if (!downloadData) return
    
    const blob = new Blob([downloadData], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename || 'content.txt'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="border border-gray-600 rounded">
      <div className="flex items-center justify-between p-3 bg-gray-700">
        <div className="flex items-center space-x-2">
          {icon}
          <span className="font-medium text-white">{title}</span>
        </div>
        <div className="flex items-center space-x-2">
          {downloadData && (
            <button
              onClick={downloadContent}
              className="text-gray-400 hover:text-blue-400 transition-colors"
              title="Baixar conteúdo"
            >
              <Download size={14} />
            </button>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>
      {isExpanded && (
        <div className="p-3">
          {content}
        </div>
      )}
    </div>
  )
}

// Função auxiliar para formatar tamanho de arquivo
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Função auxiliar para baixar todos os conteúdos
 const downloadAllContent = (pipeline) => {
   if (!pipeline.results) return
   
   let content = `Pipeline #${pipeline.display_name || pipeline.pipeline_id?.slice(-8) || 'Unknown'}\n`
   content += `Status: ${pipeline.status}\n`
   content += `Iniciado em: ${new Date(pipeline.started_at).toLocaleString()}\n\n`
   
   if (pipeline.results.titles?.generated_titles) {
     content += '=== TÍTULOS GERADOS ===\n'
     pipeline.results.titles.generated_titles.forEach((title, idx) => {
       content += `${idx + 1}. ${title}\n`
     })
     content += '\n'
   }
   
   if (pipeline.results.premises?.premise) {
     content += '=== PREMISSA ===\n'
     content += pipeline.results.premises.premise + '\n\n'
   }
   
   if (pipeline.results.scripts?.script) {
     content += '=== ROTEIRO ===\n'
     content += pipeline.results.scripts.script + '\n\n'
   }
   
   const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
   const url = URL.createObjectURL(blob)
   const link = document.createElement('a')
   link.href = url
   link.download = `pipeline_${pipeline.display_name || pipeline.pipeline_id?.slice(-8) || 'content'}.txt`
   document.body.appendChild(link)
   link.click()
   document.body.removeChild(link)
   URL.revokeObjectURL(url)
 }
 
 // Função auxiliar para obter ícone da etapa
  const getStepIcon = (stepId) => {
    switch (stepId) {
      case 'extraction':
        return <FileText size={16} className="text-blue-400" />
      case 'titles':
        return <FileText size={16} className="text-purple-400" />
      case 'premises':
        return <FileText size={16} className="text-indigo-400" />
      case 'scripts':
        return <FileText size={16} className="text-green-400" />
      case 'images':
        return <Image size={16} className="text-pink-400" />
      case 'tts':
        return <Mic size={16} className="text-yellow-400" />
      case 'video':
        return <Video size={16} className="text-red-400" />
      case 'cleanup':
        return <CheckCircle size={16} className="text-gray-400" />
      default:
        return <Clock size={16} className="text-gray-400" />
    }
  }
  
  // Função para baixar todas as imagens
  const downloadAllImages = async (images, pipeline) => {
    if (!images || images.length === 0) return
    
    for (let i = 0; i < images.length; i++) {
      const img = images[i]
      if (img.url) {
        try {
          const response = await fetch(img.url)
          const blob = await response.blob()
          const url = URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `imagem_${i + 1}_${pipeline?.display_name || pipeline?.pipeline_id?.slice(-8) || 'pipeline'}.jpg`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          URL.revokeObjectURL(url)
          
          // Pequeno delay entre downloads
          await new Promise(resolve => setTimeout(resolve, 500))
        } catch (error) {
          console.error(`Erro ao baixar imagem ${i + 1}:`, error)
        }
      }
    }
  }
  
  // Função para abrir modal de imagem
  const openImageModal = (imageUrl, title) => {
    const modal = document.createElement('div')
    modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4'
    modal.onclick = () => document.body.removeChild(modal)
    
    const content = document.createElement('div')
    content.className = 'relative max-w-4xl max-h-full'
    content.onclick = (e) => e.stopPropagation()
    
    const img = document.createElement('img')
    img.src = imageUrl
    img.alt = title
    img.className = 'max-w-full max-h-full object-contain rounded'
    
    const closeBtn = document.createElement('button')
    closeBtn.innerHTML = '×'
    closeBtn.className = 'absolute top-2 right-2 text-white bg-black bg-opacity-50 rounded-full w-8 h-8 flex items-center justify-center text-xl font-bold hover:bg-opacity-75'
    closeBtn.onclick = () => document.body.removeChild(modal)
    
    const titleEl = document.createElement('div')
    titleEl.textContent = title
    titleEl.className = 'absolute bottom-2 left-2 text-white bg-black bg-opacity-50 px-2 py-1 rounded text-sm'
    
    content.appendChild(img)
    content.appendChild(closeBtn)
    content.appendChild(titleEl)
    modal.appendChild(content)
    document.body.appendChild(modal)
  }

const PipelineProgress = ({ pipeline, onPause, onCancel, onViewDetails, index }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [showLogs, setShowLogs] = useState(false)

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
      case 'processing':
        return <Loader size={16} className="text-blue-400 animate-spin" />
      case 'paused':
        return <Pause size={16} className="text-yellow-400" />
      case 'completed':
        return <CheckCircle size={16} className="text-green-400" />
      case 'failed':
        return <XCircle size={16} className="text-red-400" />
      case 'cancelled':
        return <Square size={16} className="text-gray-400" />
      default:
        return <Clock size={16} className="text-gray-400" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
      case 'processing':
        return 'text-blue-400'
      case 'paused':
        return 'text-yellow-400'
      case 'completed':
        return 'text-green-400'
      case 'failed':
        return 'text-red-400'
      case 'cancelled':
        return 'text-gray-400'
      default:
        return 'text-gray-400'
    }
  }

  const getStepIcon = (step) => {
    switch (step) {
      case 'extraction':
        return <Youtube size={16} className="text-red-400" />
      case 'titles':
      case 'premises':
      case 'scripts':
        return <FileText size={16} className="text-blue-400" />
      case 'script_processing':
        return <Activity size={16} className="text-orange-400" />
      case 'tts':
        return <Mic size={16} className="text-green-400" />
      case 'images':
        return <Image size={16} className="text-pink-400" />
      case 'video':
        return <Video size={16} className="text-purple-400" />
      default:
        return <Activity size={16} className="text-gray-400" />
    }
  }

  const formatDuration = (seconds) => {
    if (!seconds) return '0s'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`
    } else {
      return `${secs}s`
    }
  }

  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return 'Agora'
    const now = new Date()
    const time = new Date(timestamp)
    const diffInSeconds = Math.floor((now - time) / 1000)
    
    if (diffInSeconds < 60) {
      return `${diffInSeconds}s atrás`
    } else if (diffInSeconds < 3600) {
      return `${Math.floor(diffInSeconds / 60)}m atrás`
    } else {
      return `${Math.floor(diffInSeconds / 3600)}h atrás`
    }
  }

  const steps = [
    { id: 'extraction', label: 'Extração', description: 'Extraindo vídeos do canal' },
    { id: 'titles', label: 'Títulos', description: 'Gerando novos títulos' },
    { id: 'premises', label: 'Premissas', description: 'Criando premissas' },
    { id: 'scripts', label: 'Roteiros', description: 'Escrevendo roteiros' },
    { id: 'script_processing', label: 'Processamento', description: 'Processando e otimizando roteiro' },
    { id: 'tts', label: 'TTS', description: 'Gerando áudio' },
    { id: 'images', label: 'Imagens', description: 'Criando imagens' },
    { id: 'video', label: 'Vídeo', description: 'Montando vídeo final' }
  ]

  const currentStepIndex = steps.findIndex(step => step.id === pipeline.current_step)
  const progress = pipeline.progress || 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden"
    >
      {/* Header */}
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getStatusIcon(pipeline.status)}
            <div>
              <h4 className="text-white font-medium">
                Pipeline #{pipeline.display_name || pipeline.pipeline_id?.slice(-8) || 'Unknown'}
              </h4>
              <p className="text-sm text-gray-400">
                Iniciado {formatTimeAgo(pipeline.started_at)}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className={`text-sm font-medium ${getStatusColor(pipeline.status)}`}>
              {(pipeline.status === 'running' || pipeline.status === 'processing') ? 'Executando' :
             pipeline.status === 'paused' ? 'Pausado' :
             pipeline.status === 'completed' ? 'Concluído' :
             pipeline.status === 'failed' ? 'Falhou' :
             pipeline.status === 'cancelled' ? 'Cancelado' : 'Aguardando'}
            </span>
            
            {/* Actions */}
            <div className="flex items-center space-x-1">
              {(pipeline.status === 'running' || pipeline.status === 'processing') && (
                <button
                  onClick={() => onPause(pipeline.pipeline_id)}
                  className="p-2 text-gray-400 hover:text-yellow-400 hover:bg-gray-700 rounded transition-colors"
                  title="Pausar"
                >
                  <Pause size={16} />
                </button>
              )}
              
              {pipeline.status === 'paused' && (
                <button
                  onClick={() => onPause(pipeline.pipeline_id)}
                  className="p-2 text-gray-400 hover:text-blue-400 hover:bg-gray-700 rounded transition-colors"
                  title="Retomar"
                >
                  <Play size={16} />
                </button>
              )}
              
              {['running', 'processing', 'paused'].includes(pipeline.status) && (
                <button
                  onClick={() => onCancel(pipeline.pipeline_id)}
                  className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded transition-colors"
                  title="Cancelar"
                >
                  <Square size={16} />
                </button>
              )}
              
              {pipeline.status === 'completed' && (
                <>
                  <button
                    onClick={() => onViewDetails(pipeline)}
                    className="p-2 text-gray-400 hover:text-blue-400 hover:bg-gray-700 rounded transition-colors"
                    title="Visualizar"
                  >
                    <Eye size={16} />
                  </button>
                  <button
                    className="p-2 text-gray-400 hover:text-green-400 hover:bg-gray-700 rounded transition-colors"
                    title="Download"
                  >
                    <Download size={16} />
                  </button>
                </>
              )}
              
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
                title={isExpanded ? 'Recolher' : 'Expandir'}
              >
                {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </button>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">
              {pipeline.current_step ? (
                <span className="flex items-center space-x-2">
                  {getStepIcon(pipeline.current_step)}
                  <span>
                    {steps.find(s => s.id === pipeline.current_step)?.label || pipeline.current_step}
                  </span>
                </span>
              ) : (
                'Aguardando'
              )}
            </span>
            <span className="text-sm text-gray-400">
              {Math.round(progress)}%
            </span>
          </div>
          
          <div className="w-full bg-gray-700 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        {/* Time Info */}
        <div className="flex items-center justify-between mt-3 text-sm text-gray-400">
          <span className="flex items-center space-x-1">
            <Clock size={14} />
            <span>
              Tempo decorrido: {formatDuration(pipeline.elapsed_time || 0)}
            </span>
          </span>
          {pipeline.estimated_completion && (
            <span>
              ETA: {formatDuration(pipeline.estimated_completion)}
            </span>
          )}
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="border-t border-gray-700"
        >
          {/* Steps Progress */}
          <div className="p-4">
            <h5 className="text-white font-medium mb-3">Progresso das Etapas</h5>
            <div className="space-y-3">
              {steps.map((step, stepIndex) => {
                const isCompleted = stepIndex < currentStepIndex
                const isCurrent = stepIndex === currentStepIndex
                const isPending = stepIndex > currentStepIndex
                
                return (
                  <div key={step.id} className="flex items-center space-x-3">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      isCompleted ? 'bg-green-500' :
                      isCurrent ? 'bg-blue-500' :
                      'bg-gray-600'
                    }`}>
                      {isCompleted ? (
                        <CheckCircle size={16} className="text-white" />
                      ) : isCurrent ? (
                        <Loader size={16} className="text-white animate-spin" />
                      ) : (
                        getStepIcon(step.id)
                      )}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className={`font-medium ${
                          isCompleted ? 'text-green-400' :
                          isCurrent ? 'text-blue-400' :
                          'text-gray-400'
                        }`}>
                          {step.label}
                        </span>
                        {isCurrent && (
                          <span className="text-xs text-blue-400">
                            {Math.round(progress)}%
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500">
                        {step.description}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Configuration Summary */}
          {pipeline.config && (
            <div className="p-4 border-t border-gray-700">
              <h5 className="text-white font-medium mb-3">Configuração</h5>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Canal:</span>
                  <p className="text-white truncate">
                    {pipeline.results?.extraction?.channel_info?.name || pipeline.channel_url?.split('/').pop() || 'N/A'}
                  </p>
                </div>
                <div>
                  <span className="text-gray-400">Vídeos:</span>
                  <p className="text-white">
                    {pipeline.video_count || 'N/A'}
                  </p>
                </div>
                <div>
                  <span className="text-gray-400">IA:</span>
                  <p className="text-white">
                    {pipeline.config.titles?.provider || 'N/A'}
                  </p>
                </div>
                <div>
                  <span className="text-gray-400">TTS:</span>
                  <p className="text-white">
                    {pipeline.config.tts?.provider || 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Logs Section */}
          <div className="p-4 border-t border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <h5 className="text-white font-medium">Logs do Processo</h5>
              <button
                onClick={() => setShowLogs(!showLogs)}
                className="text-sm text-blue-400 hover:text-blue-300"
              >
                {showLogs ? 'Ocultar' : 'Mostrar'} logs
              </button>
            </div>
            
            {showLogs && (
              <div className="space-y-3">
                {/* Process Status Logs */}
                <div className="bg-gray-800 rounded p-3">
                  <h6 className="text-green-400 font-medium mb-2 flex items-center">
                    <CheckCircle size={16} className="mr-2" />
                    Status dos Processos
                  </h6>
                  <div className="space-y-2 text-sm">
                    {steps.map((step, idx) => {
                      const isCompleted = idx < currentStepIndex
                      const isCurrent = idx === currentStepIndex
                      const isPending = idx > currentStepIndex
                      
                      return (
                        <div key={step.id} className={`flex items-center justify-between p-2 rounded bg-gray-900`}>
                          <div className="flex items-center space-x-2">
                            {isCompleted ? (
                              <CheckCircle size={16} className="text-green-400" />
                            ) : isCurrent ? (
                              <Loader size={16} className="text-blue-400 animate-spin" />
                            ) : (
                              getStepIcon(step.id)
                            )}
                            <span className={`font-medium capitalize ${
                              isCompleted ? 'text-green-400' :
                              isCurrent ? 'text-blue-400' :
                              'text-gray-400'
                            }`}>{step.label}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            {isCurrent && (
                              <span className="text-xs text-blue-400">{Math.round(progress)}%</span>
                            )}
                            <span className="text-gray-400 text-xs max-w-xs truncate">
                              {step.description}
                            </span>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
                
                {/* Generation Details */}
                <div className="bg-gray-800 rounded p-3">
                  <h6 className="text-purple-400 font-medium mb-2 flex items-center">
                    <FileText size={16} className="mr-2" />
                    Detalhes da Geração
                  </h6>
                  <div className="space-y-2 text-sm">
                    {pipeline.results?.titles && (
                      <div className="text-green-400">
                        ✓ {pipeline.results.titles.generated_titles?.length || 0} títulos gerados
                      </div>
                    )}
                    {pipeline.results?.premises && (
                      <div className="text-green-400">
                        ✓ Premissa criada ({pipeline.results.premises.premise?.length || 0} caracteres)
                      </div>
                    )}
                    {pipeline.results?.scripts && (
                      <div className="text-green-400">
                        ✓ Roteiro gerado ({pipeline.results.scripts.script?.length || 0} caracteres)
                      </div>
                    )}
                    {pipeline.results?.tts && (
                      <div className="text-green-400">
                        ✓ Áudio TTS gerado ({formatDuration(pipeline.results.tts.duration || 0)})
                      </div>
                    )}
                    {pipeline.results?.images && (
                      <div className="text-green-400">
                        ✓ {pipeline.results.images.total_images || 0} imagens geradas
                      </div>
                    )}
                    {pipeline.results?.video && (
                      <div className="text-green-400">
                        ✓ Vídeo final criado ({formatFileSize(pipeline.results.video.file_size || 0)})
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Informações de Extração */}
                <div className="bg-gray-900 rounded p-3 mb-3">
                  <h6 className="text-gray-400 font-medium mb-2">Informações de Extração</h6>
                  {pipeline.results?.extraction ? (
                    <div className="space-y-3">
                      {/* Informações do Canal e Pipeline Original */}
                      <div className="border-b border-gray-700 pb-2">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="text-blue-400 font-medium">📺 Canal:</span>
                          <span className="text-gray-300 font-semibold">
                            {pipeline.channel_url ? (
                              <a href={pipeline.channel_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
                                {pipeline.title || 'Canal'}
                              </a>
                            ) : (
                              pipeline.title || pipeline.display_name || 'Canal não identificado'
                            )}
                          </span>
                        </div>
                        {pipeline.results.extraction.channel_info?.name && (
                          <div className="text-xs text-gray-400 ml-6">
                            Nome: {pipeline.results.extraction.channel_info.name}
                            {pipeline.results.extraction.channel_info.subscriber_count && (
                              <span> • {pipeline.results.extraction.channel_info.subscriber_count.toLocaleString()} inscritos</span>
                            )}
                          </div>
                        )}
                      </div>
                      
                      {/* Estatísticas */}
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-gray-400">Total:</span>
                          <span className="text-gray-300 ml-1">
                            {pipeline.results.extraction.total_extracted || 0} vídeos
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400">Método:</span>
                          <span className="text-gray-300 ml-1">
                            {pipeline.results.extraction.method_used || 'Não disponível'}
                          </span>
                        </div>
                      </div>
                      
                      {/* Lista de Títulos Extraídos */}
                      {pipeline.results.extraction.titles && pipeline.results.extraction.titles.length > 0 && (
                        <div>
                          <div className="text-gray-400 text-sm mb-1">Títulos extraídos:</div>
                          <div className="max-h-32 overflow-y-auto space-y-1">
                            {pipeline.results.extraction.titles.slice(0, 5).map((title, index) => (
                              <div key={index} className="bg-gray-800 rounded p-2 text-xs">
                                <div className="text-gray-200 font-medium truncate">
                                  {index + 1}. {title.title}
                                </div>
                                <div className="flex justify-between text-gray-400 mt-1">
                                  <span>{title.views?.toLocaleString()} views</span>
                                  <span>{title.duration || 'N/A'}</span>
                                </div>
                              </div>
                            ))}
                            {pipeline.results.extraction.titles.length > 5 && (
                              <div className="text-gray-500 text-xs text-center py-1">
                                ... e mais {pipeline.results.extraction.titles.length - 5} vídeos
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                      
                      {/* Título Selecionado para Remodelagem */}
                      {pipeline.results?.titles?.selected_title && (
                        <div className="border-t border-gray-700 pt-3">
                          <h4 className="text-sm font-medium text-green-400 mb-2">🎯 Título Selecionado para Remodelagem:</h4>
                          <div className="bg-gradient-to-r from-green-900/30 to-purple-900/30 border border-green-700/30 rounded p-3">
                            <div className="text-green-300 font-bold text-base mb-3 bg-black/20 p-3 rounded border-l-4 border-green-500">
                              "{pipeline.results.titles.selected_title}"
                            </div>
                            {pipeline.results.titles.original_title && (
                              <div className="mb-3">
                                <div className="text-xs text-yellow-400 font-medium mb-1">📋 Título Original Usado como Base:</div>
                                <div className="text-sm text-gray-300 italic bg-gray-800/50 p-2 rounded">
                                  "{pipeline.results.titles.original_title}"
                                </div>
                              </div>
                            )}
                            {pipeline.results.titles.original_video_url && (
                              <div className="mb-3">
                                <a 
                                  href={pipeline.results.titles.original_video_url} 
                                  target="_blank" 
                                  rel="noopener noreferrer" 
                                  className="inline-flex items-center text-blue-400 hover:text-blue-300 text-sm bg-blue-900/30 px-3 py-2 rounded hover:bg-blue-900/50 transition-colors"
                                >
                                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h8m-7 4V8a2 2 0 012-2h2a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2z" />
                                  </svg>
                                  Ver vídeo original completo →
                                </a>
                              </div>
                            )}
                            <div className="text-xs text-gray-400 pt-2 border-t border-gray-700">
                              <div className="flex items-center justify-between">
                                <span>
                                  {pipeline.results.extraction?.method_used === 'manual' ? (
                                    <span className="text-orange-400">📁 Títulos fornecidos manualmente</span>
                                  ) : pipeline.results.extraction?.method_used === 'cache' ? (
                                    <span className="text-yellow-400">💾 Títulos carregados de cache local</span>
                                  ) : (
                                    <span className="text-green-400">🔄 Títulos extraídos diretamente do canal via API</span>
                                  )}
                                </span>
                                <span className="text-blue-400">
                                  Provider: {pipeline.results.titles.provider_used}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      <div className="text-xs text-gray-500 pt-1 border-t border-gray-700">
                        Extraído em: {pipeline.results.extraction.extraction_time ? 
                          new Date(pipeline.results.extraction.extraction_time).toLocaleString('pt-BR') : 'Não disponível'}
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">Aguardando informações de extração...</p>
                  )}
                </div>

                {/* Original Logs */}
                <div className="bg-gray-900 rounded p-3 max-h-40 overflow-y-auto">
                  <h6 className="text-gray-400 font-medium mb-2">Logs Detalhados</h6>
                  {pipeline.logs && pipeline.logs.length > 0 ? (
                    <div className="space-y-1">
                      {pipeline.logs.slice(-10).map((log, logIndex) => (
                        <div key={`${log.timestamp}-${logIndex}`} className="text-xs">
                          <span className="text-gray-500">
                            [{new Date(log.timestamp).toLocaleTimeString()}]
                          </span>
                          <span className={`ml-2 ${
                            log.level === 'error' ? 'text-red-400' :
                            log.level === 'warning' ? 'text-yellow-400' :
                            log.level === 'success' ? 'text-green-400' :
                            'text-gray-300'
                          }`}>
                            {log.message}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">Aguardando logs do processo...</p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Results Section */}
          {pipeline.status === 'completed' && pipeline.results && (
            <div className="p-4 border-t border-gray-700">
              <h5 className="text-white font-medium mb-3">Resultados</h5>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {pipeline.results.videos_created && (
                  <div className="bg-gray-900 rounded p-3">
                    <div className="flex items-center space-x-2 mb-2">
                      <Video size={16} className="text-purple-400" />
                      <span className="text-sm font-medium text-white">Vídeos Criados</span>
                    </div>
                    <p className="text-2xl font-bold text-purple-400">
                      {pipeline.results.videos_created}
                    </p>
                  </div>
                )}
                
                {pipeline.results.images_generated && (
                  <div className="bg-gray-900 rounded p-3">
                    <div className="flex items-center space-x-2 mb-2">
                      <Image size={16} className="text-pink-400" />
                      <span className="text-sm font-medium text-white">Imagens Geradas</span>
                    </div>
                    <p className="text-2xl font-bold text-pink-400">
                      {pipeline.results.images_generated}
                    </p>
                  </div>
                )}
                
                {pipeline.results.total_duration && (
                  <div className="bg-gray-900 rounded p-3">
                    <div className="flex items-center space-x-2 mb-2">
                      <Clock size={16} className="text-blue-400" />
                      <span className="text-sm font-medium text-white">Duração Total</span>
                    </div>
                    <p className="text-2xl font-bold text-blue-400">
                      {formatDuration(pipeline.results.total_duration)}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Error Section */}
          {pipeline.status === 'failed' && pipeline.errors && pipeline.errors.length > 0 && (
            <div className="p-4 border-t border-gray-700">
              <h5 className="text-white font-medium mb-3 flex items-center space-x-2">
                <AlertCircle size={16} className="text-red-400" />
                <span>Erros</span>
              </h5>
              <div className="space-y-2">
                {pipeline.errors.map((error, errorIndex) => (
                  <div key={errorIndex} className="bg-red-900/20 border border-red-500/30 rounded p-3">
                    <div className="flex items-start space-x-2">
                      <AlertCircle size={16} className="text-red-400 mt-0.5" />
                      <div>
                        <p className="text-red-300 font-medium">{error.step}</p>
                        <p className="text-red-200 text-sm">{error.message}</p>
                        {error.timestamp && (
                          <p className="text-red-400 text-xs mt-1">
                            {new Date(error.timestamp).toLocaleString()}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {/* Generated Content Section */}
          <div className="p-4 border-t border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <h5 className="text-white font-medium">Conteúdos Gerados</h5>
              <button
                onClick={() => downloadAllContent(pipeline)}
                className="text-sm text-blue-400 hover:text-blue-300 flex items-center space-x-1"
                title="Baixar todos os conteúdos em TXT"
              >
                <Download size={14} />
                <span>Baixar TXT</span>
              </button>
            </div>
            
            <div className="space-y-4">
              {/* Títulos */}
              {pipeline.results?.titles && (
                <ContentSection
                  title="Títulos Gerados"
                  icon={<FileText size={16} className="text-blue-400" />}
                  content={
                    <div className="space-y-3">
                      {/* Indicador da origem do prompt */}
                      <div className="mb-3">
                        <div className="text-xs text-gray-400 mb-2">Prompt utilizado:</div>
                        <PromptSourceIndicator 
                          promptSource={pipeline.results.titles.prompt_source}
                          agentInfo={pipeline.results.titles.agent_info}
                          style={pipeline.results.titles.style}
                          title={pipeline.results.titles.generated_titles?.[0] || ""}
                          promptName={pipeline.results.titles.style}
                        />
                      </div>
                      
                      {/* Lista de títulos */}
                      <div className="space-y-2">
                        {pipeline.results.titles.generated_titles?.map((title, idx) => (
                          <div key={idx} className="bg-gray-800 rounded p-2 text-sm text-gray-300">
                            {idx + 1}. {title}
                          </div>
                        ))}
                      </div>
                      
                      {/* Estatísticas */}
                      <div className="flex items-center justify-between text-xs text-gray-400 pt-2 border-t border-gray-700">
                        <span>Gerados: {pipeline.results.titles.generated_titles?.length || 0}</span>
                        <span>Provider: {pipeline.results.titles.provider_used}</span>
                      </div>
                    </div>
                  }
                  downloadData={pipeline.results.titles.generated_titles?.join('\n')}
                  filename={`titulos_${pipeline.display_name || pipeline.pipeline_id?.slice(-8)}.txt`}
                />
              )}
              
              {/* Premissa */}
              {pipeline.results?.premises && (
                <ContentSection
                  title="Premissa"
                  icon={<FileText size={16} className="text-purple-400" />}
                  content={
                    <div className="space-y-3">
                      {/* Indicador da origem do prompt */}
                      <div className="mb-3">
                        <div className="text-xs text-gray-400 mb-2">Prompt utilizado:</div>
                        <PromptSourceIndicator 
                          promptSource={pipeline.results.premises.prompt_source}
                          agentInfo={pipeline.results.premises.agent_info}
                          style={pipeline.results.premises.style || "premises"}
                          title={pipeline.results.premises.selected_title || ""}
                          promptName={pipeline.results.premises.style}
                        />
                      </div>
                      
                      {/* Conteúdo da premissa */}
                      <div className="bg-gray-800 rounded p-3 text-sm text-gray-300 whitespace-pre-wrap">
                        {pipeline.results.premises.premise}
                      </div>
                      
                      {/* Estatísticas */}
                      <div className="flex items-center justify-between text-xs text-gray-400 pt-2 border-t border-gray-700">
                        <span>Palavras: {pipeline.results.premises.word_count || 0}</span>
                        <span>Provider: {pipeline.results.premises.provider_used}</span>
                      </div>
                    </div>
                  }
                  downloadData={pipeline.results.premises.premise}
                  filename={`premissa_${pipeline.display_name || pipeline.pipeline_id?.slice(-8)}.txt`}
                />
              )}
              
              {/* Roteiro */}
              {pipeline.results?.scripts && (
                <ContentSection
                  title="Roteiro"
                  icon={<FileText size={16} className="text-green-400" />}
                  content={
                    <div className="space-y-3">
                      {/* Indicador da origem do prompt */}
                      <div className="mb-3">
                        <div className="text-xs text-gray-400 mb-2">Prompt utilizado:</div>
                        <PromptSourceIndicator 
                          promptSource={pipeline.results.scripts?.prompt_source || "system_default"}
                          agentInfo={pipeline.results.scripts?.agent_info}
                          style={pipeline.results.scripts?.style || "scripts"}
                          title={pipeline.results.premises?.selected_title || ""}
                          promptName={pipeline.results.scripts?.style}
                        />
                      </div>
                      
                      <div className="bg-gray-800 rounded p-3 text-sm text-gray-300 whitespace-pre-wrap max-h-60 overflow-y-auto">
                        {pipeline.results.scripts.script}
                      </div>
                    </div>
                  }
                  downloadData={pipeline.results.scripts.script}
                  filename={`roteiro_${pipeline.display_name || pipeline.pipeline_id?.slice(-8)}.txt`}
                />
              )}
              
              {/* Roteiro Processado */}
              {pipeline.results?.script_processing && (
                <ContentSection
                  title="Roteiro Processado"
                  icon={<Activity size={16} className="text-orange-400" />}
                  content={
                    <div className="space-y-3">
                      <div className="bg-gray-800 rounded p-3">
                        <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                          <div>
                            <span className="text-gray-400">Status:</span>
                            <p className="text-white">{pipeline.results.script_processing.status || 'N/A'}</p>
                          </div>
                          <div>
                            <span className="text-gray-400">Processado em:</span>
                            <p className="text-white">
                              {pipeline.results.script_processing.processed_at ? 
                                new Date(pipeline.results.script_processing.processed_at).toLocaleString('pt-BR') : 'N/A'}
                            </p>
                          </div>
                          {pipeline.results.script_processing.metrics && (
                            <>
                              <div>
                                <span className="text-gray-400">Caracteres originais:</span>
                                <p className="text-white">{pipeline.results.script_processing.metrics.original_length || 0}</p>
                              </div>
                              <div>
                                <span className="text-gray-400">Caracteres processados:</span>
                                <p className="text-white">{pipeline.results.script_processing.metrics.processed_length || 0}</p>
                              </div>
                            </>
                          )}
                        </div>
                        
                        {pipeline.results.script_processing.processed_script && (
                          <div className="bg-gray-900 rounded p-3 text-sm text-gray-300 whitespace-pre-wrap max-h-60 overflow-y-auto">
                            {pipeline.results.script_processing.processed_script}
                          </div>
                        )}
                      </div>
                    </div>
                  }
                  downloadData={pipeline.results.script_processing.processed_script}
                  filename={`roteiro_processado_${pipeline.display_name || pipeline.pipeline_id?.slice(-8)}.txt`}
                />
              )}
              
              {/* Áudios TTS */}
              {pipeline.results?.tts && (
                <ContentSection
                  title="Áudio TTS"
                  icon={<Mic size={16} className="text-yellow-400" />}
                  content={
                    <div className="space-y-3">
                      <div className="bg-gray-800 rounded p-3">
                        <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                          <div>
                            <span className="text-gray-400">Provedor:</span>
                            <p className="text-white">{pipeline.results.tts.provider_used || 'N/A'}</p>
                          </div>
                          <div>
                            <span className="text-gray-400">Voz:</span>
                            <p className="text-white">{pipeline.results.tts.voice || 'N/A'}</p>
                          </div>
                          <div>
                            <span className="text-gray-400">Duração:</span>
                            <p className="text-white">{formatDuration(pipeline.results.tts.duration || 0)}</p>
                          </div>
                          <div>
                            <span className="text-gray-400">Tamanho:</span>
                            <p className="text-white">{formatFileSize(pipeline.results.tts.file_size || 0)}</p>
                          </div>
                        </div>
                        
                        {/* Player de Áudio */}
                        {pipeline.results.tts.audio_url && (
                          <div className="mb-4">
                            <h6 className="text-yellow-400 font-medium mb-2 flex items-center">
                              <Play size={14} className="mr-1" />
                              Reproduzir Áudio
                            </h6>
                            <audio 
                              controls 
                              className="w-full bg-gray-900 rounded"
                              preload="metadata"
                            >
                              <source src={pipeline.results.tts.audio_url} type="audio/wav" />
                              <source src={pipeline.results.tts.audio_url} type="audio/mpeg" />
                              Seu navegador não suporta o elemento de áudio.
                            </audio>
                            <div className="flex items-center justify-between mt-2">
                              <a 
                                href={pipeline.results.tts.audio_url} 
                                download={`audio_${pipeline.display_name || pipeline.pipeline_id?.slice(-8)}.wav`}
                                className="text-blue-400 hover:text-blue-300 text-sm flex items-center space-x-1"
                              >
                                <Download size={14} />
                                <span>Baixar WAV</span>
                              </a>
                              <span className="text-gray-500 text-xs">
                                {pipeline.results.tts.filename || 'audio.wav'}
                              </span>
                            </div>
                          </div>
                        )}
                        
                        {pipeline.results.tts.segments && (
                          <div>
                            <p className="text-gray-400 text-sm mb-2">Segmentos de áudio: {pipeline.results.tts.segments.length}</p>
                            <div className="space-y-1 max-h-32 overflow-y-auto">
                              {pipeline.results.tts.segments.map((segment, idx) => (
                                <div key={idx} className="text-xs text-gray-500 bg-gray-900 rounded p-2">
                                  <span className="text-blue-400">#{segment.index}:</span> {segment.text}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  }
                />
              )}
              
              {/* Imagens */}
              {pipeline.results?.images && (
                <ContentSection
                  title="Imagens Geradas"
                  icon={<Image size={16} className="text-pink-400" />}
                  content={
                    <div className="space-y-3">
                      <div className="bg-gray-800 rounded p-3">
                        <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                          <div>
                            <span className="text-gray-400">Total de imagens:</span>
                            <p className="text-white">{pipeline.results.images.total_images || 0}</p>
                          </div>
                          <div>
                            <span className="text-gray-400">Provedor:</span>
                            <p className="text-white">{pipeline.results.images.provider || 'N/A'}</p>
                          </div>
                        </div>
                        
                        {pipeline.results.images.generated_images && (
                          <div>
                            <div className="flex items-center justify-between mb-3">
                              <h6 className="text-pink-400 font-medium">Galeria de Imagens</h6>
                              <button 
                                onClick={() => downloadAllImages(pipeline.results.images.generated_images, pipeline)}
                                className="text-blue-400 hover:text-blue-300 text-sm flex items-center space-x-1"
                              >
                                <Download size={14} />
                                <span>Baixar Todas</span>
                              </button>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
                              {pipeline.results.images.generated_images.map((img, idx) => (
                                <div key={idx} className="bg-gray-900 rounded p-3 space-y-2">
                                  <div className="flex items-center justify-between">
                                    <span className="text-blue-400 font-medium text-sm">Imagem {idx + 1}</span>
                                    {img.url && (
                                      <a 
                                        href={img.url} 
                                        download={`imagem_${idx + 1}_${pipeline.display_name || pipeline.pipeline_id?.slice(-8)}.jpg`}
                                        className="text-blue-400 hover:text-blue-300 text-xs flex items-center space-x-1"
                                      >
                                        <Download size={12} />
                                        <span>Baixar</span>
                                      </a>
                                    )}
                                  </div>
                                  
                                  {img.url && (
                                    <div className="relative group">
                                      <img 
                                        src={img.url} 
                                        alt={`Imagem ${idx + 1}`}
                                        className="w-full h-32 object-cover rounded cursor-pointer transition-transform hover:scale-105"
                                        onClick={() => openImageModal(img.url, `Imagem ${idx + 1}`)}
                                        onError={(e) => {
                                          e.target.style.display = 'none'
                                          e.target.nextSibling.style.display = 'flex'
                                        }}
                                      />
                                      <div className="hidden items-center justify-center w-full h-32 bg-gray-800 rounded text-gray-500 text-sm">
                                        Erro ao carregar imagem
                                      </div>
                                      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all rounded flex items-center justify-center opacity-0 group-hover:opacity-100">
                                        <span className="text-white text-sm font-medium">Clique para ampliar</span>
                                      </div>
                                    </div>
                                  )}
                                  
                                  <div className="space-y-1">
                                    <p className="text-gray-400 text-xs">
                                      <span className="font-medium">Prompt:</span>
                                    </p>
                                    <p className="text-gray-300 text-xs bg-gray-800 rounded p-2 max-h-16 overflow-y-auto">
                                      {img.prompt || 'Prompt não disponível'}
                                    </p>
                                  </div>
                                  
                                  {img.style && (
                                    <p className="text-gray-500 text-xs">
                                      <span className="font-medium">Estilo:</span> {img.style}
                                    </p>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  }
                />
              )}
              
              {/* Vídeo Final */}
              {pipeline.results?.video && (
                <ContentSection
                  title="Vídeo Final"
                  icon={<Video size={16} className="text-red-400" />}
                  content={
                    <div className="bg-gray-800 rounded p-3">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">Duração:</span>
                          <p className="text-white">{formatDuration(pipeline.results.video.duration || 0)}</p>
                        </div>
                        <div>
                          <span className="text-gray-400">Resolução:</span>
                          <p className="text-white">{pipeline.results.video.resolution || 'N/A'}</p>
                        </div>
                        <div>
                          <span className="text-gray-400">Tamanho:</span>
                          <p className="text-white">{formatFileSize(pipeline.results.video.file_size || 0)}</p>
                        </div>
                        <div>
                          <span className="text-gray-400">Formato:</span>
                          <p className="text-white">{pipeline.results.video.format || 'MP4'}</p>
                        </div>
                      </div>
                      {pipeline.results.video.file_path && (
                        <div className="mt-3">
                          <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">
                            Visualizar Vídeo
                          </button>
                        </div>
                      )}
                    </div>
                  }
                />
              )}
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default PipelineProgress