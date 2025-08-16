# 🎬 Auto Video Producer

**Sistema Completo de Produção Automática de Vídeos usando IA**

Um sistema avançado que automatiza todo o processo de criação de vídeos, desde a extração de conteúdo do YouTube até a geração de roteiros, áudio e vídeos finais usando múltiplas APIs de IA.

## ✨ Características Principais

### 🤖 **Automações de IA**
- **Extração YouTube**: Coleta automática de títulos e métricas de canais
- **Geração de Títulos**: Criação de títulos virais usando OpenAI, Gemini, Claude
- **Roteiros Inteligentes**: Geração de roteiros completos com múltiplos capítulos
- **Premissas Narrativas**: Criação de premissas envolventes para histórias
- **Text-to-Speech**: Conversão de texto em áudio com vozes naturais

### 📊 **Interface Completa**
- **Dashboard**: Visão geral com estatísticas em tempo real
- **Gerenciamento de Canais**: Monitoramento de canais do YouTube
- **Pipeline de Produção**: Acompanhamento de vídeos em produção
- **Biblioteca de Vídeos**: Organização e download de vídeos produzidos
- **Analytics**: Relatórios detalhados de performance
- **Configurações**: Gerenciamento de APIs e preferências

### 🔧 **Tecnologias**
- **Backend**: Python + Flask + SQLAlchemy
- **Frontend**: React + Vite + Tailwind CSS + Framer Motion
- **IA**: OpenAI, Google Gemini, Anthropic Claude, ElevenLabs
- **APIs**: RapidAPI YouTube V2, Together.ai, OpenRouter

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.8+
- Node.js 16+
- Git

### 1. Clone o Repositório
```bash
git clone https://github.com/SEU_USUARIO/auto-video-producer.git
cd auto-video-producer
```

> **📋 Primeira vez?** Veja o arquivo `GITHUB_SETUP.md` para instruções de configuração do Git e GitHub.

### 2. Instalação Automática
```bash
python start.py
```

O script `start.py` irá:
- ✅ Verificar dependências
- 📦 Instalar pacotes Python e Node.js
- 🗂️ Criar diretórios necessários
- 🚀 Iniciar backend e frontend
- 🌐 Abrir interface web

### 3. Acesse a Interface
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000

## ⚙️ Configuração

### 1. Configure suas APIs
Acesse **Configurações** na interface web e adicione suas chaves:

#### 🔑 **APIs Essenciais**
- **RapidAPI YouTube V2**: Para extração de conteúdo
- **Google Gemini**: IA gratuita para títulos e roteiros
- **OpenAI**: IA premium para melhor qualidade

#### 🔑 **APIs Opcionais**
- **Anthropic Claude**: IA alternativa
- **ElevenLabs**: Text-to-speech premium
- **Together.ai**: Geração de imagens
- **OpenRouter**: Acesso a múltiplos modelos

### 2. Teste as Conexões
Use o botão "Testar" em cada API para verificar se estão funcionando.

## 📖 Como Usar

### 🎯 **Fluxo Básico**

1. **📺 Adicione Canais**
   - Vá para "Canais"
   - Adicione canais do YouTube para monitorar
   - Configure estilo de vídeo e parâmetros

2. **🤖 Use as Automações**
   - Acesse "Automações"
   - Extraia conteúdo de canais
   - Gere títulos virais
   - Crie roteiros completos

3. **🎬 Execute Pipelines**
   - Vá para "Pipeline"
   - Inicie produção automática
   - Acompanhe progresso em tempo real

4. **📥 Baixe os Vídeos**
   - Acesse "Vídeos"
   - Visualize biblioteca completa
   - Faça download individual ou em lote

### 🛠️ **Automações Disponíveis**

#### **Extração YouTube**
```
Input: URL do canal (@NomeCanal ou link completo)
Output: Lista de títulos, views, likes, dados do canal
```

#### **Geração de Títulos**
```
Input: Títulos originais + instruções
Output: 5 títulos virais otimizados
```

#### **Roteiros IA**
```
Input: Título + contexto + número de capítulos
Output: Roteiro completo dividido em capítulos
```

#### **Premissas Narrativas**
```
Input: Título + resumo
Output: Premissa envolvente para história
```

## 🏗️ Arquitetura

```
auto-video-producer/
├── 🐍 backend/           # API Python + Flask
│   ├── app.py           # Aplicação principal
│   ├── routes/          # Rotas da API
│   ├── services/        # Serviços de IA
│   └── requirements.txt # Dependências Python
├── ⚛️ frontend/          # Interface React
│   ├── src/
│   │   ├── pages/       # Páginas da aplicação
│   │   ├── components/  # Componentes reutilizáveis
│   │   └── services/    # Serviços de API
│   └── package.json     # Dependências Node.js
├── 🚀 start.py          # Script de inicialização
└── 📚 README.md         # Este arquivo
```

## 🔌 API Endpoints

### **Automações**
- `POST /api/automations/extract-youtube` - Extrair conteúdo YouTube
- `POST /api/automations/generate-titles` - Gerar títulos
- `POST /api/automations/generate-script` - Gerar roteiros
- `POST /api/automations/generate-premise` - Gerar premissas
- `POST /api/automations/generate-tts` - Text-to-speech

### **Gerenciamento**
- `GET /api/channels` - Listar canais
- `GET /api/pipelines` - Listar pipelines
- `GET /api/videos` - Listar vídeos
- `GET /api/settings/apis` - Configurações de API

### **Sistema**
- `GET /api/system/status` - Status do sistema
- `GET /` - Informações da API

## 🎨 Interface

### **Dashboard**
- 📊 Estatísticas em tempo real
- 🎬 Pipelines ativos
- 📈 Gráficos de performance
- ⚡ Ações rápidas

### **Automações**
- 🤖 6 tipos de automação
- 🔄 Status dos agentes de IA
- 📝 Histórico de execuções
- ⚙️ Configurações personalizadas

### **Pipeline**
- 🎯 Monitoramento em tempo real
- 📊 Barras de progresso
- 🔍 Logs detalhados
- ⏹️ Controles de execução

## 🛠️ Desenvolvimento

### **Backend**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### **Frontend**
```bash
cd frontend
npm install
npm run dev
```

### **Estrutura do Banco**
- `APIConfig`: Configurações de APIs
- `Channel`: Canais monitorados
- `Pipeline`: Pipelines de produção
- `Video`: Vídeos produzidos
- `AutomationLog`: Logs de automações

## 🔧 Configurações Avançadas

### **Variáveis de Ambiente**
```bash
MAX_CONCURRENT_PIPELINES=3
DEFAULT_VIDEO_QUALITY=1080p
AUTO_RETRY_FAILED=true
MAX_VIDEO_DURATION=600
STORAGE_PATH=./outputs
TEMP_PATH=./temp
LOG_LEVEL=INFO
```

### **Personalização**
- Modifique prompts de IA em `services/ai_services.py`
- Ajuste interface em `frontend/src/pages/`
- Configure novos agentes de IA nas rotas

## 📊 Monitoramento

### **Logs**
- Backend: Console do Python
- Frontend: Console do navegador
- Automações: Página "Automações" → Logs

### **Métricas**
- Taxa de sucesso dos pipelines
- Uso de APIs por agente
- Performance de canais
- Estatísticas de vídeos

## 🆘 Solução de Problemas

### **Erros Comuns**

#### ❌ "API não configurada"
- Verifique se adicionou a chave correta
- Teste a conexão na página de configurações

#### ❌ "Erro ao extrair canal"
- Verifique se a URL está correta
- Confirme se a chave RapidAPI está válida

#### ❌ "Frontend não carrega"
- Verifique se Node.js está instalado
- Execute `npm install` no diretório frontend

#### ❌ "Backend não inicia"
- Verifique se Python 3.8+ está instalado
- Execute `pip install -r requirements.txt`

### **Suporte**
- 📧 Verifique logs para detalhes do erro
- 🔍 Teste APIs individualmente
- 🔄 Reinicie o sistema com `python start.py`

## 📈 Roadmap

### **Próximas Funcionalidades**
- 🎵 Geração automática de música de fundo
- 🖼️ Criação de thumbnails personalizados
- 📱 Upload automático para YouTube
- 🔄 Agendamento de produções
- 📊 Analytics avançados
- 🌐 Suporte a múltiplos idiomas

### **Melhorias Planejadas**
- ⚡ Otimização de performance
- 🔒 Sistema de autenticação
- 📱 Interface mobile responsiva
- 🎨 Temas personalizáveis
- 🔌 Plugin system para extensões

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**🎬 Auto Video Producer** - Transformando ideias em vídeos automaticamente!

*Desenvolvido com ❤️ para criadores de conteúdo*
