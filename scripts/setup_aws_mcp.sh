#!/bin/bash

################################################################################
# Script de Instalação do AWS MCP Server
# Projeto: FinAssist - Assistente Financeiro Serverless
#
# Este script instala e configura o AWS MCP Server para integração com Cursor AI
#
# Uso: ./scripts/setup_aws_mcp.sh
################################################################################

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funções auxiliares
print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função principal
main() {
    print_header "Instalação do AWS MCP Server"

    print_info "AWS MCP Server permite ao Cursor AI interagir com recursos AWS"
    echo "  - Consultar funções Lambda"
    echo "  - Ler logs do CloudWatch"
    echo "  - Inspecionar DynamoDB"
    echo "  - Verificar API Gateway"
    echo ""

    # Verificar pré-requisitos
    check_prerequisites

    # Instalar Node.js se necessário
    install_nodejs

    # Instalar AWS MCP Server
    install_aws_mcp

    # Configurar no Cursor
    configure_cursor

    # Resumo final
    print_summary
}

# Verificar pré-requisitos
check_prerequisites() {
    print_header "Verificando Pré-requisitos"

    # AWS CLI
    if command_exists aws; then
        AWS_VERSION=$(aws --version 2>&1 | awk '{print $1}' | cut -d'/' -f2)
        print_success "AWS CLI encontrado: $AWS_VERSION"

        # Verificar se está configurado
        if aws configure list 2>&1 | grep -q "access_key"; then
            print_success "AWS CLI configurado"
        else
            print_warning "AWS CLI não está configurado"
            print_info "Execute: aws configure"
            echo ""
            read -p "Deseja continuar mesmo assim? (s/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Ss]$ ]]; then
                print_error "Configuração cancelada"
                exit 1
            fi
        fi
    else
        print_error "AWS CLI não encontrado"
        print_info "Instale com: ./scripts/install_dev_tools.sh"
        exit 1
    fi
}

# Instalar Node.js
install_nodejs() {
    print_header "Verificando Node.js"

    if command_exists node; then
        NODE_VERSION=$(node --version)
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'v' -f2 | cut -d'.' -f1)

        print_success "Node.js encontrado: $NODE_VERSION"

        if [ "$NODE_MAJOR" -lt 18 ]; then
            print_warning "Node.js versão 18+ é recomendada (atual: $NODE_VERSION)"

            read -p "Deseja atualizar Node.js? (s/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Ss]$ ]]; then
                install_nodejs_update
            else
                print_info "Continuando com versão atual"
            fi
        fi
    else
        print_warning "Node.js não encontrado"

        read -p "Deseja instalar Node.js 20.x? (S/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            install_nodejs_update
        else
            print_error "Node.js é necessário para AWS MCP Server"
            exit 1
        fi
    fi

    # Verificar npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_success "npm encontrado: $NPM_VERSION"
    else
        print_error "npm não encontrado"
        exit 1
    fi
}

# Instalar/Atualizar Node.js
install_nodejs_update() {
    print_info "Instalando Node.js 20.x..."

    # Adicionar repositório NodeSource
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

    # Instalar Node.js
    sudo apt-get install -y nodejs

    # Verificar instalação
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION instalado com sucesso!"
    else
        print_error "Falha na instalação do Node.js"
        exit 1
    fi
}

# Instalar AWS MCP Server
install_aws_mcp() {
    print_header "Instalando AWS MCP Server"

    # Verificar se já está instalado
    if npm list -g @aws/mcp-server-aws >/dev/null 2>&1; then
        print_warning "AWS MCP Server já está instalado"

        read -p "Deseja reinstalar/atualizar? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            print_info "Pulando instalação do AWS MCP Server"
            return
        fi
    fi

    print_info "Instalando @aws/mcp-server-aws globalmente..."

    # Instalar globalmente
    if sudo npm install -g @aws/mcp-server-aws --silent; then
        print_success "AWS MCP Server instalado com sucesso!"

        # Verificar instalação
        if command_exists npx; then
            print_success "npx disponível para executar MCP Server"
        fi
    else
        print_error "Falha na instalação do AWS MCP Server"
        print_info "Tente manualmente: sudo npm install -g @aws/mcp-server-aws"
        exit 1
    fi
}

# Configurar no Cursor
configure_cursor() {
    print_header "Configurando Cursor AI"

    # Detectar sistema operacional e definir caminho
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ -n "$WSL_DISTRO_NAME" ]]; then
        # Linux ou WSL2
        CURSOR_CONFIG_DIR="$HOME/.cursor"
        CURSOR_CONFIG_FILE="$CURSOR_CONFIG_DIR/mcp_config.json"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        CURSOR_CONFIG_DIR="$HOME/Library/Application Support/Cursor"
        CURSOR_CONFIG_FILE="$CURSOR_CONFIG_DIR/mcp_config.json"
    else
        print_warning "Sistema operacional não detectado automaticamente"
        print_info "Configure manualmente: ~/.cursor/mcp_config.json"
        return
    fi

    # Criar diretório se não existir
    mkdir -p "$CURSOR_CONFIG_DIR"

    # Verificar se arquivo já existe
    if [ -f "$CURSOR_CONFIG_FILE" ]; then
        print_warning "Arquivo de configuração MCP já existe"
        print_info "Localização: $CURSOR_CONFIG_FILE"

        read -p "Deseja sobrescrever? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            print_info "Mantendo configuração atual"
            print_info "Para adicionar AWS MCP manualmente, consulte: docs/CONFIGURAR_AWS_MCP.md"
            return
        fi

        # Backup do arquivo existente
        BACKUP_FILE="${CURSOR_CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$CURSOR_CONFIG_FILE" "$BACKUP_FILE"
        print_info "Backup criado: $BACKUP_FILE"
    fi

    # Obter região AWS padrão
    AWS_REGION=$(aws configure get region 2>/dev/null || echo "us-east-1")
    AWS_PROFILE=$(aws configure get profile 2>/dev/null || echo "default")

    # Criar configuração MCP
    print_info "Criando configuração MCP para AWS..."

    cat > "$CURSOR_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "aws": {
      "command": "npx",
      "args": [
        "-y",
        "@aws/mcp-server-aws"
      ],
      "env": {
        "AWS_PROFILE": "$AWS_PROFILE",
        "AWS_REGION": "$AWS_REGION"
      }
    }
  }
}
EOF

    if [ $? -eq 0 ]; then
        print_success "Configuração MCP criada com sucesso!"
        print_info "Localização: $CURSOR_CONFIG_FILE"
        print_info "AWS Profile: $AWS_PROFILE"
        print_info "AWS Region: $AWS_REGION"
    else
        print_error "Falha ao criar configuração MCP"
        exit 1
    fi
}

# Resumo final
print_summary() {
    print_header "Resumo da Instalação"

    echo "Status das ferramentas instaladas:"
    echo ""

    # Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js: $NODE_VERSION"
    else
        print_error "Node.js: não instalado"
    fi

    # npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_success "npm: $NPM_VERSION"
    else
        print_error "npm: não instalado"
    fi

    # AWS MCP Server
    if npm list -g @aws/mcp-server-aws >/dev/null 2>&1; then
        print_success "AWS MCP Server: instalado"
    else
        print_error "AWS MCP Server: não instalado"
    fi

    # Configuração Cursor
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ -n "$WSL_DISTRO_NAME" ]]; then
        CURSOR_CONFIG_FILE="$HOME/.cursor/mcp_config.json"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        CURSOR_CONFIG_FILE="$HOME/Library/Application Support/Cursor/mcp_config.json"
    fi

    if [ -f "$CURSOR_CONFIG_FILE" ]; then
        print_success "Configuração Cursor: criada"
    else
        print_warning "Configuração Cursor: não criada"
    fi

    echo ""
    print_header "Próximos Passos"

    echo "1. Reinicie o Cursor AI completamente (fechar todas as janelas)"
    echo ""
    echo "2. No chat do Cursor, teste a integração:"
    echo "   \"Liste todas as funções Lambda disponíveis\""
    echo ""
    echo "3. Consulte o guia completo de uso:"
    echo "   docs/CONFIGURAR_AWS_MCP.md"
    echo ""
    echo "4. Exemplos de comandos úteis:"
    echo "   - \"Mostre os logs de erro das últimas 2 horas\""
    echo "   - \"Liste todas as tabelas DynamoDB\""
    echo "   - \"Qual o status da função Lambda WebhookFunction?\""
    echo ""

    print_success "Instalação concluída!"
    print_info "Documentação completa: docs/CONFIGURAR_AWS_MCP.md"
}

# Executar script
main


