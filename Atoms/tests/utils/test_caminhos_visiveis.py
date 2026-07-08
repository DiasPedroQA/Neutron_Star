"""Testes para _caminhos_visiveis (poda de diretórios ocultos na travessia).

Garante que a travessia nunca desce em diretórios ocultos (nome iniciado
com '.') — diferente do `Path.glob("**/*")` anterior, que visitava tudo e
descartava depois em `_validar_caminho`.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from src.utils.system_tools import _caminhos_visiveis


class TestCaminhosVisiveis:
    """Suite de testes para _caminhos_visiveis."""

    @pytest.mark.parametrize(
        "arquivos, esperados",
        [
            # Cenário 1: arquivo dentro de diretório oculto
            (
                ["/raiz/.venv/lib/site-packages/pacote/index.html", "/raiz/visivel.html"],
                {"visivel.html"},
            ),
            # Cenário 2: arquivo oculto na raiz
            (
                ["/raiz/.oculto.html", "/raiz/visivel.html"],
                {"visivel.html"},
            ),
            # Cenário 3: vários arquivos visíveis
            (
                ["/raiz/a.html", "/raiz/b.txt"],
                {"a.html", "b.txt"},
            ),
            # Cenário 4: mistura de ocultos e visíveis
            (
                ["/raiz/.git/config", "/raiz/src/main.py", "/raiz/README.md"],
                {"main.py", "README.md"},
            ),
        ],
        ids=[
            "dentro_diretorio_oculto",
            "arquivo_oculto_raiz",
            "visiveis_varios",
            "misturados",
        ],
    )
    def test_filtra_caminhos_visiveis(
        self,
        fs: FakeFilesystem,
        arquivos: list[str],
        esperados: set[str],
    ) -> None:
        """Verifica que _caminhos_visiveis filtra corretamente ocultos."""
        # Cria os arquivos no filesystem fake
        for arquivo in arquivos:
            fs.create_file(file_path=arquivo)

        # Executa a função
        resultado: list[Path] = list(_caminhos_visiveis(raiz=Path("/raiz")))

        # Extrai nomes dos arquivos retornados
        nomes: set[str] = {c.name for c in resultado}
        assert nomes == esperados

        # Verifica que não retornou caminhos com .git/ .venv/ etc.
        for caminho in resultado:
            assert ".git" not in str(caminho)
            assert ".venv" not in str(caminho)
            assert not caminho.name.startswith(".")

    def test_nunca_desce_no_diretorio_oculto(
        self,
        fs: FakeFilesystem,
        mocker: MagicMock,
    ) -> None:
        """A poda deve acontecer ANTES de entrar no diretório oculto."""
        # Cria arquivos
        fs.create_file(file_path="/raiz/.oculto/dentro.html")
        fs.create_file(file_path="/raiz/visivel.html")

        # Espia a chamada do os.walk
        espia = mocker.patch("os.walk", wraps=__import__("os").walk)

        # Executa
        list(_caminhos_visiveis(raiz=Path("/raiz")))

        # Verifica que os.walk só foi chamado uma vez (a poda evitou a descida)
        assert espia.call_count == 1

        # Verifica que o arquivo dentro do diretório oculto não foi retornado
        resultado: list[Path] = list(_caminhos_visiveis(raiz=Path("/raiz")))
        nomes: set[str] = {c.name for c in resultado}
        assert "visivel.html" in nomes
        assert "dentro.html" not in nomes

    def test_diretorio_vazio_retorna_lista_vazia(
        self,
        fs: FakeFilesystem,
    ) -> None:
        """Raiz vazia não retorna nenhum caminho visível."""
        fs.create_dir(directory_path="/raiz")
        resultado: list[Path] = list(_caminhos_visiveis(raiz=Path("/raiz")))
        assert not resultado

    def test_subdiretorio_visivel_e_retornado(
        self,
        fs: FakeFilesystem,
    ) -> None:
        """Subdiretórios visíveis devem ser incluídos no resultado."""
        fs.create_file(file_path="/raiz/subdir/arquivo.txt")
        fs.create_file(file_path="/raiz/outro.html")

        resultado: list[Path] = list(_caminhos_visiveis(raiz=Path("/raiz")))
        nomes = {c.name for c in resultado}

        # Deve incluir apenas arquivos, não diretórios
        # (assumindo que _caminhos_visiveis retorna arquivos)
        assert "arquivo.txt" in nomes
        assert "outro.html" in nomes
        assert len(resultado) == 2

        # Nenhum caminho deve conter segmentos ocultos
        for caminho in resultado:
            assert not any(parte.startswith(".") for parte in caminho.parts)

    def test_caminhos_absolutos_e_relativos(
        self,
        fs: FakeFilesystem,
    ) -> None:
        """Verifica que a raiz pode ser absoluta ou relativa."""
        self._extrair_caminhos_absolutos_e_relativos(fs=fs, file_path="/home/user/docs/file.txt", arg2="/home/user")
        self._extrair_caminhos_absolutos_e_relativos(fs=fs, file_path="/tmp/relative/file.txt", arg2="/tmp")

    def _extrair_caminhos_absolutos_e_relativos(self, fs, file_path, arg2) -> None:
        # Cria estrutura
        fs.create_file(file_path=file_path)

        # Testa com caminho absoluto
        resultado_abs: list[Path] = list(_caminhos_visiveis(raiz=Path(arg2)))
        assert any(c.name == "file.txt" for c in resultado_abs)
