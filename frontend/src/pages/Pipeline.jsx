/**
 * 🎬 Pipeline Page
 * 
 * Página de monitoramento do pipeline de produção
 */

import React, { useState } from 'react'
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
  Activity
} from 'lucide-react'

const Pipeline = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

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
      logs_count: 12
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
      logs_count: 8
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
      logs_count: 4
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
            Monitore o progresso da produção automática de vídeos
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2">
            <RefreshCw size={18} />
            <span>Atualizar</span>
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <Play size={18} />
            <span>Nova Produção</span>
          </button>
        </div>
      </div>

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
    </div>
  )
}

export default Pipeline
