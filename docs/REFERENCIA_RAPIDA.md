# ⚡ Referência Rápida - Assistente Financeiro

## 🎯 Visão em 30 Segundos

**O que é?** Assistente financeiro conversacional via WhatsApp
**Como funciona?** Você manda mensagem → IA processa → Registra no Excel
**Tecnologia:** Serverless AWS + OpenAI + Twilio + Microsoft Graph

---

## 📐 Arquitetura em Uma Página

### Componentes Principais

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  WhatsApp   │────▶│   Twilio    │────▶│ API Gateway │
│  (Usuário)  │     │  (Gateway)  │     │    (AWS)    │
└─────────────┘     └─────────────┘     └─────────────┘
                                                │
                                                ▼
                                        ┌───────────────┐
                                        │ Lambda Python │
                                        │ ┌───────────┐ │
                                        │ │ Handler   │ │
                                        │ │ Manager   │ │
                                        │ │ Services  │ │
                                        │ └───────────┘ │
                                        └───────┬───────┘
                                                │
                        ┌───────────────────────┼───────────────────────┐
                        ▼                       ▼                       ▼
                 ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
                 │   OpenAI    │        │  DynamoDB   │        │   Excel     │
                 │ Assistants  │        │  (Threads)  │        │  (OneDrive) │
                 └─────────────┘        └─────────────┘        └─────────────┘
```

### Fluxo de Mensagem (3 Passos)

1. **Receber**: WhatsApp → Twilio → API Gateway → Lambda
2. **Processar**: Lambda → OpenAI (+ tools) → Excel/DynamoDB
3. **Responder**: Lambda → API Gateway → Twilio → WhatsApp

---

## 📁 Estrutura de Código

```
finassist/
│
├── lambda_function.py          # 🚪 Entry point HTTP
├── conversation_manager.py     # 🎯 Orquestrador principal
│
├── services/                   # 🔌 Integrações externas
│   ├── openai_service.py      #   - OpenAI API
│   ├── twilio_service.py      #   - Twilio/TwiML
│   └── excel_service.py       #   - Microsoft Graph
│
├── data_access/                # 💾 Persistência
│   └── thread_repository.py   #   - DynamoDB
│
├── tools/                      # 🛠️ Ferramentas AI
│   └── tool_executor.py       #   - Executor
│
├── utils/                      # 🔧 Utilitários
│   ├── logger.py              #   - Logging
│   └── exceptions.py          #   - Exceções
│
├── config/                     # ⚙️ Configuração
│   └── settings.py            #   - Env vars
│
├── template.yaml               # 🏗️ IaC (SAM)
└── tests/                      # 🧪 Testes
```

---

## 🔄 Fluxo Completo (Adicionar Despesa)

```
1. "Gastei R$ 45 em almoço"
   ↓
2. Twilio → API Gateway → lambda_function.py
   ↓
3. conversation_manager.handle_incoming_message()
   ↓
4. Busca thread_id no DynamoDB (ou cria novo)
   ↓
5. Adiciona mensagem à thread do OpenAI
   ↓
6. Executa Assistant (Run)
   ↓
7. Assistant identifica: tool_call = "add_expense"
   ↓
8. tool_executor executa: excel_service.add_expense()
   ↓
9. Microsoft Graph API: adiciona linha no Excel
   ↓
10. Retorna resultado ao OpenAI
   ↓
11. OpenAI gera resposta: "Despesa registrada!"
   ↓
12. TwiML → Twilio → WhatsApp
```

---

## 🛠️ Ferramentas (Tools) Disponíveis

| Tool | Função | Parâmetros |
|------|--------|------------|
| `add_expense` | Adicionar despesa | date, category, description, amount |
| `get_expenses_by_category` | Consultar por categoria | category, start_date, end_date |
| `get_expenses_by_period` | Consultar por período | start_date, end_date |

---

## 💾 Dados Armazenados

### DynamoDB - Threads
```json
{
  "sender_id": "whatsapp:+5511999999999",  // 🔑 Primary Key
  "thread_id": "thread_abc123xyz",
  "created_at": "2025-10-21T10:30:00Z",
  "last_interaction": "2025-10-21T14:45:00Z"
}
```

### Excel - Despesas
| Data | Categoria | Descrição | Valor |
|------|-----------|-----------|-------|
| 2025-10-21 | Alimentação | Almoço | 45.00 |

---

## 🔐 Credenciais Necessárias

| Serviço | Credenciais | Onde Obter |
|---------|-------------|------------|
| OpenAI | API Key + Assistant ID | https://platform.openai.com |
| Twilio | Account SID + Auth Token | https://console.twilio.com |
| Microsoft | Client ID + Secret + Refresh Token | https://portal.azure.com |
| AWS | Access Key + Secret Key | `aws configure` |

---

## 🚀 Comandos Essenciais

### Setup Inicial
```bash
make setup              # Instalar dependências
cp env.example .env     # Configurar variáveis
make oauth-setup        # Obter refresh token MS Graph
make generate-env-json  # Gerar env.json para SAM
```

### Desenvolvimento Local
```bash
# Terminal 1: DynamoDB Local
make start-dynamodb-local

# Terminal 2: API Local
make start-api

# Terminal 3: Túnel Público
make start-ngrok
```

### Testes
```bash
make test           # Todos os testes
make test-unit      # Unitários
make test-integration  # Integração
make lint           # Verificar código
```

### Deploy AWS
```bash
make build          # Build do projeto
make deploy         # Deploy para AWS
```

---

## 📊 Métricas e Custos

### Performance
- **Cold Start**: ~1-2 segundos
- **Warm Request**: ~500ms - 2s (dependendo do OpenAI)
- **Timeout Lambda**: 60 segundos

### Custos Mensais (1000 mensagens)
| Serviço | Custo (USD) |
|---------|-------------|
| AWS Lambda | $0.20 |
| API Gateway | $3.50 |
| DynamoDB | $0.25 |
| CloudWatch Logs | $0.50 |
| OpenAI API (GPT-4) | $5 - $20 |
| OpenAI Whisper | $0.60 |
| Twilio WhatsApp (mensagens) | $5.00 |
| Twilio (número) | $1.15 |
| **Total** | **~$16 - $38** |

**Nota:** Twilio Sandbox (dev) é 100% gratuito mas limitado a números pré-aprovados.

---

## ⚠️ Limitações Conhecidas

- ⏱️ Timeout Lambda: 60 segundos
- 🔄 Cold Start: Primeira requisição mais lenta
- 📊 Excel API: Rate limits (pode throttle)
- 💰 Custos OpenAI: Variam com uso

---

## 🐛 Troubleshooting Rápido

### Erro: "Table does not exist"
```bash
make create-dynamodb-table
```

### Erro: "OPENAI_API_KEY not configured"
```bash
# Verificar .env
make generate-env-json
```

### Lambda timeout
Aumentar em `template.yaml`:
```yaml
Globals:
  Function:
    Timeout: 120
```

### Twilio não recebe mensagens
1. Verificar se ngrok está rodando
2. URL do webhook está correta no Twilio?
3. Ver logs: `sam logs --tail`

---

## 📚 Documentação Completa

- **[ARQUITETURA.md](ARQUITETURA.md)** - Arquitetura detalhada
- **[DIAGRAMAS.md](DIAGRAMAS.md)** - Diagramas visuais
- **[SETUP_AMBIENTE.md](SETUP_AMBIENTE.md)** - Guia de setup
- **[PRIMEIROS_PASSOS.md](PRIMEIROS_PASSOS.md)** - Checklist inicial
- **[README Principal](../README.md)** - Documentação geral

---

## 🎓 Conceitos-Chave

### Serverless (FaaS)
Execução de código sem gerenciar servidores. Paga-se apenas pelo tempo de execução.

### OpenAI Assistants API
Serviço da OpenAI que gerencia threads de conversação e executa ferramentas (tools).

### Thread
Histórico de conversação entre usuário e assistant, armazenado no OpenAI.

### Tool Call
Quando o assistant identifica que precisa executar uma função (ex: adicionar despesa).

### TwiML
XML usado pelo Twilio para responder mensagens WhatsApp.

### DynamoDB
Banco NoSQL serverless da AWS. Usado para mapear usuário ↔ thread_id.

### SAM (Serverless Application Model)
Framework AWS para definir e deployar aplicações serverless via IaC.

---

## 🔗 Links Rápidos

**Produção:**
- OpenAI Platform: https://platform.openai.com
- Twilio Console: https://console.twilio.com
- Azure Portal: https://portal.azure.com
- AWS Console: https://console.aws.amazon.com

**APIs:**
- OpenAI Docs: https://platform.openai.com/docs/assistants
- Twilio Docs: https://www.twilio.com/docs/whatsapp
- MS Graph Docs: https://docs.microsoft.com/graph

**Desenvolvimento:**
- AWS SAM: https://docs.aws.amazon.com/sam
- Python 3.11: https://docs.python.org/3.11
- pytest: https://docs.pytest.org

---

**Atualizado em**: 21/10/2025
**Versão**: 1.0

> 💡 **Dica**: Salve este arquivo como favorito! É seu guia de referência rápida para o projeto.


