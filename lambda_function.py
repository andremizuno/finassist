"""
Handler principal do AWS Lambda para o Assistente Financeiro.

Este módulo serve como entry point da função Lambda, processando
webhooks do Twilio (WhatsApp) e retornando respostas TwiML.
"""

import json
from urllib.parse import parse_qs
from typing import Dict, Any

from conversation_manager import conversation_manager
from services.twilio_service import twilio_service
from utils.logger import setup_logger
from utils.exceptions import FinancialAssistantError

# Logger específico deste módulo
logger = setup_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal da função Lambda.
    
    Este handler é invocado pelo AWS Lambda quando há uma requisição
    do API Gateway (webhook do Twilio).
    
    Args:
        event: Evento do API Gateway contendo dados da requisição
        context: Contexto de execução do Lambda
    
    Returns:
        dict: Resposta HTTP com TwiML para o Twilio
    """
    logger.info("=== Início da execução do Lambda ===")
    logger.debug(f"Event recebido: {json.dumps(event)}")
    
    try:
        # Etapa 1: Parsear o body da requisição
        # O Twilio envia dados como application/x-www-form-urlencoded
        body = event.get('body', '')
        
        if event.get('isBase64Encoded', False):
            import base64
            body = base64.b64decode(body).decode('utf-8')
        
        # Parse dos parâmetros form-urlencoded
        params = parse_qs(body)
        
        logger.debug(f"Parâmetros parseados: {params}")
        
        # Etapa 2: Extrair informações da mensagem do Twilio
        # O Twilio envia os valores como listas, pegamos o primeiro item
        sender_id = params.get('From', [''])[0]
        message_body = params.get('Body', [''])[0]
        
        if not sender_id or not message_body:
            logger.error(
                "Requisição inválida: 'From' ou 'Body' ausentes"
            )
            return _create_error_response(
                status_code=400,
                message="Requisição inválida: dados ausentes"
            )
        
        logger.info(
            f"Mensagem recebida de {sender_id}: {message_body[:100]}..."
        )
        
        # Etapa 3: Processar mensagem através do ConversationManager
        try:
            response_text = conversation_manager.handle_incoming_message(
                sender_id=sender_id,
                message_text=message_body
            )
            
            logger.info("Mensagem processada com sucesso")
            
        except FinancialAssistantError as e:
            # Erro conhecido da aplicação - retornar mensagem amigável
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            response_text = (
                "Desculpe, ocorreu um erro ao processar sua mensagem. "
                "Por favor, tente novamente em alguns instantes."
            )
        
        # Etapa 4: Gerar resposta TwiML
        twiml = twilio_service.create_twiml_response(response_text)
        
        # Etapa 5: Retornar resposta HTTP para o API Gateway
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/xml',
                'Access-Control-Allow-Origin': '*'  # Para CORS
            },
            'body': twiml
        }
        
    except Exception as e:
        # Erro inesperado - logar e retornar erro genérico
        logger.error(
            f"Erro crítico não tratado no lambda_handler: {str(e)}",
            exc_info=True
        )
        return _create_error_response(
            status_code=500,
            message="Erro interno do servidor"
        )
    
    finally:
        logger.info("=== Fim da execução do Lambda ===")


def _create_error_response(
    status_code: int,
    message: str
) -> Dict[str, Any]:
    """
    Cria uma resposta HTTP de erro.
    
    Args:
        status_code: Código HTTP de erro
        message: Mensagem de erro
    
    Returns:
        dict: Resposta HTTP formatada
    """
    # Gerar TwiML de erro para o usuário
    twiml = twilio_service.create_error_response()
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'text/xml',
            'Access-Control-Allow-Origin': '*'
        },
        'body': twiml
    }


# Para testes locais
if __name__ == '__main__':
    """
    Permite testar o handler localmente sem o SAM CLI.
    
    Execute: python lambda_function.py
    """
    # Evento de exemplo simulando webhook do Twilio
    test_event = {
        'body': 'From=whatsapp%3A%2B5511999999999&Body=Olá%2C%20quanto%20gastei%20este%20mês%3F',
        'isBase64Encoded': False
    }
    
    # Contexto mock (não usado neste handler)
    test_context = {}
    
    print("Testando lambda_handler localmente...")
    result = lambda_handler(test_event, test_context)
    print(f"\nResultado: {json.dumps(result, indent=2)}")

