/**
 * 📊 Dashboard Page
 * 
 * Página principal com visão geral do sistema
 */

import React from 'react'
import { motion } from 'framer-motion'
import {
  Play,
  Pause,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Users,
  Video,
  Zap,
  Activity,
  BarChart3,
  Calendar
} from 'lucide-react'

import LoadingSpinner from '../components/LoadingSpinner'

const Dashboard = () => {
  // Stats cards data
  const statsCards = [
    {
      title: 'Pipelines Ativos',
      value: 3,
      change: '+2',
      changeType: 'positive',
      icon: Zap,
      color: 'blue'
    },
    {
      title: 'Na Fila',
      value: 7,
      change: '+5',
      changeType: 'positive',
      icon: Clock,
      color: 'yellow'
    },
    {
      title: 'Concluídos Hoje',
      value: 12,
      change: '+8',
      changeType: 'positive',
      icon: CheckCircle,
      color: 'green'
    },
    {
      title: 'Total de Canais',
      value: 15,
      change: '+3',
      changeType: 'positive',
      icon: Users,
      color: 'purple'
    }
  ]

  // Recent pipelines (mock data)
  const recentPipelines = [
    {
      id: '1',
      title: 'Como Ganhar Dinheiro Online - Método Infalível',
      channel: 'Motivação Viral',
      status: 'generating_audio',
      progress: 75,
      startedAt: '10:30',
      estimatedCompletion: '11:15'
    },
    {
      id: '2',
      title: 'Segredos dos Milionários Revelados',
      channel: 'Success Stories',
      status: 'generating_images',
      progress: 60,
      startedAt: '10:45',
      estimatedCompletion: '11:30'
    },
    {
      id: '3',
      title: 'Transforme Sua Vida em 30 Dias',
      channel: 'Vida Plena',
      status: 'optimizing',
      progress: 25,
      startedAt: '11:00',
      estimatedCompletion: '11:45'
    }
  ]

  const getStatusColor = (status) => {
    const colors = {
      'pending': 'text-gray-400',
      'collecting': 'text-blue-400',
      'optimizing': 'text-yellow-400',
      'creating_premise': 'text-orange-400',
      'generating_script': 'text-purple-400',
      'generating_audio': 'text-green-400',
      'generating_images': 'text-pink-400',
      'editing_video': 'text-red-400',
      'completed': 'text-green-500',
      'failed': 'text-red-500'
    }
    return colors[status] || 'text-gray-400'
  }

  const getStatusText = (status) => {
    const texts = {
      'pending': 'Aguardando',
      'collecting': 'Coletando',
      'optimizing': 'Otimizando',
      'creating_premise': 'Criando Premissa',
      'generating_script': 'Gerando Roteiro',
      'generating_audio': 'Gerando Áudio',
      'generating_images': 'Gerando Imagens',
      'editing_video': 'Editando Vídeo',
      'completed': 'Concluído',
      'failed': 'Falhou'
    }
    return texts[status] || 'Desconhecido'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-1">
            Visão geral do sistema de produção automática
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2">
            <BarChart3 size={18} />
            <span>Relatório</span>
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <Play size={18} />
            <span>Iniciar Produção</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsCards.map((card, index) => {
          const Icon = card.icon
          return (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm font-medium">{card.title}</p>
                  <p className="text-2xl font-bold text-white mt-1">{card.value}</p>
                  <div className="flex items-center mt-2">
                    <span className={`text-sm font-medium ${
                      card.changeType === 'positive' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {card.change}
                    </span>
                    <span className="text-gray-500 text-sm ml-1">vs ontem</span>
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${
                  card.color === 'blue' ? 'bg-blue-500 bg-opacity-20' :
                  card.color === 'yellow' ? 'bg-yellow-500 bg-opacity-20' :
                  card.color === 'green' ? 'bg-green-500 bg-opacity-20' :
                  'bg-purple-500 bg-opacity-20'
                }`}>
                  <Icon size={24} className={`${
                    card.color === 'blue' ? 'text-blue-400' :
                    card.color === 'yellow' ? 'text-yellow-400' :
                    card.color === 'green' ? 'text-green-400' :
                    'text-purple-400'
                  }`} />
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Pipelines */}
        <div className="lg:col-span-2">
          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="p-6 border-b border-gray-700">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Pipelines Ativos</h2>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-sm text-gray-400">Atualizando em tempo real</span>
                </div>
              </div>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {recentPipelines.map((pipeline) => (
                  <motion.div
                    key={pipeline.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-gray-700 rounded-lg p-4 border border-gray-600"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="font-medium text-white truncate">
                          {pipeline.title}
                        </h3>
                        <p className="text-sm text-gray-400">{pipeline.channel}</p>
                      </div>
                      <div className="text-right">
                        <span className={`text-sm font-medium ${getStatusColor(pipeline.status)}`}>
                          {getStatusText(pipeline.status)}
                        </span>
                        <p className="text-xs text-gray-500">
                          {pipeline.startedAt} → {pipeline.estimatedCompletion}
                        </p>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="w-full bg-gray-600 rounded-full h-2">
                      <motion.div
                        className="bg-blue-500 h-2 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${pipeline.progress}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                    <div className="flex justify-between items-center mt-2">
                      <span className="text-xs text-gray-400">
                        {pipeline.progress}% concluído
                      </span>
                      <div className="flex items-center space-x-2">
                        <button className="text-xs text-blue-400 hover:text-blue-300">
                          Ver Detalhes
                        </button>
                        <button className="text-xs text-red-400 hover:text-red-300">
                          Cancelar
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* System Status & Quick Actions */}
        <div className="space-y-6">
          {/* System Status */}
          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="p-6 border-b border-gray-700">
              <h2 className="text-xl font-semibold text-white">Status do Sistema</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">APIs Configuradas</span>
                  <div className="flex items-center space-x-2">
                    <CheckCircle size={16} className="text-green-400" />
                    <span className="text-green-400 text-sm">Online</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Modelos de IA</span>
                  <span className="text-white text-sm">2</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Serviços TTS</span>
                  <span className="text-white text-sm">2</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Geração de Imagens</span>
                  <span className="text-white text-sm">1</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="p-6 border-b border-gray-700">
              <h2 className="text-xl font-semibold text-white">Ações Rápidas</h2>
            </div>
            <div className="p-6 space-y-3">
              <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2">
                <Play size={18} />
                <span>Executar Coleta</span>
              </button>
              <button className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center justify-center space-x-2">
                <Video size={18} />
                <span>Ver Vídeos</span>
              </button>
              <button className="w-full px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors flex items-center justify-center space-x-2">
                <Users size={18} />
                <span>Gerenciar Canais</span>
              </button>
              <button className="w-full px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors flex items-center justify-center space-x-2">
                <Activity size={18} />
                <span>Ver Analytics</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
