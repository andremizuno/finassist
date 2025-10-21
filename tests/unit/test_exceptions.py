"""
Testes unitários para exceções customizadas.
"""

import pytest
from utils.exceptions import (
    FinancialAssistantError,
    OpenAIAPIError,
    TwilioAPIError,
    MicrosoftGraphAPIError,
    DynamoDBError,
    ToolExecutionError,
    ConfigurationError
)


@pytest.mark.unit
class TestExceptions:
    """Testes para as exceções customizadas."""
    
    def test_base_exception(self):
        """Testa a exceção base."""
        error = FinancialAssistantError("Erro base")
        assert str(error) == "Erro base"
        assert isinstance(error, Exception)
    
    def test_openai_api_error(self):
        """Testa exceção da OpenAI API."""
        error = OpenAIAPIError("Erro na OpenAI")
        assert isinstance(error, FinancialAssistantError)
        assert str(error) == "Erro na OpenAI"
    
    def test_twilio_api_error(self):
        """Testa exceção da Twilio API."""
        error = TwilioAPIError("Erro no Twilio")
        assert isinstance(error, FinancialAssistantError)
        assert str(error) == "Erro no Twilio"
    
    def test_microsoft_graph_api_error(self):
        """Testa exceção da Microsoft Graph API."""
        error = MicrosoftGraphAPIError("Erro no Graph")
        assert isinstance(error, FinancialAssistantError)
        assert str(error) == "Erro no Graph"
    
    def test_dynamodb_error(self):
        """Testa exceção do DynamoDB."""
        error = DynamoDBError("Erro no DynamoDB")
        assert isinstance(error, FinancialAssistantError)
        assert str(error) == "Erro no DynamoDB"
    
    def test_tool_execution_error(self):
        """Testa exceção de execução de ferramenta."""
        error = ToolExecutionError("Erro na ferramenta")
        assert isinstance(error, FinancialAssistantError)
        assert str(error) == "Erro na ferramenta"
    
    def test_configuration_error(self):
        """Testa exceção de configuração."""
        error = ConfigurationError("Erro de configuração")
        assert isinstance(error, FinancialAssistantError)
        assert str(error) == "Erro de configuração"

