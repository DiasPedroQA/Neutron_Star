# backend/infrastructure/identifier.py

"""Módulo de identificação de um Sistema Operacional"""

import platform
from pathlib import Path

from Atoms.backend.core.entities import ModeloSistemaOperacional


def detectar_sistema_operacional() -> ModeloSistemaOperacional:
    """Detecta o sistema operacional atual."""

    return ModeloSistemaOperacional(
        nome_sistema=platform.system().lower(),
        versao_sistema=platform.release(),
        user_home=Path.home(),
    )
