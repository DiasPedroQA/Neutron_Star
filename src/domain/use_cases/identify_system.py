"""Use case para identificar o sistema operacional e registrar log."""

from src.domain.entities.operating_system import OperatingSystem
from src.domain.ports.logger_port import LoggerPort
from src.domain.ports.system_detector_port import SystemDetectorPort


class IdentifySystemUseCase:
    """Caso de uso: identificar o sistema operacional e registrar log."""

    def __init__(self, detector: SystemDetectorPort, logger: LoggerPort) -> None:
        self._detector: SystemDetectorPort = detector
        self._logger: LoggerPort = logger

    def identify_system(self) -> OperatingSystem:
        """Executa a detecção e loga o resultado."""
        self._logger.info(message="Iniciando identificação do sistema...")
        os_info: OperatingSystem = self._detector.detect()
        self._logger.info(message=f"Sistema identificado: {os_info.name} {os_info.release}")
        return os_info
