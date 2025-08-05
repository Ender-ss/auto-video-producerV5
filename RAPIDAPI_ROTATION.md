# Sistema de Rotação de Chaves RapidAPI

## Visão Geral

O sistema foi atualizado para suportar rotação automática de até 6 chaves RapidAPI, resolvendo o problema de quota mensal excedida.

## Como Configurar

### 1. Adicionar Chaves no Arquivo de Configuração

Edite o arquivo `backend/config/api_keys.json` e adicione suas chaves RapidAPI:

```json
{
  "rapidapi_keys": [
    "sua_chave_1_aqui",
    "sua_chave_2_aqui",
    "sua_chave_3_aqui",
    "sua_chave_4_aqui",
    "sua_chave_5_aqui",
    "sua_chave_6_aqui"
  ],
  "rapidapi": "sua_chave_principal_aqui"
}
```

### 2. Como Funciona

- **Rotação Automática**: O sistema automaticamente alterna entre as chaves disponíveis
- **Detecção de Quota**: Quando uma chave excede a quota mensal, ela é marcada como falhada
- **Reset Diário**: Chaves falhadas são resetadas diariamente (útil para limites diários)
- **Fallback**: Se todas as chaves falharem, o sistema usa a chave principal como fallback

### 3. Logs do Sistema

O sistema exibe logs informativos:
- `🔄 Usando chave da rotação: xxxxx...` - Chave sendo utilizada
- `📊 Quota mensal excedida para chave: xxxxx...` - Chave com quota excedida
- `🔄 Tentando com nova chave: xxxxx...` - Alternando para nova chave

## Funções Atualizadas

As seguintes funções agora suportam rotação de chaves:
- `get_channel_id_rapidapi()` - Busca ID do canal
- `get_channel_details_rapidapi()` - Detalhes do canal
- `get_channel_videos_rapidapi()` - Lista de vídeos do canal

## Benefícios

1. **Maior Disponibilidade**: Até 6x mais requisições mensais
2. **Recuperação Automática**: Sistema continua funcionando mesmo com chaves esgotadas
3. **Transparente**: Funciona automaticamente sem intervenção manual
4. **Compatível**: Mantém compatibilidade com configuração de chave única

## Testando o Sistema

1. Acesse a aba "Automações" no frontend
2. Configure pelo menos 2 chaves RapidAPI diferentes
3. Teste a extração de um canal do YouTube
4. Observe os logs no terminal para ver a rotação em ação

## Solução de Problemas

- **Erro 429 persistente**: Verifique se todas as chaves são válidas
- **Chaves não carregando**: Reinicie o servidor após modificar `api_keys.json`
- **Logs não aparecem**: Verifique se o sistema de debug está ativo