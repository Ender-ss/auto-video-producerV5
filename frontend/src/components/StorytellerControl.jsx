import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Save, 
  FileText, 
  Settings, 
  CheckCircle, 
  AlertCircle,
  Clock,
  BookOpen,
  Zap,
  Eye
} from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const StorytellerControl = ({ onStoryComplete }) => {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState('');
  const [storyContent, setStoryContent] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState('');
  const [storyPlan, setStoryPlan] = useState(null);
  const [chapters, setChapters] = useState([]);
  const [validationResults, setValidationResults] = useState({});
  const [cacheInfo, setCacheInfo] = useState({});
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Carregar agentes disponíveis
  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await fetch(`${API_BASE}/storyteller/agents`);
      const data = await response.json();
      if (data.success) {
        setAgents(data.agents);
        if (data.agents.length > 0) {
          setSelectedAgent(data.agents[0].id);
        }
      }
    } catch (error) {
      console.error('Erro ao carregar agentes:', error);
      setError('Erro ao carregar agentes');
    }
  };

  const generateStoryPlan = async () => {
    if (!storyContent.trim() || !selectedAgent) {
      setError('Por favor, insira o conteúdo da história e selecione um agente');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setSuccess(null);
    setCurrentStep('Gerando plano da história...');

    try {
      const response = await fetch(`${API_BASE}/storyteller/generate-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: storyContent,
          agent_id: selectedAgent,
          options: {
            max_chapters: 10,
            target_duration: 300,
            include_cliffhangers: true
          }
        }),
      });

      const data = await response.json();
      if (data.success) {
        setStoryPlan(data.plan);
        setCurrentStep('Dividindo conteúdo em capítulos...');
        await splitContent(data.plan);
      } else {
        throw new Error(data.error || 'Erro ao gerar plano');
      }
    } catch (error) {
      setError(error.message);
      setIsProcessing(false);
    }
  };

  const splitContent = async (plan) => {
    try {
      const response = await fetch(`${API_BASE}/storyteller/split-content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan: plan,
          agent_id: selectedAgent
        }),
      });

      const data = await response.json();
      if (data.success) {
        setChapters(data.chapters);
        setCurrentStep('Validando capítulos...');
        await validateChapters(data.chapters);
      } else {
        throw new Error(data.error || 'Erro ao dividir conteúdo');
      }
    } catch (error) {
      setError(error.message);
      setIsProcessing(false);
    }
  };

  const validateChapters = async (chapters) => {
    try {
      const validations = {};
      
      for (let i = 0; i < chapters.length; i++) {
        const chapter = chapters[i];
        setCurrentStep(`Validando capítulo ${i + 1}/${chapters.length}...`);
        
        const response = await fetch(`${API_BASE}/storyteller/validate-chapter`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            chapter: chapter,
            agent_id: selectedAgent
          }),
        });

        const data = await response.json();
        validations[chapter.id] = data;
      }

      setValidationResults(validations);
      setSuccess('História processada com sucesso!');
      setCurrentStep('Concluído');
      
      if (onStoryComplete) {
        onStoryComplete({
          plan: storyPlan,
          chapters: chapters,
          validations: validations
        });
      }
    } catch (error) {
      setError('Erro ao validar capítulos: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const clearCache = async () => {
    try {
      const response = await fetch(`${API_BASE}/storyteller/cache/clear`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('Cache limpo com sucesso!');
      }
    } catch (error) {
      setError('Erro ao limpar cache');
    }
  };

  const getCacheInfo = async () => {
    try {
      const response = await fetch(`${API_BASE}/storyteller/cache/info`);
      const data = await response.json();
      if (data.success) {
        setCacheInfo(data.cache);
      }
    } catch (error) {
      console.error('Erro ao obter info do cache:', error);
    }
  };

  const resetAll = () => {
    setStoryContent('');
    setStoryPlan(null);
    setChapters([]);
    setValidationResults({});
    setError(null);
    setSuccess(null);
    setCurrentStep('');
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <BookOpen className="w-6 h-6" />
            Storyteller Unlimited
          </h2>
          <p className="text-gray-600 mt-1">
            Transforme qualquer história em conteúdo viral com IA
          </p>
        </div>
        <button
          onClick={getCacheInfo}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          title="Ver informações do cache"
        >
          <Eye className="w-5 h-5" />
        </button>
      </div>

      {/* Seleção de Agente */}
      <div className="space-y-4">
        <label className="block text-sm font-medium text-gray-700">
          Estilo de História
        </label>
        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isProcessing}
        >
          <option value="">Selecione um agente...</option>
          {agents.map((agent) => (
            <option key={agent.id} value={agent.id}>
              {agent.name} - {agent.description}
            </option>
          ))}
        </select>
      </div>

      {/* Conteúdo da História */}
      <div className="space-y-4">
        <label className="block text-sm font-medium text-gray-700">
          Conteúdo da História
        </label>
        <textarea
          value={storyContent}
          onChange={(e) => setStoryContent(e.target.value)}
          placeholder="Cole aqui o conteúdo completo da sua história..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-32"
          rows={8}
          disabled={isProcessing}
        />
        <div className="text-sm text-gray-500">
          {storyContent.length} caracteres
        </div>
      </div>

      {/* Botões de Controle */}
      <div className="flex items-center gap-3">
        <button
          onClick={generateStoryPlan}
          disabled={isProcessing || !storyContent.trim() || !selectedAgent}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isProcessing ? (
            <>
              <Clock className="w-4 h-4 animate-spin" />
              Processando...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Gerar História
            </>
          )}
        </button>

        <button
          onClick={resetAll}
          disabled={isProcessing}
          className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          Limpar
        </button>

        <button
          onClick={clearCache}
          disabled={isProcessing}
          className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 transition-colors"
        >
          <Zap className="w-4 h-4" />
          Limpar Cache
        </button>
      </div>

      {/* Status de Processamento */}
      {isProcessing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-600 animate-spin" />
            <p className="text-blue-800 font-medium">{currentStep}</p>
          </div>
        </div>
      )}

      {/* Mensagens de Erro/Sucesso */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <p className="text-green-800">{success}</p>
          </div>
        </div>
      )}

      {/* Plano da História */}
      {storyPlan && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Plano da História
          </h3>
          <div className="text-sm text-gray-600 space-y-1">
            <p><strong>Agente:</strong> {storyPlan.agent_name}</p>
            <p><strong>Capítulos:</strong> {storyPlan.total_chapters}</p>
            <p><strong>Duração estimada:</strong> {storyPlan.estimated_duration} minutos</p>
            <p><strong>Estilo:</strong> {storyPlan.style}</p>
          </div>
        </div>
      )}

      {/* Capítulos */}
      {chapters.length > 0 && (
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            <BookOpen className="w-4 h-4" />
            Capítulos Gerados ({chapters.length})
          </h3>
          <div className="space-y-3">
            {chapters.map((chapter, index) => (
              <div key={chapter.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">
                    Capítulo {index + 1}: {chapter.title}
                  </h4>
                  {validationResults[chapter.id] && (
                    <div className={`px-2 py-1 rounded text-xs font-medium ${
                      validationResults[chapter.id].is_valid 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {validationResults[chapter.id].is_valid ? 'Válido' : 'Precisa ajuste'}
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-2">
                  {chapter.content.substring(0, 150)}...
                </p>
                <div className="text-xs text-gray-500 space-x-4">
                  <span>{chapter.character_count} caracteres</span>
                  <span>{chapter.estimated_duration}s</span>
                  <span>{chapter.cliffhanger_type}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cache Info */}
      {Object.keys(cacheInfo).length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
          <h4 className="font-medium mb-2">Informações do Cache</h4>
          <div className="grid grid-cols-2 gap-2">
            <div>Contextos: {cacheInfo.contexts || 0}</div>
            <div>Breakpoints: {cacheInfo.breakpoints || 0}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StorytellerControl;