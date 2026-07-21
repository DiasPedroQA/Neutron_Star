"""Adaptador de exportação de bookmarks para tabela Markdown.

Implementa um exportador concreto que gera uma tabela legível (Título, URL,
Data de adição, Pasta), útil para colar em anotações ou documentação.
"""

from pathlib import Path

from aplicacao.portas.exportador import Exportador
from dominio.entidades import TagA, VirtualFolder
from dominio.tempo import converter_timestamp_unix
from dominio.travessia import iterar_bookmarks_com_caminho


class ExportadorMarkdown(Exportador):
    """Exportador de bookmarks para tabela Markdown."""

    _CABECALHO = "| Título | URL | Data de adição | Pasta |"
    _SEPARADOR = "|--------|-----|----------------|-------|"

    def exportar(self, raiz: VirtualFolder, caminho_saida: Path | None = None) -> str | None:
        """Exporta bookmarks como tabela Markdown (ver Exportador.exportar)."""
        linhas: list[str] = [self._CABECALHO, self._SEPARADOR]
        linhas.extend(
            self._montar_linha(pasta=pasta, bookmark_data=bookmark)
            for pasta, bookmark in iterar_bookmarks_com_caminho(pasta=raiz)
        )
        conteudo: str = "\n".join(linhas) + "\n"
        if caminho_saida:
            caminho_saida.write_text(data=conteudo, encoding="utf-8")
        return conteudo

    @staticmethod
    def _montar_linha(pasta: str, bookmark_data: TagA) -> str:
        """Monta uma linha da tabela para um favorito, formatando a data se possível."""
        data: str = ""
        if convertida := converter_timestamp_unix(valor=bookmark_data.data_adicao):
            data = convertida.strftime(format="%Y-%m-%d %H:%M")
        return f"| {bookmark_data.titulo} | {bookmark_data.url} | {data} | {pasta} |"
