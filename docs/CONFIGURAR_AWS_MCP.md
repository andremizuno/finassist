# 🔌 Configurar AWS MCP Server no Cursor AI

> **⚠️ AVISO**: Este guia é para usuários avançados. O AWS MCP Server oficial requer configuração Docker complexa e ainda está em desenvolvimento.
>
> **✅ RECOMENDAÇÃO**: Use a **AWS Toolkit Extension** (incluída nas extensões recomendadas) para uma experiência mais simples e completa.

> Guia para instalar e configurar o AWS Model Context Protocol Server, permitindo interagir com recursos AWS diretamente no Cursor AI.

## 📋 Índice

- [O que é AWS MCP Server](#o-que-é-aws-mcp-server)
- [Benefícios para o Projeto](#benefícios-para-o-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração no Cursor](#configuração-no-cursor)
- [Uso e Exemplos](#uso-e-exemplos)
- [Troubleshooting](#troubleshooting)

## 🎯 O que é AWS MCP Server

O **Model Context Protocol (MCP)** é um protocolo que permite ao Cursor AI (Claude) interagir diretamente com serviços externos. O **AWS MCP Server** conecta o Cursor aos seus recursos AWS, permitindo:

- 📊 **Consultar recursos**: Lambda, DynamoDB, S3, API Gateway
- 📝 **Ler logs**: CloudWatch Logs em tempo real
- 🔍 **Inspecionar configurações**: IAM, VPC, Security Groups
- 🚀 **Gerenciar recursos**: Criar, atualizar, deletar (via linguagem natural)
- 🐛 **Debug facilitado**: Ver erros e métricas sem sair do IDE

## 💡 Benefícios para o Projeto FinAssist

### Desenvolvimento Local
- Ver logs do Lambda em tempo real durante testes
- Verificar se DynamoDB está rodando e acessível
- Consultar configurações do SAM template

### Debug em Produção
- Ler logs de erros do CloudWatch diretamente no chat
- Verificar status das funções Lambda deployadas
- Consultar dados da tabela DynamoDB em produção
- Inspecionar configurações do API Gateway

### Monitoramento
- Verificar métricas de performance
- Ver invocações recentes de Lambda
- Analisar erros e exceções

## 📦 Pré-requisitos

### 1. Node.js e npm

O AWS MCP Server é distribuído via npm.

```bash
# Verificar se Node.js está instalado
node --version  # Deve ser >= 18.x

# Se não estiver instalado (WSL2/Ubuntu)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar instalação
node --version
npm --version
```

### 2. AWS CLI Configurado

```bash
# Verificar configuração
aws configure list

# Se não estiver configurado
aws configure
```

### 3. Credenciais AWS com Permissões

Certifique-se de que suas credenciais AWS têm permissões para:
- CloudWatch Logs (leitura)
- Lambda (leitura/listagem)
- DynamoDB (leitura/listagem)
- IAM (leitura - opcional)

## 🔧 Instalação

### Método 1: Instalação Global (Recomendado)

```bash
# Instalar AWS MCP Server globalmente
npm install -g @aws/mcp-server-aws

# Verificar instalação
which mcp-server-aws
# Deve retornar: /usr/local/bin/mcp-server-aws ou similar
```

### Método 2: Instalação Local no Projeto

```bash
# No diretório do projeto
cd /home/mizuno/projetos/mizuno/finassist

# Instalar como dependência de desenvolvimento
npm init -y  # Se não tiver package.json
npm install --save-dev @aws/mcp-server-aws
```

### Verificar Instalação

```bash
# Testar servidor MCP
npx @aws/mcp-server-aws --help
```

## ⚙️ Configuração no Cursor

### 1. Localizar Arquivo de Configuração

O Cursor usa configuração MCP em:
- **Linux/WSL2**: `~/.cursor/mcp_config.json`
- **Windows**: `%APPDATA%\Cursor\mcp_config.json`
- **macOS**: `~/Library/Application Support/Cursor/mcp_config.json`

### 2. Criar/Editar Configuração MCP

```bash
# Criar diretório se não existir
mkdir -p ~/.cursor

# Editar arquivo de configuração
nano ~/.cursor/mcp_config.json
```

### 3. Adicionar AWS MCP Server

Cole a seguinte configuração:

```json
{
  "mcpServers": {
    "aws": {
      "command": "npx",
      "args": [
        "-y",
        "@aws/mcp-server-aws"
      ],
      "env": {
        "AWS_PROFILE": "default",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

**Ajustes opcionais:**
- `AWS_PROFILE`: Use seu perfil AWS específico
- `AWS_REGION`: Região AWS padrão do seu projeto

### 4. Configuração Avançada (Múltiplos Perfis)

Se você trabalha com múltiplas contas AWS:

```json
{
  "mcpServers": {
    "aws-dev": {
      "command": "npx",
      "args": ["-y", "@aws/mcp-server-aws"],
      "env": {
        "AWS_PROFILE": "dev",
        "AWS_REGION": "us-east-1"
      }
    },
    "aws-prod": {
      "command": "npx",
      "args": ["-y", "@aws/mcp-server-aws"],
      "env": {
        "AWS_PROFILE": "prod",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

### 5. Reiniciar Cursor

```bash
# Fechar completamente o Cursor e reabrir
# Ou usar Command Palette: Developer: Reload Window
```

## 🚀 Uso e Exemplos

Após configurar, você pode usar comandos em linguagem natural no chat do Cursor:

### Consultar Funções Lambda

```
"Liste todas as funções Lambda na região us-east-1"
"Mostre as configurações da função WebhookFunction"
"Quais são as últimas 20 linhas de log da função WebhookFunction?"
```

### CloudWatch Logs

```
"Mostre os logs de erro da função Lambda nas últimas 2 horas"
"Há algum erro no CloudWatch Logs do grupo /aws/lambda/WebhookFunction?"
"Filtre logs que contenham 'OPENAI_API_KEY not configured'"
```

### DynamoDB

```
"Liste todas as tabelas DynamoDB"
"Mostre o schema da tabela FinAssist-Threads"
"Quantos itens tem na tabela FinAssist-Threads?"
```

### API Gateway

```
"Liste todos os APIs do API Gateway"
"Mostre as configurações do API FinAssistAPI"
"Quais são os endpoints configurados?"
```

### Debugging

```
"A função Lambda teve erros nas últimas 24 horas?"
"Qual foi o último erro da função WebhookFunction?"
"Mostre as métricas de invocação da última hora"
```

## 🧪 Testar Integração

### 1. Verificar Conexão

No chat do Cursor, digite:

```
"Liste as funções Lambda disponíveis"
```

Se configurado corretamente, o Cursor usará o AWS MCP para buscar informações reais da sua conta AWS.

### 2. Teste Completo

```
"Verifique o status dos seguintes recursos AWS:
1. Função Lambda: WebhookFunction (se existir em produção)
2. Tabela DynamoDB: FinAssist-Threads (se existir)
3. API Gateway: FinAssistAPI (se existir)
4. Logs recentes de erro"
```

## 🔧 Troubleshooting

### Erro: "MCP Server não encontrado"

**Causa**: Node.js ou npm não instalado, ou MCP não configurado.

**Solução**:
```bash
# Reinstalar MCP Server
npm install -g @aws/mcp-server-aws

# Verificar caminho
which mcp-server-aws

# Atualizar mcp_config.json com caminho completo
{
  "command": "/usr/local/bin/npx",
  "args": ["-y", "@aws/mcp-server-aws"]
}
```

### Erro: "AWS credentials not configured"

**Causa**: Credenciais AWS não configuradas ou perfil incorreto.

**Solução**:
```bash
# Verificar credenciais
aws configure list
aws sts get-caller-identity

# Reconfigurar se necessário
aws configure

# No mcp_config.json, certifique-se de usar o perfil correto
"AWS_PROFILE": "default"
```

### Erro: "Access Denied" ao consultar recursos

**Causa**: Credenciais AWS sem permissões necessárias.

**Solução**:

Adicione as seguintes políticas IAM ao seu usuário:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:ListFunctions",
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "logs:FilterLogEvents",
        "logs:GetLogEvents",
        "dynamodb:ListTables",
        "dynamodb:DescribeTable",
        "apigateway:GET"
      ],
      "Resource": "*"
    }
  ]
}
```

### MCP não aparece no Cursor

**Causa**: Configuração não foi carregada ou arquivo no local errado.

**Solução**:
```bash
# Verificar local correto do arquivo (WSL2)
ls -la ~/.cursor/mcp_config.json

# Se não existir, criar
mkdir -p ~/.cursor
nano ~/.cursor/mcp_config.json

# Copiar configuração do exemplo acima

# Reiniciar Cursor COMPLETAMENTE (fechar todas as janelas)
```

### Cursor não reconhece comandos MCP

**Causa**: Servidor MCP não está rodando.

**Solução**:
```bash
# Testar servidor manualmente
npx @aws/mcp-server-aws

# Verificar logs do Cursor
# Help → Toggle Developer Tools → Console
# Procurar por erros relacionados a MCP
```

## 📚 Recursos Adicionais

### Documentação Oficial

- **AWS MCP Server**: https://github.com/awslabs/mcp
- **Model Context Protocol**: https://modelcontextprotocol.io/
- **AWS Cloud Control API MCP**: https://aws.amazon.com/blogs/devops/introducing-aws-cloud-control-api-mcp-server-natural-language-infrastructure-management-on-aws/

### MCP Servers Úteis Adicionais

Além do AWS MCP, considere instalar:

1. **GitHub MCP**: Integração com repositórios GitHub
   ```bash
   npm install -g @modelcontextprotocol/server-github
   ```

2. **PostgreSQL MCP**: Se usar PostgreSQL (alternativa ao DynamoDB)
   ```bash
   npm install -g @modelcontextprotocol/server-postgres
   ```

## 🎯 Próximos Passos

Após configurar o AWS MCP:

1. **Teste a integração** com comandos simples
2. **Explore os recursos** disponíveis na sua conta AWS
3. **Use no dia-a-dia** para debug e monitoramento
4. **Combine com AWS Toolkit** extension para máxima produtividade

## 💡 Dicas de Uso

### Durante Desenvolvimento Local

```
"Mostre os logs do DynamoDB Local"
"Verifique se a API local está respondendo"
```

### Durante Debug em Produção

```
"Quais foram os últimos 10 erros na função Lambda em produção?"
"A tabela DynamoDB tem algum item com erro?"
"Mostre métricas de performance da última hora"
```

### Monitoramento Contínuo

```
"Crie um resumo do status de todos os recursos AWS do projeto FinAssist"
"Há algum alerta ou erro ativo nos últimos 30 minutos?"
```

---

**Dúvidas?** Consulte o [README principal](../README.md) ou a [documentação de setup](./SETUP_AMBIENTE.md).

**Pronto para usar AWS MCP!** 🚀

