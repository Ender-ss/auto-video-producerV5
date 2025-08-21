/**
 * 📝 Custom Prompt Manager
 * 
 * Componente para gerenciar prompts personalizados
 */

import React, { useState, useEffect } from 'react'
import { 
  Save, 
  Trash2, 
  Edit, 
  Plus, 
  Search, 
  Tag, 
  Clock,
  CheckCircle,
  AlertCircle,
  Copy,
  Download,
  Upload
} from 'lucide-react'

const CustomPromptManager = ({ 
  onSelectPrompt, 
  selectedPromptId = null,
  showInModal = false 
}) => {
  const [prompts, setPrompts] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [showForm, setShowForm] = useState(false)
  const [editingPrompt, setEditingPrompt] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    prompt_text: '',
    category: 'geral'
  })
  const [message, setMessage] = useState({ type: '', text: '' })

  const categories = [
    { value: 'all', label: '📋 Todos' },
    { value: 'geral', label: '📝 Geral' },
    { value: 'titulos', label: '🎯 Títulos' },
    { value: 'premissas', label: '📖 Premissas' },
    { value: 'roteiros', label: '🎬 Roteiros' },
    { value: 'marketing', label: '📢 Marketing' }
  ]

  useEffect(() => {
    loadPrompts()
  }, [])

  const loadPrompts = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/settings/custom-prompts')
      const data = await response.json()
      
      if (data.success) {
        setPrompts(data.prompts)
      } else {
        showMessage('error', data.error || 'Erro ao carregar prompts')
      }
    } catch (error) {
      showMessage('error', 'Erro ao conectar com o servidor')
    } finally {
      setLoading(false)
    }
  }

  const savePrompt = async () => {
    try {
      if (!formData.name.trim() || !formData.prompt_text.trim()) {
        showMessage('error', 'Nome e texto do prompt são obrigatórios')
        return
      }

      setLoading(true)
      
      const url = editingPrompt 
        ? `/api/settings/custom-prompts/${editingPrompt.id}`
        : '/api/settings/custom-prompts'
      
      const method = editingPrompt ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      const data = await response.json()
      
      if (data.success) {
        showMessage('success', data.message)
        setShowForm(false)
        setEditingPrompt(null)
        setFormData({ name: '', prompt_text: '', category: 'geral' })
        loadPrompts()
      } else {
        showMessage('error', data.error || 'Erro ao salvar prompt')
      }
    } catch (error) {
      showMessage('error', 'Erro ao conectar com o servidor')
    } finally {
      setLoading(false)
    }
  }

  const deletePrompt = async (promptId, promptName) => {
    if (!confirm(`Tem certeza que deseja deletar o prompt "${promptName}"?`)) {
      return
    }

    try {
      setLoading(true)
      const response = await fetch(`/api/settings/custom-prompts/${promptId}`, {
        method: 'DELETE'
      })
      
      const data = await response.json()
      
      if (data.success) {
        showMessage('success', data.message)
        loadPrompts()
      } else {
        showMessage('error', data.error || 'Erro ao deletar prompt')
      }
    } catch (error) {
      showMessage('error', 'Erro ao conectar com o servidor')
    } finally {
      setLoading(false)
    }
  }

  const editPrompt = (prompt) => {
    setEditingPrompt(prompt)
    setFormData({
      name: prompt.name,
      prompt_text: prompt.prompt_text,
      category: prompt.category
    })
    setShowForm(true)
  }

  const copyPrompt = (promptText) => {
    navigator.clipboard.writeText(promptText)
    showMessage('success', 'Prompt copiado para a área de transferência!')
  }

  const showMessage = (type, text) => {
    setMessage({ type, text })
    setTimeout(() => setMessage({ type: '', text: '' }), 3000)
  }

  const filteredPrompts = prompts.filter(prompt => {
    const matchesSearch = prompt.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         prompt.prompt_text.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || prompt.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className={`${showInModal ? 'max-h-96 overflow-y-auto' : ''}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          📝 Prompts Personalizados
        </h3>
        <button
          onClick={() => {
            setShowForm(true)
            setEditingPrompt(null)
            setFormData({ name: '', prompt_text: '', category: 'geral' })
          }}
          className="bg-blue-600 text-white px-3 py-1 rounded-lg hover:bg-blue-700 flex items-center gap-2 text-sm"
        >
          <Plus className="w-4 h-4" />
          Novo Prompt
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
              placeholder="Buscar por nome ou conteúdo..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">🏷️ Categoria</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
          <h4 className="font-semibold mb-3">
            {editingPrompt ? '✏️ Editar Prompt' : '➕ Novo Prompt'}
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">Nome</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Nome do prompt..."
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Categoria</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {categories.slice(1).map(cat => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Texto do Prompt</label>
            <textarea
              value={formData.prompt_text}
              onChange={(e) => setFormData(prev => ({ ...prev, prompt_text: e.target.value }))}
              placeholder="Digite o texto do prompt..."
              rows={6}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={savePrompt}
              disabled={loading}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              {loading ? 'Salvando...' : 'Salvar'}
            </button>
            <button
              onClick={() => {
                setShowForm(false)
                setEditingPrompt(null)
                setFormData({ name: '', prompt_text: '', category: 'geral' })
              }}
              className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {/* Prompts List */}
      {loading && !showForm ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Carregando prompts...</p>
        </div>
      ) : filteredPrompts.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {searchTerm || selectedCategory !== 'all' 
            ? 'Nenhum prompt encontrado com os filtros aplicados'
            : 'Nenhum prompt salvo ainda. Crie seu primeiro prompt!'
          }
        </div>
      ) : (
        <div className="space-y-3">
          {filteredPrompts.map(prompt => (
            <div
              key={prompt.id}
              className={`border rounded-lg p-4 transition-all ${
                selectedPromptId === prompt.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{prompt.name}</h4>
                  <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                    <Tag className="w-3 h-3" />
                    <span>{categories.find(c => c.value === prompt.category)?.label || prompt.category}</span>
                    <Clock className="w-3 h-3 ml-2" />
                    <span>{new Date(prompt.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                
                <div className="flex gap-1">
                  {onSelectPrompt && (
                    <button
                      onClick={() => onSelectPrompt(prompt)}
                      className="p-1 text-blue-600 hover:bg-blue-100 rounded"
                      title="Usar este prompt"
                    >
                      <CheckCircle className="w-4 h-4" />
                    </button>
                  )}
                  <button
                    onClick={() => copyPrompt(prompt.prompt_text)}
                    className="p-1 text-gray-600 hover:bg-gray-100 rounded"
                    title="Copiar prompt"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => editPrompt(prompt)}
                    className="p-1 text-blue-600 hover:bg-blue-100 rounded"
                    title="Editar prompt"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deletePrompt(prompt.id, prompt.name)}
                    className="p-1 text-red-600 hover:bg-red-100 rounded"
                    title="Deletar prompt"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded border">
                <div className="max-h-20 overflow-y-auto">
                  {prompt.prompt_text && prompt.prompt_text.length > 200 
                    ? `${prompt.prompt_text.substring(0, 200)}...`
                    : prompt.prompt_text || ''
                  }
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default CustomPromptManager
