# Makefile para automação de tarefas do Assistente Financeiro
# Execute 'make help' para ver todos os comandos disponíveis

.PHONY: help setup install install-dev clean test lint format \
        generate-env-json start-dynamodb-local create-dynamodb-table \
        stop-dynamodb-local start-api start-ngrok oauth-setup build deploy

# Variáveis
VENV_DIR = .venv
PYTHON = python3
PIP = $(VENV_DIR)/bin/pip
PYTEST = $(VENV_DIR)/bin/pytest
BLACK = $(VENV_DIR)/bin/black
FLAKE8 = $(VENV_DIR)/bin/flake8
SAM = sam
DOCKER_COMPOSE = docker-compose

# Cores para output
COLOR_RESET = \033[0m
COLOR_BOLD = \033[1m
COLOR_GREEN = \033[32m
COLOR_YELLOW = \033[33m
COLOR_BLUE = \033[34m

# Default target
.DEFAULT_GOAL := help

help: ## Mostra esta mensagem de ajuda
	@echo "$(COLOR_BOLD)Assistente Financeiro - Comandos Disponíveis$(COLOR_RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_GREEN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""

setup: ## Configura o ambiente de desenvolvimento (cria venv e instala dependências)
	@echo "$(COLOR_BLUE)Configurando ambiente de desenvolvimento...$(COLOR_RESET)"
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	@echo "$(COLOR_GREEN)✓ Ambiente configurado com sucesso!$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_YELLOW)Próximos passos:$(COLOR_RESET)"
	@echo "  1. Ative o ambiente virtual: source $(VENV_DIR)/bin/activate"
	@echo "  2. Copie .env.example para .env e configure suas credenciais"
	@echo "  3. Execute: make generate-env-json"

install: ## Instala apenas dependências de produção
	$(PIP) install -r requirements.txt

install-dev: ## Instala dependências de desenvolvimento
	$(PIP) install -r requirements-dev.txt

clean: ## Remove arquivos temporários e artefatos de build
	@echo "$(COLOR_YELLOW)Limpando artefatos...$(COLOR_RESET)"
	rm -rf $(VENV_DIR)
	rm -rf .aws-sam/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f env.json
	rm -f .ms_graph_tokens.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(COLOR_GREEN)✓ Limpeza concluída!$(COLOR_RESET)"

test: ## Executa todos os testes com coverage
	@echo "$(COLOR_BLUE)Executando testes...$(COLOR_RESET)"
	$(PYTEST)

test-unit: ## Executa apenas testes unitários
	@echo "$(COLOR_BLUE)Executando testes unitários...$(COLOR_RESET)"
	$(PYTEST) -m unit

test-integration: ## Executa apenas testes de integração
	@echo "$(COLOR_BLUE)Executando testes de integração...$(COLOR_RESET)"
	$(PYTEST) -m integration

lint: ## Verifica qualidade do código com flake8
	@echo "$(COLOR_BLUE)Verificando qualidade do código...$(COLOR_RESET)"
	$(FLAKE8) . --count --select=E9,F63,F7,F82 --show-source --statistics
	$(FLAKE8) . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

format: ## Formata código com black
	@echo "$(COLOR_BLUE)Formatando código...$(COLOR_RESET)"
	$(BLACK) .
	@echo "$(COLOR_GREEN)✓ Código formatado!$(COLOR_RESET)"

generate-env-json: ## Gera env.json a partir do .env para SAM CLI
	@echo "$(COLOR_BLUE)Gerando env.json...$(COLOR_RESET)"
	$(PYTHON) scripts/generate_env_json.py

start-dynamodb-local: ## Inicia DynamoDB Local via Docker
	@echo "$(COLOR_BLUE)Iniciando DynamoDB Local...$(COLOR_RESET)"
	$(DOCKER_COMPOSE) up -d dynamodb-local
	@echo "$(COLOR_GREEN)✓ DynamoDB Local rodando na porta 8000$(COLOR_RESET)"
	@sleep 2
	@make create-dynamodb-table

stop-dynamodb-local: ## Para DynamoDB Local
	@echo "$(COLOR_YELLOW)Parando DynamoDB Local...$(COLOR_RESET)"
	$(DOCKER_COMPOSE) down

create-dynamodb-table: ## Cria tabela no DynamoDB Local
	@echo "$(COLOR_BLUE)Criando tabela no DynamoDB Local...$(COLOR_RESET)"
	@aws dynamodb create-table \
		--table-name FinancialAssistantThreads \
		--attribute-definitions AttributeName=sender_id,AttributeType=S \
		--key-schema AttributeName=sender_id,KeyType=HASH \
		--billing-mode PAY_PER_REQUEST \
		--endpoint-url http://localhost:8000 \
		--region us-east-1 \
		2>/dev/null && echo "$(COLOR_GREEN)✓ Tabela criada!$(COLOR_RESET)" || echo "$(COLOR_YELLOW)Tabela já existe$(COLOR_RESET)"

build: generate-env-json ## Builda a aplicação com SAM
	@echo "$(COLOR_BLUE)Building aplicação...$(COLOR_RESET)"
	$(SAM) build

start-api: build ## Inicia API local com SAM CLI
	@echo "$(COLOR_BLUE)Iniciando API local com SAM CLI...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)API estará disponível em: http://127.0.0.1:3000$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Webhook endpoint: http://127.0.0.1:3000/webhook/whatsapp$(COLOR_RESET)"
	@echo ""
	$(SAM) local start-api --env-vars env.json --port 3000

start-ngrok: ## Inicia ngrok para expor API local
	@echo "$(COLOR_BLUE)Iniciando ngrok...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Configure o webhook do Twilio com a URL HTTPS exibida pelo ngrok$(COLOR_RESET)"
	@echo ""
	ngrok http 3000

oauth-setup: ## Executa fluxo OAuth para obter tokens do Microsoft Graph
	@echo "$(COLOR_BLUE)Iniciando configuração OAuth do Microsoft Graph...$(COLOR_RESET)"
	$(PYTHON) scripts/oauth_microsoft_graph.py

create-assistant: ## Cria um novo OpenAI Assistant com configurações pré-definidas
	@echo "$(COLOR_BLUE)Criando OpenAI Assistant...$(COLOR_RESET)"
	$(PYTHON) scripts/create_assistant.py

deploy: ## Faz deploy da aplicação para AWS (PRODUÇÃO)
	@echo "$(COLOR_YELLOW)⚠️  ATENÇÃO: Você está prestes a fazer deploy em PRODUÇÃO!$(COLOR_RESET)"
	@echo ""
	@read -p "Digite 'sim' para confirmar: " confirm; \
	if [ "$$confirm" = "sim" ]; then \
		echo "$(COLOR_BLUE)Fazendo deploy...$(COLOR_RESET)"; \
		$(SAM) build && \
		$(SAM) deploy --guided; \
	else \
		echo "$(COLOR_YELLOW)Deploy cancelado$(COLOR_RESET)"; \
	fi

validate-template: ## Valida o template SAM
	@echo "$(COLOR_BLUE)Validando template.yaml...$(COLOR_RESET)"
	$(SAM) validate

logs: ## Exibe logs da função Lambda (requer AWS CLI configurado)
	@echo "$(COLOR_BLUE)Buscando logs...$(COLOR_RESET)"
	$(SAM) logs -n FinancialAssistantFunction --stack-name financial-assistant-prod --tail

invoke-local: ## Invoca a função Lambda localmente com evento de teste
	@echo "$(COLOR_BLUE)Invocando função Lambda localmente...$(COLOR_RESET)"
	@echo '{"body": "From=whatsapp%3A%2B5511999999999&Body=Ol%C3%A1", "isBase64Encoded": false}' | \
	$(SAM) local invoke FinancialAssistantFunction --env-vars env.json --event -

