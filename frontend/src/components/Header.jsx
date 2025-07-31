/**
 * 📱 Header Component
 * 
 * Cabeçalho da aplicação
 */

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Menu,
  Search,
  Bell,
  Settings,
  User,
  Activity,
  Wifi,
  WifiOff,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react'

const Header = ({ onMenuClick, systemStatus }) => {
  const [showNotifications, setShowNotifications] = useState(false)
  const [showProfile, setShowProfile] = useState(false)

  // Status do sistema
  const isOnline = systemStatus?.apis_configured?.youtube_api || false
  const hasErrors = !systemStatus?.ready_for_production || false

  // Notificações mock
  const notifications = [
    {
      id: 1,
      type: 'success',
      title: 'Pipeline Concluído',
      message: 'Vídeo "Como Ganhar Dinheiro Online" foi produzido com sucesso',
      time: '2 min atrás',
      icon: CheckCircle
    },
    {
      id: 2,
      type: 'warning',
      title: 'API Limit',
      message: 'OpenAI API próxima do limite diário',
      time: '15 min atrás',
      icon: AlertCircle
    },
    {
      id: 3,
      type: 'info',
      title: 'Novo Canal',
      message: 'Canal "Motivação Diária" foi adicionado',
      time: '1 hora atrás',
      icon: Activity
    }
  ]

  const getStatusColor = () => {
    if (hasErrors) return 'text-red-400'
    if (!isOnline) return 'text-yellow-400'
    return 'text-green-400'
  }

  const getStatusIcon = () => {
    if (hasErrors) return WifiOff
    if (!isOnline) return AlertCircle
    return Wifi
  }

  const StatusIcon = getStatusIcon()

  return (
    <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left Side */}
        <div className="flex items-center space-x-4">
          {/* Menu Button */}
          <button
            onClick={onMenuClick}
            className="p-2 rounded-lg hover:bg-gray-700 transition-colors lg:hidden"
          >
            <Menu size={20} className="text-gray-400" />
          </button>

          {/* Search */}
          <div className="relative hidden md:block">
            <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar canais, vídeos, pipelines..."
              className="pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-80"
            />
          </div>

          {/* System Status */}
          <div className="flex items-center space-x-2 px-3 py-1 bg-gray-700 rounded-lg">
            <StatusIcon size={16} className={getStatusColor()} />
            <span className="text-sm text-gray-300">
              {hasErrors ? 'Configuração Incompleta' : 
               !isOnline ? 'APIs Limitadas' : 
               'Sistema Online'}
            </span>
          </div>
        </div>

        {/* Right Side */}
        <div className="flex items-center space-x-4">
          {/* Quick Stats */}
          <div className="hidden lg:flex items-center space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <Zap size={16} className="text-blue-400" />
              <span className="text-gray-300">3 Ativos</span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock size={16} className="text-yellow-400" />
              <span className="text-gray-300">7 na Fila</span>
            </div>
            <div className="flex items-center space-x-2">
              <Activity size={16} className="text-green-400" />
              <span className="text-gray-300">12 Canais</span>
            </div>
          </div>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
              <Bell size={20} className="text-gray-400" />
              {notifications.length > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                  {notifications.length}
                </span>
              )}
            </button>

            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  className="absolute right-0 mt-2 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50"
                >
                  <div className="p-4 border-b border-gray-700">
                    <h3 className="text-lg font-semibold text-white">Notificações</h3>
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {notifications.map((notification) => {
                      const Icon = notification.icon
                      return (
                        <div
                          key={notification.id}
                          className="p-4 border-b border-gray-700 hover:bg-gray-700 transition-colors"
                        >
                          <div className="flex items-start space-x-3">
                            <Icon 
                              size={18} 
                              className={`mt-1 ${
                                notification.type === 'success' ? 'text-green-400' :
                                notification.type === 'warning' ? 'text-yellow-400' :
                                'text-blue-400'
                              }`} 
                            />
                            <div className="flex-1">
                              <h4 className="text-sm font-medium text-white">
                                {notification.title}
                              </h4>
                              <p className="text-sm text-gray-400 mt-1">
                                {notification.message}
                              </p>
                              <p className="text-xs text-gray-500 mt-2">
                                {notification.time}
                              </p>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Settings */}
          <button className="p-2 rounded-lg hover:bg-gray-700 transition-colors">
            <Settings size={20} className="text-gray-400" />
          </button>

          {/* Profile */}
          <div className="relative">
            <button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <User size={16} className="text-white" />
              </div>
              <span className="hidden md:block text-sm text-gray-300">Admin</span>
            </button>

            <AnimatePresence>
              {showProfile && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50"
                >
                  <div className="p-3">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                        <User size={18} className="text-white" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-white">Admin</div>
                        <div className="text-xs text-gray-400">Administrador</div>
                      </div>
                    </div>
                    <div className="border-t border-gray-700 pt-3 space-y-2">
                      <button className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded transition-colors">
                        Perfil
                      </button>
                      <button className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded transition-colors">
                        Configurações
                      </button>
                      <button className="w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-gray-700 rounded transition-colors">
                        Sair
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
