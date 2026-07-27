"""Criação e manipulação de contextos (ParametrosBusca)."""

from pathlib import Path
from typing import Any, cast

from aplicacao.tipos import ParametrosBusca

# Constantes globais
DEFAULT_FORMATOS: list[str] = [".json", ".csv", "pdf", "txt", "md"]


def criar_contexto(
    diretorio: Path | None = None,
    *,
    formatos_exportacao: list[str] | None = None,
    diretorio_saida: Path | str | None = None,
) -> ParametrosBusca:
    """Cria um contexto ParametrosBusca com valores padrão."""
    if formatos_exportacao is None:
        formatos_exportacao = DEFAULT_FORMATOS.copy()
    if diretorio is None:
        diretorio = Path.home()
    if diretorio_saida is None:
        diretorio_saida = Path(diretorio, "Extracoes")

    return {
        "diretorio": diretorio,
        "formatos_exportacao": formatos_exportacao,
        "diretorio_saida": str(diretorio_saida),
    }


def atualizar_contexto(
    contexto: ParametrosBusca,
    **kwargs: Any,
) -> ParametrosBusca:
    """Atualiza um contexto com novos valores."""
    # Merge existing contexto with overrides in kwargs and ensure correct type
    merged: dict[str, object | Any] = {**contexto, **kwargs}
    return cast(ParametrosBusca, merged)
