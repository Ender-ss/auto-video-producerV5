import React, { useState } from 'react';
import { Loader2, Play, Clock, CheckCircle, XCircle, Youtube, Zap, Download, AlertCircle } from 'lucide-react';

const YouTubeExtractComparison = () => {
  const [url, setUrl] = useState('https://www.youtube.com/@eusouodh');
  const [maxTitles, setMaxTitles] = useState(10);
  const [minViews, setMinViews] = useState(0);
  const [maxViews, setMaxViews] = useState('');
  const [days, setDays] = useState(30);
  
  const [results, setResults] = useState({
    rapidapi: null,
    youtube: null,
    ytdlp: null
  });
  
  const [loading, setLoading] = useState({
    rapidapi: false,
    youtube: false,
    ytdlp: false
  });
  
  const [errors, setErrors] = useState({
    rapidapi: null,
    youtube: null,
    ytdlp: null
  });

  const testMethod = async (method, endpoint) => {
    setLoading(prev => ({ ...prev, [method]: true }));
    setResults(prev => ({ ...prev, [method]: null }));
    setErrors(prev => ({ ...prev, [method]: null }));
    
    try {
      const payload = {
        url,
        channel_url: url, // Para yt-dlp que espera channel_url
        max_titles: maxTitles,
        min_views: minViews || 0,
        max_views: maxViews ? parseInt(maxViews) : null,
        days: days ? parseInt(days) : null
      };
      
      console.log(`🧪 Testando ${method}:`, payload);
      
      const response = await fetch(`/api/automations/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });
      
      const responseText = await response.text();
      let data;
      
      try {
        data = JSON.parse(responseText);
      } catch (parseError) {
        throw new Error(`Erro ao parsear JSON: ${parseError.message}`);
      }
      
      setResults(prev => ({ ...prev, [method]: {
        status: response.status,
        data: data,
        success: data.success || false,
        response_time: data.response_time || 'N/A'
      }}));
      
      if (!data.success) {
        setErrors(prev => ({ ...prev, [method]: data.error || 'Erro desconhecido' }));
      }
      
    } catch (error) {
      console.error(`Erro no teste ${method}:`, error);
      setErrors(prev => ({ ...prev, [method]: error.message }));
    } finally {
      setLoading(prev => ({ ...prev, [method]: false }));
    }
  };

  const testAllMethods = async () => {
    await Promise.all([
      testMethod('rapidapi', 'test-rapidapi'),
      testMethod('youtube', 'test-youtube-api'),
      testMethod('ytdlp', 'test-ytdlp')
    ]);
  };

  const getMethodIcon = (method) => {
    switch (method) {
      case 'rapidapi': return <Zap className="w-5 h-5 text-yellow-500" />;
      case 'youtube': return <Youtube className="w-5 h-5 text-red-500" />;
      case 'ytdlp': return <Download className="w-5 h-5 text-blue-500" />;
      default: return <Play className="w-5 h-5" />;
    }
  };

  const getMethodName = (method) => {
    switch (method) {
      case 'rapidapi': return 'RapidAPI';
      case 'youtube': return 'YouTube API Oficial';
      case 'ytdlp': return 'yt-dlp';
      default: return method;
    }
  };

  const getStatusBadge = (method) => {
    const isLoading = loading[method];
    const result = results[method];
    const error = errors[method];
    
    if (isLoading) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          <Loader2 className="w-3 h-3 mr-1 animate-spin" /> Testando...
        </span>
      );
    }
    if (error) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <XCircle className="w-3 h-3 mr-1" /> Erro
        </span>
      );
    }
    if (result?.success) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <CheckCircle className="w-3 h-3 mr-1" /> Sucesso
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
        Aguardando
      </span>
    );
  };

  const ResultCard = ({ method }) => {
    const result = results[method];
    const error = errors[method];
    const isLoading = loading[method];
    
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            {getMethodIcon(method)}
            <h3 className="text-lg font-semibold text-white">{getMethodName(method)}</h3>
          </div>
          {getStatusBadge(method)}
        </div>
        
        <button
          onClick={() => testMethod(method, `test-${method === 'youtube' ? 'youtube-api' : method}`)}
          disabled={isLoading}
          className="w-full mb-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg flex items-center justify-center space-x-2 transition-colors"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Testando...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Testar {getMethodName(method)}</span>
            </>
          )}
        </button>
        
        {result && (
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <Clock className="w-4 h-4" />
              <span>Tempo: {result.response_time}s</span>
            </div>
            
            {result.success ? (
              <div className="space-y-2">
                <div className="text-sm font-medium text-green-400">
                  ✅ {result.data?.data?.total_videos || 0} vídeos extraídos
                </div>
                <div className="text-xs text-gray-500">
                  {result.data?.data?.message}
                </div>
                
                {result.data?.data?.videos && result.data.data.videos.length > 0 && (
                  <div className="space-y-1 max-h-40 overflow-y-auto">
                    <div className="text-xs font-medium text-gray-300">Primeiros títulos:</div>
                    {result.data.data.videos.slice(0, 3).map((video, index) => (
                      <div key={index} className="text-xs p-2 bg-gray-700 rounded border-l-2 border-green-400">
                        <div className="font-medium text-white truncate">{video.title}</div>
                        <div className="text-gray-400">{video.views?.toLocaleString()} visualizações</div>
                      </div>
                    ))}
                    {result.data.data.videos.length > 3 && (
                      <div className="text-xs text-gray-500 text-center py-1">
                        ... e mais {result.data.data.videos.length - 3} vídeos
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-sm font-medium text-red-400">
                  ❌ Erro na extração
                </div>
                <div className="text-xs text-red-300 bg-red-900/30 p-2 rounded">
                  {error || result.data?.error || 'Erro desconhecido'}
                </div>
              </div>
            )}
          </div>
        )}
        
        {error && !result && (
          <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg">
            <div className="flex items-center space-x-2 text-red-400 mb-1">
              <AlertCircle className="w-4 h-4" />
              <span className="font-semibold text-sm">Erro:</span>
            </div>
            <div className="text-red-300 text-xs">{error}</div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-white">Comparação de Métodos de Extração YouTube</h1>
          <p className="text-gray-400">Teste e compare os três métodos de extração de vídeos do YouTube</p>
        </div>

        {/* Configurações */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Configurações do Teste</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-1">URL do Canal</label>
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="MrBeast, @MrBeast, ou UCX6OQ3DkcsbYNE6H8uQQuVA"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Máx. Títulos</label>
              <input
                type="number"
                value={maxTitles}
                onChange={(e) => setMaxTitles(parseInt(e.target.value) || 5)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Min. Visualizações</label>
              <input
                type="number"
                value={minViews}
                onChange={(e) => setMinViews(parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Máx. Visualizações</label>
              <input
                type="number"
                value={maxViews}
                onChange={(e) => setMaxViews(e.target.value)}
                placeholder="Opcional"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <div className="flex gap-4">
            <button 
              onClick={testAllMethods}
              disabled={Object.values(loading).some(Boolean)}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg flex items-center space-x-2 transition-colors"
            >
              {Object.values(loading).some(Boolean) ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Testando...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Testar Todos os Métodos</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Resultados */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <ResultCard method="rapidapi" />
          <ResultCard method="youtube" />
          <ResultCard method="ytdlp" />
        </div>

        {/* Comparação de Performance */}
        {Object.values(results).some(r => r?.success) && (
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Comparação de Performance</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(results).map(([method, result]) => {
                if (!result?.success) return null;
                return (
                  <div key={method} className="text-center p-4 bg-gray-700 rounded-lg">
                    <div className="flex items-center justify-center space-x-2 mb-2">
                      {getMethodIcon(method)}
                      <span className="font-medium text-white">{getMethodName(method)}</span>
                    </div>
                    <div className="text-2xl font-bold text-blue-400">{result.response_time}s</div>
                    <div className="text-sm text-gray-400">{result.data?.data?.total_videos || 0} vídeos</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default YouTubeExtractComparison;