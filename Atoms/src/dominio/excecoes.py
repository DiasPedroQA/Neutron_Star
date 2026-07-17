"""Exceções de domínio para erros relacionados a bookmarks.

Define uma hierarquia de erros específicos para problemas ao validar
diretórios de entrada e interpretar arquivos de favoritos em HTML.
"""


class ErroBookmarks(Exception):
    """Exceção base para erros do módulo."""

    def __init__(
        self,
        mensagem: str,
        *,
        contexto: dict[str, str | list[str]] | None = None,
    ) -> None:
        super().__init__(mensagem)
        self.contexto: dict[str, str | list[str]] = contexto or {}

    def __str__(self) -> str:
        base: str = super().__str__()
        if not self.contexto:
            return base
        detalhes: str = ", ".join(f"{k}={v!r}" for k, v in self.contexto.items())
        return f"{base} [{detalhes}]"


class NenhumDiretorioValidoError(ErroBookmarks):
    """Nenhum diretório de entrada é válido."""


class ErroParseBookmarks(ErroBookmarks):
    """Falha ao interpretar o arquivo de bookmarks."""
