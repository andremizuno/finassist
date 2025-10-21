"""
Serviço para geração de respostas TwiML para o Twilio.

Este módulo cria as respostas no formato TwiML (XML) que o Twilio
espera receber dos webhooks para enviar mensagens de volta ao usuário.
"""

from twilio.twiml.messaging_response import MessagingResponse

from utils.logger import setup_logger
from utils.exceptions import TwilioAPIError

# Logger específico deste módulo
logger = setup_logger(__name__)


class TwilioService:
    """
    Serviço responsável por gerar respostas TwiML para o Twilio.
    
    O Twilio espera que o webhook retorne XML no formato TwiML
    com as mensagens que devem ser enviadas ao usuário.
    """
    
    def create_twiml_response(self, message_text: str) -> str:
        """
        Cria uma resposta TwiML contendo a mensagem especificada.
        
        Args:
            message_text: Texto da mensagem a ser enviada ao usuário
            
        Returns:
            str: XML TwiML formatado
            
        Raises:
            TwilioAPIError: Se houver erro ao gerar o TwiML
        """
        try:
            logger.debug(
                f"Gerando resposta TwiML com mensagem de {len(message_text)} caracteres"
            )
            
            # Criar objeto de resposta TwiML
            response = MessagingResponse()
            
            # Adicionar mensagem
            response.message(message_text)
            
            # Converter para string XML
            twiml = str(response)
            
            logger.info("Resposta TwiML gerada com sucesso")
            logger.debug(f"TwiML gerado: {twiml}")
            
            return twiml
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta TwiML: {str(e)}")
            raise TwilioAPIError(
                f"Falha ao gerar resposta TwiML: {str(e)}"
            ) from e
    
    def create_error_response(self, error_message: str = None) -> str:
        """
        Cria uma resposta TwiML de erro para o usuário.
        
        Útil quando ocorre um erro na aplicação e precisamos informar
        o usuário de forma amigável.
        
        Args:
            error_message: Mensagem de erro customizada (opcional)
            
        Returns:
            str: XML TwiML formatado com mensagem de erro
        """
        try:
            # Mensagem padrão se nenhuma for fornecida
            if not error_message:
                error_message = (
                    "Desculpe, ocorreu um erro ao processar sua mensagem. "
                    "Por favor, tente novamente em alguns instantes."
                )
            
            logger.debug("Gerando resposta TwiML de erro")
            
            response = MessagingResponse()
            response.message(error_message)
            
            twiml = str(response)
            
            logger.info("Resposta TwiML de erro gerada")
            return twiml
            
        except Exception as e:
            # Se até a geração de erro falhar, retornar XML mínimo válido
            logger.error(f"Erro crítico ao gerar resposta de erro: {str(e)}")
            return '<?xml version="1.0" encoding="UTF-8"?><Response><Message>Erro no sistema</Message></Response>'


# Instância global do serviço (singleton pattern)
twilio_service = TwilioService()

