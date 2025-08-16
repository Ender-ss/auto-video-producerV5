# Especificações Técnicas de Implementação - Auto Video Producer

## 1. Sistema de Roteiros Longos (1+ hora)

### 1.1 Arquitetura de Segmentação

**Estrutura de Dados:**
```python
class LongScript:
    def __init__(self):
        self.total_duration = 0  # em minutos
        self.segments = []
        self.transitions = []
        self.metadata = {}
        
class ScriptSegment:
    def __init__(self):
        self.id = ""
        self.title = ""
        self.content = ""
        self.duration = 0  # em minutos
        self.images_needed = 0
        self.audio_file = ""
        self.order = 0
```

**Implementação Backend:**
```python
# backend/services/long_script_generator.py
class LongScriptGenerator:
    def __init__(self):
        self.max_segment_duration = 20  # minutos
        self.min_segment_duration = 10  # minutos
        
    async def generate_long_script(self, topic, target_duration, style):
        # 1. Criar outline baseado na duração
        outline = await self.create_outline(topic, target_duration)
        
        # 2. Gerar segmentos individuais
        segments = []
        for section in outline:
            segment = await self.generate_segment(section, style)
            segments.append(segment)
            
        # 3. Criar transições
        transitions = await self.generate_transitions(segments)
        
        # 4. Compilar script final
        return self.compile_script(segments, transitions)
        
    async def create_outline(self, topic, duration):
        # Usar LLM para criar estrutura baseada na duração
        prompt = f"""
        Crie um outline detalhado para um vídeo de {duration} minutos sobre {topic}.
        Divida em segmentos de 10-20 minutos cada.
        Inclua:
        - Introdução (5-10 min)
        - Desenvolvimento (segmentos principais)
        - Conclusão (5-10 min)
        """
        return await self.llm_service.generate(prompt)
```

### 1.2 Interface Frontend

**Componente React:**
```jsx
// frontend/src/components/LongScriptGenerator.jsx
const LongScriptGenerator = () => {
    const [targetDuration, setTargetDuration] = useState(60); // minutos
    const [segments, setSegments] = useState([]);
    const [isGenerating, setIsGenerating] = useState(false);
    
    const generateLongScript = async () => {
        setIsGenerating(true);
        try {
            const response = await fetch('/api/automations/generate-long-script', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: formData.topic,
                    target_duration: targetDuration,
                    style: formData.style
                })
            });
            
            const result = await response.json();
            setSegments(result.segments);
        } catch (error) {
            console.error('Erro ao gerar roteiro longo:', error);
        } finally {
            setIsGenerating(false);
        }
    };
    
    return (
        <div className="long-script-generator">
            <div className="duration-selector">
                <label>Duração Alvo (minutos):</label>
                <input 
                    type="number" 
                    value={targetDuration}
                    onChange={(e) => setTargetDuration(e.target.value)}
                    min="60"
                    max="180"
                />
            </div>
            
            <div className="segments-preview">
                {segments.map((segment, index) => (
                    <SegmentCard key={index} segment={segment} />
                ))}
            </div>
            
            <button onClick={generateLongScript} disabled={isGenerating}>
                {isGenerating ? 'Gerando...' : 'Gerar Roteiro Longo'}
            </button>
        </div>
    );
};
```

## 2. Sistema de Fila e Automação

### 2.1 Queue Manager

**Implementação com Redis:**
```python
# backend/services/queue_manager.py
import redis
import json
from datetime import datetime
from enum import Enum

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class QueueManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.queue_name = "video_production_queue"
        self.processing_queue = "processing_queue"
        
    async def add_job(self, job_data):
        job = {
            'id': self.generate_job_id(),
            'type': job_data['type'],
            'data': job_data,
            'status': JobStatus.PENDING.value,
            'created_at': datetime.now().isoformat(),
            'priority': job_data.get('priority', 5),
            'retry_count': 0,
            'max_retries': 3
        }
        
        # Adicionar à fila com prioridade
        self.redis_client.zadd(
            self.queue_name, 
            {json.dumps(job): job['priority']}
        )
        
        return job['id']
        
    async def get_next_job(self):
        # Pegar job com maior prioridade
        job_data = self.redis_client.zpopmax(self.queue_name)
        if job_data:
            job = json.loads(job_data[0][0])
            job['status'] = JobStatus.PROCESSING.value
            
            # Mover para fila de processamento
            self.redis_client.hset(
                self.processing_queue, 
                job['id'], 
                json.dumps(job)
            )
            
            return job
        return None
        
    async def complete_job(self, job_id, result):
        job_data = self.redis_client.hget(self.processing_queue, job_id)
        if job_data:
            job = json.loads(job_data)
            job['status'] = JobStatus.COMPLETED.value
            job['completed_at'] = datetime.now().isoformat()
            job['result'] = result
            
            # Salvar resultado
            self.redis_client.hset(f"completed_jobs", job_id, json.dumps(job))
            self.redis_client.hdel(self.processing_queue, job_id)
            
    async def fail_job(self, job_id, error):
        job_data = self.redis_client.hget(self.processing_queue, job_id)
        if job_data:
            job = json.loads(job_data)
            job['retry_count'] += 1
            job['last_error'] = str(error)
            
            if job['retry_count'] < job['max_retries']:
                job['status'] = JobStatus.RETRYING.value
                # Recolocar na fila com prioridade menor
                self.redis_client.zadd(
                    self.queue_name,
                    {json.dumps(job): job['priority'] - 1}
                )
            else:
                job['status'] = JobStatus.FAILED.value
                self.redis_client.hset(f"failed_jobs", job_id, json.dumps(job))
                
            self.redis_client.hdel(self.processing_queue, job_id)
```

### 2.2 Worker Process

**Implementação do Worker:**
```python
# backend/services/queue_worker.py
import asyncio
from .queue_manager import QueueManager
from .video_processor import VideoProcessor

class QueueWorker:
    def __init__(self):
        self.queue_manager = QueueManager()
        self.video_processor = VideoProcessor()
        self.is_running = False
        
    async def start(self):
        self.is_running = True
        print("Worker iniciado...")
        
        while self.is_running:
            try:
                job = await self.queue_manager.get_next_job()
                if job:
                    await self.process_job(job)
                else:
                    await asyncio.sleep(5)  # Aguardar novos jobs
                    
            except Exception as e:
                print(f"Erro no worker: {e}")
                await asyncio.sleep(10)
                
    async def process_job(self, job):
        try:
            job_type = job['type']
            job_data = job['data']
            
            if job_type == 'extract_channel_videos':
                result = await self.process_channel_extraction(job_data)
            elif job_type == 'generate_video':
                result = await self.process_video_generation(job_data)
            elif job_type == 'batch_process':
                result = await self.process_batch(job_data)
            else:
                raise ValueError(f"Tipo de job desconhecido: {job_type}")
                
            await self.queue_manager.complete_job(job['id'], result)
            
        except Exception as e:
            await self.queue_manager.fail_job(job['id'], e)
            
    async def process_channel_extraction(self, data):
        # Extrair vídeos de um canal
        channel_url = data['channel_url']
        max_videos = data.get('max_videos', 10)
        
        videos = await self.video_processor.extract_channel_videos(
            channel_url, max_videos
        )
        
        # Adicionar jobs de geração para cada vídeo
        for video in videos:
            await self.queue_manager.add_job({
                'type': 'generate_video',
                'video_data': video,
                'priority': data.get('priority', 5)
            })
            
        return {'extracted_videos': len(videos)}
```

### 2.3 Dashboard de Monitoramento

**Interface React:**
```jsx
// frontend/src/pages/QueueDashboard.jsx
import React, { useState, useEffect } from 'react';

const QueueDashboard = () => {
    const [queueStats, setQueueStats] = useState({
        pending: 0,
        processing: 0,
        completed: 0,
        failed: 0
    });
    const [jobs, setJobs] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    
    useEffect(() => {
        fetchQueueStats();
        const interval = setInterval(fetchQueueStats, 5000); // Atualizar a cada 5s
        return () => clearInterval(interval);
    }, []);
    
    const fetchQueueStats = async () => {
        try {
            const response = await fetch('/api/queue/stats');
            const data = await response.json();
            setQueueStats(data.stats);
            setJobs(data.recent_jobs);
        } catch (error) {
            console.error('Erro ao buscar estatísticas:', error);
        } finally {
            setIsLoading(false);
        }
    };
    
    const addBatchJob = async () => {
        const channels = [
            'https://youtube.com/channel1',
            'https://youtube.com/channel2'
        ];
        
        try {
            await fetch('/api/queue/add-batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    channels: channels,
                    max_videos_per_channel: 5,
                    priority: 8
                })
            });
            
            fetchQueueStats(); // Atualizar stats
        } catch (error) {
            console.error('Erro ao adicionar batch:', error);
        }
    };
    
    return (
        <div className="queue-dashboard">
            <div className="stats-grid">
                <div className="stat-card pending">
                    <h3>Pendentes</h3>
                    <span className="stat-number">{queueStats.pending}</span>
                </div>
                <div className="stat-card processing">
                    <h3>Processando</h3>
                    <span className="stat-number">{queueStats.processing}</span>
                </div>
                <div className="stat-card completed">
                    <h3>Concluídos</h3>
                    <span className="stat-number">{queueStats.completed}</span>
                </div>
                <div className="stat-card failed">
                    <h3>Falharam</h3>
                    <span className="stat-number">{queueStats.failed}</span>
                </div>
            </div>
            
            <div className="queue-controls">
                <button onClick={addBatchJob} className="btn-primary">
                    Adicionar Batch de Canais
                </button>
            </div>
            
            <div className="jobs-list">
                <h3>Jobs Recentes</h3>
                {jobs.map(job => (
                    <JobCard key={job.id} job={job} />
                ))}
            </div>
        </div>
    );
};

const JobCard = ({ job }) => {
    const getStatusColor = (status) => {
        switch(status) {
            case 'pending': return 'orange';
            case 'processing': return 'blue';
            case 'completed': return 'green';
            case 'failed': return 'red';
            default: return 'gray';
        }
    };
    
    return (
        <div className="job-card">
            <div className="job-header">
                <span className="job-id">{job.id}</span>
                <span 
                    className="job-status" 
                    style={{ color: getStatusColor(job.status) }}
                >
                    {job.status}
                </span>
            </div>
            <div className="job-details">
                <p><strong>Tipo:</strong> {job.type}</p>
                <p><strong>Criado:</strong> {new Date(job.created_at).toLocaleString()}</p>
                {job.completed_at && (
                    <p><strong>Concluído:</strong> {new Date(job.completed_at).toLocaleString()}</p>
                )}
            </div>
        </div>
    );
};

export default QueueDashboard;
```

## 3. Sistema de Canais Monitorados

### 3.1 Monitor de Canais

**Implementação Backend:**
```python
# backend/services/channel_monitor.py
import asyncio
from datetime import datetime, timedelta
from .youtube_service import YouTubeService
from .database import Database

class ChannelMonitor:
    def __init__(self):
        self.youtube_service = YouTubeService()
        self.db = Database()
        self.is_monitoring = False
        
    async def start_monitoring(self):
        self.is_monitoring = True
        print("Monitoramento de canais iniciado...")
        
        while self.is_monitoring:
            try:
                channels = await self.get_monitored_channels()
                
                for channel in channels:
                    await self.check_channel_updates(channel)
                    
                await asyncio.sleep(300)  # Verificar a cada 5 minutos
                
            except Exception as e:
                print(f"Erro no monitoramento: {e}")
                await asyncio.sleep(60)
                
    async def check_channel_updates(self, channel):
        try:
            # Buscar vídeos recentes
            recent_videos = await self.youtube_service.get_recent_videos(
                channel['channel_id'],
                since=channel['last_check']
            )
            
            if recent_videos:
                # Analisar vídeos para relevância
                relevant_videos = await self.analyze_relevance(
                    recent_videos, 
                    channel['criteria']
                )
                
                if relevant_videos:
                    # Adicionar à fila de processamento
                    await self.queue_videos_for_processing(
                        relevant_videos, 
                        channel
                    )
                    
                    # Notificar usuário
                    await self.send_notification(
                        channel['user_id'],
                        f"Encontrados {len(relevant_videos)} vídeos relevantes em {channel['name']}"
                    )
                    
            # Atualizar timestamp da última verificação
            await self.update_last_check(channel['id'])
            
        except Exception as e:
            print(f"Erro ao verificar canal {channel['name']}: {e}")
            
    async def analyze_relevance(self, videos, criteria):
        relevant = []
        
        for video in videos:
            score = 0
            
            # Verificar critérios de views
            if video['view_count'] >= criteria.get('min_views', 1000):
                score += 1
                
            # Verificar palavras-chave
            keywords = criteria.get('keywords', [])
            title_lower = video['title'].lower()
            
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    score += 2
                    
            # Verificar duração
            duration = video.get('duration', 0)
            if criteria.get('min_duration', 0) <= duration <= criteria.get('max_duration', 3600):
                score += 1
                
            # Verificar engagement rate
            engagement = (video.get('like_count', 0) + video.get('comment_count', 0)) / max(video.get('view_count', 1), 1)
            if engagement >= criteria.get('min_engagement', 0.01):
                score += 1
                
            if score >= criteria.get('min_score', 2):
                video['relevance_score'] = score
                relevant.append(video)
                
        return relevant
        
    async def queue_videos_for_processing(self, videos, channel):
        from .queue_manager import QueueManager
        queue_manager = QueueManager()
        
        for video in videos:
            await queue_manager.add_job({
                'type': 'generate_video',
                'video_data': video,
                'channel_data': channel,
                'priority': channel.get('priority', 5),
                'auto_process': channel.get('auto_process', False)
            })
```

### 3.2 Interface de Configuração

**Componente React:**
```jsx
// frontend/src/components/ChannelMonitorConfig.jsx
const ChannelMonitorConfig = ({ channel, onSave }) => {
    const [criteria, setCriteria] = useState({
        min_views: 1000,
        keywords: [],
        min_duration: 300, // 5 minutos
        max_duration: 1800, // 30 minutos
        min_engagement: 0.01,
        min_score: 2
    });
    
    const [monitoring, setMonitoring] = useState({
        enabled: false,
        check_interval: 300, // 5 minutos
        auto_process: false,
        priority: 5
    });
    
    const handleSave = async () => {
        const config = {
            channel_id: channel.id,
            criteria: criteria,
            monitoring: monitoring
        };
        
        try {
            await fetch('/api/channels/monitor/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            
            onSave(config);
        } catch (error) {
            console.error('Erro ao salvar configuração:', error);
        }
    };
    
    return (
        <div className="monitor-config">
            <h3>Configuração de Monitoramento</h3>
            
            <div className="criteria-section">
                <h4>Critérios de Relevância</h4>
                
                <div className="form-group">
                    <label>Views Mínimas:</label>
                    <input 
                        type="number" 
                        value={criteria.min_views}
                        onChange={(e) => setCriteria({...criteria, min_views: parseInt(e.target.value)})}
                    />
                </div>
                
                <div className="form-group">
                    <label>Palavras-chave (separadas por vírgula):</label>
                    <input 
                        type="text" 
                        value={criteria.keywords.join(', ')}
                        onChange={(e) => setCriteria({...criteria, keywords: e.target.value.split(', ')})}
                    />
                </div>
                
                <div className="form-group">
                    <label>Duração Mínima (segundos):</label>
                    <input 
                        type="number" 
                        value={criteria.min_duration}
                        onChange={(e) => setCriteria({...criteria, min_duration: parseInt(e.target.value)})}
                    />
                </div>
                
                <div className="form-group">
                    <label>Duração Máxima (segundos):</label>
                    <input 
                        type="number" 
                        value={criteria.max_duration}
                        onChange={(e) => setCriteria({...criteria, max_duration: parseInt(e.target.value)})}
                    />
                </div>
            </div>
            
            <div className="monitoring-section">
                <h4>Configurações de Monitoramento</h4>
                
                <div className="form-group">
                    <label>
                        <input 
                            type="checkbox" 
                            checked={monitoring.enabled}
                            onChange={(e) => setMonitoring({...monitoring, enabled: e.target.checked})}
                        />
                        Habilitar Monitoramento
                    </label>
                </div>
                
                <div className="form-group">
                    <label>
                        <input 
                            type="checkbox" 
                            checked={monitoring.auto_process}
                            onChange={(e) => setMonitoring({...monitoring, auto_process: e.target.checked})}
                        />
                        Processamento Automático
                    </label>
                </div>
                
                <div className="form-group">
                    <label>Prioridade (1-10):</label>
                    <input 
                        type="number" 
                        min="1" 
                        max="10"
                        value={monitoring.priority}
                        onChange={(e) => setMonitoring({...monitoring, priority: parseInt(e.target.value)})}
                    />
                </div>
            </div>
            
            <button onClick={handleSave} className="btn-primary">
                Salvar Configuração
            </button>
        </div>
    );
};
```

## 4. Otimizações de Performance

### 4.1 Cache Inteligente

**Sistema de Cache Redis:**
```python
# backend/services/cache_service.py
import redis
import json
import hashlib
from datetime import timedelta

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=1)
        
    def generate_key(self, prefix, data):
        # Gerar chave única baseada nos dados
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
        
    async def get_or_set(self, key, fetch_function, ttl=3600):
        # Tentar buscar do cache
        cached_data = self.redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
            
        # Se não encontrou, executar função e cachear
        data = await fetch_function()
        self.redis_client.setex(key, ttl, json.dumps(data))
        return data
        
    async def cache_video_metadata(self, video_url, metadata):
        key = self.generate_key("video_meta", {"url": video_url})
        self.redis_client.setex(key, 86400, json.dumps(metadata))  # 24h TTL
        
    async def get_cached_video_metadata(self, video_url):
        key = self.generate_key("video_meta", {"url": video_url})
        cached = self.redis_client.get(key)
        return json.loads(cached) if cached else None
```

### 4.2 Processamento Paralelo

**Implementação com AsyncIO:**
```python
# backend/services/parallel_processor.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ParallelProcessor:
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    async def process_multiple_videos(self, video_urls):
        # Processar múltiplos vídeos em paralelo
        tasks = []
        
        for url in video_urls:
            task = asyncio.create_task(self.process_single_video(url))
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar resultados válidos
        valid_results = [r for r in results if not isinstance(r, Exception)]
        errors = [r for r in results if isinstance(r, Exception)]
        
        return valid_results, errors
        
    async def process_single_video(self, video_url):
        # Processar um vídeo individual
        try:
            # Extração de metadados
            metadata_task = asyncio.create_task(self.extract_metadata(video_url))
            
            # Geração de título
            title_task = asyncio.create_task(self.generate_title(video_url))
            
            # Geração de premissa
            premise_task = asyncio.create_task(self.generate_premise(video_url))
            
            # Aguardar todas as tarefas
            metadata, title, premise = await asyncio.gather(
                metadata_task, title_task, premise_task
            )
            
            return {
                'url': video_url,
                'metadata': metadata,
                'title': title,
                'premise': premise
            }
            
        except Exception as e:
            print(f"Erro ao processar {video_url}: {e}")
            raise e
```

## 5. Métricas e Monitoramento

### 5.1 Sistema de Analytics

**Implementação:**
```python
# backend/services/analytics_service.py
from datetime import datetime, timedelta
import json

class AnalyticsService:
    def __init__(self):
        self.db = Database()
        
    async def track_event(self, event_type, data):
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'user_id': data.get('user_id')
        }
        
        await self.db.insert('analytics_events', event)
        
    async def get_performance_metrics(self, days=7):
        start_date = datetime.now() - timedelta(days=days)
        
        metrics = {
            'videos_processed': await self.count_events('video_completed', start_date),
            'avg_processing_time': await self.avg_processing_time(start_date),
            'success_rate': await self.calculate_success_rate(start_date),
            'queue_performance': await self.queue_metrics(start_date)
        }
        
        return metrics
        
    async def count_events(self, event_type, since):
        query = """
        SELECT COUNT(*) FROM analytics_events 
        WHERE type = %s AND timestamp >= %s
        """
        result = await self.db.fetch_one(query, (event_type, since))
        return result[0] if result else 0
        
    async def avg_processing_time(self, since):
        query = """
        SELECT AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) 
        FROM video_jobs 
        WHERE created_at >= %s AND status = 'completed'
        """
        result = await self.db.fetch_one(query, (since,))
        return result[0] if result else 0
```

### 5.2 Dashboard de Analytics

**Interface React:**
```jsx
// frontend/src/pages/Analytics.jsx
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Analytics = () => {
    const [metrics, setMetrics] = useState(null);
    const [timeRange, setTimeRange] = useState(7);
    
    useEffect(() => {
        fetchMetrics();
    }, [timeRange]);
    
    const fetchMetrics = async () => {
        try {
            const response = await fetch(`/api/analytics/metrics?days=${timeRange}`);
            const data = await response.json();
            setMetrics(data);
        } catch (error) {
            console.error('Erro ao buscar métricas:', error);
        }
    };
    
    if (!metrics) return <div>Carregando...</div>;
    
    return (
        <div className="analytics-dashboard">
            <div className="time-selector">
                <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
                    <option value={7}>Últimos 7 dias</option>
                    <option value={30}>Últimos 30 dias</option>
                    <option value={90}>Últimos 90 dias</option>
                </select>
            </div>
            
            <div className="metrics-grid">
                <MetricCard 
                    title="Vídeos Processados" 
                    value={metrics.videos_processed}
                    icon="📹"
                />
                <MetricCard 
                    title="Tempo Médio" 
                    value={`${Math.round(metrics.avg_processing_time / 60)} min`}
                    icon="⏱️"
                />
                <MetricCard 
                    title="Taxa de Sucesso" 
                    value={`${Math.round(metrics.success_rate * 100)}%`}
                    icon="✅"
                />
                <MetricCard 
                    title="Jobs na Fila" 
                    value={metrics.queue_performance.pending}
                    icon="📋"
                />
            </div>
            
            <div className="charts-section">
                <div className="chart-container">
                    <h3>Processamento ao Longo do Tempo</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={metrics.daily_stats}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Line type="monotone" dataKey="videos" stroke="#8884d8" />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

const MetricCard = ({ title, value, icon }) => (
    <div className="metric-card">
        <div className="metric-icon">{icon}</div>
        <div className="metric-content">
            <h4>{title}</h4>
            <span className="metric-value">{value}</span>
        </div>
    </div>
);

export default Analytics;
```

Esta especificação técnica fornece a base completa para implementar todas as melhorias identificadas no Auto Video Producer, com foco em escalabilidade, performance e automação avançada.