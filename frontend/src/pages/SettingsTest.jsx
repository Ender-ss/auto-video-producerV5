/**
 * 🧪 Settings Test Page - Para testar múltiplas chaves Gemini
 */

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Key, Zap, Save } from 'lucide-react'

const SettingsTest = () => {
  const [apiKeys, setApiKeys] = useState({
    gemini_1: '',
    gemini_2: '',
    gemini_3: '',
    gemini_4: '',
    gemini_5: '',
    gemini_6: '',
    gemini_7: '',
    gemini_8: '',
    gemini_9: '',
    gemini_10: ''
  })

  const handleInputChange = (key, value) => {
    setApiKeys(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleSave = async () => {
    try {
      const response = await fetch('/api/settings/api-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiKeys)
      })
      
      if (response.ok) {
        alert('✅ Chaves salvas com sucesso!')
      } else {
        alert('❌ Erro ao salvar chaves')
      }
    } catch (error) {
      alert('❌ Erro: ' + error.message)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            🧪 Teste - Múltiplas Chaves Gemini
          </h1>
          <p className="text-gray-400">
            Página de teste para configurar múltiplas chaves Gemini
          </p>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <div className="flex items-center space-x-2 mb-6">
            <Zap size={24} className="text-blue-400" />
            <h2 className="text-xl font-semibold text-white">
              Google Gemini - Rotação de Chaves
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {[1,2,3,4,5,6,7,8,9,10].map(num => (
              <div key={num} className="bg-gray-700 rounded-lg p-4">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Gemini Chave {num}
                </label>
                <input
                  type="password"
                  value={apiKeys[`gemini_${num}`] || ''}
                  onChange={(e) => handleInputChange(`gemini_${num}`, e.target.value)}
                  placeholder={`Digite a chave Gemini ${num}...`}
                  className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
          </div>

          <button
            onClick={handleSave}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Save size={18} />
            <span>Salvar Chaves</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default SettingsTest
