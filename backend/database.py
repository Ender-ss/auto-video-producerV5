"""🗄️ Database Configuration
Configuração centralizada do banco de dados para evitar importações circulares
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Instância global do SQLAlchemy
db = SQLAlchemy()

class ImageQueue(db.Model):
    """Fila de geração de imagens"""
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    prompts = db.Column(db.Text, nullable=False)  # JSON array de prompts
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    current_prompt_index = db.Column(db.Integer, default=0)
    total_prompts = db.Column(db.Integer, nullable=False)
    provider = db.Column(db.String(50), default='pollinations')
    model = db.Column(db.String(100), default='flux')
    style = db.Column(db.String(200), default='cinematic, high detail, 4k')
    format_size = db.Column(db.String(20), default='1024x1024')
    quality = db.Column(db.String(20), default='standard')
    generated_images = db.Column(db.Text, nullable=True)  # JSON array de URLs
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'prompts': json.loads(self.prompts) if self.prompts else [],
            'status': self.status,
            'progress': self.progress,
            'current_prompt_index': self.current_prompt_index,
            'total_prompts': self.total_prompts,
            'provider': self.provider,
            'model': self.model,
            'style': self.style,
            'format_size': self.format_size,
            'quality': self.quality,
            'generated_images': json.loads(self.generated_images) if self.generated_images else [],
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class ScriptPrompt(db.Model):
    """Prompts gerados automaticamente a partir de roteiros"""
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    script_content = db.Column(db.Text, nullable=False)
    generated_prompts = db.Column(db.Text, nullable=False)  # JSON array
    total_prompts = db.Column(db.Integer, nullable=False)
    provider = db.Column(db.String(50), default='pollinations')
    model = db.Column(db.String(100), default='flux')
    style = db.Column(db.String(200), default='cinematic, high detail, 4k')
    format_size = db.Column(db.String(20), default='1024x1024')
    quality = db.Column(db.String(20), default='standard')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'script_content': self.script_content,
            'generated_prompts': json.loads(self.generated_prompts) if self.generated_prompts else [],
            'total_prompts': self.total_prompts,
            'provider': self.provider,
            'model': self.model,
            'style': self.style,
            'format_size': self.format_size,
            'quality': self.quality,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }