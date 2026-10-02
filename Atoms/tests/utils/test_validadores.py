# Atoms/tests/adaptadores/test_schemas.py
# pylint: disable=protected-access, too-many-public-methods

"""Testes unitários para os schemas de validação de payload (adaptadores.schemas)."""

from typing import Any

import pytest

from src.utils.validadores import FORMATOS_VALIDOS, ValidadorRequisicao

# from adaptadores.schemas import FORMATOS_VALIDOS, ValidadorRequisicao


# ===========================================================================
# _validar_arquivos
# ===========================================================================
class TestValidarArquivos:
    """Cobre as ramificações do helper estático _validar_arquivos."""

    @pytest.mark.parametrize(
        ("arquivos", "mensagem_esperada"),
        [
            pytest.param(
                None,
                "O campo 'arquivos_selecionados' é obrigatório.",
                id="none-obrigatorio",
            ),
            pytest.param(
                "caminho/para/arquivo.csv",
                "O campo 'arquivos_selecionados' deve ser uma lista.",
                id="string-no-lugar-de-lista",
            ),
            pytest.param(
                {"arquivo": "a.csv"},
                "O campo 'arquivos_selecionados' deve ser uma lista.",
                id="dict-no-lugar-de-lista",
            ),
            pytest.param(
                42,
                "O campo 'arquivos_selecionados' deve ser uma lista.",
                id="int-no-lugar-de-lista",
            ),
            pytest.param(
                (),
                "O campo 'arquivos_selecionados' deve ser uma lista.",
                id="tupla-nao-e-lista",
            ),
            pytest.param(
                [],
                "A lista de arquivos selecionados não pode estar vazia.",
                id="lista-vazia",
            ),
            pytest.param(
                ["a.csv", 123],
                "Todos os caminhos na lista de arquivos devem ser válidos.",
                id="item-nao-string",
            ),
            pytest.param(
                ["a.csv", None],
                "Todos os caminhos na lista de arquivos devem ser válidos.",
                id="item-none",
            ),
            pytest.param(
                ["a.csv", ""],
                "Todos os caminhos na lista de arquivos devem ser válidos.",
                id="item-string-vazia",
            ),
            pytest.param(
                ["a.csv", "   "],
                "Todos os caminhos na lista de arquivos devem ser válidos.",
                id="item-so-espacos",
            ),
            pytest.param(
                ["a.csv", "\t\n"],
                "Todos os caminhos na lista de arquivos devem ser válidos.",
                id="item-so-whitespace",
            ),
        ],
    )
    def test_retorna_mensagem_para_entrada_invalida(
        self, arquivos: Any, mensagem_esperada: str
    ) -> None:
        resultado = ValidadorRequisicao._validar_arquivos(arquivos)

        assert resultado == mensagem_esperada

    @pytest.mark.parametrize(
        "arquivos",
        [
            pytest.param(["a.csv"], id="um-arquivo"),
            pytest.param(["a.csv", "b.json"], id="dois-arquivos"),
            pytest.param(["  a.csv  "], id="com-espacos-nas-bordas"),
            pytest.param(["/abs/path/a.csv"], id="caminho-absoluto"),
            pytest.param(["sem/extensao"], id="sem-extensao-e-aceito"),
        ],
    )
    def test_retorna_none_para_entrada_valida(self, arquivos: list[str]) -> None:
        assert ValidadorRequisicao._validar_arquivos(arquivos) is None


# ===========================================================================
# _validar_extensao
# ===========================================================================
class TestValidarExtensao:
    """Cobre as ramificações do helper estático _validar_extensao."""

    @pytest.mark.parametrize(
        ("extensao", "mensagem_esperada"),
        [
            pytest.param(
                None,
                "O campo 'extensao_destino' é obrigatório.",
                id="none-obrigatorio",
            ),
            pytest.param(
                123,
                "O campo 'extensao_destino' deve ser uma string.",
                id="int-nao-e-string",
            ),
            pytest.param(
                ["csv"],
                "O campo 'extensao_destino' deve ser uma string.",
                id="lista-nao-e-string",
            ),
            pytest.param(
                {"ext": "csv"},
                "O campo 'extensao_destino' deve ser uma string.",
                id="dict-nao-e-string",
            ),
            pytest.param(
                "",
                "Formato de destino inválido. Escolha apenas 'csv' ou 'json'.",
                id="string-vazia",
            ),
            pytest.param(
                "   ",
                "Formato de destino inválido. Escolha apenas 'csv' ou 'json'.",
                id="string-so-espacos",
            ),
            pytest.param(
                "xml",
                "Formato de destino inválido. Escolha apenas 'csv' ou 'json'.",
                id="formato-nao-suportado-xml",
            ),
            pytest.param(
                "xlsx",
                "Formato de destino inválido. Escolha apenas 'csv' ou 'json'.",
                id="formato-nao-suportado-xlsx",
            ),
            pytest.param(
                "cs v",
                "Formato de destino inválido. Escolha apenas 'csv' ou 'json'.",
                id="espaco-no-meio",
            ),
        ],
    )
    def test_retorna_mensagem_para_entrada_invalida(
        self, extensao: Any, mensagem_esperada: str
    ) -> None:
        assert ValidadorRequisicao._validar_extensao(extensao) == mensagem_esperada

    @pytest.mark.parametrize(
        "extensao",
        [
            pytest.param("csv", id="csv-minusculo"),
            pytest.param("CSV", id="csv-maiusculo"),
            pytest.param("Csv", id="csv-misto"),
            pytest.param("json", id="json-minusculo"),
            pytest.param("JSON", id="json-maiusculo"),
            pytest.param(".csv", id="csv-com-ponto"),
            pytest.param(".json", id="json-com-ponto"),
            pytest.param("  csv  ", id="csv-com-espacos"),
            pytest.param("  .JSON  ", id="json-maiusculo-ponto-espacos"),
        ],
    )
    def test_retorna_none_para_extensao_valida(self, extensao: str) -> None:
        assert ValidadorRequisicao._validar_extensao(extensao) is None


# ===========================================================================
# validar_processamento_lote — API pública
# ===========================================================================
class TestValidarProcessamentoLoteSucesso:
    """Caminho feliz do método público."""

    @pytest.mark.parametrize(
        ("payload", "id_do_caso"),
        [
            (
                {"arquivos_selecionados": ["a.csv"], "extensao_destino": "json"},
                "minimo-valido",
            ),
            (
                {
                    "arquivos_selecionados": ["a.csv", "b.txt", "c.html"],
                    "extensao_destino": "csv",
                },
                "multiplos-arquivos",
            ),
            (
                {
                    "arquivos_selecionados": ["a.csv"],
                    "extensao_destino": ".JSON",
                },
                "extensao-normalizada-com-ponto-maiusculo",
            ),
            (
                {
                    "arquivos_selecionados": ["a.csv"],
                    "extensao_destino": "  CSV  ",
                    "campo_extra": "ignorado",
                },
                "campos-extras-sao-ignorados",
            ),
        ],
    )
    def test_retorna_true_e_string_vazia(self, payload: dict[str, Any], id_do_caso: str) -> None:
        resultado = ValidadorRequisicao.validar_processamento_lote(payload)

        assert resultado == (True, "")
        assert id_do_caso  # silencia "unused" se alguém remover o param


class TestValidarProcessamentoLotePayloadInvalido:
    """Payload que nem é um dict."""

    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param(None, id="none"),
            pytest.param([], id="lista-vazia"),
            pytest.param(["a.csv"], id="lista-com-item"),
            pytest.param("string", id="string"),
            pytest.param(42, id="int"),
            pytest.param(True, id="bool"),
            pytest.param((), id="tupla"),
        ],
    )
    def test_retorna_false_para_payload_nao_dict(self, payload: Any) -> None:
        sucesso, mensagem = ValidadorRequisicao.validar_processamento_lote(payload)

        assert sucesso is False
        assert mensagem == "O payload da requisição deve ser um objeto JSON."


class TestValidarProcessamentoLoteErrosDelegados:
    """Erros propagados dos helpers — confirma ordem de validação."""

    @pytest.mark.parametrize(
        ("payload", "mensagem_esperada"),
        [
            pytest.param(
                {"extensao_destino": "csv"},
                "O campo 'arquivos_selecionados' é obrigatório.",
                id="arquivos-ausente",
            ),
            pytest.param(
                {"arquivos_selecionados": None, "extensao_destino": "csv"},
                "O campo 'arquivos_selecionados' é obrigatório.",
                id="arquivos-none",
            ),
            pytest.param(
                {"arquivos_selecionados": "a.csv", "extensao_destino": "csv"},
                "O campo 'arquivos_selecionados' deve ser uma lista.",
                id="arquivos-nao-e-lista",
            ),
            pytest.param(
                {"arquivos_selecionados": [], "extensao_destino": "csv"},
                "A lista de arquivos selecionados não pode estar vazia.",
                id="arquivos-lista-vazia",
            ),
            pytest.param(
                {"arquivos_selecionados": ["a.csv", ""], "extensao_destino": "csv"},
                "Todos os caminhos na lista de arquivos devem ser válidos.",
                id="arquivos-item-vazio",
            ),
            pytest.param(
                {"arquivos_selecionados": ["a.csv"]},
                "O campo 'extensao_destino' é obrigatório.",
                id="extensao-ausente",
            ),
            pytest.param(
                {"arquivos_selecionados": ["a.csv"], "extensao_destino": None},
                "O campo 'extensao_destino' é obrigatório.",
                id="extensao-none",
            ),
            pytest.param(
                {"arquivos_selecionados": ["a.csv"], "extensao_destino": 123},
                "O campo 'extensao_destino' deve ser uma string.",
                id="extensao-nao-e-string",
            ),
            pytest.param(
                {"arquivos_selecionados": ["a.csv"], "extensao_destino": "xml"},
                "Formato de destino inválido. Escolha apenas 'csv' ou 'json'.",
                id="extensao-invalida",
            ),
        ],
    )
    def test_propaga_mensagem_do_helper(
        self, payload: dict[str, Any], mensagem_esperada: str
    ) -> None:
        sucesso, mensagem = ValidadorRequisicao.validar_processamento_lote(payload)

        assert sucesso is False
        assert mensagem == mensagem_esperada

    def test_valida_arquivos_antes_de_extensao(self) -> None:
        """Ordem importa: se ambos estão errados, o erro de arquivos vem primeiro."""
        payload = {
            "arquivos_selecionados": [],
            "extensao_destino": "xml",
        }

        sucesso, mensagem = ValidadorRequisicao.validar_processamento_lote(payload)

        assert sucesso is False
        assert "arquivos selecionados não pode estar vazia" in mensagem


class TestValidarProcessamentoLoteRetorno:
    """Contrato do retorno (tupla de 2, tipos corretos)."""

    def test_retorno_e_tupla_de_dois_elementos(self) -> None:
        resultado: tuple[bool, str] = ValidadorRequisicao.validar_processamento_lote(
            dados={"arquivos_selecionados": ["a.csv"], "extensao_destino": "csv"}
        )
        resultado_esperado = 2

        assert isinstance(resultado, tuple)
        assert len(resultado) == resultado_esperado

    def test_sucesso_retorna_string_vazia_nao_none(self) -> None:
        _, mensagem = ValidadorRequisicao.validar_processamento_lote(
            {"arquivos_selecionados": ["a.csv"], "extensao_destino": "csv"}
        )

        assert mensagem == ""
        assert mensagem is not None


# ===========================================================================
# Contrato da classe / módulo
# ===========================================================================
class TestContratoDoModulo:
    """Docstring para TestContratoDoModulo"""

    def test_formatos_validos_contem_apenas_csv_e_json(self) -> None:
        assert FORMATOS_VALIDOS == {"csv", "json"}

    def test_helpers_sao_estaticos(self) -> None:
        assert isinstance(ValidadorRequisicao.__dict__["_validar_arquivos"], staticmethod)
        assert isinstance(ValidadorRequisicao.__dict__["_validar_extensao"], staticmethod)

    def test_metodo_publico_e_classmethod(self) -> None:
        assert isinstance(ValidadorRequisicao.__dict__["validar_processamento_lote"], classmethod)

    def test_pode_ser_chamado_via_instancia(self) -> None:
        validador = ValidadorRequisicao()

        sucesso, mensagem = validador.validar_processamento_lote(
            {"arquivos_selecionados": ["a.csv"], "extensao_destino": "csv"}
        )

        assert (sucesso, mensagem) == (True, "")
