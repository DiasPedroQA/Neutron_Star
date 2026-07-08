"""Configuração centralizada de logging para o Neutron Star.

Fornece uma função para obter loggers configurados com formato consistente
e níveis de log controláveis via variável de ambiente.
"""

import logging
import os
import sys
from typing import Any, Literal, TextIO

# ── Configurações padrão ────────────────────────────────────────────

DEFAULT_LOG_LEVEL: Literal[20] = logging.INFO
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
LOG_DATE_FORMAT = "%Y_%m_%d %H:%M:%S"


# ── Níveis de log por ambiente ─────────────────────────────────────


def _nivel_por_ambiente() -> int:
    """Define o nível de log baseado na variável de ambiente LOG_LEVEL."""
    nivel_map: dict[str, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return nivel_map.get(os.getenv(key="LOG_LEVEL", default="INFO").upper(), DEFAULT_LOG_LEVEL)


# ── Configuração do logger raiz ────────────────────────────────────


def _configurar_logger_raiz() -> None:
    """Configura o logger raiz com formato e nível definidos."""
    nivel: int = _nivel_por_ambiente()

    # Remove handlers existentes para evitar duplicação
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Cria handler para console (stdout)
    console_handler: logging.StreamHandler[TextIO | Any] = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(level=nivel)

    # Formatação
    formatter: logging.Formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    console_handler.setFormatter(fmt=formatter)

    # Adiciona ao logger raiz
    logging.root.addHandler(hdlr=console_handler)
    logging.root.setLevel(level=nivel)


# ── Função pública ──────────────────────────────────────────────────


def get_logger(nome: str) -> logging.Logger:
    """Retorna um logger configurado para o módulo especificado.

    Args:
        nome: Nome do logger (geralmente __name__ do módulo).

    Returns:
        Logger configurado com os parâmetros definidos.

    Exemplo:
        logger = get_logger(__name__)
        logger.debug("Mensagem de debug")
        logger.info("Mensagem informativa")
        logger.warning("Aviso")
        logger.error("Erro")
    """
    # Configura o logger raiz na primeira chamada
    if not logging.root.handlers:
        _configurar_logger_raiz()

    logger: logging.Logger = logging.getLogger(name=nome)
    logger.setLevel(level=_nivel_por_ambiente())
    return logger


# ── Atalhos para níveis específicos ───────────────────────────────


# Opcional: exportar funções diretas para uso rápido
def debug(msg: str, *args, **kwargs) -> None:
    """Log em nível DEBUG."""
    get_logger(nome="root").debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """Log em nível INFO."""
    get_logger(nome="root").info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """Log em nível WARNING."""
    get_logger(nome="root").warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """Log em nível ERROR."""
    get_logger(nome="root").error(msg, *args, **kwargs)


# ── Inicialização automática ───────────────────────────────────────

# Configura o logger raiz no import do módulo
_configurar_logger_raiz()
