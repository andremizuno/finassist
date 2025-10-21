# 📖 Glossário Técnico - Assistente Financeiro

## Índice

- [Conceitos Gerais](#conceitos-gerais)
- [Arquitetura e Infraestrutura](#arquitetura-e-infraestrutura)
- [AWS Services](#aws-services)
- [OpenAI](#openai)
- [APIs e Integrações](#apis-e-integrações)
- [Desenvolvimento](#desenvolvimento)
- [Termos do Projeto](#termos-do-projeto)

---

## Conceitos Gerais

### Serverless
Modelo de computação em nuvem onde o provedor gerencia a infraestrutura automaticamente. O desenvolvedor foca apenas no código da aplicação, sem se preocupar com servidores, escalabilidade ou manutenção. Pagamento baseado apenas no uso real (execuções/tempo).

**Exemplo**: AWS Lambda executa código apenas quando necessário, cobrando por milissegundos de execução.

### FaaS (Function as a Service)
Subcategoria de serverless focada em executar funções individuais em resposta a eventos. Cada função é independente, stateless e efêmera.

**No projeto**: Lambda function processa cada mensagem WhatsApp como evento isolado.

### Event-Driven Architecture
Arquitetura baseada em eventos onde componentes reagem a ocorrências (eventos) ao invés de polling contínuo.

**No projeto**: Lambda é acionada quando uma mensagem WhatsApp chega via webhook.

### Stateless
Aplicações que não mantêm estado entre requisições. Cada execução é independente, sem memória de execuções anteriores.

**No projeto**: Lambda não guarda nada entre execuções; contexto vem do DynamoDB.

### Webhook
URL de callback onde um serviço externo envia notificações HTTP quando eventos ocorrem.

**No projeto**: Twilio envia POST para API Gateway quando usuário manda mensagem WhatsApp.

---

## Arquitetura e Infraestrutura

### IaC (Infrastructure as Code)
Prática de gerenciar infraestrutura através de código versionável, ao invés de configuração manual.

**No projeto**: `template.yaml` (SAM) define Lambda, API Gateway, DynamoDB como código.

### CloudFormation
Serviço AWS para provisionar recursos via templates (JSON/YAML). Base do AWS SAM.

**No projeto**: SAM compila `template.yaml` em CloudFormation stack.

### Stack
Conjunto de recursos AWS gerenciados como unidade única pelo CloudFormation.

**No projeto**: `financial-assistant-prod` stack contém Lambda + API Gateway + DynamoDB.

### Cold Start
Latência inicial quando uma função serverless é invocada após período de inatividade. Ocorre porque o provedor precisa inicializar o ambiente de execução.

**No projeto**: Primeira mensagem pode demorar ~1-2s; subsequentes são mais rápidas.

### Warm Start
Execução de função serverless que reutiliza ambiente já inicializado, resultando em latência menor.

### Throttling
Limitação de taxa de requisições imposta por APIs para evitar sobrecarga.

**No projeto**: Microsoft Graph API tem limites de requests/minuto.

---

## AWS Services

### Lambda
Serviço de computação serverless que executa código em resposta a eventos sem gerenciar servidores.

**No projeto**: Função Python 3.11 que processa mensagens WhatsApp.

**Configuração**:
- Runtime: Python 3.11
- Memory: 512 MB
- Timeout: 60 segundos

### API Gateway
Serviço gerenciado para criar, publicar e gerenciar APIs REST/WebSocket.

**No projeto**: Endpoint HTTP para webhook do Twilio (`POST /webhook/whatsapp`).

**Tipo**: REST API com integração Lambda Proxy.

### DynamoDB
Banco de dados NoSQL serverless, totalmente gerenciado, com latência de milissegundos.

**No projeto**: Armazena mapeamento entre usuários WhatsApp e threads OpenAI.

**Modelo**: Key-Value store com `sender_id` como partition key.

### CloudWatch
Serviço de monitoramento e observabilidade da AWS.

**No projeto**: Logs de execução da Lambda, métricas (invocations, errors, duration).

### IAM (Identity and Access Management)
Serviço de controle de acesso e permissões na AWS.

**No projeto**: Lambda Execution Role com permissões para DynamoDB e CloudWatch Logs.

### SAM (Serverless Application Model)
Framework open-source da AWS para definir e deployar aplicações serverless usando CloudFormation estendido.

**No projeto**: `template.yaml` define toda a infraestrutura; `sam deploy` provisiona tudo.

### SAM CLI
Ferramenta de linha de comando para desenvolvimento local, build e deploy de aplicações SAM.

**Comandos usados**: `sam build`, `sam local start-api`, `sam deploy`

---

## OpenAI

### Assistants API
Serviço da OpenAI para criar assistentes de IA com capacidades de conversação, gerenciamento de threads e execução de ferramentas.

**Vantagens**: Gerencia contexto automaticamente, suporta tool calling nativo.

### Thread
Sessão de conversação persistente entre usuário e assistant no OpenAI. Contém histórico completo de mensagens.

**No projeto**: Cada usuário WhatsApp tem uma thread única, identificada por `thread_id`.

### Message
Mensagem individual dentro de uma thread. Pode ser do usuário (`user`) ou do assistant (`assistant`).

### Run
Processo de execução do assistant sobre uma thread. Processa mensagens pendentes e gera resposta.

**Estados**: `queued`, `in_progress`, `requires_action`, `completed`, `failed`, `expired`

### Tool (Function)
Função customizada que o assistant pode chamar para realizar ações (ex: consultar dados, fazer cálculos).

**No projeto**: `add_expense`, `get_expenses_by_category`, `get_expenses_by_period`

### Tool Call
Requisição do assistant para executar uma tool com parâmetros específicos.

**Fluxo**:
1. Assistant identifica necessidade
2. Retorna `requires_action` com tool_calls
3. Aplicação executa funções
4. Retorna outputs para assistant
5. Assistant gera resposta final

### Function Calling
Capacidade de LLMs de identificar quando devem chamar funções externas e extrair parâmetros da conversação natural.

---

## APIs e Integrações

### Twilio
Plataforma de comunicação em nuvem que oferece APIs para SMS, voz, vídeo e WhatsApp.

**No projeto**: Gateway para mensagens WhatsApp Business API.

### TwiML (Twilio Markup Language)
Linguagem XML usada pelo Twilio para instruir como responder chamadas/mensagens.

**Exemplo**:
```xml
<Response>
    <Message>Olá! Como posso ajudar?</Message>
</Response>
```

### Microsoft Graph API
API unificada da Microsoft para acessar dados do Microsoft 365 (OneDrive, Excel, Outlook, Teams, etc.).

**No projeto**: Lê/escreve dados em planilha Excel no OneDrive do usuário.

### OAuth 2.0
Protocolo de autorização que permite aplicações acessarem recursos em nome do usuário sem compartilhar senha.

**No projeto**: Usado para acessar Excel no OneDrive via Microsoft Graph.

### Refresh Token
Token de longa duração usado para obter novos access tokens quando expiram.

**No projeto**: Armazenado em variável de ambiente, renova access token automaticamente.

### Access Token
Token de curta duração (geralmente 1 hora) usado para autenticar requisições à API.

**No projeto**: Renovado automaticamente via refresh token quando expira.

### Bearer Token
Tipo de access token enviado no header HTTP: `Authorization: Bearer {token}`

---

## Desenvolvimento

### Virtual Environment (venv)
Ambiente Python isolado com dependências próprias, evitando conflitos entre projetos.

**Comandos**:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
```

### Requirements File
Arquivo listando dependências Python do projeto.

**No projeto**:
- `requirements.txt`: Dependências de produção
- `requirements-dev.txt`: Ferramentas de desenvolvimento (pytest, flake8, etc.)

### Makefile
Arquivo com comandos automatizados para tarefas comuns do projeto.

**Exemplos**: `make setup`, `make test`, `make deploy`

### pytest
Framework de testes para Python, com recursos avançados de fixtures, parametrização e plugins.

**No projeto**: Testes unitários e de integração em `/tests`

### Mocking
Técnica de substituir dependências reais por objetos simulados em testes.

**No projeto**: Testes unitários mocam OpenAI, Twilio, DynamoDB para isolar lógica.

### Coverage
Métrica de quanto do código é executado durante testes. Relatório HTML mostra linhas cobertas/não cobertas.

**Comando**: `make test` gera relatório em `htmlcov/`

### Linting
Análise estática de código para identificar erros, má formatação ou violações de estilo.

**Ferramentas**: flake8 (linter), black (formatter)

### Docker
Plataforma para executar aplicações em containers isolados e portáveis.

**No projeto**: DynamoDB Local roda em container Docker para desenvolvimento.

### Docker Compose
Ferramenta para definir e executar aplicações Docker multi-container via arquivo YAML.

**No projeto**: `docker-compose.yml` configura DynamoDB Local.

### ngrok
Ferramenta que cria túnel HTTPS para expor aplicação local à internet.

**No projeto**: Expõe API local para Twilio enviar webhooks durante desenvolvimento.

---

## Termos do Projeto

### Sender ID
Identificador único do usuário, no formato do número WhatsApp Twilio.

**Formato**: `whatsapp:+5511999999999`

**Uso**: Partition key no DynamoDB; identifica thread do usuário.

### Thread ID
Identificador da thread de conversação no OpenAI.

**Formato**: `thread_abc123xyz`

**Uso**: Armazenado no DynamoDB, mapeado ao sender_id.

### Thread Repository
Camada de abstração para operações de persistência de threads no DynamoDB.

**Arquivo**: `data_access/thread_repository.py`

**Funções**: `get_thread_id()`, `save_thread_id()`

### Conversation Manager
Componente central que orquestra todo o fluxo de conversação.

**Arquivo**: `conversation_manager.py`

**Responsabilidades**:
- Gerenciar threads
- Coordenar OpenAI
- Executar tools
- Tratar erros

### Tool Executor
Componente que executa ferramentas (tools) solicitadas pelo OpenAI Assistant.

**Arquivo**: `tools/tool_executor.py`

**Função**: Parse tool_calls → Executa funções → Retorna outputs

### Service Layer
Camada de serviços que encapsula integrações com APIs externas.

**Arquivos**: `services/openai_service.py`, `services/twilio_service.py`, `services/excel_service.py`

### Lambda Handler
Função entry point da aplicação Lambda que recebe eventos do API Gateway.

**Arquivo**: `lambda_function.py`

**Assinatura**: `lambda_handler(event, context)`

### Environment Variables
Variáveis de configuração armazenadas fora do código (secrets, endpoints, etc.).

**Arquivos**: `.env` (local), `env.json` (SAM local), `template.yaml` (produção)

### Polling
Técnica de verificar repetidamente o status de uma operação até completar.

**No projeto**: Verifica status do Run do OpenAI a cada 1 segundo até `completed`.

### Retry Logic
Lógica de retentar operações que falharam temporariamente.

**No projeto**: Implementado para chamadas ao Microsoft Graph (renovação de token).

### Exception Handling
Tratamento estruturado de erros com exceções customizadas.

**No projeto**: `FinancialAssistantError`, `OpenAIAPIError`, `DynamoDBError`, `ToolExecutionError`

---

## Acrônimos Comuns

| Acrônimo | Significado | Descrição |
|----------|-------------|-----------|
| **API** | Application Programming Interface | Interface para interação entre sistemas |
| **REST** | Representational State Transfer | Estilo arquitetural para APIs |
| **HTTP** | HyperText Transfer Protocol | Protocolo de comunicação web |
| **JSON** | JavaScript Object Notation | Formato de dados estruturados |
| **XML** | eXtensible Markup Language | Formato de marcação (usado no TwiML) |
| **ARN** | Amazon Resource Name | Identificador único de recursos AWS |
| **SDK** | Software Development Kit | Conjunto de ferramentas de desenvolvimento |
| **CLI** | Command Line Interface | Interface de linha de comando |
| **IDE** | Integrated Development Environment | Ambiente de desenvolvimento (Cursor, VS Code) |
| **CRUD** | Create, Read, Update, Delete | Operações básicas de dados |
| **NoSQL** | Not Only SQL | Bancos não-relacionais (ex: DynamoDB) |
| **TTL** | Time To Live | Tempo de expiração de um recurso |
| **UUID** | Universally Unique Identifier | Identificador único universal |
| **CORS** | Cross-Origin Resource Sharing | Permissões de acesso entre domínios |
| **IAM** | Identity and Access Management | Gerenciamento de identidades e acessos |
| **VPC** | Virtual Private Cloud | Rede virtual isolada na AWS |
| **SID** | Security Identifier | Identificador de segurança (ex: Account SID do Twilio) |

---

## Conceitos de Python

### Decorator
Função que modifica o comportamento de outra função.

**Exemplo**: `@classmethod`, `@staticmethod`, `@property`

### Context Manager
Objeto que gerencia recursos com setup/cleanup automático via `with`.

**Exemplo**: Abertura de arquivos, conexões de banco

### Type Hints
Anotações de tipos em Python para melhor documentação e verificação.

**Exemplo**: `def add(a: int, b: int) -> int:`

### f-string
String formatada com interpolação de variáveis em Python 3.6+.

**Exemplo**: `f"Olá, {nome}!"`

### List Comprehension
Sintaxe concisa para criar listas a partir de iteráveis.

**Exemplo**: `[x*2 for x in range(10)]`

### Lambda Function (Python)
Função anônima de uma linha.

**Exemplo**: `lambda x: x * 2`

**Nota**: Não confundir com AWS Lambda!

---

## Padrões de Código

### Singleton
Padrão onde classe tem apenas uma instância global.

**No projeto**: Services são instanciados uma vez e reutilizados (`openai_service`, `twilio_service`).

### Dependency Injection
Padrão onde dependências são fornecidas externamente ao invés de criadas internamente.

**No projeto**: Services passados para managers ao invés de instanciados dentro.

### Repository Pattern
Abstração de acesso a dados, separando lógica de negócio da persistência.

**No projeto**: `ThreadRepository` abstrai operações do DynamoDB.

### Service Layer
Camada que encapsula lógica de negócio e integrações externas.

**No projeto**: `services/` contém integrações com APIs externas.

---

## Recursos Adicionais

### Documentação Relacionada
- [ARQUITETURA.md](ARQUITETURA.md) - Arquitetura completa
- [DIAGRAMAS.md](DIAGRAMAS.md) - Diagramas visuais
- [REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md) - Guia rápido

### Links Externos
- [AWS Glossário](https://docs.aws.amazon.com/general/latest/gr/glos-chap.html)
- [OpenAI Docs](https://platform.openai.com/docs)
- [Python Glossário](https://docs.python.org/3/glossary.html)

---

**Atualizado em**: 21/10/2025
**Versão**: 1.0

> 💡 **Dica**: Use Ctrl+F (Cmd+F no Mac) para buscar termos específicos neste glossário!


