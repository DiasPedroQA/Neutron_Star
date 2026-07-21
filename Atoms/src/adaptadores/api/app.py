"""Adaptador de API HTTP para o núcleo de bookmarks.

Este módulo é só uma casca fina: interpreta requisições HTTP, chama as
mesmas funções da camada `aplicacao` usadas pela CLI (main.py) e traduz o
resultado de volta para JSON. Nenhuma regra de negócio mora aqui — se a
lógica de busca, extração ou exportação mudar, ela muda em um único lugar
(aplicacao/), e tanto a CLI quanto esta API continuam corretas.
"""

from pathlib import Path

from aplicacao.casos_de_uso.processar_lote import processar_arquivos_em_lote
from aplicacao.etapas import etapa_buscar
from aplicacao.tipos import ParametrosBusca
from dominio.excecoes import ErroBookmarks
from fastapi import FastAPI, HTTPException

from adaptadores.api.schemas import (
    RequisicaoBusca,
    RequisicaoProcessarLote,
    RespostaBusca,
    RespostaProcessarLote,
)

app = FastAPI(
    title="Neutron Star — API de Bookmarks",
    description="Mesmo núcleo de aplicação usado pela CLI, exposto via HTTP.",
    version="0.1.0",
)


@app.get(path="/health")
def verificar_saude() -> dict[str, str]:
    """Endpoint simples de verificação de disponibilidade da API."""
    return {"status": "ok"}


@app.post(
    path="/bookmarks/buscar",
    responses={422: {"description": "Erro de validação ou processamento"}},
)
def buscar(requisicao: RequisicaoBusca) -> RespostaBusca:
    """Busca arquivos de bookmarks em um diretório, aplicando os mesmos filtros da CLI.

    Reaproveita `aplicacao.etapas.etapa_buscar` — a mesma função chamada pelo `main.py`.
    """
    try:
        contexto: ParametrosBusca = etapa_buscar(
            contexto_busca={
                "diretorio": Path(requisicao.diretorio),
                "extensao": requisicao.extensao,
                "chaves": requisicao.chaves,
                "exigir_data": requisicao.exigir_data,
            }
        )
    except ErroBookmarks as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro

    arquivos: list[Path] = contexto.get("arquivos_encontrados", [])
    return RespostaBusca(arquivos_encontrados=[str(arquivo) for arquivo in arquivos])


@app.post(path="/bookmarks/lote")
def processar_lote(requisicao: RequisicaoProcessarLote) -> RespostaProcessarLote:
    """Processa um conjunto de arquivos de bookmarks, exportando cada um.

    Reaproveita `aplicacao.casos_de_uso.processar_lote.processar_arquivos_em_lote`
    — a mesma função usada pelo modo `--lote` da CLI.
    """
    arquivos: list[Path] = [Path(arquivo) for arquivo in requisicao.arquivos]
    diretorio_saida: Path | None = Path(requisicao.diretorio_saida) if requisicao.diretorio_saida else None

    falhas: dict[Path, ErroBookmarks] = processar_arquivos_em_lote(
        arquivos=arquivos, formatos=requisicao.formatos, diretorio_saida=diretorio_saida
    )

    return RespostaProcessarLote(
        total=len(arquivos),
        sucesso=len(arquivos) - len(falhas),
        falhas={str(arquivo): str(erro) for arquivo, erro in falhas.items()},
    )
