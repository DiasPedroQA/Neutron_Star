# Atoms/dominio/excecoes.py

"""Exceções personalizadas do domínio de bookmarks."""


class BookmarkNaoEncontradoError(Exception):
    """Exceção levantada quando um bookmark não é encontrado."""
