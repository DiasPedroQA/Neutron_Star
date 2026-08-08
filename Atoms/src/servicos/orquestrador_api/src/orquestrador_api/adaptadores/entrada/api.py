# """Adaptador de entrada HTTP do orquestrador — só traduz HTTP ↔ caso de uso."""

# from __future__ import annotations

# from fastapi import Depends, FastAPI, HTTPException, Response
# from pydantic import BaseModel

# from dominio.excecoes import PastaInvalidaError

# from orquestrador_api.aplicacao.casos_uso import BuscarEConverterBookmarks
# from orquestrador_api.composicao import obter_buscar_e_converter_bookmarks

# app = FastAPI(title="orquestrador-api", version="0.1.0")


# class PedidoBuscarEConverter(BaseModel):
#     """Corpo da requisição: pasta a buscar e formato de saída desejado."""

#     pasta: str
#     formato: str


# @app.get("/saude")
# def saude() -> dict[str, str]:
#     """Endpoint de health-check."""
#     return {"status": "ok"}


# @app.post("/buscar-e-converter")
# def buscar_e_converter(
#     pedido: PedidoBuscarEConverter,
#     caso_de_uso: BuscarEConverterBookmarks = Depends(obter_buscar_e_converter_bookmarks),
# ) -> Response:
#     """Busca bookmarks em `pedido.pasta` e converte para `pedido.formato`, retornando o conteúdo gerado."""
#     try:
#         conteudo = caso_de_uso.executar(pedido.pasta, pedido.formato)
#     except PastaInvalidaError as erro:
#         raise HTTPException(status_code=404, detail=str(erro)) from erro
#     return Response(content=conteudo)
