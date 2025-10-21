# 🚀 Primeiros Passos - Guia Rápido para Começar

> Checklist completo para configurar o ambiente e começar a desenvolver no projeto FinAssist.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Checklist de Configuração](#checklist-de-configuração)
- [Fluxo de Trabalho Diário](#fluxo-de-trabalho-diário)
- [Comandos Essenciais](#comandos-essenciais)
- [Problemas Comuns](#problemas-comuns)

## 🎯 Visão Geral

Este guia fornece um checklist passo-a-passo para novos desenvolvedores configurarem o ambiente e começarem a trabalhar no projeto FinAssist.

**Tempo estimado de configuração**: 30-60 minutos (primeira vez)

## ✅ Checklist de Configuração

### Fase 1: Ferramentas Básicas (15 min)

#### ☐ 1.1 Verificar Sistema Operacional
- [ ] WSL2 está instalado e atualizado (se Windows)
- [ ] Terminal funcionando corretamente

```bash
wsl --version  # Windows
uname -a       # Linux
```

#### ☐ 1.2 Instalar Python 3.9+
- [ ] Python está instalado
- [ ] pip está disponível
- [ ] venv está disponível

```bash
python3 --version  # Deve retornar 3.9 ou superior
pip3 --version
python3 -m venv --help
```

Se não estiver instalado:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

#### ☐ 1.3 Instalar Git
- [ ] Git está instalado
- [ ] Git está configurado

```bash
git --version
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```

### Fase 2: Ferramentas AWS e Docker (20 min)

#### ☐ 2.1 Instalar AWS CLI
- [ ] AWS CLI instalado
- [ ] AWS CLI configurado

```bash
# Verificar instalação
aws --version

# Se não estiver instalado, usar script automatizado:
./scripts/install_dev_tools.sh

# Configurar credenciais
aws configure
```

#### ☐ 2.2 Instalar SAM CLI
- [ ] SAM CLI instalado
- [ ] SAM CLI funcionando

```bash
# Verificar instalação
sam --version

# Se não estiver instalado:
./scripts/install_dev_tools.sh
```

#### ☐ 2.3 Configurar Docker
- [ ] Docker Desktop instalado (Windows)
- [ ] Docker funcionando no WSL2
- [ ] Docker testado com hello-world

```bash
# Verificar Docker
docker --version
docker ps

# Testar
docker run hello-world
```

**Importante**: No Windows, certifique-se de ativar a integração WSL2 no Docker Desktop:
- Docker Desktop → Settings → Resources → WSL Integration
- Ativar sua distribuição WSL2
- Apply & Restart

### Fase 3: Ferramentas de Desenvolvimento (10 min)

#### ☐ 3.1 Instalar ngrok
- [ ] ngrok instalado
- [ ] ngrok configurado com authtoken

```bash
# Verificar instalação
ngrok version

# Se não estiver instalado:
./scripts/install_dev_tools.sh

# Configurar authtoken (obtenha em https://dashboard.ngrok.com)
ngrok config add-authtoken SEU_AUTHTOKEN
```

#### ☐ 3.2 Instalar Extensões do Cursor AI
- [ ] Abrir Cursor AI
- [ ] Instalar extensões recomendadas quando solicitado
- [ ] Ou instalar manualmente:
  - AWS Toolkit
  - Python
  - Pylance
  - Docker
  - Python Test Explorer
  - DotENV
  - GitLens

#### ☐ 3.3 Usar AWS Toolkit (Incluída nas extensões)

A extensão **AWS Toolkit** é a forma recomendada de interagir com recursos AWS:

**Funcionalidades**:
- Ver logs do CloudWatch
- Explorar funções Lambda
- Navegação visual de recursos
- Deploy e debug integrado

**Instalação**: Automática ao aceitar extensões recomendadas

---

**Nota sobre AWS MCP Server**: O MCP Server da AWS é experimental e requer configuração Docker avançada. Para uso avançado, consulte [CONFIGURAR_AWS_MCP.md](./CONFIGURAR_AWS_MCP.md)

### Fase 4: Configuração do Projeto (15 min)

#### ☐ 4.1 Clonar/Acessar Repositório
```bash
cd /home/mizuno/projetos/mizuno/finassist
```

#### ☐ 4.2 Criar Ambiente Virtual
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas

```bash
# Criar e ativar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Ou usar Makefile:
make setup
```

#### ☐ 4.3 Configurar Variáveis de Ambiente
- [ ] Arquivo .env criado
- [ ] Credenciais preenchidas

```bash
# Copiar template
cp env.example .env

# Editar com suas credenciais
nano .env  # ou abrir no Cursor
```

**Credenciais necessárias:**
- OpenAI API Key + Assistant ID
- Twilio Account SID + Auth Token + WhatsApp Number
- Microsoft Graph Client ID + Client Secret + Refresh Token
- AWS Credentials (via aws configure)

#### ☐ 4.4 Obter Refresh Token do Microsoft Graph
```bash
# Executar fluxo OAuth
make oauth-setup

# Seguir instruções no navegador
# Copiar refresh_token para o .env
```

#### ☐ 4.5 Gerar Configuração SAM
```bash
# Gerar env.json a partir do .env
make generate-env-json
```

### Fase 5: Verificação Final (5 min)

#### ☐ 5.1 Executar Script de Verificação
```bash
# Tornar script executável (primeira vez)
chmod +x scripts/verify_environment.sh

# Executar verificação completa
./scripts/verify_environment.sh
```

O script deve mostrar todas as verificações passando (✅).

#### ☐ 5.2 Testar Ambiente Local

**Terminal 1: DynamoDB Local**
```bash
make start-dynamodb-local
```

**Terminal 2: API Local (SAM)**
```bash
make start-api
# Aguardar até ver: "Mounting WebhookFunction at http://127.0.0.1:3000/webhook/whatsapp"
```

**Terminal 3: ngrok**
```bash
make start-ngrok
# Copiar URL HTTPS exibida
```

#### ☐ 5.3 Executar Testes
```bash
# Em um novo terminal, com .venv ativado
make test
```

Se todos os testes passarem, seu ambiente está pronto! 🎉

## 🔄 Fluxo de Trabalho Diário

### Iniciando o Dia

```bash
# 1. Ativar ambiente virtual
cd /home/mizuno/projetos/mizuno/finassist
source .venv/bin/activate

# 2. Atualizar código (se necessário)
git pull

# 3. Iniciar serviços locais

# Terminal 1: DynamoDB Local
make start-dynamodb-local

# Terminal 2: API Local
make start-api

# Terminal 3: ngrok (se precisar testar webhooks)
make start-ngrok
```

### Durante o Desenvolvimento

```bash
# Executar testes
make test                  # Todos os testes com cobertura
make test-unit             # Apenas testes unitários
make test-integration      # Apenas testes de integração

# Verificar linting
make lint

# Formatar código
make format

# Ver logs do Lambda local
# Os logs aparecem no terminal onde rodou 'make start-api'
```

### Finalizando o Dia

```bash
# Parar serviços (Ctrl+C em cada terminal)
# Ou parar todos os containers Docker:
make stop-dynamodb-local

# Desativar ambiente virtual
deactivate

# Commit suas mudanças
git add .
git commit -m "Descrição das mudanças"
git push
```

## 📖 Comandos Essenciais

### Makefile (Atalhos)

```bash
# Setup inicial
make setup                 # Criar venv + instalar deps

# Desenvolvimento local
make start-dynamodb-local  # Iniciar DynamoDB Local
make stop-dynamodb-local   # Parar DynamoDB Local
make start-api             # Iniciar API local (SAM)
make start-ngrok           # Iniciar ngrok (túnel)

# Testes
make test                  # Todos os testes + cobertura
make test-unit             # Testes unitários
make test-integration      # Testes de integração

# Qualidade de código
make lint                  # Verificar linting
make format                # Formatar código

# Utilitários
make oauth-setup           # OAuth Microsoft Graph
make generate-env-json     # Gerar env.json do .env
make clean                 # Limpar arquivos temporários

# Deploy
make build                 # Build SAM
make deploy                # Deploy para AWS
```

### Docker

```bash
# Listar containers rodando
docker ps

# Ver logs de um container
docker logs dynamodb-local

# Parar todos os containers
docker stop $(docker ps -q)

# Limpar containers parados
docker container prune
```

### SAM CLI

```bash
# Build aplicação
sam build

# Iniciar API local
sam local start-api --env-vars env.json

# Invocar função diretamente
sam local invoke WebhookFunction --event events/whatsapp_message.json

# Ver logs do Lambda
# (aparece automaticamente no terminal do start-api)
```

### pytest

```bash
# Executar todos os testes
pytest

# Executar testes específicos
pytest tests/unit/test_twilio_service.py

# Executar com cobertura
pytest --cov=. --cov-report=html

# Modo verbose
pytest -v

# Parar no primeiro erro
pytest -x
```

## 🔧 Problemas Comuns

### "docker: command not found"

**Causa**: Docker não está acessível no WSL2

**Solução**:
1. Verificar se Docker Desktop está rodando (Windows)
2. Docker Desktop → Settings → Resources → WSL Integration
3. Ativar integração para sua distribuição
4. Reiniciar terminal WSL2

### "sam: command not found"

**Causa**: SAM CLI não está no PATH

**Solução**:
```bash
# Adicionar ao PATH
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verificar
sam --version
```

### "Table does not exist" (DynamoDB)

**Causa**: Tabela não foi criada no DynamoDB Local

**Solução**:
```bash
make create-dynamodb-table
```

### "OPENAI_API_KEY not configured"

**Causa**: Variáveis de ambiente não estão carregadas

**Solução**:
```bash
# Verificar se .env existe e está preenchido
cat .env

# Gerar env.json novamente
make generate-env-json

# Reiniciar API local
make start-api
```

### Testes falhando

**Causa**: Dependências desatualizadas ou ambiente incorreto

**Solução**:
```bash
# Limpar e reinstalar
make clean
rm -rf .venv
make setup

# Executar testes novamente
make test
```

### ngrok "authentication failed"

**Causa**: Authtoken inválido ou não configurado

**Solução**:
```bash
# Reconfigurar authtoken (obtenha em https://dashboard.ngrok.com)
ngrok config add-authtoken SEU_NOVO_AUTHTOKEN

# Testar
ngrok http 3000
```

### Lambda timeout em desenvolvimento local

**Causa**: Timeout muito curto

**Solução**:
Editar `template.yaml`:
```yaml
Globals:
  Function:
    Timeout: 120  # Aumentar para 2 minutos
```

## 📚 Recursos Adicionais

### Documentação do Projeto

- [README.md](../README.md) - Documentação principal
- [SETUP_AMBIENTE.md](./SETUP_AMBIENTE.md) - Guia detalhado de instalação
- [QUICKSTART.md](../QUICKSTART.md) - Guia rápido de uso

### Documentação Externa

- [AWS SAM Developer Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/)
- [OpenAI Assistants API](https://platform.openai.com/docs/assistants/overview)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [pytest Documentation](https://docs.pytest.org/)

## 🎓 Próximos Passos

Agora que seu ambiente está configurado:

1. **Explore o código**: Comece por `lambda_function.py` e `conversation_manager.py`
2. **Leia a arquitetura**: Entenda o fluxo de mensagens no README
3. **Execute os testes**: Familiarize-se com os testes existentes
4. **Teste localmente**: Envie mensagens WhatsApp de teste
5. **Faça sua primeira mudança**: Escolha uma issue simples para começar

## 💡 Dicas

- **Use o Cursor AI**: Aproveite o IntelliSense e as sugestões da IA
- **Mantenha o ambiente virtual ativado**: Evita problemas de dependências
- **Teste frequentemente**: Execute `make test` após cada mudança
- **Consulte os logs**: Eles são seus melhores amigos para debugging
- **Use o Makefile**: Comandos já estão otimizados

---

**Dúvidas?** Consulte o [README principal](../README.md) ou a [documentação de setup](./SETUP_AMBIENTE.md).

**Pronto para começar!** 🚀

