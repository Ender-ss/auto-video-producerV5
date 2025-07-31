/**
 * 📺 Channels Page
 * 
 * Página de gerenciamento de canais
 */

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Plus,
  Search,
  Filter,
  MoreVertical,
  Play,
  Pause,
  Settings,
  Trash2,
  ExternalLink,
  Users,
  Video,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Edit
} from 'lucide-react'

const Channels = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)

  // Mock data
  const channels = [
    {
      id: '1',
      name: 'Motivação Viral',
      url: 'https://www.youtube.com/@motivacaoviral',
      is_active: true,
      subscribers: '2.5M',
      total_videos_produced: 45,
      last_production: '2024-01-30T10:30:00',
      video_style: 'motivational',
      success_rate: 92,
      avg_views: '150K'
    },
    {
      id: '2',
      name: 'Success Stories',
      url: 'https://www.youtube.com/@successstories',
      is_active: true,
      subscribers: '1.8M',
      total_videos_produced: 32,
      last_production: '2024-01-30T08:15:00',
      video_style: 'educational',
      success_rate: 88,
      avg_views: '95K'
    },
    {
      id: '3',
      name: 'Vida Plena',
      url: 'https://www.youtube.com/@vidaplena',
      is_active: false,
      subscribers: '890K',
      total_videos_produced: 18,
      last_production: '2024-01-29T16:45:00',
      video_style: 'story',
      success_rate: 95,
      avg_views: '75K'
    }
  ]

  const getStyleBadge = (style) => {
    const styles = {
      'motivational': { label: 'Motivacional', color: 'bg-blue-500' },
      'educational': { label: 'Educativo', color: 'bg-green-500' },
      'entertainment': { label: 'Entretenimento', color: 'bg-purple-500' },
      'story': { label: 'História', color: 'bg-yellow-500' },
      'news': { label: 'Notícias', color: 'bg-red-500' }
    }
    const styleInfo = styles[style] || { label: style, color: 'bg-gray-500' }
    return (
      <span className={`px-2 py-1 text-xs font-medium text-white rounded-full ${styleInfo.color}`}>
        {styleInfo.label}
      </span>
    )
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR') + ' às ' + date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Canais</h1>
          <p className="text-gray-400 mt-1">
            Gerencie os canais monitorados para produção automática
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Plus size={18} />
          <span>Adicionar Canal</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar canais..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full"
          />
        </div>
        <button className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2">
          <Filter size={18} />
          <span>Filtros</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total de Canais</p>
              <p className="text-2xl font-bold text-white">{channels.length}</p>
            </div>
            <Users size={24} className="text-blue-400" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Canais Ativos</p>
              <p className="text-2xl font-bold text-white">
                {channels.filter(c => c.is_active).length}
              </p>
            </div>
            <CheckCircle size={24} className="text-green-400" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Vídeos Produzidos</p>
              <p className="text-2xl font-bold text-white">
                {channels.reduce((sum, c) => sum + c.total_videos_produced, 0)}
              </p>
            </div>
            <Video size={24} className="text-purple-400" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Taxa de Sucesso</p>
              <p className="text-2xl font-bold text-white">
                {Math.round(channels.reduce((sum, c) => sum + c.success_rate, 0) / channels.length)}%
              </p>
            </div>
            <TrendingUp size={24} className="text-yellow-400" />
          </div>
        </div>
      </div>

      {/* Channels List */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">Canais Monitorados</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {channels.map((channel, index) => (
              <motion.div
                key={channel.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-700 rounded-lg p-6 border border-gray-600 hover:border-gray-500 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-red-600 rounded-lg flex items-center justify-center">
                      <Video size={24} className="text-white" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-semibold text-white">
                          {channel.name}
                        </h3>
                        {channel.is_active ? (
                          <CheckCircle size={16} className="text-green-400" />
                        ) : (
                          <Pause size={16} className="text-gray-400" />
                        )}
                        {getStyleBadge(channel.video_style)}
                      </div>
                      <div className="flex items-center space-x-4 mt-1 text-sm text-gray-400">
                        <span>{channel.subscribers} inscritos</span>
                        <span>•</span>
                        <span>{channel.total_videos_produced} vídeos produzidos</span>
                        <span>•</span>
                        <span>Taxa: {channel.success_rate}%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="text-right text-sm">
                      <p className="text-gray-400">Última produção</p>
                      <p className="text-white">{formatDate(channel.last_production)}</p>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button className="p-2 rounded-lg hover:bg-gray-600 transition-colors">
                        <Play size={16} className="text-green-400" />
                      </button>
                      <button className="p-2 rounded-lg hover:bg-gray-600 transition-colors">
                        <Settings size={16} className="text-gray-400" />
                      </button>
                      <button className="p-2 rounded-lg hover:bg-gray-600 transition-colors">
                        <ExternalLink size={16} className="text-blue-400" />
                      </button>
                      <button className="p-2 rounded-lg hover:bg-gray-600 transition-colors">
                        <MoreVertical size={16} className="text-gray-400" />
                      </button>
                    </div>
                  </div>
                </div>
                
                {/* Channel Stats */}
                <div className="grid grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-600">
                  <div className="text-center">
                    <p className="text-sm text-gray-400">Frequência</p>
                    <p className="text-white font-medium">24h</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-400">Máx/Dia</p>
                    <p className="text-white font-medium">2</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-400">Média Views</p>
                    <p className="text-white font-medium">{channel.avg_views}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-400">Status</p>
                    <p className={`font-medium ${channel.is_active ? 'text-green-400' : 'text-gray-400'}`}>
                      {channel.is_active ? 'Ativo' : 'Pausado'}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Channels
