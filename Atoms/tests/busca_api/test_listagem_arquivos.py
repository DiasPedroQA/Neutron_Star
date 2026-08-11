"""Cobertura de integração do fluxo de busca."""

# pylint: disable=too-few-public-methods

from aplicacao.casos_uso import ListarArquivos
from aplicacao.portas import Diretorio
from dominio.entidades import ArquivoTemp


class DiretorioSemArquivos(Diretorio):
    """Diretório falso que representa uma busca sem resultados."""

    def buscar_arquivos_html(self) -> list[ArquivoTemp]:
        """Retorna uma lista vazia de arquivos HTML."""
        return []


def test_busca_vazia_retorna_lista_vazia() -> None:
    """O caso de uso preserva uma busca sem arquivos."""
    assert ListarArquivos(diretorio=DiretorioSemArquivos()).executar_busca() == []
