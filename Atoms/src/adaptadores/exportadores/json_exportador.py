"""Adaptador de exportação de bookmarks para JSON estruturado.

Implementa um exportador concreto que serializa a hierarquia de
favoritos em uma string JSON, opcionalmente gravando o resultado em arquivo.
"""

import json
from pathlib import Path

from aplicacao.portas.exportador import Exportador
from dominio.entidades import BookmarkFolder


class ExportadorJSON(Exportador):  # pylint: disable=too-few-public-methods
    """Exportador de bookmarks para JSON estruturado.
    Converte a hierarquia de favoritos em uma representação textual em formato JSON."""

    def exportar(self, raiz: BookmarkFolder, caminho_saida: Path | None = None) -> str | None:
        """Gera uma saída em JSON com toda a hierarquia de bookmarks.
        Opcionalmente grava o conteúdo gerado em um arquivo no caminho informado.

        Args:
            raiz: Pasta raiz que contém toda a estrutura de bookmarks a ser serializada.
            caminho_saida: Caminho de arquivo onde o JSON será gravado, se fornecido.

        Returns:
            String JSON contendo a hierarquia de favoritos exportada.
        """
        conteudo: str = json.dumps(raiz.to_dict(), indent=2, ensure_ascii=False)
        if caminho_saida:
            caminho_saida.write_text(data=conteudo, encoding="utf-8")
        return conteudo
