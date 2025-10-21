"""
Configurações da aplicação.

Este módulo carrega todas as variáveis de ambiente necessárias
para a aplicação funcionar, tanto em desenvolvimento local quanto
em produção no AWS Lambda.
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
# Isso funciona apenas em desenvolvimento local
# No Lambda, as variáveis são injetadas diretamente pelo AWS
load_dotenv()


# ============================================
# OpenAI Assistant API
# ============================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")


# ============================================
# Twilio (WhatsApp)
# ============================================
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")


# ============================================
# Microsoft Graph API (Azure AD)
# ============================================
MS_GRAPH_CLIENT_ID = os.getenv("MS_GRAPH_CLIENT_ID")
MS_GRAPH_CLIENT_SECRET = os.getenv("MS_GRAPH_CLIENT_SECRET")
MS_GRAPH_TENANT_ID = os.getenv("MS_GRAPH_TENANT_ID", "common")

# Tokens OAuth2 (gerenciados dinamicamente pelo excel_service)
MS_GRAPH_REFRESH_TOKEN = os.getenv("MS_GRAPH_REFRESH_TOKEN")
MS_GRAPH_ACCESS_TOKEN = os.getenv("MS_GRAPH_ACCESS_TOKEN")
MS_GRAPH_TOKEN_EXPIRATION_INITIAL = os.getenv("MS_GRAPH_TOKEN_EXPIRATION_INITIAL", "0")


# ============================================
# AWS DynamoDB
# ============================================
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "FinancialAssistantThreads")

# Endpoint personalizado para DynamoDB Local (apenas dev local)
# Se não estiver definido, usa o serviço DynamoDB da AWS
DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL")


# ============================================
# Configurações da Aplicação
# ============================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Timeout máximo para execução de ferramentas (segundos)
TOOL_EXECUTION_TIMEOUT_SECONDS = int(
    os.getenv("TOOL_EXECUTION_TIMEOUT_SECONDS", "60")
)

# Intervalo de polling para verificar status do Assistant Run (segundos)
ASSISTANT_RUN_POLLING_INTERVAL_SECONDS = int(
    os.getenv("ASSISTANT_RUN_POLLING_INTERVAL_SECONDS", "1")
)


# ============================================
# Validações
# ============================================

def validate_configuration():
    """
    Valida se as configurações essenciais estão presentes.
    
    Exibe avisos para configurações faltantes, mas não bloqueia
    a aplicação (útil para testes e desenvolvimento incremental).
    """
    # Validar OpenAI
    if not OPENAI_API_KEY or not ASSISTANT_ID:
        print(
            "⚠️  AVISO: Variáveis de ambiente OpenAI (OPENAI_API_KEY, ASSISTANT_ID) "
            "podem estar faltando ou incorretas."
        )
    
    # Validar Twilio
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER]):
        print(
            "⚠️  AVISO: Variáveis de ambiente Twilio (TWILIO_ACCOUNT_SID, "
            "TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER) podem estar faltando."
        )
    
    # Validar Microsoft Graph
    if not all([MS_GRAPH_CLIENT_ID, MS_GRAPH_CLIENT_SECRET]):
        print(
            "⚠️  AVISO: Variáveis de ambiente Microsoft Graph (MS_GRAPH_CLIENT_ID, "
            "MS_GRAPH_CLIENT_SECRET) podem estar faltando."
        )
    
    # Informar sobre DynamoDB Local
    if DYNAMODB_ENDPOINT_URL:
        print(
            f"ℹ️  INFO: Usando DynamoDB Local em {DYNAMODB_ENDPOINT_URL}"
        )
    else:
        print(
            "ℹ️  INFO: Usando AWS DynamoDB (produção/nuvem)"
        )


# Executar validação ao importar o módulo
# Comentar esta linha se quiser desabilitar os avisos
validate_configuration()

