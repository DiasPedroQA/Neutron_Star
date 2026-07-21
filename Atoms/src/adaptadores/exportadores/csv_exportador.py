"""Adaptador de exportação de bookmarks para arquivos CSV.

Implementa um exportador concreto que produz uma tabela com colunas
pré-definidas, representando cada favorito em uma linha para análise em planilhas ou ferramentas de dados.
"""

import csv
from io import StringIO
from pathlib import Path

from aplicacao.portas.exportador import Exportador
from dominio.entidades import VirtualFolder
from dominio.travessia import iterar_bookmarks


class ExportadorCSV(Exportador):
    """Exportador de bookmarks para arquivo CSV tabular."""

    _CABECALHO: list[str] = [
        "url",
        "titulo",
        "data_adicao",
        "ultima_modificacao",
        "icon_uri",
    ]

    def exportar(self, raiz: VirtualFolder, caminho_saida: Path | None = None) -> str | None:
        """Exporta bookmarks como CSV tabular (ver Exportador.exportar)."""
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(self._CABECALHO)
        for bm in iterar_bookmarks(pasta=raiz):
            writer.writerow([bm.url, bm.titulo, bm.data_adicao, bm.ultima_modificacao, bm.icon_uri])
        conteudo: str = output.getvalue()
        if caminho_saida:
            caminho_saida.write_text(data=conteudo, encoding="utf-8")
        return conteudo
