/**
 * 📊 Analytics Page
 * 
 * Página de analytics e relatórios
 */

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Calendar,
  Download,
  RefreshCw,
  Filter,
  Users,
  Video,
  Clock,
  Zap,
  Activity,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react'

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('7d')

  const performanceMetrics = [
    {
      title: 'Vídeos Produzidos',
      value: '145',
      change: '+23%',
      changeType: 'positive',
      icon: Video,
      color: 'blue'
    },
    {
      title: 'Taxa de Sucesso',
      value: '94%',
      change: '+2%',
      changeType: 'positive',
      icon: CheckCircle,
      color: 'green'
    },
    {
      title: 'Tempo Médio',
      value: '42min',
      change: '-8min',
      changeType: 'positive',
      icon: Clock,
      color: 'yellow'
    },
    {
      title: 'Custo Total',
      value: '$44.00',
      change: '+$12',
      changeType: 'negative',
      icon: TrendingUp,
      color: 'purple'
    }
  ]

  const channelPerformance = [
    { name: 'Motivação Viral', videos: 45, success_rate: 92 },
    { name: 'Success Stories', videos: 32, success_rate: 88 },
    { name: 'Vida Plena', videos: 18, success_rate: 95 },
    { name: 'Finanças Inteligentes', videos: 28, success_rate: 85 }
  ]

  const aiUsageData = [
    { service: 'OpenAI GPT-4', requests: 245, cost: 12.30, success_rate: 98 },
    { service: 'Gemini Pro', requests: 180, cost: 0.00, success_rate: 94 },
    { service: 'ElevenLabs TTS', requests: 95, cost: 28.50, success_rate: 99 },
    { service: 'FLUX Images', requests: 320, cost: 0.00, success_rate: 96 }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Analytics</h1>
          <p className="text-gray-400 mt-1">
            Análise detalhada da performance do sistema
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-32"
          >
            <option value="7d">7 dias</option>
            <option value="30d">30 dias</option>
            <option value="90d">90 dias</option>
            <option value="1y">1 ano</option>
          </select>
          <button className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2">
            <RefreshCw size={18} />
            <span>Atualizar</span>
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <Download size={18} />
            <span>Exportar</span>
          </button>
        </div>
      </div>

      {/* Performance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {performanceMetrics.map((metric, index) => {
          const Icon = metric.icon
          return (
            <motion.div
              key={metric.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-800 rounded-lg p-6 border border-gray-700"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm font-medium">{metric.title}</p>
                  <p className="text-2xl font-bold text-white mt-1">{metric.value}</p>
                  <div className="flex items-center mt-2">
                    <span className={`text-sm font-medium ${
                      metric.changeType === 'positive' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {metric.change}
                    </span>
                    <span className="text-gray-500 text-sm ml-1">vs período anterior</span>
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${
                  metric.color === 'blue' ? 'bg-blue-500 bg-opacity-20' :
                  metric.color === 'green' ? 'bg-green-500 bg-opacity-20' :
                  metric.color === 'yellow' ? 'bg-yellow-500 bg-opacity-20' :
                  'bg-purple-500 bg-opacity-20'
                }`}>
                  <Icon size={24} className={`${
                    metric.color === 'blue' ? 'text-blue-400' :
                    metric.color === 'green' ? 'text-green-400' :
                    metric.color === 'yellow' ? 'text-yellow-400' :
                    'text-purple-400'
                  }`} />
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Channel Performance */}
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-semibold text-white">Performance por Canal</h2>
            <p className="text-gray-400 text-sm mt-1">Taxa de sucesso e produção</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {channelPerformance.map((channel, index) => (
                <motion.div
                  key={channel.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 bg-gray-700 rounded-lg"
                >
                  <div>
                    <h3 className="font-medium text-white">{channel.name}</h3>
                    <p className="text-sm text-gray-400">{channel.videos} vídeos produzidos</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-white">{channel.success_rate}%</p>
                    <p className="text-xs text-gray-400">taxa de sucesso</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* AI Usage */}
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-semibold text-white">Uso de APIs de IA</h2>
            <p className="text-gray-400 text-sm mt-1">Requisições e custos</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {aiUsageData.map((service, index) => (
                <motion.div
                  key={service.service}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 bg-gray-700 rounded-lg"
                >
                  <div>
                    <h3 className="font-medium text-white">{service.service}</h3>
                    <div className="flex items-center space-x-4 mt-1 text-sm text-gray-400">
                      <span>{service.requests} requisições</span>
                      <span>•</span>
                      <span>{service.success_rate}% sucesso</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-white">
                      ${service.cost.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-400">custo total</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">Saúde do Sistema</h2>
          <p className="text-gray-400 text-sm mt-1">Status dos componentes principais</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500 bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-3">
                <CheckCircle size={32} className="text-green-400" />
              </div>
              <h3 className="font-semibold text-white">APIs Online</h3>
              <p className="text-sm text-gray-400 mt-1">Todos os serviços funcionando</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-500 bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-3">
                <AlertCircle size={32} className="text-yellow-400" />
              </div>
              <h3 className="font-semibold text-white">Rate Limits</h3>
              <p className="text-sm text-gray-400 mt-1">Alguns limites próximos</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-500 bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-3">
                <Activity size={32} className="text-blue-400" />
              </div>
              <h3 className="font-semibold text-white">Performance</h3>
              <p className="text-sm text-gray-400 mt-1">Sistema operando normalmente</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics
