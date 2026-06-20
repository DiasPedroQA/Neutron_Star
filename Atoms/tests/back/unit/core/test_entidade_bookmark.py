# Atoms/tests/back/unit/core/test_entidade_bookmark.py

"""Testes para a entidade Favorito."""

from datetime import datetime, timezone
import pytest
from backend.core.entidades.entidade_bookmark import Favorito

DATA_UTC = datetime(year=2025, month=12, day=25, tzinfo=timezone.utc)


class TestFavorito:
    def test_criacao_basica(self) -> None:
        fav = Favorito(titulo="Google", url="https://google.com", data_adicao=DATA_UTC)
        assert fav.titulo == "Google"
        assert fav.url == "https://google.com"
        assert fav.data_adicao == DATA_UTC

    def test_criacao_sem_data_usa_padrao(self) -> None:
        fav = Favorito(titulo="Sem data", url="http://example.com")
        assert fav.data_adicao.year == 1970

    def test_alias_title(self) -> None:
        fav = Favorito(title="Alias", url="http://x.com")
        assert fav.titulo == "Alias"
        assert fav.title == "Alias"

    def test_alias_add_date(self) -> None:
        fav = Favorito(titulo="x", url="x", add_date=DATA_UTC)
        assert fav.data_adicao == DATA_UTC
        assert fav.add_date == DATA_UTC

    def test_prioridade_titulo_sobre_title(self) -> None:
        fav = Favorito(titulo="Novo", title="Antigo", url="http://x.com")
        assert fav.titulo == "Novo"

    def test_frozen_impede_alteracao(self) -> None:
        fav = Favorito(titulo="T", url="U")
        with pytest.raises(expected_exception=Exception):
            fav.titulo = "Outro"  # type: ignore[misc]
