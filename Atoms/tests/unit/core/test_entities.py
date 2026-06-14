# pylint: disable=redefined-outer-name

"""Testes unitários — Camada 1: entities (Atoms/backend/core/entidades).

Filosofia TDD aplicada aqui:
    - Cada teste cobre UM comportamento observável.
    - Zero I/O, zero disco, zero mocks — entidades puras.
    - Nome do teste = documentação viva do comportamento esperado.
    - Ordem de execução: ModeloArquivo → ModeloPasta → ModeloSistemaOperacional.

Ciclo Red-Green-Blue:
    Red   → rodar este arquivo antes de implementar e ver falhar pelo motivo certo.
    Green → implementar o mínimo nas entities para cada teste passar.
    Blue  → refatorar sem quebrar nenhum teste verde.

Avisos de tipagem intencionais:
    Alguns testes passam tipos errados propositalmente para verificar que a entity
    rejeita entradas inválidas. Esses casos usam `# type: ignore[arg-type]` para
    silenciar o mypy sem esconder o comportamento testado.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from Atoms.backend.core.entidades.entidade_arquivo import ModeloArquivo
from Atoms.backend.core.entidades.entidade_diretorio import ModeloPasta
from Atoms.backend.core.entidades.entidade_sistema_operacional import ModeloSistemaOperacional
from Atoms.backend.core.entidades.resultado_processamento import EstatisticasProcessamento, ResultadoProcessamento

# ===========================================================================
# Fixtures compartilhadas neste módulo
# Fixtures globais (usadas em múltiplas camadas) ficam em tests/conftest.py.
# Aqui ficam apenas as fixtures locais a este arquivo.
# ===========================================================================


@pytest.fixture()
def pasta_raiz(tmp_path: Path) -> ModeloPasta:
    """Retorna um ModeloPasta raiz sem pai para uso nos testes."""
    return ModeloPasta(nome_pasta="home", caminho_absoluto=tmp_path, pasta_pai=None)


@pytest.fixture()
def caminho_arquivo_html(tmp_path: Path) -> Path:
    """Retorna um caminho temporário para um arquivo HTML fictício."""
    return tmp_path / "bookmarks.html"


# ===========================================================================
# ModeloArquivo
# ===========================================================================


class TestModeloArquivoCreation:
    def test_cria_com_campos_validos(self, caminho_arquivo_html: Path) -> None:
        arq = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=caminho_arquivo_html,
            tamanho_arquivo_bytes=512,
            file_is_html=True,
        )

        assert arq.nome_arquivo == "bookmarks.html"
        assert arq.caminho_arquivo == caminho_arquivo_html
        assert arq.tamanho_arquivo_bytes == 512
        assert arq.file_is_html is True

    def test_cria_arquivo_nao_html(self, tmp_path: Path) -> None:
        arq = ModeloArquivo(
            nome_arquivo="dados.csv",
            caminho_arquivo=tmp_path / "dados.csv",
            tamanho_arquivo_bytes=256,
            file_is_html=False,
        )

        assert arq.file_is_html is False

    def test_tamanho_zero_e_valido(self, tmp_path: Path) -> None:
        arq = ModeloArquivo(
            nome_arquivo="vazio.html",
            caminho_arquivo=tmp_path / "vazio.html",
            tamanho_arquivo_bytes=0,
            file_is_html=True,
        )

        assert arq.tamanho_arquivo_bytes == 0


class TestModeloArquivoValidation:
    def test_nome_vazio_levanta_value_error(self, caminho_arquivo_html: Path) -> None:
        with pytest.raises(expected_exception=ValueError, match="nome"):
            ModeloArquivo(
                nome_arquivo="",
                caminho_arquivo=caminho_arquivo_html,
                tamanho_arquivo_bytes=100,
                file_is_html=True,
            )

    def test_nome_apenas_espacos_levanta_value_error(self, caminho_arquivo_html: Path) -> None:
        with pytest.raises(expected_exception=ValueError, match="nome"):
            ModeloArquivo(
                nome_arquivo="   ",
                caminho_arquivo=caminho_arquivo_html,
                tamanho_arquivo_bytes=100,
                file_is_html=True,
            )

    def test_nome_inconsistente_com_caminho_levanta_value_error(self, tmp_path: Path) -> None:
        with pytest.raises(expected_exception=ValueError, match="nome"):
            ModeloArquivo(
                nome_arquivo="outro_nome.html",
                caminho_arquivo=tmp_path / "bookmarks.html",
                tamanho_arquivo_bytes=100,
                file_is_html=True,
            )

    def test_tamanho_negativo_levanta_value_error(self, caminho_arquivo_html: Path) -> None:
        with pytest.raises(expected_exception=ValueError, match="tamanho"):
            ModeloArquivo(
                nome_arquivo="bookmarks.html",
                caminho_arquivo=caminho_arquivo_html,
                tamanho_arquivo_bytes=-1,
                file_is_html=True,
            )

    def test_caminho_relativo_levanta_value_error(self) -> None:
        with pytest.raises(expected_exception=ValueError, match="absoluto"):
            ModeloArquivo(
                nome_arquivo="bookmarks.html",
                caminho_arquivo=Path("relative/bookmarks.html"),
                tamanho_arquivo_bytes=100,
                file_is_html=True,
            )

    def test_nome_com_barras_levanta_value_error(self, tmp_path: Path) -> None:
        with pytest.raises(expected_exception=ValueError, match="barras"):
            ModeloArquivo(
                nome_arquivo="subdir/bookmarks.html",
                caminho_arquivo=tmp_path / "bookmarks.html",
                tamanho_arquivo_bytes=100,
                file_is_html=True,
            )

    def test_inferir_flag_html_de_suffix(self, tmp_path: Path) -> None:
        arq = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=tmp_path / "bookmarks.html",
            tamanho_arquivo_bytes=100,
            file_is_html=False,
        )

        assert arq.file_is_html is True


class TestModeloArquivoEquality:
    def test_igualdade_por_caminho(self, caminho_arquivo_html: Path) -> None:
        a = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=caminho_arquivo_html,
            tamanho_arquivo_bytes=100,
            file_is_html=True,
        )
        b = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=caminho_arquivo_html,
            tamanho_arquivo_bytes=100,
            file_is_html=True,
        )

        assert a == b

    def test_desigualdade_por_caminho_diferente(self, tmp_path: Path) -> None:
        a = ModeloArquivo(
            nome_arquivo="a.html",
            caminho_arquivo=tmp_path / "a.html",
            tamanho_arquivo_bytes=100,
            file_is_html=True,
        )
        b = ModeloArquivo(
            nome_arquivo="b.html",
            caminho_arquivo=tmp_path / "b.html",
            tamanho_arquivo_bytes=100,
            file_is_html=True,
        )

        assert a != b


# ===========================================================================
# ModeloPasta
# ===========================================================================


class TestModeloPastaCreation:
    def test_cria_pasta_raiz_sem_pai(self, pasta_raiz: ModeloPasta) -> None:
        assert pasta_raiz.nome_pasta == "home"
        assert pasta_raiz.caminho_absoluto.is_absolute()
        assert pasta_raiz.pasta_pai is None
        assert pasta_raiz.subpastas == []
        assert pasta_raiz.arquivos == []

    def test_cria_pasta_com_pai_inconsistente_levanta_value_error(self, tmp_path: Path) -> None:
        pai = ModeloPasta(nome_pasta="home", caminho_absoluto=tmp_path / "home", pasta_pai=None)

        with pytest.raises(expected_exception=ValueError, match="Pasta pai inconsistente"):
            ModeloPasta(
                nome_pasta="intruso",
                caminho_absoluto=tmp_path / "outro_lugar" / "intruso",
                pasta_pai=pai,
            )

    def test_nome_relativo_levanta_value_error(self) -> None:
        with pytest.raises(expected_exception=ValueError, match="absoluto"):
            ModeloPasta(
                nome_pasta="home",
                caminho_absoluto=Path("relative/home"),
            )

    def test_nome_com_barras_levanta_value_error(self, tmp_path: Path) -> None:
        with pytest.raises(expected_exception=ValueError, match="barras"):
            ModeloPasta(
                nome_pasta="sub/dir",
                caminho_absoluto=tmp_path / "sub",
            )

    def test_pasta_pai_invalido_levanta_type_error(self, tmp_path: Path) -> None:
        with pytest.raises(expected_exception=TypeError, match="pasta_pai"):
            ModeloPasta(
                nome_pasta="home",
                caminho_absoluto=tmp_path,
                pasta_pai="not-a-pasta",  # type: ignore[arg-type]
            )


class TestModeloPastaSubpastas:
    def test_adiciona_subpasta_valida(self, pasta_raiz: ModeloPasta, tmp_path: Path) -> None:
        sub = ModeloPasta(nome_pasta="Downloads", caminho_absoluto=tmp_path / "Downloads", pasta_pai=None)

        pasta_raiz.adicionar_subpasta(sub_pasta=sub)

        assert sub in pasta_raiz.subpastas
        assert sub.pasta_pai is pasta_raiz

    def test_adicionar_subpasta_duplicata_pelo_caminho_ignorada(self, pasta_raiz: ModeloPasta, tmp_path: Path) -> None:
        sub = ModeloPasta(nome_pasta="Downloads", caminho_absoluto=tmp_path / "Downloads", pasta_pai=None)

        pasta_raiz.adicionar_subpasta(sub_pasta=sub)
        pasta_raiz.adicionar_subpasta(sub_pasta=sub)

        assert pasta_raiz.subpastas.count(sub) == 1

    def test_subpasta_nao_pode_ser_si_mesma(self, pasta_raiz: ModeloPasta) -> None:
        with pytest.raises(expected_exception=ValueError, match="si mesma"):
            pasta_raiz.adicionar_subpasta(sub_pasta=pasta_raiz)

    def test_subpasta_com_outro_pai_levanta_value_error(self, pasta_raiz: ModeloPasta, tmp_path: Path) -> None:
        outro_pai = ModeloPasta(nome_pasta="outro", caminho_absoluto=tmp_path / "outro", pasta_pai=None)
        sub = ModeloPasta(
            nome_pasta="sub",
            caminho_absoluto=tmp_path / "outro" / "sub",
            pasta_pai=outro_pai,
        )

        with pytest.raises(expected_exception=ValueError, match="outro pai"):
            pasta_raiz.adicionar_subpasta(sub_pasta=sub)

    def test_subpasta_com_nome_duplicado_levanta_value_error(self, pasta_raiz: ModeloPasta, tmp_path: Path) -> None:
        sub_a = ModeloPasta(nome_pasta="Downloads", caminho_absoluto=tmp_path / "Downloads", pasta_pai=pasta_raiz)
        sub_b = ModeloPasta(nome_pasta="Downloads", caminho_absoluto=tmp_path / "Downloads_2", pasta_pai=None)

        pasta_raiz.adicionar_subpasta(sub_pasta=sub_a)

        with pytest.raises(expected_exception=ValueError, match="duplicado"):
            pasta_raiz.adicionar_subpasta(sub_pasta=sub_b)


class TestModeloPastaArquivos:
    def test_adiciona_arquivo_valido(self, pasta_raiz: ModeloPasta, caminho_arquivo_html: Path) -> None:
        arquivo = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=caminho_arquivo_html,
            tamanho_arquivo_bytes=128,
            file_is_html=True,
        )

        pasta_raiz.adicionar_arquivo(sub_arquivo=arquivo)

        assert arquivo in pasta_raiz.arquivos

    def test_adiciona_arquivo_duplicado_pelo_caminho_ignorado(self, pasta_raiz: ModeloPasta, caminho_arquivo_html: Path) -> None:
        arquivo = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=caminho_arquivo_html,
            tamanho_arquivo_bytes=128,
            file_is_html=True,
        )

        pasta_raiz.adicionar_arquivo(sub_arquivo=arquivo)
        pasta_raiz.adicionar_arquivo(sub_arquivo=arquivo)

        assert pasta_raiz.arquivos.count(arquivo) == 1

    def test_adicionar_arquivo_pai_inconsistente_levanta_value_error(self, pasta_raiz: ModeloPasta, tmp_path: Path) -> None:
        arquivo = ModeloArquivo(
            nome_arquivo="outro.html",
            caminho_arquivo=tmp_path / "other" / "outro.html",
            tamanho_arquivo_bytes=100,
            file_is_html=True,
        )

        with pytest.raises(expected_exception=ValueError, match="não está na pasta"):
            pasta_raiz.adicionar_arquivo(sub_arquivo=arquivo)

    def test_adicionar_arquivo_com_tipo_invalido_levanta_type_error(self, pasta_raiz: ModeloPasta) -> None:
        with pytest.raises(expected_exception=TypeError):
            pasta_raiz.adicionar_arquivo(sub_arquivo="nao é arquivo")  # type: ignore[arg-type]


class TestModeloPastaValidationLists:
    def test_construtor_rejeita_subpasta_com_tipo_invalido(self, tmp_path: Path) -> None:
        with pytest.raises(expected_exception=TypeError, match="ModeloPasta"):
            ModeloPasta(
                nome_pasta="home",
                caminho_absoluto=tmp_path,
                subpastas=["not-a-folder"],  # type: ignore[arg-type]
            )

    def test_construtor_rejeita_arquivo_com_tipo_invalido(self, tmp_path: Path) -> None:
        with pytest.raises(expected_exception=TypeError, match="ModeloArquivo"):
            ModeloPasta(
                nome_pasta="home",
                caminho_absoluto=tmp_path,
                subarquivos=["not-a-file"],  # type: ignore[arg-type]
            )


# ===========================================================================
# ModeloSistemaOperacional
# ===========================================================================


class TestModeloSistemaOperacionalCreation:
    def test_cria_com_campos_validos(self, tmp_path: Path) -> None:
        so = ModeloSistemaOperacional(
            nome_sistema="linux",
            versao_sistema="5.15.0",
            user_home=tmp_path,
        )

        assert so.nome_sistema == "linux"
        assert so.versao_sistema == "5.15.0"
        assert so.user_home == tmp_path

    def test_user_home_deve_ser_absoluto(self, tmp_path: Path) -> None:
        with pytest.raises(expected_exception=ValueError, match="absoluto"):
            ModeloSistemaOperacional(
                nome_sistema="linux",
                versao_sistema="5.15.0",
                user_home=Path("relative/home"),
            )

    def test_user_home_deve_existir(self, tmp_path: Path) -> None:
        invalid_home = tmp_path / "missing"

        with pytest.raises(expected_exception=ValueError, match="existente"):
            ModeloSistemaOperacional(
                nome_sistema="linux",
                versao_sistema="5.15.0",
                user_home=invalid_home,
            )

    def test_nome_sistema_com_queixa_de_newline(self, tmp_path: Path) -> None:
        with pytest.raises(expected_exception=ValueError, match="não pode conter quebras"):
            ModeloSistemaOperacional(
                nome_sistema="linux\n",
                versao_sistema="5.15.0",
                user_home=tmp_path,
            )

    def test_versao_com_barra_levanta_value_error(self, tmp_path: Path) -> None:
        with pytest.raises(expected_exception=ValueError, match="não pode conter barras"):
            ModeloSistemaOperacional(
                nome_sistema="linux",
                versao_sistema="5/15",
                user_home=tmp_path,
            )

    def test_user_home_tipo_invalido_levanta_type_error(self, tmp_path: Path) -> None:
        with pytest.raises(expected_exception=TypeError, match="Path"):
            ModeloSistemaOperacional(
                nome_sistema="linux",
                versao_sistema="5.15.0",
                user_home="/home/usuario",  # type: ignore[arg-type]
            )


class TestModeloSistemaOperacionalEquality:
    def test_instancias_iguais_sao_iguais(self, tmp_path: Path) -> None:
        a = ModeloSistemaOperacional(
            nome_sistema="linux",
            versao_sistema="5.15.0",
            user_home=tmp_path,
        )
        b = ModeloSistemaOperacional(
            nome_sistema="linux",
            versao_sistema="5.15.0",
            user_home=tmp_path,
        )

        assert a == b

    def test_instancias_diferentes_nao_sao_iguais(self, tmp_path: Path) -> None:
        a = ModeloSistemaOperacional(
            nome_sistema="linux",
            versao_sistema="5.15.0",
            user_home=tmp_path,
        )
        b = ModeloSistemaOperacional(
            nome_sistema="darwin",
            versao_sistema="5.15.0",
            user_home=tmp_path,
        )

        assert a != b


# ===========================================================================
# ResultadoProcessamento
# ===========================================================================


class TestResultadoProcessamento:
    def test_to_dict_returns_expected_structure(self, tmp_path: Path) -> None:
        estatisticas = EstatisticasProcessamento(
            total_files=1,
            processed_files=1,
            failed_files=0,
            total_bookmarks=1,
        )
        resultado = ResultadoProcessamento(
            bookmarks=[],
            statistics=estatisticas,
            root_path=str(tmp_path),
        )

        expected = {
            "bookmarks": [],
            "statistics": {
                "total_files": 1,
                "processed_files": 1,
                "failed_files": 0,
                "total_bookmarks": 1,
            },
            "root_path": str(tmp_path),
        }

        assert resultado.to_dict() == expected

    def test_root_path_deve_ser_string(self, tmp_path: Path) -> None:
        estatisticas = EstatisticasProcessamento(
            total_files=0,
            processed_files=0,
            failed_files=0,
            total_bookmarks=0,
        )

        with pytest.raises(expected_exception=TypeError, match="root_path deve ser str"):
            ResultadoProcessamento(
                bookmarks=[],
                statistics=estatisticas,
                root_path=tmp_path,  # type: ignore[arg-type]
            )
