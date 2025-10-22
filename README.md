# 💰 Assistente Financeiro Serverless

> Sistema inteligente de gerenciamento financeiro via WhatsApp, usando OpenAI Assistants API, AWS Lambda e Microsoft Excel.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Funcionalidades](#funcionalidades)
- [Pré-requisitos](#pré-requisitos)
- [Configuração](#configuração)
- [Desenvolvimento Local](#desenvolvimento-local)
- [Testes](#testes)
- [Deploy](#deploy)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

O Assistente Financeiro é uma aplicação serverless que permite gerenciar suas finanças pessoais através de conversas naturais no WhatsApp. Ele usa a OpenAI Assistants API para processamento de linguagem natural e armazena dados em planilhas Excel no OneDrive.

### Principais Características

- ✅ Conversação natural via WhatsApp (texto e áudio)
- ✅ Transcrição automática de mensagens de voz (Whisper API)
- ✅ Registro automático de despesas
- ✅ Consulta de gastos por categoria e período
- ✅ Armazenamento em Excel (OneDrive)
- ✅ Arquitetura 100% serverless (AWS Lambda)
- ✅ Ambiente de desenvolvimento local completo
- ✅ Testes automatizados

## 🏗️ Arquitetura

```
WhatsApp User
      ↓
   Twilio
      ↓
API Gateway (AWS)
      ↓
   Lambda Function
      ├─→ OpenAI Assistants API (conversa)
      ├─→ DynamoDB (threads/contexto)
      └─→ Microsoft Graph API (Excel)
```

> 📘 **Documentação Completa de Arquitetura**:
> - **[Arquitetura Detalhada](docs/ARQUITETURA.md)** - Visão completa dos componentes, fluxos e decisões arquiteturais
> - **[Diagramas Visuais](docs/DIAGRAMAS.md)** - Diagramas Mermaid interativos do sistema

### Tecnologias Utilizadas

- **Python 3.11**: Linguagem principal
- **AWS Lambda**: Execução serverless
- **AWS API Gateway**: Endpoint HTTP
- **AWS DynamoDB**: Persistência de threads
- **OpenAI Assistants API**: IA conversacional
- **Twilio**: Integração WhatsApp
- **Microsoft Graph API**: Acesso ao Excel
- **AWS SAM**: IaC e desenvolvimento local
- **Docker**: DynamoDB Local
- **pytest**: Testes automatizados

## 🚀 Funcionalidades

### Comandos Disponíveis

Você pode interagir com o assistente por **texto** ou **áudio de voz**:

- **Adicionar despesa**: "Gastei R$ 45 em almoço hoje"
- **Consultar gastos**: "Quanto gastei em alimentação este mês?"
- **Ver histórico**: "Mostre meus gastos da última semana"
- **Mensagens de voz**: Envie áudio diretamente pelo WhatsApp - será transcrito automaticamente

## 📦 Pré-requisitos

> **📘 Guias Detalhados Disponíveis:**
> - **[Guia Completo de Setup](docs/SETUP_AMBIENTE.md)** - Instruções detalhadas de instalação
> - **[Primeiros Passos](docs/PRIMEIROS_PASSOS.md)** - Checklist para começar
> - **[Script de Instalação Automática](scripts/install_dev_tools.sh)** - Instala AWS CLI, SAM CLI e ngrok automaticamente

### Instalação Rápida

Para instalar todas as ferramentas automaticamente:

```bash
# Tornar script executável
chmod +x scripts/install_dev_tools.sh

# Executar instalação
./scripts/install_dev_tools.sh

# Verificar ambiente
chmod +x scripts/verify_environment.sh
./scripts/verify_environment.sh
```

### Software Necessário

1. **Python 3.9+**
   ```bash
   python3 --version
   ```

2. **AWS CLI**
   ```bash
   # Instalação manual ou use: ./scripts/install_dev_tools.sh
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   aws --version
   ```

3. **AWS SAM CLI**
   ```bash
   # Instalação manual ou use: ./scripts/install_dev_tools.sh
   # macOS
   brew tap aws/tap
   brew install aws-sam-cli

   # WSL2/Linux: consulte docs/SETUP_AMBIENTE.md
   sam --version
   ```

4. **Docker Desktop**
   - Download: https://www.docker.com/products/docker-desktop
   - **WSL2**: Ativar integração em Settings → Resources → WSL Integration

5. **ngrok** (para desenvolvimento local)
   ```bash
   # Instalação manual ou use: ./scripts/install_dev_tools.sh
   # Download: https://ngrok.com/download
   ngrok config add-authtoken SEU_AUTHTOKEN
   ```

### Extensões Recomendadas do Cursor AI / VS Code

O projeto inclui configurações para extensões essenciais (`.vscode/extensions.json`).
O Cursor perguntará automaticamente se deseja instalá-las ao abrir o projeto.

**Extensões principais:**
- **AWS Toolkit** - Integração com AWS, logs CloudWatch, debug Lambda
- **Python** + **Pylance** - IntelliSense, debugging, type checking
- **Docker** - Gerenciar containers e imagens
- **Python Test Explorer** - Executar testes pytest visualmente
- **DotENV** - Syntax highlighting para `.env`
- **GitLens** - Git supercharged, blame, histórico

### AWS Toolkit - Integração AWS Recomendada

A extensão **AWS Toolkit** (já incluída nas extensões recomendadas) oferece integração completa com AWS:

**Funcionalidades:**
- ✅ Ver logs do CloudWatch em tempo real
- ✅ Listar e invocar funções Lambda localmente
- ✅ Navegação visual de recursos AWS
- ✅ Deploy e debug direto do IDE
- ✅ Explorar DynamoDB, S3, CloudFormation

**Instalação**: Automática quando aceitar extensões recomendadas do Cursor

### AWS MCP Server (Experimental - Futuro)

O AWS MCP Server oficial é uma opção mais avançada para integração via chat, mas requer configuração Docker mais complexa.

**Status**: Em desenvolvimento pela AWS Labs
**Guia de referência**: [docs/CONFIGURAR_AWS_MCP.md](docs/CONFIGURAR_AWS_MCP.md) (para usuários avançados)

Para mais detalhes sobre ferramentas, consulte: [docs/SETUP_AMBIENTE.md](docs/SETUP_AMBIENTE.md)

### Credenciais Necessárias

#### 1. OpenAI API
- Criar conta em https://platform.openai.com
- Obter API Key em https://platform.openai.com/api-keys
- Criar um Assistant em https://platform.openai.com/assistants

#### 2. Twilio (WhatsApp)
- Criar conta em https://www.twilio.com
- Configurar WhatsApp Sandbox ou número business
- Obter Account SID e Auth Token

#### 3. Microsoft Azure AD (Graph API)
- Acessar https://portal.azure.com
- Registrar nova aplicação em "Azure Active Directory" → "App Registrations"
- Configurar permissões: `User.Read`, `Files.ReadWrite.All`, `offline_access`
- Adicionar redirect URI: `http://localhost:8080/callback`
- Anotar Client ID e Client Secret

#### 4. AWS
```bash
aws configure
# Fornecer AWS Access Key ID e Secret Access Key
```

## ⚙️ Configuração

### 1. Clone e Setup Inicial

```bash
# Clonar repositório
git clone <seu-repositorio>
cd finassist

# Criar ambiente virtual e instalar dependências
make setup

# Ativar ambiente virtual
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar template de configuração
cp .env.example .env

# Editar .env com suas credenciais
nano .env  # ou seu editor preferido
```

Preencha todas as variáveis no arquivo `.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-...
ASSISTANT_ID=asst_...

# Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Microsoft Graph
MS_GRAPH_CLIENT_ID=...
MS_GRAPH_CLIENT_SECRET=...
MS_GRAPH_TENANT_ID=common
MS_GRAPH_REFRESH_TOKEN=...  # Obtenha com make oauth-setup

# DynamoDB Local
DYNAMODB_ENDPOINT_URL=http://localhost:8000
```

### 3. Obter Refresh Token do Microsoft Graph

```bash
# Execute o fluxo OAuth interativo
make oauth-setup

# Siga as instruções no navegador
# O refresh_token será exibido no terminal
# Adicione-o ao .env
```

### 4. Gerar env.json para SAM

```bash
make generate-env-json
```

## 💻 Desenvolvimento Local

### Iniciar Serviços

#### Terminal 1: DynamoDB Local

```bash
# Iniciar DynamoDB Local via Docker
make start-dynamodb-local

# Verificar se está rodando
docker ps | grep dynamodb
```

#### Terminal 2: API Local (SAM)

```bash
# Build e iniciar API local
make start-api

# A API estará disponível em http://127.0.0.1:3000
# Endpoint: POST http://127.0.0.1:3000/webhook/whatsapp
```

#### Terminal 3: ngrok (expor API)

```bash
# Expor API local para internet
make start-ngrok

# Copie a URL HTTPS exibida (ex: https://abc123.ngrok-free.app)
```

### Configurar Webhook do Twilio

1. Acesse https://console.twilio.com
2. Navegue até **Messaging** → **Try it out** → **Send a WhatsApp message**
3. Em **Sandbox settings** (ou configurações do número real):
   - **When a message comes in**: Cole a URL do ngrok + `/webhook/whatsapp`
   - Exemplo: `https://abc123.ngrok-free.app/webhook/whatsapp`
   - Método: **HTTP POST**
4. Salve

### Testar

Envie uma mensagem WhatsApp para o número do Twilio:

```
Olá!
```

Você deve receber uma resposta do assistente.

## 🧪 Testes

### Executar Todos os Testes

```bash
make test
```

### Testes Unitários

```bash
make test-unit
```

### Testes de Integração

```bash
# Requer DynamoDB Local rodando
make start-dynamodb-local
make test-integration
```

### Cobertura de Testes

Após executar `make test`, abra o relatório:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Qualidade de Código

```bash
# Verificar linting
make lint

# Formatar código
make format
```

## 🚀 Deploy

### Deploy para AWS

```bash
# Build e deploy
make deploy

# Siga o wizard interativo do SAM
# Forneça os parâmetros solicitados (chaves de API, etc.)
```

### Primeira Vez

No primeiro deploy, o SAM pedirá:

1. **Stack Name**: `financial-assistant-prod`
2. **AWS Region**: `us-east-1` (ou sua região preferida)
3. **Parâmetros**: Forneça todas as credenciais
4. **Confirmar mudanças**: `Y`
5. **Salvar configuração**: `Y`

### Deploys Subsequentes

```bash
# Usar configuração salva
sam deploy
```

### Configurar Webhook em Produção

Após o deploy, o SAM exibirá a URL da API:

```
Outputs:
  ApiUrl: https://xyz.execute-api.us-east-1.amazonaws.com/prod/webhook/whatsapp
```

Configure esta URL no webhook do Twilio (em produção, não sandbox).

## 📁 Estrutura do Projeto

```
finassist/
├── lambda_function.py           # Entry point do Lambda
├── conversation_manager.py      # Orquestrador principal
├── services/                    # Serviços externos
│   ├── openai_service.py       # OpenAI API
│   ├── audio_service.py        # Transcrição de áudio (Whisper)
│   ├── twilio_service.py       # Twilio/TwiML
│   └── excel_service.py        # Microsoft Graph
├── data_access/                 # Persistência
│   └── thread_repository.py    # DynamoDB
├── tools/                       # Ferramentas do Assistant
│   └── tool_executor.py        # Executor de tools
├── utils/                       # Utilitários
│   ├── logger.py               # Logging
│   └── exceptions.py           # Exceções
├── config/                      # Configurações
│   └── settings.py             # Variáveis de ambiente
├── tests/                       # Testes
│   ├── unit/                   # Testes unitários
│   └── integration/            # Testes de integração
├── scripts/                     # Scripts auxiliares
│   ├── generate_env_json.py    # Gera env.json
│   └── oauth_microsoft_graph.py # OAuth flow
├── template.yaml                # AWS SAM template
├── docker-compose.yml           # DynamoDB Local
├── Makefile                     # Automação
├── requirements.txt             # Dependências
├── requirements-dev.txt         # Deps de dev
└── README.md                    # Esta documentação
```

## 🔧 Troubleshooting

### Erro: "Table does not exist" no DynamoDB Local

```bash
# Recriar tabela
make create-dynamodb-table
```

### Erro: "OPENAI_API_KEY not configured"

Verifique se o `.env` está configurado e execute:

```bash
make generate-env-json
```

### Erro no OAuth do Microsoft Graph

1. Verifique se o redirect URI está correto no Azure AD: `http://localhost:8080/callback`
2. Verifique as permissões da aplicação
3. Execute novamente: `make oauth-setup`

### Lambda timeout em desenvolvimento local

Aumente o timeout no `template.yaml`:

```yaml
Globals:
  Function:
    Timeout: 120  # 2 minutos
```

### Twilio não recebe mensagens

1. Verifique se o ngrok está rodando
2. Verifique se a URL do webhook está correta no Twilio
3. Verifique logs do SAM CLI

### Testes falham

```bash
# Reinstalar dependências
make clean
make setup

# Executar testes novamente
make test
```

## 📚 Recursos Adicionais

### Documentação do Projeto

- **[Guia de Setup Completo](docs/SETUP_AMBIENTE.md)** - Instalação detalhada de todas as ferramentas
- **[Primeiros Passos](docs/PRIMEIROS_PASSOS.md)** - Checklist para novos desenvolvedores
- **[Configurar AWS MCP Server](docs/CONFIGURAR_AWS_MCP.md)** - Integração AWS com Cursor AI
- **[Quickstart](QUICKSTART.md)** - Guia rápido de uso

### Documentação Externa

- [OpenAI Assistants API Docs](https://platform.openai.com/docs/assistants/overview)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/)
- [AWS SAM Developer Guide](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda with Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)

## 📄 Licença

Este projeto é de uso educacional e demonstrativo.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**Desenvolvido com ❤️ para facilitar o gerenciamento de finanças pessoais.**

