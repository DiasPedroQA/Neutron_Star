"""Módulo de orquestração de pipelines de bookmarks.

Fornece:
- Pipeline básico (etapas sequenciais)
- Builder fluente para pipelines
- Execução condicional
- Dry-run e modos de validação
"""

from orquestracao.builder import PipelineBuilder
from orquestracao.condicional import executar_pipeline_condicional
from orquestracao.contextos import DEFAULT_FORMATOS, criar_contexto
from orquestracao.dry_run import executar_dry_run
from orquestracao.pipeline import ETAPAS_DISPONIVEIS, executar_pipeline_basico

__all__: list[str] = [
    "DEFAULT_FORMATOS",
    "ETAPAS_DISPONIVEIS",
    "PipelineBuilder",
    "criar_contexto",
    "executar_dry_run",
    "executar_pipeline_basico",
    "executar_pipeline_condicional",
]
