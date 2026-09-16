"""Gerenciador centralizado de logging para a aplicação Neutron Star.

.. module:: src.utils.logger_manager
   :platform: Unix, Windows
   :synopsis: Sistema de logging estruturado e resiliente.

Este módulo fornece:
- Logger singleton global para toda a aplicação
- Suporte a múltiplos handlers (console, arquivo, formatação)
- Integração com Flask para captura de eventos
- Rastreamento contextual de operações

.. doctest::

    >>> logger = get_logger("meu_modulo")
    >>> logger.info("Operação iniciada", extra={"user_id": 123})
    >>> logger.warning("Recurso deprecado", extra={"feature": "parse_html"})
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Any

__all__ = ["get_logger", "setup_logging"]


class LoggerConfig:
    """Configuração centralizada do sistema de logging.

    Attributes:
        LOG_DIR (Path): Diretório para armazenar logs de arquivo.
        LOG_LEVEL (int): Nível mínimo de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        MAX_BYTES (int): Tamanho máximo de cada arquivo de log antes de rotacionar (5MB).
        BACKUP_COUNT (int): Número máximo de arquivos de log a manter (5 backups).
        DATE_FORMAT (str): Formato de timestamp em logs (dia/mês/ano hora:minuto:segundo).
        FORMAT_DETALHADO (str): Padrão Sphinx-compatível com contexto completo.
        FORMAT_SIMPLES (str): Padrão compacto para console (sem contexto de módulo).
    """

    LOG_DIR: Path = Path(__file__).parent.parent.parent / "logs"
    LOG_LEVEL: int = logging.INFO
    MAX_BYTES: int = 5 * 1024 * 1024  # 5 MB
    BACKUP_COUNT: int = 5
    DATE_FORMAT: str = "%d/%m/%Y %H:%M:%S"

    # Formato detalhado para arquivo de log (Sphinx-style docstring)
    FORMAT_DETALHADO: str = (
        "[%(asctime)s] %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    )

    # Formato compacto para console
    FORMAT_SIMPLES: str = "%(levelname)-8s | %(name)s | %(message)s"


def _criar_diretorio_logs() -> Path:
    """Garante que o diretório de logs existe, criando se necessário.

    Returns:
        Path: Caminho absoluto do diretório de logs.

    Raises:
        OSError: Se o diretório não puder ser criado (permissões insuficientes).
    """
    try:
        LoggerConfig.LOG_DIR.mkdir(parents=True, exist_ok=True)
        return LoggerConfig.LOG_DIR
    except OSError as erro:
        raise OSError(
            f"Falha ao criar diretório de logs em '{LoggerConfig.LOG_DIR}': {erro}"
        ) from erro


def _configurar_handler_arquivo(nome_logger: str) -> logging.handlers.RotatingFileHandler:
    """Cria e configura handler rotativo para arquivo de log.

    Args:
        nome_logger (str): Nome do logger (define o nome do arquivo).

    Returns:
        logging.handlers.RotatingFileHandler: Handler configurado pronto para uso.

    Note:
        Os arquivos são nomeados em formato: `{nome_logger}.log`
        Quando atinge MAX_BYTES, rotaciona para `{nome_logger}.log.1`, etc.
    """
    dir_logs = _criar_diretorio_logs()
    caminho_arquivo = dir_logs / f"{nome_logger}.log"

    handler = logging.handlers.RotatingFileHandler(
        filename=str(caminho_arquivo),
        maxBytes=LoggerConfig.MAX_BYTES,
        backupCount=LoggerConfig.BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(LoggerConfig.LOG_LEVEL)
    formatter = logging.Formatter(
        fmt=LoggerConfig.FORMAT_DETALHADO,
        datefmt=LoggerConfig.DATE_FORMAT,
    )
    handler.setFormatter(formatter)

    return handler


def _configurar_handler_console() -> logging.StreamHandler:
    """Cria e configura handler para saída em console.

    Returns:
        logging.StreamHandler: Handler configurado para stdout.

    Note:
        Usa formato compacto (FORMAT_SIMPLES) para melhor legibilidade no terminal.
    """
    handler = logging.StreamHandler()
    handler.setLevel(LoggerConfig.LOG_LEVEL)
    formatter = logging.Formatter(
        fmt=LoggerConfig.FORMAT_SIMPLES,
        datefmt=LoggerConfig.DATE_FORMAT,
    )
    handler.setFormatter(formatter)

    return handler


def setup_logging(
    log_level: int = logging.INFO,
    diretorio_logs: Path | str | None = None,
) -> None:
    """Configura o sistema de logging global da aplicação.

    Esta função deve ser chamada uma única vez, preferencialmente no bootstrap
    da aplicação (ex: no `criar_aplicacao()` do Flask).

    Args:
        log_level (int): Nível mínimo de severidade dos logs.
                        Padrão: logging.INFO.
        diretorio_logs (Path | str | None): Caminho customizado para armazenar logs.
                                            Se None, usa LoggerConfig.LOG_DIR.

    Example:
        >>> from src.utils.logger_manager import setup_logging
        >>> setup_logging(log_level=logging.DEBUG)
    """
    if diretorio_logs:
        LoggerConfig.LOG_DIR = Path(diretorio_logs).expanduser().resolve()

    LoggerConfig.LOG_LEVEL = log_level

    # Configura o logger raiz do Python
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Limpa handlers anteriores para evitar duplicação
    root_logger.handlers.clear()

    # Adiciona handlers
    root_logger.addHandler(_configurar_handler_console())
    root_logger.addHandler(_configurar_handler_arquivo("neutron_star"))


def get_logger(nome_modulo: str) -> logging.Logger:
    """Obtém uma instância de logger configurada para um módulo específico.

    Esta função implementa o padrão singleton para loggers, garantindo que
    cada módulo tenha sua própria instância nomeada hierarquicamente.

    Args:
        nome_modulo (str): Nome do módulo (geralmente __name__).
                          Exemplo: "src.aplicacao.casos_uso"

    Returns:
        logging.Logger: Logger configurado pronto para uso.

    Example:
        >>> from src.utils.logger_manager import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Iniciando processamento", extra={"arquivo": "dados.html"})
        >>> logger.error("Falha na leitura", extra={"erro_code": 404})

    Note:
        O logger herda a configuração do logger raiz. Se setup_logging() não
        foi chamado previamente, a configuração padrão será usada.
    """
    logger = logging.getLogger(nome_modulo)
    return logger


def configurar_logger_flask(app: Any) -> None:
    """Integra o sistema de logging com aplicação Flask.

    Configura o logger da aplicação Flask para usar o sistema centralizado,
    garantindo consistência entre logs da aplicação e logs do framework.

    Args:
        app: Instância da aplicação Flask (flask.Flask).

    Example:
        >>> from flask import Flask
        >>> from src.utils.logger_manager import configurar_logger_flask, setup_logging
        >>> setup_logging()
        >>> app = Flask(__name__)
        >>> configurar_logger_flask(app)
    """
    app.logger = get_logger("flask.app")


if __name__ == "__main__":
    # Teste rápido do sistema de logging
    setup_logging(log_level=logging.DEBUG)
    logger = get_logger("teste")
    logger.debug("Mensagem de DEBUG")
    logger.info("Mensagem de INFO")
    logger.warning("Mensagem de WARNING")
    logger.error("Mensagem de ERROR")
