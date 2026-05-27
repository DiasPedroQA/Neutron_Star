"""Testes para o use case de identificação do sistema operacional."""

from src.domain.entities.operating_system import OperatingSystem
from src.domain.ports.logger_port import LoggerPort
from src.domain.ports.system_detector_port import SystemDetectorPort
from src.domain.use_cases.identify_system import IdentifySystemUseCase


class FakeSystemDetector(SystemDetectorPort):
    """Mock que retorna um SO fixo para testes."""

    def __init__(self, os_info: OperatingSystem) -> None:
        self._os: OperatingSystem = os_info

    def detect(self) -> OperatingSystem:
        return self._os


class FakeLogger(LoggerPort):
    """Logger espião que armazena as mensagens."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def info(self, message: str) -> None:
        self.messages.append(f"INFO: {message}")

    def error(self, message: str) -> None:
        self.messages.append(f"ERROR: {message}")


def test_identify_system_linux() -> None:
    """Teste para o use case de identificação do sistema operacional (Linux)."""
    # Arrange
    fake_os = OperatingSystem(
        name="Linux",
        version="#1 SMP PREEMPT_DYNAMIC",
        release="5.15.0-91-generic",
        machine="x86_64",
    )
    detector = FakeSystemDetector(os_info=fake_os)
    logger = FakeLogger()

    use_case = IdentifySystemUseCase(detector=detector, logger=logger)

    # Act
    result: OperatingSystem = use_case.identify_system()

    # Assert
    assert result.name == "Linux"
    assert result.release == "5.15.0-91-generic"
    assert len(logger.messages) == 2
    assert "Iniciando identificação" in logger.messages[0]
    assert "Sistema identificado: Linux 5.15.0-91-generic" in logger.messages[1]


def test_identify_system_windows() -> None:
    """Teste para o use case de identificação do sistema operacional (Windows)."""
    # Arrange
    fake_os = OperatingSystem(
        name="Windows",
        version="10.0.19042",
        release="10",
        machine="AMD64",
    )
    detector = FakeSystemDetector(os_info=fake_os)
    logger = FakeLogger()

    use_case = IdentifySystemUseCase(detector=detector, logger=logger)

    # Act
    result: OperatingSystem = use_case.identify_system()

    # Assert
    assert result.name == "Windows"
    assert result.release == "10"
    assert len(logger.messages) == 2
    assert "Sistema identificado: Windows 10" in logger.messages[1]
