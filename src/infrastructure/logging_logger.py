"""Implementação concreta do Logger usando a biblioteca padrão 'logging'."""

import logging
from typing import TextIO

from src.domain.ports.logger_port import LoggerPort


class LoggingLogger(LoggerPort):
    """Logger concreto usando a biblioteca padrão 'logging'."""

    def __init__(self, name: str = "NeutronStar App") -> None:
        super().__init__()
        self.debugger: logging.Logger = logging.getLogger(name=name)
        if not self.debugger.handlers:
            handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
            formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(fmt=formatter)
            self.debugger.addHandler(hdlr=handler)
            self.debugger.setLevel(level=logging.INFO)

    def info(self, message: str) -> None:
        self.debugger.info(msg=message)

    def error(self, message: str) -> None:
        self.debugger.error(msg=message)
