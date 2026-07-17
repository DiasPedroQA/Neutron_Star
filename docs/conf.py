"""Configuração do Sphinx para a documentação do Neutron Star.

Para gerar a documentação::

    make docs-html          # via Makefile
    sphinx-build -b html docs docs/_build/html   # direto

A documentação fica disponível em ``docs/_build/html/index.html``.
"""

from __future__ import annotations

import os
import sys

# Paths calculados a partir da localização deste arquivo (robusto a partir de
# qualquer diretório de onde `sphinx-build` seja invocado — raiz do repo ou não).
# Os pacotes (dominio, aplicacao, adaptadores, infraestrutura) vivem em
# Atoms/src/, que é o diretório que precisa entrar no sys.path para o autodoc
# conseguir importá-los.
_DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_DOCS_DIR)
sys.path.insert(0, os.path.join(_ROOT_DIR, "Atoms", "src"))

# NOTA: Sphinx só reconhece estas chaves em minúsculas (extensions, project,
# html_theme etc). As variáveis em maiúsculas usadas antes eram inertes:
# nenhuma delas era lida pelo Sphinx, então autodoc nunca carregava e o tema
# "furo" nunca era aplicado (o build sempre caía no tema padrão "alabaster").
project = "Neutron Star"
author = "Pedro Dias"
release = "0.1.0"
language = "pt_BR"

extensions: list[str] = [
    "sphinx.ext.autodoc",  # extrai docstrings automaticamente
    "sphinx.ext.napoleon",  # suporte a Google/NumPy docstrings
    "sphinx.ext.viewcode",  # links para o código-fonte
    "sphinx.ext.autosummary",  # tabelas de resumo automáticas
]

autodoc_typehints = "description"
autodoc_default_options: dict[str, bool] = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

templates_path: list[str] = ["_templates"]
exclude_patterns: list[str] = ["_build", "Thumbs.db", ".DS_Store"]

# Furo tem alternância automática claro/escuro nativa.
html_theme = "furo"

html_theme_options: dict[str, str | bool | dict[str, str]] = {
    "sidebar_hide_name": False,
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

html_static_path: list[str] = ["_static"]
