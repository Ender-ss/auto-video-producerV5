/**
 * 🔍 Debug Component
 * 
 * Componente para debug e análise de problemas de renderização
 */

import React, { useEffect } from 'react'

const DebugInfo = ({ title, data }) => {
  useEffect(() => {
    console.log(`🔍 DEBUG [${title}]:`, data)
    console.log('🔍 DEBUG - Window location:', window.location.href)
    console.log('🔍 DEBUG - Document ready state:', document.readyState)
    
    // Verificar se há erros no console
    const originalError = console.error
    console.error = (...args) => {
      console.log('🚨 ERRO CAPTURADO:', args)
      originalError.apply(console, args)
    }
    
    return () => {
      console.error = originalError
    }
  }, [title, data])

  return (
    <div className="fixed top-4 right-4 bg-red-900 border border-red-600 rounded p-3 text-white text-xs max-w-sm z-50">
      <h4 className="font-bold text-red-300 mb-2">🔍 DEBUG: {title}</h4>
      <pre className="text-red-200 overflow-auto max-h-32">
        {JSON.stringify(data, null, 2)}
      </pre>
      <div className="mt-2 text-red-300">
        <div>URL: {window.location.href}</div>
        <div>Ready: {document.readyState}</div>
      </div>
    </div>
  )
}

export default DebugInfo