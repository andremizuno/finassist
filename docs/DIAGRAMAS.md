# 📊 Diagramas do Sistema - Assistente Financeiro

Este documento contém diagramas visuais da arquitetura usando Mermaid.

## 🏗️ Diagrama de Arquitetura Geral

```mermaid
graph TB
    subgraph "Usuário"
        A[👤 Usuário WhatsApp]
    end

    subgraph "Gateway Externo"
        B[📱 Twilio API<br/>WhatsApp Gateway]
    end

    subgraph "AWS Cloud"
        C[🌐 API Gateway<br/>POST /webhook/whatsapp]

        subgraph "Lambda Function"
            D[⚡ lambda_function.py<br/>HTTP Handler]
            E[🎯 conversation_manager.py<br/>Orquestrador]

            subgraph "Services"
                F1[OpenAI Service]
                F2[Audio Service]
                F3[Twilio Service]
                F4[Excel Service]
            end

            subgraph "Data Access"
                G[Thread Repository]
            end

            subgraph "Tools"
                H[Tool Executor]
            end
        end

        I[💾 DynamoDB<br/>Threads Table]
    end

    subgraph "APIs Externas"
        J[🤖 OpenAI<br/>Assistants API +<br/>Whisper API]
        K[📊 Microsoft Graph<br/>Excel/OneDrive]
        L[📱 Twilio<br/>Media API]
    end

    A -->|Mensagem<br/>Texto/Áudio| B
    B -->|Webhook POST| C
    C -->|Event| D
    D --> E
    E --> F1
    E --> F2
    E --> F3
    E --> F4
    E --> G
    E --> H

    G <-->|Read/Write| I
    F1 <-->|Assistants API| J
    F2 -->|Download Áudio| L
    F2 -->|Transcrição| J
    F4 <-->|API Calls| K
    H --> F4

    D -->|TwiML| C
    C -->|Response| B
    B -->|Mensagem| A

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1e1
    style D fill:#ffe1e1
    style E fill:#ffe1e1
    style I fill:#e1ffe1
    style J fill:#f0e1ff
    style K fill:#f0e1ff
```

---

## 🔄 Fluxo de Processamento de Mensagem

```mermaid
sequenceDiagram
    actor User as 👤 Usuário
    participant WA as WhatsApp
    participant Twilio as 📱 Twilio
    participant APIGW as 🌐 API Gateway
    participant Lambda as ⚡ Lambda
    participant CM as 🎯 Conversation Manager
    participant AS as 🎤 Audio Service
    participant TR as 💾 Thread Repo
    participant DDB as DynamoDB
    participant OAI as 🤖 OpenAI
    participant Whisper as 🎙️ Whisper API
    participant TE as 🔧 Tool Executor
    participant Excel as 📊 Excel API

    User->>WA: Envia mensagem<br/>(texto/áudio)
    WA->>Twilio: Encaminha
    Twilio->>APIGW: POST /webhook/whatsapp<br/>(+ MediaUrl se áudio)
    APIGW->>Lambda: Invoca função

    Lambda->>CM: handle_incoming_message()<br/>(texto, media_url)

    alt Mensagem contém áudio
        CM->>AS: process_audio_message(media_url)
        AS->>Twilio: Download áudio<br/>(com autenticação)
        Twilio-->>AS: Arquivo de áudio
        AS->>Whisper: Transcrever (pt-BR)
        Whisper-->>AS: Texto transcrito
        AS-->>CM: Transcrição
        CM->>CM: Combinar texto + transcrição
    end

    CM->>TR: get_thread_id(sender_id)
    TR->>DDB: Query thread
    DDB-->>TR: thread_id ou null

    alt Thread não existe
        TR->>OAI: create_thread()
        OAI-->>TR: novo thread_id
        TR->>DDB: save_thread_id()
    end

    TR-->>CM: thread_id

    CM->>OAI: add_message(thread_id, mensagem)
    OAI-->>CM: success

    CM->>OAI: run_assistant(thread_id)
    OAI-->>CM: run_id

    loop Polling até completar
        CM->>OAI: get_run_status(run_id)
        OAI-->>CM: status

        alt Status = requires_action
            OAI-->>CM: tool_calls
            CM->>TE: execute_tools(tool_calls)
            TE->>Excel: add_expense() ou get_expenses()
            Excel-->>TE: resultado
            TE-->>CM: tool_outputs
            CM->>OAI: submit_tool_outputs()
        end
    end

    CM->>OAI: get_latest_response()
    OAI-->>CM: resposta final

    CM-->>Lambda: texto resposta
    Lambda-->>APIGW: TwiML XML
    APIGW-->>Twilio: HTTP 200
    Twilio-->>WA: Envia resposta
    WA-->>User: Exibe mensagem
```

---

## 🛠️ Fluxo de Execução de Tool (Adicionar Despesa)

```mermaid
flowchart TD
    A[OpenAI Assistant<br/>identifica intenção] --> B{Requires Action?}
    B -->|Sim| C[Tool Call:<br/>add_expense]
    B -->|Não| Z[Retorna resposta direta]

    C --> D[Tool Executor<br/>recebe chamada]

    D --> E[Parse argumentos:<br/>date, category, description, amount]

    E --> F[Excel Service:<br/>add_expense]

    F --> G[Obter/renovar<br/>Access Token]

    G --> H{Token válido?}
    H -->|Não| I[Renovar via<br/>Refresh Token]
    I --> J[Microsoft Graph API:<br/>POST /oauth2/token]
    J --> K[Novo Access Token]
    K --> L[Continua]

    H -->|Sim| L

    L --> M[Microsoft Graph API:<br/>POST /workbook/tables/rows]

    M --> N{Sucesso?}
    N -->|Sim| O[Retorna:<br/>status: success]
    N -->|Erro| P[Retorna:<br/>status: error]

    O --> Q[Submit Tool Outputs<br/>para OpenAI]
    P --> Q

    Q --> R[OpenAI processa<br/>resultado]

    R --> S[Gera resposta final<br/>para usuário]

    S --> T[Retorna texto]

    style C fill:#ffe1e1
    style F fill:#e1f5ff
    style M fill:#e1ffe1
    style Q fill:#f0e1ff
```

---

## 🎤 Fluxo de Processamento de Áudio (Whisper)

```mermaid
flowchart TD
    A[Usuário envia<br/>mensagem de voz<br/>pelo WhatsApp] --> B[Twilio recebe áudio]
    
    B --> C[Webhook POST<br/>com MediaUrl0]
    
    C --> D[Lambda extrai<br/>media_url e<br/>media_content_type]
    
    D --> E{É áudio?}
    
    E -->|Sim| F[Audio Service:<br/>process_audio_message]
    E -->|Não| Z[Processa como<br/>texto normal]
    
    F --> G[Download áudio<br/>da URL do Twilio]
    
    G --> H[HTTP GET com<br/>Basic Auth<br/>Account SID + Token]
    
    H --> I{Download OK?}
    
    I -->|Não| J[Log erro +<br/>mensagem genérica]
    I -->|Sim| K[Bytes do arquivo<br/>áudio OGG/MP3]
    
    K --> L[Whisper API:<br/>transcrever áudio]
    
    L --> M[POST /audio/transcriptions<br/>model: whisper-1<br/>language: pt]
    
    M --> N{Transcrição OK?}
    
    N -->|Não| O[Log erro +<br/>fallback para texto]
    N -->|Sim| P[Texto transcrito<br/>em português]
    
    P --> Q{Tem texto<br/>também?}
    
    Q -->|Sim| R[Combinar:<br/>texto +<br/>transcrição]
    Q -->|Não| S[Usar apenas<br/>transcrição]
    
    R --> T[Mensagem final<br/>para Assistant]
    S --> T
    O --> T
    J --> T
    
    T --> U[Continua fluxo<br/>normal do Assistant]
    
    style F fill:#ffe1e1
    style L fill:#e1f5ff
    style P fill:#e1ffe1
    style T fill:#f0e1ff
```

**Formatos de Áudio Suportados:**
- OGG (padrão WhatsApp)
- MP3, MP4, MPEG
- M4A, WAV, WEBM

**Limite:** 25 MB por arquivo

---

## 📁 Arquitetura de Módulos

```mermaid
graph LR
    subgraph "Entry Point"
        A[lambda_function.py]
    end

    subgraph "Core"
        B[conversation_manager.py]
    end

    subgraph "Services Layer"
        C1[openai_service.py]
        C2[audio_service.py]
        C3[twilio_service.py]
        C4[excel_service.py]
    end

    subgraph "Data Layer"
        D[thread_repository.py]
    end

    subgraph "Tools Layer"
        E[tool_executor.py]
    end

    subgraph "Utils"
        F1[logger.py]
        F2[exceptions.py]
    end

    subgraph "Config"
        G[settings.py]
    end

    A --> B
    A --> C3
    A --> F1

    B --> C1
    B --> C2
    B --> C3
    B --> C4
    B --> D
    B --> E
    B --> F1
    B --> F2

    C1 --> F1
    C2 --> F1
    C3 --> F1
    C4 --> F1
    C4 --> G

    D --> F1
    D --> F2

    E --> C4
    E --> F1
    E --> F2

    style A fill:#ff6b6b
    style B fill:#4ecdc4
    style C1 fill:#95e1d3
    style C2 fill:#95e1d3
    style C3 fill:#95e1d3
    style C4 fill:#95e1d3
    style D fill:#f9ca24
    style E fill:#6c5ce7
```

---

## 🗄️ Modelo de Dados DynamoDB

```mermaid
erDiagram
    THREADS {
        string sender_id PK
        string thread_id
        datetime created_at
        datetime last_interaction
        int message_count
        string user_name
    }
```

**Descrição:**
- `sender_id`: Número WhatsApp (formato: `whatsapp:+5511999999999`)
- `thread_id`: ID da thread do OpenAI (formato: `thread_abc123xyz`)
- `created_at`: Timestamp de criação da thread
- `last_interaction`: Timestamp da última mensagem
- `message_count`: Contador de mensagens trocadas
- `user_name`: Nome do usuário (opcional)

---

## 📊 Estrutura da Planilha Excel

```mermaid
classDiagram
    class Despesas {
        +Date data
        +String categoria
        +String descricao
        +Number valor
        +String observacoes
    }
```

**Exemplo de Dados:**

| Data | Categoria | Descrição | Valor | Observações |
|------|-----------|-----------|-------|-------------|
| 2025-10-21 | Alimentação | Almoço | 45.00 | Restaurante X |
| 2025-10-20 | Transporte | Uber | 25.50 | Casa → Trabalho |
| 2025-10-19 | Saúde | Farmácia | 68.90 | Medicamentos |

---

## 🔐 Fluxo de Autenticação Microsoft Graph

```mermaid
sequenceDiagram
    participant User as 👤 Usuário
    participant Setup as 🔧 Setup Script
    participant Azure as 🔐 Azure AD
    participant Lambda as ⚡ Lambda
    participant Graph as 📊 Graph API

    Note over User,Azure: Fase 1: Setup Inicial (Uma vez)

    User->>Setup: make oauth-setup
    Setup->>Azure: Authorization Request
    Azure->>User: Tela de login
    User->>Azure: Credenciais + Consent
    Azure->>Setup: Authorization Code
    Setup->>Azure: POST /token<br/>(code + credentials)
    Azure->>Setup: Access Token +<br/>Refresh Token
    Setup->>User: Exibe Refresh Token<br/>(adicionar ao .env)

    Note over Lambda,Graph: Fase 2: Uso em Produção

    Lambda->>Lambda: Verificar Access Token

    alt Token expirado
        Lambda->>Azure: POST /token<br/>(refresh_token)
        Azure->>Lambda: Novo Access Token
    end

    Lambda->>Graph: API Request<br/>(Authorization: Bearer token)
    Graph->>Lambda: Dados do Excel
```

---

## ⚙️ Ciclo de Vida do Assistant Run

```mermaid
stateDiagram-v2
    [*] --> queued: create_run()

    queued --> in_progress: Processando

    in_progress --> requires_action: Tool call necessário
    in_progress --> completed: Resposta pronta
    in_progress --> failed: Erro
    in_progress --> expired: Timeout

    requires_action --> in_progress: submit_tool_outputs()

    completed --> [*]: get_response()
    failed --> [*]: handle_error()
    expired --> [*]: handle_timeout()

    note right of requires_action
        Tool Executor executa
        ferramentas necessárias
        e retorna outputs
    end note
```

**Estados do Run:**

- **queued**: Run criado, aguardando processamento
- **in_progress**: OpenAI processando mensagem
- **requires_action**: Precisa executar tool call
- **completed**: Processamento concluído
- **failed**: Erro no processamento
- **expired**: Timeout (> 10 minutos)

---

## 🚀 Pipeline de Deploy

```mermaid
flowchart LR
    A[💻 Código Local] --> B[🔨 make build]
    B --> C[📦 SAM Build]
    C --> D[☁️ make deploy]
    D --> E[🚀 SAM Deploy]
    E --> F{Deploy Aprovado?}
    F -->|Sim| G[📤 Upload S3]
    G --> H[🏗️ CloudFormation<br/>Create/Update Stack]
    H --> I[⚡ Lambda Function]
    H --> J[🌐 API Gateway]
    H --> K[💾 DynamoDB Table]
    I --> L[✅ Stack Completo]
    J --> L
    K --> L
    F -->|Não| M[❌ Cancelado]

    style A fill:#e1f5ff
    style C fill:#fff4e1
    style E fill:#ffe1e1
    style L fill:#e1ffe1
    style M fill:#ffcccc
```

---

## 🧪 Ambiente de Desenvolvimento Local

```mermaid
graph TB
    subgraph "Máquina Local"
        A[🖥️ Cursor/VS Code]

        subgraph "Docker"
            B[🐳 DynamoDB Local<br/>Port 8000]
        end

        subgraph "SAM CLI"
            C[⚡ Lambda Local<br/>Port 3000]
        end

        D[🌐 ngrok<br/>Túnel HTTPS]
    end

    subgraph "Internet"
        E[📱 Twilio]
        F[👤 WhatsApp<br/>Usuário]
    end

    A --> C
    C <--> B
    C <--> D
    D <--> E
    E <--> F

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1e1
    style D fill:#f0e1ff
    style E fill:#e1ffe1
```

**Comandos:**
```bash
# Terminal 1
make start-dynamodb-local

# Terminal 2
make start-api

# Terminal 3
make start-ngrok
```

---

## 📈 Monitoramento e Observabilidade

```mermaid
graph LR
    subgraph "Lambda Execution"
        A[⚡ Lambda Function]
    end

    subgraph "AWS CloudWatch"
        B[📊 Metrics]
        C[📝 Logs]
        D[🔔 Alarms]
    end

    subgraph "AWS X-Ray (Opcional)"
        E[🔍 Traces]
        F[🗺️ Service Map]
    end

    A -->|Métricas| B
    A -->|Logs| C
    B -->|Triggers| D
    A -->|Traces| E
    E --> F

    B --> G[📧 SNS Notifications]
    D --> G

    style A fill:#ffe1e1
    style B fill:#e1f5ff
    style C fill:#e1f5ff
    style D fill:#ffe1e1
    style E fill:#f0e1ff
    style F fill:#f0e1ff
```

**Métricas Importantes:**
- Invocations (total de execuções)
- Errors (erros)
- Duration (tempo de execução)
- Throttles (limitações)
- Concurrent Executions (execuções simultâneas)

---

## 🔄 Estratégia de Retry e Error Handling

```mermaid
flowchart TD
    A[Requisição Recebida] --> B{Processar}
    B -->|Sucesso| C[✅ Retorna 200 + TwiML]
    B -->|Erro| D{Tipo de Erro?}

    D -->|OpenAI API Error| E[Log Error]
    D -->|DynamoDB Error| F[Log Error]
    D -->|Excel API Error| G[Log Error]
    D -->|Timeout| H[Log Error]
    D -->|Validation Error| I[Log Error]

    E --> J{Retry possível?}
    F --> J
    G --> J
    H --> K[❌ Resposta Amigável]
    I --> K

    J -->|Sim| L[Retry com backoff]
    J -->|Não| K

    L --> M{Sucesso?}
    M -->|Sim| C
    M -->|Não| K

    K --> N[🔔 Notificar usuário<br/>erro genérico]
    N --> O[📊 Registrar métrica]
    O --> P[Retorna 500 + TwiML erro]

    style C fill:#e1ffe1
    style K fill:#ffe1e1
    style P fill:#ffcccc
```

---

## 📚 Dependências do Projeto

```mermaid
graph TD
    A[finassist] --> B[openai]
    A --> C[boto3]
    A --> D[requests]
    A --> E[python-dotenv]
    A --> F[twilio]

    B --> G[httpx]
    C --> H[botocore]

    subgraph "Desenvolvimento"
        I[pytest]
        J[pytest-cov]
        K[black]
        L[flake8]
        M[moto]
    end

    A -.-> I
    A -.-> J
    A -.-> K
    A -.-> L
    A -.-> M

    style A fill:#4ecdc4
    style B fill:#95e1d3
    style C fill:#95e1d3
    style D fill:#95e1d3
    style E fill:#95e1d3
    style F fill:#95e1d3
    style I fill:#f9ca24
    style J fill:#f9ca24
    style K fill:#f9ca24
    style L fill:#f9ca24
    style M fill:#f9ca24
```

---

## 🎯 Decisões de Design - Trade-offs

```mermaid
mindmap
  root((Arquitetura<br/>Serverless))
    Escalabilidade
      Auto-scaling
      Sem limites
      Pay per use
    Performance
      Cold starts
      Otimizações
      Caching limitado
    Custo
      Sem custo fixo
      Paga pelo uso
      Free tier generoso
    Complexidade
      Simplicidade deploy
      Abstrações AWS
      Debugging distribuído
    Confiabilidade
      Managed services
      Retry automático
      Multi-AZ
```

---

**Documento criado em**: 21/10/2025
**Última atualização**: 22/10/2025
**Versão**: 1.1 - Adicionado suporte a áudio/Whisper API

> 💡 **Dica**: Para visualizar os diagramas Mermaid, use:
> - GitHub (suporte nativo)
> - VS Code/Cursor com extensão Mermaid Preview
> - [Mermaid Live Editor](https://mermaid.live)


