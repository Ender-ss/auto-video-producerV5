/**
 * 📺 Saved Channels Manager
 * 
 * Componente para gerenciar canais salvos do YouTube
 */

import React, { useState, useEffect } from 'react'
import { 
  Save, 
  Trash2, 
  Plus, 
  Search, 
  Tag, 
  Clock,
  CheckCircle,
  AlertCircle,
  Copy,
  ExternalLink,
  Youtube
} from 'lucide-react'

const SavedChannelsManager = ({ 
  onSelectChannel, 
  selectedChannelId = null,
  showInModal = false 
}) => {
  const [channels, setChannels] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    channel_id: '',
    input_type: 'url',
    description: '',
    category: 'geral'
  })
  const [message, setMessage] = useState({ type: '', text: '' })

  const categories = [
    { value: 'all', label: '📋 Todos' },
    { value: 'geral', label: '📺 Geral' },
    { value: 'educacao', label: '🎓 Educação' },
    { value: 'entretenimento', label: '🎬 Entretenimento' },
    { value: 'tecnologia', label: '💻 Tecnologia' },
    { value: 'negocios', label: '💼 Negócios' },
    { value: 'lifestyle', label: '✨ Lifestyle' },
    { value: 'gaming', label: '🎮 Gaming' }
  ]

  useEffect(() => {
    loadChannels()
  }, [])

  const loadChannels = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/settings/saved-channels')
      const data = await response.json()
      
      if (data.success) {
        setChannels(data.channels)
      } else {
        showMessage('error', data.error || 'Erro ao carregar canais')
      }
    } catch (error) {
      showMessage('error', 'Erro ao conectar com o servidor')
    } finally {
      setLoading(false)
    }
  }

  const saveChannel = async () => {
    try {
      if (!formData.name.trim()) {
        showMessage('error', 'Nome do canal é obrigatório')
        return
      }

      // Validar baseado no tipo de entrada
      if (formData.input_type === 'url') {
        if (!formData.url.trim()) {
          showMessage('error', 'URL do canal é obrigatória quando o tipo é URL')
          return
        }
        // Validar URL do YouTube
        if (!formData.url.includes('youtube.com') && !formData.url.includes('youtu.be')) {
          showMessage('error', 'URL deve ser de um canal do YouTube')
          return
        }
      } else if (formData.input_type === 'channel_id') {
        if (!formData.channel_id.trim()) {
          showMessage('error', 'ID do canal é obrigatório quando o tipo é ID')
          return
        }
        // Validar formato do ID do canal
        if (!formData.channel_id.startsWith('UC') && !formData.channel_id.startsWith('@')) {
          showMessage('error', 'ID do canal deve começar com "UC" ou "@"')
          return
        }
      }

      setLoading(true)
      
      const response = await fetch('/api/settings/saved-channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      const data = await response.json()
      
      if (data.success) {
        showMessage('success', data.message)
        setShowForm(false)
        setFormData({ name: '', url: '', channel_id: '', input_type: 'url', description: '', category: 'geral' })
        loadChannels()
      } else {
        showMessage('error', data.error || 'Erro ao salvar canal')
      }
    } catch (error) {
      showMessage('error', 'Erro ao conectar com o servidor')
    } finally {
      setLoading(false)
    }
  }

  const deleteChannel = async (channelId, channelName) => {
    if (!confirm(`Tem certeza que deseja deletar o canal "${channelName}"?`)) {
      return
    }

    try {
      setLoading(true)
      const response = await fetch(`/api/settings/saved-channels/${channelId}`, {
        method: 'DELETE'
      })
      
      const data = await response.json()
      
      if (data.success) {
        showMessage('success', data.message)
        loadChannels()
      } else {
        showMessage('error', data.error || 'Erro ao deletar canal')
      }
    } catch (error) {
      showMessage('error', 'Erro ao conectar com o servidor')
    } finally {
      setLoading(false)
    }
  }

  const copyChannelUrl = (url) => {
    navigator.clipboard.writeText(url)
    showMessage('success', 'URL copiada para a área de transferência!')
  }

  const showMessage = (type, text) => {
    setMessage({ type, text })
    setTimeout(() => setMessage({ type: '', text: '' }), 3000)
  }

  const filteredChannels = channels.filter(channel => {
    const matchesSearch = channel.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         channel.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || channel.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className={`${showInModal ? 'max-h-96 overflow-y-auto' : ''}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          📺 Canais Salvos
        </h3>
        <button
          onClick={() => {
            setShowForm(true)
            setFormData({ name: '', url: '', channel_id: '', input_type: 'url', description: '', category: 'geral' })
          }}
          className="bg-red-600 text-white px-3 py-1 rounded-lg hover:bg-red-700 flex items-center gap-2 text-sm"
        >
          <Plus className="w-4 h-4" />
          Novo Canal
        </button>
      </div>

      {/* Message */}
      {message.text && (
        <div className={`mb-4 p-3 rounded-lg flex items-center gap-2 ${
          message.type === 'success' 
            ? 'bg-green-100 text-green-800 border border-green-200' 
            : 'bg-red-100 text-red-800 border border-red-200'
        }`}>
          {message.type === 'success' ? (
            <CheckCircle className="w-4 h-4" />
          ) : (
            <AlertCircle className="w-4 h-4" />
          )}
          {message.text}
        </div>
      )}

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium mb-1">🔍 Buscar</label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar por nome ou descrição..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">🏷️ Categoria</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
          >
            {categories.map(cat => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
          <h4 className="font-semibold mb-3">➕ Novo Canal</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">Nome do Canal</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Ex: Canal do Felipe Neto"
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Categoria</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                {categories.slice(1).map(cat => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Tipo de Entrada</label>
            <select
              value={formData.input_type}
              onChange={(e) => setFormData(prev => ({ ...prev, input_type: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            >
              <option value="url">🔗 URL do Canal</option>
              <option value="channel_id">🆔 ID do Canal</option>
            </select>
          </div>
          
          {formData.input_type === 'url' ? (
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">URL do Canal</label>
              <input
                type="url"
                value={formData.url}
                onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                placeholder="https://www.youtube.com/@canal"
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">Ex: https://www.youtube.com/@felipenetooficial</p>
            </div>
          ) : (
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">ID do Canal</label>
              <input
                type="text"
                value={formData.channel_id}
                onChange={(e) => setFormData(prev => ({ ...prev, channel_id: e.target.value }))}
                placeholder="UCxxxxxxxxxxxxxxxxxxxxxxxx ou @usuario"
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">Ex: UCxxxxxxxxxxxxxxxxxxxxxxxx ou @felipenetooficial</p>
            </div>
          )}
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Descrição (Opcional)</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Descrição do canal..."
              rows={3}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={saveChannel}
              disabled={loading}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              {loading ? 'Salvando...' : 'Salvar'}
            </button>
            <button
              onClick={() => {
                setShowForm(false)
                setFormData({ name: '', url: '', channel_id: '', input_type: 'url', description: '', category: 'geral' })
              }}
              className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {/* Channels List */}
      {loading && !showForm ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Carregando canais...</p>
        </div>
      ) : filteredChannels.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {searchTerm || selectedCategory !== 'all' 
            ? 'Nenhum canal encontrado com os filtros aplicados'
            : 'Nenhum canal salvo ainda. Adicione seu primeiro canal!'
          }
        </div>
      ) : (
        <div className="space-y-3">
          {filteredChannels.map(channel => (
            <div
              key={channel.id}
              className={`border rounded-lg p-4 transition-all ${
                selectedChannelId === channel.id
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <Youtube className="w-4 h-4 text-red-600" />
                    {channel.name}
                  </h4>
                  <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                    <Tag className="w-3 h-3" />
                    <span>{categories.find(c => c.value === channel.category)?.label || channel.category}</span>
                    <Clock className="w-3 h-3 ml-2" />
                    <span>{new Date(channel.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                
                <div className="flex gap-1">
                  {onSelectChannel && (
                    <button
                      onClick={() => onSelectChannel(channel)}
                      className="p-1 text-red-600 hover:bg-red-100 rounded"
                      title="Usar este canal"
                    >
                      <CheckCircle className="w-4 h-4" />
                    </button>
                  )}
                  <button
                    onClick={() => copyChannelUrl(channel.url)}
                    className="p-1 text-gray-600 hover:bg-gray-100 rounded"
                    title="Copiar URL"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => window.open(channel.url, '_blank')}
                    className="p-1 text-blue-600 hover:bg-blue-100 rounded"
                    title="Abrir canal"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteChannel(channel.id, channel.name)}
                    className="p-1 text-red-600 hover:bg-red-100 rounded"
                    title="Deletar canal"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded border">
                <div className="mb-2">
                  <strong>Tipo:</strong> 
                  <span className="ml-1">
                    {channel.input_type === 'channel_id' ? '🆔 ID do Canal' : '🔗 URL do Canal'}
                  </span>
                </div>
                {channel.input_type === 'channel_id' && channel.channel_id ? (
                  <div className="mb-2">
                    <strong>ID do Canal:</strong> 
                    <span className="ml-1 font-mono text-sm bg-gray-200 px-2 py-1 rounded">
                      {channel.channel_id}
                    </span>
                  </div>
                ) : (
                  <div className="mb-2">
                    <strong>URL:</strong> 
                    <a href={channel.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline ml-1">
                      {channel.url}
                    </a>
                  </div>
                )}
                {channel.description && (
                  <div>
                    <strong>Descrição:</strong> {channel.description}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SavedChannelsManager
