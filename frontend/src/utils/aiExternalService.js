/**
 * AI External Service
 * Serviço para conectar diretamente com OpenAI e Google Gemini APIs
 * Adaptado do projeto gerador-de-roteiros original
 */

class AIService {
  constructor({ provider = 'openai', apiKey }) {
    this.provider = provider
    this.apiKey = apiKey
    
    // URLs das APIs
    this.openaiBaseUrl = 'https://api.openai.com/v1'
    this.geminiBaseUrl = 'https://generativelanguage.googleapis.com/v1beta'
  }

  /**
   * Gerar texto usando o provedor selecionado
   */
  async generateText({ prompt, maxTokens = 2000, temperature = 0.8 }) {
    try {
      if (this.provider === 'openai') {
        return await this.generateWithOpenAI(prompt, maxTokens, temperature)
      } else if (this.provider === 'gemini') {
        return await this.generateWithGemini(prompt, maxTokens, temperature)
      } else {
        throw new Error(`Provedor não suportado: ${this.provider}`)
      }
    } catch (error) {
      console.error('Erro na geração de texto:', error)
      throw error
    }
  }

  /**
   * Gerar texto usando OpenAI
   */
  async generateWithOpenAI(prompt, maxTokens, temperature) {
    const response = await fetch(`${this.openaiBaseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [
          {
            role: 'system',
            content: 'Você é um roteirista profissional especializado em criar narrativas envolventes e bem estruturadas.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: maxTokens,
        temperature: temperature,
        top_p: 1,
        frequency_penalty: 0,
        presence_penalty: 0
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(`OpenAI API Error: ${response.status} - ${errorData.error?.message || 'Erro desconhecido'}`)
    }

    const data = await response.json()
    return data.choices[0]?.message?.content || ''
  }

  /**
   * Gerar texto usando Google Gemini
   */
  async generateWithGemini(prompt, maxTokens, temperature) {
    const response = await fetch(
      `${this.geminiBaseUrl}/models/gemini-1.5-flash:generateContent?key=${this.apiKey}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: `Você é um roteirista profissional especializado em criar narrativas envolventes e bem estruturadas.\n\n${prompt}`
            }]
          }],
          generationConfig: {
            temperature: temperature,
            topK: 1,
            topP: 1,
            maxOutputTokens: maxTokens,
            stopSequences: []
          },
          safetySettings: [
            {
              category: 'HARM_CATEGORY_HARASSMENT',
              threshold: 'BLOCK_MEDIUM_AND_ABOVE'
            },
            {
              category: 'HARM_CATEGORY_HATE_SPEECH',
              threshold: 'BLOCK_MEDIUM_AND_ABOVE'
            },
            {
              category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
              threshold: 'BLOCK_MEDIUM_AND_ABOVE'
            },
            {
              category: 'HARM_CATEGORY_DANGEROUS_CONTENT',
              threshold: 'BLOCK_MEDIUM_AND_ABOVE'
            }
          ]
        })
      }
    )

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(`Gemini API Error: ${response.status} - ${errorData.error?.message || 'Erro desconhecido'}`)
    }

    const data = await response.json()
    
    if (!data.candidates || data.candidates.length === 0) {
      throw new Error('Nenhuma resposta gerada pelo Gemini')
    }

    const candidate = data.candidates[0]
    
    if (candidate.finishReason === 'SAFETY') {
      throw new Error('Conteúdo bloqueado por políticas de segurança do Gemini')
    }

    return candidate.content?.parts?.[0]?.text || ''
  }

  /**
   * Estimar tokens de um texto (aproximação)
   */
  estimateTokens(text) {
    // Aproximação: 1 token ≈ 4 caracteres para inglês, 3 para português
    return Math.ceil(text.length / 3)
  }

  /**
   * Dividir prompt em chunks se necessário
   */
  splitPromptIntoChunks(prompt, maxTokensPerChunk = 1500) {
    const estimatedTokens = this.estimateTokens(prompt)
    
    if (estimatedTokens <= maxTokensPerChunk) {
      return [prompt]
    }

    const chunks = []
    const sentences = prompt.split(/[.!?]+/)
    let currentChunk = ''
    
    for (const sentence of sentences) {
      const testChunk = currentChunk + sentence + '.'
      
      if (this.estimateTokens(testChunk) > maxTokensPerChunk && currentChunk) {
        chunks.push(currentChunk.trim())
        currentChunk = sentence + '.'
      } else {
        currentChunk = testChunk
      }
    }
    
    if (currentChunk.trim()) {
      chunks.push(currentChunk.trim())
    }
    
    return chunks
  }

  /**
   * Validar chave da API
   */
  async validateApiKey() {
    try {
      await this.generateText({
        prompt: 'Teste',
        maxTokens: 10,
        temperature: 0.1
      })
      return true
    } catch (error) {
      return false
    }
  }
}

export default AIService