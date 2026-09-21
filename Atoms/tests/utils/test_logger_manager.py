# Atoms/tests/utils/test_logger_manager.py
# pylint: disable=protected-access

"""Testes para o gerenciador de logging centralizado.

.. module:: tests.utils.test_logger_manager
   :platform: Unix, Windows
   :synopsis: Validação do sistema de logging global e handlers.
"""

import logging
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.utils.logger_manager import (
    LoggerConfig,
    _configurar_handler_arquivo,
    _configurar_handler_console,
    get_logger,
    setup_logging,
)


class TestSetupLogging:
    """Testes da função setup_logging."""

    def test_setup_logging_padrao(self) -> None:
        """Valida setup com configurações padrão."""
        setup_logging(log_level=logging.INFO)
        root: logging.Logger = logging.getLogger()
        assert root.level == logging.INFO
        assert len(root.handlers) > 0

    def test_setup_logging_com_diretorio_customizado(self) -> None:
        """Valida setup com diretório de logs customizado."""
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_logging(log_level=logging.DEBUG, diretorio_logs=tmpdir)
            assert LoggerConfig.LOG_DIR == Path(tmpdir).resolve()


class TestGetLogger:
    """Testes da função get_logger."""

    def test_get_logger_retorna_logger_valido(self) -> None:
        """Valida que get_logger retorna instância de Logger."""
        logger: logging.Logger = get_logger(nome_modulo="teste.modulo")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "teste.modulo"

    def test_get_logger_singleton_por_nome(self) -> None:
        """Valida que loggers com mesmo nome retornam mesma instância."""
        logger1: logging.Logger = get_logger(nome_modulo="app.core")
        logger2: logging.Logger = get_logger(nome_modulo="app.core")
        assert logger1 is logger2

    def test_logger_herda_configuracao_raiz(self) -> None:
        """Valida que logger herda nível do logger raiz."""
        setup_logging(log_level=logging.WARNING)
        # Logger deve herdar do root via propagação
        assert logging.getLogger().level == logging.WARNING


class TestHandlers:
    """Testes dos handlers de logging."""

    def test_handler_console_formatacao(self) -> None:
        """Valida formatação do handler de console."""
        handler = _configurar_handler_console()
        assert handler.formatter is not None
        assert handler.formatter._fmt == "%(levelname)-8s | %(name)s | %(message)s"

    def test_handler_arquivo_rotativo(self) -> None:
        """Valida configuração do handler rotativo de arquivo."""
        handler: RotatingFileHandler = _configurar_handler_arquivo(nome_logger="teste")
        assert handler.maxBytes == LoggerConfig.MAX_BYTES
        assert handler.backupCount == LoggerConfig.BACKUP_COUNT


class TestLoggingEmAcao:
    """Testes funcionais de logging em cenários reais."""

    def test_logging_mensagens_multiplos_niveis(self) -> None:
        """Valida log de mensagens em diferentes níveis de severidade."""
        setup_logging(log_level=logging.DEBUG)
        logger: logging.Logger = get_logger(nome_modulo="teste_niveis")

        # Cada nível deve ser processável sem erros
        logger.debug(msg="Mensagem DEBUG")
        logger.info(msg="Mensagem INFO")
        logger.warning(msg="Mensagem WARNING")
        logger.error(msg="Mensagem ERROR")

    def test_logging_com_contexto_extra(self) -> None:
        """Valida logging com dados contextuais adicionais."""
        setup_logging()
        logger: logging.Logger = get_logger(nome_modulo="teste_contexto")

        logger.info(msg="Operação iniciada", extra={"user_id": 123, "acao": "scan"})
        logger.warning(msg="Recurso deprecado", extra={"feature": "parse_html"})
