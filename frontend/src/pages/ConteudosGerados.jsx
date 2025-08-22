/**
 * 📁 Conteúdos Gerados Page
 * 
 * Página para visualizar todos os conteúdos gerados pelas pipelines
 */

import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { Search, Image, Music, Video, FileText, RefreshCw, AlertCircle, HardDrive, Eye, Download, Play, Pause, Calendar, Volume2, Grid, List, Trash2 } from 'lucide-react'
import axios from 'axios'
import VideoPreview from '../components/VideoPreview'

const ConteudosGerados = () => {
  const [content, setContent] = useState({
    images: [],
    audios: [],
    videos: [],
    total_files: 0
  })
  const [summary, setSummary] = useState({
    total_images: 0,
    total_audios: 0,
    total_videos: 0,
    total_files: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('all')
  const [viewMode, setViewMode] = useState('grid')
  const [currentAudio, setCurrentAudio] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const audioRef = useRef(null)

  const [showVideoPreview, setShowVideoPreview] = useState(false)
  const [selectedVideo, setSelectedVideo] = useState(null)

  const fetchContent = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('/api/images/list-generated')
      const data = await response.json()
      
      if (data.success) {
        // Adicionar URLs para áudios e vídeos
        const contentWithUrls = {
          ...data.content,
          audios: data.content.audios.map(audio => ({
            ...audio,
            url: `/api/automations/audio/${audio.filename}`
          })),
          videos: data.content.videos.map(video => ({
            ...video,
            url: `/api/automations/video/${video.filename}`
          }))
        }
        setContent(contentWithUrls)
        setSummary(data.summary)
      } else {
        setError(data.error || 'Erro ao carregar conteúdos')
      }
    } catch (err) {
      setError('Erro de conexão: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchContent()
  }, [])

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('pt-BR')
  }

  const getFilteredContent = () => {
    let allContent = []
    
    if (activeTab === 'all' || activeTab === 'images') {
      allContent = [...allContent, ...content.images.map(item => ({ ...item, type: 'image' }))]
    }
    if (activeTab === 'all' || activeTab === 'audios') {
      allContent = [...allContent, ...content.audios.map(item => ({ ...item, type: 'audio' }))]
    }
    if (activeTab === 'all' || activeTab === 'videos') {
      allContent = [...allContent, ...content.videos.map(item => ({ ...item, type: 'video' }))]
    }

    if (searchTerm) {
      allContent = allContent.filter(item => 
        item.filename.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    return allContent
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'image': return <Image size={20} className="text-pink-400" />
      case 'audio': return <Music size={20} className="text-green-400" />
      case 'video': return <Video size={20} className="text-purple-400" />
      default: return <FileText size={20} className="text-gray-400" />
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'image': return 'border-pink-500 bg-pink-500/10'
      case 'audio': return 'border-green-500 bg-green-500/10'
      case 'video': return 'border-purple-500 bg-purple-500/10'
      default: return 'border-gray-500 bg-gray-500/10'
    }
  }

  const handlePreview = (item) => {
    if (item.type === 'image' && item.url) {
      window.open(item.url, '_blank')
    } else if (item.type === 'audio' && item.url) {
      handleAudioPlay(item)
    } else if (item.type === 'video' && item.url) {
      setSelectedVideo(item)
      setShowVideoPreview(true)
    } else {
      alert('Preview não disponível para este tipo de arquivo')
    }
  }

  const handleCloseVideoPreview = () => {
    setShowVideoPreview(false)
    setSelectedVideo(null)
  }

  const handleAudioPlay = (audioItem) => {
    if (currentAudio?.filename === audioItem.filename) {
      // Se é o mesmo áudio, pausar/retomar
      if (isPlaying) {
        audioRef.current?.pause()
        setIsPlaying(false)
      } else {
        audioRef.current?.play()
        setIsPlaying(true)
      }
    } else {
      // Novo áudio
      setCurrentAudio(audioItem)
      setIsPlaying(true)
      setCurrentTime(0)
    }
  }

  const handleAudioTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime)
      setDuration(audioRef.current.duration || 0)
    }
  }

  const handleAudioEnded = () => {
    setIsPlaying(false)
    setCurrentTime(0)
  }

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const percent = (e.clientX - rect.left) / rect.width
    const newTime = percent * duration
    if (audioRef.current) {
      audioRef.current.currentTime = newTime
      setCurrentTime(newTime)
    }
  }

  const formatTime = (time) => {
    if (isNaN(time)) return '0:00'
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const handleDownload = (item) => {
    if (item.type === 'image' && item.url) {
      const link = document.createElement('a')
      link.href = item.url
      link.download = item.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } else if (item.type === 'video' && item.url) {
      const link = document.createElement('a')
      link.href = item.url
      link.download = item.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } else {
      alert('Download direto não disponível para este tipo de arquivo')
    }
  }

  const handleDelete = async (item) => {
    if (window.confirm(`Tem certeza que deseja excluir ${item.filename}?`)) {
      try {
        await axios.delete(`/api/content/${item.type}/${item.filename}`)
        fetchContent() // Atualiza a lista após a exclusão
        alert('Arquivo excluído com sucesso!')
      } catch (error) {
        console.error('Erro ao excluir arquivo:', error)
        alert('Erro ao excluir arquivo. Verifique o console para mais detalhes.')
      }
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="animate-spin mr-2" size={24} />
            <span>Carregando conteúdos...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64 flex-col">
            <AlertCircle className="text-red-400 mb-4" size={48} />
            <h2 className="text-xl font-bold mb-2">Erro ao carregar conteúdos</h2>
            <p className="text-gray-400 mb-4">{error}</p>
            <button
              onClick={fetchContent}
              className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg flex items-center space-x-2"
            >
              <RefreshCw size={16} />
              <span>Tentar novamente</span>
            </button>
          </div>
        </div>
      </div>
    )
  }

  const filteredContent = getFilteredContent()

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold mb-2">📁 Conteúdos Gerados</h1>
              <p className="text-gray-400">Visualize todos os arquivos gerados pelas pipelines</p>
            </div>
            <button
              onClick={fetchContent}
              className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg flex items-center space-x-2"
            >
              <RefreshCw size={16} />
              <span>Atualizar</span>
            </button>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center space-x-3">
                <Image className="text-pink-400" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Imagens</p>
                  <p className="text-2xl font-bold text-pink-400">{summary.total_images}</p>
                </div>
              </div>
            </div>
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center space-x-3">
                <Music className="text-green-400" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Áudios</p>
                  <p className="text-2xl font-bold text-green-400">{summary.total_audios}</p>
                </div>
              </div>
            </div>
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center space-x-3">
                <Video className="text-purple-400" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Vídeos</p>
                  <p className="text-2xl font-bold text-purple-400">{summary.total_videos}</p>
                </div>
              </div>
            </div>
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center space-x-3">
                <HardDrive className="text-blue-400" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Total</p>
                  <p className="text-2xl font-bold text-blue-400">{summary.total_files}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
              <input
                type="text"
                placeholder="Buscar arquivos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Tabs */}
            <div className="flex bg-gray-800 rounded-lg p-1 border border-gray-700">
              {[
                { id: 'all', label: 'Todos', icon: FileText },
                { id: 'images', label: 'Imagens', icon: Image },
                { id: 'audios', label: 'Áudios', icon: Music },
                { id: 'videos', label: 'Vídeos', icon: Video }
              ].map(tab => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-400 hover:text-white hover:bg-gray-700'
                    }`}
                  >
                    <Icon size={16} />
                    <span>{tab.label}</span>
                  </button>
                )
              })}
            </div>

            {/* View Mode */}
            <div className="flex bg-gray-800 rounded-lg p-1 border border-gray-700">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-md transition-colors ${
                  viewMode === 'grid'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <Grid size={16} />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-md transition-colors ${
                  viewMode === 'list'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <List size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        {filteredContent.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="mx-auto text-gray-600 mb-4" size={48} />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">Nenhum conteúdo encontrado</h3>
            <p className="text-gray-500">
              {searchTerm ? 'Tente ajustar sua busca' : 'Execute algumas pipelines para gerar conteúdos'}
            </p>
          </div>
        ) : (
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4' : 'space-y-2'}>
            {filteredContent.map((item, index) => (
              <motion.div
                key={`${item.type}-${item.filename}-${index}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`bg-gray-800 rounded-lg border ${getTypeColor(item.type)} p-4 hover:bg-gray-750 transition-colors`}
              >
                {viewMode === 'grid' ? (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        {getTypeIcon(item.type)}
                        <span className="text-xs font-medium text-gray-400 uppercase">{item.type}</span>
                      </div>
                      <div className="flex space-x-1">
                        {item.type === 'audio' && item.url && (
                          <button
                            onClick={() => handleAudioPlay(item)}
                            className={`p-1 hover:bg-gray-700 rounded ${
                              currentAudio?.filename === item.filename && isPlaying
                                ? 'text-green-400'
                                : 'text-gray-400 hover:text-white'
                            }`}
                            title={currentAudio?.filename === item.filename && isPlaying ? 'Pausar' : 'Reproduzir'}
                          >
                            {currentAudio?.filename === item.filename && isPlaying ? (
                              <Pause size={14} />
                            ) : (
                              <Play size={14} />
                            )}
                          </button>
                        )}
                        <button
                          onClick={() => handlePreview(item)}
                          className="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                          title="Visualizar"
                        >
                          <Eye size={14} />
                        </button>
                        <button
                          onClick={() => handleDownload(item)}
                          className="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                          title="Download"
                        >
                          <Download size={14} />
                        </button>
                        <button
                          onClick={() => handleDelete(item)}
                          className="p-1 text-red-400 hover:text-red-300 hover:bg-gray-700 rounded"
                          title="Excluir"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                    <h3 className="font-medium text-white mb-2 truncate" title={item.filename}>
                      {item.filename}
                    </h3>
                    <div className="text-xs text-gray-400 space-y-1">
                      <div className="flex items-center space-x-2">
                        <HardDrive size={12} />
                        <span>{formatFileSize(item.size)}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Calendar size={12} />
                        <span>{formatDate(item.created_at)}</span>
                      </div>
                      {item.directory && (
                        <div className="flex items-center space-x-2">
                          <span>📁</span>
                          <span className="truncate">{item.directory}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      {getTypeIcon(item.type)}
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-white truncate" title={item.filename}>
                          {item.filename}
                        </h3>
                        <div className="flex items-center space-x-4 text-xs text-gray-400">
                          <span>{formatFileSize(item.size)}</span>
                          <span>{formatDate(item.created_at)}</span>
                          {item.directory && <span>📁 {item.directory}</span>}
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      {item.type === 'audio' && item.url && (
                        <button
                          onClick={() => handleAudioPlay(item)}
                          className={`p-2 hover:bg-gray-700 rounded ${
                            currentAudio?.filename === item.filename && isPlaying
                              ? 'text-green-400'
                              : 'text-gray-400 hover:text-white'
                          }`}
                          title={currentAudio?.filename === item.filename && isPlaying ? 'Pausar' : 'Reproduzir'}
                        >
                          {currentAudio?.filename === item.filename && isPlaying ? (
                            <Pause size={16} />
                          ) : (
                            <Play size={16} />
                          )}
                        </button>
                      )}
                      <button
                        onClick={() => handlePreview(item)}
                        className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                        title="Visualizar"
                      >
                        <Eye size={16} />
                      </button>
                      <button
                        onClick={() => handleDownload(item)}
                        className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                        title="Download"
                      >
                        <Download size={16} />
                      </button>
                      <button
                        onClick={() => handleDelete(item)}
                        className="p-2 text-red-400 hover:text-red-300 hover:bg-gray-700 rounded"
                        title="Excluir"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Audio Player */}
      {currentAudio && (
        <div className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 p-4 z-50">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center space-x-4">
              {/* Audio Info */}
              <div className="flex items-center space-x-3 min-w-0 flex-1">
                <div className="bg-green-500/20 p-2 rounded-lg">
                  <Volume2 className="text-green-400" size={20} />
                </div>
                <div className="min-w-0 flex-1">
                  <h4 className="text-white font-medium truncate">{currentAudio.filename}</h4>
                  <p className="text-gray-400 text-sm">
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </p>
                </div>
              </div>

              {/* Controls */}
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => handleAudioPlay(currentAudio)}
                  className="bg-green-600 hover:bg-green-700 p-2 rounded-lg"
                >
                  {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                </button>
              </div>

              {/* Progress Bar */}
              <div className="flex-1 max-w-md">
                <div
                  className="bg-gray-700 h-2 rounded-full cursor-pointer"
                  onClick={handleSeek}
                >
                  <div
                    className="bg-green-500 h-2 rounded-full transition-all"
                    style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Hidden Audio Element */}
      {currentAudio && (
        <audio
          ref={audioRef}
          src={currentAudio.url}
          onTimeUpdate={handleAudioTimeUpdate}
          onEnded={handleAudioEnded}
          onLoadedMetadata={handleAudioTimeUpdate}
          autoPlay
        />
      )}

      {/* Video Preview Modal */}
      {showVideoPreview && selectedVideo && (
        <VideoPreview
          video={selectedVideo}
          isOpen={showVideoPreview}
          onClose={handleCloseVideoPreview}
        />
      )}
    </div>
  )
}

export default ConteudosGerados