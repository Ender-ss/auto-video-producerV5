# Storyteller Unlimited - Guia de Integração

Este guia documenta como usar o sistema **Storyteller Unlimited** para gerar roteiros automatizados no pipeline de produção de vídeo.

## 📋 Visão Geral

O **Storyteller Unlimited** é um sistema inteligente que gera roteiros completos baseados em:
- **Título e premissa** da história
- **Tipo de agente** (estilo narrativo)
- **Número de capítulos** desejados
- **Duração estimada** do vídeo

## 🚀 Tipos de Agentes Disponíveis

### 1. `millionaire_stories`
- **Foco**: Histórias de sucesso financeiro e empreendedorismo
- **Estilo**: Motivacional, inspirador, educativo
- **Exemplos**: De dívidas à liberdade financeira, jornadas de empreendedores

### 2. `romance_agent`
- **Foco**: Histórias românticas e relacionamentos
- **Estilo**: Emocional, dramático, envolvente
- **Exemplos**: Encontros inesperados, amores proibidos, segundas chances

### 3. `horror_agent`
- **Foco**: Histórias de terror e suspense
- **Estilo**: Misterioso, tenso, sobrenatural
- **Exemplos**: Casas assombradas, criaturas sombrias, segredos obscuros

## 🔧 Como Usar no Pipeline

### Configuração no pipeline_service.py

```python
# Ativar Storyteller Unlimited
config = {
    'script_system': 'storyteller',  # Ativa o sistema
    'agent_type': 'millionaire_stories',  # Escolhe o tipo de história
    'num_chapters': 4,  # Número de capítulos
    'title': 'Sua História Aqui',
    'premise': 'Premissa da história...'
}
```

### Uso Direto via API

```bash
# Endpoint disponível
POST http://localhost:5000/api/storyteller/generate-script

# Body da requisição
{
    "title": "Título da História",
    "premise": "Premissa da história",
    "agent_type": "millionaire_stories",
    "num_chapters": 3,
    "api_key": "sua-chave-api"
}
```

### Uso Direto via Python

```python
from services.storyteller_service import storyteller_service

# Gerar roteiro completo
result = storyteller_service.generate_storyteller_script(
    title="De Falência à Liberdade",
    premise="Como alguém superou dívidas e construiu império",
    agent_type="millionaire_stories",
    num_chapters=4,
    api_key="demo_key",
    provider="demo"
)

# Resultado contém:
# - result['full_script']    # Roteiro completo em markdown
# - result['chapters']       # Lista de capítulos com metadados
# - result['estimated_duration']  # Duração em segundos
# - result['total_characters']    # Total de caracteres
```

## 📊 Estrutura do Retorno

```json
{
    "title": "Título da História",
    "premise": "Premissa da história",
    "full_script": "# Título\n\nPremissa...\n\n## Capítulo 1\n...",
    "chapters": [
        {
            "number": 1,
            "title": "Capítulo 1",
            "content": "Conteúdo do capítulo...",
            "duration": 57,
            "start_time": 0,
            "end_time": 57,
            "word_count": 142,
            "char_count": 850
        }
    ],
    "estimated_duration": 228,
    "total_characters": 3400,
    "agent_type": "millionaire_stories",
    "num_chapters": 4,
    "success": true
}
```

## 🎯 Exemplos de Configurações

### História de Empreendedorismo
```python
config = {
    'script_system': 'storyteller',
    'agent_type': 'millionaire_stories',
    'title': 'De R$50 mil em Dívidas a Milionário',
    'premise': 'Como João Silva saiu das dívidas e construiu um negócio de 7 dígitos',
    'num_chapters': 5
}
```

### História Romântica
```python
config = {
    'script_system': 'storyteller',
    'agent_type': 'romance_agent',
    'title': 'Amor em Nova York',
    'premise': 'Dois estranhos que se encontram em uma cafeteria durante uma tempestade',
    'num_chapters': 3
}
```

### História de Terror
```python
config = {
    'script_system': 'storyteller',
    'agent_type': 'horror_agent',
    'title': 'A Casa dos Sussurros',
    'premise': 'Uma família se muda para uma casa antiga com segredos sombrios',
    'num_chapters': 4
}
```

## 📝 Arquivos de Exemplo

Os exemplos gerados estão disponíveis em:
- `examples/storyteller_example_1.md` - Empreendedorismo
- `examples/storyteller_example_2.md` - Romance
- `examples/storyteller_example_3.md` - Terror

## 🔍 Troubleshooting

### Problemas Comuns

1. **Capítulos não aparecem**
   - Verifique se `script_system` está definido como `'storyteller'`
   - Confirme que `agent_type` é válido

2. **Roteiro muito curto**
   - Aumente o número de capítulos
   - Use premissas mais detalhadas

3. **Erro no endpoint**
   - Certifique-se que o servidor está rodando: `python app.py`
   - Verifique a porta: `http://localhost:5000`

## 🎬 Próximos Passos

1. **Integração com LLM real**: Substituir o mock por integração com Gemini/OpenRouter
2. **Mais agentes**: Adicionar novos tipos de histórias
3. **Personalização**: Permitir templates customizados
4. **Análise de engajamento**: Métricas de performance por tipo de história

## 📞 Suporte

Para questões sobre integração, consulte:
- `storyteller_service.py` - Implementação principal
- `storyteller.py` - Endpoints da API
- `test_simple_storyteller.py` - Exemplos de uso