# pylint: disable=redefined-outer-name

"""Testes de infraestrutura, serviços e apresentação do Neutron Star."""

from __future__ import annotations

from pathlib import Path

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_diretorio import ModeloPasta
from backend.infrastructure.file_scanners import VarredorSistemaArquivos


class TestVarredorSistemaArquivos:
    """Testes para a vassoura de sistema de arquivos.

    Esta classe valida a construção da árvore de diretórios, os filtros de arquivos HTML e o tratamento de casos especiais.
    """

    def test_varrer_diretorio_constroi_arvore_e_encontra_html(
        self, tmp_path: Path
    ) -> None:
        """Verifica se a vassoura constrói a árvore de diretórios e encontra arquivos HTML.

        Este teste garante que arquivos HTML na pasta raiz e em subdiretórios são detectados e retornados corretamente na lista de resultados.

        Args:
            tmp_path: Diretório temporário usado como raiz para simular a estrutura de diretórios.
        """
        user_root: Path = tmp_path / "home"
        user_root.mkdir()
        (user_root / "bookmarks.html").write_text("<html></html>", encoding="utf-8")
        sub: Path = user_root / "Downloads"
        sub.mkdir()
        (sub / "favorites.bookmarks.html").write_text("<html></html>", encoding="utf-8")
        html_files: list[ModeloArquivo] = self._prepare_and_scan_tree(
            files=[
                ("bookmarks.html", "<html></html>"),
                ("Downloads/favorites.bookmarks.html", "<html></html>"),
            ],
            root=user_root,
        )
        assert len(html_files) == 2
        assert {f.nome_arquivo for f in html_files} == {
            "bookmarks.html",
            "favorites.bookmarks.html",
        }

    def test_ignora_diretorios_ocultos(self, tmp_path: Path) -> None:
        """Verifica se a vassoura ignora diretórios ocultos durante a varredura.

        Este teste garante que arquivos HTML dentro de pastas iniciadas com ponto não são considerados nos resultados da busca.

        Args:
            tmp_path: Diretório temporário usado como raiz para criar a estrutura com diretório oculto.
        """
        user_root: Path = tmp_path / "home"
        user_root.mkdir()
        oculto: Path = user_root / ".secret"
        oculto.mkdir()
        html_files: list[ModeloArquivo] = self._prepare_and_scan_tree(
            files=[(".secret/bookmarks.html", "<html></html>")], root=user_root
        )
        assert not html_files

    def test_should_ignore_non_bookmark_html_and_non_html_files(
        self, tmp_path: Path
    ) -> None:
        """Verifica se a vassoura ignora HTMLs genéricos e arquivos que não são HTML.

        Este teste garante que apenas arquivos com nomes compatíveis com listas de bookmarks sejam considerados como candidatos a bookmarks.

        Args:
            tmp_path: Diretório temporário usado como raiz para criar a estrutura de arquivos de teste.
        """

        user_root: Path = tmp_path / "home"
        user_root.mkdir()
        html_files: list[ModeloArquivo] = self._prepare_and_scan_tree(
            files=[
                ("about.html", "<html></html>"),
                ("favorites.html", "<html></html>"),
                ("bookmark_list.htm", "<html></html>"),
                ("notes.txt", "ignore"),
                ("favorito.html", "<html></html>"),
            ],
            root=user_root,
        )

        assert {f.nome_arquivo for f in html_files} == {
            "bookmark_list.htm",
            "favorito.html",
        }

    def test_scan_directory_returns_empty_when_root_missing(
        self, tmp_path: Path
    ) -> None:
        """Verifica se a varredura retorna vazia quando o diretório raiz não existe.

        Este teste garante que a vassoura lida graciosamente com pastas inexistentes sem lançar exceções nem retornar arquivos HTML.

        Args:
            tmp_path: Diretório temporário usado como base para construir o caminho inexistente.
        """
        user_root: Path = tmp_path / "home"
        pasta_usuario = ModeloPasta(nome_pasta="home", caminho_absoluto=user_root)
        vassoura: VarredorSistemaArquivos = VarredorSistemaArquivos()

        vassoura.varrer_diretorio(pasta_raiz=pasta_usuario)

        assert not vassoura.localizar_arquivos_html(pasta=pasta_usuario)

    def test_internal_filters_handle_hidden_directories_and_html_names(self) -> None:
        """Verifica se os filtros internos tratam diretórios ocultos e nomes de HTML corretamente.

        Este teste garante que diretórios especiais são ignorados e apenas arquivos com nomes compatíveis com listas de bookmarks sejam processados.
        """
        assert VarredorSistemaArquivos._deve_ignorar_diretorio(
            diretorio=Path("/tmp/.secret")
        )
        assert VarredorSistemaArquivos._deve_ignorar_diretorio(
            diretorio=Path("/tmp/System Volume Information")
        )
        assert not VarredorSistemaArquivos._deve_ignorar_diretorio(
            diretorio=Path("/tmp/bookmarks")
        )
        assert VarredorSistemaArquivos._deve_processar_arquivo(
            arquivo=Path("/tmp/bookmarks.html")
        )
        assert VarredorSistemaArquivos._deve_processar_arquivo(
            arquivo=Path("/tmp/favorito.htm")
        )
        assert not VarredorSistemaArquivos._deve_processar_arquivo(
            arquivo=Path("/tmp/readme.txt")
        )
        assert not VarredorSistemaArquivos._deve_processar_arquivo(
            arquivo=Path("/tmp/notes.html")
        )

    def _prepare_and_scan_tree(
        self, files: list[tuple[str, str]], root: Path
    ) -> list[ModeloArquivo]:
        """Cria uma estrutura de arquivos de teste e executa a vassoura HTML.

        Esta função auxiliar escreve os arquivos fornecidos, dispara a varredura e retorna a lista de arquivos HTML detectados.

        Args:
            files: Lista de tuplas com caminho relativo e conteúdo de cada arquivo a ser criado.
            root: Diretório raiz usado como pasta home para inicializar o modelo de pasta.

        Returns:
            Lista de modelos de arquivo representando os arquivos HTML encontrados pela vassoura.
        """

        for relative_path, content in files:
            file_path: Path = root / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

        pasta_identificada = ModeloPasta(nome_pasta="home", caminho_absoluto=root)
        vassoura: VarredorSistemaArquivos = VarredorSistemaArquivos()
        vassoura.varrer_diretorio(pasta_raiz=pasta_identificada)
        return vassoura.localizar_arquivos_html(pasta=pasta_identificada)
