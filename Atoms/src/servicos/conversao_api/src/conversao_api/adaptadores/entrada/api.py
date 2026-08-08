# """Adaptador de entrada HTTP do conversao_api.

# ASSUNÇÃO (marcada explicitamente): como o serviço é independente do
# busca_api, `/converter` recebe os bookmarks já extraídos como JSON no corpo
# da requisição — não um caminho de arquivo `.html` para parsear. Quem faz o
# parsing é sempre o busca_api; conversao_api só sabe converter dados que já
# tem em mãos. Quem compõe as duas etapas é o orquestrador_api.
# """

# from __future__ import annotations

# from fastapi import Depends, FastAPI, HTTPException, Response
# from pydantic import BaseModel

# from dominio.entidades import Bookmark
# from dominio.excecoes import ArquivoInvalidoError

# from conversao_api.aplicacao.casos_uso import ConverterBookmarks
# from conversao_api.composicao import obter_converter_bookmarks

# app = FastAPI(title="conversao-api", version="0.1.0")

# _MEDIA_TYPES = {
#     "csv": "text/csv",
#     "json": "application/json",
#     "parquet": "application/octet-stream",
#     "xml": "application/xml",
#     "md": "text/markdown",
# }


# class PedidoConversao(BaseModel):
#     """Corpo da requisição: bookmarks já extraídos e o formato de saída desejado."""

#     bookmarks: list[dict[str, str | None]]
#     formato: str


# @app.get("/saude")
# def saude() -> dict[str, str]:
#     """Endpoint de health-check."""
#     return {"status": "ok"}


# @app.post("/converter")
# def converter(
#     pedido: PedidoConversao,
#     caso_de_uso: ConverterBookmarks = Depends(obter_converter_bookmarks),
# ) -> Response:
#     """Converte os bookmarks recebidos para o formato solicitado e retorna o conteúdo gerado."""
#     bookmarks = [Bookmark.de_dict(dados) for dados in pedido.bookmarks]
#     try:
#         conteudo = caso_de_uso.executar(bookmarks, pedido.formato)
#     except ArquivoInvalidoError as erro:
#         raise HTTPException(status_code=400, detail=str(erro)) from erro
#     media_type = _MEDIA_TYPES.get(pedido.formato, "application/octet-stream")
#     return Response(content=conteudo, media_type=media_type)
