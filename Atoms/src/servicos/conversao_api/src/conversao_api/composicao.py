# """Composition root do conversao_api: monta o adaptador concreto e injeta no caso de uso."""

# from __future__ import annotations

# from conversao_api.adaptadores.saida.escritores import ExportadorPandas
# from conversao_api.aplicacao.casos_uso import ConverterBookmarks


# def obter_converter_bookmarks() -> ConverterBookmarks:
#     """Fábrica usada pelo FastAPI (`Depends`) para obter o caso de uso já composto."""
#     return ConverterBookmarks(ExportadorPandas())
