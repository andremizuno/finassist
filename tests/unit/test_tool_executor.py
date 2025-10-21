"""
Testes unitários para o ToolExecutor.
"""

import pytest
import json
from unittest.mock import Mock, patch

from tools.tool_executor import ToolExecutor
from utils.exceptions import ToolExecutionError


@pytest.mark.unit
class TestToolExecutor:
    """Testes para o executor de ferramentas."""
    
    @pytest.fixture
    def executor(self):
        """Fixture que retorna uma instância do ToolExecutor."""
        return ToolExecutor()
    
    def test_executor_has_tools(self, executor):
        """Testa se o executor tem ferramentas registradas."""
        assert len(executor.tools) > 0
        assert 'add_expense' in executor.tools
        assert 'get_expense_history' in executor.tools
    
    def test_execute_nonexistent_tool(self, executor):
        """Testa execução de ferramenta inexistente."""
        with pytest.raises(ToolExecutionError) as exc_info:
            executor.execute_tool('nonexistent_tool', {})
        
        assert 'não encontrada' in str(exc_info.value)
    
    @patch('tools.tool_executor.excel_service')
    def test_add_expense_success(self, mock_excel_service, executor):
        """Testa execução bem-sucedida de add_expense."""
        # Mock do serviço Excel
        mock_excel_service.add_expense.return_value = {
            'success': True
        }
        
        # Argumentos válidos
        arguments = {
            'workbook_id': 'workbook123',
            'worksheet_name': 'Despesas',
            'date': '2025-10-21',
            'description': 'Almoço',
            'category': 'Alimentação',
            'amount': 45.50
        }
        
        # Executar
        result_json = executor.execute_tool('add_expense', arguments)
        
        # Verificar
        result = json.loads(result_json)
        assert result['success'] is True
        assert 'message' in result
        
        # Verificar que o serviço foi chamado
        mock_excel_service.add_expense.assert_called_once()
    
    def test_add_expense_missing_arguments(self, executor):
        """Testa add_expense com argumentos faltando."""
        arguments = {
            'workbook_id': 'workbook123',
            # Faltam outros campos obrigatórios
        }
        
        with pytest.raises(ToolExecutionError) as exc_info:
            executor.execute_tool('add_expense', arguments)
        
        assert 'ausente' in str(exc_info.value).lower()
    
    @patch('tools.tool_executor.excel_service')
    def test_get_expense_history_success(self, mock_excel_service, executor):
        """Testa execução bem-sucedida de get_expense_history."""
        # Mock do serviço Excel
        mock_expenses = [
            {
                'date': '2025-10-20',
                'description': 'Almoço',
                'category': 'Alimentação',
                'amount': 45.50
            }
        ]
        mock_excel_service.get_expense_history.return_value = mock_expenses
        
        # Argumentos válidos
        arguments = {
            'workbook_id': 'workbook123',
            'worksheet_name': 'Despesas'
        }
        
        # Executar
        result_json = executor.execute_tool('get_expense_history', arguments)
        
        # Verificar
        result = json.loads(result_json)
        assert result['success'] is True
        assert result['count'] == 1
        assert len(result['expenses']) == 1
        
        # Verificar que o serviço foi chamado
        mock_excel_service.get_expense_history.assert_called_once()
    
    @patch('tools.tool_executor.excel_service')
    def test_tool_execution_with_exception(self, mock_excel_service, executor):
        """Testa comportamento quando ferramenta lança exceção."""
        # Mock que lança exceção
        mock_excel_service.add_expense.side_effect = Exception("Erro no Excel")
        
        arguments = {
            'workbook_id': 'workbook123',
            'worksheet_name': 'Despesas',
            'date': '2025-10-21',
            'description': 'Almoço',
            'category': 'Alimentação',
            'amount': 45.50
        }
        
        with pytest.raises(ToolExecutionError):
            executor.execute_tool('add_expense', arguments)

