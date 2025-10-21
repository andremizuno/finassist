"""
Testes unitários para o TwilioService.
"""

import pytest
from services.twilio_service import TwilioService


@pytest.mark.unit
class TestTwilioService:
    """Testes para o serviço Twilio."""
    
    @pytest.fixture
    def service(self):
        """Fixture que retorna uma instância do TwilioService."""
        return TwilioService()
    
    def test_create_twiml_response_basic(self, service):
        """Testa criação básica de resposta TwiML."""
        message = "Olá, mundo!"
        twiml = service.create_twiml_response(message)
        
        # Verificar que é XML válido e contém a mensagem
        assert '<?xml version="1.0" encoding="UTF-8"?>' in twiml
        assert '<Response>' in twiml
        assert '<Message>' in twiml
        assert message in twiml
        assert '</Message>' in twiml
        assert '</Response>' in twiml
    
    def test_create_twiml_response_special_chars(self, service):
        """Testa TwiML com caracteres especiais."""
        message = "Você gastou R$ 150,50 em alimentação!"
        twiml = service.create_twiml_response(message)
        
        assert '<Response>' in twiml
        # A mensagem deve estar codificada corretamente
        assert 'alimenta' in twiml or 'alimentação' in twiml
    
    def test_create_error_response_default(self, service):
        """Testa resposta de erro padrão."""
        twiml = service.create_error_response()
        
        assert '<Response>' in twiml
        assert '<Message>' in twiml
        assert 'Desculpe' in twiml or 'erro' in twiml
    
    def test_create_error_response_custom(self, service):
        """Testa resposta de erro customizada."""
        custom_message = "Erro específico do teste"
        twiml = service.create_error_response(custom_message)
        
        assert '<Response>' in twiml
        assert custom_message in twiml
    
    def test_create_twiml_response_empty_string(self, service):
        """Testa TwiML com string vazia."""
        twiml = service.create_twiml_response("")
        
        # Deve gerar XML válido mesmo com mensagem vazia
        assert '<Response>' in twiml
        assert '</Response>' in twiml

