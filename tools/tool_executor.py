"""
Executor de ferramentas (tools) para o OpenAI Assistant.

Este módulo mapeia as tool calls solicitadas pelo Assistant
para os métodos Python correspondentes, validando argumentos
e executando-os de forma segura.
"""

import json
import signal
from typing import Dict, Any, Callable

from services.excel_service import excel_service
from config.settings import TOOL_EXECUTION_TIMEOUT_SECONDS
from utils.logger import setup_logger
from utils.exceptions import ToolExecutionError

# Logger específico deste módulo
logger = setup_logger(__name__)


class TimeoutException(Exception):
    """Exceção lançada quando uma ferramenta excede o timeout."""
    pass


def timeout_handler(signum, frame):
    """Handler para timeout de execução de ferramentas."""
    raise TimeoutException("Execução da ferramenta excedeu o timeout")


class ToolExecutor:
    """
    Executor responsável por mapear e executar ferramentas do Assistant.
    
    Registra ferramentas disponíveis e fornece execução segura
    com timeout e validação de argumentos.
    """
    
    def __init__(self):
        """Inicializa o executor e registra ferramentas disponíveis."""
        # Mapeamento de nomes de ferramentas para funções Python
        self.tools: Dict[str, Callable] = {
            'add_expense': self._add_expense,
            'get_expense_history': self._get_expense_history
        }
        
        logger.info(
            f"ToolExecutor inicializado com {len(self.tools)} ferramentas: "
            f"{list(self.tools.keys())}"
        )
    
    def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> str:
        """
        Executa uma ferramenta com os argumentos fornecidos.
        
        Args:
            tool_name: Nome da ferramenta a executar
            arguments: Argumentos da ferramenta (como dict)
        
        Returns:
            str: Resultado da execução (como JSON string)
        
        Raises:
            ToolExecutionError: Se a ferramenta falhar ou não existir
        """
        logger.info(
            f"Executando ferramenta: {tool_name} com argumentos: {arguments}"
        )
        
        # Verificar se a ferramenta existe
        if tool_name not in self.tools:
            error_msg = (
                f"Ferramenta '{tool_name}' não encontrada. "
                f"Ferramentas disponíveis: {list(self.tools.keys())}"
            )
            logger.error(error_msg)
            raise ToolExecutionError(error_msg)
        
        try:
            # Configurar timeout para execução
            # NOTA: signal.alarm() funciona apenas em sistemas Unix
            # Para Windows ou Lambda, considere usar threading.Timer
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(TOOL_EXECUTION_TIMEOUT_SECONDS)
            
            # Executar ferramenta
            tool_function = self.tools[tool_name]
            result = tool_function(arguments)
            
            # Cancelar alarme
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            
            # Converter resultado para JSON
            result_json = json.dumps(result, ensure_ascii=False)
            
            logger.info(
                f"Ferramenta {tool_name} executada com sucesso. "
                f"Resultado: {result_json[:200]}..."  # Log parcial
            )
            
            return result_json
            
        except TimeoutException:
            error_msg = (
                f"Timeout: Ferramenta '{tool_name}' excedeu "
                f"{TOOL_EXECUTION_TIMEOUT_SECONDS}s"
            )
            logger.error(error_msg)
            raise ToolExecutionError(error_msg)
            
        except Exception as e:
            error_msg = f"Erro ao executar ferramenta '{tool_name}': {str(e)}"
            logger.error(error_msg)
            raise ToolExecutionError(error_msg) from e
    
    def _add_expense(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ferramenta para adicionar uma despesa ao Excel.
        
        Args:
            arguments: Dict contendo:
                - workbook_id: ID do workbook
                - worksheet_name: Nome da planilha
                - date: Data da despesa
                - description: Descrição
                - category: Categoria
                - amount: Valor
        
        Returns:
            dict: Resultado da operação
        """
        # Validar argumentos obrigatórios
        required_fields = [
            'workbook_id', 'worksheet_name', 'date',
            'description', 'category', 'amount'
        ]
        
        for field in required_fields:
            if field not in arguments:
                raise ToolExecutionError(
                    f"Campo obrigatório '{field}' ausente nos argumentos"
                )
        
        # Extrair argumentos
        workbook_id = arguments['workbook_id']
        worksheet_name = arguments['worksheet_name']
        
        expense_data = {
            'date': arguments['date'],
            'description': arguments['description'],
            'category': arguments['category'],
            'amount': float(arguments['amount'])
        }
        
        logger.debug(
            f"Adicionando despesa: {expense_data['description']} - "
            f"R$ {expense_data['amount']}"
        )
        
        # Chamar serviço Excel
        result = excel_service.add_expense(
            workbook_id=workbook_id,
            worksheet_name=worksheet_name,
            expense_data=expense_data
        )
        
        return {
            'success': True,
            'message': 'Despesa adicionada com sucesso',
            'data': expense_data
        }
    
    def _get_expense_history(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ferramenta para recuperar histórico de despesas do Excel.
        
        Args:
            arguments: Dict contendo:
                - workbook_id: ID do workbook
                - worksheet_name: Nome da planilha
                - filters: (opcional) Filtros a aplicar
        
        Returns:
            dict: Lista de despesas
        """
        # Validar argumentos obrigatórios
        required_fields = ['workbook_id', 'worksheet_name']
        
        for field in required_fields:
            if field not in arguments:
                raise ToolExecutionError(
                    f"Campo obrigatório '{field}' ausente nos argumentos"
                )
        
        # Extrair argumentos
        workbook_id = arguments['workbook_id']
        worksheet_name = arguments['worksheet_name']
        filters = arguments.get('filters')
        
        logger.debug(
            f"Recuperando histórico de despesas com filtros: {filters}"
        )
        
        # Chamar serviço Excel
        expenses = excel_service.get_expense_history(
            workbook_id=workbook_id,
            worksheet_name=worksheet_name,
            filters=filters
        )
        
        return {
            'success': True,
            'count': len(expenses),
            'expenses': expenses
        }


# Instância global do executor (singleton pattern)
tool_executor = ToolExecutor()

