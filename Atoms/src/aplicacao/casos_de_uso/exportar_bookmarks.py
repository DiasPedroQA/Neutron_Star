"""Caso de uso de exportação de hierarquias de bookmarks.

Orquestra a escolha do exportador adequado e delega a ele a geração
do conteúdo serializado ou arquivo correspondente ao formato pedido.
"""

from pathlib import Path

from adaptadores.exportadores.csv_exportador import ExportadorCSV
from adaptadores.exportadores.json_exportador import (
    ExportadorJSON,
)
from adaptadores.exportadores.markdown_exportador import ExportadorMarkdown
from adaptadores.exportadores.pdf_exportador import ExportadorPDF
from adaptadores.exportadores.txt_exportador import ExportadorTXT
from dominio.entidades import VirtualFolder
from dominio.excecoes import ErroBookmarks

from aplicacao.portas.exportador import Exportador

EXPORTADORES: dict[str, Exportador] = {
    ".json": ExportadorJSON(),
    ".csv": ExportadorCSV(),
    ".txt": ExportadorTXT(),
    ".pdf": ExportadorPDF(),
    ".md": ExportadorMarkdown(),
}


def exportar_bookmarks(raiz: VirtualFolder, formato: str, caminho_saida: Path | None = None) -> str | None:
    """Exporta uma hierarquia de bookmarks no formato desejado.
    Usa um exportador registrado para converter a estrutura em conteúdo serializado ou arquivo.

    A função normaliza a extensão pedida, busca o exportador correspondente e delega a ele a
    responsabilidade de gerar a saída final, retornando o conteúdo em memória quando aplicável.

    Args:
        raiz: Pasta raiz que contém toda a hierarquia de bookmarks a ser exportada.
        formato: Formato de saída desejado, como '.json', '.csv', '.txt' ou '.pdf'.
        caminho_saida: Caminho de arquivo onde o resultado será gravado, se fornecido.

    Returns:
        Conteúdo exportado como string, ou None para exportadores que trabalham apenas com saída em arquivo.

    Raises:
        ErroBookmarks: Se o formato solicitado não tiver um exportador registrado.
    """
    exportador: Exportador | None = EXPORTADORES.get(formato)
    if not exportador:
        formatos_validos: str = ", ".join(EXPORTADORES.keys())
        raise ErroBookmarks(f"Formato '{formato}' não suportado. Use: {formatos_validos}")
    return exportador.exportar(raiz=raiz, caminho_saida=caminho_saida)
