# Atoms/tests/utils/test_logger_manager.py
# pylint: disable=protected-access,redefined-outer-name

"""Testes unitários para o gerenciador de logging (utils.logger_manager)."""

import logging
import logging.handlers
from collections.abc import Callable, Generator
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any, NoReturn

import pytest

from src.utils import logger_manager
from src.utils.logger_manager import (
    LoggerConfig,
    _criar_handler_arquivo,
    _criar_handler_console,
    _garantir_diretorio,
    _instalar_no_root,
    get_logger,
    setup_logging,
)

# ===========================================================================
# Constantes dos testes (evita PLR2004 / magic values)
# ===========================================================================
BACKUP_COUNT_PADRAO = 5
BACKUP_COUNT_CUSTOMIZADO = 10
HANDLERS_APOS_SETUP = 2  # console + arquivo
HANDLERS_LIXO_INJETADO = 3  # apenas para o teste de "limpa anteriores"
MAX_BYTES_PADRAO = 5 * 1024 * 1024


# ===========================================================================
# Fixtures
# ===========================================================================
@pytest.fixture(autouse=True)
def _preservar_root_logger() -> Generator[None, Any, None]:
    """Salva/restaura handlers, nível e nome do root logger entre testes.

    Sem isto, um teste que chama setup_logging() deixa handlers abertos e
    afeta os outros testes de logging da suíte.
    """
    root: logging.Logger = logging.getLogger()
    estado: tuple[list[logging.Handler], int, str] = (list(root.handlers), root.level, root.name)

    yield

    for h in root.handlers:
        h.close()
    root.handlers.clear()
    root.handlers.extend(estado[0])
    root.setLevel(estado[1])


@pytest.fixture
def config_tmp(tmp_path: Path) -> LoggerConfig:
    """LoggerConfig apontando para tmp_path — sem tocar em ~/logs."""
    return LoggerConfig(
        log_dir=tmp_path / "logs",
        log_level=logging.DEBUG,
        max_bytes=1024,
        backup_count=2,
    )


# ===========================================================================
# LoggerConfig
# ===========================================================================
class TestLoggerConfig:
    """Contrato da dataclass LoggerConfig: frozen + defaults + customização."""

    def test_e_frozen(self, config_tmp: LoggerConfig) -> None:
        """Atribuir a um campo da dataclass levanta ``FrozenInstanceError``."""
        with pytest.raises(expected_exception=FrozenInstanceError):
            config_tmp.log_level = logging.ERROR  # type: ignore[misc]

    def test_defaults_razoaveis(self) -> None:
        """Valores default seguem o esperado (INFO, 5 MB, 5 backups, ``logs``)."""
        c = LoggerConfig()
        assert c.log_level == logging.INFO
        assert c.max_bytes == MAX_BYTES_PADRAO
        assert c.backup_count == BACKUP_COUNT_PADRAO
        assert c.log_dir.name == "logs"

    def test_aceita_customizacao(self, tmp_path: Path) -> None:
        """Campos passados no construtor sobrescrevem os defaults."""
        c = LoggerConfig(
            log_dir=tmp_path,
            log_level=logging.WARNING,
            backup_count=BACKUP_COUNT_CUSTOMIZADO,
        )
        assert c.log_dir == tmp_path
        assert c.log_level == logging.WARNING
        assert c.backup_count == BACKUP_COUNT_CUSTOMIZADO


# ===========================================================================
# _garantir_diretorio
# ===========================================================================
class TestGarantirDiretorio:
    """Criação idempotente de diretório + propagação de OSError."""

    def test_cria_diretorio_inexistente(self, tmp_path: Path) -> None:
        """Cria diretórios aninhados e devolve o caminho final."""
        alvo: Path = tmp_path / "a" / "b" / "logs"

        resultado: Path = _garantir_diretorio(diretorio=alvo)

        assert resultado == alvo
        assert alvo.is_dir()

    def test_aceita_diretorio_existente(self, tmp_path: Path) -> None:
        """Chamar sobre diretório já existente é idempotente."""
        alvo: Path = tmp_path / "ja-existe"
        alvo.mkdir()

        assert _garantir_diretorio(alvo) == alvo

    def test_propaga_oserror_com_contexto(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Erros de ``mkdir`` viram ``OSError`` com contexto e causa preservada."""

        def mkdir_que_falha(*_args: Any, **_kwargs: Any) -> NoReturn:
            raise OSError("permissão negada")

        monkeypatch.setattr(Path, "mkdir", mkdir_que_falha)
        alvo: Path = tmp_path / "sem-permissao"

        with pytest.raises(expected_exception=OSError) as exc_info:
            _garantir_diretorio(alvo)

        assert str(alvo) in str(exc_info.value)
        assert "Falha ao criar diretório de logs" in str(exc_info.value)
        # preserva a causa original (raise ... from erro)
        assert isinstance(exc_info.value.__cause__, OSError)


# ===========================================================================
# _criar_handler_arquivo
# ===========================================================================
class TestCriarHandlerArquivo:
    """Handler rotativo: tipo, nome do arquivo, diretório, config, formatter."""

    def test_retorna_rotating_file_handler(self, config_tmp: LoggerConfig) -> None:
        """Devolve uma instância de ``RotatingFileHandler``."""
        handler: logging.handlers.RotatingFileHandler = _criar_handler_arquivo(
            nome_logger="meu_logger", config=config_tmp
        )

        try:
            assert isinstance(handler, logging.handlers.RotatingFileHandler)
        finally:
            handler.close()

    def test_usa_nome_do_logger_no_arquivo(self, config_tmp: LoggerConfig) -> None:
        """O nome do logger vira ``<nome>.log`` dentro do diretório configurado."""
        handler: logging.handlers.RotatingFileHandler = _criar_handler_arquivo(
            nome_logger="minha_app", config=config_tmp
        )
        try:
            assert handler.baseFilename == str(config_tmp.log_dir / "minha_app.log")
        finally:
            handler.close()

    def test_cria_diretorio_se_ausente(self, tmp_path: Path) -> None:
        """O diretório de log é criado automaticamente se não existir."""
        config = LoggerConfig(log_dir=tmp_path / "nao-existe")
        handler: logging.handlers.RotatingFileHandler = _criar_handler_arquivo(
            nome_logger="x", config=config
        )
        try:
            assert config.log_dir.is_dir()
        finally:
            handler.close()

    def test_respeita_max_bytes_e_backup_count(self, config_tmp: LoggerConfig) -> None:
        """Repassa ``max_bytes`` e ``backup_count`` da configuração para o handler."""
        handler: logging.handlers.RotatingFileHandler = _criar_handler_arquivo(
            nome_logger="app", config=config_tmp
        )
        try:
            assert handler.maxBytes == config_tmp.max_bytes
            assert handler.backupCount == config_tmp.backup_count
        finally:
            handler.close()

    def test_respeita_level_e_encoding(self, config_tmp: LoggerConfig) -> None:
        """Configura ``level`` e ``encoding='utf-8'`` no handler."""
        handler: logging.handlers.RotatingFileHandler = _criar_handler_arquivo(
            nome_logger="app", config=config_tmp
        )
        try:
            assert handler.level == config_tmp.log_level
            assert handler.encoding == "utf-8"
        finally:
            handler.close()

    def test_formatter_usa_format_detalhado(self, config_tmp: LoggerConfig) -> None:
        """Formatter usa o formato detalhado e o date_format da configuração."""
        handler: logging.handlers.RotatingFileHandler = _criar_handler_arquivo(
            nome_logger="app", config=config_tmp
        )
        try:
            assert handler.formatter is not None
            assert handler.formatter._fmt == config_tmp.format_detalhado
            assert handler.formatter.datefmt == config_tmp.date_format
        finally:
            handler.close()


# ===========================================================================
# _criar_handler_console
# ===========================================================================
class TestCriarHandlerConsole:
    """Handler de console: StreamHandler (não FileHandler) + formato simples."""

    def test_retorna_stream_handler(self, config_tmp: LoggerConfig) -> None:
        """Devolve ``StreamHandler`` (e não ``FileHandler``)."""
        handler = _criar_handler_console(config=config_tmp)
        try:
            assert isinstance(handler, logging.StreamHandler)
            assert not isinstance(handler, logging.FileHandler)
        finally:
            handler.close()

    def test_level_e_formatter(self, config_tmp: LoggerConfig) -> None:
        """Aplica ``level`` e o formato simples da configuração."""
        handler = _criar_handler_console(config_tmp)
        try:
            assert handler.level == config_tmp.log_level
            assert handler.formatter is not None
            assert handler.formatter._fmt == config_tmp.format_simples
        finally:
            handler.close()


# ===========================================================================
# _instalar_no_root
# ===========================================================================
class TestInstalarNoRoot:
    """Instalação no logger raiz: level, handlers, limpeza de handlers antigos."""

    def test_define_level_do_root(self, config_tmp: LoggerConfig) -> None:
        """Aplica o ``log_level`` da configuração ao root logger."""
        _instalar_no_root(config=config_tmp)

        assert logging.getLogger().level == config_tmp.log_level

    def test_adiciona_exatamente_dois_handlers(self, config_tmp: LoggerConfig) -> None:
        """Instala exatamente um handler de arquivo e um de console."""
        _instalar_no_root(config=config_tmp)

        handlers: list[logging.Handler] = logging.getLogger().handlers
        assert len(handlers) == HANDLERS_APOS_SETUP
        assert any(isinstance(h, logging.handlers.RotatingFileHandler) for h in handlers)
        assert any(
            isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
            for h in handlers
        )

    def test_limpa_handlers_anteriores(self, config_tmp: LoggerConfig) -> None:
        """Descarta handlers preexistentes antes de instalar os novos."""
        root: logging.Logger = logging.getLogger()
        # O pytest instala seus próprios handlers no root: usar baseline relativo.
        baseline: int = len(root.handlers)
        for _ in range(HANDLERS_LIXO_INJETADO):
            root.addHandler(logging.NullHandler())
        assert len(root.handlers) == baseline + HANDLERS_LIXO_INJETADO

        _instalar_no_root(config_tmp)

        assert len(root.handlers) == HANDLERS_APOS_SETUP


# ===========================================================================
# setup_logging — API pública
# ===========================================================================
class TestSetupLogging:
    """Bootstrap: diretório customizado, ~, default, level, idempotência."""

    def test_usa_diretorio_customizado_com_path(self, tmp_path: Path) -> None:
        """Aceita ``Path`` e cria o arquivo de log no diretório informado."""
        alvo: Path = tmp_path / "logs-custom"

        setup_logging(log_level=logging.WARNING, diretorio_logs=alvo)

        assert alvo.is_dir()
        assert (alvo / "neutron_star.log").exists()

    def test_usa_diretorio_customizado_com_str(self, tmp_path: Path) -> None:
        """Aceita ``str`` como diretório de logs e cria o diretório."""
        alvo: Path = tmp_path / "logs-str"

        setup_logging(diretorio_logs=str(alvo))

        assert alvo.is_dir()

    def test_expande_til_e_resolve(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """``~`` é expandido via ``Path.expanduser`` antes de criar o diretório."""
        chamado: dict = {}

        original: Callable[..., Path] = Path.expanduser

        def fake_expanduser(self: Path) -> Path:
            chamado["expanduser"] = self
            return original(self)

        monkeypatch.setattr(Path, "expanduser", fake_expanduser)
        monkeypatch.setenv("HOME", str(tmp_path))

        setup_logging(diretorio_logs="~/meus-logs")

        assert "expanduser" in chamado
        assert (tmp_path / "meus-logs").is_dir()

    def test_sem_diretorio_usa_default(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Sem ``diretorio_logs``, usa o diretório padrão do módulo."""
        # redireciona o default para tmp_path
        monkeypatch.setattr(
            logger_manager,
            "_diretorio_padrao",
            lambda: tmp_path / "default-logs",
        )

        setup_logging()

        assert (tmp_path / "default-logs" / "neutron_star.log").exists()

    def test_aplica_log_level_no_root(self, tmp_path: Path) -> None:
        """Propaga ``log_level`` para o root logger."""
        setup_logging(log_level=logging.CRITICAL, diretorio_logs=tmp_path / "l")

        assert logging.getLogger().level == logging.CRITICAL

    def test_chamada_repetida_nao_duplica_handlers(self, tmp_path: Path) -> None:
        """Chamar ``setup_logging`` duas vezes não acumula handlers no root."""
        setup_logging(diretorio_logs=tmp_path / "l1")
        setup_logging(diretorio_logs=tmp_path / "l2")

        assert len(logging.getLogger().handlers) == HANDLERS_APOS_SETUP


# ===========================================================================
# get_logger — API pública
# ===========================================================================
class TestGetLogger:
    """Registry do stdlib: mesma instância por nome, herança de level, escrita."""

    def test_retorna_logger_do_stdlib(self) -> None:
        """Devolve instância de ``logging.Logger`` com o nome informado."""
        logger: logging.Logger = get_logger("meu.modulo")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "meu.modulo"

    def test_mesmo_nome_retorna_mesma_instancia(self) -> None:
        """Nomes iguais resolvem para a mesma instância (registry do stdlib)."""
        a = get_logger("x.y")
        b = get_logger("x.y")

        assert a is b

    def test_nomes_distintos_retornam_instancias_distintas(self) -> None:
        """Nomes diferentes devolvem instâncias distintas."""
        a = get_logger("a")
        b = get_logger("b")

        assert a is not b

    def test_logger_herda_level_do_root(self, tmp_path: Path) -> None:
        """O ``effective level`` sobe a hierarquia até o root configurado."""
        setup_logging(log_level=logging.ERROR, diretorio_logs=tmp_path / "l")
        logger = get_logger("herda")

        # effective level sobe pela hierarquia até o root
        assert logger.getEffectiveLevel() == logging.ERROR

    def test_logger_escreve_no_arquivo_configurado(self, tmp_path: Path) -> None:
        """Mensagens emitidas chegam ao arquivo de log configurado."""
        setup_logging(log_level=logging.INFO, diretorio_logs=tmp_path / "l")
        logger = get_logger("teste.escrita")

        logger.info("mensagem de teste")

        # flush manual dos handlers para garantir escrita em disco
        for h in logging.getLogger().handlers:
            h.flush()
        conteudo = (tmp_path / "l" / "neutron_star.log").read_text(encoding="utf-8")
        assert "mensagem de teste" in conteudo
        assert "teste.escrita" in conteudo


# ===========================================================================
# Contrato do módulo
# ===========================================================================
class TestContratoDoModulo:
    """Congela a API pública do módulo: __all__ e privados não exportados."""

    def test_all_publico(self) -> None:
        """``__all__`` expõe exatamente as três entradas públicas."""
        assert logger_manager.__all__ == [
            "LoggerConfig",
            "get_logger",
            "setup_logging",
        ]

    def test_helpers_privados_nao_vazam(self) -> None:
        """Helpers privados existem mas não estão em ``__all__``."""
        for nome in (
            "_garantir_diretorio",
            "_criar_handler_arquivo",
            "_criar_handler_console",
            "_instalar_no_root",
            "_diretorio_padrao",
        ):
            assert nome not in logger_manager.__all__
            assert hasattr(logger_manager, nome)
