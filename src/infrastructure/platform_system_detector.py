"""Implementação concreta do SystemDetector usando a biblioteca 'platform'."""

import platform
from pathlib import Path

from src.domain.entities.operating_system import OperateSystemModel
from src.domain.ports.system_detector_port import SystemDetectorPort


class OperateSystemDetector(SystemDetectorPort):
    """Detecta o SO usando a biblioteca padrão 'platform'."""

    def system_data_collector(self) -> OperateSystemModel:
        """Detecta o sistema operacional usando a biblioteca 'platform'."""
        return OperateSystemModel(
            name=platform.system(),
            version=platform.version(),
            release=platform.release(),
            machine=platform.machine(),
            user_path=Path.home(),
        )
