# Atoms/backend/debug_config.py

"""Carregamento e aplicação da configuração de debug via JSON."""

from __future__ import annotations

import json
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import TextIO, TypedDict, cast

# Logger deste módulo – NullHandler evita warnings quando ainda não há handlers
logger: logging.Logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())


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
    logger.info("Tentando carregar configuração de debug de %s", config_path)

    if not os.path.exists(path=config_path):
        print(f"Arquivo {config_path} não encontrado, usando defaults.")
        logger.warning("Arquivo %s não encontrado, usando defaults.", config_path)
        return DEFAULT_CONFIG.copy()

    try:
        with open(file=config_path, mode="r", encoding="utf-8") as f:
            user_config: dict = json.load(fp=f)
        logger.debug("JSON carregado com sucesso: %s", user_config)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Erro ao ler {config_path}: {e}. Usando defaults.")
        logger.exception("Erro ao ler %s. Usando defaults.", config_path)
        return DEFAULT_CONFIG.copy()

    # Merge raso – sobrescreve apenas as chaves presentes no user_config
    merged: DebugConfig = DEFAULT_CONFIG.copy()
    merged.update(user_config)  # type: ignore[typeddict-item]
    logger.info("Configuração mesclada com defaults: %s", merged)
    return cast(DebugConfig, merged)


def setup_logging(config: DebugConfig) -> None:
    """Aplica a configuração ao logger raiz e aos módulos.

    Args:
        config: Configuração completa, já mesclada com defaults.
    """
    global _config, _flags  # pylint: disable=global-statement
    _config = config
    _flags = config.get("flags", {})

    logger.info("Aplicando configuração de debug: %s", config)

    # Nível global
    level_name: str = config["global_level"].upper()
    level: int = cast(int, getattr(logging, level_name, logging.INFO))
    root: logging.Logger = logging.getLogger()
    root.setLevel(level=level)
    logger.debug("Nível global definido para %s (%d)", level_name, level)

    # Remove handlers existentes
    for handler in root.handlers[:]:
        root.removeHandler(hdlr=handler)
    logger.debug("Handlers anteriores removidos")

    formatter = logging.Formatter(fmt=config["format"])

    # Console
    if config["output"].get("console", True):
        console_handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
        console_handler.setFormatter(fmt=formatter)
        root.addHandler(hdlr=console_handler)
        logger.debug("Handler de console adicionado")
    else:
        logger.debug("Console desativado na configuração")

    # Arquivo (rotativo)
    if "file" in config["output"]:
        _processar_arquivo(config=config, formatter=formatter, root=root)
    else:
        logger.debug("Nenhum arquivo de log configurado")

    # Ajuste por módulo
    modules: dict[str, str] = config.get("modules", {})
    for module_name, module_level in modules.items():
        lvl: int = cast(int, getattr(logging, module_level.upper(), logging.INFO))
        logging.getLogger(name=module_name).setLevel(level=lvl)
        logger.debug("Nível de %s definido para %s", module_name, module_level)

    logger.info("Configuração de debug aplicada com sucesso")


def _processar_arquivo(
    config: DebugConfig, formatter: logging.Formatter, root: logging.Logger
) -> None:
    output = config["output"]
    # Já sabemos que 'file' existe (chamada condicional), mas informamos o type checker
    if "file" not in output:
        logger.error("Tentativa de processar arquivo sem caminho definido.")
        return
    file_path: str = output["file"]
    log_dir: str = os.path.dirname(p=file_path)
    if log_dir and not os.path.exists(path=log_dir):
        os.makedirs(name=log_dir, exist_ok=True)
        logger.debug("Diretório de log criado: %s", log_dir)

    max_bytes: int = output.get("file_max_bytes", 10 * 1024 * 1024)

    backup_count: int = output.get("file_backup_count", 5)

    file_handler = RotatingFileHandler(
        filename=file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    file_handler.setFormatter(fmt=formatter)
    root.addHandler(hdlr=file_handler)
    logger.info(
        "Handler de arquivo configurado: %s (max %d bytes, %d backups)",
        file_path,
        max_bytes,
        backup_count,
    )


def get_flag(flag_name: str, default: bool = False) -> bool:
    """Retorna o valor de uma flag customizada (sempre booleano)."""
    value = _flags.get(flag_name, default)
    logger.debug("Flag '%s' consultada: %s (default=%s)", flag_name, value, default)
    return value
