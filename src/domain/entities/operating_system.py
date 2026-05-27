"""Módulo que define a entidade do sistema operacional."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OperateSystemModel:
    """Representa informações do sistema operacional."""

    name: str  # ex.: 'Linux', 'Windows', 'Darwin'
    version: str  # ex.: '#1 SMP...', '10.0.19042'
    release: str  # ex.: '5.15.0-91-generic', '10', '21.6.0'
    machine: str  # ex.: 'x86_64', 'AMD64'
    user_path: Path  # ex.: '/home/user' ou 'C:\\Users\\user'
