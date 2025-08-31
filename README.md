# 🎬 Auto Video Producer

Sistema completo de produção automatizada de vídeos usando inteligência artificial.

## 🚀 Características Principais

- **Extração Automática**: Extrai conteúdo de canais do YouTube
- **Geração de Títulos**: Cria títulos virais usando IA (OpenAI, Gemini, Claude)
- **Roteiros Inteligentes**: Gera roteiros multi-capítulos com contexto
- **Text-to-Speech**: Converte roteiros em áudio com vozes naturais
- **Geração de Imagens**: Cria imagens relevantes para o conteúdo
- **Pipeline Completa**: Automação end-to-end da produção de vídeos

## 🛠️ Tecnologias

### Frontend
- React 18
- Vite
- Tailwind CSS
- Framer Motion

### Backend
- Python 3.8+
- Flask
- SQLAlchemy
- SQLite

### APIs de IA
- Google Gemini (múltiplas chaves com rotação)
- OpenAI GPT
- Anthropic Claude
- ElevenLabs TTS
- OpenRouter
- Together.ai

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Node.js 16 ou superior
- Git

## 🔧 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/auto-video-producer.git
cd auto-video-producer
```

### 2. Instalação automática
```bash
python start.py
```

### 3. Instalação manual

#### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Acesso

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000

## ⚙️ Configuração

### Chaves de API

Configure suas chaves de API no arquivo `backend/config/api_keys.json`:

```json
{
  "gemini": {
    "gemini_1": "sua-chave-gemini-1",
    "gemini_2": "sua-chave-gemini-2",
    "gemini_3": "sua-chave-gemini-3"
  },
  "openai": "sua-chave-openai",
  "elevenlabs": "sua-chave-elevenlabs",
  "rapidapi": "sua-chave-rapidapi"
}
```

### Sistema de Rotação de Chaves Gemini

O sistema suporta múltiplas chaves Gemini com rotação automática:
- ✅ **Rotação inteligente**: Seleciona a chave com menor uso
- ✅ **Limite dinâmico**: Usa todas as chaves disponíveis em caso de falha
- ✅ **Otimização para tier gratuito**: 250 requests/dia por chave
- ✅ **Retry automático**: Tenta com todas as chaves disponíveis

## 🎯 Funcionalidades

### 📝 Roteiros Longos Contextuais
- Geração de roteiros multi-capítulos
- Resumos contextuais entre capítulos
- Prompts personalizáveis por fase (início, meio, fim)
- Limpeza automática de conteúdo para TTS

### 🎨 Prompts Personalizados
- Prompts padrão editáveis na interface
- Prompts por fase narrativa
- Sistema hierárquico: personalizado → editado → padrão

### 🔄 Pipeline Automatizada
- Checkpoints automáticos
- Retomada de execução
- Monitoramento em tempo real
- Logs detalhados

## 📊 Limites e Otimizações

### Gemini Free Tier
- **1,500 requests/dia** por chave
- **15 requests/minuto** por chave
- **Configuração otimizada**: 250 requests/dia por chave
- **Capacidade**: ~30 roteiros longos/dia com 7 chaves

## 🔧 Desenvolvimento

### Estrutura do Projeto
```
auto-video-producer/
├── backend/                 # API Flask
│   ├── routes/             # Endpoints da API
│   ├── services/           # Lógica de negócio
│   ├── config/             # Configurações
│   └── database.py         # Modelos do banco
├── frontend/               # App React
│   ├── src/
│   │   ├── pages/          # Páginas
│   │   ├── components/     # Componentes
│   │   └── services/       # Clientes da API
└── start.py               # Launcher principal
```

### Scripts Úteis
- `python start.py` - Inicia todo o sistema
- `python backend/check_gemini_keys_status.py` - Verifica status das chaves
- `python backend/verify_gemini_system.py` - Testa sistema Gemini

## 🐛 Resolução de Problemas

### Erro de Chaves Gemini
```bash
python backend/check_gemini_keys_status.py
```

### Verificar Pipeline
```bash
python backend/check_pipeline_status.py
```

### Limpar Cache
```bash
# Remover arquivos de cache
rm -rf backend/cache/
rm -rf backend/checkpoints/
```

## 📈 Performance

- **Concorrência**: Até 3 pipelines simultâneas
- **Duração máxima**: 10 minutos por vídeo
- **Retry automático**: Habilitado
- **Throttling**: 1-3 segundos entre requests

## 🔒 Segurança

- Chaves de API armazenadas localmente
- Sem autenticação (uso individual)
- Logs não expõem informações sensíveis

## 🚀 Roadmap

- [ ] Sistema de autenticação
- [ ] Armazenamento em nuvem
- [ ] WebSockets para updates em tempo real
- [ ] Containerização com Docker
- [ ] Suporte a múltiplos usuários
- [ ] Integração com mais provedores de IA

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- OpenAI pela API GPT
- Google pelo Gemini
- Anthropic pelo Claude
- ElevenLabs pelo TTS
- Comunidade open source

---

**Desenvolvido com ❤️ para automatizar a criação de conteúdo**