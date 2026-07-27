"""Modo dry-run para simular execução sem efeitos colaterais."""

from collections.abc import Callable

from aplicacao.tipos import ParametrosBusca

from orquestracao.pipeline import ETAPAS_DISPONIVEIS


def executar_dry_run(
    contexto: ParametrosBusca,
    etapas: list[str],
) -> None:
    """
    Simula a execução de etapas sem modificar estado.

    Útil para depuração e validação de pipelines.
    """
    print("\n🧪 DRY-RUN: Etapas a serem executadas\n")
    print(f"  Estado inicial: {list(contexto.keys())}\n")

    for nome in etapas:
        etapa: Callable[[ParametrosBusca], ParametrosBusca] | None = ETAPAS_DISPONIVEIS.get(nome)
        if etapa is None:
            print(f"  ❌ {nome} (DESCONHECIDA)")
            continue

        # Tenta simular a etapa (sem efeitos colaterais)
        try:
            # Aqui poderíamos chamar uma versão "simulada" da etapa se existir
            print(f"  ✅ {nome}")
        except Exception as e:  # pylint: disable=W0718
            print(f"  ⚠️ {nome} (falha simulada: {e})")

    print(f"\n  Estado final simulado: {list(contexto.keys())}")
