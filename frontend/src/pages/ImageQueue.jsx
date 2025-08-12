import React, { useState, useEffect } from 'react';
import { Plus, Play, Pause, Trash2, Eye, Download, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const ImageQueue = () => {
  const [queues, setQueues] = useState([]);
  const [scriptPrompts, setScriptPrompts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('queue');
  
  // Estados para criar nova fila
  const [showCreateQueue, setShowCreateQueue] = useState(false);
  const [newQueue, setNewQueue] = useState({
    title: '',
    prompts: '',
    provider: 'pollinations',
    model: 'flux',
    style: 'cinematic, high detail, 4k',
    format: '1024x1024',
    quality: 'standard'
  });
  
  // Estados para geração automática
  const [showScriptToPrompts, setShowScriptToPrompts] = useState(false);
  const [scriptForm, setScriptForm] = useState({
    title: '',
    script: '',
    ai_model: 'gpt-3.5-turbo',
    auto_queue: true,
    provider: 'pollinations',
    model: 'flux',
    style: 'cinematic, high detail, 4k',
    format: '1024x1024',
    quality: 'standard'
  });

  useEffect(() => {
    fetchQueues();
    fetchScriptPrompts();
    
    // Atualizar a cada 3 segundos
    const interval = setInterval(() => {
      fetchQueues();
      fetchScriptPrompts();
    }, 3000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchQueues = async () => {
    try {
      const response = await fetch('/api/image-queue/queue');
      const data = await response.json();
      if (data.success) {
        setQueues(data.data.queues);
      }
    } catch (error) {
      console.error('Erro ao buscar filas:', error);
    }
  };

  const fetchScriptPrompts = async () => {
    try {
      const response = await fetch('/api/image-queue/script-prompts');
      const data = await response.json();
      if (data.success) {
        setScriptPrompts(data.data.script_prompts);
      }
    } catch (error) {
      console.error('Erro ao buscar prompts de script:', error);
    }
  };

  const createQueue = async () => {
    if (!newQueue.title || !newQueue.prompts) {
      alert('Título e prompts são obrigatórios!');
      return;
    }
    
    setLoading(true);
    try {
      const prompts = newQueue.prompts.split('\n').filter(p => p.trim());
      
      const response = await fetch('/api/image-queue/queue', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newQueue,
          prompts
        }),
      });
      
      const data = await response.json();
      
      // Verificar se a resposta HTTP foi bem-sucedida
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${data.error || 'Erro desconhecido'}`);
      }
      
      if (data.success) {
        setShowCreateQueue(false);
        setNewQueue({
          title: '',
          prompts: '',
          provider: 'pollinations',
          model: 'flux',
          style: 'cinematic, high detail, 4k',
          format: '1024x1024',
          quality: 'standard'
        });
        fetchQueues();
        alert('Fila criada com sucesso!');
      } else {
        alert('Erro: ' + data.error);
      }
    } catch (error) {
      console.error('Erro ao criar fila:', error);
      alert('Erro ao criar fila');
    }
    setLoading(false);
  };

  const createScriptToPrompts = async () => {
    if (!scriptForm.title || !scriptForm.script) {
      alert('Título e roteiro são obrigatórios!');
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch('/api/image-queue/script-to-prompts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(scriptForm),
      });
      
      const data = await response.json();
      if (data.success) {
        setShowScriptToPrompts(false);
        setScriptForm({
          title: '',
          script: '',
          ai_model: 'gpt-3.5-turbo',
          auto_queue: true,
          provider: 'pollinations',
          model: 'flux',
          style: 'cinematic, high detail, 4k',
          format: '1024x1024',
          quality: 'standard'
        });
        fetchScriptPrompts();
        if (scriptForm.auto_queue) {
          fetchQueues();
        }
        alert('Processamento iniciado! Os prompts serão gerados automaticamente.');
      } else {
        alert('Erro: ' + data.error);
      }
    } catch (error) {
      console.error('Erro ao processar roteiro:', error);
      alert('Erro ao processar roteiro');
    }
    setLoading(false);
  };

  const deleteQueue = async (queueId) => {
    if (!confirm('Tem certeza que deseja deletar esta fila?')) return;
    
    try {
      const response = await fetch(`/api/image-queue/queue/${queueId}`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      if (data.success) {
        fetchQueues();
        alert('Fila deletada com sucesso!');
      } else {
        alert('Erro: ' + data.error);
      }
    } catch (error) {
      console.error('Erro ao deletar fila:', error);
      alert('Erro ao deletar fila');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'processing':
        return <Play className="w-5 h-5 text-blue-500" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending': return 'Pendente';
      case 'processing': return 'Processando';
      case 'completed': return 'Concluído';
      case 'failed': return 'Falhou';
      default: return 'Desconhecido';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🎨 Fila de Imagens
          </h1>
          <p className="text-gray-600">
            Sistema avançado de geração de imagens em lote e prompts automáticos
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('queue')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'queue'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Filas de Imagens
              </button>
              <button
                onClick={() => setActiveTab('scripts')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'scripts'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Roteiros → Prompts
              </button>
            </nav>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mb-6 flex gap-4">
          {activeTab === 'queue' && (
            <button
              onClick={() => setShowCreateQueue(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Nova Fila
            </button>
          )}
          {activeTab === 'scripts' && (
            <button
              onClick={() => setShowScriptToPrompts(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Roteiro → Prompts
            </button>
          )}
        </div>

        {/* Content */}
        {activeTab === 'queue' && (
          <div className="space-y-6">
            {/* Queue List */}
            {queues.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-lg mb-2">Nenhuma fila encontrada</div>
                <p className="text-gray-500">Crie sua primeira fila de imagens!</p>
              </div>
            ) : (
              <div className="grid gap-6">
                {queues.map((queue) => (
                  <div key={queue.id} className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">
                          {queue.title}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            {getStatusIcon(queue.status)}
                            <span>{getStatusText(queue.status)}</span>
                          </div>
                          <span>{queue.current_prompt_index}/{queue.total_prompts} prompts</span>
                          <span>{queue.provider} - {queue.model}</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => deleteQueue(queue.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="mb-4">
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>Progresso</span>
                        <span>{queue.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${queue.progress}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    {/* Generated Images */}
                    {queue.generated_images && queue.generated_images.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">
                          Imagens Geradas ({queue.generated_images.filter(img => img !== null).length})
                        </h4>
                        <div className="grid grid-cols-6 gap-2">
                          {queue.generated_images.map((imageUrl, index) => (
                            imageUrl ? (
                              <div key={index} className="relative group">
                                <img
                                  src={imageUrl}
                                  alt={`Imagem ${index + 1}`}
                                  className="w-full h-20 object-cover rounded border"
                                />
                                <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded flex items-center justify-center">
                                  <a
                                    href={imageUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-white hover:text-blue-300"
                                  >
                                    <Eye className="w-4 h-4" />
                                  </a>
                                </div>
                              </div>
                            ) : (
                              <div key={index} className="w-full h-20 bg-gray-200 rounded border flex items-center justify-center">
                                <XCircle className="w-4 h-4 text-gray-400" />
                              </div>
                            )
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Error Message */}
                    {queue.error_message && (
                      <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
                        <p className="text-red-800 text-sm">{queue.error_message}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'scripts' && (
          <div className="space-y-6">
            {/* Script Prompts List */}
            {scriptPrompts.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-lg mb-2">Nenhum roteiro processado</div>
                <p className="text-gray-500">Converta seu primeiro roteiro em prompts!</p>
              </div>
            ) : (
              <div className="grid gap-6">
                {scriptPrompts.map((scriptPrompt) => (
                  <div key={scriptPrompt.id} className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">
                          {scriptPrompt.title}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            {getStatusIcon(scriptPrompt.status)}
                            <span>{getStatusText(scriptPrompt.status)}</span>
                          </div>
                          {scriptPrompt.processing_time && (
                            <span>{scriptPrompt.processing_time.toFixed(2)}s</span>
                          )}
                          {scriptPrompt.queue_id && (
                            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                              Fila #{scriptPrompt.queue_id}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    {/* Generated Prompts */}
                    {scriptPrompt.generated_prompts && scriptPrompt.generated_prompts.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">
                          Prompts Gerados ({scriptPrompt.generated_prompts.length})
                        </h4>
                        <div className="space-y-2 max-h-60 overflow-y-auto">
                          {scriptPrompt.generated_prompts.map((promptData, index) => (
                            <div key={index} className="bg-gray-50 p-3 rounded border">
                              <div className="text-xs text-gray-500 mb-1">
                                Cena {promptData.index}: {promptData.scene}
                              </div>
                              <div className="text-sm text-gray-800">
                                <strong>Prompt:</strong> {promptData.prompt}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Error Message */}
                    {scriptPrompt.error_message && (
                      <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
                        <p className="text-red-800 text-sm">{scriptPrompt.error_message}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create Queue Modal */}
      {showCreateQueue && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto text-gray-900">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Nova Fila de Imagens</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Título
                  </label>
                  <input
                    type="text"
                    value={newQueue.title}
                    onChange={(e) => setNewQueue({...newQueue, title: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Ex: Imagens para vídeo motivacional"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Prompts (um por linha)
                  </label>
                  <textarea
                    value={newQueue.prompts}
                    onChange={(e) => setNewQueue({...newQueue, prompts: e.target.value})}
                    rows={8}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Uma pessoa caminhando na praia ao pôr do sol\nUm escritório moderno com vista para a cidade\nUma família feliz no parque"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Provedor
                    </label>
                    <select
                      value={newQueue.provider}
                      onChange={(e) => setNewQueue({...newQueue, provider: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="pollinations">Pollinations.ai</option>
                      <option value="together">Together.ai</option>
                      <option value="gemini">Google Gemini</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Modelo
                    </label>
                    <select
                      value={newQueue.model}
                      onChange={(e) => setNewQueue({...newQueue, model: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="flux">Flux</option>
                      <option value="gpt">GPT</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Estilo
                  </label>
                  <input
                    type="text"
                    value={newQueue.style}
                    onChange={(e) => setNewQueue({...newQueue, style: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="cinematic, high detail, 4k"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Formato
                    </label>
                    <select
                      value={newQueue.format}
                      onChange={(e) => setNewQueue({...newQueue, format: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="1024x1024">1024x1024 (Quadrado)</option>
                      <option value="1920x1080">1920x1080 (16:9)</option>
                      <option value="1080x1920">1080x1920 (9:16)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Qualidade
                    </label>
                    <select
                      value={newQueue.quality}
                      onChange={(e) => setNewQueue({...newQueue, quality: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="standard">Padrão</option>
                      <option value="hd">HD</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowCreateQueue(false)}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={createQueue}
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Criando...' : 'Criar Fila'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Script to Prompts Modal */}
      {showScriptToPrompts && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto text-gray-900">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Roteiro → Prompts</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Título
                  </label>
                  <input
                    type="text"
                    value={scriptForm.title}
                    onChange={(e) => setScriptForm({...scriptForm, title: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Ex: Vídeo motivacional sobre sucesso"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Roteiro
                  </label>
                  <textarea
                    value={scriptForm.script}
                    onChange={(e) => setScriptForm({...scriptForm, script: e.target.value})}
                    rows={10}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Cole seu roteiro aqui. Separe as cenas com parágrafos duplos para melhor resultado."
                  />
                </div>
                
                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={scriptForm.auto_queue}
                      onChange={(e) => setScriptForm({...scriptForm, auto_queue: e.target.checked})}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      Criar fila automaticamente após gerar prompts
                    </span>
                  </label>
                </div>
                
                {scriptForm.auto_queue && (
                  <div className="bg-gray-50 p-4 rounded-lg space-y-4">
                    <h3 className="text-sm font-medium text-gray-900">Configurações da Fila</h3>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Provedor
                        </label>
                        <select
                          value={scriptForm.provider}
                          onChange={(e) => setScriptForm({...scriptForm, provider: e.target.value})}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="pollinations">Pollinations.ai</option>
                          <option value="together">Together.ai</option>
                          <option value="gemini">Google Gemini</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Modelo
                        </label>
                        <select
                          value={scriptForm.model}
                          onChange={(e) => setScriptForm({...scriptForm, model: e.target.value})}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="flux">Flux</option>
                          <option value="gpt">GPT</option>
                        </select>
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Estilo
                      </label>
                      <input
                        type="text"
                        value={scriptForm.style}
                        onChange={(e) => setScriptForm({...scriptForm, style: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="cinematic, high detail, 4k"
                      />
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowScriptToPrompts(false)}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={createScriptToPrompts}
                  disabled={loading}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  {loading ? 'Processando...' : 'Gerar Prompts'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageQueue;