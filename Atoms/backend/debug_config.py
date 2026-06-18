# Atoms/backend/debug_config.py

import json
import logging
import logging.config
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, TextIO

DEFAULT_CONFIG: dict[str, Any] = {
    "global_level": "INFO",
    "modules": {},
    "output": {"console": True},
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "flags": {},
}

_config: dict[str, Any] = {}
_flags: dict[str, Any] = {}


def load_debug_config(config_path: str = "debug_config.json") -> dict[str, Any]:
    """Carrega configuração de debug do JSON, mesclando com defaults."""
    if not os.path.exists(path=config_path):
        print(f"Arquivo {config_path} não encontrado, usando defaults.")
        return DEFAULT_CONFIG.copy()

    try:
        with open(file=config_path, mode="r", encoding="utf-8") as f:
            user_config: dict[str, Any] = json.load(fp=f)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Erro ao ler {config_path}: {e}. Usando defaults.")
        return DEFAULT_CONFIG.copy()

    # Merge raso (ajuste se precisar de deep merge)
    merged: dict[str, Any] = DEFAULT_CONFIG.copy()
    merged |= user_config
    return merged


def setup_logging(config: dict[str, Any]) -> None:
    """Aplica a configuração ao logger raiz e aos módulos."""
    global _config, _flags  # pylint: disable=global-statement
    _config = config
    _flags = config.get("flags", {})

    level: Any | int = getattr(logging, config["global_level"].upper(), logging.INFO)
    root: logging.Logger = logging.getLogger()
    root.setLevel(level)

    # Remove handlers existentes para evitar duplicação (cuidado em hot reload)
    for handler in root.handlers[:]:
        root.removeHandler(hdlr=handler)

    formatter = logging.Formatter(fmt=config["format"])

    # Console
    if config["output"].get("console", True):
        ch: logging.StreamHandler[TextIO] = logging.StreamHandler()
        ch.setFormatter(formatter)
        root.addHandler(ch)

    # Arquivo
    if "file" in config["output"]:
        log_dir: Path = os.path.dirname(config["output"]["file"])
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(name=log_dir, exist_ok=True)

        fh = RotatingFileHandler(
            filename=config["output"]["file"],
            maxBytes=config["output"].get("file_max_bytes", 10 * 1024 * 1024),
            backupCount=config["output"].get("file_backup_count", 5),
        )
        fh.setFormatter(formatter)
        root.addHandler(fh)

    # Ajuste por módulo
    for module_name, module_level in config.get("modules", {}).items():
        logging.getLogger(module_name).setLevel(
            getattr(logging, module_level.upper(), logging.INFO)
        )


def get_flag(flag_name: str, default: bool = False) -> bool:
    """Retorna o valor de uma flag customizada."""
    return bool(_flags.get(flag_name, default))


# Opcional: inicialize com defaults se ninguém chamar setup_logging
if not _config:
    _config = DEFAULT_CONFIG.copy()
    _flags = _config["flags"]
