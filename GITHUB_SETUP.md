# Configuração do GitHub para Auto Video Producer

## Passo 1: Inicializar o Repositório Git

Abra o terminal/prompt de comando na pasta do projeto e execute:

```bash
git init
```

## Passo 2: Configurar Usuário Git

Configure seu nome e email (substitua pelos seus dados):

```bash
git config user.name "Seu Nome"
git config user.email "seu.email@exemplo.com"
```

## Passo 3: Adicionar Arquivos

```bash
git add .
```

## Passo 4: Fazer Commit Inicial

```bash
git commit -m "Initial commit: Auto Video Producer project"
```

## Passo 5: Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Nome do repositório: `auto-video-producer`
3. Escolha se será público ou privado
4. **NÃO** marque "Initialize this repository with a README" (já temos arquivos)
5. Clique em "Create repository"

## Passo 6: Conectar ao GitHub

Substitua `SEU_USUARIO` pelo seu nome de usuário do GitHub:

```bash
git remote add origin https://github.com/SEU_USUARIO/auto-video-producer.git
git branch -M main
git push -u origin main
```

## Estrutura do Projeto

Este projeto contém:

- **Backend**: API Flask com sistema de geração de roteiros usando IA
- **Frontend**: Interface React para gerenciar o sistema
- **Configurações**: Sistema de chaves de API e configurações
- **Documentação**: Análises e especificações técnicas

## Arquivos Importantes

- `backend/`: Código do servidor Python/Flask
- `frontend/`: Interface React
- `.gitignore`: Configurado para ignorar arquivos sensíveis
- `README.md`: Documentação principal do projeto

## Segurança

O arquivo `.gitignore` já está configurado para:
- Ignorar chaves de API (`config/api_keys.json`)
- Ignorar arquivos temporários e cache
- Ignorar dependências (`node_modules/`, `__pycache__/`)

## Próximos Passos

Após fazer o push inicial:
1. Configure as GitHub Actions se necessário
2. Adicione colaboradores se for um projeto em equipe
3. Configure branch protection rules se necessário
4. Considere adicionar badges ao README principal

---

**Nota**: Certifique-se de nunca fazer commit de chaves de API ou informações sensíveis!