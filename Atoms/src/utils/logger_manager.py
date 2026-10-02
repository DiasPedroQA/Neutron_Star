# Atoms/src/utils/logger_manager.py
# pylint: disable=too-few-public-methods

"""Gerenciador centralizado de logging para a aplicação Neutron Star."""

import logging
import logging.handlers
from dataclasses import dataclass, field
from pathlib import Path

__all__: list[str] = ["LoggerConfig", "get_logger", "setup_logging"]


def _diretorio_padrao() -> Path:
    """Diretório default de logs: <raiz-do-projeto>/logs."""
    return Path(__file__).parent.parent.parent / "logs"


@dataclass(frozen=True)
class LoggerConfig:
    """Configuração imutável do sistema de logging.

    Attributes:
        log_dir: Diretório onde os arquivos de log serão gravados.
        log_level: Nível mínimo de severidade (logging.DEBUG, INFO, ...).
        max_bytes: Tamanho máximo de cada arquivo antes de rotacionar.
        backup_count: Quantos arquivos rotacionados manter.
        date_format: Formato de timestamp nos logs.
        format_detalhado: Formato usado no handler de arquivo.
        format_simples: Formato usado no handler de console.
    """

    log_dir: Path = field(default_factory=_diretorio_padrao)
    log_level: int = logging.INFO
    max_bytes: int = 5 * 1024 * 1024
    backup_count: int = 5
    date_format: str = "%d/%m/%Y %H:%M:%S"
    format_detalhado: str = (
        "[%(asctime)s] %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    )
    format_simples: str = "%(levelname)-8s | %(name)s | %(message)s"


def _garantir_diretorio(diretorio: Path) -> Path:
    """Garante que o diretório existe; cria recursivamente se preciso.

    Raises:
        OSError: Se não for possível criar o diretório.
    """
    try:
        diretorio.mkdir(parents=True, exist_ok=True)
    except OSError as erro:
        raise OSError(f"Falha ao criar diretório de logs em '{diretorio}': {erro}") from erro
    return diretorio


def _criar_handler_arquivo(
    nome_logger: str, config: LoggerConfig
) -> logging.handlers.RotatingFileHandler:
    """Cria handler rotativo apontando para `<config.log_dir>/<nome_logger>.log`."""
    _garantir_diretorio(config.log_dir)
    caminho = config.log_dir / f"{nome_logger}.log"

    handler = logging.handlers.RotatingFileHandler(
        filename=str(caminho),
        maxBytes=config.max_bytes,
        backupCount=config.backup_count,
        encoding="utf-8",
    )
    handler.setLevel(config.log_level)
    handler.setFormatter(logging.Formatter(fmt=config.format_detalhado, datefmt=config.date_format))
    return handler


def _criar_handler_console(config: LoggerConfig) -> logging.StreamHandler:
    """Cria handler de console (stdout) com formato compacto."""
    handler = logging.StreamHandler()
    handler.setLevel(config.log_level)
    handler.setFormatter(logging.Formatter(fmt=config.format_simples, datefmt=config.date_format))
    return handler


def _instalar_no_root(config: LoggerConfig) -> None:
    """Limpa handlers anteriores e instala os dois novos no logger raiz."""
    root = logging.getLogger()
    root.setLevel(config.log_level)
    root.handlers.clear()
    root.addHandler(_criar_handler_console(config))
    root.addHandler(_criar_handler_arquivo("neutron_star", config))


def setup_logging(
    log_level: int = logging.INFO,
    diretorio_logs: Path | str | None = None,
) -> None:
    """Configura o logging global da aplicação.

    Deve ser chamada uma única vez no bootstrap.

    Args:
        log_level: Nível mínimo de severidade.
        diretorio_logs: Caminho customizado. Se None, usa o default.
    """
    config = LoggerConfig(
        log_dir=Path(diretorio_logs).expanduser().resolve()
        if diretorio_logs
        else _diretorio_padrao(),
        log_level=log_level,
    )
    _instalar_no_root(config)


def get_logger(nome_modulo: str) -> logging.Logger:
    """Retorna o logger nomeado para o módulo.

    Delega ao registry do stdlib: chamadas com o mesmo nome retornam
    a mesma instância; o logger herda o nível do root após `setup_logging`.
    """
    return logging.getLogger(nome_modulo)
