# Atoms/src/controllers/api_controller.py
# pylint: disable=broad-exception-caught

"""Controller de rotas Web e streaming SSE via Flask."""

import http
import json
import logging
from collections.abc import Generator
from typing import Any

from flask import (
    Blueprint,
    Response,
    jsonify,
    render_template,
    request,
    stream_with_context,
)

from ..models.conversor import ConversorService
from ..models.entidades import InfoSistema, ResultadoEscaneamento, StatusConversao
from ..models.excecoes import DiretorioInexistenteError, PathInseguroError
from ..utils.logger_manager import get_logger
from ..utils.validadores import ValidadorRequisicao

api_bp = Blueprint(name="api", import_name=__name__)
logger: logging.Logger = get_logger(nome_modulo=__name__)
servico = ConversorService()


@api_bp.route(rule="/", methods=["GET"])
def index() -> str:
    """Renderiza a interface Web principal."""
    return render_template(template_name_or_list="index.html")


@api_bp.route(rule="/api/sistema", methods=["GET"])
def obter_info_sistema() -> tuple[Response, int]:
    """Retorna dados do sistema operacional e atalhos rápidos."""
    try:
        dados: InfoSistema = servico.obter_info_sistema()
        return jsonify(dados), http.HTTPStatus.OK
    except Exception as erro:
        logger.error("Erro ao obter dados do sistema: %s", erro)
        return (
            jsonify({"erro": "Falha ao obter informações do sistema."}),
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@api_bp.route(rule="/api/escanear", methods=["GET"])
def escanear_pasta() -> tuple[Response, int]:
    """Executa a varredura de diretórios em busca de arquivos HTML elegíveis."""
    caminho: str = request.args.get("caminho", "~/")
    extensao: str = request.args.get("extensao", ".html")
    profundidade_param: str = request.args.get("profundidade", "5")

    try:
        profundidade: int = int(profundidade_param)
    except ValueError:
        profundidade = 5

    try:
        dados: ResultadoEscaneamento = servico.escanear(
            caminho_str=caminho,
            extensao=extensao,
            profundidade=profundidade,
        )
        return jsonify(dados), http.HTTPStatus.OK
    except PathInseguroError as erro:
        return jsonify({"erro": str(erro)}), http.HTTPStatus.FORBIDDEN
    except DiretorioInexistenteError as erro:
        return jsonify({"erro": str(erro)}), http.HTTPStatus.NOT_FOUND
    except Exception as erro:
        logger.error("Erro durante varredura de '%s': %s", caminho, erro)
        return (
            jsonify({"erro": "Falha no escaneamento do diretório."}),
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@api_bp.route("/api/processar", methods=["POST"])
def processar_lote() -> Response | tuple[Response, int]:
    """Endpoint SSE para conversão em lote com streaming reativo de progresso."""
    dados_requisicao: Any = request.get_json(silent=True)
    valido, mensagem_erro = ValidadorRequisicao.validar_processamento_lote(dados=dados_requisicao)

    if not valido:
        return jsonify({"erro": mensagem_erro}), http.HTTPStatus.BAD_REQUEST

    arquivos: list[str] = dados_requisicao.get("arquivos_selecionados", [])
    extensao_destino: str = dados_requisicao.get("extensao_destino", "json")
    pasta_saida: str | None = dados_requisicao.get("pasta_saida")

    def gerar_eventos() -> Generator[str, None, None]:
        try:
            gerador: Generator[StatusConversao, None, None] = servico.converter_com_progresso(
                arquivos_selecionados=arquivos,
                extensao_destino=extensao_destino,
                pasta_saida=pasta_saida,
            )
            for status in gerador:
                yield f"data: {json.dumps(status, ensure_ascii=False)}\n\n"
        except Exception as erro:
            logger.error("Erro crítico no fluxo SSE: %s", erro)
            evento_falha: StatusConversao = {
                "progresso": 100,
                "arquivo_atual": "",
                "arquivos_convertidos": [],
                "erros": [{"arquivo": "geral", "erro": str(erro)}],
                "concluido": True,
                "sucesso": False,
            }
            yield f"data: {json.dumps(evento_falha, ensure_ascii=False)}\n\n"

    return Response(
        stream_with_context(gerar_eventos()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
