import React, { useState } from 'react'
import { Youtube, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react'

const YouTubeExtractTest = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [testUrl, setTestUrl] = useState('MrBeast')
  const [response, setResponse] = useState(null)
  const [error, setError] = useState(null)

  const testExtraction = async () => {
    setIsLoading(true)
    setResponse(null)
    setError(null)

    try {
      console.log('🔍 Iniciando teste de extração...')
      console.log('📝 URL/Canal:', testUrl)

      // Teste 1: Verificar se o backend está rodando
      console.log('🔗 Testando conexão com backend...')
      const healthResponse = await fetch('http://localhost:5000/api/health')
      if (!healthResponse.ok) {
        throw new Error('Backend não está respondendo')
      }
      console.log('✅ Backend conectado')

      // Teste 2: Fazer a requisição de extração
      console.log('📺 Fazendo requisição de extração...')
      const payload = {
        url: testUrl,
        config: {
          max_titles: 5,
          min_views: 1000,
          max_views: 0,
          days: 30
        }
      }

      console.log('📤 Payload enviado:', JSON.stringify(payload, null, 2))

      const extractResponse = await fetch('http://localhost:5000/api/automations/extract-youtube', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      })

      console.log('📥 Status da resposta:', extractResponse.status)
      console.log('📥 Headers da resposta:', Object.fromEntries(extractResponse.headers.entries()))

      const responseText = await extractResponse.text()
      console.log('📥 Resposta bruta:', responseText)

      let data
      try {
        data = JSON.parse(responseText)
      } catch (parseError) {
        throw new Error(`Erro ao parsear JSON: ${parseError.message}. Resposta: ${responseText}`)
      }

      console.log('📥 Dados parseados:', data)

      setResponse({
        status: extractResponse.status,
        headers: Object.fromEntries(extractResponse.headers.entries()),
        data: data,
        success: data.success || false
      })

      if (!data.success) {
        setError(data.error || 'Erro desconhecido')
      }

    } catch (err) {
      console.error('❌ Erro no teste:', err)
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h1 className="text-2xl font-bold text-white mb-6 flex items-center space-x-2">
            <Youtube className="text-red-500" />
            <span>Teste de Extração YouTube - Debug</span>
          </h1>

          {/* Formulário de Teste */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Canal/URL para testar:
            </label>
            <div className="flex space-x-3">
              <input
                type="text"
                value={testUrl}
                onChange={(e) => setTestUrl(e.target.value)}
                placeholder="MrBeast, @MrBeast, ou UCX6OQ3DkcsbYNE6H8uQQuVA"
                className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={testExtraction}
                disabled={isLoading}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg flex items-center space-x-2 transition-colors"
              >
                {isLoading ? (
                  <>
                    <RefreshCw size={18} className="animate-spin" />
                    <span>Testando...</span>
                  </>
                ) : (
                  <>
                    <Youtube size={18} />
                    <span>Testar Extração</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Resultado do Teste */}
          {error && (
            <div className="mb-6 p-4 bg-red-900/30 border border-red-700 rounded-lg">
              <div className="flex items-center space-x-2 text-red-400 mb-2">
                <AlertCircle size={18} />
                <span className="font-semibold">Erro Detectado:</span>
              </div>
              <pre className="text-red-300 text-sm whitespace-pre-wrap">{error}</pre>
            </div>
          )}

          {response && (
            <div className="space-y-4">
              {/* Status da Resposta */}
              <div className={`p-4 rounded-lg border ${
                response.success 
                  ? 'bg-green-900/30 border-green-700' 
                  : 'bg-red-900/30 border-red-700'
              }`}>
                <div className="flex items-center space-x-2 mb-2">
                  {response.success ? (
                    <CheckCircle size={18} className="text-green-400" />
                  ) : (
                    <AlertCircle size={18} className="text-red-400" />
                  )}
                  <span className={`font-semibold ${
                    response.success ? 'text-green-400' : 'text-red-400'
                  }`}>
                    Status HTTP: {response.status} - {response.success ? 'Sucesso' : 'Falha'}
                  </span>
                </div>
              </div>

              {/* Headers da Resposta */}
              <div className="bg-gray-700 rounded-lg p-4">
                <h3 className="text-white font-semibold mb-2">Headers da Resposta:</h3>
                <pre className="text-gray-300 text-sm overflow-x-auto">
                  {JSON.stringify(response.headers, null, 2)}
                </pre>
              </div>

              {/* Dados da Resposta */}
              <div className="bg-gray-700 rounded-lg p-4">
                <h3 className="text-white font-semibold mb-2">Dados da Resposta:</h3>
                <pre className="text-gray-300 text-sm overflow-x-auto max-h-96 overflow-y-auto">
                  {JSON.stringify(response.data, null, 2)}
                </pre>
              </div>

              {/* Vídeos Extraídos (se houver) */}
              {response.data?.data?.videos && response.data.data.videos.length > 0 && (
                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-white font-semibold mb-3">
                    Vídeos Extraídos ({response.data.data.videos.length}):
                  </h3>
                  <div className="space-y-2">
                    {response.data.data.videos.slice(0, 5).map((video, index) => (
                      <div key={index} className="bg-gray-600 rounded p-3">
                        <p className="text-white font-medium mb-1">
                          {index + 1}. {video.title}
                        </p>
                        <div className="text-sm text-gray-300">
                          <span>Views: {video.views?.toLocaleString() || 'N/A'}</span>
                          {video.published_at && (
                            <span className="ml-4">Data: {video.published_at}</span>
                          )}
                        </div>
                      </div>
                    ))}
                    {response.data.data.videos.length > 5 && (
                      <p className="text-gray-400 text-sm">
                        ... e mais {response.data.data.videos.length - 5} vídeos
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Instruções */}
          <div className="mt-8 p-4 bg-blue-900/30 border border-blue-700 rounded-lg">
            <h3 className="text-blue-400 font-semibold mb-2">Como usar este teste:</h3>
            <ul className="text-blue-300 text-sm space-y-1">
              <li>• Digite um nome de canal (ex: MrBeast)</li>
              <li>• Ou um handle (ex: @MrBeast)</li>
              <li>• Ou um ID de canal (ex: UCX6OQ3DkcsbYNE6H8uQQuVA)</li>
              <li>• Clique em "Testar Extração" e veja os logs detalhados</li>
              <li>• Verifique o console do navegador para logs adicionais</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default YouTubeExtractTest