# """Adaptador de saída: implementa `ExportadorPorta` usando pandas.

# `WRITERS` preserva o mapeamento formato → função de escrita do design
# original, mas cada função agora retorna `bytes` (em vez de escrever direto
# em um `Path`), já que o serviço não sabe onde o chamador vai persistir o
# resultado — só devolve o conteúdo pronto na resposta HTTP.
# """

# from __future__ import annotations

# import io
# from typing import Callable

# import pandas as pd

# from dominio.entidades import Bookmark
# from dominio.excecoes import ArquivoInvalidoError


# def _escrever_csv(df: pd.DataFrame) -> bytes:
#     return df.to_csv(index=False).encode("utf-8")


# def _escrever_json(df: pd.DataFrame) -> bytes:
#     return df.to_json(orient="records", force_ascii=False).encode("utf-8")


# def _escrever_parquet(df: pd.DataFrame) -> bytes:
#     buffer = io.BytesIO()
#     df.to_parquet(buffer, index=False)
#     return buffer.getvalue()


# def _escrever_xml(df: pd.DataFrame) -> bytes:
#     return df.to_xml(index=False).encode("utf-8")


# def _escrever_md(df: pd.DataFrame) -> bytes:
#     return df.to_markdown(index=False).encode("utf-8")


# WRITERS: dict[str, Callable[[pd.DataFrame], bytes]] = {
#     "csv": _escrever_csv,
#     "json": _escrever_json,
#     "parquet": _escrever_parquet,
#     "xml": _escrever_xml,
#     "md": _escrever_md,
# }


# class ExportadorPandas:
#     """Implementação de `ExportadorPorta` baseada em pandas, mapeando formato → função via `WRITERS`."""

#     def exportar(self, bookmarks: list[Bookmark], formato: str) -> bytes:
#         """Converte `bookmarks` para `formato`. Lança `ArquivoInvalidoError` se não suportado."""
#         escritor = WRITERS.get(formato)
#         if escritor is None:
#             formatos_validos = ", ".join(sorted(WRITERS))
#             raise ArquivoInvalidoError(
#                 f"Formato '{formato}' não suportado. Formatos válidos: {formatos_validos}"
#             )
#         df = pd.DataFrame([bookmark.para_dict() for bookmark in bookmarks])
#         return escritor(df)
