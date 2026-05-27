"""Testes de integração para identificação do sistema operacional."""

import logging
import platform

import pytest

from domain.entities.operating_system import OperatingSystem
from src.domain.use_cases.identify_system import IdentifySystemUseCase
from src.infrastructure.logging_logger import LoggingLogger
from src.infrastructure.platform_system_detector import PlatformSystemDetector


@pytest.fixture
def use_case():
    """Fornece o caso de uso configurado com dependências reais."""
    detector = PlatformSystemDetector()
    logger = LoggingLogger(name="TestNeutronStar")
    # Silencia os logs para não sujar a saída dos testes
    logger._logger.setLevel(level=logging.CRITICAL)
    return IdentifySystemUseCase(detector=detector, logger=logger)


def test_identify_system_returns_valid_os(use_case: IdentifySystemUseCase) -> None:
    """Testa se a identificação retorna dados plausíveis do SO real."""
    result: OperatingSystem = use_case.identify_system()

    # Verifica se os campos foram preenchidos
    assert result.name is not None and result.name != ""
    assert result.release is not None
    assert result.machine is not None

    # O nome deve corresponder ao sistema onde o teste está rodando
    expected_name: str = platform.system()
    assert result.name == expected_name, (
        f"Esperado SO '{expected_name}', mas obteve '{result.name}'"
    )


def test_identify_system_logs_correctly(caplog: pytest.LogCaptureFixture) -> None:
    """Testa se as mensagens de log são geradas corretamente."""
    detector = PlatformSystemDetector()
    # Usamos o logger diretamente para capturar com o caplog do pytest
    logger = LoggingLogger(name="TestLog")
    use_case = IdentifySystemUseCase(detector=detector, logger=logger)

    with caplog.at_level(level=logging.INFO, logger="TestLog"):
        use_case.identify_system()

    assert "Iniciando identificação" in caplog.text
    assert "Sistema identificado" in caplog.text
