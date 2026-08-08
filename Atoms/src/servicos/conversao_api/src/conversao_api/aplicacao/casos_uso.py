# """Casos de uso do serviço de conversão — não dependem de FastAPI nem de pandas diretamente."""

# from __future__ import annotations

# from dominio.entidades import Bookmark

# from conversao_api.aplicacao.portas import ExportadorPorta


# class ConverterBookmarks:
#     """Caso de uso: converter uma lista de bookmarks para o formato de saída solicitado."""

#     def __init__(self, exportador: ExportadorPorta) -> None:
#         self._exportador = exportador

#     def executar(self, bookmarks: list[Bookmark], formato: str) -> bytes:
#         """Executa a conversão. `ArquivoInvalidoError` é lançada pelo adaptador se o formato não for suportado."""
#         return self._exportador.exportar(bookmarks, formato)
