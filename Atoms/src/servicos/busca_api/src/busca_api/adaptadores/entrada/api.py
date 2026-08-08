# """Adaptador de entrada HTTP do busca_api — só traduz HTTP ↔ caso de uso, sem lógica de negócio."""

# from __future__ import annotations

# from pathlib import Path

# from fastapi import Depends, FastAPI, HTTPException

# from dominio.excecoes import PastaInvalidaError

# from busca_api.aplicacao.casos_uso import BuscarBookmarks
# from busca_api.composicao import obter_buscar_bookmarks

# app = FastAPI(title="busca-api", version="0.1.0")


# @app.get("/saude")
# def saude() -> dict[str, str]:
#     """Endpoint de health-check."""
#     return {"status": "ok"}


# @app.get("/buscar")
# def buscar(
#     pasta: str,
#     caso_de_uso: BuscarBookmarks = Depends(obter_buscar_bookmarks),
# ) -> dict[str, object]:
#     """Busca bookmarks em `pasta` e retorna os encontrados, junto dos arquivos processados."""
#     try:
#         resultado = caso_de_uso.executar(Path(pasta))
#     except PastaInvalidaError as erro:
#         raise HTTPException(status_code=400, detail=str(erro)) from erro
#     return {
#         "arquivos_processados": resultado.arquivos_processados,
#         "bookmarks": [bookmark.para_dict() for bookmark in resultado.bookmarks],
#     }
