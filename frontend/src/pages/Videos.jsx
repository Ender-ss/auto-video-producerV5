/**
 * 🎥 Videos Page
 * 
 * Página da biblioteca de vídeos produzidos
 */

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Play,
  Download,
  Share2,
  Trash2,
  Eye,
  Calendar,
  Clock,
  BarChart3,
  Filter,
  Search,
  Grid,
  List,
  MoreVertical,
  RefreshCw
} from 'lucide-react'

const Videos = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [viewMode, setViewMode] = useState('grid')
  const [sortBy, setSortBy] = useState('newest')

  // Mock data
  const videos = [
    {
      id: '1',
      title: 'Como Ganhar Dinheiro Online - Método Infalível 2024',
      channel: 'Motivação Viral',
      duration: 305,
      file_size: 45600000,
      created_at: '2024-01-30T10:30:00',
      video_style: 'motivational',
      download_count: 3
    },
    {
      id: '2',
      title: 'Segredos dos Milionários Que Ninguém Te Conta',
      channel: 'Success Stories',
      duration: 420,
      file_size: 62400000,
      created_at: '2024-01-30T09:15:00',
      video_style: 'educational',
      download_count: 1
    },
    {
      id: '3',
      title: 'O Maior Erro Que Você Comete Com Dinheiro',
      channel: 'Finanças Inteligentes',
      duration: 480,
      file_size: 71200000,
      created_at: '2024-01-30T08:00:00',
      video_style: 'educational',
      download_count: 5
    }
  ]

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const formatFileSize = (bytes) => {
    const mb = bytes / (1024 * 1024)
    return `${mb.toFixed(1)} MB`
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR')
  }

  const getStyleBadge = (style) => {
    const styles = {
      'motivational': { label: 'Motivacional', color: 'bg-blue-500' },
      'educational': { label: 'Educativo', color: 'bg-green-500' },
      'entertainment': { label: 'Entretenimento', color: 'bg-purple-500' },
      'story': { label: 'História', color: 'bg-yellow-500' }
    }
    const styleInfo = styles[style] || { label: style, color: 'bg-gray-500' }
    return (
      <span className={`px-2 py-1 text-xs font-medium text-white rounded-full ${styleInfo.color}`}>
        {styleInfo.label}
      </span>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Biblioteca de Vídeos</h1>
          <p className="text-gray-400 mt-1">
            Gerencie todos os vídeos produzidos automaticamente
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2">
            <RefreshCw size={18} />
            <span>Atualizar</span>
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <Download size={18} />
            <span>Download em Lote</span>
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total de Vídeos</p>
              <p className="text-2xl font-bold text-white">{videos.length}</p>
            </div>
            <Play size={24} className="text-blue-400" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Duração Total</p>
              <p className="text-2xl font-bold text-white">
                {Math.floor(videos.reduce((sum, v) => sum + v.duration, 0) / 60)}min
              </p>
            </div>
            <Clock size={24} className="text-green-400" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Tamanho Total</p>
              <p className="text-2xl font-bold text-white">
                {formatFileSize(videos.reduce((sum, v) => sum + v.file_size, 0))}
              </p>
            </div>
            <BarChart3 size={24} className="text-purple-400" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Downloads</p>
              <p className="text-2xl font-bold text-white">
                {videos.reduce((sum, v) => sum + v.download_count, 0)}
              </p>
            </div>
            <Download size={24} className="text-yellow-400" />
          </div>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar vídeos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-80"
            />
          </div>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-40"
          >
            <option value="newest">Mais Recentes</option>
            <option value="oldest">Mais Antigos</option>
            <option value="duration">Por Duração</option>
            <option value="downloads">Por Downloads</option>
          </select>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400 hover:text-white'
            }`}
          >
            <Grid size={18} />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400 hover:text-white'
            }`}
          >
            <List size={18} />
          </button>
        </div>
      </div>

      {/* Videos Grid/List */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-6">
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {videos.map((video, index) => (
                <motion.div
                  key={video.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-gray-700 rounded-lg overflow-hidden border border-gray-600 hover:border-gray-500 transition-colors"
                >
                  {/* Thumbnail */}
                  <div className="relative aspect-video bg-gray-600">
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Play size={48} className="text-white opacity-50" />
                    </div>
                    <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
                      {formatDuration(video.duration)}
                    </div>
                  </div>
                  
                  {/* Content */}
                  <div className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-medium text-white text-sm line-clamp-2">
                        {video.title}
                      </h3>
                      <button className="p-1 rounded hover:bg-gray-600 transition-colors">
                        <MoreVertical size={16} className="text-gray-400" />
                      </button>
                    </div>
                    
                    <div className="flex items-center justify-between mb-3">
                      <p className="text-xs text-gray-400">{video.channel}</p>
                      {getStyleBadge(video.video_style)}
                    </div>
                    
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                      <span>{formatDate(video.created_at)}</span>
                      <span>{formatFileSize(video.file_size)}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-xs flex items-center justify-center space-x-1">
                        <Download size={14} />
                        <span>Download</span>
                      </button>
                      <button className="p-2 rounded-lg hover:bg-gray-600 transition-colors">
                        <Eye size={14} className="text-gray-400" />
                      </button>
                      <button className="p-2 rounded-lg hover:bg-gray-600 transition-colors">
                        <Share2 size={14} className="text-gray-400" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {videos.map((video, index) => (
                <motion.div
                  key={video.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="bg-gray-700 rounded-lg p-4 border border-gray-600 hover:border-gray-500 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-24 h-14 bg-gray-600 rounded flex items-center justify-center flex-shrink-0">
                      <Play size={20} className="text-white opacity-50" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-white truncate">{video.title}</h3>
                          <div className="flex items-center space-x-4 mt-1 text-sm text-gray-400">
                            <span>{video.channel}</span>
                            <span>•</span>
                            <span>{formatDuration(video.duration)}</span>
                            <span>•</span>
                            <span>{formatFileSize(video.file_size)}</span>
                            <span>•</span>
                            <span>{formatDate(video.created_at)}</span>
                          </div>
                        </div>
                        {getStyleBadge(video.video_style)}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-400">{video.download_count} downloads</span>
                      <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm flex items-center space-x-2">
                        <Download size={16} />
                        <span>Download</span>
                      </button>
                      <button className="p-2 rounded-lg hover:bg-gray-600 transition-colors">
                        <MoreVertical size={16} className="text-gray-400" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Videos
