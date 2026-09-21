# Atoms/src/adaptadores/api.py
# pylint: disable=broad-exception-caught

"""Módulo de adaptador de API HTTP baseada em Flask Blueprint."""

import json
from collections.abc import Generator
from typing import Any

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    request,
    stream_with_context,
)

from src.dominio.entidades import InfoSistema, ResultadoEscaneamento, StatusConversao
from src.dominio.excecoes import DiretorioInexistenteError, PathInseguroError
from src.infra.conteiner import conteiner

from .schemas import ValidadorRequisicao

# Criação do Blueprint de API para registro modular no Flask
api_bp = Blueprint(name="api", import_name=__name__)


@api_bp.route(rule="/api/sistema", methods=["GET"])
def obter_sistema() -> tuple[Response, int]:
    """Retorna informações ambientais e atalhos de pastas do S.O."""
    try:
        dados: InfoSistema = conteiner.obter_info_sistema_use_case.executar()
        return jsonify(dados), 200
    except Exception as e:
        current_app.logger.exception(msg="Erro ao ler dados do sistema")
        return jsonify({"erro": f"Erro interno do servidor: {e!s}"}), 500


@api_bp.route(rule="/api/escanear", methods=["GET"])
def escanear_pasta() -> tuple[Response, int]:
    """Varre um diretório na Home do usuário em busca de arquivos HTML."""
    caminho: str = request.args.get(key="caminho", default="~/")
    extensao: str = request.args.get(key="extensao", default=".html")

    # Converte profundidade com fallback defensivo
    try:
        profundidade: int = int(request.args.get(key="profundidade", default="5"))
    except (ValueError, TypeError):
        profundidade = 5

    try:
        dados: ResultadoEscaneamento = conteiner.escanear_diretorio_use_case.executar(
            caminho_str=caminho,
            extensao=extensao,
            profundidade=profundidade,
        )
        return jsonify(dados), 200
    except PathInseguroError as e:
        current_app.logger.exception(msg="Ataque Path Traversal bloqueado")
        return jsonify({"erro": str(e)}), 403
    except DiretorioInexistenteError as e:
        return jsonify({"erro": str(e)}), 404
    except Exception as e:
        current_app.logger.exception(msg=f"Erro durante varredura de '{caminho}'")
        return jsonify({"erro": f"Falha no escaneamento: {e!s}"}), 500


@api_bp.route(rule="/api/processar", methods=["POST"])
def processar_lote() -> Response | tuple[Response, int]:
    """Processa lote de arquivos enviando progresso em tempo real por SSE."""
    payload: dict[str, Any] = request.get_json() or {}

    # Validação do Schema de Entrada na porta de API
    sucesso, msg_erro = ValidadorRequisicao.validar_processamento_lote(dados=payload)
    if not sucesso:
        return jsonify({"erro": msg_erro}), 400

    arquivos: list[str] = payload.get("arquivos_selecionados", [])
    extensao: str = payload.get("extensao_destino", "json")
    pasta_saida: str | None = payload.get("pasta_saida") or None

    def gerar_progresso_sse() -> Generator[str, None, None]:
        """Função geradora para transmissão de eventos SSE (data: {JSON}\\n\\n)."""
        try:
            gerador_use_case: Generator[StatusConversao, None, None] = (
                conteiner.converter_favoritos_use_case.executar_com_progresso(
                    arquivos_selecionados=arquivos,
                    extensao_destino=extensao,
                    pasta_saida=pasta_saida,
                )
            )
            for status in gerador_use_case:
                yield f"data: {json.dumps(status)}\n\n"
        except Exception as e:
            current_app.logger.exception(msg="Erro crítico no stream de processamento")
            erro_payload: dict[str, str] = {"erro": f"Erro crítico no pipeline: {e!s}"}
            yield f"data: {json.dumps(erro_payload)}\n\n"

    return Response(
        response=stream_with_context(generator_or_function=gerar_progresso_sse()),
        mimetype="text/event-stream",
    )
