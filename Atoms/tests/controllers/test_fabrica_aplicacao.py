# Atoms/tests/controllers/test_fabrica_aplicacao.py

"""Testes da fábrica ``criar_aplicacao``: wiring, isolamento e trilha de auditoria de erros."""

import logging
from pathlib import Path

from flask import Flask

from main import criar_aplicacao
from src.utils.logger_manager import get_logger


def test_fabrica_registra_blueprint_da_api(app: Flask) -> None:
    """A aplicação criada expõe as rotas REST e a interface web."""
    rotas: set[str] = {regra.rule for regra in app.url_map.iter_rules()}

    assert {"/", "/api/sistema", "/api/escanear", "/api/processar"} <= rotas


def test_fabrica_cria_logs_apenas_no_diretorio_informado(tmp_path: Path) -> None:
    """Dado um diretório de logs explícito, nada deve ser gravado fora dele."""
    destino: Path = tmp_path / "meus-logs"

    criar_aplicacao(diretorio_logs=destino)

    assert (destino / "erros_servidor.txt").exists()
    assert (destino / "neutron_star.log").exists()


def test_erro_logado_por_qualquer_modulo_chega_ao_arquivo_de_auditoria(tmp_path: Path) -> None:
    """Regressão: ``erros_servidor.txt`` ficava sempre vazio porque só ouvia ``app.logger``.

    Os controllers usam ``get_logger(__name__)``, que não passa pelo logger do Flask.
    """
    destino: Path = tmp_path / "logs"
    criar_aplicacao(diretorio_logs=destino)

    get_logger(nome_modulo="src.controllers.api_controller").error("falha simulada %s", 42)
    for handler in logging.getLogger().handlers:
        handler.flush()

    conteudo: str = (destino / "erros_servidor.txt").read_text(encoding="utf-8")
    assert "falha simulada 42" in conteudo


def test_info_nao_polui_o_arquivo_de_auditoria_de_erros(tmp_path: Path) -> None:
    """O arquivo de auditoria registra somente ERROR ou acima."""
    destino: Path = tmp_path / "logs"
    criar_aplicacao(diretorio_logs=destino)

    get_logger(nome_modulo="src.qualquer").info("mensagem informativa")
    for handler in logging.getLogger().handlers:
        handler.flush()

    assert "mensagem informativa" not in (destino / "erros_servidor.txt").read_text(
        encoding="utf-8"
    )
