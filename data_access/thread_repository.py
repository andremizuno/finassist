"""
Repositório para gerenciar threads do OpenAI Assistant no DynamoDB.

Este módulo é responsável por persistir e recuperar o mapeamento
entre sender_id (telefone do usuário) e thread_id (conversa do Assistant).
"""

import boto3
from botocore.exceptions import ClientError
from typing import Optional

from config.settings import DYNAMODB_TABLE_NAME, DYNAMODB_ENDPOINT_URL
from utils.logger import setup_logger
from utils.exceptions import DynamoDBError

# Logger específico deste módulo
logger = setup_logger(__name__)


class ThreadRepository:
    """
    Classe responsável por operações de persistência no DynamoDB.
    
    Gerencia o mapeamento sender_id <-> thread_id, permitindo que
    cada usuário tenha uma conversa contínua com o Assistant.
    """
    
    def __init__(self):
        """
        Inicializa o repositório configurando a conexão com DynamoDB.
        
        Se DYNAMODB_ENDPOINT_URL estiver definido, usa DynamoDB Local.
        Caso contrário, usa o serviço DynamoDB da AWS.
        """
        # Configurar conexão com DynamoDB
        if DYNAMODB_ENDPOINT_URL:
            # Modo desenvolvimento local
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url=DYNAMODB_ENDPOINT_URL
            )
            logger.info(f"Usando DynamoDB Local em {DYNAMODB_ENDPOINT_URL}")
        else:
            # Modo produção (AWS)
            self.dynamodb = boto3.resource('dynamodb')
            logger.info("Usando AWS DynamoDB (produção)")
        
        self.table = self.dynamodb.Table(DYNAMODB_TABLE_NAME)
        logger.info(f"Tabela DynamoDB configurada: {DYNAMODB_TABLE_NAME}")
    
    def get_thread_id(self, sender_id: str) -> Optional[str]:
        """
        Recupera o thread_id associado a um sender_id.
        
        Args:
            sender_id: Identificador único do usuário (ex: número WhatsApp)
            
        Returns:
            str ou None: thread_id se encontrado, None caso contrário
            
        Raises:
            DynamoDBError: Se houver erro ao acessar o DynamoDB
        """
        try:
            logger.debug(f"Buscando thread_id para sender_id: {sender_id}")
            
            response = self.table.get_item(
                Key={'sender_id': sender_id}
            )
            
            # Verificar se o item foi encontrado
            if 'Item' in response:
                thread_id = response['Item'].get('thread_id')
                logger.info(
                    f"Thread encontrada: sender_id={sender_id}, "
                    f"thread_id={thread_id}"
                )
                return thread_id
            else:
                logger.info(
                    f"Nenhuma thread encontrada para sender_id: {sender_id}"
                )
                return None
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(
                f"Erro ao buscar thread_id no DynamoDB: {error_code} - {error_message}"
            )
            raise DynamoDBError(
                f"Falha ao recuperar thread_id: {error_message}"
            ) from e
    
    def save_thread_id(self, sender_id: str, thread_id: str) -> None:
        """
        Salva o mapeamento sender_id -> thread_id no DynamoDB.
        
        Args:
            sender_id: Identificador único do usuário
            thread_id: ID da thread do OpenAI Assistant
            
        Raises:
            DynamoDBError: Se houver erro ao salvar no DynamoDB
        """
        try:
            logger.debug(
                f"Salvando mapeamento: sender_id={sender_id}, "
                f"thread_id={thread_id}"
            )
            
            self.table.put_item(
                Item={
                    'sender_id': sender_id,
                    'thread_id': thread_id
                }
            )
            
            logger.info(
                f"Mapeamento salvo com sucesso: sender_id={sender_id}"
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(
                f"Erro ao salvar thread_id no DynamoDB: {error_code} - {error_message}"
            )
            raise DynamoDBError(
                f"Falha ao salvar thread_id: {error_message}"
            ) from e
    
    def delete_thread(self, sender_id: str) -> None:
        """
        Remove o mapeamento de um sender_id do DynamoDB.
        
        Útil para resetar conversas ou limpar dados de teste.
        
        Args:
            sender_id: Identificador único do usuário
            
        Raises:
            DynamoDBError: Se houver erro ao deletar do DynamoDB
        """
        try:
            logger.debug(f"Deletando mapeamento para sender_id: {sender_id}")
            
            self.table.delete_item(
                Key={'sender_id': sender_id}
            )
            
            logger.info(
                f"Mapeamento deletado com sucesso: sender_id={sender_id}"
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(
                f"Erro ao deletar thread_id no DynamoDB: {error_code} - {error_message}"
            )
            raise DynamoDBError(
                f"Falha ao deletar thread_id: {error_message}"
            ) from e


# Instância global do repositório (singleton pattern)
# Esta instância pode ser importada e reutilizada em toda a aplicação
thread_repository = ThreadRepository()

