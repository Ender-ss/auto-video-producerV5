/**
 * 📊 Automation Results Component
 * 
 * Componente para exibir os resultados da automação completa
 */

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText,
  Lightbulb,
  BookOpen,
  ChevronDown,
  ChevronRight,
  Copy,
  Check,
  Star,
  TrendingUp,
  Clock,
  Eye,
  Download,
  Package
} from 'lucide-react'

const AutomationResults = ({ results, isVisible, onClose }) => {
  const [expandedSections, setExpandedSections] = useState({
    titles: true,
    premises: false,
    scripts: false
  })
  const [copiedItems, setCopiedItems] = useState({})

  if (!results || !isVisible) return null

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const copyToClipboard = async (text, itemId) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedItems(prev => ({ ...prev, [itemId]: true }))
      setTimeout(() => {
        setCopiedItems(prev => ({ ...prev, [itemId]: false }))
      }, 2000)
    } catch (err) {
      console.error('Erro ao copiar:', err)
    }
  }

  const exportFinalDocuments = () => {
    if (!results) return

    // Pegar o melhor título (primeiro da lista)
    const bestTitle = results.titles?.data?.generated_titles?.[0]?.title ||
                     results.titles?.data?.generated_titles?.[0] ||
                     'Título não disponível'

    // Pegar a primeira premissa
    const bestPremise = results.premises?.premises?.[0] || null

    // Pegar o roteiro completo
    const script = results.scripts?.scripts || null

    // Criar documento final
    let finalDocument = `# 📄 DOCUMENTOS FINAIS DA AUTOMAÇÃO\n\n`

    finalDocument += `## 🎯 TÍTULO SELECIONADO\n`
    finalDocument += `${bestTitle}\n\n`

    if (bestPremise) {
      finalDocument += `## 💡 PREMISSA\n`
      finalDocument += `**Título:** ${bestPremise.title}\n\n`
      finalDocument += `**Premissa:**\n${bestPremise.premise}\n\n`
    }

    if (script && script.chapters) {
      finalDocument += `## 📝 ROTEIRO COMPLETO\n\n`
      if (script.title) {
        finalDocument += `**Título do Roteiro:** ${script.title}\n\n`
      }

      script.chapters.forEach((chapter, index) => {
        finalDocument += `### Capítulo ${index + 1}: ${chapter.title}\n`
        if (chapter.duration) {
          finalDocument += `**Duração:** ${chapter.duration}\n\n`
        }
        finalDocument += `${chapter.content}\n\n---\n\n`
      })
    }

    // Copiar para clipboard
    copyToClipboard(finalDocument, 'final-documents')

    // Também fazer download
    downloadDocument(finalDocument, 'documentos-finais.md')
  }

  const downloadDocument = (content, filename) => {
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const formatScore = (score) => {
    if (typeof score === 'number') {
      return (score * 100).toFixed(1) + '%'
    }
    return 'N/A'
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
          className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold flex items-center gap-2">
                  <TrendingUp className="w-6 h-6" />
                  Resultados da Automação
                </h2>
                <p className="text-purple-100 mt-1">
                  Títulos, premissas e roteiros gerados com IA
                </p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={exportFinalDocuments}
                  className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                  title="Exportar documentos finais"
                >
                  {copiedItems['final-documents'] ? (
                    <>
                      <Check className="w-4 h-4" />
                      <span className="text-sm">Copiado!</span>
                    </>
                  ) : (
                    <>
                      <Package className="w-4 h-4" />
                      <span className="text-sm">Exportar Docs</span>
                    </>
                  )}
                </button>
                <button
                  onClick={onClose}
                  className="text-white/80 hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="overflow-y-auto max-h-[calc(90vh-120px)]">

            {/* Resumo Final - Documentos Prontos */}
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500 p-6 m-6 rounded-lg">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-green-800 mb-3 flex items-center gap-2">
                    <Package className="w-5 h-5" />
                    📋 Documentos Finais Prontos
                  </h3>

                  <div className="space-y-3">
                    {/* Título Final */}
                    <div className="bg-white/70 rounded-lg p-3 border border-green-200">
                      <h4 className="font-semibold text-green-700 text-sm mb-1">🎯 TÍTULO SELECIONADO:</h4>
                      <p className="text-gray-800 font-medium">
                        {results?.titles?.data?.generated_titles?.[0]?.title ||
                         results?.titles?.data?.generated_titles?.[0] ||
                         'Título não disponível'}
                      </p>
                    </div>

                    {/* Premissa Final */}
                    {results?.premises?.premises?.[0] && (
                      <div className="bg-white/70 rounded-lg p-3 border border-green-200">
                        <h4 className="font-semibold text-green-700 text-sm mb-1">💡 PREMISSA:</h4>
                        <p className="text-gray-800 text-sm">
                          {results.premises.premises[0].premise.substring(0, 150)}...
                        </p>
                      </div>
                    )}

                    {/* Roteiro Final */}
                    {results?.scripts?.scripts?.chapters && (
                      <div className="bg-white/70 rounded-lg p-3 border border-green-200">
                        <h4 className="font-semibold text-green-700 text-sm mb-1">📝 ROTEIRO:</h4>
                        <p className="text-gray-800 text-sm">
                          {results.scripts.scripts.chapters.length} capítulos prontos
                          {results.scripts.scripts.title && ` - "${results.scripts.scripts.title}"`}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="ml-4 flex flex-col gap-2">
                  <button
                    onClick={exportFinalDocuments}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                  >
                    {copiedItems['final-documents'] ? (
                      <>
                        <Check className="w-4 h-4" />
                        Copiado!
                      </>
                    ) : (
                      <>
                        <Download className="w-4 h-4" />
                        Baixar Docs
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => copyToClipboard(
                      `TÍTULO: ${results?.titles?.data?.generated_titles?.[0]?.title || results?.titles?.data?.generated_titles?.[0] || 'N/A'}\n\nPREMISSA: ${results?.premises?.premises?.[0]?.premise || 'N/A'}\n\nROTEIRO: ${results?.scripts?.scripts?.chapters?.length || 0} capítulos`,
                      'quick-summary'
                    )}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
                  >
                    {copiedItems['quick-summary'] ? (
                      <>
                        <Check className="w-4 h-4" />
                        Copiado!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        Copiar Resumo
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
            {/* Títulos Gerados */}
            {results.titles && (
              <div className="border-b border-gray-200">
                <button
                  onClick={() => toggleSection('titles')}
                  className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-purple-600" />
                    <h3 className="text-lg font-semibold">
                      Títulos Gerados ({results.titles.data?.generated_titles?.length || 0})
                    </h3>
                  </div>
                  {expandedSections.titles ? (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  )}
                </button>

                <AnimatePresence>
                  {expandedSections.titles && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="px-6 pb-6 space-y-4">
                        {results.titles.data?.generated_titles?.map((title, index) => (
                          <motion.div
                            key={index}
                            initial={{ x: -20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: index * 0.1 }}
                            className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded-full font-medium">
                                    #{index + 1}
                                  </span>
                                  {title.viral_score && (
                                    <div className="flex items-center gap-1">
                                      <Star className="w-4 h-4 text-yellow-500" />
                                      <span className="text-sm text-gray-600">
                                        {formatScore(title.viral_score)}
                                      </span>
                                    </div>
                                  )}
                                </div>
                                <p className="text-gray-800 font-medium leading-relaxed">
                                  {title.title || title}
                                </p>
                                {title.reasoning && (
                                  <p className="text-sm text-gray-600 mt-2">
                                    💡 {title.reasoning}
                                  </p>
                                )}
                              </div>
                              <button
                                onClick={() => copyToClipboard(title.title || title, `title-${index}`)}
                                className="flex items-center gap-1 px-3 py-1 text-sm text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-md transition-colors"
                              >
                                {copiedItems[`title-${index}`] ? (
                                  <>
                                    <Check className="w-4 h-4" />
                                    Copiado
                                  </>
                                ) : (
                                  <>
                                    <Copy className="w-4 h-4" />
                                    Copiar
                                  </>
                                )}
                              </button>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}

            {/* Premissas Geradas */}
            {results.premises && (
              <div className="border-b border-gray-200">
                <button
                  onClick={() => toggleSection('premises')}
                  className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Lightbulb className="w-5 h-5 text-yellow-600" />
                    <h3 className="text-lg font-semibold">
                      Premissas Geradas ({results.premises.premises?.length || 0})
                    </h3>
                  </div>
                  {expandedSections.premises ? (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  )}
                </button>

                <AnimatePresence>
                  {expandedSections.premises && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="px-6 pb-6 space-y-4">
                        {results.premises.premises?.map((premise, index) => (
                          <motion.div
                            key={index}
                            initial={{ x: -20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: index * 0.1 }}
                            className="bg-yellow-50 rounded-lg p-4 border border-yellow-200"
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-3">
                                  <span className="bg-yellow-100 text-yellow-700 text-xs px-2 py-1 rounded-full font-medium">
                                    Premissa #{index + 1}
                                  </span>
                                </div>
                                <h4 className="font-semibold text-gray-800 mb-2">
                                  📺 {premise.title}
                                </h4>
                                <p className="text-gray-700 leading-relaxed">
                                  {premise.premise}
                                </p>
                              </div>
                              <button
                                onClick={() => copyToClipboard(`${premise.title}\n\n${premise.premise}`, `premise-${index}`)}
                                className="flex items-center gap-1 px-3 py-1 text-sm text-gray-600 hover:text-yellow-600 hover:bg-yellow-100 rounded-md transition-colors"
                              >
                                {copiedItems[`premise-${index}`] ? (
                                  <>
                                    <Check className="w-4 h-4" />
                                    Copiado
                                  </>
                                ) : (
                                  <>
                                    <Copy className="w-4 h-4" />
                                    Copiar
                                  </>
                                )}
                              </button>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}

            {/* Roteiros Gerados */}
            {results.scripts && (
              <div>
                <button
                  onClick={() => toggleSection('scripts')}
                  className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <BookOpen className="w-5 h-5 text-blue-600" />
                    <h3 className="text-lg font-semibold">
                      Roteiros Gerados ({results.scripts.scripts?.chapters?.length || 0} capítulos)
                    </h3>
                  </div>
                  {expandedSections.scripts ? (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  )}
                </button>

                <AnimatePresence>
                  {expandedSections.scripts && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="px-6 pb-6">
                        {results.scripts.scripts?.title && (
                          <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                            <h4 className="font-semibold text-blue-800 mb-2">
                              🎬 Título do Roteiro
                            </h4>
                            <p className="text-blue-700">
                              {results.scripts.scripts.title}
                            </p>
                          </div>
                        )}

                        <div className="space-y-4">
                          {results.scripts.scripts?.chapters?.map((chapter, index) => (
                            <motion.div
                              key={index}
                              initial={{ x: -20, opacity: 0 }}
                              animate={{ x: 0, opacity: 1 }}
                              transition={{ delay: index * 0.1 }}
                              className="bg-blue-50 rounded-lg p-4 border border-blue-200"
                            >
                              <div className="flex items-start justify-between gap-3">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-3">
                                    <span className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full font-medium">
                                      Capítulo {index + 1}
                                    </span>
                                    {chapter.duration && (
                                      <div className="flex items-center gap-1">
                                        <Clock className="w-4 h-4 text-gray-500" />
                                        <span className="text-sm text-gray-600">
                                          {chapter.duration}
                                        </span>
                                      </div>
                                    )}
                                  </div>
                                  <h5 className="font-semibold text-gray-800 mb-2">
                                    {chapter.title}
                                  </h5>
                                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                                    {chapter.content}
                                  </p>
                                </div>
                                <button
                                  onClick={() => copyToClipboard(`${chapter.title}\n\n${chapter.content}`, `script-${index}`)}
                                  className="flex items-center gap-1 px-3 py-1 text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-100 rounded-md transition-colors"
                                >
                                  {copiedItems[`script-${index}`] ? (
                                    <>
                                      <Check className="w-4 h-4" />
                                      Copiado
                                    </>
                                  ) : (
                                    <>
                                      <Copy className="w-4 h-4" />
                                      Copiar
                                    </>
                                  )}
                                </button>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default AutomationResults
