# 🏗️ Arquitetura do Sistema - Assistente Financeiro Serverless

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Diagrama de Arquitetura Completo](#diagrama-de-arquitetura-completo)
3. [Componentes do Sistema](#componentes-do-sistema)
4. [Fluxo de Dados Detalhado](#fluxo-de-dados-detalhado)
5. [Camadas da Aplicação](#camadas-da-aplicação)
6. [Integrações Externas](#integrações-externas)
7. [Armazenamento e Persistência](#armazenamento-e-persistência)
8. [Segurança](#segurança)
9. [Escalabilidade e Performance](#escalabilidade-e-performance)
10. [Decisões Arquiteturais](#decisões-arquiteturais)

---

## 🎯 Visão Geral

O **Assistente Financeiro** é uma aplicação serverless construída com arquitetura FaaS (Function as a Service) que permite gerenciamento financeiro pessoal através de conversas naturais no WhatsApp.

### Princípios Arquiteturais

- ✅ **Serverless-First**: Sem gerenciamento de servidores, foco na lógica de negócio
- ✅ **Event-Driven**: Acionado por eventos (mensagens WhatsApp)
- ✅ **Pay-per-use**: Custo apenas quando em uso
- ✅ **Stateless Functions**: Funções sem estado, contexto em DynamoDB
- ✅ **Loose Coupling**: Componentes desacoplados via APIs
- ✅ **Single Responsibility**: Cada módulo com responsabilidade única

### Stack Tecnológica

| Camada | Tecnologia | Propósito |
|--------|-----------|-----------|
| **Interface** | WhatsApp + Twilio | Canal de comunicação com usuário |
| **Gateway** | AWS API Gateway | Endpoint HTTP para webhooks |
| **Compute** | AWS Lambda (Python 3.11) | Processamento serverless |
| **IA** | OpenAI Assistants API | Processamento de linguagem natural |
| **Persistência (Estado)** | AWS DynamoDB | Threads de conversação |
| **Persistência (Dados)** | Microsoft Excel (OneDrive) | Planilha de despesas |
| **IaC** | AWS SAM | Infrastructure as Code |

---

## 📐 Diagrama de Arquitetura Completo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CAMADA DE APRESENTAÇÃO                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                           ┌──────────▼──────────┐
                           │   👤 Usuário        │
                           │    WhatsApp         │
                           └──────────┬──────────┘
                                      │ Mensagem
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAMADA DE INTEGRAÇÃO EXTERNA                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                           ┌──────────▼──────────┐
                           │   📱 Twilio API     │
                           │  (WhatsApp Gateway) │
                           └──────────┬──────────┘
                                      │ HTTP POST
                                      │ (Webhook)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CAMADA DE AWS CLOUD                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                  ┌───────────────────▼───────────────────┐
                  │   🌐 AWS API Gateway (REST)          │
                  │   Endpoint: /webhook/whatsapp        │
                  │   Método: POST                       │
                  └───────────────────┬───────────────────┘
                                      │ Event
                                      │ (HTTP Request)
                                      ▼
              ┌───────────────────────────────────────────────┐
              │   ⚡ AWS Lambda Function                      │
              │   ┌──────────────────────────────────────┐   │
              │   │  lambda_function.py                  │   │
              │   │  - Handler HTTP                      │   │
              │   │  - Parse Twilio payload             │   │
              │   │  - Orquestração                     │   │
              │   └──────────────┬───────────────────────┘   │
              │                  │                            │
              │   ┌──────────────▼───────────────────────┐   │
              │   │  conversation_manager.py            │   │
              │   │  - Gerenciamento de threads         │   │
              │   │  - Coordenação OpenAI               │   │
              │   │  - Execução de tools                │   │
              │   └──────────────┬───────────────────────┘   │
              │                  │                            │
              │         ┌────────┴────────┬──────────────┐   │
              │         │                 │              │   │
              │   ┌─────▼─────┐  ┌───────▼────┐  ┌──────▼──┐
              │   │ services/ │  │data_access/│  │ tools/  │
              │   └───────────┘  └────────────┘  └─────────┘
              └─────┬───┬───┬─────────┬──────────────┬───────┘
                    │   │   │         │              │
        ┌───────────▼┐ ┌▼─────────┐  │  ┌───────────▼──────────┐
        │ OpenAI     │ │ Audio    │  │  │ Microsoft Graph API  │
        │ Assistant  │ │ Service  │  │  │ (Excel/OneDrive)     │
        │ API        │ │ (Whisper)│  │  └──────────────────────┘
        └────────────┘ └──────────┘  │
                           │          │  ┌───────────┐
                           └──────────┼─→│ Twilio    │
                                      │  │ Media API │
                                      │  └───────────┘
                                      │
                                        │
                              ┌─────────▼─────────┐
                              │  💾 DynamoDB      │
                              │  Table: Threads   │
                              │  Key: sender_id   │
                              └───────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAMADA DE ARMAZENAMENTO                               │
└─────────────────────────────────────────────────────────────────────────────┘
        │                                                  │
        │                                                  │
┌───────▼────────────┐                           ┌────────▼──────────┐
│  AWS DynamoDB      │                           │  Microsoft        │
│  - Threads         │                           │  OneDrive         │
│  - Contexto        │                           │  - Planilha Excel │
│  - Sessões         │                           │  - Despesas       │
└────────────────────┘                           └───────────────────┘
```

---

## 🔧 Componentes do Sistema

### 1. Entry Point - `lambda_function.py`

**Responsabilidade**: Handler principal da função Lambda

**Funções:**
- Receber eventos HTTP do API Gateway
- Parsear payload do Twilio (application/x-www-form-urlencoded)
- Extrair `sender_id` (número WhatsApp) e `message_body`
- Delegar processamento ao `ConversationManager`
- Gerar resposta TwiML para o Twilio
- Tratamento de erros e logging

**Fluxo:**
```python
Event (API Gateway)
  → Parse body (URL encoded)
  → Extract From/Body
  → conversation_manager.handle_incoming_message()
  → Generate TwiML response
  → Return HTTP 200 + XML
```

---

### 2. Orquestrador - `conversation_manager.py`

**Responsabilidade**: Coordenar todo o fluxo de conversação

**Componentes:**
- `ConversationManager`: Classe principal de orquestração

**Fluxo de Processamento:**

```
1. Obter/Criar Thread
   ↓
2. Adicionar Mensagem do Usuário
   ↓
3. Executar Assistant (Run)
   ↓
4. Polling Status do Run
   ↓
5. Verificar se há Tool Calls
   ├─ SIM → Executar Tools → Submeter Outputs → Volta ao passo 4
   └─ NÃO → Continua
   ↓
6. Obter Resposta Final
   ↓
7. Retornar Texto ao Usuário
```

**Responsabilidades Detalhadas:**
- Gerenciamento de threads do OpenAI Assistant
- Persistência de thread_id no DynamoDB
- Polling do status de execução do assistant
- Coordenação de execução de ferramentas (tools)
- Tratamento de timeouts e erros

---

### 3. Camada de Serviços - `services/`

#### 3.1. `openai_service.py`

**Responsabilidade**: Integração com OpenAI Assistants API

**Funções Principais:**
- `get_or_create_thread()`: Obter thread existente ou criar nova
- `add_message()`: Adicionar mensagem do usuário à thread
- `run_assistant()`: Iniciar execução do assistant
- `get_run_status()`: Verificar status do run
- `get_latest_response()`: Obter resposta mais recente
- `submit_tool_outputs()`: Enviar resultados de ferramentas

**Configuração:**
- API Key: OpenAI
- Assistant ID: Configurado no OpenAI Playground/API
- Thread Management: Threads persistem no OpenAI

---

#### 3.2. `audio_service.py`

**Responsabilidade**: Processamento de mensagens de áudio

**Funções Principais:**
- `download_audio(media_url)`: Baixa arquivo de áudio da URL do Twilio
- `transcribe_audio(audio_data, filename)`: Transcreve áudio usando Whisper API
- `process_audio_message(media_url)`: Orquestra download e transcrição completa

**Fluxo de Processamento:**
```
1. Receber media_url do Twilio
   ↓
2. Download do áudio com autenticação (Account SID + Auth Token)
   ↓
3. Transcrever usando OpenAI Whisper API (português)
   ↓
4. Retornar texto transcrito
```

**Formatos Suportados:**
- OGG (formato padrão do WhatsApp)
- MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM

**Autenticação:**
- Download: HTTP Basic Auth (Twilio credentials)
- Transcrição: OpenAI API Key (mesma do Assistant)

---

#### 3.3. `twilio_service.py`

**Responsabilidade**: Integração com Twilio e geração TwiML

**Funções Principais:**
- `create_twiml_response(message)`: Gera XML TwiML para responder WhatsApp
- `create_error_response()`: Gera TwiML de erro
- `validate_webhook()`: Valida assinatura do webhook (opcional)

**Exemplo TwiML:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Sua despesa foi registrada com sucesso!</Message>
</Response>
```

---

#### 3.4. `excel_service.py`

**Responsabilidade**: Integração com Microsoft Graph API (Excel)

**Funções Principais:**
- `get_access_token()`: Obter/renovar access token via refresh token
- `add_expense()`: Adicionar linha na planilha de despesas
- `get_expenses_by_category()`: Consultar gastos por categoria
- `get_expenses_by_period()`: Consultar gastos por período

**Autenticação:**
- OAuth 2.0 com Azure AD
- Refresh token armazenado em variável de ambiente
- Access token renovado automaticamente quando expira

**Estrutura da Planilha Excel:**
| Data | Categoria | Descrição | Valor | Observações |
|------|-----------|-----------|-------|-------------|
| 2025-10-21 | Alimentação | Almoço | 45.00 | - |

---

### 4. Camada de Dados - `data_access/`

#### `thread_repository.py`

**Responsabilidade**: Persistência de threads no DynamoDB

**Funções Principais:**
- `get_thread_id(sender_id)`: Buscar thread_id do usuário
- `save_thread_id(sender_id, thread_id)`: Salvar novo thread
- `update_thread_metadata()`: Atualizar metadados da thread

**Estrutura da Tabela DynamoDB:**
```json
{
  "sender_id": "whatsapp:+5511999999999",  // Partition Key (HASH)
  "thread_id": "thread_abc123xyz",         // OpenAI Thread ID
  "created_at": "2025-10-21T10:30:00Z",
  "last_interaction": "2025-10-21T14:45:00Z",
  "message_count": 42
}
```

**Configuração:**
- Tabela: `FinancialAssistantThreads`
- Billing Mode: PAY_PER_REQUEST (on-demand)
- Key: `sender_id` (String)

---

### 5. Execução de Ferramentas - `tools/`

#### `tool_executor.py`

**Responsabilidade**: Executar ferramentas chamadas pelo OpenAI Assistant

**Ferramentas Disponíveis:**

1. **`add_expense`**: Adicionar despesa
   - Parâmetros: `date`, `category`, `description`, `amount`
   - Ação: Chama `excel_service.add_expense()`

2. **`get_expenses_by_category`**: Consultar gastos por categoria
   - Parâmetros: `category`, `start_date`, `end_date`
   - Ação: Chama `excel_service.get_expenses_by_category()`

3. **`get_expenses_by_period`**: Consultar gastos por período
   - Parâmetros: `start_date`, `end_date`
   - Ação: Chama `excel_service.get_expenses_by_period()`

**Fluxo de Execução:**
```python
OpenAI Assistant → requires_action (tool_calls)
  → tool_executor.execute_tools(tool_calls)
  → Parse cada tool call
  → Executar função correspondente
  → Retornar outputs (JSON)
  → Submeter via openai_service.submit_tool_outputs()
```

---

## 🔄 Fluxo de Dados Detalhado

### Cenário 1: Adicionar Despesa

```
1. Usuário: "Gastei R$ 45 em almoço hoje"
   ↓
2. WhatsApp → Twilio → API Gateway → Lambda
   ↓
3. lambda_function.lambda_handler()
   - Parse: From=whatsapp:+5511999999999, Body="Gastei R$ 45..."
   ↓
4. conversation_manager.handle_incoming_message()
   ↓
5. thread_repository.get_thread_id(sender_id)
   - Se não existe: openai_service.create_thread()
   - Salva thread_id no DynamoDB
   ↓
6. openai_service.add_message(thread_id, message)
   ↓
7. openai_service.run_assistant(thread_id)
   ↓
8. Polling: Aguarda status = "requires_action"
   ↓
9. OpenAI retorna tool_call:
   {
     "name": "add_expense",
     "arguments": {
       "date": "2025-10-21",
       "category": "Alimentação",
       "description": "Almoço",
       "amount": 45.00
     }
   }
   ↓
10. tool_executor.execute_tools(tool_calls)
    ↓
11. excel_service.add_expense(...)
    - Obter access token (renova se expirado)
    - POST para Microsoft Graph API
    - Adiciona linha na planilha Excel
    ↓
12. Retorna output: {"status": "success", "message": "Despesa adicionada"}
    ↓
13. openai_service.submit_tool_outputs(run_id, outputs)
    ↓
14. Polling: Aguarda status = "completed"
    ↓
15. openai_service.get_latest_response(thread_id)
    - Retorna: "Sua despesa de R$ 45,00 em Alimentação foi registrada!"
    ↓
16. conversation_manager retorna texto
    ↓
17. twilio_service.create_twiml_response(texto)
    ↓
18. lambda_function retorna HTTP 200 + TwiML
    ↓
19. API Gateway → Twilio → WhatsApp → Usuário
```

---

### Cenário 2: Adicionar Despesa via Áudio

```
1. Usuário: [Envia áudio de voz] "Gastei quarenta e cinco reais no almoço hoje"
   ↓
2. WhatsApp → Twilio → API Gateway → Lambda
   ↓
3. lambda_function.lambda_handler()
   - Parse: From=whatsapp:+5511999999999
   - Body="" (vazio)
   - MediaUrl0="https://api.twilio.com/2010-04-01/.../Media/ME..."
   - MediaContentType0="audio/ogg"
   ↓
4. conversation_manager.handle_incoming_message(sender_id, "", media_url, "audio/ogg")
   ↓
5. Detecta que é áudio → audio_service.process_audio_message(media_url)
   ↓
6. audio_service.download_audio(media_url)
   - HTTP GET com Basic Auth (Twilio credentials)
   - Retorna bytes do arquivo OGG
   ↓
7. audio_service.transcribe_audio(audio_data)
   - Chama OpenAI Whisper API
   - Retorna: "Gastei quarenta e cinco reais no almoço hoje"
   ↓
8. conversation_manager._combine_text_and_audio("", transcription)
   - Retorna apenas a transcrição (sem texto adicional)
   ↓
9-19. [Mesmo fluxo do Cenário 1 a partir daqui]
    - Criar/obter thread
    - Adicionar mensagem transcrita
    - Executar Assistant
    - Tool call: add_expense
    - Resposta: "Despesa registrada!"
```

---

### Cenário 3: Consultar Gastos

```
1. Usuário: "Quanto gastei em alimentação este mês?"
   ↓
2-7. [Mesmo fluxo inicial até run_assistant]
   ↓
8. OpenAI retorna tool_call:
   {
     "name": "get_expenses_by_category",
     "arguments": {
       "category": "Alimentação",
       "start_date": "2025-10-01",
       "end_date": "2025-10-31"
     }
   }
   ↓
9. tool_executor.execute_tools(tool_calls)
   ↓
10. excel_service.get_expenses_by_category(...)
    - GET para Microsoft Graph API
    - Filtrar linhas da planilha
    - Somar valores
    ↓
11. Retorna output:
    {
      "total": 450.00,
      "transactions": [
        {"date": "2025-10-21", "description": "Almoço", "amount": 45.00},
        {"date": "2025-10-20", "description": "Jantar", "amount": 60.00},
        ...
      ]
    }
    ↓
12-19. [Mesmo fluxo de submit → polling → resposta]
    ↓
Usuário recebe: "Você gastou R$ 450,00 em Alimentação este mês, em 8 transações."
```

---

## 📚 Camadas da Aplicação

### Diagrama de Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  - lambda_function.py (HTTP Handler)                        │
│  - TwiML Response Generation                                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
│  - conversation_manager.py (Orchestration)                  │
│  - Tool execution logic                                     │
│  - Thread management                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┬──────────────┐
         │                               │              │
┌────────▼──────────┐  ┌────────────────▼──┐  ┌────────▼─────┐
│  SERVICE LAYER    │  │ DATA ACCESS LAYER │  │ TOOLS LAYER  │
│  - openai_service │  │ - thread_repository│  │ - tool_exec  │
│  - twilio_service │  └───────────────────┘  └──────────────┘
│  - excel_service  │
└───────────────────┘
```

### Responsabilidades por Camada

#### 1. Presentation Layer (Apresentação)
- Receber requisições HTTP
- Validar payloads
- Formatação de respostas (TwiML)
- Tratamento de erros HTTP

#### 2. Business Logic Layer (Lógica de Negócio)
- Orquestração de fluxos
- Regras de negócio
- Coordenação entre serviços
- Gerenciamento de estado da conversação

#### 3. Service Layer (Serviços)
- Integrações com APIs externas
- Autenticação e autorização
- Transformação de dados
- Retry e circuit breaker (quando aplicável)

#### 4. Data Access Layer (Acesso a Dados)
- CRUD no DynamoDB
- Gerenciamento de conexões
- Queries e filtros

#### 5. Tools Layer (Ferramentas)
- Execução de funções específicas
- Ponte entre OpenAI e serviços
- Validação de parâmetros de ferramentas

---

## 🔌 Integrações Externas

### 1. OpenAI APIs

#### 1.1. Assistants API

**Endpoint**: `https://api.openai.com/v1/`

**Recursos Utilizados:**
- `POST /threads`: Criar nova thread de conversação
- `GET /threads/{id}`: Obter thread existente
- `POST /threads/{id}/messages`: Adicionar mensagem
- `POST /threads/{id}/runs`: Executar assistant
- `GET /threads/{id}/runs/{run_id}`: Status da execução
- `POST /threads/{id}/runs/{run_id}/submit_tool_outputs`: Submeter outputs

**Autenticação:**
- Bearer Token: `Authorization: Bearer sk-...`

**Limites:**
- Rate limit: 60 requests/minute (tier dependente)
- Timeout: Configurável via polling

#### 1.2. Whisper API (Transcrição de Áudio)

**Endpoint**: `https://api.openai.com/v1/audio/transcriptions`

**Método**: `POST`

**Parâmetros:**
- `file`: Arquivo de áudio (binary)
- `model`: "whisper-1"
- `language`: "pt" (português)

**Formatos Suportados:**
- OGG, MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM

**Limite de Tamanho:**
- Máximo: 25 MB por arquivo

**Autenticação:**
- Bearer Token: `Authorization: Bearer sk-...` (mesma key do Assistant)

**Resposta:**
```json
{
  "text": "Texto transcrito do áudio"
}
```

---

### 2. Twilio WhatsApp API

**Endpoint**: Webhook configurável (API Gateway URL)

**Payload Recebido (POST):**

Mensagem de texto:
```
From=whatsapp:+5511999999999
To=whatsapp:+14155238886
Body=Olá, quanto gastei este mês?
MessageSid=SM1234567890abcdef
AccountSid=AC1234567890abcdef
NumMedia=0
```

Mensagem com áudio:
```
From=whatsapp:+5511999999999
To=whatsapp:+14155238886
Body=
NumMedia=1
MediaUrl0=https://api.twilio.com/2010-04-01/Accounts/.../Media/ME...
MediaContentType0=audio/ogg
MessageSid=SM1234567890abcdef
AccountSid=AC1234567890abcdef
```

**URLs de Mídia:**
- As URLs de mídia requerem autenticação HTTP Basic (Account SID + Auth Token)
- Mídia disponível por tempo limitado (alguns dias)
- Diversos formatos suportados: áudio, imagem, vídeo, documentos

**Resposta Esperada (TwiML):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Resposta do assistente</Message>
</Response>
```

**Autenticação:**
- Twilio valida webhook via signature (opcional)
- Credenciais: Account SID + Auth Token

---

### 3. Microsoft Graph API

**Endpoint**: `https://graph.microsoft.com/v1.0/`

**Recursos Utilizados:**
- `GET /me/drive/items/{item_id}/workbook/worksheets/{sheet_id}/range(address='A:E')`: Ler dados
- `POST /me/drive/items/{item_id}/workbook/tables/{table_id}/rows`: Adicionar linha
- `POST /oauth2/v2.0/token`: Renovar access token

**Autenticação:**
- OAuth 2.0
- Flow: Authorization Code → Refresh Token → Access Token
- Token renovation automática quando expira (3600s)

**Permissões Necessárias:**
- `User.Read`: Ler perfil do usuário
- `Files.ReadWrite.All`: Ler/escrever arquivos
- `offline_access`: Obter refresh token

---

### 4. AWS Services

#### API Gateway
- **Tipo**: REST API
- **Stage**: `prod`
- **Endpoint**: `POST /webhook/whatsapp`
- **Integração**: Lambda Proxy Integration

#### Lambda
- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 60 segundos
- **Concurrency**: Sem limite (on-demand)

#### DynamoDB
- **Billing Mode**: PAY_PER_REQUEST
- **Capacity**: Auto-scaling
- **Backup**: Point-in-time recovery (recomendado)

---

## 💾 Armazenamento e Persistência

### 1. DynamoDB - Estado de Conversação

**Propósito**: Manter mapeamento entre usuários e threads do OpenAI

**Tabela**: `FinancialAssistantThreads`

**Schema:**
```json
{
  "TableName": "FinancialAssistantThreads",
  "KeySchema": [
    {"AttributeName": "sender_id", "KeyType": "HASH"}
  ],
  "AttributeDefinitions": [
    {"AttributeName": "sender_id", "AttributeType": "S"}
  ],
  "BillingMode": "PAY_PER_REQUEST"
}
```

**Exemplo de Item:**
```json
{
  "sender_id": "whatsapp:+5511999999999",
  "thread_id": "thread_abc123xyz456",
  "created_at": "2025-10-21T10:30:00.000Z",
  "last_interaction": "2025-10-21T14:45:23.000Z",
  "message_count": 42,
  "user_name": "João Silva"
}
```

**Access Patterns:**
- Read: Por `sender_id` (Get Item)
- Write: Por `sender_id` (Put Item)
- Update: Por `sender_id` (Update Item)

---

### 2. OpenAI - Histórico de Conversação

**Propósito**: Armazenar todo o histórico de mensagens da conversação

**Gerenciamento:**
- Threads criadas pela API do OpenAI
- Persistem indefinidamente (até deletar manualmente)
- Contém todas as mensagens (usuário + assistant)

**Vantagens:**
- Contexto preservado entre interações
- Não precisa gerenciar histórico manualmente
- Suporta múltiplos "runs" na mesma thread

---

### 3. Microsoft OneDrive - Dados Financeiros

**Propósito**: Planilha Excel com dados de despesas

**Estrutura da Planilha:**

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| Data | Date | Data da despesa |
| Categoria | Text | Categoria (Alimentação, Transporte, etc.) |
| Descrição | Text | Descrição breve |
| Valor | Number | Valor em BRL |
| Observações | Text | Notas adicionais |

**Localização:**
- OneDrive pessoal ou business do usuário
- Caminho: Configurável (ex: `/Finanças/despesas.xlsx`)

**Vantagens:**
- Dados em formato familiar (Excel)
- Pode ser editado manualmente
- Fácil exportação e visualização

---

## 🔒 Segurança

### 1. Secrets Management

**Desenvolvimento Local:**
- `.env` file (nunca comitar!)
- `env.json` gerado para SAM Local

**Produção (Recomendado):**
- AWS Secrets Manager ou Systems Manager Parameter Store
- Rotação automática de secrets
- Auditoria de acessos

**Secrets Armazenados:**
- OpenAI API Key
- Twilio Auth Token
- Microsoft Graph Client Secret
- Microsoft Graph Refresh Token

---

### 2. Autenticação e Autorização

**Twilio → API Gateway:**
- Validação de webhook signature (opcional)
- IP whitelist (se necessário)

**Lambda → OpenAI:**
- API Key no header Authorization

**Lambda → Microsoft Graph:**
- OAuth 2.0 com refresh token
- Tokens de acesso com tempo de expiração

**Lambda → DynamoDB:**
- IAM Role com política restrita
- Apenas operações necessárias (GetItem, PutItem, UpdateItem)

---

### 3. Políticas IAM

**Lambda Execution Role:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/FinancialAssistantThreads"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

---

### 4. Proteção de Dados

**Em Trânsito:**
- HTTPS para todas as comunicações
- TLS 1.2+ obrigatório

**Em Repouso:**
- DynamoDB: Encryption at Rest (KMS)
- Excel: Protegido pelo OneDrive (Microsoft encryption)

**Dados Sensíveis:**
- Nenhum dado financeiro armazenado no DynamoDB
- Apenas thread_id (referência)
- Dados reais apenas no Excel do usuário

---

## ⚡ Escalabilidade e Performance

### 1. Escalabilidade Horizontal

**AWS Lambda:**
- Auto-scaling automático
- Concorrência: Até 1000 execuções simultâneas (padrão)
- Pode aumentar via request à AWS

**API Gateway:**
- Suporta milhões de requests por segundo
- Throttling configurável por estágio/rota

**DynamoDB:**
- PAY_PER_REQUEST: Escala automaticamente
- Suporta milhares de reads/writes por segundo

---

### 2. Otimizações de Performance

**Cold Start Mitigation:**
- Código otimizado (imports no topo)
- Dependências mínimas
- Reutilização de conexões HTTP (quando possível)

**Caching:**
- Access token do Microsoft Graph em memória (válido por 1h)
- Reutilização de clientes HTTP entre invocações

**Timeouts:**
- Lambda: 60s (ajustável)
- OpenAI polling: Intervalo de 1s
- Tool execution: Timeout de 60s

---

### 3. Custos Estimados

**Cenário**: 1000 mensagens/mês (uso típico individual)

#### 3.1. Custos de Infraestrutura AWS

| Serviço AWS | Custo Estimado (USD) | Detalhes |
|-------------|----------------------|----------|
| **AWS Lambda** | $0.20 | 1000 execuções × 512MB × ~3s médio |
| **API Gateway** | $3.50 | 1000 requests REST API |
| **DynamoDB** | $0.25 | Pay-per-request, ~2000 operações/mês |
| **CloudWatch Logs** | $0.50 | ~500MB logs/mês (opcional, pode desabilitar) |
| **Subtotal AWS** | **~$4.45** | |

**⚠️ Nota sobre CloudWatch:**
- O CloudWatch Logs é automaticamente habilitado pelo Lambda
- Primeiros 5GB/mês grátis no Free Tier, depois $0.50/GB
- Para economizar: reduzir logs ou desabilitar em produção

#### 3.2. Custos de APIs Externas

| Serviço Externo | Custo Estimado (USD) | Detalhes |
|-----------------|----------------------|----------|
| **OpenAI API (GPT-4)** | $5.00 - $20.00 | Depende do uso (tokens input/output) |
| **OpenAI Whisper** | $0.60 | ~100 áudios × 1min × $0.006/min |
| **Twilio WhatsApp (mensagens)** | $5.00 | 1000 msgs × $0.005/msg |
| **Twilio (número telefone)** | $1.15 | Opcional, se usar número próprio |
| **Microsoft 365 (opcional)** | $0.00 - $7.00 | Se usar conta pessoal = grátis |
| **Subtotal APIs** | **~$11.75 - $33.75** | |

#### 3.3. Total Consolidado

| Categoria | Custo (USD/mês) |
|-----------|-----------------|
| AWS (infra) | $4.45 |
| OpenAI (IA + áudio) | $5.60 - $20.60 |
| Twilio (WhatsApp + número) | $6.15 |
| Microsoft 365 | $0.00 - $7.00 |
| **TOTAL** | **$16 - $38/mês** |

**Em Reais (R$):** ~R$ 80-190/mês (câmbio @R$5,00)

---

#### 3.4. Custos Não Recorrentes (Setup Inicial)

| Item | Custo | Frequência |
|------|-------|------------|
| Registro domínio (opcional) | $12-15/ano | Anual |
| Certificado SSL | $0 | Grátis (Let's Encrypt/AWS) |
| Setup inicial AWS | $0 | Uma vez (Free Tier) |

---

#### 3.5. Opções para Reduzir Custos

##### ✅ Ambiente de Desenvolvimento (Twilio Sandbox)
- **Custo:** ~$10-28/mês (mensagens Twilio são gratuitas no Sandbox!)
- **Limitação:** Apenas números pré-aprovados que enviarem código de ativação
- **Ideal para:** Testes, desenvolvimento, uso pessoal
- **Economia:** $6.15/mês (não paga mensagens nem número)

##### ✅ Free Tier AWS (Novos Usuários)
- **Lambda:** 1M requests/mês grátis (sempre)
- **DynamoDB:** 25GB + 25 RCU/WCU grátis (sempre)
- **API Gateway:** 1M calls/mês grátis (primeiros 12 meses)
- **Economia:** ~$4/mês nos primeiros 12 meses

##### ✅ Alternativa WhatsApp: Meta Cloud API
- **Custo:** Primeiras 1000 conversas/mês **GRATUITAS**
- **Após 1000:** $0.005-0.09/conversa (varia por país)
- **Requer:** Integração diferente (não via Twilio)
- **Economia potencial:** $6.15/mês comparado ao Twilio

##### ✅ Otimizar OpenAI
- Usar GPT-3.5 Turbo ao invés de GPT-4: ~70% mais barato
- Limitar histórico de mensagens no contexto
- **Economia potencial:** $10-15/mês

---

#### 3.6. Custos Ocultos e Atenções

| Item | Descrição | Como Evitar |
|------|-----------|-------------|
| **Dados de saída AWS** | Transfer OUT para internet | Mínimo (apenas respostas JSON) |
| **Twilio números adicionais** | $1.15/mês por número | Usar apenas 1 número |
| **OpenAI token overflow** | Custos disparam com contextos longos | Limitar histórico, usar truncate |
| **DynamoDB hot partition** | Throttling = custo extra | PAY_PER_REQUEST evita isso |
| **CloudWatch métricas custom** | $0.30/métrica | Não usamos métricas custom |

**✅ Garantias:**
- **Não há cobrança por:**
  - VPC (não usamos)
  - NAT Gateway (não usamos)
  - Load Balancer (não usamos)
  - EC2 (não usamos)
  - S3 (não usamos no momento)
  - RDS (não usamos)

---

#### 3.7. Monitoramento de Custos

**Recomendações:**
1. **AWS Cost Explorer:** Monitore custos semanalmente
2. **AWS Budgets:** Configure alerta para > $10/mês
3. **Twilio Console:** Verifique uso de mensagens
4. **OpenAI Dashboard:** Acompanhe tokens consumidos

**Estimativa Conservadora (Worst Case):**
- **Mínimo (sandbox + baixo uso):** $10/mês
- **Típico (produção, 1000 msgs):** $16-38/mês
- **Alto (uso intenso, 3000+ msgs):** $25-55/mês

---

## 🎯 Decisões Arquiteturais

### 1. Por que Serverless (FaaS)?

**✅ Vantagens:**
- Sem gerenciamento de servidores
- Custo baseado em uso real
- Escalabilidade automática
- Deploy simplificado (SAM/CloudFormation)
- Foco na lógica de negócio

**❌ Trade-offs:**
- Cold starts (mitigado com otimizações)
- Limite de timeout (60s - suficiente para o caso de uso)
- Vendor lock-in AWS (mitigado com abstrações)

---

### 2. Por que OpenAI Assistants API (vs. Chat Completion)?

**✅ Vantagens:**
- Gerenciamento automático de threads
- Tool calling nativo
- Persistência de contexto
- Retry e error handling built-in

**❌ Trade-offs:**
- Custo ligeiramente maior
- Menos controle sobre prompts internos
- Dependência de serviço específico

---

### 3. Por que DynamoDB (vs. RDS/outros)?

**✅ Vantagens:**
- Serverless (sem servidor para gerenciar)
- Auto-scaling
- Latência baixa (< 10ms)
- Integração nativa com Lambda

**❌ Trade-offs:**
- Modelo de dados simples (NoSQL)
- Queries limitadas (sem JOIN)
- Custo por operação

---

### 4. Por que Excel no OneDrive (vs. banco de dados)?

**✅ Vantagens:**
- Formato familiar para usuários
- Fácil visualização e edição manual
- Não requer infraestrutura adicional
- Pode ser compartilhado facilmente

**❌ Trade-offs:**
- Performance inferior para grandes volumes
- Limitação de API (throttling)
- Dependência de conta Microsoft

---

### 5. Arquitetura Modular

**Princípios Aplicados:**

1. **Single Responsibility**: Cada módulo faz uma coisa
2. **Dependency Injection**: Serviços instanciados centralmente
3. **Loose Coupling**: Módulos se comunicam via interfaces claras
4. **High Cohesion**: Funções relacionadas agrupadas

**Benefícios:**
- Testabilidade (unit tests isolados)
- Manutenibilidade (mudanças localizadas)
- Extensibilidade (adicionar novos tools facilmente)

---

## 📝 Considerações Finais

### Melhorias Futuras

1. **Cache Redis/ElastiCache**: Para access tokens e dados frequentes
2. **SQS Queue**: Para processamento assíncrono de mensagens pesadas
3. **Step Functions**: Para orquestração de workflows complexos
4. **CloudWatch Alarms**: Para monitoramento proativo
5. **X-Ray Tracing**: Para debugging distribuído
6. **Multi-tenancy**: Suporte a múltiplos usuários com isolamento

### Limitações Conhecidas

1. **Timeout Lambda**: 60s pode ser insuficiente para conversas muito longas
2. **Throttling Excel API**: Limites de requests por minuto
3. **Cold Start**: Primeira requisição pode demorar ~1-2 segundos
4. **Sem cache**: Cada invocação refaz autenticação/queries

### Monitoramento

**Métricas Importantes:**
- Lambda invocations/errors/duration
- API Gateway 4xx/5xx errors
- DynamoDB consumed capacity
- OpenAI API latency
- Tool execution success rate

**Logs:**
- CloudWatch Logs: Todos os logs da aplicação
- X-Ray (opcional): Traces distribuídos

---

**Documento criado em**: 21/10/2025
**Versão**: 1.0
**Autores**: Equipe FinAssist

---


