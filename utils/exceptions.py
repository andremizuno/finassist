"""
Exceções customizadas para a aplicação.

Este módulo define exceções específicas para cada serviço externo
e operação, facilitando o tratamento de erros e debugging.
"""


class FinancialAssistantError(Exception):
    """
    Exceção base para todos os erros da aplicação.
    
    Todas as exceções customizadas devem herdar desta classe.
    """
    pass


class OpenAIAPIError(FinancialAssistantError):
    """
    Erro ao interagir com a OpenAI API.
    
    Exemplos:
    - Falha ao criar thread
    - Falha ao executar assistant
    - Timeout no polling de runs
    - Erro de autenticação
    """
    pass


class TwilioAPIError(FinancialAssistantError):
    """
    Erro ao interagir com a Twilio API.
    
    Exemplos:
    - Falha ao gerar TwiML
    - Erro de autenticação
    - Erro ao enviar mensagem
    """
    pass


class MicrosoftGraphAPIError(FinancialAssistantError):
    """
    Erro ao interagir com a Microsoft Graph API.
    
    Exemplos:
    - Falha ao obter access token
    - Falha ao refresh token
    - Erro ao acessar Excel/OneDrive
    - Permissões insuficientes
    """
    pass


class DynamoDBError(FinancialAssistantError):
    """
    Erro ao interagir com o DynamoDB.
    
    Exemplos:
    - Falha ao salvar thread_id
    - Falha ao recuperar thread_id
    - Tabela não encontrada
    - Erro de conexão
    """
    pass


class ToolExecutionError(FinancialAssistantError):
    """
    Erro ao executar uma ferramenta (tool) do Assistant.
    
    Exemplos:
    - Ferramenta não encontrada
    - Argumentos inválidos
    - Timeout na execução
    - Erro interno da ferramenta
    """
    pass


class ConfigurationError(FinancialAssistantError):
    """
    Erro de configuração da aplicação.
    
    Exemplos:
    - Variável de ambiente faltando
    - Valor de configuração inválido
    - Credenciais incorretas
    """
    pass

