"""🔄 Checkpoint Service
Serviço de checkpoints para salvar e recuperar estado da pipeline
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class CheckpointService:
    """Serviço de gerenciamento de checkpoints"""
    
    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
        self.checkpoints_dir = os.path.join('checkpoints')
        self.checkpoint_file = os.path.join(self.checkpoints_dir, f'checkpoint_{pipeline_id}.json')
        
        # Criar diretório de checkpoints
        os.makedirs(self.checkpoints_dir, exist_ok=True)
    
    def save_checkpoint(self, step: str, results: Dict[str, Any], 
                       config: Dict[str, Any], progress: Dict[str, int]) -> bool:
        """Salvar checkpoint do estado atual"""
        try:
            checkpoint_data = {
                'pipeline_id': self.pipeline_id,
                'timestamp': datetime.utcnow().isoformat(),
                'current_step': step,
                'completed_steps': list(results.keys()),
                'results': results,
                'config': config,
                'progress': progress,
                'version': '1.0'
            }
            
            # Salvar checkpoint
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f'Checkpoint salvo para pipeline {self.pipeline_id} na etapa {step}')
            return True
            
        except Exception as e:
            logger.error(f'Erro ao salvar checkpoint: {str(e)}')
            return False
    
    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Carregar checkpoint existente"""
        try:
            if not os.path.exists(self.checkpoint_file):
                return None
            
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            # Verificar se o checkpoint é válido
            if checkpoint_data.get('pipeline_id') != self.pipeline_id:
                logger.warning(f'Pipeline ID no checkpoint não corresponde: {checkpoint_data.get("pipeline_id")} != {self.pipeline_id}')
                return None
            
            logger.info(f'Checkpoint carregado para pipeline {self.pipeline_id}')
            return checkpoint_data
            
        except Exception as e:
            logger.error(f'Erro ao carregar checkpoint: {str(e)}')
            return None
    
    def has_checkpoint(self) -> bool:
        """Verificar se existe checkpoint para esta pipeline"""
        return os.path.exists(self.checkpoint_file)
    
    def delete_checkpoint(self) -> bool:
        """Deletar checkpoint após conclusão bem-sucedida"""
        try:
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
                logger.info(f'Checkpoint removido para pipeline {self.pipeline_id}')
            return True
            
        except Exception as e:
            logger.error(f'Erro ao remover checkpoint: {str(e)}')
            return False
    
    def get_next_step(self, completed_steps: List[str]) -> Optional[str]:
        """Determinar próxima etapa baseada nas etapas concluídas"""
        # Ordem das etapas da pipeline
        pipeline_steps = [
            'titles',
            'premises', 
            'scripts',
            'tts',
            'images',
            'video'
        ]
        
        for step in pipeline_steps:
            if step not in completed_steps:
                return step
        
        return None  # Todas as etapas concluídas
    
    def validate_checkpoint_integrity(self, checkpoint_data: Dict[str, Any]) -> bool:
        """Validar integridade do checkpoint"""
        try:
            # Verificar campos obrigatórios
            required_fields = ['pipeline_id', 'timestamp', 'current_step', 'results', 'config']
            for field in required_fields:
                if field not in checkpoint_data:
                    logger.error(f'Campo obrigatório ausente no checkpoint: {field}')
                    return False
            
            # Verificar se arquivos referenciados ainda existem
            results = checkpoint_data.get('results', {})
            
            # Verificar arquivo de áudio TTS
            if 'tts' in results:
                audio_path = results['tts'].get('audio_file_path')
                if audio_path and not os.path.exists(audio_path):
                    logger.warning(f'Arquivo de áudio não encontrado: {audio_path}')
                    return False
            
            # Verificar arquivos de imagem
            if 'images' in results:
                images = results['images'].get('generated_images', [])
                for img in images:
                    img_path = img.get('file_path')
                    if img_path and not os.path.exists(img_path):
                        logger.warning(f'Arquivo de imagem não encontrado: {img_path}')
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f'Erro na validação do checkpoint: {str(e)}')
            return False
    
    def create_recovery_report(self, checkpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Criar relatório de recuperação"""
        completed_steps = checkpoint_data.get('completed_steps', [])
        next_step = self.get_next_step(completed_steps)
        
        return {
            'pipeline_id': self.pipeline_id,
            'recovery_timestamp': datetime.utcnow().isoformat(),
            'checkpoint_timestamp': checkpoint_data.get('timestamp'),
            'completed_steps': completed_steps,
            'next_step': next_step,
            'steps_remaining': len(['titles', 'premises', 'scripts', 'tts', 'images', 'video']) - len(completed_steps),
            'can_resume': next_step is not None,
            'integrity_valid': self.validate_checkpoint_integrity(checkpoint_data)
        }
    
    @staticmethod
    def list_all_checkpoints() -> List[Dict[str, Any]]:
        """Listar todos os checkpoints disponíveis"""
        checkpoints = []
        checkpoints_dir = 'checkpoints'
        
        if not os.path.exists(checkpoints_dir):
            return checkpoints
        
        try:
            for filename in os.listdir(checkpoints_dir):
                if filename.startswith('checkpoint_') and filename.endswith('.json'):
                    filepath = os.path.join(checkpoints_dir, filename)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            checkpoint_data = json.load(f)
                        
                        checkpoints.append({
                            'filename': filename,
                            'pipeline_id': checkpoint_data.get('pipeline_id'),
                            'timestamp': checkpoint_data.get('timestamp'),
                            'current_step': checkpoint_data.get('current_step'),
                            'completed_steps': checkpoint_data.get('completed_steps', []),
                            'file_size': os.path.getsize(filepath)
                        })
                        
                    except Exception as e:
                        logger.error(f'Erro ao ler checkpoint {filename}: {str(e)}')
                        continue
            
        except Exception as e:
            logger.error(f'Erro ao listar checkpoints: {str(e)}')
        
        return checkpoints
    
    @staticmethod
    def cleanup_old_checkpoints(max_age_hours: int = 24) -> int:
        """Limpar checkpoints antigos"""
        cleaned_count = 0
        checkpoints_dir = 'checkpoints'
        
        if not os.path.exists(checkpoints_dir):
            return cleaned_count
        
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(checkpoints_dir):
                if filename.startswith('checkpoint_') and filename.endswith('.json'):
                    filepath = os.path.join(checkpoints_dir, filename)
                    
                    try:
                        file_age = current_time - os.path.getmtime(filepath)
                        
                        if file_age > max_age_seconds:
                            os.remove(filepath)
                            cleaned_count += 1
                            logger.info(f'Checkpoint antigo removido: {filename}')
                            
                    except Exception as e:
                        logger.error(f'Erro ao remover checkpoint {filename}: {str(e)}')
                        continue
            
        except Exception as e:
            logger.error(f'Erro na limpeza de checkpoints: {str(e)}')
        
        return cleaned_count