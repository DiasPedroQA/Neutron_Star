# Atoms/api.py

"""Adaptador de entrada: rotas FastAPI para todos os serviços."""

from typing import Annotated
from fastapi import APIRouter, Depends, Body
from aplicacao.casos_uso import (
    ConverterBookmarks,
    ListarBookmarks,
    OrquestrarBuscaEConversao,
)
from dependencias import (
    obter_converter_bookmarks,
    obter_listar_bookmarks,
    obter_orquestrar_busca_conversao,
)
from dominio.entidades import Bookmark

router = APIRouter()


@router.get(path="/buscar")
async def buscar(
    use_case: Annotated[ListarBookmarks, Depends(
        dependency=obter_listar_bookmarks)]
) -> dict[str, str | list[Bookmark]]:
    """Endpoint para listar todos os bookmarks."""
    dados: list[Bookmark] = use_case.buscar_arquivos_html()
    return {"status": "sucesso", "dados": dados}


@router.post(path="/converter")
async def converter(
    bookmarks: Annotated[list, Body(embed=True)],
    use_case: Annotated[ConverterBookmarks, Depends(dependency=obter_converter_bookmarks)],
) -> dict[str, str]:
    """Endpoint para converter uma lista de bookmarks para Markdown."""
    objetos: list[Bookmark] = [Bookmark(**item) for item in bookmarks]
    resultado: str = use_case.executar(bookmarks=objetos)
    return {"status": "sucesso", "conteudo": resultado}


@router.get(path="/orquestrar")
async def orquestrar(
    use_case: Annotated[
        OrquestrarBuscaEConversao, Depends(
            dependency=obter_orquestrar_busca_conversao)
    ],
) -> dict[str, str]:
    """Endpoint que busca bookmarks externamente e converte."""
    resultado: str = use_case.executar()
    return {"status": "sucesso", "conteudo": resultado}
