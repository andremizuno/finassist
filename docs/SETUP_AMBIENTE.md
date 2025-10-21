# 🛠️ Guia de Configuração do Ambiente de Desenvolvimento

> Guia completo para instalação e configuração de todas as ferramentas necessárias para desenvolvimento do projeto FinAssist.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos do Sistema](#pré-requisitos-do-sistema)
- [Instalação de Ferramentas Externas](#instalação-de-ferramentas-externas)
- [Extensões do Cursor AI](#extensões-do-cursor-ai)
- [Configuração do Ambiente Python](#configuração-do-ambiente-python)
- [Verificação do Ambiente](#verificação-do-ambiente)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

Este guia cobre a instalação de:

- **AWS SAM CLI**: Framework para desenvolvimento serverless local
- **Docker Desktop**: Container runtime para DynamoDB Local e Lambda
- **ngrok**: Túnel para expor API local para webhooks externos
- **pytest**: Framework de testes Python
- **Extensões Cursor**: Plugins para otimizar desenvolvimento

## 💻 Pré-requisitos do Sistema

### WSL2 (Windows Subsystem for Linux)

Como você está usando WSL2, certifique-se de que está atualizado:

```bash
# No PowerShell (Windows), verificar versão WSL
wsl --version

# Atualizar WSL se necessário
wsl --update
```

### Python 3.9+

Verificar instalação:

```bash
python3 --version
# Deve retornar: Python 3.9.x ou superior
```

Se não estiver instalado:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

### Git

```bash
git --version

# Se não estiver instalado:
sudo apt install git -y
```

### Ferramentas Básicas

```bash
# Instalar ferramentas essenciais
sudo apt update
sudo apt install curl unzip wget build-essential -y
```

## 🔧 Instalação de Ferramentas Externas

### 1. AWS CLI

A AWS CLI é necessária para interagir com serviços AWS e é pré-requisito do SAM CLI.

```bash
# Baixar instalador
cd /tmp
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Descompactar
unzip awscliv2.zip

# Instalar (pode requerer sudo)
sudo ./aws/install

# Verificar instalação
aws --version
# Esperado: aws-cli/2.x.x Python/3.x.x Linux/x.x.x

# Limpar arquivos temporários
cd ~
rm -rf /tmp/awscliv2.zip /tmp/aws
```

**Configurar AWS CLI:**

```bash
aws configure
# AWS Access Key ID: [sua access key]
# AWS Secret Access Key: [sua secret key]
# Default region name: us-east-1
# Default output format: json
```

### 2. AWS SAM CLI

SAM CLI permite testar funções Lambda localmente.

```bash
# Baixar instalador
cd /tmp
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip

# Descompactar
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation

# Instalar
sudo ./sam-installation/install

# Verificar instalação
sam --version
# Esperado: SAM CLI, version 1.x.x

# Limpar arquivos temporários
cd ~
rm -rf /tmp/aws-sam-cli-linux-x86_64.zip /tmp/sam-installation
```

**Configuração adicional:**

O SAM CLI usa o Docker para emular o ambiente Lambda. Certifique-se de que o Docker está configurado (próximo passo).

### 3. Docker Desktop (Windows + Integração WSL2)

Docker é essencial para rodar DynamoDB Local e emular Lambda.

#### Instalação no Windows:

1. **Download:**
   - Acesse: https://www.docker.com/products/docker-desktop/
   - Baixe Docker Desktop para Windows

2. **Instalação:**
   - Execute o instalador
   - Durante a instalação, certifique-se de que **"Use WSL 2 instead of Hyper-V"** está marcado
   - Reinicie o computador se solicitado

3. **Configuração WSL2:**
   - Abra Docker Desktop
   - Vá em **Settings** → **Resources** → **WSL Integration**
   - Ative a integração para sua distribuição WSL2 (Ubuntu, etc.)
   - Clique em **Apply & Restart**

#### Verificação no WSL2:

```bash
# Verificar se Docker está acessível no WSL2
docker --version
# Esperado: Docker version 24.x.x

docker ps
# Deve listar containers (vazio se nenhum rodando)

# Testar com container hello-world
docker run hello-world
# Deve baixar e executar com sucesso
```

#### Troubleshooting Docker:

Se `docker` não for encontrado no WSL2:

```bash
# Certificar que Docker Desktop está rodando no Windows
# Reiniciar Docker Desktop
# Verificar integração WSL2 nas configurações
```

### 4. ngrok

ngrok cria túneis seguros para expor sua API local à internet (necessário para webhooks Twilio).

#### Instalação:

```bash
# Baixar ngrok
cd /tmp
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz

# Extrair
tar -xvzf ngrok-v3-stable-linux-amd64.tgz

# Mover para /usr/local/bin
sudo mv ngrok /usr/local/bin/

# Verificar instalação
ngrok version
# Esperado: ngrok version 3.x.x

# Limpar
cd ~
rm /tmp/ngrok-v3-stable-linux-amd64.tgz
```

#### Configuração:

1. **Criar conta (gratuita):**
   - Acesse: https://dashboard.ngrok.com/signup

2. **Obter authtoken:**
   - Após login, vá para: https://dashboard.ngrok.com/get-started/your-authtoken
   - Copie seu authtoken

3. **Configurar authtoken:**
   ```bash
   ngrok config add-authtoken SEU_AUTHTOKEN_AQUI
   # Esperado: Authtoken saved to configuration file: /home/user/.ngrok2/ngrok.yml
   ```

#### Testar ngrok:

```bash
# Criar túnel de teste (Ctrl+C para parar)
ngrok http 3000

# Você verá:
# Forwarding: https://abc123.ngrok-free.app -> http://localhost:3000
```

### 5. pytest (Framework de Testes)

pytest será instalado no ambiente virtual do projeto, mas você pode verificar:

```bash
# Após ativar o ambiente virtual do projeto (.venv)
source .venv/bin/activate

# pytest já deve estar instalado via requirements-dev.txt
pytest --version
# Esperado: pytest 7.x.x
```

Se não estiver instalado:

```bash
pip install pytest pytest-cov pytest-mock
```

## 🔌 AWS MCP Server (Opcional - Recomendado)

### O que é AWS MCP Server?

O **Model Context Protocol (MCP) da AWS** permite que o Cursor AI interaja diretamente com seus recursos AWS:
- Ver logs do CloudWatch em tempo real
- Listar e inspecionar funções Lambda
- Consultar tabelas DynamoDB
- Verificar status de recursos AWS
- Debug mais rápido sem sair do IDE

### Instalação Rápida

```bash
# Instalar automaticamente
./scripts/setup_aws_mcp.sh

# Ou consulte o guia completo
cat docs/CONFIGURAR_AWS_MCP.md
```

**Requisitos**: Node.js 18+, AWS CLI configurado

**Guia completo**: [docs/CONFIGURAR_AWS_MCP.md](./CONFIGURAR_AWS_MCP.md)

## 🎨 Extensões do Cursor AI

O Cursor é compatível com extensões do VS Code. Instale as seguintes extensões essenciais:

### Como Instalar Extensões:

1. Abra o Cursor AI
2. Clique no ícone de **Extensions** na barra lateral (ou `Ctrl+Shift+X`)
3. Pesquise pelo nome ou ID da extensão
4. Clique em **Install**

### Extensões Recomendadas:

#### 1. **AWS Toolkit**
- **ID**: `amazonwebservices.aws-toolkit-vscode`
- **Por que**: Integração completa com AWS - invoke Lambda local, visualize CloudWatch Logs, gerencie recursos
- **Configuração**: Após instalar, configure o perfil AWS e região padrão

#### 2. **Python**
- **ID**: `ms-python.python`
- **Por que**: IntelliSense, debugging, linting, formatação
- **Inclui**: Pylance (type checking avançado)

#### 3. **Pylance**
- **ID**: `ms-python.vscode-pylance`
- **Por que**: Type checking e IntelliSense otimizados
- **Nota**: Geralmente instalado automaticamente com Python extension

#### 4. **Docker**
- **ID**: `ms-azuretools.vscode-docker`
- **Por que**: Gerenciar containers, imagens, logs diretamente do editor
- **Uso**: Visualizar containers DynamoDB Local, Lambda SAM

#### 5. **Python Test Explorer for Visual Studio Code**
- **ID**: `littlefoxteam.vscode-python-test-adapter`
- **Por que**: Descoberta e execução visual de testes pytest
- **Uso**: Executar testes individuais com um clique

#### 6. **DotENV**
- **ID**: `mikestead.dotenv`
- **Por que**: Syntax highlighting para arquivos `.env`
- **Uso**: Facilita edição de variáveis de ambiente

#### 7. **GitLens**
- **ID**: `eamodio.gitlens`
- **Por que**: Git supercharged - blame, histórico, navegação de commits
- **Uso**: Rastrear quem escreveu cada linha, explorar histórico

### Instalação Automática:

O projeto inclui um arquivo `.vscode/extensions.json` que o Cursor detectará automaticamente e perguntará se deseja instalar as extensões recomendadas.

## 🐍 Configuração do Ambiente Python

### 1. Criar Ambiente Virtual

```bash
# No diretório do projeto
cd /home/mizuno/projetos/mizuno/finassist

# Criar ambiente virtual
python3 -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate

# Verificar ativação (prompt deve mostrar (.venv))
which python
# Esperado: /home/mizuno/projetos/mizuno/finassist/.venv/bin/python
```

### 2. Instalar Dependências

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências de produção
pip install -r requirements.txt

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Verificar instalações
pip list
```

### 3. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo exemplo
cp env.example .env

# Editar .env com suas credenciais
nano .env  # ou code .env no Cursor
```

**Variáveis obrigatórias:**

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
MS_GRAPH_REFRESH_TOKEN=...  # Obter com: make oauth-setup

# DynamoDB Local
DYNAMODB_ENDPOINT_URL=http://localhost:8000
```

### 4. Gerar Configuração SAM

```bash
# Gerar env.json para SAM CLI
make generate-env-json
```

## ✅ Verificação do Ambiente

### Script Automatizado

Execute o script de verificação:

```bash
# Tornar script executável
chmod +x scripts/verify_environment.sh

# Executar verificação
./scripts/verify_environment.sh
```

O script verificará:
- ✅ Python 3.9+
- ✅ AWS CLI
- ✅ SAM CLI
- ✅ Docker
- ✅ ngrok
- ✅ Git
- ✅ Ambiente virtual
- ✅ Dependências Python
- ✅ Arquivo .env

### Verificação Manual

```bash
# Python
python3 --version

# AWS CLI
aws --version

# SAM CLI
sam --version

# Docker
docker --version
docker ps

# ngrok
ngrok version

# Git
git --version

# pytest (no .venv)
source .venv/bin/activate
pytest --version
```

## 🧪 Testar Ambiente

### 1. Testar Docker e DynamoDB Local

```bash
# Iniciar DynamoDB Local
make start-dynamodb-local

# Verificar se está rodando
docker ps | grep dynamodb
```

### 2. Testar SAM CLI

```bash
# Build aplicação
sam build

# Iniciar API local
sam local start-api --env-vars env.json
# Deve iniciar em http://127.0.0.1:3000
```

### 3. Testar ngrok

```bash
# Em outro terminal
ngrok http 3000

# Deve exibir URL pública
```

### 4. Executar Testes

```bash
# Testes unitários
make test-unit

# Testes de integração (requer DynamoDB rodando)
make test-integration

# Todos os testes com cobertura
make test
```

## 🔧 Troubleshooting

### Problema: `sam: command not found`

**Solução:**

```bash
# Verificar se /usr/local/bin está no PATH
echo $PATH | grep /usr/local/bin

# Se não estiver, adicionar ao ~/.bashrc
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Problema: `docker: command not found` no WSL2

**Solução:**

1. Verificar se Docker Desktop está rodando no Windows
2. Abrir Docker Desktop → Settings → Resources → WSL Integration
3. Ativar integração para sua distribuição
4. Reiniciar terminal WSL2

### Problema: SAM CLI lento ou não inicia

**Solução:**

```bash
# Verificar se Docker está rodando
docker ps

# Aumentar recursos do Docker Desktop (Windows)
# Settings → Resources → Advanced
# CPU: 4+ cores
# Memory: 4+ GB
```

### Problema: ngrok "authentication failed"

**Solução:**

```bash
# Reconfigurar authtoken
ngrok config add-authtoken SEU_AUTHTOKEN

# Verificar arquivo de configuração
cat ~/.ngrok2/ngrok.yml
```

### Problema: Testes pytest não são descobertos

**Solução:**

```bash
# Verificar se está no ambiente virtual
source .venv/bin/activate

# Reinstalar pytest
pip install --upgrade pytest pytest-cov

# Executar descoberta manual
pytest --collect-only
```

### Problema: Extensões não aparecem no Cursor

**Solução:**

1. Verificar se Cursor está atualizado
2. Tentar instalar extensões manualmente via Marketplace
3. Reiniciar Cursor após instalação

## 📚 Recursos Adicionais

### Documentação Oficial

- **AWS SAM CLI**: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
- **Docker Desktop**: https://docs.docker.com/desktop/wsl/
- **ngrok**: https://ngrok.com/docs/getting-started/
- **pytest**: https://docs.pytest.org/
- **VS Code Extensions**: https://code.visualstudio.com/docs/editor/extension-marketplace

### Tutoriais

- **AWS SAM Local Development**: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-debugging.html
- **Docker + WSL2**: https://docs.docker.com/desktop/wsl/
- **pytest Best Practices**: https://docs.pytest.org/en/stable/goodpractices.html

## 🎯 Próximos Passos

Após configurar o ambiente, consulte:

1. **[PRIMEIROS_PASSOS.md](./PRIMEIROS_PASSOS.md)**: Checklist completo para começar
2. **[README.md](../README.md)**: Documentação principal do projeto
3. **[QUICKSTART.md](../QUICKSTART.md)**: Guia rápido de uso

---

**Dúvidas?** Consulte o [README principal](../README.md) ou abra uma issue no repositório.

