"""Implementação concreta do SystemDetector usando a biblioteca 'platform'."""

import platform

from src.domain.entities.operating_system import OperatingSystem
from src.domain.ports.system_detector_port import SystemDetectorPort


class PlatformSystemDetector(SystemDetectorPort):
    """Detecta o SO usando a biblioteca padrão 'platform'."""

    def detect(self) -> OperatingSystem:
        return OperatingSystem(
            name=platform.system(),
            version=platform.version(),
            release=platform.release(),
            machine=platform.machine(),
        )
