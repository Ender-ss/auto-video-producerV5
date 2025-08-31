/**
 * 📊 Pipeline History Component
 * 
 * Componente para exibir histórico completo de pipelines
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Eye,
  Download,
  Calendar,
  Filter,
  Search,
  BarChart3,
  RefreshCw,
  FileText,
  Play,
  Pause,
  Square
} from 'lucide-react'

const PipelineHistory = () => {
  const [pipelines, setPipelines] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [dateFilter, setDateFilter] = useState('all')
  const [stats, setStats] = useState(null)
  const [currentPage, setCurrentPage] = useState(0)
  const [totalCount, setTotalCount] = useState(0)
  const itemsPerPage = 20

  useEffect(() => {
    loadPipelineHistory()
    loadStats()
  }, [currentPage, statusFilter, dateFilter])

  const loadPipelineHistory = async () => {
    try {
      setLoading(true)
      
      const params = new URLSearchParams({
        offset: currentPage * itemsPerPage,
        limit: itemsPerPage
      })
      
      if (statusFilter !== 'all') {
        params.append('status', statusFilter)
      }
      
      if (dateFilter !== 'all') {
        const now = new Date()
        let dateFrom
        
        switch (dateFilter) {
          case 'today':
            dateFrom = new Date(now.getFullYear(), now.getMonth(), now.getDate())
            break
          case 'week':
            dateFrom = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
            break
          case 'month':
            dateFrom = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate())
            break
        }
        
        if (dateFrom) {
          params.append('date_from', dateFrom.toISOString())
        }
      }
      
      const response = await fetch(`/api/pipeline/history?${params}`)
      
      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          setPipelines(result.pipelines)
          setTotalCount(result.total_count)
        }
      }
    } catch (error) {
      console.error('Erro ao carregar histórico:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch('/api/pipeline/stats')
      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          setStats(result.data)
        }
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} className="text-green-400" />
      case 'failed':
        return <XCircle size={16} className="text-red-400" />
      case 'processing':
        return <RefreshCw size={16} className="text-blue-400 animate-spin" />
      case 'paused':
        return <Pause size={16} className="text-yellow-400" />
      case 'cancelled':
        return <Square size={16} className="text-gray-400" />
      default:
        return <Clock size={16} className="text-gray-400" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-400'
      case 'failed':
        return 'text-red-400'
      case 'processing':
        return 'text-blue-400'
      case 'paused':
        return 'text-yellow-400'
      case 'cancelled':
        return 'text-gray-400'
      default:
        return 'text-gray-400'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Concluído'
      case 'failed':
        return 'Falhou'
      case 'processing':
        return 'Processando'
      case 'paused':
        return 'Pausado'
      case 'cancelled':
        return 'Cancelado'
      default:
        return 'Aguardando'
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('pt-BR')
  }

  const formatDuration = (startDate, endDate) => {
    if (!endDate) return 'N/A'
    
    const start = new Date(startDate)
    const end = new Date(endDate)
    const diffMs = end - start
    const diffMinutes = Math.floor(diffMs / 60000)
    
    if (diffMinutes < 60) {
      return `${diffMinutes}min`
    } else {
      const hours = Math.floor(diffMinutes / 60)
      const minutes = diffMinutes % 60
      return `${hours}h ${minutes}min`
    }
  }

  const filteredPipelines = pipelines.filter(pipeline => {
    const matchesSearch = pipeline.display_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         pipeline.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         pipeline.channel_url?.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesSearch
  })

  const totalPages = Math.ceil(totalCount / itemsPerPage)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Histórico de Pipelines</h1>
          <p className="text-gray-400 mt-1">Todas as pipelines executadas no sistema</p>
        </div>
        <button
          onClick={() => {
            loadPipelineHistory()
            loadStats()
          }}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw size={16} />
          <span>Atualizar</span>
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gray-800 rounded-lg p-6 border border-gray-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total de Pipelines</p>
                <p className="text-2xl font-bold text-white">{stats.total_pipelines}</p>
              </div>
              <BarChart3 size={24} className="text-blue-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gray-800 rounded-lg p-6 border border-gray-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Taxa de Sucesso</p>
                <p className="text-2xl font-bold text-green-400">{stats.success_rate}%</p>
              </div>
              <CheckCircle size={24} className="text-green-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gray-800 rounded-lg p-6 border border-gray-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Ativas Agora</p>
                <p className="text-2xl font-bold text-blue-400">{stats.active_pipelines}</p>
              </div>
              <RefreshCw size={24} className="text-blue-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gray-800 rounded-lg p-6 border border-gray-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Concluídas</p>
                <p className="text-2xl font-bold text-green-400">
                  {stats.status_distribution?.completed || 0}
                </p>
              </div>
              <CheckCircle size={24} className="text-green-400" />
            </div>
          </motion.div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nome ou URL..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
          >
            <option value="all">Todos os Status</option>
            <option value="completed">Concluído</option>
            <option value="failed">Falhou</option>
            <option value="processing">Processando</option>
            <option value="paused">Pausado</option>
            <option value="cancelled">Cancelado</option>
          </select>

          {/* Date Filter */}
          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
          >
            <option value="all">Todas as Datas</option>
            <option value="today">Hoje</option>
            <option value="week">Última Semana</option>
            <option value="month">Último Mês</option>
          </select>

          {/* Results Count */}
          <div className="flex items-center text-gray-400">
            <span className="text-sm">
              {filteredPipelines.length} de {totalCount} pipelines
            </span>
          </div>
        </div>
      </div>

      {/* Pipeline List */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <RefreshCw size={32} className="mx-auto text-blue-400 animate-spin mb-4" />
            <p className="text-gray-400">Carregando histórico...</p>
          </div>
        ) : filteredPipelines.length === 0 ? (
          <div className="p-8 text-center">
            <FileText size={32} className="mx-auto text-gray-600 mb-4" />
            <p className="text-gray-400">Nenhuma pipeline encontrada</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-700">
            {filteredPipelines.map((pipeline, index) => (
              <motion.div
                key={pipeline.pipeline_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-4 hover:bg-gray-750 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(pipeline.status)}
                    <div>
                      <h3 className="font-medium text-white">
                        Pipeline #{pipeline.display_name}
                      </h3>
                      <p className="text-sm text-gray-400 truncate max-w-md">
                        {pipeline.title || pipeline.channel_url}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-6 text-sm">
                    <div className="text-center">
                      <p className="text-gray-400">Status</p>
                      <p className={`font-medium ${getStatusColor(pipeline.status)}`}>
                        {getStatusText(pipeline.status)}
                      </p>
                    </div>

                    <div className="text-center">
                      <p className="text-gray-400">Iniciado</p>
                      <p className="text-white">{formatDate(pipeline.started_at)}</p>
                    </div>

                    <div className="text-center">
                      <p className="text-gray-400">Duração</p>
                      <p className="text-white">
                        {formatDuration(pipeline.started_at, pipeline.completed_at)}
                      </p>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => window.open(`#/pipeline/${pipeline.display_name}`, '_blank')}
                        className="p-2 text-gray-400 hover:text-blue-400 hover:bg-gray-700 rounded transition-colors"
                        title="Ver Detalhes"
                      >
                        <Eye size={16} />
                      </button>

                      {pipeline.status === 'completed' && (
                        <button
                          onClick={() => {
                            // Download results
                            const content = JSON.stringify(pipeline.results, null, 2)
                            const blob = new Blob([content], { type: 'application/json' })
                            const url = URL.createObjectURL(blob)
                            const link = document.createElement('a')
                            link.href = url
                            link.download = `pipeline_${pipeline.display_name}_results.json`
                            document.body.appendChild(link)
                            link.click()
                            document.body.removeChild(link)
                            URL.revokeObjectURL(url)
                          }}
                          className="p-2 text-gray-400 hover:text-green-400 hover:bg-gray-700 rounded transition-colors"
                          title="Download Resultados"
                        >
                          <Download size={16} />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
            disabled={currentPage === 0}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600 transition-colors"
          >
            Anterior
          </button>

          <div className="flex items-center space-x-2">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const pageNum = currentPage < 3 ? i : currentPage - 2 + i
              if (pageNum >= totalPages) return null
              
              return (
                <button
                  key={pageNum}
                  onClick={() => setCurrentPage(pageNum)}
                  className={`px-3 py-2 rounded-lg transition-colors ${
                    currentPage === pageNum
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {pageNum + 1}
                </button>
              )
            })}
          </div>

          <button
            onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
            disabled={currentPage === totalPages - 1}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600 transition-colors"
          >
            Próximo
          </button>
        </div>
      )}
    </div>
  )
}

export default PipelineHistory