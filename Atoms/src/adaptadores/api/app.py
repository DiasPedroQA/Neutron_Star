"""Adaptador de API HTTP para o núcleo de bookmarks.

Este módulo é só uma casca fina: interpreta requisições HTTP, chama as
mesmas funções da camada `aplicacao` usadas pela CLI (main.py) e traduz o
resultado de volta para JSON. Nenhuma regra de negócio mora aqui — se a
lógica de busca, extração ou exportação mudar, ela muda em um único lugar
(aplicacao/), e tanto a CLI quanto esta API continuam corretas.
"""

import argparse
from pathlib import Path

import uvicorn
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


@app.post(path="/bookmarks/buscar", response_model=RespostaBusca)
def buscar(requisicao: RequisicaoBusca) -> RespostaBusca:
    """Busca arquivos de bookmarks em um diretório, aplicando os mesmos filtros da CLI.

    Reaproveita `aplicacao.etapas.etapa_buscar` — a mesma função chamada pelo `main.py`.
    """
    try:
        contexto: ParametrosBusca = etapa_buscar(
            contexto_busca={
                "diretorio": Path(requisicao.diretorio),
            }
        )
    except ErroBookmarks as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro

    arquivos: list[Path] = contexto.get("arquivos_encontrados", [])
    return RespostaBusca(arquivos_encontrados=[str(arquivo) for arquivo in arquivos])


@app.post(path="/bookmarks/lote", response_model=RespostaProcessarLote)
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


# --------------------------------------------
# Execução direta: python -m adaptadores.api.app
# --------------------------------------------
def executar(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    """Sobe a API com uvicorn programaticamente.

    Forma alternativa de iniciar a API, sem depender de digitar o comando
    completo do uvicorn na mão. Mesma aplicação, mesmo núcleo — só muda
    quem dispara o `uvicorn.run`.

    Args:
        host: Endereço em que o servidor vai escutar.
        port: Porta em que o servidor vai escutar.
        reload: Se True, reinicia o servidor a cada mudança de código (dev only).
    """
    uvicorn.run("adaptadores.api.app:app", host=host, port=port, reload=reload)


def main(argv: list[str] | None = None) -> None:
    """Ponto de entrada de console (`neutron-api`) — lê host/porta de argumentos simples.

    Args:
        argv: Argumentos de linha de comando; se None, usa sys.argv[1:].
    """
    parser = argparse.ArgumentParser(prog="neutron-api", description="Sobe a API de bookmarks.")
    parser.add_argument("--host", default="127.0.0.1", help="Host (padrão: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=8000, help="Porta (padrão: 8000).")
    parser.add_argument("--reload", action="store_true", help="Recarrega a cada mudança de código (dev).")
    args = parser.parse_args(argv)
    executar(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
