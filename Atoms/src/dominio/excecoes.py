"""Exceções de domínio para erros relacionados a bookmarks.

Define uma hierarquia de erros específicos para problemas ao validar
diretórios de entrada e interpretar arquivos de favoritos em HTML.
"""

from __future__ import annotations


class ErroBookmarks(Exception):
    """Exceção base para erros do módulo.

    Representa falhas relacionadas a operações com bookmarks, permitindo anexar
    informações de contexto para tornar a mensagem de erro mais clara.
    """

    def __init__(
        self,
        mensagem: str,
        *,
        contexto: dict[str, object] | None = None,
    ) -> None:
        """Inicializa um erro de bookmarks com mensagem e contexto opcional.

        Armazena um dicionário de dados adicionais que podem ajudar a entender
        melhor as circunstâncias em que o erro ocorreu.

        Args:
            mensagem: Texto descritivo do erro.
            contexto: Dados adicionais sobre o erro, como parâmetros ou estado
                relevante no momento da falha.
        """
        super().__init__(mensagem)
        self.contexto: dict[str, object] = contexto or {}

    def __str__(self) -> str:
        """Retorna a mensagem de erro possivelmente enriquecida com o contexto.

        Se houver dados extras armazenados em `contexto`, a representação textual
        do erro inclui essas informações formatadas após a mensagem base.

        Returns:
            str: Representação textual do erro, com ou sem detalhes de contexto.
        """
        base: str = super().__str__()
        if not self.contexto:
            return base
        detalhes: str = ", ".join(f"{k}={v!r}" for k, v in self.contexto.items())
        return f"{base} [{detalhes}]"


class NenhumDiretorioValidoError(ErroBookmarks):
    """Nenhum diretório de entrada é válido.

    Indica que todos os diretórios analisados para busca de arquivos de bookmarks
    foram considerados inválidos ou inacessíveis.
    """

    def __init__(
        self,
        mensagem: str = "Nenhum diretório de entrada válido encontrado.",
        *,
        contexto: dict[str, object] | None = None,
    ) -> None:
        """Inicializa o erro indicando ausência de diretórios válidos.

        Permite opcionalmente registrar informações adicionais, como a lista de
        caminhos testados ou motivos da invalidez.

        Args:
            mensagem: Texto descritivo do erro, com uma mensagem padrão amigável.
            contexto: Dados adicionais sobre o erro, como diretórios verificados
                e resultados das validações.
        """
        super().__init__(mensagem=mensagem, contexto=contexto)


class ErroParseBookmarks(ErroBookmarks):
    """Falha ao interpretar o arquivo de bookmarks.

    Indica que o conteúdo de um arquivo de favoritos em HTML não pôde ser compreendido
    ou convertido na estrutura de entidades esperada.
    """

    def __init__(
        self,
        mensagem: str = "Erro ao interpretar o arquivo de bookmarks.",
        *,
        contexto: dict[str, object] | None = None,
    ) -> None:
        """Inicializa o erro de parsing de bookmarks com mensagem e contexto opcionais.

        Permite registrar informações sobre o arquivo problemático ou trechos de
        conteúdo que causaram falha na interpretação.

        Args:
            mensagem: Texto descritivo do erro, com uma mensagem padrão genérica.
            contexto: Dados adicionais sobre o erro, como caminho do arquivo,
                posição do erro ou detalhes do HTML inválido.
        """
        super().__init__(mensagem=mensagem, contexto=contexto)
