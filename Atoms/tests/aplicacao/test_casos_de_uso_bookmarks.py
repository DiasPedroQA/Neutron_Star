# Atoms/tests/aplicacao/test_casos_de_uso_bookmarks.py
# pylint: disable=too-few-public-methods

"""Testes dos casos de uso, isolados por portas falsas."""

from pathlib import Path

from aplicacao.casos_uso import BuscarEExtrairTags, ExtrairTags, ListarArquivos
from aplicacao.portas import Diretorio, LeitorArquivo
from dominio.entidades import ArquivoTemp, ConversaoResultado, TagExtraida


class DiretorioFalso(Diretorio):
    """Diretório em memória que devolve os arquivos recebidos no construtor."""

    def __init__(self, arquivos: list[ArquivoTemp]) -> None:
        self.arquivos = arquivos

    def buscar_arquivos_html(self) -> list[ArquivoTemp]:
        return self.arquivos


class LeitorFalso(LeitorArquivo):
    """Leitor em memória que associa caminhos a listas de tags."""

    def __init__(self, tags_por_caminho: dict[Path, list[TagExtraida]]) -> None:
        self.tags_por_caminho = tags_por_caminho

    def extrair_tags(self, caminho: Path) -> list[TagExtraida]:
        if caminho not in self.tags_por_caminho:
            raise FileNotFoundError(caminho)
        return self.tags_por_caminho[caminho]


def test_listar_arquivos_delega_a_busca() -> None:
    """O caso de uso retorna os arquivos providos pela porta de diretório."""
    arquivo = ArquivoTemp(
        nome="bookmarks.html",
        caminho_absoluto="/tmp/bookmarks.html",
        tamanho=1,
    )

    resultado: list[ArquivoTemp] = ListarArquivos(
        diretorio=DiretorioFalso(arquivos=[arquivo])
    ).executar_busca()

    assert resultado == [arquivo]


def test_extrair_tags_delega_o_caminho_ao_leitor() -> None:
    """O caso de uso delega a extração ao leitor recebido."""
    caminho = Path("/tmp/bookmarks.html")
    tag = TagExtraida(titulo="Exemplo", url="https://example.com")

    resultado: list[TagExtraida] = ExtrairTags(
        leitor=LeitorFalso(tags_por_caminho={caminho: [tag]})
    ).executar_extracao(caminho)

    assert resultado == [tag]


def test_buscar_e_extrair_mantem_arquivo_sem_tags_quando_a_leitura_falha() -> None:
    """Uma falha de leitura mantém o arquivo no resultado com lista de tags vazia."""
    arquivo = ArquivoTemp(
        nome="bookmarks.html",
        caminho_absoluto="/tmp/bookmarks.html",  # evita ~
        tamanho=0,
    )

    listar = ListarArquivos(diretorio=DiretorioFalso(arquivos=[arquivo]))
    extrair = ExtrairTags(leitor=LeitorFalso(tags_por_caminho={}))
    use_case = BuscarEExtrairTags(listar_arquivos=listar, extrair_tags=extrair)

    resultado: list[ConversaoResultado] = use_case.executar()

    assert resultado[0].arquivo == arquivo
    assert resultado[0].tags_extraidas == []
    assert resultado[0].erro is not None
    # Verifica apenas que indica falha, sem depender da mensagem exata
    assert "Falha" in resultado[0].erro
