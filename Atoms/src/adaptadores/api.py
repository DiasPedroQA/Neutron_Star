"""
Adaptador de API (FastAPI).

Fino de propósito, como o adaptador de CLI: expõe os mesmos casos de
uso da camada de aplicação por HTTP. Opera sobre caminhos de arquivo
já presentes no sistema de arquivos onde a API roda (sem upload de
arquivos, para manter o escopo enxuto nesta primeira versão).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from pandas import DataFrame
from pydantic import BaseModel

from src.aplicacao.casos_de_uso.buscar_bookmarks import gerar_relatorio
from src.aplicacao.casos_de_uso.converter_bookmarks import (
    adicionar_favicon_url,
    converter_arquivos,
    parse_bookmarks_html,
)

app: FastAPI = FastAPI(
    title="Bookmarks Toolkit API",
    description="Descobre, lê e converte arquivos de bookmarks (Netscape).",
    version="0.1.0",
)


class PedidoConversao(BaseModel):
    """Corpo da requisição de conversão de arquivos de bookmarks."""

    caminhos: list[str]
    formatos: list[str] = [".csv", ".json"]
    sufixo: str | None = None
    favicon: bool = False
    icone: bool = False


class RespostaConversao(BaseModel):
    """Resposta com os caminhos dos arquivos gerados."""

    arquivos_gerados: list[str]


@app.get(path="/saude")
def saude() -> dict[str, str]:
    """Endpoint simples de verificação de disponibilidade."""
    return {"status": "ok"}


@app.get(path="/buscar")
def buscar(origem: str | None = None) -> list[dict[str, Any]]:
    """Busca arquivos de bookmarks a partir de `origem` (padrão: pasta do usuário)."""
    pasta: Path = Path(origem).expanduser() if origem else Path.home()
    if not pasta.is_dir():
        raise HTTPException(status_code=400, detail=f"Pasta não encontrada: {pasta}")
    return gerar_relatorio(pasta_entrada=pasta)


@app.post(path="/converter", response_model=RespostaConversao)
def converter(pedido: PedidoConversao) -> RespostaConversao:
    """Converte os arquivos informados para os formatos solicitados."""
    caminhos: list[Path] = [Path(p) for p in pedido.caminhos]
    ausentes: list[str] = [str(p) for p in caminhos if not p.is_file()]
    if ausentes:
        raise HTTPException(status_code=400, detail=f"Arquivo(s) não encontrado(s): {ausentes}")

    def parser(caminho: Path) -> DataFrame:
        df: DataFrame = parse_bookmarks_html(html_path=caminho, extrair_icone=pedido.icone)
        return adicionar_favicon_url(df) if pedido.favicon else df

    gerados: list[Path] = converter_arquivos(
        lista_paths=caminhos,
        parser=parser,
        output_formats=pedido.formatos,
        sufixo_saida=pedido.sufixo,
    )
    return RespostaConversao(arquivos_gerados=[str(p) for p in gerados])


def main() -> None:
    """Ponto de entrada do console script `bookmarks-api` (roda com uvicorn)."""
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
