"""Use case para identificar o sistema operacional e registrar log."""

from src.domain.entities.operating_system import OperateSystemModel
from src.domain.ports.logger_port import LoggerPort
from src.domain.ports.system_detector_port import SystemDetectorPort


class IdentifySystemUseCase:
    """Caso de uso: identificar o sistema operacional e registrar log."""

    def __init__(self, agrupador_dados: SystemDetectorPort, identificador: LoggerPort) -> None:
        self._agrupador: SystemDetectorPort = agrupador_dados
        self.debugger: LoggerPort = identificador

    def identify_system(self) -> OperateSystemModel:
        """Executa a detecção e loga o resultado."""
        self.debugger.info(message="Iniciando identificação do sistema...")
        os_info: OperateSystemModel = self._agrupador.system_data_collector()
        self.debugger.info(message=f"Sistema identificado: {os_info.name} {os_info.release}")
        return os_info
