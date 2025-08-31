"""
🎬 Auto Video Producer - Backend API
Sistema completo de produção automática de vídeos usando IA
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
import logging
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'auto-video-producer-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auto_video_producer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Configurar CORS
CORS(app, 
     origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5174'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True)

# Handler específico para requisições OPTIONS (preflight)
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

# Inicializar banco de dados
from database import db, ImageQueue, ScriptPrompt
db.init_app(app)

# Criar diretórios necessários
os.makedirs('uploads', exist_ok=True)
os.makedirs('outputs', exist_ok=True)
os.makedirs('temp', exist_ok=True)

# ================================
# 📊 MODELOS DO BANCO DE DADOS
# ================================

class APIConfig(db.Model):
    """Configurações de APIs"""
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(50), unique=True, nullable=False)
    api_key = db.Column(db.Text, nullable=True)
    is_configured = db.Column(db.Boolean, default=False)
    usage_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'api_name': self.api_name,
            'is_configured': self.is_configured,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat()
        }

class Channel(db.Model):
    """Canais monitorados"""
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    channel_id = db.Column(db.String(100), unique=True, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    video_style = db.Column(db.String(50), default='motivational')
    max_videos_per_day = db.Column(db.Integer, default=2)
    min_views_threshold = db.Column(db.Integer, default=1000)
    total_videos_produced = db.Column(db.Integer, default=0)
    last_production = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'channel_id': self.channel_id,
            'url': self.url,
            'is_active': self.is_active,
            'video_style': self.video_style,
            'max_videos_per_day': self.max_videos_per_day,
            'min_views_threshold': self.min_views_threshold,
            'total_videos_produced': self.total_videos_produced,
            'last_production': self.last_production.isoformat() if self.last_production else None,
            'created_at': self.created_at.isoformat()
        }

class Pipeline(db.Model):
    """Pipelines de produção"""
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    pipeline_id = db.Column(db.String(100), unique=True, nullable=False)  # UUID consistente
    display_name = db.Column(db.String(50), unique=True, nullable=False)  # Nome amigável (ex: 2025-01-31-001)
    title = db.Column(db.String(500), nullable=False)
    channel_url = db.Column(db.String(500), nullable=True)  # URL do canal processado
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=True)
    status = db.Column(db.String(50), default='pending')
    progress = db.Column(db.Integer, default=0)
    current_step = db.Column(db.String(200), nullable=True)
    video_style = db.Column(db.String(50), default='motivational')
    target_duration = db.Column(db.Integer, default=300)  # segundos
    
    # Configuração completa da pipeline
    config_json = db.Column(db.Text, nullable=True)  # JSON da configuração completa
    agent_config = db.Column(db.Text, nullable=True)  # JSON da configuração do agente
    
    # Resultados de cada step
    extraction_results = db.Column(db.Text, nullable=True)  # JSON dos títulos extraídos
    titles_results = db.Column(db.Text, nullable=True)  # JSON dos títulos gerados
    premises_results = db.Column(db.Text, nullable=True)  # JSON das premissas
    scripts_results = db.Column(db.Text, nullable=True)  # JSON dos roteiros
    tts_results = db.Column(db.Text, nullable=True)  # JSON dos resultados TTS
    images_results = db.Column(db.Text, nullable=True)  # JSON das imagens
    video_results = db.Column(db.Text, nullable=True)  # JSON do vídeo final
    
    # Arquivos gerados
    script_content = db.Column(db.Text, nullable=True)
    audio_file_path = db.Column(db.String(500), nullable=True)
    video_file_path = db.Column(db.String(500), nullable=True)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    estimated_completion = db.Column(db.DateTime, nullable=True)
    
    # Controle de erros
    error_message = db.Column(db.Text, nullable=True)
    warnings = db.Column(db.Text, nullable=True)  # JSON de warnings
    
    def to_dict(self):
        """Converter para dicionário com todos os dados"""
        # Parse dos resultados JSON
        try:
            config = json.loads(self.config_json) if self.config_json else {}
            agent_config = json.loads(self.agent_config) if self.agent_config else {}
            extraction_results = json.loads(self.extraction_results) if self.extraction_results else {}
            titles_results = json.loads(self.titles_results) if self.titles_results else {}
            premises_results = json.loads(self.premises_results) if self.premises_results else {}
            scripts_results = json.loads(self.scripts_results) if self.scripts_results else {}
            tts_results = json.loads(self.tts_results) if self.tts_results else {}
            images_results = json.loads(self.images_results) if self.images_results else {}
            video_results = json.loads(self.video_results) if self.video_results else {}
            warnings = json.loads(self.warnings) if self.warnings else []
        except Exception as e:
            logger.error(f"Erro ao fazer parse dos JSONs da pipeline {self.pipeline_id}: {e}")
            config = {}
            agent_config = {}
            extraction_results = {}
            titles_results = {}
            premises_results = {}
            scripts_results = {}
            tts_results = {}
            images_results = {}
            video_results = {}
            warnings = []
        
        return {
            'id': self.id,
            'pipeline_id': self.pipeline_id,
            'display_name': self.display_name,
            'title': self.title,
            'channel_url': self.channel_url,
            'channel_id': self.channel_id,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'video_style': self.video_style,
            'target_duration': self.target_duration,
            'config': config,
            'agent': agent_config,
            'results': {
                'extraction': extraction_results,
                'titles': titles_results,
                'premises': premises_results,
                'scripts': scripts_results,
                'tts': tts_results,
                'images': images_results,
                'video': video_results
            },
            'steps': self._get_steps_status(),
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'error_message': self.error_message,
            'warnings': warnings
        }
    
    def _get_steps_status(self):
        """Gerar status dos steps baseado nos resultados"""
        steps = {
            'extraction': {
                'status': 'completed' if self.extraction_results else 'pending',
                'result': json.loads(self.extraction_results) if self.extraction_results else None
            },
            'titles': {
                'status': 'completed' if self.titles_results else 'pending', 
                'result': json.loads(self.titles_results) if self.titles_results else None
            },
            'premises': {
                'status': 'completed' if self.premises_results else 'pending',
                'result': json.loads(self.premises_results) if self.premises_results else None
            },
            'scripts': {
                'status': 'completed' if self.scripts_results else 'pending',
                'result': json.loads(self.scripts_results) if self.scripts_results else None
            },
            'tts': {
                'status': 'completed' if self.tts_results else 'pending',
                'result': json.loads(self.tts_results) if self.tts_results else None
            },
            'images': {
                'status': 'completed' if self.images_results else 'pending',
                'result': json.loads(self.images_results) if self.images_results else None
            },
            'video': {
                'status': 'completed' if self.video_results else 'pending',
                'result': json.loads(self.video_results) if self.video_results else None
            }
        }
        return steps
    
    @staticmethod
    def generate_display_name():
        """Gerar nome amigável único no formato YYYY-MM-DD-XXX"""
        from sqlalchemy import func
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Buscar o último número do dia
        last_pipeline = Pipeline.query.filter(
            Pipeline.display_name.like(f"{today}-%")
        ).order_by(Pipeline.display_name.desc()).first()
        
        if last_pipeline:
            try:
                last_number = int(last_pipeline.display_name.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"{today}-{next_number:03d}"

class PipelineLog(db.Model):
    """Logs persistentes das pipelines"""
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    pipeline_id = db.Column(db.String(100), db.ForeignKey('pipeline.pipeline_id'), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # info, warning, error, success
    step = db.Column(db.String(50), nullable=True)  # extraction, titles, etc.
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text, nullable=True)  # JSON com dados extras
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'pipeline_id': self.pipeline_id,
            'level': self.level,
            'step': self.step,
            'message': self.message,
            'data': json.loads(self.data) if self.data else None,
            'timestamp': self.timestamp.isoformat()
        }

class Video(db.Model):
    """Vídeos produzidos"""
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=True)
    pipeline_id = db.Column(db.Integer, db.ForeignKey('pipeline.id'), nullable=True)
    duration = db.Column(db.Float, nullable=False)  # segundos (mudado para Float para suportar decimais)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # bytes
    video_style = db.Column(db.String(50), default='motivational')
    resolution = db.Column(db.String(20), default='1920x1080')  # Novo campo
    fps = db.Column(db.Integer, default=30)  # Novo campo
    status = db.Column(db.String(50), default='completed')  # Novo campo
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'channel_id': self.channel_id,
            'pipeline_id': self.pipeline_id,
            'duration': self.duration,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'video_style': self.video_style,
            'resolution': self.resolution,
            'fps': self.fps,
            'status': self.status,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat()
        }

class AutomationLog(db.Model):
    """Logs de automações"""
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    automation_type = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), default='pending')
    input_data = db.Column(db.Text, nullable=True)
    output_data = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    agent_used = db.Column(db.String(50), nullable=True)
    processing_time = db.Column(db.Float, nullable=True)  # segundos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'automation_type': self.automation_type,
            'title': self.title,
            'status': self.status,
            'agent_used': self.agent_used,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }

# Modelos ImageQueue e ScriptPrompt movidos para database.py

# ================================
# 🏠 ROTAS PRINCIPAIS
# ================================

@app.route('/')
def index():
    """Página inicial da API"""
    return jsonify({
        'message': '🎬 Auto Video Producer API',
        'version': '1.0.0',
        'status': 'online',
        'endpoints': {
            'system': '/api/system/status',
            'channels': '/api/channels',
            'pipelines': '/api/pipelines',
            'videos': '/api/videos',
            'automations': '/api/automations',
            'settings': '/api/settings',
            'images': '/api/images',
            'image_queue': '/api/image-queue'
        }
    })

@app.route('/api/system/status')
def system_status():
    """Status do sistema"""
    try:
        # Verificar APIs configuradas
        apis = APIConfig.query.all()
        apis_configured = {api.api_name: api.is_configured for api in apis}
        
        # Estatísticas básicas
        total_channels = Channel.query.count()
        active_channels = Channel.query.filter_by(is_active=True).count()
        total_pipelines = Pipeline.query.count()
        active_pipelines = Pipeline.query.filter(Pipeline.status.in_(['pending', 'processing'])).count()
        total_videos = Video.query.count()
        
        return jsonify({
            'success': True,
            'data': {
                'status': 'online',
                'ready_for_production': any(apis_configured.values()),
                'apis_configured': apis_configured,
                'statistics': {
                    'total_channels': total_channels,
                    'active_channels': active_channels,
                    'total_pipelines': total_pipelines,
                    'active_pipelines': active_pipelines,
                    'total_videos': total_videos
                }
            }
        })
    except Exception as e:
        logger.error(f"Erro ao obter status do sistema: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ================================
# 🚀 INICIALIZAÇÃO
# ================================

def init_database():
    """Inicializar banco de dados"""
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        
        # Criar configurações padrão de APIs se não existirem
        default_apis = [
            'openai', 'gemini', 'claude', 'elevenlabs', 
            'rapidapi', 'together', 'openrouter'
        ]
        
        for api_name in default_apis:
            existing_api = APIConfig.query.filter_by(api_name=api_name).first()
            if not existing_api:
                api_config = APIConfig(api_name=api_name)
                db.session.add(api_config)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.warning(f"Erro ao criar configurações padrão: {e}")
            
        logger.info("✅ Banco de dados inicializado com sucesso!")

# Importar e registrar rotas
def register_blueprints():
    """Registrar blueprints das rotas"""
    try:
        from routes.automations import automations_bp, load_rapidapi_keys, load_gemini_keys
        from routes.premise import premise_bp
        from routes.scripts import scripts_bp
        from routes.workflow import workflow_bp
        from routes.channels import channels_bp
        from routes.pipelines import pipelines_bp
        from routes.pipeline_complete import pipeline_complete_bp
        from routes.videos import videos_bp
        from routes.settings import settings_bp
        from routes.system import system_bp
        from routes.tests import tests_bp
        from routes.images import images_bp
        from routes.image_queue import image_queue_bp
        from routes.prompts_config import prompts_config_bp

        # Carregar chaves na inicialização
        load_rapidapi_keys()
        logger.info("✅ Chaves RapidAPI carregadas na inicialização!")
        
        load_gemini_keys()
        logger.info("✅ Chaves Gemini carregadas na inicialização!")

        app.register_blueprint(automations_bp, url_prefix='/api/automations')
        app.register_blueprint(premise_bp, url_prefix='/api/premise')
        app.register_blueprint(scripts_bp, url_prefix='/api/scripts')
        app.register_blueprint(workflow_bp, url_prefix='/api/workflow')
        app.register_blueprint(channels_bp, url_prefix='/api/channels')
        app.register_blueprint(pipelines_bp, url_prefix='/api/pipelines')
        app.register_blueprint(pipeline_complete_bp, url_prefix='/api/pipeline')
        app.register_blueprint(videos_bp, url_prefix='/api/videos')
        app.register_blueprint(settings_bp, url_prefix='/api/settings')
        app.register_blueprint(system_bp, url_prefix='/api/system')
        app.register_blueprint(tests_bp, url_prefix='/api/tests')
        app.register_blueprint(images_bp, url_prefix='/api/images')
        app.register_blueprint(image_queue_bp, url_prefix='/api/image-queue')
        app.register_blueprint(prompts_config_bp, url_prefix='/api')

        logger.info("✅ Rotas registradas com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao registrar rotas: {e}")

# Registrar blueprints apenas se executado diretamente
if __name__ == '__main__':
    init_database()
    register_blueprints()
    
    # Adicionar logs iniciais ao sistema em tempo real
    try:
        from routes.system import add_real_time_log
        add_real_time_log("🎬 Auto Video Producer Backend iniciado!", "success", "system")
        add_real_time_log("📡 API disponível em: http://localhost:5000", "info", "system")
        add_real_time_log("🌐 Frontend disponível em: http://localhost:5173", "info", "system")
        add_real_time_log("🔧 Sistema de logs em tempo real ativo", "info", "system")
    except ImportError:
        pass

    logger.info("🎬 Auto Video Producer Backend iniciado!")
    logger.info("📡 API disponível em: http://localhost:5000")
    logger.info("🌐 Frontend disponível em: http://localhost:5173")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
