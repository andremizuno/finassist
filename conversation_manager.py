"""
Gerenciador de conversação com o OpenAI Assistant.

Este módulo orquestra todo o fluxo de conversação:
1. Obter ou criar thread do usuário
2. Adicionar mensagem à thread
3. Executar o assistant
4. Processar tool calls se necessário
5. Retornar resposta final
"""

import json
from typing import Dict, Any, List

from services.openai_service import openai_service
from data_access.thread_repository import thread_repository
from tools.tool_executor import tool_executor
from utils.logger import setup_logger
from utils.exceptions import (
    FinancialAssistantError,
    OpenAIAPIError,
    DynamoDBError,
    ToolExecutionError
)

# Logger específico deste módulo
logger = setup_logger(__name__)


class ConversationManager:
    """
    Gerenciador responsável por orquestrar toda a conversa com o usuário.
    
    Coordena os serviços de OpenAI, DynamoDB e execução de ferramentas
    para processar mensagens do usuário e gerar respostas.
    """
    
    def __init__(self):
        """Inicializa o gerenciador."""
        logger.info("ConversationManager inicializado")
    
    def handle_incoming_message(
        self,
        sender_id: str,
        message_text: str
    ) -> str:
        """
        Processa uma mensagem recebida e retorna a resposta do assistant.
        
        Este é o método principal que coordena todo o fluxo:
        1. Obter/criar thread para o usuário
        2. Adicionar mensagem à thread
        3. Executar o assistant
        4. Se necessário, executar tool calls e resubmeter
        5. Retornar resposta final
        
        Args:
            sender_id: ID único do remetente (ex: número WhatsApp)
            message_text: Texto da mensagem enviada pelo usuário
        
        Returns:
            str: Resposta gerada pelo assistant
        
        Raises:
            FinancialAssistantError: Se houver erro no processamento
        """
        logger.info(
            f"Processando mensagem de {sender_id}: {message_text[:50]}..."
        )
        
        try:
            # Etapa 1: Obter ou criar thread para o usuário
            thread_id = self._get_or_create_thread(sender_id)
            logger.debug(f"Usando thread_id: {thread_id}")
            
            # Etapa 2: Adicionar mensagem do usuário à thread
            openai_service.add_message(thread_id, message_text)
            
            # Etapa 3: Executar o assistant
            run_result = openai_service.run_assistant(thread_id)
            
            # Etapa 4: Processar tool calls se necessário
            if run_result['status'] == 'requires_action':
                logger.info("Assistant requer execução de ferramentas")
                self._process_tool_calls(thread_id, run_result)
                
                # Após submeter tool outputs, aguardar conclusão
                # O Assistant continuará processando automaticamente
                run_result = openai_service.run_assistant(thread_id)
            
            # Etapa 5: Obter e retornar resposta final
            if run_result['status'] == 'completed':
                messages = openai_service.get_messages(thread_id, limit=1)
                
                if messages and messages[0]['role'] == 'assistant':
                    response = messages[0]['content']
                    logger.info(
                        f"Resposta gerada com sucesso para {sender_id}"
                    )
                    return response
                else:
                    logger.warning("Nenhuma resposta do assistant encontrada")
                    return "Desculpe, não consegui gerar uma resposta."
            else:
                logger.error(
                    f"Run não concluído corretamente: {run_result['status']}"
                )
                return "Desculpe, houve um problema ao processar sua mensagem."
                
        except DynamoDBError as e:
            logger.error(f"Erro no DynamoDB: {str(e)}")
            raise FinancialAssistantError(
                "Erro ao acessar banco de dados"
            ) from e
            
        except OpenAIAPIError as e:
            logger.error(f"Erro na OpenAI API: {str(e)}")
            raise FinancialAssistantError(
                "Erro ao comunicar com assistente"
            ) from e
            
        except ToolExecutionError as e:
            logger.error(f"Erro ao executar ferramenta: {str(e)}")
            raise FinancialAssistantError(
                "Erro ao executar operação solicitada"
            ) from e
            
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            raise FinancialAssistantError(
                "Erro interno do sistema"
            ) from e
    
    def _get_or_create_thread(self, sender_id: str) -> str:
        """
        Obtém thread existente ou cria nova para o usuário.
        
        Args:
            sender_id: ID único do remetente
        
        Returns:
            str: thread_id
        """
        # Tentar obter thread existente
        thread_id = thread_repository.get_thread_id(sender_id)
        
        if thread_id:
            logger.info(f"Thread existente encontrada para {sender_id}")
            return thread_id
        
        # Criar nova thread
        logger.info(f"Criando nova thread para {sender_id}")
        thread_id = openai_service.create_thread()
        
        # Salvar no DynamoDB
        thread_repository.save_thread_id(sender_id, thread_id)
        
        logger.info(f"Nova thread criada e salva: {thread_id}")
        return thread_id
    
    def _process_tool_calls(
        self,
        thread_id: str,
        run_result: Dict[str, Any]
    ) -> None:
        """
        Processa as tool calls solicitadas pelo Assistant.
        
        Executa cada ferramenta e submete os resultados de volta
        ao Assistant para que ele continue o processamento.
        
        Args:
            thread_id: ID da thread
            run_result: Resultado do run contendo required_action
        """
        required_action = run_result.get('required_action')
        
        if not required_action:
            logger.warning("process_tool_calls chamado sem required_action")
            return
        
        # Extrair tool calls
        tool_calls = required_action.submit_tool_outputs.tool_calls
        
        logger.info(f"Processando {len(tool_calls)} tool call(s)")
        
        # Executar cada tool call
        tool_outputs = []
        
        for tool_call in tool_calls:
            tool_call_id = tool_call.id
            tool_name = tool_call.function.name
            
            # Parsear argumentos (vêm como JSON string)
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                logger.error(
                    f"Erro ao parsear argumentos da tool {tool_name}: {e}"
                )
                # Retornar erro como output da ferramenta
                tool_outputs.append({
                    'tool_call_id': tool_call_id,
                    'output': json.dumps({
                        'error': 'Argumentos inválidos',
                        'message': str(e)
                    })
                })
                continue
            
            # Executar ferramenta
            try:
                logger.debug(
                    f"Executando tool: {tool_name} "
                    f"(call_id: {tool_call_id})"
                )
                
                output = tool_executor.execute_tool(tool_name, arguments)
                
                tool_outputs.append({
                    'tool_call_id': tool_call_id,
                    'output': output
                })
                
                logger.info(
                    f"Tool {tool_name} executada com sucesso"
                )
                
            except ToolExecutionError as e:
                logger.error(
                    f"Erro ao executar tool {tool_name}: {str(e)}"
                )
                # Retornar erro como output para o Assistant poder lidar
                tool_outputs.append({
                    'tool_call_id': tool_call_id,
                    'output': json.dumps({
                        'error': 'Erro na execução',
                        'message': str(e)
                    })
                })
        
        # Submeter outputs de volta ao Assistant
        run_id = run_result['run_id']
        logger.info(
            f"Submetendo {len(tool_outputs)} tool output(s) ao Assistant"
        )
        
        openai_service.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs
        )


# Instância global do gerenciador (singleton pattern)
conversation_manager = ConversationManager()

