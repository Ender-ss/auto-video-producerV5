/**
 * 🤖 Automations Page - Simplified Version
 * 
 * Versão simplificada para identificar problemas
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Youtube,
  RefreshCw,
  Settings,
  Plus,
  Eye,
  Clock,
  Calendar,
  Copy,
  FileText,
  TrendingUp
} from 'lucide-react'
import AutomationResults from '../components/AutomationResults'

const AutomationsSimple = () => {
  const [activeTab, setActiveTab] = useState('youtube')
  const [isProcessing, setIsProcessing] = useState(false)
  const [results, setResults] = useState(null)
  const [showResults, setShowResults] = useState(false)
  const [automationResults, setAutomationResults] = useState(null)

  // Estado para o formulário de extração do YouTube
  const [formData, setFormData] = useState({
    url: '',
    max_titles: 10,
    min_views: 1000,
    max_views: '',
    days: 30
  })

  // Estado das APIs
  const [apiKeys, setApiKeys] = useState({
    rapidapi: ''
  })

  const [apiStatus, setApiStatus] = useState({
    rapidapi: 'unknown'
  })

  // Carregar chaves das APIs do localStorage
  useEffect(() => {
    const savedKeys = localStorage.getItem('api_keys')
    if (savedKeys) {
      setApiKeys(JSON.parse(savedKeys))
    }
  }, [])

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const formatNumber = (num) => {
    if (!num) return '0'
    
    const number = parseInt(num)
    if (number >= 1000000000) {
      return (number / 1000000000).toFixed(1) + 'B'
    } else if (number >= 1000000) {
      return (number / 1000000).toFixed(1) + 'M'
    } else if (number >= 1000) {
      return (number / 1000).toFixed(1) + 'K'
    }
    return number.toLocaleString()
  }

  const handleTestAPI = async () => {
    if (!apiKeys.rapidapi) {
      alert('Configure a chave RapidAPI primeiro')
      return
    }

    setApiStatus(prev => ({ ...prev, rapidapi: 'testing' }))

    try {
      const response = await fetch('http://localhost:5000/api/settings/test-api', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_name: 'rapidapi',
          api_key: apiKeys.rapidapi
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setApiStatus(prev => ({ ...prev, rapidapi: 'connected' }))
        alert('✅ RapidAPI: Conectado com sucesso!')
      } else {
        setApiStatus(prev => ({ ...prev, rapidapi: 'error' }))
        alert(`❌ RapidAPI: ${data.message}`)
      }
    } catch (error) {
      setApiStatus(prev => ({ ...prev, rapidapi: 'error' }))
      alert(`❌ Erro de conexão: ${error.message}`)
    }
  }

  const handleExtractContent = async () => {
    if (!formData.url.trim()) {
      alert('Por favor, insira o ID do canal do YouTube')
      return
    }
    
    if (!apiKeys.rapidapi) {
      alert('Configure a chave RapidAPI nas Configurações primeiro')
      return
    }

    setIsProcessing(true)
    setResults(null)
    
    // Informar sobre o sistema de rate limiting
    alert('ℹ️ Iniciando extração... O sistema agora inclui delays automáticos para evitar erros de rate limiting da API.')
    
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 120000)
      
      const response = await fetch('http://localhost:5000/api/automations/extract-youtube', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: formData.url,
          api_key: apiKeys.rapidapi,
          config: {
            max_titles: parseInt(formData.max_titles),
            min_views: parseInt(formData.min_views),
            max_views: formData.max_views ? parseInt(formData.max_views) : 0,
            days: parseInt(formData.days)
          }
        }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)
      const data = await response.json()
      
      if (data.success) {
        setResults(data.data)
        if (data.data.total_videos === 0) {
          alert('⚠️ Nenhum vídeo encontrado com os filtros aplicados.')
        }
      } else {
        alert(`❌ Erro: ${data.error}`)
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        alert('⏱️ Operação cancelada por timeout.')
      } else {
        alert(`❌ Erro de conexão: ${error.message}`)
      }
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Automações de Conteúdo</h1>
        <p className="text-gray-400 mt-1">
          Extraia títulos de vídeos populares do YouTube para inspiração
        </p>
      </div>

      {/* Main Content */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-white mb-4">
            📺 Extração de Conteúdo do YouTube
          </h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Canal do YouTube
                </label>
                <input
                  type="text"
                  value={formData.url}
                  onChange={(e) => handleInputChange('url', e.target.value)}
                  placeholder="LinusTechTips ou UCX6OQ3DkcsbYNE6H8uQQuVA ou @LinusTechTips"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
                <div className="mt-2 p-3 bg-green-900/30 border border-green-700 rounded-lg">
                  <p className="text-green-300 text-sm font-medium mb-1">
                    ✅ Agora você pode usar:
                  </p>
                  <ul className="text-green-200 text-xs space-y-1">
                    <li>• <strong>Nome do canal:</strong> LinusTechTips</li>
                    <li>• <strong>Handle:</strong> @LinusTechTips</li>
                    <li>• <strong>ID do canal:</strong> UCX6OQ3DkcsbYNE6H8uQQuVA</li>
                    <li>• <strong>URL completa:</strong> https://youtube.com/@LinusTechTips</li>
                  </ul>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Máx. Títulos
                  </label>
                  <input
                    type="number"
                    value={formData.max_titles}
                    onChange={(e) => handleInputChange('max_titles', e.target.value)}
                    min="1"
                    max="50"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Min. Views
                  </label>
                  <input
                    type="number"
                    value={formData.min_views}
                    onChange={(e) => handleInputChange('min_views', e.target.value)}
                    min="0"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>
              </div>

              <button
                onClick={handleExtractContent}
                disabled={isProcessing}
                className="w-full px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
              >
                {isProcessing ? (
                  <>
                    <RefreshCw size={18} className="animate-spin" />
                    <span>Extraindo... (pode demorar até 2 min)</span>
                  </>
                ) : (
                  <>
                    <Youtube size={18} />
                    <span>Extrair Conteúdo</span>
                  </>
                )}
              </button>
            </div>

            {/* Results */}
            <div>
              {results ? (
                <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                  <h3 className="text-lg font-semibold text-white mb-4">📝 Títulos Extraídos</h3>
                  
                  {results.videos && results.videos.length > 0 ? (
                    <div className="space-y-2">
                      {results.videos.map((video, index) => (
                        <div key={index} className="bg-gray-600 rounded p-3">
                          <p className="text-white text-sm font-medium mb-1">
                            {index + 1}. {video.title}
                          </p>
                          <div className="flex items-center space-x-3 text-xs text-gray-300">
                            <span className="flex items-center space-x-1">
                              <Eye size={12} />
                              <span>{formatNumber(video.views)} views</span>
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400">Nenhum título encontrado</p>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <FileText size={48} className="mx-auto mb-4 text-gray-500 opacity-50" />
                  <h3 className="text-lg font-medium text-white mb-2">📝 Extrair Títulos</h3>
                  <p className="text-gray-400 text-sm">
                    Configure os parâmetros e clique em "Extrair Conteúdo"
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AutomationsSimple
