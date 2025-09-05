import React, { useState } from 'react'
import { motion } from 'framer-motion'
import SavedChannelsManager from './SavedChannelsManager'
import CustomPromptManager from './CustomPromptManager'
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
  Info,
  BookOpen,
  Save,
  Eye,
  User
} from 'lucide-react'

const AutomationCompleteForm = ({ onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    channel_url: '',
    video_count: 5,
    agent: {
      type: 'default', // 'default' or 'specialized'
      specialized_type: 'millionaire_stories'
    },
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
        system: 'traditional', // 'traditional' ou 'storyteller'
        provider: 'gemini', // 'gemini', 'openai', 'openrouter'
        chapters: 5,
        duration_target: '5-7 minutes',
        storyteller_agent: 'millionaire_stories',
        storyteller_chapters: 10,
        include_intro: true,
        include_outro: true,
        custom_prompts: false,
        custom_inicio: '',
        custom_meio: '',
        custom_fim: '',
        detailed_prompt: false,
        detailed_prompt_text: '',
        contextual_chapters: false,
        show_default_prompts: false,
        default_prompt_intro: `Você é um roteirista profissional especializado em conteúdo para YouTube.

TÍTULO: \{titulo\}
PREMISSA: \{premissa\}

INSTRUÇÕES:
- Escreva o primeiro capítulo (introdução) deste roteiro
- O capítulo deve ter aproximadamente 500 palavras
- Estabeleça os personagens principais, cenário e conflito inicial
- Use uma linguagem envolvente adequada para vídeos do YouTube
- Escreva apenas o conteúdo do capítulo, sem títulos ou marcações`,
        default_prompt_middle: `Você é um roteirista profissional especializado em conteúdo para YouTube.

TÍTULO: \{titulo\}
PREMISSA: \{premissa\}

CONTEXTO DO CAPÍTULO ANTERIOR:
\{resumos[i-2]\}

INSTRUÇÕES:
- Escreva o capítulo \{i\} deste roteiro, continuando a história
- O capítulo deve ter aproximadamente 500 palavras
- Mantenha coerência com o contexto fornecido
- Desenvolva a narrativa de forma orgânica
- Use uma linguagem envolvente adequada para vídeos do YouTube
- Escreva apenas o conteúdo do capítulo, sem títulos ou marcações`,
        default_prompt_conclusion: `Você é um roteirista profissional especializado em conteúdo para YouTube.

TÍTULO: \{titulo\}
PREMISSA: \{premissa\}

CONTEXTO DO CAPÍTULO ANTERIOR:
\{resumos[-1]\}

INSTRUÇÕES:
- Escreva o capítulo final (conclusão) deste roteiro
- O capítulo deve ter aproximadamente 500 palavras
- Amarre todas as pontas soltas da história
- Proporcione um fechamento satisfatório para os personagens
- Use uma linguagem envolvente adequada para vídeos do YouTube
- Escreva apenas o conteúdo do capítulo, sem títulos ou marcações`
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
        total_images: 10,
        custom_prompt: false,
        custom_instructions: ''
      },
      video: {
        enabled: true,
        resolution: '1920x1080',
        fps: 30,
        format: 'mp4',
        include_subtitles: true,
        transition_duration: 0.5
      },
      prompts: {
        titles: {
          viral: 'Crie títulos virais e envolventes para o vídeo sobre: \{topic\}. Os títulos devem ser chamativos, despertar curiosidade e incentivar cliques.',
          educational: 'Crie títulos educacionais e informativos para o vídeo sobre: \{topic\}. Os títulos devem ser claros, diretos e indicar o valor educacional.',
          professional: 'Crie títulos profissionais e sérios para o vídeo sobre: \{topic\}. Os títulos devem transmitir autoridade e credibilidade.'
        },
        premises: {
          narrative: 'Crie uma premissa narrativa envolvente para um vídeo sobre: \{title\}. A premissa deve contar uma história cativante em aproximadamente \{word_count\} palavras.',
          educational: 'Crie uma premissa educacional estruturada para um vídeo sobre: \{title\}. A premissa deve apresentar os pontos de aprendizado em aproximadamente \{word_count\} palavras.',
          informative: 'Crie uma premissa informativa e objetiva para um vídeo sobre: \{title\}. A premissa deve apresentar fatos e informações relevantes em aproximadamente \{word_count\} palavras.'
        },
        scripts: {
          inicio: `# Prompt — Início

Escreva uma narrativa de \{genre\} intitulada "\{title\}".

Premissa: \{premise\}

Este é o INÍCIO da história. Deve estabelecer:
- Personagens principais e suas motivações
- Cenário e atmosfera da história
- Conflito principal que moverá a narrativa
- Tom inicial da narrativa

**IMPORTANTE:** Seja detalhado, extenso e minucioso na descrição de cenários, personagens, ações e diálogos.`,
          meio: `# Prompt — Meio

Continue a narrativa de \{genre\} intitulada "\{title\}".

CONTEXTO ANTERIOR:
"\{previousContent\}"...

Esta é a continuação do MEIO da história. Deve:
- Continuar a narrativa de forma orgânica e coerente
- Desenvolver os personagens e suas relações
- Intensificar o conflito principal
- Adicionar novos elementos de tensão

**IMPORTANTE:** Seja detalhado, extenso e minucioso. Cada capítulo deve ter conteúdo substancial e rico em detalhes.`,
          fim: `# Prompt — Fim

Continue a narrativa de \{genre\} intitulada "\{title\}".

CONTEXTO ANTERIOR:
"\{previousContent\}"...

Este é o FIM da história. Deve:
- Resolver o conflito principal estabelecido no início
- Proporcionar conclusão satisfatória para todos os personagens principais
- Entregar o clímax esperado da história
- Fechar a história de forma impactante

**IMPORTANTE:** Seja detalhado, extenso e minucioso na conclusão. Garanta um fechamento rico e satisfatório.`
        },
        images: {
          cinematic: 'Crie uma descrição cinematográfica para uma imagem que represente: \{scene_description\}. A imagem deve ter qualidade cinematográfica, boa iluminação e composição profissional.',
          minimalist: 'Crie uma descrição minimalista para uma imagem que represente: \{scene_description\}. A imagem deve ser limpa, simples e com foco no elemento principal.',
          artistic: 'Crie uma descrição artística para uma imagem que represente: \{scene_description\}. A imagem deve ser criativa, expressiva e visualmente impactante.'
        }
      }
    }
  })

  const [activeSection, setActiveSection] = useState('basic')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showChannelsManager, setShowChannelsManager] = useState(false)
  const [showPromptManager, setShowPromptManager] = useState(false)

  // Specialized agents configuration with localStorage persistence
  const [customAgents, setCustomAgents] = useState(() => {
    try {
      const savedAgents = JSON.parse(localStorage.getItem('customAgents') || '{}')
      // Merge saved agents with default agents to ensure all properties exist
      const defaultAgents = {
        millionaire_stories: {
          name: 'Histórias de Milionários',
          description: 'Especializado em narrativas com contraste social, transformação de vida e descobertas emocionais',
          prompts: {
            titles: {
              viral: `Crie títulos virais para histórias de milionários e contraste social sobre: {topic}. 
Os títulos devem:
- Destacar o contraste social (rico vs pobre)
- Despertar curiosidade sobre a transformação
- Incluir elementos emocionais
- Ser chamativos e clickbait
Exemplos: "Milionário Descobre Segredo Chocante...", "Rica Empresária Não Sabia Que Sua Faxineira..."`,
              educational: `Crie títulos educacionais para histórias de milionários sobre: {topic}. 
Foque em:
- Lições de vida e valores
- Contrastes sociais educativos
- Mensagens inspiracionais
- Reflexões sobre riqueza e humanidade`
            },
            premises: {
              narrative: `Crie uma premissa narrativa para história de milionário sobre: {title}.
A premissa deve incluir:
- Personagem milionário/rico com vida aparentemente perfeita
- Personagem de classe baixa com qualidades humanas especiais
- Situação que os conecta (trabalho, acaso, família)
- Descoberta emocional que muda perspectivas
- Contraste entre riqueza material e riqueza humana
- Aproximadamente {word_count} palavras`,
              educational: `Crie uma premissa educacional para história de milionário sobre: {title}.
Deve abordar:
- Lições sobre valores versus dinheiro
- Importância das relações humanas
- Crítica social construtiva
- Mensagens inspiracionais
- Aproximadamente {word_count} palavras`
            },
            scripts: {
              inicio: `Você é um roteirista especializado em HISTÓRIAS DE MILIONÁRIOS com contraste social.

TÍTULO: {titulo}
PREMISSA: {premissa}

ESTILO NARRATIVO - Histórias de Milionários:
- Contraste forte entre riqueza material e pobreza emocional
- Personagens ricos aparentemente bem-sucedidos mas vazios
- Personagens pobres com riqueza humana e valores sólidos
- Descobertas familiares/pessoais que abalam estruturas
- Transformação através do reconhecimento de valores verdadeiros

ESTRUTURA DO INÍCIO:
1. Apresente o protagonista milionário em seu mundo de luxo
2. Mostre sua vida aparentemente perfeita mas emocionalmente vazia
3. Introduza o personagem de classe baixa com suas qualidades humanas
4. Estabeleça a situação que os conectará
5. Plante as sementes da descoberta que mudará tudo

ELEMENTOS OBRIGATÓRIOS:
- Contraste visual entre os dois mundos (luxo vs simplicidade)
- Características que humanizam o personagem pobre
- Sinais de vazio emocional no personagem rico
- Situação inicial que permitirá a descoberta

IMPORTANTE: Seja detalhado, extenso e minucioso. Crie uma introdução rica que estabeleça claramente os contrastes e prepare o terreno para a transformação emocional.`,
              meio: `Você é um roteirista especializado em HISTÓRIAS DE MILIONÁRIOS com contraste social.

TÍTULO: {titulo}
PREMISSA: {premissa}

CONTEXTO ANTERIOR:
{resumos[i-2]}

DESENVOLVIMENTO - Histórias de Milionários:
Esta é a continuação do MEIO da história. Deve desenvolver:

1. APROXIMAÇÃO DOS MUNDOS:
- Situações que forçam a convivência entre os personagens
- Quebra gradual de preconceitos do personagem rico
- Demonstração das qualidades humanas do personagem pobre

2. CONFLITOS E DESCOBERTAS:
- Resistência inicial do milionário em aceitar a realidade
- Pequenas revelações que abalam suas certezas
- Contraste entre valores materiais e humanos

3. INTENSIFICAÇÃO EMOCIONAL:
- Momentos de vulnerabilidade do personagem rico
- Demonstrações de generosidade/sabedoria do personagem pobre
- Pistas sobre a descoberta principal que está por vir

ELEMENTOS ESSENCIAIS:
- Diálogos que revelem diferenças de perspectiva
- Situações que testem os valores de cada personagem
- Crescimento emocional gradual do protagonista
- Preparação para o clímax da descoberta

IMPORTANTE: Seja detalhado, extenso e minucioso. Desenvolva as relações de forma orgânica, mostrando a transformação gradual através de situações concretas.`,
              fim: `Você é um roteirista especializado em HISTÓRIAS DE MILIONÁRIOS com contraste social.

TÍTULO: {titulo}
PREMISSA: {premissa}

CONTEXTO ANTERIOR:
{resumos[-1]}

CONCLUSÃO - Histórias de Milionários:
Este é o FIM da história. Deve proporcionar:

1. REVELAÇÃO PRINCIPAL:
- A descoberta emocional que muda tudo (parentesco, passado, sacrifício)
- Momento de reconhecimento da verdade
- Impacto emocional profundo no protagonista rico

2. TRANSFORMAÇÃO COMPLETA:
- Mudança radical de perspectiva do milionário
- Reconhecimento do valor das pessoas sobre o dinheiro
- Ações concretas que demonstram a mudança

3. RESOLUÇÃO EMOCIONAL:
- Reconexão com valores humanos verdadeiros
- Reparação de danos causados pela arrogância
- Novo equilíbrio entre riqueza material e emocional

4. MENSAGEM FINAL:
- Reflexão sobre o que realmente importa na vida
- Valorização das relações humanas
- Crítica construtiva aos valores puramente materialistas

ELEMENTOS FINAIS OBRIGATÓRIOS:
- Momento catártico de reconhecimento
- Ação redentora do protagonista
- Desfecho que honra ambos os personagens
- Mensagem inspiracional sobre valores humanos

IMPORTANTE: Seja detalhado, extenso e minucioso na conclusão. Crie um final emocionalmente impactante que entregue a transformação completa e deixe uma mensagem poderosa sobre valores humanos versus materiais.`
            },
            images: {
              cinematic: `Crie uma descrição cinematográfica para uma imagem de história de milionários que represente: {scene_description}. 
A imagem deve:
- Destacar contrastes sociais (luxo vs simplicidade)
- Mostrar elementos emocionais da cena
- Ter qualidade cinematográfica e iluminação dramática
- Refletir a transformação ou descoberta emocional
- Incluir simbolismo sobre valores humanos vs materiais`,
              contrast: `Crie uma descrição para imagem que contraste classes sociais representando: {scene_description}.
Foque em:
- Diferenças visuais claras entre riqueza e simplicidade
- Elementos que humanizem ambos os personagens
- Composição que destaque a conexão emocional
- Simbolismo sobre verdadeira riqueza`
            }
          }
        }
      }
      
      // Merge saved agents with defaults
      const mergedAgents = { ...defaultAgents }
      Object.keys(savedAgents).forEach(key => {
        if (mergedAgents[key]) {
          // Merge prompts
          mergedAgents[key].prompts = { 
            ...mergedAgents[key].prompts, 
            ...savedAgents[key].prompts 
          }
        } else {
          // Add new agent
          mergedAgents[key] = savedAgents[key]
        }
      })
      
      return mergedAgents
    } catch (e) {
      console.error('Failed to load saved agents from localStorage:', e)
      // Return default agents if there's an error
      return {
        millionaire_stories: {
          name: 'Histórias de Milionários',
          description: 'Especializado em narrativas com contraste social, transformação de vida e descobertas emocionais',
          prompts: {
            titles: {
              viral: `Crie títulos virais para histórias de milionários e contraste social sobre: {topic}. 
Os títulos devem:
- Destacar o contraste social (rico vs pobre)
- Despertar curiosidade sobre a transformação
- Incluir elementos emocionais
- Ser chamativos e clickbait
Exemplos: "Milionário Descobre Segredo Chocante...", "Rica Empresária Não Sabia Que Sua Faxineira..."`,
              educational: `Crie títulos educacionais para histórias de milionários sobre: {topic}. 
Foque em:
- Lições de vida e valores
- Contrastes sociais educativos
- Mensagens inspiracionais
- Reflexões sobre riqueza e humanidade`
            },
            premises: {
              narrative: `Crie uma premissa narrativa para história de milionário sobre: {title}.
A premissa deve incluir:
- Personagem milionário/rico com vida aparentemente perfeita
- Personagem de classe baixa com qualidades humanas especiais
- Situação que os conecta (trabalho, acaso, família)
- Descoberta emocional que muda perspectivas
- Contraste entre riqueza material e riqueza humana
- Aproximadamente {word_count} palavras`,
              educational: `Crie uma premissa educacional para história de milionário sobre: {title}.
Deve abordar:
- Lições sobre valores versus dinheiro
- Importância das relações humanas
- Crítica social construtiva
- Mensagens inspiracionais
- Aproximadamente {word_count} palavras`
            },
            scripts: {
              inicio: `Você é um roteirista especializado em HISTÓRIAS DE MILIONÁRIOS com contraste social.

TÍTULO: {titulo}
PREMISSA: {premissa}

ESTILO NARRATIVO - Histórias de Milionários:
- Contraste forte entre riqueza material e pobreza emocional
- Personagens ricos aparentemente bem-sucedidos mas vazios
- Personagens pobres com riqueza humana e valores sólidos
- Descobertas familiares/pessoais que abalam estruturas
- Transformação através do reconhecimento de valores verdadeiros

ESTRUTURA DO INÍCIO:
1. Apresente o protagonista milionário em seu mundo de luxo
2. Mostre sua vida aparentemente perfeita mas emocionalmente vazia
3. Introduza o personagem de classe baixa com suas qualidades humanas
4. Estabeleça a situação que os conectará
5. Plante as sementes da descoberta que mudará tudo

ELEMENTOS OBRIGATÓRIOS:
- Contraste visual entre os dois mundos (luxo vs simplicidade)
- Características que humanizam o personagem pobre
- Sinais de vazio emocional no personagem rico
- Situação inicial que permitirá a descoberta

IMPORTANTE: Seja detalhado, extenso e minucioso. Crie uma introdução rica que estabeleça claramente os contrastes e prepare o terreno para a transformação emocional.`,
              meio: `Você é um roteirista especializado em HISTÓRIAS DE MILIONÁRIOS com contraste social.

TÍTULO: {titulo}
PREMISSA: {premissa}

CONTEXTO ANTERIOR:
{resumos[i-2]}

DESENVOLVIMENTO - Histórias de Milionários:
Esta é a continuação do MEIO da história. Deve desenvolver:

1. APROXIMAÇÃO DOS MUNDOS:
- Situações que forçam a convivência entre os personagens
- Quebra gradual de preconceitos do personagem rico
- Demonstração das qualidades humanas do personagem pobre

2. CONFLITOS E DESCOBERTAS:
- Resistência inicial do milionário em aceitar a realidade
- Pequenas revelações que abalam suas certezas
- Contraste entre valores materiais e humanos

3. INTENSIFICAÇÃO EMOCIONAL:
- Momentos de vulnerabilidade do personagem rico
- Demonstrações de generosidade/sabedoria do personagem pobre
- Pistas sobre a descoberta principal que está por vir

ELEMENTOS ESSENCIAIS:
- Diálogos que revelem diferenças de perspectiva
- Situações que testem os valores de cada personagem
- Crescimento emocional gradual do protagonista
- Preparação para o clímax da descoberta

IMPORTANTE: Seja detalhado, extenso e minucioso. Desenvolva as relações de forma orgânica, mostrando a transformação gradual através de situações concretas.`,
              fim: `Você é um roteirista especializado em HISTÓRIAS DE MILIONÁRIOS com contraste social.

TÍTULO: {titulo}
PREMISSA: {premissa}

CONTEXTO ANTERIOR:
{resumos[-1]}

CONCLUSÃO - Histórias de Milionários:
Este é o FIM da história. Deve proporcionar:

1. REVELAÇÃO PRINCIPAL:
- A descoberta emocional que muda tudo (parentesco, passado, sacrifício)
- Momento de reconhecimento da verdade
- Impacto emocional profundo no protagonista rico

2. TRANSFORMAÇÃO COMPLETA:
- Mudança radical de perspectiva do milionário
- Reconhecimento do valor das pessoas sobre o dinheiro
- Ações concretas que demonstram a mudança

3. RESOLUÇÃO EMOCIONAL:
- Reconexão com valores humanos verdadeiros
- Reparação de danos causados pela arrogância
- Novo equilíbrio entre riqueza material e emocional

4. MENSAGEM FINAL:
- Reflexão sobre o que realmente importa na vida
- Valorização das relações humanas
- Crítica construtiva aos valores puramente materialistas

ELEMENTOS FINAIS OBRIGATÓRIOS:
- Momento catártico de reconhecimento
- Ação redentora do protagonista
- Desfecho que honra ambos os personagens
- Mensagem inspiracional sobre valores humanos

IMPORTANTE: Seja detalhado, extenso e minucioso na conclusão. Crie um final emocionalmente impactante que entregue a transformação completa e deixe uma mensagem poderosa sobre valores humanos versus materiais.`
            },
            images: {
              cinematic: `Crie uma descrição cinematográfica para uma imagem de história de milionários que represente: {scene_description}. 
A imagem deve:
- Destacar contrastes sociais (luxo vs simplicidade)
- Mostrar elementos emocionais da cena
- Ter qualidade cinematográfica e iluminação dramática
- Refletir a transformação ou descoberta emocional
- Incluir simbolismo sobre valores humanos vs materiais`,
              contrast: `Crie uma descrição para imagem que contraste classes sociais representando: {scene_description}.
Foque em:
- Diferenças visuais claras entre riqueza e simplicidade
- Elementos que humanizem ambos os personagens
- Composição que destaque a conexão emocional
- Simbolismo sobre verdadeira riqueza`
            }
          }
        }
      }
    }
  })

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
      // Include specialized agent data in submission
      const submissionData = {
        ...formData,
        specialized_agents: customAgents
      }
      await onSubmit(submissionData)
    } catch (error) {
      console.error('Erro ao submeter formulário:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  // Handlers for saved selections
  const handleSelectChannel = (channel) => {
    setFormData(prev => ({
      ...prev,
      channel_url: channel.url || channel.channel_id || ''
    }))
    setShowChannelsManager(false)
  }

  const handleSelectPrompt = (prompt) => {
    const { prompt_text } = prompt
    
    // Update the appropriate prompt field based on current context
    setFormData(prev => ({
      ...prev,
      config: {
        ...prev.config,
        titles: {
          ...prev.config.titles,
          custom_instructions: prompt_text
        }
      }
    }))
    setShowPromptManager(false)
  }

  const sections = [
    { id: 'basic', label: 'Básico', icon: Youtube },
    { id: 'agents', label: 'Agentes', icon: Bot },
    { id: 'ai', label: 'IA & Conteúdo', icon: Sparkles },
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
                <BasicSection 
                  formData={formData} 
                  onChange={handleInputChange}
                  onOpenChannelsManager={() => setShowChannelsManager(true)}
                />
              )}
              {activeSection === 'agents' && (
                <AgentSection 
                  formData={formData} 
                  onChange={handleInputChange}
                  specialized_agents={customAgents}
                  onUpdateAgent={setCustomAgents}
                />
              )}
              {activeSection === 'ai' && (
                <AISection 
                  formData={formData} 
                  onChange={handleInputChange}
                  onOpenPromptManager={() => setShowPromptManager(true)}
                />
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

      {/* Modals */}
      {showChannelsManager && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
          <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-4xl max-h-[80vh] overflow-hidden">
            <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 p-4 border-b border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">Canais Salvos</h3>
                <button
                  onClick={() => setShowChannelsManager(false)}
                  className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <X size={18} />
                </button>
              </div>
            </div>
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              <SavedChannelsManager 
                onSelectChannel={handleSelectChannel}
                showInModal={true}
              />
            </div>
          </div>
        </div>
      )}

      {showPromptManager && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
          <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-4xl max-h-[80vh] overflow-hidden">
            <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 p-4 border-b border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">Prompts Salvos</h3>
                <button
                  onClick={() => setShowPromptManager(false)}
                  className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <X size={18} />
                </button>
              </div>
            </div>
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              <CustomPromptManager 
                onSelectPrompt={handleSelectPrompt}
                showInModal={true}
              />
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}

// Seção Básica
const BasicSection = ({ formData, onChange, onOpenChannelsManager }) => {
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
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-300">
              URL do Canal do YouTube *
            </label>
            <button
              type="button"
              onClick={onOpenChannelsManager}
              className="flex items-center space-x-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors"
            >
              <Save size={14} />
              <span>Canais Salvos</span>
            </button>
          </div>
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

// Seção de Agentes Especializados
const AgentSection = ({ formData, onChange, specialized_agents, onUpdateAgent }) => {
  const [editingAgent, setEditingAgent] = useState(null)
  const [editingPromptType, setEditingPromptType] = useState(null)
  const [editingPromptSubtype, setEditingPromptSubtype] = useState(null)
  const [promptText, setPromptText] = useState('')

  const openPromptEditor = (agentKey, promptType, subtype = null) => {
    const agent = specialized_agents[agentKey]
    let currentPrompt = ''
    
    if (subtype) {
      currentPrompt = agent.prompts[promptType]?.[subtype] || ''
    } else {
      currentPrompt = agent.prompts[promptType] || ''
    }
    
    setEditingAgent(agentKey)
    setEditingPromptType(promptType)
    setEditingPromptSubtype(subtype)
    setPromptText(currentPrompt)
  }

  const savePrompt = () => {
    const updatedAgents = { ...specialized_agents }
    
    if (editingPromptSubtype) {
      if (!updatedAgents[editingAgent].prompts[editingPromptType]) {
        updatedAgents[editingAgent].prompts[editingPromptType] = {}
      }
      updatedAgents[editingAgent].prompts[editingPromptType][editingPromptSubtype] = promptText
    } else {
      updatedAgents[editingAgent].prompts[editingPromptType] = promptText
    }
    
    onUpdateAgent(updatedAgents)
    
    // Persist changes to localStorage
    try {
      const savedAgents = JSON.parse(localStorage.getItem('customAgents') || '{}')
      savedAgents[editingAgent] = updatedAgents[editingAgent]
      localStorage.setItem('customAgents', JSON.stringify(savedAgents))
    } catch (e) {
      console.error('Failed to save agent prompts to localStorage:', e)
    }
    
    setEditingAgent(null)
    setEditingPromptType(null)
    setEditingPromptSubtype(null)
    setPromptText('')
  }

  const cancelEdit = () => {
    setEditingAgent(null)
    setEditingPromptType(null)
    setEditingPromptSubtype(null)
    setPromptText('')
  }
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Bot size={20} className="text-purple-400" />
          <span>Agentes Especializados</span>
        </h3>
        <p className="text-gray-400 mb-6">
          Escolha um agente especializado otimizado para tipos específicos de conteúdo ou use o sistema padrão.
        </p>
      </div>

      <div className="space-y-4">
        {/* Tipo de Agente */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3">Tipo de Agente</h4>
          <div className="space-y-3">
            <label className="flex items-center space-x-3 p-3 border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700/50 transition-colors">
              <input
                type="radio"
                name="agent_type"
                value="default"
                checked={formData.agent?.type === 'default'}
                onChange={(e) => onChange('agent.type', e.target.value)}
                className="text-purple-600 focus:ring-purple-500"
              />
              <div>
                <div className="text-white font-medium">Sistema Padrão</div>
                <div className="text-gray-400 text-sm">Prompts genéricos versáteis para qualquer tipo de conteúdo</div>
              </div>
            </label>
            
            <label className="flex items-center space-x-3 p-3 border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700/50 transition-colors">
              <input
                type="radio"
                name="agent_type"
                value="specialized"
                checked={formData.agent?.type === 'specialized'}
                onChange={(e) => onChange('agent.type', e.target.value)}
                className="text-purple-600 focus:ring-purple-500"
              />
              <div className="flex-1">
                <div className="text-white font-medium">Agente Especializado (Recomendado)</div>
                <div className="text-gray-400 text-sm">Prompts otimizados para nichos específicos com melhor qualidade</div>
              </div>
              <div className="bg-purple-600 text-white text-xs px-2 py-1 rounded-full">
                RECOMENDADO
              </div>
            </label>
          </div>
        </div>

        {/* Seleção de Agente Especializado */}
        {formData.agent?.type === 'specialized' && (
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h4 className="text-lg font-medium text-white mb-3">Escolha o Agente Especializado</h4>
            <div className="space-y-4">
              {Object.entries(specialized_agents).map(([key, agent]) => (
                <div key={key} className="border border-gray-600 rounded-lg hover:bg-gray-700/50 transition-colors">
                  <div className="flex items-start space-x-3 p-4">
                    <input
                      type="radio"
                      name="specialized_agent"
                      value={key}
                      checked={formData.agent?.specialized_type === key}
                      onChange={(e) => onChange('agent.specialized_type', e.target.value)}
                      className="mt-1 text-purple-600 focus:ring-purple-500"
                    />
                    <div className="flex-1">
                      <div className="text-white font-medium">{agent.name}</div>
                      <div className="text-gray-400 text-sm">{agent.description}</div>
                    </div>
                  </div>
                  <div className="px-4 pb-4">
                    <div className="text-xs text-gray-500 mb-2">Personalizar prompts:</div>
                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => openPromptEditor(key, 'titles', 'viral')}
                        className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs transition-colors"
                      >
                        Títulos Virais
                      </button>
                      <button
                        type="button"
                        onClick={() => openPromptEditor(key, 'titles', 'educational')}
                        className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs transition-colors"
                      >
                        Títulos Educacionais
                      </button>
                      <button
                        type="button"
                        onClick={() => openPromptEditor(key, 'premises', 'narrative')}
                        className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs transition-colors"
                      >
                        Premissas Narrativas
                      </button>
                      <button
                        type="button"
                        onClick={() => openPromptEditor(key, 'premises', 'educational')}
                        className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs transition-colors"
                      >
                        Premissas Educacionais
                      </button>
                      <button
                        type="button"
                        onClick={() => openPromptEditor(key, 'scripts', 'inicio')}
                        className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs transition-colors"
                      >
                        Roteiro Início
                      </button>
                      <button
                        type="button"
                        onClick={() => openPromptEditor(key, 'scripts', 'meio')}
                        className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs transition-colors"
                      >
                        Roteiro Meio
                      </button>
                      <button
                        type="button"
                        onClick={() => openPromptEditor(key, 'scripts', 'fim')}
                        className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs transition-colors"
                      >
                        Roteiro Fim
                      </button>
                      <button
                        type="button"
                        onClick={() => openPromptEditor(key, 'images', 'cinematic')}
                        className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs transition-colors"
                      >
                        Imagens Cinematográficas
                      </button>
                      <button
                        type="button"
                        onClick={() => openPromptEditor(key, 'images', 'contrast')}
                        className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs transition-colors"
                      >
                        Imagens Contraste
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Modal de Edição de Prompt */}
      {editingAgent && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[70] flex items-center justify-center p-4">
          <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-4xl max-h-[90vh] overflow-hidden">
            <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 p-4 border-b border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">
                  Editar Prompt: {specialized_agents[editingAgent]?.name} - {editingPromptType === 'titles' ? 'Títulos' : editingPromptType === 'premises' ? 'Premissas' : editingPromptType === 'scripts' ? 'Roteiros' : 'Imagens'} - {editingPromptSubtype || 'Geral'}
                </h3>
                <button
                  type="button"
                  onClick={cancelEdit}
                  className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <X size={18} />
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Conteúdo do Prompt
                  </label>
                  <textarea
                    value={promptText}
                    onChange={(e) => setPromptText(e.target.value)}
                    rows={20}
                    className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none transition-colors resize-none font-mono text-sm"
                    placeholder="Digite o conteúdo do prompt personalizado..."
                  />
                </div>
                <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <Info size={16} className="text-blue-400 mt-0.5 flex-shrink-0" />
                    <div className="text-sm">
                      <p className="text-blue-200 font-medium mb-1">Variáveis Disponíveis</p>
                      <p className="text-blue-300">
                        Use variáveis como <code>{'{titulo}'}</code>, <code>{'{premissa}'}</code>, <code>{'{resumos[i-2]}'}</code> para conteúdo dinâmico.
                        Para roteiros, use <code>{'{resumos[-1]}'}</code> no final.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={cancelEdit}
                  className="px-6 py-2 text-gray-400 hover:text-white transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={savePrompt}
                  className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-colors"
                >
                  Salvar Prompt
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Seção de IA
const AISection = ({ formData, onChange, onOpenPromptManager }) => {
  const handleOpenPromptsConfig = () => {
    window.open('/prompts-config', '_blank')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Sparkles size={20} className="text-purple-400" />
          <span>Configuração de IA & Conteúdo</span>
        </h3>
        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={onOpenPromptManager}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm"
          >
            <Save size={14} />
            <span>Prompts Salvos</span>
          </button>
          <button
            type="button"
            onClick={handleOpenPromptsConfig}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors text-sm"
            title="Abrir configuração de prompts personalizados"
          >
            <Settings size={16} />
            <span>Configurar</span>
          </button>
        </div>
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
              <div className="h-20 bg-gray-900 rounded-lg border border-gray-600 relative">
                {formData.config.titles.custom_instructions ? (
                  <p className="p-3 text-sm text-gray-400 line-clamp-3">
                    {formData.config.titles.custom_instructions}
                  </p>
                ) : (
                  <span className="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
                    Nenhum prompt personalizado definido
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
        
        {/* Premissas */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3 flex items-center space-x-2">
            <BookOpen size={18} className="text-green-400" />
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
                <option value="narrative">Narrativa</option>
                <option value="educational">Educacional</option>
                <option value="informative">Informativo</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Público Alvo
              </label>
              <select
                value={formData.config.premises.target_audience}
                onChange={(e) => onChange('config.premises.target_audience', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="general">Geral</option>
                <option value="technical">Técnico</option>
                <option value="children">Crianças</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Palavras
              </label>
              <input
                type="number"
                min="50"
                max="200"
                value={formData.config.premises.word_count}
                onChange={(e) => onChange('config.premises.word_count', parseInt(e.target.value))}
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
              <div className="h-20 bg-gray-900 rounded-lg border border-gray-600 relative">
                {formData.config.premises.custom_instructions ? (
                  <p className="p-3 text-sm text-gray-400 line-clamp-3">
                    {formData.config.premises.custom_instructions}
                  </p>
                ) : (
                  <span className="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
                    Nenhum prompt personalizado definido
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Roteiros */}
        <div className="col-span-2 bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3 flex items-center space-x-2">
            <FileText size={18} className="text-pink-400" />
            <span>Geração de Roteiros</span>
            {formData.config.scripts.system === 'storyteller' && (
              <span className="ml-2 px-2 py-1 bg-purple-600 text-white text-xs rounded-full">
                Storyteller Unlimited Ativo
              </span>
            )}
          </h4>
          {formData.config.scripts.system === 'storyteller' && (
            <div className="mb-4 p-3 bg-purple-900/20 border border-purple-700 rounded-lg">
              <p className="text-sm text-purple-300">
                <strong>Storyteller Unlimited:</strong> Sistema avançado com divisão automática de capítulos, 
                validação de qualidade e 5 agentes especializados. Suporte para até 50 capítulos com 
                contexto inteligente e cache otimizado.
              </p>
            </div>
          )}
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Sistema de Roteiro
              </label>
              <select
                value={formData.config.scripts.system || 'traditional'}
                onChange={(e) => onChange('config.scripts.system', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="traditional">Roteiro Tradicional</option>
                <option value="storyteller">Storyteller Unlimited</option>
              </select>
            </div>
            {(!formData.config.scripts.system || formData.config.scripts.system === 'traditional') && (
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
            )}
            {formData.config.scripts.system === 'storyteller' ? (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Agente de História
                  </label>
                  <select
                    value={formData.config.scripts.storyteller_agent || 'millionaire_stories'}
                    onChange={(e) => onChange('config.scripts.storyteller_agent', e.target.value)}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                  >
                    <option value="millionaire_stories">Histórias de Milionários</option>
                    <option value="romance_agent">Romance</option>
                    <option value="horror_agent">Terror</option>
                    <option value="motivational_agent">Motivacional</option>
                    <option value="business_agent">Negócios</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Capítulos (Storyteller)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={formData.config.scripts.storyteller_chapters || 10}
                    onChange={(e) => onChange('config.scripts.storyteller_chapters', parseInt(e.target.value))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                  />
                </div>
              </>
            ) : (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Número de Capítulos
                  </label>
                  <input
                    type="number"
                    min="1"
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
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                  />
                </div>
              </>
            )}
            {formData.config.scripts.system !== 'storyteller' && (
              <>
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
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="bg-gray-900 rounded-lg border border-gray-600 relative">
                    {formData.config.scripts.custom_inicio ? (
                      <p className="p-3 text-sm text-gray-400 line-clamp-3">
                        {formData.config.scripts.custom_inicio}
                      </p>
                    ) : (
                      <span className="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
                        Nenhum prompt personalizado definido
                      </span>
                    )}
                  </div>
                  <div className="bg-gray-900 rounded-lg border border-gray-600 relative">
                    {formData.config.scripts.custom_meio ? (
                      <p className="p-3 text-sm text-gray-400 line-clamp-3">
                        {formData.config.scripts.custom_meio}
                      </p>
                    ) : (
                      <span className="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
                        Nenhum prompt personalizado definido
                      </span>
                    )}
                  </div>
                  <div className="bg-gray-900 rounded-lg border border-gray-600 relative">
                    {formData.config.scripts.custom_fim ? (
                      <p className="p-3 text-sm text-gray-400 line-clamp-3">
                        {formData.config.scripts.custom_fim}
                      </p>
                    ) : (
                      <span className="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
                        Nenhum prompt personalizado definido
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2 mb-2">
                  <input
                    type="checkbox"
                    id="scripts-detailed-prompt"
                    checked={formData.config.scripts.detailed_prompt}
                    onChange={(e) => onChange('config.scripts.detailed_prompt', e.target.checked)}
                    className="rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                  />
                  <label htmlFor="scripts-detailed-prompt" className="text-sm font-medium text-gray-300">
                    Usar prompt detalhado
                  </label>
                </div>
                <div className="h-20 bg-gray-900 rounded-lg border border-gray-600 relative">
                  {formData.config.scripts.detailed_prompt_text ? (
                    <p className="p-3 text-sm text-gray-400 line-clamp-3">
                      {formData.config.scripts.detailed_prompt_text}
                    </p>
                  ) : (
                    <span className="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
                      Nenhum prompt detalhado definido
                    </span>
                  )}
                </div>
                <div className="flex items-center space-x-2 mb-2">
                  <input
                    type="checkbox"
                    id="scripts-contextual-chapters"
                    checked={formData.config.scripts.contextual_chapters}
                    onChange={(e) => onChange('config.scripts.contextual_chapters', e.target.checked)}
                    className="rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                  />
                  <label htmlFor="scripts-contextual-chapters" className="text-sm font-medium text-gray-300">
                    Usar capítulos contextuais
                  </label>
                </div>
                <div className="flex items-center space-x-2 mb-2">
                  <input
                    type="checkbox"
                    id="scripts-show-default-prompts"
                    checked={formData.config.scripts.show_default_prompts}
                    onChange={(e) => onChange('config.scripts.show_default_prompts', e.target.checked)}
                    className="rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                  />
                  <label htmlFor="scripts-show-default-prompts" className="text-sm font-medium text-gray-300">
                    Mostrar prompts padrões
                  </label>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Seção de Mídia & Vídeo
const MediaSection = ({ formData, onChange }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Video size={20} className="text-green-400" />
          <span>Configuração de Mídia e Vídeo</span>
        </h3>
      </div>

      <div className="space-y-4">
        {/* TTS */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3 flex items-center space-x-2">
            <Mic size={18} className="text-purple-400" />
            <span>Geração de Áudio</span>
          </h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Provedor de TTS
              </label>
              <select
                value={formData.config.tts.provider}
                onChange={(e) => onChange('config.tts.provider', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="kokoro">Kokoro</option>
                <option value="elevenlabs">ElevenLabs</option>
                <option value="google">Google</option>
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
                <option value="af_bella">Bella (AF)</option>
                <option value="af_charlotte">Charlotte (AF)</option>
                <option value="af_daniel">Daniel (AF)</option>
                <option value="af_james">James (AF)</option>
                <option value="af_jill">Jill (AF)</option>
                <option value="af_olivia">Olivia (AF)</option>
                <option value="af_robert">Robert (AF)</option>
                <option value="af_tom">Tom (AF)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Idioma
              </label>
              <input
                type="text"
                value={formData.config.tts.language}
                onChange={(e) => onChange('config.tts.language', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Velocidade
              </label>
              <input
                type="number"
                step="0.1"
                min="0.5"
                max="2.0"
                value={formData.config.tts.speed}
                onChange={(e) => onChange('config.tts.speed', parseFloat(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Tom
              </label>
              <input
                type="number"
                step="0.1"
                min="0.5"
                max="2.0"
                value={formData.config.tts.pitch}
                onChange={(e) => onChange('config.tts.pitch', parseFloat(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              />
            </div>
          </div>
        </div>

        {/* Imagens */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-lg font-medium text-white mb-3 flex items-center space-x-2">
            <Image size={18} className="text-yellow-400" />
            <span>Geração de Imagens</span>
          </h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Provedor de IA
              </label>
              <select
                value={formData.config.images.provider}
                onChange={(e) => onChange('config.images.provider', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="pollinations">Pollinations</option>
                <option value="deepai">DeepAI</option>
                <option value="dall-e">DALL-E</option>
              </select>
            </div>
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
                <option value="cartoon">Cartunizado</option>
                <option value="artistic">Artístico</option>
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
                <option value="high">Alta</option>
                <option value="medium">Média</option>
                <option value="low">Baixa</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Imagens Totais
              </label>
              <input
                type="number"
                min="1"
                max="20"
                value={formData.config.images.total_images}
                onChange={(e) => onChange('config.images.total_images', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              />
            </div>
            <div className="col-span-2">
              <div className="flex items-center space-x-2 mb-2">
                <input
                  type="checkbox"
                  id="images-custom-prompt"
                  checked={formData.config.images.custom_prompt}
                  onChange={(e) => onChange('config.images.custom_prompt', e.target.checked)}
                  className="rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                />
                <label htmlFor="images-custom-prompt" className="text-sm font-medium text-gray-300">
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
                <option value="narrative">Narrativo</option>
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
                value={formData.config.scripts.chapters}
                onChange={(e) => onChange('config.scripts.chapters', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              />
              <p className="text-xs text-gray-500 mt-1">
                Sem limite máximo de capítulos
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Duração Alvo
              </label>
              <select
                value={formData.config.scripts.duration_target}
                onChange={(e) => onChange('config.scripts.duration_target', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm mb-2"
              >
                <option value="5-7 minutes">5-7 minutos</option>
                <option value="10-15 minutes">10-15 minutos</option>
                <option value="20-30 minutes">20-30 minutos</option>
                <option value="1-2 hours">1-2 horas</option>
              </select>
              <input
                type="text"
                value={formData.config.scripts.duration_target}
                onChange={(e) => onChange('config.scripts.duration_target', e.target.value)}
                placeholder="Ou digite uma duração personalizada"
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
              <div className="flex items-center space-x-2 mb-2">
                <input
                  type="checkbox"
                  id="scripts-detailed-prompt"
                  checked={formData.config.scripts.detailed_prompt}
                  onChange={(e) => onChange('config.scripts.detailed_prompt', e.target.checked)}
                  className="rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                />
                <label htmlFor="scripts-detailed-prompt" className="text-sm font-medium text-gray-300">
                  Usar prompt detalhado para roteiros longos
                </label>
              </div>
              <div className="flex items-center space-x-2 mb-2">
                <input
                  type="checkbox"
                  id="scripts-contextual-chapters"
                  checked={formData.config.scripts.contextual_chapters}
                  onChange={(e) => onChange('config.scripts.contextual_chapters', e.target.checked)}
                  className="rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                />
                <label htmlFor="scripts-contextual-chapters" className="text-sm font-medium text-gray-300">
                  Gerar roteiro longo com resumos contextuais entre capítulos
                </label>
              </div>
              <div className="flex items-center space-x-2 mb-2">
                <input
                  type="checkbox"
                  id="scripts-show-default-prompts"
                  checked={formData.config.scripts.show_default_prompts}
                  onChange={(e) => onChange('config.scripts.show_default_prompts', e.target.checked)}
                  className="rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                />
                <label htmlFor="scripts-show-default-prompts" className="text-sm font-medium text-gray-300">
                  Mostrar e editar prompts padrão do sistema
                </label>
              </div>
              {formData.config.scripts.detailed_prompt && (
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Prompt Detalhado para Roteiro Longo
                    </label>
                    <textarea
                      value={formData.config.scripts.detailed_prompt_text}
                      onChange={(e) => onChange('config.scripts.detailed_prompt_text', e.target.value)}
                      placeholder="Instruções detalhadas para a geração do roteiro longo, incluindo estilo, tom, elementos narrativos, estrutura desejada, etc..."
                      rows={5}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm resize-none"
                    />
                  </div>
                </div>
              )}
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
              {formData.config.scripts.show_default_prompts && (
                <div className="space-y-4 border-t border-gray-600 pt-4">
                  <div className="flex items-center space-x-2">
                    <Info size={16} className="text-blue-400" />
                    <h5 className="text-sm font-medium text-gray-300">Prompts Padrão do Sistema</h5>
                  </div>
                  <div className="text-xs text-gray-400 bg-gray-700 p-2 rounded">
                    Estes são os prompts padrão que o sistema usa para gerar roteiros longos contextuais. Você pode visualizar e editá-los aqui.
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Prompt Padrão - Introdução (1º capítulo)
                    </label>
                    <textarea
                      value={formData.config.scripts.default_prompt_intro}
                      onChange={(e) => onChange('config.scripts.default_prompt_intro', e.target.value)}
                      rows={8}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm resize-none font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Prompt Padrão - Desenvolvimento (capítulos do meio)
                    </label>
                    <textarea
                      value={formData.config.scripts.default_prompt_middle}
                      onChange={(e) => onChange('config.scripts.default_prompt_middle', e.target.value)}
                      rows={8}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm resize-none font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Prompt Padrão - Conclusão (último capítulo)
                    </label>
                    <textarea
                      value={formData.config.scripts.default_prompt_conclusion}
                      onChange={(e) => onChange('config.scripts.default_prompt_conclusion', e.target.value)}
                      rows={8}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm resize-none font-mono"
                    />
                  </div>
                  <div className="text-xs text-amber-400 bg-amber-900/20 p-2 rounded flex items-start space-x-2">
                    <AlertCircle size={14} className="mt-0.5 flex-shrink-0" />
                    <span>Variáveis disponíveis: {'{titulo}'}, {'{premissa}'}, {'{resumos[i-2]}'} (capítulos do meio), {'{resumos[-1]}'} (conclusão), {'{i}'} (número do capítulo)</span>
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