# Atoms/src/dominio/excecoes.py

"""Exceções personalizadas do domínio."""


class ErroDominio(Exception):
    """Classe base para todas as exceções de domínio do sistema."""


class PathInseguroError(ErroDominio):
    """Disparada quando o caminho solicitado aponta para fora da Home do usuário
    (Path Traversal)."""

    def __init__(self, caminho: str) -> None:
        super().__init__(
            f"Acesso Proibido! O caminho '{caminho}' tenta acessar "
            "arquivos fora da sua pasta pessoal de segurança."
        )


class DiretorioInexistenteError(ErroDominio):
    """Disparada quando o diretório solicitado não pôde ser encontrado fisicamente."""

    def __init__(self, caminho: str) -> None:
        super().__init__(
            f"Diretório não encontrado: O caminho '{caminho}' não existe no disco local."
        )


class NenhumFavoritoEncontradoError(ErroDominio):
    """Disparada quando o arquivo HTML é processado mas não contém nenhum link válido."""

    def __init__(self, arquivo: str) -> None:
        super().__init__(
            f"O arquivo '{arquivo}' não possui tags de favoritos válidas para extração."
        )
