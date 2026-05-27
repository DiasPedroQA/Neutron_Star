"""Implementação concreta do Logger usando a biblioteca padrão 'logging'."""

import logging
from typing import TextIO

from src.domain.ports.logger_port import LoggerPort


class LoggingLogger(LoggerPort):
    """Logger concreto usando a biblioteca padrão 'logging'."""

    def __init__(self, name: str = "NeutronStar") -> None:
        self._logger: logging.Logger = logging.getLogger(name=name)
        # Configuração básica para saída no console
        if not self._logger.handlers:
            handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
            formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(fmt=formatter)
            self._logger.addHandler(hdlr=handler)
            self._logger.setLevel(level=logging.INFO)

    def info(self, message: str) -> None:
        self._logger.info(msg=message)

    def error(self, message: str) -> None:
        self._logger.error(msg=message)
