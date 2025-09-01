/**
 * 🎯 Prompt Source Indicator Component
 * 
 * Componente para exibir indicadores visuais da origem dos prompts
 */

import React from 'react'
import { Bot, User, Settings } from 'lucide-react'

const PromptSourceIndicator = ({ promptSource, agentInfo, style, className = "", title = "", promptName = "" }) => {
  const getIndicatorConfig = () => {
    switch (promptSource) {
      case 'custom_user':
        return {
          icon: <User size={14} />,
          text: 'Prompt Personalizado',
          bgColor: 'bg-blue-500/20',
          borderColor: 'border-blue-400',
          textColor: 'text-blue-300',
          iconColor: 'text-blue-400'
        }
      
      case 'agent_specialized':
        // Show more specific information about the agent and prompt used
        let agentText = `Agente: ${agentInfo?.name || 'Especializado'}`
        if (style) {
          agentText += ` - ${style}`
        }
        if (promptName) {
          agentText += ` (${promptName})`
        } else if (title) {
          agentText += ` - Título: ${title}`
        }
        return {
          icon: <Bot size={14} />,
          text: agentText,
          bgColor: 'bg-purple-500/20',
          borderColor: 'border-purple-400',
          textColor: 'text-purple-300',
          iconColor: 'text-purple-400'
        }
      
      case 'system_default':
      default:
        let systemText = `Sistema Padrão`
        if (style) {
          systemText += ` - ${style}`
        }
        if (promptName) {
          systemText += ` (${promptName})`
        }
        return {
          icon: <Settings size={14} />,
          text: systemText,
          bgColor: 'bg-gray-500/20',
          borderColor: 'border-gray-400',
          textColor: 'text-gray-300',
          iconColor: 'text-gray-400'
        }
    }
  }

  const config = getIndicatorConfig()

  return (
    <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-lg border ${config.bgColor} ${config.borderColor} ${className}`}>
      <span className={config.iconColor}>
        {config.icon}
      </span>
      <span className={`text-xs font-medium ${config.textColor}`}>
        {config.text}
      </span>
    </div>
  )
}

export default PromptSourceIndicator