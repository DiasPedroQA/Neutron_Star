# Atoms/tests/infra/conversao_api/test_extracao_tags_bookmarks.py
# pylint: disable=too-few-public-methods

"""Cobertura de integração do fluxo de extração."""

from pathlib import Path

from aplicacao.casos_uso import ExtrairTags
from aplicacao.portas import LeitorArquivo
from dominio.entidades import TagExtraida


class LeitorComUmaTag(LeitorArquivo):
    """Leitor falso que retorna uma tag para qualquer arquivo solicitado."""

    def extrair_tags(self, caminho: Path) -> list[TagExtraida]:
        """Retorna a tag fixa usada para validar a delegação do caso de uso."""
        _: Path = caminho
        return [TagExtraida(titulo="Neutron Star", url="https://example.com")]


def test_extracao_retorna_tags_do_leitor() -> None:
    """O caso de uso devolve exatamente as tags fornecidas pela porta."""
    resultado: list[TagExtraida] = ExtrairTags(leitor=LeitorComUmaTag()).executar_extracao(
        caminho=Path("bookmarks.html")
    )

    assert [tag.titulo for tag in resultado] == ["Neutron Star"]
