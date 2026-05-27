"""Testes de integração para identificação do sistema operacional."""

import logging
import platform
from pathlib import Path

import pytest

from domain.entities.operating_system import OperateSystemModel
from domain.use_cases.identify_system import IdentifySystemUseCase
from infrastructure.logging_logger import LoggingLogger
from infrastructure.platform_system_detector import OperateSystemDetector


@pytest.fixture
def use_case() -> IdentifySystemUseCase:
    """Fornece o caso de uso configurado com dependências reais."""
    dados_coletados = OperateSystemDetector()
    mensageiro = LoggingLogger(name="TestNeutronStar App")
    # Silencia os logs para não sujar a saída dos testes
    mensageiro.debugger.setLevel(level=logging.CRITICAL)
    return IdentifySystemUseCase(agrupador_dados=dados_coletados, identificador=mensageiro)


def test_identify_system_returns_valid_os(use_case: IdentifySystemUseCase) -> None:
    """Testa se a identificação retorna dados plausíveis do SO real."""
    operating_system: OperateSystemModel = use_case.identify_system()

    # Verifica se os campos foram preenchidos
    assert operating_system.name is not None and operating_system.name != ""
    assert operating_system.release is not None and operating_system.release != ""
    assert operating_system.machine is not None and operating_system.machine != ""

    # Os dados devem corresponder ao sistema onde o teste está rodando
    expected_name: str = platform.system()
    expected_release: str = platform.release()
    expected_machine: str = platform.machine()
    expected_version: str = platform.version()
    expected_user_path: Path = Path.home()

    assert operating_system.name == expected_name, (
        f"Esperado SO '{expected_name}', mas obteve '{operating_system.name}'"
    )

    assert operating_system.release == expected_release, (
        f"Esperada versão '{expected_release}', mas obteve '{operating_system.release}'"
    )

    assert operating_system.machine == expected_machine, (
        f"Esperada máquina '{expected_machine}', mas obteve '{operating_system.machine}'"
    )

    assert operating_system.version == expected_version, (
        f"Esperada versão detalhada '{expected_version}', mas obteve '{operating_system.version}'"
    )

    assert operating_system.user_path == expected_user_path, (
        f"Esperado user_path '{expected_user_path}', mas obteve '{operating_system.user_path}'"
    )


def test_identify_system_logs_correctly(caplog: pytest.LogCaptureFixture) -> None:
    """Testa se as mensagens de log são geradas corretamente."""
    dados_coletados = OperateSystemDetector()
    # Usamos o logger diretamente para capturar com o caplog do pytest
    mensageiro = LoggingLogger(name="Mensagem de Log do Teste")
    use_case = IdentifySystemUseCase(agrupador_dados=dados_coletados, identificador=mensageiro)

    with caplog.at_level(level=logging.INFO, logger="Mensagem de Log do Teste"):
        use_case.identify_system()

    assert "Iniciando identificação" in caplog.text
    assert "Sistema identificado" in caplog.text
