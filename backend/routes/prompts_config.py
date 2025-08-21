from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime
import shutil

prompts_config_bp = Blueprint('prompts_config', __name__)

# Caminho para o arquivo de configuração de prompts
PROMPTS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'prompts_config.json')
PROMPTS_BACKUP_DIR = os.path.join(os.path.dirname(__file__), '..', 'config', 'prompts_backups')

# Criar diretórios se não existirem
os.makedirs(os.path.dirname(PROMPTS_CONFIG_FILE), exist_ok=True)
os.makedirs(PROMPTS_BACKUP_DIR, exist_ok=True)

# Configuração padrão de prompts
DEFAULT_PROMPTS = {
    "titles": {
        "name": "Geração de Títulos",
        "description": "Prompt usado pelo Gemini para gerar títulos alternativos",
        "prompt": """Você é um especialista em criação de conteúdo para YouTube. Sua tarefa é analisar o título original de um vídeo e criar versões alternativas que sejam:

1. Mais atrativas e chamativas
2. Otimizadas para SEO
3. Que despertem curiosidade
4. Mantendo a essência do conteúdo original

Título original: {original_title}

Crie 5 versões alternativas do título, cada uma em uma linha separada. Foque em:
- Usar palavras-chave relevantes
- Criar senso de urgência ou curiosidade
- Manter entre 50-60 caracteres quando possível
- Usar números quando apropriado
- Evitar clickbait excessivo

Títulos alternativos:""",
        "variables": ["original_title"]
    },
    "premises": {
        "name": "Geração de Premissas",
        "description": "Prompt usado pelo Gemini para criar premissas do roteiro",
        "prompt": """Você é um roteirista experiente especializado em conteúdo educativo e envolvente. Sua tarefa é criar premissas sólidas para um roteiro baseado no título fornecido.

Título: {title}

Crie 3 premissas diferentes para este conteúdo, cada uma deve:

1. Definir o objetivo principal do vídeo
2. Identificar o público-alvo
3. Estabelecer o tom e estilo
4. Sugerir a estrutura narrativa
5. Destacar os pontos-chave a serem abordados

Cada premissa deve ter entre 100-150 palavras e ser numerada (1, 2, 3).

Premissas:""",
        "variables": ["title"]
    },
    "scripts": {
        "name": "Geração de Roteiros",
        "description": "Prompt usado para gerar roteiros completos",
        "prompt": """Você é um roteirista profissional especializado em conteúdo para YouTube. Crie um roteiro envolvente e bem estruturado.

Título: {title}
Premissa: {premise}
Número de capítulos: {chapters}
Palavras-alvo: {target_words}

Estruture o roteiro seguindo este formato:

**INTRODUÇÃO** (10% do conteúdo)
- Hook inicial para capturar atenção
- Apresentação do tema
- Preview do que será abordado

**DESENVOLVIMENTO** (80% do conteúdo)
- Divida em {chapters} capítulos claros
- Cada capítulo deve ter título e conteúdo detalhado
- Use transições suaves entre capítulos
- Inclua exemplos práticos quando relevante

**CONCLUSÃO** (10% do conteúdo)
- Resumo dos pontos principais
- Call-to-action
- Encerramento envolvente

Objetivo de palavras: aproximadamente {target_words} palavras

Roteiro:""",
        "variables": ["title", "premise", "chapters", "target_words"]
    },
    "image_prompts": {
        "name": "Geração de Prompts de Imagem",
        "description": "Prompt usado pelo Gemini para criar prompts de imagem a partir do roteiro",
        "prompt": """Você é um especialista em direção de arte e criação de prompts para IA de geração de imagens. Sua tarefa é analisar um trecho de roteiro e criar prompts detalhados para gerar imagens que complementem o conteúdo.

Trecho do roteiro:
{script_segment}

Crie um prompt detalhado para geração de imagem que:

1. Capture a essência visual do conteúdo
2. Seja específico sobre estilo, cores e composição
3. Inclua detalhes técnicos (iluminação, ângulo, etc.)
4. Seja otimizado para IA de geração de imagens
5. Mantenha consistência visual com o tema

Formato do prompt:
- Descrição principal (o que mostrar)
- Estilo visual (fotográfico, ilustração, etc.)
- Cores dominantes
- Composição e enquadramento
- Qualidade e detalhes técnicos

Prompt de imagem:""",
        "variables": ["script_segment"]
    }
}

def load_prompts_config():
    """Carrega a configuração de prompts do arquivo JSON"""
    try:
        if os.path.exists(PROMPTS_CONFIG_FILE):
            with open(PROMPTS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Se não existe, cria com configuração padrão
            save_prompts_config(DEFAULT_PROMPTS)
            return DEFAULT_PROMPTS
    except Exception as e:
        print(f"Erro ao carregar configuração de prompts: {e}")
        return DEFAULT_PROMPTS

def save_prompts_config(config):
    """Salva a configuração de prompts no arquivo JSON"""
    try:
        with open(PROMPTS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar configuração de prompts: {e}")
        return False

def create_backup():
    """Cria backup da configuração atual"""
    try:
        if os.path.exists(PROMPTS_CONFIG_FILE):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(PROMPTS_BACKUP_DIR, f"prompts_backup_{timestamp}.json")
            shutil.copy2(PROMPTS_CONFIG_FILE, backup_file)
            return backup_file
    except Exception as e:
        print(f"Erro ao criar backup: {e}")
    return None

@prompts_config_bp.route('/prompts/config', methods=['GET'])
def get_prompts_config():
    """Retorna a configuração atual de prompts"""
    try:
        config = load_prompts_config()
        return jsonify({
            'success': True,
            'data': config,
            'message': 'Configuração de prompts carregada com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao carregar configuração de prompts'
        }), 500

@prompts_config_bp.route('/prompts/config', methods=['POST'])
def update_prompts_config():
    """Atualiza a configuração de prompts"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos',
                'message': 'É necessário fornecer os dados de configuração'
            }), 400
        
        # Validar estrutura básica
        required_sections = ['titles', 'premises', 'scripts', 'image_prompts']
        for section in required_sections:
            if section not in data:
                return jsonify({
                    'success': False,
                    'error': f'Seção {section} não encontrada',
                    'message': 'Configuração incompleta'
                }), 400
        
        # Criar backup antes de salvar
        backup_file = create_backup()
        
        # Salvar nova configuração
        if save_prompts_config(data):
            return jsonify({
                'success': True,
                'message': 'Configuração de prompts atualizada com sucesso',
                'backup_file': backup_file
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao salvar configuração',
                'message': 'Não foi possível salvar a configuração'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro interno do servidor'
        }), 500

@prompts_config_bp.route('/prompts/config/reset', methods=['POST'])
def reset_prompts_config():
    """Restaura a configuração padrão de prompts"""
    try:
        # Criar backup antes de resetar
        backup_file = create_backup()
        
        # Restaurar configuração padrão
        if save_prompts_config(DEFAULT_PROMPTS):
            return jsonify({
                'success': True,
                'message': 'Configuração restaurada para padrão',
                'backup_file': backup_file,
                'data': DEFAULT_PROMPTS
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao restaurar configuração',
                'message': 'Não foi possível restaurar a configuração padrão'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro interno do servidor'
        }), 500

@prompts_config_bp.route('/prompts/config/validate', methods=['POST'])
def validate_prompt():
    """Valida um prompt específico"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'Prompt não fornecido',
                'message': 'É necessário fornecer o prompt para validação'
            }), 400
        
        prompt = data['prompt']
        variables = data.get('variables', [])
        
        issues = []
        
        # Validações de conteúdo
        if not prompt or not prompt.strip():
            issues.append('Prompt não pode estar vazio')
        
        if prompt and len(prompt) < 10:
            issues.append('Prompt muito curto (mínimo 10 caracteres)')
            
        if prompt and len(prompt) > 5000:
            issues.append('Prompt muito longo (máximo 5000 caracteres)')
        
        # Verificar estrutura do prompt
        if prompt:
            # Verificar se há instruções básicas
            if not any(word in prompt.lower() for word in ['crie', 'gere', 'escreva', 'desenvolva', 'produza']):
                issues.append('Prompt deve conter instruções claras (ex: "crie", "gere", "escreva")')
            
            # Verificar balanceamento de chaves
            open_braces = prompt.count('{')
            close_braces = prompt.count('}')
            if open_braces != close_braces:
                issues.append('Chaves desbalanceadas nas variáveis')
            
            # Verificar variáveis malformadas
            import re
            malformed_vars = re.findall(r'{[^}]*{|{[^}]*$|^[^{]*}', prompt)
            if malformed_vars:
                issues.append('Variáveis malformadas encontradas')
            
            # Verificar se há variáveis vazias
            empty_vars = re.findall(r'{}', prompt)
            if empty_vars:
                issues.append('Variáveis vazias encontradas ({})')
        
        # Validações específicas por tipo de prompt
        prompt_lower = prompt.lower() if prompt else ''
        
        # Para prompts de título
        if any(word in prompt_lower for word in ['título', 'title', 'headline']):
            if 'viral' in prompt_lower and 'engajamento' not in prompt_lower:
                issues.append('Prompts virais devem mencionar engajamento')
        
        # Para prompts de roteiro
        if any(word in prompt_lower for word in ['roteiro', 'script', 'capítulo']):
            if '{chapters}' not in prompt and 'capítulo' in prompt_lower:
                issues.append('Prompts de roteiro com capítulos devem usar a variável {chapters}')
        
        # Para prompts de imagem
        if any(word in prompt_lower for word in ['imagem', 'image', 'visual']):
            if not any(word in prompt_lower for word in ['estilo', 'cor', 'composição', 'lighting']):
                issues.append('Prompts de imagem devem incluir diretrizes visuais')
        
        # Verificar qualidade do prompt
        if prompt and len(prompt.split()) < 5:
            issues.append('Prompt muito simples, adicione mais detalhes')
        
        # Sugestões de melhoria
        suggestions = []
        if prompt and 'por favor' not in prompt_lower and 'please' not in prompt_lower:
            suggestions.append('Considere usar linguagem mais educada')
        
        if prompt and not any(punct in prompt for punct in ['.', '!', '?']):
            suggestions.append('Adicione pontuação para melhor clareza')
        
        return jsonify({
            'success': True,
            'valid': len(issues) == 0,
            'issues': issues,
            'suggestions': suggestions,
            'stats': {
                'character_count': len(prompt) if prompt else 0,
                'word_count': len(prompt.split()) if prompt else 0,
                'variable_count': len(re.findall(r'{[^}]+}', prompt)) if prompt else 0
            },
            'message': 'Validação concluída'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao validar prompt'
        }), 500

@prompts_config_bp.route('/prompts/config/backups', methods=['GET'])
def list_backups():
    """Lista todos os backups disponíveis"""
    try:
        backups = []
        
        if os.path.exists(PROMPTS_BACKUP_DIR):
            for file in os.listdir(PROMPTS_BACKUP_DIR):
                if file.startswith('prompts_backup_') and file.endswith('.json'):
                    file_path = os.path.join(PROMPTS_BACKUP_DIR, file)
                    stat = os.stat(file_path)
                    backups.append({
                        'filename': file,
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'size': stat.st_size
                    })
        
        # Ordenar por data de criação (mais recente primeiro)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': backups,
            'message': f'{len(backups)} backups encontrados'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro ao listar backups'
        }), 500