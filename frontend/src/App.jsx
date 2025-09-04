/**
 * 🎬 Auto Video Producer - Main App Component
 * 
 * Componente principal da aplicação
 */

import React, { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'

// Components
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import LoadingSpinner from './components/LoadingSpinner'

// Pages
import Dashboard from './pages/Dashboard'
import Channels from './pages/Channels'
import AutomationsMain from './pages/AutomationsMain'
import AutomationsDev from './pages/AutomationsDev'
import AgentRoteirosSimples from './pages/AgentRoteirosSimples'
import Pipeline from './pages/Pipeline'
import Videos from './pages/Videos'
import Settings from './pages/Settings'
import SettingsTest from './pages/SettingsTest'
import SettingsDebug from './pages/SettingsDebug'
import Analytics from './pages/Analytics'
import Logs from './pages/Logs'
import ApiTests from './pages/ApiTests';
import ImageGeneration from './pages/ImageGeneration';
import ImageQueue from './pages/ImageQueue';
import YouTubeExtractTest from './pages/YouTubeExtractTest';
import YouTubeExtractComparison from './pages/YouTubeExtractComparison';
import ScreenplayGeneratorTest from './pages/ScreenplayGeneratorTest';
import LongScriptGenerator from './pages/LongScriptGenerator';
import LongScriptTest from './pages/LongScriptTest';
import PromptsConfig from './pages/PromptsConfig';
import ConteudosGerados from './pages/ConteudosGerados';
import StorytellerDemo from './pages/StorytellerDemo';

// Mock system status for demo
const mockSystemStatus = {
  ready_for_production: true,
  apis_configured: {
    text_models: true,
    tts_services: true,
    image_services: true,
    youtube_api: true
  },
  available_services: {
    text_models: ['gemini:gemini-1.5-flash', 'openai:gpt-3.5-turbo'],
    tts_services: ['gemini', 'edge'],
    image_services: ['flux']
  }
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [isLoading, setIsLoading] = useState(true)
  const [systemReady, setSystemReady] = useState(false)

  // Initialize app
  useEffect(() => {
    const initializeApp = async () => {
      try {
        setIsLoading(true)

        // Verificação rápida do sistema
        await new Promise(resolve => setTimeout(resolve, 500))

        setSystemReady(true)
        toast.success('🎬 Sistema pronto para uso!')

      } catch (error) {
        console.error('Erro na inicialização:', error)
        toast.error('❌ Erro ao conectar com o servidor')
      } finally {
        setIsLoading(false)
      }
    }

    initializeApp()
  }, [])

  // Loading screen
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🎬</div>
          <h1 className="text-2xl font-bold text-white mb-2">
            Auto Video Producer
          </h1>
          <p className="text-gray-400 mb-6">
            Inicializando sistema de produção automática...
          </p>
          <LoadingSpinner size="lg" />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="flex">
        {/* Sidebar */}
        <AnimatePresence>
          {sidebarOpen && (
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="fixed inset-y-0 left-0 z-50 w-70 lg:relative lg:z-auto"
            >
              <Sidebar onClose={() => setSidebarOpen(false)} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <div className="flex-1 flex flex-col min-h-screen">
          {/* Header */}
          <Header 
            onMenuClick={() => setSidebarOpen(!sidebarOpen)}
            systemStatus={mockSystemStatus}
          />

          {/* Page Content */}
          <main className="flex-1 p-6">
            <AnimatePresence mode="wait">
              <Routes>
                <Route 
                  path="/" 
                  element={
                    <motion.div
                      key="dashboard"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Dashboard />
                    </motion.div>
                  } 
                />
                
                <Route
                  path="/channels"
                  element={
                    <motion.div
                      key="channels"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Channels />
                    </motion.div>
                  }
                />

                <Route
                  path="/automations-dev"
                  element={
                    <motion.div
                      key="automations-dev"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <AutomationsDev />
                    </motion.div>
                  }
                />

                <Route
                  path="/automations"
                  element={
                    <motion.div
                      key="automations"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <AutomationsMain />
                    </motion.div>
                  }
                />

                <Route
                  path="/agente-roteiros"
                  element={
                    <motion.div
                      key="agente-roteiros"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <AgentRoteirosSimples />
                    </motion.div>
                  }
                />

                <Route
                  path="/pipeline"
                  element={
                    <motion.div
                      key="pipeline"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Pipeline />
                    </motion.div>
                  } 
                />
                
                <Route 
                  path="/videos" 
                  element={
                    <motion.div
                      key="videos"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Videos />
                    </motion.div>
                  } 
                />
                
                <Route 
                  path="/conteudos-gerados" 
                  element={
                    <motion.div
                      key="conteudos-gerados"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ConteudosGerados />
                    </motion.div>
                  } 
                />
                
                <Route 
                  path="/analytics" 
                  element={
                    <motion.div
                      key="analytics"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Analytics />
                    </motion.div>
                  } 
                />
                
                <Route
                  path="/settings"
                  element={
                    <motion.div
                      key="settings"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Settings />
                    </motion.div>
                  }
                />

                <Route
                  path="/prompts-config"
                  element={
                    <motion.div
                      key="prompts-config"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <PromptsConfig />
                    </motion.div>
                  }
                />

                <Route
                  path="/settings-test"
                  element={
                    <motion.div
                      key="settings-test"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <SettingsTest />
                    </motion.div>
                  }
                />

                <Route
                  path="/settings-debug"
                  element={
                    <motion.div
                      key="settings-debug"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <SettingsDebug />
                    </motion.div>
                  }
                />

                <Route
                  path="/logs"
                  element={
                    <motion.div
                      key="logs"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Logs />
                    </motion.div>
                  }
                />

                <Route
                  path="/api-tests"
                  element={
                    <motion.div
                      key="api-tests"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ApiTests />
                    </motion.div>
                  }
                />

                <Route
                  path="/image-generation"
                  element={
                    <motion.div
                      key="image-generation"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ImageGeneration />
                    </motion.div>
                  }
                />

                <Route
                  path="/image-queue"
                  element={
                    <motion.div
                      key="image-queue"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ImageQueue />
                    </motion.div>
                  }
                />

                <Route
                  path="/youtube-test"
                  element={
                    <motion.div
                      key="youtube-test"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <YouTubeExtractTest />
                    </motion.div>
                  }
                />

                <Route
                  path="/youtube-comparison"
                  element={
                    <motion.div
                      key="youtube-comparison"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <YouTubeExtractComparison />
                    </motion.div>
                  }
                />

                {/* Screenplay Generator Test */}
                <Route
                  path="/screenplay-test"
                  element={
                    <motion.div
                      key="screenplay-test"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ScreenplayGeneratorTest />
                    </motion.div>
                  }
                />

                {/* Long Script Generator */}
                <Route
                  path="/long-script-generator"
                  element={
                    <motion.div
                      key="long-script-generator"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <LongScriptGenerator />
                    </motion.div>
                  }
                />

                {/* Long Script Test */}
                <Route
                  path="/long-script-test"
                  element={
                    <motion.div
                      key="long-script-test"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <LongScriptTest />
                    </motion.div>
                  }
                />

                {/* Storyteller Unlimited Demo */}
                <Route
                  path="/storyteller-demo"
                  element={
                    <motion.div
                      key="storyteller-demo"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <StorytellerDemo />
                    </motion.div>
                  }
                />

                {/* Redirect unknown routes to dashboard */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </AnimatePresence>
          </main>
        </div>
      </div>

      {/* Overlay for mobile sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

export default App
