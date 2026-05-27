"""Módulo que define a interface para logging (desacoplada do framework)."""

from abc import ABC, abstractmethod


class LoggerPort(ABC):
    """Interface para logging (desacoplada do framework)."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    @abstractmethod
    def info(self, message: str) -> None:
        """Registra uma mensagem informativa."""
        self.messages.append(f"INFO: {message}")
        raise NotImplementedError

    @abstractmethod
    def error(self, message: str) -> None:
        """Registra uma mensagem de erro."""
        self.messages.append(f"ERROR: {message}")
        raise NotImplementedError
