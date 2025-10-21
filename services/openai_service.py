"""
Serviço para interação com a OpenAI Assistants API.

Este módulo gerencia toda a comunicação com a API de Assistants da OpenAI,
incluindo criação de threads, envio de mensagens, execução do assistant
e recuperação de respostas.
"""

import time
from typing import Dict, List, Any, Optional
from openai import OpenAI

from config.settings import (
    OPENAI_API_KEY,
    ASSISTANT_ID,
    ASSISTANT_RUN_POLLING_INTERVAL_SECONDS
)
from utils.logger import setup_logger
from utils.exceptions import OpenAIAPIError

# Logger específico deste módulo
logger = setup_logger(__name__)


class OpenAIService:
    """
    Serviço responsável por todas as interações com a OpenAI Assistants API.
    
    Gerencia threads, mensagens, execuções e respostas do Assistant.
    """
    
    def __init__(self):
        """Inicializa o cliente da OpenAI API."""
        if not OPENAI_API_KEY:
            raise OpenAIAPIError("OPENAI_API_KEY não está configurada")
        
        if not ASSISTANT_ID:
            raise OpenAIAPIError("ASSISTANT_ID não está configurado")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.assistant_id = ASSISTANT_ID
        logger.info(f"OpenAI Service inicializado com Assistant ID: {ASSISTANT_ID}")
    
    def create_thread(self) -> str:
        """
        Cria uma nova thread de conversa.
        
        Returns:
            str: ID da thread criada
            
        Raises:
            OpenAIAPIError: Se houver erro ao criar a thread
        """
        try:
            logger.debug("Criando nova thread no OpenAI")
            thread = self.client.beta.threads.create()
            logger.info(f"Thread criada com sucesso: {thread.id}")
            return thread.id
            
        except Exception as e:
            logger.error(f"Erro ao criar thread: {str(e)}")
            raise OpenAIAPIError(f"Falha ao criar thread: {str(e)}") from e
    
    def add_message(self, thread_id: str, content: str) -> None:
        """
        Adiciona uma mensagem do usuário à thread.
        
        Args:
            thread_id: ID da thread
            content: Conteúdo da mensagem do usuário
            
        Raises:
            OpenAIAPIError: Se houver erro ao adicionar a mensagem
        """
        try:
            logger.debug(f"Adicionando mensagem à thread {thread_id}")
            
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=content
            )
            
            logger.info(
                f"Mensagem adicionada com sucesso à thread {thread_id}"
            )
            
        except Exception as e:
            logger.error(
                f"Erro ao adicionar mensagem à thread {thread_id}: {str(e)}"
            )
            raise OpenAIAPIError(
                f"Falha ao adicionar mensagem: {str(e)}"
            ) from e
    
    def run_assistant(
        self,
        thread_id: str,
        max_wait_seconds: int = 60
    ) -> Dict[str, Any]:
        """
        Executa o assistant em uma thread e aguarda a conclusão.
        
        Faz polling do status da execução até que ela seja concluída,
        necessite de ação (tool calls) ou atinja o timeout.
        
        Args:
            thread_id: ID da thread
            max_wait_seconds: Tempo máximo de espera em segundos
            
        Returns:
            dict: Informações sobre a execução, incluindo status e tool calls
                  se aplicável. Formato:
                  {
                      'status': str,
                      'run_id': str,
                      'required_action': dict ou None
                  }
            
        Raises:
            OpenAIAPIError: Se houver erro na execução ou timeout
        """
        try:
            logger.debug(f"Iniciando execução do Assistant na thread {thread_id}")
            
            # Iniciar a execução
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
            
            logger.info(f"Run iniciado: {run.id} na thread {thread_id}")
            
            # Polling do status
            start_time = time.time()
            while True:
                # Verificar timeout
                elapsed = time.time() - start_time
                if elapsed > max_wait_seconds:
                    logger.error(
                        f"Timeout ao aguardar conclusão do run {run.id}"
                    )
                    raise OpenAIAPIError(
                        f"Timeout: Run não concluído em {max_wait_seconds}s"
                    )
                
                # Buscar status atualizado
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                
                logger.debug(f"Status do run {run.id}: {run.status}")
                
                # Verificar se concluído
                if run.status == "completed":
                    logger.info(f"Run {run.id} concluído com sucesso")
                    return {
                        'status': 'completed',
                        'run_id': run.id,
                        'required_action': None
                    }
                
                # Verificar se requer ação (tool calls)
                elif run.status == "requires_action":
                    logger.info(
                        f"Run {run.id} requer ação (tool calls)"
                    )
                    return {
                        'status': 'requires_action',
                        'run_id': run.id,
                        'required_action': run.required_action
                    }
                
                # Verificar se falhou
                elif run.status in ["failed", "cancelled", "expired"]:
                    error_msg = f"Run {run.id} falhou com status: {run.status}"
                    logger.error(error_msg)
                    raise OpenAIAPIError(error_msg)
                
                # Aguardar antes de verificar novamente
                time.sleep(ASSISTANT_RUN_POLLING_INTERVAL_SECONDS)
                
        except OpenAIAPIError:
            raise
        except Exception as e:
            logger.error(f"Erro ao executar assistant: {str(e)}")
            raise OpenAIAPIError(
                f"Falha ao executar assistant: {str(e)}"
            ) from e
    
    def submit_tool_outputs(
        self,
        thread_id: str,
        run_id: str,
        tool_outputs: List[Dict[str, str]]
    ) -> None:
        """
        Submete os resultados das tool calls de volta ao Assistant.
        
        Args:
            thread_id: ID da thread
            run_id: ID do run que requer as tool outputs
            tool_outputs: Lista de outputs das ferramentas. Formato:
                          [
                              {
                                  'tool_call_id': str,
                                  'output': str
                              },
                              ...
                          ]
            
        Raises:
            OpenAIAPIError: Se houver erro ao submeter os outputs
        """
        try:
            logger.debug(
                f"Submetendo tool outputs para run {run_id} na thread {thread_id}"
            )
            
            self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs
            )
            
            logger.info(
                f"Tool outputs submetidos com sucesso para run {run_id}"
            )
            
        except Exception as e:
            logger.error(
                f"Erro ao submeter tool outputs: {str(e)}"
            )
            raise OpenAIAPIError(
                f"Falha ao submeter tool outputs: {str(e)}"
            ) from e
    
    def get_messages(
        self,
        thread_id: str,
        limit: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Recupera as mensagens mais recentes de uma thread.
        
        Args:
            thread_id: ID da thread
            limit: Número máximo de mensagens a recuperar
            
        Returns:
            list: Lista de mensagens, cada uma como dict com:
                  {
                      'role': str ('user' ou 'assistant'),
                      'content': str
                  }
            
        Raises:
            OpenAIAPIError: Se houver erro ao recuperar mensagens
        """
        try:
            logger.debug(
                f"Recuperando {limit} mensagens da thread {thread_id}"
            )
            
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                limit=limit,
                order="desc"  # Mais recentes primeiro
            )
            
            # Extrair conteúdo das mensagens
            result = []
            for msg in messages.data:
                # Extrair texto do conteúdo (pode haver múltiplos blocos)
                text_content = ""
                for content_block in msg.content:
                    if content_block.type == "text":
                        text_content += content_block.text.value
                
                result.append({
                    'role': msg.role,
                    'content': text_content
                })
            
            logger.info(
                f"Recuperadas {len(result)} mensagens da thread {thread_id}"
            )
            return result
            
        except Exception as e:
            logger.error(
                f"Erro ao recuperar mensagens da thread {thread_id}: {str(e)}"
            )
            raise OpenAIAPIError(
                f"Falha ao recuperar mensagens: {str(e)}"
            ) from e


# Instância global do serviço (singleton pattern)
openai_service = OpenAIService()

