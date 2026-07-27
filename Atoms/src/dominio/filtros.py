"""Predicados de domínio para filtragem de caminhos de arquivos.

Define funções que avaliam características de nomes e caminhos, como
visibilidade, presença de palavras-chave e padrões de data, para apoio à lógica de busca.
"""

from pathlib import Path

DEFAULT_CHAVES: list[str] = ["favorito", "bookmark"]


def extrair_nome_do_caminho(caminho: Path) -> str:
    """Extrai apenas o nome do arquivo de seu caminho original."""
    return caminho.name.lower()


def caminho_nao_oculto(caminho: Path) -> bool:
    """True se nenhuma parte do caminho começa com '.'."""
    return not any(parte.startswith(".") for parte in caminho.parts)


def no_nome_contem_chave(caminho: Path) -> bool:
    """True se o nome contém ao menos uma das chaves (case-insensitive)."""
    nome: str = caminho.name.lower()
    return any(nome.startswith(chave) for chave in DEFAULT_CHAVES)
