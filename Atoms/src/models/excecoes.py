# Atoms/src/models/excecoes.py

"""Definição de exceções de domínio do Neutron Star."""


class DominioError(Exception):
    """Exceção base para todas as regras de domínio."""


class PathInseguroError(DominioError):
    """Lançada quando um caminho tenta acessar áreas fora do escopo seguro (Path Traversal)."""

    def __init__(self, caminho: str) -> None:
        super().__init__(
            f"Acesso Proibido! O caminho '{caminho}' tenta "
            "acessar arquivos fora da sua pasta pessoal de segurança."
        )


class DiretorioInexistenteError(DominioError):
    """Lançada quando o diretório informado não existe no disco."""

    def __init__(self, caminho: str) -> None:
        super().__init__(
            f"Diretório não encontrado: O caminho '{caminho}' não existe no disco local."
        )


class ExtensaoInvalidaError(DominioError):
    """Lançada quando um formato de saída ou extensão não é suportado."""


class FormatoInvalidoError(ExtensaoInvalidaError):
    """Alias compatível para formatos e extensões não suportadas."""
