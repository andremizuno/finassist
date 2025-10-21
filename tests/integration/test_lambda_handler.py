"""
Testes de integração para o lambda_handler.
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from lambda_function import lambda_handler


@pytest.mark.integration
class TestLambdaHandler:
    """Testes de integração end-to-end para o lambda handler."""
    
    @patch('lambda_function.conversation_manager')
    def test_lambda_handler_success(self, mock_conversation_manager):
        """Testa execução bem-sucedida do lambda handler."""
        # Mock da resposta do conversation manager
        mock_conversation_manager.handle_incoming_message.return_value = (
            "Você gastou R$ 150,00 em alimentação este mês."
        )
        
        # Evento simulando webhook do Twilio
        event = {
            'body': 'From=whatsapp%3A%2B5511999999999&Body=Quanto%20gastei%20em%20alimenta%C3%A7%C3%A3o%3F',
            'isBase64Encoded': False
        }
        
        context = {}
        
        # Executar handler
        response = lambda_handler(event, context)
        
        # Verificar resposta
        assert response['statusCode'] == 200
        assert response['headers']['Content-Type'] == 'text/xml'
        assert '<Response>' in response['body']
        assert '<Message>' in response['body']
        
        # Verificar que o conversation manager foi chamado
        mock_conversation_manager.handle_incoming_message.assert_called_once()
        call_args = mock_conversation_manager.handle_incoming_message.call_args
        assert 'whatsapp:+5511999999999' in call_args[1]['sender_id']
    
    @patch('lambda_function.conversation_manager')
    def test_lambda_handler_with_error(self, mock_conversation_manager):
        """Testa lambda handler quando ocorre erro no processamento."""
        # Mock que lança exceção
        from utils.exceptions import FinancialAssistantError
        mock_conversation_manager.handle_incoming_message.side_effect = (
            FinancialAssistantError("Erro no processamento")
        )
        
        event = {
            'body': 'From=whatsapp%3A%2B5511999999999&Body=teste',
            'isBase64Encoded': False
        }
        
        context = {}
        
        # Executar handler
        response = lambda_handler(event, context)
        
        # Deve retornar resposta de erro mas com status 200 (para Twilio)
        assert response['statusCode'] == 200
        assert '<Response>' in response['body']
        # A mensagem de erro deve estar contida na resposta
        assert 'Desculpe' in response['body'] or 'erro' in response['body'].lower()
    
    def test_lambda_handler_missing_parameters(self):
        """Testa lambda handler com parâmetros ausentes."""
        # Evento sem 'From' ou 'Body'
        event = {
            'body': 'InvalidParam=value',
            'isBase64Encoded': False
        }
        
        context = {}
        
        # Executar handler
        response = lambda_handler(event, context)
        
        # Deve retornar erro 400
        assert response['statusCode'] == 400
    
    @patch('lambda_function.conversation_manager')
    def test_lambda_handler_base64_encoded(self, mock_conversation_manager):
        """Testa lambda handler com body codificado em base64."""
        import base64
        
        mock_conversation_manager.handle_incoming_message.return_value = "Resposta"
        
        # Body codificado em base64
        body_raw = 'From=whatsapp%3A%2B5511999999999&Body=teste'
        body_encoded = base64.b64encode(body_raw.encode('utf-8')).decode('utf-8')
        
        event = {
            'body': body_encoded,
            'isBase64Encoded': True
        }
        
        context = {}
        
        # Executar handler
        response = lambda_handler(event, context)
        
        # Deve processar corretamente
        assert response['statusCode'] == 200
        mock_conversation_manager.handle_incoming_message.assert_called_once()

