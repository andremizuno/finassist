"""
Testes de integração com DynamoDB Local.

Estes testes requerem que o DynamoDB Local esteja rodando.
Execute: docker-compose up dynamodb-local
"""

import pytest
import boto3
import os
from botocore.exceptions import ClientError

from data_access.thread_repository import ThreadRepository
from config.settings import DYNAMODB_TABLE_NAME


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv('DYNAMODB_ENDPOINT_URL'),
    reason="DynamoDB Local não está configurado"
)
class TestDynamoDBIntegration:
    """
    Testes de integração com DynamoDB Local.
    
    Requer DynamoDB Local rodando e DYNAMODB_ENDPOINT_URL configurado.
    """
    
    @pytest.fixture(scope='class')
    def dynamodb_table(self):
        """
        Fixture que cria uma tabela real no DynamoDB Local.
        """
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=os.getenv('DYNAMODB_ENDPOINT_URL')
        )
        
        # Tentar criar tabela (pode já existir)
        try:
            table = dynamodb.create_table(
                TableName=DYNAMODB_TABLE_NAME,
                KeySchema=[
                    {'AttributeName': 'sender_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'sender_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Aguardar criação
            table.meta.client.get_waiter('table_exists').wait(
                TableName=DYNAMODB_TABLE_NAME
            )
            
            yield table
            
            # Cleanup: deletar tabela após testes
            table.delete()
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                # Tabela já existe, usar ela
                table = dynamodb.Table(DYNAMODB_TABLE_NAME)
                yield table
            else:
                raise
    
    @pytest.fixture
    def repository(self, dynamodb_table):
        """Fixture que retorna uma instância do ThreadRepository."""
        return ThreadRepository()
    
    def test_real_save_and_get(self, repository):
        """Testa salvar e recuperar dados reais."""
        sender_id = f"test:integration:{os.getpid()}"
        thread_id = "thread_integration_test"
        
        # Salvar
        repository.save_thread_id(sender_id, thread_id)
        
        # Recuperar
        retrieved_id = repository.get_thread_id(sender_id)
        
        assert retrieved_id == thread_id
        
        # Cleanup
        repository.delete_thread(sender_id)
    
    def test_real_delete(self, repository):
        """Testa deletar dados reais."""
        sender_id = f"test:integration:delete:{os.getpid()}"
        thread_id = "thread_to_delete"
        
        # Salvar
        repository.save_thread_id(sender_id, thread_id)
        
        # Verificar que existe
        assert repository.get_thread_id(sender_id) == thread_id
        
        # Deletar
        repository.delete_thread(sender_id)
        
        # Verificar que não existe mais
        assert repository.get_thread_id(sender_id) is None

