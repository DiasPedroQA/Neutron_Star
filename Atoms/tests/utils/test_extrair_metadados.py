"""Testes para a função _extrair_metadados_arquivo (e o atalho metadados_simples).

Verifica a extração de caminho, data de modificação, tamanho, permissões,
detecção de oculto (com e sem raiz de busca) e tratamento de falha de stat.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import NoReturn

import pytest
from pytest_mock import MockerFixture
from src.utils.system_tools import (
    MetadadosArquivo,
    _extrair_metadados_arquivo,
    metadados_simples,
)


def _criar_arquivo(caminho: Path, conteudo: bytes = b"hello world") -> Path:
    """Cria um arquivo com conteúdo e retorna o caminho."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(data=conteudo)
    return caminho


def _lancar_oserror(*args: object, **kwargs: object) -> NoReturn:
    """Função auxiliar que sempre levanta OSError, usada em mocks."""
    raise OSError("Erro simulado")


@pytest.fixture
def arquivo_txt(tmp_path: Path) -> Path:
    """Fixture que retorna um arquivo de texto com conteúdo."""
    return _criar_arquivo(caminho=tmp_path / "arquivo.txt", conteudo=b"hello world")


class TestExtrairMetadadosArquivo:
    """Suite de testes para _extrair_metadados_arquivo."""

    def test_arquivo_retorna_metadados_completos(self, arquivo_txt: Path) -> None:
        """Verifica que um arquivo existente retorna todos os metadados esperados."""
        dados: MetadadosArquivo | None = _extrair_metadados_arquivo(caminho=arquivo_txt)

        assert dados is not None
        assert dados["caminho"] == arquivo_txt
        assert isinstance(dados["modificado"], datetime)
        assert dados["tamanho"] == 11
        self._assert_permissoes_leitura_escrita(dados=dados, esperado=True)
        assert dados["oculto"] is False

    def test_stat_falhando_retorna_none(self, arquivo_txt: Path, mocker: MockerFixture) -> None:
        """Se o stat() falhar (ex.: arquivo removido entre a listagem e a leitura), retorna None."""
        mocker.patch.object(Path, "stat", side_effect=OSError)
        dados: MetadadosArquivo | None = _extrair_metadados_arquivo(caminho=arquivo_txt)
        assert dados is None

    def test_oserror_no_access_resulta_em_permissoes_false(
        self, arquivo_txt: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Simula erro em os.access; permissões devem ser False, sem quebrar a extração."""
        monkeypatch.setattr(os, "access", _lancar_oserror)
        dados: MetadadosArquivo | None = _extrair_metadados_arquivo(caminho=arquivo_txt)

        assert dados is not None
        self._assert_permissoes_leitura_escrita(dados=dados, esperado=False)

    def _assert_permissoes_leitura_escrita(self, dados: MetadadosArquivo, esperado: bool) -> None:
        """Confere que `legivel` e `gravavel` valem `esperado` e que `executavel` é sempre False.

        Compartilhado entre o caso feliz (permissões reais do SO, `esperado=True`)
        e o caso em que `os.access` falha (`esperado=False`).
        """
        assert dados["permissoes"]["legivel"] is esperado
        assert dados["permissoes"]["gravavel"] is esperado
        assert dados["permissoes"]["executavel"] is False

    def test_nome_com_ponto_marca_oculto_sem_raiz_busca(self, tmp_path: Path) -> None:
        """Sem `raiz_busca`, oculto é decidido só pelo nome do próprio arquivo."""
        oculto: Path = _criar_arquivo(caminho=tmp_path / ".oculto.txt")
        self._assert_oculto(caminho=oculto, esperado=True)

    def test_arquivo_sem_ponto_nao_e_oculto(self, arquivo_txt: Path) -> None:
        """Arquivo sem ponto no início não é oculto."""
        self._assert_oculto(caminho=arquivo_txt, esperado=False)

    def _assert_oculto(self, caminho: Path, esperado: bool) -> None:
        """Extrai os metadados de `caminho` (sem `raiz_busca`) e confere o campo `oculto`.

        Compartilhado entre o caso de arquivo cujo nome começa com '.' (`esperado=True`)
        e o caso de arquivo comum (`esperado=False`).
        """
        dados: MetadadosArquivo | None = _extrair_metadados_arquivo(caminho=caminho)
        assert dados is not None
        assert dados["oculto"] is esperado

    def test_componente_oculto_relativo_a_raiz_busca(self, tmp_path: Path) -> None:
        """Com `raiz_busca`, qualquer componente do caminho relativo iniciado por '.' marca oculto."""
        dentro_de_pasta_oculta: Path = _criar_arquivo(caminho=tmp_path / ".cache" / "visivel.txt")
        dados: MetadadosArquivo | None = _extrair_metadados_arquivo(caminho=dentro_de_pasta_oculta, raiz_busca=tmp_path)
        assert dados is not None
        assert dados["oculto"] is True

    def test_hash_so_e_calculado_quando_solicitado(self, arquivo_txt: Path) -> None:
        """Por padrão não calcula hash; com `calcular_hash=True`, preenche o campo."""
        sem_hash: MetadadosArquivo | None = _extrair_metadados_arquivo(caminho=arquivo_txt)
        com_hash: MetadadosArquivo | None = _extrair_metadados_arquivo(caminho=arquivo_txt, calcular_hash=True)

        assert sem_hash is not None and sem_hash["hash_checksum"] is None
        assert com_hash is not None and com_hash["hash_checksum"] is not None


class TestMetadadosSimples:
    """Suite de testes para o atalho metadados_simples."""

    def test_atalho_nao_calcula_hash_nem_oculto_por_raiz(self, arquivo_txt: Path) -> None:
        """metadados_simples nunca calcula hash e ignora raiz de busca."""
        dados: MetadadosArquivo | None = metadados_simples(caminho=arquivo_txt)
        assert dados is not None
        assert dados["hash_checksum"] is None
        assert dados["tamanho"] == 11

    def test_atalho_retorna_none_para_caminho_inexistente(self, tmp_path: Path) -> None:
        """Caminho inexistente resulta em None (stat() levanta OSError/FileNotFoundError)."""
        dados: MetadadosArquivo | None = metadados_simples(caminho=tmp_path / "nao_existe.txt")
        assert dados is None
