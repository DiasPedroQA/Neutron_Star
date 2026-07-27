"""Pipeline assíncrono para operações IO-bound."""

import asyncio
from collections.abc import Callable

from aplicacao.tipos import ParametrosBusca
from dominio.excecoes import ErroBookmarks

from orquestracao.pipeline import ETAPAS_DISPONIVEIS


async def executar_pipeline_async(
    contexto: ParametrosBusca,
    etapas: list[str],
) -> ParametrosBusca:
    """Executa pipeline assíncrono (etapas são executadas em ordem)."""
    for nome in etapas:
        etapa: Callable[[ParametrosBusca], ParametrosBusca] | None = ETAPAS_DISPONIVEIS.get(nome)
        if etapa is None:
            print(f"Etapa '{nome}' desconhecida - ignorada.")
            continue
        try:
            # Etapas síncronas: executa em thread separada
            contexto = await asyncio.to_thread(etapa, contexto)
        except (ErroBookmarks, ValueError) as e:
            print(f"Erro na etapa '{nome}': {e}")
            raise
    return contexto
