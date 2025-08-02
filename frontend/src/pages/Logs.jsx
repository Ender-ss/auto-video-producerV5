/**
 * 📋 Logs Page
 * 
 * Página para visualizar logs do sistema
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  RefreshCw,
  Download,
  Trash2,
  Search,
  Filter,
  AlertCircle,
  CheckCircle,
  XCircle,
  Info,
  Clock,
  Terminal
} from 'lucide-react'

const Logs = () => {
  const [logs, setLogs] = useState([])
  const [filteredLogs, setFilteredLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [levelFilter, setLevelFilter] = useState('all')
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastTimestamp, setLastTimestamp] = useState(0)

  const logLevels = [
    { value: 'all', label: 'Todos', color: 'gray' },
    { value: 'info', label: 'Info', color: 'blue' },
    { value: 'success', label: 'Sucesso', color: 'green' },
    { value: 'warning', label: 'Aviso', color: 'yellow' },
    { value: 'error', label: 'Erro', color: 'red' }
  ]

  useEffect(() => {
    fetchLogs()

    if (autoRefresh) {
      const interval = setInterval(fetchNewLogs, 2000) // Buscar novos logs a cada 2 segundos
      return () => clearInterval(interval)
    }
  }, [autoRefresh, lastTimestamp])

  useEffect(() => {
    filterLogs()
  }, [logs, searchTerm, levelFilter])

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:5000/api/system/logs')
      const data = await response.json()

      if (data.success) {
        const newLogs = data.data.logs || []
        setLogs(newLogs)

        // Atualizar timestamp do último log
        if (newLogs.length > 0) {
          setLastTimestamp(newLogs[0].unix_timestamp || 0)
        }
      }
    } catch (error) {
      console.error('Erro ao buscar logs:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchNewLogs = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/system/logs?since=${lastTimestamp}`)
      const data = await response.json()

      if (data.success && data.data.logs.length > 0) {
        const newLogs = data.data.logs

        // Adicionar novos logs ao início da lista (mais recentes primeiro)
        setLogs(prevLogs => {
          const combined = [...newLogs, ...prevLogs]
          // Manter apenas os últimos 500 logs para performance
          return combined.slice(0, 500)
        })

        // Atualizar timestamp
        setLastTimestamp(newLogs[0].unix_timestamp || lastTimestamp)
      }
    } catch (error) {
      console.error('Erro ao buscar novos logs:', error)
    }
  }

  const filterLogs = () => {
    let filtered = logs

    // Filtrar por nível
    if (levelFilter !== 'all') {
      filtered = filtered.filter(log => log.level === levelFilter)
    }

    // Filtrar por termo de busca
    if (searchTerm) {
      filtered = filtered.filter(log => 
        log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.source?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    setFilteredLogs(filtered)
  }

  const clearLogs = async () => {
    if (!confirm('Tem certeza que deseja limpar todos os logs?')) return
    
    try {
      const response = await fetch('http://localhost:5000/api/system/logs', {
        method: 'DELETE'
      })
      
      if (response.ok) {
        setLogs([])
        setFilteredLogs([])
      }
    } catch (error) {
      console.error('Erro ao limpar logs:', error)
    }
  }

  const downloadLogs = () => {
    const logText = filteredLogs.map(log => 
      `[${log.timestamp}] ${log.level.toUpperCase()}: ${log.message} ${log.source ? `(${log.source})` : ''}`
    ).join('\n')
    
    const blob = new Blob([logText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `logs-${new Date().toISOString().split('T')[0]}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  const getLevelIcon = (level) => {
    switch (level) {
      case 'success':
        return <CheckCircle size={16} className="text-green-400" />
      case 'error':
        return <XCircle size={16} className="text-red-400" />
      case 'warning':
        return <AlertCircle size={16} className="text-yellow-400" />
      default:
        return <Info size={16} className="text-blue-400" />
    }
  }

  const getLevelColor = (level) => {
    switch (level) {
      case 'success':
        return 'border-l-green-400 bg-green-400 bg-opacity-5'
      case 'error':
        return 'border-l-red-400 bg-red-400 bg-opacity-5'
      case 'warning':
        return 'border-l-yellow-400 bg-yellow-400 bg-opacity-5'
      default:
        return 'border-l-blue-400 bg-blue-400 bg-opacity-5'
    }
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('pt-BR')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Logs do Sistema</h1>
          <p className="text-gray-400 mt-1">
            Monitore atividades e erros do sistema em tempo real
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
              autoRefresh 
                ? 'bg-green-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <RefreshCw size={18} className={autoRefresh ? 'animate-spin' : ''} />
            <span>{autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}</span>
          </button>
          <button
            onClick={downloadLogs}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            <Download size={18} />
            <span>Baixar</span>
          </button>
          <button
            onClick={clearLogs}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center space-x-2"
          >
            <Trash2 size={18} />
            <span>Limpar</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="relative">
              <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar nos logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Filter size={18} className="text-gray-400" />
            <select
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value)}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {logLevels.map(level => (
                <option key={level.value} value={level.value}>
                  {level.label}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2 disabled:opacity-50"
          >
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
            <span>Atualizar</span>
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {logLevels.slice(1).map(level => {
          const count = logs.filter(log => log.level === level.value).length
          return (
            <div key={level.value} className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">{level.label}</p>
                  <p className="text-2xl font-bold text-white">{count}</p>
                </div>
                <div className={`p-2 rounded-lg bg-${level.color}-500 bg-opacity-20`}>
                  {getLevelIcon(level.value)}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Logs List */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white flex items-center space-x-2">
              <Terminal size={20} />
              <span>Logs Recentes</span>
            </h2>
            <span className="text-sm text-gray-400">
              {filteredLogs.length} de {logs.length} logs
            </span>
          </div>
        </div>
        
        <div className="max-h-96 overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center">
              <RefreshCw size={32} className="animate-spin text-blue-400 mx-auto mb-4" />
              <p className="text-gray-400">Carregando logs...</p>
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="p-8 text-center">
              <Terminal size={32} className="text-gray-400 mx-auto mb-4" />
              <p className="text-gray-400">Nenhum log encontrado</p>
            </div>
          ) : (
            <div className="space-y-1">
              {filteredLogs.map((log, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.02 }}
                  className={`p-3 border-l-4 ${getLevelColor(log.level)} hover:bg-gray-700 hover:bg-opacity-50 transition-colors`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      {getLevelIcon(log.level)}
                      <div className="flex-1">
                        <p className="text-white text-sm font-mono">{log.message}</p>
                        {log.source && (
                          <p className="text-gray-400 text-xs mt-1">Fonte: {log.source}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-gray-400">
                      <Clock size={12} />
                      <span>{formatTimestamp(log.timestamp)}</span>
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

export default Logs
