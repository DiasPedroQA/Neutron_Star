"""Exceções de domínio compartilhadas entre os serviços do Neutron Star."""

from __future__ import annotations


class ErroDominioNeutron(Exception):
    """Classe base para exceções de domínio do Neutron Star."""


class PastaInvalidaError(ErroDominioNeutron):
    """Lançada quando a pasta informada não existe, não é diretório, ou não contém bookmarks."""


class ArquivoInvalidoError(ErroDominioNeutron):
    """Lançada quando um arquivo, ou formato de exportação solicitado, não é suportado."""
