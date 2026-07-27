"""Builder fluente para montagem de pipelines."""

from collections.abc import Callable

from aplicacao.tipos import ParametrosBusca
from dominio.excecoes import ErroBookmarks

from orquestracao.pipeline import ETAPAS_DISPONIVEIS


class PipelineBuilder:
    """
    Builder fluente para construir e executar pipelines.

    Exemplo:
        resultado = (
            PipelineBuilder(contexto)
            .adicionar("buscar")
            .adicionar("selecionar_arquivo")
            .adicionar("extrair")
            .executar()
        )
    """

    def __init__(self, contexto_inicial: ParametrosBusca) -> None:
        self.contexto: ParametrosBusca = contexto_inicial
        self._etapas: list[tuple[str, Callable[[ParametrosBusca], bool] | None]] = []
        self._hooks_antes: list[Callable[[ParametrosBusca], None]] = []
        self._hooks_depois: list[Callable[[ParametrosBusca], None]] = []

    def adicionar(
        self,
        nome: str,
        condicao: Callable[[ParametrosBusca], bool] | None = None,
    ) -> "PipelineBuilder":
        """Adiciona uma etapa (com condição opcional)."""
        self._etapas.append((nome, condicao))
        return self

    def antes(self, hook: Callable[[ParametrosBusca], None]) -> "PipelineBuilder":
        """Adiciona um hook executado antes de cada etapa."""
        self._hooks_antes.append(hook)
        return self

    def depois(self, hook: Callable[[ParametrosBusca], None]) -> "PipelineBuilder":
        """Adiciona um hook executado depois de cada etapa."""
        self._hooks_depois.append(hook)
        return self

    def executar(self) -> ParametrosBusca:
        """Executa o pipeline com hooks."""
        for nome, condicao in self._etapas:
            # Hooks antes
            for hook in self._hooks_antes:
                hook(self.contexto)

            # Verifica condição
            if condicao is not None and not condicao(self.contexto):
                print(f"Pulando etapa '{nome}' (condição não atendida)")
                continue

            # Executa etapa
            etapa: Callable[[ParametrosBusca], ParametrosBusca] | None = ETAPAS_DISPONIVEIS.get(nome)
            if etapa is None:
                print(f"Etapa '{nome}' desconhecida - ignorada.")
                continue

            try:
                self.contexto = etapa(self.contexto)
            except (ErroBookmarks, ValueError) as e:
                print(f"Erro na etapa '{nome}': {e}")
                raise

            # Hooks depois
            for hook in self._hooks_depois:
                hook(self.contexto)

        return self.contexto
