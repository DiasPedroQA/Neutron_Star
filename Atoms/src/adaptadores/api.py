# Atoms/api.py

"""Adaptador de entrada: rotas FastAPI para todos os serviços."""

from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Body, Depends

from aplicacao.casos_uso import (
    ConverterTagExtraidas,
    ListarTagExtraidas,
    OrquestrarBuscaEConversao,
)
from dominio.entidades import TagExtraida
from montagem.dependencias import (
    obter_converter_arquivos_html,
    obter_listar_arquivos_html,
    obter_orquestrar_busca_conversao,
)

router = APIRouter()


@router.get(path="/buscar")
async def buscar(
    use_case: Annotated[ListarTagExtraidas, Depends(
        dependency=obter_listar_arquivos_html)]
) -> dict[str, str | Sequence[TagExtraida]]:
    """Endpoint para listar todos os arquivos html."""
    dados: Sequence[TagExtraida] = use_case.buscar_arquivos_html()
    return {"status": "sucesso", "dados": dados}


@router.post(path="/converter")
async def converter(
    arquivos_html: Annotated[list, Body(embed=True)],
    use_case: Annotated[ConverterTagExtraidas, Depends(dependency=obter_converter_arquivos_html)],
) -> dict[str, str]:
    """Endpoint para converter uma lista de arquivos html para Markdown."""
    objetos: list[TagExtraida] = [
        TagExtraida(**item) for item in arquivos_html]
    resultado: str = use_case.executar(arquivos_html=objetos)
    return {"status": "sucesso", "conteudo": resultado}


@router.get(path="/orquestrar")
async def orquestrar(
    use_case: Annotated[
        OrquestrarBuscaEConversao, Depends(
            dependency=obter_orquestrar_busca_conversao)
    ],
) -> dict[str, str]:
    """Endpoint que busca arquivos html externamente e converte."""
    resultado: str = use_case.executar()
    return {"status": "sucesso", "conteudo": resultado}
