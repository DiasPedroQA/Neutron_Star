# Atoms/tests/back/unit/infrastructure/test_so_identifier.py

"""Testes para o identificador de sistema operacional."""

from pathlib import Path
from unittest.mock import patch
import pytest

from backend.core.entidades.entidade_sistema_operacional import ModeloSistemaOperacional
from backend.infrastructure.controllers.so_identifier import DetectarSistemaOperacional


@pytest.fixture
def detector() -> DetectarSistemaOperacional:
    """Cria uma instância do detector de sistema operacional para uso nos testes.
    Fornece um objeto DetectarSistemaOperacional compartilhado entre os casos de teste que o requerem."""
    return DetectarSistemaOperacional()


def test_obter_nome_sistema(detector: DetectarSistemaOperacional) -> None:
    """Verifica se o detector retorna um nome de sistema operacional válido.
    Garante que o nome seja uma string não vazia representando o sistema atual."""
    nome: str = detector.obter_nome_sistema()
    assert isinstance(nome, str)
    assert nome != ""


def test_obter_versao_sistema(detector: DetectarSistemaOperacional) -> None:
    """Verifica se o detector retorna uma versão de sistema operacional em formato de texto.
    Garante que a versão seja representada como string, independentemente da plataforma."""
    versao: str = detector.obter_versao_sistema()
    assert isinstance(versao, str)


def test_obter_pasta_usuario(detector: DetectarSistemaOperacional) -> None:
    """Verifica se o detector retorna um caminho absoluto para a pasta do usuário.
    Garante que o diretório obtido represente corretamente o diretório home do sistema."""
    home: Path = detector.obter_pasta_usuario()
    assert home.is_absolute()


@patch("platform.system", return_value="Linux")
@patch("platform.release", return_value="5.15.0")
@patch("pathlib.Path.home", return_value=Path("/home/teste"))
def test_detectar_sistema_operacional(
    mock_home, mock_release, mock_system, detector: DetectarSistemaOperacional
) -> None:
    """Testa a construção do ModeloSistemaOperacional a partir de chamadas à plataforma.
    Verifica se o detector preenche corretamente nome, versão e pasta do usuário usando os valores simulados."""
    modelo: ModeloSistemaOperacional = detector.detectar_sistema_operacional()
    assert modelo.nome_sistema == "linux"
    assert modelo.versao_sistema == "5.15.0"
    assert modelo.pasta_usuario == Path("/home/teste")
    assert not mock_home
    assert not mock_release
    assert not mock_system
