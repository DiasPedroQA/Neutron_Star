"""Módulo que define a interface para logging (desacoplada do framework)."""

from abc import ABC, abstractmethod


class LoggerPort(ABC):
    """Interface para logging (desacoplada do framework)."""

    @abstractmethod
    def info(self, message: str) -> None:
        """Registra uma mensagem informativa."""
        raise NotImplementedError

    @abstractmethod
    def error(self, message: str) -> None:
        """Registra uma mensagem de erro."""
        raise NotImplementedError
