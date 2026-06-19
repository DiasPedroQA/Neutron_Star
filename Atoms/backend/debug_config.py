# Atoms/backend/debug_config.py

"""Carregamento e aplicação da configuração de debug via JSON."""

from __future__ import annotations

import json
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import TextIO, TypedDict, cast


# ── Tipos que descrevem a estrutura do JSON de debug ──────────────


class DebugOutputConfig(TypedDict, total=False):
    """Configuração dos canais de saída."""

    console: bool
    file: str
    file_max_bytes: int
    file_backup_count: int


class DebugConfig(TypedDict):
    """Estrutura completa da configuração de debug."""

    global_level: str
    # módulo → nível (ex.: 'infra.parser': 'DEBUG')
    modules: dict[str, str]
    output: DebugOutputConfig
    format: str
    flags: dict[str, bool]  # flags customizadas (sempre booleanas)


# ── Valores padrão (fallback) ────────────────────────────────────

DEFAULT_CONFIG: DebugConfig = {
    "global_level": "INFO",
    "modules": {},
    "output": {"console": True},
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "flags": {},
}

# ── Estado global inicializado com os defaults ────────────────────

_config: DebugConfig = DEFAULT_CONFIG.copy()
_flags: dict[str, bool] = _config["flags"]


# ── Funções públicas ──────────────────────────────────────────────


def load_debug_config(config_path: str = "outputs/debug_config.json") -> DebugConfig:
    """Carrega configuração de debug do JSON, mesclando com defaults.

    Args:
        config_path: Caminho para o arquivo JSON de configuração.

    Returns:
        Um dicionário tipado com a configuração mesclada.
    """
    if not os.path.exists(path=config_path):
        print(f"Arquivo {config_path} não encontrado, usando defaults.")
        return DEFAULT_CONFIG.copy()

    try:
        with open(file=config_path, mode="r", encoding="utf-8") as f:
            user_config: dict = json.load(f)  # Any apenas aqui, controlado
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Erro ao ler {config_path}: {e}. Usando defaults.")
        return DEFAULT_CONFIG.copy()

    # Merge raso – sobrescreve apenas as chaves presentes no user_config
    merged: DebugConfig = DEFAULT_CONFIG.copy()
    # type: ignore[typeddict-item]  # confiamos na estrutura
    merged.update(user_config)
    return cast(DebugConfig, merged)


def setup_logging(config: DebugConfig) -> None:
    """Aplica a configuração ao logger raiz e aos módulos.

    Args:
        config: Configuração completa, já mesclada com defaults.
    """
    global _config, _flags  # pylint: disable=global-statement
    _config = config
    _flags = config.get("flags", {})

    # Nível global
    level_name: str = config["global_level"].upper()
    level: int = cast(int, getattr(logging, level_name, logging.INFO))
    root: logging.Logger = logging.getLogger()
    root.setLevel(level)

    # Remove handlers existentes
    for handler in root.handlers[:]:
        root.removeHandler(hdlr=handler)

    formatter = logging.Formatter(fmt=config["format"])

    # Console
    if config["output"].get("console", True):
        console_handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
        console_handler.setFormatter(fmt=formatter)
        root.addHandler(hdlr=console_handler)

    # Arquivo (rotativo)
    if "file" in config["output"]:
        _processar_arquivo(config=config, formatter=formatter, root=root)
    # Ajuste por módulo
    modules: dict[str, str] = config.get("modules", {})
    for module_name, module_level in modules.items():
        lvl: int = cast(int, getattr(logging, module_level.upper(), logging.INFO))
        logging.getLogger(name=module_name).setLevel(level=lvl)


def _processar_arquivo(config, formatter, root) -> None:
    file_path: str = config["output"]["file"]
    log_dir: str = os.path.dirname(p=file_path)
    if log_dir and not os.path.exists(path=log_dir):
        os.makedirs(name=log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=file_path,
        maxBytes=config["output"].get("file_max_bytes", 10 * 1024 * 1024),
        backupCount=config["output"].get("file_backup_count", 5),
    )
    file_handler.setFormatter(fmt=formatter)
    root.addHandler(hdlr=file_handler)


def get_flag(flag_name: str, default: bool = False) -> bool:
    """Retorna o valor de uma flag customizada (sempre booleano)."""
    return _flags.get(flag_name, default)
