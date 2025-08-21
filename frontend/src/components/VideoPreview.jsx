import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X,
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize,
  Download,
  Share2,
  Eye,
  Clock,
  FileText,
  Image,
  Mic,
  Video,
  ExternalLink,
  Copy,
  Check,
  MoreVertical,
  Edit3,
  Trash2,
  RefreshCw
} from 'lucide-react'

const VideoPreview = ({ video, isOpen, onClose, onRegenerate, onEdit, onDelete }) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showControls, setShowControls] = useState(true)
  const [copied, setCopied] = useState(false)
  const [activeTab, setActiveTab] = useState('preview')
  const [showActions, setShowActions] = useState(false)
  
  const videoRef = useRef(null)
  const containerRef = useRef(null)
  const controlsTimeoutRef = useRef(null)

  useEffect(() => {
    if (!isOpen) {
      setIsPlaying(false)
      setCurrentTime(0)
      setActiveTab('preview')
    }
  }, [isOpen])

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const updateTime = () => setCurrentTime(video.currentTime)
    const updateDuration = () => setDuration(video.duration)
    const handleEnded = () => setIsPlaying(false)

    video.addEventListener('timeupdate', updateTime)
    video.addEventListener('loadedmetadata', updateDuration)
    video.addEventListener('ended', handleEnded)

    return () => {
      video.removeEventListener('timeupdate', updateTime)
      video.removeEventListener('loadedmetadata', updateDuration)
      video.removeEventListener('ended', handleEnded)
    }
  }, [isOpen])

  const togglePlay = () => {
    const video = videoRef.current
    if (!video) return

    if (isPlaying) {
      video.pause()
    } else {
      video.play()
    }
    setIsPlaying(!isPlaying)
  }

  const toggleMute = () => {
    const video = videoRef.current
    if (!video) return

    video.muted = !isMuted
    setIsMuted(!isMuted)
  }

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value)
    const video = videoRef.current
    if (!video) return

    video.volume = newVolume
    setVolume(newVolume)
    setIsMuted(newVolume === 0)
  }

  const handleSeek = (e) => {
    const video = videoRef.current
    if (!video) return

    const rect = e.currentTarget.getBoundingClientRect()
    const pos = (e.clientX - rect.left) / rect.width
    const newTime = pos * duration
    
    video.currentTime = newTime
    setCurrentTime(newTime)
  }

  const toggleFullscreen = () => {
    const container = containerRef.current
    if (!container) return

    if (!isFullscreen) {
      if (container.requestFullscreen) {
        container.requestFullscreen()
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      }
    }
    setIsFullscreen(!isFullscreen)
  }

  const formatTime = (time) => {
    if (!time || isNaN(time)) return '0:00'
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const handleMouseMove = () => {
    setShowControls(true)
    clearTimeout(controlsTimeoutRef.current)
    controlsTimeoutRef.current = setTimeout(() => {
      if (isPlaying) {
        setShowControls(false)
      }
    }, 3000)
  }

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const downloadVideo = () => {
    if (video?.output_path) {
      const link = document.createElement('a')
      link.href = video.output_path
      link.download = `${video.title || 'video'}.mp4`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  if (!isOpen || !video) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={(e) => e.target === e.currentTarget && onClose()}
      >
        <motion.div
          ref={containerRef}
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-gray-900 rounded-lg overflow-hidden max-w-6xl w-full max-h-[90vh] flex flex-col"
          onMouseMove={handleMouseMove}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-700">
            <div className="flex items-center space-x-4">
              <h3 className="text-xl font-semibold text-white truncate">
                {video.title || 'Vídeo sem título'}
              </h3>
              <div className="flex items-center space-x-2">
                <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded">
                  Concluído
                </span>
                <span className="text-sm text-gray-400">
                  {formatTime(video.duration)}
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* Action Menu */}
              <div className="relative">
                <button
                  onClick={() => setShowActions(!showActions)}
                  className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
                >
                  <MoreVertical size={20} />
                </button>
                
                {showActions && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="absolute right-0 top-full mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-10"
                  >
                    <div className="py-2">
                      <button
                        onClick={() => {
                          onEdit?.(video)
                          setShowActions(false)
                        }}
                        className="w-full px-4 py-2 text-left text-gray-300 hover:bg-gray-700 hover:text-white flex items-center space-x-2"
                      >
                        <Edit3 size={16} />
                        <span>Editar</span>
                      </button>
                      <button
                        onClick={() => {
                          onRegenerate?.(video)
                          setShowActions(false)
                        }}
                        className="w-full px-4 py-2 text-left text-gray-300 hover:bg-gray-700 hover:text-white flex items-center space-x-2"
                      >
                        <RefreshCw size={16} />
                        <span>Regenerar</span>
                      </button>
                      <div className="border-t border-gray-700 my-1" />
                      <button
                        onClick={() => {
                          onDelete?.(video)
                          setShowActions(false)
                        }}
                        className="w-full px-4 py-2 text-left text-red-400 hover:bg-red-500/20 hover:text-red-300 flex items-center space-x-2"
                      >
                        <Trash2 size={16} />
                        <span>Excluir</span>
                      </button>
                    </div>
                  </motion.div>
                )}
              </div>
              
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
              >
                <X size={20} />
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-gray-700">
            {[
              { id: 'preview', label: 'Prévia', icon: Eye },
              { id: 'details', label: 'Detalhes', icon: FileText },
              { id: 'assets', label: 'Assets', icon: Image }
            ].map(tab => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-3 border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-400 bg-blue-500/10'
                      : 'border-transparent text-gray-400 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  <Icon size={16} />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>

          {/* Content */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'preview' && (
              <div className="h-full flex flex-col">
                {/* Video Player */}
                <div className="relative flex-1 bg-black">
                  {video.output_path ? (
                    <>
                      <video
                        ref={videoRef}
                        src={video.output_path}
                        className="w-full h-full object-contain"
                        onClick={togglePlay}
                      />
                      
                      {/* Video Controls */}
                      <AnimatePresence>
                        {showControls && (
                          <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/60"
                          >
                            {/* Top Controls */}
                            <div className="absolute top-4 right-4 flex items-center space-x-2">
                              <button
                                onClick={downloadVideo}
                                className="p-2 bg-black/50 text-white hover:bg-black/70 rounded transition-colors"
                                title="Download"
                              >
                                <Download size={20} />
                              </button>
                              <button
                                onClick={toggleFullscreen}
                                className="p-2 bg-black/50 text-white hover:bg-black/70 rounded transition-colors"
                                title="Tela cheia"
                              >
                                <Maximize size={20} />
                              </button>
                            </div>
                            
                            {/* Center Play Button */}
                            {!isPlaying && (
                              <div className="absolute inset-0 flex items-center justify-center">
                                <button
                                  onClick={togglePlay}
                                  className="p-4 bg-black/50 text-white hover:bg-black/70 rounded-full transition-colors"
                                >
                                  <Play size={32} />
                                </button>
                              </div>
                            )}
                            
                            {/* Bottom Controls */}
                            <div className="absolute bottom-0 left-0 right-0 p-4">
                              {/* Progress Bar */}
                              <div
                                className="w-full h-2 bg-white/20 rounded-full cursor-pointer mb-4"
                                onClick={handleSeek}
                              >
                                <div
                                  className="h-full bg-blue-500 rounded-full transition-all"
                                  style={{ width: `${(currentTime / duration) * 100 || 0}%` }}
                                />
                              </div>
                              
                              {/* Control Buttons */}
                              <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-4">
                                  <button
                                    onClick={togglePlay}
                                    className="text-white hover:text-blue-400 transition-colors"
                                  >
                                    {isPlaying ? <Pause size={24} /> : <Play size={24} />}
                                  </button>
                                  
                                  <div className="flex items-center space-x-2">
                                    <button
                                      onClick={toggleMute}
                                      className="text-white hover:text-blue-400 transition-colors"
                                    >
                                      {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                                    </button>
                                    <input
                                      type="range"
                                      min="0"
                                      max="1"
                                      step="0.1"
                                      value={isMuted ? 0 : volume}
                                      onChange={handleVolumeChange}
                                      className="w-20 h-1 bg-white/20 rounded-full appearance-none cursor-pointer"
                                    />
                                  </div>
                                  
                                  <span className="text-white text-sm">
                                    {formatTime(currentTime)} / {formatTime(duration)}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </>
                  ) : (
                    <div className="flex items-center justify-center h-full text-gray-400">
                      <div className="text-center">
                        <Video size={48} className="mx-auto mb-4" />
                        <p>Vídeo não disponível</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'details' && (
              <div className="p-6 overflow-y-auto max-h-96">
                <div className="space-y-6">
                  {/* Basic Info */}
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-4">Informações Básicas</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm text-gray-400">Título</label>
                        <div className="flex items-center space-x-2 mt-1">
                          <p className="text-white bg-gray-800 p-2 rounded flex-1">
                            {video.title || 'N/A'}
                          </p>
                          <button
                            onClick={() => copyToClipboard(video.title || '')}
                            className="p-2 text-gray-400 hover:text-white transition-colors"
                          >
                            {copied ? <Check size={16} /> : <Copy size={16} />}
                          </button>
                        </div>
                      </div>
                      
                      <div>
                        <label className="text-sm text-gray-400">Duração</label>
                        <p className="text-white bg-gray-800 p-2 rounded mt-1">
                          {formatTime(video.duration)}
                        </p>
                      </div>
                      
                      <div>
                        <label className="text-sm text-gray-400">Criado em</label>
                        <p className="text-white bg-gray-800 p-2 rounded mt-1">
                          {video.created_at ? new Date(video.created_at).toLocaleString() : 'N/A'}
                        </p>
                      </div>
                      
                      <div>
                        <label className="text-sm text-gray-400">Status</label>
                        <p className="text-green-400 bg-gray-800 p-2 rounded mt-1">
                          Concluído
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Script */}
                  {video.script && (
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                        <FileText size={20} />
                        <span>Roteiro</span>
                      </h4>
                      <div className="bg-gray-800 rounded p-4 max-h-40 overflow-y-auto">
                        <pre className="text-gray-300 text-sm whitespace-pre-wrap">
                          {video.script}
                        </pre>
                      </div>
                    </div>
                  )}

                  {/* Configuration */}
                  {video.config && (
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-4">Configuração</h4>
                      <div className="bg-gray-800 rounded p-4">
                        <pre className="text-gray-300 text-sm">
                          {JSON.stringify(video.config, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'assets' && (
              <div className="p-6 overflow-y-auto max-h-96">
                <div className="space-y-6">
                  {/* Audio */}
                  {video.audio_path && (
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                        <Mic size={20} />
                        <span>Áudio</span>
                      </h4>
                      <div className="bg-gray-800 rounded p-4">
                        <audio controls className="w-full">
                          <source src={video.audio_path} type="audio/mpeg" />
                          Seu navegador não suporta o elemento de áudio.
                        </audio>
                      </div>
                    </div>
                  )}

                  {/* Images */}
                  {video.images && video.images.length > 0 && (
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                        <Image size={20} />
                        <span>Imagens ({video.images.length})</span>
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        {video.images.map((image, index) => (
                          <div key={index} className="bg-gray-800 rounded overflow-hidden">
                            <img
                              src={image.path || image.url}
                              alt={`Imagem ${index + 1}`}
                              className="w-full h-32 object-cover"
                            />
                            <div className="p-2">
                              <p className="text-xs text-gray-400 truncate">
                                {image.prompt || `Imagem ${index + 1}`}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Files */}
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-4">Arquivos</h4>
                    <div className="space-y-2">
                      {[
                        { label: 'Vídeo Final', path: video.output_path, icon: Video },
                        { label: 'Áudio', path: video.audio_path, icon: Mic },
                        { label: 'Roteiro', path: video.script_path, icon: FileText }
                      ].filter(file => file.path).map((file, index) => {
                        const Icon = file.icon
                        return (
                          <div key={index} className="flex items-center justify-between bg-gray-800 rounded p-3">
                            <div className="flex items-center space-x-3">
                              <Icon size={20} className="text-gray-400" />
                              <span className="text-white">{file.label}</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => copyToClipboard(file.path)}
                                className="p-1 text-gray-400 hover:text-white transition-colors"
                                title="Copiar caminho"
                              >
                                <Copy size={16} />
                              </button>
                              <a
                                href={file.path}
                                download
                                className="p-1 text-gray-400 hover:text-white transition-colors"
                                title="Download"
                              >
                                <Download size={16} />
                              </a>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default VideoPreview