"""
Testes unitários para o módulo de logging.
"""

import pytest
import logging
import os
from utils.logger import setup_logger, get_log_level


@pytest.mark.unit
class TestLogger:
    """Testes para configuração de logging."""
    
    def test_setup_logger_returns_logger(self):
        """Testa se setup_logger retorna um logger válido."""
        logger = setup_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
    
    def test_logger_has_handler(self):
        """Testa se o logger tem pelo menos um handler."""
        logger = setup_logger("test_logger_handler")
        assert len(logger.handlers) > 0
    
    def test_get_log_level_default(self):
        """Testa nível de log padrão."""
        # Remover variável de ambiente temporariamente
        original_level = os.environ.get("LOG_LEVEL")
        if "LOG_LEVEL" in os.environ:
            del os.environ["LOG_LEVEL"]
        
        level = get_log_level()
        assert level == logging.INFO
        
        # Restaurar
        if original_level:
            os.environ["LOG_LEVEL"] = original_level
    
    def test_get_log_level_custom(self, monkeypatch):
        """Testa nível de log customizado."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        level = get_log_level()
        assert level == logging.DEBUG
    
    def test_logger_no_duplicate_handlers(self):
        """Testa que não cria handlers duplicados."""
        logger_name = "test_no_duplicates"
        logger1 = setup_logger(logger_name)
        initial_handlers = len(logger1.handlers)
        
        logger2 = setup_logger(logger_name)
        final_handlers = len(logger2.handlers)
        
        assert initial_handlers == final_handlers
        assert logger1 is logger2

