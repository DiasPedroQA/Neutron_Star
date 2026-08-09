# Atoms/dominio/excecoes.py

"""Exceções personalizadas do domínio de arquivos html."""


class TagExtraidaNaoEncontradoError(Exception):
    """Exceção levantada quando um bookmark não é encontrado."""
