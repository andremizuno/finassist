"""
Configuração de logging para a aplicação.

Este módulo configura o sistema de logging com formato adequado
tanto para desenvolvimento local quanto para produção no CloudWatch.
"""

import logging
import sys
import os


def get_log_level():
    """
    Obtém o nível de log configurado na variável de ambiente.
    
    Returns:
        int: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    return getattr(logging, log_level, logging.INFO)


# Configuração do formato de log
# Formato simples e legível para desenvolvimento local e CloudWatch
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logger(name: str) -> logging.Logger:
    """
    Configura e retorna um logger com o nome especificado.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo)
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicação de handlers se o logger já foi configurado
    if logger.handlers:
        return logger
    
    logger.setLevel(get_log_level())
    
    # Handler para stdout (console e CloudWatch)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(get_log_level())
    
    # Formato do log
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


# Logger padrão para uso geral
logger = setup_logger(__name__)

