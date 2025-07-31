# 🔄 Sistema de Backup - Auto Video Producer

Sistema completo de backup e restauração para o projeto Auto Video Producer.

## 📋 Visão Geral

O sistema de backup oferece múltiplas opções para proteger seu projeto:

- **Backup Completo**: Inclui código, banco de dados e configurações
- **Backup Rápido**: Apenas arquivos essenciais do código
- **Restauração**: Restaurar projeto a partir de qualquer backup
- **Backup Automático**: Scripts para automação

## 🚀 Como Usar

### Opção 1: Interface Simples (Windows)
```bash
# Execute o arquivo batch
backup.bat
```

### Opção 2: Scripts Python Diretos

#### Backup Completo
```bash
python backup_system.py
```

#### Backup Rápido
```bash
python quick_backup.py
```

#### Restaurar Backup
```bash
python restore_system.py
```

## 📁 Estrutura dos Backups

```
Documents/APP/BACKUPS/auto-video-producer/
├── auto-video-producer_FULL_BACKUP_YYYYMMDD_HHMMSS.zip
├── auto-video-producer_SOURCE_YYYYMMDD_HHMMSS.zip
├── auto-video-producer_DATABASE_YYYYMMDD_HHMMSS.zip
├── auto-video-producer_CONFIG_YYYYMMDD_HHMMSS.json
└── quick/
    └── quick_backup_YYYYMMDD_HHMMSS.zip
```

## 🔧 Tipos de Backup

### 1. **Backup Completo** (`backup_system.py`)
- ✅ Todo o código fonte
- ✅ Banco de dados SQLite
- ✅ Configurações do projeto
- ✅ Informações do Git
- ✅ Lista de dependências
- ❌ Chaves de API (por segurança)
- ❌ node_modules, __pycache__, etc.

**Quando usar**: Antes de mudanças importantes, releases, ou semanalmente.

### 2. **Backup Rápido** (`quick_backup.py`)
- ✅ Arquivos de código essenciais
- ✅ Configurações principais
- ❌ Banco de dados
- ❌ Dependências
- ❌ Arquivos temporários

**Quando usar**: Durante desenvolvimento, várias vezes ao dia.

## 🔄 Como Restaurar

### Restauração Automática
```bash
python restore_system.py
```

1. Lista todos os backups disponíveis
2. Permite escolher qual restaurar
3. Faz backup do projeto atual (se existir)
4. Restaura código, banco e configurações
5. Opcionalmente instala dependências

### Restauração Manual
1. Extrair o arquivo `*_FULL_BACKUP_*.zip`
2. Extrair o `*_SOURCE_*.zip` no diretório do projeto
3. Extrair o `*_DATABASE_*.zip` em `backend/`
4. Instalar dependências:
   ```bash
   pip install -r backend/requirements.txt
   cd frontend && npm install
   ```
5. Configurar chaves de API em `backend/config/api_keys.json`

## ⚙️ Configuração Automática

### Backup Diário (Windows Task Scheduler)
```bash
# Criar tarefa agendada
schtasks /create /tn "AutoVideoProducer_Backup" /tr "C:\caminho\para\projeto\backup_system.py" /sc daily /st 02:00
```

### Backup ao Fazer Commit (Git Hook)
Criar arquivo `.git/hooks/pre-commit`:
```bash
#!/bin/sh
python quick_backup.py
```

## 🛡️ Segurança

### O que É Incluído
- ✅ Código fonte completo
- ✅ Banco de dados
- ✅ Configurações do projeto
- ✅ Estrutura de diretórios

### O que NÃO É Incluído (por segurança)
- ❌ Chaves de API (`api_keys.json`)
- ❌ Arquivos `.env`
- ❌ Certificados e chaves privadas
- ❌ Logs com informações sensíveis

### Recomendações
1. **Armazene backups em local seguro** (nuvem criptografada)
2. **Mantenha chaves de API separadas** (gerenciador de senhas)
3. **Teste restaurações regularmente**
4. **Mantenha múltiplas versões** de backup

## 📊 Monitoramento

### Verificar Backups Existentes
```bash
# Listar todos os backups
ls -la ../BACKUPS/auto-video-producer/

# Verificar tamanhos
du -h ../BACKUPS/auto-video-producer/
```

### Limpeza Automática
- **Backups rápidos**: Mantém apenas os 10 mais recentes
- **Backups completos**: Limpeza manual recomendada
- **Configuração**: Editar scripts para ajustar retenção

## 🚨 Recuperação de Emergência

### Cenário 1: Projeto Corrompido
```bash
python restore_system.py
# Escolher backup mais recente
```

### Cenário 2: Perda Total do Projeto
```bash
# 1. Clonar repositório GitHub
git clone https://github.com/Ender-ss/auto-video-producer.git

# 2. Restaurar backup
cd auto-video-producer
python restore_system.py

# 3. Configurar ambiente
python start.py
```

### Cenário 3: Apenas Código Perdido
```bash
# Extrair apenas o backup de código
unzip auto-video-producer_SOURCE_YYYYMMDD_HHMMSS.zip
```

## 🔗 Integração com Git

O sistema de backup complementa o Git:

- **Git**: Controle de versão e colaboração
- **Backup**: Proteção completa incluindo dados e configurações
- **GitHub**: Repositório remoto do código
- **Backup Local**: Proteção contra perda de dados locais

## 📞 Suporte

### Problemas Comuns

**Erro: "Módulo não encontrado"**
```bash
pip install -r backend/requirements.txt
```

**Erro: "Permissão negada"**
```bash
# Executar como administrador no Windows
# Verificar permissões de arquivo no Linux/Mac
```

**Backup muito grande**
```bash
# Usar backup rápido para desenvolvimento
python quick_backup.py
```

### Logs de Debug
Os scripts geram logs detalhados. Em caso de erro, verifique:
1. Mensagens de erro no console
2. Permissões de arquivo
3. Espaço em disco disponível
4. Dependências instaladas

---

## 🎯 Resumo de Comandos

```bash
# Backup completo
python backup_system.py

# Backup rápido  
python quick_backup.py

# Restaurar
python restore_system.py

# Interface Windows
backup.bat

# Verificar backups
ls ../BACKUPS/auto-video-producer/
```

**Lembre-se**: Backup é segurança. Faça regularmente! 🛡️
