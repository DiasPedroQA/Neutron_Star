"""Testes das etapas do pipeline (aplicacao/etapas.py).

Cobre o contrato central corrigido: cada etapa deve ler seus parâmetros
do contexto recebido (ParametrosBusca), nunca de valores fixos locais.
"""

from pathlib import Path

import pytest
from aplicacao.etapas import (
    etapa_buscar,
    etapa_exportar,
    etapa_extrair,
    etapa_selecionar_arquivo,
)
from aplicacao.tipos import ParametrosBusca
from dominio.entidades import TagA, VirtualFolder
from dominio.excecoes import NenhumDiretorioValidoError

_ARQUIVOS: list[Path] = [Path("a.html"), Path("b.html")]

_HTML_UM_FAVORITO = """
<DL><p>
    <DT><A HREF="https://a.com">Site A</A>
</DL><p>
"""


class TestEtapaBuscar:
    """Etapa de busca de arquivos no diretório configurado."""

    def test_encontra_arquivos_no_diretorio_informado(self, tmp_path: Path) -> None:
        """Deve usar o 'diretorio' do contexto, não um valor fixo."""
        (tmp_path / "bookmarks.html").write_text(data="x")
        contexto: ParametrosBusca = {"diretorio": tmp_path, "extensao": ".html"}

        resultado: ParametrosBusca = etapa_buscar(contexto_busca=contexto)

        assert resultado.get("arquivos_encontrados") == [tmp_path / "bookmarks.html"]

    def test_filtra_por_chaves_do_contexto(self, tmp_path: Path) -> None:
        """As chaves do contexto devem de fato restringir o resultado."""
        (tmp_path / "bookmarks_trabalho.html").write_text(data="x")
        (tmp_path / "bookmarks_pessoal.html").write_text(data="x")
        contexto: ParametrosBusca = {
            "diretorio": tmp_path,
            "extensao": ".html",
            "chaves": ["trabalho"],
        }

        resultado: ParametrosBusca = etapa_buscar(contexto_busca=contexto)

        assert resultado.get("arquivos_encontrados") == [tmp_path / "bookmarks_trabalho.html"]

    def test_diretorio_invalido_propaga_erro(self, tmp_path: Path) -> None:
        """Diretório inexistente deve propagar o erro de domínio, não silenciar."""
        contexto: ParametrosBusca = {"diretorio": tmp_path / "nao_existe"}

        with pytest.raises(expected_exception=NenhumDiretorioValidoError):
            etapa_buscar(contexto_busca=contexto)


class TestEtapaSelecionarArquivo:
    """Seleção de um arquivo dentre os encontrados na etapa anterior."""

    @pytest.mark.parametrize(
        argnames=("arquivos", "indice_arquivo", "esperado"),
        argvalues=[
            pytest.param(_ARQUIVOS, 1, Path("b.html"), id="indice_informado"),
            pytest.param([Path("unico.html")], None, Path("unico.html"), id="indice_ausente"),
            pytest.param(_ARQUIVOS, 99, Path("a.html"), id="indice_fora_do_intervalo"),
        ],
    )
    def test_seleciona_arquivo_esperado(
        self,
        arquivos: list[Path],
        indice_arquivo: int | None,
        esperado: Path,
    ) -> None:
        """Deve escolher o arquivo correto conforme o índice informado no contexto."""
        contexto: ParametrosBusca = {"arquivos_encontrados": arquivos}
        if indice_arquivo is not None:
            contexto["indice_arquivo"] = indice_arquivo

        resultado: ParametrosBusca = etapa_selecionar_arquivo(contexto_busca=contexto)

        assert resultado.get("arquivo_selecionado") == esperado

    def test_levanta_erro_quando_nenhum_arquivo_encontrado(self) -> None:
        """Lista vazia deve levantar ValueError claro, nunca IndexError silencioso."""
        contexto: ParametrosBusca = {"arquivos_encontrados": []}

        with pytest.raises(expected_exception=ValueError, match="Nenhum arquivo encontrado"):
            etapa_selecionar_arquivo(contexto_busca=contexto)


class TestEtapaExtrair:
    """Extração da árvore de bookmarks a partir do arquivo HTML selecionado."""

    def test_extrai_raiz_bookmarks_do_arquivo_selecionado(self, tmp_path: Path) -> None:
        """Deve ler o 'arquivo_selecionado' do contexto e popular 'raiz_bookmarks'."""
        arquivo: Path = tmp_path / "bookmarks.html"
        arquivo.write_text(data=_HTML_UM_FAVORITO, encoding="utf-8")
        contexto: ParametrosBusca = {"arquivo_selecionado": arquivo}

        resultado: ParametrosBusca = etapa_extrair(contexto_busca=contexto)

        assert "raiz_bookmarks" in resultado
        raiz: VirtualFolder = resultado["raiz_bookmarks"]
        assert isinstance(raiz, VirtualFolder)
        primeiro_filho = raiz.filhos_da_pasta[0]
        assert isinstance(primeiro_filho, TagA)
        assert primeiro_filho.titulo == "Site A"


class TestEtapaExportar:
    """Exportação da árvore de bookmarks nos formatos configurados."""

    def test_exporta_nos_formatos_do_contexto(self, tmp_path: Path) -> None:
        """Deve usar 'formatos_exportacao' e 'diretorio_saida' do contexto, criando os arquivos."""
        raiz = VirtualFolder(nome="Raiz", filhos_da_pasta=[TagA(url="https://a.com", titulo="A")])
        contexto: ParametrosBusca = {
            "raiz_bookmarks": raiz,
            "formatos_exportacao": [".json", ".csv"],
            "diretorio_saida": str(tmp_path),
        }

        etapa_exportar(contexto_busca=contexto)

        assert (tmp_path / "bookmarks.json").exists()
        assert (tmp_path / "bookmarks.csv").exists()

    def test_sem_raiz_bookmarks_levanta_erro_claro(self) -> None:
        """Sem 'raiz_bookmarks' no contexto, deve levantar ValueError, não AttributeError."""
        with pytest.raises(expected_exception=ValueError, match="Nenhuma raiz de bookmarks"):
            etapa_exportar(contexto_busca={})
