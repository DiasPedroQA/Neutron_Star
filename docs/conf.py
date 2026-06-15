"""Configuração do Sphinx para a documentação do Neutron Star."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(".."))  # aponta para a raiz do projeto


project = "Neutron Star"
author = "Pedro Dias"
language = "pt_BR"

extensions: list[str] = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_typehints = "description"
templates_path: list[str] = ["_templates"]
exclude_patterns: list[str] = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "alabaster"
