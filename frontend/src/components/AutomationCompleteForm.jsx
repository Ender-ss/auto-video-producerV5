import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  X,
  Youtube,
  Bot,
  Settings,
  Sparkles,
  Clock,
  Video,
  Mic,
  Image,
  FileText,
  Zap,
  AlertCircle,
  Info
} from 'lucide-react'

const AutomationCompleteForm = ({ onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    channel_url: '',
    video_count: 5,
    config: {
      extraction: {
        enabled: true,
        method: 'yt-dlp', // 'yt-dlp' ou 'rapidapi'
        rapidapi_key: ''
      },
      titles: {
        enabled: true,
        provider: 'gemini', // 'gemini', 'openai', 'claude'
        count: 10,
        style: 'viral',
        language: 'pt-BR',
        custom_prompt: false,
        custom_instructions: ''
      },
      premises: {
        enabled: true,
        provider: 'gemini',
        style: 'educational',
        target_audience: 'general',
        word_count: 200,
        custom_prompt: false,
        custom_instructions: ''
      },
      scripts: {
        enabled: true,
        provider: 'gemini', // 'gemini', 'openai', 'openrouter'
        chapters: 5,
        duration_target: '5-7 minutes',
        include_intro: true,
        include_outro: true,
        custom_prompts: false,
        custom_inicio: '',
        custom_meio: '',
        custom_fim: ''
      },
      tts: {
        enabled: true,
        provider: 'kokoro', // 'kokoro', 'elevenlabs', 'google'
        voice: 'af_bella',
        language: 'en',
        speed: 1.0,
        pitch: 1.0
      },
      images: {
        enabled: true,
        provider: 'pollinations',
        style: 'realistic',
        quality: 'high',
        count_per_chapter: 2,
        custom_prompt: false,
        custom_instructions: ''
      },
      video: {
        enabled: true,
        resolution: '1080p',
        fps: 30,
        format: 'mp4',
        include_subtitles: true,
        transition_duration: 0.5
      },
      prompts: {
        titles: {
          viral: 'Crie títulos virais e envolventes para o vídeo sobre: {topic}. Os títulos devem ser chamativos, despertar curiosidade e incentivar cliques.',
          educational: 'Crie títulos educacionais e informativos para o vídeo sobre: {topic}. Os títulos devem ser claros, diretos e indicar o valor educacional.',
          professional: 'Crie títulos profissionais e sérios para o vídeo sobre: {topic}. Os títulos devem transmitir autoridade e credibilidade.'
        },
        premises: {
          narrative: 'Crie uma premissa narrativa envolvente para um vídeo sobre: {title}. A premissa deve contar uma história cativante em aproximadamente {word_count} palavras.',
          educational: 'Crie uma premissa educacional estruturada para um vídeo sobre: {title}. A premissa deve apresentar os pontos de aprendizado em aproximadamente {word_count} palavras.',
          informative: 'Crie uma premissa informativa e objetiva para um vídeo sobre: {title}. A premissa deve apresentar fatos e informações relevantes em aproximadamente {word_count} palavras.'
        },
        scripts: {
          inicio: `# Prompt — Início

Escreva uma narrativa de {genre} intitulada "{title}".

Premissa: {premise}

Este é o INÍCIO da história. Deve estabelecer:
- Personagens principais e suas motivações
- Cenário e atmosfera da história
- Conflito principal que moverá a narrativa
- Tom inicial da narrativa

**IMPORTANTE:** Seja detalhado, extenso e minucioso na descrição de cenários, personagens, ações e diálogos.`,
          meio: `# Prompt — Meio

Continue a narrativa de {genre} intitulada "{title}".

CONTEXTO ANTERIOR:
"{previousContent}"...

Esta é a continuação do MEIO da história. Deve:
- Continuar a narrativa de forma orgânica e coerente
- Desenvolver os personagens e suas relações
- Intensificar o conflito principal
- Adicionar novos elementos de tensão

**IMPORTANTE:** Seja detalhado, extenso e minucioso. Cada capítulo deve ter conteúdo substancial e rico em detalhes.`,
          fim: `# Prompt — Fim

Continue a narrativa de {genre} intitulada "{title}".

CONTEXTO ANTERIOR:
"{previousContent}"...

Este é o FIM da história. Deve:
- Resolver o conflito principal estabelecido no início
- Proporcionar conclusão satisfatória para todos os personagens principais
- Entregar o clímax esperado da história
- Fechar a história de forma impactante

**IMPORTANTE:** Seja detalhado, extenso e minucioso na conclusão. Garanta um fechamento rico e satisfatório.`
        },
        images: {
          cinematic: 'Crie uma descrição cinematográfica para uma imagem que represente: {scene_description}. A imagem deve ter qualidade cinematográfica, boa iluminação e composição profissional.',
          minimalist: 'Crie uma descrição minimalista para uma imagem que represente: {scene_description}. A imagem deve ser limpa, simples e com foco no elemento principal.',
          artistic: 'Crie uma descrição artística para uma imagem que represente: {scene_description}. A imagem deve ser criativa, expressiva e visualmente impactante.'
        }
      }
    }
  })

  const [activeSection, setActiveSection] = useState('basic')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleInputChange = (path, value) => {
    setFormData(prev => {
      const newData = { ...prev }
      const keys = path.split('.')
      let current = newData
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {}
        current = current[keys[i]]
      }
      
      current[keys[keys.length - 1]] = value
      return newData
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    try {
      await onSubmit(formData)
    } catch (error) {
      console.error('Erro ao submeter formulário:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const sections = [
    { id: 'basic', label: 'Básico', icon: Youtube },
    { id: 'ai', label: 'IA & Conteúdo', icon: Bot },
    { id: 'media', label: 'Mídia & Vídeo', icon: Video },
    { id: 'prompts', label: 'Prompts', icon: FileText },
    { id: 'advanced', label: 'Avançado', icon: Settings }
  ]

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-4xl max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Sparkles size={24} className="text-purple-400" />
              <h2 className="text-2xl font-bold text-white">Nova Automação Completa</h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X size={20} />
            </button>
          </div>
          <p className="text-gray-300 mt-2">
            Configure todos os parâmetros para a automação completa do pipeline
          </p>
        </div>

        <div className="flex h-[calc(90vh-200px)]">
          {/* Sidebar */}
          <div className="w-64 bg-gray-800 border-r border-gray-700 p-4">
            <nav className="space-y-2">
              {sections.map((section) => {
                const Icon = section.icon
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                      activeSection === section.id
                        ? 'bg-purple-600 text-white'
                        : 'text-gray-400 hover:text-white hover:bg-gray-700'
                    }`}
                  >
                    <Icon size={18} />
                    <span>{section.label}</span>
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto">
            <form onSubmit={handleSubmit} className="p-6">
              {activeSection === 'basic' && (
                <BasicSection formData={formData} onChange={handleInputChange} />
              )}
              {activeSection === 'ai' && (
                <AISection formData={formData} onChange={handleInputChange} />
              )}
              {activeSection === 'media' && (
                <MediaSection formData={formData} onChange={handleInputChange} />
              )}
              {activeSection === 'prompts' && (
                <PromptsSection formData={formData} onChange={handleInputChange} />
              )}
              {activeSection === 'advanced' && (
                <AdvancedSection formData={formData} onChange={handleInputChange} />
              )}
            </form>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-800 border-t border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <Clock size={16} />
              <span>Tempo estimado: ~45 minutos</span>
            </div>
            <div className="flex items-center space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-2 text-gray-400 hover:text-white transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSubmit}
                disabled={isSubmitting || !formData.channel_url}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Iniciando...</span>
                  </>
                ) : (
                  <>
                    <Zap size={18} />
                    <span>Iniciar Automação</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

// Seção Básica
const BasicSection = ({ formData, onChange }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Youtube size={20} className="text-red-400" />
          <span>Configuração Básica</span>
        </h3>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            URL do Canal do YouTube *
          </label>
          <input
            type="url"
            value={formData.channel_url}
            onChange={(e) => onChange('channel_url', e.target.value)}
            placeholder="https://www.youtube.com/@canal"
            className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none transition-colors"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            URL completa do canal do YouTube para extração de vídeos
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Quantidade de Vídeos
          </label>
          <input
            type="number"
            min="1"
            max="20"
            value={formData.video_count}
            onChange={(e) => onChange('video_count', parseInt(e.target.value))}
            className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none transition-colors"
          />
          <p className="text-xs text-gray-500 mt-1">
            Número de vídeos mais recentes para processar (máximo 20)
          </p>
        </div>

        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <Info size={20} className="text-blue-400 mt-0.5" />
            <div>
              <h4 className="text-blue-300 font-medium mb-1">Como funciona</h4>
              <p className="text-blue-200 text-sm leading-relaxed">
                O sistema irá extrair os vídeos mais recentes do canal, gerar novos títulos e premissas, 
                criar roteiros únicos, produzir áudio com TTS, gerar imagens e montar vídeos finais automaticamente.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Seção de IA
const AISection = ({ formData, onChange }) => {
  const handleOpenPromptsConfig = () => {
    window.open('/prompts-config', '_blank')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Bot size={20} className="text-purple-400" />
          <span>Configuração de IA & Conteúdo</span>
        </h3>
        <button
          type="button"
          onClick={handleOpenPromptsConfig}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm"
          title="Abrir configuração de prompts personalizados"
        >
          <Settings size={16} />
          <span>Configurar Prompts</span>
        </button>
      </div>
      
      {/* Aviso sobre prompts personalizados */}
      <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Info size={16} className="text-blue-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm">
            <p className="text-blue-200 font-medium mb-1">Prompts Personalizados</p>
            <p className="text-blue-300">
              Configure prompts personalizados para títulos, premissas, roteiros e imagens. 
              Os prompts personalizados substituem os padrões quando ativados.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Títulos */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3 flex items-center space-x-2">
            <FileText size={18} className="text-yellow-400" />
            <span>Geração de Títulos</span>
          </h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Provedor de IA
              </label>
              <select
                value={formData.config.titles.provider}
                onChange={(e) => onChange('config.titles.provider', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="gemini">Google Gemini</option>
                <option value="openai">OpenAI GPT</option>
                <option value="claude">Anthropic Claude</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Quantidade de Títulos
              </label>
              <input
                type="number"
                min="5"
                max="20"
                value={formData.config.titles.count}
                onChange={(e) => onChange('config.titles.count', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Estilo
              </label>
              <select
                value={formData.config.titles.style}
                onChange={(e) => onChange('config.titles.style', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="viral">Viral</option>
                <option value="educational">Educacional</option>
                <option value="professional">Profissional</option>
              </select>
            </div>
            <div className="col-span-2">
              <div className="flex items-center space-x-2 mb-2">
                <input
                  type="checkbox"
                  id="titles-custom-prompt"
                  checked={formData.config.titles.custom_prompt}
                  onChange={(e) => onChange('config.titles.custom_prompt', e.target.checked)}
                  className="rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                />
                <label htmlFor="titles-custom-prompt" className="text-sm font-medium text-gray-300">
                  Usar prompt personalizado
                </label>
              </div>
              {formData.config.titles.custom_prompt && (
                <textarea
                  value={formData.config.titles.custom_instructions}
                  onChange={(e) => onChange('config.titles.custom_instructions', e.target.value)}
                  placeholder="Digite suas instruções personalizadas para geração de títulos..."
                  rows={3}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm resize-none"
                />
              )}
            </div>
          </div>
        </div>

        {/* Premissas */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3 flex items-center space-x-2">
            <FileText size={18} className="text-green-400" />
            <span>Geração de Premissas</span>
          </h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Provedor de IA
              </label>
              <select
                value={formData.config.premises.provider}
                onChange={(e) => onChange('config.premises.provider', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="gemini">Google Gemini</option>
                <option value="openai">OpenAI GPT</option>
                <option value="claude">Anthropic Claude</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Estilo
              </label>
              <select
                value={formData.config.premises.style}
                onChange={(e) => onChange('config.premises.style', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="educational">Educacional</option>
                <option value="entertaining">Entretenimento</option>
                <option value="informative">Informativo</option>
                <option value="persuasive">Persuasivo</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Público-alvo
              </label>
              <select
                value={formData.config.premises.target_audience}
                onChange={(e) => onChange('config.premises.target_audience', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="general">Geral</option>
                <option value="young_adults">Jovens Adultos</option>
                <option value="professionals">Profissionais</option>
                <option value="students">Estudantes</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Palavras-alvo
              </label>
              <input
                type="number"
                value={formData.config.premises.word_count}
                onChange={(e) => onChange('config.premises.word_count', parseInt(e.target.value))}
                min="50"
                max="500"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              />
            </div>
            <div className="col-span-2">
              <div className="flex items-center space-x-2 mb-2">
                <input
                  type="checkbox"
                  id="premises-custom-prompt"
                  checked={formData.config.premises.custom_prompt}
                  onChange={(e) => onChange('config.premises.custom_prompt', e.target.checked)}
                  className="rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                />
                <label htmlFor="premises-custom-prompt" className="text-sm font-medium text-gray-300">
                  Usar prompt personalizado
                </label>
              </div>
              {formData.config.premises.custom_prompt && (
                <textarea
                  value={formData.config.premises.custom_instructions}
                  onChange={(e) => onChange('config.premises.custom_instructions', e.target.value)}
                  placeholder="Digite suas instruções personalizadas para geração de premissas..."
                  rows={3}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm resize-none"
                />
              )}
            </div>
          </div>
        </div>

        {/* Roteiros */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3 flex items-center space-x-2">
            <FileText size={18} className="text-blue-400" />
            <span>Geração de Roteiros</span>
          </h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Provedor de IA
              </label>
              <select
                value={formData.config.scripts.provider}
                onChange={(e) => onChange('config.scripts.provider', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="gemini">Google Gemini</option>
                <option value="openai">OpenAI GPT</option>
                <option value="openrouter">OpenRouter</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Número de Capítulos
              </label>
              <input
                type="number"
                min="3"
                max="10"
                value={formData.config.scripts.chapters}
                onChange={(e) => onChange('config.scripts.chapters', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Duração Alvo
              </label>
              <input
                type="text"
                value={formData.config.scripts.duration_target}
                onChange={(e) => onChange('config.scripts.duration_target', e.target.value)}
                placeholder="Ex: 5-7 minutes"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              />
            </div>

            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.config.scripts.include_intro}
                  onChange={(e) => onChange('config.scripts.include_intro', e.target.checked)}
                  className="rounded border-gray-600 bg-gray-700 text-purple-600"
                />
                <span className="text-sm text-gray-300">Incluir Intro</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.config.scripts.include_outro}
                  onChange={(e) => onChange('config.scripts.include_outro', e.target.checked)}
                  className="rounded border-gray-600 bg-gray-700 text-purple-600"
                />
                <span className="text-sm text-gray-300">Incluir Outro</span>
              </label>
            </div>
            <div className="space-y-3">
              <div className="flex items-center space-x-2 mb-2">
                <input
                  type="checkbox"
                  id="scripts-custom-prompts"
                  checked={formData.config.scripts.custom_prompts}
                  onChange={(e) => onChange('config.scripts.custom_prompts', e.target.checked)}
                  className="rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                />
                <label htmlFor="scripts-custom-prompts" className="text-sm font-medium text-gray-300">
                  Usar prompts personalizados
                </label>
              </div>
              {formData.config.scripts.custom_prompts && (
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Prompt para Início (1º capítulo)
                    </label>
                    <textarea
                      value={formData.config.scripts.custom_inicio}
                      onChange={(e) => onChange('config.scripts.custom_inicio', e.target.value)}
                      placeholder="Prompt personalizado para o primeiro capítulo (início da história)..."
                      rows={3}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm resize-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Prompt para Meio (desenvolvimento)
                    </label>
                    <textarea
                      value={formData.config.scripts.custom_meio}
                      onChange={(e) => onChange('config.scripts.custom_meio', e.target.value)}
                      placeholder="Prompt personalizado para capítulos do meio (desenvolvimento da história)..."
                      rows={3}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm resize-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Prompt para Fim (último capítulo)
                    </label>
                    <textarea
                      value={formData.config.scripts.custom_fim}
                      onChange={(e) => onChange('config.scripts.custom_fim', e.target.value)}
                      placeholder="Prompt personalizado para o último capítulo (conclusão da história)..."
                      rows={3}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm resize-none"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* TTS */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3 flex items-center space-x-2">
            <Mic size={18} className="text-red-400" />
            <span>Text-to-Speech</span>
          </h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Provedor
              </label>
              <select
                value={formData.config.tts.provider}
                onChange={(e) => onChange('config.tts.provider', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="kokoro">Kokoro TTS</option>
                <option value="elevenlabs">ElevenLabs</option>
                <option value="google">Google TTS</option>
              </select>
            </div>
            {formData.config.tts.provider === 'kokoro' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Idioma
                  </label>
                  <select
                    value={formData.config.tts.language}
                    onChange={(e) => {
                      const newLanguage = e.target.value
                      let defaultVoice = 'af_bella'
                      if (newLanguage === 'pt') defaultVoice = 'pf_dora'
                      
                      onChange('config.tts.language', newLanguage)
                      onChange('config.tts.voice', defaultVoice)
                    }}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                  >
                    <option value="en">🇺🇸 Inglês</option>
                    <option value="pt">🇵🇹 Português</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Voz
                  </label>
                  <select
                    value={formData.config.tts.voice}
                    onChange={(e) => onChange('config.tts.voice', e.target.value)}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                  >
                    {formData.config.tts.language === 'pt' ? (
                      <>
                        <option value="pf_dora">🇵🇹 pf_dora - Feminina</option>
                        <option value="pm_alex">🇵🇹 pm_alex - Masculina</option>
                        <option value="pm_santa">🇵🇹 pm_santa - Masculina (Santa)</option>
                      </>
                    ) : (
                      <>
                        <option value="af_bella">🇺🇸 af_bella - Feminina</option>
                        <option value="af_sarah">🇺🇸 af_sarah - Feminina</option>
                        <option value="af_nicole">🇺🇸 af_nicole - Feminina</option>
                        <option value="am_adam">🇺🇸 am_adam - Masculina</option>
                        <option value="am_michael">🇺🇸 am_michael - Masculina</option>
                      </>
                    )}
                  </select>
                </div>
              </>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Velocidade: {formData.config.tts.speed}x
              </label>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={formData.config.tts.speed}
                onChange={(e) => onChange('config.tts.speed', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Tom: {formData.config.tts.pitch}x
              </label>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={formData.config.tts.pitch}
                onChange={(e) => onChange('config.tts.pitch', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Seção de Mídia
const MediaSection = ({ formData, onChange }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Video size={20} className="text-green-400" />
          <span>Configuração de Mídia & Vídeo</span>
        </h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Imagens */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3 flex items-center space-x-2">
            <Image size={18} className="text-pink-400" />
            <span>Geração de Imagens</span>
          </h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Estilo
              </label>
              <select
                value={formData.config.images.style}
                onChange={(e) => onChange('config.images.style', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="realistic">Realista</option>
                <option value="cartoon">Cartoon</option>
                <option value="anime">Anime</option>
                <option value="abstract">Abstrato</option>
                <option value="photographic">Fotográfico</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Qualidade
              </label>
              <select
                value={formData.config.images.quality}
                onChange={(e) => onChange('config.images.quality', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="standard">Padrão</option>
                <option value="high">Alta</option>
                <option value="ultra">Ultra</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Formato
              </label>
              <select
                value={formData.config.images.format || 'jpg'}
                onChange={(e) => onChange('config.images.format', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="jpg">JPG (Padrão)</option>
                <option value="png">PNG (Transparência)</option>
                <option value="webp">WebP (Otimizado)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Imagens por Capítulo
              </label>
              <input
                type="number"
                min="1"
                max="5"
                value={formData.config.images.count_per_chapter}
                onChange={(e) => onChange('config.images.count_per_chapter', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              />
            </div>
            <div className="col-span-2">
              <div className="flex items-center space-x-2 mb-2">
                <input
                  type="checkbox"
                  id="images-custom-prompt"
                  checked={formData.config.images.custom_prompt || false}
                  onChange={(e) => onChange('config.images.custom_prompt', e.target.checked)}
                  className="rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                />
                <label htmlFor="images-custom-prompt" className="text-sm font-medium text-gray-300">
                  Usar prompt personalizado
                </label>
              </div>
              {formData.config.images.custom_prompt && (
                <textarea
                  value={formData.config.images.custom_instructions || ''}
                  onChange={(e) => onChange('config.images.custom_instructions', e.target.value)}
                  placeholder="Digite suas instruções personalizadas para geração de imagens..."
                  rows={3}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm resize-none"
                />
              )}
            </div>
          </div>
        </div>

        {/* Vídeo */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3 flex items-center space-x-2">
            <Video size={18} className="text-blue-400" />
            <span>Configuração de Vídeo</span>
          </h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Resolução
              </label>
              <select
                value={formData.config.video.resolution}
                onChange={(e) => onChange('config.video.resolution', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="720p">720p (HD)</option>
                <option value="1080p">1080p (Full HD)</option>
                <option value="1440p">1440p (2K)</option>
                <option value="2160p">2160p (4K)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                FPS
              </label>
              <select
                value={formData.config.video.fps}
                onChange={(e) => onChange('config.video.fps', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value={24}>24 FPS</option>
                <option value={30}>30 FPS</option>
                <option value={60}>60 FPS</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Duração da Transição (segundos)
              </label>
              <input
                type="number"
                min="0"
                max="2"
                step="0.1"
                value={formData.config.video.transition_duration}
                onChange={(e) => onChange('config.video.transition_duration', parseFloat(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              />
            </div>
            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.config.video.include_subtitles}
                  onChange={(e) => onChange('config.video.include_subtitles', e.target.checked)}
                  className="rounded border-gray-600 bg-gray-700 text-purple-600"
                />
                <span className="text-sm text-gray-300">Incluir Legendas</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Seção de Prompts
const PromptsSection = ({ formData, onChange }) => {
  const [editingPrompt, setEditingPrompt] = useState(null)
  const [tempPromptValue, setTempPromptValue] = useState('')

  const defaultPrompts = {
    titles: {
      viral: 'Crie títulos virais e envolventes para o vídeo sobre: {topic}. Os títulos devem ser chamativos, despertar curiosidade e incentivar cliques.',
      educational: 'Crie títulos educacionais e informativos para o vídeo sobre: {topic}. Os títulos devem ser claros, diretos e indicar o valor educacional.',
      professional: 'Crie títulos profissionais e sérios para o vídeo sobre: {topic}. Os títulos devem transmitir autoridade e credibilidade.'
    },
    premises: {
      narrative: 'Crie uma premissa narrativa envolvente para um vídeo sobre: {title}. A premissa deve contar uma história cativante em aproximadamente {word_count} palavras.',
      educational: 'Crie uma premissa educacional estruturada para um vídeo sobre: {title}. A premissa deve apresentar os pontos de aprendizado em aproximadamente {word_count} palavras.',
      informative: 'Crie uma premissa informativa e objetiva para um vídeo sobre: {title}. A premissa deve apresentar fatos e informações relevantes em aproximadamente {word_count} palavras.'
    },
    scripts: {
      storytelling: 'Crie um roteiro envolvente no estilo storytelling para o vídeo "{title}". Baseie-se na premissa: {premise}. O roteiro deve ter aproximadamente {duration} segundos.',
      educational: 'Crie um roteiro educacional estruturado para o vídeo "{title}". Baseie-se na premissa: {premise}. O roteiro deve ter aproximadamente {duration} segundos.',
      entertainment: 'Crie um roteiro divertido e entretenimento para o vídeo "{title}". Baseie-se na premissa: {premise}. O roteiro deve ter aproximadamente {duration} segundos.'
    },
    images: {
      cinematic: 'Crie uma descrição cinematográfica para uma imagem que represente: {scene_description}. A imagem deve ter qualidade cinematográfica, boa iluminação e composição profissional.',
      minimalist: 'Crie uma descrição minimalista para uma imagem que represente: {scene_description}. A imagem deve ser limpa, simples e com foco no elemento principal.',
      artistic: 'Crie uma descrição artística para uma imagem que represente: {scene_description}. A imagem deve ser criativa, expressiva e visualmente impactante.'
    }
  }

  const handleEditPrompt = (section, style, currentValue) => {
    setEditingPrompt(`${section}.${style}`)
    setTempPromptValue(currentValue)
  }

  const handleSavePrompt = (section, style) => {
    if (tempPromptValue.trim()) {
      onChange(`config.prompts.${section}.${style}`, tempPromptValue.trim())
      setEditingPrompt(null)
      setTempPromptValue('')
    }
  }

  const handleCancelEdit = () => {
    setEditingPrompt(null)
    setTempPromptValue('')
  }

  const handleResetPrompt = (section, style) => {
    onChange(`config.prompts.${section}.${style}`, defaultPrompts[section][style])
  }

  const handleResetSection = (section) => {
    Object.keys(defaultPrompts[section]).forEach(style => {
      onChange(`config.prompts.${section}.${style}`, defaultPrompts[section][style])
    })
  }

  const renderPromptCard = (section, style, label, description, icon) => {
    const promptPath = `${section}.${style}`
    const currentValue = formData.config.prompts[section][style]
    const isEditing = editingPrompt === promptPath
    const Icon = icon

    return (
      <div key={promptPath} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Icon size={16} className="text-blue-400" />
            <h5 className="text-sm font-medium text-white">{label}</h5>
          </div>
          <div className="flex items-center space-x-2">
            {!isEditing && (
              <>
                <button
                  type="button"
                  onClick={() => handleEditPrompt(section, style, currentValue)}
                  className="p-1 text-gray-400 hover:text-blue-400 transition-colors"
                  title="Editar prompt"
                >
                  <FileText size={14} />
                </button>
                <button
                  type="button"
                  onClick={() => handleResetPrompt(section, style)}
                  className="p-1 text-gray-400 hover:text-yellow-400 transition-colors"
                  title="Resetar para padrão"
                >
                  <AlertCircle size={14} />
                </button>
              </>
            )}
          </div>
        </div>
        
        <p className="text-xs text-gray-400 mb-3">{description}</p>
        
        {isEditing ? (
          <div className="space-y-3">
            <textarea
              value={tempPromptValue}
              onChange={(e) => setTempPromptValue(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm resize-none"
              rows={4}
              placeholder="Digite o prompt personalizado..."
            />
            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={() => handleSavePrompt(section, style)}
                disabled={!tempPromptValue.trim()}
                className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white text-xs rounded transition-colors"
              >
                Salvar
              </button>
              <button
                type="button"
                onClick={handleCancelEdit}
                className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-xs rounded transition-colors"
              >
                Cancelar
              </button>
            </div>
          </div>
        ) : (
          <div 
            className="text-xs text-gray-300 bg-gray-700 p-3 rounded cursor-pointer hover:bg-gray-600 transition-colors"
            onClick={() => handleEditPrompt(section, style, currentValue)}
            title="Clique para editar"
          >
            {currentValue && currentValue.length > 150 ? `${currentValue.substring(0, 150)}...` : currentValue || ''}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <FileText size={20} className="text-green-400" />
          <span>Configuração de Prompts</span>
        </h3>
        <p className="text-gray-400 text-sm">
          Personalize os prompts utilizados pela IA para gerar títulos, premissas, roteiros e descrições de imagens.
        </p>
      </div>

      {/* Prompts de Títulos */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-medium text-white flex items-center space-x-2">
            <Bot size={18} className="text-yellow-400" />
            <span>Prompts de Títulos</span>
          </h4>
          <button
            type="button"
            onClick={() => handleResetSection('titles')}
            className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-xs rounded transition-colors"
            title="Resetar todos os prompts de títulos"
          >
            Resetar Seção
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {renderPromptCard('titles', 'viral', 'Viral', 'Prompts para títulos chamativos e virais', Sparkles)}
          {renderPromptCard('titles', 'educational', 'Educacional', 'Prompts para títulos educacionais e informativos', FileText)}
          {renderPromptCard('titles', 'professional', 'Profissional', 'Prompts para títulos sérios e profissionais', Settings)}
        </div>
      </div>

      {/* Prompts de Premissas */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-medium text-white flex items-center space-x-2">
            <Bot size={18} className="text-blue-400" />
            <span>Prompts de Premissas</span>
          </h4>
          <button
            type="button"
            onClick={() => handleResetSection('premises')}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
            title="Resetar todos os prompts de premissas"
          >
            Resetar Seção
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {renderPromptCard('premises', 'narrative', 'Narrativa', 'Prompts para premissas narrativas envolventes', FileText)}
          {renderPromptCard('premises', 'educational', 'Educacional', 'Prompts para premissas educacionais estruturadas', Bot)}
          {renderPromptCard('premises', 'informative', 'Informativa', 'Prompts para premissas objetivas e informativas', Info)}
        </div>
      </div>

      {/* Prompts de Roteiros */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-medium text-white flex items-center space-x-2">
            <Bot size={18} className="text-purple-400" />
            <span>Prompts de Roteiros</span>
          </h4>
          <button
            type="button"
            onClick={() => handleResetSection('scripts')}
            className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-xs rounded transition-colors"
            title="Resetar todos os prompts de roteiros"
          >
            Resetar Seção
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {renderPromptCard('scripts', 'storytelling', 'Storytelling', 'Prompts para roteiros narrativos envolventes', Sparkles)}
          {renderPromptCard('scripts', 'educational', 'Educacional', 'Prompts para roteiros educacionais estruturados', FileText)}
          {renderPromptCard('scripts', 'entertainment', 'Entretenimento', 'Prompts para roteiros divertidos e cativantes', Video)}
        </div>
      </div>

      {/* Prompts de Imagens */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-medium text-white flex items-center space-x-2">
            <Bot size={18} className="text-pink-400" />
            <span>Prompts de Imagens</span>
          </h4>
          <button
            type="button"
            onClick={() => handleResetSection('images')}
            className="px-3 py-1 bg-pink-600 hover:bg-pink-700 text-white text-xs rounded transition-colors"
            title="Resetar todos os prompts de imagens"
          >
            Resetar Seção
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {renderPromptCard('images', 'cinematic', 'Cinematográfico', 'Prompts para imagens com qualidade cinematográfica', Video)}
          {renderPromptCard('images', 'minimalist', 'Minimalista', 'Prompts para imagens limpas e minimalistas', Settings)}
          {renderPromptCard('images', 'artistic', 'Artístico', 'Prompts para imagens criativas e expressivas', Image)}
        </div>
      </div>

      {/* Informações sobre variáveis */}
      <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Info size={20} className="text-blue-400 mt-0.5" />
          <div>
            <h4 className="text-blue-300 font-medium mb-2">Variáveis Disponíveis</h4>
            <div className="text-blue-200 text-sm space-y-1">
              <p><strong>Títulos:</strong> {'{topic}'} - Tópico do vídeo</p>
              <p><strong>Premissas:</strong> {'{title}'}, {'{word_count}'} - Título e contagem de palavras</p>
              <p><strong>Roteiros:</strong> {'{title}'}, {'{premise}'}, {'{duration}'} - Título, premissa e duração</p>
              <p><strong>Imagens:</strong> {'{scene_description}'} - Descrição da cena</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Seção Avançada
const AdvancedSection = ({ formData, onChange }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Settings size={20} className="text-gray-400" />
          <span>Configurações Avançadas</span>
        </h3>
      </div>

      <div className="space-y-6">
        {/* Extração */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3">Extração de Vídeos</h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Método de Extração
              </label>
              <select
                value={formData.config.extraction.method}
                onChange={(e) => onChange('config.extraction.method', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="yt-dlp">yt-dlp (Gratuito)</option>
                <option value="rapidapi">RapidAPI (Pago)</option>
              </select>
            </div>
            {formData.config.extraction.method === 'rapidapi' && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  RapidAPI Key
                </label>
                <input
                  type="password"
                  value={formData.config.extraction.rapidapi_key}
                  onChange={(e) => onChange('config.extraction.rapidapi_key', e.target.value)}
                  placeholder="Sua chave da RapidAPI"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                />
              </div>
            )}
          </div>
        </div>

        {/* Controles de Etapas */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3">Controle de Etapas</h4>
          <div className="grid grid-cols-2 gap-4">
            {[
              { key: 'extraction', label: 'Extração' },
              { key: 'titles', label: 'Títulos' },
              { key: 'premises', label: 'Premissas' },
              { key: 'scripts', label: 'Roteiros' },
              { key: 'tts', label: 'TTS' },
              { key: 'images', label: 'Imagens' },
              { key: 'video', label: 'Vídeo' }
            ].map((step) => (
              <label key={step.key} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.config[step.key].enabled}
                  onChange={(e) => onChange(`config.${step.key}.enabled`, e.target.checked)}
                  className="rounded border-gray-600 bg-gray-700 text-purple-600"
                />
                <span className="text-sm text-gray-300">{step.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Aviso */}
        <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertCircle size={20} className="text-yellow-400 mt-0.5" />
            <div>
              <h4 className="text-yellow-300 font-medium mb-1">Atenção</h4>
              <p className="text-yellow-200 text-sm leading-relaxed">
                Desabilitar etapas pode afetar o resultado final. Certifique-se de que as dependências 
                estão configuradas corretamente antes de iniciar a automação.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AutomationCompleteForm