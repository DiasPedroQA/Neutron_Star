"""Testes do parser, do despacho e dos comandos da interface CLI."""

import json
from argparse import Namespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from src.controllers.cli_controller import CLIController
from src.models.excecoes import DiretorioInexistenteError, PathInseguroError


def _informacoes_sistema() -> dict[str, Any]:
    """Cria dados de ambiente para os testes de saída da CLI."""
    return {
        "so": "Linux (6.1)",
        "usuario": "ana",
        "pasta_home": "/home/ana",
        "atalhos_sugeridos": [],
    }


def _resultado_escanear() -> dict[str, Any]:
    """Cria resultado vazio e válido para exercitar a saída do escaneamento."""
    return {
        "caminho_varrido": "/home/ana",
        "extensao_usada": ".html",
        "profundidade_usada": 5,
        "total_arquivos": 0,
        "total_elegiveis": 0,
        "tamanho_total_mb": 0.0,
        "data_busca": "01/01/2026 00:00:00",
        "arquivos": [],
        "tree": [],
    }


class TestCLIController:
    """Contrato dos comandos, códigos de saída e apresentação de resultados."""

    def test_criar_parser_interpreta_comandos_e_padrao(self) -> None:
        """Reconhece sistema, escanear e converter com seus argumentos padrão."""
        parser = CLIController.criar_parser()

        sistema = parser.parse_args(["sistema", "--json"])
        escanear = parser.parse_args(["escanear", "--caminho", "/home/ana"])
        converter = parser.parse_args(["converter", "a.html"])

        assert sistema.comando == "sistema"
        assert sistema.saida_json is True
        assert (escanear.caminho, escanear.extensao, escanear.profundidade) == (
            "/home/ana",
            ".html",
            5,
        )
        assert (converter.arquivos, converter.formato, converter.saida) == (
            ["a.html"],
            "json",
            None,
        )

    def test_executar_comando_sistema_em_json(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Imprime JSON válido e retorna código zero no caminho feliz."""
        servico: MagicMock = MagicMock()
        servico.obter_info_sistema.return_value = _informacoes_sistema()
        monkeypatch.setattr(CLIController, "servico", servico)

        codigo: int = CLIController.executar_comando_sistema(Namespace(saida_json=True))

        assert codigo == 0
        assert json.loads(capsys.readouterr().out) == _informacoes_sistema()

    def test_executar_comando_sistema_retorna_erro_no_stderr(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Retorna código um e mensagem de erro quando o serviço falha."""
        servico: MagicMock = MagicMock()
        servico.obter_info_sistema.side_effect = RuntimeError("falha simulada")
        monkeypatch.setattr(CLIController, "servico", servico)

        codigo: int = CLIController.executar_comando_sistema(Namespace(saida_json=False))
        captura = capsys.readouterr()

        assert codigo == 1
        assert "falha simulada" in captura.err

    def test_executar_comando_escanear_imprime_json(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Serializa o resumo e repassa os três parâmetros ao serviço."""
        esperado: dict[str, Any] = _resultado_escanear()
        servico: MagicMock = MagicMock()
        servico.escanear.return_value = esperado
        monkeypatch.setattr(CLIController, "servico", servico)
        args = Namespace(caminho="/home/ana", extensao=".htm", profundidade=2, saida_json=True)

        codigo: int = CLIController.executar_comando_escanear(args)

        assert codigo == 0
        assert json.loads(capsys.readouterr().out) == esperado
        servico.escanear.assert_called_once_with(
            caminho_str="/home/ana",
            extensao=".htm",
            profundidade=2,
        )

    @pytest.mark.parametrize(
        ("erro", "mensagem"),
        [
            pytest.param(PathInseguroError("/etc"), "Acesso Proibido", id="path-inseguro"),
            pytest.param(
                DiretorioInexistenteError("/ausente"), "Diretório Não Encontrado", id="ausente"
            ),
            pytest.param(RuntimeError("falha"), "Erro durante o escaneamento", id="inesperado"),
        ],
    )
    def test_executar_comando_escanear_formata_erros(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
        erro: Exception,
        mensagem: str,
    ) -> None:
        """Retorna código um e direciona erros de escaneamento para stderr."""
        servico: MagicMock = MagicMock()
        servico.escanear.side_effect = erro
        monkeypatch.setattr(CLIController, "servico", servico)

        codigo: int = CLIController.executar_comando_escanear(
            Namespace(caminho="/home/ana", extensao=".html", profundidade=5, saida_json=False)
        )

        assert codigo == 1
        assert mensagem in capsys.readouterr().err

    def test_executar_comando_converter_consume_progresso(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Consome o gerador de eventos, mostra progresso e retorna sucesso."""
        evento: dict[str, Any] = {
            "progresso": 100,
            "arquivo_atual": "",
            "arquivos_convertidos": [],
            "erros": [],
            "concluido": True,
            "sucesso": True,
        }
        servico: MagicMock = MagicMock()
        servico.converter_com_progresso.return_value = iter([evento])
        monkeypatch.setattr(CLIController, "servico", servico)

        codigo: int = CLIController.executar_comando_converter(
            Namespace(arquivos=["a.html"], formato="json", saida=None)
        )

        assert codigo == 0
        assert "Conversão finalizada com sucesso" in capsys.readouterr().out
        servico.converter_com_progresso.assert_called_once_with(
            arquivos_selecionados=["a.html"],
            extensao_destino="json",
            pasta_saida=None,
        )

    def test_executar_comando_converter_trata_path_inseguro(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Traduz bloqueio de caminho em código de saída um e mensagem localizada."""
        servico: MagicMock = MagicMock()
        servico.converter_com_progresso.side_effect = PathInseguroError("/etc")
        monkeypatch.setattr(CLIController, "servico", servico)

        codigo: int = CLIController.executar_comando_converter(
            Namespace(arquivos=["/etc/a.html"], formato="json", saida=None)
        )

        assert codigo == 1
        assert "Acesso Proibido" in capsys.readouterr().err

    def test_executar_comando_converter_retorna_erro_para_lote_parcial(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Não anuncia sucesso quando o evento final informa falhas por arquivo."""
        servico: MagicMock = MagicMock()
        servico.converter_com_progresso.return_value = iter(
            [
                {
                    "progresso": 100,
                    "arquivo_atual": "",
                    "arquivos_convertidos": [],
                    "erros": [{"arquivo": "a.html", "erro": "falha"}],
                    "concluido": True,
                    "sucesso": False,
                }
            ]
        )
        monkeypatch.setattr(CLIController, "servico", servico)

        codigo = CLIController.executar_comando_converter(
            Namespace(arquivos=["a.html"], formato="json", saida=None)
        )

        assert codigo == 1
        assert "finalizada com falhas" in capsys.readouterr().err

    @pytest.mark.parametrize(
        ("comando", "metodo"),
        [
            pytest.param("sistema", "executar_comando_sistema", id="sistema"),
            pytest.param("escanear", "executar_comando_escanear", id="escanear"),
            pytest.param("converter", "executar_comando_converter", id="converter"),
        ],
    )
    def test_main_despacha_para_o_comando_selecionado(
        self, monkeypatch: pytest.MonkeyPatch, comando: str, metodo: str
    ) -> None:
        """Delega o comando parseado ao método correspondente."""
        monkeypatch.setattr(CLIController, metodo, classmethod(lambda cls, args: 7))

        assert CLIController.main([comando, *(["a.html"] if comando == "converter" else [])]) == 7

    def test_main_parser_rejeita_comando_ausente(self) -> None:
        """Mantém argparse responsável por informar a ausência de subcomando."""
        with pytest.raises(SystemExit) as contexto:
            CLIController.main([])

        assert contexto.value.code == 2
