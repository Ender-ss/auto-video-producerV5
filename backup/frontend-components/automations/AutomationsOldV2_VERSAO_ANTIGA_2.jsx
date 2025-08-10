/**
 * 🤖 Automations Page (Old Version)
 * 
 * Página de automações completas de conteúdo (Versão Antiga)
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import CustomPromptManager from '../components/CustomPromptManager'
import SavedChannelsManager from '../components/SavedChannelsManager'
import {
  Play,
  Pause,
  Square,
  Settings,
  Youtube,
  Wand2,
  FileText,
  Mic,
  Image,
  Video,
  Download,
  RefreshCw,
  Plus,
  Trash2,
  Edit,
  Eye,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
  Bot,
  Loader2,
  FileAudio,
  User,
  Volume2,
  Sparkles,
  Target,
  Layers,
  Workflow,
  XCircle,
  Copy,
  Calendar,
  Terminal,
  AlertTriangle,
  X,
  Save
} from 'lucide-react'
import AutomationResults from '../components/AutomationResults'

const AutomationsOld = () => {
  // Copiar o conteúdo do componente AutomationsRoteirosTest.jsx aqui
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">🤖 Automações de Conteúdo <span className="text-sm text-amber-500 font-normal">[TESTE - ROTEIROS]</span></h1>
          <p className="text-gray-400 mt-1">
            Fluxos automatizados completos para criação de conteúdo para YouTube
          </p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Settings size={20} />
          <span>Status dos Agentes de IA</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Google Gemini */}
          <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium text-white">Google Gemini</h3>
                <p className="text-xs text-gray-400 mt-1">API Key válida</p>
              </div>
              <div className="bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                Online
              </div>
            </div>
          </div>

          {/* OpenAI GPT-4 */}
          <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium text-white">OpenAI GPT-4</h3>
                <p className="text-xs text-gray-400 mt-1">API Key válida</p>
              </div>
              <div className="bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                Online
              </div>
            </div>
          </div>

          {/* Anthropic Claude */}
          <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium text-white">Anthropic Claude</h3>
                <p className="text-xs text-gray-400 mt-1">API Key válida</p>
              </div>
              <div className="bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                Online
              </div>
            </div>
          </div>

          {/* OpenRouter */}
          <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium text-white">OpenRouter</h3>
                <p className="text-xs text-gray-400 mt-1">API Key válida</p>
              </div>
              <div className="bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                Online
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg flex items-center space-x-2">
          <Youtube size={16} />
          <span>Extrair do YouTube</span>
        </button>

        <button className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg flex items-center space-x-2">
          <FileText size={16} />
          <span>Geração de Roteiro</span>
        </button>

        <button className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg flex items-center space-x-2">
          <Mic size={16} />
          <span>Text-to-Speech</span>
        </button>

        <button className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg flex items-center space-x-2">
          <Image size={16} />
          <span>Geração de Imagens</span>
        </button>

        <button className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg flex items-center space-x-2">
          <Video size={16} />
          <span>Edição de Vídeo</span>
        </button>
      </div>

      {/* Extração do YouTube */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Youtube size={20} />
          <span>Extração de Conteúdo do YouTube</span>
        </h2>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Canal do YouTube
          </label>
          <input
            type="text"
            placeholder="@MrBeast ou URL do canal"
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Mín. Views
            </label>
            <input
              type="number"
              placeholder="1000"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Dias
            </label>
            <input
              type="number"
              placeholder="30"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Total
            </label>
            <input
              type="number"
              placeholder="5"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
          </div>
        </div>

        <button className="w-full bg-red-600 hover:bg-red-700 text-white py-2 rounded-lg flex items-center justify-center space-x-2">
          <Play size={16} />
          <span>Iniciar Extração</span>
        </button>
      </div>

      {/* Resultados da Extração */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white flex items-center space-x-2">
            <FileText size={20} />
            <span>Resultados da Extração</span>
          </h2>

          <button className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm flex items-center space-x-1">
            <Download size={14} />
            <span>Exportar Títulos de Vídeo</span>
          </button>
        </div>

        <div className="bg-gray-700 rounded-lg p-4 flex items-center justify-center h-64">
          <div className="text-center text-gray-400">
            <FileText size={48} className="mx-auto mb-4 opacity-50" />
            <p>Nenhum resultado disponível</p>
            <p className="text-sm mt-2">Execute uma extração para ver os resultados aqui.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AutomationsOld