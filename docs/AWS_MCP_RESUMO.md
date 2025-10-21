# 🚀 AWS MCP Server - Resumo Rápido

## ⚠️ Nota Importante

**Atualização**: O AWS MCP Server oficial da AWS Labs é mais complexo do que um simples pacote npm. Ele requer:
- Docker
- Configuração via containers
- Setup mais elaborado

**Recomendação Atual**: Use a **AWS Toolkit Extension** do Cursor como alternativa mais simples e imediata. Ela oferece funcionalidades similares:
- ✅ Ver logs do CloudWatch
- ✅ Inspecionar funções Lambda
- ✅ Gerenciar recursos AWS
- ✅ Debug integrado

A AWS Toolkit já está na lista de extensões recomendadas do projeto!

## O que seria o AWS MCP Server?

O **AWS MCP Server** oficial conectaria o Cursor AI aos seus recursos AWS de forma ainda mais integrada, permitindo interagir com eles usando **linguagem natural** no chat.

### Antes (sem integração):
```
❌ Abrir AWS Console
❌ Navegar até CloudWatch
❌ Procurar função Lambda
❌ Filtrar logs manualmente
❌ Copiar/colar erros
```

### Com AWS Toolkit (solução atual):
```
✅ Painel lateral com recursos AWS
✅ Click para ver logs do CloudWatch
✅ Navegação visual de Lambda
✅ Deploy direto do IDE
```

### Futuro com MCP (quando disponível facilmente):
```
✅ No chat: "Mostre os últimos erros da função Lambda"
✅ Resposta instantânea com logs
✅ Análise automática do erro
✅ Sugestões de correção
```

## Comandos Úteis para o Projeto FinAssist

### Durante Desenvolvimento Local
```
"O DynamoDB Local está rodando?"
"Mostre os logs do SAM CLI"
"Há algum erro nos últimos testes?"
```

### Debug em Produção
```
"Quais foram os últimos 10 erros da função WebhookFunction?"
"Mostre as métricas da função Lambda nas últimas 2 horas"
"A tabela FinAssist-Threads tem quantos registros?"
"Há algum timeout recente?"
```

### Análise de Problemas
```
"Por que a função Lambda está falhando?"
"Analise os logs de erro e sugira uma correção"
"Qual a causa mais comum de erro hoje?"
```

### Monitoramento
```
"Crie um resumo do status de todos os recursos AWS do projeto"
"Há algum alerta nos últimos 30 minutos?"
"Qual o tempo médio de execução da função Lambda?"
```

## Exemplos Reais

### Exemplo 1: Debug de Erro
**Você:** "A função Lambda está retornando erro 500, o que está acontecendo?"

**Cursor com MCP:**
1. Busca logs recentes da função
2. Identifica o erro específico
3. Mostra o stack trace
4. Sugere correção baseada no erro encontrado

### Exemplo 2: Análise de Performance
**Você:** "A API está lenta, onde está o gargalo?"

**Cursor com MCP:**
1. Consulta métricas do API Gateway
2. Verifica tempo de execução do Lambda
3. Analisa tempo de resposta do DynamoDB
4. Identifica o componente mais lento
5. Sugere otimizações

### Exemplo 3: Verificação Pré-Deploy
**Você:** "Verificar se o ambiente está pronto para deploy"

**Cursor com MCP:**
1. Lista recursos existentes
2. Verifica permissões IAM
3. Checa configurações do API Gateway
4. Confirma se DynamoDB está ativo
5. Reporta status geral

## Recursos AWS Acessíveis

✅ **Lambda Functions**: Status, configurações, logs, métricas
✅ **CloudWatch Logs**: Busca, filtros, análise de erros
✅ **DynamoDB**: Tabelas, schemas, contagem de itens
✅ **API Gateway**: Endpoints, configurações, métricas
✅ **IAM**: Roles, policies, permissões
✅ **CloudWatch Metrics**: Performance, invocações, erros

## Segurança

- ✅ Usa suas credenciais AWS existentes (aws configure)
- ✅ Mesmas permissões do seu perfil AWS
- ✅ Não armazena credenciais adicionais
- ✅ Acesso read-only por padrão

## Solução de Problemas

### MCP não funciona?
```bash
# 1. Verificar Node.js
node --version  # Deve ser >= 18.x

# 2. Verificar AWS CLI
aws configure list
aws sts get-caller-identity

# 3. Reinstalar MCP
./scripts/setup_aws_mcp.sh

# 4. Verificar configuração
cat ~/.cursor/mcp_config.json
```

### Comando não retorna nada?
- Verifique se recursos existem na AWS
- Confirme região correta no AWS CLI
- Teste credenciais: `aws lambda list-functions`

## Documentação Completa

📖 **Guia Detalhado**: [CONFIGURAR_AWS_MCP.md](./CONFIGURAR_AWS_MCP.md)
- Instalação passo-a-passo
- Configuração avançada
- Troubleshooting completo
- Exemplos de uso

## Dica Final

💡 **Use em conjunto com AWS Toolkit extension** para máxima produtividade:
- AWS Toolkit: Navegação visual de recursos
- AWS MCP: Consultas em linguagem natural
- Juntos: Ambiente de desenvolvimento super-produtivo!

---

**Pronto para usar?** Execute: `./scripts/setup_aws_mcp.sh` 🚀

