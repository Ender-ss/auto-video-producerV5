# Plano de Implementação: Etapa de Processamento de Roteiro na Pipeline

## 1. Visão Geral

### Objetivo
Implementar uma nova etapa na pipeline dedicada exclusivamente ao processamento e limpeza de roteiros após sua geração, removendo marcações de capítulos e preparando o conteúdo para as etapas subsequentes de geração de imagem e áudio.

### Justificativa
- **Separação de responsabilidades**: Isolar o processamento de roteiro do Storyteller
- **Flexibilidade**: Permitir diferentes tipos de processamento sem modificar o core
- **Testabilidade**: Facilitar testes isolados da funcionalidade
- **Manutenibilidade**: Reduzir complexidade e acoplamento
- **Escalabilidade**: Possibilitar futuras expansões de processamento

## 2. Arquitetura da Solução

### 2.1 Fluxo Atual vs Novo Fluxo

**Fluxo Atual:**
```
StorytellerService → ImageGeneration → AudioGeneration → VideoAssembly
```

**Novo Fluxo:**
```
StorytellerService → ScriptProcessingService → ImageGeneration → AudioGeneration → VideoAssembly
```

### 2.2 Componentes Principais

#### ScriptProcessingService
- **Localização**: `backend/services/script_processing_service.py`
- **Responsabilidade**: Processar e limpar roteiros gerados
- **Dependências**: `ImprovedHeaderRemoval`, `logging`, `database`

#### Modificações na Pipeline
- **Arquivo**: `backend/services/pipeline_service.py`
- **Mudança**: Adicionar nova etapa entre storyteller e image_generation

#### Novos Endpoints API
- **Arquivo**: `backend/routes/pipelines.py`
- **Endpoint**: `POST /api/v1/pipelines/{id}/process-script`

## 3. Implementação Detalhada

### 3.1 ScriptProcessingService

```python
class ScriptProcessingService:
    def __init__(self):
        self.header_remover = ImprovedHeaderRemoval()
        self.logger = logging.getLogger(__name__)
    
    def process_script(self, pipeline_id: str, raw_script: str, config: dict) -> dict:
        """Processa roteiro removendo marcações e aplicando limpezas"""
        
    def validate_input(self, script: str) -> bool:
        """Valida entrada do roteiro"""
        
    def validate_output(self, processed_script: str) -> bool:
        """Valida saída do processamento"""
        
    def get_processing_metrics(self, original: str, processed: str) -> dict:
        """Calcula métricas do processamento"""
```

### 3.2 Integração na Pipeline

#### Modificações no PipelineService

```python
# Adicionar nova etapa no enum de status
class PipelineStatus(Enum):
    # ... status existentes ...
    SCRIPT_PROCESSING = "script_processing"
    SCRIPT_PROCESSING_COMPLETED = "script_processing_completed"
    SCRIPT_PROCESSING_FAILED = "script_processing_failed"

# Adicionar método de processamento
def execute_script_processing(self, pipeline_id: str):
    """Executa etapa de processamento de roteiro"""
    try:
        # Buscar roteiro gerado pelo storyteller
        pipeline = self.get_pipeline(pipeline_id)
        raw_script = pipeline.storyteller_result
        
        # Processar roteiro
        script_processor = ScriptProcessingService()
        result = script_processor.process_script(
            pipeline_id, 
            raw_script, 
            pipeline.config
        )
        
        # Salvar resultado processado
        self.update_pipeline_script_processing(pipeline_id, result)
        
        # Avançar para próxima etapa
        self.update_pipeline_status(pipeline_id, PipelineStatus.IMAGE_GENERATION)
        
    except Exception as e:
        self.handle_pipeline_error(pipeline_id, "script_processing", str(e))
```

### 3.3 Modificações no Banco de Dados

#### Schema Updates

```sql
-- Adicionar colunas para processamento de roteiro
ALTER TABLE pipelines ADD COLUMN processed_script TEXT;
ALTER TABLE pipelines ADD COLUMN script_processing_config JSON;
ALTER TABLE pipelines ADD COLUMN script_processing_metrics JSON;
ALTER TABLE pipelines ADD COLUMN script_processing_started_at TIMESTAMP;
ALTER TABLE pipelines ADD COLUMN script_processing_completed_at TIMESTAMP;

-- Criar tabela de logs específica
CREATE TABLE script_processing_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pipeline_id) REFERENCES pipelines (id)
);
```

### 3.4 API Endpoints

#### Novo Endpoint de Processamento

```python
@pipelines_bp.route('/<pipeline_id>/process-script', methods=['POST'])
def process_script(pipeline_id):
    """Endpoint para processar roteiro de uma pipeline"""
    try:
        config = request.get_json() or {}
        
        # Validar pipeline existe e está no status correto
        pipeline = pipeline_service.get_pipeline(pipeline_id)
        if not pipeline:
            return jsonify({'error': 'Pipeline não encontrada'}), 404
            
        if pipeline.status != 'storyteller_completed':
            return jsonify({'error': 'Pipeline não está pronta para processamento'}), 400
        
        # Executar processamento
        pipeline_service.execute_script_processing(pipeline_id)
        
        return jsonify({
            'success': True,
            'message': 'Processamento de roteiro iniciado',
            'pipeline_id': pipeline_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### Atualização do Endpoint de Status

```python
# Adicionar informações de script processing no status
def get_pipeline_status_detailed(pipeline_id):
    pipeline = pipeline_service.get_pipeline(pipeline_id)
    
    status_info = {
        # ... campos existentes ...
        'script_processing': {
            'status': pipeline.status if 'script_processing' in pipeline.status else None,
            'started_at': pipeline.script_processing_started_at,
            'completed_at': pipeline.script_processing_completed_at,
            'metrics': pipeline.script_processing_metrics,
            'processed_script_length': len(pipeline.processed_script or ''),
            'original_script_length': len(pipeline.storyteller_result or '')
        }
    }
    
    return status_info
```

## 4. Configuração e Feature Flags

### 4.1 Configuração do Serviço

```python
# config/script_processing_config.json
{
    "enabled": true,
    "processing_options": {
        "remove_chapter_headers": true,
        "remove_markdown": true,
        "preserve_dialogue": true,
        "preserve_context": true
    },
    "validation": {
        "min_script_length": 100,
        "max_script_length": 50000,
        "required_preservation_ratio": 0.8
    },
    "performance": {
        "timeout_seconds": 30,
        "max_retries": 3
    }
}
```

### 4.2 Feature Flag

```python
# Adicionar no arquivo de configuração principal
SCRIPT_PROCESSING_ENABLED = os.getenv('SCRIPT_PROCESSING_ENABLED', 'false').lower() == 'true'

# Usar na pipeline
if SCRIPT_PROCESSING_ENABLED:
    self.execute_script_processing(pipeline_id)
else:
    # Pular para próxima etapa
    self.update_pipeline_status(pipeline_id, PipelineStatus.IMAGE_GENERATION)
```

## 5. Testes

### 5.1 Testes Unitários

#### test_script_processing_service.py

```python
class TestScriptProcessingService(unittest.TestCase):
    def setUp(self):
        self.service = ScriptProcessingService()
        self.sample_script = "# Capítulo 1\nConteúdo do roteiro..."
    
    def test_process_script_removes_headers(self):
        """Testa se cabeçalhos são removidos corretamente"""
        
    def test_process_script_preserves_content(self):
        """Testa se conteúdo principal é preservado"""
        
    def test_validate_input_rejects_empty_script(self):
        """Testa validação de entrada"""
        
    def test_get_processing_metrics(self):
        """Testa cálculo de métricas"""
```

### 5.2 Testes de Integração

#### test_pipeline_script_processing.py

```python
class TestPipelineScriptProcessing(unittest.TestCase):
    def test_complete_pipeline_with_script_processing(self):
        """Testa pipeline completa com nova etapa"""
        
    def test_pipeline_continues_after_script_processing(self):
        """Testa se pipeline continua após processamento"""
        
    def test_pipeline_handles_script_processing_failure(self):
        """Testa tratamento de falhas no processamento"""
```

### 5.3 Testes de Performance

```python
def test_script_processing_performance():
    """Testa impacto no tempo total da pipeline"""
    # Medir tempo antes e depois da implementação
    # Garantir que aumento seja < 10% do tempo total
```

## 6. Monitoramento e Métricas

### 6.1 Métricas de Sucesso

- **Taxa de sucesso**: > 95% das pipelines processadas com sucesso
- **Tempo de processamento**: < 5 segundos para roteiros típicos
- **Preservação de conteúdo**: > 85% do conteúdo original preservado
- **Qualidade da remoção**: > 95% dos cabeçalhos removidos corretamente

### 6.2 Logs e Alertas

```python
# Logs estruturados
logger.info("Script processing started", extra={
    'pipeline_id': pipeline_id,
    'original_length': len(raw_script),
    'config': config
})

logger.info("Script processing completed", extra={
    'pipeline_id': pipeline_id,
    'processed_length': len(processed_script),
    'processing_time': processing_time,
    'metrics': metrics
})

# Alertas automáticos
if processing_time > 10:  # segundos
    alert_manager.send_alert("Script processing slow", pipeline_id)
    
if metrics['preservation_ratio'] < 0.8:
    alert_manager.send_alert("Low content preservation", pipeline_id)
```

## 7. Plano de Implementação Faseada

### Fase 1: Desenvolvimento Base (1-2 semanas)
- [ ] Criar ScriptProcessingService
- [ ] Implementar testes unitários
- [ ] Criar configurações básicas
- [ ] Documentar API do serviço

### Fase 2: Integração Pipeline (1 semana)
- [ ] Modificar PipelineService
- [ ] Adicionar novos status no banco
- [ ] Implementar feature flag
- [ ] Criar testes de integração

### Fase 3: API e Frontend (1 semana)
- [ ] Implementar novos endpoints
- [ ] Atualizar frontend para mostrar nova etapa
- [ ] Adicionar logs e monitoramento
- [ ] Testes end-to-end

### Fase 4: Testes e Validação (1 semana)
- [ ] Testes de performance
- [ ] Testes de regressão
- [ ] Validação com roteiros reais
- [ ] Ajustes baseados em feedback

### Fase 5: Deploy e Monitoramento (1 semana)
- [ ] Deploy em ambiente de staging
- [ ] Testes com usuários beta
- [ ] Deploy gradual em produção
- [ ] Monitoramento intensivo

## 8. Critérios de Rollback

### Automáticos
- Taxa de falha > 5% em 1 hora
- Tempo médio de pipeline > 120% do baseline
- Erros críticos > 10 em 30 minutos

### Manuais
- Degradação na qualidade dos roteiros
- Feedback negativo dos usuários
- Problemas de performance não resolvidos

## 9. Arquivos a Serem Criados/Modificados

### Novos Arquivos
- `backend/services/script_processing_service.py`
- `backend/tests/test_script_processing_service.py`
- `backend/tests/test_pipeline_script_processing.py`
- `backend/config/script_processing_config.json`
- `backend/migrations/add_script_processing_fields.sql`

### Arquivos Modificados
- `backend/services/pipeline_service.py`
- `backend/routes/pipelines.py`
- `backend/database.py`
- `frontend/src/components/PipelineStatus.jsx`
- `backend/config/prompts_config.json`

## 10. Validação Final

### Checklist de Implementação
- [ ] ScriptProcessingService implementado e testado
- [ ] Pipeline modificada com nova etapa
- [ ] Banco de dados atualizado
- [ ] API endpoints funcionando
- [ ] Frontend atualizado
- [ ] Testes passando (unitários, integração, performance)
- [ ] Documentação atualizada
- [ ] Monitoramento configurado
- [ ] Feature flag funcionando
- [ ] Deploy realizado com sucesso

### Métricas de Aceitação
- ✅ Taxa de sucesso > 95%
- ✅ Tempo adicional < 10% do total da pipeline
- ✅ Preservação de conteúdo > 85%
- ✅ Remoção de cabeçalhos > 95%
- ✅ Zero regressões em funcionalidades existentes

## 11. Próximos Passos Após Implementação

1. **Coleta de Feedback**: Monitorar uso e coletar feedback dos usuários
2. **Otimizações**: Implementar melhorias baseadas em dados reais
3. **Expansão**: Adicionar novos tipos de processamento (formatação, correção gramatical)
4. **Automação**: Implementar processamento inteligente baseado no tipo de conteúdo
5. **Analytics**: Criar dashboard para acompanhar métricas de qualidade

---

**Documento criado em**: Janeiro 2025  
**Versão**: 1.0  
**Status**: Pronto para implementação  
**Responsável**: Equipe de Desenvolvimento