"""Módulo que define a interface para detecção do sistema operacional."""

from abc import ABC, abstractmethod

from src.domain.entities.operating_system import OperatingSystem


class SystemDetectorPort(ABC):
    """Interface para detecção do sistema operacional."""

    @abstractmethod
    def detect(self) -> OperatingSystem:
        """Retorna uma entidade com os dados do SO."""
        raise NotImplementedError
