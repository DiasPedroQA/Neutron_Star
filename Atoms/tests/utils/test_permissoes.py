"""Testes para a função _ler_permissoes do módulo system_tools.

Verifica a detecção de permissões de leitura, escrita e execução
em arquivos e diretórios, bem como o tratamento de erros.
"""

import os
from pathlib import Path
from typing import NoReturn

import pytest
from src.utils.system_tools import _ler_permissoes


class TestPermissoes:
    """Suite de testes para a função _ler_permissoes."""

    def test_arquivo_padrao_tem_todas_as_permissoes(self, arquivo_simples: Path) -> None:
        """Arquivo comum possui leitura, escrita e execução (não executável por padrão)."""
        legivel: bool
        gravavel: bool
        executavel: bool

        legivel, gravavel, executavel = _ler_permissoes(caminho=arquivo_simples)
        assert legivel is True
        assert gravavel is True
        assert executavel is False  # Por padrão, arquivos não são executáveis

    def test_sem_permissao_de_leitura(self, arquivo_simples: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Simula ausência de permissão de leitura via monkeypatch de os.access."""

        # Define uma função que retorna False apenas para R_OK
        def access_side_effect(path: Path, mode: int) -> bool:
            print(f"Chamando os.access com path={path}, mode={mode}")
            return mode != os.R_OK  # W_OK e X_OK retornam True

        monkeypatch.setattr(os, "access", access_side_effect)

        legivel: bool
        gravavel: bool
        executavel: bool

        legivel, gravavel, executavel = _ler_permissoes(caminho=arquivo_simples)
        assert legivel is False
        assert gravavel is True
        assert executavel is True

    def test_oserror_resulta_em_tudo_false(self, arquivo_simples: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Quando os.access levanta OSError, todas as permissões devem ser False."""

        def access_raise_oserror(*args, **kwargs) -> NoReturn:
            raise OSError("Erro simulado")

        monkeypatch.setattr(os, "access", access_raise_oserror)

        legivel: bool
        gravavel: bool
        executavel: bool

        legivel, gravavel, executavel = _ler_permissoes(caminho=arquivo_simples)
        assert legivel is False
        assert gravavel is False
        assert executavel is False
