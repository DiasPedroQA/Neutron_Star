"""Testes das funções de infraestrutura de sistema de arquivos."""

from pathlib import Path

import pytest

from src.dominio.excecoes import ErroParseBookmarks, NenhumDiretorioValidoError
from src.infraestrutura.sistema_arquivos import confirmar_dados_entrada, ler_arquivo_html, normalizar_e_validar


class TestNormalizarEValidar:
    """Normalização e validação de um caminho bruto informado como string."""

    def test_diretorio_existente_retorna_path_resolvido(self, tmp_path: Path) -> None:
        """Um diretório real deve retornar o Path correspondente."""
        assert normalizar_e_validar(caminho_bruto=str(tmp_path)) == tmp_path

    def test_caminho_inexistente_retorna_none(self, tmp_path: Path) -> None:
        """Caminho que não existe no disco deve retornar None."""
        assert normalizar_e_validar(caminho_bruto=str(tmp_path / "nao_existe")) is None

    def test_arquivo_em_vez_de_diretorio_retorna_none(self, tmp_path: Path) -> None:
        """Um arquivo (não diretório) não deve ser considerado válido."""
        arquivo: Path = tmp_path / "arquivo.txt"
        arquivo.write_text(data="x")

        assert normalizar_e_validar(caminho_bruto=str(arquivo)) is None


class TestConfirmarDadosEntrada:
    """Validação de entrada, levantando erro quando não há diretório válido."""

    def test_retorna_lista_com_diretorio_valido(self, tmp_path: Path) -> None:
        """Diretório válido deve retornar em uma lista de um elemento."""
        assert confirmar_dados_entrada(caminhos=tmp_path) == [tmp_path]

    def test_diretorio_invalido_levanta_erro_com_contexto(self, tmp_path: Path) -> None:
        """Diretório inválido deve levantar NenhumDiretorioValidoError com o caminho no contexto."""
        invalido: Path = tmp_path / "nao_existe"

        with pytest.raises(expected_exception=NenhumDiretorioValidoError) as exc_info:
            confirmar_dados_entrada(caminhos=invalido)

        assert exc_info.value.contexto["caminhos_tentados"] == invalido


class TestLerArquivoHtml:
    """Leitura de arquivos HTML com tratamento de erro amigável."""

    def test_le_conteudo_de_arquivo_existente(self, tmp_path: Path) -> None:
        """Deve retornar o conteúdo textual do arquivo, decodificado em UTF-8."""
        arquivo: Path = tmp_path / "bookmarks.html"
        arquivo.write_text(data="<html>conteúdo</html>", encoding="utf-8")

        assert ler_arquivo_html(caminho=arquivo) == "<html>conteúdo</html>"

    def test_arquivo_inexistente_levanta_erro_parse_bookmarks(self, tmp_path: Path) -> None:
        """Arquivo ausente deve virar ErroParseBookmarks, não um OSError cru."""
        with pytest.raises(expected_exception=ErroParseBookmarks, match="Não foi possível ler"):
            ler_arquivo_html(caminho=tmp_path / "nao_existe.html")
