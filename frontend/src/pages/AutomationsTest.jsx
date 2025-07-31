/**
 * 🧪 Automations Test Page
 * 
 * Página de teste simples para verificar se o problema é específico
 */

import React from 'react'

const AutomationsTest = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Teste de Automações</h1>
        <p className="text-gray-400 mt-1">
          Esta é uma página de teste simples
        </p>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-4">Teste Básico</h2>
        <p className="text-gray-300">
          Se você está vendo esta página, o roteamento está funcionando.
        </p>
        
        <div className="mt-4 p-4 bg-green-900/30 border border-green-700 rounded-lg">
          <p className="text-green-300">
            ✅ React está funcionando
          </p>
          <p className="text-green-300">
            ✅ Roteamento está funcionando
          </p>
          <p className="text-green-300">
            ✅ Tailwind CSS está funcionando
          </p>
        </div>
      </div>
    </div>
  )
}

export default AutomationsTest
