#!/bin/bash

################################################################################
# Script de Verificação do Ambiente de Desenvolvimento
# Projeto: FinAssist - Assistente Financeiro Serverless
#
# Este script verifica se todas as ferramentas e configurações necessárias
# estão instaladas e funcionando corretamente.
#
# Uso: ./scripts/verify_environment.sh
################################################################################

# Não usar set -e para permitir contadores iniciarem em 0
# set -e  # Parar em caso de erro crítico

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Contadores
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Funções auxiliares
print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED_CHECKS++))
    ((TOTAL_CHECKS++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNING_CHECKS++))
    ((TOTAL_CHECKS++))
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Comparar versões (retorna 0 se $1 >= $2)
version_ge() {
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

# Função principal
main() {
    print_header "Verificação do Ambiente de Desenvolvimento"
    print_info "Projeto: FinAssist - Assistente Financeiro Serverless"
    echo ""

    # Verificações
    check_python
    check_git
    check_aws_cli
    check_sam_cli
    check_docker
    check_ngrok
    check_venv
    check_dependencies
    check_env_file
    check_project_structure

    # Relatório final
    print_summary
}

# Verificar Python
check_python() {
    print_header "Python"

    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
            print_success "Python $PYTHON_VERSION instalado (>= 3.9)"
        else
            print_error "Python $PYTHON_VERSION instalado, mas versão 3.9+ é necessária"
        fi
    else
        print_error "Python 3 não encontrado"
        print_info "Instale com: sudo apt install python3 python3-pip python3-venv -y"
    fi

    # pip
    if command_exists pip3 || command_exists pip; then
        print_success "pip encontrado"
    else
        print_error "pip não encontrado"
        print_info "Instale com: sudo apt install python3-pip -y"
    fi
}

# Verificar Git
check_git() {
    print_header "Git"

    if command_exists git; then
        GIT_VERSION=$(git --version | awk '{print $3}')
        print_success "Git $GIT_VERSION instalado"

        # Verificar configuração básica
        if git config user.name > /dev/null 2>&1 && git config user.email > /dev/null 2>&1; then
            print_success "Git configurado (user.name e user.email)"
        else
            print_warning "Git não está completamente configurado"
            print_info "Configure com: git config --global user.name 'Seu Nome'"
            print_info "              git config --global user.email 'seu@email.com'"
        fi
    else
        print_error "Git não encontrado"
        print_info "Instale com: sudo apt install git -y"
    fi
}

# Verificar AWS CLI
check_aws_cli() {
    print_header "AWS CLI"

    if command_exists aws; then
        AWS_VERSION=$(aws --version 2>&1 | awk '{print $1}' | cut -d'/' -f2)
        print_success "AWS CLI $AWS_VERSION instalado"

        # Verificar configuração
        if [ -f ~/.aws/credentials ] || [ -f ~/.aws/config ]; then
            print_success "AWS CLI configurado"

            # Testar credenciais
            if aws sts get-caller-identity > /dev/null 2>&1; then
                print_success "Credenciais AWS válidas"
            else
                print_warning "Credenciais AWS podem estar inválidas ou sem permissões"
                print_info "Teste com: aws sts get-caller-identity"
            fi
        else
            print_warning "AWS CLI não está configurado"
            print_info "Configure com: aws configure"
        fi
    else
        print_error "AWS CLI não encontrado"
        print_info "Instale com: ./scripts/install_dev_tools.sh"
        print_info "Ou manualmente: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    fi
}

# Verificar SAM CLI
check_sam_cli() {
    print_header "AWS SAM CLI"

    if command_exists sam; then
        SAM_VERSION=$(sam --version | awk '{print $4}')
        print_success "SAM CLI $SAM_VERSION instalado"

        # Verificar se SAM pode acessar Docker
        if command_exists docker; then
            if docker ps > /dev/null 2>&1; then
                print_success "SAM CLI pode acessar Docker"
            else
                print_warning "SAM CLI instalado, mas Docker não está acessível"
                print_info "Certifique-se de que Docker Desktop está rodando"
            fi
        fi
    else
        print_error "SAM CLI não encontrado"
        print_info "Instale com: ./scripts/install_dev_tools.sh"
        print_info "Ou manualmente: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    fi
}

# Verificar Docker
check_docker() {
    print_header "Docker"

    if command_exists docker; then
        # Tentar obter versão
        DOCKER_VERSION_OUTPUT=$(docker --version 2>&1)
        
        # Verificar se o comando foi bem-sucedido
        if echo "$DOCKER_VERSION_OUTPUT" | grep -q "Docker version"; then
            DOCKER_VERSION=$(echo "$DOCKER_VERSION_OUTPUT" | awk '{print $3}' | sed 's/,//')
            print_success "Docker $DOCKER_VERSION instalado"

            # Verificar se Docker está rodando
            if docker ps > /dev/null 2>&1; then
                print_success "Docker daemon está rodando"

                # Verificar containers rodando (opcional)
                RUNNING_CONTAINERS=$(docker ps --format '{{.Names}}' 2>/dev/null)
                if echo "$RUNNING_CONTAINERS" | grep -q "dynamodb"; then
                    print_success "DynamoDB Local está rodando"
                else
                    print_info "DynamoDB Local não está rodando (execute: make start-dynamodb-local)"
                fi
            else
                print_error "Docker daemon não está rodando"
                print_info "Inicie Docker Desktop e certifique-se da integração WSL2"
            fi
        else
            print_error "Docker encontrado, mas não está configurado para WSL2"
            print_info "Configure integração WSL2 em Docker Desktop:"
            print_info "Settings → Resources → WSL Integration"
        fi
    else
        print_error "Docker não encontrado"
        print_info "Instale Docker Desktop: https://www.docker.com/products/docker-desktop/"
        print_info "Configure integração WSL2 em: Settings → Resources → WSL Integration"
    fi
}

# Verificar ngrok
check_ngrok() {
    print_header "ngrok"

    if command_exists ngrok; then
        NGROK_VERSION=$(ngrok version 2>&1 | awk '{print $3}')
        print_success "ngrok $NGROK_VERSION instalado"

        # Verificar se está configurado
        if [ -f ~/.ngrok2/ngrok.yml ]; then
            print_success "ngrok configurado"
        else
            print_warning "ngrok não está configurado (authtoken não encontrado)"
            print_info "Configure com: ngrok config add-authtoken SEU_AUTHTOKEN"
            print_info "Obtenha authtoken em: https://dashboard.ngrok.com/get-started/your-authtoken"
        fi
    else
        print_error "ngrok não encontrado"
        print_info "Instale com: ./scripts/install_dev_tools.sh"
        print_info "Ou manualmente: https://ngrok.com/download"
    fi
}

# Verificar ambiente virtual Python
check_venv() {
    print_header "Ambiente Virtual Python"

    # Obter diretório do projeto
    PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    if [ -d "$PROJECT_DIR/.venv" ]; then
        print_success "Ambiente virtual encontrado (.venv/)"

        # Verificar se tem Python
        if [ -f "$PROJECT_DIR/.venv/bin/python" ]; then
            VENV_PYTHON_VERSION=$("$PROJECT_DIR/.venv/bin/python" --version | awk '{print $2}')
            print_success "Python no venv: $VENV_PYTHON_VERSION"
        fi

        # Verificar se está ativado
        if [ -n "$VIRTUAL_ENV" ]; then
            print_success "Ambiente virtual está ativado"
        else
            print_info "Ambiente virtual não está ativado"
            print_info "Ative com: source .venv/bin/activate"
        fi
    else
        print_warning "Ambiente virtual não encontrado"
        print_info "Crie com: python3 -m venv .venv"
        print_info "Ou com: make setup"
    fi
}

# Verificar dependências Python
check_dependencies() {
    print_header "Dependências Python"

    PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    # Verificar se requirements.txt existe
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        print_success "requirements.txt encontrado"
    else
        print_error "requirements.txt não encontrado"
        return
    fi

    # Verificar se dependências estão instaladas (se venv estiver ativado ou existir)
    if [ -n "$VIRTUAL_ENV" ] || [ -f "$PROJECT_DIR/.venv/bin/python" ]; then
        PYTHON_CMD="${VIRTUAL_ENV:-$PROJECT_DIR/.venv}/bin/python"

        # Verificar algumas dependências críticas
        CRITICAL_DEPS=("openai" "twilio" "boto3" "requests")
        ALL_INSTALLED=true

        for dep in "${CRITICAL_DEPS[@]}"; do
            if $PYTHON_CMD -c "import $dep" 2>/dev/null; then
                : # Dependência instalada
            else
                ALL_INSTALLED=false
                break
            fi
        done

        if $ALL_INSTALLED; then
            print_success "Dependências críticas instaladas"
        else
            print_warning "Algumas dependências podem não estar instaladas"
            print_info "Instale com: pip install -r requirements.txt"
        fi

        # Verificar pytest
        if $PYTHON_CMD -c "import pytest" 2>/dev/null; then
            print_success "pytest instalado"
        else
            print_warning "pytest não encontrado"
            print_info "Instale com: pip install -r requirements-dev.txt"
        fi
    else
        print_info "Ambiente virtual não ativado, pulando verificação de dependências"
    fi
}

# Verificar arquivo .env
check_env_file() {
    print_header "Variáveis de Ambiente"

    PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    # Verificar .env
    if [ -f "$PROJECT_DIR/.env" ]; then
        print_success "Arquivo .env encontrado"

        # Verificar variáveis críticas
        CRITICAL_VARS=("OPENAI_API_KEY" "ASSISTANT_ID" "TWILIO_ACCOUNT_SID" "TWILIO_AUTH_TOKEN")
        MISSING_VARS=()

        for var in "${CRITICAL_VARS[@]}"; do
            if grep -q "^${var}=" "$PROJECT_DIR/.env" 2>/dev/null; then
                VALUE=$(grep "^${var}=" "$PROJECT_DIR/.env" | cut -d'=' -f2)
                if [ -n "$VALUE" ] && [ "$VALUE" != "..." ] && [[ ! "$VALUE" =~ ^\.\.\. ]]; then
                    : # Variável configurada
                else
                    MISSING_VARS+=("$var")
                fi
            else
                MISSING_VARS+=("$var")
            fi
        done

        if [ ${#MISSING_VARS[@]} -eq 0 ]; then
            print_success "Variáveis críticas configuradas"
        else
            print_warning "Algumas variáveis críticas não estão configuradas:"
            for var in "${MISSING_VARS[@]}"; do
                echo "     - $var"
            done
            print_info "Edite o arquivo .env com suas credenciais"
        fi
    else
        print_warning "Arquivo .env não encontrado"

        if [ -f "$PROJECT_DIR/env.example" ]; then
            print_info "Crie com: cp env.example .env"
        else
            print_info "Crie o arquivo .env com suas credenciais"
        fi
    fi

    # Verificar env.json (para SAM CLI)
    if [ -f "$PROJECT_DIR/env.json" ]; then
        print_success "env.json encontrado (usado pelo SAM CLI)"
    else
        print_info "env.json não encontrado (necessário para SAM CLI local)"
        print_info "Gere com: make generate-env-json"
    fi
}

# Verificar estrutura do projeto
check_project_structure() {
    print_header "Estrutura do Projeto"

    PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    # Verificar diretórios principais
    REQUIRED_DIRS=("services" "data_access" "config" "tests" "scripts")
    MISSING_DIRS=()

    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ -d "$PROJECT_DIR/$dir" ]; then
            : # Diretório existe
        else
            MISSING_DIRS+=("$dir")
        fi
    done

    if [ ${#MISSING_DIRS[@]} -eq 0 ]; then
        print_success "Estrutura de diretórios correta"
    else
        print_warning "Alguns diretórios não foram encontrados:"
        for dir in "${MISSING_DIRS[@]}"; do
            echo "     - $dir/"
        done
    fi

    # Verificar arquivos principais
    REQUIRED_FILES=("lambda_function.py" "template.yaml" "requirements.txt" "Makefile")
    MISSING_FILES=()

    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$PROJECT_DIR/$file" ]; then
            : # Arquivo existe
        else
            MISSING_FILES+=("$file")
        fi
    done

    if [ ${#MISSING_FILES[@]} -eq 0 ]; then
        print_success "Arquivos principais presentes"
    else
        print_warning "Alguns arquivos principais não foram encontrados:"
        for file in "${MISSING_FILES[@]}"; do
            echo "     - $file"
        done
    fi
}

# Relatório final
print_summary() {
    print_header "Resumo da Verificação"

    echo -e "Total de verificações: $TOTAL_CHECKS"
    echo -e "${GREEN}✅ Passou: $PASSED_CHECKS${NC}"
    echo -e "${YELLOW}⚠️  Avisos: $WARNING_CHECKS${NC}"
    echo -e "${RED}❌ Falhou: $FAILED_CHECKS${NC}"
    echo ""

    # Status geral
    if [ $FAILED_CHECKS -eq 0 ] && [ $WARNING_CHECKS -eq 0 ]; then
        print_success "Ambiente está completamente configurado! 🎉"
        echo ""
        print_info "Próximos passos:"
        echo "  1. Leia: docs/PRIMEIROS_PASSOS.md"
        echo "  2. Inicie DynamoDB Local: make start-dynamodb-local"
        echo "  3. Inicie API local: make start-api"
        echo "  4. Execute testes: make test"
    elif [ $FAILED_CHECKS -eq 0 ]; then
        print_warning "Ambiente está funcional, mas alguns avisos foram encontrados"
        echo ""
        print_info "Revise os avisos acima e corrija se necessário"
        print_info "Consulte: docs/SETUP_AMBIENTE.md"
    else
        print_error "Ambiente não está completamente configurado"
        echo ""
        print_info "Resolva os erros acima antes de continuar"
        print_info "Consulte:"
        echo "  - docs/SETUP_AMBIENTE.md - Guia completo de instalação"
        echo "  - scripts/install_dev_tools.sh - Script de instalação automatizada"
        exit 1
    fi
}

# Executar script
main

