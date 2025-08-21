/**
 * 🎬 Auto Video Producer - Main Entry Point
 * 
 * Ponto de entrada principal da aplicação React
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ReactQueryDevtools } from 'react-query/devtools'
import { Toaster } from 'react-hot-toast'

import App from './App.jsx'
import './index.css'

// Configurar React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutos
      cacheTime: 10 * 60 * 1000, // 10 minutos
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
})

// Configurar toast notifications
const toastOptions = {
  duration: 4000,
  position: 'top-right',
  style: {
    background: '#1f2937',
    color: '#f9fafb',
    border: '1px solid #374151',
    borderRadius: '8px',
    fontSize: '14px',
    maxWidth: '400px',
  },
  success: {
    iconTheme: {
      primary: '#10b981',
      secondary: '#f9fafb',
    },
  },
  error: {
    iconTheme: {
      primary: '#ef4444',
      secondary: '#f9fafb',
    },
  },
  loading: {
    iconTheme: {
      primary: '#3b82f6',
      secondary: '#f9fafb',
    },
  },
}

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    })
    
    // Log error to console in development
    if (import.meta.env.DEV) {
      console.error('Error Boundary caught an error:', error, errorInfo)
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-gray-800 rounded-lg p-6 text-center">
            <div className="text-6xl mb-4">🚨</div>
            <h1 className="text-2xl font-bold text-white mb-2">
              🚨 Ops! Algo não saiu como esperado
            </h1>
            <p className="text-gray-400 mb-4">
              Encontramos um problema técnico. Não se preocupe, isso pode acontecer!
            </p>
            <div className="bg-blue-900/30 border border-blue-600/50 rounded-lg p-3 mb-4">
              <p className="text-blue-300 text-sm">
                💡 <strong>O que você pode fazer:</strong>
              </p>
              <ul className="text-blue-200 text-sm mt-2 space-y-1">
                <li>• Recarregue a página (botão abaixo)</li>
                <li>• Verifique sua conexão com a internet</li>
                <li>• Tente novamente em alguns minutos</li>
              </ul>
            </div>
            
            {import.meta.env.DEV && this.state.error && (
              <details className="text-left bg-gray-900 p-3 rounded mb-4">
                <summary className="cursor-pointer text-red-400 font-mono text-sm">
                  Detalhes do erro (desenvolvimento)
                </summary>
                <pre className="text-xs text-gray-300 mt-2 overflow-auto">
                  {this.state.error.toString()}
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
            
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Recarregar Página
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Initialize app
const root = ReactDOM.createRoot(document.getElementById('root'))

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
          <Toaster toastOptions={toastOptions} />
          {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>
)

// Hot Module Replacement (HMR) - Vite
if (import.meta.hot) {
  import.meta.hot.accept()
}
