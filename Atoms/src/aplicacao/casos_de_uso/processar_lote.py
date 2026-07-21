"""Caso de uso de processamento de bookmarks em lote.

Processa uma lista de arquivos de bookmarks individualmente: cada um é lido,
interpretado e exportado nos formatos pedidos. Não depende de CLI nem de
qualquer framework — pode ser chamado tanto por um adaptador de linha de
comando quanto por um futuro adaptador de API, compartilhando o mesmo núcleo.
"""

from pathlib import Path

from dominio.entidades import VirtualFolder
from dominio.excecoes import ErroBookmarks
from infraestrutura.sistema_arquivos import ler_arquivo_html

from aplicacao.casos_de_uso.exportar_bookmarks import exportar_bookmarks
from aplicacao.casos_de_uso.parse_bookmarks import parse_bookmarks_html


def processar_arquivo_individual(
    arquivo: Path,
    formatos: list[str],
    diretorio_saida: Path | None = None,
) -> VirtualFolder | None:
    """Extrai e exporta um único arquivo de bookmarks nos formatos pedidos.

    Args:
        arquivo: Caminho do arquivo HTML de bookmarks a processar.
        formatos: Extensões de formato desejadas (ex.: [".json", ".md"]).
        diretorio_saida: Pasta onde salvar as saídas; se None, usa a mesma
            pasta do arquivo original.

    Returns:
        VirtualFolder | None: A raiz de bookmarks extraída, ou None se o
        arquivo não pôde ser lido ou interpretado (erro já é responsabilidade
        do chamador registrar/reportar).

    Raises:
        ErroBookmarks: Se a leitura ou interpretação do arquivo falhar.
    """
    conteudo: str = ler_arquivo_html(caminho=arquivo)
    raiz: VirtualFolder = parse_bookmarks_html(conteudo_html=conteudo)

    destino: Path = diretorio_saida or arquivo.parent
    if diretorio_saida:
        diretorio_saida.mkdir(parents=True, exist_ok=True)

    for formato in formatos:
        exportar_bookmarks(
            raiz=raiz,
            formato=formato,
            caminho_saida=destino / f"{arquivo.stem}{formato}",
        )
    return raiz


def processar_arquivos_em_lote(
    arquivos: list[Path],
    formatos: list[str],
    diretorio_saida: Path | None = None,
) -> dict[Path, ErroBookmarks]:
    """Processa vários arquivos de bookmarks, um a um, sem interromper no primeiro erro.

    Args:
        arquivos: Lista de arquivos HTML de bookmarks a processar.
        formatos: Extensões de formato desejadas (ex.: [".json", ".md"]).
        diretorio_saida: Pasta onde salvar as saídas; se None, cada arquivo é
            exportado ao lado do original.

    Returns:
        dict[Path, ErroBookmarks]: Mapa dos arquivos que falharam para o erro
        correspondente. Vazio se todos foram processados com sucesso.
    """
    falhas: dict[Path, ErroBookmarks] = {}
    for arquivo in arquivos:
        try:
            processar_arquivo_individual(arquivo=arquivo, formatos=formatos, diretorio_saida=diretorio_saida)
        except ErroBookmarks as erro:
            falhas[arquivo] = erro
    return falhas
