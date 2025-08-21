/**
 * 🎵 TTS Generator Component
 * 
 * Componente para geração de áudio Text-to-Speech
 */

import React, { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Volume2,
  Play,
  Pause,
  Download,
  Settings,
  Mic,
  Loader2,
  CheckCircle,
  AlertCircle,
  FileAudio,
  Clock,
  User,
  Zap
} from 'lucide-react'

const TTSGenerator = ({ scriptData, isVisible, onClose }) => {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedAudio, setGeneratedAudio] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentProvider, setCurrentProvider] = useState('elevenlabs')
  const [currentJobId, setCurrentJobId] = useState(null)
  const [canCancel, setCanCancel] = useState(false)
  const [voiceSettings, setVoiceSettings] = useState({
    elevenlabs: {
      voice_id: 'default',
      model_id: 'eleven_monolingual_v1',
      stability: 0.5,
      similarity_boost: 0.5,
      style: 0.0,
      use_speaker_boost: true
    },
    gemini: {
      voice_name: 'Aoede',
      model: 'gemini-2.0-flash-exp',
      speed: 1.0,
      pitch: 0.0,
      volume_gain_db: 0.0
    },
    kokoro: {
      voice: 'af_bella',
      kokoro_url: 'http://localhost:8880',
      speed: 1.0,
      language: 'en'
    }
  })
  const [segmentAudio, setSegmentAudio] = useState(true)
  const [maxCharsPerSegment, setMaxCharsPerSegment] = useState(4000)
  const [generatedSegments, setGeneratedSegments] = useState([])
  const [isJoiningAudio, setIsJoiningAudio] = useState(false)
  const [finalAudio, setFinalAudio] = useState(null)
  const [error, setError] = useState('')
  const audioRef = useRef(null)

  if (!isVisible || !scriptData) return null

  // Função para segmentar texto
  const segmentText = (text, maxChars = 4000) => {
    const segments = []
    const sentences = text.split(/[.!?]+/).filter(s => s.trim())

    let currentSegment = ''

    for (const sentence of sentences) {
      const trimmedSentence = sentence.trim()
      if (!trimmedSentence) continue

      const potentialSegment = currentSegment + (currentSegment ? '. ' : '') + trimmedSentence

      if (potentialSegment.length <= maxChars) {
        currentSegment = potentialSegment
      } else {
        if (currentSegment) {
          segments.push(currentSegment + '.')
          currentSegment = trimmedSentence
        } else {
          // Frase muito longa, dividir por palavras
          const words = trimmedSentence.split(' ')
          let wordSegment = ''

          for (const word of words) {
            const potentialWordSegment = wordSegment + (wordSegment ? ' ' : '') + word
            if (potentialWordSegment.length <= maxChars) {
              wordSegment = potentialWordSegment
            } else {
              if (wordSegment) {
                segments.push(wordSegment)
                wordSegment = word
              } else {
                segments.push(word)
              }
            }
          }

          if (wordSegment) {
            currentSegment = wordSegment
          }
        }
      }
    }

    if (currentSegment) {
      segments.push(currentSegment + '.')
    }

    return segments
  }

  const cancelCurrentJob = async () => {
    if (!currentJobId) return

    try {
      console.log(`🛑 Cancelando job ${currentJobId}...`)

      const response = await fetch(`/api/automations/tts/jobs/${currentJobId}/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      const result = await response.json()

      if (result.success) {
        console.log(`✅ Job ${currentJobId} cancelado com sucesso`)
        setIsGenerating(false)
        setCanCancel(false)
        setCurrentJobId(null)
        setError('Geração cancelada pelo usuário')
      } else {
        console.error('❌ Erro ao cancelar job:', result.error)
      }
    } catch (err) {
      console.error('❌ Erro ao cancelar job:', err)
    }
  }

  const generateAudio = async () => {
    setIsGenerating(true)
    setError('')
    setGeneratedSegments([])
    setGeneratedAudio(null)
    setFinalAudio(null)
    setCurrentJobId(null)
    setCanCancel(false)

    try {
      // Obter chaves de API
      const apiKeys = JSON.parse(localStorage.getItem('api_keys') || '{}')

      // Preparar texto do roteiro
      let fullText = ''
      if (scriptData.scripts?.chapters) {
        fullText = scriptData.scripts.chapters
          .map(chapter => chapter.content || '')
          .join('\n\n')
      } else if (typeof scriptData === 'string') {
        fullText = scriptData
      }

      if (!fullText.trim()) {
        throw new Error('Nenhum texto encontrado para gerar áudio')
      }

      // Segmentar texto se necessário
      const textSegments = segmentAudio ? segmentText(fullText, maxCharsPerSegment) : [fullText]

      console.log(`🎵 Gerando ${textSegments.length} segmentos de áudio...`)

      // Determinar configurações baseado no provider
      let endpoint, apiKey, baseRequestData

      if (currentProvider === 'elevenlabs') {
        if (!apiKeys.elevenlabs) {
          throw new Error('Chave da API ElevenLabs não configurada')
        }

        endpoint = '/api/automations/generate-tts-elevenlabs'
        apiKey = apiKeys.elevenlabs
        baseRequestData = {
          api_key: apiKey,
          voice_id: voiceSettings.elevenlabs.voice_id,
          model_id: voiceSettings.elevenlabs.model_id,
          stability: voiceSettings.elevenlabs.stability,
          similarity_boost: voiceSettings.elevenlabs.similarity_boost,
          style: voiceSettings.elevenlabs.style,
          use_speaker_boost: voiceSettings.elevenlabs.use_speaker_boost
        }
      } else if (currentProvider === 'gemini') {
        console.log('🔄 Usando rotação automática de chaves Gemini')

        endpoint = '/api/automations/generate-tts'
        baseRequestData = {
          // NÃO enviar api_key - deixar o backend usar rotação automática
          voice_name: voiceSettings.gemini.voice_name,
          model: voiceSettings.gemini.model,
          speed: voiceSettings.gemini.speed,
          pitch: voiceSettings.gemini.pitch,
          volume_gain_db: voiceSettings.gemini.volume_gain_db
        }
      } else if (currentProvider === 'kokoro') {
        console.log('🔄 Usando Kokoro TTS local')

        endpoint = '/api/automations/generate-tts-kokoro'
        baseRequestData = {
          voice: voiceSettings.kokoro.voice,
          kokoro_url: voiceSettings.kokoro.kokoro_url,
          speed: voiceSettings.kokoro.speed,
          language: voiceSettings.kokoro.language
        }
      }

      // Gerar áudio para cada segmento
      const segments = []
      for (let i = 0; i < textSegments.length; i++) {
        const segment = textSegments[i]

        console.log(`🎵 Gerando segmento ${i + 1}/${textSegments.length}...`)

        const requestData = {
          ...baseRequestData,
          text: segment
        }

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })

        const result = await response.json()

        // Capturar job_id se disponível (para Gemini e Kokoro)
        if (result.job_id && (currentProvider === 'gemini' || currentProvider === 'kokoro') && i === 0) {
          setCurrentJobId(result.job_id)
          setCanCancel(true)
          console.log(`🎵 Job ID capturado: ${result.job_id}`)
        }

        if (!result.success) {
          throw new Error(`Erro no segmento ${i + 1}: ${result.error}`)
        }

        segments.push({
          index: i + 1,
          text: segment,
          audio: result.data,
          duration: result.data.duration || 0
        })

        // Pequena pausa entre requisições para não sobrecarregar a API
        if (i < textSegments.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
      }

      setGeneratedSegments(segments)

      // Se for apenas um segmento, definir como áudio principal
      if (segments.length === 1) {
        setGeneratedAudio(segments[0].audio)
      }

      // Salvar dados de áudio no localStorage para uso na criação de vídeo
      const audioData = segments.map(segment => ({
        filename: segment.audio.filename,
        audio_url: segment.audio.audio_url,
        duration: segment.duration,
        size: segment.audio.size,
        voice_used: segment.audio.voice_used,
        provider: currentProvider,
        text_segment: segment.text ? segment.text.substring(0, 100) + (segment.text.length > 100 ? '...' : '') : ''
      }))
      
      localStorage.setItem('generated_audio_files', JSON.stringify(audioData))
      console.log('💾 Dados de áudio salvos no localStorage:', audioData)

      console.log(`✅ ${segments.length} segmentos de áudio gerados com sucesso!`)

    } catch (err) {
      console.error('❌ Erro na geração de áudio:', err)
      setError(err.message)
    } finally {
      setIsGenerating(false)
    }
  }

  const playAudio = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const joinAudioSegments = async () => {
    if (generatedSegments.length === 0) return

    setIsJoiningAudio(true)
    setError('')

    try {
      console.log('🔗 Juntando segmentos de áudio...')

      const response = await fetch('/api/automations/join-audio', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          segments: generatedSegments.map(seg => ({
            filename: seg.audio.filename,
            index: seg.index
          }))
        })
      })

      const result = await response.json()

      if (!result.success) {
        throw new Error(result.error || 'Erro ao juntar áudios')
      }

      setFinalAudio(result.data)
      
      // Salvar áudio final no localStorage
      const finalAudioData = [{
        filename: result.data.filename,
        audio_url: `/api/audio/${result.data.filename}`,
        duration: result.data.duration,
        size: result.data.size,
        voice_used: generatedSegments[0]?.audio.voice_used || 'unknown',
        provider: currentProvider,
        text_segment: 'Áudio final unificado',
        is_final: true,
        segments_count: result.data.segments_count
      }]
      
      localStorage.setItem('generated_audio_files', JSON.stringify(finalAudioData))
      console.log('💾 Áudio final salvo no localStorage:', finalAudioData)
      
      console.log('✅ Áudios unidos com sucesso:', result.data)

    } catch (err) {
      console.error('❌ Erro ao juntar áudios:', err)
      setError(err.message)
    } finally {
      setIsJoiningAudio(false)
    }
  }

  const downloadAudio = (audioData = null) => {
    const audio = audioData || generatedAudio || finalAudio
    if (audio?.filename) {
      // Criar link de download
      const link = document.createElement('a')
      link.href = `/api/download/${audio.filename}`
      link.download = audio.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const downloadSegment = (segment) => {
    downloadAudio(segment.audio)
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Volume2 className="w-6 h-6" />
                <div>
                  <h2 className="text-xl font-bold">Geração de Áudio TTS</h2>
                  <p className="text-purple-100 text-sm">
                    Transforme seu roteiro em áudio profissional
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-white/80 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* Provider Selection */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Provedor de TTS
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <button
                  onClick={() => setCurrentProvider('elevenlabs')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    currentProvider === 'elevenlabs'
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Mic className="w-5 h-5 text-purple-600" />
                    <div className="text-left">
                      <div className="font-semibold">ElevenLabs</div>
                      <div className="text-sm text-gray-600">Melhor qualidade</div>
                    </div>
                  </div>
                </button>

                <button
                  onClick={() => setCurrentProvider('gemini')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    currentProvider === 'gemini'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <User className="w-5 h-5 text-blue-600" />
                    <div className="text-left">
                      <div className="font-semibold">Gemini TTS</div>
                      <div className="text-sm text-gray-600">Gratuito</div>
                    </div>
                  </div>
                </button>

                <button
                  onClick={() => setCurrentProvider('kokoro')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    currentProvider === 'kokoro'
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Zap className="w-5 h-5 text-green-600" />
                    <div className="text-left">
                      <div className="font-semibold">Kokoro TTS</div>
                      <div className="text-sm text-gray-600">Local</div>
                    </div>
                  </div>
                </button>
              </div>
            </div>

            {/* Configurações de Segmentação */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold">⚙️ Configurações de Geração</h3>

              <div className="flex items-center space-x-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <input
                  type="checkbox"
                  id="segmentAudio"
                  checked={segmentAudio}
                  onChange={(e) => setSegmentAudio(e.target.checked)}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="segmentAudio" className="text-sm font-medium text-gray-700">
                  Segmentar áudio (recomendado para textos longos)
                </label>
              </div>

              {segmentAudio && (
                <div>
                  <label className="block text-sm font-medium mb-2">Máximo de caracteres por segmento</label>
                  <select
                    value={maxCharsPerSegment}
                    onChange={(e) => setMaxCharsPerSegment(parseInt(e.target.value))}
                    className="w-full p-2 border border-gray-300 rounded-lg"
                  >
                    <option value={2000}>2.000 caracteres (mais seguro)</option>
                    <option value={3000}>3.000 caracteres (balanceado)</option>
                    <option value={4000}>4.000 caracteres (máximo recomendado)</option>
                    <option value={5000}>5.000 caracteres (pode dar erro)</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Textos muito longos podem causar erro nas APIs. Segmentar é mais seguro.
                  </p>
                </div>
              )}
            </div>

            {/* Voice Settings */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold">🎤 Configurações de Voz</h3>

              {currentProvider === 'elevenlabs' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Voice ID</label>
                      <select
                        value={voiceSettings.elevenlabs.voice_id}
                        onChange={(e) => setVoiceSettings(prev => ({
                          ...prev,
                          elevenlabs: { ...prev.elevenlabs, voice_id: e.target.value }
                        }))}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                      >
                        <option value="default">Rachel (Padrão)</option>
                        <option value="21m00Tcm4TlvDq8ikWAM">Rachel - Feminina Americana</option>
                        <option value="AZnzlk1XvdvUeBnXmlld">Domi - Feminina Jovem</option>
                        <option value="EXAVITQu4vr4xnSDxMaL">Bella - Feminina Suave</option>
                        <option value="ErXwobaYiN019PkySvjV">Antoni - Masculina Americana</option>
                        <option value="VR6AewLTigWG4xSOukaG">Arnold - Masculina Grave</option>
                        <option value="pNInz6obpgDQGcFmaJgB">Adam - Masculina Profunda</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Modelo</label>
                      <select
                        value={voiceSettings.elevenlabs.model_id}
                        onChange={(e) => setVoiceSettings(prev => ({
                          ...prev,
                          elevenlabs: { ...prev.elevenlabs, model_id: e.target.value }
                        }))}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                      >
                        <option value="eleven_monolingual_v1">Monolingual V1 (Inglês)</option>
                        <option value="eleven_multilingual_v2">Multilingual V2 (Português)</option>
                        <option value="eleven_turbo_v2">Turbo V2 (Rápido)</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Estabilidade: {voiceSettings.elevenlabs.stability}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={voiceSettings.elevenlabs.stability}
                        onChange={(e) => setVoiceSettings(prev => ({
                          ...prev,
                          elevenlabs: { ...prev.elevenlabs, stability: parseFloat(e.target.value) }
                        }))}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Similaridade: {voiceSettings.elevenlabs.similarity_boost}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={voiceSettings.elevenlabs.similarity_boost}
                        onChange={(e) => setVoiceSettings(prev => ({
                          ...prev,
                          elevenlabs: { ...prev.elevenlabs, similarity_boost: parseFloat(e.target.value) }
                        }))}
                        className="w-full"
                      />
                    </div>
                  </div>
                </div>
              )}

              {currentProvider === 'gemini' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Voz</label>
                      <select
                        value={voiceSettings.gemini.voice_name}
                        onChange={(e) => setVoiceSettings(prev => ({
                          ...prev,
                          gemini: { ...prev.gemini, voice_name: e.target.value }
                        }))}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                      >
                        <option value="Aoede">Aoede - Feminina Suave</option>
                        <option value="Charon">Charon - Masculina Grave</option>
                        <option value="Fenrir">Fenrir - Masculina Forte</option>
                        <option value="Kore">Kore - Feminina Jovem</option>
                        <option value="Puck">Puck - Masculina Alegre</option>
                        <option value="Sage">Sage - Feminina Sábia</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Modelo</label>
                      <select
                        value={voiceSettings.gemini.model}
                        onChange={(e) => setVoiceSettings(prev => ({
                          ...prev,
                          gemini: { ...prev.gemini, model: e.target.value }
                        }))}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                      >
                        <option value="gemini-2.0-flash-exp">Gemini 2.0 Flash (Experimental)</option>
                        <option value="gemini-2.5-flash-preview-tts">Gemini 2.5 Flash TTS</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Velocidade: {voiceSettings.gemini.speed}x
                      </label>
                      <input
                        type="range"
                        min="0.5"
                        max="2.0"
                        step="0.1"
                        value={voiceSettings.gemini.speed}
                        onChange={(e) => setVoiceSettings(prev => ({
                          ...prev,
                          gemini: { ...prev.gemini, speed: parseFloat(e.target.value) }
                        }))}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Tom: {voiceSettings.gemini.pitch > 0 ? '+' : ''}{voiceSettings.gemini.pitch}
                      </label>
                      <input
                        type="range"
                        min="-20"
                        max="20"
                        step="1"
                        value={voiceSettings.gemini.pitch}
                        onChange={(e) => setVoiceSettings(prev => ({
                          ...prev,
                          gemini: { ...prev.gemini, pitch: parseFloat(e.target.value) }
                        }))}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Volume: {voiceSettings.gemini.volume_gain_db > 0 ? '+' : ''}{voiceSettings.gemini.volume_gain_db}dB
                      </label>
                      <input
                        type="range"
                        min="-96"
                        max="16"
                        step="1"
                        value={voiceSettings.gemini.volume_gain_db}
                        onChange={(e) => setVoiceSettings(prev => ({
                          ...prev,
                          gemini: { ...prev.gemini, volume_gain_db: parseFloat(e.target.value) }
                        }))}
                        className="w-full"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Kokoro TTS Settings */}
              {currentProvider === 'kokoro' && (
                <div className="space-y-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <h4 className="font-semibold text-green-800 flex items-center gap-2">
                    <Zap className="w-4 h-4" />
                    Configurações Kokoro TTS
                  </h4>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Idioma</label>
                      <select
                        value={voiceSettings.kokoro.language}
                        onChange={(e) => {
                          const newLanguage = e.target.value
                          let defaultVoice = 'af_bella'
                          if (newLanguage === 'pt') defaultVoice = 'pf_dora'
                          else if (newLanguage === 'zh') defaultVoice = 'zf_xiaobei'
                          else if (newLanguage === 'ja') defaultVoice = 'jf_alpha'

                          setVoiceSettings(prev => ({
                            ...prev,
                            kokoro: {
                              ...prev.kokoro,
                              language: newLanguage,
                              voice: defaultVoice
                            }
                          }))
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                      >
                        <option value="en">🇺🇸 Inglês</option>
                        <option value="pt">🇵🇹 Português</option>
                        <option value="zh">🇨🇳 Chinês</option>
                        <option value="ja">🇯🇵 Japonês</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Voz</label>
                      <select
                        value={voiceSettings.kokoro.voice}
                        onChange={(e) => setVoiceSettings(prev => ({
                          ...prev,
                          kokoro: { ...prev.kokoro, voice: e.target.value }
                        }))}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                      >
                        {voiceSettings.kokoro.language === 'pt' ? (
                          <>
                            <option value="pf_dora">🇵🇹 pf_dora - Feminina</option>
                            <option value="pm_alex">🇵🇹 pm_alex - Masculina</option>
                            <option value="pm_santa">🇵🇹 pm_santa - Masculina (Santa)</option>
                          </>
                        ) : voiceSettings.kokoro.language === 'zh' ? (
                          <>
                            <option value="zf_xiaobei">🇨🇳 zf_xiaobei - Feminina</option>
                            <option value="zf_xiaoni">🇨🇳 zf_xiaoni - Feminina</option>
                            <option value="zm_yunjian">🇨🇳 zm_yunjian - Masculina</option>
                          </>
                        ) : voiceSettings.kokoro.language === 'ja' ? (
                          <>
                            <option value="jf_alpha">🇯🇵 jf_alpha - Feminina</option>
                            <option value="jf_gongitsune">🇯🇵 jf_gongitsune - Feminina</option>
                            <option value="jm_kumo">🇯🇵 jm_kumo - Masculina</option>
                          </>
                        ) : (
                          <>
                            <option value="af_bella">af_bella - Feminina Americana</option>
                            <option value="af_sarah">af_sarah - Feminina Americana</option>
                            <option value="am_adam">am_adam - Masculina Americana</option>
                            <option value="am_michael">am_michael - Masculina Americana</option>
                            <option value="bf_emma">bf_emma - Feminina Britânica</option>
                            <option value="bm_george">bm_george - Masculina Britânica</option>
                          </>
                        )}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Velocidade: {voiceSettings.kokoro.speed}x
                    </label>
                    <input
                      type="range"
                      min="0.5"
                      max="2.0"
                      step="0.1"
                      value={voiceSettings.kokoro.speed}
                      onChange={(e) => setVoiceSettings(prev => ({
                        ...prev,
                        kokoro: { ...prev.kokoro, speed: parseFloat(e.target.value) }
                      }))}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">URL do Kokoro TTS</label>
                    <input
                      type="text"
                      value={voiceSettings.kokoro.kokoro_url}
                      onChange={(e) => setVoiceSettings(prev => ({
                        ...prev,
                        kokoro: { ...prev.kokoro, kokoro_url: e.target.value }
                      }))}
                      className="w-full p-2 border border-gray-300 rounded-lg"
                      placeholder="http://localhost:8880"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Generate Button */}
            <div className="flex justify-center gap-4">
              <button
                onClick={generateAudio}
                disabled={isGenerating}
                className="flex items-center gap-3 px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Gerando Áudio...
                  </>
                ) : (
                  <>
                    <Volume2 className="w-5 h-5" />
                    Gerar Áudio TTS
                  </>
                )}
              </button>

              {/* Cancel Button */}
              {isGenerating && canCancel && (
                <button
                  onClick={cancelCurrentJob}
                  className="flex items-center gap-2 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all"
                >
                  <AlertCircle className="w-5 h-5" />
                  Cancelar
                </button>
              )}
            </div>

            {/* Error Display */}
            {error && (
              <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                <AlertCircle className="w-5 h-5" />
                <span>{error}</span>
              </div>
            )}

            {/* Generated Audio Segments */}
            {generatedSegments.length > 0 && (
              <div className="space-y-4">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3 text-green-700">
                      <CheckCircle className="w-5 h-5" />
                      <span className="font-semibold">
                        {generatedSegments.length} segmentos gerados com sucesso!
                      </span>
                    </div>

                    {generatedSegments.length > 1 && (
                      <button
                        onClick={joinAudioSegments}
                        disabled={isJoiningAudio}
                        className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
                      >
                        {isJoiningAudio ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Juntando...
                          </>
                        ) : (
                          <>
                            <Download className="w-4 h-4" />
                            Juntar Áudios
                          </>
                        )}
                      </button>
                    )}
                  </div>

                  {/* Estatísticas Gerais */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                    <div className="flex items-center gap-2">
                      <FileAudio className="w-4 h-4" />
                      <span>
                        {formatFileSize(generatedSegments.reduce((total, seg) => total + (seg.audio.size || 0), 0))}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      <span>
                        {formatDuration(generatedSegments.reduce((total, seg) => total + (seg.duration || 0), 0))}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      <span>{generatedSegments[0]?.audio.voice_used}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Mic className="w-4 h-4" />
                      <span>{currentProvider}</span>
                    </div>
                  </div>

                  {/* Lista de Segmentos */}
                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {generatedSegments.map((segment, index) => (
                      <div key={index} className="bg-white p-3 rounded-lg border border-gray-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-sm">
                            Segmento {segment.index}
                          </span>
                          <div className="flex gap-2">
                            <button
                              onClick={() => {
                                const audio = new Audio(`/api/audio/${segment.audio.filename}`)
                                audio.play()
                              }}
                              className="p-1 text-green-600 hover:bg-green-100 rounded"
                              title="Reproduzir segmento"
                            >
                              <Play className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => downloadSegment(segment)}
                              className="p-1 text-blue-600 hover:bg-blue-100 rounded"
                              title="Download segmento"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <div className="text-xs text-gray-600 mb-2">
                          {formatFileSize(segment.audio.size)} • {formatDuration(segment.duration)}
                        </div>
                        <div className="text-xs text-gray-500 line-clamp-2">
                          {segment.text ? segment.text.substring(0, 100) + '...' : ''}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Final Joined Audio */}
            {finalAudio && (
              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <div className="flex items-center gap-3 text-purple-700 mb-4">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-semibold">Áudio final unificado!</span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                  <div className="flex items-center gap-2">
                    <FileAudio className="w-4 h-4" />
                    <span>{formatFileSize(finalAudio.size)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>{formatDuration(finalAudio.duration)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    <span>{finalAudio.segments_count} segmentos</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Mic className="w-4 h-4" />
                    <span>{currentProvider}</span>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      const audio = new Audio(`/api/audio/${finalAudio.filename}`)
                      audio.play()
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    <Play className="w-4 h-4" />
                    Reproduzir Final
                  </button>

                  <button
                    onClick={() => downloadAudio(finalAudio)}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Download Final
                  </button>
                </div>
              </div>
            )}

            {/* Single Audio (fallback) */}
            {generatedAudio && generatedSegments.length === 0 && (
              <div className="space-y-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-3 text-green-700">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-semibold">Áudio gerado com sucesso!</span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <FileAudio className="w-4 h-4" />
                    <span>{formatFileSize(generatedAudio.size)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>{generatedAudio.duration ? formatDuration(generatedAudio.duration) : 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    <span>{generatedAudio.voice_used}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Mic className="w-4 h-4" />
                    <span>{currentProvider}</span>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={playAudio}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    {isPlaying ? 'Pausar' : 'Reproduzir'}
                  </button>

                  <button
                    onClick={() => downloadAudio()}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                </div>

                {/* Hidden Audio Element */}
                <audio
                  ref={audioRef}
                  src={generatedAudio.audio_file ? `/api/audio/${generatedAudio.filename}` : ''}
                  onEnded={() => setIsPlaying(false)}
                  onPause={() => setIsPlaying(false)}
                  onPlay={() => setIsPlaying(true)}
                />
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default TTSGenerator
