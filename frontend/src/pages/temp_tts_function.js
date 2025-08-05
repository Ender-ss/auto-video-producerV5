const renderTTSGeneration = () => (
  <div className="space-y-6">
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
        <Mic size={24} className="text-yellow-400" />
        <span>Teste de Provedores TTS</span>
      </h3>

      {/* Seletor de Provedor */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Provedor TTS
        </label>
        <select
          value={ttsProvider}
          onChange={(e) => setTtsProvider(e.target.value)}
          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="elevenlabs">ElevenLabs</option>
          <option value="gemini">Google Gemini</option>
          <option value="kokoro">Kokoro TTS</option>
        </select>
      </div>

      {/* Área de Teste */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Texto para Teste
        </label>
        <textarea
          value={ttsTestText}
          onChange={(e) => setTtsTestText(e.target.value)}
          placeholder="Digite um texto para testar a geração de áudio..."
          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={4}
        />
      </div>

      {/* Status das APIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-700 p-4 rounded-lg">
          <h4 className="text-white font-medium mb-2">ElevenLabs</h4>
          <div className="flex items-center space-x-2">
            {apiKeys.elevenlabs ? (
              <CheckCircle size={16} className="text-green-400" />
            ) : (
              <XCircle size={16} className="text-red-400" />
            )}
            <span className={`text-sm ${
              apiKeys.elevenlabs ? 'text-green-400' : 'text-red-400'
            }`}>
              {apiKeys.elevenlabs ? 'Configurado' : 'Não configurado'}
            </span>
          </div>
        </div>
        
        <div className="bg-gray-700 p-4 rounded-lg">
          <h4 className="text-white font-medium mb-2">Gemini</h4>
          <div className="flex items-center space-x-2">
            {apiKeys.gemini ? (
              <CheckCircle size={16} className="text-green-400" />
            ) : (
              <XCircle size={16} className="text-red-400" />
            )}
            <span className={`text-sm ${
              apiKeys.gemini ? 'text-green-400' : 'text-red-400'
            }`}>
              {apiKeys.gemini ? 'Configurado' : 'Não configurado'}
            </span>
          </div>
        </div>
        
        <div className="bg-gray-700 p-4 rounded-lg">
          <h4 className="text-white font-medium mb-2">Kokoro</h4>
          <div className="flex items-center space-x-2">
            {kokoroUrl ? (
              <CheckCircle size={16} className="text-green-400" />
            ) : (
              <XCircle size={16} className="text-red-400" />
            )}
            <span className={`text-sm ${
              kokoroUrl ? 'text-green-400' : 'text-red-400'
            }`}>
              {kokoroUrl ? 'Configurado' : 'Não configurado'}
            </span>
          </div>
        </div>
      </div>

      {/* Botões de Teste */}
      <div className="flex space-x-4 mb-6">
        <button
          onClick={() => {
            if (ttsProvider === 'elevenlabs') {
              handleTestElevenLabsTTS();
            } else if (ttsProvider === 'gemini') {
              handleTestGeminiTTS();
            } else if (ttsProvider === 'kokoro') {
              handleTestKokoroTTS();
            }
          }}
          disabled={isGeneratingTTS || !ttsTestText.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isGeneratingTTS ? 'Testando...' : 'Testar TTS'}
        </button>
        
        <button
          onClick={() => window.open('/settings', '_blank')}
          className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center space-x-2"
        >
          <Settings size={16} />
          <span>Configurar APIs</span>
        </button>
        
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
        >
          <RefreshCw size={16} />
          <span>Sincronizar Chaves</span>
        </button>
      </div>

      {/* Resultado do Teste */}
      {ttsTestResult && (
        <div className="bg-gray-700 p-4 rounded-lg">
          <h4 className="text-white font-medium mb-2">Resultado do Teste</h4>
          {ttsTestResult.success ? (
            <div className="space-y-3">
              <div className="flex items-center space-x-2 text-green-400">
                <CheckCircle size={16} />
                <span>Áudio gerado com sucesso!</span>
              </div>
              {ttsTestResult.audioUrl && (
                <div className="space-y-2">
                  <audio controls className="w-full">
                    <source src={ttsTestResult.audioUrl} type="audio/mpeg" />
                    Seu navegador não suporta o elemento de áudio.
                  </audio>
                  <a
                    href={ttsTestResult.audioUrl}
                    download="teste_tts.mp3"
                    className="inline-flex items-center space-x-2 px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
                  >
                    <Download size={14} />
                    <span>Download</span>
                  </a>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-red-400">
              <XCircle size={16} />
              <span>{ttsTestResult.error || 'Erro ao gerar áudio'}</span>
            </div>
          )}
        </div>
      )}

      {/* Instruções */}
      <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-4">
        <h4 className="text-blue-200 font-medium mb-2">📋 Como usar:</h4>
        <ul className="text-gray-300 text-sm space-y-1">
          <li>1. Configure suas chaves de API nas configurações</li>
          <li>2. Selecione o provedor TTS desejado</li>
          <li>3. Digite um texto para teste</li>
          <li>4. Clique em "Testar" para gerar o áudio</li>
          <li>5. Ouça o resultado e faça download se necessário</li>
        </ul>
      </div>
    </div>
  </div>
);