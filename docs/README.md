# 📚 Documentação do Assistente Financeiro

Bem-vindo à documentação completa do projeto! Aqui você encontrará todos os recursos necessários para entender, configurar e desenvolver o sistema.

## 📖 Índice da Documentação

### 🏗️ Arquitetura e Design

- **[ARQUITETURA.md](ARQUITETURA.md)** - 📐 Documentação completa da arquitetura
  - Visão geral do sistema
  - Diagrama de componentes detalhado
  - Fluxos de dados e processamento
  - Camadas da aplicação
  - Integrações externas
  - Armazenamento e persistência
  - Segurança e escalabilidade
  - Decisões arquiteturais e trade-offs

- **[DIAGRAMAS.md](DIAGRAMAS.md)** - 📊 Diagramas visuais interativos
  - Diagrama de arquitetura geral (Mermaid)
  - Fluxo de processamento de mensagens (Sequência)
  - Execução de ferramentas (Flowchart)
  - Arquitetura de módulos
  - Modelo de dados
  - Fluxo de autenticação
  - Ciclo de vida do Assistant
  - Pipeline de deploy
  - Ambiente local
  - Monitoramento

### 🚀 Guias de Início

- **[PRIMEIROS_PASSOS.md](PRIMEIROS_PASSOS.md)** - ✅ Checklist para novos desenvolvedores
  - Passo a passo inicial
  - Verificações essenciais
  - Primeiro deploy

- **[SETUP_AMBIENTE.md](SETUP_AMBIENTE.md)** - 🔧 Guia completo de configuração
  - Instalação de ferramentas (AWS CLI, SAM, Docker, ngrok)
  - Configuração de credenciais
  - Setup do ambiente de desenvolvimento
  - Troubleshooting de instalação

### 🔌 Integrações

- **[CONFIGURAR_AWS_MCP.md](CONFIGURAR_AWS_MCP.md)** - ⚙️ AWS MCP Server (Avançado)
  - Integração AWS com Cursor AI via MCP
  - Configuração Docker
  - Comandos disponíveis
  - Para usuários avançados

- **[AWS_MCP_RESUMO.md](AWS_MCP_RESUMO.md)** - 📝 Resumo rápido do AWS MCP
  - Visão geral
  - Casos de uso
  - Links úteis

### 📖 Referências

- **[GUIA_PARA_LEIGOS.md](GUIA_PARA_LEIGOS.md)** - 💬 Guia super simples para não-técnicos
  - Explicação em linguagem cotidiana
  - Sem jargão técnico
  - Exemplos do dia a dia
  - Perguntas e respostas
  - Para quem não entende nada de tecnologia

- **[REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md)** - ⚡ Guia de referência em uma página
  - Visão em 30 segundos
  - Comandos essenciais
  - Troubleshooting rápido
  - Custos e performance

- **[GLOSSARIO.md](GLOSSARIO.md)** - 📚 Glossário técnico completo
  - Conceitos de arquitetura
  - Termos AWS
  - OpenAI e APIs
  - Padrões de código
  - Acrônimos

## 🎯 Começando

Se você é **novo no projeto**, recomendamos seguir esta ordem:

1. **Leia o [README principal](../README.md)** - Visão geral e quick start
2. **Configure seu ambiente**: [SETUP_AMBIENTE.md](SETUP_AMBIENTE.md)
3. **Siga o checklist**: [PRIMEIROS_PASSOS.md](PRIMEIROS_PASSOS.md)
4. **Entenda a arquitetura**: [ARQUITETURA.md](ARQUITETURA.md)
5. **Visualize o sistema**: [DIAGRAMAS.md](DIAGRAMAS.md)

## 🏗️ Para Desenvolvedores

Se você vai **desenvolver ou modificar o sistema**:

1. **Estude a arquitetura completa**: [ARQUITETURA.md](ARQUITETURA.md)
   - Entenda cada componente
   - Conheça os fluxos de dados
   - Revise as decisões arquiteturais

2. **Use os diagramas como referência**: [DIAGRAMAS.md](DIAGRAMAS.md)
   - Visualize fluxos de processamento
   - Compreenda integrações
   - Mapeie dependências

3. **Configure ferramentas avançadas** (opcional):
   - [CONFIGURAR_AWS_MCP.md](CONFIGURAR_AWS_MCP.md) para integração AWS

## 📊 Diagramas Rápidos

### Arquitetura Simplificada
```
Usuário WhatsApp
      ↓
   Twilio (Gateway)
      ↓
API Gateway (AWS)
      ↓
Lambda Function (Python)
  ├─→ OpenAI Assistant API (IA)
  ├─→ DynamoDB (Estado)
  └─→ Microsoft Graph (Excel)
```

### Tecnologias Principais
- **Backend**: Python 3.11, AWS Lambda
- **IA**: OpenAI Assistants API
- **Mensageria**: Twilio WhatsApp
- **Persistência**: DynamoDB + Excel (OneDrive)
- **IaC**: AWS SAM (CloudFormation)

## 🔗 Links Úteis

### Documentação Externa

**AWS:**
- [AWS SAM Developer Guide](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb/)

**APIs:**
- [OpenAI Assistants API](https://platform.openai.com/docs/assistants/overview)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/)

**Ferramentas:**
- [Docker Documentation](https://docs.docker.com/)
- [ngrok Documentation](https://ngrok.com/docs)
- [pytest Documentation](https://docs.pytest.org/)

### Recursos do Projeto

- [Repositório GitHub](../) - Código-fonte
- [Issues](../../issues) - Bugs e features
- [Pull Requests](../../pulls) - Contribuições

## 📝 Convenções

### Emojis na Documentação
- 📐 Arquitetura e design
- 🚀 Deploy e infraestrutura
- 🔧 Configuração e setup
- 📊 Dados e diagramas
- ⚙️ Ferramentas e integração
- 🧪 Testes
- 🔒 Segurança
- 📚 Documentação e guias
- ✅ Checklist e tarefas
- 💡 Dicas e observações

### Estrutura de Documentos
Todos os documentos seguem o padrão:
1. **Título e descrição**
2. **Índice** (para docs longos)
3. **Conteúdo organizado em seções**
4. **Exemplos práticos**
5. **Referências e links**

## 🤝 Contribuindo

Ao adicionar nova documentação:

1. **Coloque na pasta `/docs`**
2. **Use formato Markdown (.md)**
3. **Adicione ao índice** (este arquivo)
4. **Inclua exemplos práticos**
5. **Referencie de outros documentos** quando relevante
6. **Use diagramas** quando ajudar a clareza (Mermaid, ASCII art)

## 📅 Manutenção

**Última atualização**: 21/10/2025
**Versão da documentação**: 1.0

---

**Feito com ❤️ pela equipe FinAssist**


