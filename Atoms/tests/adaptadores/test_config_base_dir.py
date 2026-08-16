# Atoms/tests/adaptadores/test_config_base_dir.py

"""Testes do resolvedor de diretório-base configurável via env var."""

from pathlib import Path

import pytest

from adaptadores.api import _get_base_dir


def test_get_base_dir_respeita_env_var_neutron_star_base_dir(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A env var NEUTRON_STAR_BASE_DIR deve sobrescrever o diretório padrão."""
    monkeypatch.setenv("NEUTRON_STAR_BASE_DIR", "/tmp/base-de-teste")

    resultado: Path = _get_base_dir()

    assert resultado == Path("/tmp/base-de-teste")


def test_get_base_dir_usa_home_quando_env_var_ausente(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Se a env var não estiver definida, o diretório padrão deve ser o home do usuário."""
    monkeypatch.delenv("NEUTRON_STAR_BASE_DIR", raising=False)

    resultado: Path = _get_base_dir()

    assert resultado == Path.home()
