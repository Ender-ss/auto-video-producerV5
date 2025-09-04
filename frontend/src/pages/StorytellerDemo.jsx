import React, { useState } from 'react';
import StorytellerControl from '../components/StorytellerControl';
import { Download, Copy, Share2, PlayCircle, BookOpen } from 'lucide-react';

const StorytellerDemo = () => {
  const [completedStory, setCompletedStory] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);

  const handleStoryComplete = (storyData) => {
    setCompletedStory(storyData);
    setSelectedChapter(null);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const exportStory = () => {
    if (!completedStory) return;
    
    const exportData = {
      ...completedStory,
      exported_at: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `storyteller-story-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const generateVideoScript = (chapter) => {
    return {
      title: chapter.title,
      content: chapter.content,
      duration: chapter.estimated_duration,
      style: chapter.cliffhanger_type,
      hooks: [
        "Você não vai acreditar no que aconteceu...",
        "Esta história vai mudar sua vida...",
        "Prepare-se para o plot twist..."
      ]
    };
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Storyteller Unlimited
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Transforme qualquer história em conteúdo viral com IA. 
            Divida, valide e otimize automaticamente para máximo engajamento.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Painel de Controle */}
          <div>
            <StorytellerControl onStoryComplete={handleStoryComplete} />
          </div>

          {/* Visualização dos Resultados */}
          <div className="space-y-6">
            {completedStory && (
              <>
                {/* Estatísticas */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Estatísticas da História
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-blue-600">
                        {completedStory.chapters.length}
                      </div>
                      <div className="text-sm text-blue-800">Capítulos</div>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-green-600">
                        {Math.round(completedStory.chapters.reduce((sum, ch) => sum + ch.estimated_duration, 0) / 60)}m
                      </div>
                      <div className="text-sm text-green-800">Duração Total</div>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-purple-600">
                        {completedStory.chapters.reduce((sum, ch) => sum + ch.character_count, 0)}
                      </div>
                      <div className="text-sm text-purple-800">Caracteres</div>
                    </div>
                    <div className="bg-orange-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-orange-600">
                        {Object.values(completedStory.validations).filter(v => v.is_valid).length}
                      </div>
                      <div className="text-sm text-orange-800">Válidos</div>
                    </div>
                  </div>
                </div>

                {/* Ações */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Exportar Resultados
                  </h3>
                  <div className="flex gap-3">
                    <button
                      onClick={exportStory}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      Exportar JSON
                    </button>
                    <button
                      onClick={() => copyToClipboard(JSON.stringify(completedStory, null, 2))}
                      className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                    >
                      <Copy className="w-4 h-4" />
                      Copiar Dados
                    </button>
                  </div>
                </div>

                {/* Lista de Capítulos */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Capítulos Gerados
                  </h3>
                  <div className="space-y-3">
                    {completedStory.chapters.map((chapter, index) => {
                      const validation = completedStory.validations[chapter.id];
                      const isSelected = selectedChapter?.id === chapter.id;
                      
                      return (
                        <div
                          key={chapter.id}
                          className={`border rounded-lg p-4 cursor-pointer transition-all ${
                            isSelected 
                              ? 'border-blue-500 bg-blue-50' 
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          onClick={() => setSelectedChapter(chapter)}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-gray-900">
                              Capítulo {index + 1}: {chapter.title}
                            </h4>
                            <div className="flex items-center gap-2">
                              {validation?.is_valid && (
                                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                  Válido
                                </span>
                              )}
                              {validation?.suggestions && (
                                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                                  {validation.suggestions.length} sugestões
                                </span>
                              )}
                            </div>
                          </div>
                          
                          <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                            {chapter.content}
                          </p>
                          
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>{chapter.character_count} caracteres</span>
                            <span>{chapter.estimated_duration}s</span>
                            <span className="capitalize">{chapter.cliffhanger_type}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Detalhes do Capítulo Selecionado */}
                {selectedChapter && (
                  <div className="bg-white rounded-lg shadow-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Detalhes do Capítulo
                    </h3>
                    
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">
                          {selectedChapter.title}
                        </h4>
                        <p className="text-gray-600 whitespace-pre-wrap">
                          {selectedChapter.content}
                        </p>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Duração:</span>
                          <span className="ml-2 text-gray-600">{selectedChapter.estimated_duration}s</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Caracteres:</span>
                          <span className="ml-2 text-gray-600">{selectedChapter.character_count}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Estilo:</span>
                          <span className="ml-2 text-gray-600 capitalize">{selectedChapter.cliffhanger_type}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Break Pattern:</span>
                          <span className="ml-2 text-gray-600">{selectedChapter.break_pattern}</span>
                        </div>
                      </div>

                      {completedStory.validations[selectedChapter.id] && (
                        <div>
                          <h5 className="font-medium text-gray-900 mb-2">Validação</h5>
                          <div className="text-sm space-y-1">
                            <p><strong>Válido:</strong> {completedStory.validations[selectedChapter.id].is_valid ? 'Sim' : 'Não'}</p>
                            <p><strong>Pontuação:</strong> {completedStory.validations[selectedChapter.id].score}/100</p>
                            {completedStory.validations[selectedChapter.id].suggestions && (
                              <div>
                                <strong>Sugestões:</strong>
                                <ul className="list-disc list-inside ml-4">
                                  {completedStory.validations[selectedChapter.id].suggestions.map((suggestion, i) => (
                                    <li key={i}>{suggestion}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Gerar Script de Vídeo */}
                      <div className="pt-4 border-t">
                        <button
                          onClick={() => {
                            const script = generateVideoScript(selectedChapter);
                            copyToClipboard(JSON.stringify(script, null, 2));
                          }}
                          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
                        >
                          <PlayCircle className="w-4 h-4" />
                          Copiar Script de Vídeo
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Placeholder */}
            {!completedStory && (
              <div className="bg-white rounded-lg shadow-lg p-12 text-center">
                <div className="text-gray-400">
                  <BookOpen className="w-16 h-16 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Pronto para começar?
                  </h3>
                  <p className="text-gray-600">
                    Use o painel ao lado para inserir sua história e gerar conteúdo viral com IA.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StorytellerDemo;