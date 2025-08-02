/**
 * ⚙️ Settings Page - Simplified Version
 * 
 * Página de configurações simplificada
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Key,
  Eye,
  EyeOff,
  CheckCircle,
  XCircle,
  RefreshCw,
  AlertCircle,
  Save,
  Zap
} from 'lucide-react'

const SettingsSimple = () => {
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    gemini_1: '',
    openrouter: '',
    elevenlabs: '',
    together: '',
    rapidapi: ''
  })
  const [showPasswords, setShowPasswords] = useState({})
  const [unsavedChanges, setUnsavedChanges] = useState(false)

  // Carregar chaves de API
  useEffect(() => {
    loadApiKeys()
  }, [])

  const loadApiKeys = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/settings/api-keys')
      if (response.ok) {
        const data = await response.json()
        console.log('🔍 DEBUG: Dados recebidos do backend:', data)

        if (data.success && data.keys) {
          // Mapear as chaves do backend para o formato do frontend
          const mappedKeys = {
            openai: data.keys.openai || '',
            gemini_1: data.keys.gemini || '',
            openrouter: data.keys.openrouter || '',
            elevenlabs: data.keys.elevenlabs || '',
            together: data.keys.together || '',
            rapidapi: data.keys.rapidapi || ''
          }
          console.log('🔍 DEBUG: Chaves mapeadas:', mappedKeys)
          setApiKeys(mappedKeys)
        }
      }
    } catch (error) {
      console.error('Erro ao carregar chaves de API:', error)
    }
  }

  const saveApiKeys = async () => {
    try {
      console.log('🔍 DEBUG: Salvando chaves:', apiKeys)

      const response = await fetch('http://localhost:5000/api/settings/api-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiKeys),
      })

      if (response.ok) {
        setUnsavedChanges(false)
        alert('Configurações salvas com sucesso!')
        // Recarregar as chaves para confirmar que foram salvas
        loadApiKeys()
      } else {
        const errorData = await response.json()
        console.error('Erro do servidor:', errorData)
        alert('Erro ao salvar configurações')
      }
    } catch (error) {
      console.error('Erro ao salvar chaves de API:', error)
      alert('Erro ao salvar configurações')
    }
  }

  const handleApiKeyChange = (key, value) => {
    setApiKeys(prev => ({ ...prev, [key]: value }))
    setUnsavedChanges(true)
  }

  const togglePasswordVisibility = (key) => {
    setShowPasswords(prev => ({ ...prev, [key]: !prev[key] }))
  }

  const apis = [
    { key: 'openai', name: 'OpenAI GPT-4', description: 'Melhor qualidade para títulos e roteiros' },
    { key: 'gemini_1', name: 'Google Gemini', description: 'Gratuito - Recomendado para começar' },
    { key: 'openrouter', name: 'OpenRouter', description: 'Acesso a múltiplos modelos (Claude, Llama, etc.)' },
    { key: 'elevenlabs', name: 'ElevenLabs', description: 'Text-to-Speech de alta qualidade' },
    { key: 'together', name: 'Together.ai FLUX', description: 'Geração de imagens gratuita' },
    { key: 'rapidapi', name: 'RapidAPI YouTube', description: 'Extração de dados do YouTube' }
  ]

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Configurações de API</h1>
            <p className="text-gray-400 mt-1">
              Configure suas chaves de API para habilitar todas as funcionalidades
            </p>
          </div>
          {unsavedChanges && (
            <button
              onClick={saveApiKeys}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
            >
              <Save size={18} />
              <span>Salvar Alterações</span>
            </button>
          )}
        </div>

        {/* APIs */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <div className="flex items-center space-x-2 mb-6">
            <Zap size={20} className="text-blue-400" />
            <h2 className="text-xl font-semibold text-white">Chaves de API</h2>
          </div>

          <div className="space-y-4">
            {apis.map((api) => (
              <div key={api.key} className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-medium text-white">{api.name}</h4>
                    <p className="text-sm text-gray-400">{api.description}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <div className="relative flex-1">
                    <input
                      type={showPasswords[api.key] ? 'text' : 'password'}
                      value={apiKeys[api.key] || ''}
                      onChange={(e) => handleApiKeyChange(api.key, e.target.value)}
                      placeholder={`Digite sua chave ${api.name}`}
                      className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <button
                    onClick={() => togglePasswordVisibility(api.key)}
                    className="p-2 text-gray-400 hover:text-white transition-colors"
                  >
                    {showPasswords[api.key] ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Instruções */}
          <div className="mt-6 p-4 bg-blue-900/20 border border-blue-600 rounded-lg">
            <h3 className="text-blue-400 font-medium mb-2">💡 Como obter as chaves:</h3>
            <ul className="text-blue-200 text-sm space-y-1">
              <li>• <strong>Google Gemini</strong>: <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="underline">Google AI Studio</a> (Gratuito)</li>
              <li>• <strong>OpenAI</strong>: <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="underline">OpenAI Platform</a></li>
              <li>• <strong>OpenRouter</strong>: <a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer" className="underline">OpenRouter</a></li>
              <li>• <strong>ElevenLabs</strong>: <a href="https://elevenlabs.io/app/speech-synthesis" target="_blank" rel="noopener noreferrer" className="underline">ElevenLabs</a></li>
              <li>• <strong>Together.ai</strong>: <a href="https://api.together.xyz/settings/api-keys" target="_blank" rel="noopener noreferrer" className="underline">Together.ai</a></li>
              <li>• <strong>RapidAPI</strong>: <a href="https://rapidapi.com/hub" target="_blank" rel="noopener noreferrer" className="underline">RapidAPI</a></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SettingsSimple
