# Atoms/main.py

"""Módulo de inicialização e ponto de entrada (Entrypoint) do App Neutron Star.

Execução: ``python main.py`` a partir da pasta ``Atoms/`` ou ``flask --app main run``.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask

from src.controllers.api_controller import api_bp
from src.utils.logger_manager import get_logger, setup_logging

RAIZ_APP: Path = Path(__file__).resolve().parent

logger: logging.Logger = get_logger(nome_modulo=__name__)


def criar_aplicacao(diretorio_logs: Path | None = None) -> Flask:
    """Fábrica de software para inicializar e configurar o servidor Flask.

    Args:
        diretorio_logs: Pasta dos logs. Por padrão, ``Atoms/logs``. Injetável para
            que os testes nunca escrevam no diretório real do projeto.
    """
    pasta_logs: Path = diretorio_logs if diretorio_logs is not None else RAIZ_APP / "logs"
    setup_logging(diretorio_logs=pasta_logs)
    logger.info(msg="Aplicação Neutron Star iniciando...")

    app: Flask = Flask(
        import_name=__name__,
        template_folder=str(RAIZ_APP / "src" / "views" / "templates"),
        static_folder=str(RAIZ_APP / "src" / "views" / "static"),
    )

    # Logger de auditoria rotativo (somente ERROR ou acima)
    caminho_log: Path = pasta_logs / "erros_servidor.txt"
    caminho_log.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        filename=str(caminho_log),
        maxBytes=1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(level=logging.ERROR)
    file_handler.setFormatter(
        fmt=logging.Formatter(
            fmt="[%(asctime)s] %(levelname)s em %(module)s: %(message)s",
            datefmt="%d/%m/%Y %H:%M:%S",
        )
    )
    # No logger RAIZ: os controllers usam get_logger(__name__), que não passa por app.logger.
    logging.getLogger().addHandler(hdlr=file_handler)

    app.register_blueprint(blueprint=api_bp)

    logger.info(msg="Aplicação configurada com sucesso no padrão MVC.")
    return app


if __name__ == "__main__":
    app_flask: Flask = criar_aplicacao()
    debug_ativo: bool = os.environ.get("FLASK_DEBUG") == "1"

    print("=" * 65)
    print("🚀 SISTEMA NEUTRON STAR INICIADO EM PADRÃO MVC")
    print("=" * 65)
    print("Acesse o painel local no navegador: http://127.0.0.1:5000")
    print(f"📁 Logs em: {RAIZ_APP / 'logs'}")
    print("=" * 65)

    app_flask.run(host="127.0.0.1", port=5000, debug=debug_ativo)
