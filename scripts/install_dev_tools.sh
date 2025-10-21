#!/bin/bash

################################################################################
# Script de Instalação Automatizada de Ferramentas de Desenvolvimento
# Projeto: FinAssist - Assistente Financeiro Serverless
#
# Este script instala automaticamente:
# - AWS CLI
# - AWS SAM CLI
# - ngrok
#
# Uso: ./scripts/install_dev_tools.sh
################################################################################

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função principal
main() {
    print_header "Instalação de Ferramentas de Desenvolvimento"

    print_info "Este script instalará as seguintes ferramentas:"
    echo "  - AWS CLI"
    echo "  - AWS SAM CLI"
    echo "  - ngrok"
    echo ""

    # Verificar pré-requisitos
    check_prerequisites

    # Instalar AWS CLI
    install_aws_cli

    # Instalar SAM CLI
    install_sam_cli

    # Instalar ngrok
    install_ngrok

    # Resumo final
    print_summary
}

# Verificar pré-requisitos do sistema
check_prerequisites() {
    print_header "Verificando Pré-requisitos"

    # Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        print_success "Python encontrado: $PYTHON_VERSION"
    else
        print_error "Python 3 não encontrado"
        print_info "Instale com: sudo apt install python3 python3-pip -y"
        exit 1
    fi

    # curl
    if command_exists curl; then
        print_success "curl encontrado"
    else
        print_error "curl não encontrado"
        print_info "Instale com: sudo apt install curl -y"
        exit 1
    fi

    # unzip
    if command_exists unzip; then
        print_success "unzip encontrado"
    else
        print_error "unzip não encontrado"
        print_info "Instale com: sudo apt install unzip -y"
        exit 1
    fi

    # wget
    if command_exists wget; then
        print_success "wget encontrado"
    else
        print_error "wget não encontrado"
        print_info "Instale com: sudo apt install wget -y"
        exit 1
    fi

    # Git
    if command_exists git; then
        GIT_VERSION=$(git --version | awk '{print $3}')
        print_success "Git encontrado: $GIT_VERSION"
    else
        print_warning "Git não encontrado (recomendado)"
    fi

    print_success "Todos os pré-requisitos foram atendidos!"
}

# Instalar AWS CLI
install_aws_cli() {
    print_header "Instalando AWS CLI"

    if command_exists aws; then
        AWS_VERSION=$(aws --version 2>&1 | awk '{print $1}' | cut -d'/' -f2)
        print_warning "AWS CLI já está instalado (versão $AWS_VERSION)"

        read -p "Deseja reinstalar/atualizar? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            print_info "Pulando instalação do AWS CLI"
            return
        fi
    fi

    print_info "Baixando AWS CLI..."
    cd /tmp

    # Remover instalações anteriores se existirem
    rm -rf awscliv2.zip aws

    curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

    if [ $? -ne 0 ]; then
        print_error "Falha ao baixar AWS CLI"
        exit 1
    fi

    print_info "Descompactando..."
    unzip -q awscliv2.zip

    print_info "Instalando... (pode requerer senha sudo)"
    sudo ./aws/install --update 2>/dev/null || sudo ./aws/install

    # Limpar arquivos temporários
    rm -rf awscliv2.zip aws
    cd - > /dev/null

    # Verificar instalação
    if command_exists aws; then
        AWS_VERSION=$(aws --version 2>&1 | awk '{print $1}' | cut -d'/' -f2)
        print_success "AWS CLI instalado com sucesso! Versão: $AWS_VERSION"

        # Verificar configuração
        if [ ! -f ~/.aws/credentials ]; then
            print_warning "AWS CLI não está configurado"
            print_info "Execute: aws configure"
        fi
    else
        print_error "Falha na instalação do AWS CLI"
        exit 1
    fi
}

# Instalar SAM CLI
install_sam_cli() {
    print_header "Instalando AWS SAM CLI"

    if command_exists sam; then
        SAM_VERSION=$(sam --version | awk '{print $4}')
        print_warning "SAM CLI já está instalado (versão $SAM_VERSION)"

        read -p "Deseja reinstalar/atualizar? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            print_info "Pulando instalação do SAM CLI"
            return
        fi
    fi

    print_info "Baixando SAM CLI..."
    cd /tmp

    # Remover instalações anteriores se existirem
    rm -rf aws-sam-cli-linux-x86_64.zip sam-installation

    wget -q https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip

    if [ $? -ne 0 ]; then
        print_error "Falha ao baixar SAM CLI"
        exit 1
    fi

    print_info "Descompactando..."
    unzip -q aws-sam-cli-linux-x86_64.zip -d sam-installation

    print_info "Instalando... (pode requerer senha sudo)"
    sudo ./sam-installation/install --update 2>/dev/null || sudo ./sam-installation/install

    # Limpar arquivos temporários
    rm -rf aws-sam-cli-linux-x86_64.zip sam-installation
    cd - > /dev/null

    # Verificar instalação
    if command_exists sam; then
        SAM_VERSION=$(sam --version | awk '{print $4}')
        print_success "SAM CLI instalado com sucesso! Versão: $SAM_VERSION"

        # Verificar Docker
        if ! command_exists docker; then
            print_warning "Docker não encontrado"
            print_info "SAM CLI requer Docker para funcionar"
            print_info "Instale Docker Desktop: https://www.docker.com/products/docker-desktop/"
        else
            print_success "Docker encontrado (necessário para SAM CLI)"
        fi
    else
        print_error "Falha na instalação do SAM CLI"
        exit 1
    fi
}

# Instalar ngrok
install_ngrok() {
    print_header "Instalando ngrok"

    if command_exists ngrok; then
        NGROK_VERSION=$(ngrok version | awk '{print $3}')
        print_warning "ngrok já está instalado (versão $NGROK_VERSION)"

        read -p "Deseja reinstalar/atualizar? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            print_info "Pulando instalação do ngrok"
            return
        fi
    fi

    print_info "Baixando ngrok..."
    cd /tmp

    # Remover instalações anteriores se existirem
    rm -rf ngrok-v3-stable-linux-amd64.tgz ngrok

    wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz

    if [ $? -ne 0 ]; then
        print_error "Falha ao baixar ngrok"
        exit 1
    fi

    print_info "Extraindo..."
    tar -xzf ngrok-v3-stable-linux-amd64.tgz

    print_info "Instalando... (pode requerer senha sudo)"
    sudo mv ngrok /usr/local/bin/
    sudo chmod +x /usr/local/bin/ngrok

    # Limpar arquivos temporários
    rm -rf ngrok-v3-stable-linux-amd64.tgz
    cd - > /dev/null

    # Verificar instalação
    if command_exists ngrok; then
        NGROK_VERSION=$(ngrok version | awk '{print $3}')
        print_success "ngrok instalado com sucesso! Versão: $NGROK_VERSION"

        # Verificar configuração
        if [ ! -f ~/.ngrok2/ngrok.yml ]; then
            print_warning "ngrok não está configurado"
            print_info "Para configurar:"
            print_info "1. Crie conta em: https://dashboard.ngrok.com/signup"
            print_info "2. Obtenha seu authtoken em: https://dashboard.ngrok.com/get-started/your-authtoken"
            print_info "3. Execute: ngrok config add-authtoken SEU_AUTHTOKEN"
        else
            print_success "ngrok já está configurado"
        fi
    else
        print_error "Falha na instalação do ngrok"
        exit 1
    fi
}

# Resumo final
print_summary() {
    print_header "Resumo da Instalação"

    echo "Status das ferramentas instaladas:"
    echo ""

    # AWS CLI
    if command_exists aws; then
        AWS_VERSION=$(aws --version 2>&1 | awk '{print $1}' | cut -d'/' -f2)
        print_success "AWS CLI: $AWS_VERSION"
    else
        print_error "AWS CLI: não instalado"
    fi

    # SAM CLI
    if command_exists sam; then
        SAM_VERSION=$(sam --version | awk '{print $4}')
        print_success "SAM CLI: $SAM_VERSION"
    else
        print_error "SAM CLI: não instalado"
    fi

    # ngrok
    if command_exists ngrok; then
        NGROK_VERSION=$(ngrok version | awk '{print $3}')
        print_success "ngrok: $NGROK_VERSION"
    else
        print_error "ngrok: não instalado"
    fi

    # Docker (informativo)
    echo ""
    print_info "Verificações adicionais:"
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
        print_success "Docker: $DOCKER_VERSION (necessário para SAM CLI)"
    else
        print_warning "Docker: não encontrado (necessário para SAM CLI)"
        print_info "Instale Docker Desktop: https://www.docker.com/products/docker-desktop/"
    fi

    echo ""
    print_header "Próximos Passos"
    echo "1. Configure AWS CLI:"
    echo "   aws configure"
    echo ""
    echo "2. Configure ngrok (se ainda não configurado):"
    echo "   ngrok config add-authtoken SEU_AUTHTOKEN"
    echo ""
    echo "3. Verifique o ambiente completo:"
    echo "   ./scripts/verify_environment.sh"
    echo ""
    echo "4. Consulte o guia completo:"
    echo "   docs/SETUP_AMBIENTE.md"
    echo ""

    print_success "Instalação concluída!"
}

# Executar script
main

