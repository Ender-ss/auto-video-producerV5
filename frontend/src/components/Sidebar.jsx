/**
 * 📱 Sidebar Component
 * 
 * Barra lateral de navegação
 */

import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Home,
  Youtube,
  Clapperboard,
  Video,
  BarChart3,
  Settings,
  X,
  Zap,
  Clock,
  Users,
  TrendingUp,
  FileText,
  TestTube,
  PenSquare,
  MessageSquare
} from 'lucide-react'

const Sidebar = ({ onClose }) => {
  const location = useLocation()

  const menuItems = [
    {
      path: '/',
      icon: Home,
      label: 'Dashboard',
      description: 'Visão geral do sistema'
    },
    {
      path: '/channels',
      icon: Youtube,
      label: 'Canais',
      description: 'Gerenciar canais monitorados'
    },
    {
      path: '/automations',
      icon: Zap,
      label: 'Automações',
      description: 'Sistema principal de automações'
    },
    {
      path: '/image-generation',
      icon: Zap,
      label: 'Geração de Imagens',
      description: 'Criar imagens com IA'
    },
    {
      path: '/image-queue',
      icon: Clock,
      label: 'Fila de Imagens',
      description: 'Geração em lote e prompts automáticos'
    },
    {
      path: '/pipeline',
      icon: Clapperboard,
      label: 'Pipeline',
      description: 'Monitorar produção'
    },
    {
      path: '/videos',
      icon: Video,
      label: 'Vídeos',
      description: 'Biblioteca de vídeos'
    },
    {
      path: '/conteudos-gerados',
      icon: FileText,
      label: 'Conteúdos Gerados',
      description: 'Visualizar arquivos gerados'
    },
    {
      path: '/analytics',
      icon: BarChart3,
      label: 'Analytics',
      description: 'Estatísticas e relatórios'
    },
    {
      path: '/logs',
      icon: FileText,
      label: 'Logs',
      description: 'Logs do sistema'
    },
    {
      path: '/api-tests',
      icon: TestTube,
      label: 'Testes de API',
      description: 'Diagnóstico de APIs'
    },
    {
      path: '/settings',
      icon: Settings,
      label: 'Configurações',
      description: 'APIs e preferências'
    },
    {
      path: '/prompts-config',
      icon: MessageSquare,
      label: 'Configuração de Prompts',
      description: 'Personalizar prompts da automação'
    },
    {
      path: '/automations-dev',
      icon: Zap,
      label: '🔧 DEV: Automações',
      description: 'Versão de desenvolvimento'
    },
    {
      path: '/agente-roteiros',
      icon: Zap,
      label: '🤖 DEV: Agente Simples',
      description: 'Agente simplificado (desenvolvimento)'
    },
    {
      path: '/screenplay-test',
      icon: PenSquare,
      label: '🧪 DEV: Roteiro Longo',
      description: 'Gerador de roteiros longos (teste)'
    },
    {
      path: '/long-script-generator',
      icon: PenSquare,
      label: '🎬 Gerador de Roteiros',
      description: 'Gerador de roteiros longos com resumos contextuais'
    },
    {
      path: '/long-script-test',
      icon: TestTube,
      label: '🧪 TESTE: Roteiro Longo',
      description: 'Testar geração de roteiros longos isoladamente'
    },
    {
      path: '/storyteller-demo',
      icon: TestTube,
      label: '📖 STORYTELLER: Demo',
      description: 'Demonstração do Storyteller Unlimited'
    },
    {
      path: '/youtube-comparison',
      icon: TestTube,
      label: '🧪 DEV: YouTube Comparação',
      description: 'Comparar métodos de extração YouTube'
    }
  ]

  const quickStats = [
    { icon: Zap, label: 'Pipelines Ativos', value: '3' },
    { icon: Clock, label: 'Fila', value: '7' },
    { icon: Users, label: 'Canais', value: '12' },
    { icon: TrendingUp, label: 'Hoje', value: '5' }
  ]

  return (
    <motion.div
      initial={{ x: -280 }}
      animate={{ x: 0 }}
      exit={{ x: -280 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="w-70 bg-gray-800 border-r border-gray-700 flex flex-col h-full"
    >
      {/* Header */}
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-3xl">🎬</div>
            <div>
              <h1 className="text-xl font-bold text-white">
                Auto Video Producer
              </h1>
              <p className="text-xs text-gray-400">
                Produção Automática
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <X size={20} className="text-gray-400" />
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `group flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`
              }
            >
              <Icon 
                size={18} 
                className={`flex-shrink-0 ${
                  isActive ? 'text-white' : 'text-gray-400 group-hover:text-white'
                }`} 
              />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">
                  {item.label}
                </div>
                <div className="text-xs opacity-75 truncate">
                  {item.description}
                </div>
              </div>
              {isActive && (
                <motion.div
                  layoutId="activeIndicator"
                  className="w-1 h-6 bg-white rounded-full"
                  initial={false}
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Quick Stats */}
      <div className="p-4 border-t border-gray-700">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
          Status Rápido
        </h3>
        <div className="grid grid-cols-2 gap-2">
          {quickStats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-700 rounded-lg p-3 text-center hover:bg-gray-600 transition-colors cursor-pointer"
              >
                <Icon size={16} className="text-blue-400 mx-auto mb-1" />
                <div className="text-lg font-bold text-white">{stat.value}</div>
                <div className="text-xs text-gray-400">{stat.label}</div>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-bold">U</span>
          </div>
          <div className="flex-1">
            <div className="text-sm font-medium text-white">Usuário</div>
            <div className="text-xs text-gray-400">Administrador</div>
          </div>
          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
        </div>
      </div>
    </motion.div>
  )
}

export default Sidebar
