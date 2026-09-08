"""Módulo de inicialização e ponto de entrada (Entrypoint) do App Neutron Star."""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, render_template

from src.adaptadores.api import api_bp


def criar_aplicacao() -> Flask:
    """Fábrica de software para inicializar e configurar o servidor Flask.

    Configura os caminhos dinâmicos das telas, registra as rotas da API,
    inicializa o gravador rotativo de logs e define a rota de entrega da UI.

    Não há proteção CSRF: a aplicação não usa sessão nem autenticação baseada
    em cookies, então não existe uma sessão autenticada para ser forjada — o
    CSRF protegeria contra um ataque que não se aplica a este design de API
    JSON stateless (ver README, seção de exemplo de requisição via curl).
    """
    # Define os caminhos físicos baseados no diretório deste arquivo
    raiz_app: Path = Path(__file__).parent.resolve()
    pasta_templates: Path = raiz_app / "src" / "templates"

    app = Flask(
        import_name=__name__,
        template_folder=str(pasta_templates),
        static_folder=str(raiz_app / "src" / "static"),
    )

    # 1. Configuração do Logger de Auditoria Rotativo (.txt)
    # Grava até 1MB por arquivo e mantém um histórico de até 3 arquivos
    caminho_log: Path = raiz_app / "erros_servidor.txt"
    file_handler = RotatingFileHandler(
        filename=str(caminho_log), maxBytes=1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(level=logging.ERROR)
    formatador = logging.Formatter(
        "[%(asctime)s] %(levelname)s em %(module)s: %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )
    file_handler.setFormatter(fmt=formatador)
    app.logger.addHandler(hdlr=file_handler)

    # 2. Registro do Blueprint modular da API HTTP
    app.register_blueprint(blueprint=api_bp)

    # 3. Rota de entrega da Interface de Usuário (SPA)
    @app.route(rule="/", methods=["GET"])
    def index() -> str:
        """Renderiza a página principal do aplicativo de favoritos."""
        return render_template(template_name_or_list="index.html")

    return app


if __name__ == "__main__":
    app_flask: Flask = criar_aplicacao()

    # Só ativa o depurador interativo se a variável FLASK_DEBUG for '1'
    debug_ativo: bool = os.environ.get("FLASK_DEBUG") == "1"

    print("=" * 65)
    print("🚀 SISTEMA NEUTRON STAR INICIADO COM ARQUITETURA HEXAGONAL")
    print("=" * 65)
    print("Acesse o painel local no navegador: http://127.0.0.1:5000")
    print("=" * 65)

    app_flask.run(host="127.0.0.1", port=5000, debug=debug_ativo)
