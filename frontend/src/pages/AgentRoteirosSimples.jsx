import React, { useState, useEffect } from 'react'
import { FileText, Upload, Download, Copy, Zap } from 'lucide-react'

const AgentRoteirosSimples = () => {
  // Prompt padrão otimizado para roteiros
  const defaultAgentPrompt = `FORMATO: Roteiro completo para vídeo do YouTube
DURAÇÃO: 8-15 minutos
ESTILO: Conversacional, envolvente e profissional
PÚBLICO: Brasileiro, interessado no tema

ESTRUTURA OBRIGATÓRIA DO ROTEIRO:

[ABERTURA - 0:00 a 1:00]
• Hook inicial relacionado ao título
• Apresentação do criador
• Promise do que será entregue
• Convite para like e inscrição

[INTRODUÇÃO - 1:00 a 2:30]
• Contextualização do tema
• Por que é importante/relevante
• O que o espectador vai aprender

[DESENVOLVIMENTO - 2:30 a 12:00]
• Conteúdo principal dividido em 3-5 seções
• Exemplos práticos e casos reais
• Dicas acionáveis
• Momentos de interação com o público

[CONCLUSÃO - 12:00 a 15:00]
• Resumo dos pontos principais
• Call-to-action específico
• Convite para comentários e engajamento
• Sugestão de próximo conteúdo

DIRETRIZES DE ESCRITA:
✓ Use linguagem natural e direta
✓ Inclua pausas marcadas com [PAUSA]
✓ Adicione sugestões visuais [VISUAL: descrição]
✓ Mantenha parágrafos curtos e dinâmicos
✓ Inclua perguntas retóricas para engajamento
✓ Use storytelling quando apropriado
✓ Foque em entregar valor real e prático

IMPORTANTE: Leia TODAS as informações fornecidas (título, premissa, arquivos de contexto) e crie um roteiro que integre todos esses elementos de forma coerente e natural.`

  // Estados do agente
  const [agentPrompt, setAgentPrompt] = useState(defaultAgentPrompt)
  const [agentContextFiles, setAgentContextFiles] = useState([])
  const [agentContextText, setAgentContextText] = useState('')
  const [selectedAgentTitle, setSelectedAgentTitle] = useState('')
  const [selectedAgentPremise, setSelectedAgentPremise] = useState('')
  const [agentAiProvider, setAgentAiProvider] = useState('auto')
  const [agentOpenRouterModel, setAgentOpenRouterModel] = useState('auto')
  const [agentNumChapters, setAgentNumChapters] = useState(3) // Número de capítulos (1-8)
  const [isGeneratingAgentScript, setIsGeneratingAgentScript] = useState(false)
  const [agentGeneratedScript, setAgentGeneratedScript] = useState(null)
  const [agentInstructions, setAgentInstructions] = useState('')

  // Estados para dados existentes
  const [generatedTitles, setGeneratedTitles] = useState(null)
  const [generatedPremises, setGeneratedPremises] = useState([])



  // Carregar dados existentes
  useEffect(() => {
    // Tentar carregar dados reais do localStorage primeiro
    const loadStoredData = () => {
      try {
        const storedTitles = localStorage.getItem('generatedTitles')
        const storedPremises = localStorage.getItem('generatedPremises')

        if (storedTitles) {
          const titles = JSON.parse(storedTitles)
          if (titles && titles.generated_titles && titles.generated_titles.length > 0) {
            setGeneratedTitles(titles)
            console.log('✅ Títulos carregados do localStorage:', titles.generated_titles.length)
          }
        }

        if (storedPremises) {
          const premises = JSON.parse(storedPremises)
          if (premises && premises.length > 0) {
            setGeneratedPremises(premises)
            console.log('✅ Premissas carregadas do localStorage:', premises.length)
          }
        }
      } catch (error) {
        console.log('ℹ️ Nenhum dado salvo encontrado, usando dados de exemplo')
      }

      // Se não houver dados salvos, usar dados de exemplo
      if (!generatedTitles || !generatedTitles.generated_titles) {
        const mockTitles = {
          generated_titles: [
            "Como Ganhar Dinheiro Online em 2024",
            "O Segredo dos Milionários Revelado",
            "Transforme Sua Vida em 30 Dias",
            "A Verdade Sobre Investimentos que Ninguém Te Conta",
            "Como Sair da Zona de Conforto e Ter Sucesso"
          ]
        }
        setGeneratedTitles(mockTitles)
        console.log('📝 Títulos de exemplo carregados')
      }

      if (!generatedPremises || generatedPremises.length === 0) {
        const mockPremises = [
          {
            title: "Como Ganhar Dinheiro Online em 2024",
            premise: "Uma história inspiradora sobre como uma pessoa comum descobriu métodos revolucionários para gerar renda na internet, superando todas as dificuldades e transformando sua vida financeira."
          },
          {
            title: "O Segredo dos Milionários Revelado",
            premise: "Revelação dos hábitos e estratégias secretas que os milionários usam para multiplicar sua riqueza, baseado em anos de pesquisa e entrevistas exclusivas."
          },
          {
            title: "Transforme Sua Vida em 30 Dias",
            premise: "Um desafio real de transformação pessoal onde acompanhamos alguém mudando completamente seus hábitos e mentalidade em apenas um mês."
          }
        ]
        setGeneratedPremises(mockPremises)
        console.log('🎯 Premissas de exemplo carregadas')
      }
    }

    loadStoredData()
  }, [])

  // Função para ler arquivos TXT
  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files)
    
    files.forEach(file => {
      if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          const content = e.target.result
          setAgentContextFiles(prev => [...prev, {
            name: file.name,
            content: content,
            size: file.size
          }])
        }
        reader.readAsText(file, 'UTF-8')
      } else {
        alert('Por favor, selecione apenas arquivos .txt')
      }
    })
  }

  // Função para remover arquivo de contexto
  const removeContextFile = (index) => {
    setAgentContextFiles(prev => prev.filter((_, i) => i !== index))
  }

  // Função para gerar roteiro com o agente personalizado
  const handleGenerateAgentScript = async () => {
    if (!selectedAgentTitle.trim()) {
      alert('Digite ou selecione um título')
      return
    }

    if (!selectedAgentPremise.trim()) {
      alert('Digite ou selecione uma premissa')
      return
    }

    if (!agentPrompt.trim()) {
      alert('Digite um prompt personalizado')
      return
    }

    setIsGeneratingAgentScript(true)

    try {
      console.log('🚀 Iniciando geração do roteiro...')
      console.log('📝 Título:', selectedAgentTitle)
      console.log('🎯 Premissa:', selectedAgentPremise.substring(0, 100) + '...')
      console.log('🤖 Provider:', agentAiProvider)

      // Usar diretamente o prompt personalizado com as informações do projeto
      let fullPrompt = `${agentPrompt}

## INFORMAÇÕES DO PROJETO:

### TÍTULO DO VÍDEO:
${selectedAgentTitle}

### PREMISSA/CONCEITO:
${selectedAgentPremise}`

      // Adicionar instruções específicas se fornecidas
      if (agentInstructions.trim()) {
        fullPrompt += `

### INSTRUÇÕES ESPECÍFICAS ADICIONAIS:
${agentInstructions}`
      }

      // Adicionar contexto dos arquivos
      if (agentContextFiles.length > 0) {
        fullPrompt += `

### MATERIAIS DE REFERÊNCIA:`
        agentContextFiles.forEach(file => {
          fullPrompt += `

**Arquivo: ${file.name}**
${file.content}`
        })
      }

      // Adicionar contexto adicional se fornecido
      if (agentContextText.trim()) {
        fullPrompt += `

### CONTEXTO ADICIONAL:
${agentContextText}`
      }

      // Adicionar instruções finais simples
      fullPrompt += `

## INSTRUÇÕES FINAIS:
Agora gere o roteiro completo seguindo EXATAMENTE o formato especificado acima, usando o título e premissa fornecidos.`

      console.log('📄 Prompt construído, tamanho:', fullPrompt.length, 'caracteres')
      console.log('📋 Estrutura do prompt:')
      console.log('  - Título:', selectedAgentTitle)
      console.log('  - Premissa:', selectedAgentPremise.substring(0, 100) + '...')
      console.log('  - Instruções de estilo:', agentPrompt.substring(0, 100) + '...')
      console.log('  - Arquivos de contexto:', agentContextFiles.length)
      console.log('  - Contexto adicional:', agentContextText ? 'Sim' : 'Não')
      console.log('  - Instruções específicas:', agentInstructions ? 'Sim' : 'Não')

      // Log do prompt completo (primeiros 500 caracteres para debug)
      console.log('🔍 Preview do prompt final:')
      console.log(fullPrompt.substring(0, 500) + '...')

      // Carregar chaves de API do backend
      console.log('🔑 Carregando chaves de API...')
      const keysResponse = await fetch('http://localhost:5000/api/settings/api-keys')
      const keysData = await keysResponse.json()

      console.log('📊 Resposta das chaves:', keysData)

      if (!keysData.success) {
        throw new Error('Não foi possível carregar as chaves de API: ' + (keysData.error || 'Erro desconhecido'))
      }

      // Verificar se os dados existem (backend retorna 'keys', não 'data')
      const apiKeys = keysData.keys || {}
      console.log('✅ Chaves carregadas:', Object.keys(apiKeys))

      // Usar o endpoint específico do agente para roteiros extensos
      let endpoint = 'http://localhost:5000/api/premise/generate-agent-script'
      let requestBody = {
        title: selectedAgentTitle,
        premise: selectedAgentPremise,
        custom_prompt: agentPrompt, // Prompt personalizado do usuário
        ai_provider: agentAiProvider,
        openrouter_model: agentOpenRouterModel,
        num_chapters: agentNumChapters, // Número de capítulos
        api_keys: apiKeys // Chaves carregadas do backend
      }

      console.log('🎯 Usando endpoint específico do agente para roteiros extensos (~1 hora)')
      console.log('🔑 Chaves disponíveis:', Object.keys(apiKeys))
      console.log('📦 Request body keys:', Object.keys(requestBody))

      console.log('🌐 Endpoint:', endpoint)
      console.log('📦 Request body keys:', Object.keys(requestBody))

      // Verificar se o backend está acessível
      const healthCheck = await fetch('http://localhost:5000/api/system/status', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      }).catch(() => null)

      if (!healthCheck) {
        throw new Error('Backend não está acessível. Verifique se o servidor está rodando em http://localhost:5000')
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(requestBody)
      })

      console.log('📡 Response status:', response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ Response error:', errorText)
        throw new Error(`Erro HTTP ${response.status}: ${errorText}`)
      }

      const data = await response.json()
      console.log('📊 Response data keys:', Object.keys(data))

      if (data.success) {
        let generatedContent = ''

        if (data.script && data.script.content) {
          // O endpoint do agente retorna um objeto 'script' com 'content'
          generatedContent = data.script.content
          console.log('✅ Roteiro extenso gerado com sucesso!')
          console.log('📊 Estatísticas completas:')
          console.log('  - Tamanho do roteiro:', data.script.character_count, 'caracteres')
          console.log('  - Palavras:', data.script.word_count, 'palavras')
          console.log('  - Duração estimada:', data.script.estimated_duration_minutes, 'minutos')
          console.log('🤖 IA usada:', data.provider_used)
          console.log('📄 Tamanho do prompt:', data.prompt_length, 'caracteres')

          // Verificar se é realmente um roteiro extenso
          if (generatedContent.length < 5000) {
            console.warn('⚠️ Roteiro parece curto para ~1 hora de vídeo')
            console.log('📝 Preview:', generatedContent.substring(0, 300) + '...')
          } else {
            console.log('🎬 ROTEIRO EXTENSO GERADO COM SUCESSO!')
            console.log('🎯 Adequado para vídeo de ~1 hora')
          }
        } else {
          console.error('❌ Nenhum roteiro encontrado na resposta:', data)
          throw new Error('Nenhum roteiro gerado pela IA. Verifique se as chaves de API estão configuradas.')
        }

        const scriptData = {
          title: selectedAgentTitle,
          premise: selectedAgentPremise,
          content: generatedContent,
          prompt: agentPrompt, // Prompt personalizado usado
          provider: data.provider_used || agentAiProvider,
          model: agentOpenRouterModel,
          timestamp: new Date().toISOString(),
          characterCount: data.script?.character_count || generatedContent.length,
          wordCount: data.script?.word_count || generatedContent.split(' ').length,
          estimatedDuration: data.script?.estimated_duration_minutes || 0,
          promptLength: data.prompt_length || 0,
          parts: data.script?.parts || [],
          numChapters: data.script?.num_chapters || agentNumChapters,
          generationMethod: data.generation_method || 'single'
        }

        setAgentGeneratedScript(scriptData)

        // Salvar roteiro gerado no localStorage
        try {
          const existingScripts = JSON.parse(localStorage.getItem('generated_scripts') || '[]')
          const updatedScripts = [...existingScripts, {
            id: Date.now().toString(),
            title: scriptData.title,
            content: scriptData.content,
            timestamp: scriptData.timestamp,
            provider: scriptData.provider,
            model: scriptData.model,
            characterCount: scriptData.characterCount,
            wordCount: scriptData.wordCount,
            estimatedDuration: scriptData.estimatedDuration,
            type: 'agent_script'
          }]
          localStorage.setItem('generated_scripts', JSON.stringify(updatedScripts))
          console.log('💾 Roteiro salvo no localStorage')
        } catch (error) {
          console.error('❌ Erro ao salvar roteiro no localStorage:', error)
        }

        console.log('🎉 Roteiro gerado com sucesso!')
        alert('✅ Roteiro gerado com sucesso!')
      } else {
        console.error('❌ API retornou erro:', data)
        throw new Error(data.error || 'Erro na geração do roteiro')
      }
    } catch (error) {
      console.error('💥 Erro completo na geração:', error)

      // Mensagens de erro mais específicas
      let errorMessage = error.message

      if (error.message.includes('Failed to fetch')) {
        errorMessage = 'Não foi possível conectar ao servidor. Verifique se o backend está rodando em http://localhost:5000'
      } else if (error.message.includes('NetworkError')) {
        errorMessage = 'Erro de rede. Verifique sua conexão e se o backend está acessível.'
      } else if (error.message.includes('CORS')) {
        errorMessage = 'Erro de CORS. Verifique as configurações do servidor.'
      }

      alert('❌ Erro na geração: ' + errorMessage)
    } finally {
      setIsGeneratingAgentScript(false)
    }
  }

  // Função para baixar roteiro gerado
  const downloadAgentScript = () => {
    if (!agentGeneratedScript) return

    const content = `TÍTULO: ${agentGeneratedScript.title}

PREMISSA: ${agentGeneratedScript.premise}

ROTEIRO GERADO:
${agentGeneratedScript.content}

---
Gerado em: ${new Date(agentGeneratedScript.timestamp).toLocaleString()}
Provider: ${agentGeneratedScript.provider}
${agentGeneratedScript.model !== 'auto' ? `Modelo: ${agentGeneratedScript.model}` : ''}
`

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `roteiro_agente_${agentGeneratedScript.title.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 30)}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  // Função para testar conectividade com backend
  const testBackendConnection = async () => {
    try {
      console.log('🔍 Testando conexão com backend...')
      const response = await fetch('http://localhost:5000/api/system/status', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })

      if (response.ok) {
        const data = await response.json()
        console.log('✅ Backend conectado:', data)
        alert('✅ Backend está funcionando corretamente!')
      } else {
        throw new Error(`HTTP ${response.status}`)
      }
    } catch (error) {
      console.error('❌ Erro de conexão:', error)
      alert('❌ Erro de conexão com backend: ' + error.message)
    }
  }

  // Função para resetar o agente
  const resetAgent = () => {
    setAgentPrompt('')
    setAgentContextFiles([])
    setAgentContextText('')
    setSelectedAgentTitle('')
    setSelectedAgentPremise('')
    setAgentGeneratedScript(null)
    setAgentInstructions('')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">
            🤖 Agente IA Personalizado para Roteiros
          </h1>
          <p className="text-gray-300 text-lg">
            Crie roteiros profissionais usando IA com prompts personalizados e contexto de arquivos
          </p>
        </div>

        {/* Agente IA Personalizado */}
        <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h4 className="text-xl font-bold text-white flex items-center space-x-2">
              <span className="text-2xl">🤖</span>
              <span>Agente IA Personalizado</span>
              <span className="text-sm bg-purple-600 px-2 py-1 rounded-full">AVANÇADO</span>
            </h4>
            <div className="flex space-x-2">
              <button
                onClick={testBackendConnection}
                className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
              >
                <span>🔍</span>
                <span>Testar Backend</span>
              </button>
              <button
                onClick={() => {
                  setSelectedAgentTitle('')
                  setSelectedAgentPremise('')
                }}
                className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
              >
                <span>🗑️</span>
                <span>Limpar Campos</span>
              </button>
              <button
                onClick={resetAgent}
                className="flex items-center space-x-2 px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
              >
                <span>🔄</span>
                <span>Resetar Tudo</span>
              </button>
            </div>
          </div>

          {/* Título - Manual e Seleção */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              📝 Título do Vídeo
            </label>

            {/* Campo manual sempre visível */}
            <input
              type="text"
              value={selectedAgentTitle}
              onChange={(e) => setSelectedAgentTitle(e.target.value)}
              placeholder="Digite o título do vídeo..."
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent mb-3"
            />

            {/* Seleção de títulos gerados (se disponível) */}
            {generatedTitles && generatedTitles.generated_titles && generatedTitles.generated_titles.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  📋 Ou selecione um título gerado:
                </label>
                <select
                  value=""
                  onChange={(e) => {
                    if (e.target.value) {
                      setSelectedAgentTitle(e.target.value)
                    }
                  }}
                  className="w-full px-4 py-3 bg-gray-600 border border-gray-500 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Selecione um título gerado...</option>
                  {generatedTitles.generated_titles.map((title, index) => (
                    <option key={index} value={title}>
                      {title.length > 80 ? title.substring(0, 80) + '...' : title}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Premissa - Manual e Seleção */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              🎯 Premissa do Vídeo
            </label>

            {/* Campo manual sempre visível */}
            <textarea
              value={selectedAgentPremise}
              onChange={(e) => setSelectedAgentPremise(e.target.value)}
              placeholder="Digite a premissa/história do vídeo..."
              rows={4}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none mb-3"
            />

            {/* Seleção de premissas geradas (se disponível) */}
            {generatedPremises && generatedPremises.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  📋 Ou selecione uma premissa gerada:
                </label>
                <select
                  value=""
                  onChange={(e) => {
                    if (e.target.value) {
                      setSelectedAgentPremise(e.target.value)
                    }
                  }}
                  className="w-full px-4 py-3 bg-gray-600 border border-gray-500 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Selecione uma premissa gerada...</option>
                  {generatedPremises.map((premise, index) => (
                    <option key={index} value={premise.premise}>
                      {premise.title.length > 80 ? premise.title.substring(0, 80) + '...' : premise.title}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Dicas de Uso */}
          <div className="mb-6 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
            <h6 className="text-sm font-medium text-blue-400 mb-2 flex items-center space-x-2">
              <span>💡</span>
              <span>Como Usar o Agente IA:</span>
            </h6>
            <div className="text-xs text-gray-300 space-y-2">
              <div>
                <strong>1. Título:</strong> Digite o título do seu vídeo (ex: "Como Ganhar Dinheiro Online em 2024")
              </div>
              <div>
                <strong>2. Premissa:</strong> Descreva o conceito/história (ex: "Tutorial passo a passo para iniciantes começarem a ganhar dinheiro na internet")
              </div>
              <div>
                <strong>3. Prompt:</strong> O template já está otimizado, mas você pode personalizar o estilo e formato
              </div>
              <div>
                <strong>4. Arquivos (opcional):</strong> Faça upload de materiais de referência em .txt
              </div>
              <div>
                <strong>5. Contexto (opcional):</strong> Adicione informações extras relevantes
              </div>
              <div className="mt-2 p-2 bg-green-900/20 border border-green-500/30 rounded">
                <strong>✨ Resultado:</strong> O agente vai ler TODAS as informações e gerar um roteiro completo que integra título + premissa + estilo + contexto
              </div>
            </div>
          </div>

          {/* Prompt Personalizado */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              🎭 Prompt Personalizado do Agente
            </label>
            <textarea
              value={agentPrompt}
              onChange={(e) => setAgentPrompt(e.target.value)}
              placeholder="Digite seu prompt personalizado para o agente IA..."
              rows={12}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none font-mono text-sm"
            />
          </div>

          {/* Instruções Específicas */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              📋 Instruções Específicas (Opcional)
            </label>
            <textarea
              value={agentInstructions}
              onChange={(e) => setAgentInstructions(e.target.value)}
              placeholder="Ex: Foque em drama familiar, use linguagem jovem, inclua reviravoltas, etc..."
              rows={3}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Upload de Arquivos TXT */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              📁 Arquivos de Contexto (.txt)
            </label>
            <div className="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center">
              <input
                type="file"
                multiple
                accept=".txt"
                onChange={handleFileUpload}
                className="hidden"
                id="context-files"
              />
              <label
                htmlFor="context-files"
                className="cursor-pointer flex flex-col items-center space-y-2"
              >
                <Upload size={48} className="text-gray-400" />
                <span className="text-white">Clique para selecionar arquivos .txt</span>
                <span className="text-gray-400 text-sm">Os arquivos serão usados como contexto para o agente</span>
              </label>
            </div>

            {/* Lista de arquivos carregados */}
            {agentContextFiles.length > 0 && (
              <div className="mt-4 space-y-2">
                <h6 className="text-sm font-medium text-gray-300">Arquivos Carregados:</h6>
                {agentContextFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <FileText className="text-blue-400" size={20} />
                      <span className="text-white text-sm">{file.name}</span>
                      <span className="text-gray-400 text-xs">({(file.size / 1024).toFixed(1)} KB)</span>
                    </div>
                    <button
                      onClick={() => removeContextFile(index)}
                      className="text-red-400 hover:text-red-300 text-sm"
                    >
                      ❌
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Contexto Adicional */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              💭 Contexto Adicional (Opcional)
            </label>
            <textarea
              value={agentContextText}
              onChange={(e) => setAgentContextText(e.target.value)}
              placeholder="Digite qualquer contexto adicional que o agente deve considerar..."
              rows={4}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Configurações de IA */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* Provider de IA */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                🤖 Provider de IA
              </label>
              <select
                value={agentAiProvider}
                onChange={(e) => setAgentAiProvider(e.target.value)}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="auto">🎯 Automático (Gemini)</option>
                <option value="gemini">💎 Gemini</option>
                <option value="openai">🧠 OpenAI</option>
                <option value="openrouter">🌐 OpenRouter</option>
              </select>
            </div>

            {/* Número de Capítulos */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                📚 Número de Capítulos
              </label>
              <select
                value={agentNumChapters}
                onChange={(e) => setAgentNumChapters(parseInt(e.target.value))}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={1}>1 Capítulo (Rápido)</option>
                <option value={2}>2 Capítulos (Médio)</option>
                <option value={3}>3 Capítulos (Padrão)</option>
                <option value={4}>4 Capítulos (Extenso)</option>
                <option value={5}>5 Capítulos (Longo)</option>
                <option value={6}>6 Capítulos (Muito Longo)</option>
                <option value={7}>7 Capítulos (Épico)</option>
                <option value={8}>8 Capítulos (Máximo)</option>
              </select>
              <p className="text-xs text-gray-400 mt-1">
                Mais capítulos = roteiro mais extenso (~{2 + agentNumChapters} partes)
              </p>
            </div>

            {/* Modelo OpenRouter */}
            {agentAiProvider === 'openrouter' && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  🎛️ Modelo OpenRouter
                </label>
                <select
                  value={agentOpenRouterModel}
                  onChange={(e) => setAgentOpenRouterModel(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="auto">Automático</option>
                  <option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet</option>
                  <option value="openai/gpt-4o">GPT-4o</option>
                  <option value="google/gemini-1.5-flash">Gemini 1.5 Flash</option>
                  <option value="meta-llama/llama-3.1-405b-instruct">Llama 3.1 405B</option>
                </select>
              </div>
            )}
          </div>

          {/* Botão de Geração */}
          <button
            onClick={handleGenerateAgentScript}
            disabled={isGeneratingAgentScript || !selectedAgentTitle || !selectedAgentPremise || !agentPrompt.trim()}
            className={`w-full flex items-center justify-center space-x-2 px-6 py-4 rounded-lg font-medium transition-all text-lg ${
              isGeneratingAgentScript || !selectedAgentTitle || !selectedAgentPremise || !agentPrompt.trim()
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 hover:shadow-lg transform hover:scale-105'
            }`}
          >
            {isGeneratingAgentScript ? (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                <span>Gerando Roteiro...</span>
              </>
            ) : (
              <>
                <Zap size={24} />
                <span>Gerar Roteiro com Agente IA</span>
              </>
            )}
          </button>

          {/* Resultado do Agente */}
          {agentGeneratedScript && (
            <div className="mt-8 p-6 bg-gradient-to-r from-green-900/20 to-blue-900/20 border border-green-500/30 rounded-xl">
              <div className="flex items-center justify-between mb-4">
                <h5 className="text-xl font-bold text-white flex items-center space-x-2">
                  <span className="text-2xl">✨</span>
                  <span>Roteiro Gerado pelo Agente IA</span>
                </h5>
                <div className="flex space-x-2">
                  <button
                    onClick={() => navigator.clipboard.writeText(agentGeneratedScript.content)}
                    className="flex items-center space-x-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    <Copy size={16} />
                    <span>Copiar</span>
                  </button>
                  <button
                    onClick={downloadAgentScript}
                    className="flex items-center space-x-1 px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
                  >
                    <Download size={16} />
                    <span>Baixar</span>
                  </button>
                </div>
              </div>

              {/* Informações do Roteiro */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="p-4 bg-gray-800/50 rounded-lg">
                  <h6 className="text-sm font-medium text-blue-400 mb-2">📝 Título:</h6>
                  <p className="text-white text-sm">{agentGeneratedScript.title}</p>
                </div>
                <div className="p-4 bg-gray-800/50 rounded-lg">
                  <h6 className="text-sm font-medium text-purple-400 mb-2">🎯 Premissa:</h6>
                  <p className="text-white text-sm max-h-20 overflow-y-auto">{agentGeneratedScript.premise}</p>
                </div>
              </div>

              {/* Roteiro Gerado */}
              <div className="p-4 bg-gray-800/50 rounded-lg">
                <h6 className="text-sm font-medium text-green-400 mb-3 flex items-center justify-between">
                  <span>🎬 Roteiro Completo:</span>
                  <div className="flex items-center space-x-2 text-xs text-gray-400">
                    <span>Provider: {agentGeneratedScript.provider}</span>
                    {agentGeneratedScript.generationMethod === 'multi_part' && (
                      <span>| Método: Geração em Partes</span>
                    )}
                    {agentGeneratedScript.parts && agentGeneratedScript.parts.length > 0 && (
                      <span>| Partes: {agentGeneratedScript.parts.length}</span>
                    )}
                    {agentGeneratedScript.numChapters > 0 && (
                      <span>| Capítulos: {agentGeneratedScript.numChapters}</span>
                    )}
                    {agentGeneratedScript.model !== 'auto' && (
                      <span>| Modelo: {agentGeneratedScript.model}</span>
                    )}
                    {agentGeneratedScript.wordCount > 0 && (
                      <span>| Palavras: {agentGeneratedScript.wordCount.toLocaleString()}</span>
                    )}
                    <span>| Caracteres: {agentGeneratedScript.characterCount?.toLocaleString() || agentGeneratedScript.content.length.toLocaleString()}</span>
                    {agentGeneratedScript.estimatedDuration > 0 && (
                      <span>| Duração: ~{agentGeneratedScript.estimatedDuration} min</span>
                    )}
                  </div>
                </h6>
                <div className="max-h-96 overflow-y-auto">
                  <p className="text-white text-sm whitespace-pre-wrap leading-relaxed">
                    {agentGeneratedScript.content}
                  </p>
                </div>
              </div>

              {/* Estatísticas */}
              <div className="mt-4 flex items-center justify-between text-xs text-gray-400">
                <span>Gerado em: {new Date(agentGeneratedScript.timestamp).toLocaleString()}</span>
                <span>Caracteres: {agentGeneratedScript.content.length.toLocaleString()}</span>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  )
}

export default AgentRoteirosSimples
