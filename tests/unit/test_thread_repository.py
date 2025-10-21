"""
Testes unitários para o ThreadRepository com mock do DynamoDB.
"""

import pytest
from moto import mock_dynamodb
import boto3
import os

from data_access.thread_repository import ThreadRepository
from config.settings import DYNAMODB_TABLE_NAME


@pytest.mark.unit
@mock_dynamodb
class TestThreadRepository:
    """Testes para o repositório de threads."""
    
    @pytest.fixture
    def dynamodb_table(self):
        """
        Fixture que cria uma tabela DynamoDB mockada.
        """
        # Configurar endpoint para usar o mock
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        
        # Criar cliente DynamoDB mockado
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Criar tabela
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
        
        # Aguardar criação da tabela
        table.meta.client.get_waiter('table_exists').wait(
            TableName=DYNAMODB_TABLE_NAME
        )
        
        yield table
        
        # Cleanup
        table.delete()
    
    @pytest.fixture
    def repository(self, dynamodb_table):
        """Fixture que retorna uma instância do ThreadRepository."""
        # O repository usará o DynamoDB mockado
        return ThreadRepository()
    
    def test_save_and_get_thread_id(self, repository):
        """Testa salvar e recuperar thread_id."""
        sender_id = "whatsapp:+5511999999999"
        thread_id = "thread_abc123"
        
        # Salvar
        repository.save_thread_id(sender_id, thread_id)
        
        # Recuperar
        retrieved_id = repository.get_thread_id(sender_id)
        
        assert retrieved_id == thread_id
    
    def test_get_nonexistent_thread_id(self, repository):
        """Testa recuperar thread_id que não existe."""
        sender_id = "whatsapp:+5511888888888"
        
        retrieved_id = repository.get_thread_id(sender_id)
        
        assert retrieved_id is None
    
    def test_update_thread_id(self, repository):
        """Testa atualizar thread_id existente."""
        sender_id = "whatsapp:+5511777777777"
        thread_id_1 = "thread_old"
        thread_id_2 = "thread_new"
        
        # Salvar primeiro thread_id
        repository.save_thread_id(sender_id, thread_id_1)
        
        # Atualizar com novo thread_id
        repository.save_thread_id(sender_id, thread_id_2)
        
        # Verificar que foi atualizado
        retrieved_id = repository.get_thread_id(sender_id)
        assert retrieved_id == thread_id_2
    
    def test_delete_thread(self, repository):
        """Testa deletar thread."""
        sender_id = "whatsapp:+5511666666666"
        thread_id = "thread_to_delete"
        
        # Salvar
        repository.save_thread_id(sender_id, thread_id)
        
        # Verificar que existe
        assert repository.get_thread_id(sender_id) == thread_id
        
        # Deletar
        repository.delete_thread(sender_id)
        
        # Verificar que foi deletado
        assert repository.get_thread_id(sender_id) is None

