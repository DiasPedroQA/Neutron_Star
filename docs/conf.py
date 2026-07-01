"""Configuração do Sphinx para a documentação do Neutron Star.

Para gerar a documentação::

    make docs-html          # via Makefile
    sphinx-build -b html docs docs/_build/html   # direto

A documentação fica disponível em ``docs/_build/html/index.html``.
"""

from __future__ import annotations

import os
import sys

# FIX [AVISO]: aponta para Atoms/ (onde vivem models, controllers etc.)
# para que autodoc encontre os módulos com o padrão de import atual.
sys.path.insert(0, os.path.abspath(".."))  # raiz do projeto
sys.path.insert(0, os.path.abspath("../Atoms"))  # pacotes internos

PROJECT = "Neutron Star"
AUTHOR = "Pedro Dias"
RELEASE = "0.1.0"
LANGUAGE = "pt_BR"

EXTENSIONS: list[str] = [
    "sphinx.ext.autodoc",  # extrai docstrings automaticamente
    "sphinx.ext.napoleon",  # suporte a Google/NumPy docstrings
    "sphinx.ext.viewcode",  # links para o código-fonte
    "sphinx.ext.autosummary",  # tabelas de resumo automáticas
]

AUTODOC_TYPEHINTS = "description"
AUTODOC_DEFAULT_OPTIONS: dict[str, bool] = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

TEMPLATES_PATH: list[str] = ["_templates"]
EXCLUDE_PATTERNS: list[str] = ["_build", "Thumbs.db", ".DS_Store"]

# FIX [SOLICITADO]: substituído alabaster (branco) por furo (dark mode nativo).
# Furo tem alternância automática claro/escuro e é o padrão moderno recomendado.
# Instale: pip install furo
HTML_THEME = "furo"

HTML_THEME_OPTIONS: dict[str, str | bool | dict[str, str]] = {
    # Ativa dark mode por padrão — o usuário pode alternar via botão na UI
    "light_logo": "logo.png",
    "dark_logo": "logo.png",
    "sidebar_hide_name": False,
    # Paleta escura como padrão
    "dark_css_variables": {
        "color-brand-primary": "#4FC3F7",
        "color-brand-content": "#4FC3F7",
        "color-background-primary": "#1A1A2E",
        "color-background-secondary": "#16213E",
        "color-foreground-primary": "#E0E0E0",
        "color-foreground-secondary": "#B0B0B0",
    },
    "light_css_variables": {
        "color-brand-primary": "#0277BD",
        "color-brand-content": "#0277BD",
    },
}

HTML_STATIC_PATH: list[str] = ["_static"]
