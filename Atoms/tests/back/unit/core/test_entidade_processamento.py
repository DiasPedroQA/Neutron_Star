# Atoms/tests/back/unit/core/test_entidade_processamento.py

"""Testes para EstatisticasProcessamento e ResultadoProcessamento."""

import pytest
from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.entidades.entidade_processamento import (
    EstatisticasProcessamento,
    ResultadoProcessamento,
)


class TestEstatisticas:
    def test_criacao_default(self) -> None:
        est = EstatisticasProcessamento()
        assert est.total_arquivos == 0
        assert est.arquivos_processados == 0
        assert est.arquivos_com_falha == 0
        assert est.total_favoritos == 0

    def test_inconsistencia_gera_warning_log(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        caplog.set_level(level=logging.WARNING)
        est = EstatisticasProcessamento(
            total_arquivos=5,
            arquivos_processados=6,
            arquivos_com_falha=0,
        )
        assert "Inconsistência" in caplog.text
        assert est.total_arquivos == 5

    def test_para_dict(self) -> None:
        est = EstatisticasProcessamento(total_arquivos=10, total_favoritos=50)
        d: dict[str, int] = est.para_dict()
        assert d == {
            "total_arquivos": 10,
            "arquivos_processados": 0,
            "arquivos_com_falha": 0,
            "total_favoritos": 50,
        }

    def test_to_dict_compatibilidade(self) -> None:
        est = EstatisticasProcessamento(total_arquivos=3, total_favoritos=12)
        d: dict[str, int] = est.to_dict()
        assert d["total_bookmarks"] == 12

    def test_alias_total_files_setter(self) -> None:
        est = EstatisticasProcessamento()
        est.total_files = 7
        assert est.total_arquivos == 7


class TestResultadoProcessamento:
    def test_criacao_vazia(self) -> None:
        res = ResultadoProcessamento()
        assert res.caminho_raiz == ""
        assert res.favoritos_processados == []

    def test_para_dict(self) -> None:
        res = ResultadoProcessamento(caminho_raiz="/teste")
        d: dict[str, str | list[Favorito] | dict[str, int]] = res.para_dict()
        assert d["caminho_raiz"] == "/teste"
        assert "estatisticas_processadas" in d

    def test_to_dict_compatibilidade(self) -> None:
        res = ResultadoProcessamento(caminho_raiz="/x")
        d: dict[str, str | list[Favorito] | dict[str, int]] = res.to_dict()
        assert "bookmarks" in d
